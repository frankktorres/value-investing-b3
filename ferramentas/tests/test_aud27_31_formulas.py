"""Testes que distinguem certo de errado (Onda 2, 2ª parte da auditoria de 08/10/2026: AUD-27, 28, 30, 31, 88, 90).

Os números abaixo são escritos à mão a partir da doutrina (§4, §6, §9, §11.4), SEM importar as constantes do motor: se alguém
mexer na constante, o teste vermelho é o aviso. O golden prova "igual"; aqui se prova "certo".
"""
import math

import pytest

import golden
import inflacao
import motor_nao_financeiras as M
import motor_financeiras as F
from tests.test_metodo_f2 import _emp, _serie_sintetica

ANOS = [str(a) for a in range(2016, 2026)]


# ---------------------------------------------------------------- AUD-88: régua da palavra
@pytest.mark.parametrize("pc,esperada", [
    (0.70, "BARATA"), (0.7001, "RADAR"),
    (0.90, "RADAR"), (0.9001, "JUSTA"),
    (1.10, "JUSTA"), (1.1001, "CARA"), (3.0, "CARA"),
])
def test_aud88_borda_da_regua_pertence_a_faixa_de_baixo(pc, esperada):
    assert F.palavra(pc) == esperada


# ---------------------------------------------------------------- AUD-27: preços de referência e exceção de saída
def test_aud27_precos_de_referencia_com_numeros_da_doutrina():
    p = F.precos_de_referencia(100.0)
    assert (p["compra"], p["compra_parcial"], p["saida"], p["saida_por_qualidade"]) == (
        pytest.approx(70.0), pytest.approx(80.0), pytest.approx(130.0), False)
    q = F.precos_de_referencia(100.0, saida_por_qualidade=True)
    assert q["saida"] == pytest.approx(150.0) and q["saida_por_qualidade"] is True


@pytest.mark.parametrize("anos_serie,acima,nota,esperado", [
    (10, 8, 8.0, True),        # exatamente nos três limiares
    (10, 8, 7.99, False),      # nota 8 é piso
    (10, 7, 9.5, False),       # 8 de 10 é piso
    (9, 9, 9.5, False),        # série de 10 exercícios é piso
    (10, 10, 10.0, True),
    (12, 8, 8.0, True),
])
def test_aud27_excecao_de_saida_nos_limiares_da_doutrina(anos_serie, acima, nota, esperado):
    assert M.qualifica_saida(anos_serie, acima, nota) is esperado


# ---------------------------------------------------------------- AUD-28: ROIC real contra real, valor exato
def test_aud28_roic_por_ano_e_o_nominal_deflacionado_pela_inflacao_do_proprio_ano():
    """Série sintética sem imobilizado, sem dívida e sem 'outras': ROIC nominal do ano = EBIT×(1−t)/PL, depois deflacionado."""
    extra = {a: {"imobilizado": 0.0, "pl": 1000.0, "ebit": 250.0 + 10 * (int(a) - 2016)} for a in ANOS}
    _serie_sintetica("ROICX", {a: 1000.0 for a in ANOS}, capex=100.0, imobilizado=0.0, extra_por_ano=extra)
    emp = _emp("ROICX")
    t = 0.30
    serie, _ = M.roic_por_ano(emp, w_real=0.0, t_ef=t, med_outras=None)
    assert sorted(serie) == ANOS
    for a in ANOS:
        nominal = (250.0 + 10 * (int(a) - 2016)) * (1 - t) / 1000.0
        esperado = (1 + nominal) / (1 + inflacao.inflacao_do_ano(a)) - 1
        assert serie[a] == pytest.approx(esperado, abs=1e-12), a
        assert serie[a] < nominal, a        # inflação positiva: o real é menor que o nominal


