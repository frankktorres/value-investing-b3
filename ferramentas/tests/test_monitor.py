"""Monitor semanal: fronteiras dos alertas, troca atômica do COTAHIST, aviso de dado velho e a prova
de que, no pregão do hall (02/10/2026), o monitor reproduz o P/C do golden ticker a ticker."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
import pytest

import monitor_semanal as M


@pytest.mark.parametrize("preco,esperado", [
    (7.0, M.COMPRA), (6.99, M.COMPRA), (7.01, M.OBSERVA), (7.70, M.OBSERVA), (7.71, M.NEUTRO),
    (12.99, M.NEUTRO), (13.0, M.SAIDA), (20.0, M.SAIDA)])
def test_fronteiras_compra_070_saida_130(preco, esperado):
    assert M.alerta(preco, 7.0, 13.0) == esperado          # central 10


def test_saida_por_qualidade_150():
    assert M.alerta(14.0, 7.0, 15.0) == M.NEUTRO           # 1,40× não alerta quando a saída é 1,50×
    assert M.alerta(15.0, 7.0, 15.0) == M.SAIDA


def test_sem_central_nao_alerta():
    assert M.alerta(5.0, math.nan, math.nan) == M.SEM
    assert M.alerta(5.0, -1.0, -2.0) == M.SEM


def test_troca_atomica_devolve_o_zip_bom(tmp_path: Path):
    destino, novo, velho = tmp_path / "A.ZIP", tmp_path / "A.novo", tmp_path / "A.anterior"
    destino.write_bytes(b"bom")
    novo.write_bytes(b"torto")
    chamadas = []

    def gerar(ano):
        chamadas.append(destino.read_bytes())
        if destino.read_bytes() == b"torto":
            raise ValueError("trailer não confere")
    estado = M.trocar_e_gerar(2026, novo, destino, velho, gerar)
    assert estado.startswith("falhou") and "mantido o anterior" in estado
    assert destino.read_bytes() == b"bom"
    assert chamadas == [b"torto", b"bom"]                  # o parquet foi regerado do bom


def test_troca_atomica_aceita_o_novo(tmp_path: Path):
    destino, novo, velho = tmp_path / "A.ZIP", tmp_path / "A.novo", tmp_path / "A.anterior"
    destino.write_bytes(b"velho")
    novo.write_bytes(b"novo")
    assert M.trocar_e_gerar(2026, novo, destino, velho, lambda a: None) == "atualizado"
    assert destino.read_bytes() == b"novo" and not velho.exists() and not novo.exists()


def test_ano_novo_sem_zip_anterior(tmp_path: Path):
    destino, novo = tmp_path / "A2027.ZIP", tmp_path / "A2027.novo"
    novo.write_bytes(b"x")
    assert M.trocar_e_gerar(2027, novo, destino, tmp_path / "v", lambda a: None) == "atualizado"


def _hall():
    return [dict(ticker="AAAA3", lote=1, palavra="CARA", preco=10.0, central=5.0, pc=2.0, compra=3.5,
                 saida=6.5, saida_qualidade=False, alerta=M.SAIDA, carteira=True)]


def test_dado_velho_no_topo():
    md = M.markdown(_hall(), pd.DataFrame(), {}, "2026-09-20", "2026-10-06", "falhou: x")
    assert md.startswith("> **DADO VELHO:**")
    md = M.markdown(_hall(), pd.DataFrame(), {}, "2026-10-02", "2026-10-06", "atualizado")
    assert "DADO VELHO" not in md


def test_monitor_nao_muda_palavra():
    md = M.markdown(_hall(), pd.DataFrame(), {}, "2026-10-02", "2026-10-06", "ok")
    assert "| CARA |" in md and "não muda palavra" in md


COTA = Path(__file__).resolve().parent.parent / "backtest" / "dados" / "cotahist" / "precos_2026.parquet"


@pytest.mark.skipif(not COTA.exists(), reason="COTAHIST 2026 fora do disco")
def test_no_pregao_do_hall_reproduz_o_golden():
    """Em 02/10/2026 (preços do 03) o P/C do monitor = o do golden a 2%: mesma fonte de central."""
    refs = M.referencias_do_hall()
    precos, pregao = M.ultimos_precos(set(refs), "2026-10-02")
    assert pregao == "2026-10-02"
    g = json.loads((Path(__file__).parent / "golden.json").read_text(encoding="utf-8"))["tickers"]
    comparados = 0
    for x in M.linhas_hall(refs, precos):
        gp = g[x["ticker"]]["pc"]
        if math.isfinite(gp):
            assert x["pc"] == pytest.approx(gp, rel=0.02), x["ticker"]
            comparados += 1
    assert comparados == 40      # só a RECV3 tem central ≤ 0 (a KLBN11 voltou a positivo com o ponto fixo partindo do contábil)


def test_ano_novo_com_arquivo_torto_nao_fica_no_lugar(tmp_path: Path):
    destino, novo = tmp_path / "A2027.ZIP", tmp_path / "A2027.novo"
    novo.write_bytes(b"torto")

    def gerar(ano):
        raise ValueError("trailer")
    estado = M.trocar_e_gerar(2027, novo, destino, tmp_path / "v", gerar)
    assert "não havia arquivo anterior" in estado
    assert not destino.exists() and (tmp_path / "A2027.rejeitado").exists()


def test_anterior_que_tambem_nao_regera_nao_estoura(tmp_path: Path):
    destino, novo, velho = tmp_path / "A.ZIP", tmp_path / "A.novo", tmp_path / "A.anterior"
    destino.write_bytes(b"velho")
    novo.write_bytes(b"novo")

    def gerar(ano):
        raise ValueError("sempre")
    estado = M.trocar_e_gerar(2026, novo, destino, velho, gerar)
    assert "também não regerou" in estado and destino.read_bytes() == b"velho"
