"""Lote 6 — Química e metalurgia · data-base 02/10/2026 (preços do PDF rev. 03/10) · doutrina v2.2.

Demonstrações: CVM (DFP 2016–25 + ITR, 12m até jun/2026). Preço: PDF rev. 03/10 (fechamento de 02/10, StatusInvest). Ações: composição do capital
do ITR de jun/2026 (CVM), sem tesouraria; EGIE3 com o follow-on de jul/2026. Proventos: StatusInvest, ajustados por bonificação (abaixo).
Ciclo declarado ANTES do veredito (doutrina §2, regra 4; §11.1 "preço de commodity declarado"):
  · Nenhum dos PDFs anteriores declara preço de aço, PVC ou soda. Fonte usada: índices de preço ao produtor dos EUA (BLS, via FRED) — a única
    série pública mensal e longa; não há preço em R$/t por API com fonte A/B. Convertidos a reais pela PTAX média mensal (BCB SGS 3698) e
    corrigidos pelo IPCA (BCB SGS 433) até ago/2026 — o mesmo tratamento do barril no Lote 5. Índice 2016–25 = 100.
  · Aço (GGBR4): WPU1017 "Steel Mill Products". Cloro-soda e PVC (UNIP6): 50% PCU3251803251804 "Sodium Hydroxide (Caustic Soda)" + 50% WPU0662
    "Thermoplastic Resins" (proxy do PVC — o BLS não publica a série de PVC isolada no FRED). Pesos 50/50 = HIPÓTESE (Unipar vende cloro-soda e
    PVC nos dois países; a divisão da receita não consta do material).
  · Receita de meio de ciclo = receita de 12m até jun/2026 (volume atual) × preço de meio (média 2016–25 em R$ de hoje) ÷ preço médio dos 12m.
    Janela do preço = janela da margem (UNIP6 2017–25: a série de soda também não tem jan–set/2016; achado do adversário 05/10).
    Margem = EBIT mediano do ciclo, sem não recorrentes; GGBR4 sem o impairment de cada ano e com a perda mediana como custo recorrente.
  · UNIP6: janela 2017–25 (Indupa consolidada em dez/2016; 2016 tem ganho de compra vantajosa e receita de 1 mês da Argentina).
  · LEVE3: industrial (autopeças, reposição ~36% [PDF 03/10]); receita = média dos 3 últimos exercícios + 12m; margem mediana 2016–25.
  · EGIE3: utility — método de regulado do Lote 2 (P/VP justificado sobre o patrimônio + DDM 2 estágios; TIR real implícita). Transmissão
    contabilizada como ativo de contrato (ICPC 01) → FCO não mede o caixa do negócio, EPV N/A. Follow-on de jul/2026 (274,1 mi de ações,
    R$ 8,36 bi, para 40% de Jirau): somado ao patrimônio e suposto render o Ke (VPL zero) — o valor sobe exatamente pelo caixa captado.
P/L histórico no Bogle só na LEVE3 (lucro de GGBR4 e UNIP6 dominado pelo preço da commodity).
"""
from ltm import ltm_de
import json
import pathlib
import statistics as st
import sys

import pandas as pd

from lote1_bancos import MK
from lote2_energia import pl_hist, solidez
from lote3_agro import jcp
from motor_financeiras import Financeira
from motor_financeiras import avaliar as avaliar_fin
from motor_nao_financeiras import CVM, SI, Industrial, avaliar

AQUI = pathlib.Path(__file__).parent
MACRO = AQUI / "dados" / "macro"
QUAL = lambda moat, gestao, controlador, ciclo, fisher: dict(moat=moat, gestao=gestao, controlador=controlador, ciclo=ciclo, fisher=fisher)

SERIES = {"WPU1017": "BLS PPI Steel Mill Products", "PCU3251803251804": "BLS PPI Sodium Hydroxide (Caustic Soda)",
          "WPU0662": "BLS PPI Thermoplastic Resins and Plastics Materials"}


