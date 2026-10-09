"""PDF do Lote 2 (Energia elétrica e saneamento) — doutrina v2.5. Uso: python gerar_pdf_lote2.py"""
from ltm import ltm_de
import copy
import pathlib
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, SimpleDocTemplate, Spacer, Table, TableStyle

from gerar_pdf_lote1 import AZUL, COR, LINHA, P, SERIES, br, grafico_resumo, grafico_roe, pct, tabela
from lote1_bancos import DATA_BASE, MK
from lote2_energia import CVM, EMPRESAS, alavancagem, dpas, metodo_regulado
from lote2_textos import AGENDA, ANTES, T
from motor_financeiras import avaliar, central_ao_ke, projecao
from motor_nao_financeiras import altman_z2, beneish, piotroski, sloan

sys.stdout.reconfigure(encoding="utf-8")
SAIDA = pathlib.Path(__file__).parent.parent / "ENERGIA ELÉTRICA E SANEAMENTO" / "Energia_Saneamento_rev_09-10-2026.pdf"


def rodape(c, d):
    c.saveState()
    c.setFont("Arial", 6.5)
    c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(15 * mm, 9 * mm, f"Mesa de Value Investing — Lote 2 Energia elétrica e saneamento · rev. 09/10/2026 · data-base {DATA_BASE} · "
                                  "doutrina v2.5 · não é recomendação de investimento")
    c.drawRightString(195 * mm, 9 * mm, f"p. {d.page}")
    c.restoreState()


KE_REF_REAL = 1.14 / 1.04 - 1          # "Ke de mercado 14%" da rev. 03/10, que supunha inflação de 4%
KE_REF = (1 + KE_REF_REAL) * (1 + MK.pi) - 1


def tir_real(r):
    k = r["ke_implicito"]
    return (1 + k) / (1 + MK.pi) - 1 if k else None


def extras(emp, r):
    x = {}
    x["tir"] = tir_real(r)
    x["dle"], x["cob"], x["dl"] = alavancagem(emp.ticker)
    x["ke14"] = central_ao_ke(emp, MK, KE_REF)
    e2 = copy.deepcopy(emp)
    e2.desconto_controlador = {"tipo": "zero", "razao": ""}
    x["central_sem_desc"] = avaliar(e2, MK)["central"]
    e3 = copy.deepcopy(emp)
    e3.roe_lp = max(emp.roe_inicio, emp.roe_lp)
    x["central_roe_atual"] = avaliar(e3, MK)["central"]
    a = CVM[emp.ticker]["anual"]
    d1, d0 = a["2025"], a["2024"]
    x["altman"], x["zona"] = altman_z2(ltm_de(CVM[emp.ticker]))
    x["piotroski"], _ = piotroski(d1, d0)
    x["beneish"] = beneish(d1, d0)
    x["sloan"] = sloan(d1, d0)
    return x


def preencher(s, emp, r, x):
    tir = x["tir"]
    rep = {"compra": br(r["compra"]), "pc": br(r["pc"]), "palavra": r["palavra"], "roe_lp": pct(emp.roe_lp), "dy_liq": pct(r["dy_liq"]),
           "tir": pct(tir) if tir is not None else "não calculável",
           "rf": pct(MK.rf_real, 2), "dl_ebitda": br(x["dle"]) if x["dle"] is not None else "n.d.", "ke14": br(x["ke14"]),
           "roe_impl": pct(r["roe_implicito"]), "pvp": br(r["pvp"]), "sens_roe_mais": br(r["sens"][(0, 0.02)]),
           "central_sem_desc": br(x["central_sem_desc"]), "roe_atual": pct(emp.roe_inicio), "central_roe_atual": br(x["central_roe_atual"])}
    for k, v in rep.items():
        s = s.replace("{" + k + "}", v)
    return s


