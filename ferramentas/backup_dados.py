"""Backup dos dados que NÃO se recriam (AUD-05, auditoria de 08/10/2026).

Grava em DESTINO (OneDrive) um ZIP datado com ferramentas/dados sem cvm/ (ZIPs da CVM se rebaixam por
`bootstrap_dados.py`) e um `git bundle` do repositório inteiro. Os dados são públicos (sem LGPD).
Uso: python backup_dados.py [--destino PASTA]
"""
from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import zipfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DADOS = Path(__file__).resolve().parent / "dados"
DESTINO = Path.home() / "OneDrive" / "Backups" / "value-investing"
EXCLUIR = {"cvm"}
# evidência fora de dados/ que não se recria: o log append-only da trava anti-calibração e a consulta original do proxy
EVIDENCIA = (DADOS.parent / "backtest" / "dados",)
PADROES_EVIDENCIA = ("proxy_*",)


def arquivos(dados: Path = DADOS, evidencia=EVIDENCIA, destino: Path | None = None):
    for p in sorted(dados.rglob("*")):
        if p.is_file() and not (set(p.relative_to(dados).parts) & EXCLUIR) and not _dentro(p, destino):
            yield p
    for pasta in evidencia:
        for pad in PADROES_EVIDENCIA:
            yield from (p for p in sorted(pasta.glob(pad)) if p.is_file())


def _dentro(p: Path, pasta: Path | None) -> bool:
    return pasta is not None and pasta.resolve() in p.resolve().parents


def zipar(destino: Path, dados: Path = DADOS, hoje: str | None = None, evidencia=EVIDENCIA) -> Path:
    destino = destino.resolve()
    destino.mkdir(parents=True, exist_ok=True)
    alvo = destino / f"dados_{hoje or dt.date.today().isoformat()}.zip"
    with zipfile.ZipFile(alvo, "w", zipfile.ZIP_DEFLATED) as z:
        for p in arquivos(dados, evidencia, destino):
            z.write(p, p.relative_to(dados.parent).as_posix())
    return alvo


def bundle(destino: Path, hoje: str | None = None) -> Path:
    destino = destino.resolve()
    destino.mkdir(parents=True, exist_ok=True)
    alvo = destino / f"repo_{hoje or dt.date.today().isoformat()}.bundle"
    subprocess.run(["git", "bundle", "create", str(alvo), "--all"], cwd=RAIZ, check=True)
    return alvo


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--destino", type=Path, default=DESTINO)
    a = ap.parse_args()
    for f in (zipar(a.destino), bundle(a.destino)):
        print(f"{f}  {f.stat().st_size / 1e6:.1f} MB")
