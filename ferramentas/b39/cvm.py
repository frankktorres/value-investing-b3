"""B39 — balanços da CVM por companhia, direto dos ZIPs locais (DFP 2015–2025, ITR 2025–2026). Não toca os parquets do backtest.

Reusa a leitura testada do ledger: `backtest.ledger.fatos_cvm.fatos_de_zip` (escala, planos, descrição) e
`backtest.ledger.pit._contas_de` (consolidado → individual; banco por DESCRIÇÃO; arrendamento sem dupla contagem).
O cache `b39/dados/fatos_b39.parquet` (fora do git) é derivado e reconstruível.
"""
from __future__ import annotations

import io
import re
import zipfile
from functools import lru_cache
from pathlib import Path

import pandas as pd

from backtest.ledger import identidade
from backtest.ledger.fatos_cvm import CACHE, fatos_de_zip
from backtest.ledger.pit import FINANCEIRO, INDUSTRIAL, _contas_de, _folhas
from backtest.motor.base import lucro_controlador
from backtest.motor.reduzido_fin import _pl_controlador

AQUI = Path(__file__).resolve().parent
FATOS = AQUI / "dados" / "fatos_b39.parquet"
ANOS_DFP = range(2015, 2026)
ANOS_ITR = (2025, 2026)
RE_DIV = re.compile(r"dividend|juros sobre (?:o )?capital|\bjcp\b", re.I)
# Plano de banco desde 2023 (Res. CMN 4.966): "Lucro ou Prejuízo Líquido Consolidado do Período" (3.11) e "Atribuído AOS Sócios da
# Empresa Controladora" (3.11.01). As regex de `fatos_cvm.POR_DESCRICAO` só casam o plano antigo ("Lucro/Prejuízo…", "a Sócios"):
# lucro de BB e Bradesco saía vazio de 2023 em diante. Aqui a leitura é mais larga, só para o plano financeiro.
RE_LC_FIN = re.compile(r"^atribu[íi]d[oa]s? (?:a|aos) s[óo]cios d[ae] (?:empresa )?controladora", re.I)
RE_L_FIN = re.compile(r"^lucro(?: ou |/| )?preju[íi]zo (?:l[íi]quido )?(?:consolidado )?d[oa] (?:per[íi]odo|exerc[íi]cio)", re.I)


# ------------------------------------------------------------------------------------------------ identidade
@lru_cache(maxsize=1)
def _mapa():
    return identidade.mapa_ticker_cnpj()


def cnpj_de(ticker: str, data: str) -> str | None:
    return identidade._cnpj_do_ticker_em(_mapa(), data)[ticker]


@lru_cache(maxsize=1)
def tickers_por_cnpj() -> dict[str, set[str]]:
    return identidade.tickers_do_cnpj(_mapa())


def _csv(z: zipfile.ZipFile, fim: str) -> pd.DataFrame:
    nome = [n for n in z.namelist() if n.lower().endswith(fim.lower())][0]
    return pd.read_csv(io.BytesIO(z.read(nome)), sep=";", encoding="latin-1", dtype=str)


@lru_cache(maxsize=4)
def indice_docs(categ: str, ano: int) -> pd.DataFrame:
    """CNPJ, CD_CVM, DT_REFER, VERSAO, DT_RECEB do arquivo-índice do ZIP (quem entregou o quê e quando)."""
    with zipfile.ZipFile(CACHE / f"{categ}_{ano}.zip") as z:
        d = _csv(z, f"{categ}_cia_aberta_{ano}.csv")
    d["CD_CVM"] = pd.to_numeric(d["CD_CVM"]).astype(int)
    d["VERSAO"] = pd.to_numeric(d["VERSAO"]).astype(int)
    return d[["CNPJ_CIA", "CD_CVM", "DT_REFER", "VERSAO", "DT_RECEB"]]