def _fred(i):
    b = pd.read_csv(MACRO / f"fred_{i}.csv")
    b.columns = ["d", "v"]
    b["v"] = pd.to_numeric(b["v"], errors="coerce")
    b = b.dropna()
    return pd.Series(b["v"].values, index=pd.to_datetime(b["d"]))


def _base():
    p = pd.DataFrame(json.loads((MACRO / "ptax_media_mensal.json").read_text()))
    ptax = pd.Series(p["valor"].astype(float).values, index=pd.to_datetime(p["data"], dayfirst=True))
    i = pd.DataFrame(json.loads((MACRO / "ipca_mensal.json").read_text()))
    ipca = pd.Series((1 + i["valor"].astype(float) / 100).cumprod().values, index=pd.to_datetime(i["data"], dayfirst=True))
    return ptax, ipca


def indice(pesos, a0=2016, a1=2025):
    """Índice de preço em R$ (índice US$ × PTAX), média a0–a1 = 100 em R$ de hoje. Retorna meio, 12m e fator de meio de ciclo.
    A janela do preço é a mesma da margem (UNIP6: 2017–25; a série de soda também não tem jan–set/2016)."""
    ptax, ipca = _base()
    idx = None
    for k, w in pesos.items():
        s = _fred(k)
        s = s / s.loc[str(a0):str(a1)].mean() * 100
        idx = w * s if idx is None else idx + w * s
    df = pd.DataFrame({"idx": idx, "ptax": ptax, "ipca": ipca}).dropna()
    base_i = df["ipca"].iloc[-1]
    df["rs"] = df["idx"] * df["ptax"]
    df["real"] = df["rs"] * base_i / df["ipca"]
    anual = df.groupby(df.index.year).mean()
    meio = anual.loc[a0:a1, "real"].mean()
    ltm = df.loc["2025-07":"2026-06", "rs"].mean()
    ltm_real = df.loc["2025-07":"2026-06", "real"].mean()
    k = 100 / meio                      # reescala: meio de ciclo = 100
    return dict(anual=anual * k, meio=100.0, ltm=ltm * k, ltm_real=ltm_real * k, fator=meio / ltm, janela=f"{a0}–{a1 - 2000:02d}", ultimo=(df.index[-1].strftime("%m/%Y"), df["rs"].iloc[-1] * k),
                base=df.index[-1].strftime("%m/%Y"), idx_usd=anual["idx"])


ACO = indice({"WPU1017": 1.0})
CLORO = indice({"PCU3251803251804": 0.5, "WPU0662": 0.5}, 2017)
SODA = indice({"PCU3251803251804": 1.0}, 2017)
PVC = indice({"WPU0662": 1.0}, 2017)


def acoes_jun26(tk):
    """Ações em circulação em 30/06/2026 (ITR, composição do capital), sem tesouraria."""
    import io
    import zipfile
    z = zipfile.ZipFile(AQUI / "dados" / "cvm" / "itr_2026.zip")
    n = [x for x in z.namelist() if "composicao" in x][0]
    df = pd.read_csv(io.BytesIO(z.read(n)), sep=";", encoding="latin-1", dtype=str)
    cod = {"LEVE3": "MAHLE METAL LEVE", "EGIE3": "ENGIE BRASIL ENERGIA", "UNIP6": "UNIPAR CARBOCLORO", "GGBR4": "GERDAU S.A."}[tk]
    d = df[df["DENOM_CIA"].str.startswith(cod) & (df["DT_REFER"] == "2026-06-30")].iloc[-1]
    return float(d["QT_ACAO_TOTAL_CAP_INTEGR"]) - float(d["QT_ACAO_TOTAL_TESOURO"])


