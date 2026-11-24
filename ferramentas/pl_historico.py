"""P/L histórico de fim de exercício pela CVM + COTAHIST — uma conta para o hall (lotes) e o dossiê (fase 3, fatia 3, 20/10/2026).

P/L do ano = fechamento do último pregão até o fim do exercício (B3, COTAHIST, lote padrão) × ações do DFP ÷ lucro do
controlador (CVM); mediana dos anos com 0 < P/L < 40 (o corte do `pl_hist` antigo, que lia o P/L da StatusInvest, nota C).
Evento em ações aprovado até o fim do exercício cuja data-com é o dia do fechamento usado ou depois: o DFP já conta as ações
novas, o preço ainda é "com" (no dia da data-com o papel é da ação antiga, como em `proventos_hall`) → as ações voltam à base
antiga. Data-com no último pregão do ano (SLCE3 30/12/2021 e 30/12/2025) conta (adversário, 20/10). Exercício fora do ano
civil (SMTO3, abr–mar: o DFP de mar/2026 é o "2026" da CVM) usa `mes_fim`.

2016–19 (B30, 20/10): o DFP antes de 2020 não traz a composição do capital → P/L = fechamento ÷ LPA básico da classe do
ticker (DRE, conta 3.99.01.xx, mesmo DFP). O LPA usa a média ponderada das ações; ele só entra se as ações que implica
(lucro ÷ LPA) ficarem a menos de `TOL_LPA` das ações do primeiro DFP com composição, levadas à base de preço do ano pelos
eventos entre os dois fechamentos — pega erro de escala da CVM (TIMS3 2020: LPA 0,08 com lucro ÷ ações = 0,76). Fora da
tolerância, ou com evento que torna ambígua a base do LPA (ver `mediana`), o ano fica fora (não se inventa ação).

No hall, sem o COTAHIST ou os DFP 2016–19 no disco (clone limpo), o valor vem do snapshot versionado (`derivados_zip`, chave
`pl_hist.<TK>`).
"""
from __future__ import annotations

import calendar
import math
import statistics as st
from functools import lru_cache
from pathlib import Path

AQUI = Path(__file__).resolve().parent
COTAHIST = AQUI / "backtest" / "dados" / "cotahist"
ANOS = range(2016, 2027)                     # parquets que a conta pode ler (2026: SMTO3 e o pregão mais recente)
DFP = AQUI / "dados" / "cvm"
ANOS_LPA = range(2016, 2020)                 # DFP sem composição do capital → LPA básico (B30)
TOL_LPA = 1.25                               # ações implícitas no LPA × ações do DFP com composição (razão máxima)
CLASSE_LPA = {"3": "ON", "4": "PN", "5": "PNA", "6": "PNB"}


@lru_cache(maxsize=None)
def _dfp(ano: int, nome: str):
    """Arquivo `dfp_cia_aberta_<nome>_<ano>.csv` (nome "" = o índice, com DT_RECEB) do ZIP do DFP."""
    import io
    import zipfile
    import pandas as pd
    z = zipfile.ZipFile(DFP / f"dfp_{ano}.zip")
    alvo = f"dfp_cia_aberta_{nome + '_' if nome else ''}{ano}.csv".lower()
    n = next(x for x in z.namelist() if x.lower().endswith(alvo))
    return pd.read_csv(io.BytesIO(z.read(n)), sep=";", encoding="latin-1", dtype=str)


def publicacao_dfp(tk: str, ano: int) -> str | None:
    """Data de entrega (DT_RECEB) da versão do DFP do exercício que a conta lê (a mais recente)."""
    from coletar_cvm import EMPRESAS, filtra
    d = filtra(_dfp(ano, ""), EMPRESAS[tk][0]) if tk in EMPRESAS else None
    return str(d["DT_RECEB"].iloc[-1])[:10] if d is not None and len(d) else None


def lpa_basico(tk: str, ano: int) -> float | None:
    """LPA básico (R$/ação, sem a escala do arquivo) da classe do ticker no DFP do exercício: consolidado; sem ele ou com ele
    zerado, individual (VLID3 2016–17: con 0, ind preenchido — AUD-68: zero com lucro é linha não preenchida). None sem linha
    ou com LPA ≤ 0 nos dois (FLRY3 2023–25 entrega zero)."""
    from coletar_cvm import EMPRESAS, filtra
    classe = CLASSE_LPA.get(tk[4:])
    if classe is None or tk not in EMPRESAS:
        return None
    for suf in ("con", "ind"):
        d = filtra(_dfp(ano, f"DRE_{suf}"), EMPRESAS[tk][0])
        if d.empty:
            continue
        d = d[d["ORDEM_EXERC"].str.upper().str.replace("Ú", "U").str.startswith("ULTIMO")
              & d["CD_CONTA"].str.match(r"3\.99\.01\.\d+$") & (d["DS_CONTA"].str.strip().str.upper() == classe)]
        if len(d) and float(d["VL_CONTA"].iloc[-1]) > 0:
            return float(d["VL_CONTA"].iloc[-1])
    return None


@lru_cache(maxsize=None)
def _precos(ano: int):
    import pandas as pd
    p = pd.read_parquet(COTAHIST / f"precos_{ano}.parquet", columns=["data", "codbdi", "ticker", "preult"])
    return p[p["codbdi"] == "02"]


