"""Regressão dos dossiês (Etapa 5): o veredito recalculado bate com o JSON salvo em `dossie/vereditos/` e a normalização
do ciclo da CMIN3 é coerente. Mudança no motor, na base ou numa ficha que mexa num dossiê aprovado falha aqui."""
import json
import math
import pathlib

import pytest
from dados_opcionais import TEM_RAW, requer_suplemento_b3

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
# MÉTODO VIGENTE NA DATA DO VEREDITO. O JSON salvo é o registro (append-only) do método e do dado de quando foi gravado; o
# recálculo na MESMA data, pelo método vigente, é fixado aqui — mudança de motor que mexa num dossiê aprovado falha nesta tabela.
# Histórico: Onda 1.1/1.2 (08/10, AUD-01/02/07/12/13/08) e Onda 3 (10/10, AUD-15) — ver 09-diario.
# 24/11/2026 (B34): (1) o recálculo passou a ser POINT-IN-TIME (`dossie.base.na_data`): LTM já publicado na data (Res. CVM 80,
# art. 31, II) e IPCA até o mês D − 2 — com o motor de antes do H2 ele reproduz exatamente os valores salvos/fixados de FESA4,
# SHUL4, VLID3, BLAU3, HYPE3-10-06 e LEVE3; (2) H2 (doutrina v2.7: D/E a mercado, sem ponto fixo) muda todos os centrais;
# (3) dado, não método: CMIN3 — macro externa (FRED minério/PTAX) revisada depois da data, sem vintage no repo (com a macro de
# antes, 3,3668 volta exato); ALLD3 — dois JCP aprovados em 29/09 que a API da B3 só listou depois de 19/10 (com o arquivo de
# antes, 14,9142 volta exato). ALLD3 BARATA → RADAR no recálculo (dispersão 2,17 > 1,8, §11.3) — decisão do Frank no 09.
METODO_VIGENTE = {
    "ALLD3-2026-10-15": dict(central=15.9743, pc=0.3944, palavra="RADAR"),          # salvo 14,9142 BARATA (antes do H2)
    # B60 (26/11/2026, dado): série de 02/10 recoletada pelo coletor de hoje; entra `proventos_a_pagar` do ITR 2T26 e o motor
    # passa a pôr o provento já ex na DL (AUD-02). BLAU3 8,1372 → 7,6457 (passivo R$ 114,7 mi); CMIN3 3,6317 → 3,5987 (a ficha
    # já descontava o campo do passivo de contrato; resta o ajuste da B3). O `lucro_controlador` 0 → None de 2022–24 da CMIN3
    # muda o OE desses anos, mas não o central (cíclica: EPV/DCF pela receita de meio). Palavras iguais.
    "BLAU3-2026-10-02": dict(central=7.6457, pc=1.4152, palavra="NÃO CONCLUSIVO"),  # pré-B60 8,1372; pré-H2 8,2998
    "CMIN3-2026-10-06": dict(central=3.5987, pc=1.3727, palavra="CARA"),            # pré-B60 3,6317; pré-H2 3,3668 (macro de
                                                                                    # antes); minério no IPCA da data (era 3,6810)
    "FESA4-2026-10-15": dict(central=7.7010, pc=0.8090, palavra="RADAR"),           # salvo 7,6189
    "HYPE3-2026-10-06": dict(central=15.7668, pc=1.7125, palavra="CARA"),           # pré-H2 16,9224
    "LEVE3-2026-10-06": dict(central=38.3920, pc=0.9520, palavra="NÃO CONCLUSIVO"), # pré-H2 38,4467
    "SHUL4-2026-10-15": dict(central=3.7866, pc=1.3204, palavra="CARA"),            # salvo 3,9037
    "VLID3-2026-10-15": dict(central=16.5501, pc=1.1390, palavra="CARA"),           # salvo 16,6050
}
# Notas da regra 11 no método vigente, quando diferem do JSON salvo (o resto das notas tem de bater com ele).
NOTAS_VIGENTES = {
    # H2: o moat compara ROIC com o WACC real, que mudou com o D/E a mercado
    "ALLD3-2026-10-15": {"notas_regra11": {"moat": 1, "gestao": 1, "controlador": 5, "ciclo": 3, "fisher": 1}, "media_regra11": 2.2},
    # Fase 3, fatia 2b (20/10/2026): a bonificação de 2021 da Schulz (FRE; a B3 não publica) desfaz a "diluição" → gestão 0 → 1
    "SHUL4-2026-10-15": {"notas_regra11": {"moat": 0, "gestao": 1, "controlador": 3, "ciclo": 3, "fisher": 2}, "media_regra11": 2.0},
}


@requer_suplemento_b3
def _recalcular(salvo):
    """Veredito na data salva; sem dados/raw (clone limpo, nuvem) pula em vez de falhar (QA 21/10/2026)."""
    try:
        return gerar.veredito(gerar.calcular(salvo["ticker"], salvo["data_preco"]))
    except FileNotFoundError:
        if TEM_RAW:
            raise
        pytest.skip("dados/raw fora do disco (coletas brutas ignoradas pelo git; clone limpo/nuvem)")


