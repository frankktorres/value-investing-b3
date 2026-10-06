"""Motor reduzido em casos sintéticos: fórmula à mão, prêmio, contagem de ações e procedência.

Nenhum teste aqui olha o golden — o motor reduzido só pode ser corrigido por prova sintética
(trava anti-calibração da fatia 12).
"""
from __future__ import annotations

import math

import pandas as pd
import pytest

from backtest.config import PADRAO
from backtest.ledger.pit import Exercicio, LedgerPIT
from backtest.mercado_bt import MercadoBT
from backtest.motor import reduzido_fin, reduzido_nf
from backtest.motor.base import Ano, Insumos, montar, soma_dfc
from backtest.motor.perfil import Perfil
from backtest.motor.reduzido import avaliar

T = "2020-06-30"
MK = MercadoBT(data=T, rf_real=0.04, pi=0.035, premio=0.05, fonte="teste")
SEM_EVENTO = pd.DataFrame(columns=["ticker", "data_ex", "fator"])


def _ex(ano: int, contas: dict, dfc=(), receb: str | None = None) -> Exercicio:
    return Exercicio(dt_refer=f"{ano}-12-31", dt_receb=receb or f"{ano + 1}-03-20", versao=1,
                     versao_disco=1, estado="limpo", conjunto="con", contas=contas, dfc=dfc)


def _ledger(anuais, acoes=100.0, aprov="2015-04-30", receb="2019-05-31") -> LedgerPIT:
    return LedgerPIT(cd_cvm=1, data_corte=T, plano="industrial", anuais=tuple(anuais),
                     ultimo_itr=None, acoes=acoes, acoes_dt_refer="2019-01-01",
                     acoes_dt_receb=receb, acoes_fonte="fre", acoes_ambiguo=False,
                     mes_ipca="2020-05", acoes_aprovacao=aprov)


def _perfil(p="servicos") -> Perfil:
    return Perfil(cd_cvm=1, setor="x", perfil=p, dt_receb="2020-01-10", motivo_exclusao="")


def _anos_fin(n=10, pl=1000.0, lucro=150.0, div=75.0):
    return tuple(Ano(dt_refer=f"{2010 + k}-12-31", ano=2010 + k,
                     contas={"pl": pl, "nao_controladores": 0.0, "lucro_controlador": lucro},
                     da=0.0, capex=0.0, dividendos=div, arrendamento=0.0, real=1.0)
                 for k in range(n))


def _ins(anos, perfil="banco", papeis=100_000.0) -> Insumos:
    l = _ledger([_ex(a.ano, a.contas) for a in anos])
    return Insumos(ticker="XXXX3", cd_cvm=1, data_corte=T, perfil=_perfil(perfil), ledger=l,
                   anos=anos, balanco=dict(anos[-1].contas), balanco_dt_refer=anos[-1].dt_refer,
                   papeis=papeis, fator_evento=1.0, por_papel=1)


# ------------------------------------------------------------------ cópias fiéis ao original
def test_copias_financeiras_identicas_ao_motor_financeiras():
    import lote1_bancos
    import motor_financeiras as mf
    for emp in lote1_bancos.EMPRESAS:
        mk = lote1_bancos.MK
        for roe in (emp.roe_lp, emp.roe_lp - 0.03, emp.roe_inicio):
            orig = mf.ddm_dois_estagios(emp, mk, roe)[0]
            copia = reduzido_fin.ddm_dois_estagios(emp.vpa, emp.roe_inicio, roe, emp.payout,
                                                   mk.ke_nom, mk.g_teto)
            assert copia == orig
            assert reduzido_fin.g_de(roe, emp.payout, mk.g_teto) == mf.g_de(emp, mk, roe)
        assert reduzido_fin.pvp_justificado(0.15, 0.06, 0.16) == mf.pvp_justificado(0.15, 0.06, 0.16)


