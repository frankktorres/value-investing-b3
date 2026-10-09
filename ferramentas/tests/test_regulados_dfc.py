"""AUD-20 (doutrina v2.5 §11.2): todo regulado declara onde está o investimento na DFC, com as linhas da DFP 2025
conferidas contra o ZIP da CVM. Até a v2.4 o lote dizia "investimento no FCO" para os 9, e isso só valia em 2."""
from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pandas as pd
import pytest

import lote2_energia as L2
import universo

ZIP = Path(__file__).resolve().parent.parent / "dados" / "cvm" / "dfp_2025.zip"
CVM = {"TAEE11": "020257", "ISAE4": "018376", "CMIG4": "002453", "CPFE3": "018660", "CPLE3": "014311",
       "SAPR11": "018627", "CSMG3": "019445", "SBSP3": "014443", "EGIE3": "017329"}


def test_todo_regulado_declara_o_investimento_na_dfc():
    utilities = {tk for tk, it in universo.avaliar_todos().items() if getattr(it["empresa"], "perfil", "") == "utility"}
    assert utilities == set(L2.REGULADOS_DFC) == set(CVM)


def test_classificacao_vem_das_linhas_citadas():
    assert {tk: L2.investimento_dfc(tk) for tk in L2.REGULADOS_DFC} == {
        "TAEE11": "FCO", "ISAE4": "FCO", "EGIE3": "misto", "CPLE3": "misto",
        "CPFE3": "FCI", "CMIG4": "FCI", "SAPR11": "FCI", "CSMG3": "FCI", "SBSP3": "FCI"}
    m = L2.metodo_regulado("SBSP3")
    assert "proxy" in m and "6.02.01 -13,74 bi" in m and "FCI" in m


def _dfc(nome: str) -> pd.DataFrame:
    z = zipfile.ZipFile(ZIP)
    df = pd.read_csv(io.BytesIO(z.read(nome)), sep=";", encoding="latin-1", dtype=str)
    df["VL_CONTA"] = pd.to_numeric(df["VL_CONTA"], errors="coerce")
    df["CD_CVM"] = df["CD_CVM"].str.zfill(6)
    df = df[df["ORDEM_EXERC"].str.upper().str.contains("LTIMO")]
    return df[df["VERSAO"] == df.groupby("CD_CVM")["VERSAO"].transform("max")]


@pytest.mark.skipif(not ZIP.exists(), reason="DFP 2025 da CVM fora do disco (dados/cvm é ignorado pelo git)")
def test_linhas_citadas_batem_com_a_dfp_2025():
    dfc = {"con": _dfc("dfp_cia_aberta_DFC_MI_con_2025.csv"), "ind": _dfc("dfp_cia_aberta_DFC_MI_ind_2025.csv")}
    erradas = []
    for tk, (dem, fco, fci) in L2.REGULADOS_DFC.items():
        d = dfc[dem][dfc[dem]["CD_CVM"] == CVM[tk]]
        if dem == "ind":
            assert dfc["con"][dfc["con"]["CD_CVM"] == CVM[tk]].empty, f"{tk} tem DFC consolidada"
        valores = dict(zip(d["CD_CONTA"], d["VL_CONTA"]))
        for conta, v in {**fco, **fci}.items():
            if valores.get(conta) != v:
                erradas.append((tk, conta, v, valores.get(conta)))
    assert not erradas
