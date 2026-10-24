"""O4b, parte 2: testes para os sobreviventes 9–20 de docs/oraculo/mutacao-2026-10-23.md.

Financeiras (9–17): `central_ao_ke` com desconto por cenários, as faixas do "vence a renda fixa", o Bogle real, o DPA
líquido do IR do JCP, o teto de Bazin só com dividendo coberto e as bordas da exceção de compra parcial (0,80×).
Não financeiras (18–20): DCF reverso de 1 e 2 estágios e Ke implícito — limites da busca e o E do ponto fixo.
Nenhum código de motor muda; só prova o que o motor já faz.
"""
import dataclasses
from dataclasses import replace
from statistics import median
from unittest import mock

import pytest

import mercado
import motor_financeiras as F
import motor_nao_financeiras as M
from oraculo import sanidade as S

MK = mercado.vigente()


@pytest.fixture(scope="module")
def banco():
    e = next((e for e in S.empresas().values()
              if isinstance(e, F.Financeira) and not e.horizonte_finito and e.sotp is None and e.roe_lp > 0
              and e.desconto_controlador["tipo"] == "zero" and not e.fora_circulo), None)
    if e is None:
        pytest.skip("nenhum banco do hall serve de base (sem desconto, dentro do círculo, ROE > 0)")
    return e


CENARIOS = {"tipo": "cenarios", "delta_roe": 0.03, "peso": 0.3, "razao": "teste"}


# ------------------------------------------------------------------ itens 9 e 10: central_ao_ke com cenários
def test_central_ao_ke_no_ke_da_casa_e_o_central_do_motor_com_cenarios(banco):
    emp = replace(banco, desconto_controlador=CENARIOS)
    r = F.avaliar(emp, MK)
    assert r["desc_controlador"] > 0.001                      # o cenário de interferência pesa de fato
    assert F.central_ao_ke(emp, MK, MK.ke_nom) == pytest.approx(r["central"], rel=1e-9)


def test_central_ao_ke_pondera_base_e_interferencia(banco):
    emp = replace(banco, desconto_controlador=CENARIOS)
    base, inter = {"a": 10.0, "b": 14.0, "c": 20.0}, {"a": 4.0, "b": 6.0, "c": 9.0}
    with mock.patch.object(F, "ancoras", lambda e, mk, roe: dict(base if roe >= e.roe_lp - 1e-12 else inter)):
        c = F.central_ao_ke(emp, MK, 0.20)
    assert c == pytest.approx(median(0.7 * base[k] + 0.3 * inter[k] for k in base))   # = 0,7 × 14 + 0,3 × 6 = 11,6


# ------------------------------------------------------------------ itens 11 a 13: Bogle e "vence a renda fixa"
def _faixa(x, rf):
    return "Sim" if x >= rf + 0.03 else ("Empate" if x >= rf + 0.015 else "Não")


def test_vence_rf_segue_as_faixas_de_3_e_1_5_pp(banco):
    rf = MK.rf_liq_real
    vistos = {}
    # varre o preço para o Bogle líquido real cruzar as duas fronteiras, inclusive entre rf − 3 p.p. e rf + 3 p.p.
    for f in [x / 200 for x in range(20, 801)]:
        r = F.avaliar(replace(banco, preco=banco.preco * f), MK)
        b = r["bogle_liq_real"]
        assert r["vence_rf"] == _faixa(b, rf), (f, b)
        assert r["carimbo_rf"] == (b < rf)
        vistos.setdefault(round((b - rf) * 200), r["vence_rf"])  # faixas de 0,5 p.p. em volta da rf
    faixas = {k for k in vistos}
    # pontos dos dois lados de cada borda (rf, rf + 1,5 e rf + 3 p.p.) e no meio de cada faixa
    for k in (-6, -1, 0, 2, 3, 5, 6, 8):
        assert k in faixas, (k, sorted(faixas))


def test_bogle_real_e_a_conversao_de_fisher_do_nominal(banco):
    for f in (0.6, 1.0, 1.7):
        r = F.avaliar(replace(banco, preco=banco.preco * f, pl_hist=None), MK)
        assert r["bogle_real"] == pytest.approx((1 + r["bogle_nom"]) / (1 + MK.pi) - 1, rel=1e-12)
        assert r["bogle_real"] < r["bogle_nom"]                 # π > 0


