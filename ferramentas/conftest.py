"""Põe ferramentas/ no sys.path para os testes importarem os lotes e os motores."""
import inspect
import os
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).parent))


def _skip_de_plataforma(item) -> bool:
    """Identifica estruturalmente se o skip decorre de incompatibilidade de SO/plataforma
    (marcador `@pytest.mark.plataforma` ou condição `skipif` referenciando `os.name`,
    `sys.platform` ou `platform.system` no código-fonte da função de teste)."""
    if item.get_closest_marker("plataforma") is not None:
        return True
    obj = getattr(item, "obj", None)
    if obj is not None:
        try:
            src = inspect.getsource(obj).split("def ", 1)[0]
            if "skipif" in src and any(t in src for t in ("os.name", "sys.platform", "platform.system")):
                return True
        except (OSError, TypeError):
            pass
    return False


# AUD-89: teste pulado por falta de dado não é teste verde. Com EXIGIR_DADOS=1 (checkout com os dados baixados) todo skip vira
# falha; sem a variável, o resumo diz quantos testes NÃO rodaram.
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    rep = (yield).get_result()
    if os.environ.get("EXIGIR_DADOS") == "1" and rep.skipped and not hasattr(rep, "wasxfail"):
        if not _skip_de_plataforma(item):
            motivo = rep.longrepr[2] if isinstance(rep.longrepr, tuple) else str(rep.longrepr)
            rep.outcome = "failed"
            rep.longrepr = f"EXIGIR_DADOS=1: teste pulado ({motivo}); baixe os dados (bootstrap_dados.py / backtest/*) ou rode sem a variável"


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    rep = (yield).get_result()
    if os.environ.get("EXIGIR_DADOS") == "1" and rep.skipped:       # skip no nível do módulo (allow_module_level)
        rep.outcome = "failed"
        rep.longrepr = f"EXIGIR_DADOS=1: módulo pulado na coleta ({rep.longrepr})"


def _parcial(config) -> bool:
    # caminho explícito = parcial; valor de opção (`-p no:cacheprovider`) não é caminho (22/10: a tela dizia "sem registro")
    args = list(config.invocation_params.args)
    caminho = config.args_source == pytest.Config.ArgsSource.ARGS
    return caminho or any(a in ("-k", "-m", "--lf", "--ff", "-x") or a.startswith(("-k", "-m")) for a in args)


def pytest_sessionstart(session):
    """B37: guarda a árvore testada (HEAD + árvore de trabalho) no início da suíte inteira."""
    session.config._mesa_arvore = None
    if _parcial(session.config):
        return
    try:
        import suite_marcador
        session.config._mesa_arvore = suite_marcador.arvore_trabalho(pathlib.Path(__file__).parent)
    except (RuntimeError, OSError):
        pass


def _registrar_suite_verde(session, exitstatus, n):
    """B37: suíte inteira com 0 falha/erro/pulado e árvore igual do início ao fim -> registro lido pelo pre-push do master.
    Independe de CLAUDE_NO_SUITE_LOG: o conferir_noite (worktree) também precisa registrar para juntar no master."""
    try:
        import suite_marcador
        inicio = getattr(session.config, "_mesa_arvore", None)
        fim = suite_marcador.arvore_trabalho(pathlib.Path(__file__).parent) if inicio else None
        if suite_marcador.deve_registrar(n, _parcial(session.config), int(exitstatus), inicio, fim):
            suite_marcador.registrar_verde(inicio, n["passed"], pathlib.Path(__file__).parent)
    except (RuntimeError, OSError):
        pass


def pytest_sessionfinish(session, exitstatus):
    """Registro da última suíte COMPLETA (alimenta a tela Sistema): `dados/suite_ultima.json`, ignorado pelo git. Rodada parcial
    (caminho, -k, -m, ou o backtest) não grava — o número só vale se for a suíte inteira do dia a dia."""
    import datetime
    import json
    args = list(session.config.invocation_params.args)
    parcial = _parcial(session.config)
    tr = session.config.pluginmanager.get_plugin("terminalreporter")
    if tr is not None and not parcial:
        _registrar_suite_verde(session, exitstatus, {k: len(tr.stats.get(k, [])) for k in ("passed", "failed", "error", "skipped")})
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
