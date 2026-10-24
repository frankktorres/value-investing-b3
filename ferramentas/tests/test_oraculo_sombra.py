"""Fase 4 (camada 3): o motor-sombra confere em casos de livro e não importa os motores (independência)."""
import ast
import pathlib

import pytest

from oraculo import sombra

AQUI = pathlib.Path(__file__).resolve().parents[1]


def test_sombra_nao_importa_os_motores():
    arvore = ast.parse((AQUI / "oraculo" / "sombra.py").read_text(encoding="utf-8"))
    nomes = {a.name for n in ast.walk(arvore) if isinstance(n, ast.Import) for a in n.names} | \
            {n.module for n in ast.walk(arvore) if isinstance(n, ast.ImportFrom)}
    assert nomes <= {"__future__", "statistics"}, nomes


def test_fcff_estavel_caso_de_livro():
    # NOPAT 100, g 2%, ROIC 10% → reinvestimento 20%; FCFF₁ = 100 × 1,02 × 0,8 = 81,6; WACC 8% → 81,6 ÷ 0,06 = 1.360
    assert sombra.fcff_estavel(100, 0.02, 0.10, 0.08) == pytest.approx(1360)
    assert sombra.fcff_estavel(100, 0.0, 0.10, 0.08) == pytest.approx(1250)            # g = 0 → EPV
    assert sombra.fcff_estavel(100, -0.02, None, 0.08) == pytest.approx(98 / 0.10)      # declínio sem liberar capital


def test_pvp_justificado_e_ddm_caso_de_livro():
    # ROE 15%, payout 60% → g = 6%; Ke 12% → P/VP = (0,15 − 0,06) ÷ (0,12 − 0,06) = 1,5; ROE constante: DDM = P/VP × VPA
    x = dict(vpa=10.0, roe_inicio=0.15, roe_lp=0.15, payout=0.6, ke_nom=0.12, g_teto=0.10, dc={"tipo": "zero"})
    r = sombra.financeira(x)
    assert r["ancoras"]["P/VP justificado"] == pytest.approx(15.0)
    assert r["ancoras"]["DDM 2 estágios"] == pytest.approx(15.0)
    assert sombra.financeira(dict(x, dc={"tipo": "fixo", "pct": 0.1}))["central"] == pytest.approx(13.5)


def test_industrial_epv_e_ponte():
    # receita 1.000, margem 20%, alíquota 0 → NOPAT 200; π 0 e WACC 10% → EPV da firma 2.000; ponte 500; 10 ações
    x = dict(perfil="ciclica", pi=0.0, wacc_nom=0.10, ke_nom=0.12, receita_meio=1000, m25=0.2, m50=0.2, m75=0.2,
             ajuste_manut=0.0, t=0.0, g=0.0, g1=None, anos_g1=0, cap_inv=1000, cap_rep=1000, dl=500, minor=0, n=10,
             oe_norm=None, declinio_sem_liberacao=False, passivos_acionista=0, reproducao=None, desc=0.0)
    r = sombra.industrial(x)
    assert r["ancoras"]["EPV"] == pytest.approx((2000 - 500) / 10)
    assert r["ancoras"]["DCF"] == pytest.approx(150)


def test_divergencia():
    assert sombra.divergencia(102, 100) == pytest.approx(0.02)
    assert sombra.divergencia(0, 0) == 0.0 and sombra.divergencia(1, 0) is None


BASE = dict(perfil="servicos", pi=0.0, wacc_nom=0.10, ke_nom=0.12, receita_meio=1000, m25=0.1, m50=0.2, m75=0.3,
            ajuste_manut=0.0, t=0.0, g=0.02, g1=None, anos_g1=0, cap_inv=1000, cap_rep=1000, dl=0, minor=0, n=1,
            oe_norm=None, declinio_sem_liberacao=False, passivos_acionista=0, reproducao=None, desc=0.0)


def test_dcf_pondera_25_50_25_com_piso_zero_e_trava_de_g():
    # ROIC por cenário = NOPAT ÷ 1.000: 10% (= WACC, não cria → g 0), 20% e 30% (criam → g 2%, reinvestimento 0,02 ÷ ROIC)
    pess = 100 / 0.10
    base = 200 * 1.02 * (1 - 0.02 / 0.20) / 0.08
    otim = 300 * 1.02 * (1 - 0.02 / 0.30) / 0.08
    assert sombra.industrial(BASE)["ancoras"]["DCF"] == pytest.approx(0.25 * pess + 0.5 * base + 0.25 * otim)
    neg = dict(BASE, dl=1500)                                   # cenário pessimista negativo entra como zero
    pess_n, base_n, otim_n = pess - 1500, base - 1500, otim - 1500
    assert pess_n < 0
    assert sombra.industrial(neg)["ancoras"]["DCF"] == pytest.approx(0.5 * base_n + 0.25 * otim_n)


def test_declinio_sem_liberar_capital_nao_reinveste_negativo():
    x = dict(BASE, g=-0.02, m25=0.05, m50=0.05, m75=0.05)       # ROIC 5% < WACC: não cria; freio da AUD-34
    assert sombra.industrial(x)["ancoras"]["DCF"] == pytest.approx(50 * 0.98 / 0.12)


def test_dois_estagios_caso_de_livro():
    # NOPAT 100, g1 10% por 2 anos com ROIC 20% (reinveste 50%), depois g 0; WACC 10%
    v = sombra.fcff_dois_estagios(100, 0.10, 2, 0.0, 0.20, 0.10)
    esperado = 110 * 0.5 / 1.1 + 121 * 0.5 / 1.1 ** 2 + (121 / 0.10) / 1.1 ** 2
    assert v == pytest.approx(esperado)


def test_desconto_do_controlador_por_cenarios_na_financeira():
    x = dict(vpa=10.0, roe_inicio=0.15, roe_lp=0.15, payout=0.6, ke_nom=0.12, g_teto=0.10,
             dc={"tipo": "cenarios", "delta_roe": 0.03, "peso": 0.5})
    base = sombra.financeira(dict(x, dc={"tipo": "zero"}))["ancoras"]["P/VP justificado"]
    inter = sombra.financeira(dict(x, roe_lp=0.12, dc={"tipo": "zero"}))["ancoras"]["P/VP justificado"]
    assert sombra.financeira(x)["ancoras"]["P/VP justificado"] == pytest.approx(0.5 * base + 0.5 * inter)
