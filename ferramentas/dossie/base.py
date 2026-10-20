"""Base das fichas de dossiê fora do hall (Etapa 5) — o mesmo motor e o mesmo mercado do hall, com dados próprios.

Nada aqui grava no `cvm_series.json` nem no `series_*.json` do hall: as séries do dossiê ficam em `dossie/dados/` e entram
nos dicionários do motor só em memória (`carregar`). Um ticker novo num lote quebraria o golden de 41 (test_regressao).

Fontes (doutrina §2, regra 1 do 02):
  · demonstrações e ações em circulação — CVM, DFP/ITR (A), coletadas por `coletar_cvm.main(..., arq=SERIES)`;
  · preço — COTAHIST da B3, fechamento de DATA_BASE (A); outra data só com o mercado do mesmo dia (`na_data`, `mercado`);
  · proventos por data-com — API pública da B3, cache do hall em dados/proventos_hall/ (A), com as regras do coletor do
    hall (`proventos_hall.dpa_jcp`: classe do ticker, parcelas × repetição conferidas na DMPL, restituição de capital fora,
    eventos em ações da B3 + FRE). Cache e suplemento baixados DEPOIS da data-base (`python proventos_ex.py TK` e
    `python proventos_hall.py --suplemento TK`), senão falha alto;
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
PREGAO = {"BLAU3": "BLAU", "CMIN3": "CSNMINERACAO", "HYPE3": "HYPERA", "LEVE3": "METAL LEVE", "ALLD3": "ALLIED",
          "FESA4": "FERBASA", "SHUL4": "SCHULZ", "VLID3": "VALID"}
CNPJ = {"BLAU3": "58.430.828/0001-60", "CMIN3": "08.902.291/0001-15", "HYPE3": "02.932.074/0001-91",
        "LEVE3": "60.476.884/0001-87", "ALLD3": "20.247.322/0001-47",
        "FESA4": "15.141.799/0001-03", "SHUL4": "84.693.183/0001-68", "VLID3": "33.113.309/0001-47"}



def isin_do_ticker(tk: str) -> str | None:
    """ISIN do ticker no COTAHIST mais recente (lote padrão), para escolher a classe certa entre os eventos da B3."""
    anos = sorted(COTAHIST.glob("precos_*.parquet"))
    if not anos:
        return None
    p = pd.read_parquet(anos[-1], columns=["ticker", "codbdi", "codisi"])
    x = p[(p["ticker"] == tk) & (p["codbdi"] == "02")]
    return str(x["codisi"].iloc[-1]) if len(x) else None


def eventos_em_acoes(tk: str, suplemento=None) -> list[dict]:
    """Eventos em ações do SUPLEMENTO da B3 (cache do backtest, ou `suplemento` no formato de `carregar_suplemento`), com as
    regras de `proventos_hall.eventos_em_acoes` (semântica conferida na CVM; tipo novo falha alto) e a classe pelo ISIN do
    COTAHIST. Não traz os eventos que só o FRE tem — o dossiê usa `eventos(tk)`; isto fica para a renda da carteira e testes."""
    import proventos_hall
    if suplemento is None:
        from backtest.precos.proventos_b3 import carregar_suplemento
        suplemento = carregar_suplemento()
    return proventos_hall.eventos_em_acoes(tk, suplemento, isin_do_ticker)


def eventos(tk: str) -> list[dict]:
    """Eventos em ações do ticker com data-com até DATA_BASE: suplemento da B3 (cache do hall) + os que a B3 omite e o FRE da
    CVM traz (`proventos_hall.EVENTOS_FRE`; SHUL4 2018 e 2021). O mesmo conjunto que ajusta o DPA (`proventos_b3`)."""
    import proventos_hall
    return proventos_hall.eventos(tk, DATA_BASE)


def proventos_b3(tk: str) -> tuple[dict[str, float], dict[str, float]]:
    """DPA e JCP por ano da data-com (R$ por ação de HOJE, na classe do ticker), com data-com até DATA_BASE — as regras do
    coletor do hall (`proventos_hall.dpa_jcp`, fase 3 fatia 2b): classe por `proventos_ex.CLASSE` (FESA4/SHUL4 são PN),
    linhas iguais = parcelas que somam salvo repetição conferida na DMPL (`GRUPOS_CONFERIDOS`; grupo novo falha alto),
    restituição de capital fora (§6.4), eventos da B3 + FRE com o provento do mesmo dia na base antiga. Série desde 2016."""
    import proventos_hall
    return proventos_hall.dpa_jcp(tk, DATA_BASE)


def proventos_b3_legado(tk: str) -> tuple[dict[str, float], dict[str, float]]:
    """A regra ANTERIOR à fatia 2b (cache do backtest pelo nome de pregão, `sem_repeticao` do AUD-23, restituição de capital
    somada, evento só da B3 e estrito na data-com), agora na classe do ticker. Só o relatório das financeiras a usa, até elas
    terem os grupos de linhas iguais conferidos na DMPL (fatia 4, docs/MISSOES.md 9f); e o oráculo do teste da fatia 2."""
    from backtest.precos.proventos_b3 import carregar_dinheiro, sem_repeticao
    import proventos_ex
    ev = eventos_em_acoes(tk)
    d = carregar_dinheiro()
    d = d[(d["nome"] == PREGAO[tk]) & (d["tipo_acao"] == proventos_ex.CLASSE.get(tk, "ON"))]
    d = sem_repeticao(d, ["nome", "data_com", "tipo"])
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
    """Mercado do dia (rf e π da mesma data do preço, §4): a data do hall vem de `mercado_vigente.json`; outra data vem de
    `dados/mercado_<data>.json` (Tesouro Transparente + ETTJ ANBIMA). Data sem arquivo falha alto."""
    data = data or DATA_BASE
    import mercado as mercado_hall
    if data == mercado_hall.dados()["data"]:     # AUD-78: a data do hall vem do arquivo único, não de literal
        return mercado_hall.vigente()
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
    ev = eventos(tk)
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
    SI[tk]["divergencias_b3_si"] = divergencias_b3_si(dpa, SI[tk]["dpa_statusinvest"])
    return SI[tk]


TOL_B3_SI = 0.03           # AUD-23: DPA anual da B3 contra o da StatusInvest (fonte C): acima disso, alerta


def divergencias_b3_si(dpa_b3: dict, dpa_si: dict, tol: float = TOL_B3_SI) -> list[tuple[str, float, float]]:
    """[(ano, DPA B3, DPA StatusInvest)] onde os dois diferem mais que `tol` (relativo ao maior). Os anos só de um lado
    entram: ou a B3 ou a StatusInvest não tem o ano, e isso também é divergência a olhar."""
    out = []
    for a in sorted(set(dpa_b3) | set(dpa_si)):
        x, y = float(dpa_b3.get(a, 0.0)), float(dpa_si.get(a, 0.0))
        if abs(x - y) > tol * max(abs(x), abs(y), 1e-12):
            out.append((a, x, y))
    return out


def jcp_share(tk: str) -> float:
    s = SI[tk]
    tot = sum(s["dpa_por_ano_datacom"].get(a, 0) for a in ("2024", "2025"))
    j = sum(s["jcp_por_ano_datacom"].get(a, 0) for a in ("2024", "2025"))
    return j / tot if tot else 0.0


def defasagem(tk: str) -> float:
    """Meses data-com → pagamento, média ponderada pelo valor (datas da StatusInvest, fonte C só para datas)."""
    return defasagem_meses(tk, si={tk: SI[tk]})
