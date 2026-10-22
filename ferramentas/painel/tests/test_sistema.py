"""Contrato da tela Sistema (N4): idade de cada dado, boletins, golden e suíte — só lê o que existe; faltou → None com motivo."""
import json

import pytest

from painel import contrato, sistema


@pytest.fixture()
def ferr(tmp_path):
    f = tmp_path / "ferramentas"
    (f / "dados" / "cvm").mkdir(parents=True)
    (f / "dados" / "proventos_hall").mkdir()
    (f / "monitor").mkdir()
    (f / "tests").mkdir()
    (tmp_path / "BOLETINS").mkdir()
    return f


def _preenche(f):
    (f / "dados" / "cvm" / "MANIFESTO.json").write_text(json.dumps({"atualizado_em": "2026-10-19", "arquivos": {}}), encoding="utf-8")
    (f / "dados" / "cvm_series.json").write_text(json.dumps({"A": {"ltm_ref": "2T26"}, "B": {"ltm_ref": "2T26"}}), encoding="utf-8")
    (f / "dados" / "proventos_hall" / "A.json").write_text(json.dumps({"baixado_em": "2026-10-08"}), encoding="utf-8")
    (f / "dados" / "proventos_hall" / "B.json").write_text(json.dumps({"baixado_em": "2026-10-15"}), encoding="utf-8")
    (f / "monitor" / "historico.csv").write_text("rodada,pregao\n2026-10-09,2026-10-08\n2026-10-16,2026-10-15\n", encoding="utf-8")
    (f.parent / "BOLETINS" / "2026-10-16-monitor.md").write_text("x", encoding="utf-8")
    (f.parent / "BOLETINS" / "2026-10-23-temporada.md").write_text("x", encoding="utf-8")
    (f / "tests" / "golden.json").write_text(json.dumps({"motivo": "B30: P/L", "tickers": {"A": {}, "B": {}}}), encoding="utf-8")
    (f / "tests" / "golden_log.md").write_text("- 2026-10-08 20:43 — antigo\n- 2026-10-20 12:00 — B30: P/L\n", encoding="utf-8")


def test_idade_de_cada_dado(ferr):
    _preenche(ferr)
    d = {x["chave"]: x for x in sistema.dados("2026-10-22", "2026-10-20", ferr)}
    assert (d["cotahist"]["data"], d["cotahist"]["idade_dias"]) == ("2026-10-20", 2)
    assert (d["cvm"]["data"], d["cvm"]["idade_dias"]) == ("2026-10-19", 3) and "2T26" in d["cvm"]["obs"]
    assert (d["proventos_b3"]["data"], d["proventos_b3"]["idade_dias"]) == ("2026-10-08", 14)   # o mais antigo manda
    assert "2 tickers" in d["proventos_b3"]["obs"]
    assert (d["monitor"]["data"], d["monitor"]["idade_dias"]) == ("2026-10-16", 6)
    assert d["temporada"]["data"] == "2026-10-23"


def test_montar_boletins_golden_e_suite(ferr):
    _preenche(ferr)
    (ferr / "dados" / "suite_ultima.json").write_text(json.dumps({"data": "2026-10-22", "passed": 937, "failed": 0, "skipped": 42}),
                                                      encoding="utf-8")
    s = sistema.montar("2026-10-22", "2026-10-20", ferr)
    assert s["boletins"]["monitor"] == {"arquivo": "2026-10-16-monitor.md", "data": "2026-10-16"}
    assert s["boletins"]["temporada"]["data"] == "2026-10-23"
    assert s["golden"] == {"data": "2026-10-20", "hora": "12:00", "motivo": "B30: P/L", "tickers": 2}
    assert s["suite"]["passed"] == 937 and s["avisos"] == []


def test_tudo_ausente_vira_none_com_motivo_sem_quebrar(ferr):
    s = sistema.montar("2026-10-22", None, ferr)
    assert all(x["data"] is None and x["idade_dias"] is None and sistema.SEM_REGISTRO in x["obs"] for x in s["dados"])
    assert s["boletins"] == {"monitor": None, "temporada": None}
    assert s["golden"] is None and s["suite"] is None and s["avisos"]


def test_json_quebrado_nao_derruba(ferr):
    (ferr / "dados" / "cvm" / "MANIFESTO.json").write_text("{quebrado", encoding="utf-8")
    (ferr / "tests" / "golden.json").write_text("[1]", encoding="utf-8")
    (ferr / "dados" / "suite_ultima.json").write_text("{}", encoding="utf-8")
    s = sistema.montar("2026-10-22", None, ferr)
    assert s["golden"] is None and s["suite"] is None


def test_data_invalida_nao_gera_idade():
    assert sistema._idade("ontem", "2026-10-22") is None and sistema._idade(None, "2026-10-22") is None


def test_sem_dado_pessoal_no_sistema(ferr):
    _preenche(ferr)
    txt = json.dumps(sistema.montar("2026-10-22", "2026-10-20", ferr), ensure_ascii=False).lower()
    assert "quantidade" not in txt and "preco_medio" not in txt and "corretora" not in txt


def test_gerar_grava_sistema_json_no_contrato():
    import inspect
    assert "sistema.json" in inspect.getsource(contrato.gerar)
