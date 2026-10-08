"""Base das fichas de dossiê fora do hall (Etapa 5) — o mesmo motor e o mesmo mercado do hall, com dados próprios.

Nada aqui grava no `cvm_series.json` nem no `series_*.json` do hall: as séries do dossiê ficam em `dossie/dados/` e entram
nos dicionários do motor só em memória (`carregar`). Um ticker novo num lote quebraria o golden de 41 (test_regressao).

Fontes (doutrina §2, regra 1 do 02):
  · demonstrações e ações em circulação — CVM, DFP/ITR (A), coletadas por `coletar_cvm.main(..., arq=SERIES)`;
  · preço — COTAHIST da B3, fechamento de DATA_BASE (A); outra data só com o mercado do mesmo dia (`na_data`, `mercado`);
  · proventos por data-com — API pública da B3, cache do backtest (A);
  · data de pagamento, só para a defasagem do §6.3 — StatusInvest (C; a B3 não publica a data de pagamento nessa API).
"""
from __future__ import annotations

import io
import json
import pathlib
import statistics as st
import zipfile
from collections import defaultdict
from contextlib import contextmanager

import pandas as pd

from defasagem import defasagem_meses
from montar_series import series as series_statusinvest
from motor_financeiras import Mercado
from motor_nao_financeiras import CVM, SI

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
SERIES = AQUI / "dados" / "cvm_series_dossie.json"
COTAHIST = RAIZ / "backtest" / "dados" / "cotahist"
ZIP = RAIZ / "dados" / "cvm"
DATA_BASE = "2026-10-02"      # o mesmo dia do hall e da triagem: rf e preço do mesmo dia (§4)

# nome de pregão (= NOMRES do COTAHIST = tradingName da B3) e CNPJ (FCA/FRE)
PREGAO = {"BLAU3": "BLAU", "CMIN3": "CSNMINERACAO", "HYPE3": "HYPERA", "LEVE3": "METAL LEVE"}
CNPJ = {"BLAU3": "58.430.828/0001-60", "CMIN3": "08.902.291/0001-15", "HYPE3": "02.932.074/0001-91",
        "LEVE3": "60.476.884/0001-87"}


# Tipos de evento com semântica conferida contra a contagem de ações da CVM (fonte A). Nos dois o `fator_b3` é o % de ações
# novas sobre as antigas, e o multiplicador da quantidade é 1 + fator/100:
#   · BONIFICACAO — BLAU 30,0 em 2026 = 30 novas por 100, batendo 177,7 → 228,8 mi no DFP;
#   · DESDOBRAMENTO — BBAS 100,0 em 15/04/2024 (2 por 1): DFP 2023 → 2024, 2.865.417.020 → 5.730.834.040 ações integralizadas
#     (×2 exato). O fator NÃO é a razão (seria ×100): MGLU 300,0 em 2020 é o 4 por 1.
# Grupamento (o fator é a razão, ex.: MGLU 0,1 em 2024) e os demais tipos falham alto em vez de ajustar errado.
SEMANTICA_CONFERIDA = ("BONIFICACAO", "DESDOBRAMENTO", "GRUPAMENTO")
# par desdobramento + grupamento na mesma data, conferido contra a contagem de ações da CVM (FRE): LEVE3 14/05/2012,
# 42.769.500 → 128.308.500 ações (×3 = 300 × 0,01)
PARES_CONFERIDOS = {("LEVE", "2012-05-14")}
# GRUPAMENTO (08/10/2026, dossiê LEVE3): a B3 publica o fator como RAZÃO nova ÷ antiga (MGLU 2024: 0,1 = 10 para 1), não
# como percentual — multiplicador = fator, e fator >= 1 falha alto. Na LEVE3 o evento é de 14/05/2012 (desdobramento ×300
# + grupamento ÷100 na mesma data = ×3 líquido), fora da janela do dossiê; não move número.


def isin_do_ticker(tk: str) -> str | None:
    """ISIN do ticker no COTAHIST mais recente (lote padrão), para escolher a classe certa entre os eventos da B3."""
    anos = sorted(COTAHIST.glob("precos_*.parquet"))
    if not anos:
        return None
    p = pd.read_parquet(anos[-1], columns=["ticker", "codbdi", "codisi"])
    x = p[(p["ticker"] == tk) & (p["codbdi"] == "02")]
    return str(x["codisi"].iloc[-1]) if len(x) else None


