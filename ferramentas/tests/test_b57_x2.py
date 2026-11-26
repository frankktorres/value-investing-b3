"""B57 — X2 do Z'' de Altman com os lucros retidos da lei: reservas de lucros (2.03.04) + lucros/prejuízos acumulados
(2.03.05). Emenda 13 do `docs/PRE-REGISTRO-v3.md`; fontes em `docs/b57/FONTES-B57.md`. Camada 1: esperado à mão."""
import pytest

import coletar_cvm
import motor_nao_financeiras as M

# GAFISA S.A. (CD_CVM 016101; fora do conjunto de desenvolvimento), DFP 2025 versão 1, consolidado, último exercício, R$ mil:
# dfp_cia_aberta_BPA_con_2025.csv (1, 1.01), _BPP_con_ (2.01, 2.02, 2.03, 2.03.04, 2.03.05), _DRE_con_ (3.05).
GAFISA = dict(ativo=4727891.0, ac=2508821.0, pc=2010992.0, pnc=1179866.0, pl=1537033.0, reservas_lucro=0.0,
              lucros_acumulados=-624248.0, ebit=-414570.0)
# À mão: X1 = (2.508.821 − 2.010.992) ÷ 4.727.891 = 0,1052962; X2 = (0 − 624.248) ÷ 4.727.891 = −0,1320352;
# X3 = −414.570 ÷ 4.727.891 = −0,0876860; X4 = 1.537.033 ÷ (2.010.992 + 1.179.866) = 0,4816990.
# Z'' = 3,25 + 6,56 × 0,1052962 + 3,26 × (−0,1320352) + 6,72 × (−0,0876860) + 1,05 × 0,4816990 = 3,42684.
# Com o X2 antigo (só 2.03.04 = 0): 3,85728 — o prejuízo acumulado de R$ 624 mi não aparecia.
Z_GAFISA = 3.42684


def test_x2_conta_o_prejuizo_acumulado():
    z, zona = M.altman_z2(GAFISA)
    assert z == pytest.approx(Z_GAFISA, abs=1e-4)
    assert zona == "perigo"                     # < 4,15


def test_x2_soma_reservas_e_lucro_do_ano_sem_destino():
    # Balanço de ITR inventado, números redondos: X1 = (300 − 200) ÷ 1000 = 0,10; X2 = (100 + 50) ÷ 1000 = 0,15;
    # X3 = 100 ÷ 1000 = 0,10; X4 = 500 ÷ (200 + 300) = 1,00 → Z'' = 3,25 + 0,656 + 0,489 + 0,672 + 1,05 = 6,117.
    d = dict(ativo=1000.0, ac=300.0, pc=200.0, pnc=300.0, pl=500.0, reservas_lucro=100.0, lucros_acumulados=50.0, ebit=100.0)
    z, zona = M.altman_z2(d)
    assert z == pytest.approx(6.117, abs=1e-9)
    assert zona == "segura"                     # > 5,85


@pytest.mark.parametrize("como", ["sem a chave", "None"])
def test_sem_a_2_03_05_e_erro_explicito(como):
    d = dict(GAFISA)
    if como == "sem a chave":
        del d["lucros_acumulados"]
    else:
        d["lucros_acumulados"] = None
    with pytest.raises(ValueError, match="2.03.05"):
        M.altman_z2(d)                          # nunca 0 silencioso (série antiga não recoletada)


def test_coletor_le_a_2_03_05_no_balanco_do_ltm():
    assert coletar_cvm.BPP["lucros_acumulados"] == "2.03.05"
    assert coletar_cvm.BPP["reservas_lucro"] == "2.03.04"
    assert "lucros_acumulados" in coletar_cvm.CHAVES_BALANCO     # o LTM leva o balanço da data do ITR
