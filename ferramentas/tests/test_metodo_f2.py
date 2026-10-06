"""Testes unitários das regras da Etapa 2 (F2) — doutrina v2.2.

D8 janela do ciclo e quebra estrutural · D9 capex de manutenção com Δreceita real · D10 ROIC a custo de reposição ·
D7 saída por qualidade · aluguel pago só pelo principal · defasagem manual só com fonte.

O golden prova o resultado dos 41 tickers; estes testes provam as REGRAS, inclusive casos que hoje nenhum ticker
exercita (série sintética), para que uma mudança futura não passe calada.
"""
import pytest

import inflacao
import motor_nao_financeiras as M
from motor_financeiras import (ANOS_ROIC_MINIMO, NOTA_QUALIDADE_MINIMA, SAIDA_PADRAO, SAIDA_QUALIDADE, Financeira,
                               precos_de_referencia)
from motor_nao_financeiras import JANELA_MINIMA_SAIDA
from motor_financeiras import avaliar as avaliar_fin


def _serie_sintetica(tk, receitas, capex, imobilizado=1000.0, da=100.0, extra_por_ano=None):
    """Injeta um ticker artificial em M.CVM. Anos como str, valores em R$ mil."""
    anual = {}
    for ano, rec in receitas.items():
        anual[ano] = {"receita": rec, "capex": capex, "imobilizado": imobilizado, "intangivel": 0.0,
                      "biologico": 0.0, "da": da, "lucro": 200.0, "ac": 0.0, "pc": 0.0, "caixa": 0.0,
                      "aplic_cp": 0.0, "emprest_cp": 0.0, "emprest_lp": 0.0, "arrendamento": 0.0, "pl": 1000.0,
                      "ebit": 0.15 * rec, "lair": 250.0, "ir": -75.0, "ativo": 2000.0, "reservas_lucro": 0.0,
                      "nao_controladores": 0.0, "receber": 0.0, "estoques": 0.0}
        anual[ano].update((extra_por_ano or {}).get(ano, {}))
    M.CVM[tk] = {"anual": anual, "ltm_2T26": dict(anual[max(anual)])}
    M.idade_e_fator.cache_clear()
    return anual


# ---------------------------------------------------------------- D9: Δreceita real
def test_d9_receita_que_cresce_so_com_a_inflacao_nao_tem_capex_de_crescimento():
    """Receita subindo exatamente o IPCA = volume parado: todo o capex é manutenção (o viés que o D9 corrige)."""
    anos = [str(a) for a in range(2016, 2026)]
    base = 10_000.0
    receitas = {a: base / inflacao.DEFLATOR[a] * inflacao.DEFLATOR["2025"] for a in anos}
    _serie_sintetica("TESTE9", receitas, capex=500.0)
    cm, cresc = M.capex_manutencao("TESTE9", "2025", "2024")
    assert cresc == pytest.approx(0.0, abs=1e-6)
    assert cm == pytest.approx(500.0)


def test_d9_crescimento_real_de_verdade_ainda_reduz_o_capex_de_manutencao():
    anos = [str(a) for a in range(2016, 2026)]
    receitas = {a: 10_000.0 / inflacao.DEFLATOR[a] * inflacao.DEFLATOR["2025"] * (1.05 ** (int(a) - 2016))
                for a in anos}
    _serie_sintetica("TESTE9B", receitas, capex=500.0)
    cm, cresc = M.capex_manutencao("TESTE9B", "2025", "2024")
    assert cresc > 0
    assert cm < 500.0


def test_d9_piso_zero_e_capex_ausente():
    anos = [str(a) for a in range(2016, 2026)]
    receitas = {a: 1_000.0 * (1.5 ** (int(a) - 2016)) for a in anos}   # explosão real de receita
    _serie_sintetica("TESTE9C", receitas, capex=10.0)
    cm, _ = M.capex_manutencao("TESTE9C", "2025", "2024")
    assert cm == 0.0
    M.CVM["TESTE9C"]["anual"]["2025"]["capex"] = None
    assert M.capex_manutencao("TESTE9C", "2025", "2024") == (None, None)