def eventos_em_acoes(tk: str, suplemento=None) -> list[dict]:
    """Eventos em ações da B3 (GetListedSupplementCompany, fonte A) pela raiz do ticker, com o multiplicador da quantidade
    de ações (`SEMANTICA_CONFERIDA`); qualquer outro tipo falha alto. `suplemento` = DataFrame no formato de
    `carregar_suplemento` (testes)."""
    if suplemento is None:
        from backtest.precos.proventos_b3 import carregar_suplemento
        suplemento = carregar_suplemento()
    s = suplemento[suplemento["raiz"] == tk[:4]]
    isins = sorted({str(i) for i in s.get("isin", []) if str(i)})
    proprio = isin_do_ticker(tk) if len(isins) > 1 else None
    if proprio in isins:
        # a classe do próprio ticker decide (LEVE3: a ON tem o par de 2012; a PN, extinta, só os eventos de 1992)
        s = s[s["isin"] == proprio]
        chave = lambda x, f: (x["tipo"], x["data_com"], f)
    elif len(isins) > 1:
        # com o ISIN: cada classe tem o seu conjunto de eventos; conjuntos iguais = o mesmo evento repetido (conta uma vez);
        # conjuntos diferentes = fator diferente por classe, sem semântica conferida. Isso aceita dois eventos do MESMO tipo
        # na mesma data com fatores diferentes (LEVE3, 28/04/1992: bonificações de 20% e 1.080% em ON e PN)
        por_isin = {i: sorted((r["tipo"], str(r["data_com"])[:10], float(r["fator_b3"])) for _, r in s[s["isin"] == i].iterrows())
                    for i in isins}
        if len({tuple(v) for v in por_isin.values()}) > 1:
            raise NotImplementedError(f"{tk}: eventos diferentes por classe {sorted(por_isin)} — ajustar à mão")
        s = s[s["isin"] == isins[0]]
        chave = lambda x, f: (x["tipo"], x["data_com"], f)
    else:
        chave = lambda x, f: (x["tipo"], x["data_com"])
    out = {}
    for _, e in s.iterrows():
        if e["tipo"] not in SEMANTICA_CONFERIDA:
            raise NotImplementedError(f"{tk}: evento {e['tipo']} sem semântica conferida — ajustar à mão")
        f = float(e["fator_b3"])
        if not f > 0:
            raise ValueError(f"{tk}: {e['tipo']} de {e['data_com']} com fator {e['fator_b3']!r}")
        if e["tipo"] == "GRUPAMENTO" and not f < 1:
            raise ValueError(f"{tk}: GRUPAMENTO de {e['data_com']} com fator {f} >= 1 (a B3 publica a razão, ex. 0,1)")
        x = {"tipo": e["tipo"], "data_com": str(e["data_com"])[:10], "aprovacao": str(e["data_aprovacao"])[:10],
             "multiplicador": f if e["tipo"] == "GRUPAMENTO" else 1 + f / 100}
        # a B3 repete o evento por ISIN (ON, PN, UNIT): um só por (tipo, data-com), senão o multiplicador entra ao quadrado
        # (adversário, 07/10); fatores diferentes entre classes na mesma data não têm semântica conferida → falha alto
        k = chave(x, f)
        if k in out and out[k]["multiplicador"] != x["multiplicador"]:
            raise NotImplementedError(f"{tk}: {k} com fatores diferentes por classe — ajustar à mão")
        out[k] = x
    # desdobramento + grupamento na MESMA data-com: a B3 não publica o par de um jeito só (LEVE3 2012: 29.900% e 0,01 = ×3; TIMS3
    # 2025: 100 e 0,01 = ×1; VIVT3 2025: 80 e 0,025 = ×2 — adversário, 08/10). Só passa o par conferido contra a contagem de ações
    # da CVM; o resto falha alto
    datas = {}
    for x in out.values():
        datas.setdefault(x["data_com"], set()).add(x["tipo"])
    for d, tipos in datas.items():
        if {"DESDOBRAMENTO", "GRUPAMENTO"} <= tipos and (tk[:4], d) not in PARES_CONFERIDOS:
            raise NotImplementedError(f"{tk}: desdobramento e grupamento na mesma data ({d}) sem conferência na CVM — ajustar à mão")
    return list(out.values())


