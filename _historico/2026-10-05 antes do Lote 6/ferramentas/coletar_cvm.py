"""Demonstrações padronizadas a partir dos dados abertos da CVM (DFP anual + ITR) — fonte A.

Uso: python coletar_cvm.py SUZB3 KLBN11 ...  → dados/cvm_series.json
Cache dos ZIPs em dados/cvm/. Valores em R$ mil (convertidos se a escala vier em unidade).
Contas pelo código CVM (estáveis): DRE 3.xx, BPA 1.xx, BPP 2.xx; DFC método indireto 6.xx.
D&A e capex saem das linhas da DFC por descrição (declarado no JSON: quais linhas entraram).
"""
import io
import json
import pathlib
import re
import sys
import zipfile
from collections import defaultdict

import pandas as pd
import requests

AQUI = pathlib.Path(__file__).parent
CACHE = AQUI / "dados" / "cvm"
URL = {"DFP": "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/DFP/DADOS/dfp_cia_aberta_{a}.zip",
       "ITR": "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/itr_cia_aberta_{a}.zip"}

# denominação na CVM (regex) e ações por unit negociada
EMPRESAS = {
    "SUZB3": (r"^SUZANO S\.?A", 1), "KLBN11": (r"^KLABIN S\.?A", 5), "RANI3": (r"^IRANI PAPEL", 1),
    "B3SA3": (r"^B3 S\.?A", 1), "SMTO3": (r"^S[AÃ]O MARTINHO S\.?A", 1), "KEPL3": (r"^KEPLER WEBER", 1),
    "SLCE3": (r"^SLC AGR[IÍ]COLA", 1),
    "SAPR11": ("cvm:018627", 5), "CSMG3": ("cvm:019445", 1), "SBSP3": ("cvm:014443", 1), "TAEE11": ("cvm:020257", 3),
    "ISAE4": ("cvm:018376", 1), "CMIG4": ("cvm:002453", 1), "CPFE3": ("cvm:018660", 1), "CPLE3": ("cvm:014311", 1),
    "PETR4": ("cvm:009512", 1), "PRIO3": ("cvm:022187", 1), "RECV3": ("cvm:025780", 1), "UGPA3": ("cvm:018465", 1),
    "VBBR3": ("cvm:024295", 1),
}
DRE = {"receita": "3.01", "custo": "3.02", "lucro_bruto": "3.03", "desp_vendas": "3.04.01", "desp_ga": "3.04.02",
       "outras_receitas_op": "3.04.04", "outras_despesas_op": "3.04.05", "ebit": "3.05", "res_fin": "3.06", "desp_fin": "3.06.02", "lair": "3.07", "ir": "3.08", "lucro": "3.11",
       "lucro_controlador": "3.11.01"}
BPA = {"ativo": "1", "ac": "1.01", "caixa": "1.01.01", "aplic_cp": "1.01.02", "receber": "1.01.03", "estoques": "1.01.04",
       "anc": "1.02", "rlp": "1.02.01", "investimentos": "1.02.02", "imobilizado": "1.02.03", "intangivel": "1.02.04"}
BPP = {"passivo": "2", "pc": "2.01", "emprest_cp": "2.01.04", "pnc": "2.02", "emprest_lp": "2.02.01", "pl": "2.03",
       "reservas_lucro": "2.03.04", "nao_controladores": "2.03.09"}
DFC = {"fco": "6.01", "fci": "6.02", "fcf_fin": "6.03"}
RE_DA = re.compile(r"deprecia|amortiza|exaust|colhid", re.I)   # inclui "ativos biológicos colhidos" (cana, florestas)
RE_DA_NAO = re.compile(r"juros|capta|empr[eé]stimo|cambia|financiamento", re.I)   # amortização de custo de captação não é D&A (05/10)
RE_CAPEX = re.compile(r"(aquisi|adi[cç]|compra|investiment|aplica[cç][aã]o|forma[cç][aã]o|plantio|desembolso|^em )"
                      r".*(imobiliz|intang|biol[oó]g|florest|plant|lavoura|bens|madeira|software)", re.I)
