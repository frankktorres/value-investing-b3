"""Testes unitários das regras da doutrina v2.3 (07/10/2026) — as 6 decisões da Etapa 5.

(2) desconto de controlador só em âncora > 0 · (3) média da regra 11 no motor, controlador com peso 2 quando discricionário ·
(6) alíquota por fase, sem piso de 15% · (5) `outros_passivos` financeiro na DL · (1) `capex_expansao` opcional ·
(4) margem ao preço de meio só em cíclica com janela >= 7.

O golden prova o resultado dos 41 tickers; estes testes provam as REGRAS em série sintética, inclusive os casos que hoje
nenhum ticker do hall exercita.
"""
import pytest

import motor_financeiras as F
import motor_nao_financeiras as M
from lote1_bancos import MK


def _serie(tk, receita=10_000.0, anos=range(2016, 2026), **campos):
    """Ticker artificial em M.CVM/M.SI (R$ mil). `campos` sobrepõe os valores de todos os anos e do LTM."""
    anual = {}
    for a in anos:
        d = {"receita": receita, "capex": 500.0, "imobilizado": 5_000.0, "intangivel": 0.0, "biologico": 0.0, "da": 500.0,
             "lucro": 1_000.0, "ac": 3_000.0, "pc": 1_000.0, "caixa": 500.0, "aplic_cp": 0.0, "emprest_cp": 0.0,
             "emprest_lp": 1_000.0, "arrendamento": 0.0, "pl": 6_000.0, "ebit": 1_500.0, "lair": 1_500.0, "ir": -500.0,
             "ativo": 10_000.0, "pnc": 1_000.0, "reservas_lucro": 0.0, "nao_controladores": 0.0, "receber": 0.0,
             "lucro_bruto": 4_000.0, "fco": 1_200.0, "acoes": 1_000_000.0, "juros_pagos": 100.0}
        d.update(campos)
        anual[str(a)] = d
    M.CVM[tk] = {"anual": anual, "ltm_2T26": dict(anual[str(max(anos))])}
    M.SI[tk] = {"dpa_por_ano_datacom": {str(a): 0.5 for a in anos}}
    M.idade_e_fator.cache_clear()
    return anual


def _emp(tk, **kw):
    kw.setdefault("defasagem_meses", 0.0)
    kw.setdefault("defasagem_fonte", "teste sintético")
    return M.Industrial(tk, tk, kw.pop("perfil", "servicos"), preco=kw.pop("preco", 10.0), n_acoes=1_000_000.0, **kw)


# ---------------------------------------------------------------- (2) desconto só em âncora > 0
def test_2_descontar_poupa_ancora_negativa_e_nula():
    assert F.descontar({"a": 10.0, "b": -4.0, "c": 0.0}, 0.3) == {"a": 7.0, "b": -4.0, "c": 0.0}
    assert F.descontar({"a": 10.0}, 0.0) == {"a": 10.0}


def test_2_nao_financeira_com_ancora_negativa_continua_nao_conclusiva_e_sem_melhora():
    """Dívida enorme → EPV e DCF negativos; o OE (fluxo do acionista) fica positivo. Com 30% de desconto, só o OE cai."""
    _serie("TESTEV23A", emprest_lp=60_000.0)
    emp = _emp("TESTEV23A", desconto_controlador={"tipo": "fixo", "pct": 0.30, "razao": "teste"})
    r = M.avaliar(emp, MK)
    for k, x in r["anc"].items():
        assert r["ancoras"][k] == pytest.approx(x if x <= 0 else 0.7 * x), k
    assert any(x <= 0 for x in r["ancoras"].values())
    assert r["palavra"] == "NÃO CONCLUSIVO"


