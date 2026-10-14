"""Gera o PDF do Lote 1 (Bancos e Seguridade) pela doutrina v2.5. Uso: python gerar_pdf_lote1.py"""
import glob
import io
import json
import math
import pathlib
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import series_vigente
from historico_arquivos import guardar
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from lote1_bancos import DATA_BASE, EMPRESAS, MK, MK_FOCUS
from lote1_textos import AGENDA, ANTES, T
from motor_financeiras import (HORIZONTE, IR_JCP, PIB_REAL_LP, PREMIO_KE, avaliar, central_ao_ke, entrada_parcial, projecao)

sys.stdout.reconfigure(encoding="utf-8")
AQUI = pathlib.Path(__file__).parent
RAIZ = AQUI.parent
SAIDA = RAIZ / "BANCOS E SEGURIDADE" / "Banco_Seguridade_rev_09-10-2026.pdf"

pdfmetrics.registerFont(TTFont("Arial", "C:/Windows/Fonts/arial.ttf"))
pdfmetrics.registerFont(TTFont("Arial-B", "C:/Windows/Fonts/arialbd.ttf"))
pdfmetrics.registerFont(TTFont("Arial-I", "C:/Windows/Fonts/ariali.ttf"))
pdfmetrics.registerFont(TTFont("Arial-BI", "C:/Windows/Fonts/arialbi.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-B", italic="Arial-I", boldItalic="Arial-BI")

AZUL = colors.HexColor("#1F3A5F")
CINZA = colors.HexColor("#F2F4F7")
LINHA = colors.HexColor("#C9D1DC")
COR = {"BARATA": colors.HexColor("#1E7B3A"), "RADAR": colors.HexColor("#2F6DB5"), "JUSTA": colors.HexColor("#B7791F"),
       "CARA": colors.HexColor("#B83232"), "NÃO CONCLUSIVO": colors.HexColor("#6B7280")}

S = {
    "h1": ParagraphStyle("h1", fontName="Arial-B", fontSize=17, leading=21, textColor=AZUL, spaceAfter=4),
    "h2": ParagraphStyle("h2", fontName="Arial-B", fontSize=11.5, leading=14, textColor=AZUL, spaceBefore=6, spaceAfter=3),
    "h3": ParagraphStyle("h3", fontName="Arial-B", fontSize=9, leading=11, textColor=AZUL, spaceBefore=4, spaceAfter=2),
    "p": ParagraphStyle("p", fontName="Arial", fontSize=8.2, leading=10.4, alignment=TA_LEFT),
    "pi": ParagraphStyle("pi", fontName="Arial-I", fontSize=7.6, leading=9.6, textColor=colors.HexColor("#4B5563")),
    "cel": ParagraphStyle("cel", fontName="Arial", fontSize=7.4, leading=9),
    "celb": ParagraphStyle("celb", fontName="Arial-B", fontSize=7.4, leading=9),
    "box": ParagraphStyle("box", fontName="Arial", fontSize=8.6, leading=11.2),
}


def br(x, casas=2):
    if x is None:
        return "—"
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, casas=1):
    return "—" if x is None else br(100 * x, casas) + "%"


def texto_entrada_parcial(r, emp, armadilhas=()):
    """§9, exceção da 1ª parcela pela regra única do motor (AUD-42): o texto diz o motivo de cada recusa."""
    ok, motivos = entrada_parcial(r, emp.fora_circulo, armadilhas)
    return ("aplicável — 1ª parcela (≤ 1/3) só até R$ " + br(r["compra_parcial"])) if ok else "não se aplica (" + "; ".join(motivos) + ")"


def nota_f2(r):
    """Notas da Etapa 2 (F2) que só aparecem quando valem: saída por qualidade (§9) e quebra suspeita (§11.4)."""
    t = ""
    if r.get("saida_por_qualidade"):
        t += (f"A saída é 1,50× o central pela exceção de qualidade do §9 (ROIC > WACC a custo de reposição em "
              f"{r['roic_anos_acima']} de {r['roic_anos_total']} exercícios e nota de qualidade {br(r['notas']['qualidade'], 1)}). ")
    if r.get("op", {}).get("quebra_suspeita"):
        t += (f"Quebra estrutural SUSPEITA: a mediana dos 5 últimos exercícios difere {pct(r['op']['divergencia_janela'])} "
              "da janela (§11.4) — janela mantida; trocá-la é decisão declarada. ")
    return t


def P(t, st="cel"):
    return Paragraph(t, S[st])


def tabela(dados, larg, cab=True, zebra=True, extra=None):
    t = Table([[c if not isinstance(c, str) else P(c, "celb" if (cab and i == 0) else "cel") for c in linha]
               for i, linha in enumerate(dados)], colWidths=larg, repeatRows=1 if cab else 0)
    est = [("GRID", (0, 0), (-1, -1), 0.3, LINHA), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
           ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3)]
    if cab:
        est += [("BACKGROUND", (0, 0), (-1, 0), CINZA)]
    if zebra:
        for i in range(2 if cab else 1, len(dados), 2):
            est.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#FAFBFC")))
    if extra:
        est += extra
    t.setStyle(TableStyle(est))
    return t


