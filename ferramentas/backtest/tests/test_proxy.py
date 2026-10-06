"""Regras do portão do proxy em casos sintéticos — declaradas antes da 1ª rodada."""
from __future__ import annotations

import math

from backtest.config import PADRAO
from backtest.experimento.proxy import baselines, comparar, portao

INF = math.inf


def test_um_nivel_e_nc():
    assert comparar("CARA", 2.0, "CARA", 2.1) == (True, True, 0.10000000000000009)
    assert comparar("CARA", 2.0, "JUSTA", 1.0)[:2] == (False, True)
    assert comparar("CARA", 2.0, "RADAR", 0.8)[:2] == (False, False)
    assert comparar("NÃO CONCLUSIVO", 1.05, "CARA", 1.2)[:2] == (False, False)
    assert comparar("CARA", 1.2, "NÃO CONCLUSIVO", 1.2)[:2] == (False, False)
    assert comparar("NÃO CONCLUSIVO", 1.05, "NÃO CONCLUSIVO", 1.10)[:2] == (True, True)


def test_excluido_e_erro_e_delta_infinito():
    assert comparar("CARA", 2.0, None, None) == (False, False, INF)


def test_infinito_dos_dois_lados_e_zero_de_um_lado_e_infinito():
    assert comparar("NÃO CONCLUSIVO", INF, "NÃO CONCLUSIVO", INF)[2] == 0.0
    assert comparar("NÃO CONCLUSIVO", INF, "CARA", 2.0)[2] == INF
    assert comparar("CARA", 2.0, "NÃO CONCLUSIVO", INF)[2] == INF


def _l(gp, gpc, pp, ppc, disp=1.5):
    e, u, d = comparar(gp, gpc, pp, ppc)
    return {"golden_palavra": gp, "golden_pc": gpc, "exata": e, "um_nivel": u, "delta_pc": d,
            "proxy_dispersao": disp if pp else None, "ingenuo_palavra": None, "ingenuo_pc": None}


def test_portao_conta_excluido_no_denominador():
    ls = [_l("CARA", 2.0, "CARA", 2.05)] * 8 + [_l("CARA", 2.0, None, None)] * 2
    pt = portao(ls)
    assert pt["n"] == 10 and pt["concordancia"] == 0.8 and pt["criterio_palavra"]
    assert pt["mediana_delta_pc"] < 0.06 and pt["passou"]
    ls = ls[:7] + [_l("CARA", 2.0, None, None)] * 3
    assert not portao(ls)["criterio_palavra"] and not portao(ls)["passou"]


def test_portao_falha_pelo_pc_mesmo_com_palavra_certa():
    ls = [_l("CARA", 2.0, "CARA", 2.5)] * 10
    pt = portao(ls)
    assert pt["criterio_palavra"] and not pt["criterio_pc"] and not pt["passou"]
    assert PADRAO.proxy_delta_pc_max == 0.15 and PADRAO.proxy_concordancia_min == 0.80


def test_baseline_sempre_cara_e_nao_degeneracao():
    ls = [_l("CARA", 2.0, "CARA", 2.0)] * 3 + [_l("JUSTA", 1.0, "JUSTA", 1.0),
                                                _l("RADAR", 0.8, "RADAR", 0.8, disp=1.0)]
    b = baselines(ls)
    assert (b["sempre_cara_exata"], b["sempre_cara_um_nivel"]) == (3, 4)
    assert (b["nao_cara_n"], b["nao_cara_exata"]) == (2, 2)
    assert b["dispersao_maior_que_1"] == "4/5" and not b["nao_degeneracao_ok"]
