"""Fatia 8 — hipótese (a) da contagem de ações: a discordância FRE × composicao_capital se
concentra em empresa abaixo do piso de liquidez?

Critério declarado ANTES de medir (06/10/2026): (a) é um não-problema se, entre as empresas ACIMA
do piso de liquidez (`config.limite_liquidez`, R$ reais, 60 pregões até 31/12), a concordância for
>= 90% com tolerância de 1%. Abaixo disso a discordância não é só ilíquida e o P/C continua sem
base nas empresas que o backtest realmente usa.

Comparação, para cada (companhia, ano Y de 2020 a 2024), em 31/12/Y:
  FRE:   o FRE ENTREGUE EM Y+1 — `dt_refer` = Y+1-01-01 (convenção até 2022) ou Y+1-12-31 (de 2023
         em diante: o FRE de "2023-12-31" é entregue em mai/2023, então descreve o meio de 2023, não
         o fim) —, com `aprovacao` <= Y-12-31; vale a aprovação mais recente, depois a versão maior.
         A janela antiga [Y-12-31, Y+1-01-01] perdia 2022 inteiro (nenhum FRE com dt_refer nela) e
         usava o FRE entregue em Y em 2023-24 (achado do `adversario`, 06/10/2026).
  DFP:   `composicao_capital` de 31/12/Y, versão maior.
O `composicao_capital` traz `acoes_integralizadas` e `acoes_total` (= integralizadas - tesouraria);
o FRE traz capital integralizado, SEM abater tesouraria. Compara-se o FRE contra as DUAS, e a
diferença entre elas é o teste da hipótese (d): a comparação original podia estar contrastando
bruto com líquido de tesouraria.

UNIDADE: o `composicao_capital` da DFP vem em MILHARES em parte das companhias (BRB 2020: 28.014
no DFP contra 28.014.650 no FRE; o BB vem em unidades). Medido na primeira rodada: era a causa da
quase totalidade da "discordância" de 58%. `ok_*` aceita razão 1 OU 1000 (`escala_mil`).

Liquidez da companhia = soma dos volumes de todos os seus papéis (ON+PN+UNT...), via o mapa
ticker <-> CNPJ do FCA (`valor_mobiliario`, com datas de negociação).
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from .. import cotahist
from ..config import PADRAO, limite_liquidez
from .identidade import _cnpj_do_ticker_em, mapa_ticker_cnpj

AQUI = Path(__file__).resolve().parent.parent
DADOS = AQUI / "dados"
ANOS = range(2020, 2025)
TOLERANCIA = 0.01
CRITERIO_NAO_PROBLEMA = 0.90


def liquidez_por_cnpj(corte: str, m: pd.DataFrame, cal) -> pd.Series:
    liq = cotahist.liquidez_media(corte, cal=cal)           # por ticker, só ações/units
    mapa = _cnpj_do_ticker_em(m, corte)
    c = liq.rename_axis("ticker").reset_index()
    c["cnpj"] = c["ticker"].map(mapa)
    return c.dropna(subset=["cnpj"]).groupby("cnpj")["liquidez"].sum()


def _fre_fim_de(fre: pd.DataFrame, ano: int) -> pd.DataFrame:
    fim = f"{ano}-12-31"
    entregue_em_y1 = fre["dt_refer"].isin((f"{ano + 1}-01-01", f"{ano + 1}-12-31"))
    d = fre[entregue_em_y1
            & (fre["aprovacao"].fillna("") <= fim) & (fre["aprovacao"].fillna("") != "")]
    d = d.sort_values(["cnpj", "aprovacao", "versao"]).groupby("cnpj").tail(1)
    return d[["cnpj", "acoes_total", "acoes_on", "acoes_pn", "acoes_ambiguo"]].rename(
        columns={"acoes_total": "fre_total", "acoes_on": "fre_on", "acoes_pn": "fre_pn"})


def comparar(tolerancia: float = TOLERANCIA) -> pd.DataFrame:
    fre = pd.read_parquet(DADOS / "acoes_fre.parquet")
    comp = pd.read_parquet(DADOS / "acoes_composicao.parquet")
    m = mapa_ticker_cnpj()
    cal = cotahist.calendario()
    linhas = []
    for ano in ANOS:
        fim = f"{ano}-12-31"
        c = comp[(comp["dt_refer"] == fim) & (comp["fonte_acoes"] == "dfp_composicao")]
        c = c.sort_values(["cnpj", "versao"]).groupby("cnpj").tail(1)[
            ["cnpj", "acoes_integralizadas", "acoes_total"]].rename(
            columns={"acoes_integralizadas": "dfp_integr", "acoes_total": "dfp_liquido"})
        j = _fre_fim_de(fre, ano).merge(c, on="cnpj", how="inner")
        j["ano"] = ano
        liq = liquidez_por_cnpj(fim, m, cal)
        j["liquidez"] = j["cnpj"].map(liq)                      # NaN = nenhum papel no COTAHIST
        j["piso"] = limite_liquidez(PADRAO, fim)
        linhas.append(j)
    d = pd.concat(linhas, ignore_index=True)
    rel = lambda a, b: (a - b).abs() / b.clip(lower=1)           # noqa: E731
    # Escala: a referência da DFP pode estar em milhares. Compara em unidades E com a referência x1000.
    d["ok_integr_bruto"] = rel(d["fre_total"], d["dfp_integr"]) <= tolerancia      # sem corrigir unidade
    ok_u = rel(d["fre_total"], d["dfp_integr"]) <= tolerancia
    ok_m = rel(d["fre_total"], d["dfp_integr"] * 1000) <= tolerancia
    d["escala_mil"] = ok_m & ~ok_u
    d["ok_integr"] = ok_u | ok_m
    d["ok_liquido"] = (rel(d["fre_total"], d["dfp_liquido"]) <= tolerancia) | (
        rel(d["fre_total"], d["dfp_liquido"] * 1000) <= tolerancia)
    # Hipótese (b): somar por classe (ON + PN) quando `Quantidade_Total_Acoes` vem zerada/errada.
    soma = d["fre_on"].fillna(0) + d["fre_pn"].fillna(0)
    ok_soma = (rel(soma, d["dfp_integr"]) <= tolerancia) | (rel(soma, d["dfp_integr"] * 1000) <= tolerancia)
    d["ok_soma_classes"] = ok_soma
    d["ok_total_ou_soma"] = d["ok_integr"] | ok_soma
    d["ok_qualquer"] = d["ok_integr"] | d["ok_liquido"]
    d["liquida"] = d["liquidez"] >= d["piso"]
    d["sem_papel"] = d["liquidez"].isna()
    return d


def resumo(d: pd.DataFrame) -> dict[str, object]:
    def taxa(x: pd.DataFrame, col: str) -> float:
        return float(x[col].mean()) if len(x) else float("nan")

    liq, ilq = d[d["liquida"]], d[~d["liquida"]]
    disc = d[~d["ok_integr"]]
    r = {
        "n_cnpj_ano": int(len(d)), "n_cnpj": int(d["cnpj"].nunique()),
        "concorda_sem_corrigir_unidade": taxa(d, "ok_integr_bruto"),
        "frac_referencia_em_milhares": taxa(d, "escala_mil"),
        "concorda_vs_liquido_de_tesouraria": taxa(d, "ok_liquido"),
        "concorda_vs_integralizado": taxa(d, "ok_integr"),
        "concorda_qualquer": taxa(d, "ok_qualquer"),
        "n_liquidas": int(len(liq)), "n_iliquidas_ou_sem_papel": int(len(ilq)),
        "n_sem_papel_no_cotahist": int(d["sem_papel"].sum()),
        "liquidas_concorda_vs_liquido": taxa(liq, "ok_liquido"),
        "liquidas_concorda_sem_corrigir_unidade": taxa(liq, "ok_integr_bruto"),
        "liquidas_concorda_vs_integr": taxa(liq, "ok_integr"),
        "liquidas_concorda_qualquer": taxa(liq, "ok_qualquer"),
        "liquidas_concorda_total_ou_soma_classes": taxa(liq, "ok_total_ou_soma"),
        "todas_concorda_total_ou_soma_classes": taxa(d, "ok_total_ou_soma"),
        "iliquidas_concorda_vs_liquido": taxa(ilq, "ok_liquido"),
        "discordantes_apos_unidade": int(len(disc)),
        "discordantes_abaixo_do_piso_pct": float((~disc["liquida"]).mean()) if len(disc) else float("nan"),
        "criterio_a_90pct_nas_liquidas": CRITERIO_NAO_PROBLEMA,
    }
    # Dois vereditos, com nome que diz o que medem (o booleano único contradizia o número relatado):
    #  · a hipótese (a) como FORMULADA — liquidez explica a discordância — usa a taxa sem corrigir
    #    unidade, e é refutada: quem explica é a unidade da referência;
    #  · a pergunta que importa ao backtest — o FRE é confiável nas líquidas? — usa a taxa corrigida.
    r["hipotese_a_liquidez_explica"] = bool(
        r["liquidas_concorda_sem_corrigir_unidade"] >= CRITERIO_NAO_PROBLEMA)
    r["fre_confiavel_nas_liquidas"] = bool(r["liquidas_concorda_vs_integr"] >= CRITERIO_NAO_PROBLEMA)
    return r


def main() -> int:
    d = comparar()
    r = resumo(d)
    for k, v in r.items():
        print(f"{k}: {v:.4f}" if isinstance(v, float) else f"{k}: {v}")
    (DADOS / "diagnostico_acoes.json").write_text(
        json.dumps(r, indent=2, ensure_ascii=False), encoding="utf-8")
    d.to_parquet(DADOS / "diagnostico_acoes.parquet", index=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
