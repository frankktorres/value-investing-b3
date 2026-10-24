"""Blocos qualitativos do relatório: MOAT, GESTÃO, DÍVIDA, GOVERNANÇA, DIVIDENDOS e RISCOS.

Nada é inventado nem recalculado: cada linha sai (1) do resultado do motor (`avaliar`: ROIC×WACC, Altman, Piotroski, Beneish,
Sloan, cobertura, DL/EBITDA), (2) da evidência do dossiê (`dossie/notas.py`, `evidencia.py`, insumos com fonte A/B), (3) do FRE
da CVM (`dossie/fre.py`, que nunca devolve CPF nem nome de pessoa física) ou (4) dos proventos da B3 (`base.proventos_b3`).
Ticker do hall sem dossiê (BBSE3): as notas 0–5 são as ARBITRADAS do lote (nota "—") e o relatório diz isso; o que o FRE e a
B3 dão por ticker entra do mesmo jeito. Texto livre só de `relatorio/textos/<TK>.json`, cada um com fonte A/B (senão `ValueError`).

Cortes das bandeiras de RISCOS: Beneish > −1,78 e dispersão > 1,8× vêm da doutrina (§8, §9); Altman usa a zona do motor; os
demais (Sloan, cobertura, DL/EBITDA, payout, ROIC×WACC, diluição, defasagem) são cortes DO RELATÓRIO, marcados "informativo —
corte do relatório" até passarem pelo `verificador-fonte`.
"""
from __future__ import annotations

import json
import pathlib

from relatorio import procedencia as pr
from relatorio.modelo import SEM_FONTE, Numero, Origem, Secao, decide, pior
from relatorio.render_md import fmt

TEXTOS = pathlib.Path(__file__).resolve().parent / "textos"
ANO_FRE = 2026
# CNPJ (FCA/FRE) e nome de pregão (NOMRES do COTAHIST = tradingName da B3) dos tickers do hall que têm relatório; os do
# dossiê vêm de `dossie.base`. Ticker fora das duas tabelas fica sem FRE e sem proventos da B3 (o bloco avisa).
# N11 (22/10/2026): CNPJ de `triagem/dados/triagem_2026-10-02.csv` (EGIE3 conferido no cadastro da CVM); pregão `None` = ainda não
# confirmado na API da B3 (tradingName) — a rede da nuvem barra b3.com.br (403), então não se grava palpite: o bloco de proventos
# avisa e o FRE já aparece. Confirmar na máquina do Frank: TAEE11 (TAESA?), ITUB4 (ITAUUNIBANCO?), EGIE3, SAPR11.
CADASTRO = {"BBSE3": ("17.344.597/0001-94", "BBSEGURIDADE"),
            "PETR4": ("33.000.167/0001-01", "PETROBRAS"),             # pregão de proventos_ex.PREGAO (usado no hall)
            "EGIE3": ("02.474.103/0001-19", None),
            "TAEE11": ("07.859.971/0001-30", None),
            "ITUB4": ("60.872.504/0001-23", None),
            "SAPR11": ("76.484.013/0001-45", None)}
CORTE_BENEISH, CORTE_SLOAN, CORTE_COBERTURA, CORTE_DL_EBITDA = -1.78, 0.10, 1.5, 3.0
CORTE_DISPERSAO, CORTE_DILUICAO, CORTE_DEFASAGEM = 1.8, 0.02, 12.0
INFO_CORTE = "informativo — corte do relatório (heurística do projeto, sem fonte)"


def _n(rot, valor, origens=(), unidade="", obs="", papel="informativo"):
    return Numero(rot, valor, unidade, tuple(origens), papel, obs)


def _pct(v):
    return fmt(v, "%")


def _cadastro(c: dict) -> tuple[str | None, str | None]:
    from dossie import base
    tk = c["tk"]
    if tk in base.CNPJ:
        return base.CNPJ[tk], base.PREGAO[tk]
    return CADASTRO.get(tk, (None, None))


def _o_fre(pacote: dict | None, tabela: str) -> Origem:
    f = (pacote or {}).get("fonte") or {}
    return Origem(f"CVM FRE {ANO_FRE}", "A", f"CVM, FRE {ANO_FRE} (id_doc {f.get('id_doc', '?')}, versão {f.get('versao', '?')}), "
                  f"tabela {tabela}, dados abertos", data=pr._iso(f.get("dt_refer")))   # N12: DT_REFER do formulário


