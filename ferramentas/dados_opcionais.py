"""Marcadores de teste para dados fora do git (AUD-38, 09/10/2026).

Clone limpo não tem o suplemento da B3 (backtest/dados/proventos/suplemento, cache rebaixável). Os testes que dependem dele
saem como SKIPPED com o motivo no relatório (`pytest -rs`), em vez de falhar na coleta ou passar sem checar. Para recriá-lo:
`python -m backtest.precos.proventos_b3` (ver o cabeçalho do módulo).
"""
import pathlib

import pytest

from backtest.precos.proventos_b3 import PASTA

# dados/raw/ (coletas brutas por dia, ignorada pelo git): a nuvem não tem — quem precisa dela pula em vez de falhar (QA 21/10/2026)
RAW = pathlib.Path(__file__).resolve().parent / "dados" / "raw"
TEM_RAW = RAW.is_dir()
# 27/11/2026: 1ª noite da rotina deu BASE VERMELHA com 4 testes lendo dados/raw sem pular (minério da CMIN3, executor ALLD3).
# Com os dados (PC do Frank) o teste roda; com EXIGIR_DADOS=1 o conftest transforma o pulo em falha (a manhã confere).
requer_raw = pytest.mark.skipif(not TEM_RAW, reason="dados/raw fora do disco (coletas brutas ignoradas pelo git; clone limpo/nuvem)")

TEM_SUPLEMENTO_B3 = any((PASTA / "suplemento").glob("*.json"))
requer_suplemento_b3 = pytest.mark.skipif(
    not TEM_SUPLEMENTO_B3, reason="suplemento da B3 fora do disco (backtest/dados é ignorado pelo git); ver dados_opcionais.py")
