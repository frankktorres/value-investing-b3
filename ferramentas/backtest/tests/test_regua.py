"""Portão da fatia 11: a régua reimplementada reproduz palavra e central dos 41 do golden.

Ler `golden.json` aqui é legítimo: é teste, não runtime do backtest (test_isolamento varre só os
módulos). As âncoras do golden já vêm com o desconto do controlador, e o preço é `pc × central`.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from backtest.config import PADRAO
from backtest.motor.regua import (BARATA, CARA, JUSTA, NAO_CONCLUSIVO, NIVEL, RADAR, avaliar_bt,
                                  palavra_da_escala)

GOLDEN = Path(__file__).resolve().parents[2] / "tests" / "golden.json"


def _golden() -> dict:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))["tickers"]


def test_golden_tem_41():
    assert len(_golden()) == 41


@pytest.mark.parametrize("ticker", sorted(_golden()))
def test_reproduz_palavra_e_central_do_golden(ticker):
    g = _golden()[ticker]
    preco = g["pc"] * g["central"] if math.isfinite(g["pc"]) else 1.0
    v = avaliar_bt(g["ancoras"], preco)
    assert v.palavra == g["palavra"]
    assert v.central == pytest.approx(g["central"], abs=0.01)
    if math.isfinite(g["pc"]):
        assert v.pc == pytest.approx(g["pc"], abs=0.005)
    else:
        assert math.isinf(v.pc)


def test_bordas_da_escala():
    assert palavra_da_escala(0.70) == BARATA
    assert palavra_da_escala(0.7000001) == RADAR
    assert palavra_da_escala(0.90) == RADAR
    assert palavra_da_escala(1.10) == JUSTA
    assert palavra_da_escala(1.1000001) == CARA


def test_dispersao_desce_so_o_lado_favoravel():
    # dispersão 2,0 (> 1,8, < 3): BARATA vira RADAR, CARA fica
    v = avaliar_bt({"a": 10.0, "b": 15.0, "c": 20.0}, preco=9.0)       # pc 0,6
    assert (v.palavra_escala, v.palavra, v.confianca) == (BARATA, RADAR, "baixa")
    v = avaliar_bt({"a": 10.0, "b": 15.0, "c": 20.0}, preco=12.0)      # pc 0,8
    assert v.palavra == JUSTA
    v = avaliar_bt({"a": 10.0, "b": 15.0, "c": 20.0}, preco=30.0)      # pc 2
    assert v.palavra == CARA


def test_dispersao_acima_de_3_e_ancora_nao_positiva_sao_nao_conclusivo():
    assert avaliar_bt({"a": 10.0, "b": 15.0, "c": 31.0}, 5.0).palavra == NAO_CONCLUSIVO
    assert avaliar_bt({"a": 10.0, "b": 15.0, "c": 30.0}, 5.0).palavra != NAO_CONCLUSIVO
    v = avaliar_bt({"a": -1.0, "b": 15.0, "c": 20.0}, 5.0)
    assert v.palavra == NAO_CONCLUSIVO and math.isinf(v.dispersao)


def test_central_nao_positivo_da_pc_infinito():
    v = avaliar_bt({"a": -5.0, "b": -1.0, "c": 2.0}, 5.0)
    assert math.isinf(v.pc) and v.palavra == NAO_CONCLUSIVO


def test_fora_do_circulo_tem_teto_radar():
    assert avaliar_bt({"a": 10.0, "b": 10.5}, 5.0, fora_circulo=True).palavra == RADAR
    assert avaliar_bt({"a": 10.0, "b": 10.5}, 15.0, fora_circulo=True).palavra == CARA


def test_numeros_vem_da_config():
    from dataclasses import replace
    cfg = replace(PADRAO, palavra_barata=0.50)
    assert avaliar_bt({"a": 10.0, "b": 10.0}, 6.0, cfg).palavra == RADAR
    assert avaliar_bt({"a": 10.0, "b": 10.0}, 6.0).palavra == BARATA


def test_niveis_ordenados_e_nc_sem_nivel():
    assert [NIVEL[p] for p in (BARATA, RADAR, JUSTA, CARA)] == [0, 1, 2, 3]
    assert NAO_CONCLUSIVO not in NIVEL