def fim_do_exercicio(ano: int | str, mes_fim: int = 12) -> str:
    ano = int(ano)
    return f"{ano}-{mes_fim:02d}-{calendar.monthrange(ano, mes_fim)[1]:02d}"


def fechamento_ate(tk: str, data: str) -> tuple[str, float] | None:
    """(pregão, PREULT) do último pregão do ticker no ano de `data`, até `data` inclusive."""
    p = _precos(int(data[:4]))
    x = p[(p["ticker"] == tk) & (p["data"].astype(str).str[:10] <= data)].sort_values("data")
    return (str(x["data"].iloc[-1])[:10], float(x["preult"].iloc[-1])) if len(x) else None


def _fator_pos(eventos: list[dict], fim: str, dia: str) -> float:
    """Eventos aprovados até o fim do exercício com data-com no dia do fechamento ou depois (o DFP já os conta; o preço não)."""
    return math.prod(x["multiplicador"] for x in eventos if x["aprovacao"] <= fim and x["data_com"] >= dia)


def mediana(tk: str, anual: dict, eventos: list[dict], escala, mes_fim: int = 12, fechamento=fechamento_ate,
            lpa=lpa_basico, publicacao=publicacao_dfp) -> float | None:
    """A conta (o dossiê passa a sua escala pelo FRE; o hall, a das ações registradas). Ano sem ações e em `ANOS_LPA`: LPA.

    No ano pelo LPA, evento com data-com no fechamento ou depois e aprovado até a entrega do DFP deixa ambíguo se o LPA veio
    reexpresso (CPC 41 §64) → o ano fica fora; aprovado depois da entrega, o LPA está na base do preço (adversário, 20/10).
    Classe: 2016–19 é o P/L da classe do ticker; 2020+ é preço × todas as ações ÷ lucro — com PN de dividendo 10% maior a
    diferença é de 3–7% (FESA4, SHUL4, VIVT3 enquanto havia PN), dentro da trava; declarado, não corrigido."""
    base, ref = {}, None                    # ano → (dia, preço, lucro, fim); ref = (dia, ações na base do preço) do 1º DFP com ações
    for ano, d in sorted(anual.items()):
        lucro = d.get("lucro_controlador") or d.get("lucro")
        if not ((lucro and lucro > 0) or (ref is None and d.get("acoes"))):
            continue
        fim = fim_do_exercicio(ano, mes_fim)
        f = fechamento(tk, fim)
        if not f:
            continue
        if ref is None and d.get("acoes"):          # a referência só precisa de ações e preço, não de lucro (VLID3 2020)
            ref = (f[0], escala(d["acoes"]) / _fator_pos(eventos, fim, f[0]))
        if lucro and lucro > 0:
            base[ano] = (*f, lucro, fim)
    xs = []
    for ano, (dia, px, lucro, fim) in base.items():
        acoes = anual[ano].get("acoes")
        if acoes:
            pl = px * escala(acoes) / _fator_pos(eventos, fim, dia) / (lucro * 1000)     # lucro em R$ mil
        elif int(ano) in ANOS_LPA and ref and ref[0] > dia and (v := lpa(tk, int(ano))):
            entrega = publicacao(tk, int(ano))
            if not entrega or any(x["data_com"] >= dia and x["aprovacao"] <= entrega for x in eventos):
                continue
            esperadas = ref[1] / math.prod(x["multiplicador"] for x in eventos if dia <= x["data_com"] < ref[0])
            if abs(math.log(lucro * 1000 / v / esperadas)) > math.log(TOL_LPA):
                continue
            pl = px / v
        else:
            continue
        if 0 < pl < 40:
            xs.append(pl)
    return st.median(xs) if xs else None


def escala_por_referencia(ref: float):
    """Formulário da CVM em milhares ou em unidades: vale q ou q × 1000, o mais perto (em log) das ações registradas do
    lote (mesmo critério de `tests/test_fase3_procedencia.test_acoes_registradas_conferem_com_o_dfp`)."""
    return lambda q: min((q, q * 1000), key=lambda x: abs(math.log(x / ref)))


def do_hall(tk: str, ref_acoes: float, mes_fim: int = 12) -> float | None:
    """P/L histórico do ticker do hall (não financeira), registrado em `insumos_a`. Ticker em units não é suportado (o preço é
    da unit e as ações do DFP são ações): falha alto."""
    import derivados_zip
    import insumos_a
    import proventos_hall
    from motor_nao_financeiras import CVM
    if (CVM[tk].get("acoes_por_unit") or 1) != 1:
        raise ValueError(f"{tk}: P/L histórico em units não suportado")

    def calcular():
        return mediana(tk, CVM[tk]["anual"], proventos_hall.eventos(tk), escala_por_referencia(ref_acoes), mes_fim)
    # caminho absoluto dos DFP: `pasta / caminho absoluto` é o próprio caminho → exige os dois conjuntos
    entradas = [f"precos_{a}.parquet" for a in ANOS] + [str(DFP / f"dfp_{a}.zip") for a in ANOS_LPA]
    v = derivados_zip.obter(f"pl_hist.{tk}", entradas, calcular, pasta=COTAHIST)
    return insumos_a.registrar(tk, "pl_hist", v, insumos_a.PL_HIST_CVM) if v is not None else None
