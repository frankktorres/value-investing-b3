"""Camada 2 — propriedades e relações metamórficas dos dois motores (docs/VALIDACAO.md §1; PRE-REGISTRO-v3 §3 e emenda 2).

Leis que valem para QUALQUER entrada, conferidas pelo Hypothesis com semente fixa sobre as empresas reais dos lotes:
  Ke ↑ ⇒ central não sobe · fluxo ↑ ⇒ central não cai · central não depende do preço · desdobramento · permutação ·
  preço ↑ nunca melhora a palavra · sem NaN/inf · g < Ke · a nota não decide a palavra · Piotroski/Beneish fora da nota ·
  Graham-BR e teto de renda nunca são âncora · âncora única ⇒ confiança baixa · Focus só como sensibilidade.
O caso "dado crítico ausente ⇒ nunca BARATA, RADAR ou JUSTA" era xfail(strict) ligado à H10 (zero silencioso) e o desconto do
controlador nos industriais era o achado A1; a Fase 3 (23/10/2026) corrigiu os dois e tirou as marcas.

Perfil (emenda 2): financeira (~2 ms) roda sempre os 500 exemplos do §3; industrial (~0,06 s sem os Ke/g implícitos) roda o
perfil curto na suíte do dia a dia e os 500 só com `python -m oraculo --completo` (ORACULO_PERFIL=completo).
Os Ke/g implícitos (busca de 70 passos cada) não entram em central nem em palavra; nos industriais eles são trocados por None
para caber no tempo (`_rapido`). O resto de `avaliar` roda inteiro.
"""
import copy
import math
import os
from contextlib import ExitStack, contextmanager
from dataclasses import replace
from functools import cache
from unittest import mock

import pytest
from hypothesis import HealthCheck, Phase, given, seed, settings, strategies as st

import mercado
import motor_financeiras as F
import motor_nao_financeiras as M
from oraculo import sanidade as S

SEMENTE = 20261022
COMPLETO = os.environ.get("ORACULO_PERFIL") == "completo"
N_IND = 500 if COMPLETO else 12
N_FIN = 500
DECISAO = ("BARATA", "RADAR", "JUSTA")
PALAVRAS = (*F.ORDEM, "NÃO CONCLUSIVO")
TOL_PF = 1e-4      # o ponto fixo do WACC para em |ΔE/E| < 1e-5 (TOL_PONTO_FIXO): ruído relativo do central dessa ordem
# campo crítico (VALIDACAO §5) → chaves da série; dívida = as três linhas da bruta
CRITICOS = {"caixa": ("caixa",), "divida": ("emprest_cp", "emprest_lp"), "pl": ("pl",), "lucro": ("lucro", "lucro_controlador"),
            "receita": ("receita",), "da": ("da",), "imobilizado": ("imobilizado",)}
# H10 medida em 22/10 (preço a 0,8 × central, 21 industriais): caixa 14, dívida 14, PL 9, D&A 18 e imobilizado 16 tickers saem
# com palavra de decisão; lucro e receita já viram recusa. Fase 3 (23/10): os cinco viram NÃO CONCLUSIVO (`M.criticos_ausentes`);
# a lista fica para o teste nomeado da H10 cobrir exatamente os campos que eram abertos
H10_ABERTOS = ["caixa", "da", "divida", "imobilizado", "pl"]

MK = mercado.vigente()


def _cfg(n, **kw):
    return settings(max_examples=n, deadline=None, database=None, derandomize=False,
                    suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much], **kw)


@cache
def _empresas():
    return S.empresas()


def _ind():
    return sorted(t for t, e in _empresas().items() if isinstance(e, M.Industrial))


def _fin():
    return sorted(t for t, e in _empresas().items() if isinstance(e, F.Financeira))


@contextmanager
def _rapido():
    with mock.patch.object(M, "ke_implicito", lambda *a, **k: None), mock.patch.object(M, "g_implicito", lambda *a, **k: None):
        yield


@contextmanager
def _serie(tk, nova):
    """Troca a série CVM do ticker só dentro do bloco; o cache da idade do imobilizado é por ticker e é limpo nas duas pontas."""
    M.idade_e_fator.cache_clear()
    try:
        with mock.patch.dict(M.CVM, {tk: nova}):
            yield
    finally:
        M.idade_e_fator.cache_clear()


