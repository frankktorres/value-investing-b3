"""PDF do Lote 5 (Petróleo, gás e combustíveis) — doutrina v2.5. Uso: python gerar_pdf_lote5.py"""
from ltm import ltm_de
import copy
import pathlib
import sys
from statistics import median

import matplotlib.pyplot as plt
from historico_arquivos import guardar
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle

import re

import gerar_pdf_lote1  # registra as fontes Arial
from gerar_pdf_lote1 import AZUL, br, COR, grafico_resumo, img, LINHA, nota_f2, pct, tabela, texto_entrada_parcial

_P = gerar_pdf_lote1.P


def P(t, st="cel"):
    """Escapa '&' solto (E&P, D&A) para o parser do reportlab; vale também dentro de tabela()."""
    return _P(re.sub(r"&(?!amp;|lt;|gt;|#)", "&amp;", t) if isinstance(t, str) else t, st)


gerar_pdf_lote1.P = P
from lote1_bancos import DATA_BASE, MK
from lote5_petroleo import (EMPRESAS, FATOR_BARRIL, FORA_DO_HALL, FX_SPOT, M, PETR_ABANDONO, PETR_ATUARIAL, PETR_CENARIOS)
from lote5_textos import AGENDA, ANTES, T
from motor_nao_financeiras import CVM, SI, avaliar, estrutura_de_capital, valores

sys.stdout.reconfigure(encoding="utf-8")
REV = "09-10-2026"
SAIDA = pathlib.Path(__file__).parent.parent / "PETROLEO E GÁS" / f"Petroleo_Gas_rev_{REV}.pdf"
EP = ("PETR4", "PRIO3", "RECV3")
CAPTURA = 0.70     # fração da receita incremental (preço) que vira EBIT — royalties, participação especial e custos atrelados a preço (HIPÓTESE)
IMPOSTO_EXPORT = 0.12


def desc_de(emp):
    dc = emp.desconto_controlador
    return (dc.get("pct", 0.0) if dc["tipo"] == "fixo" else
            sum(c["prob"] * c["perda"] for c in dc["cenarios"]) if dc["tipo"] == "cenarios" else 0.0)


def central_rapido(emp):
    # v2.4 (AUD-12/13): a sensibilidade usa a MESMA base do central publicado — Ke da empresa e pesos no ponto fixo, refeitos
    # para a variante (antes: Ke de 5 p.p. e pesos a preço, não comparável ao central)
    ec = estrutura_de_capital(emp, MK)
    r = valores(emp, ec["mk"], e_peso=ec["e_peso"])
    return median(r["anc"].values()) * (1 - desc_de(emp))


def central_nopat(emp, r, nopat, divida_extra=0.0):
    """Central com outro NOPAT normalizado, g = 0 (como no caso base: ROIC < WACC em todas): EPV e DCF movem juntos (o DCF mantém a
    distância de cenários p25/p75 do caso base); reprodução e Owner Earnings não mudam."""
    epv = (nopat / r["wacc_real"] - r["dl"] - r["minor"] - divida_extra) / r["n"]
    dcf = epv + (r["dcf_pond"] - r["dcf"]["base"])
    terc = r["reprod"] if emp.perfil == "ciclica" else (r["oe_val"] - divida_extra / r["n"] if r["oe_val"] else None)
    return median([x for x in (epv, dcf, terc) if x is not None]) * (1 - desc_de(emp))


def nopat_brent(r, brent, fx=FX_SPOT):
    R = r["op"]["receita_meio"]
    rs = R * brent * fx / M["barril_meio"]
    return (R * (r["m"] + r["op"]["ajuste_manut"]) + CAPTURA * (rs - R)) * (1 - r["aliquota"])


def extras(emp, r):
    a, ltm = CVM[emp.ticker]["anual"], ltm_de(CVM[emp.ticker])
    x = {}
    x["pl_ltm"] = emp.preco / (ltm["lucro"] / r["n"]) if ltm.get("lucro") and ltm["lucro"] > 0 else None
    tk = emp.ticker
    if tk in EP:
        x["brent"] = {b: central_nopat(emp, r, nopat_brent(r, b)) for b in (60, 70, 90, 100, 114)}
        x["brent_eq"] = M["barril_meio"] / FX_SPOT
    if tk == "PETR4":
        x["abandono"] = central_nopat(emp, r, r["nopat"], PETR_ABANDONO * (1 - 0.34))
        e2 = copy.deepcopy(emp)
        e2.desconto_controlador = {"tipo": "zero", "razao": ""}
        x["sem_desc"] = central_rapido(e2)
        e3 = copy.deepcopy(emp)
        e3.da_receita = None
        x["regra_ebit"] = central_rapido(e3)
        x["imp_rec"] = r["op"]["impairment_recorrente"]
        e4 = copy.deepcopy(emp)
        e4.outros_passivos = PETR_ATUARIAL
        e4.outros_passivos_fonte = "déficit atuarial (sensibilidade; o custo atuarial já está no EBIT)"
        x["com_atuarial"] = central_rapido(e4)
    if tk == "PRIO3":
        R = r["op"]["receita_meio"]
        x["imposto"] = central_nopat(emp, r, r["nopat"] - IMPOSTO_EXPORT * R * (1 - r["aliquota"]))
        x["vol187"] = central_nopat(emp, r, r["nopat"] * 187 / 172)
        e3 = copy.deepcopy(emp)
        e3.da_receita, e3.anos_ciclo, e3.outras_liquidas = None, [str(y) for y in range(2016, 2026)], False
        e3.receita_meio = ltm["receita"] * FATOR_BARRIL
        x["regra_ebit"] = central_rapido(e3)
    if tk == "RECV3":
        e2 = copy.deepcopy(emp)
        e2.g_real = 0.0
        x["g0"] = central_rapido(e2)
        x["por_metodo"] = {k: (emp.preco / val if val > 0 else None) for k, val in r["ancoras"].items()}
    if emp.deflator:
        ebit_ltm = ltm["ebit"]
        x["ebit_ltm"] = ebit_ltm
        x["ebit_meio"] = r["op"]["receita_meio"] * r["m"]
        x["guerra"] = central_nopat(emp, r, (ebit_ltm + r["op"]["receita_meio"] * r["op"]["ajuste_manut"]) * (1 - r["aliquota"]))
    if r["trava"] is None:
        x["trava_txt"] = "não se aplica (palavra não é JUSTA)."
    elif r["trava"]:
        x["trava_txt"] = f"passa — Bogle {pct(r['bogle_nom'])} a ±2 p.p. do Ke nominal {pct(r["ke_nom_emp"])}."
    else:
        bog_meio = r["lpa_norm"] / emp.preco + r["g_nom"]
        ok = abs(bog_meio - r["ke_nom_emp"]) <= 0.02
        x["trava_txt"] = (f"falha pelo Bogle de dividendos ({pct(r['bogle_nom'])} vs Ke {pct(r["ke_nom_emp"])}): o DPA de 5 anos (R$ {br(r['dpa5'])}) "
                          f"vem de 2021–25, com Brent médio acima do meio de ciclo e os extraordinários de 2022. Com o lucro de meio de ciclo "
                          f"inteiro distribuído (LPA R$ {br(r['lpa_norm'])}) o retorno é {pct(bog_meio)} — "
                          + ("passa: dentro de ±2 p.p. do Ke." if ok else "ainda fora de ±2 p.p."))
    return x


