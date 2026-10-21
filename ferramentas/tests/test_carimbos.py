"""Armadilha registrada bloqueia a exceção da 1ª parcela a 0,80× em todo lugar que a calcula (D2, 21/10/2026)."""
import pathlib
import types

import pytest

import carimbos
import golden
from gerar_pdf_lote1 import texto_entrada_parcial
from motor_financeiras import entrada_parcial


def _r_elegivel():
    return {"palavra": "JUSTA", "central": 10.0, "notas": {"qualidade": 9.0, "solidez": 8.0}, "dispersao": 1.2,
            "pc": 0.75, "compra_parcial": 8.0}


def test_todo_carimbo_tem_texto_e_fonte_e_ticker_conhecido():
    hall = set(golden.carregar())
    for tk, lista in carimbos.CARIMBOS.items():
        assert tk in hall, tk
        assert lista and all(c.strip() and f.strip() for c, f in lista), tk


def test_ticker_sem_carimbo_segue_elegivel():
    assert carimbos.de("GGBR4") == []          # §7: único com zero das quatro
    assert entrada_parcial(_r_elegivel(), False, carimbos.de("GGBR4"))[0]


def test_carimbo_registrado_bloqueia_a_excecao():
    ok, motivos = entrada_parcial(_r_elegivel(), False, carimbos.de("UNIP6"))
    assert not ok and any(m.startswith("armadilha: dividendo não coberto") for m in motivos)


def test_pdf_dos_lotes_usa_o_registro_quando_a_ficha_nao_passa_armadilha():
    emp = types.SimpleNamespace(ticker="EGIE3", fora_circulo=False)
    txt = texto_entrada_parcial(_r_elegivel(), emp)
    assert txt.startswith("não se aplica") and "lucro não recorrente" in txt
    limpo = texto_entrada_parcial(_r_elegivel(), types.SimpleNamespace(ticker="GGBR4", fora_circulo=False))
    assert limpo.startswith("aplicável")
    # lista explícita (lote 6) substitui o registro, inclusive a vazia
    assert texto_entrada_parcial(_r_elegivel(), emp, []).startswith("aplicável")


@pytest.mark.skipif(not (pathlib.Path(__file__).resolve().parents[1] / "dados" / "cvm_series.json").exists(),
                    reason="dados/cvm_series.json fora do disco (dados brutos fora do git)")
def test_relatorio_real_da_unip6_recusa_pela_armadilha():
    from relatorio.montar import montar
    textos = [t for s in montar("UNIP6").secoes for t in s.texto]
    linha = next(t for t in textos if t.startswith("Exceção da 1ª parcela"))
    assert "não —" in linha and "armadilha: dividendo não coberto" in linha
