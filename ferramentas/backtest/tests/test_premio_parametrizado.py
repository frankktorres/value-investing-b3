"""Prova que o prêmio do Ke é parametrizável SEM editar os motores — o portão da fatia 1.

A sensibilidade de 3 a 6 p.p. que a F3 pede só é possível se o prêmio puder variar. Mas
`PREMIO_KE = 0.05` é constante de módulo (motor_financeiras.py:15), lida por `Mercado.ke_real`
(:38). A saída não é subclassar `Mercado` — `central_ao_ke` (:227) e o caminho de sensibilidade
(:348) reconstroem `Mercado(rf, pi)` por dentro e a subclasse sumiria em silêncio.

A saída é `ke_nom=`, e o teste decisivo é algébrico: trocar `PREMIO_KE` por outro valor e exigir
que o resultado seja IDÊNTICO. Se for, está provado que a constante não participa do cálculo
quando `ke_nom` é passado — mais forte do que qualquer sentinela de construção.

O teste também prova o LIMITE: `avaliar(emp, mk)`, que não recebe `ke_nom`, responde a `PREMIO_KE`.
É por isso que o backtest nunca o chama. Se um dia alguém apontar o backtest para `avaliar`, este
teste é o que explica por que não.

Importar os lote*.py AQUI é legítimo e não contradiz test_isolamento: o que está proibido é o
RUNTIME do backtest ler premissa de 2026; um teste que afirma uma propriedade do motor precisa de
uma empresa real para afirmá-la sobre.
"""
from __future__ import annotations

import pytest

from backtest.mercado_bt import MercadoBT

PREMIOS = (0.03, 0.04, 0.05, 0.06)


@pytest.fixture(scope="module")
def mk():
    """A curva de 02/10/2026 que a mesa usou no lote 1 — serve como curva qualquer."""
    return MercadoBT(data="2026-10-02", rf_real=0.0706, pi=0.0646, premio=0.05,
                     titulo_rf="Tesouro IPCA+ 2045", fonte="teste")


@pytest.fixture(scope="module")
def financeira():
    import lote1_bancos
    return lote1_bancos.EMPRESAS[0], lote1_bancos.MK


@pytest.fixture(scope="module")
def industrial():
    # Tem de ser um Industrial de verdade: lote2_energia.EMPRESAS[0] é TAEE11, que é Financeira
    # (utility holding entra pelo motor financeiro) e não tem `anos_ciclo`.
    import lote3_agro
    from motor_nao_financeiras import Industrial
    emp = lote3_agro.EMPRESAS[0]
    assert isinstance(emp, Industrial), f"{emp.ticker} não é Industrial"
    return emp, lote3_agro.MK


# ----------------------------------------------------------------- a álgebra do MercadoBT
def test_ke_nom_e_a_unica_porta_do_premio(mk: MercadoBT) -> None:
    for premio in PREMIOS:
        m = mk.com_premio(premio)
        assert m.ke_real == pytest.approx(m.rf_real + premio)
        assert m.ke_nom == pytest.approx((1 + m.rf_real + premio) * (1 + m.pi) - 1)
    kes = [mk.com_premio(p).ke_nom for p in PREMIOS]
    assert kes == sorted(kes), "Ke nominal tem de crescer com o prêmio"


def test_premio_nao_contamina_a_divida_nem_o_g_teto(mk: MercadoBT) -> None:
    """rf_nom (base do Kd) e g_teto não podem se mover com o prêmio de EQUITY."""
    base = mk.com_premio(0.03)
    for premio in PREMIOS:
        m = mk.com_premio(premio)
        assert m.rf_nom == pytest.approx(base.rf_nom)
        assert m.g_teto == pytest.approx(base.g_teto)