RE_DIV = re.compile(r"dividend|juros sobre (?:o )?capital", re.I)
RE_RECOMPRA = re.compile(r"(recompra|aquisi[cç][aã]o).*(a[cç][oõ]es|tesouraria)", re.I)


def zip_de(tipo, ano):
    CACHE.mkdir(parents=True, exist_ok=True)
    f = CACHE / f"{tipo.lower()}_{ano}.zip"
    if not f.exists():
        r = requests.get(URL[tipo].format(a=ano), timeout=300)
        r.raise_for_status()
        f.write_bytes(r.content)
    return zipfile.ZipFile(f)


def ler(z, nome):
    alvo = [n for n in z.namelist() if n.lower().endswith(nome.lower())]
    if not alvo:
        return None
    df = pd.read_csv(io.BytesIO(z.read(alvo[0])), sep=";", encoding="latin-1", dtype=str)
    if "VL_CONTA" in df:
        df["VL_CONTA"] = pd.to_numeric(df["VL_CONTA"], errors="coerce")
        df.loc[df.get("ESCALA_MOEDA", "MIL") == "UNIDADE", "VL_CONTA"] /= 1000
    return df


def filtra(df, regex):
    if regex.startswith("cvm:") and "CD_CVM" not in df:
        return df.iloc[0:0]
    if regex.startswith("cvm:"):
        d = df[df["CD_CVM"].astype(str).str.zfill(6) == regex[4:]]
    else:
        d = df[df["DENOM_CIA"].str.contains(regex, regex=True, na=False, case=False)]
    if d.empty:
        return d
    if "VERSAO" in d:
        d = d[d["VERSAO"] == d.groupby("DT_REFER")["VERSAO"].transform("max")]
    return d


def buscar(z, nome, ano, regex):
    """Demonstração filtrada: consolidada; se a empresa não tiver (sem controladas), a individual.
    DFC: indireto antes de direto."""
    base = nome.replace("_con", "")
    tentativas = [base + "_con", base + "_ind"]
    if base == "DFC_MI":
        tentativas = ["DFC_MI_con", "DFC_MD_con", "DFC_MI_ind", "DFC_MD_ind"]
    ultimo = None
    for n in tentativas:
        df = ler(z, f"{n}_{ano}.csv")
        if df is None:
            continue
        d = filtra(df, regex)
        ultimo = d
        if not d.empty:
            return d
    return ultimo


def contas(d, mapa):
    out = {}
    for k, cod in mapa.items():
        v = d.loc[d["CD_CONTA"] == cod, "VL_CONTA"]
        out[k] = float(v.iloc[0]) if len(v) else None
    return out


RE_ARREND = re.compile(r"arrendamento", re.I)
RE_BIO = re.compile(r"biol[oó]g", re.I)
RE_VJ = re.compile(r"valor justo.*biol|biol.*valor justo", re.I)
RE_IMPAIR = re.compile(r"valor de recupera|recuperabilidade|impairment", re.I)


def folhas(x):
    cods = set(x["CD_CONTA"])
    mask = pd.Series([not any(c != o and o.startswith(c + ".") for o in cods) for c in x["CD_CONTA"]], index=x.index, dtype=bool)
    return x.loc[mask]


def extras_bp(d):
    """Arrendamento (IFRS 16) fora de 2.01.04/2.02.01 e ativos biológicos (BPA), por descrição."""
    out = {}
    if d.empty or "DS_CONTA" not in d:
        return out
    if d["CD_CONTA"].str.startswith("2").any():
        x = d[(d["CD_CONTA"].str.startswith("2.01") | d["CD_CONTA"].str.startswith("2.02"))
              & ~d["CD_CONTA"].str.startswith("2.01.04") & ~d["CD_CONTA"].str.startswith("2.02.01")
              & d["DS_CONTA"].str.contains(RE_ARREND, na=False)]
        x = folhas(x)
        out["arrendamento"] = float(x["VL_CONTA"].sum()) if len(x) else 0.0
    if d["CD_CONTA"].str.startswith("1").any():
        x = folhas(d[d["CD_CONTA"].str.startswith("1.0") & d["DS_CONTA"].str.contains(RE_BIO, na=False)])
        out["biologico"] = float(x["VL_CONTA"].sum()) if len(x) else 0.0
    return out