def test_d9_nao_vale_para_ciclica():
    """Commodity: a receita cresce por preço, não por capacidade — todo o capex é manutenção, sem deflator."""
    receitas = {str(a): 1_000.0 * (1.2 ** (a - 2016)) for a in range(2016, 2026)}
    _serie_sintetica("TESTE9D", receitas, capex=333.0)
    assert M.capex_manutencao("TESTE9D", "2025", "2024", ciclica=True) == (333.0, 0.0)


# ---------------------------------------------------------------- D8: janela e quebra estrutural
def _emp(tk, **kw):
    return M.Industrial(tk, tk, kw.pop("perfil", "servicos"), preco=10.0, n_acoes=1_000_000.0, **kw)


def test_d8_janela_curta_exige_razao_declarada():
    curta = [str(a) for a in range(2021, 2026)]
    with pytest.raises(ValueError, match="janela"):
        M.exigir_declaracoes(_emp("TESTE8", anos_ciclo=curta))
    M.exigir_declaracoes(_emp("TESTE8", anos_ciclo=curta, janela_razao="cisão em 2021 (fato declarado)"))


def test_d8_janela_cheia_nao_exige_razao():
    M.exigir_declaracoes(_emp("TESTE8B"))


def test_d8_divergencia_levanta_suspeita_sem_trocar_a_janela():
    """Mediana dos 5 últimos muito acima da da janela: sinaliza, mas a janela e os números seguem os de 10 anos."""
    anos = [str(a) for a in range(2016, 2026)]
    receitas = {a: 1_000.0 for a in anos}
    # margem de 5% nos 5 primeiros anos e 20% nos 5 últimos (quebra de 300%)
    extra = {a: {"ebit": 50.0 if int(a) < 2021 else 200.0} for a in anos}
    _serie_sintetica("TESTE8C", receitas, capex=100.0, extra_por_ano=extra)
    op = M.premissas_operacionais(_emp("TESTE8C"))
    assert op["quebra_suspeita"] is True
    assert op["divergencia_janela"] > M.LIMITE_QUEBRA
    assert op["m50"] == pytest.approx(0.125)        # mediana das 10 margens, não a dos 5 últimos
    assert op["m50_5a"] == pytest.approx(0.20)


def test_d8_ciclica_nunca_levanta_quebra():
    """Em cíclica a janela de 10 anos é obrigatória (§2: no ciclo inteiro, não no pico)."""
    anos = [str(a) for a in range(2016, 2026)]
    extra = {a: {"ebit": 50.0 if int(a) < 2021 else 200.0} for a in anos}
    _serie_sintetica("TESTE8D", {a: 1_000.0 for a in anos}, capex=100.0, extra_por_ano=extra)
    op = M.premissas_operacionais(_emp("TESTE8D", perfil="ciclica"))
    assert op["quebra_suspeita"] is False
    assert op["divergencia_janela"] > M.LIMITE_QUEBRA


# ---------------------------------------------------------------- D10: ROIC a custo de reposição
def test_d10_idade_media_e_limitada_e_o_fator_nunca_encolhe_o_capital():
    assert inflacao.idade_media(1000, 100) == pytest.approx(10.0)
    assert inflacao.idade_media(1000, 10) == inflacao.IDADE_MAX        # teto
    assert inflacao.idade_media(1000, 10_000) == inflacao.IDADE_MIN    # piso
    assert inflacao.idade_media(1000, 0) == inflacao.IDADE_MIN         # D&A ausente
    for da in (20, 100, 500):
        _, fator = inflacao.reposicao(1000, da)
        assert fator >= 1.0


def test_d10_capital_a_reposicao_nunca_e_menor_que_o_contabil():
    _serie_sintetica("TESTE10", {str(a): 1_000.0 for a in range(2016, 2026)}, capex=100.0,
                     imobilizado=5_000.0, da=500.0)
    idade, cap = M.capital_reposicao("TESTE10", 10_000.0)
    assert idade == pytest.approx(10.0)
    assert cap > 10_000.0


