"""Bloco PREÇO e VEREDITO: cada fórmula com o seu valor por ação, o papel (entra no central × informativa) e a fonte.

Nada é recalculado: os valores são as chaves de `avaliar()` dos motores. Fórmula pedida que o motor não usa para o setor
(EPV, DCF e Owner Earnings em financeira) aparece com o motivo, sem número.
"""
from __future__ import annotations

import carimbos
from motor_financeiras import descontar, entrada_parcial
from relatorio import procedencia as pr
from relatorio.modelo import Numero, Secao, decide, pior

ROTULO = {
    "DCF (3 cenários)": "DCF — fluxo de caixa descontado, 3 cenários de margem (25/50/25)",
    "DCF normalizado (3 cenários)": "DCF normalizado — 3 cenários de margem de meio de ciclo (25/50/25)",
    "EPV": "EPV (Greenwald) — lucro operacional sem crescimento ÷ WACC",
    "EPV de meio de ciclo": "EPV (Greenwald) de meio de ciclo",
    "Owner Earnings ÷ (Ke − g)": "Buffett — Owner Earnings ÷ (Ke − g)",
    "Valor de reprodução": "Greenwald — valor de reprodução (PL contábil)",
    "P/VP justificado": "P/VP justificado — VPA × (ROE − g) ÷ (Ke − g)",
    "DDM 2 estágios": "DDM — dividendos descontados, 2 estágios",
    "DDM até o fim do contrato": "DDM até o fim do contrato (seguradora com prazo)",
    "SOTP": "SOTP — soma das partes (holding)",
}
NAO_SE_APLICA_FIN = ("não se aplica a financeira: dívida é matéria-prima e o fluxo do acionista é o dividendo — o motor de "
                     "financeiras usa P/VP justificado e DDM")


def _num(rot, valor, origens, unidade="R$", papel="", obs="", baixo=None, alto=None):
    return Numero(rot, valor, unidade, tuple(origens), papel, obs, baixo, alto)


def _faixa_dcf(r: dict) -> tuple[float | None, float | None]:
    """Baixo/alto do DCF = cenários pessimista e otimista de margem (25º e 75º percentil) do motor, com o desconto de controlador
    como no valor (só em valor > 0). A âncora do central é a ponderação 25/50/25 dos três, com cenário negativo = 0."""
    dcf = r.get("dcf")
    if not isinstance(dcf, dict) or "pessimista" not in dcf or "otimista" not in dcf:
        return None, None
    f = descontar({"b": dcf["pessimista"], "a": dcf["otimista"]}, r.get("desc_controlador") or 0.0)
    return f["b"], f["a"]


def secao_preco(c: dict) -> Secao:
    r, t, fin = c["r"], pr.tabela(c), c["financeira"]
    s = Secao("Preço justo por método")
    for nome, v in r["ancoras"].items():
        baixo, alto = _faixa_dcf(r) if nome.startswith("DCF") else (None, None)
        s.numeros.append(_num(ROTULO.get(nome, nome), v, pr.de(t, *pr.ANCORA.get(nome, ())), papel="central", baixo=baixo, alto=alto))
    for d in r.get("ancoras_descartadas", []):
        s.avisos.append(f"Âncora descartada pelo motor: {d}.")
    if fin:
        for metodo in ("DCF", "EPV (Greenwald)", "Buffett — Owner Earnings"):
            s.numeros.append(_num(metodo, None, (), papel="informativo", obs=NAO_SE_APLICA_FIN))
    info = pr.INFO_FIN if fin else pr.INFO_NF
    linhas = [("graham_orig", "Graham — √(22,5 × LPA normalizado × VPA)", "R$", ""),
              ("graham_br", "Graham-BR — o 22,5 reescalado ao Ke real de hoje", "R$", ""),
              ("graham_rev", "Graham revisado — LPA × (8,5 + 2g), reescalado ao Ke", "R$", ""),
              ("bazin6", "Bazin — DPA sustentável ÷ 6%", "R$", ""),
              ("teto_renda", "Teto de renda — DPA líquido ÷ rf líquida (valor presente)", "R$", ""),
              ("bogle_nom", "Bogle — retorno esperado em 10 anos (DY + g + re-rating)", "%", ""),
              ("peg", "Lynch — PEG (P/L ÷ crescimento nominal)", "x", ""),
              ("dy", "Dividend yield sustentável (valor presente)", "%", "")]
    for k, rot, un, obs in linhas:
        if k in r and (k in info):
            s.numeros.append(_num(rot, r[k], pr.de(t, *info[k]), un, "informativo", obs))
    centrais = [n for n in s.numeros if n.papel == "central"]
    s.numeros.append(_num("Valor central (mediana das âncoras, já com o desconto de controlador)", r["central"],
                          [o for n in centrais for o in n.origens]))
    return s