# -------------------------------------------- financeiras: central_ao_ke é prêmio-agnóstico
def test_central_ao_ke_responde_ao_premio(mk: MercadoBT, financeira) -> None:
    from motor_financeiras import central_ao_ke
    emp, mk_casa = financeira
    centrais = [central_ao_ke(emp, mk_casa, mk.com_premio(p).ke_nom) for p in PREMIOS]
    assert len(set(round(c, 6) for c in centrais)) == len(PREMIOS), \
        f"o central tem de mudar com o prêmio; saiu {centrais}"
    assert centrais == sorted(centrais, reverse=True), \
        f"prêmio maior => Ke maior => central MENOR; saiu {centrais}"


def test_central_ao_ke_ignora_a_constante_do_modulo(
        mk: MercadoBT, financeira, monkeypatch: pytest.MonkeyPatch) -> None:
    """A prova: trocar PREMIO_KE não pode mudar nada quando ke_nom é passado."""
    import motor_financeiras
    emp, mk_casa = financeira
    ke = mk.com_premio(0.04).ke_nom
    antes = motor_financeiras.central_ao_ke(emp, mk_casa, ke)
    for falso in (0.0, 0.01, 0.13, 0.5):
        monkeypatch.setattr(motor_financeiras, "PREMIO_KE", falso)
        depois = motor_financeiras.central_ao_ke(emp, mk_casa, ke)
        assert depois == pytest.approx(antes, rel=1e-12), (
            f"PREMIO_KE={falso} mudou o central de {antes} para {depois}: o prêmio NÃO se cancela, "
            "e a sensibilidade de 3-6 p.p. estaria medindo a constante do módulo")


# ------------------------------------- não-financeiras: valores(..., ke_nom=) é prêmio-agnóstico
def test_valores_responde_ao_premio(mk: MercadoBT, industrial) -> None:
    from motor_nao_financeiras import central_de, valores
    emp, mk_casa = industrial
    centrais = []
    for p in PREMIOS:
        anc = valores(emp, mk_casa, ke_nom=mk.com_premio(p).ke_nom)["anc"]
        centrais.append(central_de(anc)[0])
    assert len(set(round(c, 6) for c in centrais)) == len(PREMIOS), \
        f"o central tem de mudar com o prêmio; saiu {centrais}"
    assert centrais == sorted(centrais, reverse=True), \
        f"prêmio maior => central menor; saiu {centrais}"


def test_valores_ignora_a_constante_do_modulo(
        mk: MercadoBT, industrial, monkeypatch: pytest.MonkeyPatch) -> None:
    import motor_financeiras
    import motor_nao_financeiras
    emp, mk_casa = industrial
    ke = mk.com_premio(0.04).ke_nom

    def central(emp, mk_casa, ke):
        return motor_nao_financeiras.central_de(
            motor_nao_financeiras.valores(emp, mk_casa, ke_nom=ke)["anc"])[0]

    antes = central(emp, mk_casa, ke)
    for falso in (0.0, 0.01, 0.13, 0.5):
        # o motor não-financeiro lê a constante do módulo das financeiras; trocar nos dois lugares
        monkeypatch.setattr(motor_financeiras, "PREMIO_KE", falso)
        monkeypatch.setattr(motor_nao_financeiras, "PREMIO_KE", falso, raising=False)
        depois = central(emp, mk_casa, ke)
        assert depois == pytest.approx(antes, rel=1e-12), (
            f"PREMIO_KE={falso} mudou o central de {antes} para {depois}")


# --------------------------------------------------------------------------------- o limite
def test_avaliar_NAO_e_premio_agnostico_por_isso_o_backtest_nao_o_usa(financeira) -> None:
    """Documenta a fronteira: sem `ke_nom`, o prêmio volta a ser a constante do módulo."""
    import motor_financeiras
    emp, mk_casa = financeira
    antes = motor_financeiras.avaliar(emp, mk_casa)["central"]
    original = motor_financeiras.PREMIO_KE
    try:
        motor_financeiras.PREMIO_KE = 0.10
        depois = motor_financeiras.avaliar(emp, mk_casa)["central"]
    finally:
        motor_financeiras.PREMIO_KE = original
    assert depois != pytest.approx(antes), (
        "avaliar() deveria responder a PREMIO_KE. Se parou de responder, a porta do prêmio mudou "
        "e o backtest precisa ser reexaminado.")
