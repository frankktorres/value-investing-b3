"""Conferência da manhã da rodada da nuvem (22/10/2026).

A rotina noturna (claude.ai, "VALUE B3 — noturno") grava num ramo `claude/*` e roda sem os dados locais (ZIPs da CVM,
COTAHIST, carteira): lá ~42 testes pulam, inclusive golden e dossiês — o "nenhuma palavra mudou" dela não é prova. Aqui:

1. `git fetch --prune`; candidatos = ramos `origin/claude/*` com commit que o master não tem (o mais antigo primeiro);
2. para cada um: worktree temporária em `origin/master` + merge do ramo (testa o RESULTADO da junção, não o ramo sozinho)
   + os dados locais ignorados pelo git (ZIP/parquet por hard link; o resto copiado, para um teste que regrave um JSON não
   tocar no original) + suíte completa (`pytest --ignore=backtest`);
3. verde e sem mexer em golden/doutrina → push do merge para o master, apaga o ramo remoto (já contido; nada se perde) e
   atualiza o checkout local com `pull --ff-only` se ele estiver limpo;
4. senão deixa o ramo como está e diz por quê. Ramo `claude/*` sem commit novo (já contido no master) é apagado.

    python conferir_noite.py                 # confere e junta
    python conferir_noite.py --so-conferir   # só roda os testes da junção; não envia nada

Saída: 0 = nada a fazer ou tudo juntado; 30 = testes vermelhos; 31 = precisa do Frank (golden/doutrina, conflito, ramo ainda
recebendo commit, push recusado). Pelo Agendador: `agendador/noite.vbs <python> conferir` → log em monitor/conferir.log.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PROTEGIDOS = ("ferramentas/tests/golden.json", "01-doutrina-value-investing.md")   # muda palavra: só com decisão do Frank
FORA = ("ferramentas/painel/web/dados", "ferramentas/dados/cvm/_antes", "ferramentas/monitor",
        "ferramentas/dados/suite_ultima.json")             # regerável, velho ou log: não vai para a worktree
LINK = (".zip", ".parquet")                                # grandes e só lidos (quem regrava troca o arquivo inteiro)
PARADO_MIN = 30                                            # commit mais novo que isto = a rotina ainda está rodando
VERMELHO, PRECISA = 30, 31


def git(*args: str, cwd: Path | None = None, check: bool = True) -> str:
    # cwd resolvido NA CHAMADA: um default `= RAIZ` fica preso na definição e o teste que troca RAIZ empurrou para o
    # GitHub real em 22/10/2026 (a mesma armadilha do HISTORICO do monitor_semanal)
    r = subprocess.run(["git", *args], cwd=cwd or RAIZ, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {(r.stderr or r.stdout).strip()[-400:]}")
    return r.stdout.strip()


def ramos() -> tuple[list[str], list[str]]:
    """(com commit novo, do mais antigo ao mais novo; já contidos no master)."""
    novos, contidos = [], []
    for r in git("for-each-ref", "--format=%(refname:short)", "refs/remotes/origin/claude/").splitlines():
        (novos if int(git("rev-list", "--count", f"origin/master..{r}")) else contidos).append(r)
    novos.sort(key=lambda r: int(git("log", "-1", "--format=%ct", r)))
    return novos, contidos


def dados_locais() -> list[str]:
    """Caminhos ignorados pelo git sob ferramentas/ que os testes leem (ZIPs, COTAHIST, raw, carteira)."""
    saida = git("ls-files", "--others", "--ignored", "--exclude-standard", "--directory", "ferramentas").splitlines()
    return [p.rstrip("/") for p in saida
            if "__pycache__" not in p and ".pytest_cache" not in p and not p.rstrip("/").startswith(FORA)]


def _um(origem: Path, destino: Path) -> None:
    if destino.exists():
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    if origem.suffix.lower() in LINK:
        try:
            os.link(origem, destino)
            return
        except OSError:
            pass                                           # outro disco ou FS sem hard link: copia
    shutil.copy2(origem, destino)


def espelhar(rel: str, wt: Path) -> None:
    origem = RAIZ / rel
    if origem.is_dir():
        for f in origem.rglob("*"):
            if f.is_file() and "__pycache__" not in f.parts:
                _um(f, wt / f.relative_to(RAIZ))
    elif origem.is_file():
        _um(origem, wt / rel)


def suite(wt: Path) -> tuple[int, str]:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "CLAUDE_NO_SUITE_LOG": "1"}
    r = subprocess.run([sys.executable, "-m", "pytest", "--ignore=backtest", "-q", "-p", "no:cacheprovider"],
                       cwd=wt / "ferramentas", capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=1800, env=env)
    linhas = r.stdout.splitlines()
    resumo = next((l.strip("= ") for l in reversed(linhas) if " passed" in l or " failed" in l or " error" in l), "sem resumo")
    falhas = [l for l in linhas if l.startswith(("FAILED", "ERROR"))][:10]
    return r.returncode, resumo + ("".join(f"\n    {f}" for f in falhas))


def conferir(ramo: str, so_conferir: bool) -> int:
    idade = (time.time() - int(git("log", "-1", "--format=%ct", ramo))) / 60
    if idade < PARADO_MIN:
        print(f"{ramo}: último commit há {idade:.0f} min — a rotina ainda deve estar rodando; fica para a próxima.")
        return PRECISA
    protegidos = git("diff", "--name-only", f"origin/master...{ramo}", "--", *PROTEGIDOS)
    if protegidos:
        print(f"{ramo}: mexe em {protegidos.replace(chr(10), ', ')} (muda palavra) — junção só com decisão do Frank.")
        return PRECISA
    wt = Path(tempfile.mkdtemp(prefix="noite-"))
    try:
        git("worktree", "add", "--detach", str(wt), "origin/master")
        msg = f"Junta a rodada da nuvem ({ramo.removeprefix('origin/')}) — conferida com os dados locais (conferir_noite)"
        if subprocess.run(["git", "merge", "--no-ff", "--no-edit", "-m", msg, ramo], cwd=wt,
                          capture_output=True).returncode:
            git("merge", "--abort", cwd=wt, check=False)
            print(f"{ramo}: conflito com o master — junção à mão.")
            return PRECISA
        for rel in dados_locais():
            espelhar(rel, wt)
        rc, resumo = suite(wt)
        print(f"{ramo}: suíte da junção com dados locais — {resumo}")
        if rc != 0:
            print(f"{ramo}: VERMELHO — ramo mantido, nada foi para o master.")
            return VERMELHO
        if so_conferir:
            return 0
        envio = subprocess.run(["git", "push", "origin", "HEAD:master"], cwd=wt, capture_output=True, text=True)
        if envio.returncode:
            print(f"{ramo}: push recusado (o master andou durante a conferência?): {envio.stderr.strip()[-300:]}")
            return PRECISA
        git("push", "origin", "--delete", ramo.removeprefix("origin/"))
        print(f"{ramo}: VERDE — juntado ao master ({git('rev-parse', '--short', 'HEAD', cwd=wt)}) e ramo apagado.")
        return 0
    finally:
        git("worktree", "remove", "--force", str(wt), check=False)
        shutil.rmtree(wt, ignore_errors=True)
        git("worktree", "prune", check=False)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--so-conferir", action="store_true", help="só roda os testes da junção; não envia nada")
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"conferir_noite {time.strftime('%Y-%m-%d %H:%M')}")
    git("fetch", "--prune", "origin")
    novos, contidos = ramos()
    if not a.so_conferir:
        for r in contidos:                                 # já estão no master: apagar não perde nada
            git("push", "origin", "--delete", r.removeprefix("origin/"))
            print(f"{r}: já contido no master — ramo apagado.")
    if not novos:
        print("Nenhuma rodada nova da nuvem para conferir.")
        return 0
    rc = max(conferir(r, a.so_conferir) for r in novos)
    if rc == 0 and not a.so_conferir:
        limpo = not git("status", "--porcelain", "--untracked-files=no") and git("rev-parse", "--abbrev-ref", "HEAD") == "master"
        if limpo and not subprocess.run(["git", "pull", "--ff-only", "origin", "master"], cwd=RAIZ,
                                        capture_output=True).returncode:
            print("Checkout local atualizado (pull --ff-only).")
        else:
            print("Checkout local NÃO atualizado (alterações locais ou fora do master): rode `git pull` quando puder.")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
