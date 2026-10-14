"""Onda 3 da auditoria de 08/10/2026 — riscos latentes do motor (AUD-11, 45, 46, 47, 51, 52, 54, 85, 103).

Nenhum muda palavra no hall de hoje; cada teste falha com a versão anterior do código (mutação à mão, registrada no `09`).
"""
import dataclasses
import math
import pathlib

import pytest

import motor_financeiras as F
from motor_financeiras import Financeira, Mercado, palavra, precos_de_referencia

MK = Mercado(rf_real=0.05, pi=0.05)


def _emp(**kw):
    base = dict(ticker="T", nome="T", perfil="banco", preco=10.0, vpa=20.0, lpa_12m=2.0, roe_lp=0.10, roe_inicio=0.10,
                payout=0.5, dpa_medio_5a=1.0, defasagem_meses=0, defasagem_fonte="teste",
                desconto_controlador={"tipo": "zero", "razao": "teste sintético"})
    base.update(kw)
    return Financeira(**base)


# ---------------------------------------------------------------- AUD-11: guardas do motor de financeiras
@pytest.mark.parametrize("roe_lp", [-0.05, -0.02, 0.0])
def test_aud11_roe_lp_nao_positivo_e_nao_conclusivo_sem_quebrar(roe_lp):
    r = F.avaliar(_emp(roe_lp=roe_lp, roe_inicio=roe_lp), MK)      # antes: TypeError (complexo) ou ZeroDivisionError
    assert r["palavra"] == "NÃO CONCLUSIVO"
    assert r["pl_atual"] is None and r["dmult"] == 0.0
    assert not isinstance(r["bogle_nom"], complex)


def test_aud11_central_negativo_sem_preco_de_referencia_e_nota_de_preco_zero():
    r = F.avaliar(_emp(roe_lp=-0.05, roe_inicio=-0.05), MK)
    assert r["central"] < 0
    assert r["pc"] == math.inf and r["notas"]["preco"] == 0       # antes: P/C negativo → BARATA e nota de preço 10
    assert r["compra"] is None and r["saida"] is None


# ---------------------------------------------------------------- AUD-46: fronteira da régua em ponto flutuante
def test_aud46_preco_igual_a_fronteira_fica_na_faixa_de_baixo():
    for c in (x / 100 for x in range(100, 5000, 7)):
        assert palavra(0.70 * c / c) == "BARATA", c
        assert palavra(0.90 * c / c) == "RADAR", c
        assert palavra(1.10 * c / c) == "JUSTA", c
    assert palavra(0.7000001) == "RADAR"                # o arredondamento é de 1e-9, não muda faixa real


# ---------------------------------------------------------------- AUD-52: NÃO CONCLUSIVO sem preço negativo nem Infinity
def test_aud52_central_nao_positivo_sem_compra_nem_saida():
    assert precos_de_referencia(-3.67) == dict(compra=None, compra_parcial=None, saida=None, saida_por_qualidade=False)
    assert precos_de_referencia(10.0)["compra"] == pytest.approx(7.0)


def test_aud52_instantaneo_grava_null_no_lugar_de_infinity():
    import json
    from universo import instantaneo
    item = dict(lote=5, r=dict(central=-3.67, pc=math.inf, palavra="NÃO CONCLUSIVO", ancoras={"EPV": -1.0},
                               notas={"geral": 2.7}))
    snap = instantaneo(item)
    assert snap["pc"] is None
    json.dumps(snap, allow_nan=False)                    # antes: ValueError (Infinity não é JSON)


def test_aud52_registro_prospectivo_aceita_pc_null():
    from registro_prospectivo import linhas_do_golden
    g = {"tickers": {"RECV3": {"pc": None, "central": 0.0, "palavra": "NÃO CONCLUSIVO", "lote": 5}}}
    import registro_prospectivo as R
    g["tickers"]["RECV3"].update({c: None for c in R.CAMPOS if c not in g["tickers"]["RECV3"]})
    linha = linhas_do_golden(g, "2026-10-02", "2.6", "x", "2026-10-10")[0]
    assert linha["preco"] is None and linha["pc"] is None


def test_aud52_golden_vigente_sem_infinity():
    txt = (pathlib.Path(__file__).parent / "golden.json").read_text(encoding="utf-8")
    assert "Infinity" not in txt and "NaN" not in txt


# ---------------------------------------------------------------- AUD-45: precedência da régua no motor de produção
def test_aud45_circulo_tem_teto_radar_e_nao_mexe_no_resto():
    base = F.avaliar(_emp(), MK)                           # dispersão 1,0
    c = base["central"]
    assert F.avaliar(_emp(preco=0.5 * c, fora_circulo=True), MK)["palavra"] == "RADAR"
    assert F.avaliar(_emp(preco=0.8 * c, fora_circulo=True), MK)["palavra"] == "RADAR"
    assert F.avaliar(_emp(preco=1.5 * c, fora_circulo=True), MK)["palavra"] == "CARA"


