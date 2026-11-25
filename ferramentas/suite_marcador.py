"""B37 (25/11/2026): registro das árvores em que a suíte INTEIRA passou, lido pela trava do push no `master`.

Por quê: o hook Stop só guarda snapshot em `wip/auto` e nada impedia um push vermelho no `master` (regra "nada no master
sem a suíte inteira verde depois da última mudança" estava só no texto). Modelo: UNION `.githooks/trava_main.py`.

- `arvore_trabalho()` = hash da árvore que a suíte está testando: HEAD + tudo o que não é ignorado na árvore de trabalho
  (índice temporário; HEAD, índice real e arquivos não mudam). É o mesmo hash que um commit com esse conteúdo terá.
- Só o `conftest.py` chama `registrar_verde`, no fim da suíte inteira com 0 falha, 0 erro, 0 pulado e a árvore igual à do
  início (arquivo mexido durante a suíte = nada registrado).
- O registro fica em `<git-common-dir>/mesa_suite_verde.json`: fora da árvore, nunca commitado, o mesmo para a worktree
  do `conferir_noite.py`. Editar à mão é proibido (deny no `.claude/settings.json`); a trava ainda exige nº de aprovados
  ≥ piso (`.githooks/piso_testes.json`, só sobe).
Só stdlib.
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import tempfile
from pathlib import Path

NOME = "mesa_suite_verde.json"
MAX_REGISTROS = 30


def _git(*args: str, cwd: Path | str | None = None, env: dict | None = None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                       env=env)
    if r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {(r.stderr or r.stdout).strip()[-300:]}")
    return r.stdout.strip()


def raiz(cwd: Path | str | None = None) -> Path:
    return Path(_git("rev-parse", "--show-toplevel", cwd=cwd))


def arquivo_registro(cwd: Path | str | None = None) -> Path:
    comum = Path(_git("rev-parse", "--git-common-dir", cwd=cwd))
    if not comum.is_absolute():
        comum = Path(cwd or os.getcwd()) / comum
    return comum.resolve() / NOME


def arvore_trabalho(cwd: Path | str | None = None) -> str:
    """Hash da árvore HEAD + árvore de trabalho (não ignorados), sem tocar HEAD, índice real ou arquivos."""
    topo = raiz(cwd)
    with tempfile.TemporaryDirectory() as d:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(d) / "idx")}
        _git("read-tree", "HEAD", cwd=topo, env=env)
        _git("add", "-A", "--", ".", cwd=topo, env=env)
        return _git("write-tree", cwd=topo, env=env)


def ler(cwd: Path | str | None = None) -> list[dict]:
    """Registros verdes; arquivo ausente ou estragado = nenhum (a trava recusa)."""
    try:
        dados = json.loads(arquivo_registro(cwd).read_text(encoding="utf-8"))
        return [r for r in dados.get("verdes", []) if isinstance(r, dict) and isinstance(r.get("arvore"), str)]
    except (OSError, ValueError, AttributeError, RuntimeError):
        return []


def registrar_verde(arvore: str, aprovados: int, cwd: Path | str | None = None) -> Path:
    """Acrescenta (ou renova) o registro da árvore. Só o conftest chama."""
    arq = arquivo_registro(cwd)
    antigos = [r for r in ler(cwd) if r["arvore"] != arvore]
    novo = {"arvore": arvore, "aprovados": int(aprovados), "data": datetime.datetime.now().isoformat(timespec="seconds")}
    arq.write_text(json.dumps({"verdes": (antigos + [novo])[-MAX_REGISTROS:]}, ensure_ascii=False, indent=1),
                   encoding="utf-8")
    return arq


def deve_registrar(contagem: dict, parcial: bool, exitstatus: int, inicio: str | None, fim: str | None) -> bool:
    """Suíte inteira (não parcial), rc 0, nenhum falho/erro/pulado, ≥ 1 aprovado e a árvore igual do início ao fim."""
    return (not parcial and exitstatus == 0 and contagem.get("passed", 0) > 0
            and not any(contagem.get(k, 0) for k in ("failed", "error", "skipped"))
            and bool(inicio) and inicio == fim)


def verde_da_arvore(arvore: str, cwd: Path | str | None = None) -> dict | None:
    return next((r for r in reversed(ler(cwd)) if r["arvore"] == arvore), None)
