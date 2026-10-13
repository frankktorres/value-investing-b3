"""Hook Stop: commit + push automáticos.

- Na nuvem (CLAUDE_CODE_REMOTE) não faz nada: lá o Claude commita sozinho (ver CLAUDE.md).
- Varre segredo nos arquivos alterados; se achar, não commita nada.
- Testes dos módulos alterados verdes -> commit em master + push.
- Testes vermelhos, ausentes para código, ou DRY -> commit só no ramo wip/auto (plumbing; a árvore de trabalho não muda).
- Só doc/dados sem código -> commit direto em master.
Uso: python auto_commit.py [--dry]   (--dry só mostra a decisão)
"""
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2])
FERR = RAIZ / "ferramentas"
DRY = "--dry" in sys.argv
RAMO = "master"
WIP = "wip/auto"

SEGREDO_ARQ = re.compile(r"(^|/)\.env|\.pem$|\.key$|\.p12$|id_rsa|credentials", re.I)
SEGREDO_TXT = re.compile(
    r"(ghp_|gho_|github_pat_)[A-Za-z0-9_]{20,}|sk-ant-[A-Za-z0-9_-]{20,}|AKIA[0-9A-Z]{16}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY"
    r"|(api[_-]?key|secret|passw(or)?d|senha|token)\s*[:=]\s*['\"][A-Za-z0-9_\-/+=]{16,}['\"]", re.I)
PESSOAL = re.compile(r"(?i)pre[cç]o m[eé]dio\s*[:=]\s*R?\$?\s*\d|quantidade\s*[:=]\s*\d+\s*a[cç][oõ]es|corretora\s*[:=]\s*\w+|\bCPF\b\s*[:=]?\s*\d{3}\.")
EXCECAO_TXT = {"auto_commit.py"}  # este arquivo contém os padrões


def git(*args, env=None, check=False):
    r = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True, env=env, encoding="utf-8", errors="replace")
    if check and r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r


def alterados():
    """Caminhos alterados/novos (não ignorados) e removidos."""
    r = git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    itens, partes = [], r.stdout.split("\0")
    i = 0
    while i < len(partes):
        p = partes[i]
        i += 1
        if len(p) < 4:
            continue
        st, caminho = p[:2], p[3:]
        if st[0] in "RC":
            i += 1  # pula o caminho de origem
        itens.append((st, caminho))
    return itens


def varrer_segredo(itens):
    achados = []
    for st, c in itens:
        if "D" in st:
            continue
        if SEGREDO_ARQ.search(c.replace("\\", "/")):
            achados.append(f"{c}: nome de arquivo de segredo")
            continue
        f = RAIZ / c
        if f.name in EXCECAO_TXT or not f.is_file() or f.stat().st_size > 5_000_000:
            continue
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        m = SEGREDO_TXT.search(txt) or PESSOAL.search(txt)
        if m:
            achados.append(f"{c}: padrão de segredo/dado pessoal ({m.group(0)[:12]}…)")
    return achados


def testes_dos_modulos(itens):
    """Retorna (lista_de_comandos, motivo_sem_teste). Código alterado fora de ferramentas/ ou no backtest -> sem verificação."""
    py = [c.replace("\\", "/") for st, c in itens if c.endswith(".py") and "D" not in st]
    if not py:
        return [], None
    alvos = set()
    for c in py:
        if not c.startswith("ferramentas/"):
            return None, f"código fora de ferramentas/: {c}"
        if c.startswith("ferramentas/backtest/"):
            return None, f"backtest (suíte de ~13 min, só local): {c}"
        p = Path(c)
        if "tests" in p.parts or p.name.startswith("test_"):
            alvos.add(str(RAIZ / c))
            continue
        stem = p.stem
        achou = False
        for t in FERR.rglob("test_*.py"):
            if "backtest" in t.parts:
                continue
            try:
                if re.search(rf"\b{re.escape(stem)}\b", t.read_text(encoding="utf-8", errors="ignore")):
                    alvos.add(str(t))
                    achou = True
            except OSError:
                pass
        if not achou:
            return None, f"nenhum teste referencia o módulo {stem}"
    return [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", *sorted(alvos)], None


def rodar_testes(cmd):
    r = subprocess.run(cmd, cwd=FERR, capture_output=True, text=True, timeout=900, encoding="utf-8", errors="replace")
    return r.returncode == 0, (r.stdout + r.stderr)[-1500:]


def msg_commit(itens, sufixo=""):
    n = len(itens)
    nomes = ", ".join(Path(c).name for _, c in itens[:3]) + ("…" if n > 3 else "")
    return f"auto: {n} arquivo(s) — {nomes}{sufixo}\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"


def commit_master(itens, msg):
    for st, c in itens:
        git("add", "-A", "--", c, check=True)  # sempre caminho a caminho, nunca "add ."
    git("commit", "-q", "-m", msg, check=True)
    return git("push", "origin", RAMO)


def commit_wip(itens, msg):
    """Commit no ramo wip/auto sem trocar de branch nem tocar a árvore/índice reais."""
    with tempfile.TemporaryDirectory() as d:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(d) / "idx")}
        pai = git("rev-parse", "--verify", "-q", f"refs/heads/{WIP}").stdout.strip() or git("rev-parse", "HEAD").stdout.strip()
        git("read-tree", pai, env=env, check=True)
        for st, c in itens:
            git("add", "-A", "--", c, env=env, check=True)
        arvore = git("write-tree", env=env, check=True).stdout.strip()
        novo = git("commit-tree", arvore, "-p", pai, "-m", msg, check=True).stdout.strip()
    git("update-ref", f"refs/heads/{WIP}", novo, check=True)
    return git("push", "origin", f"{WIP}:{WIP}")


def main():
    if os.environ.get("CLAUDE_CODE_REMOTE"):
        return "nuvem: hook desligado"
    try:
        if json.load(sys.stdin).get("stop_hook_active"):
            return "stop_hook_active"
    except Exception:
        pass
    if git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip() != RAMO:
        return f"fora de {RAMO}: nada feito"
    itens = alterados()
    if not itens:
        return "árvore limpa"
    achados = varrer_segredo(itens)
    if achados:
        return "BLOQUEADO por varredura de segredo/dado pessoal:\n  " + "\n  " .join(achados)
    cmd, motivo = testes_dos_modulos(itens)
    if cmd is None:
        destino, info = "wip", f"sem teste verificável ({motivo})"
    elif cmd:
        ok, saida = rodar_testes(cmd)
        destino, info = ("master", "testes verdes") if ok else ("wip", "testes VERMELHOS:\n" + saida)
    else:
        destino, info = "master", "sem código alterado"
    if DRY:
        return f"[dry] destino={destino}; {info}; {len(itens)} arquivo(s)"
    if destino == "master":
        r = commit_master(itens, msg_commit(itens))
    else:
        r = commit_wip(itens, msg_commit(itens, " [wip]"))
    return f"{destino}: {info}; push {'ok' if r.returncode == 0 else 'FALHOU: ' + r.stderr.strip()[:200]}"


if __name__ == "__main__":
    try:
        out = main()
    except Exception as e:  # nunca travar o fim da sessão
        out = f"auto_commit falhou: {e}"
    print(json.dumps({"systemMessage": f"[auto-commit] {out}"}))
    sys.exit(0)
