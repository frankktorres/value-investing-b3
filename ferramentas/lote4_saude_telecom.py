"""Lote 4 — Saúde, telecom e blue chips · data-base 02/10/2026 (preços do PDF rev. 03/10) · doutrina v2.2.

Demonstrações: CVM (DFP 2016–25 + ITR, 12m até jun/2026). Preço: PDF rev. 03/10 (fechamento de 02/10). Ações: composição do capital do ITR de
jun/2026 (CVM), sem tesouraria. Proventos: StatusInvest por data-com, com as correções abaixo. Controladores: FRE 2026 da CVM (posição acionária).
Premissas declaradas ANTES do veredito:
  · IFRS 16 desde 2019: TIMS3, VIVT3 e FLRY3 têm arrendamento relevante dentro da dívida (2.01.04.03/2.02.01.03 ou linha própria). A margem de
    antes de 2019 traz o aluguel dentro do EBIT — usar essa margem E a dívida de arrendamento de hoje contaria o aluguel duas vezes. Janela da
    margem = 2019–25; a mediana de "outras receitas" segue com 10 anos (doutrina §11.1).
  · "Outras" líquidas (3.04.04 + 3.04.05) no lote todo: TIM e Vivo lançam pares de ganho e perda (TIM 2021: +2,85 / −2,35 bi); a bruta
    tiraria o ganho e deixaria a perda. TIMS3 e VIVT3: capex de rede = manutenção (reposição tecnológica 4G/5G/fibra; a receita cresce por
    preço/inflação, não por capacidade) — mesma regra da cíclica (mediana de capex ÷ receita na janela).
  · Owner Earnings com o aluguel pago descontado (IFRS 16: a D&A somada de volta tem a depreciação do direito de uso). VIVT3 e WEGE3: proxy
    (ver arrendamento_pago_proxy). FLRY3: a linha 'Pagamento de Arrendamento Mercantil' pode incluir juros (inferência do adversário) —
    mantida inteira (conservador); afeta só o OE e a cobertura do provento.
  · FLRY3: Pardini incorporado em ago/2023 (troca de ações). Receita de base = média de 2024, 2025 e 12m (perímetro atual); 2023 tem 5 meses.
  · Alíquota (doutrina §2, v2.3: mediana de 5 anos sem piso; crédito com prazo = fase): ABEV3 usa a média de 2024–25 (21%) — a Lei
    14.789/2023 passou a tributar a subvenção de ICMS a partir de 2024, e 2021–23 (1–5%) não representam mais o normal; o OE é refeito a
    21% nos anos antigos. HYPE3: crédito com prazo (ágio até 2030, `fiscal.py`) → efetiva até 2030 e 34% depois (até a v2.2: piso de 15%).
    TIMS3: mediana 5,4% ("benefício regional + JCP", texto deste lote, sem fonte nem prazo conferidos) → 34% até o dossiê.
  · WEGE3 (compounder, ROIC > WACC): DCF em 2 estágios — g real dos 10 primeiros anos = g sustentável (ROE mediano de 5 anos × retenção
    recorrente, deflacionado pela inflação implícita), depois g real 2% (PIB real de longo prazo, teto da doutrina). DCF reverso devolve o g dos
    10 anos que o preço embute. EPV e Owner Earnings seguem sem crescimento de 1º estágio (é o que eles medem).
  · Defasagem do provento (doutrina §6.3, a valor presente ao Ke nominal): HYPE3 18 meses (JCP de 2026 pago até 31/12/2027) · VIVT3 10 (JCP
    pago até 30/04/2027) · FLRY3 9 (dividendo de dez/25 em 3 parcelas até set/2027; JCP antecipado) · WEGE3 9 (JCP de 2026 pago em 10/03/2027;
    extraordinário em 3 parcelas até 2028) · ABEV3 6 · TIMS3 4 (JCP de set/26 pago até 22/01/2027). ITSA4: ~2 meses, desprezado.
  · Proventos: VIVT3 sem "Amortização" (redução de capital, não lucro — §6.4); ABEV3 JCP de 22/06/2026 = R$ 0,0449 (a StatusInvest grava
    0,449, erro de vírgula confirmado no RI pelo PDF 03/10).
  · ITSA4 (holding, doutrina §11.2: SOTP + DDM): SOTP = patrimônio da holding (controladora, jun/26) − Itaú a valor contábil + Itaú ao valor
    central da casa (ITUB4 do Lote 1, recalculado ao mesmo Ke) − custo da holding capitalizado (G&A 12m ÷ Ke real) − PIS/Cofins sobre o
    JCP recebido até o fim de 2027 (R$ 860 mi/ano × 15 meses, a valor presente). Participação no Itaú pelo
    FRE 2026: 2.202,6 mi de ações diretas + 66,53% das 2.905,1 mi da IUPAR = 4.135,4 mi (37,50%). Demais participações (Alpargatas, Dexco,
    Motiva, Aegea, Copa, NTS) a valor contábil — a casa não tem valor justo delas (conservador: o PDF cita R$ 16,6 bi a mercado, marcado [H]).
"""
import io
import json
import pathlib
import statistics as st
import sys
import zipfile

