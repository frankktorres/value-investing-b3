"""Matriz de rastreabilidade (docs/VALIDACAO.md §3): regra do 01 sem teste e sem lacuna declarada = falha; a catraca de
lacunas só cai; o .md gerado bate com a matriz."""
from oraculo import rastreabilidade as R
from oraculo.matriz import LACUNAS_MAX, REGRAS


def test_matriz_sem_problemas():
    assert R.verificar(REGRAS, LACUNAS_MAX) == []


def test_md_gerado_esta_atualizado():
    assert R.SAIDA.read_text(encoding="utf-8").splitlines() == R.gerar_md(REGRAS).splitlines()


# ---------------------------------------------------------------- o verificador pega o que deve pegar (camada 1 do próprio oráculo)
def _r(**kw):
    base = dict(id="X1", sec="§9", linha=1, regra="r", tipo="calculo", funcoes=[], testes=[], camada=1)
    base.update(kw)
    return base


def test_regra_calculavel_sem_teste_e_sem_lacuna_falha():
    probs = R.verificar([_r()], 0, secoes=["§9"])
    assert any("sem teste e sem lacuna" in p for p in probs)


def test_lacuna_precisa_da_fase_e_entra_na_catraca():
    assert any("sem a fase" in p for p in R.verificar([_r(lacuna="um dia")], 1, secoes=["§9"]))
    assert R.verificar([_r(lacuna="Fase 2: propriedade")], 1, secoes=["§9"]) == []
    assert any("subiu" in p for p in R.verificar([_r(lacuna="Fase 2: x")], 0, secoes=["§9"]))
    assert any("caiu" in p for p in R.verificar([_r(lacuna="Fase 2: x")], 2, secoes=["§9"]))


def test_secao_do_01_sem_linha_falha():
    assert any("§4: seção do 01 sem" in p for p in R.verificar([_r(tipo="texto")], 0, secoes=["§9", "§4"]))


def test_funcao_e_teste_inexistentes_falham():
    probs = R.verificar([_r(funcoes=["motor_financeiras.nao_existe"],
                            testes=["tests/test_regressao.py::test_nao_existe", "tests/nao_existe.py::t"])], 0, secoes=["§9"])
    assert any("função inexistente" in p for p in probs)
    assert any("teste inexistente" in p for p in probs)
    assert any("arquivo de teste inexistente" in p for p in probs)


def test_existentes_passam():
    probs = R.verificar([_r(funcoes=["motor_financeiras.palavra"],
                            testes=["tests/test_oraculo_rastreabilidade.py::test_existentes_passam"])], 0, secoes=["§9"])
    assert probs == []


def test_secoes_lidas_do_01_incluem_subsecoes():
    secs = R.secoes_da_doutrina()
    assert "§4" in secs and "§4.1" in secs and "§11.3" in secs
    assert all(s.startswith("§") for s in secs)
