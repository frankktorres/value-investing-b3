"""python -m relatorio TICKER [--data AAAA-MM-DD] → RELATORIOS/<TK>-<data>.pdf (+ .md e .json).
python -m relatorio CARTEIRA → RELATORIOS/privado/CARTEIRA-<pregão>.md e .pdf (painel da carteira e da meta + histórico em dados/privado/renda.jsonl; ver carteira.py)."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
from dataclasses import asdict

from relatorio import render_md, render_pdf
from relatorio.montar import montar

SAIDA = pathlib.Path(__file__).resolve().parents[2] / "RELATORIOS"


def gravar(rel, pasta: pathlib.Path = SAIDA) -> list[pathlib.Path]:
    pasta.mkdir(exist_ok=True)
    md = pasta / f"{rel.tk}-{rel.data}.md"
    md.write_text(render_md.render(rel), encoding="utf-8")
    js = pasta / f"{rel.tk}-{rel.data}.json"
    js.write_text(json.dumps(_sem_inf(asdict(rel)), ensure_ascii=False, indent=1), encoding="utf-8")   # inf → null
    pdf = render_pdf.render(rel, pasta / f"{rel.tk}-{rel.data}.pdf")
    return [md, js, pdf]


def _sem_inf(x):
    if isinstance(x, float) and (x != x or abs(x) == float("inf")):
        return None
    if isinstance(x, dict):
        return {k: _sem_inf(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_sem_inf(v) for v in x]
    return x


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="relatório por empresa (vista dos motores; não grava veredito)")
    ap.add_argument("ticker")
    ap.add_argument("--data", help="data-base AAAA-MM-DD (só ticker com ficha de dossiê)")
    a = ap.parse_args(argv)
    if a.ticker.upper() == "CARTEIRA":                       # painel da carteira e da meta (dado pessoal, fora do git)
        from relatorio import carteira
        try:
            rel = carteira.carregar()
            for p in carteira.painel(rel):
                print(p)
        except (KeyError, ValueError, FileNotFoundError, PermissionError) as ex:
            print(f"ERRO: {ex}", file=sys.stderr)
            return 2
        print("CARTEIRA" + (f" · {len(rel.avisos)} aviso(s)" if rel.avisos else ""))
        return 0
    try:
        rel = montar(a.ticker, a.data)
    except (KeyError, ValueError, FileNotFoundError) as ex:
        print(f"ERRO: {ex}", file=sys.stderr)
        return 2
    for p in gravar(rel):
        print(p)
    print(f"{rel.tk}: {rel.palavra}" + (f" · {len(rel.avisos)} aviso(s)" if rel.avisos else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