# ---------------------------------------------------------------- proventos ajustados (StatusInvest não ajusta bonificação)
def ajustar_dpa(tk, n_atual):
    s = SI[tk]
    if tk == "EGIE3":       # bonificação de 40% em 01/12/2025 [PDF 03/10]: data-com anterior ÷ 1,4
        dpa, jc = {}, {}
        for e in s["eventos"]:
            d, m, a = e["data_com"].split("/")
            f = 1 / 1.4 if (a, m, d) < ("2025", "12", "01") else 1.0
            dpa[a] = dpa.get(a, 0) + e["valor"] * f
            if "JCP" in (e["tipo"] or "").upper():
                jc[a] = jc.get(a, 0) + e["valor"] * f
        s["dpa_por_ano_datacom"], s["jcp_por_ano_datacom"] = dict(sorted(dpa.items())), dict(sorted(jc.items()))
    elif tk in ("GGBR4", "UNIP6"):   # bonificações (GGBR4 2023–24; UNIP6 2022 e 2024): × ações no fim do ano ÷ ações de hoje (aprox.)
        a = CVM[tk]["anual"]
        def n_ano(y):
            x = (a.get(str(y), {}).get("acoes") or 0)
            x = x * 1000 if 0 < x < 1e7 else x
            return x or None
        ref = next(n_ano(y) for y in range(2016, 2026) if n_ano(y))
        for chave in ("dpa_por_ano_datacom", "jcp_por_ano_datacom"):
            # só bonificação reduz o DPA antigo (fator < 1); recompra (ações de antes > hoje) não infla o passado
            s[chave] = {y: val * min(1.0, (n_ano(int(y)) or ref) / n_atual) if int(y) <= 2025 else val for y, val in s[chave].items()}


N = {tk: acoes_jun26(tk) for tk in ("LEVE3", "EGIE3", "UNIP6", "GGBR4")}
EGIE_FOLLOW_ON = dict(acoes=274.1e6, valor=8_360_000, data="jul/2026")        # R$ mil; [PDF 07/09 e 03/10]
EGIE_DIV_AGO26 = 770_800      # R$ mil, data-com 20/08/2026 (R$ 0,5442 × 1.416 mi): sai do PL de 30/06 — o preço de 02/10 já é ex
N["EGIE3"] += EGIE_FOLLOW_ON["acoes"]
for _tk in N:
    ajustar_dpa(_tk, N[_tk])


# ---------------------------------------------------------------- EGIE3 (regulado)
def roe_limpo(tk, anos):
    """ROE do controlador por ano, sem 'outras receitas' acima da mediana de 10 anos (após IR de 34%) — UBP de 2024 etc."""
    a = CVM[tk]["anual"]
    xs = [((a[y].get("outras_receitas_op") or 0) + (a[y].get("outras_despesas_op") or 0)) / a[y]["receita"] for y in map(str, range(2016, 2026))]
    med = st.median(xs)
    out = {}
    for y in anos:
        d, p = a[str(y)], a[str(y - 1)]
        exc = max(0.0, (d.get("outras_receitas_op") or 0) + (d.get("outras_despesas_op") or 0) - med * d["receita"])
        pl = lambda x: x["pl"] - (x.get("nao_controladores") or 0)
        out[y] = (d["lucro_controlador"] - 0.66 * exc) / ((pl(d) + pl(p)) / 2)
    return out