import pandas as pd

from fiscal import ALIQUOTA_FASE
from lote1_bancos import EMPRESAS as LOTE1
from lote1_bancos import MK
from lote2_energia import pl_hist
from lote3_agro import jcp
from motor_financeiras import Financeira, central_ao_ke
from motor_financeiras import avaliar as avaliar_fin
from motor_nao_financeiras import ANOS, CVM, SI, Industrial, avaliar

AQUI = pathlib.Path(__file__).parent
ZIP = AQUI / "dados" / "cvm"
QUAL = lambda moat, gestao, controlador, ciclo, fisher: dict(moat=moat, gestao=gestao, controlador=controlador, ciclo=ciclo, fisher=fisher)
PRECO = {"TIMS3": 18.55, "VIVT3": 30.14, "ITSA4": 14.67, "FLRY3": 23.50, "HYPE3": 25.16, "ABEV3": 15.84, "WEGE3": 51.45}   # fech. 02/10 [PDF 03/10]
NOME_CVM = {"TIMS3": "TIM S.A.", "VIVT3": "TELEF", "FLRY3": "FLEURY", "HYPE3": "HYPERA", "ABEV3": "AMBEV", "WEGE3": "WEG S.A.",
            "ITSA4": "ITAÚSA", "ITUB": "ITAU UNIBANCO HOLDING"}
IFRS16 = [str(a) for a in range(2019, 2026)]
# §11.4: janela pós-quebra declarada. A quebra é a adoção do IFRS 16 em 2019 — antes disso o aluguel está dentro do EBIT e usar
# essa margem junto com a dívida de arrendamento de hoje contaria o aluguel duas vezes (§11.1).
RAZAO_IFRS16 = ("IFRS 16 adotado em 2019: antes de 2019 o aluguel está dentro do EBIT e usar essa margem com a dívida de "
                "arrendamento de hoje contaria o aluguel duas vezes (§11.1)")


def _csv(arq, nome):
    z = zipfile.ZipFile(ZIP / arq)
    n = [x for x in z.namelist() if nome in x][0]
    return pd.read_csv(io.BytesIO(z.read(n)), sep=";", encoding="latin-1", dtype=str)


def acoes_jun26(tk):
    """Ações em circulação em 30/06/2026 (ITR, composição do capital), sem tesouraria."""
    df = _csv("itr_2026.zip", "composicao")
    d = df[df["DENOM_CIA"].str.upper().str.startswith(NOME_CVM[tk]) & (df["DT_REFER"] == "2026-06-30")].iloc[-1]
    n = float(d["QT_ACAO_TOTAL_CAP_INTEGR"]) - float(d["QT_ACAO_TOTAL_TESOURO"])
    return n * 1000 if n < 1e8 else n          # Ambev, Itaúsa e Itaú informam a quantidade em milhares


N = {tk: acoes_jun26(tk) for tk in PRECO}
N["ITUB"] = acoes_jun26("ITUB")


