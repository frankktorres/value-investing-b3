"""Travas 4.2, 4.3 e 4.4 do pacote de autonomia (25/11/2026), cada uma com canário que prova que ela bloqueia.

- 4.2 `.claude/hooks/trava_config.py`: edição de config de qualidade/trava/golden/_historico existente é barrada (exit 2);
  arquivo novo é livre; catraca só cai, piso só sobe; `MESA_LIBERA_CONFIG=1` libera. Como Bash não passa pelo hook, o
  conteúdo dos protegidos fica fixado por hash (`travas_hashes.json`) e as tolerâncias do golden por valor.
- 4.3 `golden.salvar`: sem `GOLDEN_REGRAVAR=1` ou sem "camada N" no motivo -> PermissionError; nada é gravado.
- 4.4 `.claude/hooks/avisos.py fim`: árvore ≠ última suíte verde -> aviso; igual -> silêncio.

Regravar os hashes (só o Frank, depois de liberar): `MESA_LIBERA_CONFIG=1 python tests/test_travas.py --gravar-hashes`.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent.parent            # ferramentas/
RAIZ = AQUI.parent
HASHES = Path(__file__).with_name("travas_hashes.json")
PROTEGIDOS = [
    "ferramentas/pytest.ini", "ferramentas/conftest.py", "ferramentas/suite_marcador.py", "ferramentas/golden.py",
    ".githooks/pre-push", ".githooks/trava_master.py",
    ".claude/settings.json", ".claude/hooks/trava_config.py", ".claude/hooks/avisos.py", ".claude/hooks/auto_commit.py",
    "ferramentas/tests/test_travas.py", "ferramentas/tests/test_b37_trava_master.py",
    "ferramentas/tests/test_motor_puro.py", "ferramentas/tests/test_docs_caminhos.py",
]
sys.path.insert(0, str(RAIZ / ".claude" / "hooks"))
import avisos  # noqa: E402
import trava_config  # noqa: E402


def _hash(rel: str) -> str:
    return hashlib.sha256((RAIZ / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest()


# ---------- 4.2: hook ----------

@pytest.fixture
def mini(tmp_path, monkeypatch):
    """Cópia mínima de uma raiz com os arquivos protegidos, para o hook decidir sem tocar o repo real."""
    (tmp_path / "ferramentas" / "tests").mkdir(parents=True)
    (tmp_path / ".githooks").mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / "_historico" / "2026-01-01 x").mkdir(parents=True)
    (tmp_path / "ferramentas" / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    (tmp_path / "ferramentas" / "golden.py").write_text(
        'import json\nTOL = {"central": 0.01,\n       "pc": 0.005}\nEXATOS = ("palavra",)\n\ndef f():\n    return 1\n',
        encoding="utf-8")
    (tmp_path / "ferramentas" / "tests" / "golden.json").write_text("{}", encoding="utf-8")
    (tmp_path / "ferramentas" / "tests" / "x_catraca.json").write_text(
        json.dumps({"_nota": "n", "por_arquivo": {"a.py": 3, "b.md": ["x", "y"]}}), encoding="utf-8")
    (tmp_path / ".githooks" / "piso_testes.json").write_text(json.dumps({"piso": 100}), encoding="utf-8")
    (tmp_path / ".githooks" / "pre-push").write_text("#!/bin/sh\n", encoding="utf-8")
    (tmp_path / ".claude" / "settings.json").write_text("{}", encoding="utf-8")
    (tmp_path / "_historico" / "2026-01-01 x" / "velho.md").write_text("v", encoding="utf-8")
    monkeypatch.setattr(trava_config, "RAIZ", tmp_path.resolve())
    return tmp_path


def _bloqueia(raiz, ferramenta, rel, **entrada):
    return trava_config.motivo_bloqueio(ferramenta, {"file_path": str(raiz / rel), **entrada})


def test_canario_hook_bloqueia_config_travas_golden_e_historico(mini):
    assert _bloqueia(mini, "Edit", "ferramentas/pytest.ini", old_string="[pytest]", new_string="[pytest]\n-x")
    assert _bloqueia(mini, "Write", ".githooks/pre-push", content="exit 0")
    assert _bloqueia(mini, "Edit", ".claude/settings.json", old_string="{}", new_string='{"a":1}')
    assert _bloqueia(mini, "Write", "ferramentas/tests/golden.json", content="{}")
    assert _bloqueia(mini, "Edit", "ferramentas/golden.py", old_string='"pc": 0.005', new_string='"pc": 0.05')
    assert _bloqueia(mini, "Write", "_historico/2026-01-01 x/velho.md", content="sobrescrito")
    assert _bloqueia(mini, "Edit", "ferramentas/tests/x_catraca.json", old_string='"a.py": 3', new_string='"a.py": 4')
    assert _bloqueia(mini, "Edit", "ferramentas/tests/x_catraca.json", old_string='"y"]', new_string='"y", "z"]')
    assert _bloqueia(mini, "Write", ".githooks/piso_testes.json", content='{"piso": 99}')
    assert _bloqueia(mini, "Write", ".githooks/piso_testes.json", content='{"piso": "x"}')
    assert _bloqueia(mini, "Edit", "ferramentas/tests/x_catraca.json", old_string='"a.py": 3', new_string='"a.py": NaN')
    # o golden.py inteiro: o TOL vale onde é usado (`> 10 * TOL[campo]`), não só onde é definido (adversário, 25/11)
    assert _bloqueia(mini, "Edit", "ferramentas/golden.py", old_string="return 1", new_string="return 2")
    # arquivo NOVO que desligaria a qualidade ou as travas (adversário, 25/11)
    assert _bloqueia(mini, "Write", "ferramentas/tests/conftest.py", content="collect_ignore = ['test_travas.py']")
    assert _bloqueia(mini, "Write", ".claude/settings.local.json", content='{"disableAllHooks": true}')
    assert _bloqueia(mini, "Write", "pyproject.toml", content="[tool.pytest.ini_options]\naddopts = '-k nada'")
    assert _bloqueia(mini, "Write", ".githooks/pre-commit", content="exit 0")
    # worktree de subagente dentro do repo: mesmas regras (adversário, 25/11)
    wt = mini / ".claude" / "worktrees" / "agent-1"
    for rel in (".githooks/pre-push", "ferramentas/tests/golden.json", "_historico/2026-01-01 x/velho.md"):
        (wt / rel).parent.mkdir(parents=True, exist_ok=True)
        (wt / rel).write_text("x", encoding="utf-8")
        assert _bloqueia(mini, "Write", f".claude/worktrees/agent-1/{rel}", content="y"), rel


def test_canario_hook_libera_o_que_e_livre(mini):
    assert _bloqueia(mini, "Write", "ferramentas/novo.py", content="x = 1") is None
    assert _bloqueia(mini, "Write", "_historico/2026-11-25 y/novo.md", content="n") is None
    assert _bloqueia(mini, "Write", "ferramentas/tests/test_novo.py", content="def test_x(): pass") is None
    assert _bloqueia(mini, "Edit", "ferramentas/tests/x_catraca.json", old_string='"a.py": 3', new_string='"a.py": 2') is None
    assert _bloqueia(mini, "Edit", "ferramentas/tests/x_catraca.json", old_string='["x", "y"]', new_string='["x"]') is None
    assert _bloqueia(mini, "Write", ".githooks/piso_testes.json", content='{"piso": 101}') is None


def test_canario_hook_de_verdade_pelo_stdin():
    """O script real, com o JSON que o Claude Code manda: pytest.ini do repo -> exit 2; liberado -> exit 0."""
    entrada = json.dumps({"tool_name": "Edit", "tool_input": {
        "file_path": str(AQUI / "pytest.ini"), "old_string": "[pytest]", "new_string": "[pytest]"}})
    env = {k: v for k, v in os.environ.items() if k != "MESA_LIBERA_CONFIG"}
    env["CLAUDE_PROJECT_DIR"] = str(AQUI)            # sessão aberta em ferramentas/ não desloca a raiz (adversário, 25/11)
    script = str(RAIZ / ".claude" / "hooks" / "trava_config.py")
    r = subprocess.run([sys.executable, script], input=entrada, capture_output=True, text=True, env=env, encoding="utf-8")
    assert r.returncode == 2 and "TRAVA 4.2" in r.stderr
    r = subprocess.run([sys.executable, script], input=entrada, capture_output=True, text=True,
                       env={**env, "MESA_LIBERA_CONFIG": "1"}, encoding="utf-8")
    assert r.returncode == 0
    # TOL do golden.py real, com acento no old_string (o stdin chega em UTF-8)
    linha = next(l for l in (AQUI / "golden.py").read_text(encoding="utf-8").splitlines() if l.startswith("TOL = "))
    velho = "# tolerância absoluta por campo (R$ para valores por ação; fração para taxas)\n" + linha
    entrada = json.dumps({"tool_name": "Edit", "tool_input": {"file_path": str(AQUI / "golden.py"), "old_string": velho,
                                                             "new_string": velho.replace('"pc": 0.005', '"pc": 0.5')}})
    r = subprocess.run([sys.executable, script], input=entrada, capture_output=True, text=True, env=env, encoding="utf-8")
    assert r.returncode == 2 and "golden.py" in r.stderr


def test_protegidos_com_hash_fixado():
    """Edição por Bash não passa pelo hook: o conteúdo dos protegidos tem que bater com o hash gravado."""
    gravado = json.loads(HASHES.read_text(encoding="utf-8"))["hashes"]
    atual = {rel: _hash(rel) for rel in PROTEGIDOS}
    difere = sorted(rel for rel in PROTEGIDOS if gravado.get(rel) != atual[rel])
    assert not difere, ("arquivo protegido mudou sem liberação do Frank (trava 4.2): " + ", ".join(difere)
                        + ". Liberado? `MESA_LIBERA_CONFIG=1 python tests/test_travas.py --gravar-hashes`")


PISO_MINIMO = 1237   # B37: o piso do pre-push nunca abaixo disto (adversário, 25/11: baixar por Bash anularia o max())


def test_piso_do_push_nao_baixa():
    piso = json.loads((RAIZ / ".githooks" / "piso_testes.json").read_text(encoding="utf-8"))["piso"]
    assert isinstance(piso, int) and piso >= PISO_MINIMO, f"piso {piso} < {PISO_MINIMO}: o piso só sobe"


def test_tolerancias_do_golden_fixadas():
    import golden
    assert golden.TOL == {"central": 0.01, "ancoras": 0.01, "pc": 0.005, "nota_geral": 0.05, "bogle_nom": 0.0005,
                          "dy": 0.0005, "fator_defasagem": 0.0005, "cobertura_juros": 0.05}
    assert golden.EXATOS == ("palavra", "vence_rf", "lote", "data_preco")


# ---------- 4.3: golden só com variável + camada ----------

@pytest.fixture
def golden_tmp(tmp_path, monkeypatch):
    import golden
    monkeypatch.setattr(golden, "GOLDEN", tmp_path / "golden.json")
    monkeypatch.setattr(golden, "LOG", tmp_path / "golden_log.md")
    monkeypatch.delenv("GOLDEN_REGRAVAR", raising=False)
    return golden


def test_canario_golden_sem_variavel_e_barrado(golden_tmp):
    with pytest.raises(PermissionError, match="GOLDEN_REGRAVAR"):
        golden_tmp.salvar({"X": {"central": 1.0, "ancoras": {}}}, "camada 3: teste")
    assert not golden_tmp.GOLDEN.exists() and not golden_tmp.LOG.exists()


def test_canario_golden_sem_camada_e_barrado(golden_tmp, monkeypatch):
    monkeypatch.setenv("GOLDEN_REGRAVAR", "1")
    with pytest.raises(PermissionError, match="camada"):
        golden_tmp.salvar({"X": {"central": 1.0, "ancoras": {}}}, "mudou o motor")
    assert not golden_tmp.GOLDEN.exists()


def test_golden_com_variavel_e_camada_grava(golden_tmp, monkeypatch):
    monkeypatch.setenv("GOLDEN_REGRAVAR", "1")
    golden_tmp.salvar({"X": {"central": 1.0, "ancoras": {}}}, "camada 3: teste de gravação")
    assert json.loads(golden_tmp.GOLDEN.read_text(encoding="utf-8"))["tickers"]["X"]["central"] == 1.0
    assert "camada 3" in golden_tmp.LOG.read_text(encoding="utf-8")


# ---------- 4.4: aviso no fim do turno ----------

def _g(cwd, *a):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    rp = tmp_path / "r"
    rp.mkdir()
    _g(rp, "init", "-q", "-b", "master")
    _g(rp, "config", "user.email", "t@e")
    _g(rp, "config", "user.name", "t")
    (rp / "a.py").write_text("x = 1\n", encoding="utf-8")
    _g(rp, "add", "-A")
    _g(rp, "commit", "-q", "-m", "base")
    return rp


def test_aviso_sai_em_utf8_pelo_pipe():
    """O Claude Code lê o JSON do Stop em UTF-8; no Windows o pipe sairia em cp1252 (adversário, 25/11)."""
    codigo = ("import sys; sys.argv=['avisos.py','fim']; sys.path.insert(0, r'%s'); import avisos; "
              "avisos.aviso_suite = lambda raiz=None: 'código mudou ação'; avisos.main(['fim'])"
              % (RAIZ / ".claude" / "hooks"))
    env = {k: v for k, v in os.environ.items() if k not in ("CLAUDE_CODE_REMOTE", "PYTHONIOENCODING", "PYTHONUTF8")}
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, env=env)
    assert json.loads(r.stdout.decode("utf-8"))["systemMessage"] == "código mudou ação"


def test_canario_aviso_quando_arvore_mudou_depois_da_suite(repo):
    import suite_marcador
    assert "nenhuma suíte" in avisos.aviso_suite(repo)
    suite_marcador.registrar_verde(suite_marcador.arvore_trabalho(repo), 10, cwd=repo)
    assert avisos.aviso_suite(repo) is None
    (repo / "a.py").write_text("x = 2\n", encoding="utf-8")
    msg = avisos.aviso_suite(repo)
    assert msg and "a.py" in msg and "mudou depois da última suíte verde" in msg


if __name__ == "__main__" and "--gravar-hashes" in sys.argv:
    if os.environ.get("MESA_LIBERA_CONFIG") != "1":
        sys.exit("só com MESA_LIBERA_CONFIG=1 (decisão do Frank)")
    HASHES.write_text(json.dumps({"_nota": "Trava 4.2: hash (LF) dos protegidos. Regravar só com liberação do Frank.",
                                  "hashes": {rel: _hash(rel) for rel in PROTEGIDOS}}, indent=1), encoding="utf-8")
    print(f"gravado {HASHES}")
