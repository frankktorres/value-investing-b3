"""Trava 4.6 (pacote de autonomia, 25/11/2026): documento vigente citando arquivo que não existe reprova.

Escopo: os documentos que descrevem o PRESENTE e que a sessão segue (CLAUDE.md, README, DNA, doutrina, brief,
validação, oráculo, agentes/skills/comandos do `.claude/`). Diários, BACKLOG, MISSOES e pré-registros ficam fora: citam
o passado ou o que ainda vai existir.
Caminho citado = trecho entre crases com `/` ou extensão conhecida, sem espaço nem coringa/placeholder. Existe = está
no git (arquivo ou pasta, a partir da raiz, de `ferramentas/` ou da pasta do .md; nome solto vale em qualquer pasta) ou é
ignorado pelo `.gitignore` (mora fora do git; não dá para conferir na nuvem). Não olha o disco: o resultado é o mesmo
na máquina do Frank e na nuvem.
As quebras de hoje ficam em `docs_caminhos_catraca.json` (lista que só encolhe). Canário: citação inventada reprova.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess

import pytest

RAIZ = pathlib.Path(__file__).resolve().parents[2]
CATRACA = pathlib.Path(__file__).with_name("docs_caminhos_catraca.json")
VIGENTES = ["CLAUDE.md", "README.md", "PROJECT_BRIEF.md", "01-doutrina-value-investing.md", "docs/00-DNA.md",
            "docs/VALIDACAO.md", "docs/ORACULO.md"]
VIGENTES_GLOB = [".claude/agents/*.md", ".claude/skills/*/SKILL.md", ".claude/commands/*.md"]
EXT = (".py", ".md", ".json", ".jsonl", ".txt", ".cmd", ".vbs", ".ps1", ".sh", ".ini", ".toml", ".csv", ".html",
       ".js", ".css", ".yml", ".yaml", ".pdf", ".parquet", ".zip", ".lock", ".cfg")
CRASE = re.compile(r"`([^`\n]+)`")
PLACEHOLDER = re.compile(r"[<>*{}$%|=(),;\[\]\\'\"]|AAAA|\bXX\b|\.\.\.|…|^-|://|^~|^[A-Za-z]:|^/|^\.\w+$"
                         r"|^(wip|claude|origin|refs)/")             # comando /x, extensão solta, nome de ramo


def candidatos(texto: str) -> list[str]:
    saida = []
    for bruto in CRASE.findall(texto):
        c = re.sub(r":\d+(-\d+)?$", "", bruto.strip())          # arquivo.py:207 -> arquivo.py
        c = re.sub(r"#.*$", "", c)                             # âncora de seção
        if not c or " " in c or PLACEHOLDER.search(c):
            continue
        if "/" in c or c.lower().endswith(EXT):
            saida.append(c.rstrip("/") if c.endswith("/") and len(c) > 1 else c)
    return saida


class Indice:
    def __init__(self, raiz: pathlib.Path):
        self.raiz = raiz
        # rastreados + novos não ignorados: a suíte roda antes do commit (é a árvore que o commit vai ter)
        arquivos = subprocess.run(["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"], cwd=raiz, capture_output=True, text=True,
                                  encoding="utf-8").stdout.split("\0")
        self.arquivos = {a for a in arquivos if a}
        self.pastas = {str(pathlib.PurePosixPath(a).parents[i]) for a in self.arquivos
                       for i in range(len(pathlib.PurePosixPath(a).parents) - 1)}
        self.nomes = {pathlib.PurePosixPath(a).name for a in self.arquivos}

    def _ignorado(self, rel: str) -> bool:
        r = subprocess.run(["git", "check-ignore", "-q", "--no-index", rel], cwd=self.raiz, capture_output=True)
        return r.returncode == 0

    def existe(self, cand: str, pasta_md: str) -> bool:
        if "/" not in cand and cand in self.nomes:
            return True
        bases = ["", "ferramentas/"] + ([pasta_md + "/"] if pasta_md not in ("", ".") else [])
        for base in bases:
            rel = str(pathlib.PurePosixPath(base + cand))
            if rel in self.arquivos or rel in self.pastas:
                return True
        if "/" in cand and any(a.endswith("/" + cand) for a in self.arquivos | self.pastas):
            return True                                         # relativo a uma subpasta (web/dados/x.json)
        return any(self._ignorado(str(pathlib.PurePosixPath(b + cand))) for b in bases)


def documentos() -> list[pathlib.Path]:
    docs = [RAIZ / d for d in VIGENTES if (RAIZ / d).is_file()]
    for g in VIGENTES_GLOB:
        docs += sorted(RAIZ.glob(g))
    return docs


def quebrados(indice: Indice) -> dict[str, list[str]]:
    saida = {}
    for doc in documentos():
        rel = doc.relative_to(RAIZ).as_posix()
        pasta = str(pathlib.PurePosixPath(rel).parent)
        q = sorted({c for c in candidatos(doc.read_text(encoding="utf-8", errors="replace"))
                    if not indice.existe(c, pasta)})
        if q:
            saida[rel] = q
    return saida


@pytest.fixture(scope="module")
def indice():
    return Indice(RAIZ)


def test_canario_citacao_inventada_reprova(indice):
    texto = "Veja `ferramentas/nao_existe_b37.py` e `docs/00-DNA.md` e `golden.py` e `ferramentas/dados/cvm/x.zip`."
    assert [c for c in candidatos(texto) if not indice.existe(c, "docs")] == ["ferramentas/nao_existe_b37.py"]


def test_canario_placeholder_nao_conta():
    assert candidatos("`docs/oraculo/AAAA-MM-DD.md` `relatorio <TK>` `*.md` `python -m pytest` `C:\\x\\y.py`") == []


def test_documentos_vigentes_sem_caminho_quebrado_novo(indice):
    catraca = json.loads(CATRACA.read_text(encoding="utf-8"))["por_arquivo"]
    atual = quebrados(indice)
    novos = {d: [c for c in q if c not in catraca.get(d, [])] for d, q in atual.items()}
    novos = {d: q for d, q in novos.items() if q}
    sumiram = {d: [c for c in q if c not in atual.get(d, [])] for d, q in catraca.items()}
    sumiram = {d: q for d, q in sumiram.items() if q}
    assert not novos, "documento vigente cita arquivo que não existe (corrija o caminho):\n" + json.dumps(
        novos, ensure_ascii=False, indent=1)
    assert not sumiram, "quebra consertada: tire da catraca tests/docs_caminhos_catraca.json:\n" + json.dumps(
        sumiram, ensure_ascii=False, indent=1)
