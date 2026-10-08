"""PDF do Lote 4 (Saúde, telecom e blue chips) — doutrina v2.2. Uso: python gerar_pdf_lote4.py"""
from ltm import ltm_de
import copy
import pathlib
import re
import sys
from statistics import median

import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle

import gerar_pdf_lote1  # registra as fontes Arial
from gerar_pdf_lote1 import AZUL, COR, LINHA, br, grafico_resumo, grafico_roe, img, pct, tabela

_P = gerar_pdf_lote1.P


def P(t, st="cel"):
    """Escapa '&' solto (D&A) para o parser do reportlab; vale também dentro de tabela()."""
    return _P(re.sub(r"&(?!amp;|lt;|gt;|#)", "&amp;", t) if isinstance(t, str) else t, st)


gerar_pdf_lote1.P = P
import lote3_agro
import lote4_saude_telecom as L4
import lote5_petroleo
import lote6_quimica
from lote1_bancos import DATA_BASE, MK
from lote4_saude_telecom import EMPRESAS, ITSA, ITSA4, ITSA_PAYOUT, ITSA_ROE_LP, ITUB4, N, WEG_G1, WEG_PAYOUT, WEG_ROE5, sotp_partes
from lote4_textos import AGENDA, ANTES, T
from motor_financeiras import Mercado, avaliar as avaliar_fin, projecao
from motor_nao_financeiras import ANOS, CVM, SI, avaliar, ebit_aj, valores

sys.stdout.reconfigure(encoding="utf-8")
REV = "05-10-2026"
SAIDA = pathlib.Path(__file__).parent.parent / "SAÚDE, TELECOM E BLUECHIPS" / f"Saude_Telecom_Bluechips_rev_{REV}.pdf"
PERFIL = {"TIMS3": "telecom", "VIVT3": "telecom", "FLRY3": "serviços de saúde (diagnóstico)", "HYPE3": "farmacêutica", "ABEV3": "consumo (bebidas)",
          "WEGE3": "bens de capital (compounder)"}
FORA_DO_HALL = {"UNIP6", "VBBR3"}


def central_rapido(emp, **kw):
    return median(valores(emp, MK, **kw)["anc"].values())


def com(emp, **campos):
    e = copy.deepcopy(emp)
    for k, val in campos.items():
        setattr(e, k, val)
    return e


def margem_ano(emp, r, y):
    a = CVM[emp.ticker]["anual"][y]
    return ebit_aj(a, r["op"]["med_outras"], emp.outras_liquidas) / a["receita"]


def rf_txt(r):
    return r["vence_rf"] + (f" (sem re-rating: {r['rf_sem_rerating']})" if r["so_com_rerating"] else "")


def extras(emp, r):
    tk = emp.ticker
    a, ltm = CVM[tk]["anual"], ltm_de(CVM[tk])
    x = {"pl_ltm": emp.preco / (ltm["lucro_controlador"] / r["n"]) if ltm.get("lucro_controlador", 0) > 0 else None,
         "pvp": emp.preco / r["vpa"], "arr": (ltm.get("arrendamento") or 0), "arr_pago": ltm.get("arrendamento_pago") or 0}
    x["m_ltm"] = ebit_aj(ltm, r["op"]["med_outras"], emp.outras_liquidas) / ltm["receita"]
    x["c_ltm"] = central_rapido(emp, margem=x["m_ltm"])
    x["pc_ltm"] = emp.preco / x["c_ltm"]
    if tk == "HYPE3":
        x["c34"] = central_rapido(com(emp, aliquota=0.34, aliquota_fase=None))     # 34% já, sem a fase até 2030 (v2.3)
    if tk == "ABEV3":
        x["c_aliq_motor"] = central_rapido(com(emp, aliquota=None))
    if tk == "WEGE3":
        x["c_m5"] = central_rapido(com(emp, anos_ciclo=[str(y) for y in range(2021, 2026)], anos_outras=ANOS))
        x["g1_0"] = central_rapido(com(emp, g1_real=0.0))
        x["g1_12"] = central_rapido(com(emp, g1_real=0.12))
        x["m5"] = median(margem_ano(emp, r, str(y)) for y in range(2021, 2026))
    if tk in ("TIMS3", "VIVT3"):
        x["c_greenwald"] = central_rapido(com(emp, capex_ciclico=False))
    n = r["notas"]
    x["excecao"] = (f"não se aplica (qualidade {br(n['qualidade'], 1)}, solidez {br(n['solidez'], 1)}; exige ≥ 8 e ≥ 7, zero armadilhas)"
                    if not (n["qualidade"] >= 8 and n["solidez"] >= 7) else
                    f"não se aplica — a palavra é {r['palavra']} (a exceção exige preço ≤ 0,80× o central: R$ {br(r['compra_parcial'])})")
    return x


def preencher(s, emp, r, x):
    ki = r["ke_implicito"]
    rep = {"compra": br(r["compra"]), "saida": br(r["saida"]), "central": br(r["central"]), "pc": br(r["pc"]), "palavra": r["palavra"],
           "ke_impl": pct(ki) if ki else "n.d.", "ke_impl_real": pct((1 + ki) / (1 + MK.pi) - 1) if ki else "n.d.",
           "rf_real": pct(MK.rf_real, 2), "ke_nom": pct(MK.ke_nom), "m50": pct(r["op"]["m50"]), "m25": pct(r["op"]["m25"]), "m75": pct(r["op"]["m75"]),
           "m_ltm": pct(x["m_ltm"]), "c_ltm": br(x["c_ltm"]), "pc_ltm": br(x["pc_ltm"]), "roic": pct(r["roic"]), "wacc": pct(r["wacc"]),
           "dl_ebitda": br(r["dl_ebitda"]), "dl": br(r["dl"] / 1e6, 2), "cobertura": br(r["cobertura_juros"], 1) if r["cobertura_juros"] else "n.d.",
           "dpa5": br(r["dpa5"]), "fcfe": br(r["fcfe_acao"]), "dpa_sust": br(r["dpa_sust"]), "dy_liq": pct(r["dy_liq"]), "dy": pct(r["dy"]),
           "fvp": pct(1 - r["fator_defasagem"], 0), "defas": br(emp.defasagem_meses, 0), "aliquota": pct(r["aliquota"], 0),
           "altman": br(r["altman"]), "altman_zona": r["altman_zona"], "piot": str(r["piotroski"]), "pvp": br(x["pvp"]),
           "pl_ltm": br(x["pl_ltm"], 1) if x["pl_ltm"] else "n.d.", "arr": br(x["arr"] / 1e6, 2), "arr_pago": br(x["arr_pago"] / 1e6, 2),
           "rec_meio": br(r["op"]["receita_meio"] / 1e6, 2), "bogle": pct(r["bogle_nom"]), "bogle_real": pct(r["bogle_liq_real"]),
           "lpa_norm": br(r["lpa_norm"]), "sens_m_mais": br(r["sens"][(0, 0.02)]), "sens_m_menos": br(r["sens"][(0, -0.02)]),
           "excecao": x["excecao"], "oe_bi": br((r["oe_norm"] or 0) / 1e6, 2), "ey": pct(r["ey"]), "roc": pct(r["roc"]),
           "epv": br(r["ancoras"].get("EPV", 0)), "dcf": br(r["ancoras"].get("DCF (3 cenários)", 0)),
           "g_impl": (pct(r["g_implicito"]) if r["g_implicito"] is not None and r["g_implicito"] > -0.05 else "n.a.")}
    for k in ("c34", "c_aliq_motor", "c_m5", "g1_0", "g1_12", "c_greenwald"):
        if k in x:
            rep[k] = br(x[k])
    if "m5" in x:
        rep["m5"] = pct(x["m5"])
    rep.update({"g1": pct(WEG_G1), "roe5": pct(WEG_ROE5), "payout_weg": pct(WEG_PAYOUT, 0)})
    for k, val in rep.items():
        s = s.replace("{" + k + "}", val)
    assert "{" not in s, s
    return s


