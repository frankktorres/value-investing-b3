"""Guarda o arquivo vigente em `_historico/` antes de sobrescrevê-lo (inviolável 4; AUD-84).

`atualizar_hall_lote*.py`, `hall03 --corrigir`, `triagem/rodar.py` e `gerar_pdf_lote*.py` regravam o arquivo vigente sem
copiar o anterior: o git só protege o que já foi commitado. Agora cada gravação passa por `guardar` (copia só quando o
conteúdo vai mudar) ou `gravar_texto`.

Destino: `_historico/AAAA-MM-DD <rótulo>/<nome>`; segunda cópia do mesmo arquivo no mesmo dia vira `<nome>.2.<ext>` etc.
"""
from __future__ import annotations

import datetime as dt
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent


def _igual(a: bytes, b: bytes) -> bool:
    """Igual ignorando a diferença CRLF/LF (core.autocrlf no Windows): só conteúdo conta."""
    return a.replace(b"\r\n", b"\n") == b.replace(b"\r\n", b"\n")


def guardar(arquivo: Path, rotulo: str, novo: bytes | None = None, raiz: Path = RAIZ,
            hoje: str | None = None) -> Path | None:
    """Copia `arquivo` para `_historico/<hoje> <rotulo>/` se existir e (quando `novo` é dado) se o conteúdo for mudar.

    Devolve o caminho da cópia, ou None se não havia o que guardar."""
    arquivo = Path(arquivo)
    if not arquivo.exists():
        return None
    atual = arquivo.read_bytes()
    if novo is not None and _igual(atual, novo):
        return None
    pasta = Path(raiz) / "_historico" / f"{hoje or dt.date.today().isoformat()} {rotulo}"
    pasta.mkdir(parents=True, exist_ok=True)
    destino, n = pasta / arquivo.name, 1
    while destino.exists():
        if _igual(destino.read_bytes(), atual):
            return destino                      # essa versão já está guardada
        n += 1
        destino = pasta / f"{arquivo.stem}.{n}{arquivo.suffix}"
    shutil.copyfile(arquivo, destino)
    return destino


def gravar_texto(arquivo: Path, texto: str, rotulo: str, raiz: Path = RAIZ, hoje: str | None = None,
                 **kw) -> None:
    """`Path.write_text(texto, encoding="utf-8", **kw)` precedido de `guardar` (kw: ex. `newline="\\n"`)."""
    arquivo = Path(arquivo)
    guardar(arquivo, rotulo, texto.encode("utf-8"), raiz, hoje)
    arquivo.write_text(texto, encoding="utf-8", **kw)