def test_aud28_contagem_acima_do_wacc_real_usa_o_roic_deflacionado():
    """ROIC nominal 12,0% ao ano em todos os exercícios: com WACC real 7% a contagem só bate se o ROIC for REAL.
    Em 2016–2025 a inflação anual fica acima de 3,2%, então o real é < 8,5% — e o nominal (12%) passaria sempre."""
    extra = {a: {"imobilizado": 0.0, "pl": 1000.0, "ebit": 120.0 / 0.70} for a in ANOS}   # NOPAT 120 com t = 30%
    _serie_sintetica("ROICY", {a: 1000.0 for a in ANOS}, capex=100.0, imobilizado=0.0, extra_por_ano=extra)
    _, acima = M.roic_por_ano(_emp("ROICY"), w_real=0.07, t_ef=0.30, med_outras=None)
    reais = {a: (1.12) / (1 + inflacao.inflacao_do_ano(a)) - 1 for a in ANOS}
    assert acima == sum(1 for a in ANOS if reais[a] > 0.07)
    assert 0 < acima < len(ANOS), "o cenário tem de separar exercícios acima e abaixo, senão não distingue real de nominal"
    assert acima < sum(1 for a in ANOS if 0.12 > 0.07)   # o nominal contaria os 10


# ---------------------------------------------------------------- AUD-30: golden com NaN
def test_aud30_golden_nao_aceita_nan_em_nenhum_campo():
    g = {"X": {"central": 10.0, "pc": 1.0, "ancoras": {"a": 9.0, "b": 11.0}, "palavra": "JUSTA", "dy": 0.05}}
    for campo in ("central", "pc", "dy"):
        a = {"X": {**g["X"], campo: math.nan}}
        assert golden.comparar(g, a), campo
        assert golden.comparar(a, a), f"NaN dos dois lados também é mudança ({campo})"
    a = {"X": {**g["X"], "ancoras": {"a": math.nan, "b": 11.0}}}
    assert golden.comparar(g, a)
    assert not golden.comparar(g, g)


def test_aud30_infinito_igual_continua_igual_e_salvar_recusa_nan(tmp_path, monkeypatch):
    g = {"X": {"central": math.inf, "ancoras": {}}}
    assert not golden.comparar(g, g)
    monkeypatch.setattr(golden, "GOLDEN", tmp_path / "g.json")
    monkeypatch.setattr(golden, "LOG", tmp_path / "log.md")
    with pytest.raises(ValueError, match="NaN"):
        golden.salvar({"X": {"central": math.nan, "ancoras": {}}}, "teste de recusa de NaN")
    with pytest.raises(ValueError, match="NaN"):
        golden.salvar({"X": {"central": 1.0, "ancoras": {"a": math.nan}}}, "teste de recusa de NaN")
    assert not (tmp_path / "g.json").exists()


# ---------------------------------------------------------------- AUD-31: fórmulas à mão
def test_aud31_liquido_diferido_com_conta_escrita_a_mao():
    # 10% a.a. por 10 anos: 1,1^10 = 2,5937424601; IR de 15% só sobre o ganho; volta a taxa anual
    esperado = ((2.5937424601 - 1) * 0.85 + 1) ** 0.1 - 1
    assert F.liquido_diferido(0.10) == pytest.approx(esperado, abs=1e-10)
    assert F.liquido_diferido(0.10) == pytest.approx(0.0894, abs=5e-5)    # ≈ 8,94% (sanidade do valor absoluto)
    assert F.liquido_diferido(0.0) == 0.0 and F.liquido_diferido(-0.02) == -0.02     # sem ganho não há IR
    assert F.liquido_diferido(0.10, anos=1) == pytest.approx(0.10 * 0.85)             # 1 ano: 15% do ganho


def test_aud31_mercado_com_numeros_de_exemplo():
    mk = F.Mercado(rf_real=0.06, pi=0.04)
    assert mk.ke_real == pytest.approx(0.11)                       # rf + 5 p.p.
    assert mk.ke_nom == pytest.approx(1.11 * 1.04 - 1)             # 15,44%
    assert mk.rf_nom == pytest.approx(1.06 * 1.04 - 1)             # 10,24%
    assert mk.rf_liq_nom == pytest.approx(((1.1024 ** 10 - 1) * 0.85 + 1) ** 0.1 - 1)
    assert mk.rf_liq_real == pytest.approx((1 + mk.rf_liq_nom) / 1.04 - 1)
    assert mk.rf_liq_nom < mk.rf_nom


