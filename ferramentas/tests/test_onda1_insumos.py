"""Onda 1.1 da auditoria de 08/10/2026 — insumos que movem o valor central (AUD-01, AUD-16, AUD-02, AUD-04, AUD-03).

Cada teste foi escrito ANTES da correção e falhou no código antigo (saída guardada no 09-diário). O golden prova o resultado
dos 41 tickers; estes provam as REGRAS em série sintética e os insumos do hall que a auditoria achou errados.
"""
import pandas as pd
import pytest

import coletar_cvm as C
import inflacao as I
import motor_nao_financeiras as M
from lote1_bancos import MK
from tests.test_doutrina_v23 import _emp, _serie


def _deflator_ltm_2t26():
    """Calculado aqui, sem o código do motor: média do índice de jul/2025 a jun/2026 → R$ da data-base."""
    meses = [m for m in I._INDICE if 2025 * 12 + 6 <= m <= 2026 * 12 + 5]
    assert len(meses) == 12
    return I.BASE / (sum(I._INDICE[m] for m in meses) / 12)


# ---------------------------------------------------------------- AUD-01: receita de meio em R$ de hoje
def test_aud01_deflator_ltm_e_a_media_dos_12_meses_do_ltm():
    assert I.deflator_ltm("2T26") == pytest.approx(_deflator_ltm_2t26(), rel=1e-12)
    for ref in ("3T26", "4T30"):            # meses além da série: usa os que existem (ou 1,0), nunca quebra
        assert 1.0 <= I.deflator_ltm(ref) < 1.2


def test_aud01_receita_constante_em_termos_reais_da_receita_de_meio_igual():
    """Receita de R$ 10.000 mil de hoje em todos os anos, publicada em R$ de cada ano: a receita de meio tem de ser 10.000."""
    R = 10_000.0
    anual = _serie("TESTO1R")
    for y, d in anual.items():
        d["receita"] = R / I.DEFLATOR[y]
    M.CVM["TESTO1R"]["ltm_2T26"]["receita"] = R / _deflator_ltm_2t26()
    assert M.premissas_operacionais(_emp("TESTO1R"))["receita_meio"] == pytest.approx(R, rel=1e-9)


def test_aud01_receita_media_do_lote4_em_reais_de_hoje():
    """FLRY3 usa receita_media(2024, 2025 + LTM): achado na reprodução — a mesma média nominal, fora da lista da auditoria."""
    import lote4_saude_telecom as L4
    R = 10_000.0
    anual = _serie("TESTO1F")
    for y, d in anual.items():
        d["receita"] = R / I.DEFLATOR[y]
    M.CVM["TESTO1F"]["ltm_2T26"]["receita"] = R / _deflator_ltm_2t26()
    assert L4.receita_media("TESTO1F", ["2024", "2025"]) == pytest.approx(R, rel=1e-9)
    assert L4.receita_media("TESTO1F", ["2024", "2025"], ltm=False) == pytest.approx(R, rel=1e-9)


# ---------------------------------------------------------------- AUD-16: OE e DPA em R$ de hoje
def test_aud16_oe_e_dpa_constantes_em_termos_reais():
    """Lucro de R$ 900 mil de hoje e DPA de R$ 0,50 de hoje, publicados em R$ de cada ano. Capex = D&A e balanço constante:
    OE do ano = lucro do ano. A mediana tem de dar 900 e o DPA médio 0,50 — no nominal ficavam ~5–15% abaixo."""
    L, D = 900.0, 0.50
    anual = _serie("TESTO1O")
    for y, d in anual.items():
        d["receita"] = 10_000.0 / I.DEFLATOR[y]
        d["lucro"] = L / I.DEFLATOR[y]
        d["capex"] = d["da"] = 500.0 / I.DEFLATOR[y]
    M.CVM["TESTO1O"]["ltm_2T26"] = dict(anual["2025"])
    M.SI["TESTO1O"]["dpa_por_ano_datacom"] = {y: D / I.DEFLATOR[y] for y in anual}
    r = M.avaliar(_emp("TESTO1O"), MK)
    assert r["oe_norm"] == pytest.approx(L, rel=1e-6)
    assert r["dpa5"] == pytest.approx(D, rel=1e-9)


