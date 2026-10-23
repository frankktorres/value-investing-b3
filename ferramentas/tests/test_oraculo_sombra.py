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
    # receita 1.000, margem 20%, t 0 → NOPAT 200; WACC = π → WACC real 0 seria inválido, então π 0 e WACC 10%: EPV firma 2.000
    x = dict(perfil="ciclica", pi=0.0, wacc_nom=0.10, ke_nom=0.12, receita_meio=1000, m25=0.2, m50=0.2, m75=0.2,
             ajuste_manut=0.0, t=0.0, g=0.0, g1=None, anos_g1=0, cap_inv=1000, cap_rep=1000, dl=500, minor=0, n=10,
             oe_norm=None, declinio_sem_liberacao=False, passivos_acionista=0, reproducao=None, desc=0.0)
    r = sombra.industrial(x)
    assert r["ancoras"]["EPV"] == pytest.approx((2000 - 500) / 10)
    assert r["ancoras"]["DCF"] == pytest.approx(150)


def test_divergencia():
    assert sombra.divergencia(102, 100) == pytest.approx(0.02)
    assert sombra.divergencia(0, 0) == 0.0 and sombra.divergencia(1, 0) is None