def test_aud31_renda_defasagem_e_bogle_de_todos_os_tickers_recalculados_fora_do_motor():
    """Para os 41 tickers: fator de defasagem, IRRF do JCP (17,5%), yield líquido, Bogle e Bogle líquido real refeitos aqui,
    com a alíquota 0,175 e o resgate 0,15 escritos à mão. Mutar o sinal ou o valor do IR quebra isto, não só o golden."""
    import universo
    mk = universo.MK
    for tk, item in universo.avaliar_todos().items():
        r, emp = item["r"], item["empresa"]
        nf = "g_nom" in r
        ke = r["ke_nom_emp"] if nf else r["ke"]
        g = r["g_nom"] if nf else r["g"]
        meses = r["defasagem_meses"]
        assert r["fator_defasagem"] == pytest.approx((1 + ke) ** (-meses / 12), abs=1e-12), tk
        assert r["dy_liq"] == pytest.approx(r["dy"] * (1 - emp.jcp_share * 0.175), abs=1e-12), tk
        assert r["dy_liq"] <= r["dy"] + 1e-15, tk
        assert r["bogle_nom"] == pytest.approx(r["dy"] + g + r["dmult"], abs=1e-12), tk
        gc = g + r["dmult"]
        liq = (((1 + gc) ** 10 - 1) * 0.85 + 1) ** 0.1 - 1 if gc > 0 else gc
        assert r["bogle_liq_real"] == pytest.approx((1 + r["dy_liq"] + liq) / (1 + mk.pi) - 1, abs=1e-12), tk


# ---------------------------------------------------------------- AUD-90: limiares da alíquota e da quebra estrutural
def _com_aliquota(tk, taxa, anos_com_lair=5):
    extra = {a: {"lair": 1000.0 if i >= 10 - anos_com_lair else 0.0, "ir": -1000.0 * taxa} for i, a in enumerate(ANOS)}
    _serie_sintetica(tk, {a: 1000.0 for a in ANOS}, capex=100.0, extra_por_ano=extra)
    return _emp(tk)


@pytest.mark.parametrize("taxa,regra,valor", [
    (0.12, "sem_origem", 0.34),       # abaixo de 15% sem origem declarada → 34% (um limiar de 10% daria "mediana" aqui)
    (0.1499, "sem_origem", 0.34),
    (0.15, "mediana", 0.15),          # no limiar vale a mediana
    (0.20, "mediana", 0.20),
    (0.40, "mediana", 0.34),          # teto de 34%
])
def test_aud90_limiar_de_origem_da_aliquota(taxa, regra, valor):
    v, r = M.aliquota_regra(_com_aliquota("ALQ", taxa))
    assert (r, v) == (regra, pytest.approx(valor))


def test_aud90_aliquota_baixa_com_origem_declarada_vale_a_mediana():
    emp = _com_aliquota("ALQ2", 0.12)
    emp.aliquota_permanente_fonte = "JCP permanente (teste)"
    assert M.aliquota_regra(emp) == (pytest.approx(0.12), "permanente")


def test_aud90_minimo_de_tres_anos_para_a_mediana_da_aliquota():
    assert M.aliquota_regra(_com_aliquota("ALQ3", 0.25, anos_com_lair=3)) == (pytest.approx(0.25), "mediana")
    assert M.aliquota_regra(_com_aliquota("ALQ4", 0.25, anos_com_lair=2)) == (0.34, "sem_dado")
    assert M.mediana_efetiva(_com_aliquota("ALQ5", 0.25, anos_com_lair=2)) is None


@pytest.mark.parametrize("fator,divergencia,quebra", [
    (1.6, 0.2308, False),            # abaixo de 25%
    (1.9, 0.3103, True),             # acima de 25% e abaixo de 40%: um limite de 40% não pegaria
    (2.5, 0.4286, True),
])
def test_aud90_limite_de_quebra_estrutural_25_por_cento(fator, divergencia, quebra):
    extra = {a: {"ebit": 100.0 if int(a) < 2021 else 100.0 * fator} for a in ANOS}
    _serie_sintetica("QBR", {a: 1000.0 for a in ANOS}, capex=100.0, extra_por_ano=extra)
    op = M.premissas_operacionais(_emp("QBR"))
    assert op["divergencia_janela"] == pytest.approx(divergencia, abs=5e-4)
    assert op["quebra_suspeita"] is quebra


def test_aud90_janela_minima_da_saida_e_dez_exercicios():
    assert M.JANELA_MINIMA_SAIDA == 10 and M.qualifica_saida(10, 8, 8.0) and not M.qualifica_saida(9, 8, 8.0)
