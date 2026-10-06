"""Fatias 9-10 — retorno total por ticker-data de corte, nos horizontes de 1, 3 e 5 anos.

Uso: python -m backtest.precos.retorno              (gera backtest/dados/retornos.parquet)
     python -m backtest.precos.retorno --relatorio  (resumo por corte: N, status, cobertura)

DUAS METADES, E SÓ UMA OLHA O FUTURO
  · SINAL (o que se sabia em T): universo = `cotahist.universo_liquido(T)`; `preco_corte` = PREULT
    NOMINAL do último negócio do papel até o último pregão <= T. Nunca sai do índice ajustado: o
    índice retroajustado embute desdobramento e provento POSTERIORES a T (look-ahead clássico,
    multiplicativo e silencioso). `sentinela_corte` prova isto truncando o dado em T.
  · RESULTADO (T -> T+h): pode e deve usar o que aconteceu depois de T, inclusive eventos.

ÍNDICE DE RETORNO TOTAL, por LINHAGEM (sucessão de código: KROT3 -> COGN3, ver espinha.py):
    I_t = I_{t-1} x (P_t x F_t + D_t) / P_{t-1}
  F_t = produto dos fatores de evento em ações com data ex em (t-1, t]; D_t = proventos em dinheiro
  por ação ANTIGA com data ex em (t-1, t], reinvestidos no fechamento do dia ex. Proventos BRUTOS
  (`cfg.proventos_brutos`, convenção do Ibovespa); `ret_liq` desconta `cfg.jcp_ir` do JCP.
  Dia com preço <= 0 (BGIP4 2021-05-18, erro do arquivo) é tratado como dia sem negócio.

DESLISTAGEM (`cfg.regra_deslistagem = "ibov"`): a linhagem parada há mais de 10 pregões em T+h vale o
último negócio (OPA e incorporação já estão no preço — risco #11) e o valor é reinvestido no
Ibovespa até T+h. Zerar puniria a incorporação bem-sucedida; truncar o horizonte criaria
sobrevivência pela porta dos fundos. Suspensão longa que volta DEPOIS de T+h é tratada igual
(aproximação declarada: o acionista não podia vender). Vão de mais de VAO_QUEBRA pregões dentro da
linhagem é quebra de identidade (código reutilizado) e nenhuma janela o atravessa.

STATUS por linha: `ok` · `sem_fator` (evento em ações sem fator dentro de (T, T+h]: a linha fica,
sem retorno, para o relatório contar) · `horizonte_fora` (T+h depois do último pregão em disco).
"""
from __future__ import annotations

import argparse
import bisect
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from .. import cotahist
from ..calendario import Calendario, horizonte_fim
from ..config import PADRAO, Config
from . import espinha, eventos as ev_mod, ibov as ibov_mod, proventos_b3

DESTINO = Path(__file__).resolve().parent.parent / "dados" / "retornos.parquet"
JCP = "JRS CAP PROPRIO"
VAO_QUEBRA = 250    # pregões (~1 ano) sem negócio dentro da linhagem = quebra de identidade


# ----------------------------------------------------------------------------- sinal: preço em T
def preco_de_corte(precos: pd.DataFrame, ticker: str, corte: str, cal: Calendario
                   ) -> tuple[float, str]:
    """(PREULT nominal, data) do último negócio de `ticker` até o último pregão <= `corte`."""
    ate = cal.ultimo_ate(corte)
    x = precos[(precos["ticker"] == ticker) & (precos["data"] <= (ate or "")) & (precos["preult"] > 0)]
    if x.empty:
        return float("nan"), ""
    r = x.iloc[-1]
    return float(r["preult"]), str(r["data"])


def precos_de_corte(precos: pd.DataFrame, tickers, corte: str, cal: Calendario) -> pd.DataFrame:
    """Versão em lote de `preco_de_corte` (mesma regra): ticker, preco_corte, data_preco."""
    ate = cal.ultimo_ate(corte) or ""
    x = precos[precos["ticker"].isin(set(tickers)) & (precos["data"] <= ate) & (precos["preult"] > 0)]
    x = x.groupby("ticker").tail(1)
    return x[["ticker", "preult", "data"]].rename(columns={"preult": "preco_corte", "data": "data_preco"})