# ---------------------------------------------------------------- AUD-02: provento já ex na dívida líquida
def test_aud02_coletor_separa_proventos_a_pagar():
    df = pd.DataFrame([
        ("2.01.04", "Empréstimos e Financiamentos", 999.0),
        ("2.01.05.02.01", "Dividendos e JCP a Pagar", 100.0),
        ("2.01.05.02.02", "Dividendo Mínimo Obrigatório a Pagar", 40.0),           # ainda não aprovado → não é ex
        ("2.01.05.02.05", "Proventos e Direitos sobre Títulos em Custódia", 50.0),  # B3: dinheiro de terceiros
        ("2.02.02.02.07", "Dividendos a pagar", 30.0),                              # parcelas futuras (WEGE3)
        ("2.02.04.02.05", "Juros sobre o capital próprio", 20.0),                   # provisão, não provento declarado
    ], columns=["CD_CONTA", "DS_CONTA", "VL_CONTA"])
    assert C.extras_bp(df)["proventos_a_pagar"] == 130.0


def test_aud02_provento_a_pagar_entra_na_dl_e_sai_do_oe():
    _serie("TESTO1P")
    emp = _emp("TESTO1P")
    r0 = M.valores(emp, MK)
    M.CVM["TESTO1P"]["ltm_2T26"]["proventos_a_pagar"] = 250.0
    r1 = M.valores(emp, MK)
    n = emp.n_acoes / 1000
    assert r1["dl"] - r0["dl"] == pytest.approx(250.0)
    assert r1["oe_val"] - r0["oe_val"] == pytest.approx(-250.0 / n)
    assert r1["epv"] - r0["epv"] == pytest.approx(-250.0 / n)
    assert r1["proventos_ja_ex"]["total"] == pytest.approx(250.0)


def test_aud02_ltm_de_quarto_trimestre_falha_alto():
    """No 4T o passivo pode trazer o mínimo obrigatório ainda não aprovado dentro da linha genérica: decidir à mão."""
    _serie("TESTO1Q")
    M.CVM["TESTO1Q"]["ltm_2T26"]["proventos_a_pagar"] = 10.0
    M.CVM["TESTO1Q"]["ltm_ref"] = "4T26"
    with pytest.raises(NotImplementedError, match="4T"):
        M.valores(_emp("TESTO1Q"), MK)


def _reg(classe, aprov, com, valor, lote=1.0):
    return {"tipo_acao": classe, "data_aprovacao": aprov, "data_com": com, "valor": valor, "lote": lote}


def test_aud02_b3_aprovado_depois_do_balanco_e_ex_no_preco_conta():
    import proventos_ex as P
    regs = [_reg("ON", "2026-08-06", "2026-08-21", 1.0),           # aprovado depois, ex antes do preço → conta
            _reg("ON", "2026-07-10", "2026-07-20", 300.0, 1000.0),  # idem, cotado por lote de mil → 0,30
            _reg("ON", "2026-05-11", "2026-06-01", 5.0),            # já no balanço e ex → nada a somar
            _reg("ON", "2026-06-20", "2026-10-20", 2.0),            # no balanço mas NÃO ex no preço → sai do passivo
            _reg("ON", "2026-09-30", "2026-10-05", 7.0),            # data-com depois do preço → nada
            _reg("PN", "2026-08-06", "2026-08-21", 9.0)]            # outra classe → ignorado
    x = P.ajuste_b3("WEGE3", 1_000_000.0, "2T26", data_preco="2026-10-02", regs=regs)
    assert x["depois"] == pytest.approx(1_300.0)        # (1,00 + 0,30) × 1 mi de ações, em R$ mil
    assert x["nao_ex"] == pytest.approx(2_000.0)


def test_aud02_b3_sem_data_de_aprovacao_falha_alto():
    import proventos_ex as P
    with pytest.raises(ValueError, match="aprova"):
        P.ajuste_b3("WEGE3", 1.0, "2T26", data_preco="2026-10-02", regs=[_reg("ON", "", "2026-08-21", 1.0)])


def test_aud02_todo_ticker_nao_financeiro_tem_nome_de_pregao():
    """Ticker sem mapa somaria zero em silêncio — a mesma omissão do AUD-02."""
    import proventos_ex as P
    import universo
    tks = {e.ticker for _, emps, motor in universo.GRUPOS if motor is M.avaliar for e in emps}
    assert tks - set(P.PREGAO) == set()


def test_aud02_wege3_com_os_dividendos_a_pagar_do_itr():
    """ITR 2T26: 2.01.05.02.01 R$ 2.468.860 mil + 2.02.02.02.07 R$ 3.464.232 mil (auditoria, seção 2.1)."""
    from ltm import ltm_de
    assert ltm_de(M.CVM["WEGE3"])["proventos_a_pagar"] == pytest.approx(5_933_092, abs=1)


# ---------------------------------------------------------------- AUD-04: follow-on do ISAE4 (§11.2)
def test_aud04_isae4_patrimonio_mais_caixa_captado_sobre_acoes_pos_oferta():
    import lote2_energia as L2
    e = next(x for x in L2.EMPRESAS if x.ticker == "ISAE4")
    l = L2.ltm_de(L2.CVM["ISAE4"])
    pl_ctrl, acoes = l["pl"] - l["nao_controladores"], l["acoes"]
    novas = 1_200_000 * 1000 / 27.0
    assert e.vpa == pytest.approx((pl_ctrl + 1_200_000) * 1000 / (acoes + novas), rel=1e-9)
    assert e.vpa == pytest.approx(33.21, abs=0.01)


