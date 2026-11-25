"""Trava 4.2 (pacote de autonomia, 25/11/2026): hook PreToolUse que protege a configuração de qualidade e as travas.

Bloqueia (exit 2, motivo no stderr) Edit/Write/MultiEdit/NotebookEdit que:
- mexa em config de teste/qualidade EXISTENTE: `pytest.ini`, `conftest.py`, `ruff.toml`/`.ruff.toml`, `mypy.ini`,
  `setup.cfg`, seções `[tool.pytest*]`/`[tool.ruff*]`/`[tool.mypy*]` de `pyproject.toml`;
- mexa nas travas: `.githooks/**`, `.claude/hooks/**`, `.claude/settings.json`, testes-canário das travas;
- edite o golden à mão (`tests/golden.json`, `tests/golden_log.md`) ou as tolerâncias `TOL`/`EXATOS` do `golden.py`;
- suba uma catraca (`*catraca*.json`: número só cai, lista só encolhe) ou baixe o piso (`.githooks/piso_testes.json`);
- sobrescreva arquivo EXISTENTE em `_historico/` (histórico é só acréscimo; arquivo novo lá é livre).
Arquivo novo fora disso é livre. Liberação: só o Frank, abrindo a sessão com `MESA_LIBERA_CONFIG=1`.
A edição por Bash não passa por aqui: o `tests/test_travas.py` fixa o conteúdo dos protegidos por hash.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

RAIZ = Path(os.environ.get("CLAUDE_PROJECT_DIR") or Path(__file__).resolve().parents[2]).resolve()

CONFIG_NOMES = {"pytest.ini", "conftest.py", "ruff.toml", ".ruff.toml", "mypy.ini", "setup.cfg"}
TRAVAS_PREFIXOS = (".githooks/", ".claude/hooks/")
TRAVAS_ARQUIVOS = {
    ".claude/settings.json",
    "ferramentas/tests/test_travas.py", "ferramentas/tests/travas_hashes.json",
    "ferramentas/tests/test_b37_trava_master.py", "ferramentas/tests/test_motor_puro.py",
    "ferramentas/tests/test_docs_caminhos.py", "ferramentas/suite_marcador.py",
}
GOLDEN_DADOS = {"ferramentas/tests/golden.json", "ferramentas/tests/golden_log.md"}
PISO = ".githooks/piso_testes.json"
SECAO_PYPROJECT = re.compile(r"^\s*\[tool\.(pytest|ruff|mypy)", re.M)
LINHA_TOL = re.compile(r"^(TOL|EXATOS)\s*=", re.M)


def relativo(caminho: str) -> str | None:
    try:
        return Path(caminho).resolve().relative_to(RAIZ).as_posix()
    except (ValueError, OSError):
        return None


def novo_conteudo(ferramenta: str, entrada: dict, atual: str) -> str | None:
    """Conteúdo que o arquivo terá depois da ferramenta (None = não dá para saber)."""
    if ferramenta == "Write":
        return entrada.get("content", "")
    edicoes = entrada.get("edits") if ferramenta == "MultiEdit" else [entrada] if ferramenta == "Edit" else None
    if edicoes is None:
        return None
    txt = atual
    for e in edicoes:
        velho, novo = e.get("old_string", ""), e.get("new_string", "")
        if not velho or velho not in txt:
            return None                                          # não dá para reproduzir: os sensíveis bloqueiam
        txt = txt.replace(velho, novo) if e.get("replace_all") else txt.replace(velho, novo, 1)
    return txt


def _folhas(x, prefixo=""):
    if isinstance(x, dict):
        for k, v in x.items():
            yield from _folhas(v, f"{prefixo}/{k}")
    else:
        yield prefixo, x


def catraca_subiu(velho: str, novo: str) -> str | None:
    """Número só cai, lista só encolhe; chave nova ou JSON inválido = subiu."""
    try:
        a, b = dict(_folhas(json.loads(velho))), dict(_folhas(json.loads(novo)))
    except ValueError:
        return "JSON inválido"
    for k, v in b.items():
        if isinstance(v, bool) or not isinstance(v, (int, float, list)):
            if k in a and a[k] != v and not k.endswith(("_nota", "/_nota")):
                return f"{k} mudou"
            continue
        if k not in a:
            return f"{k} é nova"
        if isinstance(v, list):
            if not set(map(str, v)) <= set(map(str, a[k] or [])):
                return f"{k} ganhou itens"
        elif not isinstance(a[k], (int, float)) or v > a[k]:
            return f"{k} subiu de {a[k]} para {v}"
    return None


def motivo_bloqueio(ferramenta: str, entrada: dict) -> str | None:
    caminho = entrada.get("file_path") or entrada.get("notebook_path") or ""
    rel = relativo(caminho) if caminho else None
    if rel is None:
        return None
    arq = RAIZ / rel
    existe = arq.is_file()
    atual = arq.read_text(encoding="utf-8", errors="replace") if existe else ""
    nome = Path(rel).name

    if rel.startswith("_historico/") and existe:
        return "arquivo existente em _historico/ (histórico é só acréscimo; grave uma pasta nova)"
    if not existe:
        return None                                              # arquivo novo é livre
    novo = novo_conteudo(ferramenta, entrada, atual)
    if rel == PISO:                                              # antes da regra de .githooks/: subir é livre
        try:
            if novo is None or int(json.loads(novo)["piso"]) < int(json.loads(atual)["piso"]):
                return "o piso de testes só sobe"
        except (ValueError, KeyError, TypeError):
            return "piso_testes.json inválido"
        return None
    if nome in CONFIG_NOMES:
        return f"{nome} é configuração de teste/qualidade"
    if rel.startswith(TRAVAS_PREFIXOS) or rel in TRAVAS_ARQUIVOS:
        return f"{rel} é uma trava do pacote de autonomia"
    if rel in GOLDEN_DADOS:
        return "golden só se regrava por golden.salvar com GOLDEN_REGRAVAR=1 e motivo citando a camada (trava 4.3)"
    if nome == "pyproject.toml":
        if novo is None or SECAO_PYPROJECT.findall(atual) != SECAO_PYPROJECT.findall(novo) or \
                _secoes(atual) != _secoes(novo):
            return "seções [tool.pytest/ruff/mypy] do pyproject.toml são configuração de qualidade"
    if rel == "ferramentas/golden.py":
        if novo is None or _linhas_tol(atual) != _linhas_tol(novo):
            return "TOL/EXATOS do golden.py são as tolerâncias do golden"
    if "catraca" in nome and nome.endswith(".json"):
        subiu = catraca_subiu(atual, novo) if novo is not None else "edição ilegível"
        if subiu:
            return f"catraca só cai ({subiu})"
    return None


def _secoes(txt: str) -> list[str]:
    """Texto das seções [tool.pytest/ruff/mypy] (do cabeçalho até a próxima seção)."""
    blocos, atual = [], None
    for linha in txt.splitlines():
        if linha.strip().startswith("["):
            atual = linha.strip() if SECAO_PYPROJECT.match(linha) else None
            if atual:
                blocos.append([atual])
            continue
        if atual:
            blocos[-1].append(linha.rstrip())
    return ["\n".join(b) for b in blocos]


def _linhas_tol(txt: str) -> list[str]:
    """As atribuições TOL/EXATOS inteiras (até a linha que fecha o literal)."""
    saida, dentro, prof = [], False, 0
    for linha in txt.splitlines():
        if not dentro and LINHA_TOL.match(linha):
            dentro, prof = True, 0
        if dentro:
            saida.append(linha.rstrip())
            prof += linha.count("{") + linha.count("(") + linha.count("[")
            prof -= linha.count("}") + linha.count(")") + linha.count("]")
            if prof <= 0:
                dentro = False
    return saida


def main() -> int:
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")   # Windows: sem isto sai cp1252
    except AttributeError:
        pass
    if os.environ.get("MESA_LIBERA_CONFIG") == "1":
        return 0
    try:
        dados = json.loads(sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
    except ValueError:
        return 0
    motivo = motivo_bloqueio(dados.get("tool_name", ""), dados.get("tool_input") or {})
    if motivo:
        print(f"TRAVA 4.2 (pacote de autonomia): edição bloqueada — {motivo}. Liberar é decisão do Frank "
              "(CLAUDE.md, \"Quem decide\"): registre em docs/PENDENTE-FRANK.md com recomendação.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
