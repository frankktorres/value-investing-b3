"""Atualiza o 03-hall-de-acoes.md com o Lote 5 recalculado (números do motor). Idempotente."""
import pathlib
import re
import sys

from lote1_bancos import MK
from lote5_petroleo import EMPRESAS, FORA_DO_HALL
from motor_nao_financeiras import avaliar

sys.stdout.reconfigure(encoding="utf-8")
HALL = pathlib.Path(__file__).parent.parent / "03-hall-de-acoes.md"
SETOR = {"PETR4": "Petróleo estatal", "PRIO3": "E&P", "RECV3": "E&P onshore", "UGPA3": "Distribuição", "VBBR3": "Distribuição"}
CAB = {"BARATA": "### BARATA", "RADAR": "### RADAR", "JUSTA": "### JUSTA", "CARA": "### CARA", "NÃO CONCLUSIVO": "### NÃO CONCLUSIVO"}
SECAO_NC = ("### NÃO CONCLUSIVO (âncora ≤ 0 ou âncoras discordam mais de 3× — doutrina §11.3; sem preço de compra)\n\n"
            "| Ticker | Setor | Preço 02/10 | Mediana das âncoras | P/C | Compra 0,70× | Saída 1,30× | Pendências v2 / motivo |\n"
            "|---|---|---|---|---|---|---|---|\n")


def br(x, c=2):
    return f"{x:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def motivo(tk, e, r):
    m = (f"**recalculado v2.1 (05/10)**; Ke implícito {br(100 * r['ke_implicito'], 1) + '%' if r['ke_implicito'] else 'n.d.'}; "
         f"ROIC {br(100 * r['roic'], 1)}% × WACC {br(100 * r['wacc'], 1)}%; confiança {r['confianca']}")
    if tk in ("PETR4", "PRIO3", "RECV3"):
        m += "; barril de meio de ciclo R$ 406 (≈ US$ 78)"
    if tk == "PETR4":
        m += (f"; desconto de controlador {br(100 * r['desc_controlador'], 0)}% em cenários; ganhos de desinvestimento 2019–22 fora da margem; "
              "déficit atuarial fora da ponte (custo já no EBIT); com abandono ou déficit como dívida seria CARA")
    if tk == "PRIO3":
        m += "; base 1S26 (Peregrino); com imposto de exportação permanente o central cai ~50%"
    if tk == "RECV3":
        ex = {k.split(" ")[0]: br(v) for k, v in r["ancoras"].items()}
        m += (f"; EPV {ex['EPV']} · DCF {ex['DCF']} · reprodução {ex['Valor']} — as âncoras de lucro são ≤ 0 no meio de ciclo; "
              "**defeito estrutural:** produção em declínio (−11% a/a) com ROIC abaixo do WACC")
    if tk == "UGPA3":
        m += "; EBIT real 2021–25; nem a margem de guerra permanente justifica o preço"
    if e.preco > r["saida"] and r["palavra"] != "NÃO CONCLUSIVO":
        m += " (S)"
    return m


def main():
    t = HALL.read_text(encoding="utf-8")
    t = t.replace("### NÃO CONCLUSIVO (âncoras discordam mais de 3× — doutrina §11.3; sem preço de compra)", SECAO_NC.split("\n")[0])
    if "### NÃO CONCLUSIVO" not in t:
        t = t.replace("\n---\n\n## 2. As que vencem", "\n" + SECAO_NC + "\n---\n\n## 2. As que vencem", 1)
    linhas = [l for l in t.split("\n") if not re.match(r"^\| (%s) \|" % "|".join(SETOR), l)]
    res = {e.ticker: (e, avaliar(e, MK)) for e in EMPRESAS}
    for tk in sorted(SETOR, key=lambda k: -res[k][1]["pc"]):
        e, r = res[tk]
        if tk in FORA_DO_HALL:
            continue
        i = next(k for k, l in enumerate(linhas) if l.startswith(CAB[r["palavra"]]))
        j = next(k for k in range(i, len(linhas)) if linhas[k].startswith("|---"))
        ncols = linhas[j].count("|") - 1
        nc = r["palavra"] == "NÃO CONCLUSIVO"
        sc = r["central"] <= 0
        base = [tk, SETOR[tk], br(e.preco), "**≤ 0 (v2)**" if sc else f"**{br(r['central'])} (v2)**", "n.a." if sc else br(r["pc"]),
                "n.a." if nc else br(r["compra"]),
                "n.a." if nc else br(r["saida"])]
        base += ([r["vence_rf"] + " (v2, líquida)", motivo(tk, e, r)] if ncols == 9 else [motivo(tk, e, r)])
        linhas.insert(j + 1, "| " + " | ".join(base) + " |")
    e, r = res["VBBR3"]
    i = next(k for k, l in enumerate(linhas) if l.startswith("## 4. Fora do hall"))
    j = next(k for k in range(i, len(linhas)) if linhas[k].startswith("|---"))
    linhas.insert(j + 1, f"| VBBR3 | R$ {br(e.preco)} · **central {br(r['central'])} (v2.1, 05/10; P/C {br(r['pc'])})** | Redundante com UGPA3 e pior em "
                         "dívida, Comerc e diferimento de JCP (14–18 meses); EBIT real 2020–25 sem créditos tributários; só a margem de guerra "
                         "permanente justificaria o preço |")
    t = "\n".join(linhas)
    t = t.replace("**exceto os Lotes 1 (Bancos e Seguridade), 2 (Energia e Saneamento) e 3 (Agro e B3), recalculados em 04–05/10 pela v2.0/2.1**",
                  "**exceto os Lotes 1 (Bancos e Seguridade), 2 (Energia e Saneamento), 3 (Agro e B3) e 5 (Petróleo e Gás), recalculados em 04–05/10 pela v2.0/2.1**")
    t = t.replace("| 5 | Petróleo, gás e combustíveis (5) | `PETROLEO E GÁS/Petroleo_Gas_rev_03-10-2026.pdf` | `…_rev_06-09-2026.pdf` |",
                  "| 5 | Petróleo, gás e combustíveis (5) | `PETROLEO E GÁS/Petroleo_Gas_rev_05-10-2026.pdf` **(v2.1)** | `…_rev_03-10-2026.pdf`, `…_rev_06-09-2026.pdf` |")
    pal = {p: [tk for tk, (_, r) in res.items() if r["palavra"] == p and tk not in FORA_DO_HALL] for p in ("RADAR", "JUSTA", "CARA", "NÃO CONCLUSIVO")}
    reg = ("| 05/10/2026 | Lote 5 (5) | recalculado pela v2.1 | Barril de meio de ciclo declarado (média de 10 anos do Brent × câmbio em R$ de hoje = "
           "R$ 406/bbl, ≈ US$ 78); E&P por EBITDA mediano − D&A atual; distribuidoras por EBIT real; PETR4 com 8% de desconto de controlador em cenários. "
           + " · ".join(f"{p}: {', '.join(v)}" for p, v in pal.items() if v)
           + f" · VBBR3 fora do hall (CARA {br(res['VBBR3'][1]['pc'])}). Razão (c): a rev. 03/10 usava Brent US$ 70 sem câmbio, múltiplos sem capex "
             "e '+1 tri de topo' |")
    t = "\n".join(l for l in t.split("\n") if not l.startswith("| 05/10/2026 | Lote 5 (5) |"))
    t = t.rstrip("\n") + "\n" + reg + "\n"
    HALL.write_text(t, encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