# ------------------------------------------------------------------ financeira à mão
def test_financeira_a_mao():
    i = _ins(_anos_fin())
    anc, p = reduzido_fin.ancoras(i, MK)
    assert p["roe_lp"] == pytest.approx(0.15)
    assert p["payout"] == pytest.approx(0.5)
    vpa = 1000.0 * 1000 / 100_000                       # R$ mil -> R$, por ação = 10
    g = min(0.15 * 0.5, MK.g_teto)
    assert anc["P/VP justificado"] == pytest.approx(vpa * (0.15 - g) / (MK.ke_nom - g))
    assert anc["Lucro normalizado capitalizado"] == pytest.approx(150 * 1000 / 100_000 / MK.ke_real)
    # g = 7,5% acima do teto (π + 2%): o estágio explícito cresce mais que o terminal -> DDM > P/VP
    assert anc["DDM 2 estágios"] > anc["P/VP justificado"]
    # sem ITR, roe_inicio = último ROE = roe_lp, e com g abaixo do teto o DDM cai no P/VP
    # justificado (a degeneração conhecida — o DDM só vira ângulo próprio quando o ITR diverge)
    anc, p = reduzido_fin.ancoras(_ins(_anos_fin(div=105.0)), MK)
    assert p["g"] < MK.g_teto
    assert anc["DDM 2 estágios"] == pytest.approx(anc["P/VP justificado"], rel=1e-9)


def test_payout_e_recortado_em_0_1():
    _, p = reduzido_fin.ancoras(_ins(_anos_fin(div=400.0)), MK)
    assert p["payout"] == 1.0


# ------------------------------------------------------------------ não-financeira à mão
def _anos_nf(n=10, receita=1000.0, ebit=200.0, imob=500.0, pl=800.0, da=50.0, capex=50.0,
             divida=0.0, caixa=0.0):
    return tuple(Ano(dt_refer=f"{2010 + k}-12-31", ano=2010 + k,
                     contas={"receita": receita, "ebit": ebit, "lair": ebit, "ir": -0.34 * ebit,
                             "lucro": 0.66 * ebit, "imobilizado": imob, "pl": pl,
                             "nao_controladores": 0.0, "emprest_lp": divida, "caixa": caixa,
                             "ac": 300.0, "pc": 200.0},
                     da=da, capex=capex, dividendos=0.0, arrendamento=0.0, real=1.0)
                 for k in range(n))


def test_nao_financeira_a_mao():
    i = _ins(_anos_nf(), perfil="servicos")
    anc, p = reduzido_nf.ancoras(i, MK, preco=10.0)
    assert p["aliquota"] == pytest.approx(0.34)
    assert p["ajuste_manut"] == 0.0
    # sem dívida, WACC = Ke; real = Ke real
    assert p["wacc_real"] == pytest.approx(MK.ke_real)
    assert anc["EPV de meio de ciclo"] == pytest.approx(1000 * 0.2 * 0.66 / MK.ke_real * 1000 / 100_000)
    # receita constante -> capex de manutenção = capex inteiro; OE = lucro + D&A − capex
    assert anc["Owner Earnings capitalizado"] == pytest.approx(
        132.0 / (MK.ke_real - PADRAO.g_real_oe) * 1000 / 100_000)


def test_capex_de_crescimento_sai_da_manutencao():
    anos = list(_anos_nf(n=3))
    anos[2] = Ano(**{**anos[2].__dict__, "contas": {**anos[2].contas, "receita": 1200.0},
                     "capex": 200.0})
    m = reduzido_nf.capex_manutencao(tuple(anos))
    # intensidade 500/1000 = 0,5; Δreceita 200 -> crescimento 100; manutenção 200 − 100
    assert m == [None, 50.0, 100.0]


def test_premio_move_as_ancoras_com_ke_e_nao_a_reproducao():
    i = _ins(_anos_nf(), perfil="ciclica")
    ant = None
    for pr in (0.03, 0.04, 0.05, 0.06):
        anc, _ = reduzido_nf.ancoras(i, MK.com_premio(pr), preco=10.0)
        if ant:
            assert anc["EPV de meio de ciclo"] < ant["EPV de meio de ciclo"]
            assert anc["Owner Earnings capitalizado"] < ant["Owner Earnings capitalizado"]
            assert anc["Valor de reprodução"] == ant["Valor de reprodução"]
        ant = anc
    ant = None
    for pr in (0.03, 0.04, 0.05, 0.06):
        anc, _ = reduzido_fin.ancoras(_ins(_anos_fin()), MK.com_premio(pr))
        if ant:
            assert all(anc[k] < ant[k] for k in anc)
        ant = anc


def test_ancoras_nao_degeneram():
    """Âncoras com ângulos diferentes: dispersão > 1 num caso genérico."""
    anc, _ = reduzido_nf.ancoras(_ins(_anos_nf(), perfil="servicos"), MK, preco=10.0)
    v = list(anc.values())
    assert max(v) / min(v) > 1.05


