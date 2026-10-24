"""O4b: testes para os mutantes que sobreviveram no motor das financeiras (docs/oraculo/mutacao-2026-10-23.md, itens 1–8).

As âncoras são fixadas por `mock` para montar exatamente a borda de cada regra do §11.3/AUD-11; o resto do motor roda inteiro.
Nenhum código de motor muda; só prova o que o motor já faz.
"""
from dataclasses import replace
from unittest import mock

import pytest

import mercado
import motor_financeiras as F
from oraculo import sanidade as S

MK = mercado.vigente()


@pytest.fixture(scope="module")
def banco():
    e = next(e for e in S.empresas().values()
             if isinstance(e, F.Financeira) and not e.horizonte_finito and e.sotp is None and e.roe_lp > 0
             and e.desconto_controlador["tipo"] == "zero" and not e.fora_circulo)
    return e


def _av(emp, anc, preco_fator=0.5):
    """Avalia com as âncoras dadas; o preço fica a `preco_fator` × a mediana (0,5 → régua BARATA)."""
    from statistics import median
    central = median(anc.values())
    emp = replace(emp, preco=preco_fator * central if central > 0 else emp.preco)
    with mock.patch.object(F, "ancoras", lambda *a, **k: dict(anc)):
        return F.avaliar(emp, MK)


def test_dispersao_acima_de_3_sozinha_da_nao_conclusivo(banco):          # item 1 (`or` → `and`) e item 2 (`> 4`)
    r = _av(banco, {"a": 10.0, "b": 35.0})
    assert r["dispersao"] == pytest.approx(3.5) and r["palavra"] == "NÃO CONCLUSIVO"


def test_dispersao_exatamente_3_nao_e_nao_conclusivo(banco):              # item 2 (`> 3` → `>= 3`)
    r = _av(banco, {"a": 10.0, "b": 30.0})
    assert r["palavra"] != "NÃO CONCLUSIVO" and r["confianca"] == "baixa"


def test_dispersao_exatamente_1_8_nao_desce_a_palavra(banco):              # item 3 (`> 1.8` → `>= 1.8`)
    r = _av(banco, {"a": 10.0, "b": 18.0})
    assert r["palavra"] == "BARATA" and r["confianca"] == "normal"
    r = _av(banco, {"a": 10.0, "b": 18.5})
    assert r["palavra"] == "RADAR" and r["confianca"] == "baixa"


def test_lpa_normalizado_nao_positivo_sozinho_da_nao_conclusivo(banco):   # item 5 (`or` → `and`; `<=` → `<`)
    for roe in (-0.05, 0.0):
        r = _av(replace(banco, roe_lp=roe), {"a": 10.0, "b": 11.0})
        assert r["central"] > 0 and r["palavra"] == "NÃO CONCLUSIVO", roe


def test_ancora_exatamente_zero_da_nao_conclusivo(banco):                  # item 6 (`v <= 0` → `v < 0`)
    r = _av(banco, {"a": 0.0, "b": 10.0, "c": 12.0})
    assert r["central"] > 0 and r["palavra"] == "NÃO CONCLUSIVO"


def test_desconto_zero_reporta_zero(banco):                                # item 7
    assert _av(banco, {"a": 10.0, "b": 11.0})["desc_controlador"] == 0.0


def test_desconto_por_cenarios_reporta_a_perda_ponderada(banco):           # item 8
    base, inter = {"a": 10.0, "b": 12.0}, {"a": 8.0, "b": 9.0}
    emp = replace(banco, desconto_controlador={"tipo": "cenarios", "delta_roe": 0.02, "peso": 0.25, "razao": "teste"})
    # ROE de longo prazo → base; ROE − delta → cenário de interferência (as outras chamadas, de sensibilidade, levam o mesmo par)
    with mock.patch.object(F, "ancoras", lambda e, mk, roe: dict(base if roe >= e.roe_lp - 1e-12 else inter)):
        r = F.avaliar(replace(emp, preco=5.0), MK)
    esperado = 1 - (0.75 * 22 + 0.25 * 17) / 22
    assert r["desc_controlador"] == pytest.approx(esperado)
