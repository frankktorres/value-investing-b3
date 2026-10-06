"""Registro prospectivo: append-only, idempotente, e recusa reescrever o passado."""
import json
import math

import pytest

from registro_prospectivo import ler, registrar


def _golden(tmp_path, pc=2.0, central=10.0):
    g = {"motivo": "t", "tickers": {
        "AAAA3": {"palavra": "CARA", "pc": pc, "central": central, "lote": 1},
        "BBBB3": {"palavra": "NÃO CONCLUSIVO", "pc": math.inf, "central": -0.2, "lote": 2}}}
    p = tmp_path / "golden.json"
    p.write_text(json.dumps(g), encoding="utf-8")
    return p


def test_registra_e_e_idempotente(tmp_path):
    reg = tmp_path / "r.jsonl"
    g = _golden(tmp_path)
    assert registrar("2026-10-02", "v2.2", g, reg, hoje="2026-10-06") == 2
    assert registrar("2026-10-02", "v2.2", g, reg, hoje="2026-10-07") == 0
    ls = ler(reg)
    assert len(ls) == 2
    a = next(l for l in ls if l["ticker"] == "AAAA3")
    assert a["preco"] == 20.0 and a["doutrina"] == "v2.2"
    b = next(l for l in ls if l["ticker"] == "BBBB3")
    assert b["preco"] is None and b["pc"] is None          # ∞ não vira JSON inválido


def test_recusa_reescrever_a_mesma_data(tmp_path):
    reg = tmp_path / "r.jsonl"
    registrar("2026-10-02", "v2.2", _golden(tmp_path), reg)
    with pytest.raises(ValueError, match="append-only"):
        registrar("2026-10-02", "v2.2", _golden(tmp_path, pc=1.5), reg)
    assert registrar("2027-04-01", "v2.2", _golden(tmp_path, pc=1.5), reg) == 2
    assert len(ler(reg)) == 4