def vj_biologico(d):
    """Ganho/perda de valor justo de ativo biológico dentro do resultado operacional (DRE 3.02–3.04)."""
    if d.empty or "DS_CONTA" not in d:
        return 0.0
    x = folhas(d[(d["CD_CONTA"].str.startswith("3.02") | d["CD_CONTA"].str.startswith("3.04"))
                 & d["DS_CONTA"].str.contains(RE_VJ, na=False)])
    return float(x["VL_CONTA"].sum()) if len(x) else 0.0


def impairment(d):
    """Perda (−) ou reversão (+) por redução ao valor recuperável dentro do resultado operacional (DRE 3.02–3.04)."""
    if d.empty or "DS_CONTA" not in d:
        return 0.0
    x = folhas(d[(d["CD_CONTA"].str.startswith("3.02") | d["CD_CONTA"].str.startswith("3.04"))
                 & d["DS_CONTA"].str.contains(RE_IMPAIR, na=False)])
    return float(x["VL_CONTA"].sum()) if len(x) else 0.0


def dfc_extra(d):
    if d.empty or "DS_CONTA" not in d:
        return {"da": None, "capex": None, "dividendos_pagos": 0.0, "recompra": 0.0}, {}
    da = d[d["CD_CONTA"].str.startswith("6.01.01") & d["DS_CONTA"].str.contains(RE_DA, na=False) & ~d["DS_CONTA"].str.contains(RE_DA_NAO, na=False)]
    cap = d[d["CD_CONTA"].str.startswith("6.02") & d["DS_CONTA"].str.contains(RE_CAPEX, na=False) & (d["VL_CONTA"] < 0)]
    div = d[d["CD_CONTA"].str.startswith("6.03") & d["DS_CONTA"].str.contains(RE_DIV, na=False) & (d["VL_CONTA"] < 0)]
    rec = d[d["CD_CONTA"].str.startswith("6.03") & d["DS_CONTA"].str.contains(RE_RECOMPRA, na=False) & (d["VL_CONTA"] < 0)]
    da, cap, div, rec = folhas(da), folhas(cap), folhas(div), folhas(rec)
    return ({"da": float(da["VL_CONTA"].sum()) if len(da) else None,
             "capex": float(-cap["VL_CONTA"].sum()) if len(cap) else None,
             "dividendos_pagos": float(-div["VL_CONTA"].sum()) if len(div) else 0.0,
             "recompra": float(-rec["VL_CONTA"].sum()) if len(rec) else 0.0},
            {"linhas_da": list(da["DS_CONTA"]), "linhas_capex": list(cap["DS_CONTA"])})


def anual(tk, ano):
    regex, _ = EMPRESAS[tk]
    z = zip_de("DFP", ano)
    res, aud = {}, {}
    cnpj = None
    for nome, mapa in (("DRE_con", DRE), ("BPA_con", BPA), ("BPP_con", BPP), ("DFC_MI_con", DFC)):
        d = buscar(z, nome, ano, regex)
        if d is None:
            continue
        if cnpj is None and len(d) and "CNPJ_CIA" in d:
            cnpj = d["CNPJ_CIA"].iloc[0]
        d = d[d["ORDEM_EXERC"].str.upper().str.startswith("ÚLTIMO") | d["ORDEM_EXERC"].str.upper().str.startswith("ULTIMO")]
        res.update(contas(d, mapa))
        res.update(extras_bp(d))
        if nome == "DRE_con":
            res["vj_biologico"] = vj_biologico(d)
            res["impairment"] = impairment(d)
        if nome == "DFC_MI_con":
            e, a = dfc_extra(d)
            res.update(e)
            aud.update(a)
    cap = ler(z, f"composicao_capital_{ano}.csv")
    if cap is not None:
        c = cap[cap["CNPJ_CIA"] == cnpj] if (cnpj and "CNPJ_CIA" in cap) else filtra(cap, regex)
        if len(c):
            tot = pd.to_numeric(c["QT_ACAO_TOTAL_CAP_INTEGR"], errors="coerce").iloc[-1]
            tes = pd.to_numeric(c.get("QT_ACAO_TOTAL_TESOURO", pd.Series([0])), errors="coerce").fillna(0).iloc[-1]
            res["acoes"] = float(tot - tes)
    return res, aud