def img(fig, w_mm):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    w, h = fig.get_size_inches()
    return Image(buf, width=w_mm * mm, height=w_mm * mm * h / w)


SERIES = series_vigente.carregar()      # AUD-24: série vigente explícita, não "a mais nova da pasta"


def grafico_roe(tk, r, emp):
    roe = {int(k): v for k, v in SERIES[tk]["indicadores"]["roe"]["anos"].items() if v is not None and int(k) >= 2014}
    anos = sorted(roe)
    fig, ax = plt.subplots(figsize=(3.6, 1.9))
    ax.bar([str(a) if a < 2026 else "12m" for a in anos], [roe[a] for a in anos], color="#8DA9C4", width=0.7)
    ax.axhline(100 * MK.ke_nom, color="#B83232", lw=1.2, label=f"Ke nominal da casa {pct(MK.ke_nom)}")
    ax.axhline(100 * emp.roe_lp, color="#1F3A5F", lw=1, ls="--", label=f"ROE de longo prazo {pct(emp.roe_lp)}")
    if r["ke_implicito"]:
        ax.axhline(100 * r["ke_implicito"], color="#B7791F", lw=1, ls=":", label=f"Ke implícito no preço {pct(r['ke_implicito'])}")
    ax.set_title(f"{tk} — ROE anual (%) [SI]", fontsize=7.5)
    ax.tick_params(labelsize=6)
    plt.setp(ax.get_xticklabels(), rotation=60)
    ax.set_ylim(0, max(max(roe.values()), 100 * MK.ke_nom) * 1.15)
    ax.legend(fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=2, frameon=False)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return img(fig, 82)


def grafico_resumo(res):
    itens = sorted(res, key=lambda r: r["pc"])
    fig, ax = plt.subplots(figsize=(7.2, 2.7))
    for x0, x1, c in ((0, .7, "#E3F1E7"), (.7, .9, "#E2ECF7"), (.9, 1.1, "#FBF1DF"), (1.1, 3.0, "#F8E1E1")):
        ax.axvspan(x0, x1, color=c, lw=0)
    ax.barh([r["ticker"] for r in itens], [r["pc"] for r in itens], color="#1F3A5F", height=0.55)
    for y, r in enumerate(itens):
        ax.text(r["pc"] + 0.03, y, br(r["pc"]) + "×", va="center", fontsize=6.5)
    for x in (.7, .9, 1.1, 1.3):
        ax.axvline(x, color="#6B7280", lw=0.6, ls="--")
    for x, lab in ((.35, "BARATA"), (.8, "RADAR"), (1.0, "JUSTA"), (2.0, "CARA (saída em 1,30)")):
        ax.text(x, len(itens) - 0.35, lab, fontsize=5.5, ha="center", color="#374151")
    ax.set_xlim(0, 2.9)
    ax.set_xlabel("Preço ÷ valor central (Ke da casa)", fontsize=7)
    ax.tick_params(labelsize=6.5)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    return img(fig, 175)


def rodape(c, d):
    c.saveState()
    c.setFont("Arial", 6.5)
    c.setFillColor(colors.HexColor("#6B7280"))
    c.drawString(15 * mm, 9 * mm, f"Mesa de Value Investing — Lote 1 Bancos e Seguridade · rev. 09/10/2026 · data-base {DATA_BASE} · doutrina v2.5 · "
                                  "não é recomendação de investimento")
    c.drawRightString(195 * mm, 9 * mm, f"p. {d.page}")
    c.restoreState()


def lynch(emp, r):
    cat = "crescimento lento" if r["g"] < MK.pi + 0.01 else "stalwart"
    pl12 = emp.preco / emp.lpa_12m
    g_pct = 100 * r["g"]
    peg = pl12 / g_pct if g_pct > 0 else None
    pegy = pl12 / (g_pct + 100 * r["dy"])
    g_real = 100 * ((1 + r["g"]) / (1 + MK.pi) - 1)
    return cat, pl12, peg, pegy, g_real


def graham7(emp, r):
    s = SERIES[emp.ticker]
    roe = [v for k, v in s["indicadores"]["roe"]["anos"].items() if v is not None and 2016 <= int(k) <= 2025]
    dpa = s["dpa_por_ano_datacom"]
    pagos = sum(1 for a in range(2016, 2026) if dpa.get(str(a), 0) > 0)
    pl12 = emp.preco / emp.lpa_12m
    f = MK.fator_graham
    crit = [("porte (valor de mercado > R$ 10 bi)", (s["valor_mercado"] or 0) > 1e10),
            ("lucro positivo nos anos da série", all(x > 0 for x in roe) and len(roe) >= 5),
            (f"proventos em {pagos} de 10 anos (20 anos não verificado)", pagos >= 9),
            (f"P/L {br(pl12, 1)} ≤ 15 × f = {br(15 * f, 1)}", pl12 <= 15 * f),
            (f"P/L × P/VP {br(pl12 * r['pvp'], 1)} ≤ 22,5 × f = {br(22.5 * f, 1)}", pl12 * r["pvp"] <= 22.5 * f)]
    ok = sum(1 for _, v in crit if v)
    return ok, crit


