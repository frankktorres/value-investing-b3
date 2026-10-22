"""N11: o cadastro do relatório (CNPJ para o FRE, pregão para os proventos da B3) cobre os tickers da carteira que ficavam sem FRE."""
import csv
import pathlib

import pytest

from relatorio import quali

TRIAGEM = pathlib.Path(__file__).resolve().parents[1] / "triagem" / "dados" / "triagem_2026-10-02.csv"
CINCO = ["EGIE3", "PETR4", "TAEE11", "ITUB4", "SAPR11"]


@pytest.mark.parametrize("tk", CINCO)
def test_cadastro_tem_cnpj_para_o_fre(tk):
    cnpj, _ = quali._cadastro({"tk": tk})
    assert cnpj and len(cnpj) == 18


@pytest.mark.skipif(not TRIAGEM.exists(), reason="sem a triagem de 02/10")
@pytest.mark.parametrize("tk", CINCO)
def test_cnpj_confere_com_a_triagem(tk):
    linhas = {r["ticker"]: r["cnpj"] for r in csv.DictReader(TRIAGEM.open(encoding="utf-8"))}
    assert quali._cadastro({"tk": tk})[0] == linhas[tk]


def test_petr4_usa_o_pregao_do_hall():
    import proventos_ex
    assert quali._cadastro({"tk": "PETR4"})[1] == proventos_ex.PREGAO["PETR4"] == "PETROBRAS"


@pytest.mark.parametrize("tk", ["EGIE3", "TAEE11", "ITUB4", "SAPR11"])
def test_pregao_nao_conferido_nao_e_chutado(tk):
    assert quali._cadastro({"tk": tk})[1] is None


def test_ticker_desconhecido_continua_sem_cadastro():
    assert quali._cadastro({"tk": "XXXX3"}) == (None, None)
