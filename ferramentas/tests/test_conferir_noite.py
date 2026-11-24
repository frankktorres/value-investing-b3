"""conferir_noite (22/10/2026): a junção da rodada da nuvem só vai ao master com a suíte verde e sem tocar em golden/doutrina.
Repositório git de mentira (origin = repo bare em tmp_path); a suíte é trocada por um resultado fixo."""
import subprocess

import pytest

import conferir_noite as C

DADOS_LOCAIS = C.dados_locais


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path, monkeypatch):
    for k, v in {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                 "GIT_COMMITTER_EMAIL": "t@t"}.items():
        monkeypatch.setenv(k, v)
    origem, local = tmp_path / "origem.git", tmp_path / "local"
    _git(tmp_path, "init", "-q", "--bare", "-b", "master", str(origem))
    _git(tmp_path, "clone", "-q", str(origem), str(local))
    _git(local, "checkout", "-q", "-b", "master")
    (local / "ferramentas" / "tests").mkdir(parents=True)
    (local / "ferramentas" / "tests" / "golden.json").write_text("{}\n")
    (local / "a.txt").write_text("a\n")
    _git(local, "add", ".")
    _git(local, "commit", "-q", "-m", "base")
    _git(local, "push", "-q", "origin", "master")
    monkeypatch.setattr(C, "RAIZ", local)
    monkeypatch.setattr(C, "PARADO_MIN", 0)
    monkeypatch.setattr(C, "dados_locais", lambda: [])
    # trava: nenhum git do módulo pode cair no repositório real (aconteceu em 22/10 com o default preso na definição)
    assert C.git("rev-parse", "--show-toplevel").replace("\\", "/").lower() == str(local).replace("\\", "/").lower()
    assert C.git("remote", "get-url", "origin").replace("\\", "/").lower() == str(origem).replace("\\", "/").lower()
    return local


def _rodada(local, nome, arquivo="b.txt"):
    _git(local, "checkout", "-q", "-b", nome)
    p = local / arquivo
    p.write_text(p.read_text() + "x\n" if p.exists() else "b\n")
    _git(local, "add", ".")
    _git(local, "commit", "-q", "-m", f"rodada {nome}")
    _git(local, "push", "-q", "origin", nome)
    _git(local, "checkout", "-q", "master")


def _remotos(local):
    _git(local, "fetch", "-q", "--prune", "origin")
    return _git(local, "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/")


def test_verde_junta_no_master_apaga_o_ramo_e_atualiza_o_checkout(repo, monkeypatch):
    monkeypatch.setattr(C, "suite", lambda wt: (0, "10 passed"))
    _rodada(repo, "claude/noite-1")
    assert C.main([]) == 0
    assert "claude/noite-1" not in _remotos(repo)
    assert (repo / "b.txt").exists()                                       # pull --ff-only trouxe a junção
    assert _git(repo, "log", "-1", "--format=%s", "origin/master").startswith("Junta a rodada da nuvem (claude/noite-1)")


def test_vermelho_nao_toca_no_master_e_mantem_o_ramo(repo, monkeypatch):
    monkeypatch.setattr(C, "suite", lambda wt: (1, "1 failed, 9 passed"))
    antes = _git(repo, "rev-parse", "origin/master")
    _rodada(repo, "claude/noite-2")
    assert C.main([]) == C.VERMELHO
    assert "origin/claude/noite-2" in _remotos(repo)
    assert _git(repo, "rev-parse", "origin/master") == antes


def test_golden_alterado_espera_o_frank_sem_rodar_a_suite(repo, monkeypatch):
    monkeypatch.setattr(C, "suite", lambda wt: pytest.fail("não devia rodar a suíte"))
    _rodada(repo, "claude/noite-3", arquivo="ferramentas/tests/golden.json")
    assert C.main([]) == C.PRECISA
    assert "origin/claude/noite-3" in _remotos(repo)


