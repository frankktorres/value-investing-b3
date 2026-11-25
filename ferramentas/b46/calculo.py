"""Funções puras da B46 (emenda 12 do `docs/PRE-REGISTRO-v3.md`). Sem rede, sem disco, sem importar o motor.

Variante "separar a dificuldade" — Damodaran, *Valuing Distressed and Declining Companies* (jun/2009), p. 14 e 37-42 (nota B):
valor do acionista = valor de continuidade × (1 − π) + ramo de dificuldade × π, com o ramo de dificuldade = 0 (limite
declarado nos dois sentidos na emenda 12), a continuidade a um D/E sustentável (o da indústria) e π = probabilidade
acumulada de calote em 10 anos pela classe de rating (Tabela 5 do paper, de Altman 2007).
Convenções: taxas em fração; D/E a mercado (dívida bruta com arrendamentos ÷ valor de mercado do patrimônio).
"""
from __future__ import annotations

from typing import Mapping

PREMIO = 0.05            # prêmio do Ke real sem dívida dos industriais (01 §4); repetido aqui, sem importar o motor
CONCORDANCIA = 0.20      # |π(i) − π(ii)| ≤ 20 p.p. ≈ uma faixa da régua (emenda 12, C3)
SEM_PI = ("Valor de reprodução",)   # valor de ativo, não de continuidade: fica fora do π (emenda 12, item 3)

# Damodaran (2009), Tabela 5 "Bond Rating and Probability of Default – 1971 - 2007", coluna de 10 anos (p. 41-42)
TABELA_5 = {"AAA": 0.0007, "AA": 0.0051, "A+": 0.0057, "A": 0.0066, "A-": 0.0500, "BBB": 0.0754, "BB": 0.1963,
            "B+": 0.2825, "B": 0.3680, "B-": 0.4212, "CCC": 0.5902, "CC": 0.6660, "C+": 0.7516, "C": 0.8103,
            "C-": 0.8716}
# classe sem linha na Tabela 5 → a pior seguinte que existe (conservador); calote declarado → π = 1 (emenda 12)
PIOR_SEGUINTE = {"AAA/AA+": "AA", "AA/AA-": "A+", "BBB+": "BBB", "BBB-": "BB", "BB+": "BB", "BB-": "B+", "CCC+": "CCC",
                 "CCC-": "CC"}
CALOTE = ("D", "CC/D")

# Altman, *50 Years of Altman Z-Score* (LSE), slide 26, "US Bond Rating Equivalents Based on Z''-Score Model",
# coluna "Median 2013 Z''-Score" (a mais recente e a única monotônica), do melhor ao pior
ALTMAN_2013 = (("AAA/AA+", 8.80), ("AA/AA-", 8.40), ("A+", 8.22), ("A", 6.94), ("A-", 6.12), ("BBB+", 5.80),
               ("BBB", 5.75), ("BBB-", 5.70), ("BB+", 5.65), ("BB", 5.52), ("BB-", 5.07), ("B+", 4.81), ("B", 4.03),
               ("B-", 3.74), ("CCC+", 2.84), ("CCC", 2.57), ("CCC-", 1.72), ("CC/D", 0.05))


def pi_de_classe(classe: str) -> float:
    """π acumulada de 10 anos da classe. Classe desconhecida → KeyError (falha alto, nunca um padrão)."""
    if classe in CALOTE:
        return 1.0
    return TABELA_5[PIOR_SEGUINTE.get(classe, classe)]


def rating_altman(z: float) -> str:
    """A melhor classe cuja mediana de 2013 ≤ Z''; abaixo da última mediana, a pior classe (CC/D)."""
    for classe, mediana in ALTMAN_2013:
        if z >= mediana:
            return classe
    return ALTMAN_2013[-1][0]


def de_da_participacao(d_sobre_d_mais_e: float) -> float:
    """D/(D+E) → D/E."""
    return d_sobre_d_mais_e / (1 - d_sobre_d_mais_e)


def de_continuidade(de_mercado: float, de_industria: float) -> float:
    """D/E da continuidade = o menor entre o a mercado e o da indústria (Damodaran 2009, p. 14 e 38)."""
    return min(de_mercado, de_industria)


def ke_nominal(rf_real: float, pi_inflacao: float, t: float, de: float) -> float:
    """Ke nominal = (1 + rf real + 5 p.p. × [1 + (1 − t) × D/E]) × (1 + π) − 1 (Hamada, 01 §4)."""
    return (1 + rf_real + PREMIO * (1 + (1 - t) * de)) * (1 + pi_inflacao) - 1


def pi_combinado(pi_i: float | None, pi_ii: float | None) -> float | None:
    """Média das 2 estimativas; com uma só, a única (marcada no relatório); sem nenhuma, None (não avaliado)."""
    xs = [x for x in (pi_i, pi_ii) if x is not None]
    return sum(xs) / len(xs) if xs else None


def concordam(pi_i: float | None, pi_ii: float | None) -> bool:
    """C3: as duas existem e diferem no máximo 20 p.p."""
    return pi_i is not None and pi_ii is not None and abs(pi_i - pi_ii) <= CONCORDANCIA + 1e-12


def ancoras_com_pi(anc: Mapping[str, float], pi: float) -> dict[str, float]:
    """Cada âncora de continuidade × (1 − π); as de ativo (reprodução) ficam iguais."""
    return {k: (x if k in SEM_PI else x * (1 - pi)) for k, x in anc.items()}
