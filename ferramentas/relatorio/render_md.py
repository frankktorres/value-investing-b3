"""Relatório em Markdown: cada número com valor, nota e fonte na mesma linha."""
from __future__ import annotations

from relatorio.modelo import Numero, Relatorio, decide

PAPEL = {"central": "entra no central", "informativo": "informativo", "": ""}


def fmt(v, unidade: str = "") -> str:
    if v is None:
        return "—"
    if isinstance(v, str):
        return v
    if isinstance(v, int) and not isinstance(v, bool):
        return str(v)
    if unidade == "R$ mil":          # valores do balanço da CVM, em R$ mil
        return fmt(v / 1e6, "") + " bi" if abs(v) >= 1e6 else fmt(v / 1e3, "") + " mi"
    if unidade == "%":
        return f"{100 * v:.1f}%".replace(".", ",")
    if unidade == "x":
        return f"{v:.2f}×".replace(".", ",")
    if unidade == "R$":
        return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{v:.2f}".replace(".", ",")


def _celula(t: str) -> str:
    return t.replace("|", "/").replace("\n", " ")


def _nota(n: Numero) -> str:
    return n.nota if decide(n.nota) or n.valor is None else f"**{n.nota}**"


def render(rel: Relatorio) -> str:
    L = [f"# {rel.tk} — {rel.nome}", "",
         f"**Palavra: {rel.palavra}** · data-base {rel.data} · origem: {rel.origem}", "",
         "Relatório gerado pelos motores do repositório (vista; não grava veredito). Nota da fonte: A oficial, B primária "
         "com ressalva, C agregador ou não conferido, — sem fonte. Só A/B embasa decisão.", ""]
    if rel.avisos:
        L += ["## Avisos", ""] + [f"- {a}" for a in rel.avisos] + [""]
    for s in rel.secoes:
        L += [f"## {s.titulo}", ""]
        if s.numeros:
            L += ["| Item | Valor | Papel | Nota | Fonte |", "|---|---|---|---|---|"]
            for n in s.numeros:
                fonte = n.obs if n.valor is None and n.obs else (n.fonte + (f" ({n.obs})" if n.obs else ""))
                nota = "" if n.valor is None and not n.origens else _nota(n)
                L.append(f"| {_celula(n.rotulo)} | {fmt(n.valor, n.unidade)} | {PAPEL.get(n.papel, n.papel)} | "
                         f"{nota} | {_celula(fonte)} |")
            L.append("")
        for titulo, cab, linhas in s.tabelas:
            L += [f"**{titulo}**", "", "| " + " | ".join(cab) + " |", "|" + "---|" * len(cab)]
            L += ["| " + " | ".join(x) + " |" for x in linhas] + [""]
        for x in s.texto:
            L += [x, ""]
        L += [f"> {a}" for a in s.avisos if a not in rel.avisos] + ([""] if s.avisos else [])
    L += ["## Fontes", "", "| Fonte | Nota | O que é |", "|---|---|---|"]
    L += [f"| {o.fonte} | {o.nota} | {_celula(o.detalhe or o.fonte)} |" for o in rel.fontes().values()]
    return "\n".join(L).rstrip() + "\n"
