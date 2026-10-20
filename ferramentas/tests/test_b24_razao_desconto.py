"""B24 (AUD-41, decisão de 14/10/2026): o desconto de controlador é "sempre declarado, inclusive zero" (doutrina §5).

Razão vazia não roda em nenhum dos dois motores; sem fonte nota A/B a razão é o marcador SEM_RAZAO (nunca inventada).
"""
from dataclasses import replace

import pytest

import lote1_bancos
import motor_financeiras as MF
import motor_nao_financeiras as MN
from lote1_bancos import MK


def _universo():
    import universo
    return [e for _, emps, _ in universo.GRUPOS for e in emps]


@pytest.mark.parametrize("razao", ["", "   ", None])
def test_financeira_sem_razao_nao_roda(razao):
    itub = next(e for e in lote1_bancos.EMPRESAS if e.ticker == "ITUB4")
    e = replace(itub, desconto_controlador={"tipo": "zero", "razao": razao})
    with pytest.raises(ValueError, match="ITUB4: desconto_controlador .* sem razão"):
        MF.avaliar(e, MK)


def test_financeira_default_do_dataclass_nao_roda():
    itub = next(e for e in lote1_bancos.EMPRESAS if e.ticker == "ITUB4")
    e = MF.Financeira(itub.ticker, itub.nome, itub.perfil, preco=itub.preco, vpa=itub.vpa, lpa_12m=itub.lpa_12m,
                      roe_lp=itub.roe_lp, roe_inicio=itub.roe_inicio, payout=itub.payout, dpa_medio_5a=itub.dpa_medio_5a)
    with pytest.raises(ValueError, match="sem razão"):
        MF.avaliar(e, MK)


def test_industrial_sem_razao_nao_roda():
    e = MN.Industrial("TESTEB24", "teste", "servicos", preco=10.0, n_acoes=1_000_000.0)
    with pytest.raises(ValueError, match="TESTEB24: .*desconto_controlador \\(zero\\) sem razão"):
        MN.exigir_declaracoes(e)


def test_fixo_ou_cenarios_tambem_exigem_razao():
    e = MN.Industrial("TESTEB24", "teste", "servicos", preco=10.0, n_acoes=1_000_000.0,
                      desconto_controlador={"tipo": "fixo", "pct": 0.1, "razao": ""})
    assert MF.falta_razao_desconto(e)


def test_marcador_sem_razao_conta_como_declarado():
    e = MN.Industrial("TESTEB24", "teste", "servicos", preco=10.0, n_acoes=1_000_000.0,
                      desconto_controlador={"tipo": "zero", "razao": MF.SEM_RAZAO})
    assert MF.falta_razao_desconto(e) is None


def test_universo_todo_declarado_e_23_sem_fonte():
    """Trava contra regressão: os 23 sem fonte A/B (28 em 14/10/2026; B26 de 20/10 achou 5) só saem desta conta com razão de fonte A/B escrita."""
    emps = _universo()
    assert all(MF.falta_razao_desconto(e) is None for e in emps)
    sem = sorted(e.ticker for e in emps if e.desconto_controlador["razao"] == MF.SEM_RAZAO)
    assert len(sem) == 23, sem
    leve = next(e for e in emps if e.ticker == "LEVE3")
    razao = leve.desconto_controlador["razao"]
    assert "FRE 2026" in razao and "DFP 2025 nota 13" in razao and "Ressalva do D3" in razao   # citação conferida contra o insumo
    # B26 (20/10/2026): sem controlador pelo FRE 2026 (CVM id conferido na tabela de posição acionária)
    ids = {"PRIO3": "161257", "KEPL3": "161068", "RECV3": "161485", "VBBR3": "159172", "B3SA3": "161005"}
    for tk, id_doc in ids.items():
        r = next(e for e in emps if e.ticker == tk).desconto_controlador["razao"]
        assert r != MF.SEM_RAZAO and f"FRE 2026, CVM id {id_doc}, nota A" in r, tk


def test_nenhum_codigo_monta_desconto_com_razao_vazia():
    """Revisão adversarial de 14/10: a sensibilidade "sem desconto" do gerar_pdf_lote2 quebrava o PDF inteiro."""
    import pathlib
    raiz = pathlib.Path(__file__).resolve().parent.parent
    ruins = [str(f.relative_to(raiz)) for f in raiz.rglob("*.py") if "backtest" not in f.parts and "tests" not in f.parts
             and f.name not in ("motor_financeiras.py", "motor_nao_financeiras.py")      # default do dataclass: não declarar = falha
             and '"razao": ""' in f.read_text(encoding="utf-8")]
    assert ruins == []
