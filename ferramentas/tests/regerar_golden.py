"""Regrava o golden de propósito: python -m tests.regerar_golden --motivo "o que mudou e por quê"."""
import argparse
import sys

import golden
import universo


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--motivo", required=True, help="por que o golden muda (vai para tests/golden_log.md)")
    motivo = ap.parse_args().motivo.strip()
    if len(motivo) < 15:
        sys.exit("motivo curto demais: explique o que mudou e por quê")
    atual = universo.instantaneo_todos()
    try:
        mud = golden.comparar(golden.carregar(), atual)
    except FileNotFoundError:
        mud = []
    golden.salvar(atual, motivo)
    print(f"golden regravado: {len(atual)} tickers, {len(mud)} mudanças. Motivo: {motivo}")
    if mud:
        print(golden.formatar(mud))


if __name__ == "__main__":
    main()
