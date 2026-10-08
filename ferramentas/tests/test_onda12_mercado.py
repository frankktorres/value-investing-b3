"""Onda 1.2 da auditoria de 08/10/2026, bloco 1 — convenções de mercado (AUD-78, AUD-06, AUD-72).

Escritos antes da correção: no código antigo `mercado.py` e `mercado_vigente.json` não existiam e o instantâneo não tinha
data do preço, então todos falhavam por ImportError/KeyError.
"""
import datetime as dt
import json
import pathlib

import pytest

import mercado

DADOS = pathlib.Path(__file__).resolve().parent.parent / "dados" / "mercado.json"


@pytest.mark.skipif(not DADOS.exists(), reason="dados/ fica fora do git")
def test_aud78_vigente_confere_com_a_coleta_bruta():
    mv, bruto = mercado.dados(), json.loads(DADOS.read_text(encoding="utf-8"))
    rf = bruto["tesouro_direto_TesouroTransparente"][mv["data"]][mv["rf_chave_mercado_json"]]
    assert rf["data"] == mv["data"]
    assert mv["rf_real"] == pytest.approx(rf["valor"] / 100, abs=1e-12)
    pi = bruto["anbima_ettj_inflacao_implicita"][mv["pi_chave_mercado_json"]]
    assert pi["data"] == mv["data"]
    assert mv["pi"] == pytest.approx(pi["valor"] / 100, abs=0.00005)      # 4 casas, declarado no arquivo


@pytest.mark.skipif(not DADOS.exists(), reason="dados/ fica fora do git")
def test_aud06_rf_e_a_taxa_de_compra_da_manha_e_assim_rotulada():
    mv, bruto = mercado.dados(), json.loads(DADOS.read_text(encoding="utf-8"))
    tipo = bruto["tesouro_direto_TesouroTransparente"][mv["data"]][mv["rf_chave_mercado_json"]]["tipo"]
    assert "Compra Manha" in tipo
    assert "compra da manhã" in mv["rf_tipo"] and "fechamento" not in mv["rf_tipo"]


def test_aud78_hall_triagem_e_dossie_leem_o_mesmo_arquivo():
    import lote1_bancos
    from dossie import base
    from triagem.config import PADRAO
    mv = mercado.vigente()
    assert (lote1_bancos.MK.rf_real, lote1_bancos.MK.pi) == (mv.rf_real, mv.pi)
    assert (PADRAO.rf_real, PADRAO.pi, PADRAO.data_mercado) == (mv.rf_real, mv.pi, mercado.dados()["data"])
    m = base.mercado(mercado.dados()["data"])
    assert (m.rf_real, m.pi) == (mv.rf_real, mv.pi)


def test_aud78_nenhum_literal_de_rf_ou_pi_fora_do_arquivo():
    raiz = pathlib.Path(mercado.__file__).parent
    for nome in ("lote1_bancos.py", "triagem/config.py", "dossie/base.py"):
        txt = (raiz / nome).read_text(encoding="utf-8")
        assert "0.0706" not in txt and "0.0646" not in txt, nome


def test_aud72_aviso_so_acima_de_15_dias():
    assert mercado.idade_dias("2026-10-02", dt.date(2026, 10, 17)) == 15
    assert mercado.aviso_idade("2026-10-02", dt.date(2026, 10, 17)) == ""
    av = mercado.aviso_idade("02/10/2026", dt.date(2026, 10, 18))
    assert "16 dias" in av and "atualizar antes de decidir" in av


def test_aud72_instantaneo_guarda_a_data_do_preco():
    import universo
    item = dict(lote=1, data_preco="02/10/2026",
                r=dict(central=1.0, pc=1.0, palavra="JUSTA", ancoras={"x": 1.0}, notas=dict(geral=5.0)))
    assert universo.instantaneo(item)["data_preco"] == "02/10/2026"
