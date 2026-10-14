"""Lote 1 — Bancos e Seguridade · data-base 02/10/2026 · doutrina v2.0.

Cada premissa tem a justificativa ao lado. Séries: StatusInvest (dados/raw/2026-10-04); fatos: PDFs rev. 07/09 e 03/10
(fontes primárias citadas lá); mercado: Tesouro Transparente, ANBIMA (ETTJ) e BCB (Focus).
"""
import mercado
from motor_financeiras import SEM_RAZAO, Financeira, avaliar

DATA_BASE = "02/10/2026"

# rf e π vêm de `mercado_vigente.json` (AUD-78: um arquivo só, conferido contra dados/mercado.json por teste).
# rf: Tesouro IPCA+ 2050 SEM cupom (o mais longo sem cupom), 7,06% — Tesouro Transparente, taxa de COMPRA DA MANHÃ de
#     02/10: o Tesouro Direto não publica fechamento e a ANBIMA não traz a NTN-B Principal (a NTN-B 2050 com cupom, outro
#     instrumento, fechou a 7,14% — sensibilidade no 09, AUD-06).
# π:  inflação implícita ANBIMA (ETTJ de fechamento), vértice de 10 anos = horizonte da comparação: 6,46%.
#     Focus (25/09): 4,99% 2026 · 4,31% 2027 · 3,50% 2029–30 — só sensibilidade.
MK = mercado.vigente()
MK_FOCUS = mercado.focus()
if MK.data != DATA_BASE:
    raise ValueError(f"mercado_vigente.json é de {MK.data}, o lote é de {DATA_BASE}: rf e π têm de ser do dia do preço (§4)")

QUAL = lambda moat, gestao, controlador, ciclo, fisher: dict(moat=moat, gestao=gestao, controlador=controlador, ciclo=ciclo, fisher=fisher)
# notas arbitradas (pré-v4). v2.3: peso 2 do controlador (regra 11, §10) onde a interferência JÁ consumada está declarada no
# desconto do próprio lote — critério mecânico provisório; o dossiê de cada ticker decide pela evidência
DISC = "interferência consumada declarada no desconto do lote (critério provisório v2.3, até o dossiê): "