def itr_ytd(tk, ano, mes=6):
    """Fluxos acumulados no ano até o trimestre (DRE e DFC) e balanço da data, do ITR."""
    regex, _ = EMPRESAS[tk]
    z = zip_de("ITR", ano)
    res = {}
    for nome, mapa, fluxo in (("DRE_con", DRE, True), ("BPA_con", BPA, False), ("BPP_con", BPP, False), ("DFC_MI_con", DFC, True)):
        d = buscar(z, nome, ano, regex)
        if d is None or d.empty:
            continue
        d = d[d["DT_REFER"].str[5:7].astype(int) == mes]
        d = d[d["ORDEM_EXERC"].str.upper().str.startswith("ÚLTIMO") | d["ORDEM_EXERC"].str.upper().str.startswith("ULTIMO")]
        if fluxo and "DT_INI_EXERC" in d:
            d = d[d["DT_INI_EXERC"].str[5:7] == "01"]          # acumulado no ano
        res.update(contas(d, mapa))
        res.update(extras_bp(d))
        if nome == "DRE_con":
            res["vj_biologico"] = vj_biologico(d)
            res["impairment"] = impairment(d)
        if nome == "DFC_MI_con":
            res.update(dfc_extra(d)[0])
    return res


def main(tks, anos=range(2016, 2026)):
    saida = {}
    for tk in tks:
        serie, auditoria = {}, {}
        anos_tk = range(2016, 2027) if tk == "SMTO3" else anos   # exercício abr–mar: DFP de mar/2026 está no arquivo 2026
        for a in anos_tk:
            try:
                serie[a], auditoria[a] = anual(tk, a)
            except Exception as ex:  # ano sem arquivo ou empresa sem dado
                serie[a], auditoria[a] = {"erro": str(ex)}, {}
        # LTM até jun/2026 = 2025 + 1S26 − 1S25 (fluxos); balanço de 30/06/2026
        ltm = {}
        if tk == "SMTO3":
            ltm = dict(serie.get(2026, {}), nota="fluxos: exercício abr/2025–mar/2026 (DFP); balanço: ITR de jun/2026")
            try:
                b = itr_ytd(tk, 2026, 6)
                for k in list(BPA) + list(BPP) + ["arrendamento", "biologico"]:
                    if b.get(k) is not None:
                        ltm[k] = b[k]
            except Exception:
                pass
        else:
          try:
            y26, y25 = itr_ytd(tk, 2026), itr_ytd(tk, 2025)
            fy = serie.get(2025, {})
            for k in list(DRE) + list(DFC) + ["da", "capex", "dividendos_pagos", "recompra", "vj_biologico", "impairment"]:
                if None not in (fy.get(k), y26.get(k), y25.get(k)):
                    ltm[k] = fy[k] + y26[k] - y25[k]
            for k in list(BPA) + list(BPP) + ["arrendamento", "biologico"]:
                ltm[k] = y26.get(k)
            ltm["acoes"] = fy.get("acoes")
          except Exception as ex:
            ltm = {"erro": str(ex)}
        saida[tk] = {"anual": serie, "ltm_2T26": ltm, "auditoria_linhas_dfc": auditoria, "acoes_por_unit": EMPRESAS[tk][1]}
        ok = [a for a in serie if serie[a].get("receita")]
        print(tk, "anos com DRE:", ok[0] if ok else None, "→", ok[-1] if ok else None, "| LTM receita:", ltm.get("receita"))
    arq = AQUI / "dados" / "cvm_series.json"
    tudo = json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}
    tudo.update(saida)                     # mescla: recoletar um lote não apaga os outros
    arq.write_text(json.dumps(tudo, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main(sys.argv[1:])
