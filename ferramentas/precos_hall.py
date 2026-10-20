"""Preço de referência do hall com data e fonte declaradas (AUD-67).

Fase 3, fatia 3 (20/10/2026): as não financeiras leem o preço com `preco(tk)` (sem literal, registrado em `insumos_a`);
as financeiras ainda digitam (`preco=` no construtor; fatia 4). TODOS são o fechamento oficial (PREULT do COTAHIST da B3) do mesmo pregão, `PRECO_DATA`. A fonte com data é o
snapshot versionado `dados/precos_hall_<data>.csv`; `tests/test_precos_hall.py` confere lote × snapshot
(sempre) e snapshot × parquet do COTAHIST (quando o parquet está no disco).

Antes da Onda 1.3 quatro preços vinham de sites de terceiros (PRIO3, VBBR3, UNIP6, UGPA3: −1,3% a +0,5%
do fechamento) e nada conferia.

    cd ferramentas && python precos_hall.py            # confere os lotes contra o snapshot (código 1 se divergir)
    cd ferramentas && python precos_hall.py --gerar    # regera o snapshot do parquet (ao trocar PRECO_DATA)
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PRECO_DATA = "2026-10-02"
PRECO_DATA_BR = "/".join(reversed(PRECO_DATA.split("-")))      # formato do golden (`data_preco`)
PRECO_FONTE = "COTAHIST_A2026.ZIP (B3), PREULT do pregão"
SNAPSHOT = AQUI / "dados" / f"precos_hall_{PRECO_DATA}.csv"
TOL = 0.005                     # meio centavo: o lote digita com 2 casas


def parquet_existe(data: str = PRECO_DATA) -> bool:
    from backtest import cotahist
    return cotahist.parquet_de(int(data[:4])).exists()


def fechamentos(tickers, data: str = PRECO_DATA) -> dict[str, float]:
    """{ticker: PREULT} exatamente no pregão `data` (falha alto se a data não for pregão)."""
    import pandas as pd
    from backtest import cotahist
    d = pd.read_parquet(cotahist.parquet_de(int(data[:4])), columns=["data", "ticker", "preult"])
    d = d[(d["data"] == data) & (d["ticker"].isin(list(tickers))) & (d["preult"] > 0)]
    if d.empty:
        raise ValueError(f"{data} não é pregão no COTAHIST (ou nenhum ticker achado)")
    return {t: float(p) for t, p in zip(d["ticker"], d["preult"])}


def ler(caminho: Path = SNAPSHOT) -> dict[str, float]:
    with caminho.open(encoding="utf-8", newline="") as f:
        linhas = list(csv.DictReader(f))
    datas = {x["data"] for x in linhas}
    if datas != {PRECO_DATA}:
        raise ValueError(f"snapshot {caminho.name} com data {datas}, esperado {PRECO_DATA}")
    return {x["ticker"]: float(x["preult"]) for x in linhas}


_SNAP: dict[str, float] = {}


def preco(tk: str) -> float:
    """Fase 3, fatia 3 (20/10/2026): o lote não digita o preço — lê o fechamento do snapshot e registra a procedência
    (`insumos_a`); literal por cima do lido fica sem registro e a nota do preço cai para C."""
    import insumos_a
    if not _SNAP:
        _SNAP.update(ler())
    return insumos_a.registrar(tk, "preco", _SNAP[tk], insumos_a.PRECO_COTAHIST)


def gerar(tickers, caminho: Path = SNAPSHOT) -> dict[str, float]:
    fech = fechamentos(tickers)
    faltam = sorted(set(tickers) - set(fech))
    if faltam:
        raise ValueError(f"sem fechamento em {PRECO_DATA}: {faltam}")
    with caminho.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["ticker", "data", "preult", "fonte"])
        for t in sorted(fech):
            w.writerow([t, PRECO_DATA, f"{fech[t]:.2f}", PRECO_FONTE])
    return fech


def divergencias(precos_lote: dict[str, float], snap: dict[str, float]) -> list[tuple[str, float, float | None]]:
    """[(ticker, preço do lote, fechamento oficial)] fora da tolerância ou sem fechamento."""
    return [(t, p, snap.get(t)) for t, p in sorted(precos_lote.items())
            if t not in snap or abs(p - snap[t]) > TOL]


def precos_dos_lotes() -> dict[str, float]:
    import universo
    return {t: float(it["empresa"].preco) for t, it in universo.avaliar_todos().items()}


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gerar", action="store_true")
    a = ap.parse_args(argv)
    lote = precos_dos_lotes()
    if a.gerar:
        gerar(lote)
        print(f"{SNAPSHOT.name}: {len(lote)} fechamentos de {PRECO_DATA}")
    div = divergencias(lote, ler())
    for t, p, s in div:
        print(f"{t}: lote {p:.2f} × fechamento {PRECO_DATA} {s if s is None else f'{s:.2f}'}")
    print(f"{len(lote)} preços; {len(div)} fora do fechamento oficial de {PRECO_DATA}")
    return 1 if div else 0


if __name__ == "__main__":
    sys.exit(main())