# ------------------------------------------------------------------ DFC
def test_soma_dfc_separa_grupo_e_nao_soma_pai_com_filho():
    dfc = (("6.01.01.02", "Depreciação e Amortização", 40.0),
           ("6.03.02", "Amortização de Empréstimos", -500.0),
           ("6.02.01", "Aquisição de Imobilizado e Intangível", -90.0),
           ("6.02.01.01", "Aquisição de Imobilizado", -60.0),
           ("6.02.01.02", "Aquisição de Intangível", -30.0),
           ("6.02.03", "Venda de Imobilizado", 15.0),
           ("6.03.05", "Dividendos e Juros sobre o Capital Próprio Pagos", -70.0),
           ("6.02.04", "Dividendos Recebidos", 12.0),
           ("6.03.06", "Pagamento de Arrendamentos", -9.0))
    assert soma_dfc(dfc, PADRAO.dfc_da) == 40.0
    assert soma_dfc(dfc, PADRAO.dfc_capex) == -90.0
    assert soma_dfc(dfc, PADRAO.dfc_dividendos) == -70.0
    assert soma_dfc(dfc, PADRAO.dfc_arrendamento) == -9.0


# ------------------------------------------------------------------ contagem de ações × eventos
def _montar(eventos, **kw):
    anos = [_ex(2010 + k, {"receita": 1000.0, "ebit": 200.0, "lair": 200.0, "ir": -68.0,
                           "lucro": 132.0, "imobilizado": 500.0, "pl": 800.0})
            for k in range(10)]
    return montar(1, "XXXX3", "cnpj", T, eventos, perfil=_perfil(),
                  ledger=_ledger(anos, **kw), por_papel=1)


def test_desdobramento_entre_entrega_do_fre_e_T_multiplica_as_acoes():
    ev = pd.DataFrame({"ticker": ["XXXX3"] * 4,
                       "data_ex": ["2015-04-30", "2017-08-01", "2019-08-01", "2020-07-15"],
                       "fator": [10.0, 3.0, 2.0, 5.0]})
    i = _montar(ev)
    # só o de 2019-08 está em (entrega do FRE = 2019-05-31, T]: o FRE entregue já mostra a
    # contagem pós-2015 e pós-2017; o de depois de T não aconteceu ainda
    assert i.fator_inicio == "2019-05-31"
    assert i.fator_evento == 2.0 and i.papeis == 200.0
    # meta-teste: sem o fator o valor por ação dobra — o P/C sairia pela metade
    sem = _montar(SEM_EVENTO)
    assert sem.por_acao(800.0) == pytest.approx(2 * i.por_acao(800.0))


def test_contagem_ja_pos_evento_nao_aplica_o_fator_de_novo():
    """IRBR3 2024 (adversario): a linha do FRE aprovada na AGE do grupamento já traz a contagem
    nova; a data ex vem depois da aprovação e antes da entrega. Aplicar de novo = 30x de erro."""
    ev = pd.DataFrame({"ticker": ["XXXX3"], "data_ex": ["2019-03-10"], "fator": [1 / 30]})
    i = _montar(ev, aprov="2019-02-20", receb="2019-05-31")
    assert i.fator_evento == 1.0 and i.papeis == 100.0


def test_evento_sem_fator_exclui():
    ev = pd.DataFrame({"ticker": ["XXXX3"], "data_ex": ["2019-10-10"], "fator": [math.nan]})
    assert _montar(ev).motivo_exclusao == "evento_sem_fator"


def test_unit_divide_pela_composicao():
    anos = [_ex(2010 + k, {"pl": 800.0}) for k in range(10)]
    i = montar(1, "XXXX11", "cnpj", T, SEM_EVENTO, perfil=_perfil(), ledger=_ledger(anos),
               por_papel=3)
    assert i.papeis == pytest.approx(100.0 / 3)


def test_contagem_de_acoes_posterior_a_T_levanta():
    with pytest.raises(AssertionError, match="vazamento"):
        _montar(SEM_EVENTO, receb="2020-08-01")
    with pytest.raises(AssertionError, match="vazamento"):
        _montar(SEM_EVENTO, aprov="2020-09-01")


def test_janela_curta_e_acoes_ambiguas_excluem():
    anos = [_ex(2016 + k, {"pl": 1.0}) for k in range(4)]
    i = montar(1, "XXXX3", "cnpj", T, SEM_EVENTO, perfil=_perfil(), ledger=_ledger(anos),
               por_papel=1)
    assert i.motivo_exclusao == "janela_curta"
    assert _montar(SEM_EVENTO, aprov="").motivo_exclusao == "acoes_indisponiveis"