def _o_ins(c: dict, *chaves: str) -> Origem:
    """Origem dos insumos não mecânicos do dossiê: a pior nota entre os pedidos (só A/B existe lá; sem insumo → "—")."""
    from dossie import gerar
    ins = gerar.insumos(c["tk"])
    notas = [ins[k]["nota_fonte"] for k in chaves if ins.get(k) and ins[k].get("nota_fonte")]
    return Origem("dossiê (insumo)", pior(Origem("x", n) for n in notas) if notas else SEM_FONTE,
                  f"dossie/insumos/{c['tk']}.json: {', '.join(chaves)} (cada um com fonte A/B escrita no arquivo)")


def _o_notas(c: dict) -> Origem:
    """Nota 0–5: regra 11 sobre evidência A (dossiê) ou a nota arbitrada do lote (sem fonte numérica)."""
    if c["dossie"] is not None:
        return _o_ins(c, "ma_ruim", "interferencias", "partes_rel_sobre_receita", "tag_along", "discricionario")
    return Origem("nota arbitrada (pré-v4)", SEM_FONTE, "nota 0–5 do QUAL do lote, arbitrada antes da regra 11 (02 v4); o "
                  "dossiê do ticker a substitui por nota com evidência")


def _nota_final(c: dict, chave: str):
    if c["dossie"] is not None:
        return c["dossie"]["final"][chave]
    return (c["empresa"].qualitativo or {}).get(chave)


def _componentes(c: dict, chave: str) -> list[str]:
    return list(c["dossie"]["base_n"][chave].componentes) if c["dossie"] is not None else []


def texto_extra(tk: str, bloco: str) -> tuple[str | None, Origem | None]:
    """Parágrafo opcional de `relatorio/textos/<TK>.json` (`{bloco: {valor, fonte, nota_fonte}}`); sem fonte A/B → ValueError."""
    arq = TEXTOS / f"{tk}.json"
    if not arq.exists():
        return None, None
    from dossie.gerar import _valor
    v, f = _valor(json.loads(arq.read_text(encoding="utf-8")), bloco)
    if v is None:
        return None, None
    nota = f[f.rfind("[") + 1:-1]
    return v, Origem(f"texto {tk}.json", nota, f)


def _fecha(s: Secao, c: dict, bloco: str) -> Secao:
    t, o = texto_extra(c["tk"], bloco)
    if t:
        s.numeros.append(_n("Comentário (relatorio/textos)", t, [o]))
    return s


def _tabela_anos(titulo: str, origem: Origem, cab: list[str], linhas: list[list[str]]):
    return (f"{titulo} — fonte: {origem.fonte}, nota {origem.nota}", cab, linhas)


# ---------------------------------------------------------------------------------------------------------------- MOAT
def _margens(c: dict) -> dict:
    if c["dossie"] is not None:
        return c["dossie"]["mg"]
    from dossie import evidencia as ev
    r = c["r"]
    return ev.margens(c["tk"], list(r["roic_serie"]), r["op"].get("med_outras"), True)