def test_d10_sem_imobilizado_o_capital_nao_muda():
    _serie_sintetica("TESTE10B", {str(a): 1_000.0 for a in range(2016, 2026)}, capex=100.0,
                     imobilizado=0.0, da=50.0)
    _, cap = M.capital_reposicao("TESTE10B", 10_000.0)
    assert cap == pytest.approx(10_000.0)


def test_d10_filtro_usa_o_menor_dos_dois_roic():
    """Em todo ticker real o ROIC a reposição é ≤ o contábil, e é ele que decide filtro 1, nota e trava."""
    import lote4_saude_telecom as L4
    for emp in L4.EMPRESAS:
        if not isinstance(emp, M.Industrial):
            continue
        r = M.valores(emp, L4.MK)
        assert r["roic_reposicao"] <= r["roic"] + 1e-12
        assert r["roic_filtro"] == pytest.approx(min(r["roic"], r["roic_reposicao"]))
        assert r["cap_inv_reposicao"] >= r["cap_inv"]
        assert inflacao.IDADE_MIN <= r["idade_imobilizado"] <= inflacao.IDADE_MAX


# ---------------------------------------------------------------- aluguel pago: só o principal
def test_aluguel_linha_limpa_sai_inteira():
    anos = [str(a) for a in range(2016, 2026)]
    extra = {a: {"arrendamento_pago": 90.0} for a in anos}
    _serie_sintetica("TESTEAL", {a: 1_000.0 for a in anos}, capex=100.0, extra_por_ano=extra)
    assert M.aluguel_principal(_emp("TESTEAL"), "2025", "2024", kd_real=0.17) == pytest.approx(90.0)


def test_aluguel_linha_mista_desconta_so_o_principal():
    anos = [str(a) for a in range(2016, 2026)]
    extra = {a: {"arrendamento_pago": 0.0, "arrendamento_pago_com_juros": 100.0,
                 "arrendamento_saldo": 400.0} for a in anos}
    _serie_sintetica("TESTEAL2", {a: 1_000.0 for a in anos}, capex=100.0, extra_por_ano=extra)
    # juro estimado = saldo médio 400 × Kd 0,15 = 60 → principal 40
    assert M.aluguel_principal(_emp("TESTEAL2"), "2025", "2024", kd_real=0.15) == pytest.approx(40.0)


def test_aluguel_mista_sem_saldo_sai_inteira_conservador():
    """ABEV3: a empresa não reporta o passivo no balanço estruturado → o juro não é estimável, desconta tudo."""
    anos = [str(a) for a in range(2016, 2026)]
    extra = {a: {"arrendamento_pago_com_juros": 100.0, "arrendamento_saldo": 0.0} for a in anos}
    _serie_sintetica("TESTEAL3", {a: 1_000.0 for a in anos}, capex=100.0, extra_por_ano=extra)
    assert M.aluguel_principal(_emp("TESTEAL3"), "2025", "2024", kd_real=0.17) == pytest.approx(100.0)


def test_aluguel_principal_nunca_fica_negativo():
    anos = [str(a) for a in range(2016, 2026)]
    extra = {a: {"arrendamento_pago_com_juros": 10.0, "arrendamento_saldo": 10_000.0} for a in anos}
    _serie_sintetica("TESTEAL4", {a: 1_000.0 for a in anos}, capex=100.0, extra_por_ano=extra)
    assert M.aluguel_principal(_emp("TESTEAL4"), "2025", "2024", kd_real=0.17) == 0.0


def test_aluguel_serie_sem_o_campo_nao_desconta_nada():
    _serie_sintetica("TESTEAL5", {str(a): 1_000.0 for a in range(2016, 2026)}, capex=100.0)
    assert M.aluguel_principal(_emp("TESTEAL5"), "2025", "2024", kd_real=0.17) == 0.0


