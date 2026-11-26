"""Rotina noturna (26/11/2026): canários do portão (`rotina/checar_rotina.py`), BOOTSTRAP × nuvem, PROTOCOLO e pré-voo.

O portão é a trava que vale de verdade: a manhã (`conferir_noite.portao`) roda o da origin/master contra o ramo. Aqui ele é
exercitado num repositório git de mentira (origin = repo bare em tmp_path), inclusive extraído para uma pasta vazia com
`python -I` (como a manhã faz): nada do repo pode ser necessário para ele recusar o motor."""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import conferir_noite
from rotina import checar_rotina as C
from rotina import nuvem

RAIZ = Path(__file__).resolve().parents[2]
ROTINA = RAIZ / "docs" / "ops" / "rotina"


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


def _escreve(local, rel, texto):
    p = local / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto, encoding="utf-8")


def _commit(local, msg):
    _git(local, "add", "-A")
    _git(local, "commit", "-q", "-m", msg)
    return _git(local, "rev-parse", "HEAD")


@pytest.fixture
def mini(tmp_path, monkeypatch):
    for k, v in {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                 "GIT_COMMITTER_EMAIL": "t@t"}.items():
        monkeypatch.setenv(k, v)
    origem, local = tmp_path / "origem.git", tmp_path / "local"
    _git(tmp_path, "init", "-q", "--bare", "-b", "master", str(origem))
    _git(tmp_path, "clone", "-q", str(origem), str(local))
    _git(local, "checkout", "-q", "-b", "master")
    _escreve(local, "docs/MISSOES.md", "# MISSOES\n\n## Próximas\n")
    _escreve(local, "docs/RELATORIO-DIARIO.md", "# RELATORIO\n\n## 26/11/2026 — sessão do Frank\n- dia\n")
    _escreve(local, "ferramentas/motor_x.py", "X = 1\n")
    _escreve(local, "_historico/2026-11-01 velho/a.md", "velho\n")
    base = _commit(local, "base")
    _escreve(local, "docs/MISSOES.md", "# MISSOES\n\n## Próximas\n**B99 — doc.**\n"
             f"*Carimbo (nuvem):* B99 · escopo: `docs/b99.md` · fonte: nenhuma · pronta: {base[:7]}\n")
    _commit(local, "carimbo B99")
    _git(local, "push", "-q", "origin", "master")
    _git(local, "checkout", "-q", "-b", "claude/t")
    return local


def _roda(local, capsys, *args):
    rc = C.main(["--repo", str(local), "--base", "origin/master", *args])
    return rc, capsys.readouterr().out


def _noite(local, rel, texto="novo\n"):
    _escreve(local, rel, texto)


# ---- escopo e proibidos ----------------------------------------------------------------------------------------------

def test_dentro_do_escopo_passa(mini, capsys):
    _noite(mini, "docs/b99.md")
    rc, out = _roda(mini, capsys)
    assert rc == 0, out
    assert "OK A docs/b99.md (escopo B99)" in out


def test_fora_do_escopo_para(mini, capsys):
    _noite(mini, "docs/b99.md")
    _noite(mini, "docs/outro.md")
    rc, out = _roda(mini, capsys)
    assert rc == 1 and "docs/outro.md: FORA DO ESCOPO" in out


def test_motor_para_mesmo_no_escopo(mini, capsys):
    _git(mini, "checkout", "-q", "master")
    m = mini / "docs/MISSOES.md"
    m.write_text(m.read_text(encoding="utf-8") + "*Carimbo (nuvem):* B95 · escopo: `ferramentas/motor_x.py` · fonte: nenhuma"
                 f" · pronta: {_git(mini, 'rev-parse', '--short', 'HEAD')}\n", encoding="utf-8")
    _commit(mini, "carimbo B95 (errado: motor)")
    _git(mini, "push", "-q", "origin", "master")
    _git(mini, "checkout", "-q", "-B", "claude/t", "master")
    _noite(mini, "ferramentas/motor_x.py", "X = 2\n")
    rc, out = _roda(mini, capsys)
    assert rc == 1 and "ferramentas/motor_x.py: PROIBIDO" in out


def test_escopo_escrito_pela_noite_nao_vale_e_carimbo_novo_para(mini, capsys):
    """O escopo vem do MISSOES da BASE; carimbo acrescentado no ramo é recusado (senior A1)."""
    m = mini / "docs/MISSOES.md"
    m.write_text(m.read_text(encoding="utf-8") + "*Carimbo (nuvem):* B98 · escopo: `docs/outro.md` · fonte: nenhuma · "
                 f"pronta: {_git(mini, 'rev-parse', '--short', 'HEAD')}\n", encoding="utf-8")
    _noite(mini, "docs/outro.md")
    rc, out = _roda(mini, capsys)
    assert rc == 1
    assert "docs/outro.md: FORA DO ESCOPO" in out and "carimbo novo ou alterado pela noite" in out


def test_mover_missao_para_feitas_e_livre(mini, capsys):
    m = mini / "docs/MISSOES.md"
    m.write_text("# MISSOES\n\n## Próximas\n\n## Feitas\n- **B99** (27/11, claude/t): doc.\n", encoding="utf-8")
    _noite(mini, "docs/b99.md")
    rc, out = _roda(mini, capsys)
    assert rc == 0, out