def preencher(s, r):
    return (s.replace('{compra}', br(r['compra'])).replace('{ke_impl}', pct(r['ke_implicito']))
             .replace('{roe_impl}', pct(r['roe_implicito'])).replace('{pc}', br(r['pc']))
             .replace('{pvp_perp}', br(r['pvp_perpetuo']) if r.get('pvp_perpetuo') else '—'))


def ficha(emp, r, story):
    tx = {k: ([preencher(x, r) for x in v] if isinstance(v, list) else preencher(v, r)) for k, v in T[emp.ticker].items()}
    palavra = r["palavra"]
    cor = COR.get(palavra, AZUL)
    carimbo = ""
    if emp.ticker == "BRSR6":
        carimbo = " · defeito estrutural (controlador)"
    if emp.ticker == "SANB11":
        carimbo = " · fora do hall (OPA de permuta)"
    cab = Table([[P(f"<font name='Arial-B' size=14 color='#1F3A5F'>{emp.ticker}</font>  "
                    f"<font size=9>{emp.nome} · {emp.perfil.replace('_', ' ')}</font>", "p"),
                  P(f"<font name='Arial-B' size=12 color='white'>{palavra}</font><font size=7 color='white'>{carimbo}</font>", "p")]],
                colWidths=[120 * mm, 60 * mm], rowHeights=[11 * mm])
    cab.setStyle(TableStyle([("BACKGROUND", (1, 0), (1, 0), cor), ("ALIGN", (1, 0), (1, 0), "CENTER"),
                             ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 0), (0, 0), 1.2, AZUL),
                             ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(cab)
    story.append(Spacer(1, 3))
    ki = r["ke_implicito"]
    kpi = [["Preço 02/10", "Valor central", "P/C", "Compra 0,70×", "Saída 1,30×", "Ke implícito", "Vence a RF?", "Nota geral"],
           [f"R$ {br(emp.preco)}", f"R$ {br(r['central'])}", br(r["pc"]) + "×", f"R$ {br(r['compra'])}", f"R$ {br(r['saida'])}",
            pct(ki), r["vence_rf"] + (" (só com re-rating)" if r["so_com_rerating"] else "") + (" *" if r["carimbo_rf"] else ""), br(r["notas"]["geral"], 1)]]
    story.append(tabela(kpi, [22.5 * mm] * 8, extra=[("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONTSIZE", (0, 1), (-1, 1), 9)]))
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Círculo de competência.</b> {tx['circulo']}", "p"))
    story.append(Spacer(1, 3))

    pr = emp.prudencial
    fatos = [["Fato", "Valor", "Fonte"],
             ["Preço (fechamento)", f"R$ {br(emp.preco)}", "[SI] 02/10"],
             ["VPA · P/VP", f"R$ {br(emp.vpa)} · {br(r['pvp'])}×", "[SI]"],
             ["LPA 12m · P/L 12m", f"R$ {br(emp.lpa_12m, 3)} · {br(emp.preco / emp.lpa_12m, 1)}×", "[SI]"],
             ["ROE 12m (início da projeção)", pct(emp.roe_inicio), "[SI]/guidance"],
             ["ROE de longo prazo (mediana 10a)", pct(emp.roe_lp), "[SI] 2016–25"],
             ["Payout de longo prazo · g", f"{pct(emp.payout, 0)} · {pct(r['g'])}", "política / motor"],
             ["DPA médio 5a · sustentável", f"R$ {br(emp.dpa_medio_5a, 3)} · R$ {br(r['dpa_sust'], 3)}", "[SI] data-com"]]
    if pr.get("cet1"):
        fatos.append(["CET1 · inadimplência 90d", f"{br(pr['cet1'], 1)}% · {br(pr.get('inad90'), 1) if pr.get('inad90') else '—'}%", "PDF 07/09 (2T26)"])
    if pr.get("cobertura"):
        fatos.append(["Cobertura 90d", f"{br(pr['cobertura'], 0)}%", "PDF 07/09 (2T26)"])
    t_fatos = tabela(fatos, [42 * mm, 33 * mm, 21 * mm])
    lado = Table([[t_fatos, grafico_roe(emp.ticker, r, emp)]], colWidths=[98 * mm, 84 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)

    # quadro clássico
    story.append(P("Quadro clássico (doutrina §11) — todos os valores ao Ke da casa", "h3"))
    ke, g = r["ke"], r["g"]
    an = list(r["ancoras"].items())
    cat, pl12, peg, pegy, g_real = lynch(emp, r)
    ok7, crit7 = graham7(emp, r)
    proj = projecao(emp, 3)
    linhas = [["Método", "Valor", "Marca", "Fórmula / insumos"]]
    if emp.horizonte_finito:
        hf = emp.horizonte_finito
        linhas.append([an[0][0], f"R$ {br(an[0][1])}", "ÂNCORA",
                       f"dividendos até o fim do contrato ({hf['anos']} anos; payout {pct(emp.payout, 0)}), depois perpetuidade com "
                       f"{pct(hf['prob_renovacao'], 0)} de renovação e lucro {pct(hf['haircut_renov'], 0)} menor; Ke {pct(ke, 2)}"])
        linhas.append(["P/VP justificado perpétuo", f"R$ {br(r['pvp_perpetuo'])}", "INFORMATIVO",
                       f"(ROE {pct(emp.roe_lp)} − g {pct(g)}) ÷ (Ke {pct(ke, 2)} − g) × VPA {br(emp.vpa)} — ignora o fim do contrato; por isso não é âncora"])
    else:
        linhas.append([an[0][0], f"R$ {br(an[0][1])}", "ÂNCORA",
                       f"(ROE {pct(emp.roe_lp)} − g {pct(g)}) ÷ (Ke {pct(ke, 2)} − g) = {br(r['pvp_just'])}× VPA {br(emp.vpa)}"])
        linhas.append([an[1][0], f"R$ {br(an[1][1])}", "ÂNCORA",
                       f"ROE de {pct(emp.roe_inicio)} → {pct(emp.roe_lp)} em 5 anos; payout {pct(emp.payout, 0)}; terminal = P/VP justificado no ano 5"])
    if r["desc_controlador"] > 0:
        linhas.append(["Desconto de controlador", f"−{pct(r['desc_controlador'])}", "no valor",
                       emp.desconto_controlador["razao"]])
    linhas += [
        ["Lucro projetado (próprio)", " · ".join(f"R$ {br(x[2])}" for x in proj), "INFORMATIVO",
         "LPA anos 1–3: ROE convergindo ao de longo prazo sobre VPA que cresce pela retenção. Consenso: não encontrado no material"],
        ["Graham original", f"R$ {br(r['graham_orig'])}", "INFORMATIVO", f"√(22,5 × LPA normalizado {br(r['lpa_norm'])} × VPA)"],
        ["Graham-BR", f"R$ {br(r['graham_br'])}", "INFORMATIVO", f"f = (1/Ke real)/8,5 = {br(MK.fator_graham, 3)}; mesmo LPA normalizado"],
        ["7 critérios do defensivo", f"{ok7} de 5 verificáveis", "INFORMATIVO",
         "; ".join(("[sim] " if v else "[não] ") + n for n, v in crit7) + "; liquidez corrente e LPA +1/3 em 10a: N/A ou série não ajustada"],
        ["Teto de renda (Bazin calibrado)", f"R$ {br(r['teto_renda'])}" if r["teto_renda"] else "N/A", "INFORMATIVO",
         f"DPA sustentável líquido {br(r['dpa_sust_liq'], 3)} ÷ RF nominal líquida {pct(MK.rf_liq_nom, 2)} — preço acima do qual a renda perde para o Tesouro"],
        ["Bazin original (6%)", f"R$ {br(r['bazin6'])}", "INFORMATIVO", "DPA sustentável ÷ 6% — calibrado para outra taxa de juros"],
        ["Lynch", f"PEG {br(peg)} · PEGY {br(pegy)}", "INFORMATIVO",
         f"categoria: {cat}; P/L 12m {br(pl12, 1)} ÷ g nominal {br(100 * g, 1)}% (g real {br(g_real, 1)}%); PEGY soma o DY sustentável"],
        ["DCF reverso", f"ROE {pct(r['roe_implicito'], 0)} · Ke {pct(ki)}", "INFORMATIVO",
         "ROE perpétuo que o preço exige ao Ke da casa; e o Ke que o preço embute com o ROE de longo prazo"],
        ["Bogle (10 anos)", f"{pct(r['bogle_nom'])} nominal", "INFORMATIVO",
         f"investimento (DY {pct(r['dy'])} + g {pct(g)}) = {pct(r['ret_investimento'])} · especulativo (P/L {br(r['pl_atual'], 1)} → "
         f"{br(r['pl_final'], 1)}) = {pct(r['ret_especulativo'])} · real líquido {pct(r['bogle_liq_real'])}"],
        ["FCFE (owner earnings de banco)", f"R$ {br(r['dpa_fcfe'], 3)}/ação", "INFORMATIVO",
         "lucro normalizado × (1 − g/ROE): o que sobra após reter o capital do crescimento" if emp.perfil != "holding_seguro"
         else "capital-leve: lucro normalizado × payout de política"],
        ["Greenblatt · EPV · DCF FCFF · Altman · Piotroski · Beneish · Sloan", "N/A", "N/A por perfil",
         "modelos de empresa não financeira (EBIT, capital investido, dívida como financiamento). Substitutos: P/VP justificado (EPV de financeira) e prudencial na tabela de fatos"],
        ["Teste do R$ 1 retido", "não calculado", "—", "série de VPA/LPA da fonte não ajustada por desdobramento; fica para a coleta CVM"],
    ]
    story.append(tabela(linhas, [33 * mm, 27 * mm, 21 * mm, 101 * mm]))
    story.append(PageBreak())

    # página 2
    story.append(P(f"{emp.ticker} — reconstrução, renda e veredito", "h2"))
    rec = [["Âncora", "Valor", "Peso"]] + [[k, f"R$ {br(v)}", "mediana"] for k, v in r["ancoras"].items()]
    rec.append(["<b>Valor central</b>", f"<b>R$ {br(r['central'])}</b>", f"dispersão {br(r['dispersao'])}× · confiança {r['confianca']}"])
    sens = r["sens"]
    tsens = [["Central (R$)", "ROE −2 p.p.", "ROE base", "ROE +2 p.p."]]
    for dk, nome in ((-0.01, "Ke −1 p.p. (rf real)"), (0, "Ke da casa"), (0.01, "Ke +1 p.p. (rf real)")):
        tsens.append([nome] + [br(sens[(dk, dr)]) for dr in (-0.02, 0, 0.02)])
    lado = Table([[tabela(rec, [38 * mm, 22 * mm, 30 * mm]), tabela(tsens, [24 * mm, 20 * mm, 20 * mm, 20 * mm])]],
                 colWidths=[92 * mm, 90 * mm])
    lado.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    story.append(lado)
    story.append(Spacer(1, 3))
    story.append(P(f"<b>Controlador.</b> {tx['controlador']}", "p"))
    story.append(Spacer(1, 3))

    s = SERIES[emp.ticker]
    dpa = s["dpa_por_ano_datacom"]
    jcp = s["jcp_por_ano_datacom"]
    anos = [a for a in range(2021, 2027)]
    renda = [["Proventos por data-com [SI]"] + [str(a) if a < 2026 else "2026 até 02/10" for a in anos],
             ["DPA total (R$)"] + [br(dpa.get(str(a), 0), 3) for a in anos],
             ["dos quais JCP (R$)"] + [br(jcp.get(str(a), 0), 3) for a in anos]]
    story.append(tabela(renda, [38 * mm] + [24 * mm] * 6))
    story.append(Spacer(1, 2))
    rf = [["Renda e renda fixa (10 anos, líquido de IR)", "Valor"],
          ["Yield sustentável bruto · líquido (JCP × 0,825)", f"{pct(r['dy'])} · {pct(r['dy_liq'])}"],
          ["Coberto por caixa?", "Sim — DPA sustentável ≤ FCFE normalizado" if emp.cobertura_caixa else "Não"],
          ["Retorno esperado real líquido (Bogle)", pct(r["bogle_liq_real"])],
          ["RF real líquida (Tesouro IPCA+ 2050, IR no resgate)", f"{pct(MK.rf_liq_real, 2)} → Sim ≥ {pct(MK.rf_liq_real + .03, 2)} · Empate ≥ {pct(MK.rf_liq_real + .015, 2)}"],
          ["Sem re-rating (só DY + g, líquido real)", f"{pct(r['so_inv_liq_real'])} → {r['rf_sem_rerating']}"],
          ["Vence a RF?", r["vence_rf"] + (" — só se o múltiplo voltar à média histórica; sem isso: " + r["rf_sem_rerating"] if r["so_com_rerating"] else "")
                          + (" — * perde para o Tesouro no ponto médio" if r["carimbo_rf"] else "")]]
    story.append(tabela(rf, [95 * mm, 87 * mm]))
    story.append(Spacer(1, 3))

    n = r["notas"]
    ver = [[P(f"<b>Veredito: <font color='{cor.hexval()}'>{palavra}</font></b> — preço {br(r['pc'])}× o central. "
              f"Compra R$ {br(r['compra'])} · justo R$ {br(r['central'])} · saída R$ {br(r['saida'])}. "
              f"Entrada parcial (exceção §9): {texto_entrada_parcial(r, emp)}.<br/>"
              f"<b>Gatilho que invalida:</b> {tx['gatilho']}<br/>"
              f"<b>Compraria para renda?</b> {tx['renda']}<br/><b>Compraria para ganho de capital?</b> {tx['capital']}<br/>"
              f"<b>Notas</b> (30/20/25/25): qualidade {br(n['qualidade'], 1)} · solidez {br(n['solidez'], 1)} · renda {br(n['renda'], 1)} · "
              f"preço {br(n['preco'], 1)} → <b>{br(n['geral'], 1)}</b>", "box")]]
    tv = Table(ver, colWidths=[182 * mm])
    tv.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, cor), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#FBFBFD")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 6), ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    story.append(tv)
    story.append(Spacer(1, 3))
    sa = Table([[P("<b>3 números que sustentam</b><br/>" + "<br/>".join("• " + x for x in tx["sustentam"]), "cel"),
                 P("<b>3 números que ameaçam</b><br/>" + "<br/>".join("• " + x for x in tx["ameacam"]), "cel")]],
               colWidths=[91 * mm, 91 * mm])
    sa.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("GRID", (0, 0), (-1, -1), 0.3, LINHA)]))
    story.append(sa)
    story.append(Spacer(1, 3))
    antes = ANTES[emp.ticker]
    story.append(P(f"<b>De → para (rev. 03/10 → hoje).</b> {antes[0]}, central R$ {br(antes[1])} → {palavra}, central R$ {br(r['central'])}. "
                   f"Razão (c) — o método v1 estava errado: valor central fora do Ke da casa e/ou inflação de 4% abaixo da implícita (6,46%); "
                   f"preço inalterado (R$ {br(emp.preco)}).", "p"))
    story.append(P("<b>Autocrítica (5 linhas).</b> " + " ".join(f"{i + 1}) {x}" for i, x in enumerate(tx["autocritica"])), "p"))
    story.append(P(f"<b>Eventos com data.</b> {AGENDA}.", "p"))
    story.append(P(f"<b>Não encontrado.</b> {tx['nao_encontrado']}", "pi"))
    story.append(PageBreak())


