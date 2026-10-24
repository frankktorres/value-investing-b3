"""N12: a data de cada fonte de verdade chega ao produto (`Origem.data`) só onde um arquivo do repo a declara.

COTAHIST = data do pregão do caso; proventos da B3 = `baixado_em` do cache; CVM DFP/ITR = fim do trimestre do LTM (`ltm_ref`);
FRE = DT_REFER do formulário; mercado = a data do arquivo de rf/π. Origem sem data declarada continua "" (o contrato a mostra como null).
"""
import json
from types import SimpleNamespace

import pytest

import proventos_hall
from relatorio import procedencia as pr
from relatorio import quali


def test_iso_aceita_os_dois_formatos_e_nao_chuta_o_resto():
    assert pr._iso("2026-10-02") == "2026-10-02"
    assert pr._iso("02/10/2026") == "2026-10-02"
    assert pr._iso("") == "" and pr._iso(None) == "" and pr._iso("out/2026") == ""
    assert pr._iso("2026-13-45") == "" and pr._iso("31/02/2026") == ""          # formato certo, data impossível


@pytest.mark.parametrize("ref, esperado", [("2T26", "2026-06-30"), ("3T26", "2026-09-30"), ("4T25", "2025-12-31"),
                                           ("1T26", "2026-03-31"), ("9T26", ""), ("xx", "")])
def test_data_do_ltm_pelo_ltm_ref(monkeypatch, ref, esperado):
    import motor_nao_financeiras as M
    monkeypatch.setitem(M.CVM, "ZZZZ3", {"ltm_ref": ref, "ltm": {}, "anual": {}})
    assert pr._data_ltm("ZZZZ3") == esperado
    monkeypatch.setitem(M.CVM, "ZZZZ3", {f"ltm_{ref}": {}, "ltm": {}, "anual": {}})     # série antiga: só a chave ltm_<ref>
    assert pr._data_ltm("ZZZZ3") == esperado


def test_data_do_ltm_sem_trimestre_declarado_nao_vira_2t26(monkeypatch):
    import motor_nao_financeiras as M
    monkeypatch.setitem(M.CVM, "ZZZZ3", {"ltm": {}, "anual": {}})
    assert pr._data_ltm("ZZZZ3") == ""


def test_data_do_ltm_sem_serie_fica_vazia():
    assert pr._data_ltm("NAOEXISTE9") == ""


def test_proventos_b3_levam_o_baixado_em_do_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(proventos_hall, "PASTA", tmp_path)
    (tmp_path / "ZZZZ3.json").write_text(json.dumps({"ticker": "ZZZZ3", "baixado_em": "2026-10-08", "results": []}),
                                         encoding="utf-8")
    (tmp_path / "YYYY3.json").write_text(json.dumps({"ticker": "YYYY3", "results": []}), encoding="utf-8")
    o = proventos_hall.origem_b3("ZZZZ3")
    assert (o.fonte, o.nota, o.data) == (proventos_hall.ORIGEM_B3.fonte, "A", "2026-10-08")
    assert proventos_hall.origem_b3("YYYY3").data == ""          # sem o campo: sem data
    assert proventos_hall.origem_b3("XXXX3").data == ""          # sem o arquivo: sem data


def test_fre_leva_o_dt_refer_e_sem_ele_fica_vazio():
    o = quali._o_fre({"fonte": {"id_doc": 1, "versao": 2, "dt_refer": "2026-01-01"}}, "t")
    assert o.data == "2026-01-01"
    assert quali._o_fre({"fonte": {"id_doc": 1, "versao": 2}}, "t").data == ""
    assert quali._o_fre(None, "t").data == ""
    assert quali._o_fre({"fonte": {"dt_refer": "01/01/2026"}}, "t").data == "2026-01-01"


def test_tabela_do_lote_tem_data_em_cotahist_cvm_e_proventos_e_vazio_no_digitado():
    """Caminho real do relatório (procedencia.tabela) sobre uma não financeira do hall."""
    from relatorio.caso import caso
    tk = "WEGE3"
    t = pr.tabela(caso(tk))
    assert t["preco"].data == pr._iso(__import__("precos_hall").PRECO_DATA)
    assert t["serie"].data == "2026-06-30"                       # WEGE3: ltm_ref "2T26" na série do repo
    assert t["proventos"].data == proventos_hall.origem_b3(tk).data != ""
    assert t["mercado"].data != ""
    assert t["proventos_ja_ex"].data == t["proventos"].data          # N12b: o mesmo cache da B3
    assert t["defasagem"].data == ""                             # StatusInvest (datas) / declarada: sem data no registro


