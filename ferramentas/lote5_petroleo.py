"""Lote 5 — Petróleo, gás e combustíveis · data-base 02/10/2026 (preços do PDF rev. 03/10) · doutrina v2.2.

Demonstrações: CVM (DFP 2016–25 + ITR, 12m até jun/2026). Preço: PDF rev. 03/10 (fechamento de 02/10). Ações, proventos: CVM/StatusInvest.
Ciclo declarado ANTES do veredito (doutrina §2, regra 4):
  · Barril de meio de ciclo = média de 10 anos (2016–25) do Brent em R$ de hoje = Brent (EIA, via FRED) × PTAX média mensal (BCB SGS 3698),
    corrigido pelo IPCA (BCB SGS 433) até ago/2026. Decomposto: Brent US$ 82 (média real 10a, em US$ de ago/2026, CPI-EUA) ×
    câmbio real R$ 4,95 (mesma média, a preços de hoje). Equivale a Brent ~US$ 78 ao câmbio de 02/10 (R$ 5,22).
  · E&P (PETR4, PRIO3, RECV3): receita de meio de ciclo = receita do período-base (volume atual) × barril de meio ÷ barril médio do
    período (Brent × PTAX). Período-base: 12m até jun/2026; PRIO3 = 1S26 anualizado, trimestre a trimestre (Peregrino consolidado no
    meio dos 12m — o 12m subestima o volume atual). Margem = EBITDA mediano de 10 anos (RECV3: 2020–25) − D&A atual ÷ receita de meio
    (a exaustão segue o portfólio de hoje, inclusive reservas compradas). PRIO3: ganhos de compra vantajosa (3.04.05) saem como não recorrentes.
  · Distribuição (UGPA3, VBBR3): a receita sobe e desce com o preço do combustível e a margem % anda ao contrário — normaliza-se o EBIT em
    R$ de hoje (IPCA). Janela = perímetro comparável: UGPA3 2021–25 (sem Oxiteno/Extrafarma, descontinuadas em 2021); VBBR3 2020–25
    (gestão privada desde jul/2019). Perfil serviços (DCF, EPV, Owner Earnings), com a regra de capex de commodity (a receita cresce por preço).
P/L histórico fora do Bogle em todas (lucro dominado por Brent e margem de guerra).
"""
from ltm import ltm_de
import json
import pathlib
import sys
from statistics import mean

import pandas as pd

from fiscal import ALIQUOTA_FASE
from lote1_bancos import MK
from lote3_agro import acoes, jcp
from motor_nao_financeiras import CVM, Industrial, avaliar

AQUI = pathlib.Path(__file__).parent
MACRO = AQUI / "dados" / "macro"
QUAL = lambda moat, gestao, controlador, ciclo, fisher: dict(moat=moat, gestao=gestao, controlador=controlador, ciclo=ciclo, fisher=fisher)


