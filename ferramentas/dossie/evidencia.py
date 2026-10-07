"""Evidência quantitativa das notas qualitativas (02 v4, regra 11) — insumos mecânicos da rubrica de `notas.py`.

Tudo sai do resultado do motor (`avaliar`) e das séries da CVM já carregadas; nada é digitado. O que a rubrica pede e não é
mecânico (M&A ruim, interferências consumadas, os 15 pontos de Fisher, ajustes ±1) vem do arquivo de insumos do dossiê
(`dossie/insumos/<TK>.json`), cada item com fonte — ver `gerar.py`.
"""
from __future__ import annotations

import csv
import math
import pathlib
import re

from inflacao import fator_entre
from motor_nao_financeiras import CVM, ebit_aj

RAIZ = pathlib.Path(__file__).resolve().parent.parent
TRIAGEM = sorted((RAIZ / "triagem" / "dados").glob("triagem_*.csv"))


def margens(tk: str, anos: list[str], med_outras: float | None, liquidas: bool) -> dict[str, dict[str, float]]:
    """Margem bruta e margem EBIT ajustada (sem "outras" não recorrentes, como no motor) por exercício."""
    a = CVM[tk]["anual"]
    out = {}
    for x in anos:
        d = a.get(x, {})
        if not d.get("receita"):
            continue
        out[x] = {"bruta": (d.get("lucro_bruto") or 0) / d["receita"] if d.get("lucro_bruto") is not None else None,
                  "ebit": ebit_aj(d, med_outras, liquidas) / d["receita"], "ebit_contabil": d.get("ebit")}
    return out


def receitas_reais(tk: str, anos: list[str]) -> dict[str, float]:
    """Receita de cada exercício em R$ do último exercício da lista (IPCA)."""
    a = CVM[tk]["anual"]
    ult = anos[-1]
    return {x: a[x]["receita"] * fator_entre(x, ult) for x in anos if a.get(x, {}).get("receita")}


def r1_da_triagem(tk: str) -> float | str | None:
    """Q4 (R$ 1 retido) da última triagem, no mesmo dia-base e sobre o ledger point-in-time: número, "n/a" (retém
    pouco — teste indefinido) ou None (não medido: hall excluído da triagem, ou janela curta)."""
    if not TRIAGEM:
        return None
    with open(TRIAGEM[-1], encoding="utf-8") as f:
        for lin in csv.DictReader(f):
            if lin["ticker"] != tk:
                continue
            q4 = lin.get("Q4") or ""
            if q4.startswith("n/a retém"):
                return "n/a"
            m = re.search(r"R\$ (-?[\d\.]+,\d+)", q4)
            return float(m.group(1).replace(".", "").replace(",", ".")) if m else None
    return None


def diluicao(tk: str, anos: list[str], eventos: list[dict], primeiro_listado: str) -> tuple[float | None, str]:
    """CAGR das ações em circulação desde o 1º fim de exercício com ação negociada (antes disso a contagem não é a do
    acionista de bolsa), com as bonificações e desdobramentos desfeitos (não diluem). Recompra líquida → CAGR negativo."""
    a = CVM[tk]["anual"]
    xs = [x for x in anos if x >= primeiro_listado and a.get(x, {}).get("acoes")]
    if len(xs) < 2:
        return None, "menos de 2 exercícios com ação negociada"

    def ajust(x):       # só o evento aprovado DENTRO da janela: o anterior a ela (HYPE3, desdobramento de 2009) já está nas duas pontas
        n = a[x]["acoes"]
        for e in eventos:
            if f"{xs[0]}-12-31" < e["aprovacao"] <= f"{x}-12-31":
                n /= e["multiplicador"]
        return n
    n0, n1, t = ajust(xs[0]), ajust(xs[-1]), int(xs[-1]) - int(xs[0])
    return (n1 / n0) ** (1 / t) - 1, f"{xs[0]} → {xs[-1]}: {n0 / 1e6:,.1f} → {n1 / 1e6:,.1f} mi (bonificações/desdobramentos desfeitos)"


def remuneracao_sobre_lucro(tk: str, rem: dict, anos: list[str]) -> tuple[float | None, str]:
    """Remuneração total da administração (FRE) ÷ lucro do controlador, médias dos mesmos exercícios (até 3)."""
    a = CVM[tk]["anual"]
    comuns = [x for x in anos if x in rem and a.get(x, {}).get("lucro") is not None][-3:]
    if not comuns:
        return None, "sem exercício comum entre FRE e DFP"
    lucro = sum((a[x].get("lucro_controlador") or a[x]["lucro"]) * 1000 for x in comuns) / len(comuns)
    r = sum(rem[x]["total"] for x in comuns) / len(comuns)
    if lucro <= 0:
        return None, f"lucro médio ≤ 0 em {comuns}"
    return r / lucro, f"{comuns}: remuneração média R$ {r / 1e6:,.1f} mi ÷ lucro médio R$ {lucro / 1e6:,.1f} mi"


def partes_relacionadas_bruto(tk: str, partes: list[dict], ano_receita: str) -> tuple[float | None, str]:
    """Soma do montante das transações do FRE ÷ receita do exercício. BRUTO: o montante do FRE é o valor do contrato
    (às vezes plurianual ou um saldo), não o fluxo do ano — o dossiê confere pela nota explicativa (D7) e usa a nota."""
    rec = CVM[tk]["anual"][ano_receita]["receita"] * 1000
    tot = sum(p["montante"] or 0 for p in partes)
    return (tot / rec if rec else None), f"{len(partes)} transações, R$ {tot / 1e6:,.1f} mi ÷ receita {ano_receita}"


def mna_provavel(tk: str, anos: list[str]) -> list[str]:
    """Exercícios em que intangível + investimentos saltaram mais de 20% do ativo: sinal de aquisição a examinar."""
    a = CVM[tk]["anual"]
    out = []
    for x0, x1 in zip(anos, anos[1:]):
        d0, d1 = a.get(x0, {}), a.get(x1, {})
        if not (d0.get("ativo") and d1.get("ativo")):
            continue
        salto = ((d1.get("intangivel") or 0) + (d1.get("investimentos") or 0)) - \
                ((d0.get("intangivel") or 0) + (d0.get("investimentos") or 0))
        if salto > 0.20 * d0["ativo"]:
            out.append(x1)
    return out


def anos_prejuizo(tk: str, anos: list[str]) -> int:
    a = CVM[tk]["anual"]
    return sum(1 for x in anos if (a.get(x, {}).get("ebit") or 0) < 0)


def finito(x):
    return x if isinstance(x, (int, float)) and math.isfinite(x) else None