def test_aud45_circulo_depois_dispersao_desce_dois_niveis():
    r0 = F.avaliar(_emp(roe_inicio=0.5), MK)               # P/VP 9,52 × DDM 20,06: dispersão 2,1
    assert 1.8 < r0["dispersao"] < 3
    c = r0["central"]
    barata = F.avaliar(_emp(roe_inicio=0.5, preco=0.5 * c), MK)
    assert barata["palavra_regua"] == "BARATA" and barata["palavra"] == "RADAR"
    fora = F.avaliar(_emp(roe_inicio=0.5, preco=0.5 * c, fora_circulo=True), MK)
    assert fora["palavra"] != "BARATA"
    assert F.avaliar(_emp(roe_inicio=0.5, preco=1.5 * c), MK)["palavra"] == "CARA"     # CARA não muda


def test_aud45_dispersao_acima_de_3_e_nao_conclusivo_mesmo_fora_do_circulo():
    r = F.avaliar(_emp(roe_inicio=0.8, preco=5.0, fora_circulo=True), MK)
    assert r["dispersao"] > 3 and r["palavra"] == "NÃO CONCLUSIVO"


def test_aud45_motor_nf_mesma_precedencia_no_hall():
    import motor_nao_financeiras as M
    import universo
    t = universo.avaliar_todos()
    e, r = t["WEGE3"]["empresa"], t["WEGE3"]["r"]
    assert r["dispersao"] <= 1.8
    c = r["central"]
    assert M.avaliar(dataclasses.replace(e, preco=0.5 * c), universo.MK)["palavra"] == "BARATA"
    assert M.avaliar(dataclasses.replace(e, preco=0.5 * c, fora_circulo=True), universo.MK)["palavra"] == "RADAR"


# ---------------------------------------------------------------- AUD-10 (v2.6): trava de coerência na palavra FINAL
def test_aud10_radar_que_vira_justa_pela_dispersao_passa_pela_trava():
    c = F.avaliar(_emp(roe_inicio=0.5), MK)["central"]
    r = F.avaliar(_emp(roe_inicio=0.5, preco=0.8 * c), MK)          # régua RADAR, dispersão 2,1 → JUSTA; Bogle 13,5% × Ke 15,5%
    assert r["palavra_regua"] == "RADAR" and r["trava"] is False
    assert r["palavra"] == "NÃO CONCLUSIVO" and "trava" in r["confianca"]
    assert F.avaliar(_emp(roe_inicio=0.5, preco=0.8 * c, trava_razao="premissa X diverge"), MK)["palavra"] == "JUSTA"


# ---------------------------------------------------------------- AUD-15, 34, 53 (v2.6): regras do DCF e do OE
def test_aud53_cenario_negativo_entra_como_zero_e_recv3_segue_nao_conclusiva():
    import universo
    r = universo.avaliar_todos()["RECV3"]["r"]
    assert min(r["dcf"].values()) < 0 and r["dcf_pond"] >= 0
    assert r["palavra"] == "NÃO CONCLUSIVO" and r["compra"] is None


def test_aud34_declinio_com_roic_abaixo_do_wacc_nao_explode_o_dcf():
    import motor_nao_financeiras as M
    import universo
    e = next(x for x in universo.lote3_agro.EMPRESAS + universo.lote6_quimica.EMPRESAS if x.ticker == "KLBN11")
    ec = M.estrutura_de_capital(e, universo.MK)
    base = {g: M.valores(e, ec["mk"], e_peso=ec["e_peso"], g_real=g)["dcf"]["base"] for g in (0.0, -0.003, -0.05)}
    assert base[-0.05] <= base[-0.003] <= base[0.0] * 1.0001          # antes: 3,79 → 39,43 → 357,65 (subia com o declínio)


def test_aud15_owner_earnings_usa_o_lucro_do_controlador(monkeypatch):
    import motor_nao_financeiras as M
    import universo
    e = next(x for x in universo.lote3_agro.EMPRESAS + universo.lote6_quimica.EMPRESAS if x.ticker == "KLBN11")
    a, ltm = M.serie("KLBN11")
    d = a["2024"]
    assert d["lucro_controlador"] is not None and d["lucro_controlador"] != d["lucro"]
    oe = M.owner_earnings_ano(e, "2024", "2023", 0.05)
    monkeypatch.setattr(M, "serie", lambda tk: ({**a, "2024": dict(d, lucro_controlador=None)}, ltm))
    oe_consolidado = M.owner_earnings_ano(e, "2024", "2023", 0.05)
    assert oe - oe_consolidado == pytest.approx(d["lucro_controlador"] - d["lucro"])


