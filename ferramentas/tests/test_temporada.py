"""Testes da ferramenta da temporada (F8): série sintética, nada de rede."""
import io
import zipfile

import pytest

import coletar_cvm as cc
import temporada as T
from ltm import ltm_de, ltm_ref_de


def _zip_itr(linhas):
    """ZIP mínimo de ITR com a DRE consolidada: linhas = [(CD_CVM, DT_REFER)]."""
    csv = "CD_CVM;DENOM_CIA;DT_REFER;ORDEM_EXERC;CD_CONTA;VL_CONTA;ESCALA_MOEDA\n"
    for cd, dt in linhas:
        csv += f"{cd};EMPRESA {cd};{dt};ÚLTIMO;3.01;100;MIL\n"
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("itr_cia_aberta_DRE_con_2026.csv", csv.encode("latin-1"))
    return zipfile.ZipFile(io.BytesIO(buf.getvalue()))


EMP = {"AAAA3": ("cvm:000001", 1), "BBBB3": ("cvm:000002", 1), "CCCC3": ("cvm:000003", 1)}


def test_detecta_quem_publicou_o_trimestre():
    z = _zip_itr([("000001", "2026-06-30"), ("000001", "2026-09-30"), ("000002", "2026-06-30")])
    pub, aus, sem = T.quem_publicou(z, ["AAAA3", "BBBB3", "CCCC3", "ZZZZ3"], "2026-09-30", EMP)
    assert pub == ["AAAA3"]
    assert aus == ["BBBB3", "CCCC3"]
    assert sem == ["ZZZZ3"]          # sem regra de coleta CVM


def test_trimestre_que_ja_existe_e_detectado_na_simulacao():
    z = _zip_itr([("000001", "2026-06-30"), ("000002", "2026-06-30")])
    assert T.quem_publicou(z, ["AAAA3", "BBBB3", "CCCC3"], "2026-06-30", EMP)[0] == ["AAAA3", "BBBB3"]


def test_interpretar_trimestre():
    assert T.interpretar_trimestre("3T26") == (2026, 9, "2026-09-30")
    assert T.interpretar_trimestre("2t26") == (2026, 6, "2026-06-30")
    with pytest.raises(ValueError):
        T.interpretar_trimestre("4T26")      # 4T vem na DFP
    from datetime import date
    assert T.trimestre_atual(date(2026, 10, 8)) == "3T26"
    assert T.trimestre_atual(date(2026, 2, 1)) == "3T25"


def test_rotulo_ltm_do_coletor():
    assert cc.rotulo_ltm(2026, 6) == "2T26"
    assert cc.rotulo_ltm(2026, 9) == "3T26"


def test_compatibilidade_ltm_generico_e_ltm_2t26():
    antigo = {"anual": {}, "ltm_2T26": {"receita": 1}}
    novo = {"anual": {}, "ltm": {"receita": 2}, "ltm_ref": "3T26", "ltm_3T26": {"receita": 2}}
    assert ltm_de(antigo) == {"receita": 1} and ltm_ref_de(antigo) == "2T26"
    assert ltm_de(novo) == {"receita": 2} and ltm_ref_de(novo) == "3T26"
    assert ltm_de({"ltm": {"receita": 3}, "ltm_2T26": {"receita": 1}}) == {"receita": 3}   # a genérica vence


def test_motor_le_ltm_generico_e_cai_no_antigo():
    import motor_nao_financeiras as M
    M.CVM["TESTETEMP"] = {"anual": {"2025": {"receita": 1}}, "ltm_2T26": {"receita": 10}}
    try:
        assert M.serie("TESTETEMP")[1] == {"receita": 10}
        M.CVM["TESTETEMP"]["ltm"] = {"receita": 20}
        assert M.serie("TESTETEMP")[1] == {"receita": 20}
    finally:
        del M.CVM["TESTETEMP"]


