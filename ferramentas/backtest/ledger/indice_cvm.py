"""Índice de documentos da CVM com DT_RECEB e VERSAO — a espinha do point-in-time.

O achado que manda neste módulo: **o dado aberto da CVM não é arquivo histórico, é espelho vivo.**
Medido nos ZIPs em disco:

  · o CABEÇALHO (`dfp_cia_aberta_{ano}.csv`) guarda TODAS as versões de cada documento, cada uma
    com seu DT_RECEB. No ZIP de 2016 há DT_RECEB até 2019-12-07;
  · os CSVs de DEMONSTRAÇÃO (`..._DRE_con_{ano}.csv`) guardam UMA ÚNICA versão por
    (CD_CVM, DT_REFER) — medido: 0 de 340 pares com mais de uma. E é a ÚLTIMA.

Consequência que derruba a saída intuitiva: baixar o ZIP "do ano de publicação" NÃO recupera o
número original. `dfp_2016.zip` baixado em 2026 serve o FY2016 já reapresentado. E `ORDEM_EXERC`
(ÚLTIMO/PENÚLTIMO) só ordena os dois exercícios DENTRO de um documento — não é histórico de versão.

Logo o que se pode fazer é saber SE o número está contaminado, não qual era o número limpo:

    V_T     = max{versao : dt_receb <= T}      # a versão que um humano teria visto em T
    V_disco = versao presente no CSV de demonstração
    limpo        <=>  V_T existe e V_T == V_disco
    contaminado  <=>  V_T existe e V_T <  V_disco     (temos número do futuro)
    indisponivel <=>  não há V_T                      (nada publicado até T)

Regra de disponibilidade: OBSERVADA, nunca legal. `disponível em T <=> existe documento com
DT_RECEB <= T que contém o exercício`. O prazo regulatório não entra: supor "DFP disponível em
31/03" entrega a quem atrasou um balanço que ninguém tinha, e atrasa quem entregou em fevereiro.

Chave sempre (cd_cvm, dt_refer) — NUNCA ano. `dfp_2017.zip` tem 4 valores distintos de DT_REFER:
exercício social diferente de dezembro existe (SMTO3 fecha em março).
"""
from __future__ import annotations

import io
import zipfile
from functools import lru_cache
from pathlib import Path

import pandas as pd

CACHE = Path(__file__).resolve().parent.parent.parent / "dados" / "cvm"
DESTINO = Path(__file__).resolve().parent.parent / "dados"

CATEGORIAS = ("dfp", "itr")
COLS = ["CNPJ_CIA", "DT_REFER", "VERSAO", "DENOM_CIA", "CD_CVM", "CATEG_DOC", "ID_DOC",
        "DT_RECEB", "LINK_DOC"]

LIMPO, CONTAMINADO, INDISPONIVEL = "limpo", "contaminado", "indisponivel"
SEM_DEMONSTRACAO = "sem_demonstracao"


def _ler_csv(z: zipfile.ZipFile, nome: str) -> pd.DataFrame | None:
    alvo = [n for n in z.namelist() if n.lower().endswith(nome.lower())]
    if not alvo:
        return None
    return pd.read_csv(io.BytesIO(z.read(alvo[0])), sep=";", encoding="latin-1", dtype=str)


def anos_em_disco(categ: str) -> list[int]:
    return sorted(int(p.stem.split("_")[1]) for p in CACHE.glob(f"{categ}_*.zip"))


