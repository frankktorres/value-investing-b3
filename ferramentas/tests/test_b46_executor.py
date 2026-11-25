"""B46: os dois consertos do executor apontados pelo `adversario` (25/11), com empresa falsa e esperado à mão."""
from __future__ import annotations

from dataclasses import dataclass

import pytest

import motor_nao_financeiras as M
from b46 import rodar as R


@dataclass
class Falsa:
    ticker: str = "FALS3"
    preco: float = 10.0
    outros_passivos_financeiros: float = 50.0


def test_choque_de_divida_multiplica_o_d_inteiro():
    # D do motor = (empréstimos CP 100 + LP 200 + arrendamento 30) + outros passivos financeiros 50 = 380;
    # dívida +10% → 418 (= 380 × 1,1), caixa 40 fixo
    b = {"emprest_cp": 100.0, "emprest_lp": 200.0, "arrendamento": 30.0, "caixa": 40.0, "aplic_cp": 0.0}
    emp = Falsa()
    assert M.divida_do_desconto(emp, b) == pytest.approx(380.0)
    with R._choque_divida(1.1):
        d = M.divida_do_desconto(R.emp_chocada(emp, dict(preco=1.0, divida=1.1)), b)
        assert M.divida_liquida(b)[1] == pytest.approx(40.0)
    assert d == pytest.approx(418.0)
    assert M.divida_do_desconto(emp, b) == pytest.approx(380.0)          # o patch não vaza para fora do `with`


def test_choque_de_preco_so_mexe_no_preco():
    e = R.emp_chocada(Falsa(), dict(preco=0.7, divida=1.0))
    assert (e.preco, e.outros_passivos_financeiros) == (pytest.approx(7.0), pytest.approx(50.0))


def test_sem_rating_i_vale_so_o_pi_ii():
    # Z'' 4,0 → B- (slide 26, mediana 2013 3,74) → 42,12% (Tabela 5)
    pi_i, r_ii, pi_ii, pi = R.pi_das_estimativas(None, 4.0)
    assert (pi_i, r_ii) == (None, "B-") and pi == pytest.approx(0.4212) and pi_ii == pytest.approx(0.4212)


def test_sem_z_vale_so_o_pi_i_e_com_as_duas_a_media():
    assert R.pi_das_estimativas("CC", None)[3] == pytest.approx(0.666)
    assert R.pi_das_estimativas("CC", 4.0)[3] == pytest.approx((0.666 + 0.4212) / 2)
    assert R.pi_das_estimativas(None, None)[3] is None
