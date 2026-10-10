"""Onda 3 da auditoria de 08/10/2026 — dados que armavam o ITR 3T26 (AUD-68).

A CVM entrega 3.11.01 (lucro do controlador) = 0 em exercícios em que só a linha 3.11 foi preenchida, e as ações do LTM
vinham do DFP do ano anterior (o desdobramento 5:1 da SBSP3 entre mar e jun/2026 não aparecia).
"""
import json
import pathlib

import coletar_cvm as cc
from ltm import ltm_de

SERIES = pathlib.Path(__file__).parent.parent / "dados" / "cvm_series.json"


def test_aud68_zero_do_controlador_com_lucro_e_sem_dado():
    assert cc.sanear_lucro_controlador({"lucro": 8.0, "lucro_controlador": 0.0})["lucro_controlador"] is None
    assert cc.sanear_lucro_controlador({"lucro": 0.0, "lucro_controlador": 0.0})["lucro_controlador"] == 0.0
    assert cc.sanear_lucro_controlador({"lucro": 8.0, "lucro_controlador": 7.5})["lucro_controlador"] == 7.5
    assert cc.sanear_lucro_controlador({"receita": 1.0}) == {"receita": 1.0}         # balanço/DFC não ganham chave


def test_aud68_exercicio_sem_dado_vira_lacuna_no_ltm_e_nao_soma_so_o_semestre():
    fy = cc.sanear_lucro_controlador({"lucro": 8.0, "lucro_controlador": 0.0})
    ltm, lacunas, _ = cc.combinar_ltm(fy, {"lucro": 3.0, "lucro_controlador": 3.0}, {"lucro": 3.0, "lucro_controlador": 0.0})
    assert "lucro_controlador" not in ltm and "lucro_controlador" in lacunas
    assert ltm["lucro"] == 8.0


def test_aud68_acoes_do_ltm_vem_do_itr():
    ltm, _, _ = cc.combinar_ltm({"acoes": 700.0}, {"acoes": 3506.0}, {})
    assert ltm["acoes"] == 3506.0
    ltm, _, _ = cc.combinar_ltm({"acoes": 700.0}, {}, {})
    assert ltm["acoes"] == 700.0                                                   # ITR sem composição: fica o DFP


def test_aud68_series_vigente_sem_controlador_zerado_e_sbsp3_pos_desdobramento():
    d = json.loads(SERIES.read_text(encoding="utf-8"))
    zerados = [(tk, a) for tk, reg in d.items() for a, x in [*reg.get("anual", {}).items(), ("ltm", ltm_de(reg))]
               if x.get("lucro_controlador") == 0 and x.get("lucro")]
    assert zerados == []
    # LTM com o exercício sem dado vira lacuna (adversário 10/10: o da KLBN11 ficou −973 mi, conta com 2025 zerado)
    for tk, reg in d.items():
        fy = reg["anual"].get("2026" if tk == "SMTO3" else "2025", {})
        if fy.get("lucro_controlador") is None:
            assert "lucro_controlador" not in ltm_de(reg), tk
    s = ltm_de(d["SBSP3"])
    assert s["acoes"] > 3.4e9 and "lucro_controlador" not in s
