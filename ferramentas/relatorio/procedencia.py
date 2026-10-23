"""De onde vem cada insumo do motor, com a nota real — por caminho (dossiê / lote) e por campo.

Dossiê (dossie/base.py): demonstrações e ações da CVM, preço do COTAHIST e proventos da B3 = A; datas de pagamento da
StatusInvest = C (só a defasagem). Lote: demonstrações da CVM = A (não financeiras); preço = COTAHIST (A, precos_hall); os
escalares digitados das financeiras (VPA, ROE, payout, DPA, P/L) e o DPA/P/L das não financeiras vêm da StatusInvest ou dos
fatos do lote sem fonte primária por campo = C; o que o lote marca como arbitrado = "—".
Fase 3, fatia 1 (19/10/2026) — não financeira do lote, POR CAMPO: `acoes` só é A se o valor que a empresa carrega é o que o
lote registrou de uma fonte oficial (`insumos_a`); as âncoras usam o provento já ex da B3 (`proventos_ja_ex`, A), não o DPA
da StatusInvest (que só entra nos informativos); e todo campo de DADO do `Industrial` fora do default que entra nas âncoras
(`DADO_ANCORA_NF`) pesa na nota do central (`dados_lote`): registrado → a nota da fonte; senão C. Julgamento
(`JULGAMENTO_NF`: janela, g, alíquota, receita de meio, desconto…) é premissa da casa com razão escrita, não dado: não mexe
na nota de fonte (as principais saem em `premissas()`).
Fatia 2 (20/10/2026): o DPA/JCP das não financeiras do lote é da B3 (`proventos_hall`, A) quando o valor que o motor lê é o
registrado (`proventos_nf`); só os informativos (DY, Bazin, teto, Bogle) o usam.
Fatia 3 (20/10/2026): no caminho do lote NF o preço e o P/L histórico só são A se o valor é o registrado (`precos_hall.preco`,
`pl_historico.do_hall`).
Campo que não está aqui não ganha nota boa: `de()` devolve C ("não classificado").
"""
from __future__ import annotations

import dataclasses
import json
import pathlib

from relatorio.modelo import NOTAS, SEM_FONTE, Origem

C_SI_DATAS = Origem("StatusInvest (datas)", "C", "datas de pagamento da StatusInvest, só para a defasagem do provento (§6.3)")
C_LOTE = Origem("lote (digitado)", "C", "escalar digitado no lote a partir da StatusInvest ou dos fatos do lote, sem fonte "
                "primária por campo (cabeçalho do lote)")
B3_JA_EX = Origem("B3 proventos (já ex)", "A", "B3, proventos em dinheiro (API pública GetListedCashDividends): o provento "
                  "já ex ainda no caixa do balanço, na dívida líquida (proventos_ex.py, §11.1)")
INSUMOS_DOSSIE = pathlib.Path(__file__).resolve().parent.parent / "dossie" / "insumos"

# campos do `Industrial` (motor_nao_financeiras): identidade, DADO com chave própria na tabela, DADO que entra nas âncoras do
# central e JULGAMENTO (premissa da casa, escrita — não é nota de fonte). Todo campo novo do dataclass tem de cair num deles
# (tests/test_fase3_procedencia.py), senão um dado digitado entraria no central sem pesar na nota.
IDENTIDADE_NF = ("ticker", "nome", "perfil")
DADO_PROPRIO_NF = {"preco": "preco", "n_acoes": "acoes", "jcp_share": "proventos", "anos_pagos_10": "proventos",
                   "pl_hist": "pl_hist", "defasagem_meses": "defasagem", "kd_ri": "kd", "spread_kd": "kd"}
# adversário (19/10): receita de meio (receita da CVM × índice de preço de commodity), D&A ÷ receita de meio, alíquota digitada,
# crédito de IR com prazo e g do 1º estágio (medido na StatusInvest, WEGE3) são NÚMEROS que chegam ao central — dado, não julgamento
DADO_ANCORA_NF = ("outros_passivos", "outros_passivos_financeiros", "reproducao_por_acao", "fator_preco",
                  "custo_variavel_preco", "capex_expansao", "deflator", "receita_meio", "da_receita", "aliquota",
                  "aliquota_fase", "g1_real")