def secao_moat(c: dict) -> Secao:
    r, t, emp = c["r"], pr.tabela(c), c["empresa"]
    s = Secao("Vantagem competitiva (moat)")
    nota, on = _nota_final(c, "moat"), _o_notas(c)
    if c["financeira"]:
        spread = (emp.roe_lp - r["ke"]) if emp.roe_lp is not None and r.get("ke") is not None else None
        o_esc = pr.de(t, "roe_lp", "mercado")
        s.numeros += [
            _n("ROE de longo prazo (premissa do lote)", emp.roe_lp, pr.de(t, "roe_lp"), "%"),
            _n("ROE inicial (premissa do lote)", emp.roe_inicio, pr.de(t, "roe_inicio"), "%"),
            _n("Ke nominal", r.get("ke"), pr.de(t, "mercado"), "%"),
            _n("Spread ROE LP − Ke (o retorno acima do custo do acionista)", spread, o_esc, "%",
               "vantagem se positivo; sem série anual no motor de financeiras (informativo)"),
            _n("ROE implícito no preço", r.get("roe_implicito"), pr.de(t, *pr.INFO_FIN["roe_implicito"]), "%"),
        ]
        s.texto.append("Financeira: o moat por ROIC × WACC não se aplica (dívida é matéria-prima); a vista é ROE × Ke. Não há "
                       "série anual de ROE no motor de financeiras: os dois ROEs são escalares do lote.")
    else:
        serie, wacc = r["roic_serie"], r["wacc_real"]
        mg = _margens(c)
        o = t["serie"]
        linhas = [[a, _pct(v), _pct(wacc), _pct((mg.get(a) or {}).get("bruta")), _pct((mg.get(a) or {}).get("ebit"))]
                  for a, v in serie.items()]
        s.tabelas.append(_tabela_anos("ROIC real × WACC real e margens por exercício", o,
                                      ["Ano", "ROIC real", "WACC real", "Margem bruta", "Margem EBIT aj."], linhas))
        s.numeros += [
            _n("Exercícios com ROIC real > WACC real", f"{r['roic_anos_acima']} de {r['roic_anos_total']}", [o]),
            _n("WACC real", wacc, [o, *pr.de(t, "mercado")], "%"),
            _n("ROIC a custo de reposição (último)", r.get("roic_reposicao"), [o], "%"),
            _n("ROC de Greenblatt (EBIT ÷ capital tangível)", r.get("roc"), [o], "%", "ranking; não entra na nota"),
            _n("Earnings yield (EBIT ÷ EV)", r.get("ey"), [o, *pr.de(t, "preco")], "%", "ranking; não entra na nota"),
        ]
    s.numeros.append(_n("Nota de moat (0–5)", nota, [on], "", "; ".join(_componentes(c, "moat")) or "arbitrada no lote"))
    return _fecha(s, c, "moat")


# -------------------------------------------------------------------------------------------------------------- GESTÃO
def _remuneracao(c: dict):
    cnpj, _ = _cadastro(c)
    from dossie import fre
    if c["dossie"] is not None:
        return c["dossie"]["fr"]
    return fre.resumo(cnpj, ANO_FRE) if cnpj else None


def secao_gestao(c: dict) -> Secao:
    s = Secao("Gestão e alocação de capital")
    d, nota, on = c["dossie"], _nota_final(c, "gestao"), _o_notas(c)
    fr = _remuneracao(c)
    t = pr.tabela(c)
    if d is not None:
        r1 = d["r1"]
        s.numeros += [
            _n("R$ 1 retido → valor de mercado criado (Q4 da triagem)", r1 if r1 is not None else None, [t["serie"], t["preco"]],
               "R$", "≥ 1,5 bom; < 1,0 ruim" if r1 is not None else "não medido (ticker fora da triagem e sem insumo)"),
            _n("CAGR das ações em circulação", d["dil"], [t["acoes"]], "%", d["dil_txt"]),
            _n("Remuneração da administração ÷ lucro", d["rem_l"], [t["serie"], _o_fre(fr["remuneracao"], "remuneracao_total_orgao")],
               "%", d["rem_txt"]),
            _n("Aquisições prováveis (salto de intangível+investimentos > 20% do ativo)", ", ".join(d["mna"]) or "nenhuma", [t["serie"]]),
            _n("M&A destruidor de valor? (insumo do dossiê)", "sim" if "ma_ruim" in _ins_true(c) else "não",
               [_o_ins(c, "ma_ruim")], "", "evidência e conta no dossiê (insumos/%s.json)" % c["tk"]),
        ]
        fis = (_ins(c).get("fisher") or {}).get("respostas")
        if fis:
            s.numeros.append(_n("Fisher — respostas 'sim' de 15", f"{sum(x == 'sim' for x in fis)} de 15", [_o_ins(c, "fisher")],
                                "", f"nota {d['final']['fisher']}; {sum(x == 'sem' for x in fis)} sem evidência"))
    else:
        s.numeros.append(_n("Nota de gestão (0–5)", nota, [on], "", "arbitrada no lote (pré-v4)"))
        s.avisos.append("Ticker do hall sem dossiê: R$ 1 retido, diluição e M&A não foram medidos (precisam de ficha: CVM + FRE "
                        "+ insumos A/B).")
    if fr and fr.get("remuneracao"):
        rem = fr["remuneracao"]["dados"]
        o = _o_fre(fr["remuneracao"], "remuneracao_total_orgao")
        anos = sorted(rem)[-4:]
        s.tabelas.append(_tabela_anos(f"Remuneração total da administração (R$ mi; {anos[-1]} = prevista no FRE)", o,
                                      ["Exercício", "Total", "Diretoria", "Conselho adm.", "Conselho fiscal"],
                                      [[a, *[f"{(rem[a].get(k) or 0) / 1e6:,.1f}".replace(".", ",") for k in
                                             ("total", "Diretoria Estatutária", "Conselho de Administração", "Conselho Fiscal")]]
                                       for a in anos]))
    if d is not None:
        s.numeros.append(_n("Nota de gestão (0–5)", nota, [on], "", "; ".join(_componentes(c, "gestao"))))
    return _fecha(s, c, "gestao")


