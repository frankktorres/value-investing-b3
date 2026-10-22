"""Oráculo, camadas 4 e 5: o próprio conferente precisa pegar o que deve pegar (docs/ORACULO.md §2)."""
import math

import pytest

from oraculo import reconciliacao as R
from oraculo import sanidade as S


# ---------------------------------------------------------------- camada 4: tolerâncias do PRE-REGISTRO-v3 §3
def test_status_respeita_a_tolerancia_relativa_e_a_absoluta():
    assert R._status("bp", 1000.0, 1004.0, 1000.0)[0] == "ok"            # 0,4% ≤ 0,5%
    assert R._status("bp", 1000.0, 1006.0, 1000.0)[0] == "divergente"    # 0,6%
    assert R._status("bp", 0.5, 0.0, 0.5)[0] == "ok"                     # ≤ R$ 1 mil
    assert R._status("div", 109.0, 100.0)[0] == "ok"                     # dividendos: 10%
    assert R._status("bp", None, 1.0)[0] == "sem_dado"                   # ausente nunca vira ok nem zero


def test_identidade_quebrada_so_falha_em_ticker_com_palavra_de_decisao():
    linhas = [dict(ticker="AAA", check="bp", status="divergente"), dict(ticker="BBB", check="bp", status="divergente"),
              dict(ticker="AAA", check="div", status="divergente")]
    out = R.classificar(linhas, {"AAA": "BARATA", "BBB": "CARA"})
    assert [r["status"] for r in out] == ["falha", "bandeira", "bandeira"]


@pytest.fixture
def dfp_2025():
    if R._demo("2025", "BPA") is None:
        pytest.skip("sem dados/cvm/dfp_2025.zip")


def test_wege3_2025_fecha_nas_identidades(dfp_2025):
    """Caso real conferido no DFP 2025 da WEG (CVM 5410): DFC 6.01+6.02+6.03+6.04 = 6.05 = −1.051.101; saldo final 6.296.498."""
    st = {r["check"]: r for r in R.conferir("WEGE3", "2025")}
    for c in ("bp", "bp_partes", "dfc", "dfc_saldo", "dfc_bp", "dre_dmpl"):
        assert st[c]["status"] == "ok", c
    assert st["dfc"]["esperado"] == pytest.approx(-1_051_101.0)
    assert st["dfc_bp"]["calculado"] == pytest.approx(6_296_498.0)


def test_acoes_em_milhares_viram_bandeira_de_escala(dfp_2025):
    """KEPL3 2025: lucro do controlador 156.270 mil e LPA 0,9017 → ~173 mi de ações; a série guardava 173.332 (milhares)."""
    st = {r["check"]: r for r in R.conferir("KEPL3", "2025", acoes=173_332.0)}
    assert "acoes_escala" in st and "lpa" not in st
    st = {r["check"]: r for r in R.conferir("KEPL3", "2025", acoes=173_332_000.0)}
    assert st["lpa"]["status"] == "ok"


# ---------------------------------------------------------------- camada 5: alarmes
def _l(tk, **kw):
    base = dict(ticker=tk, financeira=False, palavra="CARA", central=10.0, preco=10.0, pc=1.0, ke_nom=0.18, ke_real=0.11,
                ke_implicito=0.15, dispersao=1.1, nao_finitos=[], lpa_norm=1.0, roic=0.1, roic_serie={})
    base.update(kw)
    return base


def test_ke_acima_do_teto_bloqueia_salvo_conhecido():
    c = S.checks([_l("NOVO1", ke_nom=0.31)] + [_l(tk, ke_nom=0.5) for tk in S.CONHECIDOS])
    assert any("NOVO1" in b for b in c["bloqueantes"])
    assert not any(tk in b for b in c["bloqueantes"] for tk in S.CONHECIDOS)


def test_catraca_dos_conhecidos_exige_tirar_quem_saiu_do_alarme():
    tk = next(iter(S.CONHECIDOS))
    c = S.checks([_l(tk, ke_nom=0.20)])
    assert any("catraca" in b and tk in b for b in c["bloqueantes"])


def test_nao_finito_bloqueia():
    c = S.checks([_l("X", nao_finitos=["central"])] + [_l(tk, ke_nom=0.5) for tk in S.CONHECIDOS])
    assert any("não finito" in b for b in c["bloqueantes"])


def test_screen_ruim_em_palavra_de_compra_e_bandeira_vermelha():
    c = S.checks([_l("Y", palavra="BARATA", piotroski=2, beneish=-1.0)] + [_l(tk, ke_nom=0.5) for tk in S.CONHECIDOS])
    assert sum("Y:" in b for b in c["bandeiras"]) == 2
    assert not any("Y:" in b for b in c["bloqueantes"])


def test_compounder_pela_serie_ou_pelo_roic_atual():
    assert S._compounder(dict(roic_serie={str(a): 0.12 for a in range(2016, 2026)}, roic=0.05))
    assert S._compounder(dict(roic_serie={}, roic=0.16))
    assert not S._compounder(dict(roic_serie={str(a): 0.04 for a in range(2016, 2026)}, roic=0.10))
    assert math.isclose(S.KE_TETO, 0.30)
