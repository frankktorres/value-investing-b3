"""B46 (emenda 12 do docs/PRE-REGISTRO-v3.md): funções puras da variante "separar a dificuldade" (Damodaran, 2009).

Camada 1: cada esperado é calculado à mão no comentário, a partir da fonte (Tabela 5 do Damodaran 2009, p. 41-42; slide 26
do Altman, "50 Years of Altman Z-Score"; waccemerg.xls), nunca importando a constante do módulo testado.
"""
from __future__ import annotations

import math

import pytest

from b46 import calculo as C


def test_pi_da_tabela_5_literal():
    # Damodaran (2009), Tabela 5, coluna de 10 anos: BB 19,63%; B- 42,12%; CC 66,6%; CCC 59,02%; B+ 28,25%
    assert C.pi_de_classe("BB") == pytest.approx(0.1963)
    assert C.pi_de_classe("B-") == pytest.approx(0.4212)
    assert C.pi_de_classe("CC") == pytest.approx(0.666)
    assert C.pi_de_classe("CCC") == pytest.approx(0.5902)
    assert C.pi_de_classe("B+") == pytest.approx(0.2825)


def test_classe_fora_da_tabela_vai_para_a_pior_seguinte():
    # emenda 12: BB+ → BB (19,63%), BBB- → BB, BB- → B+ (28,25%), CCC+ → CCC (59,02%), CCC- → CC (66,6%),
    # AA/AA- → A+ (0,57%), AAA/AA+ → AA (0,51%), BBB+ → BBB (7,54%); D e CC/D → 1
    assert C.pi_de_classe("BB+") == pytest.approx(0.1963)
    assert C.pi_de_classe("BBB-") == pytest.approx(0.1963)
    assert C.pi_de_classe("BB-") == pytest.approx(0.2825)
    assert C.pi_de_classe("CCC+") == pytest.approx(0.5902)
    assert C.pi_de_classe("CCC-") == pytest.approx(0.666)
    assert C.pi_de_classe("AA/AA-") == pytest.approx(0.0057)
    assert C.pi_de_classe("AAA/AA+") == pytest.approx(0.0051)
    assert C.pi_de_classe("BBB+") == pytest.approx(0.0754)
    assert C.pi_de_classe("D") == 1.0
    assert C.pi_de_classe("CC/D") == 1.0


def test_classe_desconhecida_falha_alto():
    with pytest.raises(KeyError):
        C.pi_de_classe("Z")


def test_pi_nao_cai_com_rating_pior():
    # C2c: ordem do rating sintético (credito.py), do melhor ao pior
    ordem = ["AAA", "AA", "A+", "A", "A-", "BBB", "BB+", "BB", "B+", "B", "B-", "CCC", "CC", "C", "D"]
    pis = [C.pi_de_classe(r) for r in ordem]
    assert all(a <= b for a, b in zip(pis, pis[1:]))
    ordem_z = [c for c, _ in C.ALTMAN_2013]
    pis_z = [C.pi_de_classe(r) for r in ordem_z]
    assert all(a <= b for a, b in zip(pis_z, pis_z[1:]))


def test_rating_altman_pela_coluna_2013():
    # slide 26, coluna 2013: a melhor classe cuja mediana ≤ Z''. Z'' 9,0 → AAA/AA+ (8,80); 5,76 → BBB (5,75);
    # 5,74 → BBB- (5,70); 4,0 → B- (3,74); 1,72 → CCC- (mediana 1,72 ≤ 1,72); 0,05 → CC/D; −1 → CC/D
    assert C.rating_altman(9.0) == "AAA/AA+"
    assert C.rating_altman(5.76) == "BBB"
    assert C.rating_altman(5.74) == "BBB-"
    assert C.rating_altman(4.0) == "B-"
    assert C.rating_altman(1.72) == "CCC-"
    assert C.rating_altman(0.05) == "CC/D"
    assert C.rating_altman(-1.0) == "CC/D"


def test_de_continuidade_e_o_menor():
    # Steel D/(D+E) 0,3373 → D/E = 0,3373 / 0,6627 = 0,50898; CSNA3 a mercado 11,75 → 0,50898
    de_ind = C.de_da_participacao(0.3373)
    assert de_ind == pytest.approx(0.3373 / 0.6627)
    assert C.de_continuidade(11.75, de_ind) == pytest.approx(0.3373 / 0.6627)
    assert C.de_continuidade(0.2, de_ind) == pytest.approx(0.2)


def test_ke_nominal_de_continuidade_a_mao():
    # rf real 7,56%, π 7,17%, t 34%, D/E 0,50898: prêmio = 5 × (1 + 0,66 × 0,50898) = 6,6796 p.p.;
    # Ke real = 7,56 + 6,6796 = 14,2396%; nominal = 1,142396 × 1,0717 − 1 = 22,4304%
    premio = 0.05 * (1 + 0.66 * (0.3373 / 0.6627))
    esperado = (1 + 0.0756 + premio) * 1.0717 - 1
    assert C.ke_nominal(0.0756, 0.0717, 0.34, 0.3373 / 0.6627) == pytest.approx(esperado)
    assert esperado == pytest.approx(0.22430, abs=1e-4)


def test_pi_combinado_e_concordancia():
    # 2 estimativas → média; concordam se |Δ| ≤ 20 p.p.
    assert C.pi_combinado(0.4212, 0.666) == pytest.approx((0.4212 + 0.666) / 2)
    assert C.concordam(0.4212, 0.5902) is True       # Δ 16,9 p.p.
    assert C.concordam(0.0754, 0.4212) is False      # Δ 34,6 p.p.
    # com uma estimativa só, vale a única (marcada) e ela NÃO conta como concordante no C3 (emenda 12)
    assert C.pi_combinado(0.3, None) == pytest.approx(0.3)
    assert C.pi_combinado(None, 0.3) == pytest.approx(0.3)
    assert C.pi_combinado(None, None) is None
    assert C.concordam(0.3, None) is False


def test_ancoras_de_continuidade_vezes_1_menos_pi_e_reproducao_fora():
    anc = {"EPV de meio de ciclo": 10.0, "DCF normalizado (3 cenários)": 20.0, "Valor de reprodução": 30.0}
    out = C.ancoras_com_pi(anc, 0.25)
    assert out == {"EPV de meio de ciclo": 7.5, "DCF normalizado (3 cenários)": 15.0, "Valor de reprodução": 30.0}
    assert C.ancoras_com_pi(anc, 1.0)["EPV de meio de ciclo"] == 0.0


def test_ancora_nao_positiva_nao_vira_positiva():
    # âncora ≤ 0 continua ≤ 0 (o motor a usa para forçar NÃO CONCLUSIVO); × (1 − π) não muda o sinal
    out = C.ancoras_com_pi({"EPV": -3.0, "DCF (3 cenários)": 5.0}, 0.5)
    assert out["EPV"] == -1.5 and math.isclose(out["DCF (3 cenários)"], 2.5)
