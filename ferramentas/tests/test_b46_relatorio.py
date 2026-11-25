"""B46: a leitura pela regra da emenda 12 (C1–C4 → PASSA / FALHA / NÃO CONCLUSIVA) sobre um JSON sintético."""
from __future__ import annotations

import copy

from b46 import relatorio as R

RF, PI = 0.0756, 0.0717


def _ke(de, t=0.34):
    # à mão: (1 + rf real + 5 p.p. × [1 + (1 − t) × D/E]) × (1 + π) − 1
    return (1 + RF + 0.05 * (1 + (1 - t) * de)) * (1 + PI) - 1


def _linha(tk, de_m, de_ind, r_i, pi_i, z, r_ii, pi_ii, central=10.0):
    pi = (pi_i + pi_ii) / 2
    sem = {"EPV": 8.0, "DCF (3 cenários)": 12.0}
    com = {k: v * (1 - pi) for k, v in sem.items()}
    de_c = min(de_m, de_ind)
    comp = dict(erro=None, central=central * (1 - pi), pc=1.0, palavra="CARA", ke_nom=_ke(de_c), rf_real=RF, pi_inflacao=PI,
                t=0.34, de_cont=de_c, de_mercado=de_m, de_ind=de_ind, industria="Steel", rating_i=r_i, pi_i=pi_i, z=z,
                rating_ii=r_ii, pi_ii=pi_ii, pi=pi, concordam=abs(pi_i - pi_ii) <= 0.2, anc_sem_pi=sem, anc_com_pi=com)
    de = dict(comp, central=central, anc_sem_pi=dict(sem), anc_com_pi=dict(sem), pi=0.0)
    base = dict(erro=None, central=central * 0.9, pc=1.2, palavra="CARA", ke_nom=0.45)
    ch = {"preco_0.7": dict(comp), "preco_1.3": dict(comp), "divida_1.1": dict(comp, central=comp["central"] * 0.97)}
    return dict(tk=tk, grupo="b36", financeira=False, base=base, de=de, completo=comp, choques=ch)


def _res():
    return dict(linhas=[
        # B- (42,12%) e Z'' 4,0 → B- (42,12%): concordam
        _linha("AAA1", 11.75, 0.509, "B-", 0.4212, 4.0, "B-", 0.4212),
        # CC (66,6%) e Z'' 5,76 → BBB (7,54%): discordam (Δ 59 p.p.)
        _linha("BBB2", 10.0, 0.588, "CC", 0.666, 5.76, "BBB", 0.0754),
        # CCC (59,02%) e Z'' 2,6 → CCC (59,02%): concordam
        _linha("CCC3", 3.3, 0.704, "CCC", 0.5902, 2.6, "CCC", 0.5902),
        dict(tk="BANC4", grupo="hall", financeira=True)])


def test_passa_com_2_de_3_concordantes():
    res = _res()
    assert R.c1(res)["passou"] and R.c2(res)["passou"] and R.c4(res)["passou"]
    r3 = R.c3(res)
    assert (r3["n"], len(r3["concordam"])) == (3, 2)
    assert R.leitura(R.c1(res), R.c2(res), r3, R.c4(res)) == "PASSA"


def test_nao_conclusiva_quando_c3_cai():
    res = _res()
    res["linhas"][2] = _linha("CCC3", 3.3, 0.704, "CCC", 0.5902, 5.76, "BBB", 0.0754)   # agora 1 de 3
    assert R.leitura(R.c1(res), R.c2(res), R.c3(res), R.c4(res)) == "NÃO CONCLUSIVA"


def test_falha_quando_ke_nao_bate_com_a_formula():
    res = _res()
    res["linhas"][0]["completo"]["ke_nom"] += 0.001
    assert not R.c1(res)["passou"]
    assert R.leitura(R.c1(res), R.c2(res), R.c3(res), R.c4(res)) == "FALHA"


def test_falha_quando_preco_mexe_no_central_acima_do_limite():
    res = _res()
    res["linhas"][0]["choques"]["preco_0.7"] = dict(res["linhas"][0]["completo"], central=res["linhas"][0]["completo"]["central"] * 1.02)
    r2 = R.c2(res)
    assert not r2["passou"] and "preco_0.7" in r2["falhas"][0]


def test_central_nao_positivo_que_nao_muda_passa_e_que_muda_falha():
    # emenda 12, C2a: "mudam o central em no máximo 0,5%" — 0 → 0 e −2,77 → −2,77 não mudam; −2,77 → −2,70 muda (relativo
    # indefinido com central ≤ 0 → reprova)
    res = _res()
    for n in ("preco_0.7", "preco_1.3"):
        res["linhas"][0]["choques"][n] = dict(res["linhas"][0]["completo"], central=0.0)
    res["linhas"][0]["completo"]["central"] = 0.0
    res["linhas"][0]["choques"]["divida_1.1"]["central"] = 0.0
    assert R.c2(res)["passou"]
    res["linhas"][0]["completo"]["central"] = -2.77
    for n in ("preco_0.7", "preco_1.3"):
        res["linhas"][0]["choques"][n]["central"] = -2.77
    res["linhas"][0]["choques"]["divida_1.1"]["central"] = -2.80
    assert R.c2(res)["passou"]
    res["linhas"][0]["choques"]["preco_0.7"]["central"] = -2.70
    assert not R.c2(res)["passou"]


def test_falha_quando_mais_divida_sobe_o_central_acima_do_limite():
    res = _res()
    res["linhas"][1]["choques"]["divida_1.1"] = dict(res["linhas"][1]["completo"], central=res["linhas"][1]["completo"]["central"] * 1.01)
    assert not R.c2(res)["passou"]


def test_vazio_sem_razao_reprova_c4():
    res = _res()
    res["linhas"][0]["completo"] = dict(erro=dict(tipo="não avaliado", mensagem=""))
    assert not R.c4(res)["passou"]
    res2 = _res()
    res2["linhas"][0]["completo"] = dict(erro=dict(tipo="não avaliado", mensagem="AAA1: sem indústria"))
    assert R.c4(res2)["passou"] and R.c4(res2)["nao_avaliados"]


def test_relatorio_tem_a_leitura_e_as_tres_secoes():
    txt = R.gerar(copy.deepcopy(_res()))
    assert "Leitura pela regra: **PASSA**" in txt
    assert "financeira — não se aplica" in txt and "## Dossiês" in txt and "## B36" in txt
