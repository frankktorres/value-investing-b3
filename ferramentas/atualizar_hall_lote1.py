"""Atualiza o 03-hall-de-acoes.md com o Lote 1 recalculado (números vindos do motor). Idempotente."""
import pathlib
import re
import sys

from lote1_bancos import EMPRESAS, MK
from motor_financeiras import avaliar

sys.stdout.reconfigure(encoding="utf-8")
HALL = pathlib.Path(__file__).parent.parent / "03-hall-de-acoes.md"
SETOR = {"ITUB4": "Banco", "BBDC4": "Banco", "BBAS3": "Banco estatal", "ABCB4": "Banco de atacado", "BRSR6": "Banco estatal RS",
         "BRBI11": "Banco de investimento", "BBSE3": "Seguridade", "CXSE3": "Seguridade", "PSSA3": "Seguradora"}
FORA_DO_HALL = {"BBAS3", "BRSR6"}   # saíram do hall em 05/10 (falham 2 dos filtros 1–4, doutrina §2) — não reinserir
NOTA = {"BBAS3": "falha filtros 1 (ROE < Ke) e 3 (controlador) → **sai do hall pela v2.0 §2** (aguarda confirmação)",
        "BRSR6": "defeito estrutural (folha do RS, V3); falha filtros 1 e 3 → **sai do hall pela v2.0 §2** (aguarda confirmação)"}


def br(x, c=2):
    return f"{x:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def main():
    t = HALL.read_text(encoding="utf-8")
    res = {e.ticker: (e, avaliar(e, MK)) for e in EMPRESAS}
    linhas = t.split("\n")
    # remove as linhas antigas dos 9 tickers do hall (SANB11 fica em "Fora do hall")
    linhas = [l for l in linhas if not re.match(r"^\| (%s) \| (?!R\$)" % "|".join(SETOR), l)]
    t = "\n".join(linhas)
    novas = []
    for tk in sorted(SETOR, key=lambda k: res[k][1]["pc"]):
        if tk in FORA_DO_HALL:
            continue
        e, r = res[tk]
        s = " (S)" if e.preco > r["saida"] else ""
        motivo = (f"**recalculado v2.0 (04/10)**{s}; Ke implícito {br(100 * r['ke_implicito'], 1)}% vs Ke da casa {br(100 * MK.ke_nom, 1)}%; "
                  f"retorno de investimento {br(100 * r['ret_investimento'], 1)}%; vence RF: {r['vence_rf']}")
        if tk in NOTA:
            motivo += "; " + NOTA[tk]
        novas.append(f"| {tk} | {SETOR[tk]} | {br(e.preco)} | **{br(r['central'])} (v2)** | {br(r['pc'])} | {br(r['compra'])} | {br(r['saida'])} | {motivo} |")
    cab = "| Ticker | Setor | Preço 02/10 | Central (v1) | P/C | Compra 0,70× | Saída 1,30× | Pendências v2 / motivo |\n|---|---|---|---|---|---|---|---|"
    assert cab in t
    t = t.replace(cab, cab.replace("Central (v1)", "Central") + "\n" + "\n".join(novas), 1)

    e, r = res["SANB11"]
    t = re.sub(r"\| SANB11 \| R\$ 28,09 · central [^|]+\|",
               f"| SANB11 | R$ 28,09 · central {br(r['central'])} pelo fundamental (v2, P/C {br(r['pc'])}); permuta implícita R$ 28,11 |", t)
    t = t.replace("Os valores centrais abaixo ainda são os da rev. 03/10, feita pela doutrina v1.0.",
                  "Os valores centrais abaixo ainda são os da rev. 03/10, feita pela doutrina v1.0 — **exceto o Lote 1 (Bancos e Seguridade), "
                  "recalculado em 04/10 pela v2.0** (`Banco_Seguridade_rev_04-10-2026.pdf`, contas em `ferramentas/`).")
    t = t.replace("| 1 | Bancos e seguridade (10) | `BANCOS E SEGURIDADE/Banco_Seguridade_rev_03-10-2026.pdf` | `…_rev_07-09-2026.pdf` |",
                  "| 1 | Bancos e seguridade (10) | `BANCOS E SEGURIDADE/Banco_Seguridade_rev_04-10-2026.pdf` **(v2.0)** | `…_rev_03-10-2026.pdf`, `…_rev_07-09-2026.pdf` |")
    reg = (f"| 04/10/2026 | Lote 1 (10) | recalculado pela v2.0 | Ke nominal {br(100 * MK.ke_nom, 2)}% (IPCA+ 2050 sem cupom 7,06% + 5 p.p.; inflação implícita 6,46%). "
           "Todos CARA: P/C de " + br(min(r['pc'] for _, r in res.values())) + "× a " + br(max(r['pc'] for _, r in res.values())) +
           "×. Razão (c): a rev. 03/10 calculava o justo a Ke de mercado 14% ou na coluna real e supunha IPCA de 4%. "
           "BBAS3 e BRSR6 falham 2 filtros (1 e 3) |")
    if "| 04/10/2026 | Lote 1 (10) |" not in t:
        t = t.rstrip("\n") + "\n" + reg + "\n"
    HALL.write_text(t, encoding="utf-8")
    print("\n".join(novas))


if __name__ == "__main__":
    main()
