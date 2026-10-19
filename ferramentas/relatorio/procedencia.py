"""De onde vem cada insumo do motor, com a nota real — por caminho (dossiê / lote) e por campo.

Dossiê (dossie/base.py): demonstrações e ações da CVM, preço do COTAHIST e proventos da B3 = A; datas de pagamento da
StatusInvest = C (só a defasagem). Lote: demonstrações da CVM = A (não financeiras); preço = COTAHIST (A, precos_hall); os
escalares digitados das financeiras (VPA, ROE, payout, DPA, P/L) e os proventos/ações das não financeiras vêm da
StatusInvest ou dos fatos do lote sem fonte primária por campo = C; o que o lote marca como arbitrado = "—".
Campo que não está aqui não ganha nota boa: `de()` devolve C ("não classificado").
"""
from __future__ import annotations

from relatorio.modelo import SEM_FONTE, Origem

C_SI_DATAS = Origem("StatusInvest (datas)", "C", "datas de pagamento da StatusInvest, só para a defasagem do provento (§6.3)")
C_LOTE = Origem("lote (digitado)", "C", "escalar digitado no lote a partir da StatusInvest ou dos fatos do lote, sem fonte "
                "primária por campo (cabeçalho do lote)")


def _mercado(c: dict) -> Origem:
    import mercado as mercado_hall
    d = mercado_hall.dados()
    if c["mk"].data in (d["data"], "/".join(reversed(d["data"].split("-")))):
        return Origem("Tesouro + ANBIMA", "A", f"rf: {d['rf_titulo']}, {d['rf_tipo']}; π: {d['pi_tipo']} — {d['data']} "
                      "(mercado_vigente.json)")
    return Origem("Tesouro + ANBIMA", "A", f"rf: Tesouro Transparente; π: ETTJ ANBIMA — dados/mercado_{c['mk'].data}.json")


def tabela(c: dict) -> dict[str, Origem]:
    """{campo: Origem} do caso. Campos: serie, acoes, preco, proventos, defasagem, pl_hist, mercado e os escalares das
    financeiras (vpa, roe_lp, roe_inicio, payout, dpa_medio_5a, horizonte_finito, sotp)."""
    emp, data = c["empresa"], c["data"]
    t = {"preco": Origem("COTAHIST", "A", f"B3, COTAHIST, fechamento (PREULT) de {data}"), "mercado": _mercado(c)}
    if c["dossie"] is not None:
        anos = c["dossie"]["anos"]
        t |= {"serie": Origem("CVM DFP/ITR", "A", f"CVM, DFP {anos[0]}–{anos[-1]} + ITR de 2026 (LTM), dados abertos"),
              "acoes": Origem("CVM ITR (ações)", "A", "CVM, composição do capital do ITR (sem tesouraria)"),
              "proventos": Origem("B3 proventos", "A", "B3, proventos em dinheiro por data-com (API pública)"),
              "pl_hist": Origem("CVM + COTAHIST", "A", "P/L histórico: lucro e ações do DFP (CVM) × fechamento do ano (B3)")}
    elif c["financeira"]:
        t |= {k: C_LOTE for k in ("vpa", "roe_lp", "roe_inicio", "payout", "dpa_medio_5a", "pl_hist")}
        t["proventos"] = t["dpa_medio_5a"]
        if emp.horizonte_finito:
            t["horizonte_finito"] = Origem("arbitrado (contrato)", SEM_FONTE, "probabilidade de renovação e haircut de "
                                           "margem do contrato arbitrados no lote, sem fonte numérica (AUD-58)")
        if emp.sotp is not None:
            t["sotp"] = Origem("SOTP do lote", SEM_FONTE, "soma das partes do lote: participações e descontos sem nota "
                               "por campo")
    else:
        t |= {"serie": Origem("CVM DFP/ITR", "A", "CVM, DFP 2016–25 + ITR de 2026 (LTM), dados abertos"), "acoes": C_LOTE,
              "proventos": Origem("StatusInvest (DPA)", "C", "DPA por data-com da StatusInvest"), "pl_hist": C_LOTE}
    if emp.defasagem_meses is not None and emp.defasagem_fonte.strip():
        t["defasagem"] = Origem("defasagem declarada", "C", f"declarada na ficha: {emp.defasagem_fonte}")
    else:
        t["defasagem"] = C_SI_DATAS
    return t


