"""PDF do Lote 6 (Química e metalurgia) — doutrina v2.5. Uso: python gerar_pdf_lote6.py"""
from ltm import ltm_de
from inflacao import DEFLATOR
import copy
import pathlib
import re
import sys
from statistics import median

import matplotlib.pyplot as plt
from historico_arquivos import guardar
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle

import gerar_pdf_lote1  # registra as fontes Arial
from gerar_pdf_lote1 import AZUL, br, COR, grafico_resumo, grafico_roe, img, LINHA, nota_f2, pct, tabela, texto_entrada_parcial

_P = gerar_pdf_lote1.P


def P(t, st="cel"):
    """Escapa '&' solto (D&A) para o parser do reportlab; vale também dentro de tabela()."""
    return _P(re.sub(r"&(?!amp;|lt;|gt;|#)", "&amp;", t) if isinstance(t, str) else t, st)


gerar_pdf_lote1.P = P
from lote1_bancos import DATA_BASE, MK
from lote2_energia import alavancagem, metodo_regulado
from lote6_quimica import (ACO, CLORO, EGIE, EGIE_DADOS, EGIE_DIV_AGO26, EGIE_FOLLOW_ON, EMPRESAS, N, PVC, SERIES, SODA)
from lote6_textos import AGENDA, ANTES, T
from motor_financeiras import avaliar as avaliar_fin
from motor_financeiras import projecao
from motor_nao_financeiras import CVM, SI, altman_z2, avaliar, beneish, ebit_aj, estrutura_de_capital, piotroski, sloan, valores

sys.stdout.reconfigure(encoding="utf-8")
REV = "09-10-2026"
SAIDA = pathlib.Path(__file__).parent.parent / "QUÍMICA E METALÚRGIA" / f"Quimica_Metalurgia_rev_{REV}.pdf"
INDICE = {"GGBR4": ACO, "UNIP6": CLORO}
NOME_IDX = {"GGBR4": "aço (BLS WPU1017)", "UNIP6": "cesta 50% soda (BLS PCU3251803251804) + 50% resinas termoplásticas (BLS WPU0662)"}


def desc_de(emp):
    dc = emp.desconto_controlador
    return (dc.get("pct", 0.0) if dc["tipo"] == "fixo" else
            sum(c["prob"] * c["perda"] for c in dc["cenarios"]) if dc["tipo"] == "cenarios" else 0.0)


def central_rapido(emp, **kw):
    # v2.4 (AUD-12/13): a sensibilidade usa a MESMA base do central publicado — Ke da empresa e pesos no ponto fixo, refeitos
    # para a variante (antes: Ke de 5 p.p. e pesos a preço, não comparável ao central)
    ec = estrutura_de_capital(emp, MK)
    r = valores(emp, ec["mk"], e_peso=ec["e_peso"], **kw)
    return median(r["anc"].values()) * (1 - desc_de(emp))


def com(emp, **campos):
    e = copy.deepcopy(emp)
    for k, val in campos.items():
        setattr(e, k, val)
    return e


def margem_ano(emp, r, y):
    a = CVM[emp.ticker]["anual"][y]
    return ebit_aj(a, r["op"]["med_outras"], emp.outras_liquidas) / a["receita"]


def extras(emp, r):
    tk = emp.ticker
    a, ltm = CVM[tk]["anual"], ltm_de(CVM[tk])
    x = {"pl_ltm": emp.preco / (ltm["lucro_controlador"] / r["n"]) if ltm.get("lucro_controlador", 0) > 0 else None,
         "pvp": emp.preco / r["vpa"], "ebit_ltm": ltm["ebit"] - ((ltm.get("impairment") or 0) if emp.impairment_normalizado else 0), "ebit_meio": r["op"]["receita_meio"] * r["m"],
         "div_bruta": (ltm.get("emprest_cp") or 0) + (ltm.get("emprest_lp") or 0)}
    # preço ÷ cada âncora: a ficha NÃO CONCLUSIVO mostra (antes só a UNIP6; o EGIE3 passou a NC com a trava da v2.4)
    x["por_metodo"] = {k: (emp.preco / val if val > 0 else None) for k, val in r["ancoras"].items()}
    if tk in INDICE:
        ix = INDICE[tk]
        rec12 = ltm["receita"]
        # receita a outro nível de preço com a MESMA margem % (sem alavancagem operacional — conservador para cima e para baixo)
        x["preco_idx"] = {lv: central_rapido(com(emp, receita_meio=rec12 * ix["fator"] * lv / 100)) for lv in (70, 80, 90, 110, 120)}
        x["p12m"] = central_rapido(com(emp, receita_meio=rec12))
        x["p_ult"] = central_rapido(com(emp, receita_meio=rec12 * ix["fator"] * ix["ultimo"][1] / 100))
        x["idx12m"], x["idx_ult"], x["fator"] = ix["ltm"], ix["ultimo"][1], ix["fator"]
    if tk == "UNIP6":
        x["div25"], x["lucro25"] = a["2025"]["dividendos_pagos"], a["2025"]["lucro_controlador"]
        x["div22"] = (a["2022"].get("emprest_cp") or 0) + (a["2022"].get("emprest_lp") or 0)
        m3 = median(margem_ano(emp, r, y) for y in ("2023", "2024", "2025"))
        x["m3a"], x["c3a"] = m3, central_rapido(emp, margem=m3)
        s = 1.0                         # quanto a receita de meio precisa cair para as âncoras ficarem abaixo de 3× (e a palavra voltar)
        while s > 0.5:
            s -= 0.005
            rr = avaliar(com(emp, receita_meio=emp.receita_meio * s), MK)
            if rr["dispersao"] <= 3:
                break
        x["corte"], x["palavra_corte"], x["pc_corte"] = 1 - s, rr["palavra"], rr["pc"]
    if tk == "LEVE3":
        x["m_ltm"] = ltm["ebit"] / ltm["receita"]
        x["c_ltm"] = central_rapido(emp, margem=x["m_ltm"])
        x["div21"] = (a["2021"].get("emprest_cp") or 0) + (a["2021"].get("emprest_lp") or 0)
        x["g0"] = central_rapido(com(emp, g_real=0.0))
        x["c34"] = central_rapido(com(emp, aliquota=0.34))
        dpa = SI[tk]["dpa_por_ano_datacom"]
        # em R$ de hoje, como o dpa5 do motor (AUD-16); o extraordinário de R$ 5,54 é de 2023 (adversário, 08/10/2026)
        x["dpa_sem_extra"] = (sum(dpa.get(str(y), 0) * DEFLATOR[str(y)] for y in range(2021, 2026)) - 5.54 * DEFLATOR["2023"]) / 5
        a5 = [str(y) for y in range(2021, 2026)]
        luc_med = median(a[y]["lucro"] * DEFLATOR[y] for y in a5)   # R$ de hoje, como o oe_norm (AUD-16)
        lucro_norm = r["lpa_norm"] * r["n"]
        oe_alt = r["oe_norm"] - (luc_med - lucro_norm)
        anc = dict(r["ancoras"])
        anc["Owner Earnings ÷ (Ke − g)"] = r["oe_val"] * oe_alt / r["oe_norm"]
        x["oe_alt"], x["c_oe"] = anc["Owner Earnings ÷ (Ke − g)"], median(anc.values())
    if r["trava"] is None:     # v2.4 (AUD-08): trava falha numa JUSTA pela régua vira NÃO CONCLUSIVO — o texto tem de dizer
        x["trava_txt"] = "não se aplica (palavra pela régua não é JUSTA)."
    elif r["trava"]:
        x["trava_txt"] = f"passa — Bogle {pct(r['bogle_nom'])} a ±2 p.p. do Ke nominal {pct(r["ke_nom_emp"])}."
    else:
        reinv = r["gr"] / r["roic"] if r["roic"] and r["gr"] > 0 else 0.0
        bog_meio = r["lpa_norm"] * (1 - reinv) / emp.preco + r["g_nom"]
        ok = abs(bog_meio - r["ke_nom_emp"]) <= 0.02
        x["trava_ok"] = ok
        x["trava_txt"] = (f"<b>{'passa' if ok else 'FALHA'}</b>. Bogle com re-rating {pct(r['bogle_nom'])} ({br(100 * (r['bogle_nom'] - r["ke_nom_emp"]), 1)} p.p. do Ke "
                          f"{pct(r["ke_nom_emp"])}): o P/L final de 10 anos ({br(r['pl_final'], 1)}) é sobre lucro reportado de pico e o de hoje sobre o normalizado "
                          f"({br(r['pl_atual'], 1)}). Sem re-rating, com o lucro normalizado (LPA R$ {br(r['lpa_norm'])}) menos o reinvestimento do DCF "
                          f"({pct(reinv)}), {pct(bog_meio)} ({br(100 * (bog_meio - r["ke_nom_emp"]), 1)} p.p.) — "
                          + ("dentro de ±2 p.p." if ok else "fora de ±2 p.p. Premissa que diverge: o LPA normalizado desconta juros nominais (a parcela de "
                             "inflação é devolução de principal, que o EPV não cobra) e as âncoras embutem Ke de " + pct(r["ke_implicito"]) +
                             ". Não corrigido: a palavra fica com a pendência T (doutrina §9) até o 3T26."))
    n = r["notas"]
    bloqueio = {"LEVE3": ("não se aplica — qualidade e solidez passam, mas a doutrina §7 lista a Mahle em 'ROE inflado' (ROE 12m ~72% × ROIC "
                          "{roic}) e em 'lucro não recorrente' (lucro 12m 1,5× o normalizado); zero armadilhas não está demonstrado — "
                          "liberar exige mudar o §7 (decisão do Frank)"), "UNIP6": "não se aplica (defeito estrutural)"}
    # AUD-42: regra única do §9; o bloqueio do lote entra como armadilha (o motor não calcula carimbos)
    arm = [bloqueio[emp.ticker].replace("{roic}", pct(r["roic"]))] if emp.ticker in bloqueio else []
    x["excecao"] = texto_entrada_parcial(r, emp, arm)
    return x