def _ins(c):
    from dossie import gerar
    return gerar.insumos(c["tk"])


def _ins_true(c):
    return [k for k in ("ma_ruim",) if (_ins(c).get(k) or {}).get("valor") is True]


# -------------------------------------------------------------------------------------------------------------- DÍVIDA
def secao_divida(c: dict) -> Secao:
    r, t = c["r"], pr.tabela(c)
    s = Secao("Endividamento e solidez")
    if c["financeira"]:
        s.texto.append("Não se aplica a financeira — a dívida é a matéria-prima do negócio. "
                       "Para seguradora a solidez é prudencial (índice de solvência), fora do motor.")
        n = r["notas"]["solidez"]
        s.numeros.append(_n("Nota de solidez (0–10) declarada", n, [Origem("nota declarada no lote", SEM_FONTE,
                       f"solidez_manual do lote: {c['empresa'].solidez_manual}; razão no texto da ficha, sem fonte numérica")],
                            "", "não se aplica a leitura de DL/EBITDA"))
        s.numeros.append(_n("Cobertura de caixa dos dividendos (lote)", "sim" if c["empresa"].cobertura_caixa else "não",
                            [pr.C_LOTE]))
        return _fecha(s, c, "divida")
    o = t["serie"]
    pi = Origem("Damodaran (ratings)", "B", "Damodaran, Ratings, Interest Coverage Ratios and Default Spread, jan/2026 (base do autor)")
    kd = r["kd_info"]
    s.numeros += [
        _n("Dívida bruta", r["bruta"], [o], "R$ mil", "balanço do último trimestre"),
        _n("Caixa e aplicações", r["caixa"], [o], "R$ mil"),
        _n("Dívida líquida", r["dl"], [o], "R$ mil"),
        _n("DL ÷ EBITDA (LTM)", r.get("dl_ebitda"), [o], "x", "sem dívida líquida positiva = sem alavancagem"),
        _n("DL ÷ EBITDA normalizado", r.get("dl_ebitda_norm"), [o], "x", "entra na nota de solidez"),
        _n("Cobertura de juros (EBIT ÷ juros)", r.get("cobertura_juros"), [o], "x", f"juros: {r.get('cobertura_fonte', '?')}"),
        _n("Altman Z'' (não financeiras)", r.get("altman"), [o], "", f"zona {r.get('altman_zona')}"),
        _n("Piotroski F (0–9)", r.get("piotroski"), [o], "", "exibido; não entra na nota (v2.6)"),
        _n("Beneish M", r.get("beneish"), [o], "", "> −1,78 = alerta (doutrina §8); exibido"),
        _n("Sloan — accruals ÷ ativo médio", r.get("sloan"), [o], "%", "qualidade do lucro; exibido"),
        _n("Custo da dívida Kd (nominal)", r["kd"], [pi if kd.get("origem") == "sintético" else o, *pr.de(t, "mercado")], "%",
           f"origem {kd.get('origem')}, rating sintético {kd.get('rating', '—')}"),
        _n("Peso da dívida no capital (D ÷ (D+E))", r.get("de_peso"), [o, t["preco"]], "%"),
        _n("Nota de solidez (0–10)", r["notas"]["solidez"], [o], "", "média de DL/EBITDA norm., cobertura e Altman (doutrina §10)"),
    ]
    return _fecha(s, c, "divida")


