"""Lote 2 — Energia elétrica e saneamento · data-base 02/10/2026 (fechamento; preços do PDF rev. 03/10) · doutrina v2.2.

Regulados: nas transmissoras a contabilidade de concessão (ICPC 01/IFRS 15) põe o investimento em ativo de contrato
dentro do FCO — "FCO − capex" não funciona; nas distribuidoras e no saneamento o investimento está no FCI (AUD-20:
SBSP3 6.02.01 −13,7 bi na DFP 2025). Sem base regulatória e WACC regulatório com fonte A/B, o DCF regulatório é o
P/VP justificado como PROXY declarado, onde quer que o investimento esteja (doutrina v2.5 §11.2; `REGULADOS_DFC`).
Método de regulado (doutrina §11.2, utility):
  · DCF regulatório = P/VP justificado: patrimônio (proxy da base regulatória) × (ROE − g) ÷ (Ke − g)
  · DDM em 2 estágios (ROE do início converge ao de longo prazo em 5 anos)
  · TIR real implícita = Ke implícito no preço, em termos reais — comparada à rf (piso) e ao Ke real (sempre).
VPA/LPA/ROE/proventos: StatusInvest (base pós-bonificação, coerente com o preço). Alavancagem e cobertura: CVM (12m até jun/26).
"""
from ltm import ltm_de
import json
import pathlib
import statistics as st
import sys

from lote1_bancos import MK
from juros import juros_do_periodo
from motor_financeiras import Financeira, avaliar, interp

AQUI = pathlib.Path(__file__).parent
CVM = json.loads((AQUI / "dados" / "cvm_series.json").read_text(encoding="utf-8"))
SI = json.loads(sorted((AQUI / "dados").glob("series_*.json"))[-1].read_text(encoding="utf-8"))
QUAL = lambda moat, gestao, controlador, ciclo, fisher: dict(moat=moat, gestao=gestao, controlador=controlador, ciclo=ciclo, fisher=fisher)


def roe_lp(tk):
    r = SI[tk]["indicadores"]["roe"]["anos"]
    return st.median(r[str(a)] for a in range(2016, 2026) if r.get(str(a)) is not None) / 100


# lacunas da StatusInvest completadas pela CVM (DFC, dividendos e JCP pagos ÷ ações — base caixa, não data-com)
DPA_CVM = {"ISAE4": {"2024": 1.88}}


def dpas(tk):
    d = dict(SI[tk]["dpa_por_ano_datacom"])
    d.update(DPA_CVM.get(tk, {}))
    return d


def dpa5(tk):
    d = dpas(tk)
    return sum(d.get(str(a), 0) for a in range(2021, 2026)) / 5


def jcp(tk):
    s = SI[tk]
    tot = sum(s["dpa_por_ano_datacom"].get(a, 0) for a in ("2024", "2025"))
    return sum(s["jcp_por_ano_datacom"].get(a, 0) for a in ("2024", "2025")) / tot if tot else 0.0


def anos_pagos(tk):
    d = dpas(tk)
    return sum(1 for a in range(2016, 2026) if d.get(str(a), 0) > 0)


def pl_hist(tk):
    p = SI[tk]["indicadores"]["p_l"]["anos"]
    xs = [p[str(a)] for a in range(2016, 2026) if p.get(str(a)) and 0 < p[str(a)] < 40]
    return st.median(xs) if xs else None


def alavancagem(tk):
    l = ltm_de(CVM[tk])
    bruta = (l.get("emprest_cp") or 0) + (l.get("emprest_lp") or 0) + (l.get("arrendamento") or 0)
    dl = bruta - (l.get("caixa") or 0) - (l.get("aplic_cp") or 0)
    ebitda = l["ebit"] + (l.get("da") or 0)
    juros, _ = juros_do_periodo(l)
    if juros <= 1e4 and (l.get("res_fin") or 0) < 0:      # sem a linha de despesa (SBSP3): usa o resultado financeiro líquido
        juros = -l["res_fin"]
    cob = l["ebit"] / juros if juros > 1e4 else None
    return dl / ebitda if ebitda > 0 else None, cob, dl


def solidez(tk):
    dle, cob, _ = alavancagem(tk)
    a = interp(-(dle or 0), [(-5, 1), (-4, 3), (-3, 5), (-2, 7), (-1, 9), (0, 10)])
    c = interp(cob, [(1, 1), (2, 3), (3, 5), (5, 8), (8, 10)]) if cob else 5
    return (a + c) / 2


def ind(tk, k):
    return SI[tk]["indicadores"][k]["atual"]


