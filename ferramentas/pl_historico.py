"""P/L histórico de fim de exercício pela CVM + COTAHIST — uma conta para o hall (lotes) e o dossiê (fase 3, fatia 3, 20/10/2026).

P/L do ano = fechamento do último pregão até o fim do exercício (B3, COTAHIST, lote padrão) × ações do DFP ÷ lucro do
controlador (CVM); mediana dos anos com 0 < P/L < 40 (o corte do `pl_hist` antigo, que lia o P/L da StatusInvest, nota C).
Evento em ações aprovado até o fim do exercício cuja data-com é o dia do fechamento usado ou depois: o DFP já conta as ações
novas, o preço ainda é "com" (no dia da data-com o papel é da ação antiga, como em `proventos_hall`) → as ações voltam à base
antiga. Data-com no último pregão do ano (SLCE3 30/12/2021 e 30/12/2025) conta (adversário, 20/10). Exercício fora do ano
civil (SMTO3, abr–mar: o DFP de mar/2026 é o "2026" da CVM) usa `mes_fim`.

No hall, sem o COTAHIST no disco (clone limpo), o valor vem do snapshot versionado (`derivados_zip`, chave `pl_hist.<TK>`).
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


def mediana(tk: str, anual: dict, eventos: list[dict], escala, mes_fim: int = 12, fechamento=fechamento_ate) -> float | None:
    """A conta (o dossiê passa a sua escala pelo FRE; o hall, a das ações registradas)."""
    xs = []
    for ano, d in anual.items():
        lucro, acoes = d.get("lucro_controlador") or d.get("lucro"), d.get("acoes")
        if not (lucro and acoes and lucro > 0):
            continue
        fim = fim_do_exercicio(ano, mes_fim)
        f = fechamento(tk, fim)
        if not f:
            continue
        dia, px = f
        n = escala(acoes)
        for x in eventos:
            if x["aprovacao"] <= fim and x["data_com"] >= dia:
                n /= x["multiplicador"]
        pl = px * n / (lucro * 1000)          # lucro em R$ mil
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
    v = derivados_zip.obter(f"pl_hist.{tk}", [f"precos_{a}.parquet" for a in ANOS], calcular, pasta=COTAHIST)
    return insumos_a.registrar(tk, "pl_hist", v, insumos_a.PL_HIST_CVM) if v is not None else None
