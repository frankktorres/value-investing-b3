"""H2 (B34) — D/E a mercado, sem ponto fixo; decisão do Frank em 24/11/2026 (pré-registro, emenda 3; `09`).

Coerência obrigatória: a dívida do desconto (prêmio de Hamada e pesos do WACC) é a MESMA que a ponte do valor da firma para o
valor por ação subtrai — dívida bruta com arrendamentos + outros passivos financeiros; a ponte soma o caixa; o fluxo não desconta
o arrendamento uma segunda vez. Escritos contra a regra; no código de 23/11 (ponto fixo, D = só a bruta) o de coerência falha.
Sintéticos: rodam sem os ZIPs da CVM.
"""
import dataclasses

import pytest

import motor_nao_financeiras as M
from lote1_bancos import MK
from tests.test_doutrina_v23 import _emp, _serie

BRUTA_LP, ARREND, CAIXA, OPF = 2_000.0, 800.0, 500.0, 300.0     # R$ mil


def _caso(tk, **kw):
    _serie(tk, emprest_lp=BRUTA_LP, arrendamento=ARREND, caixa=CAIXA)
    return _emp(tk, outros_passivos_financeiros=kw.pop("opf", OPF), outros_passivos_fonte="teste sintético", **kw)


# ---------------------------------------------------------------- coerência desconto × ponte
def test_divida_do_desconto_e_a_mesma_da_ponte():
    """D do Hamada e dos pesos = bruta + arrendamento + outros passivos financeiros; a ponte subtrai esse D e soma o caixa."""
    emp = _caso("TESTEH2COER")
    d_esperado = BRUTA_LP + ARREND + OPF
    r = M.avaliar(emp, MK)
    ec = M.estrutura_de_capital(emp, MK)
    assert ec["d"] == pytest.approx(d_esperado)                       # prêmio de Hamada
    assert r["d"] == pytest.approx(d_esperado)                        # pesos do WACC
    assert r["premio_ke"] == pytest.approx(M.premio_alavancado(d_esperado, emp.preco * emp.n_acoes / 1000, r["aliquota"]))
    caixa_livre = CAIXA - r["proventos_ja_ex"]["total"]
    assert r["dl"] == pytest.approx(d_esperado - caixa_livre)        # ponte: EV − D + caixa livre


def test_ponte_soma_o_caixa_um_por_um_com_o_desconto_igual():
    """Com o Ke e o WACC iguais (mesma bruta, mesmo E), R$ 1 a mais de caixa vira R$ 1 a mais no EPV do acionista."""
    emp = _caso("TESTEH2CX1")
    ec = M.estrutura_de_capital(emp, MK)
    epv0 = M.valores(emp, ec["mk"], e_peso=ec["e_peso"])["anc"]["EPV"]
    _serie("TESTEH2CX1", emprest_lp=BRUTA_LP, arrendamento=ARREND, caixa=CAIXA + 1_000.0)
    ec1 = M.estrutura_de_capital(emp, MK)
    assert ec1["mk"].ke_nom == ec["mk"].ke_nom
    epv1 = M.valores(emp, ec1["mk"], e_peso=ec1["e_peso"])["anc"]["EPV"]
    assert epv1 - epv0 == pytest.approx(1_000.0 / (emp.n_acoes / 1000), rel=1e-9)


def test_fluxo_nao_desconta_o_arrendamento_de_novo():
    """O FCFF parte do EBIT (já com a depreciação do direito de uso, sem o juro do arrendamento): o aluguel pago não mexe em EPV
    nem DCF — o passivo de arrendamento já está na dívida. Só o OE (fluxo do acionista) desconta o principal pago."""
    emp = _caso("TESTEH2ARR")
    r0 = M.avaliar(emp, MK)
    _serie("TESTEH2ARR", emprest_lp=BRUTA_LP, arrendamento=ARREND, caixa=CAIXA, arrendamento_pago=200.0)
    r1 = M.avaliar(emp, MK)
    assert r1["ancoras"]["EPV"] == pytest.approx(r0["ancoras"]["EPV"], rel=1e-12)
    assert r1["ancoras"]["DCF (3 cenários)"] == pytest.approx(r0["ancoras"]["DCF (3 cenários)"], rel=1e-12)
    assert r1["ancoras"]["Owner Earnings ÷ (Ke − g)"] < r0["ancoras"]["Owner Earnings ÷ (Ke − g)"]


