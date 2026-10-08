"""Onda 1.2 da auditoria de 08/10/2026, bloco 3 — decisões do Frank de 08/10 (AUD-12 e AUD-13).

AUD-12: Ke sobe com a dívida (Hamada 1972): os 5 p.p. são o risco do negócio sem dívida.
AUD-13: pesos do WACC no ponto fixo (valor da casa), então o central não muda quando só o preço muda.
Escritos antes da mudança; no código antigo falhavam (sem `premio_alavancado`/`estrutura_de_capital`, e o central variava
com o preço).
"""
import pytest

import motor_nao_financeiras as M
from lote1_bancos import MK
from tests.test_doutrina_v23 import _emp, _serie


def test_aud12_sem_divida_o_premio_e_o_da_casa_e_cresce_com_a_divida():
    assert M.premio_alavancado(0.0, 1_000.0, 0.34) == pytest.approx(0.05)
    assert M.premio_alavancado(1_000.0, 1_000.0, 0.34) == pytest.approx(0.05 * 1.66)
    assert M.premio_alavancado(2_000.0, 1_000.0, 0.34) > M.premio_alavancado(1_000.0, 1_000.0, 0.34)
    assert MK.premio == 0.05 and MK.ke_real == pytest.approx(MK.rf_real + 0.05)    # financeira e mercado: 5 p.p. fixos


def test_aud13_central_nao_muda_quando_so_o_preco_muda():
    _serie("TESTE12PF", emprest_lp=4_000.0)
    centrais = [M.avaliar(_emp("TESTE12PF", preco=p), MK)["central"] for p in (5.0, 10.0, 20.0)]
    assert centrais[0] == pytest.approx(centrais[1], rel=1e-4) == pytest.approx(centrais[2], rel=1e-4)


def test_aud12_13_ke_da_empresa_e_o_do_ponto_fixo():
    _serie("TESTE12PF2", emprest_lp=4_000.0)
    r = M.avaliar(_emp("TESTE12PF2"), MK)
    assert r["ponto_fixo"]
    assert r["e_peso"] == pytest.approx(r["central"] * 1_000.0, rel=1e-4)          # E = central × mil ações (R$ mil)
    assert r["premio_ke"] == pytest.approx(M.premio_alavancado(r["d"], r["e_peso"], r["aliquota"]), rel=1e-9)
    assert r["ke_real_emp"] > MK.ke_real                                          # com dívida, Ke acima da régua sem dívida
    assert r["e"] == pytest.approx(10.0 * 1_000.0)                                 # o EV/porte continua a preço de mercado


def test_aud13_sem_central_positivo_nao_ha_ponto_fixo_e_a_palavra_e_nao_conclusiva():
    _serie("TESTE12PF3", emprest_lp=60_000.0)
    r = M.avaliar(_emp("TESTE12PF3"), MK)
    assert not r["ponto_fixo"] and r["palavra"] == "NÃO CONCLUSIVO"
    assert r["e_peso"] == pytest.approx(6_000.0)      # patrimônio contábil (independe do preço), só para exibir


def test_aud12_hall_nao_financeiro_usa_o_ke_proprio():
    import universo
    for tk, it in universo.avaliar_todos().items():
        r = it["r"]
        if isinstance(it["empresa"], M.Industrial):
            assert r["premio_ke"] >= 0.05 - 1e-12, tk
            assert r["premio_ke"] == pytest.approx(M.premio_alavancado(r["d"], r["e_peso"], r["aliquota"]), rel=1e-9), tk


def test_aud13_klbn11_mesmo_central_a_qualquer_preco():
    """Adversário (08/10): partindo do preço, a KLBN11 desistia (central ≤ 0) ou achava raiz conforme o preço."""
    import dataclasses
    import lote3_agro
    k = next(e for e in lote3_agro.EMPRESAS if e.ticker == "KLBN11")
    centrais = {p: M.avaliar(dataclasses.replace(k, preco=p), MK)["central"] for p in (5.0, 18.62, 40.0)}
    assert max(centrais.values()) - min(centrais.values()) < 1e-6, centrais
