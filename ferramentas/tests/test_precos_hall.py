"""AUD-67: todo preço digitado num lote é o fechamento oficial (PREULT do COTAHIST) da data declarada, e o
snapshot versionado com data e fonte é igual ao COTAHIST."""
from __future__ import annotations

import pytest

import precos_hall as PH
import universo


@pytest.fixture(scope="module")
def todos():
    return universo.avaliar_todos()


def test_todo_preco_do_lote_e_o_fechamento_oficial(todos):
    snap = PH.ler()
    div = PH.divergencias({t: float(it["empresa"].preco) for t, it in todos.items()}, snap)
    assert not div, f"preço do lote fora do fechamento de {PH.PRECO_DATA}: {div}"


def test_data_do_preco_vem_do_snapshot_nao_da_taxa(todos):
    assert PH.PRECO_DATA_BR == "02/10/2026"
    assert {it["data_preco"] for it in todos.values()} == {PH.PRECO_DATA_BR}
    assert all(it["data_preco"] is PH.PRECO_DATA_BR for it in todos.values())    # vem do snapshot, não do MK
    assert PH.SNAPSHOT.name.endswith(f"{PH.PRECO_DATA}.csv")


def test_snapshot_tem_data_e_fonte_em_toda_linha():
    import csv
    with PH.SNAPSHOT.open(encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    assert linhas and all(x["data"] == PH.PRECO_DATA and x["fonte"] == PH.PRECO_FONTE for x in linhas)


def test_divergencia_aponta_o_ticker():
    assert PH.divergencias({"AAAA3": 10.0, "BBBB3": 5.0}, {"AAAA3": 10.004}) == [("BBBB3", 5.0, None)]
    assert PH.divergencias({"AAAA3": 10.01}, {"AAAA3": 10.0}) == [("AAAA3", 10.01, 10.0)]


@pytest.mark.skipif(not PH.parquet_existe(), reason="COTAHIST do ano do preço fora do disco")
def test_snapshot_igual_ao_cotahist():
    snap = PH.ler()
    fech = PH.fechamentos(snap)
    assert set(fech) == set(snap)
    assert all(abs(fech[t] - snap[t]) < 1e-6 for t in snap), {t: (snap[t], fech[t]) for t in snap
                                                               if abs(fech[t] - snap[t]) >= 1e-6}
