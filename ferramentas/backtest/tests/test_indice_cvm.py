"""Portão da fatia 3: o índice de DT_RECEB/VERSAO e a classificação de contaminação.

Casos conferidos à mão contra os ZIPs, não contra a própria implementação. O central é a
NEOENERGIA: o FY2016 dela tem SETE versões, de 2017-02-22 a 2019-04-24, e o CSV de demonstração
serve a versão 7. Logo um leitor de 30/06/2017 via a versão 1, e o número que temos hoje é do
futuro — `contaminado`. Já em 30/06/2019 a versão 7 era pública: `limpo`. Se este teste passar a
falhar, ou a CVM mudou o espelho ou a seleção point-in-time quebrou.
"""
from __future__ import annotations

import pytest

from backtest.config import PADRAO
from backtest.ledger import indice_cvm as ic

NEOENERGIA = 15539
BCO_BRASIL = 1023


@pytest.fixture(scope="module")
def idx_dfp():
    return ic.indexar("dfp")


@pytest.fixture(scope="module")
def idx_itr():
    return ic.indexar("itr")


# ------------------------------------------------------------------------------ o índice existe
def test_indice_tem_tamanho_esperado(idx_dfp, idx_itr) -> None:
    assert len(idx_dfp) > 10_000, f"DFP: esperava mais de 10 mil documento-versões, veio {len(idx_dfp)}"
    assert len(idx_itr) > 30_000, f"ITR: esperava mais de 30 mil, veio {len(idx_itr)}"
    assert idx_dfp["cd_cvm"].nunique() > 1_000
    assert idx_dfp["dt_receb"].min() < "2012-01-01", "o índice tem de alcançar o início da série"


def test_identidade_documento_versao_e_unica(idx_dfp, idx_itr) -> None:
    for idx in (idx_dfp, idx_itr):
        assert not idx.duplicated(["cd_cvm", "dt_refer", "versao"]).any()


def test_dt_receb_nunca_precede_o_exercicio_nos_dados_usados(idx_dfp) -> None:
    """Linha com recebimento antes do fim do exercício é corrupção, e é excluída da visão PIT."""
    for d in PADRAO.datas_corte[:3]:
        vis = ic.documentos_visiveis("dfp", d)
        assert (vis["dt_refer"] <= vis["dt_receb"]).all()


def test_existe_exercicio_social_fora_de_dezembro(idx_dfp) -> None:
    """Prova que chavear por ano-calendário misturaria exercícios — a chave é (cd_cvm, dt_refer)."""
    refs_2017 = set(idx_dfp.loc[idx_dfp["ano_zip"] == 2017, "dt_refer"])
    assert len(refs_2017) > 1, f"esperava DT_REFER variado em 2017, veio {refs_2017}"
    assert any(not r.endswith("-12-31") for r in refs_2017)


# ------------------------------------------------------- o caso NEOENERGIA, conferido à mão
def test_neoenergia_fy2016_tem_sete_versoes(idx_dfp) -> None:
    neo = idx_dfp[(idx_dfp["cd_cvm"] == NEOENERGIA) & (idx_dfp["dt_refer"] == "2016-12-31")]
    assert len(neo) == 7, f"esperava 7 versões, veio {len(neo)}"
    assert neo["dt_receb"].min() == "2017-02-22"
    assert neo["dt_receb"].max() == "2019-04-24"


def test_neoenergia_contaminada_em_2017_e_limpa_em_2019() -> None:
    def estado(T: str) -> tuple[int, int, str]:
        v = ic.documentos_visiveis("dfp", T)
        r = v[(v["cd_cvm"] == NEOENERGIA) & (v["dt_refer"] == "2016-12-31")]
        assert len(r) == 1, f"em {T} esperava 1 linha para o FY2016, veio {len(r)}"
        return int(r["versao"].iloc[0]), int(r["versao_disco"].iloc[0]), r["estado"].iloc[0]

    assert estado("2017-06-30") == (1, 7, ic.CONTAMINADO)
    assert estado("2019-06-30") == (7, 7, ic.LIMPO)
    assert estado("2025-12-31") == (7, 7, ic.LIMPO)


def test_fy2016_da_neoenergia_nao_existe_antes_de_ser_entregue() -> None:
    """Em 31/12/2016 o exercício acabou de fechar e nada foi entregue: ausência, não número."""
    v = ic.documentos_visiveis("dfp", "2016-12-31")
    r = v[(v["cd_cvm"] == NEOENERGIA) & (v["dt_refer"] == "2016-12-31")]
    assert r.empty, "exercício visível antes do primeiro DT_RECEB (2017-02-22)"


# --------------------------------------------------------- o ITR do próprio trimestre não vale
def test_itr_do_2t_nao_esta_disponivel_no_corte_de_30_06() -> None:
    """Medido: o ITR de 30/06/2014 do BB foi recebido em 14/08/2014. Em T=30/06 vale o 1T."""
    v = ic.documentos_visiveis("itr", "2014-06-30")
    bb = v[v["cd_cvm"] == BCO_BRASIL]
    assert "2014-06-30" not in set(bb["dt_refer"]), "ITR do 2T não podia estar visível em 30/06"
    assert "2014-03-31" in set(bb["dt_refer"]), "o ITR do 1T devia estar visível"


# -------------------------------------------------------------- a taxa de contaminação é baixa
def test_contaminacao_e_pequena_e_decrescente() -> None:
    """Regressão do bug que marcava 45%: ler só a DRE consolidada deixava sem aferição as
    companhias que não entregam consolidada, e ausência de prova era contada como contaminação."""
    rel = ic.relatorio_contaminacao("dfp", PADRAO.datas_corte)
    assert rel["pct_contaminado"].max() < 5.0, \
        f"contaminação acima de 5% indica junção errada, não reapresentação: \n{rel.to_string()}"
    assert rel["sem_demonstracao"].max() < 50, \
        f"muitos exercícios sem demonstração nenhuma — a leitura con+ind quebrou:\n{rel.to_string()}"
    primeiros = rel.head(4)["pct_contaminado"].mean()
    ultimos = rel.tail(4)["pct_contaminado"].mean()
    assert ultimos < primeiros, \
        "exercício recente teve menos tempo para ser reapresentado; a taxa devia cair"


def test_visiveis_crescem_com_a_data() -> None:
    ns = [len(ic.documentos_visiveis("dfp", d)) for d in PADRAO.datas_corte]
    assert ns == sorted(ns), f"o conjunto visível só pode crescer com T: {ns}"


def test_estados_sao_exaustivos() -> None:
    v = ic.documentos_visiveis("dfp", "2020-06-30")
    assert set(v["estado"]) <= {ic.LIMPO, ic.CONTAMINADO, ic.SEM_DEMONSTRACAO}
    assert not v["estado"].isna().any()
