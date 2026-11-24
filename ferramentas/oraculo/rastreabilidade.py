"""Matriz de rastreabilidade § da doutrina → função → teste → camada (docs/VALIDACAO.md §3).

A fonte da verdade é `oraculo/matriz.py`; este módulo confere a matriz contra o repositório e gera `docs/RASTREABILIDADE.md`.
    python -m oraculo.rastreabilidade              # regrava o .md
    python -m oraculo.rastreabilidade --verificar  # só confere; código ≠ 0 se houver problema ou o .md estiver velho
"""
from __future__ import annotations

import ast
import importlib
import pathlib
import re
import sys

AQUI = pathlib.Path(__file__).resolve().parent
FERRAMENTAS = AQUI.parent
RAIZ = FERRAMENTAS.parent
DOUTRINA = RAIZ / "01-doutrina-value-investing.md"
SAIDA = RAIZ / "docs" / "RASTREABILIDADE.md"
TIPOS = ("calculo", "veto", "dado", "texto")
CAMADAS = (0, 1, 2, 3, 4, 5, 6, 7)


def secoes_da_doutrina(caminho: pathlib.Path = DOUTRINA) -> list[str]:
    """§ de cada cabeçalho numerado do 01 ("## 4. …" → "§4", "### 4.1 …" → "§4.1"); o histórico de versões não é regra."""
    secs = []
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^#{2,3}\s+(\d+(?:\.\d+)?)\.?\s", linha)
        if m:
            secs.append("§" + m.group(1))
    return secs


def _testes_do_arquivo(arq: pathlib.Path) -> set[str]:
    """Nomes `test_x` e `Classe::test_x` definidos no arquivo (sem importar: a coleta não pode depender de dado)."""
    arvore = ast.parse(arq.read_text(encoding="utf-8"))
    nomes = set()
    for no in arvore.body:
        if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef)) and no.name.startswith("test"):
            nomes.add(no.name)
        elif isinstance(no, ast.ClassDef):
            for f in no.body:
                if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)) and f.name.startswith("test"):
                    nomes.add(f"{no.name}::{f.name}")
    return nomes


def _funcao_existe(nome: str) -> bool:
    mod, _, attr = nome.rpartition(".")
    if not mod:
        return False
    if str(FERRAMENTAS) not in sys.path:
        sys.path.insert(0, str(FERRAMENTAS))
    try:
        m = importlib.import_module(mod)
    except Exception:
        return False
    return hasattr(m, attr)


def verificar(regras: list[dict], lacunas_max: int, secoes: list[str] | None = None) -> list[str]:
    """Problemas da matriz; lista vazia = verde. Cada regra calculável precisa de teste ou de lacuna declarada com a fase."""
    secoes = secoes_da_doutrina() if secoes is None else secoes
    probs = []
    ids = [r["id"] for r in regras]
    for i in sorted({x for x in ids if ids.count(x) > 1}):
        probs.append(f"id repetido: {i}")
    cobertas = {r["sec"] for r in regras}
    for s in secoes:
        if s not in cobertas:
            probs.append(f"{s}: seção do 01 sem nenhuma linha na matriz")
    for s in sorted(cobertas - set(secoes)):
        probs.append(f"{s}: a matriz cita uma seção que o 01 não tem")
    cache: dict[str, set[str]] = {}
    for r in regras:
        rid = r["id"]
        if r.get("tipo") not in TIPOS:
            probs.append(f"{rid}: tipo inválido {r.get('tipo')!r}")
        if r.get("camada") not in CAMADAS:
            probs.append(f"{rid}: camada inválida {r.get('camada')!r}")
        for f in r.get("funcoes", []):
            if not _funcao_existe(f):
                probs.append(f"{rid}: função inexistente {f}")
        for t in r.get("testes", []):
            arq, _, nome = t.partition("::")
            caminho = FERRAMENTAS / arq
            if not caminho.is_file():
                probs.append(f"{rid}: arquivo de teste inexistente {arq}")
                continue
            if arq not in cache:
                cache[arq] = _testes_do_arquivo(caminho)
            if nome not in cache[arq]:
                probs.append(f"{rid}: teste inexistente {t}")
        if r.get("tipo") != "texto" and not r.get("testes") and not r.get("lacuna"):
            probs.append(f"{rid}: regra sem teste e sem lacuna declarada ({r.get('regra', '')[:60]})")
        if r.get("lacuna") and not re.search(r"Fase \d", r["lacuna"]):
            probs.append(f"{rid}: lacuna sem a fase que a fecha")
    n_lac = sum(1 for r in regras if r.get("lacuna"))
    if n_lac != lacunas_max:
        probs.append(f"catraca: {n_lac} lacunas declaradas, teto {lacunas_max} "
                     f"({'subiu — feche a lacuna ou justifique' if n_lac > lacunas_max else 'caiu — baixe LACUNAS_MAX no mesmo commit'})")
    return probs