def ficha(emp, r, story):
    x = extras(emp, r)
    tx = {k: ([preencher(i, emp, r, x) for i in v] if isinstance(v, list) else preencher(v, emp, r, x)) for k, v in T[emp.ticker].items()}
    palavra = r["palavra"]
    nc = palavra == "NÃO CONCLUSIVO"
    if nc:       # §9: sem palavra não há preço de compra nem de saída (o texto da ficha falava em "compra ≤ R$ …")
        tx["capital"] = f"Não. NÃO CONCLUSIVO ({br(r['pc'])}× o central): sem palavra não há preço de compra nem de saída (§9)."
    cor = COR.get(palavra, AZUL)
    cab = Table([[P(f"<font name='Arial-B' size=14 color='#1F3A5F'>{emp.ticker}</font>  <font size=9>{emp.nome} · regulado</font>", "p"),
                  P(f"<font name='Arial-B' size=12 color='white'>{palavra}</font>", "p")]], colWidths=[120 * mm, 60 * mm], rowHeights=[11 * mm])
    cab.setStyle(TableStyle([("BACKGROUND", (1, 0), (1, 0), cor), ("ALIGN", (1, 0), (1, 0), "CENTER"), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("LINEBELOW", (0, 0), (0, 0), 1.2, AZUL)]))
    story.append(cab)
    story.append(Spacer(1, 3))
    tir = x["tir"]
    kpi = [["Preço 02/10", "Valor central", "P/C", "Compra 0,70×", "Saída 1,30×", "TIR real implícita", "Vence a RF?", "Nota geral"],
           [f"R$ {br(emp.preco)}", f"R$ {br(r['central'])}", br(r["pc"]) + "×", "n.a." if nc else f"R$ {br(r['compra'])}", "n.a." if nc else f"R$ {br(r['saida'])}",
            pct(tir) if tir is not None else "n.c.", r["vence_rf"] + (" (só c/ re-rating)" if r["so_com_rerating"] else ""), br(r["notas"]["geral"], 1)]]
    story.append(tabela(kpi, [22.5 * mm] * 8, extra=[("ALIGN", (0, 0), (-1, -1), "CENTER")]))
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Círculo de competência.</b> {tx['circulo']}", "p"))
    story.append(Spacer(1, 3))
    l = ltm_de(CVM[emp.ticker])
    fatos = [["Fato", "Valor", "Fonte"],
             ["Preço (fechamento 02/10)", f"R$ {br(emp.preco)}", "PDF 03/10"],
             ["VPA · P/VP", f"R$ {br(emp.vpa)} · {br(r['pvp'])}×", "[SI]"],
             ["LPA 12m · P/L 12m", f"R$ {br(emp.lpa_12m, 3)} · {br(emp.preco / emp.lpa_12m, 1)}×", "[SI]"],
             ["ROE 12m (início) · de longo prazo", f"{pct(emp.roe_inicio)} · {pct(emp.roe_lp)}", "[SI] mediana 2016–25"],
             ["Payout · g perpétuo", f"{pct(emp.payout, 0)} · {pct(r['g'])}", "política / motor"],
             ["DPA médio 5a · sustentável", f"R$ {br(emp.dpa_medio_5a, 3)} · R$ {br(r['dpa_sust'], 3)}", "[SI] data-com"],
             ["Dívida líquida · DL/EBITDA", f"R$ {br(x['dl'] / 1e6, 1)} bi · {br(x['dle']) if x['dle'] is not None else 'n.d.'}×", "[CVM] jun/26, c/ arrendamento"],
             ["Cobertura de juros (EBIT ÷ despesa financeira)", f"{br(x['cob'], 1) if x['cob'] else 'n.d.'}×", "[CVM] 12m"],
             ["Receita · EBIT 12m", f"R$ {br(l['receita'] / 1e6, 1)} bi · {br(l['ebit'] / 1e6, 2)} bi", "[CVM]"]]
    lado = Table([[tabela(fatos, [42 * mm, 33 * mm, 22 * mm]), grafico_roe(emp.ticker, r, emp)]], colWidths=[98 * mm, 84 * mm])
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
            f"patrimônio (proxy da base regulatória) × (ROE {pct(emp.roe_lp)} − g {pct(g)}) ÷ (Ke {pct(ke, 2)} − g) = {br(r['pvp_just'])}× VPA"],
           ["DDM 2 estágios", f"R$ {br(an[1][1])}", "ÂNCORA", f"ROE {pct(emp.roe_inicio)} → {pct(emp.roe_lp)} em 5 anos; payout {pct(emp.payout, 0)}; terminal = P/VP justificado"],
           ["TIR real implícita", pct(tir) if tir is not None else "n.c.", "TESTE (§4)",
            f"retorno real que o preço embute (mesmo modelo); piso rf {pct(MK.rf_real, 2)} · Ke real {pct(MK.ke_real, 2)} — "
            + ("perde até para o Tesouro → CARA independentemente do resto" if (tir is None or tir < MK.rf_real) else
               ("acima do Tesouro, abaixo do Ke da casa" if tir < MK.ke_real else "acima do Ke da casa"))]]
    if r["desc_controlador"] > 0:
        lin.append(["Desconto de controlador", f"−{pct(r['desc_controlador'])}", "no valor", emp.desconto_controlador["razao"]])
    lin += [
        ["Lucro projetado (próprio)", " · ".join(f"R$ {br(p[2])}" for p in proj), "INFORMATIVO", "LPA anos 1–3 (ROE convergindo sobre VPA que cresce pela retenção). Consenso: não encontrado"],
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
         "INFORMATIVO", "exercício 2025 vs 2024 [CVM]; em concessão o Altman tende à zona cinzenta pela estrutura de capital (dívida longa regulada)"],
        ["Greenblatt · EPV · Owner Earnings", "N/A", "N/A por perfil",
         "regulado: o retorno é o regulatório (P/VP justificado e TIR), não EBIT/capital nem FCO − capex. " + metodo_regulado(emp.ticker)],
    ]
    story.append(tabela(lin, [33 * mm, 27 * mm, 21 * mm, 101 * mm]))
    story.append(PageBreak())

    story.append(P(f"{emp.ticker} — reconstrução, renda e veredito", "h2"))
    rec = [["Âncora", "Valor", "Peso"]] + [[k, f"R$ {br(v)}", "mediana"] for k, v in r["ancoras"].items()]
    rec.append(["<b>Valor central</b>", f"<b>R$ {br(r['central'])}</b>", f"dispersão {br(r['dispersao'])}× · {r['confianca']}"])
    ts = [["Central (R$)", "ROE −2 p.p.", "ROE base", "ROE +2 p.p."]]
    for dk, nome in ((-0.01, "Ke −1 p.p."), (0, "Ke da casa"), (0.01, "Ke +1 p.p.")):
        ts.append([nome] + [br(r["sens"][(dk, dr)]) for dr in (-0.02, 0, 0.02)])
    lado = Table([[tabela(rec, [40 * mm, 20 * mm, 30 * mm]), tabela(ts, [24 * mm, 20 * mm, 20 * mm, 20 * mm])]], colWidths=[92 * mm, 90 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Controlador.</b> {tx['controlador']}", "p"))
    story.append(Spacer(1, 3))
    dpa, jc = dpas(emp.ticker), SERIES[emp.ticker]["jcp_por_ano_datacom"]
    yrs = list(range(2021, 2027))
    story.append(tabela([["Proventos por data-com [SI]"] + [str(y) if y < 2026 else "2026 até 02/10" for y in yrs],
                         ["DPA total (R$)"] + [br(dpa.get(str(y), 0), 3) for y in yrs],
                         ["dos quais JCP (R$)"] + [br(jc.get(str(y), 0), 3) for y in yrs]], [38 * mm] + [24 * mm] * 6))
    story.append(Spacer(1, 2))
    story.append(tabela([["Renda e renda fixa (10 anos, líquido de IR)", "Valor"],
                         ["Yield sustentável bruto · líquido (JCP × 0,825)", f"{pct(r['dy'])} · {pct(r['dy_liq'])}"],
                         ["Coberto por caixa?", "Sim — DPA sustentável ≤ FCFE normalizado" if r["dpa_fcfe"] >= emp.dpa_medio_5a else
                          "Parcial — o DPA médio supera o FCFE normalizado; entra o menor"],
                         ["Retorno esperado real líquido (Bogle) · sem re-rating", f"{pct(r['bogle_liq_real'])} · {pct(r['so_inv_liq_real'])}"],
                         ["RF real líquida", f"{pct(MK.rf_liq_real, 2)} → Sim ≥ {pct(MK.rf_liq_real + .03, 2)} · Empate ≥ {pct(MK.rf_liq_real + .015, 2)}"],
                         ["Vence a RF?", r["vence_rf"] + (" — só com re-rating; sem: " + r["rf_sem_rerating"] if r["so_com_rerating"] else "")]],
                        [95 * mm, 87 * mm]))
    story.append(Spacer(1, 3))
    n = r["notas"]
    ver = Table([[P(f"<b>Veredito: <font color='{cor.hexval()}'>{palavra}</font></b> — preço {br(r['pc'])}× o central. " +
                    ("Sem palavra: sem preço de compra nem de saída (§9)." if nc else f"Compra R$ {br(r['compra'])} · justo R$ {br(r['central'])} · saída R$ {br(r['saida'])}.") + "<br/>"
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
    a0 = ANTES[emp.ticker]
    story.append(P(f"<b>De → para (rev. 03/10 → hoje).</b> {a0[0]}, central R$ {br(a0[1])} → {palavra}, central R$ {br(r['central'])}. "
                   "Razão (c) — o método v1 estava errado: centrais por ajuste avulso em R$ sobre o anterior, Ke com inflação de 4% e TIR "
                   f"usada só quando reprovava; preço inalterado (R$ {br(emp.preco)}).", "p"))
    story.append(P("<b>Autocrítica (5 linhas).</b> " + " ".join(f"{i + 1}) {t}" for i, t in enumerate(tx["autocritica"])), "p"))
    story.append(P(f"<b>Eventos com data.</b> {AGENDA}.", "p"))
    story.append(P(f"<b>Não encontrado.</b> {tx['nao_encontrado']}", "pi"))
    story.append(PageBreak())


def capa(res, story):
    story.append(P("Fichas de Avaliação — Value Investing B3", "h1"))
    story.append(P(f"Lote 2 — Energia elétrica e saneamento (8 empresas) · rev. 09/10/2026 · data-base {DATA_BASE} · doutrina v2.5", "h2"))
    tirs = [r for r in res if r["tir"] is not None]
    abaixo = [r["ticker"] for r in res if r["tir"] is None or r["tir"] < MK.rf_real]
    acima = [r["ticker"] for r in tirs if r["tir"] >= MK.rf_real + 0.02]
    baratas_ref = [r["ticker"] for r in res if r["ke14"] > r["preco_"]]
    box = (f"<b>Conclusão.</b> Ao Ke da casa ({pct(MK.ke_nom)} nominal; {pct(MK.ke_real)} real), <b>as 8 estão CARAS</b> (P/C de "
           f"{br(min(r['pc'] for r in res))}× a {br(max(r['pc'] for r in res))}×). <b>Nenhuma compra autorizada.</b> A TIR real implícita — o retorno que o preço "
           f"embute — vai de {pct(min(r['tir'] for r in tirs))} a {pct(max(r['tir'] for r in tirs))}; "
           f"<b>{', '.join(abaixo) or 'nenhuma'} rende(m) menos que o Tesouro IPCA+ ({pct(MK.rf_real, 2)}) sem risco</b>, e só {', '.join(acima) or 'nenhuma'} paga 2 p.p. ou mais acima dele. "
           f"Mesmo ao 'Ke de mercado' da rev. 03/10 ({pct(KE_REF_REAL)} real) só {', '.join(baratas_ref) or 'nenhuma'} ficaria abaixo do valor — "
           "a régua da casa é o que separa. As privatizadas (SBSP3, CSMG3, CPLE3) exigem ROE futuro muito acima do histórico — é aposta na "
           "eficiência, não margem de segurança. <i>Preços de 02/10, antes do 1º turno; atualizar antes de decidir.</i>")
    tb = Table([[P(box, "box")]], colWidths=[182 * mm])
    tb.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, AZUL), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF3F9")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(tb)
    story.append(P("Quadro-resumo", "h3"))
    q = [["Ticker", "Palavra", "Preço", "Central", "P/C", "Compra", "Saída", "TIR real", "Ke 03/10", "Vence RF", "Nota", "03/10"]]
    for r in sorted(res, key=lambda z: z["pc"]):
        a0 = ANTES[r["ticker"]]
        q.append([r["ticker"], f"<font color='{COR.get(r['palavra'], AZUL).hexval()}'><b>{r['palavra']}</b></font>", br(r["preco_"]), br(r["central"]),
                  br(r["pc"]), "n.a." if r["palavra"] == "NÃO CONCLUSIVO" else br(r["compra"]), "n.a." if r["palavra"] == "NÃO CONCLUSIVO" else br(r["saida"]), pct(r["tir"]) if r["tir"] is not None else "n.c.", br(r["ke14"]),
                  r["vence_rf"] + ("*" if r["so_com_rerating"] else ""), br(r["notas"]["geral"], 1), f"{a0[0]} {br(a0[1])}"])
    story.append(tabela(q, [14 * mm, 14 * mm, 12 * mm, 13 * mm, 10 * mm, 13 * mm, 13 * mm, 15 * mm, 14 * mm, 14 * mm, 10 * mm, 30 * mm]))
    story.append(Spacer(1, 4))
    story.append(grafico_resumo(res))
    story.append(P("TIR real = retorno real que o preço embute (Ke implícito ÷ inflação implícita). Ke 03/10 = valor central ao 'Ke de mercado' "
                   f"que a rev. 03/10 usava (14% com inflação de 4% = {pct(KE_REF_REAL)} real = {pct(KE_REF)} nominal hoje) — só sensibilidade, "
                   "nunca o veredito. * vence só com re-rating.", "pi"))
    story.append(PageBreak())
    story.append(P("Metodologia dos regulados", "h2"))
    met = [["Item", "Regra"],
           ["Por que não FCO − capex", "Nas transmissoras (TAEE11, ISAE4) a concessão (ICPC 01/IFRS 15) põe o investimento em ativo de contrato "
                                       "dentro do FCO (ISAE4 tem FCO negativo); nas distribuidoras e no saneamento o capex está no FCI, mas o ciclo de "
                                       "investimento deixa o FCO − capex negativo (SBSP3). Lucro de caixa e lucro contábil divergem enquanto a base cresce. "
                                       "Sem base regulatória e WACC regulatório com fonte A/B, o DCF regulatório é o P/VP justificado como proxy "
                                       "declarado (doutrina v2.5 §11.2); cada ficha diz onde está o investimento (FCO, FCI ou misto)."],
           ["Âncoras", "DCF regulatório = patrimônio (proxy da base regulatória) × (ROE − g) ÷ (Ke − g) · DDM em 2 estágios (ROE do 12m converge à mediana de "
                       "10 anos em 5 anos; terminal = P/VP justificado). Central = mediana. Tudo ao Ke da casa."],
           ["TIR real implícita (doutrina §4)", "Sempre calculada: o Ke que iguala o valor central ao preço, deflacionado pela inflação implícita. "
                                                "TIR < rf = perde para o Tesouro sem risco (CARA de qualquer forma); < Ke real = não paga o prêmio exigido."],
           ["g e payout", f"g = ROE × (1 − payout), teto {pct(MK.g_teto, 2)} (π + 2% real). Payout pela política/histórico declarado por empresa."],
           ["Controlador", "Uma vez, no valor: CMIG4 17,7% (precedente 40% × cenário 44% menor), SAPR11 15% (Agepar). Privatizadas e privadas: zero, com a razão."],
           ["Solidez", "Média da nota de dívida líquida/EBITDA (com arrendamento) e da cobertura de juros, da CVM (12m até jun/26)."],
           ["Dados", "VPA/LPA/ROE/proventos: StatusInvest (base pós-bonificação). Demonstrações: CVM (DFP 2016–25 + ITR; Sabesp e Sanepar pela demonstração individual "
                     "quando não há consolidada). Preços: fechamento de 02/10 (PDF 03/10)."]]
    story.append(tabela(met, [36 * mm, 146 * mm]))
    story.append(PageBreak())


def main():
    res = []
    for e in EMPRESAS:
        r = avaliar(e, MK)
        r["preco_"] = e.preco
        r["tir"] = tir_real(r)
        r["ke14"] = central_ao_ke(e, MK, KE_REF)
        res.append(r)
    doc = SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=14 * mm,
                            title="Lote 2 — Energia elétrica e saneamento · rev. 09/10/2026", author="Mesa de Value Investing")
    story = []
    capa(res, story)
    for i in sorted(range(len(EMPRESAS)), key=lambda k: res[k]["pc"]):
        ficha(EMPRESAS[i], res[i], story)
    story.append(P("Apêndice — fontes", "h2"))
    story.append(tabela([["Rótulo", "Fonte"],
                         ["[CVM]", "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/ e /ITR/DADOS/ (cache em ferramentas/dados/cvm)"],
                         ["[SI]", "https://statusinvest.com.br — indicadores, proventos por data-com (coleta de 05/10/2026; preço não usado)"],
                         ["Mercado", "Tesouro Transparente (IPCA+ 2050 sem cupom 7,06%), ANBIMA ETTJ (inflação implícita 6,46%), BCB Focus 25/09"],
                         ["PDF 07/09 · 03/10", "Fichas anteriores (pasta ENERGIA ELÉTRICA E SANEAMENTO): fatos regulatórios, controlador, agenda — fontes primárias citadas lá"]],
                        [26 * mm, 156 * mm]))
    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    print("gerado:", SAIDA)
    for r in sorted(res, key=lambda z: z["pc"]):
        print(r["ticker"], r["palavra"], round(r["central"], 2), round(r["pc"], 2), "TIR", r["tir"] and round(100 * r["tir"], 1))


if __name__ == "__main__":
    main()