# Doutrina §11.2 — emissão de ações depois do balanço: patrimônio + caixa captado, o dinheiro novo rendendo o Ke (VPL zero), igual
# ao EGIE3 (lote6.egie). AUD-04 (08/10/2026): o VPA da StatusInvest dividia o PL de 30/06 (sem o dinheiro) pelas ações de depois
# da oferta. Ações novas = valor ÷ preço da oferta; somadas às da CVM dão as 703,3 mi que a StatusInvest já usava.
FOLLOW_ON = {"ISAE4": dict(valor=1_200_000, preco=27.0, data="jul/2026",       # R$ mil; R$ 1,2 bi a R$ 27 [fatos_lote2; PDF 03/10]
                           fonte="follow-on de jul/2026 (fatos_lote2.json, PDF rev. 03/10); valor bruto — custo da oferta a conferir no RI")}


def follow_on(tk, roe_antigo_lp, roe_antigo_ini):
    """(VPA, ROE de longo prazo, ROE de partida) com o follow-on: o P/VP justificado é linear no ROE, então o ROE ponderado
    (antigo no PL antigo, Ke no dinheiro novo) equivale a valor antigo + caixa captado."""
    f, l = FOLLOW_ON[tk], ltm_de(CVM[tk])
    pl_old = l["pl"] - l["nao_controladores"]
    pl_new = pl_old + f["valor"]
    w = f["valor"] / pl_new
    acoes = l["acoes"] + f["valor"] * 1000 / f["preco"]
    return pl_new * 1000 / acoes, (1 - w) * roe_antigo_lp + w * MK.ke_nom, (1 - w) * roe_antigo_ini + w * MK.ke_nom


def F(tk, nome, preco, payout, roe_inicio=None, desconto=None, qual=None, roe=None):
    vpa = ind(tk, "vpa")
    r_lp = roe if roe is not None else roe_lp(tk)
    r_ini = roe_inicio if roe_inicio is not None else ind(tk, "roe") / 100
    if tk in FOLLOW_ON:
        vpa, r_lp, r_ini = follow_on(tk, r_lp, r_ini)
    return Financeira(tk, nome, "utility", preco=preco, vpa=vpa, lpa_12m=ind(tk, "lpa"),
                      roe_lp=r_lp, roe_inicio=r_ini,
                      payout=payout, dpa_medio_5a=dpa5(tk), jcp_share=jcp(tk), pl_hist=pl_hist(tk),
                      desconto_controlador=desconto or {"tipo": "zero", "razao": ""}, solidez_manual=solidez(tk),
                      anos_pagos_10=anos_pagos(tk), qualitativo=qual or {},
                      # v2.3: peso 2 do controlador onde a interferência consumada está declarada no desconto (provisório, até o dossiê)
                      controlador_discricionario=desconto is not None,
                      controlador_discricionario_fonte=("interferência consumada declarada no desconto do lote (critério provisório "
                                                        "v2.3, até o dossiê): " + desconto["razao"]) if desconto else "")


# §11.2 (doutrina v2.5, AUD-20): onde está o investimento de cada regulado na DFC de 2025 (DFC_MI; "con" = consolidada,
# "ind" = individual — a Sanepar só publica a individual). Valores em R$ mil, conferidos contra o ZIP da CVM por
# tests/test_regulados_dfc.py. As linhas 6.01.x são o investimento que a concessão põe DENTRO do FCO; as 6.02.x, o
# capex no FCI. Nenhum dos 9 tem base regulatória e WACC regulatório com fonte A/B → em todos o DCF regulatório é o
# P/VP justificado sobre o patrimônio, como proxy declarado (a condição "investimento no FCO" da v2.1 só valia em 2).
REGULADOS_DFC = {
    "TAEE11": ("con", {"6.01.01.14": -2_299_138}, {"6.02.04": -43_797}),
    "ISAE4": ("con", {"6.01.01.08": -10_688_556}, {"6.02.04": -27_604, "6.02.05": -16_845}),
    "EGIE3": ("con", {"6.01.01.13": -1_509_763}, {"6.02.11": -1_752_248}),
    "CPLE3": ("con", {"6.01.01.04": -867_817}, {"6.02.04": -2_903_661, "6.02.10": -162_100, "6.02.12": -43_788}),
    "CPFE3": ("con", {}, {"6.02.03": -4_963_868, "6.02.02": -369_941, "6.02.04": -20_543}),
    "CMIG4": ("con", {}, {"6.02.04": -5_386_242, "6.02.02": -699_182, "6.02.03": -378_608}),
    "SAPR11": ("ind", {}, {"6.02.01": -2_615_418}),
    "CSMG3": ("con", {}, {"6.02.10": -1_937_331, "6.02.11": -727_089, "6.02.12": -83_019}),
    "SBSP3": ("con", {}, {"6.02.01": -13_740_392}),
}
FCI_MAX_NO_FCO = 0.10        # até 10% do investimento no FCI ainda é "FCO" (TAEE11: 1,9%; ISAE4: 0,4%)


