"""Hook Stop: só snapshot em wip/auto. NUNCA commita nem empurra o master.

Decisão do Frank de 24/11/2026 (igual à F49 do UNION, de 25/10): até aqui o hook commitava e empurrava no `master` a
cada fim de turno (ex.: b33c14e), com só os testes do módulo — ou sem teste nenhum quando só mudava documento. O
`master` agora só recebe o commit explícito da sessão (suíte verde; motor/doutrina/golden com registro no 09).

- Na nuvem (CLAUDE_CODE_REMOTE) não faz nada: lá o Claude commita no ramo claude/* (ver CLAUDE.md).
- Varre segredo/dado pessoal nos arquivos alterados; se achar, não guarda nem envia nada.
- Árvore suja -> commit em wip/auto por plumbing (HEAD, índice e árvore de trabalho não mudam) + push só de wip/auto.
- Árvore limpa com commit local sem push -> só avisa.
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
DRY = "--dry" in sys.argv
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
    """Caminhos alterados/novos (não ignorados) e removidos. A origem de uma renomeação entra como removida."""
    r = git("status", "--porcelain=v1", "-z", "--untracked-files=all")
    itens, partes = [], r.stdout.split("\0")
    i = 0
    while i < len(partes):
        p = partes[i]
        i += 1
        if len(p) < 4:
            continue
        st, caminho = p[:2], p[3:]
        itens.append((st, caminho))
        if st[0] in "RC":
            if st[0] == "R" and i < len(partes) and partes[i]:
                itens.append(("D ", partes[i]))  # sem isto o arquivo antigo ficaria no snapshot
            i += 1  # pula o caminho de origem
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


def msg_commit(itens):
    n = len(itens)
    nomes = ", ".join(Path(c).name for _, c in itens[:3]) + ("…" if n > 3 else "")
    return f"auto: snapshot de {n} arquivo(s) — {nomes} [wip]\n\nCo-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>"


def commit_wip(itens, msg):
    """Snapshot (HEAD + alterações) em wip/auto sem trocar de branch nem tocar HEAD, índice ou árvore de trabalho.
    Só a ref wip/auto é escrita e só ela é empurrada."""
    head = git("rev-parse", "HEAD", check=True).stdout.strip()
    with tempfile.TemporaryDirectory() as d:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(d) / "idx")}
        git("read-tree", head, env=env, check=True)
        for st, c in itens:  # sempre caminho a caminho, nunca "add ."
            git("add", "-A", "--", c, env=env, check="D" not in st)  # removido que nem estava no HEAD: nada a fazer
        arvore = git("write-tree", env=env, check=True).stdout.strip()
    pai = git("rev-parse", "--verify", "-q", f"refs/heads/{WIP}").stdout.strip() or head
    if git("rev-parse", f"{pai}^{{tree}}").stdout.strip() == arvore:
        return "igual ao último snapshot: nada novo a guardar"
    novo = git("commit-tree", arvore, "-p", pai, "-m", msg, check=True).stdout.strip()
    git("update-ref", f"refs/heads/{WIP}", novo, check=True)
    r = git("push", "origin", f"{WIP}:{WIP}")
    return f"push {'ok' if r.returncode == 0 else 'FALHOU: ' + r.stderr.strip()[:200]}"


def main():
    if os.environ.get("CLAUDE_CODE_REMOTE"):
        return "nuvem: hook desligado"
    if not DRY and not sys.stdin.isatty():
        try:
            if json.load(sys.stdin).get("stop_hook_active"):
                return "stop_hook_active"
        except Exception:
            pass
    itens = alterados()
    if not itens:
        n = git("rev-list", "--count", "@{u}..HEAD").stdout.strip()
        return "árvore limpa" + (f"; ATENÇÃO: {n} commit(s) local(is) sem push" if n not in ("", "0") else "")
    achados = varrer_segredo(itens)
    if achados:
        return "BLOQUEADO por varredura de segredo/dado pessoal (nada guardado nem enviado):\n  " + "\n  ".join(achados)
    if f"branch refs/heads/{WIP}" in git("worktree", "list", "--porcelain").stdout.splitlines():
        return f"{WIP} está em uso (checkout aqui ou em outra worktree): snapshot NÃO gravado"
    if DRY:
        return f"[dry] snapshot de {len(itens)} arquivo(s) em {WIP}; master intocado"
    info = commit_wip(itens, msg_commit(itens))
    return f"snapshot de {len(itens)} arquivo(s) em {WIP}; {info}; master intocado (o commit no master é explícito)"


if __name__ == "__main__":
    try:
        out = main()
    except Exception as e:  # nunca travar o fim da sessão
        out = f"auto_commit falhou: {e}"
    print(json.dumps({"systemMessage": f"[auto-commit] {out}"}))
    sys.exit(0)
