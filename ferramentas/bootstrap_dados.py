r"""Receita de bootstrap dos dados fora do git (AUD-38 e AUD-73, auditoria de 08/10/2026).

Clone limpo:
    python -m venv .venv && .venv\Scripts\activate && pip install -r requirements.txt
    cd ferramentas && python -m pytest --ignore=backtest        # roda sem ZIPs, com os snapshots versionados
Para recalcular dos ZIPs da CVM (o que o golden de fato usa):
    python bootstrap_dados.py --baixar        # só os ZIPs que os lotes e o coletor leem (~500 MB); não sobrescreve
    python bootstrap_dados.py --verificar     # compara com dados/cvm/MANIFESTO.json (a CVM reescreve arquivos: diferença = avisar)
    python bootstrap_dados.py --derivados     # regera dados/derivados_zip.json dos ZIPs (só depois de conferir o golden)
O backtest precisa de todos os anos de DFP/ITR/FCA/FRE e do COTAHIST: `python backtest/baixar_cvm.py` (1,4 GB) e backtest/precos.
"""
from __future__ import annotations

import argparse
import sys

import manifesto_cvm
from derivados_zip import CVM

_BASE = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC"
# lote4: itr_2025/2026, dfp_2019-25, fre_2026; lote5: itr_2026; lote6: itr_2026
ESSENCIAIS = ([("dfp", a) for a in range(2016, 2027)] + [("itr", 2025), ("itr", 2026), ("fre", 2026)])


def _url(tipo: str, ano: int) -> str:
    return f"{_BASE}/{tipo.upper()}/DADOS/{tipo}_cia_aberta_{ano}.zip"


def baixar() -> int:
    import requests
    CVM.mkdir(parents=True, exist_ok=True)
    falhas = 0
    for tipo, ano in ESSENCIAIS:
        alvo = CVM / f"{tipo}_{ano}.zip"
        if alvo.exists():
            continue
        print(f"baixando {alvo.name} …", flush=True)
        try:
            r = requests.get(_url(tipo, ano), timeout=600)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"  FALHOU: {e}")
            falhas += 1
            continue
        tmp = alvo.with_suffix(".zip.novo")
        tmp.write_bytes(r.content)
        tmp.replace(alvo)
    return falhas


def derivados() -> int:
    import derivados_zip
    import lote3_agro            # noqa: F401  (P/L histórico, fatia 3)
    import lote4_saude_telecom   # noqa: F401  (o import recalcula dos ZIPs e preenche derivados_zip.CALCULADOS)
    import lote5_petroleo        # noqa: F401
    import lote6_quimica         # noqa: F401
    n = derivados_zip.gravar_snapshot()
    print(f"{n} chaves gravadas em {derivados_zip.SNAPSHOT}")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--baixar", action="store_true")
    g.add_argument("--verificar", action="store_true")
    g.add_argument("--derivados", action="store_true")
    a = ap.parse_args(argv)
    if a.baixar:
        return 1 if baixar() else 0
    if a.verificar:
        return manifesto_cvm.main(["--verificar"])
    return derivados()


if __name__ == "__main__":
    sys.exit(main())
