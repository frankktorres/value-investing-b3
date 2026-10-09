"""Atualiza o 03-hall-de-acoes.md com o Lote 6 recalculado (números do motor). Idempotente."""
import pathlib
import re
import sys

from historico_arquivos import gravar_texto
from lote1_bancos import MK
from lote6_quimica import ACO, CLORO, EGIE, EGIE_DADOS, EMPRESAS
from motor_financeiras import avaliar as avaliar_fin
from motor_nao_financeiras import avaliar
from gerar_pdf_lote6 import egie_extras

sys.stdout.reconfigure(encoding="utf-8")
HALL = pathlib.Path(__file__).parent.parent / "03-hall-de-acoes.md"
SETOR = {"GGBR4": "Siderurgia", "UNIP6": "Química", "LEVE3": "Autopeças", "EGIE3": "Geração"}
FORA_DO_HALL = {"UNIP6"}   # saíram do hall em 05/10 (falham 2 dos filtros 1–4, doutrina §2) — não reinserir
CAB = {"BARATA": "### BARATA", "RADAR": "### RADAR", "JUSTA": "### JUSTA", "CARA": "### CARA", "NÃO CONCLUSIVO": "### NÃO CONCLUSIVO"}


def pct_ou_nd(x):
    """ROIC pode ser None (sem capital investido positivo) — não derruba o hall."""
    return "n.d." if x is None else br(100 * x, 1) + "%"


def br(x, c=2):
    return f"{x:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def motivo(tk, r):
    ke = f"Ke implícito {br(100 * r['ke_implicito'], 1) + '%' if r['ke_implicito'] else 'n.d.'}"
    if tk == "EGIE3":
        tir = (1 + r["ke_implicito"]) / (1 + MK.pi) - 1 if r["ke_implicito"] else None
        return (f"**recalculado v2.2 (05/10)**; TIR real {br(100 * tir, 1) + '%' if tir else 'n.d.'}; ROE lp {br(100 * EGIE.roe_lp, 1)}% × Ke nominal "
                f"{br(100 * MK.ke_nom, 1)}%; método de regulado (P/VP justificado + DDM); patrimônio + follow-on de R$ 8,36 bi (Jirau 40%) ao Ke, "
                f"1.416 mi de ações; ROE lp do negócio existente {br(100 * EGIE_DADOS['roe_old_lp'], 1)}% (sem UBP de 2024); **no fio:** vira CARA com ROE "
                f"< {br(100 * VIRADA['roe_virada'], 1)}% (média 2017–25 → {br(VIRADA['central_media'])}; ROE 12m → {br(VIRADA['central_roe_atual'])}); "
                "trava JUSTA passa só com re-rating")
    m = f"**recalculado v2.2 (05/10)**; {ke}; ROIC {pct_ou_nd(r['roic'])} contábil / {pct_ou_nd(r['roic_reposicao'])} a reposição × WACC {br(100 * r['wacc'], 1)}%; confiança {r['confianca']}"
    if tk == "GGBR4":
        m += (f"; aço de meio de ciclo (índice BLS × câmbio, R$ de hoje; 12m {br(ACO['ltm_real'], 0)} em R$ de hoje vs meio 100); impairment normalizado; "
              f"EPV {br(r['ancoras']['EPV de meio de ciclo'])} abaixo do livro {br(r['reprod'])} — ROIC < WACC, o livro não é piso")
    if tk == "UNIP6":
        ex = {k.split(" ")[0]: br(v) for k, v in r["ancoras"].items()}
        m += (f"; cesta soda/PVC de meio de ciclo (12m {br(CLORO['ltm_real'], 0)} vs meio 100, janela 2017–25); EPV {ex['EPV']} · DCF {ex['DCF']} · reprodução "
              f"{ex['Valor']} — lucro de meio de ciclo × livro distribuído discordam {br(r['dispersao'])}× (no fio do limite de 3×); **defeito estrutural:** dividendo não "
              "coberto por caixa (2025: proventos 2,7× o lucro; dívida bruta 1,4 → 3,7 bi; zero provento em 2026); 2 filtros falham (2 e 4) → "
              "**candidata a sair do hall (aguarda Frank)**")
    if tk == "LEVE3":
        m += ("; única do lote com ROIC > WACC; **T** (trava falha por pouco: Bogle sem re-rating 2,3 p.p. abaixo do Ke); exceção de 1ª parcela "
              "bloqueada pelo §7 (Mahle citada em ROE inflado — decisão do Frank); dívida financiou parte do provento")
    return m


