"""Relatório em PDF (reportlab, mesmo estilo dos `gerar_pdf_lote*.py`): cada número com valor, nota e fonte na mesma linha.

O PDF é uma vista do mesmo `Relatorio` que o Markdown usa — nada é recalculado aqui. Fonte Arial do Windows; sem ela (outra
máquina) cai para Helvetica e troca os símbolos que ela não tem (≥, ≤, →, −, √) por equivalentes em ASCII.
"""
from __future__ import annotations

import pathlib
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from relatorio.modelo import Numero, Relatorio, decide
from relatorio.render_md import PAPEL, fmt

FONTES = {"Arial": "arial.ttf", "Arial-B": "arialbd.ttf", "Arial-I": "ariali.ttf", "Arial-BI": "arialbi.ttf"}
PASTA_FONTES = pathlib.Path("C:/Windows/Fonts")
TROCAS = {"≥": ">=", "≤": "<=", "→": "->", "−": "-", "√": "raiz ", "Σ": "soma", "≈": "~", "±": "+/-"}


def _registrar() -> tuple[str, str, str]:
    """(normal, negrito, itálico): Arial se os quatro TTF existem, senão Helvetica."""
    if all((PASTA_FONTES / f).exists() for f in FONTES.values()):
        for nome, arq in FONTES.items():
            if nome not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont(nome, str(PASTA_FONTES / arq)))
        pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-B", italic="Arial-I", boldItalic="Arial-BI")
        return "Arial", "Arial-B", "Arial-I"
    return "Helvetica", "Helvetica-Bold", "Helvetica-Oblique"


NORMAL, NEGRITO, ITALICO = _registrar()
COM_ARIAL = NORMAL == "Arial"
AZUL = colors.HexColor("#1F3A5F")
CINZA = colors.HexColor("#F2F4F7")
LINHA = colors.HexColor("#C9D1DC")
ALERTA = colors.HexColor("#B83232")
COR_PALAVRA = {"BARATA": "#1E7B3A", "RADAR": "#2F6DB5", "JUSTA": "#B7791F", "CARA": "#B83232", "NÃO CONCLUSIVO": "#6B7280"}

S = {
    "h1": ParagraphStyle("h1", fontName=NEGRITO, fontSize=17, leading=21, textColor=AZUL, spaceAfter=4),
    "h2": ParagraphStyle("h2", fontName=NEGRITO, fontSize=11.5, leading=14, textColor=AZUL, spaceBefore=8, spaceAfter=3, keepWithNext=1),
    "h3": ParagraphStyle("h3", fontName=NEGRITO, fontSize=8.6, leading=11, textColor=AZUL, spaceBefore=5, spaceAfter=2, keepWithNext=1),
    "p": ParagraphStyle("p", fontName=NORMAL, fontSize=8.2, leading=10.4, alignment=TA_LEFT, spaceAfter=3),
    "pi": ParagraphStyle("pi", fontName=ITALICO, fontSize=7.6, leading=9.6, textColor=colors.HexColor("#4B5563")),
    "cel": ParagraphStyle("cel", fontName=NORMAL, fontSize=7.4, leading=9),
    "celb": ParagraphStyle("celb", fontName=NEGRITO, fontSize=7.4, leading=9),
    "obs": ParagraphStyle("obs", fontName=ITALICO, fontSize=6.6, leading=8, textColor=colors.HexColor("#4B5563")),
    "aviso": ParagraphStyle("aviso", fontName=NORMAL, fontSize=8, leading=10.2, textColor=colors.HexColor("#7A1F1F")),
}


def _seguro(t: str) -> str:
    if not COM_ARIAL:
        for a, b in TROCAS.items():
            t = t.replace(a, b)
    return t