def _avaliar(emp, mk=MK):
    """Resultado do motor ou None quando ele recusa com erro explícito (NÃO CONCLUSIVO legítimo)."""
    try:
        if isinstance(emp, F.Financeira):
            return F.avaliar(emp, mk)
        with _rapido():
            return M.avaliar(emp, mk)
    except (ValueError, NotImplementedError, RuntimeError, ZeroDivisionError):
        return None


@cache
def _base(tk):
    r = _avaliar(_empresas()[tk])
    assert r is not None, f"{tk}: o motor recusou a avaliação de base"
    return r


def _central(r):
    return r["central"] if r is not None else None


def _nao_sobe(novo, velho):
    return novo <= velho + TOL_PF * abs(velho) + 1e-9


def _rank(p):
    return F.ORDEM.index(p)


# ================================================================ Ke ↑ ⇒ central não sobe
@seed(SEMENTE)
@_cfg(N_IND)
@given(tk=st.sampled_from(_ind()), dp=st.floats(0.002, 0.05))
def test_ke_maior_nao_sobe_o_central_industrial(tk, dp):
    """Prêmio do acionista maior (o Hamada multiplica a constante de 5 p.p.); Kd fica igual — só o Ke se move."""
    emp = _empresas()[tk]
    c0 = _central(_base(tk))
    with mock.patch.object(M, "PREMIO_KE", M.PREMIO_KE + dp):
        c1 = _central(_avaliar(emp))
    if c1 is not None:
        assert _nao_sobe(c1, c0), (tk, dp, c0, c1)


@seed(SEMENTE)
@_cfg(N_FIN)
@given(tk=st.sampled_from(_fin()), drf=st.floats(0.0, 0.05), dp=st.floats(0.0, 0.05))
def test_ke_maior_nao_sobe_o_central_financeira(tk, drf, dp):
    emp = _empresas()[tk]
    c0 = _central(_base(tk))
    c1 = _central(_avaliar(emp, replace(MK, rf_real=MK.rf_real + drf, premio=MK.premio + dp)))
    if c1 is not None:
        assert _nao_sobe(c1, c0), (tk, drf, dp, c0, c1)


# ================================================================ fluxo ↑ ⇒ central não cai
@seed(SEMENTE)
@_cfg(N_IND)
@given(tk=st.sampled_from(_ind()), dm=st.floats(0.002, 0.05))
def test_fluxo_maior_nao_baixa_o_central_industrial(tk, dm):
    """Margem normalizada maior nos três cenários (p25, mediana, p75) = mais fluxo operacional pela mesma receita."""
    emp = _empresas()[tk]
    c0 = _central(_base(tk))
    orig = M.premissas_operacionais

    def mais(e):
        op = orig(e)
        return dict(op, m25=op["m25"] + dm, m50=op["m50"] + dm, m75=op["m75"] + dm)
    with mock.patch.object(M, "premissas_operacionais", mais):
        c1 = _central(_avaliar(emp))
    if c1 is not None:
        assert _nao_sobe(c0, c1), (tk, dm, c0, c1)


@seed(SEMENTE)
@_cfg(N_FIN)
@given(tk=st.sampled_from(_fin()), d=st.floats(0.001, 0.10))
def test_fluxo_maior_nao_baixa_o_central_financeira(tk, d):
    """ROE de longo prazo e de partida maiores = mais lucro pelo mesmo patrimônio."""
    emp = _empresas()[tk]
    c0 = _central(_base(tk))
    c1 = _central(_avaliar(replace(emp, roe_lp=emp.roe_lp + d, roe_inicio=emp.roe_inicio + d)))
    if c1 is not None:
        assert _nao_sobe(c0, c1), (tk, d, c0, c1)


# ================================================================ central não depende do preço
@seed(SEMENTE)
@_cfg(N_IND)
@given(tk=st.sampled_from(_ind()), f=st.floats(0.2, 5.0))
def test_central_nao_depende_do_preco_industrial(tk, f):
    emp = _empresas()[tk]
    r = _avaliar(replace(emp, preco=emp.preco * f))
    assert r is not None
    assert r["central"] == pytest.approx(_base(tk)["central"], rel=1e-12), (tk, f)


@seed(SEMENTE)
@_cfg(N_FIN)
@given(tk=st.sampled_from(_fin()), f=st.floats(0.2, 5.0))
def test_central_nao_depende_do_preco_financeira(tk, f):
    emp = _empresas()[tk]
    r = _avaliar(replace(emp, preco=emp.preco * f))
    assert r["central"] == pytest.approx(_base(tk)["central"], rel=1e-12), (tk, f)