def preencher(s, emp, r, x):
    gi = r["g_implicito"]
    g_txt = ("não alcançável — com ROIC abaixo do WACC crescer não cria valor" if gi is None else ("≤ −5%" if gi <= -0.05 else pct(gi)))
    rep = {"compra": br(r["compra"]), "ke_impl": pct(r["ke_implicito"]) if r["ke_implicito"] else "n.d.", "g_impl": g_txt,
           "central": br(r["central"]), "pc": br(r["pc"]), "m50": pct(r["op"]["m50"]), "m25": pct(r["op"]["m25"]), "m75": pct(r["op"]["m75"]),
           "piotroski": str(r["piotroski"]), "beneish": br(r["beneish"]) if r["beneish"] is not None else "n.d.",
           "dl_ebitda": br(r["dl_ebitda"]), "dl_ebitda_norm": br(r["dl_ebitda_norm"]), "dy_liq": pct(r["dy_liq"]),
           "dcf_pess": br(r["dcf"]["pessimista"] * (1 - r["desc_controlador"])), "aliquota": pct(r["aliquota"], 0), "altman": br(r["altman"]),
           "altman_zona": r["altman_zona"], "cobertura": br(r["cobertura_juros"], 1) if r["cobertura_juros"] else "n.d.",
           "sens_m_mais": br(r["sens"][(0, 0.02)]), "sens_m_menos": br(r["sens"][(0, -0.02)]), "dispersao": br(r["dispersao"]),
           "roc": pct(r["roc"]), "ey": pct(r["ey"]), "trava_txt": x["trava_txt"], "roic": pct(r["roic"]), "wacc": pct(r["wacc"]),
           "pl_ltm": br(x["pl_ltm"], 1) if x["pl_ltm"] else "n.d.", "reprod": br(r["reprod"]), "palavra": r["palavra"],
           "epv": br(r["ancoras"].get("EPV de meio de ciclo", r["ancoras"].get("EPV", 0))), "dl_bi": br(r["dl"] / 1e6, 1),
           "desc": pct(r["desc_controlador"], 0), "saida": br(r["saida"]), "rec_meio": br(r["op"]["receita_meio"] / 1e6, 1),
           "nopat": br(r["nopat"] / 1e6, 2), "dpa5": br(r["dpa5"]), "fcfe": br(r["fcfe_acao"]), "lpa_norm": br(r["lpa_norm"]),
           "barril": br(M["barril_meio"], 0), "brent_eq": br(M["barril_meio"] / FX_SPOT, 0), "aj_txt": pct(-r["op"]["ajuste_manut"]) + " da receita",
           "da_pct": pct(emp.da_receita) if emp.da_receita is not None else "n.d."}
    for k in ("abandono", "sem_desc", "regra_ebit", "imposto", "vol187", "g0", "guerra", "com_atuarial"):
        if k in x:
            rep[k] = br(x[k])
    if "brent" in x:
        for b, val in x["brent"].items():
            rep[f"b{b}"] = br(val)
    if "imp_rec" in x:
        rep["imp_rec"] = pct(x["imp_rec"])
    if "ebit_ltm" in x:
        rep["ebit_ltm"] = br(x["ebit_ltm"] / 1e6, 2)
        rep["ebit_meio"] = br(x["ebit_meio"] / 1e6, 2)
    for k, val in rep.items():
        s = s.replace("{" + k + "}", val)
    assert "{" not in s, s
    return s