def macro():
    b = pd.read_csv(MACRO / "brent_fred.csv")
    b.columns = ["d", "v"]
    b["v"] = pd.to_numeric(b["v"], errors="coerce")
    b = b.dropna()
    b["d"] = pd.to_datetime(b["d"])
    brent = b.set_index("d")["v"].resample("MS").mean()
    p = pd.DataFrame(json.loads((MACRO / "ptax_media_mensal.json").read_text()))
    ptax = pd.Series(p["valor"].astype(float).values, index=pd.to_datetime(p["data"], dayfirst=True))
    i = pd.DataFrame(json.loads((MACRO / "ipca_mensal.json").read_text()))
    ipca = pd.Series((1 + i["valor"].astype(float) / 100).cumprod().values, index=pd.to_datetime(i["data"], dayfirst=True))
    c = pd.read_csv(MACRO / "cpi_us_fred.csv")
    cpi = pd.Series(pd.to_numeric(c.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(c.iloc[:, 0]))
    df = pd.DataFrame({"brent": brent, "ptax": ptax, "ipca": ipca, "cpi": cpi})
    df["cpi"] = df["cpi"].interpolate(limit_area="inside")    # out/2025 sem CPI (paralisação do governo dos EUA): interpolado
    df = df.dropna()
    base_i, base_c = df["ipca"].iloc[-1], df["cpi"].iloc[-1]
    df["rs"] = df["brent"] * df["ptax"]
    df["rs_real"] = df["rs"] * base_i / df["ipca"]
    df["us_real"] = df["brent"] * base_c / df["cpi"]
    df["fx_real"] = df["rs_real"] / df["us_real"]
    anual = df.groupby(df.index.year).mean()
    d10 = anual.loc[2016:2025]
    ltm = df.loc["2025-07":"2026-06"]
    return dict(
        anual=anual, mensal=df, base=df.index[-1].strftime("%m/%Y"),
        barril_meio=d10["rs_real"].mean(), brent_meio_real=d10["us_real"].mean(), fx_meio_real=d10["fx_real"].mean(),
        brent_meio_nominal=d10["brent"].mean(), barril_ltm=ltm["rs"].mean(), brent_ltm=ltm["brent"].mean(), ptax_ltm=ltm["ptax"].mean(),
        brent_ultimo=(b["d"].iloc[-1].strftime("%d/%m/%Y"), b["v"].iloc[-1]),
        deflator={str(a): base_i / anual.loc[a, "ipca"] for a in range(2016, 2026)},
    )


M = macro()
FX_SPOT = 5.216                       # R$/US$ comercial 02/10/2026 (BCB, citado no PDF rev. 03/10 do Lote 3)
FATOR_BARRIL = M["barril_meio"] / M["barril_ltm"]


def barril(ini, fim):
    """Brent × PTAX médio (R$/bbl nominal) entre dois meses 'AAAA-MM'."""
    a = M["mensal"].loc[ini:fim]
    return (a["brent"] * a["ptax"]).mean()


def base_ep(tk):
    """(receita de meio de ciclo, D&A anual atual) em R$ mil — doutrina §11.1, E&P."""
    ltm = ltm_de(CVM[tk])
    if tk != "PRIO3":
        return ltm["receita"] * FATOR_BARRIL, ltm["da"]
    from coletar_cvm import itr_ytd
    t1, s1 = itr_ytd(tk, 2026, 3), itr_ytd(tk, 2026, 6)
    r1, r2 = t1["receita"], s1["receita"] - t1["receita"]
    rec = 2 * (r1 * M["barril_meio"] / barril("2026-01", "2026-03") + r2 * M["barril_meio"] / barril("2026-04", "2026-06"))
    return rec, 2 * s1["da"]


BASE = {tk: base_ep(tk) for tk in ("PETR4", "PRIO3", "RECV3")}


def receita_ep(tk):
    return BASE[tk][0]


def da_ep(tk):
    return BASE[tk][1] / BASE[tk][0]


# Passivo atuarial (pensão e saúde, R$ 92,5 bi: 2.01.06.02.04 + 2.02.04.02.04 do ITR de jun/2026) NÃO entra na ponte: o custo atuarial
# (R$ 9,7 bi em 2025, DFC 6.01.01.02) já é despesa dentro do EBIT normalizado — capitalizado ao WACC equivale ao próprio déficit; subtraí-lo
# contaria duas vezes (achado do adversário, 05/10). Provisão de abandono (R$ 153,7 bi) também fora: o custo de desmantelamento é capitalizado
# e depreciado na D&A, que já está no EBIT — os dois aparecem como sensibilidade na ficha.
PETR_ATUARIAL = (5_710_000 + 86_743_000)
PETR_ABANDONO = (14_674_000 + 139_038_000)

PETR_CENARIOS = [
    dict(nome="Sem nova interferência além da já precificada (subvenção ao diesel paga pela União; imposto de exportação expira)", prob=0.50, perda=0.0),
    dict(nome="Interferência moderada: preço 15–25% abaixo da paridade por ~2 anos + capex de baixo retorno (refino, fertilizantes) — V1 + V3",
         prob=0.35, perda=0.10),
    dict(nome="Repetição de 2011–14: preço abaixo da paridade por 3–4 anos, alavancagem e corte de dividendo — V1 + V3 + V5", prob=0.15, perda=0.30),
]

# Preços = fechamento oficial (PREULT do COTAHIST) de 02/10/2026 — data e fonte em precos_hall.py (AUD-67).
EMPRESAS = [
    Industrial("PETR4", "Petrobras (PN)", "ciclica", preco=51.17, n_acoes=acoes("PETR4"), g_real=0.01, jcp_share=jcp("PETR4"),
               # AUD-03 (08/10/2026): a margem de E&P é EBITDA − D&A ATUAL, e a D&A atual já tem a depreciação do direito de uso;
               # o EBITDA de 2016–18 é pré-IFRS 16 e carrega o aluguel como custo → aluguel descontado duas vezes (as 3 menores margens)
               anos_ciclo=[str(a) for a in range(2019, 2026)], anos_outras=[str(a) for a in range(2016, 2026)],
               janela_razao="IFRS 16 adotado em 2019: o EBITDA de 2016–18 traz o aluguel como custo e a D&A atual já traz a depreciação "
                            "do direito de uso (doutrina §11.1 DCF e §11.4.2); 2019–25 cobre vale (2020) e pico (2022) do Brent",
               receita_meio=receita_ep("PETR4"), da_receita=da_ep("PETR4"), outras_liquidas=True,
               desconto_controlador={"tipo": "cenarios", "cenarios": PETR_CENARIOS,
                                     "razao": "V1 (preços 2011–14; diesel abaixo da paridade desde mar/26), V3 (refino, fertilizantes), V5 (extraordinários)"},
               controlador_discricionario=True,
               controlador_discricionario_fonte="interferência consumada declarada no desconto do lote (critério provisório v2.3, até o "
                                                "dossiê): União — V1 preços 2011–14 e diesel abaixo da paridade desde mar/26, V3, V5",
               qualitativo=QUAL(4, 2, 1, 2, 2)),
    Industrial("PRIO3", "PRIO", "ciclica", preco=63.01, n_acoes=acoes("PRIO3"), g_real=0.01, jcp_share=jcp("PRIO3"),
               anos_ciclo=[str(a) for a in range(2019, 2026)], anos_outras=[str(a) for a in range(2016, 2026)],
               janela_razao="perímetro operado atual: Frade a partir de 2019 (receita de R$ 849 mi em 2018 para R$ 1,64 bi em 2019); antes de 2019 a escala e os ativos são de outra empresa",
               receita_meio=receita_ep("PRIO3"), da_receita=da_ep("PRIO3"), outras_liquidas=True, qualitativo=QUAL(3, 4, 4, 1, 3),
               aliquota_fase=ALIQUOTA_FASE["PRIO3"]),   # v2.3 (08/10): prejuízo fiscal com uso projetado até 2032 (fiscal.py)
    Industrial("RECV3", "PetroReconcavo", "ciclica", preco=11.20, n_acoes=acoes("RECV3"), g_real=-0.03, jcp_share=jcp("RECV3"),
               anos_ciclo=[str(a) for a in range(2020, 2026)], receita_meio=receita_ep("RECV3"), da_receita=da_ep("RECV3"), declinio_sem_liberacao=True,
               janela_razao="a série da CVM começa em 2020 (IPO em set/2020); não há exercício anterior",
               qualitativo=QUAL(1, 2, 3, 2, 2)),
    Industrial("UGPA3", "Ultrapar", "servicos", preco=38.61, n_acoes=acoes("UGPA3"), g_real=0.01, jcp_share=jcp("UGPA3"),
               anos_ciclo=[str(a) for a in range(2021, 2026)], deflator=M["deflator"], capex_ciclico=True,
               janela_razao="perímetro comparável: Oxiteno e Extrafarma descontinuadas em 2021 — antes a margem é de outro conjunto de negócios",
               qualitativo=QUAL(3, 3, 4, 3, 3)),
    Industrial("VBBR3", "Vibra Energia", "servicos", preco=38.15, n_acoes=acoes("VBBR3"), g_real=0.01, jcp_share=jcp("VBBR3"),
               anos_ciclo=[str(a) for a in range(2020, 2026)], deflator=M["deflator"], capex_ciclico=True,
               janela_razao="gestão privada desde jul/2019 (saída da Petrobras): a margem anterior é de empresa estatal",
               outras_liquidas=True, anos_outras=[str(a) for a in range(2016, 2026)], fora_circulo=False,
               qualitativo=QUAL(3, 3, 4, 3, 2)),
]
FORA_DO_HALL = {"VBBR3"}

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Ke nominal {MK.ke_nom:.2%} | rf nom {MK.rf_nom:.2%} | RF real líq {MK.rf_liq_real:.2%} | π {MK.pi:.2%}")
    print(f"Barril meio R$ {M['barril_meio']:.0f} (Brent real US$ {M['brent_meio_real']:.1f} × FX real {M['fx_meio_real']:.2f}; nominal 10a US$ {M['brent_meio_nominal']:.1f}) "
          f"| LTM R$ {M['barril_ltm']:.0f} (Brent {M['brent_ltm']:.1f} × {M['ptax_ltm']:.3f}) | fator {FATOR_BARRIL:.3f} | último Brent {M['brent_ultimo']}")
    print("base E&P:", {k: (round(v[0] / 1e6, 2), round(v[1] / v[0], 3)) for k, v in BASE.items()})
    for e in EMPRESAS:
        r = avaliar(e, MK)
        anc = " | ".join(f"{k}: {x:.2f}" for k, x in r["ancoras"].items())
        ki = r["ke_implicito"]; gi = r["g_implicito"]
        print(f"{e.ticker:6} P {e.preco:6.2f} central {r['central']:6.2f} P/C {r['pc']:.2f} {r['palavra']:6} disp {r['dispersao']:.2f} desc {r['desc_controlador']:.1%} | {anc}")
        print(f"       WACC {r['wacc']:.1%} ROIC {r['roic']:.1%} margem {r['m']:.1%} (p25 {r['op']['m25']:.1%} p75 {r['op']['m75']:.1%}) aj {r['op']['ajuste_manut']:.1%} "
              f"rec_meio {r['op']['receita_meio']/1e6:.1f}bi IR {r['aliquota']:.0%} DL {r['dl']/1e6:.1f}bi DL/EBITDA {r['dl_ebitda'] and round(r['dl_ebitda'],2)} "
              f"norm {r['dl_ebitda_norm'] and round(r['dl_ebitda_norm'],2)} cob {r['cobertura_juros'] and round(r['cobertura_juros'],1)} nao_rec {list(r['op']['nao_rec'])}")
        print(f"       Ke* {ki and f'{ki:.1%}'} g* {gi and f'{gi:.1%}'} | Bogle {r['bogle_nom']:.1%} liq real {r['bogle_liq_real']:.1%} RF {r['vence_rf']}/{r['rf_sem_rerating']} | "
              f"OE {r['oe_norm'] and round(r['oe_norm']/1e3)} mi DPA5 {r['dpa5']:.2f} FCFE/ação {r['fcfe_acao']:.2f} coberto {r['coberto']} | "
              f"Z'' {r['altman']:.2f} {r['altman_zona']} F {r['piotroski']} M {r['beneish'] and round(r['beneish'],2)} | EY {r['ey'] and round(100*r['ey'],1)} ROC {r['roc'] and round(100*r['roc'],1)} | nota {r['notas']['geral']:.1f}")
        print(f"       margens {[round(100*x,1) for x in r['op']['margens']]}")
