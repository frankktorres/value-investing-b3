"""Relatório da B39 gerado só do `b39/resultado_B39.json`. Uso, de `ferramentas/`:

    python -m b39.relatorio          # grava docs/b39/B39-2026-11.md

Não roda cálculo nem coleta; não escreve nada além do relatório. Nenhum número aqui é ordem de compra ou venda.
"""
from __future__ import annotations

import json
import pathlib
import sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
ENTRADA = AQUI / "resultado_B39.json"
SAIDA = RAIZ / "docs" / "b39" / "B39-2026-11.md"


def pct(x: float | None, casas: int = 2) -> str:
    return "—" if x is None else f"{x * 100:.{casas}f}%".replace(".", ",")


def pp(x: float | None) -> str:
    return "—" if x is None else f"{x * 100:+.2f}".replace(".", ",") + " p.p."


def bi(x: float | None) -> str:
    return "—" if x is None else f"R$ {x / 1e6:,.1f} bi".replace(",", "X").replace(".", ",").replace("X", ".")


def direcao(sens: float | None, base: float | None) -> str:
    if sens is None or base is None:
        return "—"
    d = sens - base
    return "igual" if abs(d) < 5e-5 else (f"sobe {pp(d)}" if d > 0 else f"desce {pp(d)}")


def montar(r: dict) -> str:
    m, e, g, dl = r["mercado"], r["estimativas"], r["gatilho"], r["deltas"]
    dam = m["damodaran"]
    L = [f"# B39 — Ke da Mesa × Ke implícito do mercado (data-base {r['data_base']})", "",
         "Gerado por `cd ferramentas && python -m b39.relatorio` a partir de `ferramentas/b39/resultado_B39.json` "
         f"(gerado em {r['gerado_em']}). Regras escritas antes de rodar: `docs/PRE-REGISTRO-v3.md` §7, emendas 9 e 10; "
         "conferência das fontes: `docs/b39/FONTES-B39.md`. Medição: não muda motor, doutrina nem golden. "
         "Nenhum número aqui é ordem de compra ou venda.", "",
         f"## Veredito do gatilho: **{g['veredito']}**", "",
         f"Mediana dos Δ = **{pp(g['mediana'])}** (limite: |mediana| > 3,00 p.p., nos dois sentidos; {g['n']} de 3 estimativas"
         + (f"; faltou: {', '.join(g['faltam'])}" if g["faltam"] else "") + ")."
         + (f" Sentido: {g['sentido']}." if g.get("sentido") else ""), ""]
    if g["veredito"] == "DISPARA":
        L += ["**Saída (emenda 9): só uma proposta, sem mudar nada.** O nível do Ke/prêmio entra na calibração (B35, com a B46), "
              "como tentativa contada no orçamento de 24 (§0.4), e o prêmio p do DNA §1.1 sai dessa calibração. "
              "⏸ Decisão do Frank, em outro chat.", "",
              f"Proposta (só ordem de grandeza; o número sai da calibração, não daqui): o Ke real da Mesa está {pp(-g['mediana'])} "
              "acima da mediana do que o mercado cobra. A coluna \"prêmio implícito\" abaixo mostra o intervalo do que as três "
              "leituras dão para o prêmio sobre a rf de 10 anos; a calibração (B35 + B46) escolhe dentro dele, com o orçamento do §0.4.", ""]
    elif g["veredito"] == "NÃO DISPARA":
        L += ["**Saída (emenda 9):** o Ke fica, com este motivo; a causa do \"tudo CARA\" se procura em outra camada "
              "(âncoras, normalização; DNA, causas b–d).", ""]
    else:
        L += ["**Saída (emenda 9):** menos de 2 estimativas; nada muda.", ""]

    L += ["## Mercado (uma data só)", "",
          "| Insumo | Valor | Fonte |", "|---|---|---|",
          f"| rf real | {pct(m['rf_real'])} | {m['rf_titulo']} — {m['rf_fonte']} (nota A) |",
          f"| π | {pct(m['pi'], 4)} | {m['pi_fonte']} (nota A) |",
          f"| s (spread de default, Brasil {dam['rating_moodys']}) | {pct(dam['s_adj_default_spread'])} | Damodaran `ctryprem`, "
          f"atualizada em {dam['atualizado']} (nota B) |",
          f"| ERP total do Brasil | {pct(dam['erp_total'])} | idem (CRP {pct(dam['crp'])} + maduro {pct(dam['erp_maduro_implicito'])}) |",
          f"| Carteira do Ibovespa | {m['ibov']['n']} ações | {m['ibov']['fonte']}, consultada em {m['ibov']['data_da_carteira_b3']} (nota A) |",
          f"| IPCA (lucro real) | até {r['mes_ipca']} | SGS 433 (nota A) |", "",
          "## As três estimativas (Ke real)", "",
          "| | Estimativa | Ke implícito | Ke da Mesa | Δ | Prêmio implícito (Ke − rf) | Prêmio da Mesa |", "|---|---|---|---|---|---|---|"]
    for k in ("i", "ii", "iii"):
        x = e[k]
        pi_ = None if x["ke_real"] is None else x["ke_real"] - m["rf_real"]
        pm = None if x["ke_mesa_real"] is None else x["ke_mesa_real"] - m["rf_real"]
        L.append(f"| ({k}) | {x['nome']} | {pct(x['ke_real'])} | {pct(x['ke_mesa_real'])} | {pp(dl[k])} | {pp(pi_)} | {pp(pm)} |")
    ii = e["ii"]
    L += ["", f"Ke da Mesa: (i) rf + 5 p.p.; (ii) e (iii) rf + o prêmio do índice ponderado pelo valor de mercado (5 p.p. nas "
          "financeiras; 5 × [1 + 0,66 × D/E] nas demais, D/E a mercado). (ii) pondera só as que entraram no E10; (iii), todas.", "",
          f"(ii): {ii['n']} de {ii['n_indice']} companhias do índice com E10 (mínimo de 5 exercícios); cobertura "
          f"{pct(ii['cobertura_vm'], 1)} do valor de mercado ({bi(ii['soma_vm'])} de {bi(ii['vm_total'])}) e "
          f"{pct(ii['cobertura_peso_ibov'], 1)} do peso no Ibovespa; Σ E10 = {bi(ii['soma_e10'])}.", "",
          "## Sensibilidades (só relatadas; não mudam o gatilho)", "",
          "| Estimativa | Variante | Ke real | Direção vs. a base |", "|---|---|---|---|"]
    nomes = {"g_real_0%": "g real 0%", "g_real_2%": "g real 2%", "roe_ltm": "ROE LTM no lugar da mediana",
             "sem_petr_vale": "sem PETR3/PETR4 e VALE3", "lucro_ltm": "lucro LTM no lugar do E10",
             "gordon_g_0%": "Gordon, payout mediano, g real 0%", "gordon_g_1%": "Gordon, payout mediano, g real 1%",
             "gordon_g_2%": "Gordon, payout mediano, g real 2%", "sem_tirar_s": "sem tirar s (rf real + ERP total)"}
    for k in ("i", "ii", "iii"):
        for s, v in e[k]["sens"].items():
            L.append(f"| ({k}) | {nomes.get(s, s)} | {pct(v)} | {direcao(v, e[k]['ke_real'])} |")
    if ii.get("payout_mediano") is not None:
        L += ["", f"Payout mediano do agregado (dividendos/JCP pagos na DFC ÷ lucro, 2016–2025): {pct(ii['payout_mediano'], 1)}."]

    L += ["", "## (i) Bancos", "", "| Banco | Exercícios | ROE mediano | P/VP | Ke real | Último balanço |", "|---|---|---|---|---|---|"]
    for b in r["bancos"]:
        L.append(f"| {b['ticker']} | {b['n_roes']} | {pct(b['roe_normalizado'], 1)} | "
                 f"{'—' if b['pvp'] is None else f'{b['pvp']:.2f}'.replace('.', ',')} | "
                 f"{pct(b.get('ke_real')) if 'ke_real' in b else 'fora: ' + b.get('fora', '')} | {b['dt_refer_ultimo'] or '—'} |")

    fora = [x for x in r["empresas"] if x.get("no_indice") and (x.get("e10") is None or not x.get("vm"))]
    L += ["", "## (ii) Fora do agregado (declarado)", ""]
    if fora:
        L += ["| Companhia | Tickers | Peso no Ibovespa | Motivo |", "|---|---|---|---|"]
        for x in sorted(fora, key=lambda y: -y["part"]):
            mot = x.get("erro") or ("sem valor de mercado: " + x.get("nota_vm", "") if not x.get("vm")
                                    else f"{x.get('n_exercicios_e10', 0)} exercícios com lucro (mínimo 5)")
            L.append(f"| {x.get('nome') or x['cnpj']} | {', '.join(x['tickers'])} | {pct(x['part'], 2)} | {mot} |")
    else:
        L.append("Nenhuma.")
    av = [(x["tickers"], a) for x in r["empresas"] for a in x.get("avisos", [])]
    av += [(x["tickers"], x["nota_vm"]) for x in r["empresas"] if x.get("nota_vm")]
    if av:
        L += ["", "Avisos de dado:", ""] + [f"- {', '.join(t)}: {a}" for t, a in av]

    L += ["", "## Simplificações e vieses declarados (emendas 9 e 10)", "",
          "- t = 34% para todas no Hamada (o motor usa a alíquota perpétua de cada uma): o prêmio sai no mínimo e o Ke da Mesa "
          "erra para baixo, o lado de **não** disparar quando o Ke da Mesa é alto demais.",
          "- D = empréstimos e financiamentos (CP + LP) + arrendamento lançado fora deles, do último ITR. Os \"outros passivos "
          "financeiros\" da ficha de cada empresa não existem para o índice inteiro e ficam em zero: o prêmio sai mais baixo, o "
          "mesmo lado do item anterior.",
          "- (ii) Sobrevivência: só os componentes de hoje. Holdings e controladas listadas (ITSA4/ITUB4, BRAP4/VALE3, GOAU4/GGBR4) "
          "entram as duas, como no próprio índice: lucro e valor de mercado contados dos dois lados.",
          "- (ii) E10 ÷ P é o EPV reverso da Mesa, não um resultado de Shiller (emenda 10): sem crescimento, subestima o Ke quando "
          "o crescimento cria valor. As linhas de Gordon dão o tamanho.",
          "- (ii) Lucro real: cada exercício levado a R$ do último IPCA publicado em T pelo índice médio dos 12 meses do exercício "
          "(`inflacao.deflator_periodo`).",
          "- (iii) Tirar s de uma NTN-B levada a nominal é extensão da Mesa: o Damodaran não trata título indexado de governo com "
          "risco de default (emenda 10).",
          "- Valor de mercado = ações ON e PN do último ITR (sem tesouraria) × o preço de fechamento de cada classe em T (COTAHIST); "
          "uma classe sem pregão usa o preço da outra (avisado acima).", ""]
    return "\n".join(L)


def main() -> int:
    r = json.loads(ENTRADA.read_text(encoding="utf-8"))
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(montar(r), encoding="utf-8")
    print(f"gravado {SAIDA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
