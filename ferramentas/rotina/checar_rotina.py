"""Portão da rotina noturna da Mesa (26/11/2026; molde do UNION, sem regra clínica).

Prova, a partir do git e nunca à mão, que a rodada da nuvem só mexeu no que a sessão do dia carimbou:

1. diff = `merge-base(--base, HEAD)` × árvore de trabalho (+ não rastreados) ou × `--head SHA` (modo da manhã, sem árvore);
2. caminho PROIBIDO (motor, doutrina, régua, golden, DNA, pré-registro, travas, config de teste, `_historico` existente, a
   própria rotina) → PARAR, mesmo que esteja no escopo;
3. senão, precisa estar em SEMPRE (docs de controle da noite, pasta do Desktop, snapshot NOVO de upload-desktop) ou no
   `escopo:` de uma missão carimbada no `docs/MISSOES.md` da BASE (`git show`): a noite não alarga o próprio escopo;
4. linha com `pronta:`/`escopo:` acrescentada ou alterada no MISSOES pela noite → PARAR (carimbo é da sessão do dia);
5. diff vazio → PARAR (noite sem entrega).

Autossuficiente de propósito (só biblioteca padrão, nada do repo): a manhã (`conferir_noite.py`) extrai ESTE arquivo da
`origin/master` por `git show` para uma pasta vazia e o roda contra o ramo; assim o portão que vale é o da base, nunca o que
a noite poderia ter editado. Compatível com Python 3.11 (a nuvem pode cair no python3 do sistema).

    python ferramentas/rotina/checar_rotina.py --base origin/master                   # pré-checagem (noite)
    python ferramentas/rotina/checar_rotina.py --base origin/master --suite --colar   # portão final (noite)
    python checar_rotina.py --repo <raiz> --base origin/master --head <sha>           # manhã (estático)

Saída: 0 = OK; 1 = PARAR; 2 = erro de uso/ambiente (a manhã trata qualquer código ≠ 0 como "precisa do Frank").
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# (glob, motivo). `*` não cruza `/`; `**/` = zero ou mais pastas; `/**` no fim = tudo abaixo.
PROIBIDO: tuple[tuple[str, str], ...] = (
    ("01-doutrina-value-investing.md", "doutrina"),
    ("03-hall-de-acoes.md", "palavra do hall"),
    ("09-diario-de-decisoes.md", "diário de método"),
    ("docs/00-DNA.md", "DNA (só o Frank)"),
    ("docs/PRE-REGISTRO-v3.md", "pré-registro (método)"),
    ("CLAUDE.md", "regras do projeto"),
    ("ferramentas/*.py", "motor e módulos da raiz que mudam palavra (inclui motor_*, golden.py, conferir_noite.py)"),
    ("ferramentas/tests/golden*", "golden"),
    ("ferramentas/tests/travas_hashes.json", "trava"),
    ("ferramentas/tests/test_travas.py", "trava"),
    ("ferramentas/tests/test_b37_trava_master.py", "trava"),
    ("ferramentas/tests/test_motor_puro.py", "trava"),
    ("ferramentas/tests/test_docs_caminhos.py", "trava"),
    ("ferramentas/tests/test_conferir_noite*.py", "trava da manhã"),
    ("ferramentas/tests/test_rotina*.py", "testes da rotina"),
    ("ferramentas/dossie/**", "dossiê (palavra)"),
    ("ferramentas/dados/**", "dados"),
    ("ferramentas/backtest/**", "régua/backtest"),
    ("ferramentas/oraculo/**", "oráculo (método)"),
    ("ferramentas/prospectivo/**", "registro prospectivo (append-only)"),
    ("**/insumos/**", "insumos do motor"),
    ("**/conftest.py", "config de teste"),
    ("**/pytest.ini", "config de teste"),
    ("**/pyproject.toml", "config de teste"),
    ("**/setup.cfg", "config de teste"),
    ("**/tox.ini", "config de teste"),
    ("**/ruff.toml", "config de teste"),
    ("**/.ruff.toml", "config de teste"),
    ("**/mypy.ini", "config de teste"),
    ("**/.mypy.ini", "config de teste"),
    ("**/*catraca*.json", "catraca"),
    ("requirements*", "dependências"),
    (".githooks/**", "trava B37"),
    (".claude/**", "config/hooks/skills/agentes"),
    ("ferramentas/rotina/**", "a própria rotina"),
    ("docs/ops/rotina/**", "a própria rotina"),
    ("scripts/rotina_preflight.sh", "a própria rotina"),
    ("scripts/cloud_setup.sh", "a própria rotina"),
)
SEMPRE = ("docs/RELATORIO-DIARIO.md", "docs/MISSOES.md", "docs/BACKLOG.md", "docs/DECISOES.md", "docs/PENDENTE-FRANK.md")
SEMPRE_PASTA = "UPLOAD CLAUDE DESKTOP/"                       # regerada pelo `desktop.atualizar` (último passo da noite)
HIST_NOVO = re.compile(r"^_historico/[^/]+ upload-desktop/[^/]+$")   # snapshot do desktop.atualizar: só arquivo NOVO
HIST = re.compile(r"(^|/)_historico/")
CARIMBO = re.compile(r"Carimbo \(nuvem\):\*?\s*([A-Za-z]+\d+[a-z]?)\b(.*)$")
ESCOPO = re.compile(r"escopo:\s*((?:`[^`]+`[,;\s]*)+)")
PRONTA = re.compile(r"pronta:\s*`?([0-9a-f]{7,40})\b")
MISSOES = "docs/MISSOES.md"
RELATORIO = "docs/RELATORIO-DIARIO.md"


def _regex(glob: str) -> re.Pattern[str]:
    out, i = "", 0
    while i < len(glob):
        if glob.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif glob.startswith("**", i):
            out, i = out + ".*", i + 2
        elif glob[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif glob[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(glob[i]), i + 1
    return re.compile(out + r"\Z")


_PROIBIDO = tuple((_regex(g), g, m) for g, m in PROIBIDO)


def proibido(caminho: str, status: str = "M") -> str | None:
    """Motivo se o caminho é proibido para a noite; None se não é."""
    if HIST.search(caminho):
        return None if (status == "A" and HIST_NOVO.match(caminho)) else "_historico existente (ou fora do snapshot do desktop)"
    for rx, g, m in _PROIBIDO:
        if rx.match(caminho):
            return f"{m} [{g}]"
    return None


class Git:
    def __init__(self, repo: Path):
        self.repo = repo

    def __call__(self, *args: str, check: bool = True) -> str:
        r = subprocess.run(["git", "-c", "core.quotepath=off", *args], cwd=self.repo, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if check and r.returncode:
            raise RuntimeError(f"git {' '.join(args)}: {(r.stderr or r.stdout).strip()[-300:]}")
        return r.stdout

    def ok(self, *args: str) -> bool:
        return subprocess.run(["git", *args], cwd=self.repo, capture_output=True).returncode == 0


def tocados(git: Git, base: str, head: str | None) -> list[tuple[str, str]]:
    """[(status, caminho)] do diff; `--no-renames`: renomear vira D + A (apagar em _historico continua pego)."""
    alvo = [base, head] if head else [base]
    campos = git("diff", "--name-status", "--no-renames", "-z", *alvo).split("\0")
    pares = [(campos[i][:1], campos[i + 1]) for i in range(0, len(campos) - 1, 2) if campos[i]]
    if not head:
        pares += [("A", p) for p in git("ls-files", "-z", "--others", "--exclude-standard").split("\0") if p]
    return sorted(set(pares), key=lambda p: p[1])


def missoes_da_base(git: Git, base: str) -> tuple[dict[str, set[str]], list[str]]:
    """{ID: caminhos do escopo} das missões carimbadas no MISSOES da base, e avisos (carimbo inválido não vale)."""
    try:
        texto = git("show", f"{base}:{MISSOES}")
    except RuntimeError:
        return {}, [f"{MISSOES} ausente na base"]
    escopos: dict[str, set[str]] = {}
    avisos: list[str] = []
    for linha in texto.splitlines():
        m = CARIMBO.search(linha)
        if not m:
            continue
        mid, resto = m.group(1), m.group(2)
        e, p = ESCOPO.search(resto), PRONTA.search(resto)
        if not e or not p:
            avisos.append(f"{mid}: carimbo sem `escopo:` ou sem `pronta:` — não vale")
            continue
        if not git.ok("merge-base", "--is-ancestor", p.group(1), base):
            avisos.append(f"{mid}: `pronta: {p.group(1)}` não é ancestral da base — não vale")
            continue
        itens = re.findall(r"`([^`]+)`", e.group(1))
        glob = [i for i in itens if any(c in i for c in "*?[")]
        if glob:                                            # fase 1: só caminho literal (senior, 26/11)
            avisos.append(f"{mid}: escopo com glob {glob} — na fase 1 só caminho literal; ignorado")
        escopos.setdefault(mid, set()).update(i.strip() for i in itens if i not in glob)
    return escopos, avisos


def _carimbos(texto: str) -> set[str]:
    return {l.strip() for l in texto.splitlines() if "pronta:" in l or "escopo:" in l}


def carimbo_novo(git: Git, base: str, head: str | None) -> list[str]:
    try:
        antes = git("show", f"{base}:{MISSOES}")
    except RuntimeError:
        antes = ""
    if head:
        depois = git("show", f"{head}:{MISSOES}", check=False)
    else:
        arq = git.repo / MISSOES
        depois = arq.read_text(encoding="utf-8") if arq.exists() else ""
    return sorted(_carimbos(depois) - _carimbos(antes))


def avaliar(git: Git, base_ref: str, head: str | None) -> tuple[list[str], list[str], str]:
    """(linhas, motivos de PARAR, merge-base)."""
    ponta = head or "HEAD"
    base = git("merge-base", base_ref, ponta).strip()
    escopos, avisos = missoes_da_base(git, base)
    dono = {c: mid for mid, cs in escopos.items() for c in cs}
    linhas = [f"base {base[:7]} ({base_ref}) · ponta {git('rev-parse', '--short', ponta).strip()}"
              f"{'' if head else ' + árvore de trabalho'} · missões carimbadas: {', '.join(sorted(escopos)) or 'nenhuma'}"]
    linhas += [f"aviso: {a}" for a in avisos]
    parar: list[str] = []
    pares = tocados(git, base, head)
    if not pares:
        parar.append("diff vazio: noite sem entrega")
    for st, c in pares:
        motivo = proibido(c, st)
        if motivo:
            parar.append(f"{st} {c}: PROIBIDO — {motivo}")
        elif c in SEMPRE or c.startswith(SEMPRE_PASTA) or HIST_NOVO.match(c):
            linhas.append(f"OK {st} {c} (controle da noite)")
        elif c in dono:
            linhas.append(f"OK {st} {c} (escopo {dono[c]})")
        else:
            parar.append(f"{st} {c}: FORA DO ESCOPO de toda missão carimbada na base")
    if any(c == MISSOES for _, c in pares):
        parar += [f"{MISSOES}: carimbo novo ou alterado pela noite (é da sessão do dia): {l[:90]}"
                  for l in carimbo_novo(git, base, head)]
    return linhas, parar, base


def suite(repo: Path) -> tuple[int, str]:
    r = subprocess.run([sys.executable, "-m", "pytest", "--ignore=backtest", "-q", "-p", "no:cacheprovider", "-ra"],
                       cwd=repo / "ferramentas", capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=5400, env=None)
    ls = r.stdout.splitlines()
    resumo = next((l.strip("= ") for l in reversed(ls) if any(k in l for k in (" passed", " failed", " error"))), "sem resumo")
    falhas = [l for l in ls if l.startswith(("FAILED", "ERROR"))][:15]
    return r.returncode, resumo + "".join(f"\n  {f}" for f in falhas)


def colar(repo: Path, linhas: list[str], parar: list[str], base: str, git: Git) -> None:
    """Escreve a prova no 1º bloco `## … Rotina na nuvem` do relatório (substitui a prova anterior desse bloco)."""
    arq = repo / RELATORIO
    texto = arq.read_text(encoding="utf-8")
    ls = texto.split("\n")
    ini = next((i for i, l in enumerate(ls) if l.startswith("## ")), None)
    if ini is None or "Rotina na nuvem" not in ls[ini]:
        raise ValueError("o 1º bloco `## ` do relatório não é o da noite (`## AAAA-MM-DD · Rotina na nuvem (ramo …)`)")
    fim = next((i for i in range(ini + 1, len(ls)) if ls[i].startswith("## ")), len(ls))
    bloco = ls[ini:fim]
    if any(l.startswith("- **Prova (gerada por") for l in bloco):
        k = next(i for i, l in enumerate(bloco) if l.startswith("- **Prova (gerada por"))
        f = next((i for i in range(k + 3, len(bloco)) if bloco[i].strip() == "```"), len(bloco) - 1)
        bloco = bloco[:k] + bloco[f + 1:]
    while bloco and not bloco[-1].strip():
        bloco.pop()
    sujo = len([p for p in git("status", "--porcelain").splitlines() if p.strip()])
    head = git("rev-parse", "--short", "HEAD").strip() + (f"+{sujo}-sem-commit" if sujo else "")
    veredito = "PARAR" if parar else "OK"
    bloco += [f"- **Prova (gerada por `checar_rotina.py`; não editar à mão):** PORTÃO {veredito}",
              f"<!-- prova: checar_rotina base={base[:7]} head={head} -->", "```text",
              *linhas, *[f"PARAR {p}" for p in parar], "```", ""]
    arq.write_text("\n".join(ls[:ini] + bloco + ls[fim:]), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", type=Path, help="raiz do repositório (padrão: o git da pasta atual)")
    ap.add_argument("--base", default="origin/master")
    ap.add_argument("--head", help="commit do ramo (modo da manhã: estático, sem árvore de trabalho)")
    ap.add_argument("--suite", action="store_true", help="roda a suíte (sem backtest) e PARA se falhar")
    ap.add_argument("--colar", action="store_true", help="grava a prova no bloco da noite do relatório")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if a.head and (a.suite or a.colar):
        ap.error("--head é o modo estático da manhã: sem --suite/--colar")
    try:
        repo = (a.repo or Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                                              check=True).stdout.strip())).resolve()
        git = Git(repo)
        linhas, parar, base = avaliar(git, a.base, a.head)
        if a.suite and not parar:
            rc, resumo = suite(repo)
            linhas.append(f"suíte (nuvem, sem os testes de dados; o conferidor da manhã confirma): rc {rc} · {resumo}")
            if rc:
                parar.append(f"suíte vermelha (rc {rc})")
        if a.colar:
            try:
                colar(repo, linhas, parar, base, git)
            except ValueError as ex:
                parar.append(f"prova NÃO colada: {ex}")
    except (RuntimeError, OSError, subprocess.CalledProcessError) as ex:
        print(f"ERRO do portão: {ex}")
        return 2
    print("\n".join(linhas + [f"PARAR {p}" for p in parar]))
    print(f"PORTÃO: {'PARAR (' + str(len(parar)) + ')' if parar else 'OK'}")
    return 1 if parar else 0


if __name__ == "__main__":
    sys.exit(main())