@lru_cache(maxsize=8)
def indexar(categ: str) -> pd.DataFrame:
    """Cabeçalho de TODOS os ZIPs de `categ`: uma linha por (documento, versão).

    Colunas: cd_cvm, cnpj, denom, categ, dt_refer, versao, dt_receb, id_doc, link_doc, ano_zip.
    """
    if categ not in CATEGORIAS:
        raise ValueError(f"categoria desconhecida: {categ}")
    partes = []
    for ano in anos_em_disco(categ):
        with zipfile.ZipFile(CACHE / f"{categ}_{ano}.zip") as z:
            d = _ler_csv(z, f"{categ}_cia_aberta_{ano}.csv")
        if d is None or d.empty:
            continue
        d = d.reindex(columns=COLS)
        d["ano_zip"] = ano
        partes.append(d)
    if not partes:
        raise FileNotFoundError(f"nenhum ZIP de {categ} em {CACHE}")

    idx = pd.concat(partes, ignore_index=True)
    idx = idx.rename(columns={"CNPJ_CIA": "cnpj", "DT_REFER": "dt_refer", "VERSAO": "versao",
                              "DENOM_CIA": "denom", "CD_CVM": "cd_cvm", "CATEG_DOC": "categ",
                              "ID_DOC": "id_doc", "DT_RECEB": "dt_receb", "LINK_DOC": "link_doc"})
    idx["cd_cvm"] = pd.to_numeric(idx["cd_cvm"], errors="coerce").astype("Int64")
    idx["versao"] = pd.to_numeric(idx["versao"], errors="coerce").astype("Int64")
    idx = idx.dropna(subset=["cd_cvm", "dt_refer", "versao", "dt_receb"])

    # Sanidade: recebimento antes do fim do exercício é linha corrompida, não entrega adiantada.
    idx["dt_receb_suspeita"] = idx["dt_receb"] < idx["dt_refer"]
    # O mesmo documento pode aparecer no ZIP de mais de um ano; a identidade é (cd_cvm,dt_refer,versao).
    idx = (idx.sort_values(["cd_cvm", "dt_refer", "versao", "ano_zip"])
              .drop_duplicates(["cd_cvm", "dt_refer", "versao"], keep="first")
              .reset_index(drop=True))
    return idx


@lru_cache(maxsize=64)
def versao_em_disco(categ: str, ano: int) -> pd.DataFrame:
    """A VERSAO que o CSV de demonstração daquele ZIP realmente serve, por (cd_cvm, dt_refer).

    Lida da DRE, CONSOLIDADA E INDIVIDUAL. Ler só a consolidada era um bug medido: companhia sem
    controlada não entrega demonstração consolidada, e 2069 dos 4547 exercícios visíveis em
    2017-06-30 ficavam sem `versao_disco`. Como ausência de prova de limpeza era classificada como
    contaminação, a taxa saía em ~45% — quando a contaminação real é 28 de 2478, ou 1,1%.
    """
    partes = []
    with zipfile.ZipFile(CACHE / f"{categ}_{ano}.zip") as z:
        for sufixo in ("con", "ind"):
            d = _ler_csv(z, f"{categ}_cia_aberta_DRE_{sufixo}_{ano}.csv")
            if d is not None and not d.empty:
                partes.append(d[["CD_CVM", "DT_REFER", "VERSAO"]])
    if not partes:
        return pd.DataFrame(columns=["cd_cvm", "dt_refer", "versao_disco"])
    d = pd.concat(partes, ignore_index=True).drop_duplicates()
    d.columns = ["cd_cvm", "dt_refer", "versao_disco"]
    d["cd_cvm"] = pd.to_numeric(d["cd_cvm"], errors="coerce").astype("Int64")
    d["versao_disco"] = pd.to_numeric(d["versao_disco"], errors="coerce").astype("Int64")
    d = d.dropna()
    # Se con e ind trouxerem versões diferentes, a mais alta é a que o leitor de hoje obtém.
    return (d.sort_values(["cd_cvm", "dt_refer", "versao_disco"])
             .drop_duplicates(["cd_cvm", "dt_refer"], keep="last").reset_index(drop=True))


@lru_cache(maxsize=8)
def _versoes_em_disco(categ: str) -> pd.DataFrame:
    partes = [versao_em_disco(categ, a) for a in anos_em_disco(categ)]
    d = pd.concat([p for p in partes if not p.empty], ignore_index=True)
    # Quando o mesmo exercício aparece em mais de um ZIP, o que vale é a versão MAIS ALTA servida:
    # é essa que o leitor de hoje obtém, e portanto é essa que pode estar contaminada.
    return (d.sort_values(["cd_cvm", "dt_refer", "versao_disco"])
             .drop_duplicates(["cd_cvm", "dt_refer"], keep="last").reset_index(drop=True))