def gerar_md(regras: list[dict]) -> str:
    calc = [r for r in regras if r["tipo"] != "texto"]
    com_teste = [r for r in calc if r.get("testes")]
    por_camada = {c: sum(1 for r in com_teste if r["camada"] == c) for c in CAMADAS}
    linhas = [
        "# Rastreabilidade — doutrina → função → teste → camada",
        "",
        "Gerado por `cd ferramentas && python -m oraculo.rastreabilidade` a partir de `ferramentas/oraculo/matriz.py`. Não edite à mão.",
        "Contrato: `docs/VALIDACAO.md` §3. Camadas: 0 = só regressão/golden · 1 = especificado · 2 = propriedade · 3 = diferencial ·",
        "4 = reconciliação · 5 = sanidade · 6 = resultado · 7 = desafio.",
        "",
        f"**{len(regras)} regras** ({len(calc)} calculáveis, {len(regras) - len(calc)} de texto) · "
        f"**{len(com_teste)} com teste** · **{sum(1 for r in regras if r.get('lacuna'))} lacunas declaradas** · "
        "por camada do teste mais forte: " + ", ".join(f"{c}: {n}" for c, n in por_camada.items() if n),
        "",
        "| id | § | linha | regra | tipo | funções | testes | camada | lacuna | nota |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in regras:
        def esc(s):
            return str(s).replace("|", "\\|")
        linhas.append("| " + " | ".join([
            r["id"], r["sec"], str(r.get("linha", "")), esc(r.get("regra", "")), r["tipo"],
            "<br>".join(f"`{f}`" for f in r.get("funcoes", [])) or "—",
            "<br>".join(f"`{t}`" for t in r.get("testes", [])) or "—",
            str(r["camada"]) if r.get("testes") else "—",
            esc(r.get("lacuna", "")) or "—",
            esc(r.get("nota", "")) or "—",
        ]) + " |")
    return "\n".join(linhas) + "\n"


def main(argv: list[str] | None = None) -> int:
    from oraculo.matriz import LACUNAS_MAX, REGRAS
    argv = sys.argv[1:] if argv is None else argv
    probs = verificar(REGRAS, LACUNAS_MAX)
    for p in probs:
        print("PROBLEMA:", p)
    md = gerar_md(REGRAS)
    if "--verificar" in argv:
        atual = SAIDA.read_text(encoding="utf-8").splitlines() if SAIDA.is_file() else []
        if atual != md.splitlines():
            print("PROBLEMA: docs/RASTREABILIDADE.md desatualizado; rode `python -m oraculo.rastreabilidade`")
            return 1
    else:
        SAIDA.write_text(md, encoding="utf-8", newline="\n")
        print(f"gravado {SAIDA.relative_to(RAIZ)} ({len(REGRAS)} regras)")
    return 1 if probs else 0


if __name__ == "__main__":
    raise SystemExit(main())
