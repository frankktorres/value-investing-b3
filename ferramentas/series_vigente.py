"""Arquivo vigente das séries do StatusInvest (AUD-24).

Antes, motor_nao_financeiras, lote2_energia e defasagem pegavam `sorted(glob("series_*.json"))[-1]`: um
`series_` parcial com data mais nova (ex.: `montar_series.py 2026-10-07 BBAS3 ITUB4`) virava o "último" e
derrubava o import dos 41 (KeyError no primeiro ticker ausente). Agora o arquivo vigente é uma constante
explícita; trocar de arquivo é uma edição deliberada aqui, e o carregamento confere a cobertura.
"""
from __future__ import annotations

import json
import pathlib

AQUI = pathlib.Path(__file__).parent
VIGENTE = "series_2026-10-05.json"
TICKERS_ESPERADOS = 41            # o universo dos 6 lotes (tests/test_regressao.py::test_universo_completo)


def carregar(nome: str = VIGENTE, pasta: pathlib.Path = AQUI / "dados",
             minimo: int = TICKERS_ESPERADOS) -> dict:
    dados = json.loads((pasta / nome).read_text(encoding="utf-8"))
    if len(dados) < minimo:
        raise ValueError(f"{nome} cobre {len(dados)} tickers, o vigente precisa de >= {minimo} (AUD-24)")
    return dados
