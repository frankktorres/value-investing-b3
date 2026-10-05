"""Lote 3 — Papel e celulose, infraestrutura de mercado e agro · data-base 02/10/2026 · doutrina v2.0.

Demonstrações: CVM (DFP 2016–25 + ITR, LTM até 2T26; SMTO3 exercício abr–mar até mar/2026). Preço, ações, proventos e P/L
histórico: StatusInvest. Mercado: mesmo do Lote 1 (Tesouro Transparente, ANBIMA, BCB).
P/L histórico só entra no Bogle quando o lucro não é dominado por câmbio/ciclo (B3SA3, SMTO3, SLCE3); nas demais o Bogle
vai sem re-rating — declarado.
"""
import sys

from lote1_bancos import MK
from motor_nao_financeiras import CVM, SI, Industrial, avaliar

QUAL = lambda moat, gestao, controlador, ciclo, fisher: dict(moat=moat, gestao=gestao, controlador=controlador, ciclo=ciclo, fisher=fisher)


def jcp(tk):
    s = SI[tk]
    tot = sum(s["dpa_por_ano_datacom"].get(a, 0) for a in ("2024", "2025"))
    j = sum(s["jcp_por_ano_datacom"].get(a, 0) for a in ("2024", "2025"))
    return j / tot if tot else 0.0


def acoes(tk):
    """Ações em circulação (sem tesouraria) do último DFP na CVM; KLBN11 em units (5 ações)."""
    d = CVM[tk]["anual"]["2026" if tk == "SMTO3" else "2025"]
    n = d["acoes"]
    if n < 1e7:          # alguns formulários da CVM informam a quantidade em milhares
        n *= 1000
    return n / CVM[tk]["acoes_por_unit"]


EMPRESAS = [
    Industrial("SUZB3", "Suzano", "ciclica", preco=44.35, n_acoes=acoes("SUZB3"), spread_kd=0.015, g_real=0.01, jcp_share=jcp("SUZB3"),
               qualitativo=QUAL(4, 4, 4, 2, 3)),
    Industrial("KLBN11", "Klabin (unit)", "ciclica", preco=18.62, n_acoes=acoes("KLBN11"), spread_kd=0.015, g_real=0.01, jcp_share=jcp("KLBN11"),
               qualitativo=QUAL(3, 3, 3, 2, 3)),
    Industrial("RANI3", "Irani", "ciclica", preco=7.94, n_acoes=acoes("RANI3"), spread_kd=0.025, g_real=0.01, jcp_share=jcp("RANI3"),
               qualitativo=QUAL(2, 3, 3, 2, 3)),
    Industrial("B3SA3", "B3", "servicos", preco=19.00, n_acoes=acoes("B3SA3"), spread_kd=0.012, g_real=0.02, jcp_share=jcp("B3SA3"),
               pl_hist=20.3, qualitativo=QUAL(5, 4, 4, 3, 4)),
    Industrial("SMTO3", "São Martinho", "ciclica", preco=19.34, n_acoes=acoes("SMTO3"), spread_kd=0.015, g_real=0.01, jcp_share=jcp("SMTO3"),
               anos_ciclo=[str(a) for a in range(2017, 2027)], pl_hist=9.7, qualitativo=QUAL(3, 4, 4, 2, 3)),
    Industrial("KEPL3", "Kepler Weber", "ciclica", preco=6.78, n_acoes=acoes("KEPL3"), spread_kd=0.02, g_real=0.01, jcp_share=jcp("KEPL3"),
               qualitativo=QUAL(3, 3, 3, 2, 3)),
    Industrial("SLCE3", "SLC Agrícola", "ciclica", preco=17.20, n_acoes=acoes("SLCE3"), spread_kd=0.02, g_real=0.01, jcp_share=jcp("SLCE3"),
               pl_hist=10.6, reproducao_por_acao=27.12,
               reproducao_fonte="NAV das terras R$ 27,12/ação (Itaú BBA, nota B, não auditado) — o PL contábil registra terra a custo histórico",
               qualitativo=QUAL(3, 4, 4, 2, 3)),
]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Ke nominal {MK.ke_nom:.2%} | RF real líq {MK.rf_liq_real:.2%}")
    for e in EMPRESAS:
        r = avaliar(e, MK)
        anc = " | ".join(f"{k}: {x:.2f}" for k, x in r["ancoras"].items())
        ki = r["ke_implicito"]; gi = r["g_implicito"]
        print(f"{e.ticker:6} P {e.preco:6.2f} central {r['central']:6.2f} P/C {r['pc']:.2f} {r['palavra']:6} disp {r['dispersao']:.2f} | {anc}")
        print(f"       WACC {r['wacc']:.1%} ROIC {r['roic']:.1%} margem {r['m']:.1%} (p25 {r['op']['m25']:.1%} p75 {r['op']['m75']:.1%}) rec_meio {r['op']['receita_meio']/1e6:.1f}bi "
              f"DL/EBITDA {r['dl_ebitda'] and round(r['dl_ebitda'],2)} norm {r['dl_ebitda_norm'] and round(r['dl_ebitda_norm'],2)} cob {r['cobertura_juros'] and round(r['cobertura_juros'],1)}")
        print(f"       Ke* {ki and f'{ki:.1%}'} g_real* {gi and f'{gi:.1%}'} | Bogle {r['bogle_nom']:.1%} liq real {r['bogle_liq_real']:.1%} RF {r['vence_rf']}/{r['rf_sem_rerating']} | "
              f"OE {r['oe_norm'] and round(r['oe_norm']/1e3)} mi DPA5 {r['dpa5']:.2f} FCFE/ação {r['fcfe_acao']:.2f} coberto {r['coberto']} | "
              f"Z'' {r['altman']:.2f} {r['altman_zona']} F {r['piotroski']} M {r['beneish'] and round(r['beneish'],2)} Sloan {r['sloan']:.1%} | EY {r['ey'] and f'{r[chr(101)+chr(121)]:.1%}'} ROC {r['roc'] and f'{r[chr(114)+chr(111)+chr(99)]:.1%}'} | nota {r['notas']['geral']:.1f}")
