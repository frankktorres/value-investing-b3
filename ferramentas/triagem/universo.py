"""Universo da triagem em T: papéis negociados, um por companhia, e as exclusões pré-ledger com motivo.

Fontes (nota A): COTAHIST da B3 (liquidez, CODBDI) e FCA da CVM (identidade, setor, situação do
emissor). A situação do emissor é lida AQUI, por um leitor próprio: mexer em
`backtest/motor/perfil.py` mudaria o `hash_motor` registrado na consulta única do proxy (Etapa 3).
"""
from __future__ import annotations

import zipfile
from functools import lru_cache
from pathlib import Path

import pandas as pd

from backtest import cotahist
from backtest.config import PADRAO as BT, limite_liquidez
from backtest.ledger.identidade import _cnpj_do_ticker_em, mapa_ticker_cnpj
from backtest.motor.perfil import _ultimo_ate, cd_cvm_do_cnpj, normaliza, setor_chave

from .config import IDENTIDADE_MANUAL, PADRAO, ConfigTriagem

CVM = Path(__file__).resolve().parent.parent / "dados" / "cvm"

# Motivos (texto que vai para o 06). Ordem de aplicação = ordem desta tupla.
LIQUIDEZ, SEM_IDENTIDADE, RECUPERACAO, SETOR, JA_ANALISADA = (
    "liquidez abaixo do piso", "sem identidade na CVM", "recuperação/falência/liquidação",
    "setor a evitar (§8)", "já analisada (hall)")


@lru_cache(maxsize=1)
def _fca_geral() -> pd.DataFrame:
    cols = ["ID_Documento", "Data_Referencia", "Versao", "Codigo_CVM", "CNPJ_Companhia",
            "Setor_Atividade", "Situacao_Emissor", "Especie_Controle_Acionario",
            "Mes_Encerramento_Exercicio_Social"]
    partes = []
    for f in sorted(CVM.glob("fca_*.zip")):
        a = f.stem.split("_")[1]
        with zipfile.ZipFile(f) as z:
            cab = pd.read_csv(z.open(f"fca_cia_aberta_{a}.csv"), sep=";", encoding="latin-1",
                              dtype=str, usecols=["ID_DOC", "DT_RECEB"])
            g = pd.read_csv(z.open(f"fca_cia_aberta_geral_{a}.csv"), sep=";", encoding="latin-1",
                            dtype=str, usecols=lambda c: c in cols)
        cab = cab.rename(columns={"ID_DOC": "ID_Documento"}).drop_duplicates("ID_Documento")
        partes.append(g.merge(cab, on="ID_Documento", how="inner"))
    d = pd.concat(partes, ignore_index=True)
    for c in cols:
        if c not in d.columns:
            d[c] = pd.NA
    d["cd_cvm"] = pd.to_numeric(d["Codigo_CVM"], errors="coerce").astype("Int64")
    d["Versao"] = pd.to_numeric(d["Versao"], errors="coerce")
    return d.dropna(subset=["cd_cvm", "DT_RECEB"])


def fca_em(cd_cvm: int, data_corte: str, _geral: pd.DataFrame | None = None) -> dict:
    """Setor, situação do emissor e controle no FCA mais recente entregue até T ({} se nenhum)."""
    g = _fca_geral() if _geral is None else _geral
    d = _ultimo_ate(g[g["cd_cvm"] == cd_cvm], data_corte)
    if d.empty:
        return {}
    r = d.iloc[0]
    txt = lambda k: "" if pd.isna(r.get(k)) else str(r.get(k))                 # noqa: E731
    return {"setor": txt("Setor_Atividade"), "situacao": txt("Situacao_Emissor"),
            "controle": txt("Especie_Controle_Acionario"),
            "mes_encerramento": txt("Mes_Encerramento_Exercicio_Social"),
            "fca_dt_receb": txt("DT_RECEB")}


def piso_liquidez(data_corte: str, cfg: ConfigTriagem = PADRAO) -> float:
    """Maior entre o piso do backtest (R$ reais de 2014-05, IPCA <= T) e o volume da posição."""
    return max(limite_liquidez(BT, data_corte), cfg.volume_minimo_posicao)


def ultimo_codbdi(data_corte: str) -> pd.Series:
    """CODBDI do último negócio de cada ticker até T (ano de T e o anterior)."""
    ano = int(data_corte[:4])
    partes = [pd.read_parquet(cotahist.parquet_de(a), columns=["data", "ticker", "codbdi"])
              for a in (ano - 1, ano) if cotahist.parquet_de(a).exists()]
    d = pd.concat(partes, ignore_index=True)
    d = d[d["data"] <= data_corte].sort_values(["ticker", "data"])
    return d.groupby("ticker")["codbdi"].last()