def test_2_financeira_fixo_poupa_ancora_negativa(monkeypatch):
    monkeypatch.setattr(F, "ancoras", lambda emp, mk, roe: {"P/VP justificado": -5.0, "DDM": 20.0})
    fin = F.Financeira("TESTEV23F", "x", "banco", preco=10.0, vpa=10.0, lpa_12m=1.0, roe_lp=0.15, roe_inicio=0.15,
                       payout=0.5, dpa_medio_5a=0.5, defasagem_meses=0.0, defasagem_fonte="teste",
                       desconto_controlador={"tipo": "fixo", "pct": 0.35, "razao": "teste"})
    r = F.avaliar(fin, MK)
    assert r["ancoras"] == {"P/VP justificado": -5.0, "DDM": pytest.approx(13.0)}
    assert r["palavra"] == "NÃO CONCLUSIVO"
    assert F.central_ao_ke(fin, MK, MK.ke_nom) == pytest.approx((-5.0 + 13.0) / 2)


def test_2_ke_implicito_usa_o_central_descontado():
    """§5: uma única vez, no valor — o Ke que o preço embute se mede contra o central COM o desconto."""
    _serie("TESTEV23K")
    sem = _emp("TESTEV23K", preco=5.0)
    com = _emp("TESTEV23K", preco=5.0, desconto_controlador={"tipo": "fixo", "pct": 0.30, "razao": "teste"})
    k0, k1 = M.ke_implicito(sem, MK), M.ke_implicito(com, MK)
    assert k0 is not None and k1 is not None and k1 < k0
    c1 = M.central_de(M.descontar(M.valores(com, MK, ke_nom=k1)["anc"], 0.30))[0]
    assert c1 == pytest.approx(com.preco, rel=1e-4)


# ---------------------------------------------------------------- (3) média da regra 11 no motor
def test_3_media_qualitativa_peso_do_controlador():
    q = dict(moat=4, gestao=3, controlador=1, ciclo=2, fisher=3)
    assert F.media_qualitativa(q) == pytest.approx(13 / 5)
    assert F.media_qualitativa(q, discricionario=True) == pytest.approx(14 / 6)
    assert F.media_qualitativa({}) == 2.5                      # neutro: o 5 de 10 de antes
    with pytest.raises(ValueError, match="chaves"):
        F.media_qualitativa({"media_regra11": 2.0})           # o truque de chave única do dossiê v2.2 não passa mais calado


def test_3_notas_do_dossie_e_motor_usam_a_mesma_conta():
    from dossie import notas
    assert notas.media(0, 1, 3, 3, 1, True) == pytest.approx(F.media_qualitativa(notas.para_qual(0, 1, 3, 3, 1), True))
    assert notas.media(0, 1, 3, 3, 1, True) == pytest.approx((0 + 1 + 6 + 3 + 1) / 6)


def test_3_peso_2_sem_fonte_nao_roda_nos_dois_motores():
    _serie("TESTEV23Q")
    with pytest.raises(ValueError, match="controlador_discricionario_fonte"):
        M.exigir_declaracoes(_emp("TESTEV23Q", controlador_discricionario=True))
    fin = F.Financeira("TESTEV23QF", "x", "banco", preco=10.0, vpa=10.0, lpa_12m=1.0, roe_lp=0.15, roe_inicio=0.15,
                       payout=0.5, dpa_medio_5a=0.5, defasagem_meses=0.0, defasagem_fonte="teste",
                       controlador_discricionario=True)
    with pytest.raises(ValueError, match="controlador_discricionario_fonte"):
        F.avaliar(fin, MK)


def test_3_hall_peso_2_so_onde_a_interferencia_consumada_esta_declarada():
    import universo
    disc = {e.ticker: e for _, emps, _ in universo.GRUPOS for e in emps if e.controlador_discricionario}
    assert sorted(disc) == ["BBAS3", "BRSR6", "CMIG4", "PETR4", "SAPR11"]
    for tk, e in disc.items():
        assert e.desconto_controlador["tipo"] != "zero" and e.controlador_discricionario_fonte.strip(), tk
    todos = [e for _, emps, _ in universo.GRUPOS for e in emps]
    assert all(e.qualitativo_origem == "arbitrada, pré-v4" for e in todos)