def investimento_dfc(tk: str) -> str:
    """'FCO', 'FCI' ou 'misto' — calculado das linhas citadas, não digitado."""
    _, fco, fci = REGULADOS_DFC[tk]
    no_fco, no_fci = -sum(fco.values()), -sum(fci.values())
    if no_fco <= 0:
        return "FCI"
    return "FCO" if no_fci / (no_fco + no_fci) <= FCI_MAX_NO_FCO else "misto"


def metodo_regulado(tk: str) -> str:
    """Frase da ficha: o método e por quê (§11.2 v2.5)."""
    _, fco, fci = REGULADOS_DFC[tk]
    mi = lambda d: " + ".join(f"{k} " + f"{v / 1e6:.2f}".replace(".", ",") + " bi" for k, v in d.items())
    onde = {"FCO": f"investimento no FCO pela contabilidade de concessão ({mi(fco)})",
            "FCI": f"investimento no FCI ({mi(fci)})",
            "misto": f"investimento misto: FCO {mi(fco)}; FCI {mi(fci)}"}[investimento_dfc(tk)]
    return (f"DCF regulatório = P/VP justificado sobre o patrimônio, como proxy da base (§11.2 v2.5): {onde} na DFP 2025; "
            "sem base regulatória e WACC regulatório com fonte A/B")


# Preços = fechamento oficial (PREULT do COTAHIST) de 02/10/2026 — data e fonte em precos_hall.py (AUD-67).
EMPRESAS = [
    F("TAEE11", "Taesa (unit)", 42.85, payout=0.75, qual=QUAL(4, 3, 3, 4, 3)),
    F("ISAE4", "ISA Energia (ex-CTEEP)", 28.19, payout=0.60, qual=QUAL(4, 4, 4, 4, 3)),
    F("CPFE3", "CPFL Energia", 48.09, payout=0.60, qual=QUAL(4, 4, 4, 4, 4)),
    F("CMIG4", "Cemig", 11.41, payout=0.50, qual=QUAL(3, 3, 1, 3, 3),
      desconto={"tipo": "fixo", "pct": 0.177,
                "razao": "MG: MP 579 (2012), corte de dividendo e venda de ativos (2016) consumados; Propag/federalização — precedente da casa: "
                         "40% de probabilidade de um cenário com valor 44% menor (0,4 × 44% = 17,7%)"}),
    F("CPLE3", "Copel", 16.61, payout=0.55, qual=QUAL(3, 3, 4, 3, 3)),
    F("SAPR11", "Sanepar (unit)", 35.21, payout=0.35, roe_inicio=0.10, qual=QUAL(4, 3, 1, 4, 3),
      desconto={"tipo": "fixo", "pct": 0.15,
                "razao": "PR: Agepar destinou R$ 4,4 bi à tarifa em 2026 (V2 consumado) — precedente da casa: 15%"}),
    F("CSMG3", "Copasa", 56.25, payout=0.60, qual=QUAL(4, 3, 3, 4, 3)),
    F("SBSP3", "Sabesp", 28.23, payout=0.25, qual=QUAL(5, 4, 4, 4, 4)),
]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Ke nominal {MK.ke_nom:.2%} · real {MK.ke_real:.2%} · rf real {MK.rf_real:.2%}")
    for e in EMPRESAS:
        r = avaliar(e, MK)
        ki = r["ke_implicito"]
        tir = (1 + ki) / (1 + MK.pi) - 1 if ki else None
        dle, cob, _ = alavancagem(e.ticker)
        anc = " | ".join(f"{k}: {x:.2f}" for k, x in r["ancoras"].items())
        print(f"{e.ticker:7} P {e.preco:6.2f} VPA {e.vpa:6.2f} ROE lp {e.roe_lp:.1%} ini {e.roe_inicio:.1%} g {r['g']:.1%} | central {r['central']:6.2f} "
              f"P/C {r['pc']:.2f} {r['palavra']:6} | {anc} | TIR real {tir and f'{tir:.1%}'} | Bogle {r['bogle_nom']:.1%} RF {r['vence_rf']}/{r['rf_sem_rerating']} "
              f"| DL/EBITDA {dle and round(dle,2)} cob {cob and round(cob,1)} | nota {r['notas']['geral']:.1f}")
