"""Perfil e estrutura da ação em T, pelo FCA da CVM — sem nenhuma decisão por ticker.

O motor de hoje recebe `perfil` digitado em cada lote*.py. No backtest isso seria julgamento de
2026 aplicado a 2015. Aqui o perfil sai do `Setor_Atividade` do FCA mais recente ENTREGUE até T
(`DT_RECEB <= T`), traduzido pela tabela congelada `Config.perfil_por_setor`, escrita a partir dos
setores distintos do FCA e do §11.2 da doutrina antes da primeira rodada do proxy.

Também daqui sai a composição da unit (`Composicao_BDR_Unit`, texto livre: "1 ON / 2 PN",
"1 KLBN3 + 4 KLBN4"). O FRE conta ON+PN; o preço de BRBI11 é por unit — sem a composição, o P/C de
toda unit sai errado pelo fator 3 a 5.
"""
from __future__ import annotations

import re
import unicodedata
import zipfile
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import pandas as pd

from ..config import PADRAO, Config

CVM = Path(__file__).resolve().parent.parent.parent / "dados" / "cvm"

BANCO, SEGURADORA, UTILITY, CICLICA, SERVICOS, HOLDING = (
    "banco", "seguradora", "utility", "ciclica", "servicos", "holding")
MOTOR_FIN = (BANCO, SEGURADORA, UTILITY)            # P/VP justificado · DDM · lucro normalizado
PLANO_FINANCEIRO = (BANCO, SEGURADORA)              # utility tem o plano de contas industrial
_PREFIXO_HOLDING = re.compile(r"^emp\. adm\. part\. ?- ?")


def normaliza(s: str) -> str:
    """Sem acento, minúsculo, espaços colapsados — a chave de `perfil_por_setor` e das regex."""
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s).strip().lower()


def setor_chave(setor: str) -> str:
    """'Emp. Adm. Part. - Energia Elétrica' -> 'energia eletrica': a holding segue o setor declarado."""
    return _PREFIXO_HOLDING.sub("", normaliza(setor))


@dataclass(frozen=True)
class Perfil:
    cd_cvm: int
    setor: str
    perfil: str
    dt_receb: str            # do FCA usado — vai para a procedência e para o teste de não-vazamento
    motivo_exclusao: str     # "" quando o motor roda

    @property
    def motor(self) -> str:
        return "fin" if self.perfil in MOTOR_FIN else "nf"

    @property
    def plano(self) -> str:
        return "financeiro" if self.perfil in PLANO_FINANCEIRO else "industrial"


def _ler(z: zipfile.ZipFile, nome: str, cols: list[str]) -> pd.DataFrame:
    return pd.read_csv(z.open(nome), sep=";", encoding="latin-1", dtype=str, usecols=cols)


@lru_cache(maxsize=1)
def _fca() -> tuple[pd.DataFrame, pd.DataFrame]:
    """(geral, valor_mobiliario) de todos os FCA, cada linha com o DT_RECEB do seu documento."""
    gerais, vms = [], []
    for f in sorted(CVM.glob("fca_*.zip")):
        a = f.stem.split("_")[1]
        with zipfile.ZipFile(f) as z:
            cab = _ler(z, f"fca_cia_aberta_{a}.csv", ["ID_DOC", "DT_RECEB"])
            g = _ler(z, f"fca_cia_aberta_geral_{a}.csv",
                     ["ID_Documento", "Data_Referencia", "Versao", "Codigo_CVM", "CNPJ_Companhia",
                      "Setor_Atividade"])
            v = _ler(z, f"fca_cia_aberta_valor_mobiliario_{a}.csv",
                     ["ID_Documento", "Data_Referencia", "Versao", "CNPJ_Companhia",
                      "Valor_Mobiliario", "Codigo_Negociacao", "Composicao_BDR_Unit"])
        cab = cab.rename(columns={"ID_DOC": "ID_Documento"}).drop_duplicates("ID_Documento")
        gerais.append(g.merge(cab, on="ID_Documento", how="inner"))
        vms.append(v.merge(cab, on="ID_Documento", how="inner"))
    geral = pd.concat(gerais, ignore_index=True)
    geral["cd_cvm"] = pd.to_numeric(geral["Codigo_CVM"], errors="coerce").astype("Int64")
    geral["Versao"] = pd.to_numeric(geral["Versao"], errors="coerce")
    vm = pd.concat(vms, ignore_index=True)
    vm["Versao"] = pd.to_numeric(vm["Versao"], errors="coerce")
    vm["Codigo_Negociacao"] = vm["Codigo_Negociacao"].fillna("").str.strip().str.upper()
    return geral.dropna(subset=["cd_cvm", "DT_RECEB"]), vm.dropna(subset=["DT_RECEB"])


