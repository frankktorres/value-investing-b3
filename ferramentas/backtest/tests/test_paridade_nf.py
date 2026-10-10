"""Paridade entre o motor reduzido (backtest/triagem) e `motor_nao_financeiras` da mesa (AUD-91).

Até aqui só as funções puras de `contas.py` e as financeiras tinham teste de equivalência; as
premissas do motor reduzido não-financeiro (margem, receita de meio, ajuste de manutenção, alíquota)
podiam derivar da mesa sem nenhum teste vermelho (mutações M01–M13, M15, M16 sobreviviam).

Método: uma empresa SINTÉTICA entra nos dois motores com a mesma série. Para os dois lados serem
comparáveis o IPCA é achatado em 1,0 (a mesa lê `DEFLATOR`; o reduzido lê `Ano.real`) e a receita é
constante — com Δreceita = 0 o Greenwald dá manutenção = capex nos dois, que é onde as fórmulas
declaram coincidir. O que NÃO coincide por desenho (janela de receita, ajuste de manutenção com
crescimento — mesa com Greenwald, reduzido com o capex total —, alíquota v2.3) está fixado em `test_divergencias_declaradas_*`: se um dos lados mudar,
o teste vira e obriga a decidir se a mudança deve chegar ao outro.

Importar a mesa aqui é legítimo (mesmo critério de test_premio_parametrizado): o que é proibido é o
RUNTIME do backtest ler premissa de 2026.
"""
from __future__ import annotations

import pytest

from backtest.mercado_bt import MercadoBT
from backtest.motor import reduzido_nf
from backtest.motor.base import Ano
from backtest.tests.test_reduzido import _ins

TK = "ZZZZ3"
ANOS = [str(a) for a in range(2016, 2026)]
MK = MercadoBT(data="2020-06-30", rf_real=0.04, pi=0.035, premio=0.05, fonte="teste")

# 10 exercícios com margem, D&A, IR e "outras receitas" que variam — mediana ≠ média, excesso de
# "outras" em um ano. Receita, imobilizado e capex constantes (ver docstring do módulo).
RECEITA, IMOB, CAPEX, DA = 1000.0, 600.0, 80.0, 50.0
EBIT = [150, 170, 120, 200, 210, 90, 160, 180, 140, 175]
OUTRAS = [10, 12, 8, 90, 11, 9, 10, 13, 12, 10]            # 2019 tem excesso (não recorrente)
TAXA = [0.30, 0.28, 0.33, 0.25, 0.27, 0.20, 0.22, 0.34, 0.33, 0.32]   # mediana dos 5 últimos (0,32) ≠ dos 3 últimos (0,33)


def _conta(k: int, taxa: float | None = None) -> dict:
    ebit = float(EBIT[k])
    t = TAXA[k] if taxa is None else taxa
    return {"receita": RECEITA, "ebit": ebit, "lair": ebit, "ir": -t * ebit, "lucro": (1 - t) * ebit,
            "imobilizado": IMOB, "outras_receitas_op": float(OUTRAS[k]), "pl": 800.0,
            "nao_controladores": 0.0, "emprest_lp": 0.0, "caixa": 0.0, "ac": 300.0, "pc": 200.0}


def _mesa(monkeypatch: pytest.MonkeyPatch, taxa=None, anos_com_taxa=None):
    """Registra a empresa sintética na mesa e achata o IPCA em 1,0. Devolve (módulo, Industrial)."""
    import motor_nao_financeiras as mesa
    anual = {}
    for k, a in enumerate(ANOS):
        t = taxa if anos_com_taxa is None or k in anos_com_taxa else None
        c = _conta(k, t)
        anual[a] = {**c, "da": DA, "capex": CAPEX}
        if anos_com_taxa is not None and k not in anos_com_taxa:
            anual[a]["lair"] = 0.0                                   # fora da amostra do imposto
    ultimo = dict(anual[ANOS[-1]])
    monkeypatch.setitem(mesa.CVM, TK, {"anual": anual, "ltm": ultimo, "ltm_ref": "2T26"})
    monkeypatch.setattr(mesa, "DEFLATOR", {a: 1.0 for a in ANOS})
    monkeypatch.setattr(mesa, "deflator_ltm", lambda ref: 1.0)
    monkeypatch.setattr(mesa, "fator_entre", lambda de, para: 1.0)
    emp = mesa.Industrial(ticker=TK, nome="sintética", perfil="servicos", preco=10.0, n_acoes=100_000.0)
    return mesa, emp


def _reduzido(taxa=None, anos_com_taxa=None):
    anos = []
    for k, a in enumerate(ANOS):
        t = taxa if anos_com_taxa is None or k in anos_com_taxa else None
        c = _conta(k, t)
        if anos_com_taxa is not None and k not in anos_com_taxa:
            c["lair"] = 0.0
        anos.append(Ano(dt_refer=f"{a}-12-31", ano=int(a), contas=c, da=DA, capex=CAPEX,
                        dividendos=0.0, arrendamento=0.0, real=1.0))
    return reduzido_nf.premissas(_ins(tuple(anos), perfil="servicos"))


