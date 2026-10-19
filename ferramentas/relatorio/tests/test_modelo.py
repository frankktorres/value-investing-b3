"""Nota de fonte: a pior dos insumos, nunca promovida; sem origem = sem fonte."""
import pytest

from relatorio.modelo import Numero, Origem, Relatorio, Secao, decide, pior
from relatorio.render_md import fmt, render

A = Origem("CVM DFP/ITR", "A", "CVM, DFP")
B = Origem("RI", "B")
C = Origem("StatusInvest", "C")
X = Origem("arbitrado", "—")


def test_pior_e_a_nota_mais_fraca():
    assert pior([A, B]) == "B"
    assert pior([A, C, B]) == "C"
    assert pior([A, X, C]) == "—"


def test_sem_origem_nao_vira_a():
    assert pior([]) == "—"
    assert Numero("x", 1.0).nota == "—"


def test_derivado_nao_e_promovido():
    n = Numero("central", 10.0, "R$", (A, A, C))
    assert n.nota == "C" and not decide(n.nota)


@pytest.mark.parametrize("nota", ["D", "a", "", "A+"])
def test_nota_invalida_falha(nota):
    with pytest.raises(ValueError):
        Origem("x", nota)


def test_origem_sem_fonte_falha():
    with pytest.raises(ValueError):
        Origem("  ", "A")


def test_fonte_sem_repeticao_na_ordem():
    assert Numero("x", 1.0, "", (A, C, A)).fonte == "CVM DFP/ITR; StatusInvest"


def test_fmt():
    assert fmt(1234.5, "R$") == "R$ 1.234,50"
    assert fmt(0.1234, "%") == "12,3%"
    assert fmt(1.731, "x") == "1,73×"
    assert fmt(None, "R$") == "—"


def test_render_marca_nota_fraca_e_traz_legenda():
    s = Secao("Preço", [Numero("DCF", 10.0, "R$", (A,), "central"), Numero("Bazin", 8.0, "R$", (C,), "informativo"),
                        Numero("EPV", None, "", (), "informativo", "não se aplica")])
    md = render(Relatorio("TST3", "Teste", "2026-10-02", "dossiê", "JUSTA", [s], ["aviso um"]))
    assert "| DCF | R$ 10,00 | entra no central | A | CVM DFP/ITR |" in md
    assert "| Bazin | R$ 8,00 | informativo | **C** | StatusInvest |" in md
    assert "| EPV | — | informativo |  | não se aplica |" in md
    assert "- aviso um" in md
    assert "| CVM DFP/ITR | A | CVM, DFP |" in md