def _ultimo_ate(d: pd.DataFrame, data_corte: str) -> pd.DataFrame:
    """Linhas do FCA mais recente (Data_Referencia, Versao) já entregue em T."""
    d = d[d["DT_RECEB"] <= data_corte]
    if d.empty:
        return d
    topo = d.sort_values(["Data_Referencia", "Versao", "DT_RECEB"]).iloc[-1]
    return d[(d["Data_Referencia"] == topo["Data_Referencia"]) & (d["Versao"] == topo["Versao"])]


def perfil_de_setor(setor: str, cfg: Config = PADRAO) -> str:
    return dict(cfg.perfil_por_setor).get(setor_chave(setor), cfg.perfil_padrao)


def perfil_em(cd_cvm: int, data_corte: str, cfg: Config = PADRAO,
              _geral: pd.DataFrame | None = None) -> Perfil:
    """Perfil da companhia como se via em T. `_geral` só existe para o teste injetar o FCA."""
    geral = _fca()[0] if _geral is None else _geral
    d = _ultimo_ate(geral[geral["cd_cvm"] == cd_cvm], data_corte)
    if d.empty or pd.isna(d.iloc[0]["Setor_Atividade"]):
        return Perfil(cd_cvm, "", "", "" if d.empty else str(d.iloc[0]["DT_RECEB"]), "sem_setor")
    r = d.iloc[0]
    p = perfil_de_setor(r["Setor_Atividade"], cfg)
    motivo = f"perfil_{p}_excluido" if p in cfg.perfis_excluidos else ""
    return Perfil(cd_cvm, str(r["Setor_Atividade"]), p, str(r["DT_RECEB"]), motivo)


def cd_cvm_do_cnpj(cnpj: str) -> int | None:
    """CNPJ -> código CVM (identidade, não muda no tempo)."""
    g = _fca()[0]
    c = g.loc[g["CNPJ_Companhia"] == cnpj, "cd_cvm"].dropna().unique()
    return int(c[0]) if len(c) == 1 else None


# Número seguido de palavra, sem ser o dígito final de um ticker ("1 KLBN3 + 4 KLBN4" -> 1 e 4).
_QTD = re.compile(r"(?<![A-Za-z0-9])(\d+)\s*(?=[A-Za-z])")


def acoes_na_unit(texto: str) -> int | None:
    """'1 ON / 2 PN' -> 3. None quando não dá para ler sem ambiguidade (recibo, bônus, vazio)."""
    t = normaliza(texto or "")
    if not t or re.search(r"recibo|bonus|subscri", t):
        return None
    qs = [int(x) for x in _QTD.findall(t)]
    return sum(qs) if qs and all(q > 0 for q in qs) else None


def acoes_por_papel(ticker: str, cnpj: str, data_corte: str,
                    _vm: pd.DataFrame | None = None) -> int | None:
    """Quantas ações do FRE um papel representa em T: 1 para ON/PN; a composição para unit.

    None = unit sem composição legível no FCA em T -> o motor exclui com motivo, nunca supõe 1.
    """
    vm = _fca()[1] if _vm is None else _vm
    d = _ultimo_ate(vm[vm["CNPJ_Companhia"] == cnpj], data_corte)
    linha = d[d["Codigo_Negociacao"] == ticker.upper()]
    e_unit = (linha["Valor_Mobiliario"].fillna("").map(normaliza).str.contains("unit").any()
              if not linha.empty else ticker.upper().endswith("11"))
    if not e_unit:
        return 1
    for txt in linha["Composicao_BDR_Unit"].dropna():
        n = acoes_na_unit(txt)
        if n:
            return n
    return None