# ================================================================ desdobramento (k ações por 1): central ÷ k, mesma palavra
@seed(SEMENTE)
@_cfg(N_IND)
@given(tk=st.sampled_from(_ind()), k=st.sampled_from([0.1, 0.25, 0.5, 2.0, 3.0, 4.0, 10.0]))
def test_desdobramento_industrial(tk, k):
    """Todo dado POR AÇÃO de fora da CVM (DPA da B3/StatusInvest, provento por ação do ajuste da B3, reprodução por ação) também
    é ajustado pelo desdobramento — como as fontes fazem; o que está em R$ mil não muda."""
    emp = _empresas()[tk]
    novo = replace(emp, preco=emp.preco / k, n_acoes=emp.n_acoes * k,
                   reproducao_por_acao=emp.reproducao_por_acao / k if emp.reproducao_por_acao else emp.reproducao_por_acao)
    si = dict(M.SI[tk], dpa_por_ano_datacom={a: x / k for a, x in M.SI[tk]["dpa_por_ano_datacom"].items()})
    b3 = M.ajuste_b3
    with mock.patch.dict(M.SI, {tk: si}), \
         mock.patch.object(M, "ajuste_b3", lambda t, n, *a, **kw: b3(t, n / k, *a, **kw)):
        r = _avaliar(novo)
    r0 = _base(tk)
    assert r is not None
    assert r["central"] * k == pytest.approx(r0["central"], rel=TOL_PF), (tk, k)
    assert r["palavra"] == r0["palavra"], (tk, k)


@seed(SEMENTE)
@_cfg(N_FIN)
@given(tk=st.sampled_from(_fin()), k=st.floats(0.1, 10.0))
def test_desdobramento_financeira(tk, k):
    emp = _empresas()[tk]
    sotp = emp.sotp
    novo = replace(emp, preco=emp.preco / k, vpa=emp.vpa / k, lpa_12m=emp.lpa_12m / k, dpa_medio_5a=emp.dpa_medio_5a / k,
                   sotp=(lambda mk: sotp(mk) / k) if sotp is not None else None)
    r, r0 = _avaliar(novo), _base(tk)
    assert r["central"] * k == pytest.approx(r0["central"], rel=1e-9), (tk, k)
    assert r["palavra"] == r0["palavra"], (tk, k)


# ================================================================ permutação
@seed(SEMENTE)
@_cfg(N_IND)
@given(tk=st.sampled_from(_ind()), data=st.data())
def test_ordem_dos_exercicios_na_serie_nao_muda_nada_industrial(tk, data):
    """A ordem em que os exercícios aparecem no dicionário da série não pode mudar central nem palavra."""
    serie = M.CVM[tk]
    anos = data.draw(st.permutations(list(serie["anual"])))
    nova = dict(serie, anual={a: serie["anual"][a] for a in anos})
    with _serie(tk, nova):
        r = _avaliar(_empresas()[tk])
    r0 = _base(tk)
    assert r["central"] == pytest.approx(r0["central"], rel=1e-12), (tk, anos)
    assert r["palavra"] == r0["palavra"]


