"""Atualiza o 03-hall-de-acoes.md com o Lote 4 recalculado (números do motor), o ranking Greenblatt de todo o hall e a seção 'vencem a RF'
com todos os lotes v2. Idempotente."""
import pathlib
import re
import sys

import lote1_bancos
import lote2_energia
import lote3_agro
import lote5_petroleo
import lote6_quimica
from gerar_pdf_lote4 import FORA_DO_HALL, ranking_hall
from lote1_bancos import MK
from lote4_saude_telecom import EMPRESAS, ITSA4, ITSA_ROE_LP, WEG_G1, sotp_partes
from motor_financeiras import avaliar as avaliar_fin
from motor_nao_financeiras import avaliar

sys.stdout.reconfigure(encoding="utf-8")
HALL = pathlib.Path(__file__).parent.parent / "03-hall-de-acoes.md"
SETOR = {"TIMS3": "Telecom", "VIVT3": "Telecom", "ITSA4": "Holding", "FLRY3": "Saúde", "HYPE3": "Farmacêutica", "ABEV3": "Bebidas",
         "WEGE3": "Bens de capital"}
CAB = {"BARATA": "### BARATA", "RADAR": "### RADAR", "JUSTA": "### JUSTA", "CARA": "### CARA", "NÃO CONCLUSIVO": "### NÃO CONCLUSIVO"}
FORA = FORA_DO_HALL | {"BBAS3", "BRSR6", "SANB11"}


def br(x, c=2):
    return f"{x:,.{c}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def motivo(tk, r):
    ke = f"Ke implícito {br(100 * r['ke_implicito'], 1) + '%' if r['ke_implicito'] else 'n.d.'}"
    if tk == "ITSA4":
        s = sotp_partes(MK)
        tir = (1 + r["ke_implicito"]) / (1 + MK.pi) - 1 if r["ke_implicito"] else None
        return (f"**recalculado v2.1 (05/10)**; holding: SOTP {br(r['ancoras']['SOTP'])} (Itaú 37,5% pelo FRE ao central do Lote 1, R$ {br(s['itau_ps'])} "
                f"por ITUB4; demais a valor contábil; G&A capitalizado) · DDM {br(r['ancoras']['DDM 2 estágios'])}; ROE lp {br(100 * ITSA_ROE_LP, 1)}% × Ke "
                f"{br(100 * MK.ke_nom, 1)}%; retorno real implícito {br(100 * tir, 1) + '%' if tir else 'n.d.'} — abaixo do Tesouro; **na carteira, acima da "
                "saída (S)**")
    m = f"**recalculado v2.1 (05/10)**; {ke}; ROIC {br(100 * r['roic'], 1)}% × WACC {br(100 * r['wacc'], 1)}%; confiança {r['confianca']}"
    extra = {"TIMS3": "; margem EBIT 2019–25 (IFRS 16) e arrendamento na dívida; capex de rede = manutenção; com a margem dos 12m seguiria CARA",
             "VIVT3": "; margem 2019–25 estável; arrendamento na dívida; yield recorrente sem a redução de capital; política de payout de 2027 não encontrada",
             "FLRY3": "; perímetro com Pardini (receita 2024–12m); provento no limite do FCFE, dividendo em 3 parcelas até 2027",
             "HYPE3": "; a menos cara do lote; alíquota no piso de 15% (a 34% cai mais); JCP pago 15–21 meses depois (valor presente)",
             "ABEV3": "; cria valor (ROIC > WACC); alíquota pós-subvenção 21%; Imposto Seletivo fora do número",
             "WEGE3": f"; melhor negócio do hall; DCF 2 estágios (g real {br(100 * WEG_G1, 1)}% por 10 anos, ROE × retenção); o preço exige "
                      f"{br(100 * r['g_implicito'], 0) if r['g_implicito'] else 'n.d.'}% real por 10 anos"}
    return m + extra.get(tk, "") + (" (S)" if r["preco_"] > r["saida"] else "")


