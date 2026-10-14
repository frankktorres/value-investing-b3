"""Registro prospectivo: append-only, idempotente, e recusa reescrever o passado."""
import json
import math

import pytest

import registro_prospectivo as rp
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


# ---------------------------------------------------------------- B25 (14/10/2026): pré-registro AUD-32/98/99, uma regra por teste
def _l(tk, data="2026-10-02", origem="hall", pc=1.0, registrado="2026-10-02", palavra="CARA"):
    return {"origem": origem, "data_preco": data, "ticker": tk, "pc": pc, "palavra": palavra, "registrado_em": registrado}


def test_b25_postos_com_empates_e_ic():
    assert rp._postos([10, 20, 20, 30]) == [1, 2.5, 2.5, 4]
    assert rp.ic_postos([1, 2, 3, 4], [40, 30, 20, 10]) == pytest.approx(-1.0)
    assert rp.ic_postos([1, 2, 3], [5, 5, 5]) is None          # um lado sem variação
    assert rp.ic_postos([1, 2, 2, 3], [1, 2, 3, 4]) == pytest.approx(0.9486833, abs=1e-6)


def test_b25_dossie_vence_hall_na_mesma_rodada_e_rodadas_distintas_ficam():
    reg = [_l("HYPE3", pc=0.9), _l("HYPE3", origem="dossie", pc=1.2), _l("HYPE3", data="2026-10-06", origem="dossie", pc=1.1)]
    v = rp.linhas_validas(reg)
    assert [(x["data_preco"], x["origem"], x["pc"]) for x in v] == [("2026-10-02", "dossie", 1.2), ("2026-10-06", "dossie", 1.1)]
    # ordem de gravação não importa
    assert rp.linhas_validas(list(reversed(reg))) == v


def test_b25_linha_registrada_depois_do_pregao_e_retroativa():
    v = rp.linhas_validas([_l("A", registrado="2026-10-06"), _l("B")])
    assert {x["ticker"]: x["retroativa"] for x in v} == {"A": True, "B": False}


def test_b25_comparador_e_a_media_simples_do_hall_no_mesmo_periodo():
    reg = [_l("A"), _l("B"), _l("C"), _l("X", data="2026-10-06", origem="dossie")]
    ret = {"A": 0.10, "B": 0.20, "C": 0.60, "X": 0.50}
    # o retorno depende do período: no período do X (06/10) o hall rendeu o dobro — o comparador tem de usar o período do X
    f = lambda tk, i, fim: ret[tk] * (2 if i == "2026-10-06" and tk != "X" else 1)
    ex = {e["ticker"]: e for e in rp.excedentes(reg, f, hoje="2027-12-31")}
    assert ex["A"]["media_hall"] == pytest.approx(0.30) and ex["A"]["excedente"] == pytest.approx(-0.20)
    assert ex["X"]["fim"] == "2027-10-06"                       # dossiê compara com o hall da rodada anterior, no SEU período
    assert ex["X"]["media_hall"] == pytest.approx(0.60) and ex["X"]["excedente"] == pytest.approx(-0.10)


def test_b25_horizonte_nao_vencido_nao_entra():
    assert rp.excedentes([_l("A")], lambda *a: 0.1, hoje="2027-10-01") == []
    assert len(rp.excedentes([_l("A")], lambda *a: 0.1, hoje="2027-10-02")) == 1


def _rodadas(ics_sinal, n=12, pc_none=0):
    """Registro sintético: uma rodada por ano; P/C 1..n; retorno crescente (sinal +1) ou decrescente (−1) no P/C."""
    reg, ret = [], {}
    for k, s in enumerate(ics_sinal):
        data = f"{2020 + k}-01-0{1 + k % 2}"
        for i in range(n):
            tk = f"T{k}_{i}"
            reg.append(_l(tk, data=data, pc=None if i < pc_none else float(i + 1), registrado=data))
            ret[tk] = s * (i + 1) / 100
    return reg, (lambda tk, ini, fim: ret[tk])


def test_b25_rodada_pequena_fica_fora_do_ic():
    reg, ret = _rodadas([-1], n=rp.N_MIN_IC - 1)
    r = rp.avaliar(reg, ret, hoje="2030-01-01")
    assert r["rodadas"] == [] and r["fora_do_ic"][0]["n"] == rp.N_MIN_IC - 1