# ---------------------------------------------------------------------------------------------------------- GOVERNANÇA
def secao_governanca(c: dict) -> Secao:
    s = Secao("Governança e controlador")
    cnpj, _ = _cadastro(c)
    fr = _remuneracao(c)
    nota, on = _nota_final(c, "controlador"), _o_notas(c)
    if not fr:
        s.avisos.append("Sem FRE para este ticker: " + ("CNPJ não cadastrado em relatorio/quali.py (CADASTRO)." if not cnpj
                        else f"a CVM não tem FRE {ANO_FRE} para o CNPJ."))
        s.numeros.append(_n("Nota de controlador (0–5)", nota, [on], "", "arbitrada no lote (pré-v4)"))
        return _fecha(s, c, "governanca")
    ac = fr["acionistas"]
    o_ac, o_ff = _o_fre(ac, "posicao_acionaria"), _o_fre(fr["free_float"], "distribuicao_capital")
    tem = fr["tem_controlador"]
    s.numeros.append(_n("Tem acionista controlador (FRE)?", {True: "sim", False: "não", None: "FRE sem 1º nível"}[tem], [o_ac]))
    linhas = [[a["acionista"], f"{a['pct_total']:.2f}%".replace(".", ",") if a["pct_total"] is not None else "—",
               "controlador" if a["controlador"] else "", "acordo de acionistas" if a["acordo"] else ""] for a in ac["dados"][:6]]
    if linhas:
        s.tabelas.append(_tabela_anos("Acionistas de 1º nível (pessoa física anonimizada)", o_ac,
                                      ["Acionista", "% do capital", "Papel", "Acordo"], linhas))
    ff = (fr["free_float"] or {}).get("dados") or {}
    if ff:
        s.numeros += [
            _n("Ações em circulação (free float, FRE)", (ff["pct_total_circulacao"] or 0) / 100, [o_ff], "%"),
            _n("Acionistas pessoa física / jurídica / institucionais", f"{ff['n_pf']:,.0f} / {ff['n_pj']:,.0f} / "
               f"{ff['n_institucionais']:,.0f}".replace(",", "."), [o_ff]),
        ]
    adm = (fr["administradores"] or {}).get("dados", {}).get("resumo") or {}
    o_adm = _o_fre(fr["administradores"], "administrador_membro_conselho_fiscal")
    if adm:
        n_tot = sum(v["n"] for v in adm.values())
        n_ctl = sum(v["eleitos_controlador"] for v in adm.values())
        s.numeros.append(_n("Administradores e fiscais eleitos pelo controlador", f"{n_ctl} de {n_tot}", [o_adm], "",
                            "; ".join(f"{k}: {v['eleitos_controlador']}/{v['n']}" for k, v in adm.items())))
    pt = fr["partes_relacionadas"]
    o_pt = _o_fre(pt, "transacao_parte_relacionada")
    tot = sum(p["montante"] or 0 for p in pt["dados"])
    obs = "bruto: o montante do FRE é o valor do contrato, não o fluxo do ano (pista, não nota)"
    if c["dossie"] is not None and c["dossie"]["pr_bruto"] is not None:
        s.numeros.append(_n("Partes relacionadas ÷ receita (FRE, bruto)", c["dossie"]["pr_bruto"], [o_pt, pr.tabela(c)["serie"]],
                            "%", f"{c['dossie']['pr_txt']}; {obs}"))
    else:
        s.numeros.append(_n("Transações com partes relacionadas (FRE)", f"{len(pt['dados'])} — montante bruto "
                            f"{fmt(tot / 1e3, 'R$ mil')}", [o_pt], "", obs))
    rf = fr["relacao_familiar"]
    if rf is not None:
        s.numeros.append(_n("Vínculos familiares entre administradores e pessoas ligadas ao emissor", f"{len(rf['dados'])}",
                            [_o_fre(rf, "relacao_familiar")]))
    if c["dossie"] is not None:
        d = c["dossie"]
        tag, tag_o = _tag_along(c)
        s.numeros += [
            _n("Tag along", tag, [tag_o], "%" if isinstance(tag, float) else "", "estatuto social (o FRE não traz a tabela)"),
            _n("Controle discricionário sobre capital e payout? (peso 2 na média, §10)", "sim" if d["disc"] else "não",
               [_o_ins(c, "discricionario")]),
        ]
    dc = (c["dossie"] or {}).get("dc") or c["empresa"].desconto_controlador or {}
    s.numeros.append(_n("Desconto de controlador no valor central", c["r"].get("desc_controlador") or 0.0,
                        [Origem("premissa de julgamento", SEM_FONTE, "desconto declarado na ficha/insumo (§5 da doutrina)")],
                        "%", f"{dc.get('tipo', 'zero')}: {(dc.get('razao') or 'sem razão documentada').strip()}"))
    s.numeros.append(_n("Nota de controlador (0–5)", nota, [on], "", "; ".join(_componentes(c, "controlador")) or "arbitrada no lote"))
    return _fecha(s, c, "governanca")