def todos_v2():
    """palavra, vence RF e re-rating de cada ticker do hall, de todos os lotes recalculados."""
    out = {}
    for e in lote1_bancos.EMPRESAS + lote2_energia.EMPRESAS + [lote6_quimica.EGIE, ITSA4]:
        out[e.ticker] = avaliar_fin(e, MK)
    for e in lote3_agro.EMPRESAS + lote5_petroleo.EMPRESAS + lote6_quimica.EMPRESAS + EMPRESAS:
        out[e.ticker] = avaliar(e, MK)
    return {tk: r for tk, r in out.items() if tk not in FORA}


def main():
    t = HALL.read_text(encoding="utf-8")
    linhas = [l for l in t.split("\n") if not re.match(r"^\| (%s) \| (?!R\$)" % "|".join(SETOR), l)]
    res = {e.ticker: avaliar(e, MK) for e in EMPRESAS}
    res["ITSA4"] = avaliar_fin(ITSA4, MK)
    for e in EMPRESAS + [ITSA4]:
        res[e.ticker]["preco_"] = e.preco
    for tk in sorted(SETOR, key=lambda k: -res[k]["pc"]):
        r = res[tk]
        i = next(k for k, l in enumerate(linhas) if l.startswith(CAB[r["palavra"]]))
        j = next(k for k in range(i, len(linhas)) if linhas[k].startswith("|---"))
        ncols = linhas[j].count("|") - 1
        base = [tk, SETOR[tk], br(r["preco_"]), f"**{br(r['central'])} (v2)**", br(r["pc"]), br(r["compra"]), br(r["saida"])]
        base += ([r["vence_rf"] + " (v2, líquida)", motivo(tk, r)] if ncols == 9 else [motivo(tk, r)])
        linhas.insert(j + 1, "| " + " | ".join(base) + " |")
    t = "\n".join(linhas)

    # cabeçalho e alerta de método: os 6 lotes estão recalculados
    t = re.sub(r"\*Atualizado em [^\n]*\*", "*Atualizado em 05/10/2026 · 41 empresas analisadas (36 no hall + 5 fora) · centrais recalculados em 04–05/10/2026 "
               "pela doutrina v2.0/2.1 (6 lotes) · cotações de fechamento de 02/10/2026 (véspera do 1º turno) — atualizar antes de decidir*", t, count=1)
    novo_alerta = ("> **Método (05/10/2026): os 6 lotes estão recalculados pela doutrina v2.0/2.1** — contas em `ferramentas/` (demonstrações da CVM, "
                   "fonte A), Ke nominal 19,30% (Tesouro IPCA+ 2050 sem cupom 7,06% + 5 p.p.; inflação implícita ANBIMA 6,46%), preços de fechamento "
                   "de 02/10. Cada central é reconstruível na ficha do PDF do lote (tabela âncora → mediana). A palavra segue a régua contínua v2.0 "
                   "(≤ 0,70 BARATA · ≤ 0,90 RADAR · ≤ 1,10 JUSTA · > 1,10 CARA), com compra = 0,70× e saída = 1,30× o central. **Os preços são de 02/10, "
                   "véspera do 1º turno — conferir a cotação antes de qualquer decisão.**")
    t = re.sub(r"> \*\*⚠ ALERTA DE MÉTODO.*?\n\n> \*\*Base de Ke a usar no recálculo:\*\*[^\n]*\n", novo_alerta + "\n", t, count=1, flags=re.S)

    # seção 2: quem vence a RF (v2, líquida, ponto médio)
    tv = todos_v2()
    sim = sorted(tk for tk, r in tv.items() if r["vence_rf"] == "Sim")
    emp = sorted(tk for tk, r in tv.items() if r["vence_rf"] == "Empate")
    rr = sorted(tk for tk, r in tv.items() if r["vence_rf"] in ("Sim", "Empate") and r["so_com_rerating"])
    sec2 = ("## 2. As que vencem a renda fixa (v2, líquida de IR, ponto médio do retorno esperado de 10 anos)\n\n"
            f"RF real líquida de referência: {br(100 * MK.rf_liq_real, 2)}% a.a. (Sim ≥ +3 p.p.; Empate ≥ +1,5 p.p.).\n\n"
            f"- **Sim:** {', '.join(sim) or 'nenhuma'}\n- **Empate:** {', '.join(emp) or 'nenhuma'}\n"
            f"- **Só com re-rating do múltiplo** (sem ele não vencem): {', '.join(rr) or 'nenhuma'}\n\n"
            "Vencer a RF não autoriza compra: a compra depende só de preço ≤ 0,70 × central (§9). Nenhuma das listadas está nesse preço.\n")
    t = re.sub(r"## 2\. As que vencem a renda fixa.*?(?=\n---)", sec2, t, count=1, flags=re.S)

    # seção 3: ranking Greenblatt de todo o hall
    lin = ranking_hall()
    tab = ["| Posição | Ticker | EY | Rank EY | ROC | Rank ROC | Soma |", "|---|---|---|---|---|---|---|"]
    tab += [f"| {z['pos']}º | {z['ticker']} | {br(100 * z['ey'], 1)}% | {z['rey']} | {br(100 * z['roc'], 1)}% | {z['rroc']} | {z['soma']} |" for z in lin]
    sec3 = ("## 3. Ranking Greenblatt (Fórmula Mágica) — não financeiras\n\n"
            f"*Preenchido em 05/10/2026 no recálculo do Lote 4, com todas as não financeiras do hall ({len(lin)}; Lotes 3–6): EY = EBIT 12m (jun/26) ÷ EV "
            "(valor de mercado a 02/10 + dívida líquida com arrendamento); ROC = EBIT ÷ (capital de giro operacional + imobilizado líquido) [CVM]. Bancos, "
            "seguradoras, holdings e concessões ficam fora (N/A por perfil). O ranking ordena; quem decide a compra é o preço ÷ central.*\n\n"
            + "\n".join(tab) + "\n")
    t = re.sub(r"## 3\. Ranking Greenblatt.*?(?=\n---)", sec3, t, count=1, flags=re.S)

    t = t.replace("| 4 | Saúde, telecom, blue chips (7) | `SAÚDE, TELECOM E BLUECHIPS/Saúde_Telecom_Bluechips_rev_03-10-2026.pdf` | `…_rev_06-09-2026.pdf` |",
                  "| 4 | Saúde, telecom, blue chips (7) | `SAÚDE, TELECOM E BLUECHIPS/Saude_Telecom_Bluechips_rev_05-10-2026.pdf` **(v2.1)** | "
                  "`Saúde_Telecom_Bluechips_rev_03-10-2026.pdf`, `…_rev_06-09-2026.pdf` |")
    t = t.replace("*As versões de 06–07/09 trazem quadro clássico mais completo (Graham, Bazin, EPV, Piotroski) que as de 03/10 — úteis como insumo, nunca como valor.*",
                  "*As versões de 06–07/09 e 03/10 ficam como histórico de fatos (eventos, proventos declarados, gatilhos) — nunca como valor.*")
    reg = ("| 05/10/2026 | Lote 4 (7) | recalculado pela v2.1 | Todos CARA: "
           + ", ".join(f"{tk} {br(res[tk]['central'])} ({br(res[tk]['pc'])})" for tk in sorted(res, key=lambda k: res[k]["pc"]))
           + ". TIMS3 e VIVT3 RADAR → CARA; ITSA4, FLRY3 e HYPE3 JUSTA → CARA; ABEV3 e WEGE3 seguem CARA. IFRS 16: margem 2019–25 e arrendamento "
             "na dívida (teles e FLRY3); Owner Earnings com o aluguel pago; capex de rede = manutenção; WEGE3 por DCF em 2 estágios (g real ROE × "
             "retenção); ITSA4 por SOTP (Itaú ao central do Lote 1, participação pelo FRE) + DDM. Todas seguem no hall (TIMS3, VIVT3, FLRY3, HYPE3 e "
             "ITSA4 falham só o filtro 1). Razão (c): a rev. 03/10 era 'anterior × fator de Ke' e misturava g nominal com Ke real (WEGE3). Ranking "
             "Greenblatt do hall preenchido (§3) |")
    t = "\n".join(l for l in t.split("\n") if not l.startswith("| 05/10/2026 | Lote 4 (7) |"))
    t = t.rstrip("\n") + "\n" + reg + "\n"
    HALL.write_text(t, encoding="utf-8")
    print("ok", {tk: (r["palavra"], round(r["central"], 2), round(r["pc"], 2)) for tk, r in res.items()})
    print("RF sim", sim, "empate", emp, "rerating", rr)


if __name__ == "__main__":
    main()
