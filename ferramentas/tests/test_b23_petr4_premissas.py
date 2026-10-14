"""B23 (AUD-64): a ficha da PETR4 mostra numa tabela só o P/C de cada premissa que move a palavra."""
import math

import pytest

import golden

G = pytest.importorskip("gerar_pdf_lote5")


@pytest.fixture(scope="module")
def petr4():
    e = next(e for e in G.EMPRESAS if e.ticker == "PETR4")
    r = G.avaliar(e, G.MK)
    return e, r, G.extras(e, r)


def test_tabela_tem_todas_as_premissas_do_aud64_e_a_base_e_o_golden(petr4):
    e, r, x = petr4
    nomes = [n for n, _, _ in x["pc_premissa"]]
    for chave in ("Caso base", "controlador", "IFRS 16", "outras", "regra EBIT", "Brent", "atuarial", "Abandono", "Capex LTM"):
        assert any(chave in n for n in nomes), chave
    base = x["pc_premissa"][0]
    assert base[2] == pytest.approx(golden.carregar()["PETR4"]["pc"], abs=0.005)
    assert all(c > 0 and q is not None and math.isfinite(q) for _, c, q in x["pc_premissa"])


def test_ficha_monta_com_a_tabela(petr4):
    e, r, _ = petr4
    story = []
    G.ficha(e, r, 1, story)
    assert any("P/C por premissa" in str(getattr(f, "_cellvalues", "")) for f in story)
