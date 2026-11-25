"""B37 (25/11/2026): trava do push no master. Canários: push real para um repositório bare temporário.

- sem registro verde da árvore -> barrado; registro forjado com contagem abaixo do piso -> barrado;
- registro verde com contagem ≥ piso -> passa; push para outra ref -> passa; apagar master -> barrado.
"""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent.parent          # ferramentas/
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / ".githooks"))
import suite_marcador  # noqa: E402
import trava_master  # noqa: E402


def g(cwd, *args, check=True):
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise AssertionError(f"git {args}: {r.stderr}")
    return r


@pytest.fixture
def repo(tmp_path):
    rp = tmp_path / "repo"
    rp.mkdir()
    g(rp, "init", "-q", "-b", "master")
    g(rp, "config", "user.email", "teste@exemplo")
    g(rp, "config", "user.name", "teste")
    g(rp, "config", "core.autocrlf", "false")
    (rp / ".githooks").mkdir()
    for nome in ("pre-push", "trava_master.py", "piso_testes.json"):
        shutil.copy2(RAIZ / ".githooks" / nome, rp / ".githooks" / nome)
    os.chmod(rp / ".githooks" / "pre-push", os.stat(rp / ".githooks" / "pre-push").st_mode | stat.S_IEXEC)
    (rp / "ferramentas").mkdir()
    shutil.copy2(AQUI / "suite_marcador.py", rp / "ferramentas" / "suite_marcador.py")
    (rp / ".gitignore").write_text("ignorado.txt\n__pycache__/\n", encoding="utf-8")
    (rp / "a.txt").write_text("1\n", encoding="utf-8")
    g(rp, "add", "-A")
    g(rp, "commit", "-q", "-m", "base")
    g(rp, "config", "core.hooksPath", ".githooks")
    bare = tmp_path / "remoto.git"
    g(tmp_path, "init", "-q", "--bare", str(bare))
    g(rp, "remote", "add", "origin", str(bare))
    return rp


def _piso(rp):
    return json.loads((rp / ".githooks" / "piso_testes.json").read_text(encoding="utf-8"))["piso"]


def test_arvore_trabalho_igual_ao_commit_e_muda_com_arquivo(repo):
    arv = g(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    assert suite_marcador.arvore_trabalho(repo) == arv
    (repo / "ignorado.txt").write_text("x", encoding="utf-8")         # ignorado não conta
    assert suite_marcador.arvore_trabalho(repo) == arv
    (repo / "novo.txt").write_text("x", encoding="utf-8")             # não rastreado conta
    assert suite_marcador.arvore_trabalho(repo) != arv
    g(repo, "status", "--porcelain")                                   # índice real intacto
    assert g(repo, "diff", "--cached", "--name-only").stdout.strip() == ""


def test_registro_ausente_ou_estragado_e_vazio(repo):
    assert suite_marcador.ler(repo) == []
    suite_marcador.arquivo_registro(repo).write_text("{lixo", encoding="utf-8")
    assert suite_marcador.ler(repo) == []


@pytest.mark.parametrize("cont,parcial,rc,ini,fim,esperado", [
    ({"passed": 10}, False, 0, "a", "a", True),
    ({"passed": 10, "failed": 1}, False, 1, "a", "a", False),
    ({"passed": 10, "skipped": 1}, False, 0, "a", "a", False),
    ({"passed": 10, "error": 1}, False, 1, "a", "a", False),
    ({"passed": 10}, True, 0, "a", "a", False),                       # suíte parcial
    ({"passed": 10}, False, 0, "a", "b", False),                      # arquivo mexido durante a suíte
    ({"passed": 10}, False, 0, None, None, False),                    # sem git
])
def test_deve_registrar(cont, parcial, rc, ini, fim, esperado):
    assert suite_marcador.deve_registrar(cont, parcial, rc, ini, fim) is esperado


def test_decidir(repo):
    head = g(repo, "rev-parse", "HEAD").stdout.strip()
    arv = g(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    assert trava_master.decidir("0" * 40, [], 1, cwd=str(repo))[0] is False
    assert trava_master.decidir(head, [], 1, cwd=str(repo))[0] is False
    assert trava_master.decidir(head, [{"arvore": arv, "aprovados": 5}], 6, cwd=str(repo))[0] is False
    assert trava_master.decidir(head, [{"arvore": arv, "aprovados": "x"}], 1, cwd=str(repo))[0] is False
    assert trava_master.decidir(head, [{"arvore": arv, "aprovados": 6}], 6, cwd=str(repo))[0] is True


def test_piso_vale_o_maior_entre_arquivo_e_commit(repo):
    head = g(repo, "rev-parse", "HEAD").stdout.strip()
    p = _piso(repo)
    (repo / ".githooks" / "piso_testes.json").write_text(json.dumps({"piso": 1}), encoding="utf-8")
    assert trava_master.piso(head, cwd=str(repo)) == p                  # baixar só no arquivo não baixa


def test_canario_push_vermelho_e_barrado_e_verde_passa(repo):
    # 1) árvore sem suíte verde registrada -> barrado
    r = g(repo, "push", "origin", "master", check=False)
    assert r.returncode != 0 and "TRAVA B37" in r.stderr
    # 2) registro forjado à mão com contagem abaixo do piso -> barrado
    arv = g(repo, "rev-parse", "HEAD^{tree}").stdout.strip()
    suite_marcador.arquivo_registro(repo).write_text(
        json.dumps({"verdes": [{"arvore": arv, "aprovados": 3}]}), encoding="utf-8")
    r = g(repo, "push", "origin", "master", check=False)
    assert r.returncode != 0 and "abaixo do piso" in r.stderr
    # 3) outra ref passa sem registro
    assert g(repo, "push", "origin", "master:refs/heads/wip/auto", check=False).returncode == 0
    # 4) registro verde com contagem >= piso -> passa
    suite_marcador.registrar_verde(arv, _piso(repo), cwd=repo)
    r = g(repo, "push", "origin", "master", check=False)
    assert r.returncode == 0, r.stderr
    # 5) commit novo (árvore nova) sem suíte -> barrado de novo
    (repo / "a.txt").write_text("2\n", encoding="utf-8")
    g(repo, "commit", "-q", "-am", "mudou")
    r = g(repo, "push", "origin", "master", check=False)
    assert r.returncode != 0 and "não tem suíte inteira verde" in r.stderr
    # 6) apagar o master -> barrado
    r = g(repo, "push", "origin", ":master", check=False)
    assert r.returncode != 0
