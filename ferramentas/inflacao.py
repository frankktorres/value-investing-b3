"""Índice de inflação da casa (IPCA) — fonte única para deflacionar receita e corrigir imobilizado.

Série: dados/macro/ipca_mensal.json (BCB, SGS 433, variação mensal em %, desde 01/1980 — fonte nota A,
coletada por coletar_macro.py). Convenção da casa, igual à que o Lote 5 já usava: o índice de um exercício é a
MÉDIA dos índices mensais do ano, porque receita e capex se acumulam ao longo do ano, não no fechamento.

Usos (doutrina §11.1):
  · DEFLATOR[ano] → fator que leva R$ daquele exercício a R$ da data-base (último mês da série).
  · fator_entre(de, para) → leva R$ do exercício `de` a R$ do exercício `para` (usado no Δreceita real).
  · reposicao(imobilizado, da) → (idade média, fator) para o imobilizado a custo de reposição aproximado.
"""
from __future__ import annotations

import json
import pathlib

AQUI = pathlib.Path(__file__).parent
_SERIE = json.loads((AQUI / "dados" / "macro" / "ipca_mensal.json").read_text(encoding="utf-8"))

# idade média do imobilizado: limites da doutrina, não da série (a série cobre 46 anos)
IDADE_MIN, IDADE_MAX = 1.0, 15.0


def _mes(data: str) -> int:
    """'01/08/2026' → 24320 (meses desde o ano 0), para aritmética de prazo sem dependência de calendário."""
    _, mm, aa = data.split("/")
    return int(aa) * 12 + int(mm) - 1


_INDICE: dict[int, float] = {}
_acc = 1.0
for _reg in _SERIE:
    _acc *= 1 + float(_reg["valor"]) / 100
    _INDICE[_mes(_reg["data"])] = _acc

PRIMEIRO_MES, BASE_MES = min(_INDICE), max(_INDICE)
BASE = _INDICE[BASE_MES]
DATA_BASE = f"{BASE_MES % 12 + 1:02d}/{BASE_MES // 12}"
COBERTURA_ANOS = (BASE_MES - PRIMEIRO_MES) / 12

_ANOS = sorted({m // 12 for m in _INDICE})
MEDIA_ANO = {a: sum(v for m, v in _INDICE.items() if m // 12 == a) / sum(1 for m in _INDICE if m // 12 == a)
             for a in _ANOS}
DEFLATOR = {str(a): BASE / MEDIA_ANO[a] for a in _ANOS}


def _indice_ano(ano: str | int) -> float:
    """Índice médio do exercício. Ano fora da série (antes de 1980 ou depois do último mês) usa o extremo mais
    próximo, em vez de derrubar o motor — a série é coletada por coletar_macro.py e pode ficar atrás do exercício."""
    a = int(ano)
    return MEDIA_ANO[min(max(a, _ANOS[0]), _ANOS[-1])]


def fator_entre(de: str | int, para: str | int) -> float:
    """Fator que expressa R$ do exercício `de` em R$ do exercício `para` (> 1 quando `para` é posterior)."""
    return _indice_ano(para) / _indice_ano(de)


def inflacao_do_ano(ano: str | int) -> float:
    """Inflação do exercício (índice médio do ano ÷ índice médio do anterior − 1). Serve para pôr o ROIC de um
    exercício antigo em termos reais e compará-lo com o WACC real (doutrina §4: real com real).

    Ano fora da série usa o último exercício medido (não zero: inflação zero trataria nominal como real).
    O ano corrente tem média parcial (os meses já publicados), e exercício social deslocado (SMTO3, abr–mar) é
    aproximado pelo ano-calendário de fechamento — aproximação declarada.
    """
    a = min(max(int(ano), _ANOS[0] + 1), _ANOS[-1])
    return MEDIA_ANO[a] / MEDIA_ANO[a - 1] - 1


def indice_ha(anos: float) -> float:
    """Índice de `anos` antes da data-base (meses arredondados); antes do início da série, o primeiro índice."""
    return _INDICE.get(max(BASE_MES - round(anos * 12), PRIMEIRO_MES), _INDICE[PRIMEIRO_MES])


def idade_media(imobilizado: float, da: float) -> float:
    """Idade média do imobilizado ≈ imobilizado líquido ÷ D&A anual.

    Sob depreciação linear e safras uniformes, líquido ÷ bruto = ½ e D&A = bruto ÷ vida útil, logo
    líquido ÷ D&A = vida útil ÷ 2 = idade média. Aproximação declarada: a D&A da DFC inclui amortização de
    intangível e do direito de uso, o que SUBESTIMA a idade — a correção sai conservadora. Limitada a
    [IDADE_MIN, IDADE_MAX] anos.
    """
    if not da or da <= 0 or imobilizado <= 0:
        return IDADE_MIN
    return min(max(imobilizado / da, IDADE_MIN), IDADE_MAX)


def reposicao(imobilizado: float, da: float) -> tuple[float, float]:
    """(idade média, fator de correção do imobilizado a R$ da data-base pelo IPCA da idade média)."""
    idade = idade_media(imobilizado, da)
    return idade, BASE / indice_ha(idade)


def fator_idade(ano: str | int, idade: float) -> float:
    """Fator que corrige um imobilizado de `idade` anos para os preços MÉDIOS do exercício `ano`.

    Serve à série histórica de ROIC a reposição (§9): cada exercício é medido com os preços do próprio exercício,
    não com os de hoje. Referência: meio do ano (os valores do exercício se acumulam ao longo dele).
    """
    ref = min(int(ano) * 12 + 6, BASE_MES)
    agora = _INDICE[ref] if ref in _INDICE else _INDICE[BASE_MES]
    antes = _INDICE.get(max(ref - round(idade * 12), PRIMEIRO_MES), _INDICE[PRIMEIRO_MES])
    return agora / antes
