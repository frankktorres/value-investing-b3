"""AUD-17 (auditoria 08/10/2026): DDM de 2 estágios e P/VP justificado com resposta calculada à mão.

Antes, a única guarda era a regressão contra o golden, que o próprio motor gerou (circular: erro de fórmula seria gravado
sem alarme). Aqui as respostas vêm de aritmética de papel, fora do motor.
Mercado do teste: rf real 5%, prêmio 5%, π 5% → Ke nominal 1,10 × 1,05 − 1 = 15,5%; teto de g = 1,05 × 1,02 − 1 = 7,1%.
"""
import pytest

from motor_financeiras import Financeira, Mercado, ddm_dois_estagios, g_de, pvp_justificado

MK = Mercado(rf_real=0.05, pi=0.05)
KE = 0.155


def _emp(**kw):
    base = dict(ticker="T", nome="T", perfil="banco", preco=10.0, vpa=20.0, lpa_12m=2.0, roe_lp=0.10, roe_inicio=0.10,
                payout=0.5, dpa_medio_5a=1.0)
    base.update(kw)
    return Financeira(**base)


def test_ke_do_mercado_do_teste():
    assert MK.ke_nom == pytest.approx(KE)
    assert MK.g_teto == pytest.approx(0.071)


def test_pvp_justificado_a_mao():
    # (ROE − g) / (Ke − g) = (0,10 − 0,05) / (0,155 − 0,05) = 0,05 / 0,105
    assert pvp_justificado(0.10, 0.05, KE) == pytest.approx(0.05 / 0.105)
    # ROE = Ke → vale o patrimônio (P/VP = 1), qualquer que seja o g
    assert pvp_justificado(KE, 0.05, KE) == pytest.approx(1.0)
    # ROE abaixo do Ke destrói valor: P/VP < 1; acima, > 1
    assert pvp_justificado(0.10, 0.05, KE) < 1 < pvp_justificado(0.20, 0.05, KE)


def test_g_perpetuo_e_roe_vezes_retencao_com_teto():
    assert g_de(_emp(), MK, 0.10) == pytest.approx(0.05)                 # 0,10 × (1 − 0,5)
    assert g_de(_emp(payout=0.1), MK, 0.20) == pytest.approx(0.071)      # 0,18 > teto → teto


def test_ddm_com_roe_constante_e_igual_a_gordon():
    # ROE de partida = ROE de longo prazo → o PL e os dividendos crescem a g desde o ano 1, então o DDM de 2 estágios
    # tem de coincidir com Gordon: D1 / (Ke − g) = (0,5 × 0,10 × 20) / 0,105 = 1 / 0,105
    vp, fluxo, terminal = ddm_dois_estagios(_emp(), MK, 0.10)
    assert vp == pytest.approx(1.0 / 0.105, rel=1e-9)
    assert vp == pytest.approx(20.0 * pvp_justificado(0.10, 0.05, KE), rel=1e-9)       # = VPA × P/VP justificado
    assert [round(d, 6) for _, _, _, d, _ in fluxo] == [round(1.0 * 1.05 ** (t - 1), 6) for t in range(1, 6)]


def test_ddm_com_roe_convergindo_valores_de_papel():
    # ROE 6% → 10% em 5 anos (6,8 / 7,6 / 8,4 / 9,2 / 10,0%), payout 50%, VPA 20; contas feitas fora do motor
    vp, fluxo, terminal = ddm_dois_estagios(_emp(roe_inicio=0.06), MK, 0.10)
    assert [round(f[4], 4) for f in fluxo] == [20.68, 21.4658, 22.3674, 23.3963, 24.5661]       # VPA no fim de cada ano
    assert [round(f[3], 4) for f in fluxo] == [0.68, 0.7858, 0.9016, 1.0289, 1.1698]            # dividendos
    assert terminal == pytest.approx(11.6982, abs=1e-4)             # VPA5 × (0,10 − 0,05) / (0,155 − 0,05)
    assert vp == pytest.approx(8.6015, abs=1e-4)                    # 2,9102 de dividendos a VP + 11,6982 / 1,155^5


def test_ddm_roe_menor_vale_menos():
    alto = ddm_dois_estagios(_emp(roe_inicio=0.10), MK, 0.10)[0]
    baixo = ddm_dois_estagios(_emp(roe_inicio=0.06), MK, 0.10)[0]
    assert baixo < alto
