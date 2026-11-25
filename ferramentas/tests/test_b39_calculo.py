"""B39 — funções puras (emenda 9/10), casos à mão. Sem dados."""
import pytest

from b39 import calculo as c


def test_real_nominal_ida_e_volta():
    assert c.real(c.nominal(0.07, 0.05), 0.05) == pytest.approx(0.07)
    assert c.nominal(0.0, 0.05) == pytest.approx(0.05)


# ------------------------------------------------------------------ (i) bancos
def test_ke_banco_todo_nominal_a_mao():
    # ROE 20%, P/VP 2, g real 1%, π 5% → g_nom = 1,01×1,05 − 1 = 6,05%; Ke_nom = 6,05 + (20 − 6,05)/2 = 13,025%
    k_nom, k_real = c.ke_banco(0.20, 2.0, 0.01, 0.05)
    assert k_nom == pytest.approx(0.13025)
    assert k_real == pytest.approx(1.13025 / 1.05 - 1)          # 7,643%


def test_ke_banco_falha_se_misturar_roe_nominal_com_g_real():
    # A conta errada (g real no lugar do nominal) dá Ke_nom = 1% + 19%/2 = 10,5% → real 5,24%: 2,4 p.p. abaixo
    errado_real = c.real(0.01 + (0.20 - 0.01) / 2.0, 0.05)
    _, k_real = c.ke_banco(0.20, 2.0, 0.01, 0.05)
    assert k_real - errado_real == pytest.approx(0.02402, abs=1e-4)
    assert k_real != pytest.approx(errado_real, abs=1e-3)


def test_ke_banco_pvp_1_da_o_roe():
    k_nom, _ = c.ke_banco(0.15, 1.0, 0.01, 0.05)
    assert k_nom == pytest.approx(0.15)                          # P/VP = 1 ⇔ Ke = ROE, qualquer g


def test_ke_banco_pvp_invalido():
    with pytest.raises(ValueError):
        c.ke_banco(0.15, 0.0, 0.01, 0.05)


def test_roe_sobre_pl_medio_e_mediana_10_minimo_5():
    pl = {2014 + i: 100.0 + 10 * i for i in range(12)}          # 2014..2025
    lucro = {a: 0.2 * pl[a] for a in range(2015, 2026)}
    roes = c.roe_anuais(lucro, pl)
    assert roes[2015] == pytest.approx(0.2 * 110 / 105)          # PL médio (100 + 110)/2
    assert len(roes) == 11
    xs = sorted(roes[a] for a in range(2016, 2026))             # só os 10 últimos
    assert c.roe_normalizado(roes) == pytest.approx((xs[4] + xs[5]) / 2)
    assert c.roe_normalizado({2021: .1, 2022: .1, 2023: .1, 2024: .1}) is None
    assert c.roe_normalizado({a: .1 for a in range(2021, 2026)}) == pytest.approx(.1)


def test_roe_pula_ano_sem_pl_anterior_ou_pl_negativo():
    assert c.roe_anuais({2020: 10.0, 2021: 10.0}, {2020: 100.0, 2021: 100.0}) == {2021: 0.1}
    assert c.roe_anuais({2021: 10.0}, {2020: -50.0, 2021: 20.0}) == {}


# ------------------------------------------------------------------ (ii) índice
def test_e10_media_dos_10_ultimos_minimo_5():
    assert c.e10([1.0] * 2 + [2.0] * 10) == pytest.approx(2.0)
    assert c.e10([None, 1, 2, 3, 4]) is None
    assert c.e10([1, 2, 3, 4, 5]) == pytest.approx(3.0)
    assert c.e10([None] * 5 + [1, 2, 3, 4, 5]) == pytest.approx(3.0)   # None não conta, nem como zero


def test_agregado_e_soma_sobre_soma_nao_media_dos_ep():
    # A: E10 10, VM 100 (E/P 10%); B: lucro quase zero, E10 0,01, VM 300 (E/P ~0%).
    comps = [{"e10": 10.0, "vm": 100.0}, {"e10": 0.01, "vm": 300.0}]
    r = c.ke_indice(comps, vm_total=400.0)
    assert r["ke"] == pytest.approx(10.01 / 400)                 # 2,50%
    media_ep = (10 / 100 + 0.01 / 300) / 2                       # 5,00%: dobra o Ke
    inverso_media_pl = 1 / ((100 / 10 + 300 / 0.01) / 2)         # ~0,007%: P/L de lucro ~0 explode
    assert r["ke"] != pytest.approx(media_ep, abs=1e-3)
    assert r["ke"] != pytest.approx(inverso_media_pl, abs=1e-3)


def test_ke_indice_cobertura_menor_que_metade_nao_sai():
    r = c.ke_indice([{"e10": 5.0, "vm": 40.0}, {"e10": None, "vm": 60.0}], vm_total=100.0)
    assert r["ke"] is None and r["cobertura"] == pytest.approx(0.4)
    r = c.ke_indice([{"e10": 5.0, "vm": 50.0}, {"e10": None, "vm": 50.0}], vm_total=100.0)
    assert r["ke"] == pytest.approx(0.1)


def test_gordon_indice():
    assert c.ke_gordon_indice(0.5, 10.0, 100.0, 0.01) == pytest.approx(0.5 * 10 * 1.01 / 100 + 0.01)