# ---------------------------------------------------------------- H2 (a)(b)(c) sob a regra nova
def test_h2_a_ke_e_pesos_nao_dependem_do_central(monkeypatch):
    """Sem ponto fixo: a estrutura de capital nem chama o cálculo do valor — o laço central → D/E → Ke não existe."""
    emp = _caso("TESTEH2A")
    ec = M.estrutura_de_capital(emp, MK)

    def proibido(*a, **k):
        raise AssertionError("estrutura_de_capital chamou valores(): o Ke voltou a depender do central")
    monkeypatch.setattr(M, "valores", proibido)
    ec2 = M.estrutura_de_capital(emp, MK)
    assert ec2["mk"].ke_nom == ec["mk"].ke_nom and ec2["e_peso"] == emp.preco * emp.n_acoes / 1000


def test_h2_b_caixa_maior_com_a_mesma_bruta_nao_reduz_o_central():
    emp = _caso("TESTEH2B")
    c0 = M.avaliar(emp, MK)["central"]
    _serie("TESTEH2B", emprest_lp=BRUTA_LP, arrendamento=ARREND, caixa=CAIXA + 2_000.0)
    assert M.avaliar(emp, MK)["central"] >= c0


def test_h2_c_ke_nominal_acima_da_conferencia_e_nao_conclusivo(monkeypatch):
    emp = _caso("TESTEH2C")
    r0 = M.avaliar(emp, MK)
    assert r0["palavra"] != "NÃO CONCLUSIVO" or "Ke nominal" not in r0["confianca"]
    monkeypatch.setattr(M, "KE_NOM_CONFERENCIA", r0["ke_nom_emp"] - 1e-6)
    r = M.avaliar(emp, MK)
    assert r["palavra"] == "NÃO CONCLUSIVO" and "Ke nominal" in r["confianca"]


def test_regra_economica_com_kd_liquido_abaixo_do_ke_mais_divida_no_peso_baixa_o_wacc():
    """Regra do WACC (Damodaran, cap. 8 p. 52), não "favorece comprar": com Ke fixo e Kd × (1 − t) < Ke, mais peso de dívida
    (E menor, mesma D) baixa o WACC; com Kd × (1 − t) > Ke, sobe.

    OBSERVAÇÃO, NÃO ALVO (pré-registro, emendas 4 e 5): no motor, o preço menor reduz E; esse canal costuma vencer a alta do Ke
    pelo Hamada e o central sobe quando o preço cai (17 de 21 industriais em 24/11/2026, até +14% numa queda de 30%). Esse efeito
    não é propriedade desejada e não é testado aqui; o remédio é o B35 (Kd que reage à alavancagem)."""
    emp = _caso("TESTEH2W")
    ke, t = 0.25, M.aliquota(emp)
    kd_baixo = 0.8 * ke / (1 - t)          # Kd × (1 − t) < Ke
    kd_alto = 1.2 * ke / (1 - t)           # Kd × (1 − t) > Ke
    for kd, desce in ((kd_baixo, True), (kd_alto, False)):
        w = [M.wacc(emp, MK, ke_nom=ke, kd=kd, e_peso=e)[0] for e in (20_000.0, 10_000.0, 5_000.0)]   # E cai, D igual
        assert (w[0] > w[1] > w[2]) if desce else (w[0] < w[1] < w[2]), (kd, w)


def test_e_do_d_e_e_o_preco_da_data_base_sem_media():
    emp = _caso("TESTEH2P")
    for p in (5.0, 10.0, 20.0):
        r = M.avaliar(dataclasses.replace(emp, preco=p), MK)
        assert r["e_peso"] == pytest.approx(p * emp.n_acoes / 1000)
        assert r["de_peso"] == pytest.approx((BRUTA_LP + ARREND + OPF) / r["e_peso"])


# ---------------------------------------------------------------- conferência no hall (dados reais)
def test_hall_ke_acima_de_30_so_com_nao_conclusivo_e_d_igual_ao_da_ponte():
    import universo
    for tk, it in universo.avaliar_todos().items():
        emp, r = it["empresa"], it["r"]
        if not isinstance(emp, M.Industrial):
            continue
        _, ltm = M.serie(tk)
        assert r["d"] == pytest.approx(M.divida_liquida(ltm)[0] + emp.outros_passivos_financeiros), tk
        assert r["dl"] == pytest.approx(r["d"] - r["caixa_livre"]), tk
        assert r["e_peso"] == pytest.approx(emp.preco * emp.n_acoes / 1000), tk
        if r["ke_nom_emp"] > M.KE_NOM_CONFERENCIA:
            assert r["palavra"] == "NÃO CONCLUSIVO", (tk, r["ke_nom_emp"])
