"""B37 (25/11/2026): push no `master` só com a suíte INTEIRA verde registrada para a árvore empurrada.

Como decide (para cada ref empurrada para `refs/heads/master`; outras refs passam):
- apagar o `master` -> recusa;
- a árvore do commit empurrado precisa estar no registro verde (`ferramentas/suite_marcador.py`, gravado só pelo
  `conftest.py` no fim da suíte inteira com 0 falha/erro/pulado) -> senão recusa;
- o registro precisa ter nº de aprovados ≥ piso (`.githooks/piso_testes.json`; vale o MAIOR entre o piso da árvore de
  trabalho e o do commit empurrado: baixar o piso exige mexer nos dois) -> senão recusa.
Sem isenção para `.md`: testes leem documentos (datas fixas, caminhos citados).
Ligada por `git config core.hooksPath .githooks` (config local; a nuvem não usa e grava em `claude/*`).
Sem dependência fora da stdlib.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI.parent / "ferramentas"))
import suite_marcador  # noqa: E402

ZERO = "0" * 40
ALVO = "refs/heads/master"
PISO_ARQ = ".githooks/piso_testes.json"


def _piso_de(texto: str | None) -> int:
    try:
        return int(json.loads(texto)["piso"])
    except (TypeError, ValueError, KeyError):
        return 0


def piso(local_sha: str, cwd: str | None = None) -> int:
    raiz = suite_marcador.raiz(cwd)
    try:
        do_arquivo = (raiz / PISO_ARQ).read_text(encoding="utf-8")
    except OSError:
        do_arquivo = None
    r = subprocess.run(["git", "show", f"{local_sha}:{PISO_ARQ}"], cwd=raiz, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    do_commit = r.stdout if r.returncode == 0 else None
    p = max(_piso_de(do_arquivo), _piso_de(do_commit))
    if p <= 0:
        raise RuntimeError(f"piso ausente ou inválido em {PISO_ARQ}")
    return p


def decidir(local_sha: str, verdes: list[dict], piso_min: int, cwd: str | None = None) -> tuple[bool, str]:
    if local_sha == ZERO:
        return False, "apagar o master"
    arvore = suite_marcador._git("rev-parse", f"{local_sha}^{{tree}}", cwd=cwd)
    reg = next((r for r in reversed(verdes) if r.get("arvore") == arvore), None)
    if reg is None:
        return False, f"a árvore {arvore[:10]} não tem suíte inteira verde registrada (rode a suíte DEPOIS da última mudança)"
    try:
        aprovados = int(reg.get("aprovados", 0))
    except (TypeError, ValueError):
        aprovados = 0
    if aprovados < piso_min:
        return False, f"registro com {aprovados} aprovados, abaixo do piso de {piso_min} (teste apagado ou registro forjado)"
    dica = f"; piso pode subir para {aprovados} ({PISO_ARQ})" if aprovados > piso_min else ""
    return True, f"suíte verde ({aprovados} aprovados) na árvore {arvore[:10]}{dica}"


def main() -> int:
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")   # Windows: sem isto sai cp1252 e o git mostra lixo
    except AttributeError:
        pass
    recusas, avisos = [], []
    verdes = suite_marcador.ler()
    for linha in sys.stdin.read().splitlines():
        partes = linha.split()
        if len(partes) != 4 or partes[2] != ALVO:
            continue
        try:
            passa, motivo = decidir(partes[1], verdes, piso(partes[1]))
        except RuntimeError as e:
            passa, motivo = False, str(e)
        (avisos if passa else recusas).append(f"{partes[1][:8]} -> master: {motivo}")
    for a in avisos:
        print(f"trava B37: {a}", file=sys.stderr)
    if recusas:
        print("TRAVA B37: push no master RECUSADO. Rode a suíte inteira na árvore exata do commit "
              "(`cd ferramentas && python -m pytest --ignore=backtest -q`, árvore limpa ou só com o que vai no commit) "
              "e empurre de novo:\n  " + "\n  ".join(recusas), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
