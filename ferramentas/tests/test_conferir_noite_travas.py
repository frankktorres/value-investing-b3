"""Pacote de autonomia (25/11/2026, achado do senior): a junção da noite não leva ao master mudança de trava.

Na nuvem o Bash não passa pelo hook `trava_config`; um ramo `claude/*` que mudasse um arquivo protegido junto com o
`travas_hashes.json` daria suíte verde. Por isso o `conferir_noite.PROTEGIDOS` cobre a lista do hook (uma fonte conferida
pela outra) e o `git diff` com esses pathspecs acusa a mudança. Canário: repositório temporário, ramo que mexe em trava.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent.parent
RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / ".claude" / "hooks"))
import conferir_noite  # noqa: E402
import trava_config  # noqa: E402


def _coberto(rel: str) -> bool:
    for p in conferir_noite.PROTEGIDOS:
        if p.startswith(":(glob)**/"):
            if Path(rel).match(p.removeprefix(":(glob)**/")):
                return True
        elif rel == p or rel.startswith(p.rstrip("/") + "/"):
            return True
    return False


def test_protegidos_da_noite_cobrem_os_do_hook():
    do_hook = (set(trava_config.TRAVAS_ARQUIVOS) | set(trava_config.GOLDEN_DADOS) | {trava_config.PISO}
               | {p + "x.py" for p in trava_config.TRAVAS_PREFIXOS} | {".claude/settings.json"}
               | {f"ferramentas/{n}" for n in trava_config.CONFIG_NOMES} | {"ferramentas/tests/x_catraca.json"})
    faltam = sorted(r for r in do_hook if not _coberto(r))
    assert not faltam, f"conferir_noite.PROTEGIDOS não cobre: {faltam}"


def _g(cwd, *a):
    return subprocess.run(["git", *a], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


@pytest.mark.parametrize("rel", [".githooks/pre-push", "ferramentas/tests/conftest.py", ".claude/settings.json",
                                 "ferramentas/tests/motor_puro_catraca.json", "ferramentas/golden.py"])
def test_canario_diff_da_juncao_acusa_trava(tmp_path, rel):
    _g(tmp_path, "init", "-q", "-b", "master")
    _g(tmp_path, "config", "user.email", "t@e")
    _g(tmp_path, "config", "user.name", "t")
    (tmp_path / "a.md").write_text("a", encoding="utf-8")
    _g(tmp_path, "add", "-A")
    _g(tmp_path, "commit", "-q", "-m", "base")
    _g(tmp_path, "checkout", "-q", "-b", "claude/x")
    (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / rel).write_text("afrouxa", encoding="utf-8")
    _g(tmp_path, "add", "-A")
    _g(tmp_path, "commit", "-q", "-m", "ramo")
    saida = _g(tmp_path, "diff", "--name-only", "master...claude/x", "--", *conferir_noite.PROTEGIDOS)
    assert rel in saida.splitlines()
