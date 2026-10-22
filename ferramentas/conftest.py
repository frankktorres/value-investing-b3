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


def pytest_sessionfinish(session, exitstatus):
    """Registro da última suíte COMPLETA (alimenta a tela Sistema): `dados/suite_ultima.json`, ignorado pelo git. Rodada parcial
    (caminho, -k, -m, ou o backtest) não grava — o número só vale se for a suíte inteira do dia a dia."""
    import json
    import datetime
    args = list(session.config.invocation_params.args)
    parcial = [a for a in args if not a.startswith("-")] or any(a in ("-k", "-m", "--lf", "--ff", "-x") or a.startswith(("-k", "-m"))
                                                                for a in args)
    tr = session.config.pluginmanager.get_plugin("terminalreporter")
    if parcial or tr is None or os.environ.get("CLAUDE_NO_SUITE_LOG") == "1":
        return
    n = {k: len(tr.stats.get(k, [])) for k in ("passed", "failed", "error", "skipped")}
    if n["passed"] + n["failed"] < 400:                      # nem a suíte base (≈ 900) rodou: não registra
        return
    try:
        (pathlib.Path(__file__).parent / "dados" / "suite_ultima.json").write_text(json.dumps({
            "data": datetime.date.today().isoformat(), "passed": n["passed"], "failed": n["failed"] + n["error"],
            "skipped": n["skipped"], "args": args}, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def pytest_terminal_summary(terminalreporter):
    pulados = terminalreporter.stats.get("skipped", [])
    if pulados:
        terminalreporter.write_line(
            f"ATENÇÃO (AUD-89): {len(pulados)} teste(s) PULADO(S) por falta de dado — verde não significa que rodaram. "
            "Com os dados baixados, use EXIGIR_DADOS=1 para tratar skip como falha.", yellow=True)
