"""N2 (check-up 21/10/2026): regras do motor que nenhum teste cobria. Só testes; o código do motor não muda."""
import dataclasses

import pytest

import motor_financeiras as F
import motor_nao_financeiras as M
from tests.test_metodo_f2 import _emp as _industrial
from tests.test_onda3_motor import MK as MK_FIN
from tests.test_onda3_motor import _emp as _financeira


# ---------------------------------------------------------------- desconto de controlador por cenários (§5)
def test_desconto_por_cenarios_e_soma_prob_vezes_perda():
    emp = _industrial("TN2A", desconto_controlador={
        "tipo": "cenarios", "razao": "teste",
        "cenarios": [{"prob": 0.5, "perda": 0.10}, {"prob": 0.3, "perda": 0.30}, {"prob": 0.2, "perda": 0.0}]})
    assert M.desconto_pct(emp) == pytest.approx(0.5 * 0.10 + 0.3 * 0.30 + 0.2 * 0.0)


def test_desconto_fixo_e_zero():
    assert M.desconto_pct(_industrial("TN2B", desconto_controlador={"tipo": "fixo", "pct": 0.15, "razao": "t"})) == 0.15
    assert M.desconto_pct(_industrial("TN2C", desconto_controlador={"tipo": "zero", "razao": "t"})) == 0.0


def test_desconto_so_incide_em_ancora_positiva():
    out = F.descontar({"a": 100.0, "b": -20.0, "c": 0.0}, 0.25)
    assert out == {"a": 75.0, "b": -20.0, "c": 0.0}      # ≤ 0 fica como está: continua forçando NÃO CONCLUSIVO


def test_desconto_por_cenarios_reduz_o_central_na_mediana():
    desc = 0.5 * 0.10 + 0.3 * 0.30
    anc = {"dcf": 10.0, "epv": 12.0, "oe": 14.0}
    assert M.central_de(F.descontar(anc, desc))[0] == pytest.approx(12.0 * (1 - desc))


# ---------------------------------------------------------------- escala da nota de Preço (cada degrau)
@pytest.mark.parametrize("pc,nota", F.ESCALA_PRECO)
def test_nota_preco_nos_degraus(pc, nota):
    assert F.nota_preco(pc) == pytest.approx(nota)


@pytest.mark.parametrize("pc,nota", [(0.1, 10), (0.60, 10), (1.50, 0), (3.0, 0), (float("inf"), 0)])
def test_nota_preco_satura_nas_pontas(pc, nota):
    assert F.nota_preco(pc) == nota


def test_nota_preco_interpola_entre_degraus_e_nunca_sobe_com_o_preco():
    pontos = F.ESCALA_PRECO
    for (x0, y0), (x1, y1) in zip(pontos, pontos[1:]):
        assert F.nota_preco((x0 + x1) / 2) == pytest.approx((y0 + y1) / 2)
    grade = [0.5 + i / 100 for i in range(120)]
    notas = [F.nota_preco(x) for x in grade]
    assert all(a >= b for a, b in zip(notas, notas[1:]))


# ---------------------------------------------------------------- saída a 1,50× nunca em financeira (§9)
def test_financeira_sai_sempre_a_1_30_nunca_a_1_50():
    r = F.avaliar(_financeira(), MK_FIN)
    assert r["central"] > 0
    assert r["saida_por_qualidade"] is False
    assert r["saida"] == pytest.approx(F.SAIDA_PADRAO * r["central"])
    assert r["saida"] != pytest.approx(F.SAIDA_QUALIDADE * r["central"])


def test_financeira_de_qualidade_altissima_continua_1_30():
    r = F.avaliar(_financeira(roe_lp=0.40, roe_inicio=0.40, payout=0.5), MK_FIN)
    assert r["saida_por_qualidade"] is False and r["saida"] == pytest.approx(1.30 * r["central"])


# ---------------------------------------------------------------- DCF reverso: ida e volta preço → g → preço
@pytest.mark.parametrize("tk", ["SUZB3", "KEPL3", "PETR4"])      # PETR4 tem desconto de controlador por cenários
def test_g_implicito_ida_e_volta(tk):
    import universo
    emp = next(e for _, emps, _ in universo.GRUPOS for e in emps if e.ticker == tk)
    mk = universo.MK
    g = M.g_implicito(emp, mk)
    assert g is not None and -0.05 <= g < 0.08
    volta = dataclasses.replace(emp, g_real=g)
    dcf = M.valores(volta, mk)["dcf"]["base"]
    assert M.descontar({"b": dcf}, M.desconto_pct(emp))["b"] == pytest.approx(emp.preco, rel=1e-6)


def test_g_implicito_cresce_com_o_preco():
    import universo
    emp = next(e for _, emps, _ in universo.GRUPOS for e in emps if e.ticker == "KEPL3")
    mais_caro = dataclasses.replace(emp, preco=emp.preco * 1.01)
    assert M.g_implicito(mais_caro, universo.MK) > M.g_implicito(emp, universo.MK)


def test_g_implicito_none_quando_nem_o_teto_de_g_paga_o_preco():
    import universo
    emp = next(e for _, emps, _ in universo.GRUPOS for e in emps if e.ticker == "KEPL3")
    assert M.g_implicito(dataclasses.replace(emp, preco=emp.preco * 100), universo.MK) is None
