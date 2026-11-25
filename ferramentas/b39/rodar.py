"""B39 — monta insumos → cálculo → `b39/resultado_B39.json`. Uso, de `ferramentas/`:

    python -m b39.insumos     # uma vez (rede)
    python -m b39.rodar       # CVM local + COTAHIST local; grava o JSON
    python -m b39.relatorio   # gera docs/b39/B39-2026-11.md só do JSON

Regras: emenda 9 do `docs/PRE-REGISTRO-v3.md`, com as atribuições da emenda 10. Nada aqui muda motor, doutrina ou golden.
"""
from __future__ import annotations

import datetime as dt
import json
import pathlib
import statistics as st
import sys

import pandas as pd

import inflacao
from b39 import calculo as c
from b39 import cvm
from b39.insumos import INSUMOS, T

AQUI = pathlib.Path(__file__).resolve().parent
SAIDA = AQUI / "resultado_B39.json"
COTAHIST = AQUI.parent / "backtest" / "dados" / "cotahist" / "precos_2026.parquet"

BANCOS = ("ITUB4", "BBDC4", "BBAS3", "ABCB4", "BRSR6", "BRBI11", "SANB11", "BPAC11")   # hall (lote1_bancos "banco") + BPAC11
# Financeiras do motor de financeiras da Mesa (lote1_bancos: bancos e seguradoras; ITSA4; BPAC11) → prêmio fixo de 5 p.p.
FINANCEIRAS_MESA = set(BANCOS) | {"BBSE3", "CXSE3", "PSSA3", "ITSA4"}
SEM_PETR_VALE = {"PETR3", "PETR4", "VALE3"}


def _ler(nome: str) -> dict:
    return json.loads((INSUMOS / f"{nome}.json").read_text(encoding="utf-8"))


def precos_em(data: str) -> dict[str, tuple[float, float]]:
    d = pd.read_parquet(COTAHIST)
    d = d[(d["data"].astype(str) == data) & (d["codbdi"] == "02")]
    if d.empty:
        raise ValueError(f"sem pregão no COTAHIST em {data}")
    return {r.ticker.strip(): (float(r.preult), float(r.voltot)) for r in d.itertuples()}


def precos_por_classe(tickers: set[str], precos: dict) -> dict:
    """ON = final 3; PN = final 4–8 (a mais negociada). Units (11) não entram na conta das ações."""
    on = [t for t in tickers if len(t) == 5 and t.endswith("3") and t in precos]
    pn = [t for t in tickers if len(t) == 5 and t[-1] in "45678" and t in precos]
    mais = lambda xs: max(xs, key=lambda t: precos[t][1]) if xs else None
    ton, tpn = mais(on), mais(pn)
    return {"on": precos[ton][0] if ton else None, "pn": precos[tpn][0] if tpn else None, "ticker_on": ton, "ticker_pn": tpn}


def _unit(tks: set[str], precos: dict, cnpj: str) -> tuple[str, float, float] | None:
    """(ticker, preço, ações por unit) da unit negociada; composição da FCA em T (`backtest.motor.perfil.acoes_por_papel`)."""
    from backtest.motor import perfil
    for t in sorted(tks):
        if t.endswith("11") and t in precos:
            k = perfil.acoes_por_papel(t, cnpj, T)
            if k and k > 1:
                return t, precos[t][0], float(k)
    return None


