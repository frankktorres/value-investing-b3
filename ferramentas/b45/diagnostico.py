"""B45 — diagnóstico camada a camada das 5 industriais da B36 com central ≤ 0 ou P/C absurdo (SÓ LEITURA, sem conserto).

Uso, de `ferramentas/`:   python -m b45.diagnostico [TK ...]      (padrão: RAIL3 SMFT3 MOVI3 EMBJ3 BEEF3)

Reroda o executor congelado da B36 (`holdout_b36.executor`, mesma ficha-padrão, mesmos insumos do protocolo, data-base
19/11/2026) e abre cada camada do motor `motor_nao_financeiras.valores/avaliar`: margens por ano e quartis, receita de meio,
ajuste de manutenção, NOPAT, WACC/Ke, EV de cada âncora, ponte EV → ação (dívida do desconto, caixa livre, minoritários),
ações. Grava `docs/b45/camadas.json`; não grava em `holdout_b36/resultados/`, golden, dossiê ou prospectivo.
"""
from __future__ import annotations

import json
import pathlib
import sys

AQUI = pathlib.Path(__file__).resolve().parent
SAIDA = AQUI.parent.parent / "docs" / "b45" / "camadas.json"
PADRAO = ("RAIL3", "SMFT3", "MOVI3", "EMBJ3", "BEEF3")


def _f(x, nd=4):
    return None if x is None else (round(x, nd) if isinstance(x, float) else x)


def camadas(tk: str, series: pathlib.Path | None = None) -> dict:
    import motor_nao_financeiras as M
    from dossie import base, gerar
    from holdout_b36 import executor as X
    c = X.cadastro()[tk]
    ins = X.ler_insumos(tk)
    nome = X.ficha_padrao(c, X._dia_statusinvest(tk))
    with X.registrado(c, nome, ins, series or X.SERIES):
        cc = gerar.calcular(tk, X.T)
        with base.na_data(X.T), base.isolado(tk):
            base.carregar(tk, dia_statusinvest=X._dia_statusinvest(tk))
            a, ltm = M.serie(tk)
            anos = cc["r"]["op"]["anos"]
            por_ano = {x: dict(receita=a[x].get("receita"), ebit=a[x].get("ebit"),
                               margem_ebit_aj=_f(M.ebit_aj(a[x], cc["r"]["op"]["med_outras"], True) / a[x]["receita"]),
                               lucro=a[x].get("lucro"), lucro_controlador=a[x].get("lucro_controlador"),
                               pl=a[x].get("pl"), nao_controladores=a[x].get("nao_controladores"),
                               divida_bruta=M.divida_liquida(a[x])[0], caixa=M.divida_liquida(a[x])[1],
                               da=a[x].get("da"), capex=a[x].get("capex"))
                       for x in anos}
            ltm_c = {k: ltm.get(k) for k in ("ref", "receita", "ebit", "lucro", "lucro_controlador", "pl", "nao_controladores",
                                             "emprest_cp", "emprest_lp", "arrendamento", "caixa", "aplic_cp", "juros_pagos",
                                             "desp_fin", "ativo")}
    r = cc["r"]
    op = r["op"]
    n = r["n"]
    w_real = r["wacc_real"]
    ev_epv = r["nopat"] / w_real + r["beneficio_fiscal_acao"] * n if w_real else None
    ponte = r["dl"] + r["minor"]
    return dict(
        ticker=tk, perfil=c["perfil"], setor=c["setor"], preco=cc["preco"], n_acoes_mil=n,
        palavra=r["palavra"], palavra_regua=r["palavra_regua"], confianca=r["confianca"], pc=r["pc"],
        central=r["central"], dispersao=r["dispersao"], ancoras=r["ancoras"], ancoras_descartadas=r["ancoras_descartadas"],
        dcf_cenarios=r["dcf"], dcf_pond=r["dcf_pond"], epv=r["epv"], oe_val=r["oe_val"], oe_norm=r["oe_norm"],
        oe_por_ano=r["oe"],
        margem=dict(m25=op["m25"], m50=op["m50"], m75=op["m75"], m50_5a=op["m50_5a"], margens=op["margens"],
                    ajuste_manut=op["ajuste_manut"], med_outras=op["med_outras"], quebra_suspeita=op["quebra_suspeita"],
                    divergencia_janela=op["divergencia_janela"]),
        receita_meio=op["receita_meio"], lucro_pre_ir=op["receita_meio"] * (r["m"] + op["ajuste_manut"]),
        aliquota=r["aliquota"], aliquota_regra=r["aliquota_regra"], nopat=r["nopat"],
        ke_nom=cc["r"].get("ke_nom_emp"), wacc_nom=r["wacc"], wacc_real=w_real, kd=r["kd"], kd_info=r["kd_info"],
        e_mercado=r["e"], d_desconto=r["d"], d_sobre_e=r["d"] / r["e"] if r["e"] else None,
        bruta=r["bruta"], caixa=r["caixa"], caixa_livre=r["caixa_livre"], dl=r["dl"], minor=r["minor"],
        outros_passivos_financeiros=r["outros_passivos_financeiros"],
        ev_epv_firma=ev_epv, ponte_dl_mais_minor=ponte, ponte_sobre_ev_epv=(ponte / ev_epv if ev_epv else None),
        cap_inv=r["cap_inv"], roic=r["roic"], roic_filtro=r["roic_filtro"],
        lpa_norm=r["lpa_norm"], vpa=r["vpa"], reprod=r["reprod"],
        ltm=ltm_c, por_ano=por_ano,
    )


