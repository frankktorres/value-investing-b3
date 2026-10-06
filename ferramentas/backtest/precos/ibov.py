"""Fatia 9 — Ibovespa diário (B3, fonte A), benchmark e destino da regra de deslistagem.

Uso: python -m backtest.precos.ibov   (baixa 2014-hoje para backtest/dados/ibov.parquet)

O Ibovespa é índice de RETORNO TOTAL (a B3 reinveste os proventos na carteira teórica), por isso é
o benchmark certo contra o retorno total das ações — comparar com retorno só de preço puniria a
ação pagadora de dividendo, justamente o perfil da BARATA (risco #10 do plano da Etapa 3).

FONTE: B3 `indexStatisticsProxy/IndexCall/GetPortfolioDay/{base64 {"index":"IBOV","year":...}}`,
uma tabela dia x mês de fechamentos por ano, com 2 casas. O SGS 7 do BCB, que seria o natural,
deixou de ser publicado (HTTP 404 em qualquer intervalo de 2022 em diante, conferido em 06/10/2026).
A API devolve corpo vazio intermitente → retry com espera crescente.
"""
from __future__ import annotations

import base64
import json
import sys
import time
from datetime import date
from pathlib import Path

import pandas as pd
import requests

ARQUIVO = Path(__file__).resolve().parent.parent / "dados" / "ibov.parquet"
URL = "https://sistemaswebb3-listados.b3.com.br/indexStatisticsProxy/IndexCall/GetPortfolioDay/"
INICIO = 2013


def _ano(ano: int) -> list[tuple[str, float]]:
    payload = base64.b64encode(json.dumps(
        {"language": "pt-br", "index": "IBOV", "year": str(ano)}).encode()).decode()
    erro = ""
    for i in range(5):
        try:
            r = requests.get(URL + payload, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
            if r.status_code == 200 and r.text.strip():
                j = r.json()
                if "results" in j:
                    out = []
                    for linha in j["results"]:
                        for m in range(1, 13):
                            v = linha.get(f"rateValue{m}")
                            if v:
                                out.append((f"{ano}-{m:02d}-{int(linha['day']):02d}",
                                            float(v.replace(".", "").replace(",", "."))))
                    return out
            erro = f"HTTP {r.status_code} {r.text[:80]!r}"
        except (requests.RequestException, ValueError) as e:
            erro = repr(e)[:120]
        time.sleep(2 ** (i + 1))
    raise RuntimeError(f"IBOV {ano}: {erro}")


def baixar() -> pd.DataFrame:
    partes = []
    for a in range(INICIO, date.today().year + 1):
        partes += _ano(a)
    d = pd.DataFrame(partes, columns=["data", "ibov"])
    d = d.drop_duplicates("data").sort_values("data", ignore_index=True)
    if (d["ibov"] <= 0).any():
        raise ValueError("Ibovespa com valor não positivo")
    ARQUIVO.parent.mkdir(parents=True, exist_ok=True)
    d.to_parquet(ARQUIVO, index=False)
    return d


def serie() -> pd.Series:
    """Ibovespa por data ISO."""
    d = pd.read_parquet(ARQUIVO)
    return d.set_index("data")["ibov"]


if __name__ == "__main__":
    d = baixar()
    print(f"Ibovespa (B3): {len(d)} pregões, {d['data'].iloc[0]} a {d['data'].iloc[-1]}")
    sys.exit(0)
