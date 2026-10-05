"""Transforma o cru da StatusInvest em séries anuais por ticker (ROE, LPA, VPA, P/L, P/VP, DPA por data-com, JCP)."""
import json
import pathlib
import sys
from collections import defaultdict
from datetime import datetime

RAW = pathlib.Path(__file__).parent / "dados" / "raw"


def num(s):
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return float(s)
    s = s.replace(".", "").replace(",", ".").strip()
    try:
        return float(s)
    except ValueError:
        return None


def series(tk: str, dia: str):
    # coleta mais recente (até `dia`) que tenha o ticker — permite lotes coletados em dias diferentes
    dias = sorted(x.name for x in RAW.iterdir() if x.is_dir() and x.name <= dia and (x / f"{tk}_indicadores.json").exists())
    base = RAW / dias[-1]
    ind = json.loads((base / f"{tk}_indicadores.json").read_text(encoding="utf-8"))
    d = ind["data"]
    lista = d[list(d.keys())[0]]
    out = {}
    for it in lista:
        k = it["key"]
        out[k] = {"atual": it.get("actual"), "anos": {int(r["rank"]): r.get("value") for r in it.get("ranks", []) if r.get("rank")}}
    prov = json.loads((base / f"{tk}_proventos.json").read_text(encoding="utf-8"))
    eventos = []
    for e in prov.get("assetEarningsModels", []):
        eventos.append({
            "tipo": e.get("et"), "valor": e.get("v"),
            "data_com": e.get("ed"), "pagamento": e.get("pd"),
        })
    dpa_ano = defaultdict(float)
    jcp_ano = defaultdict(float)
    for e in eventos:
        try:
            ano = datetime.strptime(e["data_com"], "%d/%m/%Y").year
        except (TypeError, ValueError):
            continue
        v = e["valor"] or 0
        dpa_ano[ano] += v
        if e["tipo"] and "JCP" in e["tipo"].upper():
            jcp_ano[ano] += v
    pag = json.loads((base / f"{tk}_pagina.json").read_text(encoding="utf-8"))
    preco = num(pag.get("preco"))
    vm = num(pag.get("valor_mercado"))
    pl = num(pag.get("patrimonio_liquido"))
    n = vm / preco if vm and preco else None
    return {
        "preco": preco, "valor_mercado": vm, "patrimonio_liquido": pl, "n_acoes_implicito": n,
        "vpa_implicito": pl / n if pl and n else None,
        "indicadores": {k: out[k] for k in ("roe", "lpa", "vpa", "p_l", "p_vp", "dy") if k in out},
        "dpa_por_ano_datacom": dict(sorted(dpa_ano.items())),
        "jcp_por_ano_datacom": dict(sorted(jcp_ano.items())),
        "eventos": eventos,
    }


if __name__ == "__main__":
    dia = sys.argv[1]
    tks = sys.argv[2:]
    res = {tk: series(tk, dia) for tk in tks}
    destino = pathlib.Path(__file__).parent / "dados" / f"series_{dia}.json"
    destino.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for tk, s in res.items():
        r = s["indicadores"]["roe"]["anos"]
        print(f"\n{tk} preço {s['preco']} | n {s['n_acoes_implicito'] and round(s['n_acoes_implicito']/1e6)} mi | VPA {s['vpa_implicito'] and round(s['vpa_implicito'],2)} | atual ROE {s['indicadores']['roe']['atual']} LPA {s['indicadores']['lpa']['atual']} VPA {s['indicadores']['vpa']['atual']} P/L {s['indicadores']['p_l']['atual']} P/VP {s['indicadores']['p_vp']['atual']}")
        print("  ROE ", {a: r[a] for a in sorted(r) if a >= 2014})
        pl_ = s["indicadores"]["p_l"]["anos"]; print("  P/L ", {a: pl_[a] for a in sorted(pl_) if a >= 2014})
        pv = s["indicadores"]["p_vp"]["anos"]; print("  P/VP", {a: pv[a] for a in sorted(pv) if a >= 2014})
        lp = s["indicadores"]["lpa"]["anos"]; print("  LPA ", {a: lp[a] for a in sorted(lp) if a >= 2014})
        print("  DPA ", {a: round(v, 3) for a, v in s["dpa_por_ano_datacom"].items() if a >= 2014})
        print("  JCP ", {a: round(v, 3) for a, v in s["jcp_por_ano_datacom"].items() if a >= 2021})
