"""Registro prospectivo: append-only, idempotente, e recusa reescrever o passado."""
import json
import math

import pytest

from registro_prospectivo import ler, registrar, registrar_dossies


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


def _veredito(pasta, tk, pc=1.3, preco=25.16):
    v = {"ticker": tk, "data_preco": "2026-10-02", "preco": preco, "central": 19.27, "pc": pc,
         "palavra": "CARA", "doutrina": "v2.2"}
    (pasta / f"{tk}-2026-10-02.json").write_text(json.dumps(v), encoding="utf-8")


def test_dossie_nao_colide_com_o_hall(tmp_path):
    reg = tmp_path / "r.jsonl"
    registrar("2026-10-02", "v2.2", _golden(tmp_path), reg)
    ved = tmp_path / "ved"
    ved.mkdir()
    _veredito(ved, "AAAA3")                                  # mesmo ticker e data do hall
    _veredito(ved, "HYPE3")
    assert registrar_dossies(ved, reg, hoje="2026-10-07") == 2
    assert registrar_dossies(ved, reg, hoje="2026-10-08") == 0   # idempotente
    ls = ler(reg)
    assert len(ls) == 4
    assert {l["origem"] for l in ls if l["ticker"] == "AAAA3"} == {"hall", "dossie"}


def test_dossie_recusa_reescrever_e_linha_antiga_vale_hall(tmp_path):
    reg = tmp_path / "r.jsonl"
    ved = tmp_path / "ved"
    ved.mkdir()
    _veredito(ved, "HYPE3")
    registrar_dossies(ved, reg)
    _veredito(ved, "HYPE3", pc=1.1)
    with pytest.raises(ValueError, match="append-only"):
        registrar_dossies(ved, reg)
    # linha antiga (sem `origem`) conta como "hall": registrar de novo o hall não duplica
    antigo = tmp_path / "a.jsonl"
    registrar("2026-10-02", "v2.2", _golden(tmp_path), antigo)
    ls = [{k: v for k, v in l.items() if k != "origem"} for l in ler(antigo)]
    antigo.write_text("".join(json.dumps(l) + "\n" for l in ls), encoding="utf-8")
    from registro_prospectivo import _caminho_corrente, _corrente, _linhas_cruas
    _caminho_corrente(antigo).write_text("".join(e + "\n" for e in _corrente(_linhas_cruas(antigo))), encoding="utf-8")
    assert registrar("2026-10-02", "v2.2", _golden(tmp_path), antigo) == 0


