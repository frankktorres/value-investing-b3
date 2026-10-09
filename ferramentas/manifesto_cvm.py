"""Manifesto sha256 dos ZIPs da CVM em dados/cvm/ (AUD-109 e AUD-73, auditoria de 08/10/2026).

Os ZIPs ficam fora do git (1,4 GB, recoletáveis), mas alimentam o golden: se a CVM reapresentar o ITR, o golden muda sem que
nada aponte a causa. O `dados/cvm/MANIFESTO.json` (versionado) registra sha256 e tamanho de cada ZIP usado; `verificar()` diz
quais diferem do registrado, quais faltam e quais não têm registro.

A CVM reescreve os arquivos de dados abertos — um download novo pode legitimamente diferir. Por isso `temporada.baixar_itr`
guarda a cópia datada do ZIP anterior em `dados/cvm/_antes/` e chama `registrar()` para atualizar o manifesto.

Uso: python manifesto_cvm.py --verificar | --gerar
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import pathlib
import sys

AQUI = pathlib.Path(__file__).parent
CACHE = AQUI / "dados" / "cvm"
MANIFESTO = CACHE / "MANIFESTO.json"


def sha256_arquivo(caminho: pathlib.Path) -> tuple[str, int]:
    """(sha256 hex, bytes lidos). O tamanho vem da leitura, não do stat (arquivo aberto por outro processo fica defasado)."""
    h, n = hashlib.sha256(), 0
    with caminho.open("rb") as f:
        while bloco := f.read(1 << 20):
            h.update(bloco)
            n += len(bloco)
    return h.hexdigest(), n


def _zips(pasta: pathlib.Path) -> list[pathlib.Path]:
    return sorted(pasta.glob("*.zip"))


def carregar(manifesto: pathlib.Path = MANIFESTO) -> dict:
    if not manifesto.exists():
        return {}
    return json.loads(manifesto.read_text(encoding="utf-8")).get("arquivos", {})


def _salvar(arquivos: dict, manifesto: pathlib.Path) -> None:
    manifesto.parent.mkdir(parents=True, exist_ok=True)
    corpo = {"nota": "sha256 dos ZIPs da CVM em dados/cvm (fora do git). A CVM reescreve arquivos; ver manifesto_cvm.py.",
             "atualizado_em": dt.date.today().isoformat(), "arquivos": dict(sorted(arquivos.items()))}
    manifesto.write_text(json.dumps(corpo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")


def gerar(pasta: pathlib.Path = CACHE, manifesto: pathlib.Path = MANIFESTO) -> int:
    """Recalcula o manifesto de todos os ZIPs presentes. Devolve quantos."""
    arquivos = {}
    for z in _zips(pasta):
        sha, n = sha256_arquivo(z)
        arquivos[z.name] = {"sha256": sha, "bytes": n}
    _salvar(arquivos, manifesto)
    return len(arquivos)


def registrar(caminho: pathlib.Path, manifesto: pathlib.Path = MANIFESTO) -> dict:
    """Atualiza só a entrada de um ZIP (depois de um download deliberado)."""
    arquivos = carregar(manifesto)
    sha, n = sha256_arquivo(caminho)
    arquivos[caminho.name] = {"sha256": sha, "bytes": n}
    _salvar(arquivos, manifesto)
    return arquivos[caminho.name]


def verificar(pasta: pathlib.Path = CACHE, manifesto: pathlib.Path = MANIFESTO) -> dict[str, list[str]]:
    """{'ok', 'diferem', 'faltam', 'sem_registro'} (listas de nomes). 'faltam' = no manifesto mas não em disco."""
    reg = carregar(manifesto)
    out = {"ok": [], "diferem": [], "faltam": [], "sem_registro": []}
    for nome, info in reg.items():
        f = pasta / nome
        if not f.exists():
            out["faltam"].append(nome)
        elif sha256_arquivo(f)[0] == info["sha256"]:
            out["ok"].append(nome)
        else:
            out["diferem"].append(nome)
    out["sem_registro"] = [z.name for z in _zips(pasta) if z.name not in reg]
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Manifesto sha256 dos ZIPs da CVM")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--verificar", action="store_true", help="compara os ZIPs em disco com o manifesto")
    g.add_argument("--gerar", action="store_true", help="recalcula o manifesto com os ZIPs que estão em disco")
    a = ap.parse_args(argv)
    if a.gerar:
        print(f"manifesto gravado: {gerar()} ZIPs em {MANIFESTO}")
        return 0
    r = verificar()
    print(f"ok {len(r['ok'])} · diferem {len(r['diferem'])} · faltam {len(r['faltam'])} · sem registro {len(r['sem_registro'])}")
    for chave in ("diferem", "faltam", "sem_registro"):
        for nome in r[chave]:
            print(f"  {chave}: {nome}")
    return 1 if r["diferem"] else 0


if __name__ == "__main__":
    sys.exit(main())
