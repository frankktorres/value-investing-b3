"""CMIN3 (CSN Mineração) — ficha do dossiê · data-base 02/10/2026 · doutrina v2.2 · mesmo motor e mercado do hall.

Cíclica (minério de ferro). Ciclo normalizado EM NÚMERO antes do veredito (02 regra 7; doutrina §11.1, §11.4):
  · Janela da margem 2019–2025 (7 exercícios): o 1º DFP com DRE da companhia na CVM é o de 2020 (comparativo 2019; registro
    pré-IPO, IPO em fev/2021). É o máximo disponível (02 regra 4), não uma janela escolhida — e é curta para um ciclo de
    minério: 2020–23 tiveram o minério acima do meio, com o pico de 2021.
  · PREÇO: minério 62% Fe CFR China (FMI, série PIORECRUSDM do FRED, US$/t seca, nota B) × PTAX média mensal (BCB SGS 3698)
    corrigido pelo IPCA (BCB SGS 433) até o último mês com as três séries. Meio de ciclo = média de 10 anos 2016–25 em R$ de hoje
    (§11.1, como o barril do Lote 5) — a janela do preço NÃO encolhe com a da margem: encolher para 2019–25 poria o pico
    no meio de ciclo.
  · CÂMBIO: o preço em R$ de hoje é decomposto em US$ real (CPI-US, FRED CPIAUCSL) × câmbio real, para mostrar quanto do
    preço de meio vem do dólar e quanto do minério (`normalizacao()`).
  · RECEITA DE MEIO = receita dos 12m até jun/2026 (volume atual) × preço de meio ÷ preço dos 12m (jul/25–jun/26) × volume de
    meio ÷ volume dos 12m (VOLUME abaixo).
  · MARGEM: cada ano da janela é reexpresso ao preço de meio (motor: `fator_preco`): a receita do ano vai ao preço de meio e o
    custo fica, exceto a fração que acompanha o preço (`custo_variavel_preco`: royalty + minério comprado de terceiros, nota
    de custos por natureza do DFP). Sem isso, a mediana de 2019–25 leva o preço alto embutido e, aplicada à receita de meio,
    conta o preço duas vezes. A leitura literal (margem bruta da janela) e a janela 2019–25 para o preço vão como sensibilidade.
  · Capex de manutenção pela regra de cíclica (mediana de capex/receita contra D&A/receita): os projetos de expansão (P15,
    itabiritos) entram como manutenção — conservador; não há exceção de capex de expansão na doutrina (pendência do Frank).
  · PONTE firma → ação: passivo de contrato de R$ 11,8 bi (minério pré-vendido com componente de financiamento — a receita
    já entrou no caixa) e dividendos a pagar já ex (R$ 1,16 bi) entram como dívida (`outros_passivos`, ITR 2T26).
  · Kd = rf nominal + 1,5 p.p.; g real 1% (só vale se ROIC > WACC); P/L histórico fora do Bogle (lucro dominado pelo preço,
    como GGBR4/UNIP6 no Lote 6).
  · Ações: composição do capital do ITR de jun/2026 (CVM), sem tesouraria; o DFP 2025 informa 10× (corrigido em `base`).
  · Qualitativo: NUNCA digitado — vem de `notas.py` sobre a evidência (02 v4, regra 11) pelo `gerar.py`.
"""
from __future__ import annotations

import json
import pathlib
from functools import lru_cache

import pandas as pd

from dossie import base
from motor_nao_financeiras import CVM, Industrial

TK = "CMIN3"
ANOS = [str(a) for a in range(2019, 2026)]
JANELA_PRECO = (2016, 2025)
LTM = ("2025-07", "2026-06")
RAZAO_JANELA = ("1º DFP com DRE na CVM é o de 2020, com o comparativo de 2019 (registro pré-IPO; IPO fev/2021): janela = o "
                "máximo disponível (02 regra 4); a margem de cada ano é reexpressa ao minério de meio de 10 anos (fator_preco)")
