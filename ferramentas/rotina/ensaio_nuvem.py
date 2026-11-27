"""Ensaio da nuvem (27/11/2026): roda a suíte numa cópia da árvore ATUAL sem nada que o git ignora (sem dados).

Por que existe: a 1ª noite da rotina (27/11) deu BASE VERMELHA porque 4 testes liam `ferramentas/dados/raw` sem pular e o
`.gitignore` só casava pastas ausentes sem a barra final. No PC tudo estava verde — só um clone sem dados mostra isso.
Rodar antes de carimbar missões para a noite (`/mesa-fechar`, passo 2) e depois de mexer em teste que lê dado local.

Como: `git stash create` (árvore com as alterações não commitadas) → worktree temporário destacado → copia os arquivos novos
não ignorados → `python -m pytest --ignore=backtest -q` em `ferramentas/`. Verde = rc 0 (pulos são esperados: é a nuvem).
Não toca no checkout nem no índice; o worktree é removido no fim.

    cd ferramentas && python -m rotina.ensaio_nuvem
"""
from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parents[2]


def git(*args: str, cwd: pathlib.Path = RAIZ) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                          check=True).stdout.strip()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    alvo = git("stash", "create") or git("rev-parse", "HEAD")
    novos = [a for a in git("ls-files", "-z", "--others", "--exclude-standard").split("\0") if a]
    wt = pathlib.Path(tempfile.mkdtemp(prefix="mesa_ensaio_nuvem_"))
    try:
        git("worktree", "add", "--detach", str(wt), alvo)
        for a in novos:
            destino = wt / a
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(RAIZ / a, destino)
        r = subprocess.run([sys.executable, "-m", "pytest", "--ignore=backtest", "-q", "-p", "no:cacheprovider"],
                           cwd=wt / "ferramentas", capture_output=True, text=True, encoding="utf-8", errors="replace")
        linhas = r.stdout.strip().splitlines()
        for ln in linhas:
            if ln.startswith(("FAILED", "ERROR")):
                print(ln)
        print(f"ensaio da nuvem ({alvo[:7]}, {len(novos)} novos): {linhas[-1] if linhas else 'sem resumo'}")
        print("VERDE — a nuvem deve achar a base verde." if r.returncode == 0 else
              "VERMELHO — a noite pararia em BASE VERMELHA; consertar antes de carimbar missões.")
        return r.returncode
    finally:
        git("worktree", "remove", "--force", str(wt))
        shutil.rmtree(wt, ignore_errors=True)
        git("worktree", "prune")


if __name__ == "__main__":
    raise SystemExit(main())