# ---------------------------------------------------------------- proventos corrigidos (StatusInvest)
def corrigir_proventos():
    for tk in PRECO:
        s = SI[tk]
        dpa, jc = {}, {}
        for e in s["eventos"]:
            if not e["data_com"]:
                continue
            tipo, val = (e["tipo"] or ""), e["valor"] or 0
            if tk == "VIVT3" and tipo.startswith("Amortiza"):
                continue                                  # redução de capital (§6.4)
            if tk == "ABEV3" and e["data_com"] == "22/06/2026" and abs(val - 0.449) < 0.001:
                val = 0.0449                              # erro de vírgula da StatusInvest [PDF 03/10, RI]
            a = e["data_com"][-4:]
            dpa[a] = dpa.get(a, 0) + val
            if "JCP" in tipo.upper():
                jc[a] = jc.get(a, 0) + val
        s["dpa_por_ano_datacom"], s["jcp_por_ano_datacom"] = dict(sorted(dpa.items())), dict(sorted(jc.items()))


corrigir_proventos()


def arrendamento_pago_proxy():
    """Owner Earnings (IFRS 16): o aluguel pago sai do OE. VIVT3 e WEGE3 pagam o arrendamento dentro da linha de amortização de empréstimos da DFC
    → proxy = parcela circulante do passivo de arrendamento no fim do ano anterior (principal que vence no ano), limitada ao principal total pago
    (6.03 pagamento/amortização, sem juros) menos a dívida financeira circulante do ano anterior (achado do adversário 05/10: o proxy da Vivo
    passava do principal pago). TIMS3 2021: a DFC desse ano não traz a linha → média de 2020 e 2022."""
    for tk, cod in {"VIVT3": "017671", "WEGE3": "005410"}.items():
        for a in range(2020, 2026):
            bp = _csv(f"dfp_{a - 1}.zip", f"BPP_con_{a - 1}")
            bp = bp[(bp["CD_CVM"].str.zfill(6) == cod) & bp["ORDEM_EXERC"].str.startswith("Ú") & bp["CD_CONTA"].str.startswith("2.01")]
            bp = bp.assign(v=pd.to_numeric(bp["VL_CONTA"]))
            arr = bp[bp["DS_CONTA"].str.contains("rrendamento", na=False) & ~bp["DS_CONTA"].str.contains("ulta|rovis", na=False)]
            arr = arr[[not any(o != c and o.startswith(c + ".") for o in arr["CD_CONTA"]) for c in arr["CD_CONTA"]]]
            div_cp = bp[bp["CD_CONTA"].isin(["2.01.04.01", "2.01.04.02"])]["v"].sum()
            fc = _csv(f"dfp_{a}.zip", f"DFC_MI_con_{a}")
            fc = fc[(fc["CD_CVM"].str.zfill(6) == cod) & fc["ORDEM_EXERC"].str.startswith("Ú") & fc["CD_CONTA"].str.startswith("6.03")]
            fc = fc.assign(v=pd.to_numeric(fc["VL_CONTA"]))
            pago = -fc[fc["DS_CONTA"].str.contains(r"principal|amortiza|arrendament|empr[eé]stim", case=False, na=False)
                       & ~fc["DS_CONTA"].str.contains(r"juros|dividend|a[cç][oõ]es|derivativ|acionista|capital", case=False, na=False)
                       & (fc["v"] < 0)]["v"].sum()
            CVM[tk]["anual"][str(a)]["arrendamento_pago"] = max(0.0, min(arr["v"].sum(), pago - div_cp))
    t = CVM["TIMS3"]["anual"]
    t["2021"]["arrendamento_pago"] = (t["2020"]["arrendamento_pago"] + t["2022"]["arrendamento_pago"]) / 2


arrendamento_pago_proxy()



def receita_media(tk, anos, ltm=True):
    a, l = CVM[tk]["anual"], CVM[tk]["ltm_2T26"]
    xs = [a[y]["receita"] for y in anos] + ([l["receita"]] if ltm else [])
    return sum(xs) / len(xs)


# ---------------------------------------------------------------- WEGE3: g do 1º estágio
def g1_sustentavel(tk):
    """g sustentável nominal = ROE mediano 2021–25 × (1 − payout recorrente mediano 2021–25), deflacionado pela π implícita.
    Payout recorrente = DPA ÷ LPA, sem o extraordinário de dez/2025 (R$ 1,2385 em 3 parcelas — PDF 03/10). A série da StatusInvest só traz a 1ª
    parcela (R$ 0,4128, data-com 19/12/2025) — é ela que sai (achado do adversário 05/10)."""
    i = SI[tk]["indicadores"]
    roe = st.median(i["roe"]["anos"][str(a)] for a in range(2021, 2026)) / 100
    dpa = dict(SI[tk]["dpa_por_ano_datacom"])
    dpa["2025"] = dpa["2025"] - 0.4128
    pay = st.median(dpa[str(a)] / i["lpa"]["anos"][str(a)] for a in range(2021, 2026))
    g_nom = roe * (1 - pay)
    return (1 + g_nom) / (1 + MK.pi) - 1, roe, pay