# ---------------------------------------------------------------- defasagem do provento (§6.3)
def test_defasagem_manual_exige_fonte_nos_dois_motores():
    with pytest.raises(ValueError, match="defasagem_fonte"):
        M.exigir_declaracoes(_emp("TESTEDEF", defasagem_meses=9))
    M.exigir_declaracoes(_emp("TESTEDEF", defasagem_meses=9, defasagem_fonte="JCP pago até 30/04/2027 (RI)"))
    fin = Financeira("TESTEF", "x", "banco", preco=10.0, vpa=10.0, lpa_12m=1.0, roe_lp=0.15,
                     roe_inicio=0.15, payout=0.5, dpa_medio_5a=0.5, defasagem_meses=8)
    with pytest.raises(ValueError, match="defasagem_fonte"):
        avaliar_fin(fin, __import__("lote1_bancos").MK)


def test_defasagem_todos_os_tickers_reais_declaram_o_que_usam():
    import lote1_bancos as L1, lote2_energia as L2, lote3_agro as L3
    import lote4_saude_telecom as L4, lote5_petroleo as L5, lote6_quimica as L6
    for mod in (L1, L2, L3, L4, L5, L6):
        extras = [x for x in (getattr(mod, "ITSA4", None), getattr(mod, "EGIE", None)) if x is not None]
        for emp in list(mod.EMPRESAS) + extras:
            if isinstance(emp, M.Industrial):
                M.exigir_declaracoes(emp)
            elif emp.defasagem_meses is not None:
                assert emp.defasagem_fonte.strip(), emp.ticker


# ---------------------------------------------------------------- D7: saída por qualidade (§9)
def test_d7_precos_de_referencia():
    p = precos_de_referencia(100.0)
    assert (p["compra"], p["compra_parcial"], p["saida"]) == (70.0, 80.0, SAIDA_PADRAO * 100)
    assert p["saida_por_qualidade"] is False
    q = precos_de_referencia(100.0, True)
    assert q["saida"] == SAIDA_QUALIDADE * 100
    assert q["saida_por_qualidade"] is True


def test_d7_financeira_nunca_usa_a_excecao():
    """Não há série de 10 anos para financeira no repositório → a exceção não se aplica (declarado no §9)."""
    import lote1_bancos as L1
    for emp in L1.EMPRESAS:
        r = avaliar_fin(emp, L1.MK)
        assert r["saida"] == pytest.approx(SAIDA_PADRAO * r["central"])
        assert r["saida_por_qualidade"] is False


def test_d7_saida_segue_os_dois_criterios_em_todos_os_tickers():
    import lote3_agro as L3, lote4_saude_telecom as L4, lote5_petroleo as L5, lote6_quimica as L6
    for mod in (L3, L4, L5, L6):
        for emp in mod.EMPRESAS:
            if not isinstance(emp, M.Industrial):
                continue
            r = M.avaliar(emp, mod.MK)
            esperado = (r["roic_anos_total"] >= JANELA_MINIMA_SAIDA
                        and r["roic_anos_acima"] >= ANOS_ROIC_MINIMO
                        and r["notas"]["qualidade"] >= NOTA_QUALIDADE_MINIMA)
            assert r["saida_por_qualidade"] is esperado, emp.ticker
            assert r["saida"] == pytest.approx((SAIDA_QUALIDADE if esperado else SAIDA_PADRAO) * r["central"])


def test_d7_serie_de_roic_cobre_a_janela_declarada():
    import lote4_saude_telecom as L4
    for emp in L4.EMPRESAS:
        if not isinstance(emp, M.Industrial):
            continue
        r = M.avaliar(emp, L4.MK)
        assert r["roic_anos_total"] == len(M.anos_validos(emp.ticker, emp.anos_ciclo))
        assert 0 <= r["roic_anos_acima"] <= r["roic_anos_total"]