# ------------------------------------------------------------------ itens 14 e 15: DPA líquido e teto de Bazin
def test_dpa_liquido_desconta_o_ir_so_da_parcela_em_jcp(banco):
    for share in (0.0, 0.4, 1.0):
        r = F.avaliar(replace(banco, jcp_share=share), MK)
        assert r["dpa_sust_liq"] == pytest.approx(r["dpa_sust_vp"] * (1 - share * F.IR_JCP), rel=1e-12)
    assert F.IR_JCP == 0.175


def test_teto_de_bazin_so_com_dividendo_coberto(banco):
    r = F.avaliar(replace(banco, cobertura_caixa=True, jcp_share=0.4), MK)
    assert r["teto_renda"] == pytest.approx(r["dpa_sust_liq"] / MK.rf_liq_nom, rel=1e-12)
    assert F.avaliar(replace(banco, cobertura_caixa=False), MK)["teto_renda"] is None


# ------------------------------------------------------------------ itens 16 e 17: bordas da exceção de 0,80×
def _r(**kw):
    base = dict(palavra="JUSTA", central=10.0, pc=0.75, dispersao=1.5, notas={"qualidade": 8.5, "solidez": 7.5})
    notas = {k: kw.pop(k) for k in ("qualidade", "solidez") if k in kw}
    base.update(kw)
    base["notas"] = {**base["notas"], **notas}
    return base


def test_entrada_parcial_bordas_inclusivas():
    assert F.entrada_parcial(_r())[0]
    assert F.entrada_parcial(_r(qualidade=8.0))[0]                      # ≥ 8
    assert not F.entrada_parcial(_r(qualidade=7.999))[0]
    assert F.entrada_parcial(_r(solidez=7.0))[0]                        # ≥ 7
    assert not F.entrada_parcial(_r(solidez=6.999))[0]
    assert F.entrada_parcial(_r(dispersao=1.8))[0]                      # ≤ 1,8×
    assert not F.entrada_parcial(_r(dispersao=1.8001))[0]
    assert F.entrada_parcial(_r(pc=0.80))[0]                            # ≤ 0,80×
    assert not F.entrada_parcial(_r(pc=0.8001))[0]


def test_entrada_parcial_central_zero_e_recusa_mesmo_com_palavra():
    ok, m = F.entrada_parcial(_r(central=0.0, pc=float("inf")))
    assert not ok and "sem palavra (NÃO CONCLUSIVO)" in m


def test_entrada_parcial_arredonda_o_pc_em_9_casas():
    # 0,80 + 4e-10: em 9 casas vira 0,80 (passa); em 10 casas seria 0,8000000004 (recusaria)
    assert F.entrada_parcial(_r(pc=0.80 + 4e-10))[0]
    assert not F.entrada_parcial(_r(pc=0.80 + 6e-9))[0]


# ------------------------------------------------------------------ itens 18 a 20: não financeiras
# No Ke da própria empresa o DCF fica plano para g ≥ 0 em 19 de 21 industriais (ROIC < WACC: a trava de Greenwald zera o g
# positivo; em 24/10). A B3SA3 cria valor (ROIC 24,6% × WACC 18,1%): o preço é montado a partir do próprio DCF para a busca ter
# resposta conhecida.
def _emp(tk):
    import universo
    return next(e for _, emps, _ in universo.GRUPOS for e in emps if e.ticker == tk), universo.MK


@pytest.fixture(scope="module")
def b3sa3():
    emp, mk0 = _emp("B3SA3")
    ec = M.estrutura_de_capital(emp, mk0)
    return emp, ec["mk"], ec["e_peso"]


def _dcf(emp, mk, ep, **kw):
    return M.descontar({"b": M.valores(emp, mk, e_peso=ep, **kw)["dcf"]["base"]}, M.desconto_pct(emp))["b"]


def test_g_implicito_ida_e_volta_com_o_e_do_ponto_fixo(b3sa3):          # item 18 (e_peso → None no 1 estágio)
    emp, mk, ep = b3sa3
    assert _dcf(emp, mk, ep, g_real=0.02) > _dcf(emp, mk, ep, g_real=0.0)      # cria valor: o DCF responde ao g
    assert _dcf(emp, mk, ep, g_real=0.01) != pytest.approx(_dcf(emp, mk, None, g_real=0.01), rel=1e-4)
    e = replace(emp, preco=_dcf(emp, mk, ep, g_real=0.01))
    assert M.g_implicito(e, mk, ep) == pytest.approx(0.01, abs=1e-8)


