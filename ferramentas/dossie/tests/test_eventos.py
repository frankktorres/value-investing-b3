"""Eventos em ações (dossie/base.eventos_em_acoes): só bonificação e desdobramento têm semântica conferida contra a CVM."""
import pandas as pd
import pytest
from dados_opcionais import requer_suplemento_b3

from dossie import base


def _sup(*linhas):
    return pd.DataFrame([dict(raiz=r, tipo=t, fator_b3=f, data_com=c, data_aprovacao=a, isin="") for r, t, f, c, a in linhas])


def test_desdobramento_bbas_2024_dobra_as_acoes():
    # BBAS 100,0 em 15/04/2024: DFP 2023 → 2024 = 2.865.417.020 → 5.730.834.040 ações integralizadas (CVM, fonte A)
    ev = base.eventos_em_acoes("BBAS3", _sup(("BBAS", "DESDOBRAMENTO", 100.0, "2024-04-15", "2024-02-02")))
    assert ev == [{"tipo": "DESDOBRAMENTO", "data_com": "2024-04-15", "aprovacao": "2024-02-02", "multiplicador": 2.0}]
    assert 2_865_417_020 * ev[0]["multiplicador"] == 5_730_834_040


def test_desdobramento_4_por_1_e_bonificacao():
    ev = base.eventos_em_acoes("MGLU3", _sup(("MGLU", "DESDOBRAMENTO", 300.0, "2020-10-13", "2020-10-07")))
    assert ev[0]["multiplicador"] == 4.0
    ev = base.eventos_em_acoes("BLAU3", _sup(("BLAU", "BONIFICACAO", 30.0, "2026-01-05", "2025-12-15")))
    assert ev[0]["multiplicador"] == pytest.approx(1.3)


def test_so_a_raiz_do_ticker_conta():
    s = _sup(("HYPE", "DESDOBRAMENTO", 100.0, "2009-12-30", "2009-12-30"), ("MGLU", "GRUPAMENTO", 0.1, "2024-05-24", "2024-04-24"))
    assert [e["multiplicador"] for e in base.eventos_em_acoes("HYPE3", s)] == [2.0]


def test_mesmo_evento_em_varios_isins_conta_uma_vez():
    # ITUB: bonificação de 3% e desdobramento de 50% repetidos para ON e PN no suplemento real (achado do adversário)
    s = _sup(("ITUB", "DESDOBRAMENTO", 50.0, "2018-11-19", "2018-07-27"), ("ITUB", "DESDOBRAMENTO", 50.0, "2018-11-19", "2018-07-27"),
             ("ITUB", "BONIFICACAO", 3.0, "2019-12-30", "2019-12-20"), ("ITUB", "BONIFICACAO", 3.0, "2019-12-30", "2019-12-20"))
    ev = base.eventos_em_acoes("ITUB4", s)
    assert [e["multiplicador"] for e in ev] == pytest.approx([1.5, 1.03])


def test_fatores_diferentes_por_classe_na_mesma_data_falham_alto():
    s = _sup(("XPTO", "BONIFICACAO", 10.0, "2024-05-24", "2024-04-24"), ("XPTO", "BONIFICACAO", 20.0, "2024-05-24", "2024-04-24"))
    with pytest.raises(NotImplementedError):
        base.eventos_em_acoes("XPTO3", s)


@pytest.mark.parametrize("tipo", ["INCORPORACAO", "CIS RED CAP"])
def test_tipo_sem_semantica_conferida_falha_alto(tipo):
    with pytest.raises(NotImplementedError):
        base.eventos_em_acoes("XPTO3", _sup(("XPTO", tipo, 0.1, "2024-05-24", "2024-04-24")))


@pytest.mark.parametrize("fator", [0.0, -50.0, float("nan")])
def test_fator_invalido_falha_alto(fator):
    with pytest.raises(ValueError):
        base.eventos_em_acoes("XPTO3", _sup(("XPTO", "DESDOBRAMENTO", fator, "2024-05-24", "2024-04-24")))


@requer_suplemento_b3
def test_hype3_real_carrega():
    # o suplemento real da B3 (cache do backtest): HYPE3 só tem o desdobramento de 30/12/2009, fator 100 (2 por 1)
    ev = base.eventos_em_acoes("HYPE3")
    assert [(e["tipo"], e["data_com"], e["multiplicador"]) for e in ev] == [("DESDOBRAMENTO", "2009-12-30", 2.0)]


def test_grupamento_usa_o_fator_como_razao_e_falha_com_fator_de_percentual():
    ev = base.eventos_em_acoes("MGLU3", _sup(("MGLU", "GRUPAMENTO", 0.1, "2024-05-24", "2024-04-24")))
    assert ev[0]["multiplicador"] == pytest.approx(0.1)
    with pytest.raises(ValueError, match="razão"):
        base.eventos_em_acoes("XPTO3", _sup(("XPTO", "GRUPAMENTO", 100.0, "2024-05-24", "2024-04-24")))


@requer_suplemento_b3
def test_leve3_real_carrega_com_o_par_de_2012():
    ev = {(e["tipo"], e["data_com"]): e["multiplicador"] for e in base.eventos_em_acoes("LEVE3")}
    assert ev[("DESDOBRAMENTO", "2012-05-14")] * ev[("GRUPAMENTO", "2012-05-14")] == pytest.approx(3.0)


def test_dois_eventos_do_mesmo_tipo_na_mesma_data_em_todas_as_classes_contam_os_dois():
    linhas = [dict(raiz="XPTO", tipo="BONIFICACAO", fator_b3=f, data_com="1992-04-28", data_aprovacao="1992-04-28", isin=i)
              for i in ("BRXPTOACNOR1", "BRXPTOACNPR1") for f in (20.0, 1080.0)]
    ev = base.eventos_em_acoes("XPTO3", pd.DataFrame(linhas))
    assert sorted(e["multiplicador"] for e in ev) == pytest.approx([1.2, 11.8])
    linhas[-1]["fator_b3"] = 500.0                      # a PN com fator diferente da ON → falha alto
    with pytest.raises(NotImplementedError, match="por classe"):
        base.eventos_em_acoes("XPTO3", pd.DataFrame(linhas))


@pytest.mark.parametrize("tk, raiz, desd, grup, data", [("TIMS3", "TIMS", 100.0, 0.01, "2025-07-02"),
                                                       ("VIVT3", "VIVT", 80.0, 0.025, "2025-04-14")])
def test_par_desdobramento_grupamento_sem_conferencia_falha_alto(tk, raiz, desd, grup, data):
    """A B3 não publica o par de um jeito só: TIMS3 (×1 de fato) e VIVT3 (×2) sairiam ×0,02 e ×0,045 (adversário, 08/10)."""
    s = _sup((raiz, "DESDOBRAMENTO", desd, data, data), (raiz, "GRUPAMENTO", grup, data, data))
    with pytest.raises(NotImplementedError, match="mesma data"):
        base.eventos_em_acoes(tk, s)
