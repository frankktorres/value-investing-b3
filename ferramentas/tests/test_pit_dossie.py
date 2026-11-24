"""Recálculo point-in-time do dossiê (B34, 24/11/2026): na data D vale o LTM já publicado (Res. CVM 80/2022, art. 31, II: ITR em
até 45 dias do fim do trimestre; o 4T não tem ITR, § 3º) e o "R$ de hoje" no IPCA que já tinha saído (mês D − 2). Sintéticos."""
import pytest

import inflacao
import ltm

SERIE = {"anual": {}, "ltm": {"x": 3}, "ltm_ref": "3T26", "ltm_2T26": {"x": 2}, "ltm_3T26": {"x": 3}}


@pytest.mark.parametrize("data, ref", [("2026-08-13", None), ("2026-08-14", "2T26"), ("2026-10-06", "2T26"),
                                       ("2026-11-13", "2T26"), ("2026-11-14", "3T26"), ("2027-01-10", "3T26")])
def test_ltm_publicado_na_data_pelo_prazo_do_itr(data, ref):
    if ref is None:          # 30/06 + 45 dias = 14/08: antes disso nenhum LTM da série estava publicado
        with pytest.raises(ValueError):
            ltm.ref_na_data(SERIE, data)
    else:
        assert ltm.ref_na_data(SERIE, data) == ref


def test_quarto_trimestre_falha_alto():
    with pytest.raises(ValueError, match="DFP"):
        ltm.ref_na_data({"ltm_4T26": {}, "ltm_ref": "4T26"}, "2027-06-01")


def test_na_data_troca_toda_leitura_de_ltm_e_volta():
    assert ltm.ltm_de(SERIE) == {"x": 3} and ltm.ltm_ref_de(SERIE) == "3T26"
    with ltm.na_data("2026-10-06"):
        assert ltm.ltm_de(SERIE) == {"x": 2} and ltm.ltm_ref_de(SERIE) == "2T26"
    assert ltm.ltm_de(SERIE) == {"x": 3} and ltm.ltm_ref_de(SERIE) == "3T26"


def test_ipca_ate_o_mes_d_menos_2_e_volta_mesmo_com_erro():
    deflator, base_mes, d2020 = inflacao.DEFLATOR, inflacao.BASE_MES, inflacao.DEFLATOR["2020"]
    corte = inflacao.mes_publicado_em("2026-10-15")          # out/2026 → ago/2026
    assert corte == 2026 * 12 + 7
    with pytest.raises(RuntimeError):
        with inflacao.ate(corte):
            assert inflacao.BASE_MES == corte and inflacao.DEFLATOR is deflator      # mesmo objeto: quem importou vê o corte
            assert inflacao.DEFLATOR["2020"] < d2020                                 # R$ de ago/26 < R$ do último mês
            raise RuntimeError("sai com erro")
    assert inflacao.BASE_MES == base_mes and inflacao.DEFLATOR["2020"] == d2020