def test_3_nota_de_qualidade_do_hall_aplica_o_peso():
    import lote1_bancos as L1
    bbas = next(e for e in L1.EMPRESAS if e.ticker == "BBAS3")
    r = F.avaliar(bbas, MK)
    esperado = 0.5 * F.nota_spread(bbas.roe_lp, MK.ke_nom) + 0.5 * 2 * (4 + 3 + 2 * 1 + 2 + 3) / 6
    assert r["notas"]["qualidade"] == pytest.approx(esperado)
    assert r["controlador_peso"] == 2 and r["qualitativo_origem"] == "arbitrada, pré-v4"


# ---------------------------------------------------------------- (6) alíquota por fase, sem piso de 15%
def test_6_mediana_acima_de_15_vale_sem_piso_e_sem_retributar_o_oe():
    _serie("TESTEV23T1", ir=-300.0)                         # 20%
    emp = _emp("TESTEV23T1")
    assert M.aliquota_regra(emp) == (pytest.approx(0.20), "mediana")
    _serie("TESTEV23T1B", ir=-600.0)                        # 40% → teto 34%
    assert M.aliquota_regra(_emp("TESTEV23T1B")) == (pytest.approx(0.34), "mediana")


def test_6_mediana_abaixo_de_15_so_vale_com_origem_permanente_declarada():
    _serie("TESTEV23T2", ir=-75.0)                          # 5%
    assert M.aliquota_regra(_emp("TESTEV23T2")) == (M.ALIQUOTA_MARGINAL, "sem_origem")
    perm = _emp("TESTEV23T2", aliquota_permanente_fonte="JCP recorrente, nota 21 do DFP (teste)")
    assert M.aliquota_regra(perm) == (pytest.approx(0.05), "permanente")
    _serie("TESTEV23T2B", lair=-100.0)                      # sem ano com LAIR > 0
    assert M.aliquota_regra(_emp("TESTEV23T2B")) == (M.ALIQUOTA_MARGINAL, "sem_dado")


def test_6_fase_declaracao_incompleta_ou_ambigua_nao_roda():
    _serie("TESTEV23T3", ir=-75.0)
    for ruim in ({"ate": 2030}, {"fonte": "x"}, {"ate": "2030", "fonte": "x"}, {"ate": 2030, "fonte": "x", "efetiva": 0.5}):
        with pytest.raises(ValueError, match="aliquota_fase"):
            M.exigir_declaracoes(_emp("TESTEV23T3", aliquota_fase=ruim))
    with pytest.raises(ValueError, match="não combina"):
        M.exigir_declaracoes(_emp("TESTEV23T3", aliquota_fase={"ate": 2030, "fonte": "x"}, aliquota=0.2))


