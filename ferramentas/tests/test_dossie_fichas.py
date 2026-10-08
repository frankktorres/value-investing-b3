"""Regressão dos dossiês (Etapa 5): o veredito recalculado bate com o JSON salvo em `dossie/vereditos/` e a normalização
do ciclo da CMIN3 é coerente. Mudança no motor, na base ou numa ficha que mexa num dossiê aprovado falha aqui."""
import json
import math
import pathlib

import pytest

from dossie import gerar
from dossie.fichas import cmin3

VEREDITOS = pathlib.Path(gerar.__file__).resolve().parent / "vereditos"
# Vereditos de uma doutrina anterior que o motor atual NÃO reproduz por decisão declarada — ficam no disco e no registro
# (append-only) como histórico; o veredito novo é de outra data. Doutrina v2.3 (07/10/2026), 09-diario.
SUPERADOS = {
    "HYPE3-2026-10-02": "v2.2: alíquota no piso de 15% para sempre; v2.3 = fase até 2030 e 34% depois (HYPE3-2026-10-06)",
    "CMIN3-2026-10-02": "v2.2: passivo de contrato fora da DL; v2.3 = financeiro na DL, a trava do ROIC zera o g do DCF e a "
                        "dispersão cai abaixo de 3x (CMIN3-2026-10-06)",
}
ARQUIVOS = sorted(p.stem for p in VEREDITOS.glob("*.json"))
# Onda 1.1 da auditoria (08/10/2026): receita de meio, OE e DPA em R$ de hoje (AUD-01/16) e provento já ex na dívida (AUD-02)
# mudam o central destes dossiês. O registro é append-only (veredito novo = data nova) e ainda não há rodada de data nova:
# o JSON antigo fica no disco e o recálculo na MESMA data é fixado aqui, para a regressão continuar valendo. Ver 09-diario.
METODO_ONDA_1_1 = {
    # Onda 1.2 (08/10/2026): Kd sintético (AUD-07), Ke pela alavancagem e pesos no ponto fixo (AUD-12/13), trava do §9 (AUD-08)
    "BLAU3-2026-10-02": dict(central=8.2998, pc=1.3036, palavra="NÃO CONCLUSIVO"),  # 1.1: 8,798
    "HYPE3-2026-10-06": dict(central=16.9224, pc=1.5955, palavra="CARA"),           # 1.1: 18,3522
    "LEVE3-2026-10-06": dict(central=38.3732, pc=0.9525, palavra="NÃO CONCLUSIVO"), # 1.1: 42,5717 RADAR; agora JUSTA com trava falha
    "CMIN3-2026-10-06": dict(central=3.3668, pc=1.4673, palavra="CARA"),            # salvo 3,6329
}


@pytest.mark.parametrize("nome", sorted(METODO_ONDA_1_1))
def test_veredito_refeito_pela_onda_1_1(nome):
    salvo = json.loads((VEREDITOS / f"{nome}.json").read_text(encoding="utf-8"))
    v = gerar.veredito(gerar.calcular(salvo["ticker"], salvo["data_preco"]))
    novo = METODO_ONDA_1_1[nome]
    assert v["central"] == pytest.approx(novo["central"], abs=1e-3) and v["pc"] == pytest.approx(novo["pc"], abs=1e-3)
    assert v["palavra"] == novo["palavra"]
    assert v["central"] != pytest.approx(salvo["central"], abs=1e-3)      # o JSON antigo continua sendo o do método antigo


@pytest.mark.parametrize("nome", [n for n in ARQUIVOS if n not in SUPERADOS and n not in METODO_ONDA_1_1])
def test_veredito_salvo_reproduz(nome):
    salvo = json.loads((VEREDITOS / f"{nome}.json").read_text(encoding="utf-8"))
    v = gerar.veredito(gerar.calcular(salvo["ticker"], salvo["data_preco"]))
    for k in ("central", "pc", "desc_controlador", "media_regra11", "preco"):
        assert v[k] == pytest.approx(salvo[k], abs=1e-4), k
    for k in ("palavra", "palavra_regua", "notas_regra11", "discricionario"):
        assert v[k] == salvo[k], k


def test_veredito_superado_tem_sucessor_mais_novo_e_continua_no_disco():
    for nome in SUPERADOS:
        tk, data = nome.split("-", 1)
        assert nome in ARQUIVOS, nome
        assert any(n.startswith(tk + "-") and n.split("-", 1)[1] > data for n in ARQUIVOS if n not in SUPERADOS), nome


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
    from dossie import base
    dc = gerar.insumos("CMIN3")["desconto_controlador"]
    atual = max(n for n in ARQUIVOS if n.startswith("CMIN3-") and n not in SUPERADOS)
    salvo = json.loads((VEREDITOS / f"{atual}.json").read_text(encoding="utf-8"))
    with base.na_data(salvo["data_preco"]):          # a sensibilidade usa o mercado e o preço da data do veredito
        n = cmin3.normalizacao(dc)
    adotado = next(v for k, v in n["sensibilidade"].items() if k.startswith("c "))
    assert adotado["central"] == pytest.approx(METODO_ONDA_1_1.get(atual, salvo)["central"], abs=1e-3)