@pytest.mark.parametrize("nome", sorted(METODO_VIGENTE))
def test_veredito_no_metodo_vigente_na_data(nome):
    salvo = json.loads((VEREDITOS / f"{nome}.json").read_text(encoding="utf-8"))
    v = _recalcular(salvo)
    novo = METODO_VIGENTE[nome]
    assert v["central"] == pytest.approx(novo["central"], abs=1e-3) and v["pc"] == pytest.approx(novo["pc"], abs=1e-3)
    assert v["palavra"] == novo["palavra"]
    assert v["central"] != pytest.approx(salvo["central"], abs=1e-3)      # o JSON antigo continua sendo o do método antigo
    esperado = salvo | NOTAS_VIGENTES.get(nome, {})
    if nome in NOTAS_VIGENTES:
        assert all(salvo[k] != x for k, x in NOTAS_VIGENTES[nome].items())     # o JSON antigo segue o de antes
    for k in ("desc_controlador", "media_regra11", "preco"):
        assert v[k] == pytest.approx(esperado[k], abs=1e-4), k
    for k in ("notas_regra11", "discricionario"):
        assert v[k] == esperado[k], k


def test_todo_veredito_salvo_esta_fixado_ou_superado():
    assert set(ARQUIVOS) == set(METODO_VIGENTE) | set(SUPERADOS)


def test_veredito_superado_tem_sucessor_mais_novo_e_continua_no_disco():
    for nome in SUPERADOS:
        tk, data = nome.split("-", 1)
        assert nome in ARQUIVOS, nome
        assert any(n.startswith(tk + "-") and n.split("-", 1)[1] > data for n in ARQUIVOS if n not in SUPERADOS), nome


@requer_suplemento_b3
def test_dossie_de_ticker_do_hall_nao_vaza_para_o_lote():
    # HYPE3 está no Lote 4: o dossiê troca SI["HYPE3"] (proventos da B3) só dentro do calcular; o hall continua igual
    from motor_nao_financeiras import CVM, SI
    si, cvm = SI["HYPE3"], CVM["HYPE3"]
    gerar.calcular("HYPE3")
    assert SI["HYPE3"] is si and CVM["HYPE3"] is cvm
    assert "indicadores" in SI["HYPE3"]          # o do hall (StatusInvest), que o pl_hist do lote lê


@requer_suplemento_b3
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


@requer_suplemento_b3
def test_normalizacao_chamada_sozinha_e_linha_adotada_igual_ao_central():
    from dossie import base
    dc = gerar.insumos("CMIN3")["desconto_controlador"]
    atual = max(n for n in ARQUIVOS if n.startswith("CMIN3-") and n not in SUPERADOS)
    salvo = json.loads((VEREDITOS / f"{atual}.json").read_text(encoding="utf-8"))
    with base.na_data(salvo["data_preco"]):          # a sensibilidade usa o mercado e o preço da data do veredito
        n = cmin3.normalizacao(dc)
    adotado = next(v for k, v in n["sensibilidade"].items() if k.startswith("c "))
    assert adotado["central"] == pytest.approx(METODO_VIGENTE[atual]["central"], abs=1e-3)


def test_aud23_b3_repete_linha_de_jcp_e_a_soma_nao_dobra():
    """AUD-23: HYPE3 01/02/2024 vem duas vezes idêntica na B3; a regra do backtest tem de valer no dossiê."""
    import pandas as pd

    from backtest.precos.proventos_b3 import sem_repeticao
    d = pd.DataFrame([("HYPERA", "2024-02-01", "JRS CAP PROPRIO", 0.09725)] * 2
                     + [("HYPERA", "2024-02-22", "JRS CAP PROPRIO", 0.09725),
                        ("HYPERA", "2024-12-27", "JRS CAP PROPRIO", 0.16911),
                        ("HYPERA", "2024-12-27", "DIVIDENDO", 0.12170)],
                     columns=["nome", "data_com", "tipo", "valor"])
    u = sem_repeticao(d, ["nome", "data_com", "tipo"])
    assert len(u) == 4 and u["valor"].sum() == pytest.approx(0.09725 * 2 + 0.16911 + 0.12170)


def test_aud23_dpa_real_da_hype3_2024_bate_com_a_statusinvest():
    from dossie import base
    dpa, _ = base.proventos_b3("HYPE3")
    assert dpa["2024"] == pytest.approx(1.1678, abs=1e-3)        # era 1,2651 com a linha duplicada
    assert base.divergencias_b3_si({"2024": 1.1678}, {"2024": 1.1678}) == []


def test_aud23_divergencia_acima_de_3_por_cento_vira_alerta():
    from dossie import base
    assert base.divergencias_b3_si({"2024": 1.2651}, {"2024": 1.1678}) == [("2024", 1.2651, 1.1678)]
    assert base.divergencias_b3_si({"2024": 1.20}, {"2024": 1.19}) == []
    assert [a for a, _, _ in base.divergencias_b3_si({"2024": 1.0}, {"2025": 1.0})] == ["2024", "2025"]


@requer_suplemento_b3
def test_minerio_da_cmin3_no_mesmo_r_de_hoje_do_motor_na_data():
    """Adversário (24/11/2026): o minério lia o IPCA direto do arquivo e ficava em cache — no recálculo na data ele usava o IPCA
    de um mês ainda não publicado e misturava duas bases de "R$ de hoje"."""
    import inflacao
    from dossie import base
    fora = cmin3.minerio()["base"]
    with base.na_data("2026-10-06"):
        assert cmin3.minerio()["base"] == inflacao.DATA_BASE == "08/2026"
    assert cmin3.minerio()["base"] == fora