def _md(t: str) -> str:
    """Texto do relatório → marcação do Paragraph: escapa o XML e converte **negrito**."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", _seguro(escape(str(t))))


def P(t: str, st: str = "cel") -> Paragraph:
    return Paragraph(_md(t), S[st])


def _tabela(dados: list[list], larg: list[float], zebra: bool = True) -> Table:
    t = Table([[c if not isinstance(c, str) else P(c, "celb" if i == 0 else "cel") for c in linha] for i, linha in enumerate(dados)],
              colWidths=larg, repeatRows=1)
    est = [("GRID", (0, 0), (-1, -1), 0.3, LINHA), ("VALIGN", (0, 0), (-1, -1), "TOP"),
           ("TOPPADDING", (0, 0), (-1, -1), 1.6), ("BOTTOMPADDING", (0, 0), (-1, -1), 1.6),
           ("LEFTPADDING", (0, 0), (-1, -1), 3), ("RIGHTPADDING", (0, 0), (-1, -1), 3),
           ("BACKGROUND", (0, 0), (-1, 0), CINZA)]
    if zebra:
        est += [("BACKGROUND", (0, i), (-1, i), colors.HexColor("#FAFBFC")) for i in range(2, len(dados), 2)]
    t.setStyle(TableStyle(est))
    return t


def _nota(n: Numero) -> Paragraph:
    if n.valor is None and not n.origens:
        return P("")
    if decide(n.nota) or n.valor is None:
        return P(n.nota)
    return Paragraph(f'<font color="#B83232"><b>{escape(n.nota)}</b></font>', S["cel"])


def _numeros(nums: list[Numero], larg: float) -> Table:
    w = [larg * f for f in (0.36, 0.15, 0.10, 0.07, 0.32)]
    linhas: list[list] = [["Item", "Valor", "Papel", "Nota", "Fonte"]]
    for n in nums:
        item = [P(n.rotulo)] + ([P(n.obs, "obs")] if n.obs and n.valor is not None else [])
        fonte = n.obs if n.valor is None and n.obs else n.fonte
        linhas.append([item, P(fmt(n.valor, n.unidade)), P(PAPEL.get(n.papel, n.papel)), _nota(n), P(fonte)])
    return _tabela(linhas, w)


def _caixa_palavra(rel: Relatorio, larg: float) -> Table:
    cor = colors.HexColor(COR_PALAVRA.get(rel.palavra, "#6B7280"))
    t = Table([[Paragraph(f'<font color="white"><b>{escape(rel.palavra)}</b></font>',
                          ParagraphStyle("pal", fontName=NEGRITO, fontSize=15, leading=18, alignment=1)),
                P(f"Data-base {rel.data} · origem: {rel.origem}", "p")]], colWidths=[larg * 0.28, larg * 0.72])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), cor), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("BOX", (0, 0), (-1, -1), 0.5, LINHA), ("TOPPADDING", (0, 0), (-1, -1), 5),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    return t


def _rodape(rotulo: str):
    def desenhar(canvas, doc):
        _desenha_rodape(canvas, doc, rotulo)
    return desenhar


def _desenha_rodape(canvas, doc, rotulo):
    canvas.saveState()
    canvas.setFont(NORMAL, 6.8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    canvas.drawString(15 * mm, 9 * mm, _seguro(f"{rotulo} — vista dos motores do repositório; não é recomendação nem ordem de compra/venda."))
    canvas.drawRightString(A4[0] - 15 * mm, 9 * mm, f"p. {doc.page}")
    canvas.restoreState()


def historia(rel: Relatorio, larg: float) -> list:
    H = [Paragraph(_md(f"{rel.tk} — {rel.nome}"), S["h1"]), _caixa_palavra(rel, larg), Spacer(1, 3 * mm),
         P("Nota da fonte: A oficial (CVM, B3, Tesouro, ANBIMA, BCB); B primária com ressalva; C agregador ou não conferido; "
           "— sem fonte numérica. Só A/B embasa decisão; C e — aparecem em vermelho em vez de escondidos.", "pi")]
    if rel.avisos:
        H += [Paragraph("Avisos", S["h2"])] + [Paragraph("• " + _md(a), S["aviso"]) for a in rel.avisos]
    for s in rel.secoes:
        H.append(Paragraph(_md(s.titulo), S["h2"]))
        if s.numeros:
            H.append(_numeros(s.numeros, larg))
        for titulo, cab, linhas in s.tabelas:
            H += [Paragraph(_md(titulo), S["h3"]), _tabela([cab] + linhas, [larg / len(cab)] * len(cab))]
        for x in s.texto:
            H += [Spacer(1, 1.5 * mm), P(x, "p")]
        for a in s.avisos:
            if a not in rel.avisos:
                H.append(Paragraph("• " + _md(a), S["aviso"]))
    H += [Paragraph("Fontes", S["h2"]),
          _tabela([["Fonte", "Nota", "O que é"]] + [[o.fonte, o.nota, o.detalhe or o.fonte] for o in rel.fontes().values()],
                  [larg * 0.22, larg * 0.07, larg * 0.71])]
    return H


def render(rel: Relatorio, destino: pathlib.Path) -> pathlib.Path:
    larg = A4[0] - 30 * mm
    doc = SimpleDocTemplate(str(destino), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=14 * mm,
                            bottomMargin=16 * mm, title=_seguro(f"{rel.tk} — relatório"), author="Mesa de Value Investing")
    rodape = _rodape(f"{rel.tk} {rel.data}")
    doc.build(historia(rel, larg), onFirstPage=rodape, onLaterPages=rodape)
    return destino
