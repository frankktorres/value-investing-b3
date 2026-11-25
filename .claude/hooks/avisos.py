"""Avisos das travas (pacote de autonomia, 25/11/2026). Nunca bloqueia: sai sempre 0.

    python avisos.py inicio   # SessionStart: a trava do push (B37) está ligada? (core.hooksPath = .githooks)
    python avisos.py fim      # Stop (trava 4.4): a árvore mudou depois da última suíte inteira verde?

Na nuvem (CLAUDE_CODE_REMOTE) não faz nada: lá não há hooksPath e o push vai para `claude/*`.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]          # a do próprio arquivo, não CLAUDE_PROJECT_DIR (sessão em subpasta)
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "ferramentas"))


def git(*args: str, cwd: Path | None = None) -> str:
    r = subprocess.run(["git", *args], cwd=cwd or RAIZ, capture_output=True, text=True, encoding="utf-8",
                       errors="replace")
    return r.stdout.strip() if r.returncode == 0 else ""


def aviso_hookspath(raiz: Path | None = None) -> str | None:
    atual = git("config", "--get", "core.hooksPath", cwd=raiz)
    if atual.replace("\\", "/").rstrip("/") == ".githooks":
        return None
    return (f"AVISO (B37): core.hooksPath = {atual or '(vazio)'}; a trava do push no master está DESLIGADA. "
            "Religar: git config core.hooksPath .githooks")


def aviso_suite(raiz: Path | None = None) -> str | None:
    import suite_marcador
    raiz = raiz or RAIZ
    try:
        arvore = suite_marcador.arvore_trabalho(raiz)
    except RuntimeError:
        return None
    verdes = suite_marcador.ler(raiz)
    if any(r["arvore"] == arvore for r in verdes):
        return None
    if not verdes:
        return ("AVISO (trava 4.4): nenhuma suíte inteira verde registrada nesta cópia; o push no master será recusado "
                "até rodar `cd ferramentas && python -m pytest --ignore=backtest -q`.")
    ultimo = verdes[-1]
    mudados = [l for l in git("diff", "--name-only", ultimo["arvore"], arvore, cwd=raiz).splitlines() if l.strip()]
    lista = ", ".join(mudados[:5]) + ("…" if len(mudados) > 5 else "")
    return (f"AVISO (trava 4.4): o código mudou depois da última suíte verde ({ultimo.get('data', '?')}): "
            f"{len(mudados)} arquivo(s) — {lista}. Rode a suíte inteira antes do push no master.")


def main(argv: list[str]) -> int:
    if os.environ.get("CLAUDE_CODE_REMOTE"):
        return 0
    modo = argv[0] if argv else ""
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")   # o Claude Code lê UTF-8; pipe no Windows é cp1252
        except AttributeError:
            pass
    try:
        if modo == "inicio":
            msg = aviso_hookspath()
            if msg:
                print(msg)
        elif modo == "fim":
            msg = aviso_suite()
            if msg:
                print(json.dumps({"systemMessage": msg}, ensure_ascii=False))
    except Exception as e:  # aviso nunca derruba o turno
        print(f"avisos.py {modo}: falhou ({type(e).__name__}: {e})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