WEG_G1, WEG_ROE5, WEG_PAYOUT = g1_sustentavel("WEGE3")
ZERO = lambda razao: {"tipo": "zero", "razao": razao}

EMPRESAS = [
    Industrial("TIMS3", "TIM Brasil", "servicos", preco=PRECO["TIMS3"], n_acoes=N["TIMS3"], anos_ciclo=IFRS16, anos_outras=ANOS, outras_liquidas=True, capex_ciclico=True, janela_razao=RAZAO_IFRS16,
               spread_kd=0.01, g_real=0.01, jcp_share=jcp("TIMS3"), pl_hist=pl_hist("TIMS3"), defasagem_meses=4,
               defasagem_fonte="JCP de set/2026 pago até 22/01/2027 (calendário declarado, PDF rev. 03/10)",
               desconto_controlador=ZERO("nenhuma interferência consumada; Poste Italiane (estatal italiana) controla a TI desde 18/09/2026 — risco "
                                         "prospectivo V4/V5 sem evento; tag along pendente é opção, não desconto"),
               qualitativo=QUAL(3, 4, 3, 4, 3)),
    Industrial("VIVT3", "Telefônica Brasil (Vivo)", "servicos", preco=PRECO["VIVT3"], n_acoes=N["VIVT3"], anos_ciclo=IFRS16, anos_outras=ANOS, outras_liquidas=True, capex_ciclico=True, janela_razao=RAZAO_IFRS16,
               spread_kd=0.01, g_real=0.01, jcp_share=jcp("VIVT3"), pl_hist=pl_hist("VIVT3"), defasagem_meses=10,
               defasagem_fonte="JCP declarado pago até 30/04/2027 (calendário declarado, PDF rev. 03/10)",
               desconto_controlador=ZERO("nenhuma interferência consumada pela Telefónica S.A. (39,3% do capital pelo FRE 2026; controle com acordo)"),
               qualitativo=QUAL(4, 3, 3, 4, 3)),
    Industrial("FLRY3", "Grupo Fleury", "servicos", preco=PRECO["FLRY3"], n_acoes=N["FLRY3"], anos_ciclo=IFRS16, anos_outras=ANOS, outras_liquidas=True, janela_razao=RAZAO_IFRS16,
               receita_meio=receita_media("FLRY3", ["2024", "2025"]), spread_kd=0.015, g_real=0.01, jcp_share=jcp("FLRY3"),
               pl_hist=pl_hist("FLRY3"), defasagem_meses=9,
               defasagem_fonte="dividendo de dez/2025 em 3 parcelas até set/2027, mais JCP antecipado (calendário declarado, PDF rev. 03/10)",
               desconto_controlador=ZERO("controle compartilhado (médicos fundadores + Bradesco Seguros), sem interferência consumada"),
               qualitativo=QUAL(3, 3, 4, 4, 3)),
    Industrial("HYPE3", "Hypera Pharma", "servicos", preco=PRECO["HYPE3"], n_acoes=N["HYPE3"], outras_liquidas=True, spread_kd=0.015, g_real=0.01,
               aliquota_fase=ALIQUOTA_FASE["HYPE3"], jcp_share=jcp("HYPE3"), pl_hist=pl_hist("HYPE3"),   # v2.3: crédito com prazo
               defasagem_meses=18, defasagem_fonte="JCP de 2026 pago até 31/12/2027 (calendário declarado, PDF rev. 03/10)",
               desconto_controlador=ZERO("controlador privado (J. A. de Queiroz Filho + Maiorem, 39,3% pelo FRE 2026), sem extração consumada registrada; "
                                         "a defasagem de 15–21 meses do JCP já está no valor presente do provento"),
               qualitativo=QUAL(3, 2, 3, 4, 2)),
    Industrial("ABEV3", "Ambev", "servicos", preco=PRECO["ABEV3"], n_acoes=N["ABEV3"], outras_liquidas=True, spread_kd=0.005, g_real=0.01,
               aliquota=sum(-CVM["ABEV3"]["anual"][y]["ir"] / CVM["ABEV3"]["anual"][y]["lair"] for y in ("2024", "2025")) / 2,
               # ABEV3 (Etapa 2/F2): os 6 meses não tinham evento declarado — §6.3 manda usar o medido na StatusInvest (1,5 mês)
               jcp_share=jcp("ABEV3"), pl_hist=pl_hist("ABEV3"),
               desconto_controlador=ZERO("AB InBev sem interferência consumada; contratos com a controladora (V4) já estão no EBIT histórico"),
               qualitativo=QUAL(5, 3, 3, 4, 3)),
    Industrial("WEGE3", "WEG", "servicos", preco=PRECO["WEGE3"], n_acoes=N["WEGE3"], outras_liquidas=True, spread_kd=0.005, g_real=0.02, g1_real=WEG_G1, anos_g1=10,
               jcp_share=jcp("WEGE3"), pl_hist=pl_hist("WEGE3"), defasagem_meses=9,
               defasagem_fonte="JCP de 2026 pago em 10/03/2027 e extraordinário em 3 parcelas até 2028 (calendário declarado, PDF rev. 03/10)",
               desconto_controlador=ZERO("famílias fundadoras, sem conflito identificado"),
               qualitativo=QUAL(5, 5, 5, 3, 5)),
]