def test_6_fase_34_na_perpetuidade_e_beneficio_em_valor_presente():
    _serie("TESTEV23T4", ir=-75.0)                          # efetiva 5% até 2030
    fase = _emp("TESTEV23T4", aliquota_fase={"ate": 2030, "fonte": "teste"})
    assert M.aliquota_regra(fase) == (M.ALIQUOTA_MARGINAL, "fase")
    assert M.fase_fiscal(fase) == (pytest.approx(0.05), 4)
    r = M.valores(fase, MK)
    pre = r["op"]["receita_meio"] * (r["m"] + r["op"]["ajuste_manut"])
    w = r["wacc_real"]
    # base = lucro DEPOIS dos juros normalizados (o WACC já dá a dedução dos juros a 34%); teto = crédito observado
    anual = min((pre - r["kd"] * max(r["dl"], 0.0)) * (0.34 - 0.05), M.credito_observado(fase))
    assert anual > 0
    pv = sum(anual / (1 + w) ** t for t in range(1, 5))
    assert r["nopat"] == pytest.approx(pre * 0.66)
    assert r["anc"]["EPV"] == pytest.approx((pre * 0.66 / w + pv - r["dl"] - r["minor"]) / r["n"])
    assert r["beneficio_fiscal_acao"] == pytest.approx(pv / r["n"])
    # entre "34% para sempre" e "5% para sempre"; com a fase vencida (ate <= ANO_BASE) é o próprio 34%
    sempre34 = M.valores(_emp("TESTEV23T4", aliquota=0.34), MK)["anc"]["EPV"]
    sempre5 = M.valores(_emp("TESTEV23T4", aliquota=0.05), MK)["anc"]["EPV"]
    assert sempre34 < r["anc"]["EPV"] < sempre5
    vencida = M.valores(_emp("TESTEV23T4", aliquota_fase={"ate": M.ANO_BASE, "fonte": "teste"}), MK)
    assert vencida["anc"]["EPV"] == pytest.approx(sempre34)
    assert vencida["anc"]["DCF (3 cenários)"] == pytest.approx(M.valores(_emp("TESTEV23T4", aliquota=0.34), MK)["anc"]["DCF (3 cenários)"])


def test_6_fase_conta_os_anos_de_credito_e_credito_maior_nunca_vale_menos():
    """Adversário, 07/10: com o corte em zero a efetiva da fase saía de um ano só, e um crédito um pouco maior zerava a fase."""
    taxas = {"2021": 0.02, "2022": -0.05, "2023": -0.10, "2024": -0.30, "2025": -0.30}
    anual = _serie("TESTEV23T6")
    for a, t in taxas.items():
        anual[a]["ir"] = -t * anual[a]["lair"]
    M.CVM["TESTEV23T6"]["ltm_2T26"] = dict(anual["2025"])
    fase = _emp("TESTEV23T6", aliquota_fase={"ate": 2030, "fonte": "teste"})
    assert M.fase_fiscal(fase) == (0.0, 4)                  # mediana −10% presa em zero (antes: 2%, um ano só)
    epv0 = M.valores(fase, MK)["anc"]["EPV"]
    anual["2021"]["ir"] = 0.0006 * anual["2021"]["lair"]     # o único ano positivo vira crédito pequeno
    assert M.fase_fiscal(fase) == (0.0, 4)
    assert M.valores(fase, MK)["anc"]["EPV"] >= epv0 - 1e-9


def test_6_teto_do_beneficio_e_o_credito_observado():
    _serie("TESTEV23T7", ir=-75.0)
    fase = _emp("TESTEV23T7", aliquota_fase={"ate": 2030, "fonte": "teste"})
    cap = M.credito_observado(fase)
    assert cap > 0
    assert M.beneficio_fiscal(fase, 1e9, 0.1) == pytest.approx(sum(cap / 1.1 ** t for t in range(1, 5)))
    assert M.beneficio_fiscal(fase, -1.0, 0.1) == 0.0


def test_6_menos_de_3_anos_validos_e_sem_dado_com_oe_refeito():
    anual = _serie("TESTEV23T8")
    for a, t in {"2021": 0.20, "2022": -0.10, "2023": -0.20, "2024": -0.30, "2025": 0.18}.items():
        anual[a]["ir"] = -t * anual[a]["lair"]
    M.CVM["TESTEV23T8"]["ltm_2T26"] = dict(anual["2025"])
    emp = _emp("TESTEV23T8")
    assert M.mediana_efetiva(emp) is None
    assert M.aliquota_regra(emp) == (M.ALIQUOTA_MARGINAL, "sem_dado")
    r = M.valores(emp, MK)
    kd_real = (1 + r["kd"]) / (1 + MK.pi) - 1
    assert all(x == pytest.approx(M.owner_earnings_ano(emp, a, str(int(a) - 1), kd_real, False, 0.34)) for a, x in r["oe"])