def grafico_margem(emp, r):
    a = CVM[emp.ticker]["anual"]
    anos = r["op"]["anos"]
    fig, ax = plt.subplots(figsize=(3.6, 1.9))
    if emp.da_receita is not None:
        mg = [100 * (a[y]["ebit"] + a[y]["da"] - (a[y].get("impairment") or 0)) / a[y]["receita"] for y in anos]
        ax.bar(anos, mg, color="#8DA9C4", width=0.7)
        ebitda_med = r["op"]["m50"] + emp.da_receita + r["op"]["impairment_recorrente"]
        ax.axhline(100 * ebitda_med, color="#1F3A5F", lw=1, ls="--", label=f"EBITDA mediano {pct(ebitda_med)}")
        ax.axhline(100 * r["op"]["m50"], color="#B83232", lw=1, label=f"− D&A atual − impairment recorrente = {pct(r['op']['m50'])}")
        ax.set_title(f"{emp.ticker} — margem EBITDA sem impairment (%) [CVM]", fontsize=7.5)
    elif emp.deflator:
        ex = [a[y]["ebit"] * emp.deflator[y] / 1e6 for y in anos]
        ax.bar(anos, ex, color="#8DA9C4", width=0.7)
        med = r["op"]["receita_meio"] * r["op"]["m50"] / 1e6
        ax.axhline(med, color="#1F3A5F", lw=1, ls="--", label=f"mediana R$ {br(med, 2)} bi (sem não recorrentes)")
        ax.set_title(f"{emp.ticker} — EBIT em R$ bi de ago/2026 (IPCA) [CVM]", fontsize=7.5)
    else:
        ax.bar(anos, [100 * a[y]["ebit"] / a[y]["receita"] for y in anos], color="#8DA9C4", width=0.7)
        ax.axhline(100 * r["op"]["m50"], color="#1F3A5F", lw=1, ls="--", label=f"mediana {pct(r['op']['m50'])}")
    ax.tick_params(labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=60)
    ax.legend(fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=1, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return img(fig, 82)


def ficha(emp, r, rank, story):
    x = extras(emp, r)
    tx = {k: ([preencher(i, emp, r, x) for i in val] if isinstance(val, list) else preencher(val, emp, r, x)) for k, val in T[emp.ticker].items()}
    palavra = r["palavra"]
    nc = palavra == "NÃO CONCLUSIVO"
    cor = COR.get(palavra, AZUL)
    fora = " · FORA DO HALL" if emp.ticker in FORA_DO_HALL else ""
    perfil = {"ciclica": "cíclica (E&P)", "servicos": "distribuição (serviços, receita indexada a commodity)"}[emp.perfil]
    cab = Table([[P(f"<font name='Arial-B' size=14 color='#1F3A5F'>{emp.ticker}</font>  <font size=9>{emp.nome} · {perfil}{fora}</font>", "p"),
                  P(f"<font name='Arial-B' size=12 color='white'>{palavra}</font><font size=7 color='white'> · confiança {r['confianca']}</font>", "p")]],
                colWidths=[120 * mm, 60 * mm], rowHeights=[11 * mm])
    cab.setStyle(TableStyle([("BACKGROUND", (1, 0), (1, 0), cor), ("ALIGN", (1, 0), (1, 0), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (0, 0), 1.2, AZUL)]))
    story.append(cab)
    story.append(Spacer(1, 3))
    kpi = [["Preço 02/10", "Valor central", "P/C", "Compra 0,70×", "Saída 1,30×", "Ke implícito", "Vence a RF?", "Nota geral"],
           [f"R$ {br(emp.preco)}", ("n.a." if r["central"] <= 0 else f"R$ {br(r['central'])}" + (" (mediana)" if nc else "")),
            "n.a." if r["central"] <= 0 else br(r["pc"]) + "×",
            "n.a." if nc else f"R$ {br(r['compra'])}", "n.a." if nc else f"R$ {br(r['saida'])}",
            pct(r["ke_implicito"]) if r["ke_implicito"] else "n.d.", r["vence_rf"] + (" (só com re-rating)" if r["so_com_rerating"] else ""),
            br(r["notas"]["geral"], 1)]]
    story.append(tabela(kpi, [22.5 * mm] * 8, extra=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Círculo de competência.</b> {tx['circulo']}", "p"))
    story.append(Spacer(1, 3))
    ltm = ltm_de(CVM[emp.ticker])
    fatos = [["Fato (12m até jun/2026)", "Valor", "Fonte"],
             ["Receita · EBIT · margem", f"R$ {br(ltm['receita'] / 1e6, 1)} bi · {br(ltm['ebit'] / 1e6, 2)} bi · {pct(ltm['ebit'] / ltm['receita'])}", "[CVM]"]]
    if emp.ticker in EP:
        base = "1S26 anualizado" if emp.ticker == "PRIO3" else "12m"
        fatos += [["Receita de meio de ciclo (barril R$ " + br(M["barril_meio"], 0) + ")", f"R$ {br(r['op']['receita_meio'] / 1e6, 1)} bi (base {base})", "[CVM][BCB][EIA]"],
                  ["Margem de meio de ciclo (p25 · p75)", f"{pct(r['op']['m50'])} ({pct(r['op']['m25'])} · {pct(r['op']['m75'])}) = EBITDA mediano − D&A atual "
                   f"{pct(emp.da_receita)}" + (f" − impairment recorrente {pct(r['op']['impairment_recorrente'])}" if r["op"]["impairment_recorrente"] else ""),
                   f"[CVM] {r['op']['anos'][0]}–{r['op']['anos'][-1]}"]]
    else:
        fatos += [["EBIT normalizado (R$ de hoje)", f"R$ {br(r['op']['receita_meio'] * r['m'] / 1e6, 2)} bi (mediana real {r['op']['anos'][0]}–{r['op']['anos'][-1]}; "
                   f"12m: R$ {br(ltm['ebit'] / 1e6, 2)} bi)", "[CVM][IBGE]"]]
    fatos += [["Ajuste capex de manutenção", pct(r["op"]["ajuste_manut"]) + " da receita (capex mediano acima da D&A)", "[CVM] 10a"],
              ["Dívida líquida · DL/EBITDA 12m · normalizado", f"R$ {br(r['dl'] / 1e6, 1)} bi · {br(r['dl_ebitda'])}× · {br(r['dl_ebitda_norm'])}×", "[CVM] 30/06/2026"],
              ["ROIC normalizado · WACC", f"{pct(r['roic'])} contábil · {pct(r['roic_reposicao'])} a custo de reposição "
                f"(imobilizado de {r['idade_imobilizado']:.1f} anos corrigido pelo IPCA) · WACC {pct(r['wacc'])} "
                f"(Kd {pct(r['kd'])}; IR efetivo {pct(r['aliquota'], 0)}). O menor decide o filtro 1, a nota e a trava do crescimento", "motor"],
              ["P/L 12m · P/VP", f"{br(x['pl_ltm'], 1) if x['pl_ltm'] else 'n.d.'}× · {br(emp.preco / r['vpa'])}×", "[CVM]"]]
    if emp.outros_passivos:
        fatos.append(["Outros passivos na ponte", emp.outros_passivos_fonte, "[CVM]"])
    lado = Table([[tabela(fatos, [38 * mm, 44 * mm, 15 * mm]), grafico_margem(emp, r)]], colWidths=[98 * mm, 84 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)

    story.append(P("Quadro clássico (doutrina §11) — ao Ke da casa", "h3"))
    lin = [["Método", "Valor", "Marca", "Fórmula / insumos"]]
    ponte = "dívida líquida − minoritários" + (" − déficit atuarial" if emp.outros_passivos else "")
    dtxt = f" × (1 − desconto de controlador {pct(r['desc_controlador'], 0)})" if r["desc_controlador"] else ""
    for k, val in r["ancoras"].items():
        if k.startswith("EPV"):
            f = f"NOPAT normalizado R$ {br(r['nopat'] / 1e6, 2)} bi ÷ WACC real {pct(r['wacc_real'])} − {ponte}{dtxt}"
        elif k.startswith("DCF"):
            d = r["dcf"]
            k_ = 1 - r["desc_controlador"]
            f = (f"FCFF = NOPAT × (1+g) × (1 − g/ROIC), g real {pct(r['gr'], 0)} (zerado se ROIC < WACC; declínio não libera capital); "
                 f"margem p25/mediana/p75 = R$ {br(d['pessimista'] * k_)} / {br(d['base'] * k_)} / {br(d['otimista'] * k_)}, pesos 25/50/25")
        elif k.startswith("Valor de repro"):
            f = emp.reproducao_fonte + dtxt
        else:
            f = f"Owner Earnings mediano R$ {br(r['oe_norm'] / 1e6, 2)} bi ÷ (Ke real − g real)"
        lin.append([k, f"R$ {br(val)}", "ÂNCORA", f])
    oe_txt = ", ".join(f"{a_}: {br(v_ / 1e6, 2)}" for a_, v_ in r["oe"][-5:])
    ac_pc = ltm["ac"] / ltm["pc"]
    a = CVM[emp.ticker]["anual"]
    anos = [y for y in map(str, range(2016, 2026)) if a.get(y, {}).get("receita")]
    luc_pos = all(a[y]["lucro"] > 0 for y in anos)
    cres = a[anos[-1]]["lucro"] / a[anos[0]]["lucro"] - 1 if a[anos[0]]["lucro"] > 0 else None
    pl_n = r["pl_atual"]
    f = MK.fator_graham
    crit = [("porte > R$ 10 bi", r["e"] > 1e7), (f"liquidez corrente {br(ac_pc)} ≥ 2", ac_pc >= 2), (f"lucro positivo desde {anos[0]}", luc_pos),
            (f"lucro +1/3 na série ({pct(cres, 0) if cres is not None else 'n.d.'})", cres is not None and cres >= 1 / 3),
            (f"P/L normalizado {br(pl_n, 1) if pl_n else 'n.d.'} ≤ {br(15 * f, 1)}", bool(pl_n) and pl_n <= 15 * f),
            (f"P/L × P/VP ≤ {br(22.5 * f, 1)}", bool(pl_n) and pl_n * emp.preco / r["vpa"] <= 22.5 * f)]
    lin += [
        ["Lucro normalizado (próprio)", f"LPA R$ {br(r['lpa_norm'])}", "INFORMATIVO",
         "meio de ciclo: (NOPAT normalizado − juros líquidos após IR, Kd da casa) ÷ ações. Consenso 3 anos: não encontrado no material"],
        ["Owner Earnings por ano (R$ bi)", oe_txt or "n.d.", "INFORMATIVO", "lucro + D&A − capex de manutenção − aumento de capital de giro [CVM]"],
        ["Graham original · Graham-BR", f"R$ {br(r['graham_orig'])} · {br(r['graham_br'])}" if r["graham_orig"] else "n.d.", "INFORMATIVO",
         f"√(22,5 × LPA normalizado × VPA {br(r['vpa'])}); f = {br(f, 3)}"],
        ["Graham revisado-BR", f"R$ {br(r['graham_rev'])}" if r["graham_rev"] else "n.d.", "INFORMATIVO", f"LPA normalizado × (8,5 + 2 × g real {br(100 * r['gr'], 0)}) × f"],
        ["7 critérios do defensivo", f"{sum(1 for _, ok in crit if ok)} de 6", "INFORMATIVO",
         "; ".join(("[sim] " if ok else "[não] ") + n for n, ok in crit) + "; dividendos 20 anos: série de 10"],
        ["Teto de renda (Bazin calibrado)", f"R$ {br(r['teto_renda'])}" if r["teto_renda"] else "N/A", "INFORMATIVO",
         "DPA sustentável líquido ÷ RF nominal líquida" + ("" if r["coberto"] else " — N/A: dividendo médio acima do FCFE normalizado")],
        ["Bazin original (6%)", f"R$ {br(r['bazin6'])}" if r["bazin6"] else "N/A", "INFORMATIVO", "DPA sustentável ÷ 6%"],
        ["Lynch", f"PEG {br(r['peg'])} · PEGY {br(r['pegy'])}" if r["peg"] else "n.d.", "INFORMATIVO",
         f"categoria: {'cíclica' if emp.perfil == 'ciclica' else 'crescimento lento'}; P/L normalizado ÷ g nominal {pct(r['g_nom'])} — PEG não se aplica (Lynch)"],
        ["Greenblatt (Fórmula Mágica)", f"EY {pct(r['ey'])} · ROC {pct(r['roc'])}", "INFORMATIVO",
         f"EBIT 12m ÷ EV; EBIT ÷ (capital de giro + imobilizado). Posição no lote: {rank}º de {len(EMPRESAS)} — EBIT 12m é de topo (Brent e margem de guerra)"],
        ["DCF reverso", f"g real {('≤ −5%' if r['g_implicito'] <= -0.05 else pct(r['g_implicito'])) if r['g_implicito'] is not None else 'n.a. (ROIC < WACC)'} · "
                        f"Ke {pct(r['ke_implicito']) if r['ke_implicito'] else 'n.d.'}", "INFORMATIVO",
         "crescimento real perpétuo que o preço exige (margem mediana, Ke da casa); e o Ke que o preço embute"],
        ["Bogle (10 anos)", f"{pct(r['bogle_nom'])} nominal", "INFORMATIVO",
         f"DY sustentável {pct(r['dy'])} + g nominal {pct(r['g_nom'])} + múltiplo {pct(r['dmult'])} · real líquido {pct(r['bogle_liq_real'])}"
         + " · sem re-rating (lucro dominado por Brent e margem de guerra)"],
        ["Altman Z'' (emergentes) · Piotroski · Beneish · Sloan",
         f"{br(r['altman'])} ({r['altman_zona']}) · {r['piotroski']}/9 · {br(r['beneish']) if r['beneish'] is not None else 'n.d.'} · {pct(r['sloan'])}",
         "INFORMATIVO", f"exercício {r['ano_qualidade']} vs anterior [CVM]; Beneish > −1,78 = alerta; Sloan alto e positivo = lucro acima do caixa"],
    ]
    story.append(tabela(lin, [33 * mm, 29 * mm, 21 * mm, 99 * mm]))
    story.append(PageBreak())

    story.append(P(f"{emp.ticker} — reconstrução, sensibilidade e veredito", "h2"))
    rec = [["Âncora", "Valor", "Peso"]] + [[k, f"R$ {br(val)}", "mediana"] for k, val in r["ancoras"].items()]
    sem_central = nc and r["central"] <= 0
    rec.append(["<b>Valor central</b>", "<b>n.a.</b>" if sem_central else f"<b>R$ {br(r['central'])}</b>",
                "âncora ≤ 0" if sem_central else f"dispersão {br(r['dispersao'])}× · {r['confianca']}"])
    if nc:
        rec += [[f"Preço ÷ {k}", (br(v_) + "×") if v_ else "n.a. (âncora ≤ 0)", "margem por método"] for k, v_ in x["por_metodo"].items()]
    ts = [["Central (R$)", "margem −2 p.p.", "margem base", "margem +2 p.p."]]
    for dk, nome in ((-0.01, "Ke −1 p.p. (prêmio de Ke)"), (0, "Ke da casa"), (0.01, "Ke +1 p.p. (prêmio de Ke)")):
        ts.append([nome] + [br(r["sens"][(dk, dm)]) for dm in (-0.02, 0, 0.02)])
    lado = Table([[tabela(rec, [40 * mm, 20 * mm, 30 * mm]), tabela(ts, [24 * mm, 20 * mm, 20 * mm, 20 * mm])]], colWidths=[92 * mm, 90 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)
    story.append(Spacer(1, 3))
    if "brent" in x:
        cab_b = ["Central (R$) a Brent spot, câmbio R$ " + br(FX_SPOT, 3)] + [f"US$ {b}" for b in x["brent"]] + [f"meio (≈US$ {br(x['brent_eq'], 0)})"]
        story.append(tabela([cab_b, ["valor central"] + [br(v_) for v_ in x["brent"].values()] + [br(r["central"])]],
                            [52 * mm] + [21.6 * mm] * 6))
        story.append(P(f"Sensibilidade ao Brent permanente: {pct(CAPTURA, 0)} da receita incremental vira EBIT (royalties, participação especial e "
                       "custos atrelados ao preço — HIPÓTESE), g = 0. Não é cenário de valor: o central usa o barril de meio de ciclo.", "pi"))
        story.append(Spacer(1, 2))
    story.append(P(f"<b>Controlador.</b> {tx['controlador']}", "p"))
    if emp.desconto_controlador["tipo"] == "cenarios":
        story.append(tabela([["Cenário de interferência", "Probabilidade", "Perda de valor", "Contribuição"]] +
                            [[c["nome"], pct(c["prob"], 0), pct(c["perda"], 0), pct(c["prob"] * c["perda"], 1)] for c in PETR_CENARIOS] +
                            [["<b>Desconto aplicado uma única vez (em cenários, não no Ke)</b>", "", "", f"<b>{pct(r['desc_controlador'], 1)}</b>"]],
                            [118 * mm, 20 * mm, 22 * mm, 22 * mm]))
    story.append(Spacer(1, 3))
    dpa, jc = SI[emp.ticker]["dpa_por_ano_datacom"], SI[emp.ticker]["jcp_por_ano_datacom"]
    yrs = list(range(2021, 2027))
    story.append(tabela([["Proventos por data-com [SI]"] + [str(y) if y < 2026 else "2026 até 02/10" for y in yrs],
                         ["DPA total (R$)"] + [br(dpa.get(str(y), 0), 3) for y in yrs],
                         ["dos quais JCP (R$)"] + [br(jc.get(str(y), 0), 3) for y in yrs]], [38 * mm] + [24 * mm] * 6))
    story.append(Spacer(1, 2))
    story.append(tabela([["Renda e renda fixa (10 anos, líquido de IR)", "Valor"],
                         ["DPA médio 5a · FCFE normalizado por ação · sustentável", f"R$ {br(r['dpa5'], 3)} · R$ {br(r['fcfe_acao'], 3)} · R$ {br(r['dpa_sust'], 3)}"],
                         ["Coberto por caixa?", "Sim" if r["coberto"] else "Não — o dividendo médio supera o FCFE normalizado"],
                         ["Yield sustentável bruto · líquido", f"{pct(r['dy'])} · {pct(r['dy_liq'])}"],
                         ["Retorno esperado real líquido (Bogle) · sem re-rating", f"{pct(r['bogle_liq_real'])} · {pct(r['so_inv_liq_real'])}"],
                         ["RF real líquida", f"{pct(MK.rf_liq_real, 2)} → Sim ≥ {pct(MK.rf_liq_real + .03, 2)} · Empate ≥ {pct(MK.rf_liq_real + .015, 2)}"],
                         ["Vence a RF?", r["vence_rf"] + (" — só com re-rating; sem: " + r["rf_sem_rerating"] if r["so_com_rerating"] else "")],
                         ["Trava de coerência: JUSTA → retorno ≈ Ke", x["trava_txt"]]],
                        [95 * mm, 87 * mm]))
    story.append(Spacer(1, 3))
    n = r["notas"]
    preco_txt = ("Sem palavra: uma âncora é ≤ 0 ou as âncoras discordam mais de 3× (doutrina §11.3) — ver a margem por método acima. "
                 if nc else f"Compra R$ {br(r['compra'])} · justo R$ {br(r['central'])} · saída R$ {br(r['saida'])}. " + nota_f2(r))
    pc_txt = "sem central (âncora ≤ 0)" if r["central"] <= 0 else f"preço {br(r['pc'])}× o central"
    ver = Table([[P(f"<b>Veredito: <font color='{cor.hexval()}'>{palavra}</font></b>{fora} — {pc_txt}. {preco_txt}"
                    f"Entrada parcial (exceção §9): {texto_entrada_parcial(r, emp)}.<br/>"
                    f"<b>Gatilho que invalida:</b> {tx['gatilho']}<br/><b>Compraria para renda?</b> {tx['renda']}<br/>"
                    f"<b>Compraria para ganho de capital?</b> {tx['capital']}<br/>"
                    f"<b>Notas</b> (30/20/25/25): qualidade {br(n['qualidade'], 1)} · solidez {br(n['solidez'], 1)} · renda {br(n['renda'], 1)} · "
                    f"preço {br(n['preco'], 1)} → <b>{br(n['geral'], 1)}</b>", "box")]], colWidths=[182 * mm])
    ver.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, cor), ("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5),
                             ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.append(ver)
    story.append(Spacer(1, 3))
    sa = Table([[P("<b>3 números que sustentam</b><br/>" + "<br/>".join("• " + i for i in tx["sustentam"]), "cel"),
                 P("<b>3 números que ameaçam</b><br/>" + "<br/>".join("• " + i for i in tx["ameacam"]), "cel")]], colWidths=[91 * mm, 91 * mm])
    sa.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.3, LINHA)]))
    story.append(sa)
    story.append(Spacer(1, 3))
    an = ANTES[emp.ticker]
    story.append(P(f"<b>De → para (rev. 03/10 → hoje).</b> {an[0]}, central R$ {br(an[1])} → {palavra}, central R$ {br(r['central'])}. "
                   f"{tx['de_para']} Preço inalterado (R$ {br(emp.preco)}, fechamento de 02/10).", "p"))
    story.append(P("<b>Autocrítica (5 linhas).</b> " + " ".join(f"{i + 1}) {t}" for i, t in enumerate(tx["autocritica"])), "p"))
    story.append(P(f"<b>Eventos com data.</b> {AGENDA}.", "p"))
    story.append(P(f"<b>Não encontrado.</b> {tx['nao_encontrado']}", "pi"))
    story.append(PageBreak())


def tabela_barril():
    an = M["anual"]
    lin = [["Ano", "Brent US$/bbl", "PTAX R$/US$", "Barril R$ nominal", "Barril R$ de " + M["base"], "Brent em US$ de " + M["base"]]]
    for y in range(2016, 2026):
        lin.append([str(y), br(an.loc[y, "brent"], 1), br(an.loc[y, "ptax"], 3), br(an.loc[y, "rs"], 0), br(an.loc[y, "rs_real"], 0), br(an.loc[y, "us_real"], 1)])
    lin.append(["<b>Média 2016–25 = meio de ciclo</b>", br(M["brent_meio_nominal"], 1), "", "", f"<b>{br(M['barril_meio'], 0)}</b>",
                f"{br(M['brent_meio_real'], 1)} (câmbio real {br(M['fx_meio_real'], 2)})"])
    lin.append(["12m até jun/2026 (base E&P)", br(M["brent_ltm"], 1), br(M["ptax_ltm"], 3), br(M["barril_ltm"], 0), "", ""])
    lin.append([f"Spot (Brent {M['brent_ultimo'][0]}; câmbio 02/10)", br(M["brent_ultimo"][1], 1), br(FX_SPOT, 3), br(M["brent_ultimo"][1] * FX_SPOT, 0), "", ""])
    return tabela(lin, [52 * mm, 24 * mm, 22 * mm, 26 * mm, 28 * mm, 30 * mm])


def capa(res, rank, story):
    story.append(P("Fichas de Avaliação — Value Investing B3", "h1"))
    story.append(P(f"Lote 5 — Petróleo, gás e combustíveis (5 empresas) · rev. 09/10/2026 · data-base {DATA_BASE} · doutrina v2.5", "h2"))
    cont = {}
    for r in res:
        cont[r["palavra"]] = cont.get(r["palavra"], 0) + 1
    resumo = " · ".join(f"{k}: {v}" for k, v in sorted(cont.items()))
    box = (f"<b>Conclusão.</b> Ao Ke da casa ({pct(MK.ke_nom)} nominal) e com o barril de meio de ciclo declarado antes do veredito "
           f"(R$ {br(M['barril_meio'], 0)}/bbl = média de 10 anos do Brent em reais de hoje; ≈ US$ {br(M['barril_meio'] / FX_SPOT, 0)} ao câmbio de 02/10, "
           f"contra US$ {br(M['brent_ultimo'][1], 0)} no spot), o lote fica: <b>{resumo}</b>. <b>Nenhuma compra autorizada.</b> "
           + " · ".join(f"{p}: {', '.join(r['ticker'] for r in res if r['palavra'] == p)}" for p in ("RADAR", "JUSTA", "CARA", "NÃO CONCLUSIVO")
                        if any(r["palavra"] == p for r in res))
           + ". O preço de hoje já paga o Brent de guerra (E&P) e a margem de distribuição de guerra (UGPA3, VBBR3) como se fossem permanentes. "
             "VBBR3 é calculada mas fica fora do hall (redundante com UGPA3).")
    tb = Table([[P(box, "box")]], colWidths=[182 * mm])
    tb.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, AZUL), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF3F9")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(tb)
    story.append(P("Quadro-resumo", "h3"))
    q = [["Ticker", "Palavra", "Preço", "Central", "P/C", "Compra", "Saída", "Ke implícito", "ROIC × WACC", "Greenblatt", "Vence RF", "Nota", "03/10"]]
    for r in sorted(res, key=lambda z: z["pc"]):
        an = ANTES[r["ticker"]]
        nc = r["palavra"] == "NÃO CONCLUSIVO"
        q.append([r["ticker"] + ("†" if r["ticker"] in FORA_DO_HALL else ""), f"<font color='{COR.get(r['palavra'], AZUL).hexval()}'><b>{r['palavra']}</b></font>",
                  br(r["preco_"]), "≤ 0" if r["central"] <= 0 else br(r["central"]), "n.a." if r["central"] <= 0 else br(r["pc"]),
                  "n.a." if nc else br(r["compra"]), "n.a." if nc else br(r["saida"]),
                  pct(r["ke_implicito"]) if r["ke_implicito"] else "n.d.", f"{pct(r['roic'], 0)} × {pct(r['wacc'], 0)}",
                  f"{rank[r['ticker']]}º", r["vence_rf"] + ("*" if r["so_com_rerating"] else ""), br(r["notas"]["geral"], 1), f"{an[0]} {br(an[1])}"])
    story.append(tabela(q, [13 * mm, 18 * mm, 12 * mm, 13 * mm, 10 * mm, 12 * mm, 12 * mm, 15 * mm, 18 * mm, 14 * mm, 12 * mm, 9 * mm, 24 * mm]))
    story.append(Spacer(1, 4))
    story.append(grafico_resumo([dict(r, pc=min(r["pc"], 2.8)) for r in res]))
    story.append(P("Greenblatt = posição no lote pela soma dos rankings de EY (EBIT 12m ÷ EV) e ROC — com EBIT de topo de ciclo, só informativo. "
                   "* vence só com re-rating. † fora do hall. NÃO CONCLUSIVO: sem preço de compra; P/C limitado a 2,8 no gráfico.", "pi"))
    story.append(PageBreak())
    story.append(P("Premissa de ciclo declarada antes do veredito — o barril de meio de ciclo", "h2"))
    story.append(tabela_barril())
    story.append(P("Brent: EIA (série DCOILBRENTEU via FRED); PTAX média mensal: BCB SGS 3698; IPCA: BCB SGS 433 (IBGE); CPI-EUA: BLS via FRED "
                   "(out/2025 sem divulgação — interpolado). Médias mensais. O barril de meio de ciclo em reais de hoje decompõe-se em Brent real de "
                   f"US$ {br(M['brent_meio_real'], 1)} × câmbio real de R$ {br(M['fx_meio_real'], 2)}. A rev. 03/10 usava Brent US$ 70 sem câmbio "
                   f"declarado (≈ R$ {br(70 * FX_SPOT, 0)}/bbl ao câmbio de 02/10) — a média nominal de 10 anos (US$ {br(M['brent_meio_nominal'], 1)}) "
                   "ignora a inflação do dólar.", "pi"))
    story.append(P("Metodologia (o que é novo em relação aos Lotes 1–3)", "h2"))
    met = [["Item", "Regra"],
           ["Dados", "Demonstrações consolidadas da CVM (DFP 2016–25 + ITR; 12m até jun/2026) — fonte A. Preço: fechamento de 02/10 (PDF rev. 03/10). "
                     "Ações: composição do capital na CVM. Proventos: StatusInvest. Contas: ferramentas/motor_nao_financeiras.py + lote5_petroleo.py."],
           ["E&P: receita", "Receita do período-base × barril de meio ÷ barril do período (volume atual a preço de meio de ciclo). Base = 12m até jun/2026; "
                            "PRIO3 = 1T26 e 2T26 anualizados, cada um pelo seu barril (Peregrino consolidado no meio dos 12m)."],
           ["E&P: margem", "EBITDA sem impairment, mediana de 10 anos (RECV3 2020–25; PRIO3 2019–25, desde Frade) − D&A atual (exaustão do portfólio de hoje, "
                           "inclusive reservas compradas) ÷ receita de meio − impairment mediano de 10 anos se for perda recorrente (PETR4: baixa em 9 de 10 anos). "
                           "PRIO3: ganhos de compra vantajosa (3.04.05) saem como não recorrentes."],
           ["Distribuição: margem", "Receita indexada ao preço do combustível: a margem % cai quando o diesel sobe e o EBIT por m³ não muda. Normaliza-se o EBIT "
                                    "em R$ de hoje (IPCA), mediana do perímetro comparável (UGPA3 2021–25, sem Oxiteno/Extrafarma; VBBR3 2020–25, gestão "
                                    "privada). VBBR3: créditos tributários lançados em 3.04.05 (2020, 2023, 2024) saem como não recorrentes. Perfil serviços "
                                    "(DCF, EPV, Owner Earnings), capex de manutenção pela regra de commodity."],
           ["Dívida e ponte", "Dívida bruta inclui arrendamentos (IFRS 16; FPSOs afretados da Petrobras). Déficit atuarial fora da ponte: o custo atuarial "
                              "já é despesa no EBIT (Petrobras: R$ 9,7 bi em 2025, DFC 6.01.01.02) — capitalizado, equivale ao déficit. Provisão de abandono "
                              "fora da ponte (custo capitalizado e depreciado na D&A, que está no EBIT). Os dois aparecem como sensibilidade na PETR4."],
           ["Não recorrentes", "PETR4, PRIO3 e VBBR3 lançam ganhos (venda de ativos, compra vantajosa, créditos tributários) em 3.04.05: usa-se 3.04.04 + "
                               "3.04.05 sem o impairment; o que passa da mediana de 10 anos (em % da receita) sai do EBIT. PETR4: desinvestimentos de 2019–22."],
           ["Controlador", "PETR4: desconto em cenários ponderados (8%), nunca no Ke. Demais: zero, com a razão escrita. Imposto de exportação (12%) é risco "
                           "regulatório: sensibilidade, não desconto."],
           ["Crescimento", "Só com ROIC > WACC (nenhuma das cinco). Declínio (RECV3, −3% real) reduz o fluxo e não libera capital."],
           ["WACC e notas", f"Ke da casa {pct(MK.ke_nom, 2)}; Kd = rf nominal + spread declarado (1,5–2,5 p.p.); pesos a mercado. Notas como nos Lotes 1–3."]]
    story.append(tabela(met, [32 * mm, 150 * mm]))
    story.append(PageBreak())


