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
    # CIS RED CAP sem a coluna do ativo emitido (o formato do cache do backtest) também falha alto: sem ela não se sabe qual
    # linha é a da própria ação
    with pytest.raises(NotImplementedError):
        base.eventos_em_acoes("XPTO3", _sup(("XPTO", tipo, 0.1, "2024-05-24", "2024-04-24")))


# ---------------------------------------------------------------- cisão com redução de capital (B40, 25/11/2026)
# Linhas literais do suplemento da B3 (GetListedSupplementCompany): por classe, uma linha com a ação NOVA (assetIssued de
# outra raiz, fator = ações novas por 100) e uma com a PRÓPRIA ação (fator 100 = mantém as ações). Fonte A da quantidade:
# CVM, FRE, capital_social_reducao (redução por cisão com 0 ações canceladas) — tests/test_fase3_proventos_b3.py.
def _cis(raiz, data_com, aprov, *pares):
    """pares = (isin da classe, ativo emitido, fator)"""
    return pd.DataFrame([dict(raiz=raiz, tipo="CIS RED CAP", fator_b3=f, data_com=data_com, data_aprovacao=aprov, isin=i,
                              ativo_emitido=a) for i, a, f in pares])


CISOES = {
    # MRV → LOG: FRE 2018 "32.045.013 ações de emissão da Log" ÷ 444.139.684 MRV = 0,07215075382 (o fator da B3 ÷ 100)
    "MRVE3": (_cis("MRVE", "2018-12-20", "2018-12-12", ("BRMRVEACNOR2", "BRLOGGACNOR7", 7.215075382),
                   ("BRMRVEACNOR2", "BRMRVEACNOR2", 100.0)), [("BRLOGGACNOR7", 0.07215075382)]),
    # Cosan → Cosan Logística: FRE 2015 "cada acionista recebeu 1 (uma) ação ordinária ... da Cosan Logística"
    "CSAN3": (_cis("CSAN", "2014-10-03", "2014-10-01", ("BRCSANACNOR6", "BRRLOGACNOR4", 100.0),
                   ("BRCSANACNOR6", "BRCSANACNOR6", 100.0)), [("BRRLOGACNOR4", 1.0)]),
    # GPA → Sendas (Assaí), fora da B36: FRE 2020, redução por cisão "não houve redução do número de ações"
    "PCAR3": (_cis("PCAR", "2021-02-26", "2020-12-31", ("BRPCARACNOR3", "BRASAIACNOR0", 100.0),
                   ("BRPCARACNOR3", "BRPCARACNOR3", 100.0)), [("BRASAIACNOR0", 1.0)]),
}


@pytest.mark.parametrize("tk", sorted(CISOES))
def test_cisao_mantem_as_acoes_e_registra_o_ativo_recebido(tk):
    s, recebe = CISOES[tk]
    ev = base.eventos_em_acoes(tk, s)
    assert len(ev) == 1
    e = ev[0]
    assert (e["tipo"], e["data_com"], e["aprovacao"]) == ("CIS RED CAP", s["data_com"][0], s["data_aprovacao"][0])
    assert e["multiplicador"] == 1.0                     # NÃO 1 + 100/100 = ×2
    assert [a for a, _ in e["recebe"]] == [a for a, _ in recebe]
    assert [r for _, r in e["recebe"]] == pytest.approx([r for _, r in recebe], rel=1e-9)


def test_cisao_em_duas_classes_conta_uma_vez():
    # Itaú → XPart (01/10/2021): ON e PN, cada uma com a sua ação nova (literal do suplemento); a classe do ticker decide
    s = _cis("ITUB", "2021-10-01", "2021-01-31", ("BRITUBACNOR4", "BRXPARACNOR9", 100.0), ("BRITUBACNOR4", "BRITUBACNOR4", 100.0),
             ("BRITUBACNPR1", "BRXPARACNPR6", 100.0), ("BRITUBACNPR1", "BRITUBACNPR1", 100.0))
    import proventos_hall as ph
    ev = ph.eventos_em_acoes("ITUB4", s, lambda t: "BRITUBACNPR1")
    assert [(e["multiplicador"], e["recebe"]) for e in ev] == [(1.0, [("BRXPARACNPR6", 1.0)])]
    # sem o ISIN da classe: cada classe recebe a ação nova da sua espécie → a classe de `recebe` seria chute → falha alto
    with pytest.raises(NotImplementedError, match="várias classes"):
        ph.eventos_em_acoes("ITUB4", s)


