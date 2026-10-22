"""Conferência da manhã da rodada da nuvem (22/10/2026).

A rotina noturna (claude.ai, "VALUE B3 — noturno") grava num ramo `claude/*` e roda sem os dados locais (ZIPs da CVM,
COTAHIST, carteira): lá ~42 testes pulam, inclusive golden e dossiês — o "nenhuma palavra mudou" dela não é prova. Aqui:

1. `git fetch --prune`; candidatos = ramos `origin/claude/*` com commit que o master não tem (o mais antigo primeiro);
2. para cada um: worktree temporária em `origin/master` + merge do ramo (testa o RESULTADO da junção, não o ramo sozinho)
   + CÓPIA dos dados locais ignorados pelo git (cópia, não hard link: `open(p, "wb")` trunca o mesmo arquivo e um teste
   estragaria o original) + tela regerada + suíte completa com `EXIGIR_DADOS=1` (teste pulado = falha: verde sem rodar o
   golden era justamente o furo da nuvem);
3. verde e sem mexer em golden/doutrina → push do merge para o master, apaga o ramo remoto só se ele ainda estiver no
   commit testado (`--force-with-lease`; commit que chegou durante a suíte não se perde) e atualiza o checkout local com
   `pull --ff-only` se ele estiver limpo;
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
PREFIXO = "refs/remotes/origin/"
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
    """(com commit novo, do mais antigo ao mais novo; já contidos no master), como `origin/claude/...`. Nome cheio do ref:
    o `refname:short` vira `remotes/origin/...` quando existe ramo local homônimo."""
    novos, contidos = [], []
    for ref in git("for-each-ref", "--format=%(refname)", f"{PREFIXO}claude/").splitlines():
        r = "origin/" + ref.removeprefix(PREFIXO)
        (novos if int(git("rev-list", "--count", f"origin/master..{ref}")) else contidos).append(r)
    novos.sort(key=lambda r: int(git("log", "-1", "--format=%ct", r)))
    return novos, contidos


def apagar_remoto(ramo: str, sha: str) -> None:
    """Apaga `origin/<ramo>` só se ele ainda estiver em `sha` (o commit conferido): o que chegou depois fica."""
    nome = ramo.removeprefix("origin/")
    git("push", f"--force-with-lease={nome}:{sha}", "origin", "--delete", nome)


def dados_locais() -> list[str]:
    """Caminhos ignorados pelo git sob ferramentas/ que os testes leem (ZIPs, COTAHIST, raw, carteira). `-z`: sem ele o git
    devolve caminho com acento entre aspas e em octal, e o arquivo some da worktree em silêncio."""
    saida = git("ls-files", "-z", "--others", "--ignored", "--exclude-standard", "--directory", "ferramentas").split("\0")
    return [p.rstrip("/") for p in saida
            if p and "__pycache__" not in p and ".pytest_cache" not in p and not p.rstrip("/").startswith(FORA)]


def _um(origem: Path, destino: Path) -> None:
    if destino.exists():
        return
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)                          # cópia sempre: hard link deixaria o teste regravar o original


def espelhar(rel: str, wt: Path) -> None:
    origem = RAIZ / rel
    if origem.is_dir():
        for f in origem.rglob("*"):
            if f.is_file() and "__pycache__" not in f.parts:
                _um(f, wt / f.relative_to(RAIZ))
    elif origem.is_file():
        _um(origem, wt / rel)


def suite(wt: Path) -> tuple[int, str]:
    """Tela regerada (o teste do contrato real lê `web/dados/`) + pytest com EXIGIR_DADOS=1. Verde = rc 0 E nenhum pulado."""
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "CLAUDE_NO_SUITE_LOG": "1", "EXIGIR_DADOS": "1"}
    ferr = wt / "ferramentas"
    if (ferr / "painel" / "exportar.py").exists():
        subprocess.run([sys.executable, "-c", "from painel import exportar, contrato; exportar.main([]); contrato.main([])"],
                       cwd=ferr, capture_output=True, timeout=1800, env=env)   # falhou? o teste do contrato acusa
    r = subprocess.run([sys.executable, "-m", "pytest", "--ignore=backtest", "-q", "-p", "no:cacheprovider", "-rs"],
                       cwd=ferr, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800, env=env)
    linhas = r.stdout.splitlines()
    resumo = next((l.strip("= ") for l in reversed(linhas)
                   if any(k in l for k in (" passed", " failed", " error", " skipped", "no tests ran"))), "sem resumo")
    falhas = [l for l in linhas if l.startswith(("FAILED", "ERROR", "SKIPPED"))][:10]
    rc = r.returncode or (1 if " skipped" in resumo or resumo == "sem resumo" else 0)
    return rc, resumo + ("".join(f"\n    {f}" for f in falhas))


def conferir(ramo: str, so_conferir: bool) -> int:
    sha = git("rev-parse", ramo)                           # o commit conferido; só ele entra e só ele autoriza apagar
    idade = (time.time() - int(git("log", "-1", "--format=%ct", sha))) / 60
    if idade < PARADO_MIN:
        print(f"{ramo}: último commit há {idade:.0f} min — a rotina ainda deve estar rodando; fica para a próxima.")
        return PRECISA
    protegidos = git("diff", "--name-only", f"origin/master...{sha}", "--", *PROTEGIDOS)
    if protegidos:
        print(f"{ramo}: mexe em {protegidos.replace(chr(10), ', ')} (muda palavra) — junção só com decisão do Frank.")
        return PRECISA
    wt = Path(tempfile.mkdtemp(prefix="noite-"))
    try:
        git("worktree", "add", "--detach", str(wt), "origin/master")
        msg = f"Junta a rodada da nuvem ({ramo.removeprefix('origin/')}) — conferida com os dados locais (conferir_noite)"
        if subprocess.run(["git", "merge", "--no-ff", "--no-edit", "-m", msg, sha], cwd=wt,
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
        try:
            apagar_remoto(ramo, sha)
            print(f"{ramo}: VERDE — juntado ao master ({git('rev-parse', '--short', 'HEAD', cwd=wt)}) e ramo apagado.")
        except RuntimeError:
            print(f"{ramo}: VERDE — juntado ao master; o ramo recebeu commit novo durante a conferência e FICOU (amanhã entra).")
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
        for r in contidos:                                 # já estão no master: apagar não perde nada (lease: se andou, fica)
            try:
                apagar_remoto(r, git("rev-parse", r))
                print(f"{r}: já contido no master — ramo apagado.")
            except RuntimeError as ex:
                print(f"{r}: não apagado ({ex}).")
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
