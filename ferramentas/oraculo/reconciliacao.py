"""Camada 4 — reconciliação contábil direto do DFP da CVM (docs/VALIDACAO.md §1; tolerâncias no PRE-REGISTRO-v3 §3).

Lê os ZIPs de `dados/cvm/` com um leitor próprio e mínimo, sem passar por `coletar_cvm`/`montar_series`. Se o dado do
pipeline estiver errado, este leitor não herda o erro. Do coletor só vem o mapa ticker → código CVM, que é metadado. Confere:
  bp        ativo (1) = passivo + PL (2)
  bp_partes passivo circulante + não circulante + PL (2.01 + 2.02 + 2.03) = 2
  dfc       FCO + FCI + FCF + variação cambial (6.01 … 6.04) = aumento de caixa (6.05)
  dfc_saldo saldo final − saldo inicial (6.05.02 − 6.05.01) = 6.05
  dfc_bp    saldo final da DFC = caixa do balanço (1.01.01)
  dre_dmpl  lucro consolidado da DRE (3.11) = lucro do período na DMPL (5.05.01, PL consolidado)
  div       dividendos + JCP da DMPL (5.04.*) ≈ pagos na DFC (6.03.*) — competência × caixa: só bandeira
  lpa       lucro do controlador ÷ ações da série = LPA básico (3.99.01.*) — média ponderada × fim: só bandeira
Status: ok | bandeira | falha. "falha" só acontece numa identidade contábil (bp, bp_partes, dfc, dfc_saldo) quebrada em
ticker com palavra de decisão no hall (BARATA/RADAR/JUSTA). Nos outros casos a divergência vira bandeira.
"""
from __future__ import annotations

import functools
import json
import pathlib
import re
import zipfile

import pandas as pd

AQUI = pathlib.Path(__file__).resolve().parent
FERRAMENTAS = AQUI.parent
CACHE = FERRAMENTAS / "dados" / "cvm"
HALL = FERRAMENTAS / "painel" / "web" / "dados" / "hall.json"
IDENTIDADES = ("bp", "bp_partes", "dfc", "dfc_saldo")
DECISAO = ("BARATA", "RADAR", "JUSTA")
TOL = {  # PRE-REGISTRO-v3 §3: (relativa, absoluta em R$ mil)
    "bp": (0.005, 1.0), "bp_partes": (0.005, 1.0), "dfc": (0.01, 1.0), "dfc_saldo": (0.01, 1.0), "dfc_bp": (0.01, 1.0),
    "dre_dmpl": (0.005, 1.0), "div": (0.10, 1.0), "lpa": (0.02, 0.0),
}
RE_DIV = re.compile(r"dividend|juros sobre (?:o )?capital|jcp", re.I)
DEMOS = ("BPA", "BPP", "DFC_MI", "DRE", "DMPL")
COLS = ["CD_CVM", "DENOM_CIA", "VERSAO", "ORDEM_EXERC", "ESCALA_MOEDA", "CD_CONTA", "DS_CONTA", "VL_CONTA"]


@functools.lru_cache(maxsize=None)
def _demo(ano: str, demo: str) -> pd.DataFrame | None:
    """Uma demonstração consolidada do DFP do ano, só o exercício corrente e a última versão; valores em R$ mil."""
    zp = CACHE / f"dfp_{ano}.zip"
    if not zp.is_file():
        return None
    nome = f"dfp_cia_aberta_{demo}_con_{ano}.csv"
    with zipfile.ZipFile(zp) as z:
        if nome not in z.namelist():
            return None
        usar = COLS + (["COLUNA_DF"] if demo == "DMPL" else [])
        d = pd.read_csv(z.open(nome), sep=";", encoding="latin1", dtype=str, usecols=lambda c: c in usar)
    d = d[d["ORDEM_EXERC"].str.startswith("ÚLTIMO", na=False)].copy()
    d["CD_CVM"] = d["CD_CVM"].astype(int)
    d["VERSAO"] = d["VERSAO"].astype(int)
    d = d[d["VERSAO"] == d.groupby("CD_CVM")["VERSAO"].transform("max")]
    d["VL"] = d["VL_CONTA"].astype(float)
    unid = (d["ESCALA_MOEDA"] == "UNIDADE") & ~d["CD_CONTA"].str.startswith("3.99")   # LPA é R$/ação, não escala
    d.loc[unid, "VL"] = d.loc[unid, "VL"] / 1000.0
    return d


def _codigos(ticker: str, ano: str) -> list[int]:
    from coletar_cvm import EMPRESAS
    chave = EMPRESAS[ticker][0]
    if chave.startswith("cvm:"):
        return [int(x) for x in chave[4:].split("|")]
    d = _demo(ano, "BPA")
    if d is None:
        return []
    return sorted(d.loc[d["DENOM_CIA"].str.contains(chave, regex=True, na=False), "CD_CVM"].unique().tolist())


def _contas(ticker: str, ano: str, demo: str) -> pd.DataFrame | None:
    d = _demo(ano, demo)
    if d is None:
        return None
    cods = _codigos(ticker, ano)
    sub = d[d["CD_CVM"].isin(cods)]
    if sub.empty:
        return None
    # empresa com dois códigos na história (TIMS3): no ano, vale o que publicou
    return sub[sub["CD_CVM"] == sub["CD_CVM"].iloc[0]]