JULGAMENTO_NF = ("anos_ciclo", "janela_razao", "receita_meio_fonte",
                 "aliquota_permanente_fonte", "aliquota_fonte", "aliquota_desde", "spread_fonte", "g_real",
                 "anos_g1", "qualitativo", "qualitativo_origem", "desconto_controlador", "reproducao_fonte",
                 "usar_reproducao_como_ancora", "fora_circulo", "outras_liquidas", "anos_outras", "capex_ciclico",
                 "outros_passivos_fonte", "declinio_sem_liberacao", "impairment_normalizado", "defasagem_fonte",
                 "controlador_discricionario", "controlador_discricionario_fonte", "trava_razao")


def _fora_do_default(emp, nome: str) -> bool:
    f = next(x for x in dataclasses.fields(emp) if x.name == nome)
    if f.default is not dataclasses.MISSING:
        padrao = f.default
    elif f.default_factory is not dataclasses.MISSING:
        padrao = f.default_factory()
    else:
        return True                       # campo obrigatório: sempre informado
    return getattr(emp, nome) != padrao


def _origem_do_dado(emp, nome: str) -> Origem:
    """Nota de um campo de dado do lote: o registro em `insumos_a` (valor igual ao usado), a nota declarada no próprio campo
    (`capex_expansao.nota_fonte`) ou C."""
    import insumos_a
    v = getattr(emp, nome)
    o = insumos_a.origem(emp.ticker, nome, v)
    if o is None and isinstance(v, dict) and v.get("nota_fonte") in NOTAS and str(v.get("fonte") or "").strip():
        o = Origem(f"{nome} (declarado)", v["nota_fonte"], str(v["fonte"]))
    return o or Origem(f"lote (digitado): {nome}", "C", f"{nome} digitado no lote sem fonte primária registrada (insumos_a)")


def proventos_nf(emp) -> Origem:
    """DPA/JCP da não financeira do lote (fase 3, fatia 2): B3 (A) só se o DPA e o JCP que o motor lê (SI) e a fatia de JCP da
    empresa são os registrados por `proventos_hall`; senão a StatusInvest (C)."""
    import insumos_a
    import proventos_hall
    from motor_nao_financeiras import SI
    o = proventos_hall.origem(emp.ticker, SI)
    if o is not None and insumos_a.origem(emp.ticker, "jcp_share", emp.jcp_share) is not None:
        return o
    return Origem("StatusInvest (DPA)", "C", "DPA por data-com da StatusInvest")


def dados_ancora(emp, serie: Origem) -> Origem:
    """A pior origem entre os campos de DADO_ANCORA_NF fora do default; sem nenhum, as âncoras só usam a série (= `serie`)."""
    origens = [_origem_do_dado(emp, k) for k in DADO_ANCORA_NF if _fora_do_default(emp, k)]
    return max(origens, key=lambda o: NOTAS.index(o.nota)) if origens else serie


def kd(emp) -> Origem:
    """Custo da dívida que entra no WACC (motor_nao_financeiras.custo_divida, mesma ordem): Kd do RI ou spread declarado só com
    registro em `insumos_a` (senão C); padrão = rf (A) + spread sintético da tabela de rating (Damodaran, nota B)."""
    import credito
    import insumos_a
    if emp.kd_ri:
        return (insumos_a.origem(emp.ticker, "kd_ri", emp.kd_ri.get("valor"))
                or Origem("lote (digitado): kd_ri", "C", f"Kd do RI digitado no lote: {emp.kd_ri.get('fonte', '')}"))
    if emp.spread_kd is not None:
        return (insumos_a.origem(emp.ticker, "spread_kd", emp.spread_kd)
                or Origem("lote (digitado): spread_kd", "C", f"spread de crédito digitado no lote: {emp.spread_fonte}"))
    return Origem("Kd sintético (Damodaran)", "B", f"rf + spread pela cobertura de juros normalizada — {credito.FONTE}")


def _insumos_dossie(tk: str, serie: Origem) -> Origem:
    """Dados da ficha do dossiê que entram nas âncoras: insumos com fonte A/B obrigatória (dossie/gerar._valor); vale a pior
    nota declarada em dossie/insumos/<TK>.json (sem insumo: só a série)."""
    arq = INSUMOS_DOSSIE / f"{tk}.json"
    notas = []

    def anda(x):
        if isinstance(x, dict):
            if "nota_fonte" in x:
                notas.append(x["nota_fonte"])
            for v in x.values():
                anda(v)
        elif isinstance(x, list):
            for v in x:
                anda(v)
    if arq.exists():
        anda(json.loads(arq.read_text(encoding="utf-8")))
    nota = max(notas, key=NOTAS.index, default="A")
    if nota == "A":
        return serie
    return Origem("insumos do dossiê", nota, f"pior nota declarada em dossie/insumos/{tk}.json")


