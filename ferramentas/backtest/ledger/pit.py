"""A visão de UMA companhia em UMA data de corte — só o que era público em T.

Este é o módulo que os testes de não-vazamento vigiam. A regra é uma só:

    disponível em T  <=>  existe documento com DT_RECEB <= T que contém o exercício

e a procedência (dt_receb, versao, estado, mês do IPCA, fonte das ações) viaja como CAMPO do
ledger, não como log. É isso que torna possível o teste sentinela: truncar as fontes em T, rerodar
e exigir veredito idêntico. Sem procedência nos dados, esse teste não existe.

Sobre a contaminação por reapresentação: quando a versão que se via em T é menor que a que o CSV
serve hoje, o VALOR que temos é do futuro e não há como recuperar o original (os CSVs de
demonstração guardam só a última versão). O exercício entra com `estado="contaminado"` e o painel
decide o que fazer — a regra A exclui, a B inclui com flag, e o PDF reporta as duas. Medido: a taxa
é de ~1%, então isto não deve mover conclusão; o que não se pode é ignorar sem medir.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import pandas as pd

from ..calendario import mes_ipca_disponivel
from ..config import PADRAO, Config
from .indice_cvm import CONTAMINADO, LIMPO, SEM_DEMONSTRACAO, documentos_visiveis

DADOS = Path(__file__).resolve().parent.parent / "dados"

INDUSTRIAL, FINANCEIRO = "industrial", "financeiro"

# Em banco o CÓDIGO não identifica o campo. Medido no BCO BRASIL FY2014 consolidado:
#   2.03    = "Passivos Financeiros ao Custo Amortizado"  R$ 1.105.625.511 mil  (NÃO é PL)
#   2.08    = "Patrimônio Líquido Consolidado"            R$    85.440.036 mil  (é o PL)
#   2.03.04 = "Obrigações de Curto Prazo"                 (NÃO é reservas de lucro)
#   3.09    = "Lucro/Prejuízo Consolidado do Período"     (industrial usa 3.11)
#   3.09.01 = "Atribuído a Sócios da Empresa Controladora" (industrial usa 3.11.01)
# Lendo por código, o PL do BB saía como 86% do ativo e o lucro vinha AUSENTE — as duas âncoras
# financeiras (P/VP justificado e DDM) erradas por uma a duas ordens de grandeza em toda a janela
# de calibração. Por isso o plano financeiro resolve estes campos por DESCRIÇÃO.
DE_DESC = {"pl_desc": "pl", "nao_controladores_desc": "nao_controladores",
           "lucro_desc": "lucro", "lucro_controlador_desc": "lucro_controlador"}

# Os únicos campos cujo código é o mesmo nos dois planos: `1`/`2` são totais de balanço, e a LPA
# fica em 3.99 em qualquer plano.
CAMPOS_POR_CODIGO_FIN = ("ativo", "passivo", "lpa_1", "lpa_2")


@dataclass(frozen=True)
class Exercicio:
    """Um exercício como se via em T, com a procedência colada."""
    dt_refer: str
    dt_receb: str
    versao: int
    versao_disco: int | None
    estado: str
    conjunto: str                       # "con" (consolidado) ou "ind"
    contas: dict[str, float] = field(default_factory=dict)
    dfc: tuple[tuple[str, float], ...] = ()      # (descrição, valor) — D&A/capex saem daqui
    # Período dos fluxos. CRÍTICO no ITR: lá cada conta de fluxo tem DUAS linhas ULTIMO, a
    # acumulada no ano (01/01 -> T) e a do trimestre isolado, com os MESMOS nomes de campo dos
    # anuais. Sem registrar o período, quem montar LTM a partir de um ITR erra por ~4x sem sinal.
    dt_ini_exerc: str = ""
    periodo_meses: int = 12
    ambiguo: bool = False               # havia linha duplicada com valor distinto; ver _contas_de

    @property
    def contaminado(self) -> bool:
        return self.estado != LIMPO

    @property
    def ano(self) -> int:
        return int(self.dt_refer[:4])


@dataclass(frozen=True)
class LedgerPIT:
    cd_cvm: int
    data_corte: str
    plano: str
    anuais: tuple[Exercicio, ...]       # ordenados por dt_refer, só dt_receb <= T, truncados em 10
    ultimo_itr: Exercicio | None
    acoes: float | None
    acoes_dt_refer: str
    acoes_dt_receb: str
    acoes_fonte: str
    acoes_ambiguo: bool
    mes_ipca: str                       # último mês de IPCA público em T

    @property
    def n_exercicios(self) -> int:
        return len(self.anuais)

    @property
    def janela_curta(self) -> bool:
        return self.n_exercicios < PADRAO.janela_max

    @property
    def contaminados(self) -> int:
        return sum(e.contaminado for e in self.anuais)

    @property
    def dt_receb_maxima(self) -> str:
        """A data de recebimento mais recente usada — o teste de não-vazamento compara com T."""
        ds = [e.dt_receb for e in self.anuais]
        if self.ultimo_itr:
            ds.append(self.ultimo_itr.dt_receb)
        if self.acoes_dt_receb:
            ds.append(self.acoes_dt_receb)
        return max(ds) if ds else ""

    def procedencia(self) -> dict[str, object]:
        return {"cd_cvm": self.cd_cvm, "data_corte": self.data_corte, "plano": self.plano,
                "n_exercicios": self.n_exercicios, "janela_curta": self.janela_curta,
                "contaminados": self.contaminados, "mes_ipca": self.mes_ipca,
                "dt_receb_maxima": self.dt_receb_maxima,
                "acoes": self.acoes, "acoes_fonte": self.acoes_fonte,
                "acoes_ambiguo": self.acoes_ambiguo,
                "acoes_dt_refer": self.acoes_dt_refer, "acoes_dt_receb": self.acoes_dt_receb,
                "itr_dt_refer": self.ultimo_itr.dt_refer if self.ultimo_itr else "",
                "exercicios": tuple(e.dt_refer for e in self.anuais)}


# --------------------------------------------------------------------------- carga dos parquets
@lru_cache(maxsize=1)
def _fatos() -> pd.DataFrame:
    p = DADOS / "fatos_cvm.parquet"
    if not p.exists():
        raise FileNotFoundError(f"{p} não existe — rode `python -m backtest.ledger.fatos_cvm`")
    return pd.read_parquet(p)


@lru_cache(maxsize=1)
def _acoes() -> pd.DataFrame:
    """FRE (2010+) e, onde existir, composicao_capital da DFP/ITR (2020+) para conferência."""
    fre = pd.read_parquet(DADOS / "acoes_fre.parquet")
    return fre.sort_values(["cd_cvm", "dt_refer", "versao"])


@lru_cache(maxsize=2)
def _por_companhia(categ: str) -> dict[int, pd.DataFrame]:
    f = _fatos()
    f = f[f["categ"] == categ]
    return {int(cd): g for cd, g in f.groupby("cd_cvm")}


@lru_cache(maxsize=64)
def _visiveis(categ: str, data_corte: str) -> pd.DataFrame:
    return documentos_visiveis(categ, data_corte)


# ------------------------------------------------------------------------------- montagem do ledger
def _reduzir(d: pd.DataFrame, coluna: str) -> tuple[dict[str, float], bool]:
    """Um valor por campo, com DESEMPATE DECLARADO quando há linha duplicada.

    Medido: 2236 grupos (cd, dt_refer, conjunto, campo) da DFP têm mais de uma linha, e 23 têm
    valores DISTINTOS — nesses, `dict(zip(...))` deixava a escolha para a ordem do CSV, e um 0,0
    podia virar o EBIT (ou o contrário). A regra é o maior valor absoluto, e o exercício sai
    marcado `ambiguo` para o painel poder excluir.
    """
    contas, ambiguo = {}, False
    for campo, grupo in d.groupby(coluna):
        vals = grupo["valor"].astype(float)
        if vals.nunique() > 1:
            ambiguo = True
            contas[str(campo)] = float(vals.loc[vals.abs().idxmax()])
        else:
            contas[str(campo)] = float(vals.iloc[0])
    return contas, ambiguo


def _contas_de(g: pd.DataFrame, dt_refer: str, plano: str,
               so_acumulado: bool = False) -> tuple[dict[str, float], str, str, int, bool]:
    """Contas de um exercício. Prefere o CONSOLIDADO; cai para individual quando não há.

    `so_acumulado=True` (ITR): entre as duas linhas ULTIMO de cada conta de fluxo — a acumulada no
    ano e a do trimestre isolado — fica a ACUMULADA (a de período mais longo). Medido: em 11.469 de
    11.614 ITRs de 2T/3T a última linha do CSV é o TRIMESTRE, então deixar a ordem decidir entregava
    o trimestre com o nome do fluxo anual, erro silencioso de ~4x.

    Devolve (contas, conjunto, dt_ini_exerc, periodo_meses, ambiguo).
    """
    for conjunto in ("con", "ind"):
        base = g[(g["dt_refer"] == dt_refer) & (g["conjunto"] == conjunto)
                 & (g["ordem_exerc"] == "ULTIMO")]
        if base.empty:
            continue
        if so_acumulado and "dt_ini_exerc" in base:
            ini = base["dt_ini_exerc"].dropna()
            if not ini.empty:
                base = base[base["dt_ini_exerc"].isin([ini.min()]) | base["dt_ini_exerc"].isna()]

        # Industrial: por código. Financeiro: por DESCRIÇÃO, porque o código muda com o plano —
        # `2.03` é PL na indústria e "Passivos Financeiros ao Custo Amortizado" em banco.
        por_codigo = base[base["campo"].notna()]
        if plano == FINANCEIRO:
            contas, amb1 = _reduzir(por_codigo[por_codigo["campo"].isin(CAMPOS_POR_CODIGO_FIN)], "campo")
            por_desc = base[base["campo_desc"].notna()]
            achados, amb2 = _reduzir(por_desc, "campo_desc")
            # `pl_desc` -> `pl`, etc. A descrição vence o código em caso de conflito.
            contas.update({DE_DESC[k]: v for k, v in achados.items() if k in DE_DESC})
            ambiguo = amb1 or amb2
        else:
            contas, ambiguo = _reduzir(por_codigo, "campo")

        # IFRS 16 — e aqui estava uma DUPLA CONTAGEM da dívida bruta. `2.01.04.03` é SUBCONTA de
        # `2.01.04` (medido: 2.01.04.03 <= 2.01.04 em 132 de 132 casos), e `divida_liquida` já soma
        # `2.01.04`. Somar o arrendamento outra vez inflava a dívida bruta em 7,8% na mediana, 61%
        # no p90 e 100% no pior caso (a dívida DOBRAVA), deixando quem arrenda muito artificialmente
        # barato. `coletar_cvm.extras_bp:150-165` evita isso de propósito, e a cópia perdeu a regra.
        # Correto: para a DÍVIDA só entra arrendamento lançado FORA de 2.01.04/2.02.01; o saldo
        # completo fica em `arrendamento_saldo`, que serve só ao juro embutido do Owner Earnings.
        # Restringir ao BPP é essencial: a mesma regex de descrição casa "pagamento de
        # arrendamento" na DFC e a despesa de aluguel na DRE, que são NEGATIVAS. Sem o filtro de
        # bloco o saldo saía negativo e menor em módulo que a parte — impossível para um passivo.
        bpp = base[(base["bloco"] == "BPP")
                   & base["codigo"].str.startswith(("2.01", "2.02"), na=False)
                   & (base["campo_desc"] == "arrendamento_desc")]
        fora = bpp[~bpp["codigo"].str.startswith(("2.01.04", "2.02.01"), na=False)]
        contas.pop("arrendamento_cp", None)
        contas.pop("arrendamento_lp", None)
        contas["arrendamento"] = float(_folhas(fora)["valor"].sum()) if len(fora) else 0.0
        contas["arrendamento_saldo"] = float(_folhas(bpp)["valor"].sum()) if len(bpp) else 0.0

        ini = str(base["dt_ini_exerc"].dropna().min()) if "dt_ini_exerc" in base else ""
        meses = _meses(ini, dt_refer)
        return contas, conjunto, ini, meses, ambiguo
    return {}, "", "", 0, False


def _folhas(d: pd.DataFrame) -> pd.DataFrame:
    """Só as contas-folha: descarta código que é prefixo de outro, para não somar pai com filho."""
    if d.empty:
        return d
    cods = sorted(set(d["codigo"].dropna()))
    pais = {c for c in cods if any(o != c and o.startswith(c + ".") for o in cods)}
    return d[~d["codigo"].isin(pais)]


def _meses(ini: str, fim: str) -> int:
    if not ini or not fim or ini == "nan":
        return 12
    try:
        a, b = ini.split("-"), fim.split("-")
        return max(1, (int(b[0]) * 12 + int(b[1])) - (int(a[0]) * 12 + int(a[1])) + 1)
    except (ValueError, IndexError):
        return 12


def _dfc_de(g: pd.DataFrame, dt_refer: str) -> tuple[tuple[str, float], ...]:
    """Linhas inteiras da DFC do exercício: D&A, capex, dividendo e juros pagos saem por descrição."""
    d = g[(g["dt_refer"] == dt_refer) & (g["bloco"].isin(("DFC_MI", "DFC_MD")))
          & (g["ordem_exerc"] == "ULTIMO")]
    if d.empty:
        return ()
    for conjunto in ("con", "ind"):
        dd = d[d["conjunto"] == conjunto]
        if not dd.empty:
            return tuple(zip(dd["descricao"].astype(str), dd["valor"].astype(float)))
    return ()


def _acoes_em(cd_cvm: int, data_corte: str) -> tuple[float | None, str, str, str, bool]:
    """Contagem de ações como se via em T. (acoes, dt_refer, dt_receb, fonte, ambiguo).

    Duas filtragens, as duas por data que está no próprio dado:
      · `dt_receb <= T` — o documento tinha de estar entregue;
      · `aprovacao <= T` — a tabela do FRE é HISTÓRICO de autorizações de capital, e vale a mais
        recente já aprovada em T. Sem isto se pega linha arbitrária: o BB em 2022 tem uma linha de
        2.865.417.020 (aprovação de 2023) e outra de 286.541.720 (aprovação de 2015), um décimo —
        erro silencioso de 10x no valor de mercado.

    `ambiguo` propaga quando o documento trazia mais de um valor distinto, para o painel poder
    excluir. A pendência de 58% de concordância FRE × `composicao_capital` foi resolvida em
    06/10/2026 (`ledger/diagnostico_acoes.py`): era unidade da REFERÊNCIA (DFP em milhares em ~28%
    das companhias); corrigida, a concordância é 86,7% geral e 93,2% nas companhias acima do piso.
    Evento em ações entre a aprovação e T (desdobramento, bonificação) NÃO está aplicado aqui:
    quem combina esta contagem com o preço de T tem de ajustar pelos eventos (fatia 10).
    """
    a = _acoes()
    d = a[(a["cd_cvm"] == cd_cvm) & (a["dt_receb"] <= data_corte)]
    if d.empty:
        return None, "", "", "", False
    aprov = d["aprovacao"].fillna("")
    valido = d[(aprov <= data_corte) & (aprov != "")]
    if valido.empty:                       # sem data de aprovação utilizável: declara ambíguo
        r = d.sort_values(["dt_refer", "versao"]).iloc[-1]
        return float(r["acoes_total"]), str(r["dt_refer"]), str(r["dt_receb"]), str(r["fonte_acoes"]), True
    # Ordem por APROVAÇÃO primeiro — era o bug: ordenar por `dt_refer` antes fazia ganhar a linha
    # do documento mais recente mesmo carregando autorização velha, descartando a autorização nova
    # que estava num FRE anterior. Medido: 206 de 22.241 companhia-datas mudam de valor, com casos
    # de 30x, 481x e 1000x de erro na contagem de ações — e portanto no valor de mercado e no P/C.
    r = valido.sort_values(["aprovacao", "dt_refer", "versao"]).iloc[-1]
    return (float(r["acoes_total"]), str(r["dt_refer"]), str(r["dt_receb"]),
            str(r["fonte_acoes"]), bool(r.get("acoes_ambiguo", False)))


def ledger_em(cd_cvm: int, data_corte: str, plano: str = INDUSTRIAL,
              cfg: Config = PADRAO) -> LedgerPIT | None:
    """O que se sabia da companhia `cd_cvm` em `data_corte`. None quando nada era público."""
    porc = _por_companhia("dfp")
    if cd_cvm not in porc:
        return None
    g = porc[cd_cvm]

    vis = _visiveis("dfp", data_corte)
    vis = vis[vis["cd_cvm"] == cd_cvm]
    if vis.empty:
        return None

    anuais: list[Exercicio] = []
    for _, r in vis.sort_values("dt_refer").iterrows():
        contas, conjunto, ini, meses, amb = _contas_de(g, r["dt_refer"], plano)
        if not contas:
            continue
        vd = r["versao_disco"]
        anuais.append(Exercicio(
            dt_refer=str(r["dt_refer"]), dt_receb=str(r["dt_receb"]), versao=int(r["versao"]),
            versao_disco=None if pd.isna(vd) else int(vd), estado=str(r["estado"]),
            conjunto=conjunto, contas=contas, dfc=_dfc_de(g, r["dt_refer"]),
            dt_ini_exerc=ini, periodo_meses=meses, ambiguo=amb))
    if not anuais:
        return None
    anuais = anuais[-cfg.janela_max:]                 # janela truncada em 10, sem discrição

    itr = None
    gi = _por_companhia("itr").get(cd_cvm)
    if gi is not None:
        vi = _visiveis("itr", data_corte)
        vi = vi[vi["cd_cvm"] == cd_cvm]
        if not vi.empty:
            r = vi.sort_values("dt_refer").iloc[-1]
            # so_acumulado: no ITR fica a linha YTD, não a do trimestre isolado.
            contas, conjunto, ini, meses, amb = _contas_de(gi, r["dt_refer"], plano,
                                                           so_acumulado=True)
            if contas:
                vd = r["versao_disco"]
                itr = Exercicio(
                    dt_refer=str(r["dt_refer"]), dt_receb=str(r["dt_receb"]),
                    versao=int(r["versao"]), versao_disco=None if pd.isna(vd) else int(vd),
                    estado=str(r["estado"]), conjunto=conjunto, contas=contas,
                    dfc=_dfc_de(gi, r["dt_refer"]),
                    dt_ini_exerc=ini, periodo_meses=meses, ambiguo=amb)

    acoes, a_refer, a_receb, a_fonte, a_ambiguo = _acoes_em(cd_cvm, data_corte)
    return LedgerPIT(cd_cvm=cd_cvm, data_corte=data_corte, plano=plano,
                     anuais=tuple(anuais), ultimo_itr=itr,
                     acoes=acoes, acoes_dt_refer=a_refer, acoes_dt_receb=a_receb,
                     acoes_fonte=a_fonte, acoes_ambiguo=a_ambiguo,
                     mes_ipca=mes_ipca_disponivel(data_corte))


def auditoria(l: LedgerPIT) -> list[str]:
    """Lista vazia = ledger limpo. Qualquer item é motivo para excluir ou declarar."""
    problemas = []
    for e in l.anuais:
        if e.dt_receb > l.data_corte:
            problemas.append(f"VAZAMENTO: {e.dt_refer} recebido em {e.dt_receb} > corte {l.data_corte}")
        if e.dt_receb < e.dt_refer:
            problemas.append(f"CORRUPÇÃO: {e.dt_refer} recebido antes do fim do exercício")
    if l.ultimo_itr and l.ultimo_itr.dt_receb > l.data_corte:
        problemas.append(f"VAZAMENTO no ITR: recebido em {l.ultimo_itr.dt_receb}")
    if l.acoes_dt_receb and l.acoes_dt_receb > l.data_corte:
        problemas.append(f"VAZAMENTO nas ações: recebidas em {l.acoes_dt_receb}")
    if l.mes_ipca >= l.data_corte[:7]:
        problemas.append(f"VAZAMENTO no IPCA: mês {l.mes_ipca} não era público em {l.data_corte}")
    if l.acoes is None:
        problemas.append("sem contagem de ações pública em T")
    if l.n_exercicios < PADRAO.janela_min:
        problemas.append(f"janela curta: {l.n_exercicios} exercícios")
    datas = [e.dt_refer for e in l.anuais]
    if len(set(datas)) != len(datas):
        problemas.append(f"exercício repetido: {datas}")
    return problemas


def relatorio(datas: tuple[str, ...] = PADRAO.datas_corte, limite_companhias: int = 0) -> pd.DataFrame:
    """Quantos ledgers montam por data de corte, e com que qualidade."""
    linhas = []
    for d in datas:
        vis = _visiveis("dfp", d)
        cds = sorted(set(vis["cd_cvm"].dropna().astype(int)))
        if limite_companhias:
            cds = cds[:limite_companhias]
        ns, cont, sem_acoes, vaz = [], 0, 0, 0
        for cd in cds:
            l = ledger_em(cd, d)
            if l is None:
                continue
            ns.append(l.n_exercicios)
            cont += l.contaminados > 0
            sem_acoes += l.acoes is None
            vaz += any(p.startswith("VAZAMENTO") for p in auditoria(l))
        linhas.append({
            "data_corte": d, "ledgers": len(ns),
            "n_exerc_mediana": int(pd.Series(ns).median()) if ns else 0,
            "n_exerc_max": max(ns) if ns else 0,
            "com_janela_minima": sum(n >= PADRAO.janela_min for n in ns),
            "com_10_exercicios": sum(n >= PADRAO.janela_max for n in ns),
            "com_contaminado": cont, "sem_acoes": sem_acoes, "VAZAMENTOS": vaz})
    return pd.DataFrame(linhas)


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--relatorio", action="store_true")
    p.add_argument("--limite", type=int, default=0, help="só as N primeiras companhias (amostra)")
    args = p.parse_args()
    if args.relatorio:
        rel = relatorio(limite_companhias=args.limite)
        print(rel.to_string(index=False))
        rel.to_parquet(DADOS / "relatorio_pit.parquet", index=False)
        if int(rel["VAZAMENTOS"].sum()):
            print("\nATENCAO: ha vazamentos. Ver auditoria().")