def capa(res, story):
    story.append(P("Fichas de Avaliação — Value Investing B3", "h1"))
    story.append(P(f"Lote 1 — Bancos e Seguridade (10 empresas) · rev. 09/10/2026 · data-base {DATA_BASE} · doutrina v2.5", "h2"))
    caras = sum(1 for r in res if r["palavra"] == "CARA")
    box = (f"<b>Conclusão.</b> Ao custo de capital da casa (Ke nominal {pct(MK.ke_nom)}), <b>{caras} de 10 estão CARAS</b> e nenhuma está JUSTA, RADAR ou BARATA. "
           f"O preço de cada uma embute um retorno de {pct(min(r['ke_implicito'] for r in res))} a {pct(max(r['ke_implicito'] for r in res))} ao ano — "
           f"perto ou abaixo do que o Tesouro Prefixado paga sem risco (~14,2%). A rev. 03/10 chegou a 7 JUSTAS porque calculou o justo a "
           f"'Ke de mercado' de 14% ou na coluna de taxa real, e supôs inflação de 4% (a implícita é 6,46%). <b>Nenhuma compra autorizada.</b> "
           f"Os preços de compra estão na tabela — é a lista de espera.")
    tb = Table([[P(box, "box")]], colWidths=[182 * mm])
    tb.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 1, AZUL), ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF3F9")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
    story.append(tb)
    story.append(P("Premissas de mercado (doutrina §4)", "h3"))
    prem = [["Parâmetro", "Valor", "Fonte"],
            ["rf: Tesouro IPCA+ 2050 sem cupom (o mais longo sem cupom)", pct(MK.rf_real, 2) + " real", "[TT] taxa de compra, manhã de 02/10 (NTN-B 2050 com cupom fechou a 7,14% [AN])"],
            ["Inflação implícita (ETTJ, 10 anos)", pct(MK.pi, 2), "[AN] fechamento 02/10; Focus 2029–30: 3,50% (sensibilidade) [BCB]"],
            ["Ke real · Ke nominal", f"{pct(MK.ke_real, 2)} · {pct(MK.ke_nom, 2)}", f"rf + {pct(PREMIO_KE, 0)}; (1 + Ke real)(1 + π) − 1"],
            ["RF real líquida · nominal líquida (10 anos, IR 15% no resgate)", f"{pct(MK.rf_liq_real, 2)} · {pct(MK.rf_liq_nom, 2)}", "fórmula da doutrina §4"],
            ["Teto do g perpétuo (π + PIB real de LP)", pct(MK.g_teto, 2), f"PIB real de LP {pct(PIB_REAL_LP, 0)}"],
            ["Selic · IRRF do JCP", f"13,75% · {pct(IR_JCP, 1)}", "BCB (Copom 16/09) · LC 224/2025"]]
    story.append(tabela(prem, [70 * mm, 32 * mm, 80 * mm]))
    story.append(P("Quadro-resumo", "h3"))
    q = [["Ticker", "Palavra", "Preço", "Central", "P/C", "Compra", "Saída", "Ke implícito", "Retorno inv.", "Vence RF", "Nota", "03/10"]]
    for r in sorted(res, key=lambda x: x["pc"]):
        a = ANTES[r["ticker"]]
        q.append([r["ticker"], f"<font color='{COR.get(r['palavra'], AZUL).hexval()}'><b>{r['palavra']}</b></font>", br(r["preco_"]), br(r["central"]),
                  br(r["pc"]), br(r["compra"]), br(r["saida"]), pct(r["ke_implicito"]), pct(r["ret_investimento"]), r["vence_rf"] + ("*" if r["so_com_rerating"] else ""),
                  br(r["notas"]["geral"], 1), f"{a[0]} {br(a[1])}"])
    story.append(tabela(q, [14 * mm, 15 * mm, 13 * mm, 13 * mm, 10 * mm, 13 * mm, 13 * mm, 16 * mm, 16 * mm, 14 * mm, 10 * mm, 25 * mm]))
    story.append(Spacer(1, 4))
    story.append(grafico_resumo(res))
    story.append(P("Retorno inv. = DY sustentável + g (sem re-rating de múltiplo). Ke implícito = taxa que iguala o valor central (mesmo modelo, "
                   "mesmo ROE) ao preço. SANB11 está fora do hall (OPA de permuta, R$ 28,11 implícitos). * Vence a RF só se o múltiplo voltar à média histórica (re-rating); com DY + g apenas: Não.", "pi"))
    story.append(PageBreak())


