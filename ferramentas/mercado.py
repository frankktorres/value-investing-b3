"""Mercado vigente (rf e π) num só arquivo versionado, e a idade do preço/taxa.

AUD-78 (auditoria 08/10/2026): rf e π eram literais digitados em 3 arquivos (lote1_bancos, triagem/config, backtest/config).
Agora todos leem `mercado_vigente.json`; `tests/test_onda12_mercado.py` confere o arquivo contra `dados/mercado.json`.
AUD-06: a rf é a taxa de COMPRA DA MANHÃ do Tesouro Direto (Tesouro Transparente) — é a que o investidor consegue no título
sem cupom; o Tesouro Direto não publica fechamento (doutrina §4, v2.4).
AUD-72: a regra "cotação com mais de 15 dias exige o aviso 'atualizar antes de decidir'" (00-CONFIGURACAO, regra 3) vira código.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib

from motor_financeiras import Mercado

AQUI = pathlib.Path(__file__).parent
ARQUIVO = AQUI / "mercado_vigente.json"
LIMITE_DIAS = 15        # 00-CONFIGURACAO-DO-PROJETO.md, regra 3


def dados() -> dict:
    return json.loads(ARQUIVO.read_text(encoding="utf-8"))


def _br(iso: str) -> str:
    return dt.date.fromisoformat(iso).strftime("%d/%m/%Y")


def vigente() -> Mercado:
    m = dados()
    return Mercado(rf_real=m["rf_real"], pi=m["pi"], data=_br(m["data"]))


def focus() -> Mercado:
    m = dados()
    return Mercado(rf_real=m["rf_real"], pi=m["pi_focus"], data=_br(m["data"]) + " (π 4% — hipótese dos PDFs de 03/10)")


def _data(x) -> dt.date:
    if isinstance(x, dt.date):
        return x
    x = str(x)
    return dt.datetime.strptime(x, "%d/%m/%Y").date() if "/" in x else dt.date.fromisoformat(x)


def idade_dias(data, hoje=None) -> int:
    """Dias corridos entre a data do preço/taxa (ISO ou dd/mm/aaaa) e hoje."""
    return (_data(hoje or dt.date.today()) - _data(data)).days


def aviso_idade(data, hoje=None, limite: int = LIMITE_DIAS) -> str:
    """'' até `limite` dias; acima, o aviso da regra 3."""
    n = idade_dias(data, hoje)
    if n <= limite:
        return ""
    return f"Atenção: preço e taxa de {_br(_data(data).isoformat())}, {n} dias atrás — atualizar antes de decidir (regra 3)."
