"""Erro do proxy (motor reduzido) contra a régua completa — a base do corte de preço da fila (AUD-33).

Medido UMA vez, em 06/10/2026 (Etapa 3, `backtest/experimento/proxy.py`; o portão do proxy reprovou). O JSON da
consulta fica em `backtest/dados/`, que o git ignora; a evidência que o corte usa é extraída para
`triagem/dados/erro_proxy_2026-10-06.csv` (versionado) e não muda depois — mudar o corte exige outra consulta
declarada, nunca reescrever este arquivo.

O corte usa a **razão** proxy ÷ golden (o erro de um central é proporcional: WEGE3 4,32 → 7,11 é +2,8 de P/C mas
1,65×), só nos papéis em que o proxy é **confiável** pela mesma regra da triagem (central > 0, toda âncora > 0,
dispersão ≤ 3) — os únicos que o corte atinge. Corte = 1,10 × a MAIOR superestimação medida: mesmo com o pior erro
observado, quem fica acima dele estaria acima de 1,10 (CARA). Amostra pequena (30 papéis, quase todos CARA).

    cd ferramentas && python -m triagem.erro_proxy     # mostra a razão máxima e quem a define
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

AQUI = Path(__file__).resolve().parent
EVIDENCIA = AQUI / "dados" / "erro_proxy_2026-10-06.csv"
ORIGEM = AQUI.parent / "backtest" / "dados" / "proxy_2026-10-05.json"
CAMPOS = ("ticker", "golden_pc", "proxy_pc", "proxy_dispersao", "confiavel", "razao")


def _finito_pos(x) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x) and x > 0


def extrair(origem: Path = ORIGEM, destino: Path = EVIDENCIA, disp_max: float = 3.0) -> list[dict]:
    """Uma linha por ticker da consulta; `confiavel` pela regra da triagem (avaliar.py)."""
    linhas = json.loads(origem.read_text(encoding="utf-8"))["linhas"]
    out = []
    for l in linhas:
        anc = list((l.get("proxy_ancoras") or {}).values())
        conf = (_finito_pos(l.get("proxy_central")) and bool(anc) and all(_finito_pos(a) for a in anc)
                and l.get("proxy_dispersao") is not None and l["proxy_dispersao"] <= disp_max
                and _finito_pos(l.get("golden_pc")) and _finito_pos(l.get("proxy_pc")))
        out.append(dict(ticker=l["ticker"], golden_pc=l.get("golden_pc"), proxy_pc=l.get("proxy_pc"),
                        proxy_dispersao=l.get("proxy_dispersao"), confiavel=conf,
                        razao=l["proxy_pc"] / l["golden_pc"] if conf else None))
    with destino.open("w", encoding="utf-8", newline="\n") as f:
        w = csv.DictWriter(f, fieldnames=CAMPOS, lineterminator="\n")
        w.writeheader()
        for x in sorted(out, key=lambda x: x["ticker"]):
            w.writerow({k: ("" if x[k] is None else round(x[k], 6) if isinstance(x[k], float) else x[k])
                        for k in CAMPOS})
    return out


def ler(caminho: Path = EVIDENCIA) -> list[dict]:
    with caminho.open(encoding="utf-8", newline="") as f:
        return [dict(x, confiavel=x["confiavel"] == "True", razao=float(x["razao"]) if x["razao"] else None,
                     golden_pc=float(x["golden_pc"]) if x["golden_pc"] else None)
                for x in csv.DictReader(f)]


def razao_maxima(caminho: Path = EVIDENCIA) -> float:
    """Maior superestimação do P/C pelo proxy entre os confiáveis, a 4 casas (entra no hash da config).
    Medida contra o golden de 06/10 (régua v2.2), o que a consulta registrou."""
    return round(max(x["razao"] for x in ler(caminho) if x["confiavel"]), 4)


GOLDEN = AQUI.parent / "tests" / "golden.json"


def razao_maxima_vigente(golden: Path = GOLDEN, caminho: Path = EVIDENCIA) -> float:
    """O mesmo proxy contra o golden VIGENTE (a régua mudou depois da medição: Ondas 1.1 e 1.2). Informativo: o corte
    fica com o maior dos dois (corta menos); um teste falha se a régua vigente passar a dar razão maior que a medida."""
    g = json.loads(golden.read_text(encoding="utf-8"))["tickers"]
    return round(max(x["razao"] * x["golden_pc"] / g[x["ticker"]]["pc"]
                     for x in ler(caminho) if x["confiavel"] and _finito_pos(g[x["ticker"]]["pc"])), 4)


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    ev = [x for x in ler() if x["confiavel"]]
    for x in sorted(ev, key=lambda x: -x["razao"])[:5]:
        print(f"{x['ticker']:7} golden {x['golden_pc']:.2f} → proxy ×{x['razao']:.3f}")
    print(f"{len(ev)} confiáveis · razão máxima {razao_maxima():.4f}")