def main():
    global VIRADA
    VIRADA = egie_extras(EGIE, avaliar_fin(EGIE, MK))
    t = HALL.read_text(encoding="utf-8")
    linhas = [l for l in t.split("\n") if not re.match(r"^\| (%s) \| (?!R\$)" % "|".join(SETOR), l)]
    res = {e.ticker: (e.preco, avaliar(e, MK)) for e in EMPRESAS}
    res["EGIE3"] = (EGIE.preco, avaliar_fin(EGIE, MK))
    for tk in sorted(SETOR, key=lambda k: -res[k][1]["pc"]):
        if tk in FORA_DO_HALL:
            continue
        preco, r = res[tk]
        i = next(k for k, l in enumerate(linhas) if l.startswith(CAB[r["palavra"]]))
        j = next(k for k in range(i, len(linhas)) if linhas[k].startswith("|---"))
        ncols = linhas[j].count("|") - 1
        nc = r["palavra"] == "NÃO CONCLUSIVO"
        base = [tk, SETOR[tk], br(preco), f"**{br(r['central'])} (v2)**", br(r["pc"]),
                "n.a." if nc else br(r["compra"]), "n.a." if nc else br(r["saida"])]
        base += ([r["vence_rf"] + " (v2, líquida)", motivo(tk, r)] if ncols == 9 else [motivo(tk, r)])
        linhas.insert(j + 1, "| " + " | ".join(base) + " |")
    t = "\n".join(linhas)
    t = t.replace("3 (Agro e B3) e 5 (Petróleo e Gás), recalculados em 04–05/10 pela v2.0/2.1**",
                  "3 (Agro e B3), 5 (Petróleo e Gás) e 6 (Química e Metalurgia), recalculados em 04–05/10 pela v2.0/2.1**")
    t = t.replace("**Candidatas a sair no recálculo** (2 falhas prováveis): **UNIP6** (ROIC 7,7% < WACC; provento não coberto),",
                  "**Candidatas a sair no recálculo** (2 falhas prováveis): **UNIP6** (recalculada 05/10: falha balanço e provento — aguarda Frank),")
    t = t.replace("| 6 | Química e metalurgia: LEVE3, EGIE3, UNIP6, GGBR4 (4) | `QUÍMICA E METALÚRGIA/Química_Metalúrgia_rev_03-10-2026.pdf` | `…_rev_07-09-2026.pdf` |",
                  "| 6 | Química e metalurgia: LEVE3, EGIE3, UNIP6, GGBR4 (4) | `QUÍMICA E METALÚRGIA/Quimica_Metalurgia_rev_05-10-2026.pdf` **(v2.2)** | "
                  "`Química_Metalúrgia_rev_03-10-2026.pdf`, `…_rev_07-09-2026.pdf` |")
    pal = {p: [tk for tk, (_, r) in res.items() if r["palavra"] == p] for p in ("RADAR", "JUSTA", "CARA", "NÃO CONCLUSIVO")}
    reg = ("| 05/10/2026 | Lote 6 (4) | recalculado pela v2.2 | Preço de aço e de cloro-soda/PVC de meio de ciclo declarado (índices BLS × câmbio em R$ "
           "de hoje, média do ciclo na janela da margem: aço 2016–25, cloro-soda/PVC 2017–25); cíclicas por EPV/DCF/reprodução, LEVE3 por DCF/EPV/Owner Earnings, EGIE3 pelo método de regulado com o follow-on de "
           "Jirau. " + " · ".join(f"{p}: {', '.join(v)}" for p, v in pal.items() if v)
           + ". GGBR4 RADAR → CARA (ROIC < WACC: o livro não é piso); LEVE3 e EGIE3 CARA → JUSTA; UNIP6 sem palavra, defeito estrutural mantido. "
             "Razão (c): a rev. 03/10 reescalava o central de 07/09 por Gordon, sem preço de commodity declarado. Coletor corrigido (D&A sem custo de "
             "transação; impairment pela conta-raiz): Lotes 2, 3 e 5 sem mudança de palavra (SUZB3 37,94 → 37,12) |")
    t = "\n".join(l for l in t.split("\n") if not l.startswith("| 05/10/2026 | Lote 6 (4) |"))
    t = t.rstrip("\n") + "\n" + reg + "\n"
    gravar_texto(HALL, t, "hall lote 6")      # AUD-84: o 03 anterior vai para _historico/
    print("ok", {tk: (r["palavra"], round(r["central"], 2)) for tk, (_, r) in res.items()})


if __name__ == "__main__":
    main()
