"""Ordem pré-registro → motor, conferida pelo git (pré-registro v3, emenda 7; decisão do Frank de 24/11/2026).

Origem: a emenda 3 (H2) entrou no MESMO commit que o motor e o golden (c108bce), e o agente `oraculo` não tinha como provar que
a regra foi escrita antes do resultado. Daqui em diante (commits depois de CORTE):
  · commit (merge incluído, pelo que o merge muda por conta própria) que mexe em `docs/PRE-REGISTRO-*.md` não mexe em mais nada;
  · QUALQUER outro commit que cita "emenda N" na mensagem só passa se um commit ANTERIOR, só de pré-registro, acrescentou a
    emenda N ao §7 (as que já existiam no CORTE valem) — vale para todo arquivo, não só motor: crédito, inflação, LTM, dossiê,
    lotes novos também mudam palavra;
  · na árvore não commitada (staged, unstaged, renomeado ou novo), pré-registro mudado junto com qualquer outro arquivo reprova.
Adversário de 24/11 (7 escapes da 1ª versão): faixa "emendas 2–3", "nº 9", data na mensagem lida como emenda, emenda fora do §7,
renomeação/arquivo novo na árvore, merge, caminho com espaço.
"""
from __future__ import annotations

import pathlib
import re
import subprocess

CORTE = "b07482a"          # último commit antes da emenda 7 (24/11/2026)
# Exceção pontual, decisão do Frank (docs/PENDENTE-FRANK.md #13, opção A, 25/11/2026): a emenda 13 (B57) foi commitada junto
# com a ficha de fontes dela (sem código), antes do motor. Vale só para ESTE SHA completo com ESTE conjunto exato de arquivos
# extras; com isso o commit conta como só de pré-registro e a emenda 13 fica registrada. Qualquer outro caso reprova.
EXCECOES = {"2c7c87aa3ac40b15a4007439443a843c6292092c": frozenset({"docs/b57/FONTES-B57.md"})}
PRE = re.compile(r"^docs/PRE-REGISTRO-[^/]+\.md$")
ITEM = re.compile(r"^(\d+)\.\s", re.M)                       # item de 1º nível da lista do §7 = uma emenda
_N = r"(\d{1,2})(?![\d/])"                                   # 1–2 dígitos, nunca parte de data (24/11, 2026)
CITA = re.compile(rf"emendas?\s*(?:n\.?\s*[º°o]?\s*|#|-)?\s*{_N}((?:\s*(?:,|e|a|até|–|—|-)\s*{_N})*)", re.I)


def _git(raiz: pathlib.Path, *args: str) -> str:
    r = subprocess.run(["git", "-c", "core.quotePath=false", *args], cwd=raiz, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=60)
    if r.returncode:
        raise RuntimeError(f"git {' '.join(args)}: {r.stderr.strip()}")
    return r.stdout


def citadas(mensagem: str) -> set[int]:
    """Números de emenda citados; "2–4" e "2 a 4" são faixas."""
    out = set()
    for m in CITA.finditer(mensagem):
        ant = int(m.group(1))
        out.add(ant)
        for sep, n in re.findall(rf"\s*(,|e|a|até|–|—|-)\s*{_N}", m.group(2), re.I):
            n = int(n)
            out |= set(range(ant, n + 1)) if sep.lower() in ("a", "até", "–", "—", "-") and n >= ant else {n}
            ant = n
    return out


def emendas_do_texto(texto: str) -> set[int]:
    """Emendas = itens de 1º nível da seção "## 7. Emendas" (até a próxima seção ##)."""
    if "## 7. Emendas" not in texto:
        return set()
    secao = re.split(r"^## ", texto.split("## 7. Emendas", 1)[1], maxsplit=1, flags=re.M)[0]
    return {int(n) for n in ITEM.findall(secao)}


def _emendas_no(raiz, commit) -> set[int]:
    nums = set()
    for arq in _git(raiz, "ls-tree", "-z", "--name-only", "-r", commit, "--", "docs/").split("\0"):
        if PRE.match(arq):
            nums |= emendas_do_texto(_git(raiz, "show", f"{commit}:{arq}"))
    return nums


def _arquivos(raiz, c) -> set[str]:
    pais = _git(raiz, "rev-list", "--parents", "-n", "1", c).split()[1:]
    if len(pais) > 1:      # merge: só o que o merge muda por conta própria (resolução/edição), não o que veio dos ramos
        saida = _git(raiz, "diff-tree", "-z", "-r", "--cc", "--no-commit-id", "--name-only", c)
    else:
        saida = _git(raiz, "diff-tree", "-z", "-r", "--no-commit-id", "--name-only", "-M", c)
    return {a for a in saida.split("\0") if a}


def _sujos(raiz) -> set[str]:
    """Todo caminho mudado na árvore: staged, unstaged, novo não rastreado e os dois lados de uma renomeação."""
    campos, out, i = _git(raiz, "status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0"), set(), 0
    while i < len(campos):
        e = campos[i]
        if len(e) > 3:
            out.add(e[3:])
            if e[0] in "RC" or e[1] in "RC":      # no -z, a origem da renomeação vem no campo seguinte
                i += 1
                if i < len(campos) and campos[i]:
                    out.add(campos[i])
        i += 1
    return out


def verificar(raiz: pathlib.Path, corte: str = CORTE, excecoes: dict | None = None) -> dict:
    raiz = pathlib.Path(raiz)
    excecoes = EXCECOES if excecoes is None else excecoes
    _git(raiz, "merge-base", "--is-ancestor", corte, "HEAD")          # corte fora do histórico → erro, nunca "ok"
    registradas = _emendas_no(raiz, corte)
    problemas, n = [], 0
    for c in _git(raiz, "rev-list", "--reverse", "--topo-order", f"{corte}..HEAD").split():
        n += 1
        arqs = _arquivos(raiz, c)
        pre = {a for a in arqs if PRE.match(a)}
        curto = c[:7]
        if pre and arqs - pre and excecoes.get(c) != frozenset(arqs - pre):
            problemas.append(f"{curto} mistura pré-registro com {len(arqs - pre)} outro(s) arquivo(s) "
                             f"({', '.join(sorted(arqs - pre)[:3])}): emenda vai em commit próprio")
        elif pre:
            pai = f"{c}^"
            antes = set().union(*[emendas_do_texto(_git(raiz, "show", f"{pai}:{a}")) for a in pre
                                  if _git(raiz, "ls-tree", "--name-only", pai, "--", a).strip()] or [set()])
            depois = _emendas_no(raiz, c)
            registradas = (registradas - (antes - depois)) | (depois - antes)     # emenda apagada deixa de valer
            continue
        faltam = citadas(_git(raiz, "log", "-1", "--format=%B", c)) - registradas
        if faltam:
            problemas.append(f"{curto} cita emenda {sorted(faltam)} sem commit anterior só de pré-registro que a acrescentou")
    sujos = _sujos(raiz)
    if any(PRE.match(a) for a in sujos) and any(not PRE.match(a) for a in sujos):
        problemas.append("árvore não commitada muda pré-registro E outro arquivo: commite a emenda sozinha antes")
    return dict(status="falha" if problemas else "ok", problemas=problemas, commits=n, corte=corte,
                emendas=sorted(registradas))