def premissas(c: dict) -> list[str]:
    """Premissas de JULGAMENTO (método, não dado): ficam escritas no relatório, sem nota de fonte — a nota é de dado."""
    emp, r = c["empresa"], c["r"]
    dc = (c["dossie"] or {}).get("dc") or emp.desconto_controlador or {}
    out = [f"Perfil do motor: {emp.perfil}.",
           f"Desconto de controlador: {dc.get('tipo', 'zero')} "
           f"({f'{100 * (r.get('desc_controlador') or 0):.1f}'.replace('.', ',')}% no valor) — "
           f"{(dc.get('razao') or 'sem razão escrita').strip()[:300]}"]
    if hasattr(emp, "g_real"):
        out.append(f"g real perpétuo: {f'{100 * emp.g_real:.1f}'.replace('.', ',')}% (só conta com ROIC acima do WACC).")
    if getattr(emp, "janela_razao", ""):
        out.append(f"Janela: {emp.janela_razao}")
    out.append(f"Notas qualitativas: {r.get('qualitativo_origem', '')}.")
    return out


def de(t: dict[str, Origem], *campos: str) -> tuple[Origem, ...]:
    return tuple(t.get(k, Origem(f"{k} (não classificado)", "C", "campo sem procedência mapeada")) for k in campos)


# insumos de cada âncora (nome do motor) e de cada informativo
ANCORA = {
    "DCF (3 cenários)": ("serie", "acoes", "proventos", "mercado"),
    "DCF normalizado (3 cenários)": ("serie", "acoes", "proventos", "mercado"),
    "EPV": ("serie", "acoes", "proventos", "mercado"),
    "EPV de meio de ciclo": ("serie", "acoes", "proventos", "mercado"),
    "Owner Earnings ÷ (Ke − g)": ("serie", "acoes", "proventos", "mercado"),
    "Valor de reprodução": ("serie", "acoes", "proventos"),
    "P/VP justificado": ("vpa", "roe_lp", "payout", "mercado"),
    "DDM 2 estágios": ("vpa", "roe_inicio", "roe_lp", "payout", "mercado"),
    "DDM até o fim do contrato": ("vpa", "roe_inicio", "roe_lp", "payout", "mercado", "horizonte_finito"),
    "SOTP": ("sotp", "mercado"),
}
INFO_NF = {
    "graham_orig": ("serie", "acoes"), "graham_br": ("serie", "acoes", "mercado"),
    "graham_rev": ("serie", "acoes", "mercado"), "bazin6": ("proventos", "serie", "acoes"),
    "teto_renda": ("proventos", "defasagem", "serie", "acoes", "mercado"),
    "bogle_nom": ("proventos", "defasagem", "pl_hist", "serie", "acoes", "preco", "mercado"),
    "peg": ("preco", "serie", "acoes", "mercado"), "dy": ("proventos", "defasagem", "preco", "mercado"),
}
INFO_FIN = {
    "graham_orig": ("roe_lp", "vpa"), "graham_br": ("roe_lp", "vpa", "mercado"),
    "bazin6": ("dpa_medio_5a", "roe_lp", "vpa", "payout"),
    "teto_renda": ("dpa_medio_5a", "roe_lp", "vpa", "payout", "defasagem", "mercado"),
    "bogle_nom": ("dpa_medio_5a", "roe_lp", "vpa", "payout", "defasagem", "pl_hist", "preco", "mercado"),
    "dy": ("dpa_medio_5a", "roe_lp", "vpa", "payout", "defasagem", "preco", "mercado"),
    "roe_implicito": ("preco", "vpa", "payout", "mercado"),
}
