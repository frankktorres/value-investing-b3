"""PDF do Lote 3 (Papel e celulose, infraestrutura de mercado e agro) — doutrina v2.5. Uso: python gerar_pdf_lote3.py"""
from ltm import ltm_de
import copy
import pathlib
import sys

import matplotlib.pyplot as plt
from historico_arquivos import guardar
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle

import gerar_pdf_lote1 as g1
from gerar_pdf_lote1 import AZUL, br, COR, grafico_resumo, img, LINHA, nota_f2, P, pct, tabela
from lote1_bancos import DATA_BASE, MK
from lote3_agro import EMPRESAS
from lote3_textos import AGENDA, ANTES, T
from motor_nao_financeiras import CVM, SI, avaliar, premissas_operacionais

sys.stdout.reconfigure(encoding="utf-8")
SAIDA = pathlib.Path(__file__).parent.parent / "AGRO E B3" / "Infra_Agro_rev_09-10-2026.pdf"
ARBEX_DIVIDA = 12e6   # R$ mil — só para a alavancagem pró-forma da SUZB3 (PDF 03/10)


def rodape(c, d):
    c.saveState()
    c.setFont("Arial", 6.5)
    c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(15 * mm, 9 * mm, f"Mesa de Value Investing — Lote 3 Papel e celulose, B3 e agro · rev. 09/10/2026 · data-base {DATA_BASE} · "
                                  "doutrina v2.5 · não é recomendação de investimento")
    c.drawRightString(195 * mm, 9 * mm, f"p. {d.page}")
    c.restoreState()


def extras(emp, r):
    a, ltm = CVM[emp.ticker]["anual"], ltm_de(CVM[emp.ticker])
    x = {}
    x["dl_ebitda_pf"] = (r["dl"] + (ARBEX_DIVIDA if emp.ticker == "SUZB3" else 0)) / r["ebitda_ltm"] if r["ebitda_ltm"] > 0 else None
    ult = a["2026" if emp.ticker == "SMTO3" else "2025"]
    x["vj_ebit"] = (ult.get("vj_biologico") or 0) / ult["ebit"] if ult.get("ebit") else 0
    x["pl_ltm"] = emp.preco / (ltm["lucro"] / r["n"]) if ltm.get("lucro") and ltm["lucro"] > 0 else None
    if emp.ticker == "SLCE3":
        e2 = copy.deepcopy(emp)
        e2.reproducao_por_acao = None
        x["central_sem_nav"] = avaliar(e2, MK)["central"]
    if emp.ticker in ("SUZB3", "B3SA3"):
        e3 = copy.deepcopy(emp)
        e3.aliquota = 0.34
        r3 = avaliar(e3, MK)
        x["epv34"], x["central34"] = r3["epv"], r3["central"]
    if r["trava"] is None:
        x["trava_txt"] = "não se aplica (palavra não é JUSTA)."
    elif r["trava"]:
        x["trava_txt"] = f"passa — Bogle {pct(r['bogle_nom'])} a ±2 p.p. do Ke nominal {pct(r["ke_nom_emp"])}."
    else:
        fy = r["fcfe_acao"] / emp.preco + r["g_nom"] + r["dmult"]
        x["trava_txt"] = (f"falha pelo Bogle de dividendos ({pct(r['bogle_nom'])} vs Ke {pct(r["ke_nom_emp"])}): o dividendo paga só parte do FCFE; "
                          f"com o FCFE inteiro (desalavancagem retida) o retorno é {pct(fy)} — a diferença é o caixa retido, não erro do central.")
    return x