# ----------------------------------------------------------------------------- resultado: índice
def indices(precos: pd.DataFrame, eventos: pd.DataFrame, dinheiro: pd.DataFrame,
            linhagem: dict[str, str], cfg: Config = PADRAO, pregoes=None) -> pd.DataFrame:
    """Uma linha por (linhagem, dia com negócio): idx_total, idx_liq, idx_preco, n_sem_fator acumulado,
    contagens acumuladas de proventos e eventos."""
    d = precos[precos["preult"] > 0][["data", "ticker", "preult"]].copy()
    d["lin"] = d["ticker"].map(linhagem)
    d = d.sort_values(["lin", "data"]).drop_duplicates(["lin", "data"], keep="last").reset_index(drop=True)

    def no_dia_de_negocio(tab: pd.DataFrame) -> pd.Series:
        """Posição em `d` do 1º dia com negócio da linhagem com data >= data_ex."""
        pos = np.full(len(tab), -1)
        grupos = {k: (g.index.to_numpy(), g["data"].to_numpy()) for k, g in d.groupby("lin")}
        for j, (lin, dex) in enumerate(zip(tab["lin"], tab["data_ex"])):
            if lin not in grupos:
                continue
            idx, datas = grupos[lin]
            k = np.searchsorted(datas, dex, side="left")
            if k < len(datas):
                pos[j] = idx[k]
        return pd.Series(pos, index=tab.index)

    n = len(d)
    F = np.ones(n)
    sem = np.zeros(n)
    n_ev = np.zeros(n)
    e = eventos[eventos["fonte"] != "salto_nao_ajustado"].copy()
    e["lin"] = e["ticker"].map(linhagem)
    e = e[e["lin"].notna()]
    e["pos"] = no_dia_de_negocio(e)
    for pos, f in zip(e["pos"], e["fator"]):
        if pos < 0:
            continue
        if np.isfinite(f):
            F[pos] *= f
        else:
            sem[pos] += 1
        n_ev[pos] += 1

    D = np.zeros(n)
    Dl = np.zeros(n)
    n_pv = np.zeros(n)
    c = dinheiro.copy()
    c["lin"] = c["ticker"].map(linhagem)
    c = c[c["lin"].notna() & (c["data_ex"] != "")]
    c["pos"] = no_dia_de_negocio(c)
    ir = np.where(c["tipo"].to_numpy() == JCP, cfg.jcp_ir, 0.0)
    for pos, v, t in zip(c["pos"], c["valor_acao"], ir):
        if pos < 0:
            continue
        D[pos] += v
        Dl[pos] += v * (1 - t)
        n_pv[pos] += 1

    P = d["preult"].to_numpy()
    # Vão de mais de VAO_QUEBRA pregões sem negócio dentro da linhagem é QUEBRA: o código foi
    # reutilizado por outra coisa (NATU3 parou em 12/2019 a R$ 36,86 e voltou em 07/2025 a R$ 10,19,
    # achado do `adversario`). A razão entre os dois lados não é retorno de ninguém.
    todas = np.array(pregoes if pregoes is not None else sorted(d["data"].unique()))
    pos = np.searchsorted(todas, d["data"].to_numpy())
    mesma = (d["lin"] == d["lin"].shift(1)).to_numpy()
    vao = np.r_[0, np.diff(pos)]
    quebra = mesma & (vao > VAO_QUEBRA)
    novo = ~mesma | quebra
    P_ant = np.r_[np.nan, P[:-1]]
    r_tot = np.where(novo, 1.0, (P * F + D) / P_ant)
    r_liq = np.where(novo, 1.0, (P * F + Dl) / P_ant)
    r_pre = np.where(novo, 1.0, (P * F) / P_ant)
    grp = d["lin"].to_numpy()
    out = d[["lin", "data", "ticker", "preult"]].copy()
    out["seg"] = pd.Series(novo.astype(int)).groupby(grp).cumsum().to_numpy()
    for nome, r in (("idx_total", r_tot), ("idx_liq", r_liq), ("idx_preco", r_pre)):
        out[nome] = np.exp(pd.Series(np.log(r)).groupby(grp).cumsum().to_numpy())
    for nome, v in (("cum_sem_fator", sem), ("cum_eventos", n_ev), ("cum_proventos", n_pv)):
        out[nome] = pd.Series(v).groupby(grp).cumsum().to_numpy()
    return out


