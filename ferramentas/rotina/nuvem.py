"""BOOTSTRAP × nuvem (26/11/2026): o texto do campo de comando da rotina tem de ser o bloco literal do BOOTSTRAP.md.

A API da nuvem só é alcançável pela ferramenta RemoteTrigger do Claude Code (não por este Python). Por isso:
1. `bloco` imprime o bloco literal (é o `content` do RemoteTrigger `update`);
2. depois do `update`, o RemoteTrigger `get` devolve o texto publicado; salvo num arquivo, `conferir <arquivo>` compara com o
   bloco e, se igual, grava `docs/ops/rotina/nuvem.json` (sha256 + data + próximo horário). Diferente → rc 1, nada gravado;
3. `tests/test_rotina.py` exige sha256(bloco) == nuvem.json: mudar o BOOTSTRAP sem republicar e conferir deixa a suíte vermelha.

    cd ferramentas && python -m rotina.nuvem bloco
    cd ferramentas && python -m rotina.nuvem conferir <arquivo> --next-run 2026-11-27T07:40:00Z --enabled true
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
BOOTSTRAP = RAIZ / "docs" / "ops" / "rotina" / "BOOTSTRAP.md"
REGISTRO = RAIZ / "docs" / "ops" / "rotina" / "nuvem.json"
TRIGGER = "trig_016wrGPsNHp4dUaVAExNhZyU"


def normalizar(texto: str) -> str:
    return "\n".join(l.rstrip() for l in texto.replace("\r\n", "\n").strip().split("\n"))


def bloco(caminho: Path = BOOTSTRAP) -> str:
    texto = caminho.read_text(encoding="utf-8").replace("\r\n", "\n")
    ini = texto.index("```text\n") + len("```text\n")
    return normalizar(texto[ini:texto.index("\n```", ini)])


def sha(texto: str) -> str:
    return hashlib.sha256(normalizar(texto).encode("utf-8")).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("bloco")
    c = sub.add_parser("conferir")
    c.add_argument("arquivo", type=Path)
    c.add_argument("--next-run", default=None)
    c.add_argument("--enabled", default=None)
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    if a.cmd == "bloco":
        print(bloco())
        return 0
    nuvem, local = normalizar(a.arquivo.read_text(encoding="utf-8")), bloco()
    if nuvem != local:
        ln, ll = nuvem.split("\n"), local.split("\n")
        i = next((k for k in range(min(len(ln), len(ll))) if ln[k] != ll[k]), min(len(ln), len(ll)))
        print(f"DIFERENTE na linha {i + 1}: nuvem={ln[i][:120] if i < len(ln) else '(fim)'!r} "
              f"repo={ll[i][:120] if i < len(ll) else '(fim)'!r}")
        return 1
    REGISTRO.write_text(json.dumps({"trigger_id": TRIGGER, "sha256": sha(local), "caracteres": len(local),
                                    "conferido_em": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
                                    "enabled": a.enabled, "next_run_at": a.next_run}, ensure_ascii=False, indent=1) + "\n",
                        encoding="utf-8")
    print(f"IGUAL ({len(local)} caracteres) → {REGISTRO.relative_to(RAIZ).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
