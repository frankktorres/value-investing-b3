"""O3b (H10): provento da StatusInvest sem valor não entra como 0 no DPA por ano — fica em `eventos_sem_valor`."""
import json

import montar_series as ms


def test_provento_sem_valor_nao_soma_zero(tmp_path, monkeypatch):
    dia = tmp_path / "2026-10-07"
    dia.mkdir()
    (dia / "ZZZZ3_indicadores.json").write_text(json.dumps({"data": {"x": []}}), encoding="utf-8")
    (dia / "ZZZZ3_proventos.json").write_text(json.dumps({"assetEarningsModels": [
        {"et": "Dividendo", "v": 1.0, "ed": "10/05/2025"},
        {"et": "JCP", "v": None, "ed": "10/06/2025"},
        {"et": "JCP", "v": 0.5, "ed": "10/07/2025"}]}), encoding="utf-8")
    (dia / "ZZZZ3_pagina.json").write_text(json.dumps({"preco": "10,00"}), encoding="utf-8")
    monkeypatch.setattr(ms, "RAW", tmp_path)
    s = ms.series("ZZZZ3", "2026-10-07")
    assert s["dpa_por_ano_datacom"] == {2025: 1.5} and s["jcp_por_ano_datacom"] == {2025: 0.5}
    assert [e["data_com"] for e in s["eventos_sem_valor"]] == ["10/06/2025"]
