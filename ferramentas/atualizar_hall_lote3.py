"""Atualiza o 03-hall-de-acoes.md com o Lote 3 recalculado (números do motor). Rodar uma vez por recálculo."""
import pathlib
import re
import sys

from lote1_bancos import MK
from lote3_agro import EMPRESAS
from motor_nao_financeiras import avaliar

sys.stdout.reconfigure(encoding="utf-8")
HALL = pathlib.Path(__file__).parent.parent / "03-hall-de-acoes.md"
SETOR = {"SUZB3": "Celulose", "KLBN11": "Papel", "RANI3": "Embalagem", "B3SA3": "Infraestrutura de mercado",
         "SMTO3": "Açúcar e etanol", "KEPL3": "Agro, bens de capital", "SLCE3": "Agro, terras"}
CAB = {"BARATA": "### BARATA", "RADAR": "### RADAR", "JUSTA": "### JUSTA", "CARA": "### CARA"}


def pct_ou_nd(x):
    """ROIC pode ser None (sem capital investido positivo) — não derruba o hall."""
    return "n.d." if x is None else br(100 * x, 1) + "%"


def br(x, c=2):
    return f"{x:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    t = HALL.read_text(encoding="utf-8")
    linhas = [l for l in t.split("\n") if not re.match(r"^\| (%s) \|" % "|".join(SETOR), l)]
    res = {e.ticker: (e, avaliar(e, MK)) for e in EMPRESAS}
    for tk in sorted(SETOR, key=lambda k: -res[k][1]["pc"]):
        e, r = res[tk]
        p = r["palavra"]
        motivo = (f"**recalculado v2.2 (05/10; base 04/10)**; Ke implícito {br(100 * r['ke_implicito'], 1)}%; ROIC {pct_ou_nd(r['roic'])} contábil / {pct_ou_nd(r['roic_reposicao'])} a reposição × WACC "
                  f"{br(100 * r['wacc'], 1)}%; confiança {r['confianca']}")
        if tk == "SLCE3":
            motivo += "; CARA mesmo com o NAV de terras de terceiro; arrendamento de terras (IFRS 16) na dívida"
        if tk == "SMTO3":
            motivo += "; margem bimodal: BARATA só com margem ≥ 27%; outras receitas não recorrentes de mar/2024 normalizadas"
        if e.preco > r["saida"]:
            motivo += " (S)"
        i = next(k for k, l in enumerate(linhas) if l.startswith(CAB[p]))
        j = next(k for k in range(i, len(linhas)) if linhas[k].startswith("|---"))
        ncols = linhas[j].count("|") - 1
        base = [tk, SETOR[tk], br(e.preco), f"**{br(r['central'])} (v2)**", br(r["pc"]), br(r["compra"]), br(r["saida"])]
        if ncols == 9:
            base += [r["vence_rf"] + " (v2, líquida)", motivo]
        else:
            base += [motivo]
        linhas.insert(j + 1, "| " + " | ".join(base) + " |")
    t = "\n".join(linhas)
    t = t.replace("**exceto o Lote 1 (Bancos e Seguridade), recalculado em 04/10 pela v2.0**",
                  "**exceto os Lotes 1 (Bancos e Seguridade) e 3 (Agro e B3), recalculados em 04/10 pela v2.0**")
    t = t.replace("| 3 | Papel e celulose, infraestrutura, agro (7) | `AGRO E B3/Infra_Agro_rev_03-10-2026.pdf` | `…_rev_06-09-2026.pdf` |",
                  "| 3 | Papel e celulose, infraestrutura, agro (7) | `AGRO E B3/Infra_Agro_rev_04-10-2026.pdf` **(v2.0)** | `…_rev_03-10-2026.pdf`, `…_rev_06-09-2026.pdf` |")
    reg = ("| 04/10/2026 | Lote 3 (7) | recalculado pela v2.0 | Demonstrações da CVM (10 anos), margem de meio de ciclo, capex de manutenção "
           "descontado do lucro, arrendamentos na dívida. RADAR: SMTO3 · JUSTA: KEPL3 · CARA: SUZB3, RANI3, SLCE3, B3SA3, KLBN11. Razão (c): a rev. 03/10 usava "
           "números redondos e múltiplos de EBITDA sem capex de manutenção |")
    t = "\n".join(l for l in t.split("\n") if not l.startswith("| 04/10/2026 | Lote 3 (7) |"))
    t = t.rstrip("\n") + "\n" + reg + "\n"
    HALL.write_text(t, encoding="utf-8")
    print("ok")


if __name__ == "__main__":
    main()
