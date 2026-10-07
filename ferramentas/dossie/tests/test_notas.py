"""Fronteiras de cada faixa da rubrica de notas (dossie/notas.py)."""
import pytest

from dossie import notas
from dossie.notas import Nota

W = 0.08
EST = [0.40, 0.41, 0.40, 0.41, 0.40, 0.41]  # margem estável (dp ~0,5 p.p.)


def roic(n_acima, total):
    """total exercícios; n_acima com ROIC > WACC."""
    return {2000 + i: (0.15 if i < n_acima else 0.01) for i in range(total)}


def moat(n_acima, total, brutas=EST, ebit=None):
    return notas.moat(roic(n_acima, total), W, brutas, ebit).base


# ------------------------------------------------------------------ moat
def test_moat_f_1_vale_5():
    assert moat(10, 10) == 5


def test_moat_f_08_exato_vale_4_e_abaixo_vale_3():
    assert moat(8, 10) == 4
    assert moat(11, 14) == 3          # 0,786 < 0,8


def test_moat_f_07_exato_vale_3_e_abaixo_vale_2():
    assert moat(7, 10) == 3
    assert moat(9, 13) == 2           # 0,692 < 0,7


def test_moat_f_05_exato_vale_2_e_abaixo_vale_1():
    assert moat(5, 10) == 2
    assert moat(6, 13) == 1           # 0,46 < 0,5


def test_moat_f_zero_vale_0_e_qualquer_acima_vale_1():
    assert moat(0, 10) == 0
    assert moat(1, 10) == 1


def test_moat_janela_zero_vale_0():
    assert notas.moat({}, W, EST).base == 0


def test_moat_desvio_margem_bruta_na_fronteira():
    assert moat(10, 10, brutas=[0.40, 0.45, 0.50]) == 5       # dp = 5,0 p.p. exato: sem penalidade
    assert moat(10, 10, brutas=[0.40, 0.46, 0.52]) == 4       # dp = 6 p.p. > 5


def test_moat_usa_margem_ebit_se_bruta_ausente_ou_curta():
    n = notas.moat(roic(10, 10), W, None, [0.10, 0.30, 0.10, 0.30])
    assert n.base == 4 and any("EBIT" in c for c in n.componentes)
    n2 = notas.moat(roic(10, 10), W, [0.4, 0.4], EST)          # bruta com < 3 pontos
    assert n2.base == 5 and any("EBIT" in c for c in n2.componentes)


def test_moat_sem_nenhuma_margem_perde_1_conservador():
    assert notas.moat(roic(10, 10), W, None, None).base == 4
    assert notas.moat(roic(10, 10), W, [0.4], [0.4, 0.5]).base == 4


def test_moat_tetos_de_janela():
    assert moat(10, 10) == 5          # 10 exercícios: sem teto
    assert moat(9, 9) == 4            # 9 < 10: teto 4
    assert moat(7, 7) == 4            # 7 não é < 7
    assert moat(6, 6) == 3            # 6 < 7: teto 3
    assert moat(3, 3) == 3


def test_moat_piso_zero():
    assert notas.moat(roic(0, 10), W, None, None).base == 0


def test_moat_componentes_explicam_com_numero():
    n = notas.moat(roic(8, 10), W, EST)
    assert isinstance(n, Nota) and n.nome == "moat"
    assert any("8 de 10" in c for c in n.componentes)


# ------------------------------------------------------------------ ciclo
FLAT = [100, 101, 102, 103]
M_OK = [0.20, 0.20, 0.20, 0.20]


def test_ciclo_queda_na_fronteira():
    assert notas.ciclo(FLAT, M_OK, 0).base == 5                       # nunca cai
    assert notas.ciclo([100, 95.01, 96], M_OK, 0).base == 5           # queda 4,99%
    assert notas.ciclo([100, 95, 96], M_OK, 0).base == 4              # 5% exato
    assert notas.ciclo([100, 90, 96], M_OK, 0).base == 3              # 10% exato
    assert notas.ciclo([100, 80, 96], M_OK, 0).base == 2              # 20% exato
    assert notas.ciclo([100, 65, 96], M_OK, 0).base == 1              # 35% exato