def valor_mercado(acoes: dict | None, p: dict, unit=None) -> tuple[float | None, str]:
    """R$ mil = (ON × preço ON + PN × preço PN) ÷ 1000. Com unit negociada (composição da FCA), vale a unit para todas as ações:
    (ON + PN) ÷ ações por unit × preço da unit — a unit é o papel líquido; a classe avulsa pode ser ilíquida (IGTI3: R$ 75 mil no
    dia, 0,39 do valor pela unit; adversário de 25/11). Classe com ações e sem pregão usa o preço da outra (declarado)."""
    if not acoes:
        return None, "sem composição do capital"
    pon, ppn, nota = p["on"], p["pn"], ""
    if unit:
        t, pu, k = unit
        return (acoes["on"] + acoes["pn"]) / k * pu / 1000, f"pela unit {t} ({k:g} ações por unit)"
    if acoes["on"] > 0 and pon is None:
        pon, nota = ppn, "ON sem pregão: preço da PN"
    if acoes["pn"] > 0 and ppn is None:
        ppn, nota = pon, "PN sem pregão: preço da ON"
    if (acoes["on"] > 0 and pon is None) or (acoes["pn"] > 0 and ppn is None):
        return None, "sem preço"
    return (acoes["on"] * (pon or 0) + acoes["pn"] * (ppn or 0)) / 1000, nota