@pytest.mark.parametrize("ativo", ["BRXPTOACNPR8", "BRXPTOR01OR1"])
def test_cisao_que_entrega_outra_classe_da_propria_empresa_falha_alto(ativo):
    """Adversário (25/11): 1 PN (ou recibo) por ON da mesma empresa é ação nova; reconhecer a linha própria só pela raiz
    deixaria passar com ×1."""
    s = _cis("XPTO", "2024-05-24", "2024-04-24", ("BRXPTOACNOR1", "BRNOVAACNOR1", 50.0), ("BRXPTOACNOR1", ativo, 100.0))
    with pytest.raises(NotImplementedError, match="outro ISIN"):
        base.eventos_em_acoes("XPTO3", s)


def test_cisao_com_ativo_emitido_nan_falha_alto():
    """Adversário (25/11): NaN (concat com o formato do backtest) não pode virar o ativo "nan"."""
    s = _cis("XPTO", "2024-05-24", "2024-04-24", ("BRXPTOACNOR1", float("nan"), 50.0), ("BRXPTOACNOR1", "BRXPTOACNOR1", 100.0))
    with pytest.raises(NotImplementedError, match="ativo emitido"):
        base.eventos_em_acoes("XPTO3", s)


def test_cisao_com_fator_da_propria_acao_diferente_de_100_falha_alto():
    s = _cis("XPTO", "2024-05-24", "2024-04-24", ("BRXPTOACNOR1", "BRNOVAACNOR1", 50.0), ("BRXPTOACNOR1", "BRXPTOACNOR1", 90.0))
    with pytest.raises(NotImplementedError, match="própria"):
        base.eventos_em_acoes("XPTO3", s)


def test_cisao_sem_a_linha_da_propria_acao_ou_sem_a_nova_falha_alto():
    with pytest.raises(NotImplementedError, match="própria"):
        base.eventos_em_acoes("XPTO3", _cis("XPTO", "2024-05-24", "2024-04-24", ("BRXPTOACNOR1", "BRNOVAACNOR1", 50.0)))
    with pytest.raises(NotImplementedError, match="recebida"):
        base.eventos_em_acoes("XPTO3", _cis("XPTO", "2024-05-24", "2024-04-24", ("BRXPTOACNOR1", "BRXPTOACNOR1", 100.0)))
    with pytest.raises(NotImplementedError, match="ativo emitido"):
        base.eventos_em_acoes("XPTO3", _cis("XPTO", "2024-05-24", "2024-04-24", ("BRXPTOACNOR1", "", 100.0),
                                            ("BRXPTOACNOR1", "BRXPTOACNOR1", 100.0)))


def test_cisao_nao_muda_o_provento():
    """A ação recebida na cisão é redução de capital (§6.4), não provento; e o provento antes da data-com não é dividido."""
    import proventos_hall as ph
    s, _ = CISOES["MRVE3"]
    ev = ph.eventos_em_acoes("MRVE3", s)
    regs = [dict(tipo_acao="ON", data_aprovacao="2018-04-20", data_com="2018-04-30", valor=0.5, lote=1.0, tipo="DIVIDENDO")]
    assert [p["valor_hoje"] for p in ph.proventos("MRVE3", "2026-10-02", regs=regs, ev=ev, grupos={})] == [0.5]


@requer_suplemento_b3
@pytest.mark.parametrize("tk", ["CSAN3", "MRVE3"])
def test_cisao_do_cache_real_da_b36_carrega(tk):
    """As duas da B36 que paravam em proventos_hall.py:207 (B40): o cache do hall tem as duas linhas e carrega."""
    import proventos_hall as ph
    if not ph._arquivo_suplemento(tk).exists():
        pytest.skip(f"sem o suplemento do hall de {tk}")
    # pelo caminho do hall (classe do ticker pelo ISIN: a CSAN tem um recibo de bonificação de 2008 em outro ISIN)
    ev = [e for e in ph.eventos(tk, "2026-11-24") if e["tipo"] == "CIS RED CAP"]
    s, recebe = CISOES[tk]
    assert [(e["data_com"], e["multiplicador"]) for e in ev] == [(s["data_com"][0], 1.0)]
    assert [r for _, r in ev[0]["recebe"]] == pytest.approx([r for _, r in recebe], rel=1e-9)


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