def egie():
    l = ltm_de(CVM["EGIE3"])
    pl_old = l["pl"] - l["nao_controladores"] - EGIE_DIV_AGO26
    pl_new = pl_old + EGIE_FOLLOW_ON["valor"]
    roes = roe_limpo("EGIE3", range(2017, 2026))
    roe_old_lp = st.median(roes.values())
    roe_old_ini = l["lucro_controlador"] / pl_old
    w = EGIE_FOLLOW_ON["valor"] / pl_new
    # P/VP justificado é linear no ROE: ROE combinado = média ponderada (antigo × Ke no dinheiro novo) ⇔ valor antigo + caixa captado
    blend = lambda r: (1 - w) * r + w * MK.ke_nom
    dados = dict(pl_old=pl_old, pl_new=pl_new, roes=roes, roe_old_lp=roe_old_lp, roe_old_ini=roe_old_ini, peso_novo=w)
    return Financeira("EGIE3", "Engie Brasil Energia", "utility", preco=30.70, vpa=pl_new * 1000 / N["EGIE3"], lpa_12m=l["lucro_controlador"] * 1000 / N["EGIE3"],
                      roe_lp=blend(roe_old_lp), roe_inicio=blend(roe_old_ini), payout=0.55,
                      dpa_medio_5a=sum(SI["EGIE3"]["dpa_por_ano_datacom"].get(str(a), 0) for a in range(2021, 2026)) / 5,
                      jcp_share=jcp("EGIE3"), pl_hist=pl_hist("EGIE3"), solidez_manual=solidez("EGIE3"),
                      anos_pagos_10=sum(1 for a in range(2016, 2026) if SI["EGIE3"]["dpa_por_ano_datacom"].get(str(a), 0) > 0),
                      qualitativo=QUAL(4, 4, 3, 4, 3)), dados


EGIE, EGIE_DADOS = egie()