def test_dossie_duplicata_na_rodada_cosmetica_e_inf(tmp_path):
    reg = tmp_path / "r.jsonl"
    ved = tmp_path / "ved"
    ved.mkdir()
    _veredito(ved, "HYPE3")
    (ved / "HYPE3-2026-10-02-rev.json").write_text(
        (ved / "HYPE3-2026-10-02.json").read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(ValueError, match="duas vezes"):
        registrar_dossies(ved, reg)
    assert ler(reg) == []                                    # nada gravado
    (ved / "HYPE3-2026-10-02-rev.json").unlink()
    registrar_dossies(ved, reg)
    v = json.loads((ved / "HYPE3-2026-10-02.json").read_text(encoding="utf-8"))
    v["parecer_frank"] = "concorda"                          # mudança que não é veredito
    (ved / "HYPE3-2026-10-02.json").write_text(json.dumps(v, indent=4), encoding="utf-8")
    _veredito(ved, "NOVO3")
    assert registrar_dossies(ved, reg) == 1
    with pytest.raises(FileNotFoundError):
        registrar_dossies(tmp_path / "nada", reg)
    v["pc"] = math.inf
    (ved / "INF3-2026-10-02.json").write_text(json.dumps({**v, "ticker": "INF3"}), encoding="utf-8")
    registrar_dossies(ved, reg)
    assert "Infinity" not in reg.read_text(encoding="utf-8")


def test_aud108_sha_do_golden_nao_depende_do_eol(tmp_path):
    """AUD-108: o mesmo conteúdo em LF e em CRLF (autocrlf do Windows) tem de dar o mesmo golden_sha."""
    import hashlib

    from registro_prospectivo import sha_arquivo
    lf = b'{"a": 1,\n "b": 2}\n'
    crlf = lf.replace(b"\n", b"\r\n")
    assert sha_arquivo(lf) == sha_arquivo(crlf) == hashlib.sha256(lf).hexdigest()[:16]
    g_lf, g_crlf = tmp_path / "lf.json", tmp_path / "crlf.json"
    corpo = _golden(tmp_path).read_bytes()
    g_lf.write_bytes(corpo.replace(b"\r\n", b"\n"))
    g_crlf.write_bytes(corpo.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
    registrar("2026-10-02", "v2.2", g_lf, tmp_path / "a.jsonl", hoje="2026-10-06")
    registrar("2026-10-02", "v2.2", g_crlf, tmp_path / "b.jsonl", hoje="2026-10-06")
    assert {l["golden_sha"] for l in ler(tmp_path / "a.jsonl")} == {l["golden_sha"] for l in ler(tmp_path / "b.jsonl")}


def test_aud102_corrente_acusa_adulteracao_do_passado(tmp_path):
    """AUD-102: editar, apagar ou inserir linha antiga tem de ser acusado; o registro intacto passa."""
    from registro_prospectivo import verificar
    reg = tmp_path / "r.jsonl"
    registrar("2026-10-02", "v2.2", _golden(tmp_path), reg)
    registrar("2026-11-02", "v2.2", _golden(tmp_path, pc=1.5), reg)
    assert verificar(reg) == []
    original = reg.read_text(encoding="utf-8")
    reg.write_text(original.replace('"CARA"', '"BARATA"', 1), encoding="utf-8")      # CARA → BARATA
    assert verificar(reg) != []
    reg.write_text("\n".join(original.splitlines()[1:]) + "\n", encoding="utf-8")     # apaga a 1ª linha
    assert verificar(reg) != []
    reg.write_text(original + original.splitlines()[0] + "\n", encoding="utf-8")      # acrescenta à mão
    assert verificar(reg) != []
    with pytest.raises(ValueError, match="adulterado"):
        registrar("2027-01-04", "v2.2", _golden(tmp_path), reg)                       # nova data não "lava" o passado
    reg.write_text(original, encoding="utf-8")
    assert registrar("2027-01-04", "v2.2", _golden(tmp_path), reg) == 2
    assert verificar(reg) == []


def test_aud102_registro_real_integro():
    """O registro versionado confere com a corrente versionada."""
    from registro_prospectivo import verificar
    assert verificar() == []


def test_aud82_preco_oficial_vence_o_produto_arredondado(tmp_path):
    """AUD-82: com o snapshot da data, o preço gravado é o fechamento (inclusive onde a P/C é ∞, como RECV3)."""
    import precos_hall
    reg = tmp_path / "r.jsonl"
    g = {"motivo": "t", "tickers": {
        "PRIO3": {"palavra": "CARA", "pc": 1.5, "central": 40.0, "lote": 5},
        "RECV3": {"palavra": "NÃO CONCLUSIVO", "pc": math.inf, "central": -0.2, "lote": 5}}}
    p = tmp_path / "g.json"
    p.write_text(json.dumps(g), encoding="utf-8")
    registrar(precos_hall.PRECO_DATA, "v2.5", p, reg, hoje="2026-10-09")
    snap = precos_hall.ler()
    por = {l["ticker"]: l["preco"] for l in ler(reg)}
    assert por == {"PRIO3": snap["PRIO3"], "RECV3": snap["RECV3"]} and por["RECV3"] is not None
    reg2 = tmp_path / "r2.jsonl"
    registrar("2026-11-06", "v2.5", p, reg2, hoje="2026-11-06")             # data sem snapshot: cai no produto
    por2 = {l["ticker"]: l["preco"] for l in ler(reg2)}
    assert por2 == {"PRIO3": 60.0, "RECV3": None}
