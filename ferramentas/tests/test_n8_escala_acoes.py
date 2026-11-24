"""N8 (QA 21/10): a CVM informa a composição do capital em MIL em alguns formulários (`cvm_series.json`: RANI3, KEPL3, CSMG3,
TAEE11, CMIG4, VBBR3, ABEV3-DFP, ITSA4). `coletar_cvm.acoes_em_circulacao` devolve o número cru; quem lê precisa reescalar.
Estes testes fixam os leitores que chegam a valor por ação."""
import json
import pathlib

import pytest

SERIES = pathlib.Path(__file__).resolve().parents[1] / "dados" / "cvm_series.json"
pytestmark = pytest.mark.skipif(not SERIES.exists(), reason="sem dados/cvm_series.json")


@pytest.mark.parametrize("tk,minimo", [("RANI3", 1e8), ("KEPL3", 1e8), ("VBBR3", 1e9)])
def test_lote3_reescala_as_acoes_em_mil_para_unidades(tk, minimo):
    import lote3_agro
    bruto = json.loads(SERIES.read_text(encoding="utf-8"))[tk]["anual"]["2025"]["acoes"]
    assert bruto < 1e7                                   # o cru está em mil
    assert lote3_agro.acoes(tk) == pytest.approx(bruto * 1000) and lote3_agro.acoes(tk) > minimo


def test_follow_on_da_isae4_le_acoes_em_unidades():
    """Único leitor de `ltm['acoes']` que vira valor por ação (`lote2_energia.follow_on`): se o formulário da ISAE4 passar a vir
    em mil, o VPA com follow-on estoura 1.000× — este teste avisa antes."""
    import lote2_energia
    from ltm import ltm_de
    assert ltm_de(lote2_energia.CVM["ISAE4"])["acoes"] > 1e8


def test_taee11_nao_usa_acoes_da_cvm_no_valor():
    """TAEE11 (1.033.497 mil = 1,033 bi de ações = 344,5 mi units) é financeira do motor por VPA/LPA da StatusInvest: nenhum
    campo `acoes` da CVM entra no preço dela. Se entrar um dia (follow-on), reescalar antes."""
    import lote2_energia
    assert "TAEE11" not in lote2_energia.FOLLOW_ON


def test_reescalar_acoes_nao_multiplica_small_cap_em_unidades_e_converte_ambev_em_milhares():
    """F1-03: o limiar antigo `n < 1e8` em lote4 multiplicava por 1000 qualquer empresa com 20M–99M ações já em unidades;
    `reescalar_acoes` preserva 50M em unidades e converte 15,45M (Ambev em milhares) para 15,45B."""
    from motor_nao_financeiras import reescalar_acoes

    # Empresa com 50 milhões de ações já em unidades (ex.: small/mid cap entre 20M e 100M)
    assert reescalar_acoes(50_000_000.0) == 50_000_000.0
    # Ambev no ITR: 15.452.795 (em milhares) -> 15.452.795.000 unidades
    assert reescalar_acoes(15_452_795.0) == 15_452_795_000.0
    # Com referência explícita do FRE (ex.: small cap com 18M ações em unidades vs referência FRE de 18,5M)
    assert reescalar_acoes(18_000_000.0, ref=18_500_000.0) == 18_000_000.0
    # Com referência explícita do FRE quando o ITR vem em milhares (18.000 mil vs 18,5M no FRE)
    assert reescalar_acoes(18_000.0, ref=18_500_000.0) == 18_000_000.0