# ---------------------------------------------------------------- AUD-42 (v2.6): entrada parcial numa regra só
def _r(**kw):
    r = dict(palavra="JUSTA", central=10.0, pc=0.78, dispersao=1.2, notas=dict(qualidade=8.5, solidez=7.5))
    r.update(kw)
    return r


def test_aud42_entrada_parcial_exige_as_cinco_condicoes_e_o_preco():
    from motor_financeiras import entrada_parcial
    assert entrada_parcial(_r()) == (True, [])
    assert entrada_parcial(_r(pc=0.80 * 7 / 7)) == (True, [])                 # fronteira 0,80 (AUD-46) entra
    casos = [(_r(pc=0.84), "0,80"), (_r(notas=dict(qualidade=7.9, solidez=9)), "qualidade"),
             (_r(notas=dict(qualidade=9, solidez=6.9)), "solidez"), (_r(dispersao=1.9), "dispersão"),
             (_r(palavra="NÃO CONCLUSIVO"), "NÃO CONCLUSIVO")]
    for r, motivo in casos:
        ok, m = entrada_parcial(r)
        assert not ok and any(motivo in x for x in m), (motivo, m)
    assert entrada_parcial(_r(), fora_circulo=True)[0] is False                  # antes nenhum PDF testava o círculo
    ok, m = entrada_parcial(_r(), armadilhas=["defeito estrutural"])
    assert not ok and m == ["armadilha: defeito estrutural"]


def test_aud42_pdfs_usam_a_regra_do_motor():
    aqui = pathlib.Path(__file__).parent.parent
    for n in (1, 3, 4, 5, 6):
        txt = (aqui / f"gerar_pdf_lote{n}.py").read_text(encoding="utf-8")
        assert "texto_entrada_parcial(" in txt and 'n["qualidade"] >= 8' not in txt and "n['qualidade'] >= 8" not in txt, n


# ---------------------------------------------------------------- AUD-54, 47, 51: motor de não financeiras
def test_aud54_dl_ebitda_indefinido_e_a_pior_nota():
    from motor_nao_financeiras import nota_alavancagem
    assert nota_alavancagem(None) == 1                     # antes: tratado como 0 → nota 10
    assert nota_alavancagem(0) == 10 and nota_alavancagem(5) == 1


def test_aud47_ancora_owner_earnings_descartada_fica_registrada():
    import motor_nao_financeiras as M
    import universo
    tim = universo.avaliar_todos()["TIMS3"]
    assert tim["r"]["ancoras_descartadas"] == []
    r = M.avaliar(dataclasses.replace(tim["empresa"], g_real=0.20), universo.MK)
    assert "Owner Earnings ÷ (Ke − g)" not in r["ancoras"]
    assert r["ancoras_descartadas"] and "Ke real ≤ g" in r["ancoras_descartadas"][0]


def test_aud51_vivt3_avisa_que_a_aliquota_esta_perto_do_limiar_de_15():
    import universo
    t = universo.avaliar_todos()
    assert t["VIVT3"]["r"]["aliquota_perto_do_limiar"] is True        # mediana 15,53%
    assert t["WEGE3"]["r"]["aliquota_perto_do_limiar"] is False


# ---------------------------------------------------------------- AUD-85 e AUD-103: o LTM da temporada chega a tudo
def test_aud85_injetar_limpa_o_cache_da_idade_do_imobilizado():
    import motor_nao_financeiras as M
    import temporada
    M.idade_e_fator("TIMS3")
    assert M.idade_e_fator.cache_info().currsize > 0
    temporada.injetar({})
    assert M.idade_e_fator.cache_info().currsize == 0


def test_aud103_carregar_cvm_aplica_o_ltm_da_temporada(monkeypatch):
    import series_vigente
    novo = {"receita": 1.0}
    monkeypatch.setitem(series_vigente.CVM_SOBREPOSTO, "EGIE3", {"ltm": novo, "ltm_ref": "3T26"})
    d = series_vigente.carregar_cvm()
    assert d["EGIE3"]["ltm"] == novo and d["EGIE3"]["ltm_ref"] == "3T26" and d["EGIE3"]["ltm_3T26"] == novo
    assert d["EGIE3"]["anual"]                                    # a série anual fica


def test_aud103_nenhum_lote_le_o_cvm_series_por_fora_do_carregador():
    """Quem lê o arquivo direto escapa do LTM da temporada (premissas calculadas no import ficam com o LTM velho)."""
    aqui = pathlib.Path(__file__).parent.parent
    fora = [p.name for p in aqui.glob("*.py")
            if p.name not in ("series_vigente.py", "coletar_cvm.py", "temporada.py")
            and '"cvm_series.json").read_text' in p.read_text(encoding="utf-8")]
    assert fora == []