def test_6_oe_retributado_a_aliquota_perpetua():
    _serie("TESTEV23T5", ir=-75.0)                          # 5% observado → 34% perpétua (sem origem)
    emp = _emp("TESTEV23T5")
    d = M.CVM["TESTEV23T5"]["anual"]["2025"]
    puro = M.owner_earnings_ano(emp, "2025", "2024", 0.05)
    refeito = M.owner_earnings_ano(emp, "2025", "2024", 0.05, t_retributar=0.34)
    assert refeito == pytest.approx(puro - (d["ir"] + 0.34 * d["lair"]))      # lucro 1000 → LAIR × 0,66 = 990
    r = M.valores(emp, MK)
    assert r["aliquota_regra"] == "sem_origem"
    assert all(x == pytest.approx(M.owner_earnings_ano(emp, a, str(int(a) - 1), (1 + r["kd"]) / (1 + MK.pi) - 1, False, 0.34))
               for a, x in r["oe"])
    del M.CVM["TESTEV23T5"]["anual"]["2025"]["ir"]
    assert M.owner_earnings_ano(emp, "2025", "2024", 0.05, t_retributar=0.34) is None   # sem a linha do IR o ano sai


def test_6_hall_so_hype3_tem_fase_e_os_abaixo_de_15_estao_declarados():
    import universo
    nf = [e for _, emps, _ in universo.GRUPOS for e in emps if isinstance(e, M.Industrial)]
    assert [e.ticker for e in nf if e.aliquota_fase] == ["HYPE3"]
    regras = {e.ticker: M.aliquota_regra(e)[1] for e in nf}
    assert regras["HYPE3"] == "fase" and regras["ABEV3"] == "explicita"
    assert sorted(t for t, x in regras.items() if x == "sem_origem") == ["PRIO3", "TIMS3"]
    assert all(x in ("mediana", "fase", "explicita", "sem_origem") for x in regras.values())


# ---------------------------------------------------------------- (5) outros_passivos financeiro na DL
def test_5_financeiro_entra_na_dl_e_no_capital_operacional_so_na_ponte():
    _serie("TESTEV23P")
    X = 2_000.0
    op = M.avaliar(_emp("TESTEV23P", g_real=0.0, outros_passivos=X, outros_passivos_fonte="teste"), MK)
    fi = M.avaliar(_emp("TESTEV23P", g_real=0.0, outros_passivos_financeiros=X, outros_passivos_fonte="teste"), MK)
    assert fi["dl"] == pytest.approx(op["dl"] + X)
    assert fi["cap_inv"] == pytest.approx(op["cap_inv"] + X) and fi["roic"] < op["roic"]
    assert fi["dl_ebitda"] > op["dl_ebitda"]
    # com g = 0 não há trava de crescimento: a ponte firma → equity desconta o mesmo valor nos dois casos
    for k in op["ancoras"]:
        assert fi["ancoras"][k] == pytest.approx(op["ancoras"][k]), k


def test_5_outros_passivos_sem_fonte_nao_roda():
    _serie("TESTEV23P2")
    for campo in ("outros_passivos", "outros_passivos_financeiros"):
        with pytest.raises(ValueError, match="outros_passivos_fonte"):
            M.exigir_declaracoes(_emp("TESTEV23P2", **{campo: 1.0}))


# ---------------------------------------------------------------- (1) capex de expansão identificado
EXP = {"projeto": "fábrica nova (teste)", "fonte": "FR 01/01/2025 (teste)", "nota_fonte": "A", "retorno_projetado": "n.d."}


