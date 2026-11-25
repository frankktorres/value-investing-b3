"""Funções puras da B39 (emenda 9 do `docs/PRE-REGISTRO-v3.md`, atribuições corrigidas pela emenda 10). Sem rede, sem disco.

Convenções: taxas em fração (0,0786 = 7,86% a.a.); nominal → real sempre por (1 + x) ÷ (1 + π) − 1; valores em R$ mil.
"""
from __future__ import annotations

import statistics as st
from typing import Iterable, Sequence

G_REAL = 0.01            # g real dos bancos (o do B39)
LIMIAR = 0.03            # X = 3 p.p., no Ke real, nos dois sentidos
PREMIO = 0.05            # prêmio da Mesa: fixo nas financeiras; base sem dívida nas demais (01 §4)
T_HAMADA = 0.34          # simplificação declarada da emenda 9 (o motor usa a alíquota perpétua de cada uma)
JANELA = 10              # exercícios
MINIMO = 5               # exercícios; abaixo, fora (Graham & Dodd, 1934, p. 452, citado em Campbell & Shiller)
COBERTURA_MIN = 0.5      # (ii) não sai com menos da metade do valor de mercado do índice


def real(nominal: float, pi: float) -> float:
    return (1 + nominal) / (1 + pi) - 1


def nominal(real_: float, pi: float) -> float:
    return (1 + real_) * (1 + pi) - 1


# ------------------------------------------------------------------------------------------------ (i) bancos
def roe_anuais(lucro: dict[int, float], pl: dict[int, float]) -> dict[int, float]:
    """ROE nominal do exercício = lucro do controlador ÷ PL médio do controlador (início e fim). Ano sem PL do anterior,
    com PL médio ≤ 0 ou sem lucro fica fora."""
    out = {}
    for a, l in sorted(lucro.items()):
        p0, p1 = pl.get(a - 1), pl.get(a)
        if l is None or p0 is None or p1 is None:
            continue
        m = (p0 + p1) / 2
        if m > 0:
            out[a] = l / m
    return out


def roe_normalizado(roes: dict[int, float]) -> float | None:
    """Mediana dos 10 últimos exercícios (mínimo 5); None abaixo do mínimo."""
    xs = [roes[a] for a in sorted(roes)][-JANELA:]
    return st.median(xs) if len(xs) >= MINIMO else None


def ke_banco(roe_nom: float, pvp: float, g_real: float, pi: float) -> tuple[float, float]:
    """Gordon sobre o P/VP, todo em nominal (o ROE contábil é nominal): Ke_nom = g_nom + (ROE − g_nom) ÷ (P/VP), com
    g_nom = (1 + g_real)(1 + π) − 1; depois Ke_real = (1 + Ke_nom) ÷ (1 + π) − 1. Devolve (Ke_nom, Ke_real)."""
    if pvp <= 0:
        raise ValueError(f"P/VP não positivo: {pvp}")
    g = nominal(g_real, pi)
    k = g + (roe_nom - g) / pvp
    return k, real(k, pi)


def inflacao_acumulada(taxas_mensais: Sequence[float]) -> float:
    """Inflação acumulada de variações mensais em fração (IPCA do ano = jan–dez da SGS 433)."""
    f = 1.0
    for t in taxas_mensais:
        f *= 1 + t
    return f - 1


def roe_reais(roes_nom: dict[int, float], ipca_ano: dict[int, float]) -> dict[int, float]:
    """Emenda 11: ROE real do exercício = (1 + ROE nominal) ÷ (1 + IPCA do próprio ano) − 1. Ano sem IPCA fica fora."""
    return {a: real(r, ipca_ano[a]) for a, r in roes_nom.items() if a in ipca_ano}


def ke_banco_real(roe_real: float, pvp: float, g_real: float) -> float:
    """Emenda 11: Gordon todo em real, Ke real = g real + (ROE real − g real) ÷ (P/VP). Nenhuma π futura entra."""
    if pvp <= 0:
        raise ValueError(f"P/VP não positivo: {pvp}")
    return g_real + (roe_real - g_real) / pvp