def _tag_along(c: dict):
    ins = _ins(c).get("tag_along")
    if ins and ins.get("valor") is not None:
        return ins["valor"], _o_ins(c, "tag_along")
    return None, _o_ins(c, "tag_along")


# ------------------------------------------------------------------------------------------------------------ DIVIDENDOS
def _proventos(c: dict):
    """(DPA por ano, JCP por ano, motivo) da B3 — vazio se o ticker não tem nome de pregão cadastrado. Não financeira do hall
    e dossiê: o coletor do hall (`proventos_hall`, o mesmo DPA que o motor lê — classe certa, parcelas somadas, eventos B3 +
    FRE; no dossiê, data-com até a data do veredito). Financeira: a regra antiga (`base.proventos_b3_legado`) até a fatia 4."""
    import proventos_hall
    from dossie import base
    if _regra_do_hall(c):
        try:
            d, j = proventos_hall.dpa_jcp(c["tk"], c["data"] if c["dossie"] is not None else None)
            return d, j, ""
        except Exception as ex:  # noqa: BLE001 — falha do dado vira aviso, nunca número inventado
            return {}, {}, f"proventos da B3 indisponíveis: {type(ex).__name__}: {ex}"
    cnpj, pregao = _cadastro(c)
    if not pregao:
        return {}, {}, "nome de pregão não cadastrado ou ainda não conferido na API da B3 (CADASTRO em relatorio/quali.py)"
    tk, inserido = c["tk"], False
    if tk not in base.PREGAO:
        base.PREGAO[tk], inserido = pregao, True
    try:
        d, j = base.proventos_b3_legado(tk)
        return d, j, ""
    except Exception as ex:  # noqa: BLE001 — qualquer falha do dado vira aviso, nunca número inventado
        return {}, {}, f"proventos da B3 indisponíveis: {type(ex).__name__}: {ex}"
    finally:
        if inserido:
            base.PREGAO.pop(tk, None)


def _regra_do_hall(c: dict) -> bool:
    import proventos_hall
    return c["tk"] in proventos_hall.NF_HALL or c["dossie"] is not None


def secao_dividendos(c: dict) -> Secao:
    r, t, emp = c["r"], pr.tabela(c), c["empresa"]
    s = Secao("Dividendos e JCP")
    dpa, jcp, motivo = _proventos(c)
    ano_corrente = c["data"][:4]
    import proventos_hall
    o_b3 = (proventos_hall.origem_b3(c["tk"]) if _regra_do_hall(c) else
            Origem("B3 proventos", "A", "B3, proventos em dinheiro por data-com (API pública), R$ por ação de hoje na classe "
                   "do ticker (regra anterior à fase 3: linha igual conta uma vez)"))
    if dpa:
        # ano civil sem provento conta como zero (proventos_b3 só devolve anos com pagamento); começa no 1º ano com dado
        ini = max(int(min(dpa)), int(ano_corrente) - 10)
        anos = [str(a) for a in range(ini, int(ano_corrente))]
        dpa = {**{a: 0.0 for a in anos}, **dpa}
        linhas = [[a, fmt(dpa[a], "R$"), fmt(jcp.get(a, 0.0), "R$"), _pct(jcp.get(a, 0.0) / dpa[a]) if dpa[a] else "—"] for a in anos]
        if ano_corrente in dpa:
            linhas.append([f"{ano_corrente} (parcial)", fmt(dpa[ano_corrente], "R$"), fmt(jcp.get(ano_corrente, 0.0), "R$"),
                           _pct(jcp.get(ano_corrente, 0.0) / dpa[ano_corrente]) if dpa[ano_corrente] else "—"])
        s.tabelas.append(_tabela_anos("Proventos por exercício (data-com)", o_b3, ["Ano", "DPA total", "dos quais JCP", "% JCP"], linhas))
        pagos = sum(1 for a in anos if dpa[a] > 0)
        s.numeros += [
            _n("Exercícios completos com provento (últimos 10)", f"{pagos} de {len(anos)}", [o_b3]),
            _n("DPA médio dos últimos 5 exercícios completos", sum(dpa[a] for a in anos[-5:]) / len(anos[-5:]) if anos else None,
               [o_b3], "R$"),
        ]
    else:
        s.avisos.append(f"Série de proventos da B3 não disponível: {motivo}. Valores abaixo são os do motor.")
    if c["financeira"]:
        o = pr.de(t, "dpa_medio_5a")
        s.numeros += [
            _n("DPA sustentável (menor entre a média 5a e o FCFE)", r["dpa_sust"], o, "R$"),
            _n("Payout (premissa do lote)", emp.payout, pr.de(t, "payout"), "%"),
            _n("Exercícios com provento nos últimos 10 (lote)", emp.anos_pagos_10, o, "", "entra na nota de renda"),
        ]
    else:
        o = pr.de(t, "proventos", "serie", "acoes")
        pay = r["dpa_sust"] / r["lpa_norm"] if r.get("lpa_norm") and r["lpa_norm"] > 0 else None
        s.numeros += [
            _n("DPA sustentável (menor entre a média 5a e o FCFE)", r["dpa_sust"], o, "R$"),
            _n("FCFE por ação", r.get("fcfe_acao"), pr.de(t, "serie", "acoes"), "R$"),
            _n("Provento coberto pelo FCFE?", "sim" if r.get("coberto") else "não", pr.de(t, "serie", "proventos", "acoes")),
            _n("Payout sustentável (DPA sust. ÷ LPA normalizado)", pay, o, "%", "acima de 100% distribui mais do que ganha"),
        ]
    ref = pr.INFO_FIN if c["financeira"] else pr.INFO_NF
    for k, rot, un in (("dy", "Dividend yield sustentável (valor presente)", "%"), ("bazin6", "Teto de Bazin (DPA ÷ 6%)", "R$"),
                       ("teto_renda", "Teto de renda (DPA líquido ÷ rf líquida)", "R$")):
        if k in ref and r.get(k) is not None:
            s.numeros.append(_n(rot, r[k], pr.de(t, *ref[k]), un))
    s.numeros.append(_n("Defasagem do pagamento (meses)", r.get("defasagem_meses"), pr.de(t, "defasagem"), "",
                        "desconta o dividendo a valor presente (§6.3); data de pagamento é StatusInvest (C)"))
    return _fecha(s, c, "dividendos")