def test_1_expansao_identificada_sai_antes_do_greenwald_e_na_regra_de_commodity():
    _serie("TESTEV23E")
    cm0, cresc = M.capex_manutencao("TESTEV23E", "2025", "2024")
    cm1, _ = M.capex_manutencao("TESTEV23E", "2025", "2024", expansao=200.0)
    assert cm1 == pytest.approx(max(cm0 - 200.0, 0.0)) and cresc == pytest.approx(0.0)
    assert M.capex_manutencao("TESTEV23E", "2025", "2024", ciclica=True, expansao=200.0) == (300.0, 0.0)
    assert M.capex_manutencao("TESTEV23E", "2025", "2024", expansao=900.0)[0] == 0.0    # piso zero continua


def test_1_expansao_sobe_o_oe_e_o_ajuste_de_manutencao_padrao_vazio_nao_muda_nada():
    _serie("TESTEV23E2", capex=800.0)        # capex > D&A: o excesso sai do lucro normalizado
    sem = M.valores(_emp("TESTEV23E2"), MK)
    com = M.valores(_emp("TESTEV23E2", capex_expansao=dict(EXP, anos={str(a): 300.0 for a in range(2016, 2026)})), MK)
    assert com["op"]["ajuste_manut"] > sem["op"]["ajuste_manut"]
    assert com["oe_norm"] == pytest.approx(sem["oe_norm"] + 300.0)
    cic = dict(perfil="ciclica")
    s, c = (M.valores(_emp("TESTEV23E2", **cic, **kw), MK)["op"]["ajuste_manut"] for kw in
            ({}, {"capex_expansao": dict(EXP, anos={str(a): 300.0 for a in range(2016, 2026)})}))
    assert c > s


def test_1_expansao_sem_fonte_ab_ou_acima_do_capex_nao_roda():
    _serie("TESTEV23E3")
    for ruim in (dict(EXP, nota_fonte="C", anos={"2025": 10.0}), dict(EXP, anos={}), dict(EXP, anos={"2025": 501.0}),
                 dict(EXP, anos={"2031": 1.0}), {k: v for k, v in EXP.items() if k != "projeto"} | {"anos": {"2025": 1.0}}):
        with pytest.raises(ValueError, match="capex_expansao"):
            M.exigir_declaracoes(_emp("TESTEV23E3", capex_expansao=ruim))
    M.exigir_declaracoes(_emp("TESTEV23E3", capex_expansao=dict(EXP, anos={"2025": 500.0})))


# ---------------------------------------------------------------- (4) margem ao preço de meio
def test_4_margem_ao_preco_de_meio_so_em_ciclica_com_janela_de_7():
    _serie("TESTEV23M")
    fp = {str(a): 1.0 for a in range(2016, 2026)}
    with pytest.raises(ValueError, match="perfil 'ciclica'"):
        M.premissas_operacionais(_emp("TESTEV23M", fator_preco=fp))
    curta = [str(a) for a in range(2020, 2026)]
    with pytest.raises(ValueError, match="janela >= 7"):
        M.premissas_operacionais(_emp("TESTEV23M", perfil="ciclica", fator_preco=fp, anos_ciclo=curta, janela_razao="teste"))
    ok = M.premissas_operacionais(_emp("TESTEV23M", perfil="ciclica", fator_preco=fp))
    assert ok["m50"] == pytest.approx(M.premissas_operacionais(_emp("TESTEV23M", perfil="ciclica"))["m50"])   # f = 1


def test_6_caixa_liquido_nao_aumenta_a_base_do_beneficio():
    _serie("TESTEV23T9", ir=-75.0, caixa=20_000.0, emprest_lp=0.0)      # caixa líquido grande
    fase = _emp("TESTEV23T9", aliquota_fase={"ate": 2030, "fonte": "teste"})
    r = M.valores(fase, MK)
    assert r["dl"] < 0
    pre = r["op"]["receita_meio"] * (r["m"] + r["op"]["ajuste_manut"])
    esperado = sum(min(pre * (0.34 - 0.05), M.credito_observado(fase)) / (1 + r["wacc_real"]) ** t for t in range(1, 5))
    assert r["beneficio_fiscal_acao"] * r["n"] == pytest.approx(esperado)
