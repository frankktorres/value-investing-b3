"""Identidade datada: ticker <-> CNPJ pela FCA da CVM (`valor_mobiliario`, desde 2010).

Mitiga o risco #2 do plano da Etapa 3 (mapa de identidade de 2026): o ticker é ALIAS DATADO
(`Data_Inicio/Fim_Negociacao`), não chave. Limpeza medida pelo `adversario` em 06/10/2026: a FCA
traz lixo em `Codigo_Negociacao` e datas de fim <= início — ver `mapa_ticker_cnpj`.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import pandas as pd

CVM = Path(__file__).resolve().parent.parent.parent / "dados" / "cvm"
TICKER_VALIDO = r"[A-Z0-9]{3}[A-Z]\d{1,2}[A-Z]?"


def mapa_ticker_cnpj() -> pd.DataFrame:
    """ticker, cnpj, inicio, fim (ISO; fim vazio = ainda negocia). Só ações/units/BDR da FCA."""
    partes = []
    for a in range(2010, 2027):
        f = CVM / f"fca_{a}.zip"
        if not f.exists():
            continue
        with zipfile.ZipFile(f) as z:
            d = pd.read_csv(z.open(f"fca_cia_aberta_valor_mobiliario_{a}.csv"), sep=";",
                            encoding="latin-1", dtype=str)
        partes.append(d[["CNPJ_Companhia", "Codigo_Negociacao", "Data_Inicio_Negociacao",
                         "Data_Fim_Negociacao"]].dropna(subset=["Codigo_Negociacao"]))
    m = pd.concat(partes, ignore_index=True).rename(columns={
        "CNPJ_Companhia": "cnpj", "Codigo_Negociacao": "ticker",
        "Data_Inicio_Negociacao": "inicio", "Data_Fim_Negociacao": "fim"})
    m["ticker"] = m["ticker"].str.strip().str.upper()
    m["fim"] = m["fim"].fillna("")
    # A FCA traz lixo em Codigo_Negociacao (CSN como "4030", BTG como "000000", DMMO sem classe,
    # "NÃO") e fim <= início (CEAB3: 2019-10-28 nos dois). Só vale código de bolsa; fim que não
    # vem depois do início é tratado como não informado.
    m = m[m["ticker"].str.fullmatch(TICKER_VALIDO)]
    m.loc[(m["fim"] != "") & (m["fim"] <= m["inicio"].fillna("")), "fim"] = ""
    return m.drop_duplicates().reset_index(drop=True)


def _cnpj_do_ticker_em(m: pd.DataFrame, data: str) -> dict[str, str]:
    """ticker -> cnpj vigente em `data`. Ticker sem linha vigente cai para a RAIZ (4 letras),
    desde que a raiz aponte para um único CNPJ em toda a FCA — cobre a companhia cujo ano trouxe
    lixo no código (CSNA3 = "4030" em 2022) sem casar raízes ambíguas."""
    v = m[(m["inicio"].fillna("") <= data) & ((m["fim"] == "") | (m["fim"] >= data))]
    mapa = dict(zip(v["ticker"], v["cnpj"]))
    raiz = m.assign(r=m["ticker"].str[:4]).groupby("r")["cnpj"].unique()
    raiz_unica = {r: c[0] for r, c in raiz.items() if len(c) == 1}
    return _ComRaiz(mapa, raiz_unica)


class _ComRaiz(dict):
    def __init__(self, mapa: dict[str, str], raiz: dict[str, str]):
        super().__init__(mapa)
        self.raiz = raiz

    def __missing__(self, ticker: str):
        return self.raiz.get(ticker[:4])


def tickers_do_cnpj(m: pd.DataFrame) -> dict[str, set[str]]:
    """cnpj -> todos os tickers que a FCA já atribuiu a ele (qualquer data)."""
    return m.groupby("cnpj")["ticker"].agg(set).to_dict()