# Tickers que a FCA não liga ao CNPJ em T (código novo ou lixo na FCA). Código CVM de `holdout_b36/cadastro.json` (BPAC11, MBRF3,
# CSNA3) e de `coletar_cvm.EMPRESAS` (CMIN3); o CNPJ sai do índice da própria CVM.
IDENTIDADE_MANUAL = {"BPAC11": 22616, "MBRF3": 20788, "CSNA3": 4030, "CMIN3": 25585}


def identificar(ticker: str, data: str) -> tuple[str | None, int | None, str]:
    """(cnpj, cd_cvm, origem)."""
    if ticker in IDENTIDADE_MANUAL:
        cd = IDENTIDADE_MANUAL[ticker]
        for categ, ano in (("itr", 2026), ("dfp", 2025)):
            d = indice_docs(categ, ano)
            x = d[d["CD_CVM"] == cd]
            if len(x):
                return str(x["CNPJ_CIA"].iloc[0]), cd, "manual (cadastro da B36 / coletar_cvm)"
        return None, cd, "manual sem documento"
    cn = cnpj_de(ticker, data)
    return cn, (cd_cvm_de(cn) if cn else None), "FCA"


def cd_cvm_de(cnpj: str) -> int | None:
    for categ, ano in (("itr", 2026), ("dfp", 2025), ("dfp", 2024)):
        d = indice_docs(categ, ano)
        x = d[d["CNPJ_CIA"] == cnpj]
        if len(x):
            return int(x["CD_CVM"].iloc[0])
    return None


@lru_cache(maxsize=2)
def composicao(ano: int) -> pd.DataFrame:
    with zipfile.ZipFile(CACHE / f"itr_{ano}.zip") as z:
        d = _csv(z, f"itr_cia_aberta_composicao_capital_{ano}.csv")
    for c in d.columns:
        if c.startswith("QT_"):
            d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0.0)
    return d


def acoes_por_classe(cnpj: str, dt_refer: str) -> dict | None:
    """Ações ON e PN sem tesouraria da composição do capital do ITR `dt_refer` (todas as classes)."""
    d = composicao(int(dt_refer[:4]))
    x = d[(d["CNPJ_CIA"] == cnpj) & (d["DT_REFER"] == dt_refer)]
    if x.empty:
        return None
    r = x.sort_values("VERSAO").iloc[-1]
    return {"on": float(r["QT_ACAO_ORDIN_CAP_INTEGR"] - r["QT_ACAO_ORDIN_TESOURO"]),
            "pn": float(r["QT_ACAO_PREF_CAP_INTEGR"] - r["QT_ACAO_PREF_TESOURO"])}


# ------------------------------------------------------------------------------------------------ fatos
def construir(cds: set[int]) -> pd.DataFrame:
    partes = []
    for categ, anos in (("dfp", ANOS_DFP), ("itr", ANOS_ITR)):
        for a in anos:
            f = fatos_de_zip(categ, a)
            if not f.empty:
                partes.append(f[f["cd_cvm"].isin(cds)])
                print(f"  {categ}_{a}: ok", flush=True)
    out = pd.concat(partes, ignore_index=True)
    FATOS.parent.mkdir(exist_ok=True)
    out.to_parquet(FATOS, index=False)
    return out


def fatos(cds: set[int]) -> pd.DataFrame:
    if FATOS.exists():
        f = pd.read_parquet(FATOS)
        if cds <= set(f["cd_cvm"].astype(int).unique()):
            return f
    return construir(cds)


def _do_zip_proprio(g: pd.DataFrame, categ: str) -> pd.DataFrame:
    """Cada exercício lido do ZIP do próprio ano (a versão mais recente lá), não do comparativo do ano seguinte."""
    g = g[(g["categ"] == categ) & (g["dt_refer"].str[:4].astype(int) == g["ano_zip"].astype(int))]
    if g.empty:
        return g
    vmax = g.groupby("dt_refer")["versao"].transform("max")
    return g[g["versao"] == vmax]


