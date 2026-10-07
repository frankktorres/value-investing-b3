"""Regressão dos dossiês (Etapa 5): o veredito recalculado bate com o JSON salvo em `dossie/vereditos/` e a normalização
do ciclo da CMIN3 é coerente. Mudança no motor, na base ou numa ficha que mexa num dossiê aprovado falha aqui."""
import json
import math
import pathlib

import pytest

from dossie import gerar
from dossie.fichas import cmin3

VEREDITOS = pathlib.Path(gerar.__file__).resolve().parent / "vereditos"


@pytest.mark.parametrize("tk", ["BLAU3", "CMIN3", "HYPE3"])
def test_veredito_salvo_reproduz(tk):
    salvo = json.loads((VEREDITOS / f"{tk}-2026-10-02.json").read_text(encoding="utf-8"))
    v = gerar.veredito(gerar.calcular(tk))
    for k in ("central", "pc", "desc_controlador", "media_regra11"):
        assert v[k] == pytest.approx(salvo[k], abs=1e-4), k
    for k in ("palavra", "palavra_regua", "notas_regra11", "discricionario"):
        assert v[k] == salvo[k], k


def test_dossie_de_ticker_do_hall_nao_vaza_para_o_lote():
    # HYPE3 está no Lote 4: o dossiê troca SI["HYPE3"] (proventos da B3) só dentro do calcular; o hall continua igual
    from motor_nao_financeiras import CVM, SI
    si, cvm = SI["HYPE3"], CVM["HYPE3"]
    gerar.calcular("HYPE3")
    assert SI["HYPE3"] is si and CVM["HYPE3"] is cvm
    assert "indicadores" in SI["HYPE3"]          # o do hall (StatusInvest), que o pl_hist do lote lê


def test_ticker_fora_do_hall_sai_da_memoria():
    from motor_nao_financeiras import CVM, SI
    gerar.calcular("BLAU3")
    assert "BLAU3" not in SI and "BLAU3" not in CVM


def test_diluicao_so_desfaz_evento_dentro_da_janela():
    from dossie import evidencia
    from motor_nao_financeiras import CVM
    CVM["XPTO3"] = {"anual": {"2020": {"acoes": 100e6}, "2025": {"acoes": 260e6}}}
    try:
        antes = [{"aprovacao": "2009-12-30", "multiplicador": 2.0}]        # anterior à janela: já está nas duas pontas
        dentro = [{"aprovacao": "2023-04-01", "multiplicador": 2.0}]       # dentro: desfeito só no fim
        c0, t0 = evidencia.diluicao("XPTO3", ["2020", "2025"], antes, "2020")
        c1, _ = evidencia.diluicao("XPTO3", ["2020", "2025"], dentro, "2020")
        assert c0 == pytest.approx(2.6 ** 0.2 - 1) and "100.0 → 260.0" in t0.replace(",", "")
        assert c1 == pytest.approx(1.3 ** 0.2 - 1)
    finally:
        CVM.pop("XPTO3")


def test_minerio_12m_e_fatores():
    m = cmin3.minerio()
    assert m["fator"] == pytest.approx(m["meio_rs_real"] / m["ltm_rs"])
    assert set(m["fator_preco"]) == set(cmin3.ANOS)
    assert all(math.isfinite(f) and f > 0 for f in m["fator_preco"].values())
    # o ano de preço igual ao meio teria fator 1: o produto do fator pelo preço do ano devolve o meio
    for a, f in m["fator_preco"].items():
        assert f * m["anual"].loc[int(a), "rs_real"] == pytest.approx(m["meio_rs_real"])


def test_normalizacao_chamada_sozinha_e_linha_adotada_igual_ao_central():
    dc = gerar.insumos("CMIN3")["desconto_controlador"]
    n = cmin3.normalizacao(dc)
    adotado = next(v for k, v in n["sensibilidade"].items() if k.startswith("c "))
    salvo = json.loads((VEREDITOS / "CMIN3-2026-10-02.json").read_text(encoding="utf-8"))
    assert adotado["central"] == pytest.approx(salvo["central"], abs=1e-4)