# ---------------------------------------------------------------- ITSA4 (holding)
def itausa_individual():
    """Controladora (individual) de 30/06/2026 e G&A de 12 meses, do ITR/DFP da CVM."""
    def bp(nome):
        d = _csv("itr_2026.zip", f"{nome}_ind_2026")
        d = d[(d["CD_CVM"].str.zfill(6) == "007617") & (d["DT_REFER"] == "2026-06-30") & d["ORDEM_EXERC"].str.startswith("Ú")]
        return {r.CD_CONTA: float(r.VL_CONTA) for r in d.itertuples()}

    def dre(arq, ano, mes=None):
        d = _csv(arq, f"DRE_ind_{ano}")
        d = d[(d["CD_CVM"].str.zfill(6) == "007617") & d["ORDEM_EXERC"].str.startswith("Ú")]
        if mes:
            d = d[(d["DT_REFER"].str[5:7] == mes) & (d["DT_INI_EXERC"].str[5:7] == "01")]
        return {r.CD_CONTA: float(r.VL_CONTA) for r in d.itertuples()}
    a, p = bp("BPA"), bp("BPP")
    f25, y26, y25 = dre("dfp_2025.zip", 2025), dre("itr_2026.zip", 2026, "06"), dre("itr_2025.zip", 2025, "06")
    ltm = lambda k: f25[k] + y26[k] - y25[k]
    return dict(pl=p["2.03"], investimentos=a["1.02.02"], caixa=a["1.01.01"] + a["1.01.02"], divida=p["2.01.04"] + p["2.02.01"],
                ga_12m=-ltm("3.04.02"), lucro_12m=ltm("3.11"), equivalencia_12m=ltm("3.04.06"), res_fin_12m=ltm("3.06"))


def itau_pl_controlador():
    d = _csv("itr_2026.zip", "BPP_con_2026")
    d = d[(d["CD_CVM"].str.zfill(6) == "019348") & (d["DT_REFER"] == "2026-06-30") & d["ORDEM_EXERC"].str.startswith("Ú")]
    v = {r.CD_CONTA: float(r.VL_CONTA) for r in d.itertuples()}
    return v["2.08"] - v["2.08.09"]


