"""Mês em que cada provento cai: calendário de pagamento do painel da carteira.

A API da B3 (nota A) dá a data-com, não a de pagamento. A data de pagamento vem da StatusInvest (nota C, `series_vigente`,
evento casado pela data-com; mais de uma data na mesma data-com → casa também pelo valor). Sem ela, a data é estimada =
data-com + defasagem média do ticker (`defasagem.defasagem_meses`, medida na mesma StatusInvest → também C). Ticker fora da
StatusInvest fica "sem data" — nunca um mês inventado. É informativo: a renda do painel continua contada pela data-com.
"""
from __future__ import annotations

from datetime import date, timedelta

STATUSINVEST = "StatusInvest"
ESTIMADO = "estimado"
SEM_DATA = ""
VALOR_TOL = 0.02
DIAS_POR_MES = 30.4375                # o mesmo de defasagem.meses_entre


def _iso(br) -> str:
    """'03/09/2026' → '2026-09-03'; '-', vazio ou outro formato → ''."""
    s = (br or "").strip()
    return f"{s[6:10]}-{s[3:5]}-{s[0:2]}" if len(s) == 10 and s[2] == "/" and s[5] == "/" else ""


def data_de_pagamento(ev: dict, si_eventos: list[dict], defasagem: float | None) -> tuple[str, str]:
    """(data AAAA-MM-DD ou '', origem). `ev` no formato de `renda.provento_12m` (data_com ISO, por_acao sem ajuste)."""
    com = ev["data_com"]
    cands = [e for e in si_eventos if _iso(e.get("data_com")) == com and _iso(e.get("pagamento"))]
    datas = {_iso(e["pagamento"]) for e in cands}
    if len(datas) > 1 and ev["por_acao"] > 0:
        datas = {_iso(e["pagamento"]) for e in cands
                 if abs((e.get("valor") or 0) / ev["por_acao"] - 1) <= VALOR_TOL}
    if len(datas) == 1:
        return datas.pop(), STATUSINVEST
    if defasagem is None:
        return SEM_DATA, SEM_DATA
    d = date.fromisoformat(com) + timedelta(days=round(defasagem * DIAS_POR_MES))
    return d.isoformat(), ESTIMADO


def anotar(renda, si_eventos: list[dict], defasagem: float | None, data: str | None = None) -> None:
    """Põe `pagamento` e `pag_origem` em cada provento contado e em cada anunciado de um `Renda12m`.

    Com `data` (a do preço), junta aos anunciados o que só a StatusInvest tem com data-com depois dela (a API da B3 às vezes
    demora a listar): marcado `so_statusinvest`, nota C, nunca entra na renda de 12 meses."""
    for ev in (*renda.eventos, *renda.futuros):
        ev["pagamento"], ev["pag_origem"] = data_de_pagamento(ev, si_eventos, defasagem)
    if data is None:
        return
    na_b3 = {(e["data_com"], e["tipo"]) for e in (*renda.eventos, *renda.futuros, *renda.ignorados)}
    for e in si_eventos:
        com, tipo = _iso(e.get("data_com")), TIPO_SI.get((e.get("tipo") or "").strip())
        if com > data and (com, tipo) not in na_b3 and tipo and (e.get("valor") or 0) > 0:
            ev = {"data_com": com, "tipo": tipo, "por_acao": float(e["valor"]), "so_statusinvest": True}
            ev["pagamento"], ev["pag_origem"] = data_de_pagamento(ev, [e], defasagem)
            renda.futuros.append(ev)


TIPO_SI = {"Dividendo": "DIVIDENDO", "JCP": "JRS CAP PROPRIO", "Rend. Tributado": "RENDIMENTO"}   # amortização fica fora


def meses(ini: str, fim: str) -> list[str]:
    """'2025-11', '2026-02' → ['2025-11', '2025-12', '2026-01', '2026-02']."""
    a, m = int(ini[:4]), int(ini[5:7])
    out = []
    while f"{a:04d}-{m:02d}" <= fim:
        out.append(f"{a:04d}-{m:02d}")
        a, m = (a + 1, 1) if m == 12 else (a, m + 1)
    return out