def test_d7_janela_curta_nunca_qualifica():
    """Janela declarada curta (quebra estrutural) não tem histórico de ciclo: "8 de 10" não tem referente."""
    import lote4_saude_telecom as L4, lote5_petroleo as L5
    curtos = {"TIMS3", "VIVT3", "FLRY3", "PRIO3", "RECV3", "UGPA3", "VBBR3"}
    for mod in (L4, L5):
        for emp in mod.EMPRESAS:
            if not isinstance(emp, M.Industrial) or emp.ticker not in curtos:
                continue
            r = M.avaliar(emp, mod.MK)
            assert r["roic_anos_total"] < JANELA_MINIMA_SAIDA, emp.ticker
            assert r["saida_por_qualidade"] is False, emp.ticker


def test_d7_roic_por_ano_e_real_contra_real():
    """O ROIC de um exercício antigo é nominal daquele ano; comparar com o WACC nominal de hoje reprovava tudo (§4)."""
    import lote6_quimica as L6
    emp = next(e for e in L6.EMPRESAS if getattr(e, "ticker", "") == "LEVE3")
    r = M.avaliar(emp, L6.MK)
    assert r["roic_anos_acima"] == sum(1 for x in r["roic_serie"].values() if x > r["wacc_real"])
    # a série guardada já está em termos reais: tem de ser menor que a nominal do mesmo exercício
    a, _ = M.serie("LEVE3")
    mo = M.mediana_outras("LEVE3", emp.anos_outras or M.anos_validos("LEVE3", emp.anos_ciclo), emp.outras_liquidas)
    x = "2021"
    d = a[x]
    _, _, dl = M.divida_liquida(d)
    nominal = M.ebit_aj(d, mo, emp.outras_liquidas) * (1 - r["aliquota"]) / (M.v(d, "pl", 0) + dl)
    assert r["roic_serie"][x] < nominal


def test_quebra_nao_e_desligada_por_capex_ciclico():
    """`capex_ciclico` é regra de capex (capex de rede), não perfil — não pode isentar serviço do alarme de quebra."""
    anos = [str(a) for a in range(2016, 2026)]
    extra = {a: {"ebit": 50.0 if int(a) < 2021 else 200.0} for a in anos}
    _serie_sintetica("TESTEQB", {a: 1_000.0 for a in anos}, capex=100.0, extra_por_ano=extra)
    op = M.premissas_operacionais(_emp("TESTEQB", capex_ciclico=True))
    assert op["quebra_suspeita"] is True


def test_roic_a_reposicao_e_none_sem_capital_contabil_positivo():
    """Capital negativo corrigido pela inflação pode virar positivo minúsculo e explodir o ROIC a reposição."""
    anos = [str(a) for a in range(2016, 2026)]
    extra = {a: {"pl": -500.0, "imobilizado": 900.0, "da": 90.0} for a in anos}
    _serie_sintetica("TESTENEG", {a: 1_000.0 for a in anos}, capex=100.0,
                     imobilizado=900.0, da=90.0, extra_por_ano=extra)
    r = M.valores(_emp("TESTENEG", g_real=0.0), __import__("lote3_agro").MK)
    assert r["roic"] is None and r["roic_reposicao"] is None and r["roic_filtro"] is None


def test_inflacao_fora_da_serie_nao_derruba_o_motor():
    assert inflacao.fator_entre(2026, 2027) > 0
    assert inflacao.fator_entre(1900, 2025) > 0
    assert inflacao.inflacao_do_ano(2027) == pytest.approx(inflacao.inflacao_do_ano(inflacao.BASE_MES // 12))


def test_aluguel_usa_kd_real_e_desconta_mais_que_o_nominal():
    """Kd nominal de hoje sobre saldo antigo devolvia juro demais e inflava o OE — o real erra para o lado que penaliza."""
    anos = [str(a) for a in range(2016, 2026)]
    extra = {a: {"arrendamento_pago_com_juros": 100.0, "arrendamento_saldo": 400.0} for a in anos}
    _serie_sintetica("TESTEAL6", {a: 1_000.0 for a in anos}, capex=100.0, extra_por_ano=extra)
    e = _emp("TESTEAL6")
    assert M.aluguel_principal(e, "2025", "2024", 0.08) > M.aluguel_principal(e, "2025", "2024", 0.15)
