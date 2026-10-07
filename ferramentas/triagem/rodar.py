"""Roda a triagem de toda a B3 em T e gera o `06-triagem-e-fila.md`.

    cd ferramentas
    python -m triagem.rodar                     # T = data do mercado do hall (rf e preços do mesmo dia)
    python -m triagem.rodar --data 2026-10-05   # outro pregão (avisa se a rf for de outro dia)
    python -m triagem.rodar --sem-registro      # não grava em prospectivo/triagem.jsonl

Saídas: `06-triagem-e-fila.md` (raiz e cópia em UPLOAD CLAUDE DESKTOP/), `triagem/dados/triagem_T.csv`
(todas as linhas) e uma linha por papel da fila em `prospectivo/triagem.jsonl` (append-only).
"""
from __future__ import annotations

import argparse
import shutil
import sys
import time
from pathlib import Path

import pandas as pd

from backtest import cotahist
from backtest.precos import espinha, eventos as ev_mod, ibov as ibov_mod, proventos_b3

from . import avaliar as A
from .config import PADRAO, ConfigTriagem
from .universo import universo

RAIZ = Path(__file__).resolve().parent.parent.parent
DADOS = Path(__file__).resolve().parent / "dados"
SAIDA_06 = RAIZ / "06-triagem-e-fila.md"
UPLOAD_06 = RAIZ / "UPLOAD CLAUDE DESKTOP" / "06-triagem-e-fila.md"


def cadeias(precos: pd.DataFrame, tickers: list[str]) -> dict[str, list[str]]:
    """ticker -> códigos da mesma linhagem, do mais antigo ao atual (espinha.sucessoes)."""
    suc = espinha.sucessoes(precos, list(cotahist.pregoes()))
    pai = dict(zip(suc["novo"], suc["antigo"]))
    out = {}
    for t in tickers:
        c, r = [t], t
        while r in pai and pai[r] not in c:
            r = pai[r]
            c.insert(0, r)
        out[t] = c
    return out


def avaliar_todas(T: str, cfg: ConfigTriagem = PADRAO, log=print) -> tuple[pd.DataFrame, list[dict], float]:
    """(tabela pré-ledger, linhas avaliadas, piso). Linhas avaliadas = só as que passaram o pré-ledger."""
    t0 = time.time()
    tab, piso = universo(T, cfg)
    cand = tab[tab["motivo"] == ""].to_dict("records")
    log(f"universo {len(tab)} companhias · {len(cand)} seguem ao ledger · piso R$ {piso:,.0f}/dia")
    precos = espinha.precos_acoes()
    cad = cadeias(precos, [c["ticker"] for c in cand])
    todos = sorted({t for c in cad.values() for t in c})
    sub = precos[precos["ticker"].isin(todos)].copy()
    eventos = ev_mod.construir(sub, ibov_mod.serie(), proventos_b3.carregar_suplemento())
    cal = cotahist.calendario()
    mk = A.mercado(T, cfg)
    log(f"preços e eventos prontos ({time.time() - t0:.0f}s)")
    linhas = []
    for c in cand:
        c["cadeia"] = cad[c["ticker"]]
        linhas.append(A.avaliar(c, T, mk, sub, cal, eventos, cfg))
    log(f"{len(linhas)} avaliadas ({time.time() - t0:.0f}s)")
    return tab, linhas, piso


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", default=PADRAO.data_mercado)
    p.add_argument("--sem-registro", action="store_true")
    a = p.parse_args(argv)
    from . import fila, registro
    T = a.data
    tab, linhas, piso = avaliar_todas(T)
    r = fila.montar(tab, linhas, T, piso)
    DADOS.mkdir(exist_ok=True)
    r.tabela.to_csv(DADOS / f"triagem_{T}.csv", index=False, encoding="utf-8")
    md = fila.markdown(r)
    SAIDA_06.write_text(md, encoding="utf-8", newline="\n")
    shutil.copyfile(SAIDA_06, UPLOAD_06)
    print(f"06 gerado: fila {len(r.fila)} · financeiras {len(r.financeiras)} · deep value {len(r.netnet)}")
    if not a.sem_registro:
        n = registro.registrar(r)
        print(f"prospectivo/triagem.jsonl: {n} linhas novas")
    print("RE-UPLOAD no Claude Desktop: UPLOAD CLAUDE DESKTOP/06-triagem-e-fila.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
