"""Trava 4.2 (pacote de autonomia, 25/11/2026): hook PreToolUse que protege a configuração de qualidade e as travas.

Bloqueia (exit 2, motivo no stderr) Edit/Write/MultiEdit/NotebookEdit que:
- crie ou mexa em config de teste/qualidade: `pytest.ini`, `conftest.py`, `pyproject.toml`, `setup.cfg`, `tox.ini`,
  `ruff.toml`/`.ruff.toml`, `mypy.ini` (NOVO também: um conftest novo com `collect_ignore` desligaria testes);
- crie ou mexa nas travas: `.githooks/**`, `.claude/hooks/**`, `.claude/settings*.json` (um `settings.local.json` novo
  com `disableAllHooks` desligaria tudo), os testes-canário, `suite_marcador.py`, o `golden.py` inteiro (o TOL vale onde
  é usado, não só onde é definido);
- edite o golden à mão (`tests/golden.json`, `tests/golden_log.md`);
- suba uma catraca (`*catraca*.json`: número só cai, lista só encolhe) ou baixe o piso (`.githooks/piso_testes.json`);
- sobrescreva arquivo EXISTENTE em `_historico/` (histórico é só acréscimo; arquivo novo lá é livre).
Outro arquivo novo é livre. Worktree dentro do repo (`.claude/worktrees/<x>/`) segue as mesmas regras.
Liberação: só o Frank, abrindo a sessão com `MESA_LIBERA_CONFIG=1`. Bash não passa por aqui: `tests/test_travas.py`
fixa o conteúdo dos protegidos por hash e o settings.json nega Bash com `MESA_LIBERA_CONFIG`/`GOLDEN_REGRAVAR`.
"""
from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path

# A raiz é a do próprio arquivo (não CLAUDE_PROJECT_DIR: a sessão aberta em ferramentas/ deslocaria tudo)
RAIZ = Path(__file__).resolve().parents[2]

CONFIG_NOMES = {"pytest.ini", "conftest.py", "pyproject.toml", "setup.cfg", "tox.ini", "ruff.toml", ".ruff.toml",
                "mypy.ini", ".mypy.ini"}
TRAVAS_PREFIXOS = (".githooks/", ".claude/hooks/")
TRAVAS_ARQUIVOS = {
    "ferramentas/golden.py", "ferramentas/suite_marcador.py",
    "ferramentas/tests/test_travas.py", "ferramentas/tests/travas_hashes.json",
    "ferramentas/tests/test_b37_trava_master.py", "ferramentas/tests/test_motor_puro.py",
    "ferramentas/tests/test_docs_caminhos.py",
}
GOLDEN_DADOS = {"ferramentas/tests/golden.json", "ferramentas/tests/golden_log.md"}
PISO = ".githooks/piso_testes.json"


def relativo(caminho: str) -> str | None:
    try:
        rel = Path(caminho).resolve().relative_to(RAIZ.resolve()).as_posix()
    except (ValueError, OSError):
        return None
    partes = rel.split("/")
    if len(partes) > 3 and partes[0] == ".claude" and partes[1] == "worktrees":
        rel = "/".join(partes[3:])                              # worktree de subagente: mesmas regras
    return rel


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
    """Número só cai, lista só encolhe; chave nova, NaN/inf ou JSON inválido = subiu."""
    try:
        a, b = dict(_folhas(json.loads(velho))), dict(_folhas(json.loads(novo)))
    except ValueError:
        return "JSON inválido"
    for k, v in b.items():
        if isinstance(v, bool) or not isinstance(v, (int, float, list)):
            if k in a and a[k] != v and not k.endswith("_nota"):
                return f"{k} mudou"
            continue
        if k not in a:
            return f"{k} é nova"
        if isinstance(v, list):
            if not set(map(str, v)) <= set(map(str, a[k] or [])):
                return f"{k} ganhou itens"
        elif not math.isfinite(v) or not isinstance(a[k], (int, float)) or v > a[k]:
            return f"{k} subiu de {a[k]} para {v}"
    return None


def motivo_bloqueio(ferramenta: str, entrada: dict) -> str | None:
    caminho = entrada.get("file_path") or entrada.get("notebook_path") or ""
    rel = relativo(caminho) if caminho else None
    if rel is None:
        return None
    arq = Path(caminho).resolve()                                # o arquivo de verdade (inclusive na worktree)
    existe = arq.is_file()
    atual = arq.read_text(encoding="utf-8", errors="replace") if existe else ""
    nome = Path(rel).name

    if rel.startswith("_historico/"):
        return "arquivo existente em _historico/ (histórico é só acréscimo; grave uma pasta nova)" if existe else None
    if nome in CONFIG_NOMES:
        return f"{nome} é configuração de teste/qualidade (novo ou existente)"
    if rel.startswith(".claude/settings") and nome.endswith(".json"):
        return f"{rel} é configuração do Claude Code (hooks e permissões das travas)"
    novo = novo_conteudo(ferramenta, entrada, atual) if existe else None
    if rel == PISO and existe:                                   # antes da regra de .githooks/: subir é livre
        try:
            if novo is None or int(json.loads(novo)["piso"]) < int(json.loads(atual)["piso"]):
                return "o piso de testes só sobe"
        except (ValueError, KeyError, TypeError):
            return "piso_testes.json inválido"
        return None
    if rel.startswith(TRAVAS_PREFIXOS) or rel in TRAVAS_ARQUIVOS:
        return f"{rel} é uma trava do pacote de autonomia"
    if not existe:
        return None                                              # outro arquivo novo é livre
    if rel in GOLDEN_DADOS:
        return "golden só se regrava por golden.salvar com GOLDEN_REGRAVAR=1 e motivo citando a camada (trava 4.3)"
    if "catraca" in nome and nome.endswith(".json"):
        subiu = catraca_subiu(atual, novo) if novo is not None else "edição ilegível"
        if subiu:
            return f"catraca só cai ({subiu})"
    return None


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