def test_historico_existente_para_e_snapshot_novo_do_desktop_passa(mini, capsys):
    _noite(mini, "_historico/2026-11-27 upload-desktop/BACKLOG.md")
    rc, out = _roda(mini, capsys)
    assert rc == 0, out
    _noite(mini, "_historico/2026-11-01 velho/a.md", "reescrito\n")
    rc, out = _roda(mini, capsys)
    assert rc == 1 and "_historico/2026-11-01 velho/a.md: PROIBIDO" in out


def test_apagar_do_historico_para(mini, capsys):
    (mini / "_historico/2026-11-01 velho/a.md").unlink()
    _noite(mini, "docs/b99.md")
    rc, out = _roda(mini, capsys)
    assert rc == 1 and "D _historico/2026-11-01 velho/a.md: PROIBIDO" in out


def test_diff_vazio_para(mini, capsys):
    rc, out = _roda(mini, capsys)
    assert rc == 1 and "diff vazio" in out


def test_carimbo_com_glob_ou_nao_ancestral_nao_vale(mini, capsys):
    _git(mini, "checkout", "-q", "master")
    m = mini / "docs/MISSOES.md"
    m.write_text(m.read_text(encoding="utf-8")
                 + "*Carimbo (nuvem):* B97 · escopo: `docs/**` · fonte: nenhuma · pronta: "
                 + _git(mini, "rev-parse", "--short", "HEAD") + "\n"
                 + "*Carimbo (nuvem):* B96 · escopo: `docs/b96.md` · fonte: nenhuma · pronta: abcdef1\n", encoding="utf-8")
    _commit(mini, "carimbos ruins")
    _git(mini, "push", "-q", "origin", "master")
    _git(mini, "checkout", "-q", "-B", "claude/t", "master")
    _noite(mini, "docs/qualquer.md")
    _noite(mini, "docs/b96.md")
    rc, out = _roda(mini, capsys)
    assert rc == 1
    assert "B97: escopo com glob" in out and "B96: `pronta: abcdef1` não é ancestral" in out


def test_modo_da_manha_le_o_commit_do_ramo(mini, capsys):
    _noite(mini, "docs/b99.md")
    sha = _commit(mini, "B99")
    rc, out = _roda(mini, capsys, "--head", sha)
    assert rc == 0, out
    _noite(mini, "ferramentas/motor_x.py", "X = 3\n")
    sha = _commit(mini, "motor")
    rc, out = _roda(mini, capsys, "--head", sha)
    assert rc == 1 and "PROIBIDO" in out


