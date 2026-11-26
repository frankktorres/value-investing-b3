"""B45 — alcance dos dois achados de dado (só contagem por regex nos ZIPs da CVM; não abre valuation de ninguém).

Uso, de `ferramentas/`:   python -m b45.alcance        (≈ 3 min)  →  docs/b45/alcance.json

- E1: empresas com compra de imobilizado no caixa operacional (`coletar_cvm.RE_FROTA_FCO`, 6.01, valor < 0), DFP 2016–2025,
  DFC MI/MD consolidada e individual; separa as do hall/dossiês (`coletar_cvm.EMPRESAS`) — o golden só muda se houver alguma.
- E2: tickers do hall/dossiês (e as 5 da B45) cuja receita (3.01) ou EBIT (3.05) da DFP original (ÚLTIMO) difere em mais de
  0,5% do comparativo reapresentado na DFP seguinte (PENÚLTIMO). É a lista do PENDENTE #16 / B62.
"""
from __future__ import annotations

import io
import json
import pathlib
import sys
import zipfile

AQUI = pathlib.Path(__file__).resolve().parent
ZIP = AQUI.parent / "dados" / "cvm"
SAIDA = AQUI.parent.parent / "docs" / "b45" / "alcance.json"
B45 = ("RAIL3", "SMFT3", "MOVI3", "EMBJ3", "BEEF3")
TOL = 0.005


def _ler(ano: int, chave: str, cols=None):
    import pandas as pd
    z = zipfile.ZipFile(ZIP / f"dfp_{ano}.zip")
    ns = [x for x in z.namelist() if chave in x]
    return pd.read_csv(io.BytesIO(z.read(ns[0])), sep=";", encoding="latin-1", dtype=str, usecols=cols) if ns else None


def _filtro(d, pat: str):
    if pat.startswith("cvm:"):
        return d[d["CD_CVM"].astype(int).isin([int(c) for c in pat[4:].split("|")])]
    return d[d["DENOM_CIA"].str.contains(pat, case=False, regex=True, na=False)]


def frota() -> dict:
    import coletar_cvm as C
    hall, b3 = [], set()
    for ano in range(2016, 2026):
        for t in ("DFC_MI_con", "DFC_MD_con", "DFC_MI_ind", "DFC_MD_ind"):
            d = _ler(ano, t)
            if d is None:
                continue
            d = d[d["CD_CONTA"].str.startswith("6.01") & d["DS_CONTA"].str.contains(C.RE_FROTA_FCO, na=False)
                  & (d["VL_CONTA"].astype(float) < 0)]
            b3 |= set(d["DENOM_CIA"])
            for tk, (pat, _) in C.EMPRESAS.items():
                for r in _filtro(d, pat).itertuples():
                    hall.append(dict(ticker=tk, ano=ano, arquivo=t, conta=r.CD_CONTA, linha=r.DS_CONTA))
    return dict(hall_dossies=hall, empresas_b3=sorted(b3))


def reapresentacao() -> list[dict]:
    import coletar_cvm as C
    cols = ["CNPJ_CIA", "CD_CVM", "DENOM_CIA", "ORDEM_EXERC", "CD_CONTA", "VL_CONTA"]
    D = {}
    for a in range(2016, 2026):
        d = _ler(a, "DRE_con", cols)
        d = d[d["CD_CONTA"].isin(["3.01", "3.05"])].copy()
        d["ult"] = d["ORDEM_EXERC"].str.upper().str.startswith(("ÚLTIMO", "ULTIMO"))
        d["v"] = d["VL_CONTA"].astype(float)
        D[a] = d
    cad = {c["ticker"]: c for c in json.loads((AQUI.parent / "holdout_b36" / "cadastro.json").read_text(encoding="utf-8"))}
    alvos = {tk: (lambda d, p=pat: _filtro(d, p)) for tk, (pat, _) in C.EMPRESAS.items()}
    alvos |= {"*" + tk: (lambda d, c=cad[tk]["cnpj"]: d[d["CNPJ_CIA"] == c]) for tk in B45}
    out = []
    for tk, sel in alvos.items():
        for a in range(2016, 2025):
            o, r = sel(D[a]), sel(D[a + 1])
            for conta in ("3.01", "3.05"):
                vo = o[o["ult"] & (o["CD_CONTA"] == conta)]["v"].sum()
                vr = r[~r["ult"] & (r["CD_CONTA"] == conta)]["v"].sum()
                if vo and vr and abs(vr - vo) / abs(vo) > TOL:
                    out.append(dict(ticker=tk, ano=a, conta=conta, original=vo, reapresentado=vr, dif=round((vr - vo) / abs(vo), 4)))
    return out


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    f, r = frota(), reapresentacao()
    hall_r = sorted({x["ticker"] for x in r if not x["ticker"].startswith("*")})
    res = dict(e1_frota=f, e2_reapresentacao=r, e2_tickers_hall_dossies=hall_r)
    SAIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"E1: hall/dossiês com a linha = {len(f['hall_dossies'])}; empresas da B3 = {len(f['empresas_b3'])}")
    print(f"E2: {len(hall_r)} tickers do hall/dossiês: {', '.join(hall_r)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
