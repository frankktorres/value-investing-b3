"""Coleta a série mensal do IPCA (BCB, SGS 433) para dados/macro/ipca_mensal.json.

Fonte nota A: api.bcb.gov.br/dados/serie/bcdata.sgs.433 — IPCA, variação mensal em %, desde 01/01/1980
(conferido em 05/10/2026). O SGS limita o intervalo por requisição, então a série vem em blocos de 10 anos.

A série anterior começava em 01/2015, o que limitava a 11,6 anos a correção do imobilizado a custo de reposição
(doutrina §11.1, ROIC a reposição) — por isso a extensão. O arquivo substituído vai para `_historico/`.

Uso: python coletar_macro.py [--ate 31/08/2026]
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from datetime import date

import requests

H = {"User-Agent": "Mozilla/5.0"}


def _get(url: str, tentativas: int = 5):
    """O SGS devolve 502 intermitente; repete com espera crescente antes de desistir."""
    erro = "sem tentativa"
    for i in range(tentativas):
        try:
            r = requests.get(url, headers=H, timeout=60)
            if r.status_code == 200:
                return r
            erro = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            erro = str(e)
        time.sleep(2 * (i + 1))
    raise RuntimeError(f"{erro} em {url}")

AQUI = pathlib.Path(__file__).parent
DESTINO = AQUI / "dados" / "macro" / "ipca_mensal.json"
SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados?formato=json&dataInicial={ini}&dataFinal={fim}"
INICIO = 1980


def baixar(serie: int, ini_ano: int, fim: str) -> list[dict]:
    """Blocos de 10 anos (limite do SGS), concatenados na ordem cronológica, sem repetir mês."""
    fim_ano = int(fim.split("/")[-1])
    vistos, saida = set(), []
    for a in range(ini_ano, fim_ano + 1, 10):
        b = min(a + 9, fim_ano)
        url = SGS.format(serie=serie, ini=f"01/01/{a}", fim=f"31/12/{b}" if b < fim_ano else fim)
        for reg in _get(url).json():
            if reg["data"] not in vistos:
                vistos.add(reg["data"])
                saida.append({"data": reg["data"], "valor": reg["valor"]})
    saida.sort(key=lambda reg: tuple(int(x) for x in reg["data"].split("/")[::-1]))
    return saida


def conferir_sobreposicao(nova: list[dict], antiga: list[dict]) -> list[str]:
    """A parte comum tem de bater valor a valor — se divergir, o golden mudaria pelo motivo errado."""
    n = {reg["data"]: reg["valor"] for reg in nova}
    return [f"{reg['data']}: antigo {reg['valor']} × novo {n.get(reg['data'], 'ausente')}"
            for reg in antiga if n.get(reg["data"]) != reg["valor"]]


def main() -> int:
    fim = sys.argv[sys.argv.index("--ate") + 1] if "--ate" in sys.argv else date.today().strftime("%d/%m/%Y")
    antiga = json.loads(DESTINO.read_text(encoding="utf-8")) if DESTINO.exists() else []
    nova = baixar(433, INICIO, fim)
    print(f"IPCA (SGS 433): {len(nova)} meses, {nova[0]['data']} a {nova[-1]['data']}")
    if antiga:
        div = conferir_sobreposicao(nova, antiga)
        print(f"série anterior: {len(antiga)} meses desde {antiga[0]['data']}")
        if div:
            print("DIVERGÊNCIA na parte comum — nada foi gravado:")
            print("\n".join(div[:20]))
            return 1
        print("parte comum confere valor a valor")
    DESTINO.write_text(json.dumps(nova, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"gravado em {DESTINO}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