# ----------------------------------------------------------------------------- painel
def painel(idx: pd.DataFrame, universo: pd.DataFrame, precos: pd.DataFrame, cal: Calendario,
           ibov: pd.Series, linhagem: dict[str, str], cfg: Config = PADRAO) -> pd.DataFrame:
    """Uma linha por (data_corte, ticker, h)."""
    ultimo_dado = cal.pregoes[-1]
    por_lin = {k: g.reset_index(drop=True) for k, g in idx.groupby("lin")}
    linhas = []
    for corte, u in universo.groupby("data_corte"):
        pc = precos_de_corte(precos, u["ticker"], corte, cal).set_index("ticker")
        for t in u["ticker"]:
            lin = linhagem.get(t, t)
            g = por_lin.get(lin)
            base = {"data_corte": corte, "ticker": t, "linhagem": lin}
            if t not in pc.index or g is None:
                for h in cfg.horizontes_anos:
                    linhas.append({**base, "h": h, "status": "sem_preco"})
                continue
            preco, dp = pc.loc[t, "preco_corte"], pc.loc[t, "data_preco"]
            datas = g["data"].to_numpy()
            i0 = int(np.searchsorted(datas, dp, side="right")) - 1
            for h in cfg.horizontes_anos:
                fim_nom = horizonte_fim(corte, h)
                linha = {**base, "h": h, "preco_corte": preco, "data_preco": dp}
                if fim_nom > ultimo_dado:
                    linhas.append({**linha, "status": "horizonte_fora"})
                    continue
                fim = cal.ultimo_ate(fim_nom)
                i1 = int(np.searchsorted(datas, fim, side="right")) - 1
                segs = g["seg"].to_numpy()
                if segs[i1] != segs[i0]:            # janela atravessa uma quebra: vale o fim do trecho
                    i1 = i0 + int(np.searchsorted(segs[i0:], segs[i0], side="right")) - 1
                ult = datas[i1]
                # Deslistagem julgada NA JANELA (último negócio até T+h parado há mais de GAP_PREGOES),
                # não pelo último negócio da linhagem inteira — que um código reutilizado reacende.
                deslist = ult < fim and cal.quantos_entre(ult, fim) > espinha.GAP_PREGOES
                a, b = g.iloc[i0], g.iloc[i1]
                # só a deslistagem vai para o Ibov; papel parado (suspenso) em T+h fica no último preço
                fat_ibov = ibov[fim] / ibov[ult] if deslist else 1.0
                sem = b["cum_sem_fator"] - a["cum_sem_fator"]
                linha.update({
                    "data_fim": fim, "data_ultimo_negocio": ult, "deslistado": bool(deslist),
                    "ret_total": b["idx_total"] / a["idx_total"] * fat_ibov - 1,
                    "ret_liq": b["idx_liq"] / a["idx_liq"] * fat_ibov - 1,
                    "ret_preco": b["idx_preco"] / a["idx_preco"] * fat_ibov - 1,
                    "ret_ibov": ibov[fim] / ibov[dp] - 1,
                    "n_proventos": int(b["cum_proventos"] - a["cum_proventos"]),
                    "n_eventos": int(b["cum_eventos"] - a["cum_eventos"]),
                    "status": "sem_fator" if sem > 0 else "ok",
                })
                if sem > 0:
                    for k in ("ret_total", "ret_liq", "ret_preco"):
                        linha[k] = np.nan
                linhas.append(linha)
    return pd.DataFrame(linhas)


# ----------------------------------------------------------------------------- montagem
def insumos(cfg: Config = PADRAO) -> dict:
    precos = espinha.precos_acoes()
    cal = cotahist.calendario()
    pregoes = list(cal.pregoes)
    suc = espinha.sucessoes(precos, pregoes)
    lin = espinha.linhagem(precos, suc)
    ib = ibov_mod.serie()
    eventos = ev_mod.construir(precos, ib, proventos_b3.carregar_suplemento(), cfg=cfg, linhagem=lin)
    dinheiro, nao = proventos_b3.dinheiro_por_ticker(precos, pregoes, lin)
    return {"precos": precos, "cal": cal, "sucessoes": suc, "linhagem": lin, "ibov": ib,
            "eventos": eventos, "dinheiro": dinheiro, "dinheiro_nao_casado": nao,
            "universo": espinha.universo_por_corte(cfg, cal)}