def acoes_itau_da_itausa():
    """FRE 2026 (CVM), posição acionária do Itaú Unibanco: Itaúsa direta + fatia da Itaúsa na IUPAR × ações da IUPAR."""
    df = _csv("fre_2026.zip", "posicao_acionaria_2026")
    d = df[df["Nome_Companhia"].str.contains("ITAU UNIBANCO HOLDING", case=False, na=False)]
    d = d[d["Versao"] == d["Versao"].max()]
    q = lambda r: float(r["Quantidade_Total_Acoes_Circulacao"])
    direta = q(d[d["Acionista"].str.startswith("Itaúsa") & d["Acionista_Relacionado"].isna()].iloc[0])
    iupar = q(d[d["Acionista"].str.startswith("IUPAR") & d["Acionista_Relacionado"].isna()].iloc[0])
    fatia = float(d[d["Acionista"].str.startswith("Itaúsa") & (d["Acionista_Relacionado"].fillna("").str.startswith("IUPAR"))]
                  .iloc[0]["Percentual_Total_Acoes_Circulacao"]) / 100
    return direta + fatia * iupar, direta, iupar, fatia


ITSA = itausa_individual()
ITSA["pl_itau"] = itau_pl_controlador()
ITSA["acoes_itau"], ITSA["acoes_itau_diretas"], ITSA["acoes_iupar"], ITSA["fatia_iupar"] = acoes_itau_da_itausa()
ITSA["pct_itau"] = ITSA["acoes_itau"] / N["ITUB"]
ITSA["itau_contabil"] = ITSA["pct_itau"] * ITSA["pl_itau"]                 # R$ mil (equivalência ≈ % × PL do Itaú)
ITSA["outras_contabil"] = ITSA["investimentos"] - ITSA["itau_contabil"]
ITUB4 = next(e for e in LOTE1 if e.ticker == "ITUB4")
PIS_COFINS_JCP = 860_000      # R$ mil/ano, PIS/Cofins sobre JCP recebido do Itaú; fim previsto em 2027 [PDF 03/10, call do 2T26]


def sotp_partes(mk):
    itau_ps = central_ao_ke(ITUB4, mk, mk.ke_nom)
    itau_justo = ITSA["acoes_itau"] * itau_ps / 1000                         # R$ mil
    custo = ITSA["ga_12m"] / mk.ke_real                                      # perpetuidade real do G&A da holding
    # PIS/Cofins sobre o JCP recebido: ~R$ 860 mi/ano até a mudança de 2027 [PDF 03/10] → 15 meses (out/26–dez/27), conservador, a VP no meio
    pis = PIS_COFINS_JCP * 1.25 / (1 + mk.ke_nom) ** (7.5 / 12)
    total = ITSA["pl"] - ITSA["itau_contabil"] + itau_justo - custo - pis
    return dict(itau_ps=itau_ps, itau_justo=itau_justo, custo=custo, pis=pis, total=total, por_acao=total * 1000 / N["ITSA4"])


def itsa():
    i = SI["ITSA4"]["indicadores"]
    roe_lp = st.median(i["roe"]["anos"][str(a)] for a in range(2016, 2026)) / 100
    dpa = SI["ITSA4"]["dpa_por_ano_datacom"]
    payout = st.median(dpa[str(a)] / i["lpa"]["anos"][str(a)] for a in range(2021, 2026))
    vpa = ITSA["pl"] * 1000 / N["ITSA4"]
    return Financeira("ITSA4", "Itaúsa", "holding", preco=PRECO["ITSA4"], vpa=vpa, lpa_12m=ITSA["lucro_12m"] * 1000 / N["ITSA4"],
                      roe_lp=roe_lp, roe_inicio=ITSA["lucro_12m"] / ITSA["pl"], payout=payout,
                      dpa_medio_5a=sum(dpa.get(str(a), 0) for a in range(2021, 2026)) / 5, jcp_share=jcp("ITSA4"), pl_hist=pl_hist("ITSA4"),
                      anos_pagos_10=sum(1 for a in range(2016, 2026) if dpa.get(str(a), 0) > 0),
                      solidez_manual=9.0,      # holding com caixa ≥ dívida (jun/26) e dividendos do Itaú > proventos pagos; sem prudencial próprio
                      qualitativo=QUAL(4, 3, 3, 3, 3), sotp=lambda mk: sotp_partes(mk)["por_acao"],
                      desconto_controlador=ZERO("famílias Setubal/Villela sem extração consumada; a alocação em não financeiras com retorno baixo "
                                                "(NTS, Aegea) já está no valor contábil delas e no ROE da holding")), roe_lp, payout


ITSA4, ITSA_ROE_LP, ITSA_PAYOUT = itsa()

