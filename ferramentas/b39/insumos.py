"""B39 — coleta dos insumos de mercado (a rede só entra aqui). Uso, de `ferramentas/`:

    python -m b39.insumos          # grava b39/insumos/*.json (pequenos, no git) e o bruto em b39/dados/ (fora do git)

Data-base T = 19/11/2026 (a da B36; decisão registrada em docs/DECISOES.md). Cada número sai com URL, data e arquivo.
"""
from __future__ import annotations

import base64
import csv
import datetime as dt
import hashlib
import io
import json
import pathlib
import re
import sys

import requests

AQUI = pathlib.Path(__file__).resolve().parent
INSUMOS = AQUI / "insumos"
BRUTO = AQUI / "dados"
T = "2026-11-19"

URL_TESOURO = ("https://www.tesourotransparente.gov.br/ckan/dataset/df56aa42-484a-4a59-8184-7676580c81e3/resource/"
               "796d2059-14e9-44e3-80c9-2d9e30b405c1/download/PrecoTaxaTesouroDireto.csv")
URL_IBOV = "https://sistemaswebb3-listados.b3.com.br/indexProxy/indexCall/GetPortfolioDay/"
URL_DAMODARAN = "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html"
UA = {"User-Agent": "Mozilla/5.0"}


def _get(url: str) -> bytes:
    r = requests.get(url, headers=UA, timeout=120)
    r.raise_for_status()
    return r.content


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _num(s: str) -> float:
    """Número em formato brasileiro ("1.234,5", "478.975.645", "7,86")."""
    return float(s.strip().replace(".", "").replace(",", "."))


def escolher_rf(linhas: list[dict], data_base: str) -> dict:
    """Tesouro IPCA+ SEM cupom com vencimento mais próximo de 10 anos da data-base (emenda 9). Empate → o mais curto."""
    alvo = dt.date.fromisoformat(data_base).replace(year=int(data_base[:4]) + 10)
    sem = [l for l in linhas if l["tipo"] == "Tesouro IPCA+"]
    if not sem:
        raise ValueError("sem Tesouro IPCA+ sem cupom na data")
    return min(sem, key=lambda l: (abs((dt.date.fromisoformat(l["vencimento"]) - alvo).days), l["vencimento"]))


def linhas_tesouro(texto: str, data_base: str) -> list[dict]:
    d = data_base[8:10] + "/" + data_base[5:7] + "/" + data_base[:4]
    out = []
    for r in csv.DictReader(io.StringIO(texto), delimiter=";"):
        if r["Data Base"] != d:
            continue
        v = r["Data Vencimento"]
        out.append({"tipo": r["Tipo Titulo"], "vencimento": f"{v[6:]}-{v[3:5]}-{v[:2]}",
                    "taxa_compra_manha": _num(r["Taxa Compra Manha"]) / 100})
    return out


def tesouro() -> dict:
    b = _get(URL_TESOURO)
    (BRUTO / "PrecoTaxaTesouroDireto.csv").write_bytes(b)
    ls = linhas_tesouro(b.decode("latin-1"), T)
    rf = escolher_rf(ls, T)
    return {"data_base": T, "fonte": "Tesouro Transparente, PrecoTaxaTesouroDireto.csv, Taxa Compra Manha", "url": URL_TESOURO,
            "coletado_em": dt.date.today().isoformat(), "sha256_csv": _sha(b), "rf": rf, "linhas": ls}


def pi_ettj() -> dict:
    """π = inflação implícita da ETTJ ANBIMA no vértice de 2520 du (~10 anos), a mesma do `mercado_vigente.json` em T."""
    m = json.loads((AQUI.parent / "dados" / "mercado.json").read_text(encoding="utf-8"))
    e = m["anbima_ettj_inflacao_implicita"]["inflacao_implicita_vertice_mais_longo_2520du_~10a"]
    if e["data"] != T:
        raise ValueError(f"ETTJ de {e['data']}, não de T = {T}")
    return {"data_base": T, "pi": e["valor"] / 100, "fonte": "ANBIMA ETTJ, inflação implícita 2520 du (~10 anos)",
            "url": e["fonte_url"], "tipo": e["tipo"], "via": "ferramentas/dados/mercado.json (coleta de 23/11/2026)"}


def carteira_ibov() -> dict:
    p = base64.b64encode(json.dumps({"language": "pt-br", "pageNumber": 1, "pageSize": 200, "index": "IBOV",
                                     "segment": "1"}).encode()).decode()
    b = _get(URL_IBOV + p)
    j = json.loads(b)
    comps = [{"ticker": r["cod"].strip(), "nome": r["asset"].strip(), "tipo": r["type"].strip(), "part": _num(r["part"]) / 100,
              "qtd_teorica": _num(r["theoricalQty"])} for r in j["results"]]
    if len(comps) != j["page"]["totalRecords"]:
        raise ValueError("carteira incompleta")
    return {"fonte": "B3, carteira teórica do Ibovespa (GetPortfolioDay)", "url": URL_IBOV + p,
            "data_da_carteira_b3": j["header"]["date"], "coletado_em": dt.date.today().isoformat(),
            "nota": "carteira do quadrimestre set–dez/2026, a vigente em T", "sha256": _sha(b), "componentes": comps}


def damodaran_linha(html: str, pais: str = "Brazil") -> dict:
    t = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html))
    m = re.search(r"Last updated:\s*([A-Za-z]+ \d{1,2}, \d{4})", t)
    r = re.search(rf"\b{pais} (\w+) ([\d.]+)% ([\d.]+)% ([\d.]+)% ([\d.]+)% ([\d.]+|NA)%? ([\d.]+|NA)%?", t)
    if not (m and r):
        raise ValueError("linha do país ou data não encontrada")
    return {"atualizado": m.group(1), "pais": pais, "rating_moodys": r.group(1),
            "s_adj_default_spread": float(r.group(2)) / 100, "crp": float(r.group(3)) / 100,
            "erp_total": float(r.group(4)) / 100, "aliquota": float(r.group(5)) / 100,
            "cds": None if r.group(6) == "NA" else float(r.group(6)) / 100, "linha": r.group(0)}


def damodaran() -> dict:
    b = _get(URL_DAMODARAN)
    (BRUTO / "ctryprem.html").write_bytes(b)
    d = damodaran_linha(b.decode("latin-1"))
    if "2026" not in d["atualizado"] or "January" not in d["atualizado"]:
        raise ValueError(f"ctryprem não é a de jan/2026: {d['atualizado']}")
    return {**d, "fonte": "Damodaran, Country Default Spreads and Risk Premiums (NYU Stern)", "url": URL_DAMODARAN,
            "coletado_em": dt.date.today().isoformat(), "sha256_html": _sha(b),
            "erp_maduro_implicito": round(d["erp_total"] - d["crp"], 6)}


def main() -> int:
    INSUMOS.mkdir(exist_ok=True)
    BRUTO.mkdir(exist_ok=True)
    for nome, f in (("tesouro", tesouro), ("pi", pi_ettj), ("ibov", carteira_ibov), ("damodaran", damodaran)):
        (INSUMOS / f"{nome}.json").write_text(json.dumps(f(), ensure_ascii=False, indent=1), encoding="utf-8")
        print("ok", nome)
    return 0


if __name__ == "__main__":
    sys.exit(main())