@pytest.fixture(scope="module")
def b3sa3_rf_baixa():
    """Mercado com rf real de 3%: o WACC real cai a ~7,4% e o teto da busca passa a ser wacc_real − 0,002 (não 0,08)."""
    emp, mk0 = _emp("B3SA3")
    ec = M.estrutura_de_capital(emp, mercado.Mercado(0.03, mk0.pi, premio=mk0.premio))
    return emp, ec["mk"], ec["e_peso"]


@pytest.mark.parametrize("caso", ["b3sa3", "b3sa3_rf_baixa"])
def test_g_implicito_limites_da_busca(caso, request):                  # item 18 (−0,05; 0,08; wacc_real − 0,002)
    emp, mk, ep = request.getfixturevalue(caso)
    w = M.valores(emp, mk, e_peso=ep)["wacc_real"]
    hi = min(0.08, w - 0.002)
    if caso == "b3sa3_rf_baixa":
        assert hi == w - 0.002 < 0.078
        # o teto usa o WACC do E do ponto fixo: entre o teto dele e o teto pelo preço a busca não tem resposta
        hi_preco = min(0.08, M.valores(emp, mk, e_peso=None)["wacc_real"] - 0.002)
        assert hi_preco > hi + 0.002
        meio = _dcf(emp, mk, ep, g_real=(hi + hi_preco) / 2)
        assert meio > _dcf(emp, mk, ep, g_real=hi) and M.g_implicito(replace(emp, preco=meio), mk, ep) is None
    teto = _dcf(emp, mk, ep, g_real=hi)
    assert M.g_implicito(replace(emp, preco=teto * 1.0001), mk, ep) is None
    g = M.g_implicito(replace(emp, preco=teto * 0.9999), mk, ep)
    assert g is not None and hi - 0.001 < g < hi
    piso = _dcf(emp, mk, ep, g_real=-0.05)
    assert M.g_implicito(replace(emp, preco=piso * 0.9999), mk, ep) == pytest.approx(-0.05 - 1e-9, abs=1e-15)
    g = M.g_implicito(replace(emp, preco=piso * 1.0001), mk, ep)
    assert -0.05 < g < -0.049


def test_g_implicito_dois_estagios_usa_o_e_do_ponto_fixo(b3sa3):       # item 19
    emp, mk, ep = b3sa3
    emp = replace(emp, g1_real=0.05)
    assert _dcf(emp, mk, ep, g1=0.10) != pytest.approx(_dcf(emp, mk, None, g1=0.10), rel=1e-4)
    e = replace(emp, preco=_dcf(emp, mk, ep, g1=0.10))
    assert M.g_implicito(e, mk, ep) == pytest.approx(0.10, abs=1e-8)
    assert M.g_implicito(replace(e, preco=_dcf(emp, mk, ep, g1=0.40) * 1.0001), mk, ep) is None
    assert M.g_implicito(replace(e, preco=_dcf(emp, mk, ep, g1=0.0) * 0.9999), mk, ep) == pytest.approx(-1e-9, abs=1e-15)


def _central(emp, mk, ep, k):
    return M.central_de(M.descontar(M.valores(emp, mk, ke_nom=k, e_peso=ep)["anc"], M.desconto_pct(emp)))[0]


@pytest.mark.parametrize("tk", ["B3SA3", "KEPL3", "PETR4"])      # PETR4: desconto de controlador por cenários
def test_ke_implicito_ida_e_volta_e_piso(tk):                        # item 20
    emp, mk0 = _emp(tk)
    ec = M.estrutura_de_capital(emp, mk0)
    mk, ep = ec["mk"], ec["e_peso"]
    lo = mk.g_teto + 0.003
    e = replace(emp, preco=_central(emp, mk, ep, 0.20))
    assert M.ke_implicito(e, mk, ep) == pytest.approx(0.20, abs=1e-8)
    assert _central(emp, mk, ep, 0.20) != pytest.approx(_central(emp, mk, None, 0.20), rel=1e-4)
    topo = _central(emp, mk, ep, lo)
    assert M.ke_implicito(replace(emp, preco=topo * 1.0001), mk, ep) is None
    k = M.ke_implicito(replace(emp, preco=topo * 0.9999), mk, ep)
    assert k is not None and lo < k < lo + 0.002
