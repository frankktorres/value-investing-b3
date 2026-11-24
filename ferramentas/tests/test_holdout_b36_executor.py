"""B36: o executor do hold-out é o mesmo método do dossiê (equivalência na ALLD3), não vaza para os registros globais e
classifica cada insumo numa classe só (emenda 8)."""
import json

import pytest

from holdout_b36 import executor as X

ALLD3 = dict(ticker="ALLD3", cnpj="20.247.322/0001-47", cd_cvm=25330, pregao="ALLIED", classe="ON", acoes_por_unit=1,
             tipo="industrial", perfil="servicos", setor="Comércio (Atacado e Varejo)")


def _tem_dados_alld3():
    from dossie import base
    return base.SERIES.exists() and "ALLD3" in json.loads(base.SERIES.read_text(encoding="utf-8"))


@pytest.mark.skipif(not _tem_dados_alld3(), reason="sem séries do dossiê (ZIPs/dados locais)")
def test_equivalencia_alld3_executor_igual_ao_dossie():
    """Prova que o executor não muda o método: mesma ficha, mesmos insumos e mesma data → mesma palavra, P/C e Ke."""
    from dossie import base, gerar
    ref = gerar.calcular("ALLD3", "2026-10-15")["r"]
    ins = gerar.insumos("ALLD3")
    r = X.avaliar_industrial(ALLD3, "2026-10-15", ins, ficha_modulo="dossie.fichas.alld3", series=base.SERIES)
    assert r["palavra"] == ref["palavra"]
    assert r["pc"] == pytest.approx(ref["pc"], rel=1e-12)
    assert r["central"] == pytest.approx(ref["central"], rel=1e-12)
    assert r["ke_nom"] == pytest.approx(ref["ke_nom_emp"], rel=1e-12)


def test_registro_em_memoria_volta_ao_estado_anterior():
    import coletar_cvm
    import proventos_ex
    from dossie import base, gerar
    c = dict(ALLD3, ticker="ZZZZ3", cnpj="00.000.000/0001-00", pregao="ZZZ", classe="PN")
    antes = (dict(gerar.FICHAS), dict(base.CNPJ), dict(base.PREGAO), dict(proventos_ex.PREGAO), dict(proventos_ex.CLASSE),
             dict(coletar_cvm.EMPRESAS), base.SERIES, gerar.insumos)
    with X.registrado(c, "x.y", {"a": 1}):
        assert gerar.FICHAS["ZZZZ3"] == "x.y" and proventos_ex.CLASSE["ZZZZ3"] == "PN" and base.SERIES == X.SERIES
        assert gerar.insumos("ZZZZ3") == {"a": 1}
    depois = (dict(gerar.FICHAS), dict(base.CNPJ), dict(base.PREGAO), dict(proventos_ex.PREGAO), dict(proventos_ex.CLASSE),
              dict(coletar_cvm.EMPRESAS), base.SERIES, gerar.insumos)
    assert depois == antes


def test_tipo_e_perfil_pelo_setor_da_fca():
    assert X.tipo_do_setor("Bancos") == "banco"
    assert X.tipo_do_setor("Emp. Adm. Part. - Energia Elétrica") == "utility"
    assert X.tipo_do_setor("Saneamento, Serv. Água e Gás") == "utility"
    assert X.tipo_do_setor("Alimentos") == "industrial"
    assert X.perfil_do_setor("Emp. Adm. Part. - Metalurgia e Siderurgia") == "ciclica"
    assert X.perfil_do_setor("Agricultura (Açúcar, Álcool e Cana)") == "ciclica"
    assert X.perfil_do_setor("Comércio (Atacado e Varejo)") == "servicos"


def test_classes_somam_o_total_e_seguem_a_origem():
    c = dict(ALLD3)
    ins = {"ma_ruim": {"valor": False, "fonte": "DFP", "nota_fonte": "A"},
           "interferencias": {"valor": 0, "fonte": "", "nota_fonte": "A"},          # sem fonte: não vale → vazio
           "fisher": {"respostas": ["sim", "nao"] + ["sem"] * 13},
           "desconto_controlador": {"tipo": "zero", "razao": "SEM_RAZAO"}}
    cl = dict(X.classes(c, ins, {"tag_fre": 1.0, "r1_auto": False}))
    n = X.contagem(list(cl.items()))
    assert n["automatico"] + n["pesquisa"] + n["vazio"] == n["total"] == len(cl)
    assert cl["ma_ruim"] == "pesquisa" and cl["interferencias"] == "vazio" and cl["tag_along"] == "automatico"
    assert cl["fisher 1"] == "pesquisa" and cl["fisher 3"] == "vazio" and cl["desconto_controlador"] == "vazio"
    assert cl["r1_retido (Q4 da triagem)"] == "vazio"
    banco = dict(c, tipo="banco")
    cb = dict(X.classes(banco, {}))
    assert cb["prudencial cet1"] == "vazio" and cb["payout"] == "automatico" and cb["nota moat"] == "vazio"