def classificar(liq: pd.Series, cnpj_de: dict, cd_de, fca_de, codbdi: pd.Series, piso: float,
                hall_cnpjs: set[str], cfg: ConfigTriagem = PADRAO) -> pd.DataFrame:
    """Um papel por companhia (o mais líquido) + motivo pré-ledger. Função pura: o teste injeta tudo.

    liq: liquidez média por ticker (R$/dia); cnpj_de: ticker -> cnpj; cd_de: cnpj -> cd_cvm;
    fca_de: cd_cvm -> dict de `fca_em`; codbdi: último CODBDI por ticker.
    """
    linhas = []
    sem_id = [t for t in liq.index if not cnpj_de.get(t)]
    for t in sorted(sem_id):
        linhas.append({"ticker": t, "cnpj": "", "cd_cvm": None, "liquidez": float(liq[t]),
                       "outras_classes": "", "motivo": SEM_IDENTIDADE, "detalhe": ""})
    por_cnpj: dict[str, list[str]] = {}
    for t in liq.index:
        c = cnpj_de.get(t)
        if c:
            por_cnpj.setdefault(c, []).append(t)
    for cnpj, tks in sorted(por_cnpj.items()):
        tks = sorted(tks, key=lambda t: (-float(liq[t]), t))
        t = tks[0]
        cd = cd_de(cnpj)
        f = fca_de(cd) if cd is not None else {}
        lin = {"ticker": t, "cnpj": cnpj, "cd_cvm": cd, "liquidez": float(liq[t]),
               "outras_classes": " ".join(tks[1:]), "setor": f.get("setor", ""),
               "situacao": f.get("situacao", ""), "controle": f.get("controle", ""),
               "mes_encerramento": f.get("mes_encerramento", ""),
               "codbdi": str(codbdi.get(t, "")), "motivo": "", "detalhe": ""}
        lin["motivo"], lin["detalhe"] = _motivo(lin, piso, hall_cnpjs, cfg)
        linhas.append(lin)
    return pd.DataFrame(linhas)


def _motivo(l: dict, piso: float, hall_cnpjs: set[str], cfg: ConfigTriagem) -> tuple[str, str]:
    if l["liquidez"] < piso:
        return LIQUIDEZ, f"R$ {l['liquidez'] / 1e6:.2f} mi/dia"
    if l["cd_cvm"] is None:
        return SEM_IDENTIDADE, "CNPJ sem código CVM único"
    sit = normaliza(l["situacao"])
    if sit and sit not in cfg.situacao_ok:
        return RECUPERACAO, f"FCA: {l['situacao']}"
    if l["codbdi"] in cfg.codbdi_exclui:
        return RECUPERACAO, f"CODBDI {l['codbdi']} no último pregão"
    sk = setor_chave(l["setor"]) if l["setor"] else ""
    for s, txt in cfg.setores_excluidos:
        if sk == s:
            return SETOR, txt
    for raiz, txt in cfg.raizes_excluidas:
        if l["ticker"].startswith(raiz):
            return SETOR, txt
    if l["cnpj"] in hall_cnpjs:
        return JA_ANALISADA, ""
    return "", ""


def tickers_analisados() -> list[str]:
    """Os 41 do golden (36 no hall + 5 fora). Só a LISTA — nenhum número do golden entra aqui."""
    import json
    g = Path(__file__).resolve().parent.parent / "tests" / "golden.json"
    return sorted(json.loads(g.read_text(encoding="utf-8"))["tickers"])


def universo(data_corte: str, cfg: ConfigTriagem = PADRAO) -> tuple[pd.DataFrame, float]:
    """(tabela de companhias com motivo pré-ledger, piso em R$/dia) no T dado."""
    cal = cotahist.calendario(range(int(data_corte[:4]) - 1, int(data_corte[:4]) + 1))
    liq = cotahist.liquidez_media(data_corte, cal=cal, janela=BT.liquidez_pregoes)
    mapa = mapa_ticker_cnpj()
    cnpj_de = _cnpj_do_ticker_em(mapa, data_corte)
    cnpj_de_liq = {t: cnpj_de[t] or IDENTIDADE_MANUAL.get(t) for t in liq.index}
    hall = {c for t in tickers_analisados() if (c := cnpj_de[t] or IDENTIDADE_MANUAL.get(t))}
    piso = piso_liquidez(data_corte, cfg)
    tab = classificar(liq, cnpj_de_liq, cd_cvm_do_cnpj, lambda cd: fca_em(int(cd), data_corte),
                      ultimo_codbdi(data_corte), piso, hall, cfg)
    return tab, piso
