"""Eventos societários que o balanço do LTM pode ainda não conter (23/11/2026).

Os fatos (follow-on, dividendo extraordinário) ficam em `dados/eventos_societarios.json`, com fonte, e não no código dos
lotes. O follow-on só entra no patrimônio e nas ações se o balanço do LTM ainda NÃO o contiver: antes o lote somava sempre a
oferta de jul/2026, e com o LTM de 30/09 (que já a contém) a EGIE3 e a ISAE4 contavam o dinheiro duas vezes.

Decisão em dois sinais, que têm de concordar:
  · data: mês de liquidação da oferta (fato) × data do balanço que fecha o LTM (`ltm.data_do_balanco`);
  · balanço: ações do LTM menos as do último DFP anterior à oferta ≈ 0 (fora) ou ≈ ações novas (dentro), tolerância de 5%
    das ações novas. Discordância → falha alto (conferir à mão; nada silencioso).
"""
from __future__ import annotations

import json
import pathlib

from ltm import data_do_balanco, ltm_de, ltm_ref_de

AQUI = pathlib.Path(__file__).parent
ARQUIVO = AQUI / "dados" / "eventos_societarios.json"
TOLERANCIA = 0.05


def _dados() -> dict:
    return json.loads(ARQUIVO.read_text(encoding="utf-8"))


def follow_on(tk: str) -> dict | None:
    return _dados()["follow_on"].get(tk)


def extraordinario(tk: str) -> dict | None:
    return _dados()["dividendo_extraordinario"].get(tk)


def bonificacao(tk: str) -> dict | None:
    """{"data": "AAAA-MM-DD", "fator": 1,4, ...}: proventos de data-com ANTES da data são divididos pelo fator."""
    return _dados()["bonificacao"].get(tk)


def acoes_novas(f: dict) -> float:
    return float(f["acoes_novas"]) if "acoes_novas" in f else f["valor_mil"] * 1000 / f["preco_oferta"]


def follow_on_e_balanco(tk: str, reg: dict, escala=lambda n: n) -> tuple[dict, bool]:
    """(fato do follow-on com `acoes_novas`, True se o balanço do LTM já o contém). `reg` = série do ticker no cvm_series;
    `escala` = `reescalar_acoes` (ações em mil ou em unidades conforme o formulário da CVM). Sem follow-on → KeyError."""
    f = follow_on(tk)
    if f is None:
        raise KeyError(f"{tk}: sem follow-on em {ARQUIVO.name}")
    bal = data_do_balanco(ltm_ref_de(reg))
    dentro = f["mes_liquidacao"] <= bal[:7]
    anteriores = sorted(a for a in reg["anual"] if f"{a}-12" < f["mes_liquidacao"])
    if not anteriores:
        raise ValueError(f"{tk}: nenhum DFP anterior ao follow-on de {f['mes_liquidacao']} para conferir as ações")
    novas = acoes_novas(f)
    salto = escala(ltm_de(reg)["acoes"]) - escala(reg["anual"][anteriores[-1]]["acoes"])
    esperado = novas if dentro else 0.0
    if abs(salto - esperado) > TOLERANCIA * novas:
        raise ValueError(
            f"{tk}: pela data o follow-on de {f['mes_liquidacao']} está {'DENTRO' if dentro else 'FORA'} do balanço de {bal}, "
            f"mas as ações do LTM mudaram {salto:,.0f} contra o DFP {anteriores[-1]} ({esperado:,.0f} esperado) — conferir à mão")
    return dict(f, acoes_novas=novas), dentro