def montar() -> dict:
    tes, pi_, ibov, dam = _ler("tesouro"), _ler("pi"), _ler("ibov"), _ler("damodaran")
    rf, pi = tes["rf"]["taxa_compra_manha"], pi_["pi"]
    precos = precos_em(T)
    mes_ipca = inflacao.mes_publicado_em(T)

    # ---------------------------------------------------------------- identidade das companhias (índice + bancos)
    por_cnpj: dict[str, dict] = {}
    for comp in ibov["componentes"] + [{"ticker": b, "part": 0.0, "nome": ""} for b in BANCOS]:
        tk = comp["ticker"]
        cnpj, cd, origem = cvm.identificar(tk, T)
        if not cnpj or not cd:
            raise ValueError(f"{tk}: sem identidade na CVM")
        e = por_cnpj.setdefault(cnpj, {"cnpj": cnpj, "cd_cvm": cd, "origem": origem, "tickers": [], "part": 0.0,
                                      "no_indice": False, "nome": comp.get("nome", "")})
        if tk not in e["tickers"]:
            e["tickers"].append(tk)
        if comp["part"]:
            e["part"] += comp["part"]
            e["no_indice"] = True
    fat = cvm.fatos({e["cd_cvm"] for e in por_cnpj.values()})
    grupos = {int(k): g for k, g in fat.groupby("cd_cvm")}

    # ---------------------------------------------------------------- por companhia
    empresas = []
    with inflacao.ate(mes_ipca):
        for e in por_cnpj.values():
            g = grupos.get(e["cd_cvm"])
            if g is None:
                e.update(erro="sem fatos na CVM")
                empresas.append(e)
                continue
            b = cvm.companhia(g, e["cnpj"], T)
            raizes = {t[:4] for t in e["tickers"]}
            tks = set(cvm.tickers_por_cnpj().get(e["cnpj"], set())) | set(e["tickers"]) | {t for t in precos if t[:4] in raizes}
            p = precos_por_classe(tks, precos)
            u = b.get("ultimo", {})
            if u.get("acoes"):
                qt = sum(x["qtd_teorica"] for x in ibov["componentes"] if x["ticker"] in e["tickers"]) or None
                u["acoes_cvm"] = u["acoes"]
                u["acoes"], u["nota_acoes"] = cvm.escalar_acoes(u["acoes"], cvm.acoes_referencia(e["cd_cvm"], T), qt)
                if u["nota_acoes"]:
                    b["avisos"].append(u["nota_acoes"])
            vm, nota_vm = valor_mercado(u.get("acoes"), p, unit=_unit(tks, precos, e["cnpj"]))
            fin = bool(set(e["tickers"]) & FINANCEIRAS_MESA) or b["plano"] == cvm.FINANCEIRO
            anos = sorted(a for a in b["anuais"] if a >= 2016)[-c.JANELA:]
            reais = {}
            for a in anos:
                x = b["anuais"][a]
                if x["lucro"] is not None:
                    reais[a] = x["lucro"] * inflacao.deflator_periodo(int(x["dt_refer"][:4]), int(x["dt_refer"][5:7]))
            e10 = c.e10([reais.get(a) for a in anos])
            try:
                premio = c.premio_componente(fin, u.get("divida"), vm) if vm else None
            except ValueError:
                premio = None
            e.update(plano=b["plano"], financeira=fin, precos=p, vm=vm, nota_vm=nota_vm, ultimo=u, ltm=b.get("ltm"),
                     anuais={str(a): b["anuais"][a] for a in sorted(b["anuais"])}, lucro_real={str(a): v for a, v in reais.items()},
                     e10=e10, n_exercicios_e10=len(reais), premio=premio, avisos=b["avisos"])
            empresas.append(e)

    idx = [e for e in empresas if e["no_indice"]]
    vm_total = sum(e["vm"] for e in idx if e.get("vm"))

    # ---------------------------------------------------------------- (i) bancos
    bancos = []
    for tk in BANCOS:
        e = next(x for x in empresas if tk in x["tickers"])
        lucro = {int(a): x["lucro"] for a, x in e.get("anuais", {}).items()}
        pl = {int(a): x["pl"] for a, x in e.get("anuais", {}).items() if x["pl"] is not None}
        roes = c.roe_anuais(lucro, pl)
        roes = {a: v for a, v in roes.items() if a >= 2016}
        rn = c.roe_normalizado(roes)
        pl_u = e.get("ultimo", {}).get("pl")
        pvp = e["vm"] / pl_u if e.get("vm") and pl_u else None
        r = {"ticker": tk, "roes": {str(a): v for a, v in roes.items()}, "n_roes": len(roes), "roe_normalizado": rn,
             "pvp": pvp, "vm": e.get("vm"), "pl_ultimo": pl_u, "dt_refer_ultimo": e.get("ultimo", {}).get("dt_refer")}
        if rn is not None and pvp:
            r["ke_nom"], r["ke_real"] = c.ke_banco(rn, pvp, c.G_REAL, pi)
            r["sens"] = {f"g_real_{g:.0%}": c.ke_banco(rn, pvp, g, pi)[1] for g in (0.0, 0.02)}
            u = e.get("ultimo", {})
            if e.get("ltm") is not None and u.get("pl") and u.get("pl_ano_antes"):
                roe_ltm = e["ltm"] / ((u["pl"] + u["pl_ano_antes"]) / 2)
                r["roe_ltm"] = roe_ltm
                r["sens"]["roe_ltm"] = c.ke_banco(roe_ltm, pvp, c.G_REAL, pi)[1]
        else:
            r["fora"] = "menos de 5 exercícios" if rn is None else "sem P/VP"
        bancos.append(r)
    kes = [b["ke_real"] for b in bancos if "ke_real" in b]
    est_i = st.median(kes) if kes else None
    mesa_i = rf + c.PREMIO
    sens_i = {k: st.median([b["sens"][k] for b in bancos if k in b.get("sens", {})])
              for k in ("g_real_0%", "g_real_2%", "roe_ltm") if any(k in b.get("sens", {}) for b in bancos)}

    # ---------------------------------------------------------------- (ii) índice agregado
    comps_ii = [{"e10": e.get("e10"), "vm": e.get("vm")} for e in idx]
    agg = c.ke_indice(comps_ii, vm_total)
    dentro = [e for e in idx if e.get("e10") is not None and e.get("vm")]
    com_premio_ii = [{"premio": e["premio"], "vm": e["vm"]} for e in dentro if e.get("premio") is not None]
    mesa_ii = rf + c.premio_indice(com_premio_ii) if com_premio_ii else None
    sens_ii = {}
    sp = c.ke_indice([{"e10": e.get("e10"), "vm": e.get("vm")} for e in idx if not set(e["tickers"]) & SEM_PETR_VALE],
                     sum(e["vm"] for e in idx if e.get("vm") and not set(e["tickers"]) & SEM_PETR_VALE))
    sens_ii["sem_petr_vale"] = sp["ke"]
    ltm = [e for e in dentro if e.get("ltm") is not None]
    sens_ii["lucro_ltm"] = sum(e["ltm"] for e in ltm) / sum(e["vm"] for e in ltm) if ltm else None
    payouts = []
    for a in range(2016, 2026):
        L = sum(e["anuais"][str(a)]["lucro"] or 0 for e in dentro if str(a) in e.get("anuais", {}))
        D = sum(e["anuais"][str(a)]["dividendos"] or 0 for e in dentro if str(a) in e.get("anuais", {}))
        if L > 0:
            payouts.append(D / L)
    payout = st.median(payouts) if payouts else None
    if payout is not None and agg["soma_vm"]:
        for g in (0.0, 0.01, 0.02):
            sens_ii[f"gordon_g_{g:.0%}"] = c.ke_gordon_indice(payout, agg["soma_e10"], agg["soma_vm"], g)

    # ---------------------------------------------------------------- (iii) Damodaran
    k_nom_iii, est_iii = c.ke_damodaran(rf, pi, dam["s_adj_default_spread"], dam["erp_total"])
    com_premio_iii = [{"premio": e["premio"], "vm": e["vm"]} for e in idx if e.get("premio") is not None and e.get("vm")]
    mesa_iii = rf + c.premio_indice(com_premio_iii)
    sens_iii = {"sem_tirar_s": c.ke_damodaran_literal(rf, dam["erp_total"])}

    deltas = {"i": None if est_i is None else est_i - mesa_i,
              "ii": None if agg["ke"] is None or mesa_ii is None else agg["ke"] - mesa_ii,
              "iii": est_iii - mesa_iii}
    return {
        "b39": "Ke da Mesa × Ke implícito (pré-registro v3, emendas 9 e 10)",
        "gerado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "data_base": T, "mes_ipca": f"{mes_ipca // 12}-{mes_ipca % 12 + 1:02d}",
        "mercado": {"rf_real": rf, "rf_titulo": f"Tesouro IPCA+ {tes['rf']['vencimento']}", "rf_fonte": tes["fonte"],
                    "pi": pi, "pi_fonte": pi_["fonte"], "damodaran": {k: dam[k] for k in
                    ("atualizado", "rating_moodys", "s_adj_default_spread", "crp", "erp_total", "erp_maduro_implicito", "url")},
                    "ibov": {"n": len(ibov["componentes"]), "data_da_carteira_b3": ibov["data_da_carteira_b3"], "fonte": ibov["fonte"]}},
        "estimativas": {
            "i": {"nome": "Bancos (Gordon sobre P/VP, ROE mediano 10a)", "ke_real": est_i, "ke_mesa_real": mesa_i,
                  "n": len(kes), "sens": sens_i},
            "ii": {"nome": "Ibovespa agregado (Σ E10 ÷ Σ valor de mercado)", "ke_real": agg["ke"], "ke_mesa_real": mesa_ii,
                   "cobertura_vm": agg["cobertura"], "n": agg["n"], "n_indice": len(idx),
                   "cobertura_peso_ibov": sum(e["part"] for e in dentro), "soma_e10": agg["soma_e10"],
                   "soma_vm": agg["soma_vm"], "vm_total": vm_total, "payout_mediano": payout, "sens": sens_ii},
            "iii": {"nome": "rf − s + ERP total (Damodaran jan/2026)", "ke_real": est_iii, "ke_nom": k_nom_iii,
                    "ke_mesa_real": mesa_iii, "sens": sens_iii}},
        "deltas": deltas,
        "gatilho": c.gatilho(deltas),
        "bancos": bancos,
        "empresas": empresas,
    }


def main() -> int:
    r = montar()
    SAIDA.write_text(json.dumps(r, ensure_ascii=False, indent=1, default=float), encoding="utf-8")
    print(json.dumps({"deltas": r["deltas"], "gatilho": r["gatilho"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
