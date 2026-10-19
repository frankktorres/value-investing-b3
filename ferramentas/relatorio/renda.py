"""Provento por ação dos últimos 12 meses, pela data-com (API da B3 GetListedCashDividends, nota A).

Conta da renda do painel da carteira: quantidade de HOJE × provento por ação de HOJE. Por isso o provento com data-com
anterior a uma bonificação ou desdobramento (até a data do preço) é dividido pelo multiplicador, como em
`dossie.base.proventos_b3` (mesma convenção: data-com do provento ANTES da do evento). Janela: data-com em
(data − 12 meses, data]. Data-com depois da data do preço = anunciado, ainda não conta (sai à parte).

Só dinheiro que é renda: dividendo, JCP e rendimento. Restituição de capital e o que mais vier sai em `ignorados`.
Duplicata da B3 (a mesma linha repetida, AUD-23): mesma data-com e tipo com valor a até 1% conta uma vez
(`backtest.precos.proventos_b3.sem_repeticao`).
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

RENDA = {"DIVIDENDO", "JRS CAP PROPRIO", "RENDIMENTO"}
JCP = "JRS CAP PROPRIO"
DUPLICATA_TOL = 0.01


@dataclass
class Renda12m:
    total: float                      # R$ por ação de hoje, data-com na janela
    jcp: float                        # parte do total que é JCP (bruto; o IR sai no painel)
    eventos: list[dict] = field(default_factory=list)
    futuros: list[dict] = field(default_factory=list)      # data-com depois da data do preço
    ignorados: list[dict] = field(default_factory=list)    # dinheiro que não é renda (restituição de capital...)


def inicio_da_janela(data: str) -> str:
    """'2026-10-15' → '2025-10-15' (exclusivo)."""
    return f"{int(data[:4]) - 1:04d}{data[4:]}"


def _sem_repeticao(regs: list[dict]) -> list[dict]:
    out: list[dict] = []
    for r in sorted(regs, key=lambda r: (r["data_com"], r["tipo"], r["por_acao"])):
        a = out[-1] if out else None
        if a and (a["data_com"], a["tipo"]) == (r["data_com"], r["tipo"]) and a["por_acao"] > 0 \
                and abs(r["por_acao"] / a["por_acao"] - 1) <= DUPLICATA_TOL:
            continue
        out.append(r)
    return out


def provento_12m(regs: list[dict], classe: str, data: str, eventos: Sequence[dict] = ()) -> Renda12m:
    """`regs` no formato de `proventos_ex.registros`; `eventos` no de `dossie.base.eventos_em_acoes`."""
    ini = inicio_da_janela(data)
    da_classe = [dict(r, por_acao=r["valor"] / (r["lote"] or 1.0)) for r in regs
                 if r["tipo_acao"] == classe and r["data_com"]]
    out = Renda12m(0.0, 0.0)
    for r in _sem_repeticao(da_classe):
        if r["data_com"] <= ini:
            continue
        if r["data_com"] > data:
            out.futuros.append(r)
            continue
        if r["tipo"] not in RENDA:
            out.ignorados.append(r)
            continue
        v = r["por_acao"]
        for x in eventos:
            if r["data_com"] < x["data_com"] <= data:
                v /= x["multiplicador"]
        out.eventos.append(dict(r, ajustado=v))
        out.total += v
        if r["tipo"] == JCP:
            out.jcp += v
    return out