def test_margem_receita_e_manutencao_coincidem(monkeypatch: pytest.MonkeyPatch) -> None:
    mesa, emp = _mesa(monkeypatch)
    op = mesa.premissas_operacionais(emp)
    p = _reduzido()
    assert p["margem"] == pytest.approx(op["m50"], rel=1e-12)
    assert p["receita_meio"] == pytest.approx(op["receita_meio"], rel=1e-12)
    # D&A 50 < capex 80 com receita parada: o ajuste só penaliza e vale (50 − 80)/1000 nos dois
    assert p["ajuste_manut"] == pytest.approx(op["ajuste_manut"], rel=1e-12)
    assert op["ajuste_manut"] == pytest.approx(-0.03)


def test_aliquota_coincide_quando_a_mediana_esta_na_faixa_normal(monkeypatch: pytest.MonkeyPatch) -> None:
    mesa, emp = _mesa(monkeypatch)
    esperado, regra = mesa.aliquota_regra(emp)
    assert regra == "mediana"
    assert _reduzido()["aliquota"] == pytest.approx(esperado, rel=1e-12)


def test_excesso_de_outras_receitas_e_retirado_nos_dois(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sem o ajuste de 'outras' a margem mediana seria outra: prende que os dois o aplicam."""
    mesa, emp = _mesa(monkeypatch)
    com = mesa.premissas_operacionais(emp)["m50"]
    sem = sorted(e / RECEITA for e in EBIT)
    sem = (sem[4] + sem[5]) / 2
    assert com != pytest.approx(sem, rel=1e-6), "premissa do teste: o excesso de 2019 mexe na mediana"
    assert _reduzido()["margem"] == pytest.approx(com, rel=1e-12)


def test_divergencias_declaradas_aliquota_v23(monkeypatch: pytest.MonkeyPatch) -> None:
    """A alíquota do reduzido NÃO acompanhou a v2.3 da mesa — fixado, não corrigido.

    Mesa (v2.3): mediana abaixo de 15% sem origem permanente declarada → 34%; menos de 3 anos
    válidos → 34%. Reduzido: piso de 15% e mediana com 1 ano que seja. O backtest está parado e a
    trava anti-calibração (fatia 12) só admite correção do reduzido por prova sintética — por isso
    o teste prende o comportamento atual dos dois lados. Se este teste falhar, alguém mexeu em um
    lado: decidir se o outro acompanha e atualizar o par, em PROJECT_BRIEF e no diário.
    """
    # (a) taxa efetiva de 10% em todos os anos
    mesa, emp = _mesa(monkeypatch, taxa=0.10)
    assert mesa.aliquota_regra(emp) == (0.34, "sem_origem")
    assert _reduzido(taxa=0.10)["aliquota"] == pytest.approx(0.15)
    # (b) só 2 anos com imposto utilizável (< MINIMO_ANOS_ALIQUOTA)
    mesa, emp = _mesa(monkeypatch, taxa=0.30, anos_com_taxa={8, 9})
    assert mesa.aliquota_regra(emp) == (0.34, "sem_dado")
    assert _reduzido(taxa=0.30, anos_com_taxa={8, 9})["aliquota"] == pytest.approx(0.30)


def test_divergencias_declaradas_receita_de_meio_e_capex(monkeypatch: pytest.MonkeyPatch) -> None:
    """Receita que cresce: a mesa usa a média dos 3 últimos exercícios; o reduzido, a mediana da janela.

    O ajuste de manutenção também difere: a mesa abate o capex de crescimento (Greenwald, Δreceita de
    5 anos ÷ 5), então com a receita crescendo o capex vira ~0 e o ajuste some; o reduzido usa
    `min(0, D&A/receita − capex/receita)` com o capex TOTAL (o Greenwald dele só entra no owner earnings).
    Fixado para a mudança em um dos lados não passar calada (adversário, 09/10).
    """
    mesa, emp = _mesa(monkeypatch)
    a = mesa.CVM[TK]["anual"]
    for k, ano in enumerate(ANOS):
        a[ano]["receita"] = 1000.0 + 100.0 * k
    mesa.CVM[TK]["ltm"] = dict(a[ANOS[-1]])
    op = mesa.premissas_operacionais(emp)
    anos = tuple(Ano(dt_refer=f"{ano}-12-31", ano=int(ano), contas={**_conta(k), "receita": 1000.0 + 100.0 * k},
                     da=DA, capex=CAPEX, dividendos=0.0, arrendamento=0.0, real=1.0)
                 for k, ano in enumerate(ANOS))
    p = reduzido_nf.premissas(_ins(anos, perfil="servicos"))
    assert op["receita_meio"] == pytest.approx((1700 + 1800 + 1900) / 3)
    assert p["receita_meio"] == pytest.approx(1450.0)               # mediana de 1000..1900
    assert p["receita_meio"] != pytest.approx(op["receita_meio"])
    assert op["ajuste_manut"] == 0.0                                 # Greenwald tira o capex de crescimento
    assert p["ajuste_manut"] == pytest.approx(-0.0207, abs=1e-4)     # capex total vs D&A, medianas por receita