MACRO = pathlib.Path(__file__).resolve().parents[2] / "dados" / "macro"
INSUMOS = pathlib.Path(__file__).resolve().parents[1] / "insumos" / f"{TK}.json"


def _fred(nome: str, col: int = 1) -> pd.Series:
    b = pd.read_csv(MACRO / nome)
    return pd.Series(pd.to_numeric(b.iloc[:, col], errors="coerce").values, index=pd.to_datetime(b.iloc[:, 0])).dropna()


@lru_cache(maxsize=None)
def minerio() -> dict:
    """Minério 62% (US$/t) × PTAX, em R$ de hoje (IPCA). Mesmo tratamento do barril (lote5_petroleo.macro)."""
    p = pd.DataFrame(json.loads((MACRO / "ptax_media_mensal.json").read_text()))
    ptax = pd.Series(p["valor"].astype(float).values, index=pd.to_datetime(p["data"], dayfirst=True))
    i = pd.DataFrame(json.loads((MACRO / "ipca_mensal.json").read_text()))
    ipca = pd.Series((1 + i["valor"].astype(float) / 100).cumprod().values, index=pd.to_datetime(i["data"], dayfirst=True))
    df = pd.DataFrame({"usd": _fred("fred_PIORECRUSDM.csv"), "ptax": ptax, "ipca": ipca, "cpi": _fred("cpi_us_fred.csv")})
    df["cpi"] = df["cpi"].interpolate(limit_area="inside")     # out/2025 sem CPI (paralisação do governo dos EUA)
    df = df.dropna()
    bi, bc = df["ipca"].iloc[-1], df["cpi"].iloc[-1]
    df["rs"] = df["usd"] * df["ptax"]
    df["rs_real"] = df["rs"] * bi / df["ipca"]
    df["usd_real"] = df["usd"] * bc / df["cpi"]
    df["fx_real"] = df["rs_real"] / df["usd_real"]
    anual = df.groupby(df.index.year).mean()
    a0, a1 = JANELA_PRECO
    meio = anual.loc[a0:a1]
    ltm = df.loc[LTM[0]:LTM[1]]
    if len(ltm) != 12:
        raise ValueError(f"minério: 12m incompletos ({len(ltm)} meses)")
    return dict(
        base=df.index[-1].strftime("%m/%Y"), anual=anual,
        meio_rs_real=meio["rs_real"].mean(), meio_usd_real=meio["usd_real"].mean(), meio_fx_real=meio["fx_real"].mean(),
        meio_usd_nominal=meio["usd"].mean(),
        ltm_rs=ltm["rs"].mean(), ltm_usd=ltm["usd"].mean(), ltm_ptax=ltm["ptax"].mean(),
        # mesmo critério do Lote 6: meio em R$ de hoje ÷ preço nominal médio dos 12m (a receita dos 12m é nominal)
        fator=meio["rs_real"].mean() / ltm["rs"].mean(),
        fator_preco={str(y): meio["rs_real"].mean() / anual.loc[y, "rs_real"] for y in map(int, ANOS)},
        janela_2019=anual.loc[2019:2025, "rs_real"].mean(),
    )


def insumos() -> dict:
    return json.loads(INSUMOS.read_text(encoding="utf-8")) if INSUMOS.exists() else {}


def _num(chave: str):
    """Número do insumo do dossiê (fonte A/B obrigatória; sem fonte não vale — regra 11)."""
    x = insumos().get(chave)
    if not x:
        raise ValueError(f"{TK}: insumo {chave} ausente em {INSUMOS.name}")
    if x.get("nota_fonte") not in ("A", "B") or not x.get("fonte"):
        raise ValueError(f"{TK}: insumo {chave} sem fonte A/B")
    return x["valor"]