# ---------------------------------------------------------------------------------------------------------------- RISCOS
def centrais_o(t: dict, r: dict) -> list[Origem]:
    return [x for nome in r["ancoras"] for x in pr.de(t, *pr.ANCORA.get(nome, ()))]


def secao_riscos(c: dict) -> Secao:
    r, t, emp, fin = c["r"], pr.tabela(c), c["empresa"], c["financeira"]
    s = Secao("Riscos e bandeiras")
    flags: list[tuple[str, Numero]] = []

    def teste(rot, valor, origens, disparou, corte, unidade="", doutrina=False):
        sit = "DISPARA" if disparou else "ok"
        base = "corte da doutrina" if doutrina else INFO_CORTE
        n = _n(rot, valor, origens, unidade, f"{sit}" + (f" — {corte}" if corte else "") + f"; {base}")
        s.numeros.append(n)
        if disparou:
            flags.append((rot, n))

    o = t.get("serie")
    if not fin:
        teste("Altman Z'' fora da zona segura", r.get("altman"), [o], r.get("altman_zona") != "segura",
              f"zona {r.get('altman_zona')}", doutrina=True)
        teste("Beneish M acima de −1,78", r.get("beneish"), [o], r.get("beneish") is not None and r["beneish"] > CORTE_BENEISH,
              "alerta de manipulação > −1,78", doutrina=True)
        teste("Accruals de Sloan altos (|Sloan| > 10% do ativo)", r.get("sloan"), [o],
              r.get("sloan") is not None and abs(r["sloan"]) > CORTE_SLOAN, "lucro muito acima/abaixo do caixa", "%")
        teste("Cobertura de juros abaixo de 1,5×", r.get("cobertura_juros"), [o],
              r.get("cobertura_juros") is not None and r["cobertura_juros"] < CORTE_COBERTURA, "EBIT ÷ juros", "x")
        dle = r.get("dl_ebitda_norm")
        teste("DL ÷ EBITDA normalizado acima de 3×", dle, [o], dle is None or dle > CORTE_DL_EBITDA,
              "indefinido conta como disparo" if dle is None else "alavancagem", "x")
        total = r.get("roic_anos_total") or 0
        teste("ROIC real < WACC real na maioria dos exercícios", f"{r.get('roic_anos_acima')} de {total} acima", [o],
              total > 0 and r["roic_anos_acima"] < total / 2, "menos da metade dos anos acima do WACC")
        pay = r["dpa_sust"] / r["lpa_norm"] if r.get("lpa_norm") and r["lpa_norm"] > 0 else None
        teste("Payout sustentável acima de 100%", pay, pr.de(t, "proventos", "serie", "acoes"), (pay is not None and pay > 1) or (pay is None and r["dpa_sust"] > 0 and r.get("lpa_norm") is not None
                                                  and r["lpa_norm"] <= 0),
              "prejuízo normalizado com dividendo conta como disparo" if pay is None else "", "%")
        if c["dossie"] is not None and c["dossie"]["dil"] is not None:
            teste("Diluição: CAGR das ações ≥ 2% a.a.", c["dossie"]["dil"], [t["acoes"]], c["dossie"]["dil"] >= CORTE_DILUICAO,
                  "regra da nota de gestão (notas.gestao)", "%", doutrina=True)
    else:
        pay = emp.payout
        teste("Payout acima de 100%", pay, pr.de(t, "payout"), (pay is not None and pay > 1) or (pay is None and r["dpa_sust"] > 0 and r.get("lpa_norm") is not None
                                                  and r["lpa_norm"] <= 0),
              "prejuízo normalizado com dividendo conta como disparo" if pay is None else "", "%")
        teste("ROE de longo prazo abaixo do Ke", (emp.roe_lp - r["ke"]) if emp.roe_lp is not None else None,
              pr.de(t, "roe_lp", "mercado"), emp.roe_lp is not None and emp.roe_lp < r["ke"], "spread negativo destrói valor", "%")
        if emp.horizonte_finito:
            h = emp.horizonte_finito
            teste("Contrato com prazo: renovação é premissa arbitrada", f"{h['anos']} anos; renovação {h['prob_renovacao']:.0%}; "
                  f"haircut {h['haircut_renov']:.0%}", pr.de(t, "horizonte_finito"), True, "central depende de insumo sem fonte (AUD-58)")
    disp = r.get("dispersao")
    teste("Dispersão das âncoras acima de 1,8×", disp if disp != float("inf") else None, centrais_o(t, r) or [o], disp is None or disp > CORTE_DISPERSAO or disp == float("inf"),
          "desce um nível na régua; > 3× = não conclusivo", "x", doutrina=True)
    teste("Âncora única (menos de 2 âncoras calculáveis)", len(r["ancoras"]), centrais_o(t, r) or [o], len(r["ancoras"]) < 2,
          "confiança baixa (§11)", "", doutrina=True)
    d = r.get("defasagem_meses")
    teste("Defasagem do provento ≥ 12 meses", d, pr.de(t, "defasagem"), d is not None and d >= CORTE_DEFASAGEM, "")
    teste("Não vence a renda fixa (Bogle líquido real < rf líquida + 3 p.p.)", r.get("vence_rf"), pr.de(t, "mercado"),
          r.get("vence_rf") == "Não", "carimbo do §9" if r.get("carimbo_rf") else "", "", doutrina=True)
    if r.get("trava") is not None:
        teste("Trava de coerência (Bogle a ±2 p.p. do Ke) falha", "passa" if r["trava"] else "falha", pr.de(t, "mercado"),
              not r["trava"], "§9", "", doutrina=True)
    centrais = centrais_o(t, r)
    ruim = pior(centrais) if centrais else SEM_FONTE
    teste("Valor central depende de insumo C ou sem fonte", ruim, centrais or [Origem("sem âncora", SEM_FONTE, "nenhuma âncora")],
          not decide(ruim), "só A/B embasa decisão (doutrina §2)", doutrina=True)
    if c["dossie"] is not None:
        n = c["dossie"]["final"]["ciclo"]
        s.numeros.append(_n("Nota de ciclo (0–5)", n, [_o_notas(c)], "", "; ".join(_componentes(c, "ciclo"))))
    if flags:
        s.texto.append(f"**{len(flags)} bandeira(s) disparada(s):** " + "; ".join(f"{rot} ({fmt(n.valor, n.unidade)})" for rot, n in flags)
                       + ".")
    else:
        s.texto.append("Nenhuma bandeira disparada.")
    return _fecha(s, c, "riscos")


def secoes(c: dict) -> list[Secao]:
    return [secao_moat(c), secao_gestao(c), secao_divida(c), secao_governanca(c), secao_dividendos(c), secao_riscos(c)]