def retornos(cfg: Config = PADRAO, x: dict | None = None) -> pd.DataFrame:
    x = x or insumos(cfg)
    idx = indices(x["precos"], x["eventos"], x["dinheiro"], x["linhagem"], cfg, x["cal"].pregoes)
    return painel(idx, x["universo"], x["precos"], x["cal"], x["ibov"], x["linhagem"], cfg)


# ----------------------------------------------------------------------------- sentinela
COLUNA_DATA = {"precos": "data", "eventos": "data_ex", "dinheiro": "data_ex"}


def _corte_padrao(dados: dict, tickers, corte: str, cal: Calendario) -> pd.DataFrame:
    return precos_de_corte(dados["precos"], tickers, corte, cal)


def sentinela_corte(dados: dict, cal: Calendario, corte: str, tickers, fn=None) -> pd.DataFrame:
    """Diferenças no lado do SINAL entre o dado COMPLETO e o dado TRUNCADO em T.

    `dados` = {"precos", "eventos", "dinheiro"}; cada fonte é truncada pela sua coluna de data
    (`COLUNA_DATA`). Vazio = o sinal não depende de nada posterior a T. `fn(dados, tickers, corte,
    cal)` é a porta do meta-teste, que injeta um vazamento (preço retroajustado por evento futuro)
    e exige divergência — sem isso o sentinela poderia estar comparando X com X.
    """
    fn = fn or _corte_padrao
    ate = cal.ultimo_ate(corte) or ""
    cal_t = Calendario(tuple(p for p in cal.pregoes if p <= ate))
    trunc = {k: v[v[COLUNA_DATA[k]] <= ate] for k, v in dados.items()}
    cheio = fn(dados, tickers, corte, cal).set_index("ticker")
    curto = fn(trunc, tickers, corte, cal_t).set_index("ticker")
    j = cheio.join(curto, how="outer", lsuffix="_cheio", rsuffix="_trunc")
    dif = ((j["preco_corte_cheio"] != j["preco_corte_trunc"])
           | (j["data_preco_cheio"] != j["data_preco_trunc"]))
    return j[dif]


def relatorio(r: pd.DataFrame) -> pd.DataFrame:
    return (r.pivot_table(index="data_corte", columns=["h", "status"], values="ticker",
                          aggfunc="count", fill_value=0))


def cobertura(x: dict) -> dict[str, object]:
    """Qualidade dos insumos, restrita aos papéis que estiveram no universo de algum corte."""
    u = set(x["universo"]["ticker"])
    lin = x["linhagem"]
    lins = {lin.get(t, t) for t in u}
    e = x["eventos"][x["eventos"]["ticker"].map(lambda t: lin.get(t, t)).isin(lins)]
    d = x["dinheiro"][x["dinheiro"]["ticker"].map(lambda t: lin.get(t, t)).isin(lins)]
    return {"eventos_por_fonte": e["fonte"].value_counts().to_dict(),
            "eventos_com_fonte_confere_preco": float(e[e["fonte"].isin(["fre", "b3"])]["confere_preco"].mean()),
            "proventos": int(len(d)), "proventos_conferidos": float(d["conferido"].mean()),
            "sucessoes_de_codigo": int(len(x["sucessoes"]))}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--relatorio", action="store_true")
    args = p.parse_args(argv)
    if args.relatorio and DESTINO.exists():
        r = pd.read_parquet(DESTINO)
    else:
        x = insumos()
        r = retornos(x=x)
        r.to_parquet(DESTINO, index=False)
        for k, v in cobertura(x).items():
            print(f"{k}: {v}")
    pd.set_option("display.width", 200)
    print(relatorio(r).to_string())
    ok = r[r["status"] == "ok"]
    print(f"\n{len(r)} linhas; ok {len(ok)}; deslistados {int(ok['deslistado'].sum())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