def test_b25_pc_ausente_sai_do_ic_e_e_contado():
    reg, ret = _rodadas([-1], n=12, pc_none=2)
    r = rp.avaliar(reg, ret, hoje="2030-01-01")
    assert r["rodadas"][0]["n"] == 10 and r["rodadas"][0]["excluidas"] == 2
    assert r["rodadas"][0]["ic"] == pytest.approx(-1.0)


def test_b25_leitura_exige_4_rodadas_e_segue_o_sinal():
    reg, ret = _rodadas([-1, -1, -1])
    assert rp.avaliar(reg, ret, hoje="2030-01-01")["leitura"].startswith("inconclusiva")
    reg, ret = _rodadas([-1] * 7 + [1])
    r = rp.avaliar(reg, ret, hoje="2030-01-01")
    assert r["ic_medio"] == pytest.approx(-0.75) and r["t"] == pytest.approx(-3.0) and r["leitura"].startswith("apoia")
    reg, ret = _rodadas([-1] * 4)                               # IC idêntico em todas: sem dispersão, t = −inf
    r = rp.avaliar(reg, ret, hoje="2030-01-01")
    assert r["t"] == -math.inf and r["leitura"].startswith("apoia")
    reg, ret = _rodadas([1, 1, -1, 1])
    assert rp.avaliar(reg, ret, hoje="2030-01-01")["leitura"].startswith("contraria")
    reg, ret = _rodadas([-1, 1, -1, 1, -1])
    assert rp.avaliar(reg, ret, hoje="2030-01-01")["leitura"].startswith("inconclusiva: IC médio < 0")


@pytest.mark.parametrize("ruim", [float("nan"), float("inf"), None])
def test_b25_retorno_nan_inf_ou_none_e_ausente_e_contado(ruim):
    """Revisão adversarial de 14/10: um NaN na média do hall virava a leitura de "apoia" para "contraria"."""
    reg, ret = _rodadas([-1] * 4)
    estragado = lambda tk, i, f: ruim if tk.endswith("_5") else ret(tk, i, f)
    r = rp.avaliar(reg, estragado, hoje="2030-01-01")
    assert r["ic_medio"] == pytest.approx(-1.0) and r["leitura"].startswith("apoia")
    assert all(x["n"] == 11 and x["excluidas"] == 1 and x["hall_sem_retorno"] == 1 for x in r["rodadas"])


def test_b25_origem_desconhecida_levanta():
    with pytest.raises(ValueError, match="origem desconhecida"):
        rp.linhas_validas([_l("A"), _l("A", origem="manual")])


def test_b25_sem_retroativas_devolve_a_vez_ao_hall():
    reg = [_l(f"T{i}", pc=float(i)) for i in range(10)] + [_l("T0", origem="dossie", pc=5.0, registrado="2026-10-09")]
    assert next(x for x in rp.linhas_validas(reg) if x["ticker"] == "T0")["origem"] == "dossie"
    v = rp.linhas_validas(reg, sem_retroativas=True)
    assert len(v) == 10 and next(x for x in v if x["ticker"] == "T0")["origem"] == "hall"


def test_b25_sensibilidade_sem_retroativas():
    reg, ret = _rodadas([-1] * 4)
    reg = [{**l, "registrado_em": "2030-01-01"} if l["ticker"].startswith("T0_") else l for l in reg]
    assert len(rp.avaliar(reg, ret, hoje="2030-01-01")["rodadas"]) == 4
    assert len(rp.avaliar(reg, ret, hoje="2030-01-01", sem_retroativas=True)["rodadas"]) == 3


def test_b25_registro_real_uma_linha_por_ticker_e_rodada():
    reg = rp.ler()
    v = rp.linhas_validas(reg)
    chaves = [(x["data_preco"], x["ticker"]) for x in v]
    assert len(chaves) == len(set(chaves)) == len({(l["data_preco"], l["ticker"]) for l in reg})
    hype = next(x for x in v if x["ticker"] == "HYPE3" and x["data_preco"] == "2026-10-02")
    assert hype["origem"] == "dossie"
    assert all(x["retroativa"] for x in v if x["origem"] == "hall")   # hall de 02/10 registrado em 06/10