def _mercado(c: dict) -> Origem:
    import mercado as mercado_hall
    d = mercado_hall.dados()
    if c["mk"].data in (d["data"], "/".join(reversed(d["data"].split("-")))):
        return Origem("Tesouro + ANBIMA", "A", f"rf: {d['rf_titulo']}, {d['rf_tipo']}; π: {d['pi_tipo']} — {d['data']} "
                      "(mercado_vigente.json)", data=_iso(d["data"]))
    return Origem("Tesouro + ANBIMA", "A", f"rf: Tesouro Transparente; π: ETTJ ANBIMA — dados/mercado_{c['mk'].data}.json",
                  data=_iso(c["mk"].data))


def _iso(data: str | None) -> str:
    """AAAA-MM-DD a partir de AAAA-MM-DD ou DD/MM/AAAA; outro formato → "" (sem data, não se chuta)."""
    data = (data or "").strip()
    if len(data) == 10 and data[4] == "-" and data[7] == "-":
        return data
    if len(data) == 10 and data[2] == "/" and data[5] == "/":
        return f"{data[6:]}-{data[3:5]}-{data[:2]}"
    return ""


def _data_ltm(tk: str) -> str:
    """Fim do trimestre do LTM que o motor lê (`ltm_ref` da série CVM: "2T26" → 2026-06-30; trimestre civil, a mesma leitura
    de `proventos_ja_ex`). Ticker sem série carregada → "" (N12)."""
    from motor_nao_financeiras import CVM
    from ltm import ltm_ref_de
    reg = CVM.get(tk)
    if not reg:
        return ""
    ref = ltm_ref_de(reg)
    try:
        tri, ano = int(ref[0]), 2000 + int(ref[2:])
    except (ValueError, IndexError):
        return ""
    if not 1 <= tri <= 4:
        return ""
    return f"{ano}-{3 * tri:02d}-{(31 if tri in (1, 4) else 30)}"