if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print(f"Ke nominal {MK.ke_nom:.2%} | Ke real {MK.ke_real:.2%} | rf nom {MK.rf_nom:.2%} | RF real líq {MK.rf_liq_real:.2%} | π {MK.pi:.2%}")
    print("ações (mi):", {k: round(v / 1e6, 1) for k, v in N.items()})
    print(f"WEGE3 g1 real {WEG_G1:.2%} (ROE5 {WEG_ROE5:.1%}, payout {WEG_PAYOUT:.1%})")
    for e in EMPRESAS:
        r = avaliar(e, MK)
        anc = " | ".join(f"{k}: {x:.2f}" for k, x in r["ancoras"].items())
        ki, gi = r["ke_implicito"], r["g_implicito"]
        print(f"{e.ticker:6} P {e.preco:6.2f} central {r['central']:6.2f} P/C {r['pc']:.2f} {r['palavra']:6} disp {r['dispersao']:.2f} | {anc}")
        print(f"       WACC {r['wacc']:.1%} ROIC {r['roic']:.1%} margem {r['m']:.1%} (p25 {r['op']['m25']:.1%} p75 {r['op']['m75']:.1%}) aj {r['op']['ajuste_manut']:.1%} "
              f"rec_meio {r['op']['receita_meio']/1e6:.2f}bi IR {r['aliquota']:.0%} DL {r['dl']/1e6:.2f}bi DL/EBITDA {r['dl_ebitda'] and round(r['dl_ebitda'],2)} "
              f"cob {r['cobertura_juros'] and round(r['cobertura_juros'],1)} nao_rec {list(r['op']['nao_rec'])}")
        print(f"       Ke* {ki and f'{ki:.1%}'} g* {gi and f'{gi:.1%}'} | Bogle {r['bogle_nom']:.1%} liq real {r['bogle_liq_real']:.1%} RF {r['vence_rf']}/{r['rf_sem_rerating']} trava {r['trava']} | "
              f"OE {r['oe_norm'] and round(r['oe_norm']/1e3)} mi DPA5 {r['dpa5']:.2f} sust {r['dpa_sust']:.2f} vp {r['dpa_sust_vp']:.2f} FCFE/ação {r['fcfe_acao']:.2f} coberto {r['coberto']} | "
              f"Z'' {r['altman']:.2f} {r['altman_zona']} F {r['piotroski']} M {r['beneish'] and round(r['beneish'],2)} | EY {r['ey'] and round(100*r['ey'],1)} ROC {r['roc'] and round(100*r['roc'],1)} | nota {r['notas']['geral']:.1f}")
        print(f"       margens {[round(100*x,1) for x in r['op']['margens']]} | LPA norm {r['lpa_norm']:.2f} VPA {r['vpa']:.2f} Graham-BR {r['graham_br'] and round(r['graham_br'],2)}")
    r = avaliar_fin(ITSA4, MK)
    s = sotp_partes(MK)
    print(f"ITSA4  P {ITSA4.preco:.2f} central {r['central']:.2f} P/C {r['pc']:.2f} {r['palavra']} | " + " | ".join(f"{k}: {x:.2f}" for k, x in r["ancoras"].items())
          + f" | Ke* {r['ke_implicito'] and round(100*r['ke_implicito'],1)} | Bogle {r['bogle_nom']:.1%} RF {r['vence_rf']}/{r['rf_sem_rerating']} | nota {r['notas']['geral']:.1f}")
    print(f"       ações Itaú {ITSA['acoes_itau']/1e6:.1f} mi ({ITSA['pct_itau']:.2%}) × ITUB4 central {s['itau_ps']:.2f} = {s['itau_justo']/1e6:.1f} bi | contábil Itaú "
          f"{ITSA['itau_contabil']/1e6:.1f} bi | outras {ITSA['outras_contabil']/1e6:.1f} bi | PL holding {ITSA['pl']/1e6:.1f} bi | caixa {ITSA['caixa']/1e6:.2f} dívida "
          f"{ITSA['divida']/1e6:.2f} | G&A {ITSA['ga_12m']/1e3:.0f} mi → custo {s['custo']/1e6:.2f} bi | ROE lp {ITSA_ROE_LP:.1%} ini {ITSA4.roe_inicio:.1%} payout {ITSA_PAYOUT:.1%} VPA {ITSA4.vpa:.2f}")