def preencher(s, emp, r, x):
    gi = r["g_implicito"]
    rep = {"compra": br(r["compra"]), "ke_impl": pct(r["ke_implicito"]) if r["ke_implicito"] else "n.d.",
           "central": br(r["central"]), "pc": br(r["pc"]), "m50": pct(r["op"]["m50"]), "m25": pct(r["op"]["m25"]), "m75": pct(r["op"]["m75"]),
           "dl_ebitda": br(r["dl_ebitda"]), "dl_ebitda_norm": br(r["dl_ebitda_norm"]), "dy_liq": pct(r["dy_liq"]),
           "aliquota": pct(r["aliquota"], 0), "altman": br(r["altman"]), "altman_zona": r["altman_zona"],
           "cobertura": br(r["cobertura_juros"], 1) if r["cobertura_juros"] else "n.d.",
           "sens_m_mais": br(r["sens"][(0, 0.02)]), "sens_m_menos": br(r["sens"][(0, -0.02)]), "dispersao": br(r["dispersao"]),
           "roc": pct(r["roc"]), "trava_txt": x["trava_txt"], "roic": pct(r["roic"]), "wacc": pct(r["wacc"]), "reprod": br(r["reprod"]),
           "palavra": r["palavra"], "epv": br(r["ancoras"].get("EPV de meio de ciclo", r["ancoras"].get("EPV", 0))),
           "dcf": br(r["ancoras"].get("DCF normalizado (3 cenários)", r["ancoras"].get("DCF (3 cenários)", 0))),
           "dpa5": br(r["dpa5"]), "fcfe": br(r["fcfe_acao"]), "pvp": br(x["pvp"]), "excecao": x["excecao"],
           "ebit_ltm": br(x["ebit_ltm"] / 1e6, 2), "ebit_meio": br(x["ebit_meio"] / 1e6, 2), "div_bruta": br(x["div_bruta"] / 1e6, 2)}
    for k in ("p12m", "p_ult", "c3a", "c_ltm", "g0", "c34", "dpa_sem_extra", "oe_alt", "c_oe"):
        if k in x:
            rep[k] = br(x[k])
    for k in ("idx12m", "idx_ult"):
        if k in x:
            rep[k] = br(x[k], 0)
    if "fator" in x:
        rep["fator"] = br(x["fator"], 3)
        rep["acima_meio"] = pct(INDICE[emp.ticker]["ltm_real"] / 100 - 1, 0)
        rep["janela"] = INDICE[emp.ticker]["janela"]
    if "corte" in x:
        rep["corte"], rep["palavra_corte"], rep["pc_corte"] = pct(x["corte"], 1), x["palavra_corte"], br(x["pc_corte"])
    for k in ("m3a", "m_ltm"):
        if k in x:
            rep[k] = pct(x[k])
    for k in ("div25", "lucro25"):
        if k in x:
            rep[k] = br(x[k] / 1e3, 0)
    for k in ("div22", "div21"):
        if k in x:
            rep[k] = br(x[k] / 1e6, 2)
    for k, val in rep.items():
        s = s.replace("{" + k + "}", val)
    assert "{" not in s, s
    return s


