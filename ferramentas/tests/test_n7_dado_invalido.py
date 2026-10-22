"""N7 (QA 21/10/2026): NaN, ±inf, None, 0 e negativo viram recusa explícita nos motores — nunca palavra em silêncio."""
import math

import pytest

import carimbos
import motor_financeiras as F
import motor_nao_financeiras as M

NAN, INF = float("nan"), float("inf")


@pytest.mark.parametrize("pc", [NAN, None, 0, 0.0, -1, -INF])
def test_palavra_recusa_pc_invalido(pc):
    with pytest.raises(ValueError):
        F.palavra(pc)


def test_palavra_mais_inf_continua_cara():            # central ≤ 0 → pc = inf (o motor força NÃO CONCLUSIVO depois)
    assert F.palavra(INF) == "CARA"


@pytest.mark.parametrize("pc", [NAN, None, 0, -1, -INF])
def test_nota_preco_recusa_pc_invalido(pc):
    with pytest.raises(ValueError):
        F.nota_preco(pc)


@pytest.mark.parametrize("central", [NAN, INF, -INF, None, 0, -1])
def test_precos_de_referencia_sem_central_valido_nao_tem_preco(central):
    p = F.precos_de_referencia(central)
    assert p["compra"] is None and p["compra_parcial"] is None and p["saida"] is None


def _r(**kw):
    r = dict(palavra="BARATA", central=10.0, pc=0.5, dispersao=1.2, notas=dict(qualidade=9.0, solidez=8.0))
    r.update({k: v for k, v in kw.items() if k != "notas"})
    r["notas"] = {**r["notas"], **kw.get("notas", {})}
    return r


def test_entrada_parcial_caso_valido_continua_elegivel():
    assert F.entrada_parcial(_r()) == (True, [])


@pytest.mark.parametrize("campo", ["pc", "dispersao", "central"])
@pytest.mark.parametrize("ruim", [NAN, None, INF])
def test_entrada_parcial_recusa_campo_invalido(campo, ruim):
    ok, motivos = F.entrada_parcial(_r(**{campo: ruim}))
    assert ok is False and motivos and "inválido" in motivos[0]


@pytest.mark.parametrize("nota", ["qualidade", "solidez"])
@pytest.mark.parametrize("ruim", [NAN, None])
def test_entrada_parcial_recusa_nota_invalida(nota, ruim):
    ok, motivos = F.entrada_parcial(_r(notas={nota: ruim}))
    assert ok is False and "inválido" in motivos[0]


@pytest.mark.parametrize("desc", [NAN, INF, None, -0.1, 1.01])
def test_descontar_recusa_desconto_fora_de_0_1(desc):
    with pytest.raises(ValueError):
        F.descontar({"a": 10.0}, desc)


def test_descontar_bordas_validas():
    assert F.descontar({"a": 10.0, "b": -2.0}, 0) == {"a": 10.0, "b": -2.0}
    assert F.descontar({"a": 10.0}, 1) == {"a": 0.0}


def _q(**kw):
    q = dict(moat=3, gestao=3, controlador=3, ciclo=3, fisher=3)
    q.update(kw)
    return q


@pytest.mark.parametrize("ruim", [NAN, INF, None, -0.1, 5.1, 10])
@pytest.mark.parametrize("chave", F.CHAVES_QUAL)
def test_media_qualitativa_recusa_nota_fora_de_0_5(chave, ruim):
    with pytest.raises(ValueError):
        F.media_qualitativa(_q(**{chave: ruim}))


def test_media_qualitativa_bordas_validas():
    assert F.media_qualitativa(_q(moat=0, gestao=5, controlador=0, ciclo=5, fisher=0)) == pytest.approx(2.0)
    assert F.media_qualitativa({}) == 2.5


@pytest.mark.parametrize("anc", [{"a": 1.0, "b": NAN, "c": 3.0}, {"a": INF}, {"a": None}, {}])
def test_central_de_recusa_ancora_invalida(anc):
    with pytest.raises(ValueError):
        M.central_de(anc)


def test_central_de_nao_depende_da_ordem_quando_valido():
    assert M.central_de({"a": 3.0, "b": 1.0, "c": 2.0})[0] == M.central_de({"c": 2.0, "a": 3.0, "b": 1.0})[0] == 2.0


@pytest.mark.parametrize("serie,acima", [(8, 9), (10, 11), (0, 1), (10, -1), (-1, 0)])
def test_qualifica_saida_recusa_mais_anos_acima_que_a_serie(serie, acima):
    with pytest.raises(ValueError):
        M.qualifica_saida(serie, acima, 9.0)


def test_qualifica_saida_caso_valido():
    assert M.qualifica_saida(10, 8, 8.0) is True
    assert M.qualifica_saida(10, 7, 9.0) is False


def test_carimbos_de_ignora_espaco_e_caixa():
    assert carimbos.de(" unip6 ") == carimbos.de("UNIP6") != []


def test_relatorio_caso_normaliza_ticker():
    from relatorio import caso as c
    with pytest.raises(KeyError) as e:               # ticker inexistente, mas já normalizado na mensagem
        c.caso("  xxxx3 ")
    assert "XXXX3" in str(e.value)