# ------------------------------------------------------------------------------------------------ (ii) índice
def e10(lucros_reais: Sequence[float | None]) -> float | None:
    """Média aritmética dos 10 últimos lucros reais (em ordem cronológica; mínimo 5 válidos). Princípio do CAPE: a construção
    vem de Campbell & Shiller; a leitura E10 ÷ P = Ke real é o EPV reverso da Mesa (emenda 10)."""
    xs = [x for x in list(lucros_reais)[-JANELA:] if x is not None]
    return sum(xs) / len(xs) if len(xs) >= MINIMO else None


def ke_indice(comps: Iterable[dict], vm_total: float) -> dict:
    """Agregado do índice = Σ E10 ÷ Σ valor de mercado das que têm E10 (todas as classes de ação), **nunca** a média dos E/P
    individuais. `comps`: dicts com `e10` (None = fora) e `vm`. Sai `ke` None se a cobertura (VM com E10 ÷ VM do índice) < 50%."""
    dentro = [c for c in comps if c.get("e10") is not None and c.get("vm")]
    se = sum(c["e10"] for c in dentro)
    sv = sum(c["vm"] for c in dentro)
    cob = sv / vm_total if vm_total else 0.0
    return {"ke": (se / sv if sv and cob >= COBERTURA_MIN else None), "soma_e10": se, "soma_vm": sv,
            "cobertura": cob, "n": len(dentro)}


def ke_gordon_indice(payout: float, e10_: float, p: float, g_real: float) -> float:
    """Sensibilidade: Ke real = payout × E10 × (1 + g) ÷ P + g (emenda 9)."""
    return payout * e10_ * (1 + g_real) / p + g_real


# ------------------------------------------------------------------------------------------------ (iii) Damodaran
def ke_damodaran(rf_real: float, pi: float, s: float, erp: float) -> tuple[float, float]:
    """Ke nominal R$ = n − s + ERP total, n = (1 + rf)(1 + π) − 1 (o spread de default sai da taxa em moeda local antes de somar
    o ERP total: Damodaran, Country Risk 2024 p. 101; riskfree 2008). Devolve (Ke_nom, Ke_real)."""
    k = nominal(rf_real, pi) - s + erp
    return k, real(k, pi)


def ke_damodaran_literal(rf_real: float, erp: float) -> float:
    """Sensibilidade "sem tirar s": rf real da NTN-B + ERP total (forma literal)."""
    return rf_real + erp


# ------------------------------------------------------------------------------------------------ Ke da Mesa
def premio_componente(financeira: bool, divida: float | None, vm: float) -> float:
    """5 p.p. na financeira; 5 × [1 + (1 − 0,34) × D/E] nas demais (Hamada, D/E a mercado da v2.7)."""
    if financeira:
        return PREMIO
    if divida is None or vm <= 0:
        raise ValueError("não financeira sem dívida ou valor de mercado")
    return PREMIO * (1 + (1 - T_HAMADA) * max(divida, 0.0) / vm)


def premio_indice(comps: Iterable[dict]) -> float:
    """Média dos prêmios ponderada pelo valor de mercado. `comps`: dicts com `premio` e `vm`."""
    cs = [c for c in comps if c.get("premio") is not None and c.get("vm")]
    sv = sum(c["vm"] for c in cs)
    if not sv:
        raise ValueError("índice sem valor de mercado")
    return sum(c["premio"] * c["vm"] for c in cs) / sv


# ------------------------------------------------------------------------------------------------ gatilho
def gatilho(deltas: dict[str, float | None]) -> dict:
    """|mediana dos Δ| > 3 p.p. dispara, nos dois sentidos. Estimativa que não sai não é trocada: com 2, a mediana das 2 (a
    média); com menos de 2, NÃO CONCLUSIVA. Igual a 3,00 p.p. não dispara (o limite é estrito; arredonda a 1e-10)."""
    vals = [v for v in deltas.values() if v is not None]
    faltam = sorted(k for k, v in deltas.items() if v is None)
    if len(vals) < 2:
        return {"veredito": "NÃO CONCLUSIVA", "mediana": None, "n": len(vals), "faltam": faltam}
    m = st.median(vals)
    dispara = round(abs(m), 10) > LIMIAR
    return {"veredito": "DISPARA" if dispara else "NÃO DISPARA", "mediana": m, "n": len(vals), "faltam": faltam,
            "sentido": ("Ke da Mesa abaixo do implícito" if m > 0 else "Ke da Mesa acima do implícito") if dispara else ""}