def _v(df: pd.DataFrame | None, conta: str, coluna: str | None = None) -> float | None:
    if df is None:
        return None
    s = df[df["CD_CONTA"] == conta]
    if coluna is not None:
        s = s[s["COLUNA_DF"].str.contains(coluna, regex=False, na=False)]
    return float(s["VL"].iloc[0]) if len(s) else None


def _status(check: str, a: float | None, b: float | None, base: float | None = None) -> tuple[str, float | None]:
    if a is None or b is None:
        return "sem_dado", None
    rel, ab = TOL[check]
    ref = max(abs(base if base is not None else b), 1e-9)
    dif = a - b
    return ("ok" if abs(dif) <= max(rel * ref, ab) else "divergente"), dif / ref


def conferir(ticker: str, ano: str, acoes: float | None = None) -> list[dict]:
    """Checks de um (ticker, exercício). `acoes` = ações da série do pipeline (unidades) para o check do LPA."""
    bpa, bpp, dfc, dre, dmpl = (_contas(ticker, ano, x) for x in DEMOS)
    out = []

    def add(check, a, b, base=None):
        st, rel = _status(check, a, b, base)
        out.append(dict(ticker=ticker, ano=ano, check=check, calculado=a, esperado=b, dif_rel=rel, status=st))

    ativo, passivo = _v(bpa, "1"), _v(bpp, "2")
    add("bp", ativo, passivo, ativo)
    partes = [_v(bpp, c) for c in ("2.01", "2.02", "2.03")]
    add("bp_partes", sum(partes) if None not in partes else None, passivo)
    fl = [_v(dfc, c) for c in ("6.01", "6.02", "6.03")]
    camb = _v(dfc, "6.04") or 0.0       # a linha de variação cambial só existe em quem tem caixa em moeda estrangeira
    var, ini, fim = _v(dfc, "6.05"), _v(dfc, "6.05.01"), _v(dfc, "6.05.02")
    add("dfc", sum(fl) + camb if None not in fl else None, var, fim)
    add("dfc_saldo", fim - ini if None not in (fim, ini) else None, var, fim)
    add("dfc_bp", fim, _v(bpa, "1.01.01"))
    add("dre_dmpl", _v(dre, "3.11"), _v(dmpl, "5.05.01", "Consolidado"))
    if dmpl is not None and dfc is not None:
        d_dmpl = dmpl[dmpl["CD_CONTA"].str.startswith("5.04.") & dmpl["DS_CONTA"].str.contains(RE_DIV, na=False)
                      & dmpl["COLUNA_DF"].str.contains("Consolidado", regex=False, na=False)]["VL"].sum()
        d_dfc = dfc[dfc["CD_CONTA"].str.fullmatch(r"6\.03\.\d+") & dfc["DS_CONTA"].str.contains(RE_DIV, na=False)]["VL"].sum()
        add("div", abs(d_dmpl), abs(d_dfc))
    lucro_c = _v(dre, "3.11.01") or _v(dre, "3.11")     # AUD-68: há quem publique a linha do controlador zerada
    lpa = None
    if dre is not None:
        s = dre[dre["CD_CONTA"].str.startswith("3.99.01.") & (dre["VL"] != 0)]
        lpa = float(s["VL"].iloc[0]) if len(s) else None
    calc = lucro_c * 1000 / acoes if (lucro_c is not None and acoes) else None
    if calc is not None and lpa and abs(calc / lpa / 1000 - 1) < 0.05:
        # série com ações em MILHARES (a de outros tickers está em unidades): bandeira própria, não divergência de LPA
        out.append(dict(ticker=ticker, ano=ano, check="acoes_escala", calculado=calc, esperado=lpa, dif_rel=calc / lpa - 1,
                        status="divergente"))
    else:
        add("lpa", calc, lpa)
    return out


def _palavras() -> dict[str, str]:
    if not HALL.is_file():
        return {}
    return {e["tk"]: e.get("palavra") for e in json.loads(HALL.read_text(encoding="utf-8"))["empresas"]}


def classificar(linhas: list[dict], palavras: dict[str, str] | None = None) -> list[dict]:
    """divergente → falha (identidade contábil em ticker com palavra de decisão) ou bandeira (o resto)."""
    palavras = _palavras() if palavras is None else palavras
    for r in linhas:
        if r["status"] == "divergente":
            r["status"] = ("falha" if r["check"] in IDENTIDADES and palavras.get(r["ticker"]) in DECISAO else "bandeira")
    return linhas


def rodar(tickers: list[str] | None = None, anos: list[str] | None = None) -> list[dict]:
    from coletar_cvm import EMPRESAS
    import motor_nao_financeiras as M
    tickers = tickers or sorted(EMPRESAS)
    anos = anos or [str(a) for a in range(2016, 2026)]
    linhas = []
    for tk in tickers:
        serie = (M.CVM.get(tk) or {}).get("anual", {})
        for ano in anos:
            linhas += conferir(tk, ano, (serie.get(ano) or {}).get("acoes"))
    return classificar(linhas)