RE_FROTA = r"(?:compra|aquisi)\w*.*(?:imobilizado.*loca|ve[ií]culo|carros|frota)"
RE_CUSTO_VENDA = r"custo d[ae] venda d[ae] ativos utilizados na loca"


def frota_fco(cnpj: str, ano: int) -> tuple[float, float]:
    """(compra de frota no FCO, custo dos ativos de locação vendidos) do DFP `ano`, R$ mil, ambos positivos. Só diagnóstico."""
    import io
    import zipfile
    import pandas as pd
    z = zipfile.ZipFile(AQUI.parent / "dados" / "cvm" / f"dfp_{ano}.zip")
    n = [x for x in z.namelist() if "DFC_MI_con" in x][0]
    d = pd.read_csv(io.BytesIO(z.read(n)), sep=";", encoding="latin-1", dtype=str)
    d = d[(d["CNPJ_CIA"] == cnpj) & d["ORDEM_EXERC"].str.upper().str.startswith(("ÚLTIMO", "ULTIMO"))]
    v = d["VL_CONTA"].astype(float)
    compra = -v[d["CD_CONTA"].str.startswith("6.01") & d["DS_CONTA"].str.contains(RE_FROTA, case=False, na=False) & (v < 0)].sum()
    venda = v[d["CD_CONTA"].str.startswith("6.01.01") & d["DS_CONTA"].str.contains(RE_CUSTO_VENDA, case=False, na=False)].sum()
    return float(compra), float(venda)


def series_variante(tk: str, mudar) -> pathlib.Path:
    """Cópia da série do hold-out com `mudar(serie_do_ticker)` aplicado, na pasta temporária (nunca no hold-out nem no repo)."""
    from holdout_b36 import executor as X
    s = json.loads(X.SERIES.read_text(encoding="utf-8"))
    mudar(s[tk])
    import tempfile
    p = pathlib.Path(tempfile.gettempdir()) / "mesa_b45_series" / f"{tk}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(s, ensure_ascii=False), encoding="utf-8")
    return p


def contrafactuais(tk: str, series: pathlib.Path | None = None) -> dict:
    """Central e âncoras do motor com UMA camada trocada por vez (e todas juntas). Mesmo Ke (D/E a mercado não muda)."""
    import importlib
    from dataclasses import replace
    import credito
    import motor_nao_financeiras as M
    from dossie import base
    from holdout_b36 import executor as X
    c = X.cadastro()[tk]
    ins = X.ler_insumos(tk)
    nome = X.ficha_padrao(c, X._dia_statusinvest(tk))
    with X.registrado(c, nome, ins, series or X.SERIES), base.na_data(X.T), base.isolado(tk):
        emp = importlib.import_module(nome).empresa()
        mk0 = base.mercado(X.T)
        ec = M.estrutura_de_capital(emp, mk0)
        mk, ep = ec["mk"], ec["e_peso"]
        _, ltm = M.serie(tk)
        op = M.premissas_operacionais(emp)
        juros, _ = M.juros_do_periodo(ltm)
        sp_ltm, rat_ltm = credito.spread_sintetico(v if (v := (ltm.get("ebit") or 0) / juros) else None) if juros > 0 else (None, None)

        def roda(e, margem=None):
            r = M.valores(e, mk, margem=margem, e_peso=ep)
            cen, _ = M.central_de(r["anc"])
            return dict(central=cen, ancoras=r["anc"], kd=r["kd"], wacc_real=r["wacc_real"], ev_epv=r["nopat"] / r["wacc_real"],
                        dl_mais_minor=r["dl"] + r["minor"], pc=(emp.preco / cen if cen > 0 else float("inf")))
        e_rec = replace(emp, receita_meio=ltm["receita"], receita_meio_fonte="B45 contrafactual: receita LTM")
        e_kd = replace(emp, spread_kd=sp_ltm, spread_fonte=f"B45 contrafactual: cobertura EBIT LTM ÷ juros ({rat_ltm})")
        e_tudo = replace(e_kd, receita_meio=ltm["receita"], receita_meio_fonte="B45 contrafactual: receita LTM")
        out = {"base": roda(emp), "margem_5a": roda(emp, op["m50_5a"]), "receita_ltm": roda(e_rec),
               "kd_cobertura_ltm": roda(e_kd), "as_tres": roda(e_tudo, op["m50_5a"])}
        out["_kd_ltm"] = dict(cobertura_ltm=(ltm.get("ebit") or 0) / juros if juros > 0 else None, rating=rat_ltm, spread=sp_ltm)
        out["_pl_hist"] = emp.pl_hist
        out["_ke_nom"] = mk.ke_nom
    return out