def tabela(c: dict) -> dict[str, Origem]:
    """{campo: Origem} do caso. Campos: serie, acoes, preco, proventos, defasagem, pl_hist, mercado e os escalares das
    financeiras (vpa, roe_lp, roe_inicio, payout, dpa_medio_5a, horizonte_finito, sotp)."""
    emp, data = c["empresa"], c["data"]
    t = {"preco": Origem("COTAHIST", "A", f"B3, COTAHIST, fechamento (PREULT) de {data}", data=_iso(data)), "mercado": _mercado(c)}
    ltm = _data_ltm(emp.ticker)
    if c["dossie"] is not None:
        import proventos_hall          # o dossiê lê o DPA com as regras do coletor do hall (fatia 2b)
        anos = c["dossie"]["anos"]
        serie = Origem("CVM DFP/ITR", "A", f"CVM, DFP {anos[0]}–{anos[-1]} + ITR de 2026 (LTM), dados abertos", data=ltm)
        t |= {"serie": serie,
              "acoes": Origem("CVM ITR (ações)", "A", "CVM, composição do capital do ITR (sem tesouraria)", data=ltm),
              "proventos": proventos_hall.origem_b3(emp.ticker),
              "pl_hist": Origem("CVM + COTAHIST", "A", "P/L histórico: lucro e ações do DFP (CVM) × fechamento do ano (B3)"),
              "proventos_ja_ex": B3_JA_EX, "dados_lote": _insumos_dossie(emp.ticker, serie), "kd": kd(emp)}
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
        import insumos_a
        serie = Origem("CVM DFP/ITR", "A", "CVM, DFP 2016–25 + ITR de 2026 (LTM), dados abertos", data=ltm)
        t |= {"serie": serie, "acoes": insumos_a.origem(emp.ticker, "acoes", emp.n_acoes) or C_LOTE,
              "preco": insumos_a.origem(emp.ticker, "preco", emp.preco) or Origem(
                  "lote (digitado): preco", "C", "preço digitado no lote, não lido do snapshot do COTAHIST (precos_hall.preco)"),
              "proventos": proventos_nf(emp), "pl_hist": insumos_a.origem(emp.ticker, "pl_hist", emp.pl_hist) or C_LOTE,
              "proventos_ja_ex": B3_JA_EX, "dados_lote": dados_ancora(emp, serie), "kd": kd(emp)}
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
    # não financeira: o provento que entra no central é o já ex da B3 (dívida líquida, §11.1), não o DPA (só informativos)
    # e o Kd (WACC) entra nas âncoras de fluxo (adversário, 19/10); o valor de reprodução não usa Kd
    "DCF (3 cenários)": ("serie", "acoes", "proventos_ja_ex", "dados_lote", "kd", "mercado"),
    "DCF normalizado (3 cenários)": ("serie", "acoes", "proventos_ja_ex", "dados_lote", "kd", "mercado"),
    "EPV": ("serie", "acoes", "proventos_ja_ex", "dados_lote", "kd", "mercado"),
    "EPV de meio de ciclo": ("serie", "acoes", "proventos_ja_ex", "dados_lote", "kd", "mercado"),
    "Owner Earnings ÷ (Ke − g)": ("serie", "acoes", "proventos_ja_ex", "dados_lote", "kd", "mercado"),
    "Valor de reprodução": ("serie", "acoes", "proventos_ja_ex", "dados_lote"),
    "P/VP justificado": ("vpa", "roe_lp", "payout", "mercado"),
    "DDM 2 estágios": ("vpa", "roe_inicio", "roe_lp", "payout", "mercado"),
    "DDM até o fim do contrato": ("vpa", "roe_inicio", "roe_lp", "payout", "mercado", "horizonte_finito"),
    "SOTP": ("sotp", "mercado"),
}
INFO_NF = {
    # lucro normalizado (Graham, PEG, Bogle) = NOPAT de meio − juros ao Kd; DPA sustentável (Bazin, teto, DY) ≤ FCFE do OE
    "graham_orig": ("serie", "acoes", "dados_lote", "kd"), "graham_br": ("serie", "acoes", "dados_lote", "kd", "mercado"),
    "graham_rev": ("serie", "acoes", "dados_lote", "kd", "mercado"),
    "bazin6": ("proventos", "serie", "acoes", "dados_lote"),
    "teto_renda": ("proventos", "defasagem", "serie", "acoes", "dados_lote", "mercado"),
    "bogle_nom": ("proventos", "defasagem", "pl_hist", "serie", "acoes", "dados_lote", "kd", "preco", "mercado"),
    "peg": ("preco", "serie", "acoes", "dados_lote", "kd", "mercado"),
    "dy": ("proventos", "defasagem", "serie", "acoes", "dados_lote", "preco", "mercado"),
}
INFO_FIN = {
    "graham_orig": ("roe_lp", "vpa"), "graham_br": ("roe_lp", "vpa", "mercado"),
    "bazin6": ("dpa_medio_5a", "roe_lp", "vpa", "payout"),
    "teto_renda": ("dpa_medio_5a", "roe_lp", "vpa", "payout", "defasagem", "mercado"),
    "bogle_nom": ("dpa_medio_5a", "roe_lp", "vpa", "payout", "defasagem", "pl_hist", "preco", "mercado"),
    "dy": ("dpa_medio_5a", "roe_lp", "vpa", "payout", "defasagem", "preco", "mercado"),
    "roe_implicito": ("preco", "vpa", "payout", "mercado"),
}


def resumo_hall() -> dict:
    """Métrica da fase 3, no caminho do lote (os tickers do hall sem ficha de dossiê): {ticker: nota do central} e quantos
    insumos de âncora ainda são C do lote. Mesma conta do relatório (`quanti`: pior nota das âncoras), sem gerar PDF."""
    import universo
    from dossie import gerar
    from relatorio.modelo import pior
    centrais, c_lote = {}, 0
    for tk, it in universo.avaliar_todos().items():
        if tk in gerar.FICHAS:
            continue
        emp = it["empresa"]
        c = dict(tk=tk, empresa=emp, r=it["r"], mk=universo.MK, data=it["data_preco"], dossie=None,
                 financeira=hasattr(emp, "roe_lp"))
        t = tabela(c)
        origens = [o for nome in it["r"]["ancoras"] for o in de(t, *ANCORA.get(nome, ()))]
        centrais[tk] = pior(origens)
        c_lote += sum(1 for o in origens if o.fonte.startswith("lote (digitado)"))
    return {"centrais": centrais, "c_lote_nas_ancoras": c_lote}