# ------------------------------------------------------------------ (iii) Damodaran
def test_ke_damodaran_tira_s_da_taxa_nominal():
    # rf real 7,86%, π 7,17%, s 2,13%, ERP 7,47%
    n = 1.0786 * 1.0717 - 1
    k_nom, k_real = c.ke_damodaran(0.0786, 0.0717, 0.0213, 0.0747)
    assert k_nom == pytest.approx(n - 0.0213 + 0.0747)
    assert k_real == pytest.approx((1 + k_nom) / 1.0717 - 1)
    assert c.ke_damodaran_literal(0.0786, 0.0747) == pytest.approx(0.1533)


# ------------------------------------------------------------------ Ke da Mesa
def test_premio_hamada_e_ponderacao():
    assert c.premio_componente(True, None, 100.0) == 0.05
    assert c.premio_componente(False, 50.0, 100.0) == pytest.approx(0.05 * (1 + 0.66 * 0.5))
    assert c.premio_componente(False, 0.0, 100.0) == pytest.approx(0.05)   # nunca abaixo de 5 p.p.
    p = c.premio_indice([{"premio": 0.05, "vm": 300.0}, {"premio": 0.10, "vm": 100.0}])
    assert p == pytest.approx(0.0625)
    with pytest.raises(ValueError):
        c.premio_componente(False, None, 100.0)


# ------------------------------------------------------------------ gatilho
def test_gatilho_mediana_dos_tres_nos_dois_sentidos():
    assert c.gatilho({"i": 0.05, "ii": 0.04, "iii": -0.01})["veredito"] == "DISPARA"
    r = c.gatilho({"i": -0.05, "ii": -0.04, "iii": 0.10})
    assert r["veredito"] == "DISPARA" and r["mediana"] == pytest.approx(-0.04) and "acima" in r["sentido"]
    assert c.gatilho({"i": 0.02, "ii": -0.05, "iii": 0.01})["veredito"] == "NÃO DISPARA"


def test_gatilho_limite_estrito_em_3pp():
    assert c.gatilho({"i": 0.10 - 0.07, "ii": 0.03, "iii": 0.03})["veredito"] == "NÃO DISPARA"   # 0,030000000000000013
    assert c.gatilho({"i": 0.0301, "ii": 0.0301, "iii": 0.0})["veredito"] == "DISPARA"


def test_gatilho_com_duas_e_a_media_com_uma_nao_conclusiva():
    r = c.gatilho({"i": 0.02, "ii": None, "iii": 0.05})
    assert r["mediana"] == pytest.approx(0.035) and r["veredito"] == "DISPARA" and r["faltam"] == ["ii"]
    r = c.gatilho({"i": 0.10, "ii": None, "iii": None})
    assert r["veredito"] == "NÃO CONCLUSIVA" and r["mediana"] is None


# ------------------------------------------------------------------ emenda 11: (i) toda em real
ITUB4_ROE_NOM = {2016: 0.186947, 2017: 0.169033, 2018: 0.166897, 2019: 0.180795, 2020: 0.124320,
                 2021: 0.167774, 2022: 0.173788, 2023: 0.175907, 2024: 0.195487, 2025: 0.205596}
IPCA_ANO = {2016: 0.062881, 2017: 0.029473, 2018: 0.037455, 2019: 0.043060, 2020: 0.045173,       # SGS 433, jan–dez
            2021: 0.100611, 2022: 0.057848, 2023: 0.046211, 2024: 0.048313, 2025: 0.042644}


def test_itub4_a_mao_emenda11():
    # ROE real 2023 = 1,175907/1,046211 − 1 = 12,397%; 2018 = 1,166897/1,037455 − 1 = 12,477% → mediana dos 10 = 12,437%
    rr = c.roe_reais(ITUB4_ROE_NOM, IPCA_ANO)
    assert rr[2023] == pytest.approx(0.123967, abs=1e-6) and rr[2018] == pytest.approx(0.124768, abs=1e-6)
    rn = c.roe_normalizado(rr)
    assert rn == pytest.approx(0.124368, abs=1e-6)
    # Ke real = 1% + (12,437% − 1%) ÷ 1,948 = 6,871%
    assert c.ke_banco_real(rn, 1.948031, 0.01) == pytest.approx(0.06871, abs=1e-5)


def test_falha_se_misturar_roe_historico_com_pi_futuro():
    # a conta da emenda 9 (ROE nominal histórico, g nominal com a π futura de 7,17%) dá 5,43% no ITUB4: 1,4 p.p. abaixo
    misturado = c.ke_banco(c.roe_normalizado(ITUB4_ROE_NOM), 1.948031, 0.01, 0.071706)[1]
    certo = c.ke_banco_real(c.roe_normalizado(c.roe_reais(ITUB4_ROE_NOM, IPCA_ANO)), 1.948031, 0.01)
    assert misturado == pytest.approx(0.0543, abs=1e-4)
    assert certo - misturado > 0.014
    # e as duas só coincidem se a π histórica for igual à futura (aqui, IPCA constante = π)
    const = {a: 0.071706 for a in ITUB4_ROE_NOM}
    assert c.ke_banco_real(c.roe_normalizado(c.roe_reais(ITUB4_ROE_NOM, const)), 1.948031, 0.01) == pytest.approx(misturado, abs=1e-4)


def test_inflacao_acumulada():
    assert c.inflacao_acumulada([0.01] * 12) == pytest.approx(1.01 ** 12 - 1)
    assert c.roe_reais({2020: 0.1, 2030: 0.1}, {2020: 0.05}) == {2020: pytest.approx(1.1 / 1.05 - 1)}