def variante_movi3_frota() -> tuple[pathlib.Path, dict]:
    """Capex com a frota líquida (compra no FCO − custo dos carros vendidos) — o coletor só lê 6.02 (achado da B45)."""
    from holdout_b36 import executor as X
    cnpj = X.cadastro()["MOVI3"]["cnpj"]
    liq = {str(a): frota_fco(cnpj, a) for a in range(2016, 2026)}

    def mudar(s):
        for a, (compra, venda) in liq.items():
            if a in s["anual"] and s["anual"][a].get("capex") is not None:
                s["anual"][a]["capex"] += max(compra - venda, 0.0)
    return series_variante("MOVI3", mudar), liq


def variante_embj3_2019() -> pathlib.Path:
    """2019 como a DFP 2020 o reapresenta (aviação comercial de volta às operações continuadas): receita 21.802.075 e EBIT
    −309.760 (R$ mil). 'Outras' do ano ficam na mediana (sem excesso), porque o comparativo das contas 3.04.04/05 não foi lido."""
    def mudar(s):
        a = s["anual"]["2019"]
        a["receita"], a["ebit"] = 21802075.0, -309760.0
        a["outras_receitas_op"], a["outras_despesas_op"], a["impairment_outras"] = 0.0, 0.0, 0.0
    return series_variante("EMBJ3", mudar)


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    tks = [t.upper() for t in (argv if argv is not None else sys.argv[1:])] or list(PADRAO)
    out = {}
    for tk in tks:
        out[tk] = camadas(tk)
        d = out[tk]
        print(f"{tk}: palavra {d['palavra']} | central {d['central']:.2f} | P/C {d['pc']:.2f} | âncoras "
              + ", ".join(f"{k} {v:.2f}" for k, v in d["ancoras"].items())
              + f" | m50 {d['margem']['m50']:.3f} | DL {d['dl']:.0f} minor {d['minor']:.0f} EV(EPV) {d['ev_epv_firma'] or 0:.0f}")
        out[tk]["contrafactuais"] = cf = contrafactuais(tk)
        print("   ", {k: round(x["central"], 2) for k, x in cf.items() if not k.startswith("_")}, cf["_kd_ltm"])
    if "MOVI3" in out:
        p, liq = variante_movi3_frota()
        out["MOVI3"]["frota_fco_por_ano"] = liq
        out["MOVI3"]["variante_frota"] = v = camadas("MOVI3", p)
        print("    MOVI3 com frota no capex: âncoras", {k: round(x, 2) for k, x in v["ancoras"].items()}, "OE norm", v["oe_norm"])
    if "EMBJ3" in out:
        out["EMBJ3"]["variante_2019_reapresentado"] = v = camadas("EMBJ3", variante_embj3_2019())
        print("    EMBJ3 com 2019 reapresentado: âncoras", {k: round(x, 2) for k, x in v["ancoras"].items()},
              "m25/m50/m75", round(v["margem"]["m25"], 4), round(v["margem"]["m50"], 4), round(v["margem"]["m75"], 4))
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    antigo = json.loads(SAIDA.read_text(encoding="utf-8")) if SAIDA.exists() else {}
    antigo.update(out)
    SAIDA.write_text(json.dumps(antigo, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
