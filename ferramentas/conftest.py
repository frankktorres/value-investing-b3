"""Põe ferramentas/ no sys.path para os testes importarem os lotes e os motores."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))


# AUD-89: teste pulado por falta de dado não é teste verde. Com EXIGIR_DADOS=1 (checkout com os dados baixados) todo skip vira
# falha; sem a variável, o resumo diz quantos testes NÃO rodaram.
import os

import pytest


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    rep = (yield).get_result()
    if os.environ.get("EXIGIR_DADOS") == "1" and rep.skipped and not hasattr(rep, "wasxfail"):
        motivo = rep.longrepr[2] if isinstance(rep.longrepr, tuple) else str(rep.longrepr)
        rep.outcome = "failed"
        rep.longrepr = f"EXIGIR_DADOS=1: teste pulado ({motivo}); baixe os dados (bootstrap_dados.py / backtest/*) ou rode sem a variável"


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    rep = (yield).get_result()
    if os.environ.get("EXIGIR_DADOS") == "1" and rep.skipped:       # skip no nível do módulo (allow_module_level)
        rep.outcome = "failed"
        rep.longrepr = f"EXIGIR_DADOS=1: módulo pulado na coleta ({rep.longrepr})"


def pytest_terminal_summary(terminalreporter):
    pulados = terminalreporter.stats.get("skipped", [])
    if pulados:
        terminalreporter.write_line(
            f"ATENÇÃO (AUD-89): {len(pulados)} teste(s) PULADO(S) por falta de dado — verde não significa que rodaram. "
            "Com os dados baixados, use EXIGIR_DADOS=1 para tratar skip como falha.", yellow=True)