def volume() -> dict:
    """Volume vendido (Mt) por ano e dos 12m, e o volume de meio declarado no insumo (com a razão)."""
    v = _num("volume_mt")              # {"2019": ..., ..., "ltm": ..., "meio": ..., "razao_meio": "..."}
    anos = {a: v[a] for a in ANOS if v.get(a) is not None}
    return dict(anos=anos, ltm=v["ltm"], meio=v["meio"], razao=v["razao_meio"],
                fator=v["meio"] / v["ltm"], mediana=float(pd.Series(list(anos.values())).median()))


def custo_variavel() -> float:
    return float(_num("custo_variavel_preco")["fracao"])


def receita_meio() -> float:
    base.carregar(TK)
    return CVM[TK]["ltm_2T26"]["receita"] * minerio()["fator"] * volume()["fator"]


def empresa(qualitativo: dict | None = None, desconto_controlador: dict | None = None, **sobrepor) -> Industrial:
    base.carregar(TK)
    m, vol = minerio(), volume()
    kw = dict(
        anos_ciclo=ANOS, anos_outras=ANOS, janela_razao=RAZAO_JANELA, outras_liquidas=True,
        receita_meio=receita_meio(), fator_preco=m["fator_preco"], custo_variavel_preco=custo_variavel(),
        receita_meio_fonte=(f"receita 12m × minério de meio ÷ minério dos 12m ({m['fator']:.3f}; FMI 62% × PTAX, R$ de hoje, "
                            f"{JANELA_PRECO[0]}–{JANELA_PRECO[1]}) × volume de meio ÷ volume 12m ({vol['fator']:.3f})"),
        # v2.3: os dois são financeiros (o passivo de contrato tem juros, nota 22; o provento a pagar já é ex) → entram na DL
        outros_passivos_financeiros=float(_num("outros_passivos")),
        outros_passivos_fonte="passivo de contrato (minério e energia pré-vendidos, com juros) + dividendos a pagar já ex, ITR 2T26",
        spread_kd=0.015, g_real=0.01, jcp_share=base.jcp_share(TK), pl_hist=None,
        defasagem_meses=base.defasagem(TK),
        defasagem_fonte="datas de pagamento da StatusInvest (C, só datas), média ponderada pelo valor, data-com 2021–26",
        desconto_controlador=desconto_controlador or {"tipo": "zero", "razao": "pendente: D3 do dossiê"},
        qualitativo=qualitativo or {},
    )
    kw.update(sobrepor)
    return Industrial(TK, "CSN Mineração", "ciclica", preco=base.preco(TK), n_acoes=base.acoes_itr(TK), **kw)


def normalizacao(desconto_controlador: dict | None = None) -> dict:
    """Números do ciclo para o anexo e para a tabela de sensibilidade do dossiê (a: literal; b: preço 2019–25; c: adotado),
    com o mesmo desconto de controlador do central (senão a linha "c" não bate com o veredito)."""
    from motor_nao_financeiras import avaliar
    MK = base.mercado()     # o mercado da data-base corrente (v2.3: o veredito novo é de outra data)
    base.carregar(TK)       # chamável sozinha (adversário, 07/10)
    m, vol = minerio(), volume()
    rec_ltm = CVM[TK]["ltm_2T26"]["receita"]
    alt = {
        "c (adotado): preço 10a + margem reexpressa": {},
        "a (literal): preço 10a + margem bruta 2019–25": dict(fator_preco=None, custo_variavel_preco=0.0),
        "b (UNIP6): preço e margem 2019–25": dict(fator_preco=None, custo_variavel_preco=0.0,
                                               receita_meio=rec_ltm * m["janela_2019"] / m["ltm_rs"] * vol["fator"]),
    }
    sens = {}
    for nome, kw in alt.items():
        r = avaliar(empresa(desconto_controlador=desconto_controlador, **kw), MK)
        sens[nome] = dict(central=r["central"], m50=r["op"]["m50"], receita_meio=r["op"]["receita_meio"], palavra=r["palavra_regua"])
    return dict(minerio=m, volume=vol, custo_variavel=custo_variavel(), sensibilidade=sens)