def metodo(res, story):
    story.append(P("Por que tudo ficou CARA — e por que isso não é exagero", "h2"))
    alt = {r["ticker"]: r for r in (avaliar(e, MK_FOCUS) for e in EMPRESAS)}
    txt = [
        f"<b>1. O Tesouro paga caro.</b> IPCA+ de {pct(MK.rf_real, 2)} real equivale a ~{pct(MK.rf_nom)} nominal sem risco. "
        f"A régua da casa pede 5 p.p. reais a mais de uma ação: {pct(MK.ke_nom)} nominal. Bancos com ROE de 13–18% ao ano não remuneram isso — "
        "destroem valor na régua da casa (ROE < Ke), por isso o P/VP justo fica abaixo de 1× para a maioria.",
        f"<b>2. O mercado aceita menos.</b> O Ke implícito nos preços vai de {pct(min(r['ke_implicito'] for r in res))} a {pct(max(r['ke_implicito'] for r in res))}: "
        "quem compra hoje aceita retorno perto ou abaixo do da renda fixa sem risco (~14,2%). Para o value investor isso é o contrário de margem de segurança.",
        "<b>3. A hipótese escondida de 03/10.</b> Os PDFs anteriores usaram IPCA de 4%, que leva o Tesouro a ~11,3% nominal — mas o Prefixado paga 14,2%. "
        "Com a inflação implícita da própria curva (6,46%) as duas pontas ficam coerentes. Mesmo com os 4% dos PDFs, os 10 continuam CARA "
        "(P/C de " + br(min(a['pc'] for a in alt.values())) + "× a " + br(max(a['pc'] for a in alt.values())) + "×): o que produzia JUSTA era o Ke de mercado e a coluna real.",
        "<b>4. O que mudaria o veredito.</b> Queda do juro real (cada −1 p.p. no Ke sobe o central ~7–11%, ver sensibilidade em cada ficha) ou queda de preço até "
        "a linha de compra. O lote é de empresas boas (ITUB4, PSSA3, CXSE3, BBSE3 têm as melhores notas de qualidade) — o problema é o preço frente à renda fixa.",
    ]
    for t in txt:
        story.append(P(t, "p"))
        story.append(Spacer(1, 2))
    story.append(P("Metodologia (o que cada número significa)", "h2"))
    met = [["Item", "Regra"],
           ["Âncoras (decidem)", "Banco e seguradora: P/VP justificado = (ROE − g)/(Ke − g) e DDM em 2 estágios (ROE converge do atual ao de longo prazo em 5 anos; "
                                 "terminal = P/VP justificado). Holding de seguro com contrato (BBSE3): DDM até o fim do contrato + perpetuidade ponderada pela renovação — âncora única, confiança baixa. "
                                 "Central = mediana das âncoras; dispersão > 1,8× rebaixa, > 3× = não conclusivo."],
           ["ROE de longo prazo", "Mediana dos ROEs anuais de 2016–2025 [SI] — atravessa ciclo de crédito, pandemia e Selic alta. O ROE atual entra como início do DDM."],
           ["g perpétuo", f"ROE × (1 − payout) para todos (doutrina §11) — conservador para seguradoras capital-leve, declarado nas fichas. Teto: π + {pct(PIB_REAL_LP, 0)} real = {pct(MK.g_teto, 2)}."],
           ["Desconto de controlador", "Uma vez, no valor: BBAS3 por cenários (30% × ROE −4 p.p.); BRSR6 fixo de 35% (precedente). Demais: zero, com a razão escrita."],
           ["Informativos", "Graham original e Graham-BR (f = (1/Ke real)/8,5), 7 critérios, teto de renda (Bazin calibrado), Bazin 6%, Lynch (PEG/PEGY), "
                            "DCF reverso, Bogle (investimento + especulativo), FCFE. N/A por perfil: Greenblatt, EPV, DCF FCFF, Altman, Piotroski, Beneish, Sloan."],
           ["Régua e precedência", "P/C ≤ 0,70 BARATA · ≤ 0,90 RADAR · ≤ 1,10 JUSTA · > 1,10 CARA; depois círculo de competência e dispersão; compra só pela palavra final."],
           ["Notas (0–10)", "Qualidade 30% = metade spread ROE de LP − Ke (−6 p.p.→1 … +8 p.p.→10) + metade qualitativo (moat, gestão, controlador, ciclo, Fisher, 0–5). "
                            "Solidez 20% = CET1 (9%→2 … 13%→10), inadimplência 90d (7%→2 … 2%→10), cobertura (100%→3 … 250%→10); seguradoras: nota manual declarada. "
                            "Renda 25% = yield líquido ÷ RF líquida, cobertura por caixa, anos pagos. Preço 25% = escala única da doutrina §10."],
           ["Renda fixa", "Retorno esperado (Bogle) líquido: JCP × 0,825, ganho de capital com 15% diferido; comparado à RF real líquida + 3 p.p. (Sim) ou + 1,5 p.p. (Empate)."],
           ["Dados", "Séries anuais e proventos por data-com: StatusInvest [SI], coletados em 04/10 (cache em ferramentas/dados/raw). Fatos e prudencial: PDFs de 07/09 e 03/10 "
                     "com as fontes primárias que eles citam. Mercado: Tesouro Transparente [TT], ANBIMA [AN], BCB [BCB]. Todas as contas: ferramentas/motor_financeiras.py."]]
    story.append(tabela(met, [32 * mm, 150 * mm]))
    story.append(PageBreak())


