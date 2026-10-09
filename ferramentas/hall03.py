"""Confere e corrige o quadro geral do `03-hall-de-acoes.md` pelo motor (AUD-77).

As células numéricas (preço, central, P/C, compra, saída) e a marca (S) são GERADAS do motor
(`universo.avaliar_todos()`); setor, "Vence RF?" e o texto do motivo continuam escritos à mão. Até a Onda 1.2
a marca (S) era digitada e quatro linhas ficaram erradas (SUZB3, GGBR4, PRIO3 sem; KLBN11 com, sendo NC).

Regras (as mesmas do monitor, `monitor_semanal.alerta`):
- (S) ⇔ preço ≥ saída **e** palavra ≠ NÃO CONCLUSIVO;
- NÃO CONCLUSIVO → compra e saída "n.a." (§9: sem palavra final não há preço de compra nem de saída);
- central ≤ 0 → P/C "n.d."; saída pela exceção de qualidade → "(1,50×)" na célula;
- a seção (### BARATA / RADAR / JUSTA / CARA / NÃO CONCLUSIVO) tem de ser a palavra do motor.

Também gera o bloco do hall no `PROMPT-AGENTE-NOTICIAS-SEXTA.md` (entre os marcadores `hall03`).

    cd ferramentas && python hall03.py              # lista divergências (código 1 se houver)
    cd ferramentas && python hall03.py --corrigir   # reescreve as células, a marca (S) e o bloco do prompt
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
HALL = RAIZ / "03-hall-de-acoes.md"
PROMPT = RAIZ / "PROMPT-AGENTE-NOTICIAS-SEXTA.md"
NC = "NÃO CONCLUSIVO"
# §4 do 03: avaliadas pelo motor, fora do quadro geral (falham 2 filtros ou nunca entraram; prompt de sexta idem)
FORA_DO_HALL = {"BBAS3", "BRSR6", "SANB11", "UNIP6", "VBBR3"}
SECOES = {"BARATA": ("BARATA", "OPORTUNIDADE"), "RADAR": ("RADAR",), "JUSTA": ("JUSTA",), "CARA": ("CARA",),
          "NÃO CONCLUSIVO": (NC,)}
INICIO, FIM = "<!-- hall03:inicio (gerado por ferramentas/hall03.py; não editar à mão) -->", "<!-- hall03:fim -->"
# o número do central é o PRIMEIRO da célula (com ou sem negrito); outro formato = divergência, nunca troca silenciosa
_NUM = re.compile(r"^(\*\*)?(-?\d+(?:\.\d{3})*,\d+)")
# (S) só como marca: antes de ";", de "**" ou no fim da célula — "segmento (S) do grupo" não é marca
_S = re.compile(r" ?\(S\)(?=;|\*\*|\s*$)")
_TICKER = re.compile(r"^[A-Z][A-Z0-9]{3}\d{1,2}$")      # B3SA3 tem dígito na 2ª posição


def br(x: float, nd: int = 2) -> str:
    return f"{x:.{nd}f}".replace(".", ",")


# ------------------------------------------------------------------------------ esperado
def esperado(todos: dict | None = None) -> dict[str, dict]:
    """{ticker: células esperadas} pelo motor."""
    import monitor_semanal as M
    if todos is None:
        import universo
        todos = universo.avaliar_todos()
    out = {}
    for tk, it in todos.items():
        r, preco = it["r"], float(it["empresa"].preco)
        central, palavra = float(r["central"]), r["palavra"]
        sem_regua = palavra == NC or central <= 0
        q = " (1,50×)" if r.get("saida_por_qualidade") and not sem_regua else ""
        out[tk] = dict(palavra=palavra, preco=br(preco), central=br(central),
                       pc=br(preco / central) if central > 0 else "n.d.",
                       compra="n.a." if sem_regua else br(r["compra"]),
                       saida="n.a." if sem_regua else br(r["saida"]) + q,
                       s=M.alerta(preco, r["compra"], r["saida"], palavra) == M.SAIDA,
                       preco_f=preco, central_f=central, compra_f=r["compra"], saida_f=r["saida"])
    return out


# ------------------------------------------------------------------------------ leitura
def ler(texto: str) -> list[dict]:
    """Linhas do quadro geral (seção 1): ticker, seção, índice da linha e células."""
    out, secao, dentro = [], None, False
    for i, linha in enumerate(texto.split("\n")):
        if linha.startswith("## "):
            dentro = linha.startswith("## 1.")
            continue
        if not dentro:
            continue
        if linha.startswith("### "):
            secao = next((k for k in SECOES if linha[4:].startswith(k)), None)
            continue
        if not linha.startswith("| "):
            continue
        cel = [c.strip() for c in linha.strip().strip("|").split("|")]
        if not _TICKER.match(cel[0]):
            continue
        out.append(dict(ticker=cel[0], secao=secao, i=i, cel=cel))
    return out


def _celulas(cel: list[str]) -> dict[str, str]:
    return dict(preco=cel[2], central=cel[3], pc=cel[4], compra=cel[5], saida=cel[6], motivo=cel[-1])


def divergencias(texto: str, esp: dict[str, dict]) -> list[tuple[str, str, str, str]]:
    """[(ticker, campo, no 03, motor)]."""
    out = []
    linhas = ler(texto)
    vistos = {x["ticker"] for x in linhas}
    for x in linhas:
        tk, c = x["ticker"], _celulas(x["cel"])
        e = esp.get(tk)
        if e is None:
            out.append((tk, "ticker", "no 03", "fora do motor"))
            continue
        if e["palavra"] not in SECOES.get(x["secao"], ()):
            out.append((tk, "seção", str(x["secao"]), e["palavra"]))
        m = _NUM.match(c["central"])
        for campo, no03 in (("preco", c["preco"]), ("central", m.group(2) if m else c["central"]),
                            ("pc", c["pc"]), ("compra", c["compra"]), ("saida", c["saida"])):
            if no03 != e[campo]:
                out.append((tk, campo, no03, e[campo]))
        tem_s = bool(_S.search(c["motivo"]))
        if tem_s != e["s"]:
            out.append((tk, "(S)", "sim" if tem_s else "não", "sim" if e["s"] else "não"))
    for tk in sorted(set(esp) - vistos - FORA_DO_HALL):
        out.append((tk, "ticker", "ausente do 03", "no motor"))
    return out


# ------------------------------------------------------------------------------ correção
def corrigir_texto(texto: str, esp: dict[str, dict]) -> str:
    linhas = texto.split("\n")
    for x in ler(texto):
        e = esp.get(x["ticker"])
        if e is None:
            continue
        cel = list(x["cel"])
        cel[2], cel[4], cel[5], cel[6] = e["preco"], e["pc"], e["compra"], e["saida"]
        m = _NUM.match(cel[3])
        cel[3] = cel[3][:m.start(2)] + e["central"] + cel[3][m.end(2):] if m else f"**{e['central']}**"
        motivo = cel[-1]
        if e["s"] and not _S.search(motivo):
            motivo = motivo.rstrip() + " (S)"
        elif not e["s"] and _S.search(motivo):
            motivo = _S.sub("", motivo)
        cel[-1] = motivo
        linhas[x["i"]] = "| " + " | ".join(cel) + " |"
    return "\n".join(linhas)


# ------------------------------------------------------------------------------ prompt de sexta
def lista_prompt(esp: dict[str, dict]) -> str:
    """Bloco do hall no prompt de notícias: ticker e preço de compra por palavra, P/C crescente."""
    hall = {tk: e for tk, e in esp.items() if tk not in FORA_DO_HALL}
    pc = lambda tk: hall[tk]["preco_f"] / hall[tk]["central_f"] if hall[tk]["central_f"] > 0 else math.inf
    s = []
    for nome, palavras in SECOES.items():
        tks = sorted((tk for tk, e in hall.items() if e["palavra"] in palavras), key=lambda t: (pc(t), t))
        if not tks:
            continue
        if nome == NC:
            s.append(f"NÃO CONCLUSIVO (sem preço de compra nem de saída; só acompanhar): {' · '.join(tks)}")
        else:
            s.append(f"{nome}: " + " · ".join(f"{tk} {hall[tk]['compra']}" for tk in tks))
    return "\n".join([INICIO, *s, FIM])


def bloco_do_prompt(texto: str) -> str | None:
    a, b = texto.find("<!-- hall03:inicio"), texto.find(FIM)
    return texto[a:b + len(FIM)] if a >= 0 and b > a else None


def corrigir_prompt(texto: str, esp: dict[str, dict]) -> str:
    atual = bloco_do_prompt(texto)
    if atual is None:
        raise ValueError("marcadores hall03 ausentes no prompt de sexta")
    return texto.replace(atual, lista_prompt(esp))


# ------------------------------------------------------------------------------ CLI
def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corrigir", action="store_true")
    a = ap.parse_args(argv)
    esp = esperado()
    texto = HALL.read_text(encoding="utf-8")
    prompt = PROMPT.read_text(encoding="utf-8")
    if a.corrigir:
        HALL.write_bytes(corrigir_texto(texto, esp).encode("utf-8"))
        PROMPT.write_bytes(corrigir_prompt(prompt, esp).encode("utf-8"))
        texto, prompt = HALL.read_text(encoding="utf-8"), PROMPT.read_text(encoding="utf-8")
    div = divergencias(texto, esp)
    for tk, campo, no03, motor in div:
        print(f"{tk:7} {campo:8} 03: {no03:>14}   motor: {motor}")
    prompt_ok = bloco_do_prompt(prompt) == lista_prompt(esp)
    print(f"03: {len(div)} divergência(s) · prompt de sexta: {'igual ao motor' if prompt_ok else 'DIVERGE'}"
          + ("" if a.corrigir or (not div and prompt_ok) else " → python hall03.py --corrigir"))
    return 1 if div or not prompt_ok else 0


if __name__ == "__main__":
    sys.exit(main())
