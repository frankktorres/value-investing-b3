"""Fatias 9-10: retorno total, eventos em ações, proventos e o sentinela do preço de corte.

Duas partes:
  · SINTÉTICA (rápida, sem dado): a aritmética do índice — desdobramento neutro, provento no dia ex,
    deslistagem reinvestida no Ibovespa, evento depois de T+h que não pode mexer no retorno e
    evento dentro da janela que tem de mexer (o controle que mostra o teste vivo).
  · DADO REAL (pula sem os parquets): o sentinela nos 24 cortes, com o META-TESTE que injeta o
    vazamento clássico (preço de corte retroajustado por evento futuro) e EXIGE que o sentinela
    acuse — lição da Etapa 3: teste que afirma ausência precisa provar que enxergaria a presença.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.calendario import Calendario
from backtest.config import Config
from backtest.precos import eventos as ev_mod
from backtest.precos import retorno

# ----------------------------------------------------------------------------- mundo sintético
DIAS = tuple(d.strftime("%Y-%m-%d") for d in pd.bdate_range("2020-06-01", "2022-01-31"))
CAL = Calendario(DIAS)
CFG = Config(datas_corte=("2020-06-30",), horizontes_anos=(1,))
T = "2020-06-30"


def _precos(spec: dict[str, list[tuple[str, float]]], ate: dict[str, str] | None = None) -> pd.DataFrame:
    """spec: ticker -> [(a partir de, preço)], degraus. `ate`: último dia de negócio do ticker."""
    linhas = []
    for t, degraus in spec.items():
        fim = (ate or {}).get(t, DIAS[-1])
        for d in DIAS:
            if d > fim:
                break
            p = [v for ini, v in degraus if ini <= d][-1]
            linhas.append({"data": d, "ticker": t, "preult": p, "especi": "ON NM", "nomres": t,
                           "codisi": "BR" + t, "totneg": 1, "voltot": 1e7, "codbdi": "02"})
    return pd.DataFrame(linhas)


def _ev(linhas=()) -> pd.DataFrame:
    return pd.DataFrame(list(linhas), columns=["ticker", "data_ex", "fator", "fonte"])


def _dv(linhas=()) -> pd.DataFrame:
    return pd.DataFrame(list(linhas), columns=["ticker", "data_ex", "valor_acao", "tipo"])


IBOV_PLANO = pd.Series(100.0, index=list(DIAS))


def _rodar(precos, eventos, dinheiro, ibov=IBOV_PLANO, tickers=("AAAA3",)) -> pd.DataFrame:
    lin = {t: t for t in precos["ticker"].unique()}
    idx = retorno.indices(precos, eventos, dinheiro, lin, CFG)
    uni = pd.DataFrame({"data_corte": T, "ticker": list(tickers)})
    return retorno.painel(idx, uni, precos, CAL, ibov, lin, CFG).set_index("ticker")


def test_desdobramento_e_provento_no_dia_ex_dao_retorno_zero_com_preco_caindo() -> None:
    # 10 -> desdobra 1:2 em 01/09 (preço 5) -> paga 0,50 em 01/10 (preço 4,50). Dono não ganhou nada.
    p = _precos({"AAAA3": [("2020-06-01", 10.0), ("2020-09-01", 5.0), ("2020-10-01", 4.5)]})
    r = _rodar(p, _ev([("AAAA3", "2020-09-01", 2.0, "fre")]),
               _dv([("AAAA3", "2020-10-01", 0.5, "DIVIDENDO")])).loc["AAAA3"]
    assert r["status"] == "ok"
    assert r["ret_total"] == pytest.approx(0.0, abs=1e-12)
    assert r["ret_preco"] == pytest.approx(4.5 * 2 / 10 - 1)       # -10%: só preço, sem o provento
    assert r["preco_corte"] == 10.0 and r["data_preco"] == T


def test_jcp_liquido_desconta_o_ir() -> None:
    p = _precos({"AAAA3": [("2020-06-01", 10.0), ("2020-10-01", 9.0)]})
    r = _rodar(p, _ev(), _dv([("AAAA3", "2020-10-01", 1.0, retorno.JCP)])).loc["AAAA3"]
    assert r["ret_total"] == pytest.approx(0.0, abs=1e-12)
    assert r["ret_liq"] == pytest.approx((9 + 0.85) / 10 - 1)


def test_deslistagem_reinveste_no_ibov_ate_o_fim_do_horizonte() -> None:
    p = _precos({"AAAA3": [("2020-06-01", 10.0), ("2020-11-02", 12.0)]}, ate={"AAAA3": "2020-12-31"})
    ib = pd.Series([100.0 if d <= "2020-12-31" else 200.0 for d in DIAS], index=list(DIAS))
    r = _rodar(p, _ev(), _dv(), ibov=ib).loc["AAAA3"]
    assert bool(r["deslistado"]) and r["data_ultimo_negocio"] == "2020-12-31"
    assert r["ret_total"] == pytest.approx(1.2 * 2.0 - 1)


def test_evento_depois_de_t_mais_h_nao_mexe_no_retorno_e_dentro_mexe() -> None:
    p = _precos({"AAAA3": [("2020-06-01", 10.0), ("2021-09-01", 3.0)]})
    fora = _rodar(p, _ev([("AAAA3", "2021-09-01", 3.0, "fre")]), _dv()).loc["AAAA3"]
    sem = _rodar(p, _ev(), _dv()).loc["AAAA3"]
    assert fora["ret_total"] == sem["ret_total"] == pytest.approx(0.0)
    # controle: o mesmo evento DENTRO de (T, T+h] tem de aparecer
    p2 = _precos({"AAAA3": [("2020-06-01", 10.0), ("2021-03-01", 3.0)]})
    dentro = _rodar(p2, _ev([("AAAA3", "2021-03-01", 3.0, "fre")]), _dv()).loc["AAAA3"]
    sem2 = _rodar(p2, _ev(), _dv()).loc["AAAA3"]
    assert dentro["ret_total"] == pytest.approx(-0.1)
    assert sem2["ret_total"] == pytest.approx(-0.7)


def test_evento_sem_fator_na_janela_tira_o_retorno_e_marca_status() -> None:
    p = _precos({"AAAA3": [("2020-06-01", 10.0), ("2021-03-01", 5.0)]})
    r = _rodar(p, _ev([("AAAA3", "2021-03-01", np.nan, "sem_fator")]), _dv()).loc["AAAA3"]
    assert r["status"] == "sem_fator" and np.isnan(r["ret_total"])


def test_salto_nao_ajustado_nao_entra_no_indice() -> None:
    p = _precos({"AAAA3": [("2020-06-01", 0.02), ("2021-03-01", 0.01)]})
    r = _rodar(p, _ev([("AAAA3", "2021-03-01", 1.0, "salto_nao_ajustado")]), _dv()).loc["AAAA3"]
    assert r["ret_total"] == pytest.approx(-0.5)


def test_horizonte_alem_do_dado_e_status_nao_zero() -> None:
    cal = Calendario(tuple(d for d in DIAS if d <= "2021-03-31"))
    p = _precos({"AAAA3": [("2020-06-01", 10.0)]}, ate={"AAAA3": "2021-03-31"})
    lin = {"AAAA3": "AAAA3"}
    idx = retorno.indices(p, _ev(), _dv(), lin, CFG)
    r = retorno.painel(idx, pd.DataFrame({"data_corte": [T], "ticker": ["AAAA3"]}), p, cal,
                       IBOV_PLANO, lin, CFG)
    assert r["status"].tolist() == ["horizonte_fora"]


def test_encaixe_so_aceita_fator_unico_da_grade() -> None:
    g = ev_mod.grade(Config())
    assert ev_mod.encaixe(8.0 * 1.01, g, 0.02) is None          # 8 não está na grade -> não inventa
    assert ev_mod.encaixe(2.0 * 1.01, g, 0.02) == 2.0
    assert ev_mod.encaixe(1.025, g, 0.02) is None                # 1,02 e 1,03 empatam -> ambíguo
    assert ev_mod.encaixe(float("nan"), g, 0.02) is None


# ----------------------------------------------------------------------------- sentinela sintético
def _vazamento_retroajustado(dados, tickers, corte, cal):
    """O ERRO que o sentinela existe para pegar: preço de corte dividido pelo produto dos eventos
    POSTERIORES a T (é o que uma série 'ajustada' de terceiros entrega)."""
    base = retorno.precos_de_corte(dados["precos"], tickers, corte, cal)
    e = dados["eventos"]
    fut = e[e["data_ex"] > corte].groupby("ticker")["fator"].prod()
    base["preco_corte"] = base["preco_corte"] / base["ticker"].map(fut).fillna(1.0)
    return base


def test_sentinela_sintetico_limpo_e_meta_teste_acusa() -> None:
    p = _precos({"AAAA3": [("2020-06-01", 10.0), ("2020-09-01", 5.0)]})
    dados = {"precos": p, "eventos": _ev([("AAAA3", "2020-09-01", 2.0, "fre")]), "dinheiro": _dv()}
    assert retorno.sentinela_corte(dados, CAL, T, ["AAAA3"]).empty
    vaz = retorno.sentinela_corte(dados, CAL, T, ["AAAA3"], fn=_vazamento_retroajustado)
    assert len(vaz) == 1 and vaz["preco_corte_cheio"].iloc[0] == 5.0


# ----------------------------------------------------------------------------- dado real
pytestmark_real = pytest.mark.skipif(
    not (retorno.DESTINO.parent / "ibov.parquet").exists()
    or not (retorno.DESTINO.parent / "proventos" / "dinheiro").exists(),
    reason="sem ibov.parquet / cache de proventos (python -m backtest.precos.ibov / proventos_b3)")


@pytest.fixture(scope="module")
def real():
    return retorno.insumos()


@pytestmark_real
def test_sentinela_real_nos_24_cortes_e_meta_teste(real) -> None:
    dados = {k: real[k] for k in ("precos", "eventos", "dinheiro")}
    u = real["universo"]
    for corte, g in u.groupby("data_corte"):
        assert retorno.sentinela_corte(dados, real["cal"], corte, g["ticker"]).empty, corte
    # meta: num corte com evento futuro conhecido (MGLU3 desdobra em 2017, 2019, 2020), o
    # vazamento injetado TEM de aparecer
    vaz = retorno.sentinela_corte(dados, real["cal"], "2016-12-31", ["MGLU3"], fn=_vazamento_retroajustado)
    assert "MGLU3" in vaz.index


@pytestmark_real
def test_eventos_conhecidos_nas_datas_certas(real) -> None:
    e = real["eventos"].set_index(["ticker", "data_ex"])["fator"]
    esperado = {("MGLU3", "2015-10-01"): 1 / 8, ("MGLU3", "2017-09-05"): 8.0,
                ("MGLU3", "2019-08-06"): 8.0, ("MGLU3", "2020-10-14"): 4.0,
                ("MGLU3", "2024-05-27"): 0.1,
                ("ITSA4", "2014-05-05"): 1.1, ("ITSA4", "2015-05-05"): 1.1, ("ITSA4", "2016-05-02"): 1.1}
    for k, f in esperado.items():
        assert e.get(k) == pytest.approx(f, rel=0.01), k
    # PETR4 não teve evento em ações de 2014 a 2026
    assert "PETR4" not in real["eventos"]["ticker"].values


@pytestmark_real
def test_proventos_conferem_contra_o_cotahist(real) -> None:
    d = real["dinheiro"]
    assert d["conferido"].mean() >= 0.95
    # ITSA4 paga JCP mensal: dezenas de registros por ano
    assert (d["ticker"] == "ITSA4").sum() > 100


@pytestmark_real
def test_troca_de_codigo_nao_e_deslistagem(real) -> None:
    lin = real["linhagem"]
    for antigo, novo in (("KROT3", "COGN3"), ("DTEX3", "DXCO3"), ("BRDT3", "VBBR3"), ("BVMF3", "B3SA3")):
        assert lin[novo] == lin[antigo], (antigo, novo)


@pytestmark_real
def test_conferencia_externa_a_1pp(real) -> None:
    """Retorno total contra o Yahoo (nota C, congelado em fixture). Onde diverge, a divergência
    está explicada por provento que o Yahoo omite — e isso também é testado contra a B3."""
    import json
    import pathlib
    fx = json.loads((pathlib.Path(__file__).parent / "conferencia_externa.json").read_text(encoding="utf-8"))
    r = retorno.retornos(x=real).set_index(["ticker", "data_corte", "h"])
    for c in fx["casos"]:
        nosso = r.loc[(c["ticker"], c["corte"], c["h"]), "ret_total"]
        assert abs(nosso - c["yahoo"]) * 100 <= fx["tolerancia_pp"], c
    for c in fx["relativos"]:
        nosso = r.loc[(c["ticker"], c["corte"], c["h"]), "ret_total"]
        assert abs((1 + nosso) / (1 + c["yahoo"]) - 1) <= c["tolerancia_rel"], c
    d = real["dinheiro"]
    petr = d[(d["ticker"] == "PETR4") & (d["data_ex"] == "2022-11-22")]["valor_acao"].sum()
    assert petr == pytest.approx(3.3489, abs=1e-3)
    bb = d[(d["ticker"] == "BBAS3") & (d["data_ex"] == "2023-11-22")]["valor_acao"].sum()
    assert bb == pytest.approx(0.101989 + 0.686222, abs=1e-5)


# ----------------------------------------------------------------------------- regressões do adversario
def test_grade_nao_inventa_bonificacao_em_dia_parado() -> None:
    g = ev_mod.grade(Config())
    assert ev_mod.encaixe(1 / 0.9977, g, 0.02) != 1.02          # SANB 2014: razão 0,9977


def test_codigo_reutilizado_nao_congela_o_preco() -> None:
    """NATU3: parou em 2019, voltou em 2025 como outra coisa. A janela que começa antes da parada vale
    o último negócio reinvestido no Ibov — nem preço congelado, nem a razão entre as duas empresas."""
    dias = tuple(d.strftime("%Y-%m-%d") for d in pd.bdate_range("2020-06-01", "2023-12-29"))
    cal = Calendario(dias)
    linhas = [{"data": d, "ticker": "AAAA3", "preult": 10.0 if d <= "2020-09-30" else 3.0}
              for d in dias if d <= "2020-09-30" or d >= "2021-12-01"]
    p = pd.DataFrame(linhas)
    ib = pd.Series([100.0 if d <= "2020-09-30" else 150.0 for d in dias], index=list(dias))
    cfg = Config(datas_corte=(T,), horizontes_anos=(1, 3))
    lin = {"AAAA3": "AAAA3"}
    idx = retorno.indices(p, _ev(), _dv(), lin, cfg, cal.pregoes)
    r = retorno.painel(idx, pd.DataFrame({"data_corte": [T], "ticker": ["AAAA3"]}), p, cal, ib, lin,
                       cfg).set_index("h")
    for h in (1, 3):
        assert bool(r.loc[h, "deslistado"]) and r.loc[h, "data_ultimo_negocio"] == "2020-09-30"
        assert r.loc[h, "ret_total"] == pytest.approx(0.5)       # 10 -> 10, depois Ibov +50%


@pytestmark_real
def test_regressoes_do_adversario_no_dado_real(real) -> None:
    r = retorno.retornos(x=real).set_index(["ticker", "data_corte", "h"])
    # BDI 58 (Chapter 11): GOLL4 continua no arquivo e cai até o fim, não vai para o Ibov
    assert r.loc[("GOLL4", "2023-06-30", 1), "ret_total"] < -0.85
    assert not r.loc[("GOLL4", "2023-06-30", 1), "deslistado"]
    # NATU3 parou em 2019: deslistada na janela, nunca 0,000 congelado
    assert bool(r.loc[("NATU3", "2019-12-31", 1), "deslistado"])
    assert r.loc[("NATU3", "2019-12-31", 1), "ret_total"] != 0.0
    # repetição de parcela com diferença na 7ª casa conta uma vez só
    d = real["dinheiro"]
    recv = d[(d["ticker"] == "RECV3") & (d["data_com"] == "2026-01-08")]
    assert len(recv) == 1
    # VIVT3: marca-cauda depois do desdobramento de 2025 não tira linhas do painel
    v = r.xs("VIVT3", level="ticker")
    assert (v["status"] != "sem_fator").all()