def secao_veredito(c: dict) -> Secao:
    r, t = c["r"], pr.tabela(c)
    centrais = [o for nome in r["ancoras"] for o in pr.de(t, *pr.ANCORA.get(nome, ()))]
    preco = t["preco"]
    s = Secao("Veredito")
    s.numeros += [
        _num("Preço", c["preco"], [preco]),
        _num("Valor central", r["central"], centrais),
        _num("Preço ÷ central (P/C)", r["pc"] if r["pc"] != float("inf") else None, centrais + [preco], "x"),
        _num("Compra (0,70 × central)", r.get("compra"), centrais),
        _num("1ª parcela, exceção de qualidade (0,80 × central)", r.get("compra_parcial"), centrais),
        _num(f"Saída ({'1,50' if r.get('saida_por_qualidade') else '1,30'} × central)", r.get("saida"), centrais),
        _num("Ke nominal (custo do acionista)", r.get("ke_nom_emp", r.get("ke")), [t["mercado"]], "%"),
        _num("Dispersão das âncoras (maior ÷ menor)", r["dispersao"] if r["dispersao"] != float("inf") else None,
             centrais, "x"),
    ]
    ke_imp = r.get("ke_implicito")
    s.numeros.append(_num("Ke implícito no preço (o retorno que o mercado aceita)", ke_imp, centrais + [preco], "%",
                          "informativo", "" if ke_imp is not None else "nem no Ke mínimo o modelo alcança o preço"))
    if c["financeira"]:
        s.numeros.append(_num("ROE implícito no preço", r.get("roe_implicito"),
                              pr.de(t, *pr.INFO_FIN["roe_implicito"]), "%", "informativo"))
    elif r.get("g_implicito") is not None:
        s.numeros.append(_num("g real implícito no preço", r["g_implicito"], centrais + [preco], "%", "informativo"))

    s.texto.append(f"Palavra: **{r['palavra']}** (régua pelo P/C: {r['palavra_regua']}; confiança: {r['confianca']}).")
    if r.get("trava") is not None:
        s.texto.append(f"Trava de coerência (Bogle a ±2 p.p. do Ke): {'passa' if r['trava'] else 'falha'}.")
    s.texto.append(f"Vence a renda fixa (Bogle líquido real ≥ rf líquida + 3 p.p.)? {r.get('vence_rf')}.")
    ok, motivos = entrada_parcial(r, getattr(c["empresa"], "fora_circulo", False), carimbos.de(c["tk"]))
    s.texto.append("Exceção da 1ª parcela a 0,80×: " + ("elegível (números e zero armadilhas registradas em `carimbos.py`)"
                                                       if ok else "não — " + "; ".join(motivos)) + ".")
    if not decide(pior(centrais)):
        s.avisos.append(f"O valor central depende de insumo com nota {pior(centrais)} (só A/B embasa decisão): "
                        + "; ".join(sorted({o.detalhe or o.fonte for o in centrais if not decide(o.nota)})) + ".")
    return s


def secao_sensibilidade(c: dict) -> Secao:
    r = c["r"]
    s = Secao("Sensibilidade do valor central")
    eixo2 = "ROE de LP" if c["financeira"] else "margem"
    sens = r.get("sens") or {}
    ks = sorted({k for k, _ in sens})
    ds = sorted({d for _, d in sens})
    if sens:
        cab = ["Ke \\ " + eixo2] + [f"{100 * d:+.0f} p.p." for d in ds]
        linhas = [[f"{100 * k:+.0f} p.p."] + [f"{sens[(k, d)]:.2f}".replace(".", ",") for d in ds] for k in ks]
        s.tabelas.append((f"Central (R$/ação) com Ke ±1 p.p. × {eixo2} ±2 p.p.", cab, linhas))
    return s
