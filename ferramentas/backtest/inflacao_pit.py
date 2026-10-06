"""IPCA point-in-time: índice truncado no último mês que já era público na data de corte.

Por que o backtest não usa `ferramentas/inflacao.py`: aquele módulo é correto para a mesa de hoje e
errado para 2015. Ele deriva tudo do ÚLTIMO mês da série (`BASE_MES`, `BASE`, `DEFLATOR`,
`indice_ha`, `reposicao`), e até `MEDIA_ANO[ano]` — usado por `fator_entre` — é a média dos 12 meses
do ano. Em T = 30/06/2020, a média de 2020 inteiro é meio ano de inflação que ninguém conhecia.
Pequeno em reais, mas é vazamento na fundação, e a fundação é o que os outros testes tomam como
verdade.

A FONTE é a mesma e é fonte A: `dados/macro/ipca_mensal.json` (BCB, SGS 433, variação mensal em %,
desde 01/1980, versionada no git). O que não se reaproveita são as constantes derivadas, não o dado.

Convenção da casa, preservada: o índice de um exercício é a MÉDIA dos índices mensais do ano, porque
receita e capex se acumulam ao longo do ano. Aqui a média é sobre os meses que já eram públicos em T.

Disponibilidade: o IPCA do mês m sai por volta do dia 10 de m+1. Como os cortes são sempre fim de
mês, em T conhece-se até o mês anterior — ver calendario.mes_ipca_disponivel.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

FONTE = Path(__file__).resolve().parent.parent / "dados" / "macro" / "ipca_mensal.json"

IDADE_MIN, IDADE_MAX = 1.0, 15.0        # limites da doutrina §11.1, iguais aos de inflacao.py


def _n(mes: str) -> int:
    """'2014-06' → meses desde o ano 0, para aritmética de prazo sem calendário."""
    ano, m = mes.split("-")
    return int(ano) * 12 + int(m) - 1


def _mes(n: int) -> str:
    return f"{n // 12:04d}-{n % 12 + 1:02d}"


@lru_cache(maxsize=1)
def _indice() -> dict[int, float]:
    """Índice acumulado por mês (base arbitrária: só razões importam)."""
    serie = json.loads(FONTE.read_text(encoding="utf-8"))
    indice, acc = {}, 1.0
    for reg in serie:
        _, mm, aa = reg["data"].split("/")
        acc *= 1 + float(reg["valor"]) / 100
        indice[int(aa) * 12 + int(mm) - 1] = acc
    return indice


def cobertura() -> tuple[str, str]:
    i = _indice()
    return _mes(min(i)), _mes(max(i))


def indice_mes(mes: str, corte_mes: str) -> float:
    """Índice do mês `mes`, exigindo que ele fosse público em `corte_mes`.

    `corte_mes` é o último mês de IPCA disponível na data de corte
    (calendario.mes_ipca_disponivel). Pedir mês posterior é look-ahead e levanta erro — em vez de
    devolver silenciosamente o extremo da série, como faz o módulo da mesa.
    """
    if mes > corte_mes:
        raise ValueError(
            f"IPCA de {mes} não era público em um corte cujo último mês disponível é {corte_mes}")
    i = _indice()
    n = _n(mes)
    if n < min(i):
        n = min(i)                       # antes de 1980 não há série: usa o primeiro, declarado
    if n not in i:
        raise ValueError(f"IPCA de {mes} não está na série (cobertura {cobertura()})")
    return i[n]


def media_ano(ano: int | str, corte_mes: str) -> float:
    """Índice médio do exercício `ano`, sobre os meses JÁ PÚBLICOS em `corte_mes`.

    Para um exercício inteiramente anterior ao corte são os 12 meses — idêntico ao MEDIA_ANO da
    mesa. Para o ano do próprio corte é média parcial, que é o que se sabia.
    """
    a = int(ano)
    i, limite = _indice(), _n(corte_mes)
    meses = [v for n, v in i.items() if n // 12 == a and n <= limite]
    if not meses:
        primeiro, ultimo = min(i) // 12, limite // 12
        if a < primeiro:                 # exercício antes da série: usa o primeiro ano medido
            return media_ano(primeiro, corte_mes)
        raise ValueError(f"nenhum mês de {a} era público em {corte_mes} (série até {_mes(ultimo)})")
    return sum(meses) / len(meses)


def fator_mes(de_mes: str, para_mes: str, corte_mes: str) -> float:
    """Fator que expressa R$ do mês `de_mes` em R$ do mês `para_mes`, visto de `corte_mes`.

    Preferir este a `fator_entre` quando a base precisa ser ESTÁVEL entre datas de corte. A média
    do exercício (`media_ano`) é truncada no corte, então o mesmo ano rende denominadores
    diferentes vistos de 2014-05 e de 2016-05 — medido: 1,55% de diferença para 2014. Isso é
    correto para dado contábil (o exercício de fato só se conhece inteiro depois), e errado para
    uma base de referência, que tem de ser a mesma régua em todos os cortes.
    """
    return indice_mes(para_mes, corte_mes) / indice_mes(de_mes, corte_mes)


def fator_entre(de: int | str, para: int | str, corte_mes: str) -> float:
    """Fator que expressa R$ do exercício `de` em R$ do exercício `para`, visto de `corte_mes`.

    Equivalente ao inflacao.fator_entre, mas com a média do ano truncada no corte e com a data de
    referência obrigatória, não implícita.
    """
    return media_ano(para, corte_mes) / media_ano(de, corte_mes)


def idade_media(imobilizado: float, da: float) -> float:
    """Idade média ≈ imobilizado líquido ÷ D&A anual, limitada a [1, 15] anos (§11.1).

    Mesma aproximação declarada da mesa: a D&A da DFC inclui amortização de intangível e de direito
    de uso, o que subestima a idade — a correção sai conservadora.
    """
    if not da or da <= 0 or imobilizado <= 0:
        return IDADE_MIN
    return min(max(imobilizado / da, IDADE_MIN), IDADE_MAX)


def fator_idade(ano: int | str, idade: float, corte_mes: str) -> float:
    """Corrige um imobilizado de `idade` anos para os preços médios do exercício `ano`, visto de T.

    Referência: meio do exercício (os valores se acumulam ao longo dele), nunca além do corte.
    """
    i = _indice()
    ref = min(_n(f"{int(ano):04d}-07"), _n(corte_mes))
    agora = i.get(ref) or i[max(k for k in i if k <= ref)]
    # Mês mais PRÓXIMO disponível, não o primeiro da série. O fallback para 1980 daria um fator
    # absurdo (46 anos de inflação) se algum mês faltasse; a série é contínua desde 01/1980, então
    # isto é latente — mas o modo de falhar importa mais que a probabilidade.
    alvo = max(ref - round(idade * 12), min(i))
    antes = i.get(alvo) or i[min(i, key=lambda k: abs(k - alvo))]
    return agora / antes


if __name__ == "__main__":
    primeiro, ultimo = cobertura()
    print(f"série: {primeiro} .. {ultimo}  ({len(_indice())} meses)")
    for corte in ("2014-05", "2020-05", "2025-11"):
        ano = int(corte[:4])
        print(f"corte {corte}: media_ano({ano}) usa meses ate {corte}; "
              f"fator 2014 -> {ano} = {fator_entre(2014, ano, corte):.4f}")