def proventos_b3(tk: str) -> tuple[dict[str, float], dict[str, float]]:
    """DPA e JCP por ano da data-com (R$ por ação ON de HOJE), da API da B3: o provento com data-com anterior a uma
    bonificação ou desdobramento é dividido pelo multiplicador, para comparar com a quantidade atual de ações."""
    from backtest.precos.proventos_b3 import carregar_dinheiro
    ev = eventos_em_acoes(tk)
    d = carregar_dinheiro()
    d = d[(d["nome"] == PREGAO[tk]) & (d["tipo_acao"] == "ON")]
    dpa, jcp = defaultdict(float), defaultdict(float)
    for _, e in d.iterrows():
        com = str(e["data_com"])[:10]
        v = float(e["valor"])
        for x in ev:
            if com < x["data_com"]:
                v /= x["multiplicador"]
        dpa[com[:4]] += v
        if "JRS" in str(e["tipo"]).upper():
            jcp[com[:4]] += v
    return dict(sorted(dpa.items())), dict(sorted(jcp.items()))


# Correções declaradas do dado da CVM (cada uma conferida contra outra fonte A; o anexo do dossiê imprime a lista)
CORRECOES_ACOES = {
    # composição do capital do DFP 2025 informa 54.267.151.083 ações; o FRE 2025 (capital integralizado) informa
    # 5.485.338.835 e o ITR de jun/2026, 5.402.435.438 sem tesouraria → erro de unidade (×10) no formulário
    ("CMIN3", "2025"): (5_426_715_108, "DFP 2025 informa 54,27 bi (×10); FRE 2025 = 5,485 bi integralizadas"),
}


def _precos(ano: int) -> pd.DataFrame:
    p = pd.read_parquet(COTAHIST / f"precos_{ano}.parquet", columns=["data", "codbdi", "ticker", "preult"])
    return p[p["codbdi"] == "02"]


@contextmanager
def na_data(data: str | None):
    """Roda o dossiê noutra data-base (v2.3: veredito novo = data nova, o registro é append-only). Preço e mercado
    passam a ser os dessa data; ao sair, volta a DATA_BASE padrão."""
    global DATA_BASE
    antes = DATA_BASE
    DATA_BASE = data or antes
    try:
        yield DATA_BASE
    finally:
        DATA_BASE = antes


def mercado(data: str | None = None) -> Mercado:
    """Mercado do dia (rf e π da mesma data do preço, §4): 02/10 é o do hall (`lote1_bancos.MK`); outra data vem de
    `dados/mercado_<data>.json` (Tesouro Transparente + ETTJ ANBIMA). Data sem arquivo falha alto."""
    data = data or DATA_BASE
    if data == "2026-10-02":
        from lote1_bancos import MK
        return MK
    arq = RAIZ / "dados" / f"mercado_{data}.json"
    if not arq.exists():
        raise FileNotFoundError(f"sem mercado da data {data}: coletar rf e π do mesmo dia em {arq.name}")
    m = json.loads(arq.read_text(encoding="utf-8"))
    return Mercado(rf_real=m["rf_real"], pi=m["pi"], data=data)


def preco(tk: str, data: str | None = None) -> float:
    """Fechamento (PREULT, lote padrão) do COTAHIST na data — erro alto se o pregão não existir."""
    data = data or DATA_BASE
    p = _precos(int(data[:4]))
    x = p[(p["ticker"] == tk) & (p["data"].astype(str).str[:10] == data)]
    if x.empty:
        raise ValueError(f"{tk}: sem fechamento no COTAHIST em {data}")
    return float(x["preult"].iloc[-1])


def fechamento_do_ano(tk: str, ano: int) -> float | None:
    p = _precos(ano)
    x = p[p["ticker"] == tk].sort_values("data")
    return float(x["preult"].iloc[-1]) if len(x) else None


def acoes_fre(tk: str, ano: int = 2026) -> float:
    """Ações do capital integralizado no FRE (versão mais recente; fonte A, sempre em unidades)."""
    z = zipfile.ZipFile(ZIP / f"fre_{ano}.zip")
    df = pd.read_csv(io.BytesIO(z.read(f"fre_cia_aberta_capital_social_{ano}.csv")), sep=";", encoding="latin-1", dtype=str)
    d = df[(df["CNPJ_Companhia"] == CNPJ[tk]) & (df["Tipo_Capital"] == "Capital Integralizado")]
    if d.empty:
        raise ValueError(f"{tk}: sem capital integralizado no FRE {ano}")
    d = d.sort_values("Versao", key=lambda s: s.astype(int)).iloc[-1]
    return float(d["Quantidade_Total_Acoes"])


def escala(tk: str, q: float) -> float:
    """Há formulário da CVM em milhares e há small cap com < 100 mi de ações em unidades: um corte fixo erra uma das
    duas (adversário, 07/10). Vale q ou q × 1000, o mais perto (em log) das ações integralizadas do FRE."""
    import math
    ref = acoes_fre(tk)
    return min((q, q * 1000), key=lambda x: abs(math.log(x / ref)))