def test_ramo_recente_espera_a_rotina_terminar(repo, monkeypatch):
    monkeypatch.setattr(C, "PARADO_MIN", 30)
    monkeypatch.setattr(C, "suite", lambda wt: pytest.fail("não devia rodar a suíte"))
    _rodada(repo, "claude/noite-4")
    assert C.main([]) == C.PRECISA


def test_so_conferir_nao_envia_nada(repo, monkeypatch):
    monkeypatch.setattr(C, "suite", lambda wt: (0, "10 passed"))
    antes = _git(repo, "rev-parse", "origin/master")
    _rodada(repo, "claude/noite-5")
    assert C.main(["--so-conferir"]) == 0
    assert _git(repo, "rev-parse", "origin/master") == antes and "origin/claude/noite-5" in _remotos(repo)


def test_ramo_ja_contido_e_apagado(repo, monkeypatch):
    monkeypatch.setattr(C, "suite", lambda wt: pytest.fail("não devia rodar a suíte"))
    _git(repo, "push", "-q", "origin", "master:claude/velho")
    assert C.main([]) == 0
    assert "claude/velho" not in _remotos(repo)


def test_commit_que_chega_durante_a_suite_nao_se_perde(repo, monkeypatch, tmp_path):
    """Adversário 22/10: o delete sem lease apagava o commit que a rotina empurrou enquanto a suíte rodava."""
    _rodada(repo, "claude/noite-7")
    outro = tmp_path / "outro"
    _git(tmp_path, "clone", "-q", _git(repo, "remote", "get-url", "origin"), str(outro))

    def suite_com_commit_tardio(wt):
        _git(outro, "checkout", "-q", "claude/noite-7")
        (outro / "tardio.txt").write_text("t\n")
        _git(outro, "add", ".")
        _git(outro, "commit", "-q", "-m", "tardio")
        _git(outro, "push", "-q", "origin", "claude/noite-7")
        return 0, "10 passed"

    monkeypatch.setattr(C, "suite", suite_com_commit_tardio)
    assert C.main([]) == 0
    assert "origin/claude/noite-7" in _remotos(repo)                       # ficou: tem o commit tardio
    assert _git(repo, "log", "-1", "--format=%s", "origin/claude/noite-7") == "tardio"


def test_suite_com_teste_pulado_nao_e_verde(tmp_path):
    """Adversário 22/10: rc 0 com tudo pulado ia ao master; agora pulado = vermelho (EXIGIR_DADOS + resumo)."""
    (tmp_path / "ferramentas").mkdir()
    (tmp_path / "ferramentas" / "test_pula.py").write_text("import pytest\n\ndef test_x():\n    pytest.skip('sem dado')\n")
    rc, resumo = C.suite(tmp_path)
    assert rc != 0 and "skipped" in resumo


def test_dado_com_acento_vai_para_a_worktree_como_copia(repo, tmp_path):
    """Adversário 22/10: sem `-z` o caminho com acento vinha em octal e sumia; hard link deixava o teste regravar o original."""
    (repo / ".gitignore").write_text("ferramentas/dados/*.zip\n")
    dados = repo / "ferramentas" / "dados"
    dados.mkdir(parents=True)
    (dados / "preços_2024.zip").write_bytes(b"original")
    locais = DADOS_LOCAIS()                                                # o fixture troca C.dados_locais por []
    assert "ferramentas/dados/preços_2024.zip" in locais
    wt = tmp_path / "wt"
    for rel in locais:
        C.espelhar(rel, wt)
    copia = wt / "ferramentas" / "dados" / "preços_2024.zip"
    copia.write_bytes(b"REGRAVADO")
    assert (dados / "preços_2024.zip").read_bytes() == b"original"


def test_conflito_nao_envia(repo, monkeypatch):
    monkeypatch.setattr(C, "suite", lambda wt: pytest.fail("não devia rodar a suíte"))
    _rodada(repo, "claude/noite-6", arquivo="a.txt")
    (repo / "a.txt").write_text("outro\n")
    _git(repo, "commit", "-qam", "master andou")
    _git(repo, "push", "-q", "origin", "master")
    assert C.main([]) == C.PRECISA
