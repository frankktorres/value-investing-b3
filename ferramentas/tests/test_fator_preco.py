"""Margem de cíclica reexpressa ao preço de meio (Etapa 5, dossiê CMIN3): `fator_preco` e `custo_variavel_preco`.

O golden prova que os 41 não mudam (default None); estes testes provam a REGRA numa série sintética.
"""
import pytest

import motor_nao_financeiras as M
from tests.test_metodo_f2 import _serie_sintetica

ANOS = [str(a) for a in range(2019, 2026)]


def _emp(**kw):
    return M.Industrial("TESTEFP", "teste", "ciclica", preco=10.0, n_acoes=1e6, anos_ciclo=ANOS,
                        janela_razao="série sintética", **kw)


def _serie(margem=0.40):
    rec = {a: 10_000.0 for a in ANOS}
    _serie_sintetica("TESTEFP", rec, capex=500.0, extra_por_ano={a: {"ebit": margem * 10_000.0} for a in ANOS})


def test_fator_um_devolve_a_margem_original():
    _serie()
    op0 = M.premissas_operacionais(_emp())
    op1 = M.premissas_operacionais(_emp(fator_preco={a: 1.0 for a in ANOS}, custo_variavel_preco=0.1))
    assert op1["m50"] == pytest.approx(op0["m50"]) == pytest.approx(0.40)


def test_preco_do_ano_acima_do_meio_reduz_a_margem_com_custo_fixo():
    """Margem 40% a preço 2× o de meio (f = 0,5), custo fixo: receita ao meio = 0,5 → margem = 1 − 0,60/0,5 = −20%."""
    _serie()
    op = M.premissas_operacionais(_emp(fator_preco={a: 0.5 for a in ANOS}))
    assert op["m50"] == pytest.approx(-0.20)


def test_custo_variavel_acompanha_o_preco():
    """v = 10%: custo fixo = 50% da receita do ano; ao meio (f = 0,5): 1 − 0,10 − 0,50/0,5 = −10%."""
    _serie()
    op = M.premissas_operacionais(_emp(fator_preco={a: 0.5 for a in ANOS}, custo_variavel_preco=0.10))
    assert op["m50"] == pytest.approx(-0.10)


def test_custo_100pct_variavel_mantem_a_margem():
    """Se todo o custo acompanhasse o preço (v = 1 − margem), o preço não mudaria a margem."""
    _serie()
    op = M.premissas_operacionais(_emp(fator_preco={a: 0.7 for a in ANOS}, custo_variavel_preco=0.60))
    assert op["m50"] == pytest.approx(0.40)


def test_ano_sem_fator_falha_alto():
    _serie()
    f = {a: 1.0 for a in ANOS[:-1]}
    with pytest.raises(ValueError, match="fator_preco"):
        M.premissas_operacionais(_emp(fator_preco=f))
    for ruim in (0.0, -1.0, float("nan"), float("inf"), None):
        with pytest.raises(ValueError, match="fator_preco"):
            M.premissas_operacionais(_emp(fator_preco={**f, ANOS[-1]: ruim}))


def test_custo_variavel_fora_do_intervalo_falha():
    _serie()
    with pytest.raises(ValueError, match="custo_variavel_preco"):
        M.premissas_operacionais(_emp(fator_preco={a: 1.0 for a in ANOS}, custo_variavel_preco=1.0))


def test_nao_combina_com_e_p_nem_deflator():
    _serie()
    with pytest.raises(ValueError, match="não combina"):
        M.premissas_operacionais(_emp(fator_preco={a: 1.0 for a in ANOS}, da_receita=0.1))


def test_nenhum_ticker_do_hall_usa_o_campo():
    """O campo é opcional: os lotes do hall seguem sem ele (o golden confirma os números)."""
    assert M.Industrial("X", "x", "ciclica", preco=1.0, n_acoes=1.0).fator_preco is None
