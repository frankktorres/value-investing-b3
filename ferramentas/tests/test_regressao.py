"""Regressão: central, P/C, palavra, âncoras e métricas de renda/solidez dos 41 tickers contra tests/golden.json.

Falha quando algo muda além da tolerância (golden.TOL; R$ 0,01 em valores por ação). Mudança intencional:
python -m tests.regerar_golden --motivo "..."
"""
import pytest

import golden
import universo

GOLD = golden.carregar()


@pytest.fixture(scope="session")
def atual():
    return universo.instantaneo_todos()


def test_universo_completo(atual):
    assert sorted(atual) == sorted(GOLD), "tickers avaliados ≠ tickers do golden"
    assert len(GOLD) == 41


@pytest.mark.parametrize("ticker", sorted(GOLD))
def test_ticker_igual_ao_golden(atual, ticker):
    mud = golden.comparar({ticker: GOLD[ticker]}, {ticker: atual[ticker]})
    assert not mud, "mudou sem regravar o golden:\n" + golden.formatar(mud)


def test_hall_ancoras_consistentes(atual):
    """Sanidade independente do golden: central = mediana das âncoras e P/C = preço/central coerentes com a palavra."""
    from statistics import median
    for tk, s in atual.items():
        if s["palavra"] == "NÃO CONCLUSIVO":
            continue
        assert s["central"] == pytest.approx(median(s["ancoras"].values()), abs=1e-4), tk
