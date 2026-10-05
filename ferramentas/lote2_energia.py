"""Lote 2 — Energia elétrica e saneamento · data-base 02/10/2026 (fechamento; preços do PDF rev. 03/10) · doutrina v2.1.

Regulados: a contabilidade de concessão (ICPC 01/IFRS 15) põe o investimento em ativo de contrato dentro do FCO das
transmissoras — "FCO − capex" não funciona. Método de regulado (doutrina §11.2, utility):
  · DCF regulatório = P/VP justificado: patrimônio (proxy da base regulatória) × (ROE − g) ÷ (Ke − g)
  · DDM em 2 estágios (ROE do início converge ao de longo prazo em 5 anos)
  · TIR real implícita = Ke implícito no preço, em termos reais — comparada à rf (piso) e ao Ke real (sempre).
VPA/LPA/ROE/proventos: StatusInvest (base pós-bonificação, coerente com o preço). Alavancagem e cobertura: CVM (12m até jun/26).
"""
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
    l = CVM[tk]["ltm_2T26"]
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


def F(tk, nome, preco, payout, roe_inicio=None, desconto=None, qual=None, roe=None):
    return Financeira(tk, nome, "utility", preco=preco, vpa=ind(tk, "vpa"), lpa_12m=ind(tk, "lpa"),
                      roe_lp=roe if roe is not None else roe_lp(tk),
                      roe_inicio=roe_inicio if roe_inicio is not None else ind(tk, "roe") / 100,
                      payout=payout, dpa_medio_5a=dpa5(tk), jcp_share=jcp(tk), pl_hist=pl_hist(tk),
                      desconto_controlador=desconto or {"tipo": "zero", "razao": ""}, solidez_manual=solidez(tk),
                      anos_pagos_10=anos_pagos(tk), qualitativo=qual or {})


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