@seed(SEMENTE)
@_cfg(max(N_IND // 2, 6))
@given(ordem=st.permutations(_ind()[:3] + _fin()[:3]))
def test_ordem_de_avaliacao_do_universo_nao_muda_nada(ordem):
    """Avaliar as empresas em outra ordem dá o mesmo resultado (nenhum estado vaza de uma avaliação para a outra)."""
    for tk in ordem:
        r = _avaliar(_empresas()[tk])
        assert r["central"] == pytest.approx(_base(tk)["central"], rel=1e-12), (tk, ordem)
        assert r["palavra"] == _base(tk)["palavra"]


def test_ordem_das_ancoras_nao_muda_o_central():
    for tk in _ind() + _fin():
        anc = _base(tk)["ancoras"]
        invertido = dict(reversed(list(anc.items())))
        assert M.central_de(invertido)[0] == M.central_de(anc)[0] == pytest.approx(_base(tk)["central"], rel=1e-12)


# ================================================================ preço ↑ nunca melhora a palavra
def _par_de_precos(motor):
    return dict(tk=st.sampled_from(motor()), f1=st.floats(0.3, 2.0), df=st.floats(0.001, 1.0))


def _confere_preco(tk, f1, df):
    emp, c = _empresas()[tk], _base(tk)["central"]
    if not (c > 0):
        return
    r1, r2 = _avaliar(replace(emp, preco=f1 * c)), _avaliar(replace(emp, preco=(f1 + df) * c))
    if r1 is None or r2 is None:
        return
    assert _rank(r2["palavra_regua"]) >= _rank(r1["palavra_regua"]), (tk, f1, df)
    # a trava de coerência (§9) pode tirar a JUSTA para NÃO CONCLUSIVO: entre palavras da régua, a ordem tem de valer
    if r1["palavra"] in F.ORDEM and r2["palavra"] in F.ORDEM:
        assert _rank(r2["palavra"]) >= _rank(r1["palavra"]), (tk, f1, df, r1["palavra"], r2["palavra"])


@seed(SEMENTE)
@_cfg(N_IND)
@given(**_par_de_precos(_ind))
def test_preco_maior_nunca_melhora_a_palavra_industrial(tk, f1, df):
    _confere_preco(tk, f1, df)


@seed(SEMENTE)
@_cfg(N_FIN)
@given(**_par_de_precos(_fin))
def test_preco_maior_nunca_melhora_a_palavra_financeira(tk, f1, df):
    _confere_preco(tk, f1, df)


# ================================================================ sem NaN/inf no que é publicado
def _confere_finito(r):
    if r is None:
        return
    assert r["palavra"] in PALAVRAS
    c = r["central"]
    assert isinstance(c, float) and math.isfinite(c), c
    for k, x in r["ancoras"].items():
        assert math.isfinite(x), k
    assert math.isfinite(r["pc"]) or (r["pc"] == math.inf and c <= 0)
    assert math.isfinite(r["dispersao"]) or r["palavra"] == "NÃO CONCLUSIVO"
    for k in ("compra", "compra_parcial", "saida"):
        assert r[k] is None or math.isfinite(r[k]), k
    for k, x in r["notas"].items():
        assert math.isfinite(x), k
    if r["palavra"] in DECISAO:
        assert c > 0 and math.isfinite(r["pc"])


@seed(SEMENTE)
@_cfg(N_IND)
@given(tk=st.sampled_from(_ind()), dp=st.floats(-0.02, 0.05), dm=st.floats(-0.03, 0.03), f=st.floats(0.2, 5.0))
def test_sem_nan_nem_inf_industrial(tk, dp, dm, f):
    emp = _empresas()[tk]
    orig = M.premissas_operacionais

    def mexe(e):
        op = orig(e)
        return dict(op, m25=op["m25"] + dm, m50=op["m50"] + dm, m75=op["m75"] + dm)
    with mock.patch.object(M, "PREMIO_KE", M.PREMIO_KE + dp), mock.patch.object(M, "premissas_operacionais", mexe):
        _confere_finito(_avaliar(replace(emp, preco=emp.preco * f)))


@seed(SEMENTE)
@_cfg(N_FIN)
@given(tk=st.sampled_from(_fin()), drf=st.floats(-0.03, 0.05), droe=st.floats(-0.10, 0.10), f=st.floats(0.2, 5.0))
def test_sem_nan_nem_inf_financeira(tk, drf, droe, f):
    emp = _empresas()[tk]
    _confere_finito(_avaliar(replace(emp, preco=emp.preco * f, roe_lp=emp.roe_lp + droe, roe_inicio=emp.roe_inicio + droe),
                             replace(MK, rf_real=MK.rf_real + drf)))


# ================================================================ g < Ke (toda perpetuidade de Gordon converge)
@seed(SEMENTE)
@_cfg(N_IND)
@given(tk=st.sampled_from(_ind()), g=st.floats(-0.05, F.PIB_REAL_LP),
       rf=st.floats(0.03, 0.09))
def test_g_menor_que_ke_industrial(tk, g, rf):
    """g real perpétuo no domínio da doutrina (≤ PIB real de LP, §11.1) e rf real de 3% a 9%: se o motor publica palavra,
    o g usado está abaixo do WACC real (DCF) e do Ke real (OE)."""
    emp = replace(_empresas()[tk], g_real=g)
    r = _avaliar(emp, replace(MK, rf_real=rf))
    if r is None or r["palavra"] == "NÃO CONCLUSIVO":
        return
    assert r["gr"] < r["wacc_real"], (tk, g, rf, r["wacc_real"])
    assert r["gr"] < r["ke_real_emp"], (tk, g, rf, r["ke_real_emp"])


@seed(SEMENTE)
@_cfg(N_FIN)
@given(tk=st.sampled_from(_fin()), roe=st.floats(0.0, 0.45), payout=st.floats(0.0, 1.0), rf=st.floats(0.0, 0.12))
def test_g_menor_que_ke_financeira(tk, roe, payout, rf):
    emp = replace(_empresas()[tk], roe_lp=roe, roe_inicio=roe, payout=payout)
    mk = replace(MK, rf_real=rf)
    assert F.g_perpetuo(emp, mk) < mk.ke_nom


# ================================================================ a nota não decide a palavra (§10, D10.09; Piotroski/Beneish D10.05)
QUAL = st.fixed_dictionaries({k: st.integers(0, 5) for k in F.CHAVES_QUAL})


@seed(SEMENTE)
@_cfg(N_IND)
@given(tk=st.sampled_from(_ind()), q=QUAL, pf=st.integers(0, 9), mb=st.floats(-5.0, 2.0))
def test_nota_nao_decide_a_palavra_industrial(tk, q, pf, mb):
    """Notas qualitativas quaisquer e Piotroski/Beneish quaisquer: central e palavra iguais; Piotroski e Beneish nem mexem na nota."""
    emp = _empresas()[tk]
    pio, ben = M.piotroski, M.beneish
    with mock.patch.object(M, "piotroski", lambda d, p: (pf, pio(d, p)[1])), mock.patch.object(M, "beneish", lambda d, p: mb):
        r_s = _avaliar(emp)
    r0 = _base(tk)
    assert (r_s["central"], r_s["palavra"]) == (r0["central"], r0["palavra"])
    assert r_s["notas"] == r0["notas"], "Piotroski/Beneish entraram na nota"
    r_q = _avaliar(replace(emp, qualitativo=q))
    assert (r_q["central"], r_q["palavra"]) == (r0["central"], r0["palavra"]), (tk, q)


@seed(SEMENTE)
@_cfg(N_FIN)
@given(tk=st.sampled_from(_fin()), q=QUAL)
def test_nota_nao_decide_a_palavra_financeira(tk, q):
    emp = _empresas()[tk]
    r, r0 = _avaliar(replace(emp, qualitativo=q)), _base(tk)
    assert (r["central"], r["palavra"]) == (r0["central"], r0["palavra"]), (tk, q)


# ================================================================ Graham-BR e teto de renda nunca são âncora (§11.2, D11.2.08)
PROIBIDAS = ("graham", "teto", "bazin", "peg", "bogle")


@seed(SEMENTE)
@_cfg(N_FIN)
@given(tk=st.sampled_from(_ind() + _fin()), drf=st.floats(-0.03, 0.05))
def test_graham_e_teto_de_renda_nunca_sao_ancora(tk, drf):
    emp = _empresas()[tk]
    r = _avaliar(emp, replace(MK, rf_real=MK.rf_real + drf)) if isinstance(emp, F.Financeira) else _base(tk)
    if r is None:
        return
    assert not [k for k in r["ancoras"] if any(p in k.lower() for p in PROIBIDAS)], r["ancoras"].keys()
    # e o Graham-BR exibido não é o central nem entra nele: mexer no fator de Graham não move o central
    if isinstance(emp, F.Financeira):
        with mock.patch.object(F.Mercado, "fator_graham", property(lambda s: 99.0)):
            r2 = _avaliar(emp, replace(MK, rf_real=MK.rf_real + drf))
        assert r2["central"] == r["central"]


# ================================================================ âncora única ⇒ confiança baixa (§11.3, D11.3.08)
@seed(SEMENTE)
@_cfg(N_FIN)
@given(tk=st.sampled_from(_fin()), anos=st.integers(1, 15), prob=st.floats(0.0, 1.0), hc=st.floats(0.0, 0.9))
def test_ancora_unica_tem_confianca_baixa(tk, anos, prob, hc):
    """Financeira com contrato finito tem uma âncora só: a confiança nunca é 'normal'."""
    emp = replace(_empresas()[tk], horizonte_finito=dict(anos=anos, prob_renovacao=prob, haircut_renov=hc), sotp=None)
    r = _avaliar(emp)
    if r is None:
        return
    assert len(r["ancoras"]) == 1
    assert r["confianca"] != "normal", r["confianca"]


def test_industrial_sempre_tem_ao_menos_duas_ancoras():
    for tk in _ind():
        assert len(_base(tk)["ancoras"]) >= 2, tk


# ================================================================ Focus só como sensibilidade declarada (§4, D4.08)
def test_focus_nunca_e_o_mercado_dos_lotes():
    """O mercado que gera palavra (o dos lotes e o vigente) nunca é o do Focus; o Focus só existe como cenário rotulado."""
    import importlib
    vig, foc = mercado.vigente(), mercado.focus()
    assert foc.pi != vig.pi and "π" in foc.data
    for m in S.LOTES:
        mod = importlib.import_module(m)
        mk = getattr(mod, "MK", None)
        if mk is not None:
            assert mk.pi == vig.pi and mk.rf_real == vig.rf_real, m


# ================================================================ H10: dado crítico ausente ⇒ nunca palavra de decisão
def _sem_campo(serie, chaves):
    nova = copy.deepcopy(serie)
    for bloco in [nova["anual"][a] for a in nova["anual"]] + [nova[k] for k in ("ltm", "ltm_2T26") if k in nova]:
        for c in chaves:
            bloco.pop(c, None)
    return nova


def _confere_ausente(tk, campo, f):
    """Tira o campo de TODOS os períodos da série (anual e LTM) e põe o preço a f × o central que o motor ainda calcular: se
    houver central, a palavra sai de decisão (f ≤ 1,05 ⇒ BARATA/RADAR/JUSTA) — é o número publicado como se fosse medido.
    Qualquer exceção conta como recusa explícita (nenhuma palavra sai)."""
    def av(e):
        try:
            with _rapido():
                return M.avaliar(e, MK)
        except Exception:
            return None
    emp = _empresas()[tk]
    with _serie(tk, _sem_campo(M.CVM[tk], CRITICOS[campo])):
        r = av(emp)
        if r is None or not (r["central"] > 0):
            return
        r = av(replace(emp, preco=f * r["central"]))
    assert r is None or r["palavra"] not in DECISAO, (tk, campo, f, r["palavra"])


@seed(SEMENTE)
@_cfg(max(N_IND, 20))
@given(tk=st.sampled_from(_ind()), campo=st.sampled_from(sorted(set(CRITICOS) - set(H10_ABERTOS))), f=st.floats(0.5, 1.05))
def test_dado_critico_ausente_nunca_da_palavra_de_decisao(tk, campo, f):
    """Os campos críticos que já viram recusa explícita (lucro, receita): um zero silencioso NOVO neles quebra este teste."""
    _confere_ausente(tk, campo, f)


@seed(SEMENTE)
@_cfg(max(N_IND, 20), phases=[Phase.explicit, Phase.reuse, Phase.generate])
@given(tk=st.sampled_from(_ind()), campo=st.sampled_from(H10_ABERTOS), f=st.floats(0.5, 1.05))
def test_h10_dado_critico_ausente_nunca_da_palavra_de_decisao(tk, campo, f):
    """H10 (Fase 3, 23/10): os campos que davam zero silencioso agora viram NÃO CONCLUSIVO (`M.criticos_ausentes`)."""
    _confere_ausente(tk, campo, f)


# ================================================================ §5 (D5.09): o desconto do controlador entra uma vez, no valor
@seed(SEMENTE)
@_cfg(N_FIN)
@given(tk=st.sampled_from(_fin()), pct=st.floats(0.01, 0.5))
def test_desconto_do_controlador_so_no_valor_financeira(tk, pct):
    """Desconto fixo: o central cai exatamente (1 − pct) e Ke, g e as notas que não são de preço ficam iguais."""
    emp = _empresas()[tk]
    if emp.desconto_controlador["tipo"] != "zero":
        return
    r0 = _base(tk)
    r = _avaliar(replace(emp, desconto_controlador={"tipo": "fixo", "pct": pct, "razao": "propriedade"}))
    assert r["central"] == pytest.approx(r0["central"] * (1 - pct), rel=1e-12)
    assert (r["ke"], r["g"]) == (r0["ke"], r0["g"])
    assert {k: r["notas"][k] for k in ("qualidade", "solidez")} == {k: r0["notas"][k] for k in ("qualidade", "solidez")}


@seed(SEMENTE)
@_cfg(max(N_IND // 2, 6))
@given(tk=st.sampled_from(_ind()), pct=st.floats(0.05, 0.5))
def test_desconto_do_controlador_so_no_valor_industrial(tk, pct):
    emp = _empresas()[tk]
    if emp.desconto_controlador["tipo"] != "zero":
        return
    r0 = _base(tk)
    r = _avaliar(replace(emp, desconto_controlador={"tipo": "fixo", "pct": pct, "razao": "propriedade"}))
    assert r["ke_nom_emp"] == pytest.approx(r0["ke_nom_emp"], rel=1e-9), (tk, pct)
    assert r["notas"]["qualidade"] == pytest.approx(r0["notas"]["qualidade"], rel=1e-9), (tk, pct)
    if all(x > 0 for x in r0["ancoras"].values()):      # com o E do ponto fixo igual, o central cai exatamente (1 − pct)
        assert r["central"] == pytest.approx(r0["central"] * (1 - pct), rel=1e-9), (tk, pct)


def test_h10_zero_declarado_continua_valendo_e_ausente_vira_nao_conclusivo():
    """Ausente ≠ zero (VALIDACAO §5): caixa = 0 informado pela fonte não é recusa; caixa sem a chave no LTM é."""
    tk = _ind()[0]
    serie = copy.deepcopy(M.CVM[tk])
    ltm = M.ltm_de(serie)
    assert M.criticos_ausentes(tk) == []
    for chave, esperado in ((0.0, []), (None, ["caixa"])):
        ltm2 = dict(ltm)
        if chave is None:
            ltm2.pop("caixa", None)
        else:
            ltm2["caixa"] = chave
        with mock.patch.object(M, "serie", lambda t, _l=ltm2: (serie["anual"], _l)):
            assert M.criticos_ausentes(tk) == esperado
    # dívida: só é ausente sem CP E sem LP (empresa sem LP informa só a CP)
    ltm3 = {k: x for k, x in ltm.items() if k != "emprest_lp"}
    with mock.patch.object(M, "serie", lambda t: (serie["anual"], ltm3)):
        assert M.criticos_ausentes(tk) == []
    ltm4 = {k: x for k, x in ltm3.items() if k != "emprest_cp"}
    with mock.patch.object(M, "serie", lambda t: (serie["anual"], ltm4)):
        assert M.criticos_ausentes(tk) == ["divida"]


def test_h10_razao_do_nao_conclusivo_nomeia_o_campo():
    tk = next(t for t in _ind() if _base(t)["palavra"] != "NÃO CONCLUSIVO")
    with _serie(tk, _sem_campo(M.CVM[tk], ("imobilizado",))):
        r = _avaliar(_empresas()[tk])
    assert r["palavra"] == "NÃO CONCLUSIVO" and r["dado_critico_ausente"][0] == "imobilizado"   # LTM; depois os anos (O3b)
    assert "dado crítico ausente: imobilizado" in r["confianca"]



@seed(SEMENTE)
@_cfg(max(N_IND, 20))
@given(tk=st.sampled_from(_ind()), campo=st.sampled_from(M.CRITICOS_ANO), i=st.integers(0, 9), f=st.floats(0.5, 1.05))
def test_o3b_campo_ausente_num_exercicio_da_janela_nunca_da_palavra_de_decisao(tk, campo, i, f):
    """O3b: o campo some de UM exercício da janela das âncoras (o LTM fica) → nunca BARATA/RADAR/JUSTA."""
    anos = M.premissas_operacionais(_empresas()[tk])["anos"]
    ano = anos[i % len(anos)]
    nova = copy.deepcopy(M.CVM[tk])
    nova["anual"][ano].pop(campo, None)
    emp = _empresas()[tk]
    with _serie(tk, nova):
        r = _avaliar(emp)
        if r is None or not (r["central"] > 0):
            return
        r = _avaliar(replace(emp, preco=f * r["central"]))
    assert r is None or r["palavra"] not in DECISAO, (tk, campo, ano, f, r["palavra"])
    assert r is None or f"{campo} ({ano})" in r["dado_critico_ausente"]



def test_o3b_ebit_ausente_no_ltm_falha_alto():
    """EBIT sem chave no LTM não vira zero: o motor recusa com erro (nenhuma palavra sai)."""
    tk = _ind()[0]
    nova = copy.deepcopy(M.CVM[tk])
    nova["ltm"].pop("ebit", None)
    with _serie(tk, nova), pytest.raises(KeyError):
        with _rapido():
            M.avaliar(_empresas()[tk], MK)
