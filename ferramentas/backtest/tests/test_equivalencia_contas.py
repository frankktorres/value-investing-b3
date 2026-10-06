"""Prova que a cópia em backtest/motor/contas.py é a mesma fórmula do motor da mesa.

A cópia existe para o runtime do backtest não carregar `cvm_series.json` (1 MB da coleta de
out/2026, chave de período `ltm_2T26`) só por importar o motor. O preço da cópia é o risco de as
duas pontas divergirem em silêncio; este teste é o pagamento.

Duas populações:
  · ALEATÓRIA — milhares de dicts com números extremos, zeros, negativos e chaves ausentes, para
    pegar divergência de borda (tratamento de None, divisão por zero, ordem de operações);
  · REAL — todos os exercícios de todos os tickers de `cvm_series.json`, que é o dado que o motor
    de hoje de fato consome.

Ler `cvm_series.json` AQUI é legítimo: o que test_isolamento proíbe é o RUNTIME do backtest tocá-lo.
Um teste que afirma equivalência com o motor da mesa precisa do dado da mesa para afirmá-la sobre.
"""
from __future__ import annotations

import json
import math
import pathlib
import random

import pytest

import motor_nao_financeiras as mesa
from backtest.motor import contas

SERIE = pathlib.Path(__file__).resolve().parent.parent.parent / "dados" / "cvm_series.json"

# Chaves que as oito funções leem, direta ou indiretamente.
CHAVES = ("ativo", "ac", "pc", "pnc", "pl", "receita", "lucro", "lucro_bruto", "ebit", "fco",
          "caixa", "aplic_cp", "receber", "estoques", "imobilizado", "intangivel", "da",
          "emprest_cp", "emprest_lp", "arrendamento", "reservas_lucro", "desp_vendas", "desp_ga",
          "outras_receitas_op", "outras_despesas_op", "impairment", "impairment_outras", "acoes")

UM = (contas.divida_liquida, contas.capital_giro, contas.altman_z2)
DOIS = (contas.piotroski, contas.beneish, contas.sloan)


def _igual(a, b) -> bool:
    """Igualdade estrita, tratando NaN como igual a NaN e comparando tuplas/listas elemento a elemento."""
    if isinstance(a, float) and isinstance(b, float):
        return (math.isnan(a) and math.isnan(b)) or a == b
    if isinstance(a, (tuple, list)) and isinstance(b, (tuple, list)):
        return len(a) == len(b) and all(_igual(x, y) for x, y in zip(a, b))
    return a == b


def _chamar(f, *args):
    """Chama e devolve ('ok', valor) ou ('erro', nome da exceção) — a exceção também é contrato."""
    try:
        return "ok", f(*args)
    except Exception as e:                                   # noqa: BLE001 — o tipo do erro é o que se compara
        return "erro", type(e).__name__


def _dict_aleatorio(rnd: random.Random) -> dict:
    d = {}
    for k in CHAVES:
        sorte = rnd.random()
        if sorte < 0.12:
            continue                                          # chave ausente
        elif sorte < 0.20:
            d[k] = None                                       # linha vazia da CVM
        elif sorte < 0.28:
            d[k] = 0
        elif sorte < 0.34:
            d[k] = rnd.choice([1e-9, -1e-9, 1e12, -1e12])     # extremos
        else:
            d[k] = rnd.uniform(-5e7, 5e8)
    return d


@pytest.fixture(scope="module")
def aleatorios() -> list[dict]:
    rnd = random.Random(20261006)
    return [_dict_aleatorio(rnd) for _ in range(4000)]


@pytest.fixture(scope="module")
def reais() -> list[dict]:
    dados = json.loads(SERIE.read_text(encoding="utf-8"))
    saida = []
    for tk, bloco in dados.items():
        for periodo, d in bloco.items():
            if periodo == "anual":
                saida.extend(d.values())
            elif isinstance(d, dict):
                saida.append(d)
    assert len(saida) > 200, f"esperava centenas de exercícios reais, veio {len(saida)}"
    return saida


# -------------------------------------------------------------------- as oito, de um argumento
@pytest.mark.parametrize("nome", [f.__name__ for f in UM])
def test_um_argumento_equivale(nome: str, aleatorios: list[dict], reais: list[dict]) -> None:
    minha, dela = getattr(contas, nome), getattr(mesa, nome)
    for d in aleatorios + reais:
        assert _igual(_chamar(minha, d), _chamar(dela, d)), f"{nome} divergiu em {d}"


@pytest.mark.parametrize("nome", [f.__name__ for f in DOIS])
def test_dois_argumentos_equivale(nome: str, aleatorios: list[dict], reais: list[dict]) -> None:
    minha, dela = getattr(contas, nome), getattr(mesa, nome)
    pares = list(zip(aleatorios, aleatorios[1:])) + list(zip(reais, reais[1:]))
    for d, p in pares:
        assert _igual(_chamar(minha, d, p), _chamar(dela, d, p)), f"{nome} divergiu em {d} / {p}"


@pytest.mark.parametrize("liquidas", [False, True])
def test_outras_equivale(liquidas: bool, aleatorios: list[dict], reais: list[dict]) -> None:
    for d in aleatorios + reais:
        assert _igual(_chamar(contas.outras, d, liquidas),
                      _chamar(mesa.outras, d, liquidas)), f"outras divergiu em {d}"


@pytest.mark.parametrize("liquidas", [False, True])
@pytest.mark.parametrize("med", [None, 0.0, 0.015, 0.5])
def test_ebit_aj_equivale(med, liquidas: bool, aleatorios: list[dict], reais: list[dict]) -> None:
    for d in aleatorios + reais:
        assert _igual(_chamar(contas.ebit_aj, d, med, liquidas),
                      _chamar(mesa.ebit_aj, d, med, liquidas)), f"ebit_aj divergiu em {d}"


def test_helper_v_equivale_nos_usos_reais(aleatorios: list[dict]) -> None:
    """A cópia tipou `default` como numérico; isto confere que nenhum uso real muda de resultado."""
    for d in aleatorios:
        for k in CHAVES:
            for default in (0, 0.0, 1.0, -3.5):
                assert _igual(contas.v(d, k, default), mesa.v(d, k, default))


def test_a_copia_cobre_exatamente_as_funcoes_puras_declaradas() -> None:
    """Se alguém acrescentar uma função a contas.py sem pôr em PURAS, o teste de cima não a cobre."""
    publicas = {n for n in dir(contas)
                if callable(getattr(contas, n)) and not n.startswith("_") and n != "v"}
    assert publicas == {f.__name__ for f in contas.PURAS}, \
        f"função pública fora de PURAS (logo, sem teste de equivalência): {publicas ^ {f.__name__ for f in contas.PURAS}}"
