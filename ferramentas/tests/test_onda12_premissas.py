"""Onda 1.2 da auditoria de 08/10/2026, bloco 2 — premissas do custo de capital (AUD-07, AUD-09, AUD-18).

Escritos antes da correção; no código antigo falhavam: `credito` não existia, `spread_kd` tinha padrão 0,02 sem fonte,
`aliquota` explícita passava sem fonte e com 2 exercícios, e o motor não expunha a reprodução a reposição.
"""
import pytest

import credito
import motor_nao_financeiras as M
from lote1_bancos import MK
from tests.test_doutrina_v23 import _emp, _serie


# ---------------------------------------------------------------- AUD-07: Kd com fonte
def test_aud07_tabela_de_spread_nos_limites():
    assert credito.spread_sintetico(0.1) == (0.19, "D")
    assert credito.spread_sintetico(2.99) == (0.0111, "BBB")
    assert credito.spread_sintetico(3.0) == (0.0089, "A-")          # o limite pertence à faixa de cima
    assert credito.spread_sintetico(8.5) == (0.0040, "AAA")
    assert credito.spread_sintetico(None) == (0.0040, "AAA")         # sem juros pagos
    spreads = [s for _, _, s in credito.TABELA]
    assert spreads == sorted(spreads, reverse=True)                  # mais cobertura, menos spread


def test_aud07_kd_padrao_e_rf_mais_spread_sintetico_pela_cobertura_normalizada():
    _serie("TESTE12KD", juros_pagos=500.0)                           # lucro operacional ~1.500 (R$ de hoje) → cobertura ~3
    r = M.valores(_emp("TESTE12KD"), MK)
    info = r["kd_info"]
    assert info["origem"] == "sintético" and info["rating"] == "A-"
    assert 3.0 <= info["cobertura"] < 4.25
    assert r["kd"] == pytest.approx(MK.rf_nom + 0.0089)


def test_aud07_kd_do_ri_vence_o_sintetico():
    _serie("TESTE12KD2", juros_pagos=500.0)
    emp = _emp("TESTE12KD2", kd_ri=dict(valor=0.13, fonte="RI 2T26, custo médio pós-swap", data="2026-06-30"))
    r = M.avaliar(emp, MK)
    assert r["kd"] == 0.13 and r["kd_info"]["origem"] == "RI"


def test_aud07_spread_digitado_sem_fonte_nao_roda():
    _serie("TESTE12KD3")
    with pytest.raises(ValueError, match="spread_fonte"):
        M.avaliar(_emp("TESTE12KD3", spread_kd=0.02), MK)
    with pytest.raises(ValueError, match="kd_ri"):
        M.avaliar(_emp("TESTE12KD3", kd_ri=dict(valor=0.13)), MK)


def test_aud07_nenhum_spread_digitado_no_hall():
    import universo
    for _, empresas, _ in universo.GRUPOS:
        for e in empresas:
            if isinstance(e, M.Industrial):
                assert e.spread_kd is None or e.spread_fonte.strip(), e.ticker


# ---------------------------------------------------------------- AUD-09: alíquota explícita não contorna a regra
def test_aud09_explicita_abaixo_de_34_sem_fonte_nao_roda():
    _serie("TESTE12AL")
    with pytest.raises(ValueError, match="aliquota_fonte"):
        M.avaliar(_emp("TESTE12AL", aliquota=0.20), MK)
    M.avaliar(_emp("TESTE12AL", aliquota=0.34), MK)                  # 34% é o padrão conservador: não exige fonte


def test_aud09_mudanca_de_lei_com_dois_exercicios_da_34():
    _serie("TESTE12AL2", ir=-200.0)                                  # 13,3% em todos os anos
    emp = _emp("TESTE12AL2", aliquota_desde=dict(ano=2024, fonte="lei"), aliquota_permanente_fonte="JCP")
    assert M.aliquota_regra(emp) == (M.ALIQUOTA_MARGINAL, "sem_dado")
    emp3 = _emp("TESTE12AL2", aliquota_desde=dict(ano=2023, fonte="lei"), aliquota_permanente_fonte="JCP")
    assert M.aliquota_regra(emp3) == (pytest.approx(200 / 1500), "permanente")


def test_aud09_abev3_segue_a_regra():
    import lote4_saude_telecom as L4
    abev = next(e for e in L4.EMPRESAS if e.ticker == "ABEV3")
    assert abev.aliquota is None and abev.aliquota_desde["ano"] == 2024
    assert M.aliquota_regra(abev) == (M.ALIQUOTA_MARGINAL, "sem_dado")


# ---------------------------------------------------------------- AUD-18: reprodução declarada
def test_aud18_ancora_no_contabil_e_reposicao_exibida_maior_ou_igual():
    _serie("TESTE12RP")
    r = M.valores(_emp("TESTE12RP", perfil="ciclica"), MK)
    assert r["anc"]["Valor de reprodução"] == pytest.approx(r["reprod"])
    assert r["reprod"] == pytest.approx(6_000.0 / 1_000.0)          # PL ÷ ações (R$ mil ÷ mil ações)
    assert r["reprod_reposicao"] >= r["reprod"]


def test_aud07_divida_sem_juros_no_periodo_falha_alto():
    """Adversário (08/10): sem a linha de juros, a cobertura virava None e o spread, AAA, em silêncio."""
    _serie("TESTE12KD4", juros_pagos=0.0)
    with pytest.raises(ValueError, match="sem juros"):
        M.avaliar(_emp("TESTE12KD4"), MK)
    _serie("TESTE12KD5", juros_pagos=0.0, emprest_lp=0.0)          # sem dívida: AAA é correto
    assert M.valores(_emp("TESTE12KD5"), MK)["kd_info"]["rating"] == "AAA"
