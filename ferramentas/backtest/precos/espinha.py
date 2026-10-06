"""Espinha de preços do backtest: as ações do COTAHIST 2014-2026 e o universo de cada corte.

Universo de um corte T = `cotahist.universo_liquido(T)` (só ações/units, liquidez em R$ reais do
mês-âncora). É a decisão do Frank de 06/10/2026: quem negociou com liquidez na janela até T
existia em T, e o arquivo da B3 é imutável — sem viés de sobrevivência por construção.

Os preços aqui são NOMINAIS, como a B3 publicou no dia (PREULT/100/FATCOT): nenhum ajuste por
provento ou evento. O ajuste vive em `retorno.py`, e só no lado do RESULTADO (T -> T+h). O preço
que entra no sinal (P/C em T) é sempre o nominal do último pregão <= T.
"""
from __future__ import annotations

from functools import lru_cache

import pandas as pd

from .. import cotahist
from ..config import PADRAO, Config
from ..ledger.identidade import _cnpj_do_ticker_em, mapa_ticker_cnpj

COLUNAS = ["data", "ticker", "codbdi", "nomres", "especi", "codisi", "preult", "totneg", "voltot"]


@lru_cache(maxsize=1)
def _precos_cache(anos: tuple[int, ...]) -> pd.DataFrame:
    partes = [pd.read_parquet(cotahist.parquet_de(a), columns=COLUNAS) for a in anos
              if cotahist.parquet_de(a).exists()]
    d = cotahist.so_acoes(pd.concat(partes, ignore_index=True))
    return d.sort_values(["ticker", "data"], ignore_index=True)


def precos_acoes(anos: range | None = None) -> pd.DataFrame:
    """Todas as linhas de ações/units do COTAHIST nos anos dados, por (ticker, data). Cópia."""
    anos = anos or range(cotahist.PRIMEIRO, cotahist.ULTIMO + 1)
    return _precos_cache(tuple(anos)).copy()


def universo_por_corte(cfg: Config = PADRAO, cal=None) -> pd.DataFrame:
    """(data_corte, ticker, liquidez) para os cortes de `cfg`."""
    cal = cal or cotahist.calendario()
    linhas = []
    for d in cfg.datas_corte:
        u = cotahist.universo_liquido(d, cfg=cfg, cal=cal)
        linhas.append(pd.DataFrame({"data_corte": d, "ticker": u.index, "liquidez": u.values}))
    return pd.concat(linhas, ignore_index=True)


# ----------------------------------------------------------------------------- sucessão de código
# O ISIN MUDA junto com o código de negociação (DTEX3 BRDTEXACNOR3 -> DXCO3 BRDXCOACNOR8; KROT3 ->
# COGN3; CCRO3 -> MOTV3; TRPL4 -> ISAE4; ELET3 -> AXIA3; BVMF3 -> B3SA3), então seguir o papel pelo
# ISIN trataria cada troca de nome como deslistagem. Sucessão = mesmo CNPJ na FCA, mesmo sufixo de
# classe, o novo começa até `GAP_PREGOES` depois do último negócio do antigo, e o preço é contínuo
# (|log(P_novo/P_antigo)| <= `SALTO_SUCESSAO`). Incorporação com relação de troca (LAME4 -> AMER3)
# não passa no teste de preço nem de classe: fica como deslistagem, que é o tratamento declarado.
GAP_PREGOES = 10
SALTO_SUCESSAO = 0.15
SALTO_SEM_CNPJ = 0.05


def sucessoes(precos: pd.DataFrame, pregoes: list[str]) -> pd.DataFrame:
    """(antigo, novo, ultimo_antigo, primeiro_novo, cnpj)."""
    import bisect
    import numpy as np
    d = precos[precos["preult"] > 0]
    ext = d.groupby("ticker").agg(ini=("data", "min"), fim=("data", "max"))
    p_ini = d.groupby("ticker")["preult"].first()
    p_fim = d.groupby("ticker")["preult"].last()
    m = mapa_ticker_cnpj()
    linhas = []
    acabam = ext[ext["fim"] < pregoes[max(0, len(pregoes) - 1 - GAP_PREGOES)]]
    comecam = ext[ext["ini"] > pregoes[0]]
    for a, ra in acabam.iterrows():
        i = bisect.bisect_right(pregoes, ra["fim"])
        limite = pregoes[min(len(pregoes) - 1, i + GAP_PREGOES - 1)]
        cand = comecam[(comecam["ini"] > ra["fim"]) & (comecam["ini"] <= limite)]
        cand = cand[[t[4:] == a[4:] for t in cand.index]]
        if cand.empty:
            continue
        cnpj_a = _cnpj_do_ticker_em(m, ra["fim"])[a]
        for b, rb in cand.iterrows():
            cnpj_b = _cnpj_do_ticker_em(m, rb["ini"])[b]
            salto = abs(np.log(p_ini[b] / p_fim[a]))
            if cnpj_a and cnpj_b:
                if cnpj_a != cnpj_b or salto > SALTO_SUCESSAO:
                    continue
                prova = "cnpj"
            else:
                # A FCA reescreve o passado com o código atual (COGN3 "desde 2012"; KROT3 some),
                # então um lado pode não ter CNPJ. Sem CNPJ a prova é mais estrita: troca no
                # pregão seguinte e preço contínuo a ±5%.
                seguinte = pregoes[i] if i < len(pregoes) else ""
                if rb["ini"] != seguinte or salto > SALTO_SEM_CNPJ:
                    continue
                prova = "preco"
            linhas.append({"antigo": a, "novo": b, "ultimo_antigo": ra["fim"],
                           "primeiro_novo": rb["ini"], "cnpj": cnpj_a or cnpj_b or "", "prova": prova})
    return pd.DataFrame(linhas, columns=["antigo", "novo", "ultimo_antigo", "primeiro_novo", "cnpj",
                                         "prova"])


def linhagem(precos: pd.DataFrame, suc: pd.DataFrame) -> dict[str, str]:
    """ticker -> id da linhagem (o ticker mais antigo da cadeia de sucessões)."""
    pai = dict(zip(suc["novo"], suc["antigo"]))
    out = {}
    for t in precos["ticker"].unique():
        r, vistos = t, set()
        while r in pai and r not in vistos:
            vistos.add(r)
            r = pai[r]
        out[t] = r
    return out