def plano_de(g: pd.DataFrame) -> str:
    """Banco: o PL achado pela DESCRIÇÃO não está em 2.03 (no plano de banco 2.03 é passivo financeiro)."""
    b = g[(g["bloco"] == "BPP") & (g["campo_desc"] == "pl_desc") & (g["ordem_exerc"] == "ULTIMO")]
    return FINANCEIRO if len(b) and not (b["codigo"] == "2.03").any() else INDUSTRIAL


def _dividendos(base: pd.DataFrame) -> float:
    d = base[base["bloco"].str.startswith("DFC") & base["codigo"].str.startswith("6.03")
             & base["descricao"].str.contains(RE_DIV, na=False) & (base["ordem_exerc"] == "ULTIMO")]
    for conj in ("con", "ind"):
        x = d[d["conjunto"] == conj]
        if len(x):
            v = _folhas(x)["valor"]
            return float(-v[v < 0].sum())
    return 0.0


def lucro_fin(rows: pd.DataFrame, so_acumulado: bool = False) -> float | None:
    """Lucro do controlador do plano financeiro pela descrição larga (consolidado → individual); senão o lucro consolidado."""
    for conj in ("con", "ind"):
        b = rows[(rows["conjunto"] == conj) & (rows["ordem_exerc"] == "ULTIMO") & (rows["bloco"] == "DRE")]
        if b.empty:
            continue
        if so_acumulado:
            ini = b["dt_ini_exerc"].dropna()
            if not ini.empty:
                b = b[b["dt_ini_exerc"] == ini.min()]
        achado = None
        for rx in (RE_LC_FIN, RE_L_FIN):          # controlador = 0 com lucro ≠ 0 é linha não preenchida (ABCB4 2022–23)
            x = b[b["descricao"].str.contains(rx, na=False)]
            if len(x):
                v = x["valor"].astype(float)
                achado = float(v.loc[v.abs().idxmax()])
                if achado != 0:
                    return achado
        if achado is not None:
            return achado
    return None


def acoes_referencia(cd_cvm: int, data_base: str) -> float | None:
    """Contagem de ações do ledger (FRE/composição, com a unidade já saneada em `diagnostico_acoes`), só como régua de escala."""
    from backtest.ledger.pit import _acoes_em
    try:
        return _acoes_em(cd_cvm, data_base)[0]
    except FileNotFoundError:
        return None


def escalar_acoes(acoes: dict, ref: float | None, qtd_teorica: float | None) -> tuple[dict, str]:
    """A composição do capital vem em MILHARES em parte das companhias. × 1000 quando a contagem × 1000 fica a menos de 2× da
    referência do ledger, ou (sem referência) quando a contagem é menor que a quantidade teórica do Ibovespa (só flutuante)."""
    n = acoes["on"] + acoes["pn"]
    if n <= 0:
        return acoes, ""
    mil = {k: v * 1000 for k, v in acoes.items()}
    if ref:
        if 0.5 <= n * 1000 / ref <= 2 and not 0.5 <= n / ref <= 2:
            return mil, f"composição em milhares (× 1000; referência do ledger {ref:,.0f})"
        if not 0.5 <= n / ref <= 2:
            return acoes, f"contagem difere da referência do ledger ({n:,.0f} × {ref:,.0f})"
        return acoes, ""
    if qtd_teorica and n < qtd_teorica:
        return mil, "composição em milhares (× 1000; menor que a quantidade teórica do Ibovespa)"
    return acoes, ""


