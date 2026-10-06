"""Perfil pelo FCA entregue até T, e composição de unit — sem decisão por ticker."""
from __future__ import annotations

import pandas as pd

from backtest.config import PADRAO
from backtest.motor.perfil import (acoes_na_unit, acoes_por_papel, perfil_de_setor, perfil_em,
                                   setor_chave)


def _geral(linhas):
    return pd.DataFrame(linhas, columns=["cd_cvm", "Data_Referencia", "Versao", "DT_RECEB",
                                         "Setor_Atividade"])


def test_setor_da_holding_segue_o_setor_declarado():
    assert setor_chave("Emp. Adm. Part. - Energia Elétrica") == "energia eletrica"
    assert setor_chave("Emp. Adm. Part.-Bolsas de Valores/Mercadorias e Futuros") == \
        "bolsas de valores/mercadorias e futuros"
    assert perfil_de_setor("Emp. Adm. Part. - Energia Elétrica") == "utility"
    assert perfil_de_setor("Emp. Adm. Part. - Sem Setor Principal") == "holding"
    assert perfil_de_setor("Bancos") == "banco"
    assert perfil_de_setor("Petróleo e Gás") == "ciclica"
    assert perfil_de_setor("Telecomunicações") == PADRAO.perfil_padrao


def test_toda_chave_da_tabela_e_um_perfil_conhecido():
    assert {p for _, p in PADRAO.perfil_por_setor} <= {"ciclica", "utility", "banco",
                                                        "seguradora", "holding"}


def test_perfil_ignora_fca_entregue_depois_de_T():
    g = _geral([(7, "2019-01-01", 1, "2019-05-30", "Bancos"),
                (7, "2020-01-01", 1, "2020-07-20", "Emp. Adm. Part. - Sem Setor Principal")])
    p = perfil_em(7, "2020-06-30", _geral=g)
    assert (p.perfil, p.dt_receb, p.motivo_exclusao) == ("banco", "2019-05-30", "")
    assert p.motor == "fin" and p.plano == "financeiro"
    # meta-teste: o documento injetado está vivo — visto depois da entrega, o perfil muda
    q = perfil_em(7, "2020-12-31", _geral=g)
    assert q.perfil == "holding" and q.motivo_exclusao == "perfil_holding_excluido"


def test_utility_usa_motor_financeiro_com_plano_industrial():
    g = _geral([(9, "2019-01-01", 1, "2019-05-30", "Energia Elétrica")])
    p = perfil_em(9, "2020-06-30", _geral=g)
    assert (p.motor, p.plano) == ("fin", "industrial")


def test_sem_fca_ate_T_exclui():
    g = _geral([(9, "2021-01-01", 1, "2021-05-30", "Energia Elétrica")])
    assert perfil_em(9, "2020-06-30", _geral=g).motivo_exclusao == "sem_setor"


def test_composicao_da_unit():
    assert acoes_na_unit("1 ON / 2 PN") == 3
    assert acoes_na_unit("2 ações preferenciais e 1 ação ordinária") == 3
    assert acoes_na_unit("1 KLBN3 + 4 KLBN4") == 5
    assert acoes_na_unit("1 ON e 2PNs") == 3
    assert acoes_na_unit("1 PN + 3 Recibos de Subscrição") is None
    assert acoes_na_unit("") is None


def test_acoes_por_papel_le_o_fca_ate_T():
    vm = pd.DataFrame([("c", "2019-01-01", 1, "2019-05-30", "Units", "ABCD11", "1 ON e 2 PN"),
                       ("c", "2019-01-01", 1, "2019-05-30", "Ações Ordinárias", "ABCD3", None),
                       ("c", "2020-01-01", 1, "2020-08-30", "Units", "ABCD11", "1 ON e 4 PN")],
                      columns=["CNPJ_Companhia", "Data_Referencia", "Versao", "DT_RECEB",
                               "Valor_Mobiliario", "Codigo_Negociacao", "Composicao_BDR_Unit"])
    assert acoes_por_papel("ABCD3", "c", "2020-06-30", _vm=vm) == 1
    assert acoes_por_papel("ABCD11", "c", "2020-06-30", _vm=vm) == 3
    assert acoes_por_papel("ABCD11", "c", "2020-12-31", _vm=vm) == 5
    assert acoes_por_papel("ZZZZ11", "c", "2020-06-30", _vm=vm) is None