def test_ciclo_desvio_margem_na_fronteira():
    assert notas.ciclo(FLAT, [0.10, 0.13, 0.16], 0).base == 5         # dp = 3,0 p.p. exato
    assert notas.ciclo(FLAT, [0.10, 0.1301, 0.1602], 0).base == 4     # 3,01 p.p.
    assert notas.ciclo(FLAT, [0.10, 0.15, 0.20], 0).base == 4         # 5,0 exato
    assert notas.ciclo(FLAT, [0.10, 0.1501, 0.2002], 0).base == 3     # 5,01
    assert notas.ciclo(FLAT, [0.10, 0.18, 0.26], 0).base == 3         # 8,0 exato
    assert notas.ciclo(FLAT, [0.10, 0.1801, 0.2602], 0).base == 2     # 8,01
    assert notas.ciclo(FLAT, [0.10, 0.22, 0.34], 0).base == 2         # 12,0 exato
    assert notas.ciclo(FLAT, [0.10, 0.2201, 0.3402], 0).base == 1     # 12,01


def test_ciclo_base_e_o_menor_das_duas_escalas():
    assert notas.ciclo([100, 65, 96], [0.10, 0.13, 0.16], 0).base == 1   # A=1, B=5
    assert notas.ciclo(FLAT, [0.10, 0.22, 0.34], 0).base == 2           # A=5, B=2


def test_ciclo_prejuizo_operacional_teto_1():
    assert notas.ciclo(FLAT, M_OK, 1).base == 5
    assert notas.ciclo(FLAT, M_OK, 2).base == 1
    assert notas.ciclo(FLAT, M_OK, 5).base == 1


def test_ciclo_serie_curta_base_1():
    n = notas.ciclo([100, 110], [0.2, 0.2], 0)
    assert n.base == 1 and "série curta" in n.componentes[0]
    assert notas.ciclo(FLAT, [0.2, 0.2], 0).base == 1


# ------------------------------------------------------------------ gestão
def test_gestao_neutra_e_3():
    assert notas.gestao(1.2, 0.0, 0.03, False).base == 3


def test_gestao_r1_fronteiras():
    assert notas.gestao(1.5, 0.0, 0.03, False).base == 4
    assert notas.gestao(1.49, 0.0, 0.03, False).base == 3
    assert notas.gestao(1.0, 0.0, 0.03, False).base == 3
    assert notas.gestao(0.99, 0.0, 0.03, False).base == 2


def test_gestao_r1_na_e_zero_e_none_menos_1():
    assert notas.gestao("n/a", 0.0, 0.03, False).base == 3
    assert notas.gestao(None, 0.0, 0.03, False).base == 2


def test_gestao_cagr_fronteiras():
    assert notas.gestao(1.2, 0.02, 0.03, False).base == 2
    assert notas.gestao(1.2, 0.019, 0.03, False).base == 3
    assert notas.gestao(1.2, -0.01, 0.03, False).base == 4
    assert notas.gestao(1.2, -0.009, 0.03, False).base == 3
    assert notas.gestao(1.2, None, 0.03, False).base == 2


def test_gestao_remuneracao_fronteira():
    assert notas.gestao(1.2, 0.0, 0.05, False).base == 3
    assert notas.gestao(1.2, 0.0, 0.0501, False).base == 2
    assert notas.gestao(1.2, 0.0, None, False).base == 2


def test_gestao_ma():
    assert notas.gestao(1.2, 0.0, 0.03, True).base == 2
    assert notas.gestao(1.2, 0.0, 0.03, None).base == 2


def test_gestao_limites_0_e_5():
    assert notas.gestao(None, None, None, None).base == 0
    assert notas.gestao(2.0, -0.05, 0.01, False).base == 5     # 3+1+1 = 5
    assert notas.gestao(0.5, 0.05, 0.2, True).base == 0        # 3-4 = -1 -> 0


# ------------------------------------------------------------------ controlador
def test_controlador_base():
    assert notas.controlador(True, 1.0, 0.0, 0).base == 4
    assert notas.controlador(False, 1.0, 0.0, 0).base == 5
    assert notas.controlador(None, 1.0, 0.0, 0).base == 4


def test_controlador_tag_along():
    assert notas.controlador(False, 1.0, 0.0, 0).base == 5
    assert notas.controlador(False, 0.8, 0.0, 0).base == 4
    assert notas.controlador(False, None, 0.0, 0).base == 4


