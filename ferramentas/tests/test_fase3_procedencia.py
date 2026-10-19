"""Fase 3, fatia 1 (19/10/2026): procedência POR CAMPO das não financeiras do lote (relatorio/procedencia.py + insumos_a).

A nota só sobe com prova: `acoes` e os dados das âncoras só são A se o valor que a empresa carrega é o que o lote registrou de
uma fonte oficial; o central das não financeiras não usa o DPA da StatusInvest (só o provento já ex da B3). Números e
golden não mudam nesta fatia — só a nota.
"""
import dataclasses
import math
from dataclasses import replace

import pytest

import insumos_a
import lote3_agro
import lote5_petroleo
import motor_nao_financeiras as MN
from lote1_bancos import MK
from relatorio import procedencia as pr
from relatorio.modelo import pior


def _emp(tk):
    import universo
    return next(e for _, emps, _ in universo.GRUPOS for e in emps if e.ticker == tk)


def _caso(emp, dossie=None):
    return dict(tk=emp.ticker, empresa=emp, r=None, mk=MK, data="2026-10-02", dossie=dossie, financeira=False)


def _nota_central(emp, ancoras=("DCF (3 cenários)", "EPV", "Owner Earnings ÷ (Ke − g)")):
    t = pr.tabela(_caso(emp))
    return pior(o for nome in ancoras for o in pr.de(t, *pr.ANCORA[nome]))


def test_todo_campo_do_industrial_esta_classificado():
    campos = {f.name for f in dataclasses.fields(MN.Industrial)}
    grupos = [set(pr.IDENTIDADE_NF), set(pr.DADO_PROPRIO_NF), set(pr.DADO_ANCORA_NF), set(pr.JULGAMENTO_NF)]
    assert set().union(*grupos) == campos, "campo novo do Industrial sem classificação (dado ou julgamento)"
    assert sum(map(len, grupos)) == len(campos), "campo em dois grupos"


def test_acoes_so_e_A_com_o_valor_registrado():
    suz = _emp("SUZB3")
    assert pr.tabela(_caso(suz))["acoes"].nota == "A"
    outra = replace(suz, n_acoes=suz.n_acoes * 1.01)           # literal digitado por cima do coletado
    assert pr.tabela(_caso(outra))["acoes"].nota == "C"
    assert _nota_central(outra) == "C"


def test_ticker_sem_registro_fica_C():
    e = MN.Industrial("TESTEF3", "teste", "servicos", preco=10.0, n_acoes=1e6)
    assert pr.tabela(_caso(e))["acoes"].nota == "C"


@pytest.mark.parametrize("tk, campo, valor", [
    ("SUZB3", "outros_passivos_financeiros", 1_000.0),
    ("SUZB3", "kd_ri", {"valor": 0.12, "fonte": "RI", "data": "2026-06-30"}),
    ("UGPA3", "deflator", {"2025": 1.0}),
])
def test_dado_de_ancora_sem_registro_rebaixa_o_central(tk, campo, valor):
    e = _emp(tk)
    assert _nota_central(e) == "A"
    assert _nota_central(replace(e, **{campo: valor})) == "C"


def test_nav_digitado_do_slce3_segura_o_central_em_C():
    slc = _emp("SLCE3")
    assert pr.tabela(_caso(slc))["dados_lote"].nota == "C"
    assert _nota_central(slc, ("Valor de reprodução",)) == "C"


def test_capex_expansao_vale_a_nota_declarada():
    e = replace(_emp("SUZB3"), capex_expansao={"anos": {"2025": 1.0}, "projeto": "x", "fonte": "RI 2T26", "nota_fonte": "B"})
    assert pr.tabela(_caso(e))["dados_lote"].nota == "B"


def test_deflator_do_l5_registrado_do_ipca_do_bcb():
    assert pr.tabela(_caso(_emp("UGPA3")))["dados_lote"].fonte == "BCB (IPCA)"
    assert insumos_a.origem("UGPA3", "deflator", lote5_petroleo.M["deflator"]) is not None