def test_acoes_do_dfp_levam_o_fim_do_exercicio():
    import insumos_a
    import lote3_agro
    assert insumos_a.ACOES_DFP("2025", 1).data == ""                       # sem data declarada: vazio
    for tk, data in (("SLCE3", "2025-12-31"), ("SMTO3", "2026-03-31")):
        lote3_agro.acoes(tk)                                                 # as duas séries estão no repo
        assert insumos_a._REG[(tk, "acoes")][1].data == data


# ---------------------------------------------------------------- N12b: fontes compostas e séries macro
def test_com_data_vale_a_menor_e_nao_chuta():
    import insumos_a
    o = insumos_a.IPCA_BCB
    assert insumos_a.com_data(o, "2026-06-30", "2026-08-01").data == "2026-06-30"
    assert insumos_a.com_data(o, "2026-08-01").data == "2026-08-01"
    assert insumos_a.com_data(o, "2026-06-30", "").data == ""          # componente sem data → sem data
    assert insumos_a.com_data(o, "2026-13-01").data == ""
    assert insumos_a.com_data(o).data == ""
    assert insumos_a.com_data(o, "2026-06-30").fonte == o.fonte and o.data == ""   # o original não muda


def test_datas_registradas_nos_lotes():
    """O valor que a empresa carrega é o registrado, e a origem registrada leva a data (literais medidos em 24/10)."""
    import insumos_a
    import lote3_agro as l3
    import lote4_saude_telecom as l4
    import lote5_petroleo as l5
    import lote6_quimica as l6
    emp = {e.ticker: e for e in l3.EMPRESAS + l4.EMPRESAS + l5.EMPRESAS + l6.EMPRESAS if hasattr(e, "g1_real")}
    o = lambda tk, campo: insumos_a.origem(tk, campo, getattr(emp[tk], campo))
    for tk in ("UGPA3", "VBBR3"):
        assert o(tk, "deflator").data == l5.M["mensal"].index[-1].date().isoformat() == "2026-08-01", tk
    for tk in ("PETR4", "PRIO3", "RECV3"):
        assert o(tk, "receita_meio").data == o(tk, "da_receita").data == "2026-06-30", tk
    for tk in ("GGBR4", "UNIP6"):
        assert o(tk, "receita_meio").data == "2026-06-30", tk
    assert o("TIMS3", "aliquota").data == "2025-12-31"
    assert o("FLRY3", "receita_meio").data == "2026-06-30"
    assert o("WEGE3", "g1_real").data == "2025-12-31"


def test_brent_e_indices_nao_dizem_mais_recente_que_a_janela_de_12m(monkeypatch):
    """Revisor 24/10: com a CVM no 3T26 e a janela de preço ainda em jun/2026, a data fica em jun/2026."""
    import lote5_petroleo as l5
    import lote6_quimica as l6
    monkeypatch.setattr(pr, "_data_ltm", lambda tk: "2026-09-30")
    assert l5._o_brent("PETR4").data == "2026-06-30"
    assert l6._o_indice(l6.RECEITA_MEIO_ACO, "GGBR4", l6.ACO).data == "2026-06-30"


def test_pl_historico_so_tem_data_se_a_conta_rodou(monkeypatch):
    """Do snapshot (sem COTAHIST) não se sabe o ano contido → sem data; com a conta rodando, o último fim de exercício lido."""
    import derivados_zip
    import insumos_a
    import pl_historico as ph
    from motor_nao_financeiras import CVM
    monkeypatch.setattr(insumos_a, "_REG", dict(insumos_a._REG))       # o registro falso não vaza para os outros testes
    monkeypatch.setattr(derivados_zip, "obter", lambda chave, zips, calcular, pasta=None: 20.0)
    ph.do_hall("ABEV3", 1.0)
    assert insumos_a.origem("ABEV3", "pl_hist", 20.0).data == ""
    monkeypatch.setattr(derivados_zip, "obter", lambda chave, zips, calcular, pasta=None: calcular())
    monkeypatch.setattr(ph, "fechamento_ate", lambda tk, fim: (fim, 10.0) if "2020" <= fim <= "2024-12-31" else None)
    v = ph.do_hall("ABEV3", CVM["ABEV3"]["anual"]["2024"]["acoes"])
    assert v is not None and insumos_a.origem("ABEV3", "pl_hist", v).data == "2024-12-31"