def grafico_margem(emp, r):
    a = CVM[emp.ticker]["anual"]
    anos = [y for y in ANOS if a.get(y, {}).get("receita")]
    fig, ax = plt.subplots(figsize=(3.6, 1.9))
    ax.bar(anos, [100 * a[y]["ebit"] / a[y]["receita"] for y in anos], color="#C9D6E3", width=0.7, label="margem EBIT contábil")
    janela = r["op"]["anos"]
    ax.plot(janela, [100 * margem_ano(emp, r, y) for y in janela], "o", color="#1F3A5F", ms=3, label="sem não recorrentes (janela)")
    ax.axhline(100 * r["op"]["m50"], color="#B83232", lw=1, ls="--", label=f"mediana {janela[0]}–{janela[-1][2:]} {pct(r['op']['m50'])}")
    ax.set_title(f"{emp.ticker} — margem EBIT (%) [CVM]", fontsize=7.5)
    ax.tick_params(labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=60)
    ax.legend(fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=2, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return img(fig, 82)


def cabecalho(story, tk, nome, perfil, r):
    palavra = r["palavra"]
    cor = COR.get(palavra, AZUL)
    cab = Table([[P(f"<font name='Arial-B' size=14 color='#1F3A5F'>{tk}</font>  <font size=9>{nome} · {perfil}</font>", "p"),
                  P(f"<font name='Arial-B' size=12 color='white'>{palavra}</font><font size=7 color='white'> · confiança {r['confianca']}</font>", "p")]],
                colWidths=[120 * mm, 60 * mm], rowHeights=[11 * mm])
    cab.setStyle(TableStyle([("BACKGROUND", (1, 0), (1, 0), cor), ("ALIGN", (1, 0), (1, 0), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (0, 0), 1.2, AZUL)]))
    story.append(cab)
    story.append(Spacer(1, 3))
    return cor


def bloco_final(story, emp_ticker, preco, r, tx, cor, excecao):
    palavra = r["palavra"]
    n = r["notas"]
    qual_txt = (" A saída é 1,50× o central pela exceção de qualidade do §9 (ROIC > WACC a custo de reposição em "
                f"{r['roic_anos_acima']} de {r['roic_anos_total']} exercícios e nota de qualidade {br(r['notas']['qualidade'], 1)})."
                if r.get("saida_por_qualidade") else "")
    saida_txt = (f" <b>Preço acima da saída</b> (R$ {br(preco)} > R$ {br(r['saida'])}): pela doutrina §9 quem tem a ação está fora da faixa de "
                 "manutenção — decisão de venda é do investidor." if preco > r["saida"] else "") + qual_txt
    ver = Table([[P(f"<b>Veredito: <font color='{cor.hexval()}'>{palavra}</font></b> — preço {br(r['pc'])}× o central. "
                    f"Compra R$ {br(r['compra'])} · justo R$ {br(r['central'])} · saída R$ {br(r['saida'])}.{saida_txt} "
                    f"Entrada parcial (exceção §9): {excecao}.<br/>"
                    f"<b>Filtros do hall (§2):</b> {tx['filtros']}<br/>"
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
    an = ANTES[emp_ticker]
    story.append(P(f"<b>De → para (rev. 03/10 → hoje).</b> {an[0]}, central R$ {br(an[1])} → {palavra}, central R$ {br(r['central'])}. "
                   f"{tx['de_para']} Preço inalterado (R$ {br(preco)}, fechamento de 02/10).", "p"))
    story.append(P("<b>Autocrítica (5 linhas).</b> " + " ".join(f"{i + 1}) {t}" for i, t in enumerate(tx["autocritica"])), "p"))
    story.append(P(f"<b>Eventos com data.</b> {tx['agenda']} · {AGENDA}.", "p"))
    story.append(P(f"<b>Não encontrado.</b> {tx['nao_encontrado']}", "pi"))
    story.append(PageBreak())


def tabela_proventos(story, tk, nota):
    dpa, jc = SI[tk]["dpa_por_ano_datacom"], SI[tk]["jcp_por_ano_datacom"]
    yrs = list(range(2021, 2027))
    story.append(tabela([[f"Proventos por data-com [SI]{nota}"] + [str(y) if y < 2026 else "2026 até 02/10" for y in yrs],
                         ["DPA total (R$)"] + [br(dpa.get(str(y), 0), 3) for y in yrs],
                         ["dos quais JCP (R$)"] + [br(jc.get(str(y), 0), 3) for y in yrs]], [50 * mm] + [22 * mm] * 6))
    story.append(Spacer(1, 2))


def ficha(emp, r, rank, story):
    x = extras(emp, r)
    tx = {k: (val if k == "sens_extra" else [preencher(i, emp, r, x) for i in val] if isinstance(val, list) else preencher(val, emp, r, x))
          for k, val in T[emp.ticker].items()}
    cor = cabecalho(story, emp.ticker, emp.nome, PERFIL[emp.ticker], r)
    kpi = [["Preço 02/10", "Valor central", "P/C", "Compra 0,70×", "Saída 1,30×", "Ke implícito", "Vence a RF?", "Nota geral"],
           [f"R$ {br(emp.preco)}", f"R$ {br(r['central'])}", br(r["pc"]) + "×", f"R$ {br(r['compra'])}", f"R$ {br(r['saida'])}",
            pct(r["ke_implicito"]) if r["ke_implicito"] else "n.d.", rf_txt(r), br(r["notas"]["geral"], 1)]]
    story.append(tabela(kpi, [22.5 * mm] * 8, extra=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Círculo de competência.</b> {tx['circulo']}", "p"))
    story.append(Spacer(1, 3))
    ltm = ltm_de(CVM[emp.ticker])
    janela = f"{r['op']['anos'][0]}–{r['op']['anos'][-1]}"
    fatos = [["Fato (12m até jun/2026)", "Valor", "Fonte"],
             ["Receita · EBIT · margem", f"R$ {br(ltm['receita'] / 1e6, 2)} bi · {br(ltm['ebit'] / 1e6, 2)} bi · {pct(ltm['ebit'] / ltm['receita'])}", "[CVM]"],
             ["Receita base", f"R$ {br(r['op']['receita_meio'] / 1e6, 2)} bi ({tx['receita_base']})", "[CVM]"],
             ["Margem EBIT normalizada (p25 · p75)", f"{pct(r['op']['m50'])} ({pct(r['op']['m25'])} · {pct(r['op']['m75'])}), mediana {janela} sem não recorrentes"
              + (f" · quebra estrutural SUSPEITA: a mediana dos 5 últimos exercícios difere {pct(r['op']['divergencia_janela'])} da janela (§11.4) — janela mantida" if r["op"]["quebra_suspeita"] else ""), "[CVM]"],
             ["Ajuste capex de manutenção", pct(r["op"]["ajuste_manut"]) + " da receita" + (" (capex de rede = manutenção)" if emp.capex_ciclico else " (Greenwald)"), "[CVM]"],
             ["Dívida líquida c/ arrendamento · DL/EBITDA 12m", f"R$ {br(r['dl'] / 1e6, 2)} bi · {br(r['dl_ebitda'])}×", "[CVM] 30/06/2026"],
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
            f = f"NOPAT normalizado R$ {br(r['nopat'] / 1e6, 2)} bi ÷ WACC real {pct(r['wacc_real'])} − dívida líquida (com arrendamento) − minoritários"
        elif k.startswith("DCF"):
            d = r["dcf"]
            est = (f"2 estágios: g real {pct(emp.g1_real)} por {emp.anos_g1} anos (reinvestindo g ÷ ROIC), depois {pct(r['gr'], 0)}"
                   if emp.g1_real is not None else f"g real {pct(r['gr'], 0)} perpétuo (zerado se ROIC < WACC)")
            f = (f"FCFF = NOPAT × (1+g) × (1 − g/ROIC); {est}; margem p25/mediana/p75 = R$ {br(d['pessimista'])} / {br(d['base'])} / "
                 f"{br(d['otimista'])}, pesos 25/50/25")
        else:
            f = f"Owner Earnings mediano 5a R$ {br(r['oe_norm'] / 1e6, 2)} bi (com o aluguel pago descontado) ÷ (Ke real − g real)"
        lin.append([k, f"R$ {br(val)}", "ÂNCORA", f])
    oe_txt = ", ".join(f"{a_}: {br(v_ / 1e6, 2)}" for a_, v_ in r["oe"][-5:])
    ac_pc = ltm["ac"] / ltm["pc"]
    a = CVM[emp.ticker]["anual"]
    anos = [y for y in ANOS if a.get(y, {}).get("receita")]
    luc_pos = all(a[y]["lucro"] > 0 for y in anos)
    cres = a[anos[-1]]["lucro"] / a[anos[0]]["lucro"] - 1 if a[anos[0]]["lucro"] > 0 else None
    pl_n = r["pl_atual"]
    f = MK.fator_graham
    crit = [("porte > R$ 10 bi", r["e"] > 1e7), (f"liquidez corrente {br(ac_pc)} ≥ 2", ac_pc >= 2), (f"lucro positivo desde {anos[0]}", luc_pos),
            (f"lucro +1/3 na série ({pct(cres, 0) if cres is not None else 'n.d.'})", cres is not None and cres >= 1 / 3),
            (f"P/L normalizado {br(pl_n, 1) if pl_n else 'n.d.'} ≤ {br(15 * f, 1)}", bool(pl_n) and pl_n <= 15 * f),
            (f"P/L × P/VP ≤ {br(22.5 * f, 1)}", bool(pl_n) and pl_n * emp.preco / r["vpa"] <= 22.5 * f)]
    gi = r["g_implicito"]
    rev_txt = ("n.a. (ROIC < WACC: crescimento não cria valor)" if gi is None else ("≤ −5%" if gi <= -0.05 else pct(gi)))
    lin += [
        ["Lucro normalizado (próprio)", f"LPA R$ {br(r['lpa_norm'])}", "INFORMATIVO",
         "(NOPAT normalizado − juros líquidos após IR, Kd da casa) ÷ ações. Consenso 3 anos: não encontrado"],
        ["Owner Earnings por ano (R$ bi)", oe_txt or "n.d.", "ÂNCORA (acima)",
         "lucro + D&A − capex de manutenção − aumento de capital de giro − aluguel pago (IFRS 16) [CVM]"],
        ["Graham original · Graham-BR", f"R$ {br(r['graham_orig'])} · {br(r['graham_br'])}" if r["graham_orig"] else "n.d.", "INFORMATIVO",
         f"√(22,5 × LPA normalizado × VPA {br(r['vpa'])}); f = {br(f, 3)}"],
        ["Graham revisado-BR", f"R$ {br(r['graham_rev'])}" if r["graham_rev"] else "n.d.", "INFORMATIVO", f"LPA normalizado × (8,5 + 2 × g real {br(100 * r['gr'], 0)}) × f"],
        ["7 critérios do defensivo", f"{sum(1 for _, ok in crit if ok)} de 6", "INFORMATIVO",
         "; ".join(("[sim] " if ok else "[não] ") + n_ for n_, ok in crit) + "; dividendos 20 anos: série de 10"],
        ["Teto de renda (Bazin calibrado)", f"R$ {br(r['teto_renda'])}" if r["teto_renda"] else "N/A", "INFORMATIVO",
         f"DPA sustentável a valor presente (defasagem {br(emp.defasagem_meses, 0)} meses) líquido ÷ RF nominal líquida"
         + ("" if r["coberto"] else " — N/A: dividendo médio acima do FCFE normalizado")],
        ["Bazin original (6%)", f"R$ {br(r['bazin6'])}" if r["bazin6"] else "N/A", "INFORMATIVO", "DPA sustentável ÷ 6%"],
        ["Lynch", f"PEG {br(r['peg'])} · PEGY {br(r['pegy'])}" if r["peg"] else "n.d.", "INFORMATIVO",
         f"categoria: {tx['lynch']}; P/L normalizado ÷ g nominal {pct(r['g_nom'])}"],
        ["Greenblatt (Fórmula Mágica)", f"EY {pct(r['ey'])} · ROC {pct(r['roc'])}", "INFORMATIVO",
         f"EBIT 12m ÷ EV (EV com arrendamento); EBIT ÷ (capital de giro + imobilizado). Posição entre as não financeiras do hall: {rank}"],
        ["DCF reverso", f"g real {rev_txt} · Ke {pct(r['ke_implicito']) if r['ke_implicito'] else 'n.d.'}", "INFORMATIVO",
         ("g real dos 10 primeiros anos que o preço exige (perpetuidade 2%)" if emp.g1_real is not None else
          "crescimento real perpétuo que o preço exige (margem mediana, Ke da casa)") + "; e o Ke que o preço embute"],
        ["Bogle (10 anos)", f"{pct(r['bogle_nom'])} nominal", "INFORMATIVO",
         f"DY sustentável a VP {pct(r['dy'])} + g nominal {pct(r['g_nom'])} + múltiplo {pct(r['dmult'])} · real líquido {pct(r['bogle_liq_real'])}"
         f" · P/L final {br(r['pl_final'], 1) if r['pl_final'] else '—'} (mediana 2016–25 [SI])"],
        ["Altman Z'' (emergentes) · Piotroski · Beneish · Sloan",
         f"{br(r['altman'])} ({r['altman_zona']}) · {r['piotroski']}/9 · {br(r['beneish']) if r['beneish'] is not None else 'n.d.'} · {pct(r['sloan'])}",
         "INFORMATIVO", f"exercício {r['ano_qualidade']} vs anterior [CVM]; Beneish > −1,78 = alerta; Sloan alto e positivo = lucro acima do caixa"],
    ]
    story.append(tabela(lin, [33 * mm, 29 * mm, 21 * mm, 99 * mm]))
    story.append(PageBreak())

    story.append(P(f"{emp.ticker} — reconstrução, sensibilidade e veredito", "h2"))
    rec = [["Âncora", "Valor", "Peso"]] + [[k, f"R$ {br(val)}", "mediana"] for k, val in r["ancoras"].items()]
    rec.append(["<b>Valor central</b>", f"<b>R$ {br(r['central'])}</b>", f"dispersão {br(r['dispersao'])}× · {r['confianca']}"])
    rec.append([f"Com a margem dos 12m ({pct(x['m_ltm'])}) permanente", f"R$ {br(x['c_ltm'])}", f"P/C {br(x['pc_ltm'])} — sensibilidade"])
    for k, nome in tx["sens_extra"]:
        rec.append([nome, f"R$ {br(x[k])}", f"P/C {br(emp.preco / x[k])} — sensibilidade"])
    ts = [["Central (R$)", "margem −2 p.p.", "margem base", "margem +2 p.p."]]
    for dk, nome in ((-0.01, "Ke −1 p.p."), (0, "Ke da casa"), (0.01, "Ke +1 p.p.")):
        ts.append([nome] + [br(r["sens"][(dk, dm)]) for dm in (-0.02, 0, 0.02)])
    lado = Table([[tabela(rec, [44 * mm, 18 * mm, 30 * mm]), tabela(ts, [24 * mm, 20 * mm, 20 * mm, 20 * mm])]], colWidths=[94 * mm, 88 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Controlador.</b> {tx['controlador']}", "p"))
    story.append(Spacer(1, 3))
    tabela_proventos(story, emp.ticker, tx.get("nota_proventos", ""))
    story.append(tabela([["Renda e renda fixa (10 anos, líquido de IR)", "Valor"],
                         ["DPA médio 5a · FCFE normalizado por ação · sustentável", f"R$ {br(r['dpa5'], 3)} · R$ {br(r['fcfe_acao'], 3)} · R$ {br(r['dpa_sust'], 3)}"],
                         ["Defasagem do pagamento → valor presente ao Ke", f"{br(emp.defasagem_meses, 0)} meses → R$ {br(r['dpa_sust_vp'], 3)} ({pct(r['fator_defasagem'] - 1, 1)})"],
                         ["Coberto por caixa?", "Sim" if r["coberto"] else "Não — o dividendo médio supera o FCFE normalizado (entra o menor)"],
                         ["Yield sustentável a VP bruto · líquido", f"{pct(r['dy'])} · {pct(r['dy_liq'])}"],
                         ["Retorno esperado real líquido (Bogle) · sem re-rating", f"{pct(r['bogle_liq_real'])} · {pct(r['so_inv_liq_real'])}"],
                         ["RF real líquida", f"{pct(MK.rf_liq_real, 2)} → Sim ≥ {pct(MK.rf_liq_real + .03, 2)} · Empate ≥ {pct(MK.rf_liq_real + .015, 2)}"],
                         ["Vence a RF?", rf_txt(r) + (" · carimbo: perde para o Tesouro" if r["carimbo_rf"] else "")],
                         ["Trava de coerência: JUSTA → retorno ≈ Ke", "não se aplica (palavra final não é JUSTA)" if r["palavra"] != "JUSTA" else
                          ("passa" if r["trava"] else "falha")]],
                        [95 * mm, 87 * mm]))
    story.append(Spacer(1, 3))
    bloco_final(story, emp.ticker, emp.preco, r, tx, cor, x["excecao"])


# ---------------------------------------------------------------- ITSA4 (holding)
def itsa_extras(r):
    s = sotp_partes(MK)
    x = dict(s)
    x["tir"] = (1 + r["ke_implicito"]) / (1 + MK.pi) - 1 if r["ke_implicito"] else None
    # NAV a mercado: Itaú pelo preço da ITUB4 em 02/10 → desconto de holding implícito
    nav_merc = (ITSA["pl"] - ITSA["itau_contabil"] + ITSA["acoes_itau"] * ITUB4.preco / 1000 - s["custo"] - s["pis"]) * 1000 / N["ITSA4"]
    x["nav_merc"], x["desc_merc"] = nav_merc, 1 - ITSA4.preco / nav_merc
    x["outras_merc"] = s["por_acao"] + (16.6e6 - ITSA["outras_contabil"]) * 1000 / N["ITSA4"]       # demais a mercado pelo RI de 31/08 [H]
    x["itub_r"] = avaliar_fin(ITUB4, MK)
    return x


def itsa_preencher(s, r, x):
    rep = {"compra": br(r["compra"]), "saida": br(r["saida"]), "central": br(r["central"]), "pc": br(r["pc"]), "palavra": r["palavra"],
           "tir": pct(x["tir"]) if x["tir"] is not None else "n.d.", "rf_real": pct(MK.rf_real, 2), "ke_real": pct(MK.ke_real, 2),
           "ke_nom": pct(MK.ke_nom), "roe_lp": pct(ITSA_ROE_LP), "roe_ini": pct(ITSA4.roe_inicio), "payout": pct(ITSA_PAYOUT, 0),
           "itau_ps": br(x["itau_ps"]), "acoes_itau": br(ITSA["acoes_itau"] / 1e6, 1), "pct_itau": pct(ITSA["pct_itau"], 2),
           "itau_justo": br(x["itau_justo"] / 1e6, 1), "itau_contabil": br(ITSA["itau_contabil"] / 1e6, 1), "outras": br(ITSA["outras_contabil"] / 1e6, 1),
           "pl": br(ITSA["pl"] / 1e6, 1), "custo": br(x["custo"] / 1e6, 2), "pis": br(x["pis"] / 1e6, 2), "ga": br(ITSA["ga_12m"] / 1e3, 0), "sotp": br(x["por_acao"]),
           "nav_merc": br(x["nav_merc"]), "desc_merc": pct(x["desc_merc"], 0), "outras_merc": br(x["outras_merc"]),
           "itub_pc": br(x["itub_r"]["pc"]), "caixa": br(ITSA["caixa"] / 1e6, 2), "divida": br(ITSA["divida"] / 1e6, 2), "dy_liq": pct(r["dy_liq"]),
           "bogle_real": pct(r["bogle_liq_real"])}
    for k, val in rep.items():
        s = s.replace("{" + k + "}", val)
    assert "{" not in s, s
    return s


def ficha_itsa(r, story):
    x = itsa_extras(r)
    tx = {k: ([itsa_preencher(i, r, x) for i in v] if isinstance(v, list) else (itsa_preencher(v, r, x) if isinstance(v, str) else v))
          for k, v in T["ITSA4"].items()}
    cor = cabecalho(story, "ITSA4", ITSA4.nome, "holding (Itaú + não financeiras)", r)
    tir = x["tir"]
    kpi = [["Preço 02/10", "Valor central", "P/C", "Compra 0,70×", "Saída 1,30×", "Retorno real implícito", "Vence a RF?", "Nota geral"],
           [f"R$ {br(ITSA4.preco)}", f"R$ {br(r['central'])}", br(r["pc"]) + "×", f"R$ {br(r['compra'])}", f"R$ {br(r['saida'])}",
            pct(tir) if tir is not None else "n.d.", rf_txt(r), br(r["notas"]["geral"], 1)]]
    story.append(tabela(kpi, [22.5 * mm] * 8, extra=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Círculo de competência.</b> {tx['circulo']}", "p"))
    story.append(Spacer(1, 3))
    fatos = [["Fato (holding, controladora, 30/06/2026)", "Valor", "Fonte"],
             ["Patrimônio da holding · VPA", f"R$ {br(ITSA['pl'] / 1e6, 1)} bi · R$ {br(ITSA4.vpa)}", "[CVM] ITR ind."],
             ["Investimentos · dos quais Itaú (contábil)", f"R$ {br(ITSA['investimentos'] / 1e6, 1)} bi · R$ {br(ITSA['itau_contabil'] / 1e6, 1)} bi", "[CVM]"],
             ["Ações do Itaú (look-through)", f"{br(ITSA['acoes_itau'] / 1e6, 1)} mi = {br(ITSA['acoes_itau_diretas'] / 1e6, 1)} diretas + "
              f"{pct(ITSA['fatia_iupar'], 2)} × {br(ITSA['acoes_iupar'] / 1e6, 1)} da IUPAR ({pct(ITSA['pct_itau'], 2)})", "[FRE] 2026"],
             ["Caixa · dívida da holding", f"R$ {br(ITSA['caixa'] / 1e6, 2)} bi · R$ {br(ITSA['divida'] / 1e6, 2)} bi", "[CVM]"],
             ["Lucro 12m · equivalência · G&A", f"R$ {br(ITSA['lucro_12m'] / 1e6, 2)} bi · {br(ITSA['equivalencia_12m'] / 1e6, 2)} bi · "
              f"{br(ITSA['ga_12m'] / 1e3, 0)} mi", "[CVM]"],
             ["Resultado financeiro 12m", f"R$ {br(ITSA['res_fin_12m'] / 1e6, 2)} bi", "[CVM]"],
             ["ROE 12m · longo prazo · payout", f"{pct(ITSA4.roe_inicio)} · {pct(ITSA_ROE_LP)} (mediana 2016–25) · {pct(ITSA_PAYOUT, 0)}", "[CVM][SI]"]]
    lado = Table([[tabela(fatos, [38 * mm, 46 * mm, 13 * mm]), grafico_roe("ITSA4", r, ITSA4)]], colWidths=[98 * mm, 84 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)
    story.append(P("Quadro clássico (doutrina §11) — ao Ke da casa", "h3"))
    an = r["ancoras"]
    proj = projecao(ITSA4, 3)
    f = MK.fator_graham
    lin = [["Método", "Valor", "Marca", "Fórmula / insumos"],
           ["SOTP", f"R$ {br(an['SOTP'])}", "ÂNCORA",
            f"PL da holding R$ {br(ITSA['pl'] / 1e6, 1)} bi − Itaú contábil {br(ITSA['itau_contabil'] / 1e6, 1)} + Itaú ao central da casa "
            f"({br(ITSA['acoes_itau'] / 1e6, 0)} mi × R$ {br(x['itau_ps'])} = {br(x['itau_justo'] / 1e6, 1)}) − custo da holding {br(x['custo'] / 1e6, 2)} "
            f"(G&A {br(ITSA['ga_12m'] / 1e3, 0)} mi ÷ Ke real) − PIS/Cofins sobre JCP recebido até 2027 {br(x['pis'] / 1e6, 2)}; demais participações a "
            f"valor contábil (R$ {br(ITSA['outras_contabil'] / 1e6, 1)} bi)"],
           ["DDM 2 estágios", f"R$ {br(an['DDM 2 estágios'])}", "ÂNCORA",
            f"ROE {pct(ITSA4.roe_inicio)} → {pct(ITSA_ROE_LP)} em 5 anos; payout {pct(ITSA_PAYOUT, 0)}; terminal = P/VP justificado"],
           ["P/VP justificado", f"{br(r['pvp_just'])}× VPA = R$ {br(r['pvp_just'] * ITSA4.vpa)}", "INFORMATIVO",
            f"(ROE {pct(ITSA_ROE_LP)} − g {pct(r['g'])}) ÷ (Ke {pct(MK.ke_nom, 2)} − g) — perfil holding usa SOTP + DDM (§11.2)"],
           ["NAV com o Itaú a mercado", f"R$ {br(x['nav_merc'])}", "INFORMATIVO",
            f"ITUB4 a R$ {br(ITUB4.preco)} (02/10): desconto de holding implícito {pct(x['desc_merc'], 0)}"],
           ["Lucro projetado (próprio)", " · ".join(f"R$ {br(p[2])}" for p in proj), "INFORMATIVO", "LPA anos 1–3 (ROE convergindo; VPA cresce pela retenção). Consenso: não encontrado"],
           ["Graham original · Graham-BR", f"R$ {br(r['graham_orig'])} · {br(r['graham_br'])}", "INFORMATIVO", f"√(22,5 × LPA normalizado {br(r['lpa_norm'])} × VPA); f = {br(f, 3)}"],
           ["Teto de renda (Bazin calibrado)", f"R$ {br(r['teto_renda'])}" if r["teto_renda"] else "N/A", "INFORMATIVO",
            f"DPA sustentável líquido {br(r['dpa_sust_liq'], 3)} ÷ RF nominal líquida {pct(MK.rf_liq_nom, 2)}"],
           ["Bazin original (6%)", f"R$ {br(r['bazin6'])}", "INFORMATIVO", "DPA sustentável ÷ 6%"],
           ["DCF reverso", f"ROE {pct(r['roe_implicito'], 0)}", "INFORMATIVO", "ROE perpétuo que o preço exige ao Ke da casa"],
           ["Bogle (10 anos)", f"{pct(r['bogle_nom'])} nominal", "INFORMATIVO",
            f"investimento (DY {pct(r['dy'])} + g {pct(r['g'])}) = {pct(r['ret_investimento'])} · especulativo (P/L {br(r['pl_atual'], 1)} → "
            f"{br(r['pl_final'], 1) if r['pl_final'] else '—'}) = {pct(r['ret_especulativo'])} · real líquido {pct(r['bogle_liq_real'])}"],
           ["Greenblatt · EPV · Owner Earnings · Altman", "N/A", "N/A por perfil", "holding de participações: o lucro é equivalência patrimonial"]]
    story.append(tabela(lin, [33 * mm, 27 * mm, 21 * mm, 101 * mm]))
    story.append(PageBreak())
    story.append(P("ITSA4 — reconstrução, renda e veredito", "h2"))
    rec = [["Âncora", "Valor", "Peso"]] + [[k, f"R$ {br(v)}", "mediana"] for k, v in r["ancoras"].items()]
    rec.append(["<b>Valor central</b>", f"<b>R$ {br(r['central'])}</b>", f"dispersão {br(r['dispersao'])}× · {r['confianca']}"])
    rec += [[f"SOTP com as demais a mercado (RI 31/08, R$ 16,6 bi [H])", f"R$ {br(x['outras_merc'])}", "sensibilidade"],
            [f"SOTP com o Itaú a mercado (R$ {br(ITUB4.preco)})", f"R$ {br(x['nav_merc'])}", "sensibilidade — não é valor da casa"]]
    ts = [["Central (R$)", "ROE −2 p.p.", "ROE base", "ROE +2 p.p."]]
    for dk, nome in ((-0.01, "Ke −1 p.p."), (0, "Ke da casa"), (0.01, "Ke +1 p.p.")):
        ts.append([nome] + [br(r["sens"][(dk, dr)]) for dr in (-0.02, 0, 0.02)])
    lado = Table([[tabela(rec, [44 * mm, 18 * mm, 30 * mm]), tabela(ts, [24 * mm, 20 * mm, 20 * mm, 20 * mm])]], colWidths=[94 * mm, 88 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)
    story.append(P("ROE ±2 p.p. move só o DDM (o SOTP depende do Itaú, que se move com o Ke).", "pi"))
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Controlador.</b> {tx['controlador']}", "p"))
    story.append(Spacer(1, 3))
    tabela_proventos(story, "ITSA4", "")
    story.append(tabela([["Renda e renda fixa (10 anos, líquido de IR)", "Valor"],
                         ["Yield sustentável bruto · líquido (JCP × 0,825)", f"{pct(r['dy'])} · {pct(r['dy_liq'])}"],
                         ["Coberto por caixa?", "Sim — dividendos recebidos do Itaú cobrem os pagos; entra o menor entre DPA médio e o que o lucro paga"],
                         ["Retorno esperado real líquido (Bogle) · sem re-rating", f"{pct(r['bogle_liq_real'])} · {pct(r['so_inv_liq_real'])}"],
                         ["RF real líquida", f"{pct(MK.rf_liq_real, 2)} → Sim ≥ {pct(MK.rf_liq_real + .03, 2)} · Empate ≥ {pct(MK.rf_liq_real + .015, 2)}"],
                         ["Vence a RF?", rf_txt(r) + (" · carimbo: perde para o Tesouro" if r["carimbo_rf"] else "")],
                         ["Trava de coerência: JUSTA → retorno ≈ Ke", "não se aplica (palavra final não é JUSTA)"]],
                        [95 * mm, 87 * mm]))
    story.append(Spacer(1, 3))
    bloco_final(story, "ITSA4", ITSA4.preco, r, tx, cor, "não se aplica (palavra CARA)")


# ---------------------------------------------------------------- ranking Greenblatt do hall
def ranking_hall():
    """EY e ROC de todas as não financeiras do hall (Lotes 3, 4, 5 e 6), sem as que saíram. Financeiras, holdings e concessões: N/A."""
    lin = []
    for lote, emps in (("3", lote3_agro.EMPRESAS), ("4", EMPRESAS), ("5", lote5_petroleo.EMPRESAS), ("6", lote6_quimica.EMPRESAS)):
        for e in emps:
            if e.ticker in FORA_DO_HALL:
                continue
            r = avaliar(e, MK)
            lin.append(dict(ticker=e.ticker, lote=lote, ey=r["ey"] or -1, roc=r["roc"] or -1, palavra=r["palavra"]))
    ey = sorted(lin, key=lambda z: -z["ey"])
    roc = sorted(lin, key=lambda z: -z["roc"])
    for z in lin:
        z["rey"], z["rroc"] = ey.index(z) + 1, roc.index(z) + 1
        z["soma"] = z["rey"] + z["rroc"]
    lin.sort(key=lambda z: (z["soma"], z["rey"]))
    for i, z in enumerate(lin):
        z["pos"] = i + 1
    return lin


# ---------------------------------------------------------------- capa e metodologia
def capa(res, rank, story):
    story.append(P("Fichas de Avaliação — Value Investing B3", "h1"))
    story.append(P(f"Lote 4 — Saúde, telecom e blue chips (7 empresas) · rev. 05/10/2026 · data-base {DATA_BASE} · doutrina v2.2", "h2"))
    cont = {}
    for r in res:
        cont[r["palavra"]] = cont.get(r["palavra"], 0) + 1
    resumo = " · ".join(f"{k}: {v}" for k, v in sorted(cont.items()))
    acima = [r["ticker"] for r in res if r["preco_"] > r["saida"]]
    box = (f"<b>Conclusão.</b> Ao Ke da casa ({pct(MK.ke_nom)} nominal = Tesouro IPCA+ {pct(MK.rf_real, 2)} + 5 p.p.), o lote inteiro fica "
           f"<b>{resumo}</b>: o preço de hoje embute retornos de {pct(min(r['ke_implicito'] for r in res if r['ke_implicito']))} a "
           f"{pct(max(r['ke_implicito'] for r in res if r['ke_implicito']))} nominais (Ke implícito), abaixo dos {pct(MK.ke_nom)} exigidos. "
           "<b>Nenhuma compra autorizada.</b> TIMS3 e VIVT3 perdem o RADAR (o central de 03/10 era o de 07/09 × fator de Ke, sem margem "
           "normalizada nem arrendamento na dívida); ITSA4, FLRY3 e HYPE3 perdem o JUSTA. Só ABEV3 e WEGE3 criam valor (ROIC acima do WACC); "
           "nas demais o retorno sobre o capital fica abaixo do custo. "
           + (f"<b>Acima da saída (1,30× o central): {', '.join(acima)}</b> — ITSA4 está na carteira." if acima else ""))
    tb = Table([[P(box, "box")]], colWidths=[182 * mm])
    tb.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, AZUL), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF3F9")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(tb)
    story.append(P("Quadro-resumo", "h3"))
    q = [["Ticker", "Palavra", "Preço", "Central", "P/C", "Compra", "Saída", "Ke implícito", "Retorno × custo", "Greenblatt", "Vence RF", "Nota", "03/10"]]
    for r in sorted(res, key=lambda z: z["pc"]):
        an = ANTES[r["ticker"]]
        rc = (f"ROIC {pct(r['roic'], 0)} × WACC {pct(r['wacc'], 0)}" if "roic" in r else f"ROE {pct(ITSA_ROE_LP, 0)} × Ke {pct(MK.ke_nom, 0)}")
        q.append([r["ticker"], f"<font color='{COR.get(r['palavra'], AZUL).hexval()}'><b>{r['palavra']}</b></font>",
                  br(r["preco_"]), br(r["central"]), br(r["pc"]), br(r["compra"]), br(r["saida"]),
                  pct(r["ke_implicito"]) if r["ke_implicito"] else "n.d.", rc, f"{rank[r['ticker']]}º" if r["ticker"] in rank else "N/A",
                  r["vence_rf"] + ("*" if r["so_com_rerating"] else ""), br(r["notas"]["geral"], 1), f"{an[0]} {br(an[1])}"])
    story.append(tabela(q, [13 * mm, 15 * mm, 11 * mm, 12 * mm, 10 * mm, 12 * mm, 12 * mm, 14 * mm, 27 * mm, 15 * mm, 12 * mm, 9 * mm, 20 * mm]))
    story.append(Spacer(1, 4))
    story.append(grafico_resumo([dict(r, pc=min(r["pc"], 2.8)) for r in res]))
    story.append(P("Greenblatt = posição entre as não financeiras de todo o hall (19, Lotes 3–6) pela soma dos rankings de EY (EBIT 12m ÷ EV) e ROC "
                   "— ver a página do ranking; ITSA4 N/A (holding). * o resultado muda sem re-rating (ver ficha). WEGE3 aparece cortada em 2,8× no gráfico.", "pi"))
    story.append(PageBreak())
    story.append(P("Premissas e metodologia (o que é novo em relação aos Lotes 1–6)", "h2"))
    met = [["Item", "Regra"],
           ["Mercado", f"Tesouro IPCA+ 2050 sem cupom {pct(MK.rf_real, 2)} (fechamento de 02/10) · inflação implícita ANBIMA 10a {pct(MK.pi, 2)} · Ke real "
                       f"{pct(MK.ke_real, 2)} · Ke nominal {pct(MK.ke_nom, 2)} · RF real líquida {pct(MK.rf_liq_real, 2)} — o mesmo dos Lotes 1–6."],
           ["Dados", "Demonstrações consolidadas da CVM (DFP 2016–25 + ITR; 12m até jun/2026) — fonte A. TIM: TIM Participações (CVM 017639) até 2019 e "
                     "TIM S.A. (024929) depois; em 2024–25 a TIM S.A. entregou o consolidado zerado (sem controladas) → individual. Preço: fechamento de "
                     "02/10 (PDF rev. 03/10). Ações: ITR de jun/2026 sem tesouraria. Controladores e participação da Itaúsa no Itaú: FRE 2026 da CVM."],
           ["IFRS 16 (TIMS3, VIVT3, FLRY3)", "Arrendamento dentro da dívida líquida; margem só de 2019–25 (antes de 2019 o aluguel estava no EBIT — "
                                             "usar as duas coisas contaria o aluguel duas vezes); Owner Earnings desconta o aluguel pago (a D&A somada "
                                             "de volta inclui o direito de uso). VIVT3: DFC mistura arrendamento e empréstimos → proxy = parcela "
                                             "circulante do passivo de arrendamento do ano anterior, limitada ao principal pago menos a dívida financeira que vencia (o mesmo para "
                                             "WEGE3, que paga o arrendamento na linha de empréstimos)."],
           ["Telecom", "Capex de rede tratado como manutenção (reposição tecnológica; a receita cresce por preço e inflação) — mediana de capex ÷ receita "
                       "contra D&A ÷ receita, como nas cíclicas. 'Outras' líquidas (3.04.04 + 3.04.05): as duas lançam pares de ganho e perda."],
           ["Compounder (WEGE3)", f"DCF em 2 estágios: g real {pct(WEG_G1)} por 10 anos = ROE mediano 2021–25 {pct(WEG_ROE5)} × retenção "
                                  f"{pct(1 - WEG_PAYOUT, 0)} (sem o extraordinário de dez/25), deflacionado; depois 2% real (PIB de longo prazo). "
                                  "Reinvestimento = g ÷ ROIC; só com ROIC > WACC. DCF reverso dá o g de 10 anos que o preço exige."],
           ["Holding (ITSA4)", "SOTP + DDM (§11.2). SOTP = patrimônio da holding − Itaú contábil + Itaú ao central da casa (ITUB4 do Lote 1, recalculado "
                               "ao mesmo Ke) − G&A capitalizado; demais participações a valor contábil (conservador). Desconto de holding = o custo "
                               "capitalizado e o PIS/Cofins sobre o JCP recebido até a mudança de 2027 (15 meses, a valor presente), declarados; sem desconto adicional."],
           ["Alíquota", "Mediana de 5 anos entre 15% e 34% (§2). ABEV3: média 2024–25 (21%) — a Lei 14.789/2023 passou a tributar a subvenção de ICMS. "
                        "HYPE3: crédito de IR com prazo → efetiva até 2030 e 34% depois (v2.3; sensibilidade a 34% já na ficha). TIMS3: mediana 5,4% sem origem declarada → 34%."],
           ["Proventos", "Defasagem do pagamento trazida a valor presente ao Ke nominal (§6.3): HYPE3 18 meses, VIVT3 10, FLRY3 9, WEGE3 9, ABEV3 6, "
                         "TIMS3 4. VIVT3 sem redução de capital (R$ 1,25 em 2026); ABEV3 com o JCP de jun/26 corrigido (R$ 0,0449)."],
           ["Coletor e motor (valem para todos os lotes)", "Coletor: consolidado zerado → individual; código CVM sucessor; capex em linha só com o "
                                                 "nome da conta (WEG); aluguel pago da DFC sem juros nem linha mista. Motor (achado do adversário): "
                                                 "reinvestimento do DCF = g real ÷ ROIC real (Fisher); antes dividia pelo ROIC nominal. Efeito nos outros "
                                                 "lotes, sem mudança de palavra: B3SA3 9,23 → 8,90 · KEPL3 6,63 → 6,58 · LEVE3 36,82 → 36,76 (PDFs dos "
                                                 "Lotes 3 e 6 reemitidos). Cobertura de juros: desde 06/10 usa os juros pagos da DFC (sem variação cambial); "
                                                 "sem a linha, cai na despesa bruta."],
           ["Controlador", "Desconto zero nas sete, com a razão escrita em cada ficha (nenhuma interferência consumada)."]]
    story.append(tabela(met, [36 * mm, 146 * mm]))
    story.append(PageBreak())


def pagina_ranking(lin, story):
    story.append(P("Ranking Greenblatt (Fórmula Mágica) — todas as não financeiras do hall", "h2"))
    t = [["Posição", "Ticker", "Lote", "EY (EBIT 12m ÷ EV)", "Rank EY", "ROC (EBIT ÷ capital)", "Rank ROC", "Soma", "Palavra"]]
    for z in lin:
        t.append([f"{z['pos']}º", z["ticker"], z["lote"], pct(z["ey"]) if z["ey"] > -1 else "n.d.", str(z["rey"]),
                  pct(z["roc"]) if z["roc"] > -1 else "n.d.", str(z["rroc"]), str(z["soma"]),
                  f"<font color='{COR.get(z['palavra'], AZUL).hexval()}'>{z['palavra']}</font>"])
    story.append(tabela(t, [15 * mm, 18 * mm, 12 * mm, 28 * mm, 16 * mm, 30 * mm, 17 * mm, 14 * mm, 32 * mm]))
    story.append(P("EY = EBIT de 12m até jun/2026 ÷ (valor de mercado a 02/10 + dívida líquida com arrendamento); ROC = EBIT ÷ (capital de giro "
                   "operacional positivo + imobilizado líquido) [CVM]. Fora: bancos, seguradoras, holdings e concessões (N/A por perfil) e quem saiu do "
                   "hall (UNIP6, VBBR3). O ranking ordena; não substitui o veredito — a compra continua dependendo só do preço ÷ central (§9).", "pi"))
    story.append(PageBreak())


def main():
    res, inds = [], []
    for e in EMPRESAS:
        r = avaliar(e, MK)
        r["preco_"] = e.preco
        res.append(r)
    ri = avaliar_fin(ITSA4, MK)
    ri["preco_"], ri["ticker"] = ITSA4.preco, "ITSA4"
    lin = ranking_hall()
    rank_hall = {z["ticker"]: z["pos"] for z in lin}
    rank_txt = {tk: f"{p}º de {len(lin)}" for tk, p in rank_hall.items()}
    todos = res + [ri]
    doc = SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=14 * mm,
                            title=f"Lote 4 — Saúde, telecom e blue chips · rev. {REV.replace('-', '/')}", author="Mesa de Value Investing")

    def rodape(c, d):
        c.saveState()
        c.setFont("Arial", 6.5)
        c.setFillColor(colors.HexColor("#6B7280"))
        c.drawString(15 * mm, 9 * mm, f"Mesa de Value Investing — Lote 4 Saúde, telecom e blue chips · rev. 05/10/2026 · data-base {DATA_BASE} · "
                                      "doutrina v2.2 · não é recomendação de investimento")
        c.drawRightString(195 * mm, 9 * mm, f"p. {d.page}")
        c.restoreState()

    story = []
    capa(todos, rank_hall, story)
    pagina_ranking(lin, story)
    for r in sorted(todos, key=lambda z: z["pc"]):
        if r["ticker"] == "ITSA4":
            ficha_itsa(r, story)
        else:
            e = next(x for x in EMPRESAS if x.ticker == r["ticker"])
            ficha(e, r, rank_txt[e.ticker], story)
    story.append(P("Apêndice — fontes", "h2"))
    story.append(tabela([["Rótulo", "Fonte"],
                         ["[CVM]", "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/ e /ITR/DADOS/ (cache em ferramentas/dados/cvm)"],
                         ["[FRE]", "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/FRE/DADOS/fre_cia_aberta_2026.zip — posição acionária (controladores; Itaúsa/IUPAR no Itaú)"],
                         ["[SI]", "https://statusinvest.com.br (proventos por data-com; ROE, LPA e P/L históricos) — 05/10/2026"],
                         ["Mercado", "Tesouro Transparente (IPCA+ 2050 sem cupom 7,06%), ANBIMA ETTJ (inflação implícita 6,46%) — o mesmo dos Lotes 1–6"],
                         ["PDF 06/09 · 03/10", "Fichas anteriores (pasta SAÚDE, TELECOM E BLUECHIPS): eventos, proventos declarados, defasagens, gatilhos, "
                                               "agenda — fontes primárias citadas lá; extraídas em ferramentas/dados/fatos_lote4.json"]],
                        [30 * mm, 152 * mm]))
    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    print("gerado:", SAIDA)
    for r in sorted(todos, key=lambda z: z["pc"]):
        print(r["ticker"], r["palavra"], round(r["central"], 2), round(r["pc"], 2), "rank", rank_hall.get(r["ticker"]))
    print("ranking:", [(z["pos"], z["ticker"]) for z in lin])


if __name__ == "__main__":
    main()