def test_registro_e_copia():
    d = {"2024": 1.5, "2025": 1.2}
    insumos_a.registrar("TESTEF3", "deflator", d, insumos_a.IPCA_BCB)
    d["2025"] = 9.9
    assert insumos_a.origem("TESTEF3", "deflator", d) is None
    assert insumos_a.origem("TESTEF3", "deflator", {"2024": 1.5, "2025": 1.2}) is insumos_a.IPCA_BCB


@pytest.mark.parametrize("tk", ["SUZB3", "WEGE3", "PETR4"])
def test_central_nao_financeiro_nao_usa_dpa_da_statusinvest(tk):
    """O que justifica tirar o DPA da StatusInvest das âncoras: mexer nele (e no jcp_share) não mexe no central."""
    e = _emp(tk)
    antes = MN.avaliar(e, MK)
    s = MN.SI[tk]
    guardado = dict(s["dpa_por_ano_datacom"])
    try:
        s["dpa_por_ano_datacom"] = {a: 3 * v + 1 for a, v in guardado.items()}
        depois = MN.avaliar(replace(e, jcp_share=0.9 if e.jcp_share < 0.5 else 0.1), MK)
    finally:
        s["dpa_por_ano_datacom"] = guardado
    assert depois["central"] == antes["central"] and depois["palavra"] == antes["palavra"]
    assert depois["ancoras"] == antes["ancoras"]
    assert depois["dpa5"] != antes["dpa5"]                  # o DPA chega aos informativos (o teste mexeu em algo vivo)


def test_dossie_tem_as_chaves_novas_com_nota_A():
    """As âncoras NF ganharam `proventos_ja_ex` e `dados_lote`: o caminho do dossiê responde as duas (insumos todos A hoje),
    senão `de()` devolveria C "não classificado" e o central dos 8 dossiês cairia."""
    from dossie import gerar
    hyp = _emp("HYPE3")
    for tk in gerar.FICHAS:
        t = pr.tabela(_caso(replace(hyp, ticker=tk), dossie={"anos": ["2016", "2025"]}))
        for nome in ("DCF (3 cenários)", "EPV", "Owner Earnings ÷ (Ke − g)", "Valor de reprodução"):
            assert all(o.nota == "A" for o in pr.de(t, *pr.ANCORA[nome])), (tk, nome)


def test_acoes_registradas_conferem_com_o_dfp():
    """Conferência de escala (milhares × unidades, units): as ações registradas batem a ±10% com o DFP do último exercício.
    Só o caminho do lote: ticker com ficha de dossiê usa as ações do dossiê (HYPE3: ITR jun/26 11% acima do DFP 2025)."""
    from dossie import gerar
    regs = {tk: v for (tk, campo), (v, _) in insumos_a._REG.items()
            if campo == "acoes" and not tk.startswith("TEST") and tk not in gerar.FICHAS}
    assert len(regs) >= 19
    for tk, n in regs.items():
        cvm = MN.CVM[tk]
        d = cvm["anual"]["2026" if tk == "SMTO3" else "2025"]["acoes"]
        unit = cvm.get("acoes_por_unit") or 1
        perto = min((d / unit, d * 1000 / unit), key=lambda x: abs(math.log(x / n)))
        assert 0.9 < perto / n < 1.1, (tk, n, perto)


# trava da fase 3: só desce (padrão do test_b24). Medido em 19/10/2026 depois da fatia 1.
CENTRAIS_A_MINIMO = 18
C_LOTE_NAS_ANCORAS_MAXIMO = 137
NF_A = {"ABEV3", "B3SA3", "FLRY3", "GGBR4", "KEPL3", "KLBN11", "PETR4", "PRIO3", "RANI3", "RECV3", "SMTO3", "SUZB3",
        "TIMS3", "UGPA3", "UNIP6", "VBBR3", "VIVT3", "WEGE3"}


def test_trava_da_metrica_do_hall():
    r = pr.resumo_hall()
    a = {tk for tk, n in r["centrais"].items() if n == "A"}
    assert len(r["centrais"]) == 39
    assert NF_A <= a, f"perderam a nota A: {sorted(NF_A - a)}"
    assert len(a) >= CENTRAIS_A_MINIMO
    assert r["c_lote_nas_ancoras"] <= C_LOTE_NAS_ANCORAS_MAXIMO
    assert lote3_agro.acoes("SUZB3") == _emp("SUZB3").n_acoes     # registrar devolve o valor intacto