# ---------------------------------------------------------------- AUD-03: IFRS 16 na margem de E&P
def test_aud03_ep_com_ano_pre_ifrs16_na_janela_nao_roda():
    with pytest.raises(ValueError, match="IFRS 16"):
        M.exigir_declaracoes(_emp("TESTO1E", perfil="ciclica", da_receita=0.15))


def test_aud03_petr4_janela_ifrs16_e_outras_em_10_anos():
    import lote5_petroleo as L5
    p = next(x for x in L5.EMPRESAS if x.ticker == "PETR4")
    assert p.anos_ciclo == [str(a) for a in range(2019, 2026)]
    assert "IFRS 16" in p.janela_razao
    assert p.anos_outras == [str(a) for a in range(2016, 2026)]


# ---------------------------------------------------------------- adversário de 08/10/2026 (cada um reproduzido antes)
def test_adv_data_com_no_dia_do_preco_ainda_nao_e_ex():
    """O fechamento da data-com ainda carrega o provento (a B3 calcula o yield com ele)."""
    import proventos_ex as P
    x = P.ajuste_b3("WEGE3", 1_000_000.0, "2T26", data_preco="02/10/2026",
                    regs=[_reg("ON", "2026-09-20", "2026-10-02", 1.0), _reg("ON", "2026-06-20", "2026-10-02", 2.0)])
    assert x["depois"] == 0.0 and x["nao_ex"] == pytest.approx(2_000.0)


def test_adv_ticker_real_sem_nome_de_pregao_falha_alto():
    import proventos_ex as P
    with pytest.raises(KeyError, match="PREGAO"):
        P.ajuste_b3("EGIE3", 1.0, "2T26", data_preco="2026-10-02")


def test_adv_primeiro_trimestre_depois_do_exercicio_conta_o_provisionado_uma_vez(monkeypatch):
    """SMTO3 2T26: o mínimo provisionado em 31/03 (R$ 69,9 mi, rótulo genérico) foi aprovado na AGO de 03/07 — estava no passivo e
    na parte da B3. No 1º trimestre depois do fim do exercício conta o maior dos dois; no próprio fim do exercício falha alto."""
    _serie("TESTO1S")
    M.CVM["TESTO1S"]["ltm_2T26"]["proventos_a_pagar"] = 100.0
    monkeypatch.setitem(M.FIM_EXERCICIO, "TESTO1S", 3)
    monkeypatch.setattr(M, "ajuste_b3", lambda *a, **k: {"depois": 90.0, "nao_ex": 0.0, "eventos": []})
    p = M.proventos_ja_ex(_emp("TESTO1S"))
    assert p["pos_exercicio"] and p["total"] == pytest.approx(100.0) and p["no_pl"] == pytest.approx(0.0)
    M.CVM["TESTO1S"]["ltm_ref"] = "1T26"
    with pytest.raises(NotImplementedError, match="fim do exercício"):
        M.proventos_ja_ex(_emp("TESTO1S"))


def test_adv_aprovado_depois_do_balanco_sai_do_pl_ao_entrar_na_dl(monkeypatch):
    """Provento aprovado depois de 30/06 ainda está no PL de 30/06: somar à DL sem tirar do PL inflava o capital do ROIC."""
    _serie("TESTO1C")
    emp = _emp("TESTO1C", perfil="ciclica")
    r0 = M.valores(emp, MK)
    monkeypatch.setattr(M, "ajuste_b3", lambda *a, **k: {"depois": 300.0, "nao_ex": 0.0, "eventos": []})
    r1 = M.valores(emp, MK)
    assert r1["dl"] - r0["dl"] == pytest.approx(300.0)
    assert r1["cap_inv"] == pytest.approx(r0["cap_inv"])
    assert r1["reprod"] - r0["reprod"] == pytest.approx(-300.0 / (emp.n_acoes / 1000))


def test_adv_exercicio_abr_mar_deflacionado_pelos_proprios_12_meses():
    meses = [m for m in I._INDICE if 2025 * 12 + 3 <= m <= 2026 * 12 + 2]     # abr/2025–mar/2026
    assert M.deflator_exercicio("SMTO3", "2026") == pytest.approx(I.BASE / (sum(I._INDICE[m] for m in meses) / 12), rel=1e-12)
    assert M.deflator_exercicio("WEGE3", "2024") == I.DEFLATOR["2024"]