def test_controlador_partes_relacionadas_fronteiras():
    assert notas.controlador(False, 1.0, 0.05, 0).base == 5
    assert notas.controlador(False, 1.0, 0.0501, 0).base == 4
    assert notas.controlador(False, 1.0, 0.15, 0).base == 4
    assert notas.controlador(False, 1.0, 0.1501, 0).base == 3
    assert notas.controlador(False, 1.0, None, 0).base == 4


def test_controlador_interferencias_maximo_3():
    assert notas.controlador(False, 1.0, 0.0, 1).base == 4
    assert notas.controlador(False, 1.0, 0.0, 3).base == 2
    assert notas.controlador(False, 1.0, 0.0, 10).base == 2
    with pytest.raises(ValueError):
        notas.controlador(False, 1.0, 0.0, -1)


def test_controlador_piso_zero():
    assert notas.controlador(True, None, 0.5, 3).base == 0


# ------------------------------------------------------------------ Fisher
def resp(n_sim):
    return ["sim"] * n_sim + ["nao"] * (15 - n_sim)


@pytest.mark.parametrize("n,esperado", [(0, 0), (1, 0), (2, 1), (3, 1), (4, 1), (5, 2), (7, 2), (8, 3), (9, 3), (15, 5)])
def test_fisher_half_up(n, esperado):
    assert notas.fisher(resp(n)).base == esperado


def test_fisher_tres_sim_vale_1_e_cinco_sim_vale_2_nao_bancario():
    assert notas.fisher(resp(3)).base == 1
    assert notas.fisher(resp(5)).base == 2     # 1,67 -> 2
    assert notas.fisher(resp(9)).base == 3


def test_fisher_sem_conta_como_nao_sim():
    assert notas.fisher(["sim"] * 9 + ["sem"] * 6).base == 3


def test_fisher_exige_15_itens_e_valores_validos():
    with pytest.raises(ValueError):
        notas.fisher(["sim"] * 14)
    with pytest.raises(ValueError):
        notas.fisher(["sim"] * 16)
    with pytest.raises(ValueError):
        notas.fisher(["sim"] * 14 + ["talvez"])


# ------------------------------------------------------------------ final / média / para_qual
N3 = Nota("x", 3, [])


def test_final_sem_ajuste():
    assert notas.final(N3) == 3


def test_final_ajuste_com_fonte_a_ou_b():
    assert notas.final(N3, 1, "FRE 2026 p.10", "A") == 4
    assert notas.final(N3, -1, "relatório X", "B") == 2


def test_final_ajuste_sem_fonte_levanta():
    with pytest.raises(ValueError):
        notas.final(N3, 1, "", "A")
    with pytest.raises(ValueError):
        notas.final(N3, 1, "   ", "A")
    with pytest.raises(ValueError):
        notas.final(N3, -1)


def test_final_fonte_nota_c_ou_vazia_levanta():
    with pytest.raises(ValueError):
        notas.final(N3, 1, "blog", "C")
    with pytest.raises(ValueError):
        notas.final(N3, 1, "algo", "")


def test_final_ajuste_invalido_levanta():
    with pytest.raises(ValueError):
        notas.final(N3, 2, "fonte", "A")


def test_final_clamp_0_5():
    assert notas.final(Nota("x", 5, []), 1, "f", "A") == 5
    assert notas.final(Nota("x", 0, []), -1, "f", "B") == 0


def test_media_com_e_sem_peso_dobrado():
    assert notas.media(4, 3, 5, 2, 1, discricionario=False) == pytest.approx(15 / 5)
    assert notas.media(4, 3, 5, 2, 1, discricionario=True) == pytest.approx(20 / 6)


def test_para_qual_formato_dos_lotes():
    q = notas.para_qual(4, 3, 5, 2, 1)
    assert q == {"moat": 4, "gestao": 3, "controlador": 5, "ciclo": 2, "fisher": 1}


def test_controlador_interferencias_sem_evidencia_e_conservador():
    # None = busca não documentada → −1, como os demais componentes sem evidência (adversário, 07/10/2026)
    assert notas.controlador(True, 1.0, 0.0, None).base == 3
    assert notas.controlador(True, 1.0, 0.0, 0).base == 4