def grafico_margem(emp, r):
    a = CVM[emp.ticker]["anual"]
    anos = r["op"]["anos"]
    fig, ax = plt.subplots(figsize=(3.6, 1.9))
    if emp.impairment_normalizado:
        ax.bar(anos, [100 * a[y]["ebit"] / a[y]["receita"] for y in anos], color="#C9D6E3", width=0.7, label="margem EBIT contábil")
        ax.plot(anos, [100 * (margem_ano(emp, r, y) - (a[y].get("impairment") or 0) / a[y]["receita"]) for y in anos], "o", color="#1F3A5F",
                ms=3, label="sem impairment e não recorrentes")
    else:
        ax.bar(anos, [100 * a[y]["ebit"] / a[y]["receita"] for y in anos], color="#8DA9C4", width=0.7, label="margem EBIT contábil")
    ax.axhline(100 * r["op"]["m50"], color="#B83232", lw=1, ls="--", label=f"meio de ciclo {pct(r['op']['m50'])}")
    ax.set_title(f"{emp.ticker} — margem EBIT (%) [CVM]", fontsize=7.5)
    ax.tick_params(labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=60)
    ax.legend(fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=2, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return img(fig, 82)


def ficha(emp, r, rank, story):
    x = extras(emp, r)
    tx = {k: ([preencher(i, emp, r, x) for i in val] if isinstance(val, list) else preencher(val, emp, r, x)) for k, val in T[emp.ticker].items()}
    palavra = r["palavra"]
    nc = palavra == "NÃO CONCLUSIVO"
    if nc:       # §9: sem palavra não há preço de compra
        tx["capital"] = f"Não. NÃO CONCLUSIVO ({br(r['pc'])}× o central): sem palavra não há preço de compra nem de saída (§9)."
    cor = COR.get(palavra, AZUL)
    perfil = {"ciclica": "cíclica (commodity)", "servicos": "industrial (autopeças)"}[emp.perfil]
    carimbo = " · defeito estrutural" if emp.ticker == "UNIP6" else ""
    cab = Table([[P(f"<font name='Arial-B' size=14 color='#1F3A5F'>{emp.ticker}</font>  <font size=9>{emp.nome} · {perfil}</font>", "p"),
                  P(f"<font name='Arial-B' size=12 color='white'>{palavra}</font><font size=7 color='white'> · confiança {r['confianca']}{carimbo}</font>", "p")]],
                colWidths=[120 * mm, 60 * mm], rowHeights=[11 * mm])
    cab.setStyle(TableStyle([("BACKGROUND", (1, 0), (1, 0), cor), ("ALIGN", (1, 0), (1, 0), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (0, 0), 1.2, AZUL)]))
    story.append(cab)
    story.append(Spacer(1, 3))
    kpi = [["Preço 02/10", "Valor central", "P/C", "Compra 0,70×", "Saída 1,30×", "Ke implícito", "Vence a RF?", "Nota geral"],
           [f"R$ {br(emp.preco)}", f"R$ {br(r['central'])}" + (" (mediana)" if nc else ""), br(r["pc"]) + "×",
            "n.a." if nc else f"R$ {br(r['compra'])}", "n.a." if nc else f"R$ {br(r['saida'])}",
            pct(r["ke_implicito"]) if r["ke_implicito"] else "n.d.", rf_txt(r),
            br(r["notas"]["geral"], 1)]]
    story.append(tabela(kpi, [22.5 * mm] * 8, extra=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Círculo de competência.</b> {tx['circulo']}", "p"))
    story.append(Spacer(1, 3))
    ltm = ltm_de(CVM[emp.ticker])
    fatos = [["Fato (12m até jun/2026)", "Valor", "Fonte"],
             ["Receita · EBIT · margem", f"R$ {br(ltm['receita'] / 1e6, 2)} bi · {br(ltm['ebit'] / 1e6, 2)} bi · {pct(ltm['ebit'] / ltm['receita'])}", "[CVM]"]]
    if emp.ticker in INDICE:
        fatos += [["Receita de meio de ciclo", f"R$ {br(r['op']['receita_meio'] / 1e6, 2)} bi = 12m × {br(x['fator'], 3)} (preço dos 12m no índice "
                   f"{br(x['idx12m'], 0)}; meio = 100)", "[CVM][BLS][BCB]"]]
    else:
        fatos += [["Receita base", f"R$ {br(r['op']['receita_meio'] / 1e6, 2)} bi (média 2023–25 + 12m)", "[CVM]"]]
    fatos += [["Margem EBIT de meio de ciclo (p25 · p75)", f"{pct(r['op']['m50'])} ({pct(r['op']['m25'])} · {pct(r['op']['m75'])}), {r['op']['anos'][0]}–{r['op']['anos'][-1]}"
               + (f"; impairment recorrente {pct(r['op']['impairment_recorrente'], 2)}" if r["op"]["impairment_recorrente"] else ""), "[CVM]"],
              ["Ajuste capex de manutenção", pct(r["op"]["ajuste_manut"]) + " da receita", "[CVM]"],
              ["Dívida líquida · DL/EBITDA 12m · normalizado", f"R$ {br(r['dl'] / 1e6, 2)} bi · {br(r['dl_ebitda'])}× · {br(r['dl_ebitda_norm'])}×", "[CVM] 30/06/2026"],
              ["ROIC normalizado · WACC", f"{pct(r['roic'])} contábil · {pct(r['roic_reposicao'])} a custo de reposição "
                f"(imobilizado de {r['idade_imobilizado']:.1f} anos corrigido pelo IPCA) · WACC {pct(r['wacc'])} "
                f"(Kd {pct(r['kd'])}; IR efetivo {pct(r['aliquota'], 0)}). O menor decide o filtro 1, a nota e a trava do crescimento", "motor"],
              ["Ações · P/L 12m · P/VP", f"{br(r['n'] / 1e3, 1)} mi · {br(x['pl_ltm'], 1) if x['pl_ltm'] else 'n.d.'}× · {br(x['pvp'])}×", "[CVM] ITR jun/26"]]
    lado = Table([[tabela(fatos, [38 * mm, 44 * mm, 15 * mm]), grafico_margem(emp, r)]], colWidths=[98 * mm, 84 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)

    story.append(P("Quadro clássico (doutrina §11) — ao Ke da casa", "h3"))
    lin = [["Método", "Valor", "Marca", "Fórmula / insumos"]]
    for k, val in r["ancoras"].items():
        if k.startswith("EPV"):
            f = f"NOPAT normalizado R$ {br(r['nopat'] / 1e6, 2)} bi ÷ WACC real {pct(r['wacc_real'])} − dívida líquida − minoritários"
        elif k.startswith("DCF"):
            d = r["dcf"]
            f = (f"FCFF = NOPAT × (1+g) × (1 − g/ROIC), g real {pct(r['gr'], 0)} (zerado se ROIC < WACC); margem p25/mediana/p75 = "
                 f"R$ {br(d['pessimista'])} / {br(d['base'])} / {br(d['otimista'])}, pesos 25/50/25")
        elif k.startswith("Valor de repro"):
            f = emp.reproducao_fonte
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
    cic = emp.perfil == "ciclica"
    lin += [
        ["Lucro normalizado (próprio)", f"LPA R$ {br(r['lpa_norm'])}", "INFORMATIVO",
         ("meio de ciclo: " if cic else "") + "(NOPAT normalizado − juros líquidos após IR, Kd da casa) ÷ ações. Consenso 3 anos: não encontrado"],
        ["Owner Earnings por ano (R$ bi)", oe_txt or "n.d.", "INFORMATIVO" if cic else "ÂNCORA (acima)",
         "lucro + D&A − capex de manutenção − aumento de capital de giro [CVM]"],
        ["Graham original · Graham-BR", f"R$ {br(r['graham_orig'])} · {br(r['graham_br'])}" if r["graham_orig"] else "n.d.", "INFORMATIVO",
         f"√(22,5 × LPA normalizado × VPA {br(r['vpa'])}); f = {br(f, 3)}"],
        ["Graham revisado-BR", f"R$ {br(r['graham_rev'])}" if r["graham_rev"] else "n.d.", "INFORMATIVO", f"LPA normalizado × (8,5 + 2 × g real {br(100 * r['gr'], 0)}) × f"],
        ["7 critérios do defensivo", f"{sum(1 for _, ok in crit if ok)} de 6", "INFORMATIVO",
         "; ".join(("[sim] " if ok else "[não] ") + n_ for n_, ok in crit) + "; dividendos 20 anos: série de 10"],
        ["Teto de renda (Bazin calibrado)", f"R$ {br(r['teto_renda'])}" if r["teto_renda"] else "N/A", "INFORMATIVO",
         "DPA sustentável líquido ÷ RF nominal líquida" + ("" if r["coberto"] else " — N/A: dividendo médio acima do FCFE normalizado")],
        ["Bazin original (6%)", f"R$ {br(r['bazin6'])}" if r["bazin6"] else "N/A", "INFORMATIVO", "DPA sustentável ÷ 6%"],
        ["Lynch", f"PEG {br(r['peg'])} · PEGY {br(r['pegy'])}" if r["peg"] else "n.d.", "INFORMATIVO",
         f"categoria: {'cíclica — PEG não se aplica' if cic else 'crescimento lento — PEG só para stalwart/crescimento rápido'}; P/L normalizado ÷ g nominal {pct(r['g_nom'])}"],
        ["Greenblatt (Fórmula Mágica)", f"EY {pct(r['ey'])} · ROC {pct(r['roc'])}", "INFORMATIVO",
         f"EBIT 12m ÷ EV; EBIT ÷ (capital de giro + imobilizado). Posição entre as não financeiras do lote: {rank}º de {len(EMPRESAS)}"],
        ["DCF reverso", f"g real {('≤ −5%' if r['g_implicito'] <= -0.05 else pct(r['g_implicito'])) if r['g_implicito'] is not None else 'n.a. (ROIC < WACC)'} · "
                        f"Ke {pct(r['ke_implicito']) if r['ke_implicito'] else 'n.d.'}", "INFORMATIVO",
         "crescimento real perpétuo que o preço exige (margem mediana, Ke da casa); e o Ke que o preço embute"],
        ["Bogle (10 anos)", f"{pct(r['bogle_nom'])} nominal", "INFORMATIVO",
         f"DY sustentável {pct(r['dy'])} + g nominal {pct(r['g_nom'])} + múltiplo {pct(r['dmult'])} · real líquido {pct(r['bogle_liq_real'])}"
         + (" · sem re-rating (lucro dominado pelo preço da commodity)" if cic else f" · P/L final {br(r['pl_final'], 1)} (mediana 2016–25 [SI])")],
        ["Altman Z'' (emergentes) · Piotroski · Beneish · Sloan",
         f"{br(r['altman'])} ({r['altman_zona']}) · {r['piotroski']}/9 · {br(r['beneish']) if r['beneish'] is not None else 'n.d.'} · {pct(r['sloan'])}",
         "INFORMATIVO", f"exercício {r['ano_qualidade']} vs anterior [CVM]; Beneish > −1,78 = alerta; Sloan alto e positivo = lucro acima do caixa"],
    ]
    story.append(tabela(lin, [33 * mm, 29 * mm, 21 * mm, 99 * mm]))
    story.append(PageBreak())

    story.append(P(f"{emp.ticker} — reconstrução, sensibilidade e veredito", "h2"))
    rec = [["Âncora", "Valor", "Peso"]] + [[k, f"R$ {br(val)}", "mediana"] for k, val in r["ancoras"].items()]
    rec.append(["<b>Valor central</b>", f"<b>R$ {br(r['central'])}</b>", f"dispersão {br(r['dispersao'])}× · {r['confianca']}"])
    if nc:
        rec += [[f"Preço ÷ {k}", (br(v_) + "×") if v_ else "n.a.", "margem por método"] for k, v_ in x["por_metodo"].items()]
    ts = [["Central (R$)", "margem −2 p.p.", "margem base", "margem +2 p.p."]]
    for dk, nome in ((-0.01, "Ke −1 p.p. (prêmio de Ke)"), (0, "Ke da casa"), (0.01, "Ke +1 p.p. (prêmio de Ke)")):
        ts.append([nome] + [br(r["sens"][(dk, dm)]) for dm in (-0.02, 0, 0.02)])
    lado = Table([[tabela(rec, [40 * mm, 20 * mm, 30 * mm]), tabela(ts, [24 * mm, 20 * mm, 20 * mm, 20 * mm])]], colWidths=[92 * mm, 90 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)
    story.append(Spacer(1, 3))
    if "preco_idx" in x:
        cab_b = [f"Central (R$) com o índice de {'aço' if emp.ticker == 'GGBR4' else 'soda/PVC'} permanente em"] + \
                [f"{lv}" for lv in x["preco_idx"]] + [f"12m ({br(x['idx12m'], 0)})", "meio (100)"]
        story.append(tabela([cab_b, ["valor central"] + [br(v_) for v_ in x["preco_idx"].values()] + [br(x["p12m"]), br(r["central"])]],
                            [52 * mm] + [18.6 * mm] * 7))
        story.append(P("Mesma margem % (sem alavancagem operacional) — subestima o efeito do preço nos dois sentidos. Não é cenário de valor: o "
                       "central usa o preço de meio de ciclo declarado antes do veredito.", "pi"))
        story.append(Spacer(1, 2))
    story.append(P(f"<b>Controlador.</b> {tx['controlador']}", "p"))
    story.append(Spacer(1, 3))
    dpa, jc = SI[emp.ticker]["dpa_por_ano_datacom"], SI[emp.ticker]["jcp_por_ano_datacom"]
    yrs = list(range(2021, 2027))
    aj = {"GGBR4": " — ajustado por bonificação (ações CVM)", "UNIP6": " — ajustado por bonificação (ações CVM)"}.get(emp.ticker, "")
    story.append(tabela([[f"Proventos por data-com [SI]{aj}"] + [str(y) if y < 2026 else "2026 até 02/10" for y in yrs],
                         ["DPA total (R$)"] + [br(dpa.get(str(y), 0), 3) for y in yrs],
                         ["dos quais JCP (R$)"] + [br(jc.get(str(y), 0), 3) for y in yrs]], [50 * mm] + [22 * mm] * 6))
    story.append(Spacer(1, 2))
    story.append(tabela([["Renda e renda fixa (10 anos, líquido de IR)", "Valor"],
                         ["DPA médio 5a · FCFE normalizado por ação · sustentável", f"R$ {br(r['dpa5'], 3)} · R$ {br(r['fcfe_acao'], 3)} · R$ {br(r['dpa_sust'], 3)}"],
                         ["Coberto por caixa?", "Sim" if r["coberto"] else "Não — o dividendo médio supera o FCFE normalizado"],
                         ["Yield sustentável bruto · líquido", f"{pct(r['dy'])} · {pct(r['dy_liq'])}"],
                         ["Retorno esperado real líquido (Bogle) · sem re-rating", f"{pct(r['bogle_liq_real'])} · {pct(r['so_inv_liq_real'])}"],
                         ["RF real líquida", f"{pct(MK.rf_liq_real, 2)} → Sim ≥ {pct(MK.rf_liq_real + .03, 2)} · Empate ≥ {pct(MK.rf_liq_real + .015, 2)}"],
                         ["Vence a RF?", rf_txt(r)],
                         ["Trava de coerência: JUSTA → retorno ≈ Ke", x["trava_txt"]]],
                        [95 * mm, 87 * mm]))
    story.append(Spacer(1, 3))
    n = r["notas"]
    preco_txt = ((("Sem palavra: as âncoras discordam mais de 3× (doutrina §11.3)" if r["dispersao"] > 3 else f"Sem palavra: trava de coerência (§9; dispersão das âncoras {br(r['dispersao'])}×)") + " — ver a margem por método acima. ")
                 if nc else f"Compra R$ {br(r['compra'])} · justo R$ {br(r['central'])} · saída R$ {br(r['saida'])}. " + nota_f2(r))
    car = " · <b>defeito estrutural: dividendo não coberto por caixa</b> (§7)" if emp.ticker == "UNIP6" else ""
    ver = Table([[P(f"<b>Veredito: <font color='{cor.hexval()}'>{palavra}</font></b>{car} — preço {br(r['pc'])}× o central. {preco_txt}"
                    f"Entrada parcial (exceção §9): {x['excecao'] if not nc else 'não se aplica'}.<br/>"
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


# ---------------------------------------------------------------- EGIE3 (regulado)
def rf_txt(r):
    return r["vence_rf"] + (f" (sem re-rating: {r['rf_sem_rerating']})" if r["so_com_rerating"] else "")


def tir_real(r):
    k = r["ke_implicito"]
    return (1 + k) / (1 + MK.pi) - 1 if k else None


def egie_extras(emp, r):
    d = EGIE_DADOS
    w = d["peso_novo"]
    blend = lambda base, novo: (1 - w) * base + w * novo
    x = {"tir": tir_real(r)}
    x["dle"], x["cob"], x["dl"] = alavancagem(emp.ticker)
    x["jirau_rf"] = avaliar_fin(com(emp, roe_lp=blend(d["roe_old_lp"], MK.rf_nom), roe_inicio=blend(d["roe_old_ini"], MK.rf_nom)), MK)["central"]
    x["jirau_zero"] = avaliar_fin(com(emp, roe_lp=blend(d["roe_old_lp"], 0.0), roe_inicio=blend(d["roe_old_ini"], 0.0)), MK)["central"]
    x["central_roe_atual"] = avaliar_fin(com(emp, roe_lp=emp.roe_inicio), MK)["central"]
    media = sum(d["roes"].values()) / len(d["roes"])
    x["roe_media"], x["central_media"] = media, avaliar_fin(com(emp, roe_lp=blend(media, MK.ke_nom)), MK)["central"]
    lo, hi = 0.10, d["roe_old_lp"] + 0.05          # ROE do negócio existente que leva o P/C a 1,10 (fronteira JUSTA/CARA)
    for _ in range(60):
        mid = (lo + hi) / 2
        if emp.preco / avaliar_fin(com(emp, roe_lp=blend(mid, MK.ke_nom)), MK)["central"] > 1.10:
            lo = mid
        else:
            hi = mid
    x["roe_virada"] = (lo + hi) / 2
    a = CVM[emp.ticker]["anual"]
    x["altman"], x["zona"] = altman_z2(ltm_de(CVM[emp.ticker]))
    x["piotroski"], _ = piotroski(a["2025"], a["2024"])
    x["beneish"] = beneish(a["2025"], a["2024"])
    x["sloan"] = sloan(a["2025"], a["2024"])
    return x


def egie_preencher(s, emp, r, x):
    d = EGIE_DADOS
    rep = {"compra": br(r["compra"]), "pc": br(r["pc"]), "palavra": r["palavra"], "dy_liq": pct(r["dy_liq"]),
           "tir": pct(x["tir"]) if x["tir"] is not None else "não calculável", "rf": pct(MK.rf_real, 2), "ke_real": pct(MK.ke_real, 2),
           "dl_ebitda": br(x["dle"]), "roe_old_lp": pct(d["roe_old_lp"]), "roe_old_ini": pct(d["roe_old_ini"]),
           "jirau_rf": br(x["jirau_rf"]), "jirau_zero": br(x["jirau_zero"]), "central_roe_atual": br(x["central_roe_atual"]), "g": pct(r["g"]),
           "roe_virada": pct(x["roe_virada"]), "roe_media": pct(x["roe_media"]), "central_media": br(x["central_media"])}
    for k, val in rep.items():
        s = s.replace("{" + k + "}", val)
    assert "{" not in s, s
    return s


def ficha_egie(emp, r, story):
    x = egie_extras(emp, r)
    tx = {k: ([egie_preencher(i, emp, r, x) for i in v] if isinstance(v, list) else egie_preencher(v, emp, r, x)) for k, v in T["EGIE3"].items()}
    d = EGIE_DADOS
    palavra = r["palavra"]
    cor = COR.get(palavra, AZUL)
    cab = Table([[P(f"<font name='Arial-B' size=14 color='#1F3A5F'>{emp.ticker}</font>  <font size=9>{emp.nome} · utility (geração e transmissão)</font>", "p"),
                  P(f"<font name='Arial-B' size=12 color='white'>{palavra}</font><font size=7 color='white'> · confiança {r['confianca']}</font>", "p")]],
                colWidths=[120 * mm, 60 * mm], rowHeights=[11 * mm])
    cab.setStyle(TableStyle([("BACKGROUND", (1, 0), (1, 0), cor), ("ALIGN", (1, 0), (1, 0), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (0, 0), 1.2, AZUL)]))
    story.append(cab)
    story.append(Spacer(1, 3))
    tir = x["tir"]
    kpi = [["Preço 02/10", "Valor central", "P/C", "Compra 0,70×", "Saída 1,30×", "TIR real implícita", "Vence a RF?", "Nota geral"],
           [f"R$ {br(emp.preco)}", f"R$ {br(r['central'])}", br(r["pc"]) + "×", f"R$ {br(r['compra'])}", f"R$ {br(r['saida'])}",
            pct(tir) if tir is not None else "n.c.", rf_txt(r), br(r["notas"]["geral"], 1)]]
    story.append(tabela(kpi, [22.5 * mm] * 8, extra=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Círculo de competência.</b> {tx['circulo']}", "p"))
    story.append(Spacer(1, 3))
    l = ltm_de(CVM["EGIE3"])
    fatos = [["Fato", "Valor", "Fonte"],
             ["Patrimônio do controlador 30/06 − dividendo de ago/26", f"R$ {br(d['pl_old'] / 1e6, 2)} bi (dividendo R$ {br(EGIE_DIV_AGO26 / 1e6, 2)} bi, data-com 20/08)", "[CVM][SI]"],
             ["+ follow-on de jul/26 (Jirau 40%)", f"R$ {br(EGIE_FOLLOW_ON['valor'] / 1e6, 2)} bi · {br(EGIE_FOLLOW_ON['acoes'] / 1e6, 1)} mi de ações", "PDF 07/09"],
             ["Ações · VPA · P/VP", f"{br(N['EGIE3'] / 1e6, 1)} mi · R$ {br(emp.vpa)} · {br(r['pvp'])}×", "[CVM] ITR jun/26 + follow-on"],
             ["Lucro 12m (controlador) · LPA nas ações de hoje", f"R$ {br(l['lucro_controlador'] / 1e6, 2)} bi · R$ {br(emp.lpa_12m, 3)}", "[CVM]"],
             ["ROE do negócio existente: 12m · longo prazo", f"{pct(d['roe_old_ini'])} · {pct(d['roe_old_lp'])} (mediana 2017–25 sem não recorrentes)", "[CVM]"],
             ["ROE combinado (dinheiro novo ao Ke): início · longo prazo", f"{pct(emp.roe_inicio)} · {pct(emp.roe_lp)} (peso do novo {pct(d['peso_novo'], 0)})", "motor"],
             ["Payout · g perpétuo", f"{pct(emp.payout, 0)} · {pct(r['g'])}", "política mínima / motor"],
             ["Dívida líquida · DL/EBITDA · cobertura", f"R$ {br(x['dl'] / 1e6, 1)} bi · {br(x['dle'])}× · {br(x['cob'], 1) if x['cob'] else 'n.d.'}×", "[CVM] jun/26"]]
    lado = Table([[tabela(fatos, [42 * mm, 40 * mm, 15 * mm]), grafico_roe("EGIE3", r, emp)]], colWidths=[98 * mm, 84 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)
    story.append(P("Quadro clássico (doutrina §11) — ao Ke da casa", "h3"))
    ke, g = r["ke"], r["g"]
    an = list(r["ancoras"].items())
    proj = projecao(emp, 3)
    pl12 = emp.preco / emp.lpa_12m
    f = MK.fator_graham
    lin = [["Método", "Valor", "Marca", "Fórmula / insumos"],
           ["DCF regulatório (P/VP justificado)", f"R$ {br(an[0][1])}", "ÂNCORA",
            f"patrimônio (proxy da base regulatória) × (ROE {pct(emp.roe_lp)} − g {pct(g)}) ÷ (Ke {pct(ke, 2)} − g) = {br(r['pvp_just'])}× VPA. "
            + metodo_regulado(emp.ticker)],
           ["DDM 2 estágios", f"R$ {br(an[1][1])}", "ÂNCORA", f"ROE {pct(emp.roe_inicio)} → {pct(emp.roe_lp)} em 5 anos; payout {pct(emp.payout, 0)}; terminal = P/VP justificado"],
           ["TIR real implícita", pct(tir) if tir is not None else "n.c.", "TESTE (§4)",
            f"retorno real que o preço embute (mesmo modelo); piso rf {pct(MK.rf_real, 2)} · Ke real {pct(MK.ke_real, 2)} — "
            + ("perde para o Tesouro" if (tir is None or tir < MK.rf_real) else ("acima do Tesouro, abaixo do Ke da casa" if tir < MK.ke_real else "acima do Ke da casa"))],
           ["Lucro projetado (próprio)", " · ".join(f"R$ {br(p[2])}" for p in proj), "INFORMATIVO", "LPA anos 1–3 (ROE convergindo; VPA cresce pela retenção). Consenso: não encontrado"],
           ["Graham original · Graham-BR", f"R$ {br(r['graham_orig'])} · {br(r['graham_br'])}", "INFORMATIVO", f"√(22,5 × LPA normalizado {br(r['lpa_norm'])} × VPA); f = {br(f, 3)}"],
           ["7 critérios do defensivo", "—", "INFORMATIVO",
            f"P/L 12m {br(pl12, 1)} {'≤' if pl12 <= 15 * f else '>'} {br(15 * f, 1)}; P/L × P/VP {br(pl12 * r['pvp'], 1)} {'≤' if pl12 * r['pvp'] <= 22.5 * f else '>'} {br(22.5 * f, 1)}; "
            "liquidez corrente < 2 é estrutural em utility"],
           ["Teto de renda (Bazin calibrado)", f"R$ {br(r['teto_renda'])}" if r["teto_renda"] else "N/A", "INFORMATIVO",
            f"DPA sustentável líquido {br(r['dpa_sust_liq'], 3)} ÷ RF nominal líquida {pct(MK.rf_liq_nom, 2)}"],
           ["Bazin original (6%)", f"R$ {br(r['bazin6'])}", "INFORMATIVO", "DPA sustentável ÷ 6%"],
           ["DCF reverso", f"ROE {pct(r['roe_implicito'], 0)}", "INFORMATIVO", "ROE perpétuo que o preço exige ao Ke da casa"],
           ["Bogle (10 anos)", f"{pct(r['bogle_nom'])} nominal", "INFORMATIVO",
            f"investimento (DY {pct(r['dy'])} + g {pct(g)}) = {pct(r['ret_investimento'])} · especulativo (P/L {br(r['pl_atual'], 1)} → {br(r['pl_final'], 1) if r['pl_final'] else '—'}) "
            f"= {pct(r['ret_especulativo'])} · real líquido {pct(r['bogle_liq_real'])}"],
           ["Altman Z'' · Piotroski · Beneish · Sloan", f"{br(x['altman'])} ({x['zona']}) · {x['piotroski']}/9 · {br(x['beneish']) if x['beneish'] is not None else 'n.d.'} · {pct(x['sloan'])}",
            "INFORMATIVO", "exercício 2025 vs 2024 [CVM]; em utility o Altman tende à zona cinzenta pela dívida longa"],
           ["Greenblatt · EPV · Owner Earnings", "N/A", "N/A por perfil",
            "transmissão em ativo de contrato (ICPC 01): o investimento passa pelo FCO — EBIT/capital e FCO − capex não medem o negócio"]]
    story.append(tabela(lin, [33 * mm, 27 * mm, 21 * mm, 101 * mm]))
    story.append(PageBreak())
    story.append(P(f"{emp.ticker} — reconstrução, renda e veredito", "h2"))
    rec = [["Âncora", "Valor", "Peso"]] + [[k, f"R$ {br(v)}", "mediana"] for k, v in r["ancoras"].items()]
    rec.append(["<b>Valor central</b>", f"<b>R$ {br(r['central'])}</b>", f"dispersão {br(r['dispersao'])}× · {r['confianca']}"])
    rec += [["Jirau rendendo a rf nominal", f"R$ {br(x['jirau_rf'])}", "sensibilidade"], ["Jirau rendendo zero", f"R$ {br(x['jirau_zero'])}", "sensibilidade"],
            ["ROE de 12m como longo prazo", f"R$ {br(x['central_roe_atual'])}", "sensibilidade"],
            [f"ROE médio 2017–25 ({pct(x['roe_media'])}) em vez da mediana", f"R$ {br(x['central_media'])}", "sensibilidade"],
            ["ROE do negócio existente que vira CARA (P/C 1,10)", pct(x["roe_virada"]), f"mediana usada {pct(EGIE_DADOS['roe_old_lp'])}"]]
    ts = [["Central (R$)", "ROE −2 p.p.", "ROE base", "ROE +2 p.p."]]
    for dk, nome in ((-0.01, "Ke −1 p.p. (rf real)"), (0, "Ke da casa"), (0.01, "Ke +1 p.p. (rf real)")):
        ts.append([nome] + [br(r["sens"][(dk, dr)]) for dr in (-0.02, 0, 0.02)])
    lado = Table([[tabela(rec, [40 * mm, 20 * mm, 30 * mm]), tabela(ts, [24 * mm, 20 * mm, 20 * mm, 20 * mm])]], colWidths=[92 * mm, 90 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Controlador.</b> {tx['controlador']}", "p"))
    story.append(Spacer(1, 3))
    dpa, jc = SI["EGIE3"]["dpa_por_ano_datacom"], SI["EGIE3"]["jcp_por_ano_datacom"]
    yrs = list(range(2021, 2027))
    story.append(tabela([["Proventos por data-com [SI] — ÷ 1,4 antes de 01/12/25"] + [str(y) if y < 2026 else "2026 até 02/10" for y in yrs],
                         ["DPA total (R$)"] + [br(dpa.get(str(y), 0), 3) for y in yrs],
                         ["dos quais JCP (R$)"] + [br(jc.get(str(y), 0), 3) for y in yrs]], [50 * mm] + [22 * mm] * 6))
    story.append(Spacer(1, 2))
    trava = r["trava"] if r["trava"] is not None else abs(r["bogle_nom"] - r["ke_nom_emp"]) <= 0.02   # Ke da empresa (v2.4)
    story.append(tabela([["Renda e renda fixa (10 anos, líquido de IR)", "Valor"],
                         ["Yield sustentável bruto · líquido (JCP × 0,825)", f"{pct(r['dy'])} · {pct(r['dy_liq'])}"],
                         ["Coberto por caixa?", "Sim — DPA sustentável ≤ FCFE normalizado" if r["dpa_fcfe"] >= emp.dpa_medio_5a else
                          "Parcial — o DPA médio supera o FCFE normalizado; entra o menor"],
                         ["Retorno esperado real líquido (Bogle) · sem re-rating", f"{pct(r['bogle_liq_real'])} · {pct(r['so_inv_liq_real'])}"],
                         ["RF real líquida", f"{pct(MK.rf_liq_real, 2)} → Sim ≥ {pct(MK.rf_liq_real + .03, 2)} · Empate ≥ {pct(MK.rf_liq_real + .015, 2)}"],
                         ["Vence a RF?", rf_txt(r)],
                         ["Trava de coerência: JUSTA → retorno ≈ Ke", ("não se aplica" if palavra != "JUSTA" else
                          (f"passa — Bogle {pct(r['bogle_nom'])} a ±2 p.p. do Ke {pct(MK.ke_nom)}" if trava else f"falha — Bogle {pct(r['bogle_nom'])} vs Ke {pct(MK.ke_nom)}"))]],
                        [95 * mm, 87 * mm]))
    story.append(Spacer(1, 3))
    n = r["notas"]
    ver = Table([[P(f"<b>Veredito: <font color='{cor.hexval()}'>{palavra}</font></b> — preço {br(r['pc'])}× o central. "
                    f"Compra R$ {br(r['compra'])} · justo R$ {br(r['central'])} · saída R$ {br(r['saida'])}. " + nota_f2(r) + "<br/>"
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
    a0 = ANTES["EGIE3"]
    story.append(P(f"<b>De → para (rev. 03/10 → hoje).</b> {a0[0]}, central R$ {br(a0[1])} → {palavra}, central R$ {br(r['central'])}. {tx['de_para']} "
                   f"Preço inalterado (R$ {br(emp.preco)}, fechamento de 02/10).", "p"))
    story.append(P("<b>Autocrítica (5 linhas).</b> " + " ".join(f"{i + 1}) {t}" for i, t in enumerate(tx["autocritica"])), "p"))
    story.append(P(f"<b>Eventos com data.</b> {AGENDA}.", "p"))
    story.append(P(f"<b>Não encontrado.</b> {tx['nao_encontrado']}", "pi"))
    story.append(PageBreak())


# ---------------------------------------------------------------- capa e metodologia
def tabela_indices():
    lin = [["Ano", "Aço (WPU1017)", "Soda cáustica", "Resinas termopl.", "Cesta UNIP6 (50/50)"]]
    for y in range(2016, 2026):
        lin.append([str(y)] + [br(ix["anual"].loc[y, "real"], 0) for ix in (ACO, SODA, PVC, CLORO)])
    lin.append(["<b>Meio de ciclo = 100</b> (aço 2016–25; cloro-soda/PVC 2017–25)", "<b>100</b>", "<b>100</b>", "<b>100</b>", "<b>100</b>"])
    lin.append(["12m até jun/2026 (base da receita)"] + [br(ix["ltm"], 0) for ix in (ACO, SODA, PVC, CLORO)])
    lin.append([f"Último ({ACO['ultimo'][0]})"] + [br(ix["ultimo"][1], 0) for ix in (ACO, SODA, PVC, CLORO)])
    lin.append(["Fator de meio de ciclo (meio ÷ 12m)"] + [br(ix["fator"], 3) for ix in (ACO, SODA, PVC, CLORO)])
    return tabela(lin, [60 * mm, 30 * mm, 30 * mm, 30 * mm, 32 * mm])


def capa(res, rank, story):
    story.append(P("Fichas de Avaliação — Value Investing B3", "h1"))
    story.append(P(f"Lote 6 — Química e metalurgia (4 empresas) · rev. 09/10/2026 · data-base {DATA_BASE} · doutrina v2.5", "h2"))
    cont = {}
    for r in res:
        cont[r["palavra"]] = cont.get(r["palavra"], 0) + 1
    resumo = " · ".join(f"{k}: {v}" for k, v in sorted(cont.items()))
    pal = {x["ticker"]: x["palavra"] for x in res}
    por = " · ".join(f"{p}: {', '.join(r['ticker'] for r in res if r['palavra'] == p)}" for p in ("BARATA", "RADAR", "JUSTA", "CARA", "NÃO CONCLUSIVO")
                     if any(r["palavra"] == p for r in res))
    box = (f"<b>Conclusão.</b> Ao Ke da casa ({pct(MK.ke_nom)} nominal), com o preço de aço e de cloro-soda/PVC de meio de ciclo declarado antes do "
           f"veredito (média do ciclo em reais de hoje: aço 2016–25, cloro-soda/PVC 2017–25), o lote fica: <b>{resumo}</b> — {por}. <b>Nenhuma compra autorizada.</b> "
           f"LEVE3 cria valor (ROIC acima do WACC), mas a palavra é {pal['LEVE3']} (ver a ficha); EGIE3 fica {pal['EGIE3']} com o follow-on de Jirau somado ao "
           "patrimônio; GGBR4 perde o RADAR — o livro não é piso quando o ROIC de meio de ciclo fica abaixo do custo de capital; "
           f"UNIP6 fica {pal['UNIP6']} (lucro de meio de ciclo × livro distribuído, âncoras perto do corte de 3×) e mantém o defeito estrutural de dividendo não coberto.")
    tb = Table([[P(box, "box")]], colWidths=[182 * mm])
    tb.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, AZUL), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF3F9")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(tb)
    story.append(P("Quadro-resumo", "h3"))
    q = [["Ticker", "Palavra", "Preço", "Central", "P/C", "Compra", "Saída", "Ke implícito", "Retorno × custo", "Greenblatt", "Vence RF", "Nota", "03/10"]]
    for r in sorted(res, key=lambda z: z["pc"]):
        an = ANTES[r["ticker"]]
        nc = r["palavra"] == "NÃO CONCLUSIVO"
        rc = (f"ROIC {pct(r['roic'], 0)} × WACC {pct(r['wacc'], 0)}" if "roic" in r else f"ROE {pct(r['roe_lp_'], 0)} × Ke {pct(MK.ke_nom, 0)}")
        q.append([r["ticker"], f"<font color='{COR.get(r['palavra'], AZUL).hexval()}'><b>{r['palavra']}</b></font>",
                  br(r["preco_"]), br(r["central"]), br(r["pc"]), "n.a." if nc else br(r["compra"]), "n.a." if nc else br(r["saida"]),
                  pct(r["ke_implicito"]) if r["ke_implicito"] else "n.d.", rc, f"{rank[r['ticker']]}º" if r["ticker"] in rank else "N/A",
                  r["vence_rf"] + ("*" if r["so_com_rerating"] else ""), br(r["notas"]["geral"], 1), f"{an[0].split(' ')[0]} {br(an[1])}"])
    story.append(tabela(q, [13 * mm, 22 * mm, 11 * mm, 12 * mm, 10 * mm, 12 * mm, 12 * mm, 14 * mm, 25 * mm, 13 * mm, 12 * mm, 9 * mm, 17 * mm]))
    story.append(Spacer(1, 4))
    story.append(grafico_resumo([dict(r, pc=min(r["pc"], 2.8)) for r in res]))
    story.append(P("Greenblatt = posição entre as três não financeiras pela soma dos rankings de EY (EBIT 12m ÷ EV) e ROC; EGIE3 N/A (concessão). "
                   "* o resultado muda sem re-rating (ver ficha). NÃO CONCLUSIVO: sem preço de compra; o P/C mostrado é sobre a mediana das âncoras.", "pi"))
    story.append(PageBreak())
    story.append(P("Premissa de ciclo declarada antes do veredito — preço de aço e de cloro-soda/PVC", "h2"))
    story.append(tabela_indices())
    story.append(P("Índices de preço ao produtor dos EUA (BLS, via FRED: WPU1017 Steel Mill Products; PCU3251803251804 Sodium Hydroxide; WPU0662 "
                   "Thermoplastic Resins and Plastics Materials) × PTAX média mensal (BCB SGS 3698) ÷ IPCA (BCB SGS 433) até ago/2026; média do ciclo = 100, na mesma janela da margem (aço 2016–25; UNIP6 2017–25 — a Indupa entra em dez/2016 e a série de soda não tem jan–set/2016). "
                   "Nenhum dos PDFs anteriores declarava preço de aço, PVC ou soda, e não há preço em R$/t com fonte A/B por API — por isso o índice, "
                   "declarado como proxy. Limites: preço dos EUA (tarifa da seção 232 eleva o aço americano; PVC asiático deprime o PVC do Mercosul); "
                   "resinas termoplásticas incluem PE e PP além do PVC; pesos 50/50 da cesta da UNIP6 são HIPÓTESE.", "pi"))
    story.append(P("Metodologia (o que é novo em relação aos Lotes 1–5)", "h2"))
    met = [["Item", "Regra"],
           ["Dados", "Demonstrações consolidadas da CVM (DFP 2016–25 + ITR; 12m até jun/2026) — fonte A. Preço: fechamento de 02/10 (PDF rev. 03/10). "
                     "Ações: composição do capital do ITR de jun/2026, sem tesouraria (GGBR4: ON + PN ao preço da PN; UNIP6: ON + PNA + PNB ao preço da PNB). "
                     "Proventos: StatusInvest, ajustados por bonificação (EGIE3 ÷ 1,4 antes de 01/12/25; GGBR4 e UNIP6 pela contagem de ações da CVM). "
                     "Contas: ferramentas/motor_nao_financeiras.py, motor_financeiras.py e lote6_quimica.py."],
           ["Cíclicas (GGBR4, UNIP6)", "Receita de meio = receita de 12m × fator do índice (meio ÷ 12m), preço e margem na mesma janela; margem EBIT mediana do ciclo sem não recorrentes "
                                       "(3.04.04 + 3.04.05 acima da mediana); capex de manutenção pela regra de commodity; âncoras EPV, DCF e reprodução (PL). "
                                       "GGBR4: impairment sai da margem ano a ano e a perda mediana de 10 anos fica como custo. UNIP6: janela 2017–25."],
           ["Industrial (LEVE3)", "Margem EBIT mediana de 10 anos sobre a receita média de 2023–25 + 12m; capex de manutenção por Greenwald; âncoras DCF, EPV "
                                  "e Owner Earnings; P/L histórico no Bogle."],
           ["Utility (EGIE3)", "Método de regulado do Lote 2: P/VP justificado e DDM 2 estágios, TIR real implícita. Patrimônio de jun/26 − dividendo de "
                               "ago/26 + follow-on de jul/26 (R$ 8,36 bi, Jirau 40%), com o dinheiro novo rendendo o Ke (VPL zero); ROE de longo prazo = "
                               "mediana 2017–25 do ROE do controlador sem 'outras receitas' acima da mediana (UBP de 2024)."],
           ["Correções no coletor (valem para todos os lotes)", "Custo de transação e AVP de debêntures saíram da D&A (SUZB3 2021–25, KLBN11); impairment "
                               "lido na conta mais alta que casa (GGBR4 2016: 3.04.03 com filho zerado) e separado do lançado em 3.04.05. Lotes 2, 3 e 5 "
                               "conferidos: nenhuma palavra muda (SUZB3 central 37,94 → 37,12; KLBN11 5,06 → 4,98). Reemitido no Lote 4 (05/10): reinvestimento do DCF = g real ÷ ROIC real (Fisher), antes ÷ ROIC nominal — LEVE3 36,82 → 36,76; UNIP6 dispersão 3,26 → 3,14."],
           ["Controlador e carimbos", "Desconto zero nas quatro, com a razão escrita. UNIP6: defeito estrutural (dividendo não coberto por caixa, dívida "
                                     "subindo) — não é ARMADILHA porque o múltiplo não é baixo (P/L 12m > 20)."],
           ["WACC e notas", f"Ke da casa {pct(MK.ke_nom, 2)}; Kd = rf nominal + spread declarado (1,5–2 p.p.); pesos a mercado. Notas 30/20/25/25."]]
    story.append(tabela(met, [36 * mm, 146 * mm]))
    story.append(PageBreak())


def main():
    res, inds = [], []
    for e in EMPRESAS:
        r = avaliar(e, MK)
        r["preco_"] = e.preco
        res.append(r)
        inds.append(r)
    re_ = avaliar_fin(EGIE, MK)
    re_["preco_"], re_["roe_lp_"], re_["ticker"] = EGIE.preco, EGIE.roe_lp, "EGIE3"
    ey = sorted(inds, key=lambda z: -(z["ey"] or 0))
    roc = sorted(inds, key=lambda z: -(z["roc"] or 0))
    soma = {r["ticker"]: ey.index(r) + roc.index(r) for r in inds}
    rank = {tk: i + 1 for i, (tk, _) in enumerate(sorted(soma.items(), key=lambda kv: kv[1]))}
    todos = res + [re_]
    guardar(SAIDA, "pdf lote 6")      # AUD-84: o PDF anterior do mesmo nome vai para _historico/
    doc = SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=14 * mm,
                            title=f"Lote 6 — Química e metalurgia · rev. {REV.replace('-', '/')}", author="Mesa de Value Investing")

    def rodape(c, d):
        c.saveState()
        c.setFont("Arial", 6.5)
        c.setFillColor(colors.HexColor("#6B7280"))
        c.drawString(15 * mm, 9 * mm, f"Mesa de Value Investing — Lote 6 Química e metalurgia · rev. 09/10/2026 · data-base {DATA_BASE} · "
                                      "doutrina v2.5 · não é recomendação de investimento")
        c.drawRightString(195 * mm, 9 * mm, f"p. {d.page}")
        c.restoreState()

    story = []
    capa(todos, rank, story)
    for r in sorted(todos, key=lambda z: z["pc"]):
        if r["ticker"] == "EGIE3":
            ficha_egie(EGIE, r, story)
        else:
            e = next(x for x in EMPRESAS if x.ticker == r["ticker"])
            ficha(e, r, rank[e.ticker], story)
    story.append(P("Apêndice — fontes", "h2"))
    story.append(tabela([["Rótulo", "Fonte"],
                         ["[CVM]", "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/ e /ITR/DADOS/ (cache em ferramentas/dados/cvm)"],
                         ["[SI]", "https://statusinvest.com.br (proventos por data-com; ROE histórico) — 05/10/2026"],
                         ["[BLS] [BCB] [IBGE]", "fred.stlouisfed.org/series/" + ", ".join(SERIES) + "; api.bcb.gov.br SGS 3698 (PTAX) e 433 (IPCA) — ferramentas/dados/macro"],
                         ["Mercado", "Tesouro Transparente (IPCA+ 2050 sem cupom 7,06%), ANBIMA ETTJ (inflação implícita 6,46%) — o mesmo dos Lotes 1–5"],
                         ["PDF 07/09 · 03/10", "Fichas anteriores (pasta QUÍMICA E METALÚRGIA): controle, ativos, contratos, follow-on da EGIE3, gatilhos, partes "
                                               "relacionadas — fontes primárias citadas lá; extraídas em ferramentas/dados/fatos_lote6.json"]],
                        [30 * mm, 152 * mm]))
    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    print("gerado:", SAIDA)
    for r in sorted(todos, key=lambda z: z["pc"]):
        print(r["ticker"], r["palavra"], round(r["central"], 2), round(r["pc"], 2), "rank", rank.get(r["ticker"]))


if __name__ == "__main__":
    main()