def companhia(g: pd.DataFrame, cnpj: str, data_base: str) -> dict:
    """Anuais (lucro e PL do controlador, dividendos pagos), último balanço até T (PL, dívida, ações) e lucro LTM."""
    plano = plano_de(g)
    out = {"plano": plano, "anuais": {}, "avisos": []}
    dfp = _do_zip_proprio(g, "dfp")
    for dr in sorted(dfp["dt_refer"].unique()):
        if dr > data_base:
            continue
        sub = dfp[dfp["dt_refer"] == dr]
        c, conj, _ini, meses, amb = _contas_de(sub, dr, plano)
        if c and conj == "con" and not lucro_controlador(c) and not _pl_controlador(c):
            # consolidado entregue todo zerado (TIMS3 2024–25): vale o individual
            ci = _contas_de(sub[sub["conjunto"] == "ind"], dr, plano)
            if ci[0] and (lucro_controlador(ci[0]) or _pl_controlador(ci[0])):
                c, conj, _ini, meses, amb = ci
                out["avisos"].append(f"DFP {dr}: consolidado zerado, usado o individual")
        if not c or meses < 11:
            continue
        lucro = lucro_controlador(c)
        if not lucro and plano == FINANCEIRO:      # None ou 0 com o plano de banco: leitura larga pela descrição
            lucro = lucro_fin(sub)
        out["anuais"][int(dr[:4])] = {"dt_refer": dr, "conjunto": conj, "lucro": lucro,
                                      "pl": _pl_controlador(c), "dividendos": _dividendos(sub), "ambiguo": amb}
    # último ITR entregue até T (pelo DT_RECEB do índice da CVM)
    idx = indice_docs("itr", int(data_base[:4]))
    idx = idx[(idx["CNPJ_CIA"] == cnpj) & (idx["DT_RECEB"] <= data_base)]
    if idx.empty:
        out["avisos"].append("sem ITR de 2026 entregue até T")
        return out
    itr = _do_zip_proprio(g, "itr")
    entregues = sorted(idx["DT_REFER"].unique(), reverse=True)
    dr, c = entregues[0], {}
    for d_ in entregues:                       # o mais recente entregue até T que tenha números no CSV
        c, conj, _ini, meses, _amb = _contas_de(itr[itr["dt_refer"] == d_], d_, plano, so_acumulado=True)
        if c:
            if d_ != entregues[0]:
                out["avisos"].append(f"ITR {entregues[0]} entregue até T, sem números no CSV da CVM: usado o {d_}")
            dr = d_
            break
    if not c:
        out["avisos"].append("ITR entregue até T sem números no CSV")
        return out
    tardia = indice_docs("itr", int(data_base[:4]))
    tardia = tardia[(tardia["CNPJ_CIA"] == cnpj) & (tardia["DT_REFER"] == dr) & (tardia["DT_RECEB"] > data_base)]
    if len(tardia):
        out["avisos"].append(f"ITR {dr} reapresentado depois de T (o CSV guarda só a última versão)")
    acoes = acoes_por_classe(cnpj, dr)
    out["ultimo"] = {"dt_refer": dr, "dt_receb": str(idx[idx["DT_REFER"] == dr]["DT_RECEB"].max()), "conjunto": conj,
                     "pl": _pl_controlador(c) if c else None,
                     "divida": (sum(float(c.get(k) or 0.0) for k in ("emprest_cp", "emprest_lp", "arrendamento"))
                                if c and plano == INDUSTRIAL else None),
                     "acoes": acoes, "lucro_ytd": _lucro(c, itr[itr["dt_refer"] == dr], plano), "meses_ytd": meses}
    # LTM = exercício anterior + YTD de agora − YTD do ano anterior (mesmo trimestre)
    ant = dr.replace(dr[:4], str(int(dr[:4]) - 1), 1)
    c0, _, _, m0, _ = _contas_de(itr[itr["dt_refer"] == ant], ant, plano, so_acumulado=True)
    out["ultimo"]["pl_ano_antes"] = _pl_controlador(c0) if c0 else None
    fy = out["anuais"].get(int(dr[:4]) - 1)
    if c and c0 and fy and m0 == meses and fy["lucro"] is not None and fy["dt_refer"].endswith("12-31"):
        y1, y0 = out["ultimo"]["lucro_ytd"], _lucro(c0, itr[itr["dt_refer"] == ant], plano)
        out["ltm"] = None if y1 is None or y0 is None else fy["lucro"] + y1 - y0
    else:
        out["ltm"] = None
    return out


def _lucro(c: dict, rows: pd.DataFrame, plano: str) -> float | None:
    x = lucro_controlador(c) if c else None
    return lucro_fin(rows, so_acumulado=True) if x is None and plano == FINANCEIRO else x