def test_causas_margem_divida_receita():
    a = {"receita": 1000.0, "ebit": 100.0, "emprest_cp": 50.0, "emprest_lp": 150.0, "lucro": 80.0}
    n = {"receita": 1100.0, "ebit": 220.0, "emprest_cp": 100.0, "emprest_lp": 300.0, "lucro": 120.0}
    c = T.causas(a, n)
    assert c["receita_pct"] == pytest.approx(0.10)
    assert c["margem_pp"] == pytest.approx(10.0)
    assert c["divida_pct"] == pytest.approx(1.0)
    assert "n/d" in T.linha_causas(T.causas({}, {}))


def test_boletim_sem_mudanca():
    txt = T.montar_boletim("2026-11-10", "3T26", ["AAAA3"], ["BBBB3"], ["ZZZZ3"], [], {}, set())
    assert "Publicaram o ITR de 3T26: **1** (AAAA3)" in txt
    assert "Nenhuma mudança" in txt
    assert "--motivo" in txt                      # aviso: golden só é regravado com motivo
    assert "trocas de palavra" not in txt


def test_boletim_com_troca_de_palavra_e_causas():
    mud = [("AAAA3", "palavra", "AGUARDAR", "COMPRAR"), ("AAAA3", "central", 10.0, 14.0), ("AAAA3", "âncora OE", 9.0, 13.0)]
    c = {"AAAA3": T.causas({"receita": 100.0, "ebit": 10.0}, {"receita": 120.0, "ebit": 30.0})}
    txt = T.montar_boletim("2026-11-10", "3T26", ["AAAA3"], [], [], mud, c, {3})
    assert "1 trocas de palavra" in txt and "AGUARDAR → COMPRAR" in txt
    assert "| AAAA3 | âncora OE | 9.0000 | 13.0000 |" in txt
    assert "margem EBIT +" in txt and "gerar_pdf_lote3.py" in txt


def test_sem_itr_novo_sai_com_codigo_0(monkeypatch, tmp_path, capsys):
    """Fluxo completo com tudo simulado: nenhum ticker com o trimestre → mensagem e código 0, sem boletim."""
    monkeypatch.setattr(T, "baixar_itr", lambda ano: _gravar_zip(tmp_path))
    monkeypatch.setattr(T.cc, "CACHE", tmp_path)
    monkeypatch.setattr(T.cc, "EMPRESAS", {})   # ninguém tem regra de coleta → ninguém publica
    rc = T.main(["--trimestre", "3T26", "--saida", str(tmp_path / "b")])
    assert rc == 0
    assert "nenhum ticker com 3T26 ainda" in capsys.readouterr().out
    assert not (tmp_path / "b").exists()


def _gravar_zip(pasta):
    f = pasta / "itr_2026.zip"
    f.write_bytes(b"")
    with zipfile.ZipFile(f, "w") as z:
        z.writestr("itr_cia_aberta_DRE_con_2026.csv", "CD_CVM;DT_REFER\n")
    return f


def test_boletim_avisa_coleta_que_falhou():
    txt = T.montar_boletim("2026-11-10", "3T26", ["AAAA3", "BBBB3"], [], [], [], {}, set(), falhas=["BBBB3"])
    assert "coleta falhou" in txt and "BBBB3" in txt.split("coleta falhou")[1][:80]


def test_injetar_troca_so_o_ltm_e_preserva_anual(monkeypatch):
    import types
    import sys
    mod = types.ModuleType("fake_lote")
    mod.CVM = {"AAAA3": {"anual": {"2025": {"arrendamento_pago": 7.0}}, "ltm_2T26": {"receita": 1.0}}}
    monkeypatch.setitem(sys.modules, "fake_lote", mod)
    novo = {"AAAA3": {"anual": {"2025": {}}, "ltm": {"receita": 2.0}, "ltm_ref": "3T26"}}
    antigos = T.injetar(novo)
    assert antigos == {"AAAA3": {"receita": 1.0}}
    assert mod.CVM["AAAA3"]["anual"]["2025"]["arrendamento_pago"] == 7.0      # correção do lote preservada
    assert ltm_de(mod.CVM["AAAA3"]) == {"receita": 2.0} and ltm_ref_de(mod.CVM["AAAA3"]) == "3T26"