def apendice(story):
    story.append(P("Apêndice — fontes", "h2"))
    fontes = {}
    for f in glob.glob(str(AQUI / "dados" / "fatos_*.json")):
        fontes.update(json.loads(pathlib.Path(f).read_text(encoding="utf-8")).get("fontes", {}))
    base = [["[SI]", "https://statusinvest.com.br — indicatorhistoricallist, companytickerprovents e páginas /acoes/{ticker} (04/10/2026)"],
            ["[TT]", "https://www.tesourotransparente.gov.br/ckan/dataset/taxas-dos-titulos-ofertados-pelo-tesouro-direto (PrecoTaxaTesouroDireto.csv)"],
            ["[AN]", "https://www.anbima.com.br — taxas indicativas de títulos públicos (ms261002) e ETTJ de 02/10/2026"],
            ["[BCB]", "https://www.bcb.gov.br/content/focus/focus/R20260925.pdf · histórico de taxas de juros (Copom)"],
            ["PDF 07/09 · 03/10", "Fichas anteriores deste lote (pasta BANCOS E SEGURIDADE) — fontes primárias listadas abaixo"]]
    for k in sorted(fontes):
        v = fontes[k]
        if isinstance(v, dict):
            v = v.get("url") or v.get("valor") or json.dumps(v, ensure_ascii=False)
        base.append([f"[{k}]", str(v)[:180]])
    story.append(tabela([["Rótulo", "Fonte"]] + base, [22 * mm, 160 * mm]))
    story.append(Spacer(1, 4))
    story.append(P("Checklist anti-erro v2 — resultado do lote", "h3"))
    ck = [["Bloco", "Resultado"],
          ["A. Dados", "Cotação de 02/10 com data; RI não reaberto nesta revisão (fatos dos PDFs, fontes listadas); séries do [SI] recalculadas, nada 'da ficha'."],
          ["B. Ke", "Vértice único (IPCA+ 2050 sem cupom) para os 10; inflação implícita; central só ao Ke da casa; Ke de mercado só na sensibilidade."],
          ["C. Ciclo", "ROE de longo prazo pela mediana de 10 anos; ROE atual só como início do DDM."],
          ["D. Proventos", "DPA por data-com ajustado [SI]; yield sustentável = menor entre média 5a e FCFE; JCP líquido de 17,5%."],
          ["E. Controlador", "Linha de desconto em todas as fichas; BBAS3 (cenários) e BRSR6 (35%) descontados uma vez."],
          ["F. Quadro clássico", "Completo, com N/A por perfil declarado; lucro projetado próprio; DCF reverso em todas."],
          ["G. Veredito", "Régua contínua; compra 0,70×, saída 1,30×; trava de coerência não se aplica (nenhuma JUSTA)."],
          ["Pendências", "Consenso de LPA 2027–28; Basileia/CET1 de BRBI11; solvência das seguradoras; teste do R$ 1 (precisa de série ajustada); "
                         "rf = taxa de compra da manhã do Tesouro Direto (o TD não publica fechamento; doutrina v2.4, AUD-06)."]]
    story.append(tabela(ck, [32 * mm, 150 * mm]))


def main():
    res = []
    for e in EMPRESAS:
        r = avaliar(e, MK)
        r["preco_"] = e.preco
        res.append(r)
    guardar(SAIDA, "pdf lote 1")      # AUD-84: o PDF anterior do mesmo nome vai para _historico/
    doc = SimpleDocTemplate(str(SAIDA), pagesize=A4, leftMargin=14 * mm, rightMargin=14 * mm, topMargin=12 * mm, bottomMargin=14 * mm,
                            title="Lote 1 — Bancos e Seguridade · rev. 09/10/2026", author="Mesa de Value Investing")
    story = []
    capa(res, story)
    metodo(res, story)
    ordem = sorted(range(len(EMPRESAS)), key=lambda i: (EMPRESAS[i].ticker == "SANB11", res[i]["pc"]))
    for i in ordem:
        ficha(EMPRESAS[i], res[i], story)
    apendice(story)
    doc.build(story, onFirstPage=rodape, onLaterPages=rodape)
    print("gerado:", SAIDA)


if __name__ == "__main__":
    main()