def acoes_itr(tk: str, ano: int = 2026, mes: int = 6) -> float:
    """Ações em circulação (sem tesouraria) na composição do capital do ITR, pelo CNPJ."""
    z = zipfile.ZipFile(ZIP / f"itr_{ano}.zip")
    n = [x for x in z.namelist() if "composicao" in x][0]
    df = pd.read_csv(io.BytesIO(z.read(n)), sep=";", encoding="latin-1", dtype=str)
    d = df[(df["CNPJ_CIA"] == CNPJ[tk]) & (df["DT_REFER"].str[5:7] == f"{mes:02d}")]
    if d.empty:
        raise ValueError(f"{tk}: sem composição do capital no ITR {mes:02d}/{ano}")
    d = d.sort_values("VERSAO", key=lambda s: s.astype(int)).iloc[-1]
    q = float(d["QT_ACAO_TOTAL_CAP_INTEGR"]) - float(d["QT_ACAO_TOTAL_TESOURO"] or 0)
    return escala(tk, q)


def pl_hist(tk: str) -> float | None:
    """Mediana do P/L de fim de exercício (fechamento do último pregão do ano × ações do DFP ÷ lucro do controlador),
    só anos com 0 < P/L < 40 — o mesmo corte do `pl_hist` do hall, mas com fonte A em vez do agregador."""
    a = CVM[tk]["anual"]
    ev = eventos_em_acoes(tk)
    xs = []
    for ano, d in a.items():
        lucro, acoes = d.get("lucro_controlador") or d.get("lucro"), d.get("acoes")
        px = fechamento_do_ano(tk, int(ano)) if lucro and acoes else None
        if px and lucro > 0:
            n = escala(tk, acoes)
            for x in ev:      # aprovada até o fim do ano e ex depois dele: o DFP já conta as ações novas, o preço ainda não
                if x["aprovacao"] <= f"{ano}-12-31" < x["data_com"]:
                    n /= x["multiplicador"]
            pl = px * n / (lucro * 1000)          # lucro em R$ mil
            if 0 < pl < 40:
                xs.append(pl)
    return st.median(xs) if xs else None


@contextmanager
def isolado(tk: str):
    """Ticker que também está no hall (HYPE3): `carregar` troca SI[tk] (e põe CVM[tk] se faltar) na memória compartilhada com
    os lotes; na saída do bloco o que havia antes volta — senão um lote avaliado depois no mesmo processo (pytest, golden de
    41) usaria os proventos do dossiê."""
    antes = {nome: (d[tk] if tk in d else _AUSENTE) for nome, d in (("SI", SI), ("CVM", CVM))}
    try:
        yield
    finally:
        for nome, d in (("SI", SI), ("CVM", CVM)):
            if antes[nome] is _AUSENTE:
                d.pop(tk, None)
            else:
                d[tk] = antes[nome]


_AUSENTE = object()


def carregar(tk: str, dia_statusinvest: str = "2026-10-07") -> dict:
    """Põe as séries do ticker nos dicionários do motor (em memória) e devolve o que foi usado, para o anexo. Para ticker do
    hall, chamar dentro de `isolado(tk)`."""
    if tk not in CVM:
        CVM[tk] = json.loads(SERIES.read_text(encoding="utf-8"))[tk]
        for (t, ano), (n, _) in CORRECOES_ACOES.items():
            if t == tk:
                CVM[tk]["anual"][ano]["acoes"] = n
    dpa, jcp = proventos_b3(tk)
    si_c = series_statusinvest(tk, dia_statusinvest)
    SI[tk] = {"dpa_por_ano_datacom": dpa, "jcp_por_ano_datacom": jcp, "eventos": si_c["eventos"],
              "dpa_statusinvest": {str(k): v for k, v in si_c["dpa_por_ano_datacom"].items()}}
    return SI[tk]


def jcp_share(tk: str) -> float:
    s = SI[tk]
    tot = sum(s["dpa_por_ano_datacom"].get(a, 0) for a in ("2024", "2025"))
    j = sum(s["jcp_por_ano_datacom"].get(a, 0) for a in ("2024", "2025"))
    return j / tot if tot else 0.0


def defasagem(tk: str) -> float:
    """Meses data-com → pagamento, média ponderada pelo valor (datas da StatusInvest, fonte C só para datas)."""
    return defasagem_meses(tk, si={tk: SI[tk]})