def test_portao_extraido_numa_pasta_vazia_recusa_o_motor(mini, tmp_path):
    """Como a manhã roda: `git show origin/master:...` → pasta vazia → `python -I`. Import quebrado = rc ≠ 0, nunca OK."""
    _noite(mini, "ferramentas/motor_x.py", "X = 4\n")
    sha = _commit(mini, "motor")
    vazia = tmp_path / "vazia"
    vazia.mkdir()
    arq = vazia / "checar_rotina.py"
    shutil.copyfile(Path(C.__file__), arq)
    r = subprocess.run([sys.executable, "-I", str(arq), "--repo", str(mini), "--base", "origin/master", "--head", sha],
                       cwd=vazia, capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 1, r.stdout + r.stderr
    assert "ferramentas/motor_x.py: PROIBIDO" in r.stdout


def test_proibido_cobre_todos_os_protegidos_da_manha():
    """Tudo o que a manhã recusa também é proibido para a noite (a noite descobre antes, não às 07:15)."""
    for p in conferir_noite.PROTEGIDOS:
        if p.startswith(":(exclude"):
            continue
        amostra = p.removeprefix(":(glob)").replace("**/", "x/").replace("/**", "/x").replace("*", "x")
        if (RAIZ / p).is_dir():
            amostra += "/x.txt"
        assert C.proibido(amostra), f"{p} (amostra {amostra}) não é proibido para a noite"


# ---- prova no relatório ----------------------------------------------------------------------------------------------

def test_colar_sem_o_bloco_da_noite_para(mini, capsys):
    _noite(mini, "docs/b99.md")
    rc, out = _roda(mini, capsys, "--colar")
    assert rc == 1 and "prova NÃO colada" in out


def test_colar_grava_a_prova_uma_vez_so(mini, capsys):
    rel = mini / "docs/RELATORIO-DIARIO.md"
    rel.write_text(rel.read_text(encoding="utf-8").replace(
        "## 26/11/2026", "## 2026-11-27 · Rotina na nuvem (ramo claude/t)\n1. **Feito:** B99\n\n## 26/11/2026"),
        encoding="utf-8")
    _noite(mini, "docs/b99.md")
    assert _roda(mini, capsys, "--colar")[0] == 0
    assert _roda(mini, capsys, "--colar")[0] == 0
    texto = rel.read_text(encoding="utf-8")
    assert texto.count("<!-- prova: checar_rotina base=") == 1
    assert "PORTÃO OK" in texto and "OK A docs/b99.md (escopo B99)" in texto
    assert "## 26/11/2026 — sessão do Frank" in texto                              # o bloco do dia ficou intacto


# ---- BOOTSTRAP × nuvem, PROTOCOLO --------------------------------------------------------------------------------------

def test_bootstrap_e_fino_e_tem_a_trava():
    b = nuvem.bloco()
    assert len(b) < 3000
    assert b.startswith("ROTINA NOTURNA DA MESA")
    for trecho in ("TRAVA DE SOBREPOSIÇÃO (fazer ANTES de tudo)", "git rev-list --count origin/master..<ramo>",
                   "(três pontos) lista SÓ docs/RELATORIO-DIARIO.md", '"rotina pulada", "BASE VERMELHA" ou "AMBIENTE QUEBRADO"',
                   "docs/ops/rotina/PROTOCOLO.md da origin/master", "siga-o INTEIRO", "PROTOCOLO.md ausente",
                   "Nunca faça push no master", "ordem de compra ou venda"):
        assert trecho in b, trecho


def test_bootstrap_igual_ao_publicado_na_nuvem():
    """nuvem.json é gravado por `python -m rotina.nuvem conferir` com o texto do RemoteTrigger get: mudar o BOOTSTRAP sem
    republicar e conferir deixa este teste vermelho."""
    reg = json.loads((ROTINA / "nuvem.json").read_text(encoding="utf-8"))
    assert reg["trigger_id"] == nuvem.TRIGGER
    assert reg["sha256"] == nuvem.sha(nuvem.bloco()), "BOOTSTRAP mudou e a nuvem não foi conferida (ver BOOTSTRAP.md)"


def test_protocolo_tem_as_regras_da_fase_1():
    p = (ROTINA / "PROTOCOLO.md").read_text(encoding="utf-8")
    secoes = re.findall(r"^## (.+)$", p, flags=re.M)
    assert secoes[0].startswith("0. PRÉ-VOO")
    for trecho in ("Teto: 4 missões por noite", "Subagentes: no máximo 1 ao mesmo tempo", "claude-sonnet-5-5",
                   "Hora-limite: 06:30 BRT", "SEGUNDO PLANO", "/tmp/mesa_prevoo.fim", "/tmp/mesa_portao.fim",
                   "NUNCA, nem se a missão pedir: motor, doutrina, régua, golden", "nunca a escreva nem edite à mão",
                   "na nuvem, sem os testes de dados; o conferidor da manhã confirma", "A noite nunca junta"):
        assert trecho in " ".join(p.split()), trecho                               # espaços/quebras normalizados
    assert p.count("--suite --colar") == 1                                         # um portão completo por noite
    assert "checar_rotina.py --base origin/master --suite --colar; echo $? > /tmp/mesa_portao.fim) > " in p


# ---- pré-voo -----------------------------------------------------------------------------------------------------------

def _bash() -> str:
    """bash do Git no Windows (nunca o `System32\\bash.exe` do WSL); no Linux, o do sistema. Ausente = FALHA, nunca pula:
    teste pulado zera a trava B37 e deixa vermelha toda junção da manhã."""
    if os.name != "nt":
        b = shutil.which("bash")
        assert b, "bash ausente"
        return b
    exec_path = Path(subprocess.run(["git", "--exec-path"], capture_output=True, text=True).stdout.strip())
    for c in (exec_path.parents[2] / "bin" / "bash.exe", Path(r"C:\Program Files\Git\bin\bash.exe")):
        if c.is_file():
            return str(c)
    pytest.fail("bash do Git não encontrado (git --exec-path / C:\\Program Files\\Git\\bin\\bash.exe)")


def test_preflight_tem_trap_antes_de_tudo_e_marcador_em_toda_saida():
    sh = (RAIZ / "scripts" / "rotina_preflight.sh").read_text(encoding="utf-8")
    assert sh.index("trap ") < sh.index("RAIZ=")
    assert 'fim() { CODIGO="$1"; FIM_OK=1;' in sh
    assert not re.search(r"^\s*exit [01]\b", sh, flags=re.M)                      # só `fim` sai com 0/1 (grava o .fim)
    assert '"$UV" python install 3.14' in sh and "BLOQUEADO" in sh and "--ignore=backtest" in sh


def test_preflight_fora_do_git_sai_2_e_troca_o_marcador(tmp_path):
    script = tmp_path / "rotina_preflight.sh"
    shutil.copyfile(RAIZ / "scripts" / "rotina_preflight.sh", script)
    saida = tmp_path / "prevoo.md"
    (tmp_path / "prevoo.fim").write_text("0\n")                                   # marcador velho de outra noite
    env = {**os.environ, "MESA_PREVOO": saida.as_posix()}
    r = subprocess.run([_bash(), script.as_posix()], cwd=tmp_path, env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    assert r.returncode == 2, r.stdout + r.stderr
    assert (tmp_path / "prevoo.fim").read_text().strip() == "2"
    assert "AMBIENTE QUEBRADO" in saida.read_text(encoding="utf-8")