# Preços = fechamento oficial (PREULT do COTAHIST) de 02/10/2026 — data e fonte em precos_hall.py (AUD-67).
EMPRESAS = [
    Financeira("ITUB4", "Itaú Unibanco", "banco", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=44.83, vpa=19.75, lpa_12m=4.247,
               roe_lp=0.1758,      # mediana 2016–25 (13,2–21,9%)
               roe_inicio=0.215,   # ROE 12m (StatusInvest, nota C) no t = 0; o fatos_B cita 24,3% no 2T26 (AUD-63)
               payout=0.60,        # nota C, sem fonte primária (AUD-61): fatos_B dá 69,4% em 2024 COM extraordinário; política do RI a conferir
               dpa_medio_5a=2.069, jcp_share=0.41, pl_hist=9.50,
               prudencial=dict(cet1=12.3, inad90=1.9), qualitativo=QUAL(5, 5, 4, 3, 4)),
    Financeira("BBDC4", "Bradesco", "banco", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=19.23, vpa=17.11, lpa_12m=2.321,
               roe_lp=0.1343, roe_inicio=0.14, payout=0.55, dpa_medio_5a=1.143, jcp_share=1.0, pl_hist=10.55,
               prudencial=dict(cet1=11.3, inad90=4.3, cobertura=152.3), qualitativo=QUAL(4, 2, 4, 3, 3)),
    Financeira("BBAS3", "Banco do Brasil", "banco", preco=23.72, vpa=32.47, lpa_12m=2.685,
               roe_lp=0.137,       # mediana 2016–25 (8,1–19,6%)
               roe_inicio=0.10,    # guidance de lucro 2026 R$ 18–22 bi sobre PL ~R$ 186 bi; JPM 2026e ~9%
               payout=0.30,        # política vigente em 2026
               dpa_medio_5a=1.860, jcp_share=0.84, pl_hist=7.92,
               desconto_controlador=dict(tipo="cenarios", peso=0.30, delta_roe=0.04,
                                         razao="União: crédito dirigido e spreads políticos (2012–15), MP 1.314/1.376 de renegociação rural; "
                                               "30% de probabilidade de repetir um ciclo com ROE 4 p.p. abaixo do normalizado"),
               controlador_discricionario=True,
               controlador_discricionario_fonte=DISC + "União — crédito dirigido e spreads políticos (2012–15), MP 1.314/1.376",
               prudencial=dict(cet1=11.27, inad90=5.61, cobertura=148.5), qualitativo=QUAL(4, 3, 1, 2, 3)),
    Financeira("ABCB4", "ABC Brasil", "banco", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=26.15, vpa=27.85, lpa_12m=3.914,
               roe_lp=0.1283, roe_inicio=0.14, payout=0.45, dpa_medio_5a=1.698, jcp_share=1.0, pl_hist=6.89,
               prudencial=dict(cet1=11.9, inad90=0.6, cobertura=250), qualitativo=QUAL(2, 3, 4, 3, 3)),   # AUD-58: cobertura 250 sem fonte rastreável (Pilar 3 a conferir)
    Financeira("BRSR6", "Banrisul", "banco", preco=15.92, vpa=28.96, lpa_12m=4.016,
               roe_lp=0.1138, roe_inicio=0.11, payout=0.40, dpa_medio_5a=1.070, jcp_share=0.90, pl_hist=5.65,
               desconto_controlador=dict(tipo="fixo", pct=0.35,
                                         razao="Estado do RS: compra da própria folha por R$ 1,23 bi em 2026 (V3 consumado, −1,7 p.p. de CET1); precedente da casa = 35%"),
               controlador_discricionario=True,
               controlador_discricionario_fonte=DISC + "Estado do RS — compra da própria folha por R$ 1,23 bi em 2026 (V3)",
               prudencial=dict(cet1=12.4, inad90=4.62, cobertura=149.5), qualitativo=QUAL(2, 2, 1, 2, 2)),
    Financeira("BRBI11", "BR Partners", "banco", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=15.14, vpa=7.71, lpa_12m=1.520,
               roe_lp=0.2062, roe_inicio=0.197, payout=0.85, dpa_medio_5a=1.628, jcp_share=0.0, pl_hist=10.32,
               solidez_manual=6.0, anos_pagos_10=8, qualitativo=QUAL(2, 4, 3, 2, 3)),
    # AUD-58: dpa_medio_5a 1,628 contra 1,302 da StatusInvest (sem 2021, que vira 0) — o digitado inclui 2021; fonte A (RI/DFP) a conferir
    Financeira("BBSE3", "BB Seguridade", "holding_seguro", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=40.45, vpa=5.61, lpa_12m=4.733,
               roe_lp=0.687, roe_inicio=0.84, payout=0.90, dpa_medio_5a=2.673, jcp_share=0.0, pl_hist=11.10,
               horizonte_finito=dict(anos=7, prob_renovacao=0.80, haircut_renov=0.40),   # AUD-58: 0,80 e 0,40 arbitrados, sem fonte numérica
               solidez_manual=8.0, qualitativo=QUAL(4, 3, 3, 3, 3)),
    Financeira("CXSE3", "Caixa Seguridade", "holding_seguro", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=20.41, vpa=4.60, lpa_12m=1.508,
               roe_lp=0.292, roe_inicio=0.328, payout=0.85, dpa_medio_5a=1.000, jcp_share=0.0, pl_hist=11.35,   # AUD-58: dpa 1,000 sem fonte (SI 0,849; IPO 2021)
               solidez_manual=8.0, qualitativo=QUAL(4, 3, 3, 3, 3)),
    Financeira("PSSA3", "Porto Seguro", "seguradora", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=49.47, vpa=24.94, lpa_12m=5.698,
               roe_lp=0.169, roe_inicio=0.21, payout=0.50, dpa_medio_5a=1.864, jcp_share=0.83, pl_hist=9.44,
               solidez_manual=7.0, qualitativo=QUAL(4, 4, 4, 3, 4)),
    Financeira("SANB11", "Santander Brasil", "banco", desconto_controlador=dict(tipo="zero", razao=SEM_RAZAO), preco=28.09, vpa=33.95, lpa_12m=3.745,
               roe_lp=0.1342, roe_inicio=0.125, payout=0.55, dpa_medio_5a=2.046, jcp_share=0.98, pl_hist=11.92,
               prudencial=dict(cet1=11.2, inad90=3.3), qualitativo=QUAL(3, 3, 3, 3, 3)),
]

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Ke real {MK.ke_real:.2%} · Ke nominal {MK.ke_nom:.2%} · rf nominal {MK.rf_nom:.2%} · RF real líq {MK.rf_liq_real:.2%} "
          f"· RF nom líq {MK.rf_liq_nom:.2%} · g teto {MK.g_teto:.2%} · f Graham {MK.fator_graham:.3f}")
    print(f"{'tk':7}{'preço':>7}{'central':>9}{'P/C':>6} {'palavra':15}{'disp':>5}{'ROE*':>7}{'Bogle n':>8}{'liq real':>9} {'RF':7}{'trava':6}{'nota':>5}  âncoras")
    for e in EMPRESAS:
        r = avaliar(e, MK)
        anc = " | ".join(f"{k}: {v:.2f}" for k, v in r["ancoras"].items())
        print(f"{e.ticker:7}{e.preco:7.2f}{r["central"]:9.2f}{r['pc']:6.2f} {r['palavra']:15}{r['dispersao']:5.2f}{r['roe_implicito']:7.1%}"
              f"{r['bogle_nom']:8.1%}{r['bogle_liq_real']:9.1%} {r['vence_rf']:7}{str(r['trava']):6}{r['notas']['geral']:5.1f}  {anc}")
    print("\nSensibilidade: π 4% (hipótese dos PDFs de 03/10)")
    for e in EMPRESAS:
        r = avaliar(e, MK_FOCUS)
        print(f"{e.ticker:7} central {r['central']:7.2f} P/C {r['pc']:.2f} {r['palavra']}")