def test_perfil_excluido_nao_chega_ao_motor():
    p = Perfil(cd_cvm=1, setor="Emp. Adm. Part. - Sem Setor Principal", perfil="holding",
               dt_receb="2020-01-10", motivo_exclusao="perfil_holding_excluido")
    i = montar(1, "XXXX3", "cnpj", T, SEM_EVENTO, perfil=p)
    r = avaliar(i, MK, 10.0)
    assert r.veredito is None and r.motivo_exclusao == "perfil_holding_excluido"


def test_ancora_nan_exclui_em_vez_de_virar_palavra():
    anos = _anos_fin()
    anos = tuple(Ano(**{**a.__dict__, "contas": {"lucro_controlador": 150.0}}) for a in anos)
    r = avaliar(_ins(anos), MK, 10.0)
    assert r.veredito is None and r.motivo_exclusao == "ancora_indisponivel"


def test_roe_inicio_vem_do_itr_anualizado_e_separa_o_ddm():
    from dataclasses import replace
    anos = _anos_fin(div=105.0)
    i = _ins(anos)
    itr = Exercicio(dt_refer="2020-03-31", dt_receb="2020-05-10", versao=1, versao_disco=1,
                    estado="limpo", conjunto="con",
                    contas={"pl": 1000.0, "nao_controladores": 0.0, "lucro_controlador": 20.0},
                    periodo_meses=3)
    i = replace(i, ledger=replace(i.ledger, ultimo_itr=itr), balanco=dict(itr.contas))
    anc, p = reduzido_fin.ancoras(i, MK)
    assert p["roe_inicio"] == pytest.approx(0.08)          # 20 × 12/3 ÷ 1000
    assert anc["DDM 2 estágios"] < anc["P/VP justificado"]


def test_evento_antes_de_2014_sem_preco_exclui():
    fre = pd.DataFrame({"cnpj": ["cnpj"], "aprovacao": ["2012-03-01"]})
    anos = [_ex(2004 + k, {"pl": 800.0}) for k in range(10)]
    kw = dict(perfil=_perfil(), por_papel=1, fre=fre)
    i = montar(1, "XXXX3", "cnpj", T, SEM_EVENTO,
               ledger=_ledger(anos, aprov="2004-04-30", receb="2011-05-31"), **kw)
    assert i.motivo_exclusao == "evento_antes_do_cotahist"
    # meta-teste: o mesmo ledger com FRE entregue depois do evento passa
    i = montar(1, "XXXX3", "cnpj", T, SEM_EVENTO,
               ledger=_ledger(anos, aprov="2004-04-30", receb="2013-05-31"), **kw)
    assert i.motivo_exclusao == ""


def test_lucro_controlador_zero_cai_para_o_lucro():
    from backtest.motor.base import lucro_controlador
    assert lucro_controlador({"lucro_controlador": 0.0, "lucro": 591.0}) == 591.0
    assert lucro_controlador({"lucro_controlador": 0.0, "lucro": 0.0}) == 0.0
    assert lucro_controlador({"lucro_controlador": 90.0, "lucro": 100.0}) == 90.0
    assert lucro_controlador({"lucro": -123.0}) == -123.0
    assert lucro_controlador({}) is None


def test_banco_com_anos_sem_lucro_exclui():
    anos = list(_anos_fin())
    for k in (8, 9):
        anos[k] = Ano(**{**anos[k].__dict__, "contas": {"pl": 1000.0}})
    r = avaliar(_ins(tuple(anos)), MK, 10.0)
    assert r.motivo_exclusao == "ancora_indisponivel"


def test_custo_amortizado_nao_e_da():
    dfc = (("6.01.01.02", "Depreciação e amortização", 40.0),
           ("6.01.02.07", "Passivos financeiros ao custo amortizado", 900.0),
           ("6.01.02.08", "Receitas diferidas amortizadas", 30.0))
    assert soma_dfc(dfc, PADRAO.dfc_da) == 40.0


def test_dfc_do_ledger_sem_linha_duplicada():
    from backtest.ledger.pit import _dfc_de
    g = pd.DataFrame({"dt_refer": ["2022-12-31"] * 3, "bloco": ["DFC_MI"] * 3,
                      "ordem_exerc": ["ULTIMO"] * 3, "conjunto": ["con"] * 3,
                      "codigo": ["6.02.01"] * 3, "descricao": ["Aquisição de imobilizado"] * 3,
                      "valor": [-116945.0] * 3})
    assert soma_dfc(_dfc_de(g, "2022-12-31"), PADRAO.dfc_capex) == -116945.0