def preencher(s, emp, r, x):
    gi = r["g_implicito"]
    g_txt = ("não alcançável — com ROIC abaixo do WACC crescer não cria valor" if gi is None else ("≤ −5%" if gi <= -0.05 else pct(gi)))
    rep = {"compra": br(r["compra"]), "ke_impl": pct(r["ke_implicito"]), "g_impl": g_txt, "central": br(r["central"]),
           "pc": br(r["pc"]), "m50": pct(r["op"]["m50"]), "m25": pct(r["op"]["m25"]), "piotroski": str(r["piotroski"]),
           "beneish": br(r["beneish"]) if r["beneish"] is not None else "n.d.", "dl_ebitda": br(r["dl_ebitda"]),
           "dy_liq": pct(r["dy_liq"]), "dcf_pess": br(r["dcf"]["pessimista"]), "aliquota": pct(r["aliquota"], 0), "altman": br(r["altman"]),
           "altman_zona": r["altman_zona"], "cobertura": br(r["cobertura_juros"], 1) if r["cobertura_juros"] else "n.d.",
           "sens_m_mais": br(r["sens"][(0, 0.02)]), "dispersao": br(r["dispersao"]), "roc": pct(r["roc"]), "ey": pct(r["ey"]),
           "trava_txt": x["trava_txt"], "roic": pct(r["roic"]), "wacc": pct(r["wacc"]), "pl_ltm": br(x["pl_ltm"], 1) if x["pl_ltm"] else "n.d.",
           "aj_pct": pct(-r["op"]["ajuste_manut"]), "oe_mi": br(r["oe_norm"] / 1e3, 0) if r["oe_norm"] else "n.d.",
           "reprod": br(r["reprod"]), "central_sem_nav": br(x.get("central_sem_nav", 0)),
           "epv34": br(x.get("epv34", 0)), "central34": br(x.get("central34", 0)), "palavra": r["palavra"],
           "vj_ebit": pct(x["vj_ebit"], 0)}
    for k, val in rep.items():
        s = s.replace("{" + k + "}", val)
    return s