# ---------------------------------------------------------------- não financeiras
# Preços = fechamento oficial (PREULT do COTAHIST) de 02/10/2026 — data e fonte em precos_hall.py (AUD-67).
EMPRESAS = [
    Industrial("GGBR4", "Gerdau (PN)", "ciclica", preco=26.10, n_acoes=N["GGBR4"], g_real=0.01, jcp_share=jcp("GGBR4"),
               receita_meio=ltm_de(CVM["GGBR4"])["receita"] * ACO["fator"], outras_liquidas=True, impairment_normalizado=True,
               receita_meio_fonte="receita 12m × aço de meio de ciclo ÷ aço dos 12m (BLS WPU1017 × PTAX, R$ de hoje)",
               qualitativo=QUAL(3, 4, 4, 2, 3)),
    Industrial("UNIP6", "Unipar Carbocloro (PNB)", "ciclica", preco=57.02, n_acoes=N["UNIP6"], g_real=0.01, jcp_share=jcp("UNIP6"),
               anos_ciclo=[str(a) for a in range(2017, 2026)], receita_meio=ltm_de(CVM["UNIP6"])["receita"] * CLORO["fator"], outras_liquidas=True,
               janela_razao="Indupa consolidada em dez/2016: 2016 traz ganho de compra vantajosa e 1 mês de receita da Argentina "
                            "(e a série de soda não cobre jan–set/2016)",
               receita_meio_fonte="receita 12m × cesta soda/PVC de meio de ciclo ÷ cesta dos 12m (BLS × PTAX, R$ de hoje)",
               qualitativo=QUAL(3, 2, 2, 2, 2)),
    Industrial("LEVE3", "Mahle Metal Leve", "servicos", preco=34.43, n_acoes=N["LEVE3"], g_real=0.01, jcp_share=jcp("LEVE3"),
               outras_liquidas=True, pl_hist=pl_hist("LEVE3"),
               # 08/10/2026: notas por evidência do dossiê (regra 11, DOSSIES/2026-10-08-LEVE3.md) no lugar das arbitradas (4, 3, 3, 3, 3)
               qualitativo=QUAL(4, 1, 2, 3, 2), qualitativo_origem="regra 11 (dossiê 06/10/2026)", controlador_discricionario=True,
               controlador_discricionario_fonte="FRE 2026: MAHLE Indústria e Comércio 56,8% + MAHLE Industriebeteiligungen 4,2% = 61,0%; "
                                                "controle sobre preço de transferência, royalties (até 1% da receita) e compras do grupo"),
]

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Ke nominal {MK.ke_nom:.2%} | rf nom {MK.rf_nom:.2%} | RF real líq {MK.rf_liq_real:.2%} | π {MK.pi:.2%}")
    for nome, x in (("aço", ACO), ("cloro-soda/PVC", CLORO), ("soda", SODA), ("resinas", PVC)):
        print(f"{nome}: meio 100 | 12m {x['ltm']:.1f} | fator {x['fator']:.3f} | último {x['ultimo']} | anual real",
              {y: round(x['anual'].loc[y, 'real']) for y in range(2016, 2026)})
    print("ações:", {k: round(v / 1e6, 2) for k, v in N.items()})
    for e in EMPRESAS:
        r = avaliar(e, MK)
        anc = " | ".join(f"{k}: {x:.2f}" for k, x in r["ancoras"].items())
        ki = r["ke_implicito"]; gi = r["g_implicito"]
        print(f"{e.ticker:6} P {e.preco:6.2f} central {r['central']:6.2f} P/C {r['pc']:.2f} {r['palavra']:6} disp {r['dispersao']:.2f} | {anc}")
        print(f"       WACC {r['wacc']:.1%} ROIC {r['roic']:.1%} margem {r['m']:.1%} (p25 {r['op']['m25']:.1%} p75 {r['op']['m75']:.1%}) aj {r['op']['ajuste_manut']:.1%} "
              f"imp {r['op']['impairment_recorrente']:.2%} rec_meio {r['op']['receita_meio']/1e6:.2f}bi IR {r['aliquota']:.0%} DL {r['dl']/1e6:.2f}bi DL/EBITDA {r['dl_ebitda'] and round(r['dl_ebitda'],2)} "
              f"norm {r['dl_ebitda_norm'] and round(r['dl_ebitda_norm'],2)} cob {r['cobertura_juros'] and round(r['cobertura_juros'],1)} nao_rec {list(r['op']['nao_rec'])}")
        print(f"       Ke* {ki and f'{ki:.1%}'} g* {gi and f'{gi:.1%}'} | Bogle {r['bogle_nom']:.1%} liq real {r['bogle_liq_real']:.1%} RF {r['vence_rf']}/{r['rf_sem_rerating']} | "
              f"OE {r['oe_norm'] and round(r['oe_norm']/1e3)} mi DPA5 {r['dpa5']:.2f} FCFE/ação {r['fcfe_acao']:.2f} coberto {r['coberto']} | "
              f"Z'' {r['altman']:.2f} {r['altman_zona']} F {r['piotroski']} M {r['beneish'] and round(r['beneish'],2)} | EY {r['ey'] and round(100*r['ey'],1)} ROC {r['roc'] and round(100*r['roc'],1)} | nota {r['notas']['geral']:.1f}")
        print(f"       margens {[round(100*x,1) for x in r['op']['margens']]} | LPA norm {r['lpa_norm']:.2f} VPA {r['vpa']:.2f}")
    r = avaliar_fin(EGIE, MK)
    ki = r["ke_implicito"]
    tir = (1 + ki) / (1 + MK.pi) - 1 if ki else None
    d = EGIE_DADOS
    print(f"EGIE3  P {EGIE.preco:.2f} VPA {EGIE.vpa:.2f} (PL antigo {d['pl_old']/1e6:.2f} bi + {EGIE_FOLLOW_ON['valor']/1e6:.2f}) ROE lp {EGIE.roe_lp:.1%} "
          f"(antigo {d['roe_old_lp']:.1%}) ini {EGIE.roe_inicio:.1%} (antigo {d['roe_old_ini']:.1%}) g {r['g']:.1%} | central {r['central']:.2f} P/C {r['pc']:.2f} "
          f"{r['palavra']} | " + " | ".join(f"{k}: {x:.2f}" for k, x in r["ancoras"].items()) + f" | TIR real {tir and f'{tir:.1%}'} | Bogle {r['bogle_nom']:.1%} "
          f"RF {r['vence_rf']}/{r['rf_sem_rerating']} | nota {r['notas']['geral']:.1f}")
    print("       ROE limpo por ano", {k: round(100 * v, 1) for k, v in d["roes"].items()}, "DPA", {k: round(v, 2) for k, v in SI['EGIE3']['dpa_por_ano_datacom'].items() if k >= '2019'})
