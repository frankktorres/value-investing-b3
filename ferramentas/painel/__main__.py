"""python -m painel [--exportar] [--porta N] [--sem-abrir] → tela em http://127.0.0.1:8765/ (somente leitura).

--exportar regera web/dados/ a partir dos motores antes de abrir (~minutos; ver exportar.py)."""
from __future__ import annotations

import argparse
import sys

from painel import contrato, exportar, servir


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="painel web local, somente leitura")
    ap.add_argument("--exportar", action="store_true", help="regera os dados a partir dos motores antes de abrir")
    ap.add_argument("--porta", type=int, default=servir.PORTA)
    ap.add_argument("--sem-abrir", action="store_true", help="não abre o navegador")
    a = ap.parse_args(argv)
    if a.exportar:
        exportar.main([])
        try:                                                # contrato da tela v0.2 (web/dados/contrato/)
            contrato.main([])
        except Exception as ex:                             # noqa: BLE001 — a tela sobe com a última leitura válida
            print(f"contrato v0.2 não gerado: {type(ex).__name__}: {ex}", file=sys.stderr)
    elif not (exportar.DADOS / "hall.json").exists():
        print("Sem dados ainda: rode `python -m painel --exportar` (ou `painel --exportar` na raiz).", file=sys.stderr)
    servir.servir(a.porta, abrir=not a.sem_abrir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
