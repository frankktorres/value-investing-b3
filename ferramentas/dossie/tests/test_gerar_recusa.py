"""Poka-yoke do dossie.gerar: veredito já registrado no prospectivo não pode ser regravado (lição de 10/10/2026)."""
import json

from dossie import gerar


def _registro(tmp_path, *linhas):
    f = tmp_path / "registro.jsonl"
    f.write_text("\n".join(json.dumps(x) for x in linhas) + "\n", encoding="utf-8")
    return f


def test_registrado_e_reconhecido(tmp_path):
    f = _registro(tmp_path, {"origem": "dossie", "ticker": "HYPE3", "data_preco": "2026-10-02"})
    assert gerar.ja_registrado("HYPE3", "2026-10-02", f)


def test_outra_data_outro_ticker_ou_outra_origem_nao_bloqueia(tmp_path):
    f = _registro(tmp_path, {"origem": "dossie", "ticker": "HYPE3", "data_preco": "2026-10-02"},
                  {"origem": "hall", "ticker": "TIMS3", "data_preco": "2026-10-10"})
    assert not gerar.ja_registrado("HYPE3", "2026-10-10", f)
    assert not gerar.ja_registrado("BLAU3", "2026-10-02", f)
    assert not gerar.ja_registrado("TIMS3", "2026-10-10", f)


def test_sem_registro_nao_bloqueia(tmp_path):
    assert not gerar.ja_registrado("HYPE3", "2026-10-02", tmp_path / "nao_existe.jsonl")


def test_main_recusa_sem_gravar(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(gerar, "calcular", lambda tk, data=None: {"data": "2026-10-02"})
    monkeypatch.setattr(gerar, "ja_registrado", lambda tk, data, registro=None: True)
    assert gerar.main(["HYPE3"]) == 2
    assert "RECUSADO" in capsys.readouterr().err
