"""Atualiza o 03-hall-de-acoes.md com o Lote 2 recalculado (números do motor). Idempotente."""
import pathlib
import re
import sys

from lote1_bancos import MK
from lote2_energia import EMPRESAS
from motor_financeiras import avaliar

sys.stdout.reconfigure(encoding="utf-8")
HALL = pathlib.Path(__file__).parent.parent / "03-hall-de-acoes.md"
SETOR = {"TAEE11": "Transmissão", "ISAE4": "Transmissão", "CPFE3": "Utility", "CMIG4": "Utility estatal", "CPLE3": "Utility",
         "SAPR11": "Saneamento estatal", "CSMG3": "Saneamento", "SBSP3": "Saneamento"}
CAB = {"BARATA": "### BARATA", "RADAR": "### RADAR", "JUSTA": "### JUSTA", "CARA": "### CARA"}


def br(x, c=2):
    return f"{x:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    t = HALL.read_text(encoding="utf-8")
    linhas = [l for l in t.split("\n") if not re.match(r"^\| (%s) \|" % "|".join(SETOR), l)]
    res = {e.ticker: (e, avaliar(e, MK)) for e in EMPRESAS}
    for tk in sorted(SETOR, key=lambda k: -res[k][1]["pc"]):
        e, r = res[tk]
        tir = (1 + r["ke_implicito"]) / (1 + MK.pi) - 1 if r["ke_implicito"] else None
        motivo = (f"**recalculado v2.1 (05/10)**; TIR real implícita {br(100 * tir, 1) + '%' if tir is not None else 'n.c.'} "
                  f"(Tesouro {br(100 * MK.rf_real, 2)}%; Ke real {br(100 * MK.ke_real, 2)}%)")
        if tir is not None and tir < MK.rf_real:
            motivo += " — **rende menos que o Tesouro**"
        if r["desc_controlador"] > 0:
            motivo += f"; desconto de controlador {br(100 * r['desc_controlador'], 1)}%"
        if tk == "ISAE4":
            motivo += "; com 659 mi ações (DFP 2025) seria JUSTA — conferir follow-on no RI"
        if e.preco > r["saida"]:
            motivo += " (S)"
        i = next(k for k, l in enumerate(linhas) if l.startswith(CAB[r["palavra"]]))
        j = next(k for k in range(i, len(linhas)) if linhas[k].startswith("|---"))
        ncols = linhas[j].count("|") - 1
        base = [tk, SETOR[tk], br(e.preco), f"**{br(r['central'])} (v2)**", br(r["pc"]), br(r["compra"]), br(r["saida"])]
        base += ([r["vence_rf"] + " (v2, líquida)", motivo] if ncols == 9 else [motivo])
        linhas.insert(j + 1, "| " + " | ".join(base) + " |")
    t = "\n".join(linhas)
    t = t.replace("**exceto os Lotes 1 (Bancos e Seguridade) e 3 (Agro e B3), recalculados em 04/10 pela v2.0**",
                  "**exceto os Lotes 1 (Bancos e Seguridade), 2 (Energia e Saneamento) e 3 (Agro e B3), recalculados em 04–05/10 pela v2.0/2.1**")
    t = t.replace("| 2 | Energia elétrica e saneamento (8) | `ENERGIA ELÉTRICA E SANEAMENTO/Energia_Saneamento_rev_03-10-2026.pdf` | `…_rev_07-09-2026.pdf` |",
                  "| 2 | Energia elétrica e saneamento (8) | `ENERGIA ELÉTRICA E SANEAMENTO/Energia_Saneamento_rev_05-10-2026.pdf` **(v2.1)** | `…_rev_03-10-2026.pdf`, `…_rev_07-09-2026.pdf` |")
    reg = ("| 05/10/2026 | Lote 2 (8) | recalculado pela v2.1 | Regulados por P/VP justificado (patrimônio como proxy da base) + DDM, TIR real implícita "
           "sempre. Todos CARA (P/C " + br(min(r["pc"] for _, r in res.values())) + "–" + br(max(r["pc"] for _, r in res.values())) +
           "); CPLE3, CSMG3 e SBSP3 rendem menos que o Tesouro. Razão (c): a rev. 03/10 usava ajustes avulsos e inflação de 4% |")
    t = "\n".join(l for l in t.split("\n") if not l.startswith("| 05/10/2026 | Lote 2 (8) |"))
    t = t.rstrip("\n") + "\n" + reg + "\n"
    HALL.write_text(t, encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