def documentos_visiveis(categ: str, data_corte: str) -> pd.DataFrame:
    """Os documentos que um humano veria em `data_corte`, com o estado de contaminação.

    Uma linha por (cd_cvm, dt_refer) visível: a maior versão com dt_receb <= T. Colunas extra:
    `versao_disco` (o que o CSV serve hoje) e `estado` em {limpo, contaminado}. Exercício sem
    nenhuma versão até T simplesmente não aparece — é `indisponivel`, e quem pergunta por ele
    recebe ausência, não um número.
    """
    idx = indexar(categ)
    vis = idx[(idx["dt_receb"] <= data_corte) & (~idx["dt_receb_suspeita"])]
    if vis.empty:
        return pd.DataFrame(columns=list(idx.columns) + ["versao_disco", "estado"])
    vis = (vis.sort_values(["cd_cvm", "dt_refer", "versao"])
              .drop_duplicates(["cd_cvm", "dt_refer"], keep="last").copy())
    vis = vis.merge(_versoes_em_disco(categ), on=["cd_cvm", "dt_refer"], how="left")
    vis["estado"] = (vis["versao"] == vis["versao_disco"]).map({True: LIMPO, False: CONTAMINADO})
    # Terceiro estado, e não "contaminado": exercício que o cabeçalho lista mas para o qual não há
    # DRE nenhuma no ZIP. Não se sabe se o número é do futuro — não se tem o número. Misturar isso
    # com contaminação foi o que produziu a taxa falsa de 45%; são problemas diferentes e o
    # relatório os separa.
    vis.loc[vis["versao_disco"].isna(), "estado"] = SEM_DEMONSTRACAO
    vis["data_corte"] = data_corte
    return vis.reset_index(drop=True)


def relatorio_contaminacao(categ: str, datas: tuple[str, ...]) -> pd.DataFrame:
    """Quantos exercícios visíveis, quantos limpos e quantos contaminados, por data de corte."""
    linhas = []
    for d in datas:
        vis = documentos_visiveis(categ, d)
        n = len(vis)
        cont = int((vis["estado"] == CONTAMINADO).sum()) if n else 0
        limpos = int((vis["estado"] == LIMPO).sum()) if n else 0
        sem = int((vis["estado"] == SEM_DEMONSTRACAO).sum()) if n else 0
        aferiveis = limpos + cont
        linhas.append({"data_corte": d, "categ": categ, "visiveis": n,
                       "limpos": limpos, "contaminados": cont, "sem_demonstracao": sem,
                       # a taxa que importa é sobre o que se PODE aferir, não sobre o total
                       "pct_contaminado": round(100 * cont / aferiveis, 2) if aferiveis else 0.0,
                       "companhias": int(vis["cd_cvm"].nunique()) if n else 0})
    return pd.DataFrame(linhas)


def main() -> int:
    from ..config import PADRAO

    DESTINO.mkdir(parents=True, exist_ok=True)
    for categ in CATEGORIAS:
        idx = indexar(categ)
        caminho = DESTINO / f"indice_{categ}.parquet"
        idx.to_parquet(caminho, index=False)
        multi = idx.groupby(["cd_cvm", "dt_refer"])["versao"].nunique()
        print(f"{categ.upper()}: {len(idx)} documentos-versao - {idx['cd_cvm'].nunique()} companhias "
              f"- {int((multi > 1).sum())} exercicios com mais de uma versao "
              f"- dt_receb {idx['dt_receb'].min()} a {idx['dt_receb'].max()}")
        print(f"  suspeitas (dt_receb < dt_refer): {int(idx['dt_receb_suspeita'].sum())}")
        print(f"  -> {caminho.relative_to(DESTINO.parent.parent)}")

        rel = relatorio_contaminacao(categ, PADRAO.datas_corte)
        rel.to_parquet(DESTINO / f"contaminacao_{categ}.parquet", index=False)
        print(rel.to_string(index=False))
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
