"""Junta as seções num `Relatorio` e confere a palavra contra o veredito vigente (dossiê gravado ou golden do hall)."""
from __future__ import annotations

import json
import pathlib

from relatorio import procedencia as pr
from relatorio import quanti
from relatorio.caso import caso
from relatorio.modelo import Relatorio, Secao

GOLDEN = pathlib.Path(__file__).resolve().parent.parent / "tests" / "golden.json"


def vigente(c: dict) -> tuple[str, str | None]:
    """(de onde, palavra vigente) — o relatório é vista: a palavra tem de ser a mesma."""
    if c["dossie"] is not None:
        g = c["gravado"]
        return f"dossie/vereditos/{c['tk']}-{c['data']}.json", (g or {}).get("palavra")
    g = json.loads(GOLDEN.read_text(encoding="utf-8"))["tickers"].get(c["tk"], {})
    return "tests/golden.json", g.get("palavra")


def montar(tk: str, data: str | None = None) -> Relatorio:
    c = caso(tk, data)
    r = c["r"]
    rel = Relatorio(c["tk"], c["empresa"].nome, c["data"], c["origem"], r["palavra"])
    rel.secoes += [quanti.secao_veredito(c), quanti.secao_preco(c), quanti.secao_sensibilidade(c),
                   Secao("Premissas de julgamento (método, não dado)", texto=pr.premissas(c))]
    onde, p = vigente(c)
    if p is None:
        rel.avisos.append(f"Sem veredito vigente gravado para conferir ({onde}).")
    elif p != r["palavra"]:
        rel.avisos.append(f"DIVERGE do veredito vigente: {onde} diz {p}, o motor hoje diz {r['palavra']} — "
                          "dado ou premissa mudou; a palavra vigente não é trocada por este relatório.")
    if c["dossie"] is None:
        rel.avisos.append("Premissas do hall digitadas no lote (data-base do hall); o dossiê do ticker troca os escalares "
                          "por dado A da CVM/B3.")
    for s in rel.secoes:
        rel.avisos += [a for a in s.avisos if a.startswith("O valor central")]
    return rel
