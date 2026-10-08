"""Spread de crédito sintético pela cobertura de juros — Kd na falta do custo médio da dívida do RI (doutrina §2, v2.4).

AUD-07 (auditoria 08/10/2026): o spread era digitado por ticker (0,5 a 2,5 p.p.) sem fonte. Agora vem de uma tabela publicada:
Damodaran, "Ratings, Interest Coverage Ratios and Default Spread", tabela para empresas não financeiras grandes, dados de
janeiro de 2026 — https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ratings.html (aberta em 08/10/2026; nota B:
base de dados do autor, não de regulador). A página diz que o spread somado à taxa livre de risco dá o custo da dívida antes do IR.

Por que não juros pagos ÷ dívida bruta: o cupom de dívida em dólar (SUZB3, KLBN11, PETR4) não é o custo em reais (a paridade
coberta devolve a diferença de inflação pelo câmbio) e o juro do arrendamento fica fora da linha da DFC — o quociente ia de
3% (PETR4) a 29% (ABEV3, dívida mínima). Somar o spread à rf NOMINAL em reais mantém a moeda do fluxo.
"""
from __future__ import annotations

FONTE = "Damodaran, ratings.html, empresas não financeiras grandes, jan/2026 (nota B)"

# (cobertura até — exclusive, rating, spread)
TABELA = (
    (0.20, "D", 0.1900),
    (0.65, "C", 0.1600),
    (0.80, "CC", 0.1261),
    (1.25, "CCC", 0.0885),
    (1.50, "B-", 0.0509),
    (1.75, "B", 0.0321),
    (2.00, "B+", 0.0275),
    (2.25, "BB", 0.0184),
    (2.50, "BB+", 0.0138),
    (3.00, "BBB", 0.0111),
    (4.25, "A-", 0.0089),
    (5.50, "A", 0.0078),
    (6.50, "A+", 0.0070),
    (8.50, "AA", 0.0055),
    (float("inf"), "AAA", 0.0040),
)


def spread_sintetico(cobertura: float | None) -> tuple[float, str]:
    """(spread, rating) para a cobertura = lucro operacional ÷ juros. Sem juros (None ou infinita) → AAA."""
    if cobertura is None:
        return TABELA[-1][2], TABELA[-1][1]
    for limite, rating, spread in TABELA:
        if cobertura < limite:
            return spread, rating
    return TABELA[-1][2], TABELA[-1][1]