def grafico_margem(emp, r):
    a = CVM[emp.ticker]["anual"]
    anos = r["op"]["anos"]
    fig, ax = plt.subplots(figsize=(3.6, 1.9))
    ax.bar(anos, [100 * a[x]["ebit"] / a[x]["receita"] for x in anos], color="#8DA9C4", width=0.7)
    ax.axhline(100 * r["op"]["m50"], color="#1F3A5F", lw=1, ls="--", label=f"mediana {pct(r['op']['m50'])}")
    if r["op"]["ajuste_manut"] < 0:
        ax.axhline(100 * (r["op"]["m50"] + r["op"]["ajuste_manut"]), color="#B83232", lw=1, label="mediana − capex de manutenção acima da D&A")
    ax.set_title(f"{emp.ticker} — margem EBIT anual (%) [CVM]", fontsize=7.5)
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
    if nc:       # §9: sem palavra não há preço de compra nem de saída (o texto da ficha falava em "compra ≤ R$ …")
        tx["capital"] = f"Não. NÃO CONCLUSIVO ({br(r['pc'])}× o central): sem palavra não há preço de compra nem de saída (§9)."
    cor = COR.get(palavra, AZUL)
    cab = Table([[P(f"<font name='Arial-B' size=14 color='#1F3A5F'>{emp.ticker}</font>  <font size=9>{emp.nome} · {emp.perfil}</font>", "p"),
                  P(f"<font name='Arial-B' size=12 color='white'>{palavra}</font><font size=7 color='white'> · confiança {r['confianca']}</font>", "p")]],
                colWidths=[120 * mm, 60 * mm], rowHeights=[11 * mm])
    cab.setStyle(TableStyle([("BACKGROUND", (1, 0), (1, 0), cor), ("ALIGN", (1, 0), (1, 0), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (0, 0), 1.2, AZUL)]))
    story.append(cab)
    story.append(Spacer(1, 3))
    kpi = [["Preço 02/10", "Valor central", "P/C", "Compra 0,70×", "Saída 1,30×", "Ke implícito", "Vence a RF?", "Nota geral"],
           [f"R$ {br(emp.preco)}", f"R$ {br(r['central'])}", br(r["pc"]) + "×", "n.a." if nc else f"R$ {br(r['compra'])}", "n.a." if nc else f"R$ {br(r['saida'])}",
            pct(r["ke_implicito"]), r["vence_rf"] + (" (só com re-rating)" if r["so_com_rerating"] else ""), br(r["notas"]["geral"], 1)]]
    story.append(tabela(kpi, [22.5 * mm] * 8, extra=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Círculo de competência.</b> {tx['circulo']}", "p"))
    story.append(Spacer(1, 3))
    ltm = ltm_de(CVM[emp.ticker])
    per = "exercício até mar/2026" if emp.ticker == "SMTO3" else "12m até jun/2026"
    fatos = [["Fato (" + per + ")", "Valor", "Fonte"],
             ["Receita · EBIT · margem", f"R$ {br(ltm['receita'] / 1e6, 1)} bi · {br(ltm['ebit'] / 1e6, 2)} bi · {pct(ltm['ebit'] / ltm['receita'])}", "[CVM]"],
             ["Receita de meio de ciclo · margem normalizada", f"R$ {br(r['op']['receita_meio'] / 1e6, 1)} bi · {pct(r['op']['m50'])} (p25 {pct(r['op']['m25'])} · p75 {pct(r['op']['m75'])})", "[CVM] mediana 10a"],
             ["Ajuste capex de manutenção (Greenwald)", pct(r["op"]["ajuste_manut"]) + " da receita", "[CVM] 5 exercícios"],
             ["Dívida líquida · DL/EBITDA", f"R$ {br(r['dl'] / 1e6, 1)} bi · {br(r['dl_ebitda'])}×" + (f" (pró-forma Arbex {br(x['dl_ebitda_pf'])}×)" if emp.ticker == 'SUZB3' else ""), "[CVM] 30/06/2026"],
             ["Cobertura de juros (EBIT ÷ juros)", f"{br(r['cobertura_juros'], 1) if r['cobertura_juros'] else 'n.d.'}× ({r['cobertura_fonte']})", "[CVM]"],
             ["ROIC normalizado · WACC", f"{pct(r['roic'])} contábil · {pct(r['roic_reposicao'])} a custo de reposição "
               f"(imobilizado de {r['idade_imobilizado']:.1f} anos corrigido pelo IPCA) · WACC {pct(r['wacc'])} "
               f"(Kd {pct(r['kd'])}; IR efetivo {pct(r['aliquota'], 0)}). O menor decide o filtro 1, a nota e a trava do crescimento", "motor"],
             ["P/L 12m · P/VP", f"{br(x['pl_ltm'], 1) if x['pl_ltm'] else 'n.d.'}× · {br(emp.preco / r['vpa'])}×", "[SI]/[CVM]"]]
    lado = Table([[tabela(fatos, [40 * mm, 40 * mm, 17 * mm]), grafico_margem(emp, r)]], colWidths=[98 * mm, 84 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)

    story.append(P("Quadro clássico (doutrina §11) — ao Ke da casa", "h3"))
    lin = [["Método", "Valor", "Marca", "Fórmula / insumos"]]
    for k, val in r["ancoras"].items():
        if k.startswith("EPV"):
            f = f"NOPAT normalizado R$ {br(r['nopat'] / 1e6, 2)} bi ÷ WACC real {pct(r['wacc_real'])} − dívida líquida − minoritários"
        elif k.startswith("DCF"):
            d = r["dcf"]
            f = (f"FCFF = NOPAT × (1+g) × (1 − g/ROIC), g real {pct(r['gr'], 0)}; cenários margem p25/mediana/p75 = "
                 f"R$ {br(d['pessimista'])} / {br(d['base'])} / {br(d['otimista'])}, pesos 25/50/25")
        elif k.startswith("Valor de repro"):
            f = emp.reproducao_fonte
        else:
            f = f"Owner Earnings mediano R$ {br(r['oe_norm'] / 1e6, 2)} bi ÷ (Ke real − g real)"
        lin.append([k, f"R$ {br(val)}", "ÂNCORA", f])
    oe_txt = ", ".join(f"{a}: {br(v / 1e6, 2)}" for a, v in r["oe"][-5:])
    g7 = []
    ac_pc = ltm["ac"] / ltm["pc"]
    a = CVM[emp.ticker]["anual"]
    anos = r["op"]["anos"]
    luc_pos = all(a[y]["lucro"] > 0 for y in anos)
    cres = a[anos[-1]]["lucro"] / a[anos[0]]["lucro"] - 1 if a[anos[0]]["lucro"] > 0 else None
    pl_n = r["pl_atual"]
    f = MK.fator_graham
    crit = [("porte > R$ 10 bi", r["e"] > 1e7), (f"liquidez corrente {br(ac_pc)} ≥ 2", ac_pc >= 2), ("lucro positivo em 10 anos", luc_pos),
            (f"lucro +1/3 em 10 anos ({pct(cres, 0) if cres is not None else 'n.d.'})", cres is not None and cres >= 1 / 3),
            (f"P/L normalizado {br(pl_n, 1) if pl_n else 'n.d.'} ≤ {br(15 * f, 1)}", bool(pl_n) and pl_n <= 15 * f),
            (f"P/L × P/VP ≤ {br(22.5 * f, 1)}", bool(pl_n) and pl_n * emp.preco / r["vpa"] <= 22.5 * f)]
    lin += [
        ["Lucro normalizado (próprio)", f"LPA R$ {br(r['lpa_norm'])}", "INFORMATIVO",
         "meio de ciclo: (NOPAT normalizado − juros líquidos após IR) ÷ ações. Consenso 3 anos: não encontrado no material"],
        ["Owner Earnings por ano (R$ bi)", oe_txt or "n.d.", "INFORMATIVO", "lucro + D&A − capex de manutenção (Greenwald, piso 0) − aumento de capital de giro [CVM]"],
        ["Graham original · Graham-BR", f"R$ {br(r['graham_orig'])} · {br(r['graham_br'])}" if r["graham_orig"] else "n.d.", "INFORMATIVO",
         f"√(22,5 × LPA normalizado × VPA {br(r['vpa'])}); f = {br(f, 3)}"],
        ["Graham revisado-BR", f"R$ {br(r['graham_rev'])}" if r["graham_rev"] else "n.d.", "INFORMATIVO", f"LPA normalizado × (8,5 + 2 × g real {br(100 * r['gr'], 0)}) × f"],
        ["7 critérios do defensivo", f"{sum(1 for _, ok in crit if ok)} de 6", "INFORMATIVO",
         "; ".join(("[sim] " if ok else "[não] ") + n for n, ok in crit) + "; dividendos 20 anos: série de 10"],
        ["Teto de renda (Bazin calibrado)", f"R$ {br(r['teto_renda'])}" if r["teto_renda"] else "N/A", "INFORMATIVO",
         "DPA sustentável líquido ÷ RF nominal líquida" + ("" if r["coberto"] else " — N/A: dividendo médio acima do FCFE normalizado")],
        ["Bazin original (6%)", f"R$ {br(r['bazin6'])}" if r["bazin6"] else "N/A", "INFORMATIVO", "DPA sustentável ÷ 6%"],
        ["Lynch", f"PEG {br(r['peg'])} · PEGY {br(r['pegy'])}" if r["peg"] else "n.d.", "INFORMATIVO",
         f"categoria: {'cíclica' if emp.perfil == 'ciclica' else 'stalwart'}; P/L normalizado ÷ g nominal {pct(r['g_nom'])}" +
         (" — PEG não se aplica a cíclica (Lynch)" if emp.perfil == "ciclica" else "")],
        ["Greenblatt (Fórmula Mágica)", f"EY {pct(r['ey'])} · ROC {pct(r['roc'])}", "INFORMATIVO",
         f"EBIT 12m ÷ EV; EBIT ÷ (capital de giro + imobilizado). Posição no lote: {rank}º de {len(EMPRESAS)}"],
        ["DCF reverso", f"g real {('≤ −5%' if r['g_implicito'] <= -0.05 else pct(r['g_implicito'])) if r['g_implicito'] is not None else 'n.a. (ROIC < WACC)'} · Ke {pct(r['ke_implicito'])}", "INFORMATIVO",
         "crescimento real perpétuo que o preço exige (margem mediana, Ke da casa); e o Ke que o preço embute"],
        ["Bogle (10 anos)", f"{pct(r['bogle_nom'])} nominal", "INFORMATIVO",
         f"DY sustentável {pct(r['dy'])} + g nominal {pct(r['g_nom'])} + múltiplo {pct(r['dmult'])} · real líquido {pct(r['bogle_liq_real'])}"
         + ("" if r["pl_final"] else " · sem re-rating (P/L histórico não confiável em cíclica)")],
        ["Altman Z'' (emergentes) · Piotroski · Beneish · Sloan",
         f"{br(r['altman'])} ({r['altman_zona']}) · {r['piotroski']}/9 · {br(r['beneish']) if r['beneish'] is not None else 'n.d.'} · {pct(r['sloan'])}",
         "INFORMATIVO", f"exercício {r['ano_qualidade']} vs anterior [CVM]; Beneish > −1,78 = alerta; Sloan alto e positivo = lucro acima do caixa"],
    ]
    story.append(tabela(lin, [33 * mm, 29 * mm, 21 * mm, 99 * mm]))
    story.append(PageBreak())

    story.append(P(f"{emp.ticker} — reconstrução, renda e veredito", "h2"))
    rec = [["Âncora", "Valor", "Peso"]] + [[k, f"R$ {br(val)}", "mediana"] for k, val in r["ancoras"].items()]
    rec.append(["<b>Valor central</b>", f"<b>R$ {br(r['central'])}</b>", f"dispersão {br(r['dispersao'])}× · {r['confianca']}"])
    ts = [["Central (R$)", "margem −2 p.p.", "margem base", "margem +2 p.p."]]
    for dk, nome in ((-0.01, "Ke −1 p.p."), (0, "Ke da casa"), (0.01, "Ke +1 p.p.")):
        ts.append([nome] + [br(r["sens"][(dk, dm)]) for dm in (-0.02, 0, 0.02)])
    lado = Table([[tabela(rec, [40 * mm, 20 * mm, 30 * mm]), tabela(ts, [24 * mm, 20 * mm, 20 * mm, 20 * mm])]], colWidths=[92 * mm, 90 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Controlador.</b> {tx['controlador']}", "p"))
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
                         ["Vence a RF?", r["vence_rf"] + (" — só com re-rating; sem: " + r["rf_sem_rerating"] if r["so_com_rerating"] else "")]],
                        [95 * mm, 87 * mm]))
    story.append(Spacer(1, 3))
    n = r["notas"]
    pode = n["qualidade"] >= 8 and n["solidez"] >= 7 and r["confianca"] == "normal"
    ver = Table([[P(f"<b>Veredito: <font color='{cor.hexval()}'>{palavra}</font></b> — preço {br(r['pc'])}× o central. " +
                    ("Sem palavra: sem preço de compra nem de saída (§9). " if nc else f"Compra R$ {br(r['compra'])} · justo R$ {br(r['central'])} · saída R$ {br(r['saida'])}. " + nota_f2(r))
                    + f"Entrada parcial (exceção §9): {'aplicável — 1ª parcela (≤ 1/3) só até R$ ' + br(r['compra_parcial']) if pode else 'não se aplica (qualidade < 8, solidez < 7 ou confiança baixa)'}.<br/>"
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
                   "Razão (c) — o método v1 estava errado: central sem conta reproduzível (número redondo ou múltiplo de EBITDA), sem capex de "
                   f"manutenção e com inflação de 4%; preço inalterado (R$ {br(emp.preco)}).", "p"))
    story.append(P("<b>Autocrítica (5 linhas).</b> " + " ".join(f"{i + 1}) {t}" for i, t in enumerate(tx["autocritica"])), "p"))
    story.append(P(f"<b>Eventos com data.</b> {AGENDA}.", "p"))
    story.append(P(f"<b>Não encontrado.</b> {tx['nao_encontrado']}", "pi"))
    story.append(PageBreak())


def capa(res, rank, story):
    story.append(P("Fichas de Avaliação — Value Investing B3", "h1"))
    story.append(P(f"Lote 3 — Papel e celulose, infraestrutura de mercado e agro (7 empresas) · rev. 09/10/2026 · data-base {DATA_BASE} · doutrina v2.5", "h2"))
    cont = {}
    for r in res:
        cont[r["palavra"]] = cont.get(r["palavra"], 0) + 1
    resumo = " · ".join(f"{k}: {v}" for k, v in sorted(cont.items()))
    baratas = [r["ticker"] for r in res if r["palavra"] == "BARATA"]
    box = (f"<b>Conclusão.</b> Ao Ke da casa ({pct(MK.ke_nom)} nominal), com margens de meio de ciclo de 10 anos da CVM, capex de manutenção "
           f"descontado do lucro (Owner Earnings) e arrendamentos (IFRS 16) na dívida, o lote fica: <b>{resumo}</b>. "
           + (f"<b>Compra autorizada pela régua: {', '.join(baratas)}</b> — abaixo do preço de compra; é cíclica com margem bimodal "
              "(BARATA com a margem mediana, RADAR com margem de 20–25%), por isso entrada escalonada e posição pequena (ver ficha). "
              if baratas else "<b>Nenhuma compra autorizada.</b> ")
           + " · ".join(f"{p}: {', '.join(r['ticker'] for r in res if r['palavra'] == p)}" for p in ("RADAR", "JUSTA", "CARA")
                        if any(r["palavra"] == p for r in res))
           + ". A melhor empresa do lote (B3SA3) está entre as mais caras.")
    tb = Table([[P(box, "box")]], colWidths=[182 * mm])
    tb.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, AZUL), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF3F9")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(tb)
    story.append(P("Quadro-resumo", "h3"))
    q = [["Ticker", "Palavra", "Preço", "Central", "P/C", "Compra", "Saída", "Ke implícito", "ROIC × WACC", "Greenblatt", "Vence RF", "Nota", "03/10"]]
    for r in sorted(res, key=lambda z: z["pc"]):
        an = ANTES[r["ticker"]]
        q.append([r["ticker"], f"<font color='{COR.get(r['palavra'], AZUL).hexval()}'><b>{r['palavra']}</b></font>", br(r["preco_"]), br(r["central"]),
                  br(r["pc"]), "n.a." if r["palavra"] == "NÃO CONCLUSIVO" else br(r["compra"]), "n.a." if r["palavra"] == "NÃO CONCLUSIVO" else br(r["saida"]), pct(r["ke_implicito"]), f"{pct(r['roic'], 0)} × {pct(r['wacc'], 0)}",
                  f"{rank[r['ticker']]}º", r["vence_rf"] + ("*" if r["so_com_rerating"] else ""), br(r["notas"]["geral"], 1), f"{an[0]} {br(an[1])}"])
    story.append(tabela(q, [13 * mm, 15 * mm, 12 * mm, 13 * mm, 10 * mm, 12 * mm, 12 * mm, 15 * mm, 18 * mm, 15 * mm, 13 * mm, 9 * mm, 25 * mm]))
    story.append(Spacer(1, 4))
    story.append(grafico_resumo(res))
    story.append(P("Greenblatt = posição no lote pela soma dos rankings de EY (EBIT ÷ EV) e ROC (EBIT ÷ capital de giro + imobilizado); "
                   "o ranking do hall inteiro fica no 03 quando todos os lotes forem recalculados. * vence só com re-rating.", "pi"))
    story.append(PageBreak())
    story.append(P("Metodologia das não financeiras (o que mudou em relação a 03/10)", "h2"))
    met = [["Item", "Regra"],
           ["Dados", "Demonstrações consolidadas da CVM (DFP 2016–25 + ITR; 12m até jun/2026; SMTO3 exercício abr–mar até mar/2026) — fonte A. "
                     "Preço, ações, proventos: StatusInvest. Contas: ferramentas/motor_nao_financeiras.py."],
           ["Lucro de meio de ciclo", "Receita de meio de ciclo (média dos 3 últimos exercícios + 12m) × margem EBIT mediana de 10 anos × (1 − IR efetivo mediano de 5 anos, "
                                     "entre 15% e 34%, sem anos de crédito fiscal). 'Outras receitas operacionais' acima da mediana de 10 anos da empresa "
                                     "(em % da receita) saem do EBIT como não recorrentes — SMTO3 mar/2024 (R$ 0,99 bi) e SUZB3 2023 (R$ 1,5 bi)."],
           ["Capex de manutenção", "Cíclica/commodity: mediana de 10 anos de capex ÷ receita contra a de D&A ÷ receita (a receita cresce por preço, não "
                                   "por capacidade; a mediana dilui projetos como Cerrado, Puma II e Gaia). Serviços: Greenwald — capex − (capital ÷ receita) × "
                                   "Δreceita média de 5 anos. Em ambos, se o capex de manutenção supera a D&A, a diferença sai do lucro (só penaliza)."],
           ["Dívida e crescimento", "Dívida bruta inclui arrendamentos (IFRS 16). Crescimento só entra no DCF se o ROIC supera o WACC (Greenwald); "
                                    "senão g = 0 e o DCF converge para o EPV. Ganho de valor justo de ativo biológico fica no EBIT (a exaustão o devolve) e é exibido."],
           ["Âncoras", "Cíclica: EPV de meio de ciclo (NOPAT ÷ WACC real) · DCF normalizado (FCFF = NOPAT × (1+g) × (1 − g/ROIC), g real 1%, margem p25/mediana/p75, "
                       "pesos 25/50/25) · valor de reprodução (PL contábil; SLCE3: NAV das terras). Serviços (B3): DCF · EPV · Owner Earnings ÷ (Ke − g). Central = mediana."],
           ["WACC", f"Ke da casa {pct(MK.ke_nom, 2)}; Kd = rf nominal + spread de crédito declarado (1,2–2,5 p.p.); pesos a valor de mercado (dívida bruta)."],
           ["Informativos", "Graham (original, BR, revisado-BR), 7 critérios, teto de renda, Bazin 6%, Lynch, Greenblatt (ranking), DCF reverso (g real e Ke "
                            "implícitos), Bogle, Altman Z'' de emergentes, Piotroski F, Beneish M, Sloan."],
           ["Notas", "Qualidade = metade spread ROIC − WACC + metade qualitativo; Solidez = DL/EBITDA normalizado, zona Altman, cobertura de juros; "
                     "Renda e Preço como no Lote 1."]]
    story.append(tabela(met, [34 * mm, 148 * mm]))
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
    guardar(SAIDA, "pdf lote 3")      # AUD-84: o PDF anterior do mesmo nome vai para _historico/
    doc = SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=14 * mm,
                            title="Lote 3 — Papel e celulose, B3 e agro · rev. 09/10/2026", author="Mesa de Value Investing")
    story = []
    capa(res, rank, story)
    for i in sorted(range(len(EMPRESAS)), key=lambda k: res[k]["pc"]):
        ficha(EMPRESAS[i], res[i], rank[EMPRESAS[i].ticker], story)
    story.append(P("Apêndice — fontes", "h2"))
    story.append(tabela([["Rótulo", "Fonte"],
                         ["[CVM]", "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/ e /ITR/DADOS/ (cache em ferramentas/dados/cvm)"],
                         ["[SI]", "https://statusinvest.com.br (indicadores, proventos por data-com, páginas dos tickers) — 04/10/2026"],
                         ["Mercado", "Tesouro Transparente (IPCA+ 2050 sem cupom 7,06%), ANBIMA ETTJ (inflação implícita 6,46%), BCB Focus 25/09"],
                         ["PDF 06/09 · 03/10", "Fichas anteriores (pasta AGRO E B3): fatos de ciclo, controlador, NAV de terras, agenda — fontes primárias citadas lá"]],
                        [26 * mm, 156 * mm]))
    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    print("gerado:", SAIDA)
    for r in sorted(res, key=lambda z: z["pc"]):
        print(r["ticker"], r["palavra"], round(r["central"], 2), round(r["pc"], 2), "rank", rank[r["ticker"]])


if __name__ == "__main__":
    main()