def main():
    res = []
    for e in EMPRESAS:
        r = avaliar(e, MK)
        r["preco_"] = e.preco
        res.append(r)
    ey = sorted(res, key=lambda z: -(z["ey"] or 0))
    roc = sorted(res, key=lambda z: -(z["roc"] or 0))
    soma = {r["ticker"]: ey.index(r) + roc.index(r) for r in res}
    rank = {tk: i + 1 for i, (tk, _) in enumerate(sorted(soma.items(), key=lambda kv: kv[1]))}
    guardar(SAIDA, "pdf lote 5")      # AUD-84: o PDF anterior do mesmo nome vai para _historico/
    doc = SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=14 * mm,
                            title=f"Lote 5 — Petróleo, gás e combustíveis · rev. {REV.replace('-', '/')}", author="Mesa de Value Investing")

    def rodape(c, d):
        c.saveState()
        c.setFont("Arial", 6.5)
        c.setFillColor(colors.HexColor("#6B7280"))
        c.drawString(15 * mm, 9 * mm, f"Mesa de Value Investing — Lote 5 Petróleo, gás e combustíveis · rev. 09/10/2026 · data-base {DATA_BASE} · "
                                      "doutrina v2.5 · não é recomendação de investimento")
        c.drawRightString(195 * mm, 9 * mm, f"p. {d.page}")
        c.restoreState()

    story = []
    capa(res, rank, story)
    for i in sorted(range(len(EMPRESAS)), key=lambda k: res[k]["pc"]):
        ficha(EMPRESAS[i], res[i], rank[EMPRESAS[i].ticker], story)
    story.append(P("Apêndice — fontes", "h2"))
    story.append(tabela([["Rótulo", "Fonte"],
                         ["[CVM]", "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/ e /ITR/DADOS/ (cache em ferramentas/dados/cvm)"],
                         ["[SI]", "https://statusinvest.com.br (proventos por data-com) — 05/10/2026"],
                         ["[EIA] [BCB] [IBGE]", "fred.stlouisfed.org/series/DCOILBRENTEU e CPIAUCSL; api.bcb.gov.br SGS 3698 (PTAX) e 433 (IPCA) — ferramentas/dados/macro"],
                         ["Mercado", "Tesouro Transparente (IPCA+ 2050 sem cupom 7,06%), ANBIMA ETTJ (inflação implícita 6,46%) — o mesmo dos Lotes 1–3"],
                         ["PDF 06/09 · 03/10", "Fichas anteriores (pasta PETROLEO E GÁS): produção, política de preços, subvenção, imposto de exportação, cenários "
                                               "da PETR4, agenda — fontes primárias citadas lá; extraídas em ferramentas/dados/fatos_lote5.json"]],
                        [30 * mm, 152 * mm]))
    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    print("gerado:", SAIDA)
    for r in sorted(res, key=lambda z: z["pc"]):
        print(r["ticker"], r["palavra"], round(r["central"], 2), round(r["pc"], 2), "rank", rank[r["ticker"]])


if __name__ == "__main__":
    main()
