"""Painel da carteira: renda de 12 meses pela data-com, conta da meta, régua neutra e trava de dado pessoal (só grava em
pasta ignorada pelo git). Fixtures sintéticas (TEST*); o teste com dado real pula sem COTAHIST/suplemento."""
import json
import math
import pathlib

import pytest
from dados_opcionais import requer_suplemento_b3

from relatorio import carteira
from relatorio.carteira import garantir_ignorado, ler_local, montar, situacao
from relatorio.renda import Renda12m, provento_12m

RAIZ = pathlib.Path(__file__).resolve().parents[3]
DATA = "2026-10-15"


def reg(data_com, valor, tipo="DIVIDENDO", classe="ON", lote=1.0):
    return {"tipo_acao": classe, "data_aprovacao": data_com, "data_com": data_com, "valor": valor, "lote": lote, "tipo": tipo}


# ------------------------------------------------------------------------------ renda.provento_12m
def test_janela_de_12_meses_pela_data_com():
    r = provento_12m([reg("2025-10-15", 9.0), reg("2025-10-16", 1.0), reg("2026-10-15", 2.0),
                      reg("2026-03-01", 0.5, "JRS CAP PROPRIO")], "ON", DATA)
    assert r.total == pytest.approx(3.5)           # 15/10/2025 fica fora (janela exclusiva), 15/10/2026 entra
    assert r.jcp == pytest.approx(0.5)


def test_data_com_futura_vai_para_anunciados():
    r = provento_12m([reg("2026-11-30", 0.3), reg("2026-05-01", 1.0)], "ON", DATA)
    assert r.total == pytest.approx(1.0)
    assert [e["data_com"] for e in r.futuros] == ["2026-11-30"]


def test_duplicata_da_b3_conta_uma_vez_e_provento_diferente_soma():
    r = provento_12m([reg("2026-05-01", 1.0), reg("2026-05-01", 1.004), reg("2026-05-01", 0.5)], "ON", DATA)
    assert r.total == pytest.approx(1.5)


def test_so_a_classe_do_ticker():
    r = provento_12m([reg("2026-05-01", 1.0, classe="ON"), reg("2026-05-01", 1.1, classe="PN")], "PN", DATA)
    assert r.total == pytest.approx(1.1)


def test_bonificacao_na_janela_divide_o_provento_anterior():
    ev = [{"tipo": "BONIFICACAO", "data_com": "2026-06-01", "multiplicador": 1.10}]
    r = provento_12m([reg("2026-05-01", 1.1), reg("2026-07-01", 1.0)], "ON", DATA, ev)
    assert r.total == pytest.approx(1.0 + 1.0)     # 1,10 antes da bonificação de 10% = 1,00 por ação de hoje


def test_evento_depois_da_data_do_preco_nao_ajusta():
    ev = [{"tipo": "DESDOBRAMENTO", "data_com": "2026-12-01", "multiplicador": 2.0}]
    assert provento_12m([reg("2026-05-01", 1.0)], "ON", DATA, ev).total == pytest.approx(1.0)


def test_restituicao_de_capital_nao_e_renda_e_lote_divide():
    r = provento_12m([reg("2026-05-01", 5.0, "REST CAP DIN"), reg("2026-06-01", 10.0, lote=1000.0)], "ON", DATA)
    assert r.total == pytest.approx(0.01)
    assert [e["tipo"] for e in r.ignorados] == ["REST CAP DIN"]


# ------------------------------------------------------------------------------ entrada local
def _local(tmp_path, dados) -> pathlib.Path:
    p = tmp_path / "carteira.local.json"
    p.write_text(json.dumps(dados), encoding="utf-8")
    return p


def test_sem_arquivo_local_explica_o_que_fazer(tmp_path):
    with pytest.raises(FileNotFoundError, match="carteira.exemplo.json"):
        ler_local(tmp_path / "carteira.local.json")


@pytest.mark.parametrize("dados, msg", [
    ({"meta_mensal": 0, "posicoes": {"TESTA3": {"quantidade": 1}}}, "meta_mensal"),
    ({"meta_mensal": 100, "posicoes": {"TESTA3": {"quantidade": None}}}, "TESTA3 sem quantidade"),
    ({"meta_mensal": 100, "posicoes": {"TESTA3": {"quantidade": 1, "preco_medio": -2}}}, "preco_medio"),
    ({"meta_mensal": 100, "posicoes": {}}, "posicoes"),
])
def test_local_invalido_falha_alto(tmp_path, dados, msg):
    with pytest.raises(ValueError, match=msg):
        ler_local(_local(tmp_path, dados))


def test_tickers_do_local_tem_de_bater_com_carteira_tickers(tmp_path):
    p = _local(tmp_path, {"meta_mensal": 100, "posicoes": {"TESTA3": {"quantidade": 1}}})
    with pytest.raises(ValueError, match=r"faltam \['TESTB4'\]"):
        ler_local(p, ["TESTA3", "TESTB4"])


def test_exemplo_versionado_e_valido_e_tem_os_tickers_da_carteira():
    tks = json.loads(carteira.TICKERS.read_text(encoding="utf-8"))["tickers"]
    assert set(ler_local(carteira.EXEMPLO, tks)["posicoes"]) == set(tks)


# ------------------------------------------------------------------------------ painel
REFS = {"TESTA3": {"palavra": "BARATA", "central": 20.0, "compra": 14.0, "saida": 26.0},
        "TESTB4": {"palavra": "NÃO CONCLUSIVO", "central": 18.0}}


def _painel(rendas=None, meta=100.0):
    local = {"meta_mensal": meta, "posicoes": {"TESTA3": {"quantidade": 100, "preco_medio": 8.0},
                                              "TESTB4": {"quantidade": 50, "preco_medio": None}}}
    rendas = rendas or {"TESTA3": Renda12m(1.0, 0.4), "TESTB4": Renda12m(2.0, 0.0)}
    return montar(local, {"TESTA3": 10.0, "TESTB4": 20.0}, DATA, REFS, rendas, "2026-10-02",
                  fora_do_hall=frozenset({"TESTB4"}), ir_jcp=0.175)


def _num(rel, rotulo):
    return next(n for n in rel.numeros() if n.rotulo.startswith(rotulo))


def test_conta_da_meta_feita_a_mao():
    rel = _painel()
    # valor 100×10 + 50×20 = 2.000; bruta 100×1 + 50×2 = 200; líquida 100×(1 − 0,4×0,175) + 100 = 193
    assert _num(rel, "Patrimônio em ações").valor == pytest.approx(2000)
    assert _num(rel, "Renda bruta por mês").valor == pytest.approx(200 / 12)
    assert _num(rel, "Renda líquida por mês").valor == pytest.approx(193 / 12)
    assert _num(rel, "Meta atingida").valor == pytest.approx(193 / 12 / 100)
    assert _num(rel, "Falta por mês").valor == pytest.approx(100 - 193 / 12)
    assert _num(rel, "DY líquido").valor == pytest.approx(193 / 2000)
    assert _num(rel, "Patrimônio que a meta exige").valor == pytest.approx(1200 / (193 / 2000))
    assert all(n.origens for n in rel.numeros())


def test_meta_passada_nao_falta_negativo():
    assert _num(_painel(meta=1.0), "Falta por mês").valor == 0.0


def test_renda_faltando_avisa_incompleta_em_vez_de_somar_zero_calado():
    rel = _painel(rendas={"TESTA3": Renda12m(1.0, 0.0), "TESTB4": "ValueError: sem B3"})
    assert any("INCOMPLETA" in a and "TESTB4" in a for a in rel.avisos)
    assert "INCOMPLETA" in _num(rel, "Renda líquida por mês").obs


def test_sem_preco_falha_alto():
    local = {"meta_mensal": 100.0, "posicoes": {"TESTA3": {"quantidade": 1, "preco_medio": None}}}
    with pytest.raises(ValueError, match="TESTA3"):
        montar(local, {}, DATA, REFS, {"TESTA3": Renda12m(1.0, 0.0)}, "2026-10-02")


def test_regua_neutra_e_sem_ordem():
    assert situacao(13.0, REFS["TESTA3"]) == "no preço de compra ou abaixo"
    assert situacao(20.0, REFS["TESTA3"]) == "entre compra e saída"
    assert situacao(26.0, REFS["TESTA3"]) == "na saída ou acima"
    assert situacao(10.0, REFS["TESTB4"]) == "sem régua (NÃO CONCLUSIVO)"
    assert situacao(10.0, None) == "sem palavra do motor"
    md = carteira.render(_painel()).lower()
    for imperativo in ("compre", "comprar", "venda ", "vender", "recomend"):
        assert imperativo not in md
    assert "fora do hall" in md and "yield on cost" in md


# ------------------------------------------------------------------------------ trava de dado pessoal
def test_grava_so_em_pasta_ignorada(tmp_path):
    rel = _painel()
    with pytest.raises(PermissionError):
        carteira.gravar(rel, RAIZ / "RELATORIOS")             # pasta versionada
    with pytest.raises(PermissionError):
        carteira.gravar(rel, tmp_path)                       # fora do repo: git não confirma → recusa
    assert not (RAIZ / "RELATORIOS" / f"CARTEIRA-{DATA}.md").exists()
    garantir_ignorado(carteira.SAIDA / f"CARTEIRA-{DATA}.md")   # o destino padrão é ignorado
    garantir_ignorado(carteira.LOCAL)                         # e o arquivo com as quantidades também


# ------------------------------------------------------------------------------ dado real (opcional)
@requer_suplemento_b3
def test_painel_real_com_o_exemplo_monta_sem_rede():
    from backtest import cotahist
    if not cotahist.parquet_de(2026).exists():
        pytest.skip("COTAHIST 2026 fora do disco")
    rel = carteira.carregar(hoje=DATA, caminho=carteira.EXEMPLO, baixar=False)
    assert rel.data <= DATA
    linhas = rel.secoes[1].tabelas[0][2]
    assert {x[0] for x in linhas} == set(json.loads(carteira.TICKERS.read_text(encoding="utf-8"))["tickers"])
    assert not math.isnan(_num(rel, "Patrimônio em ações").valor)


# ------------------------------------------------------------------------------ calendário de pagamento
from relatorio.calendario import ESTIMADO, STATUSINVEST, anotar, data_de_pagamento, meses  # noqa: E402


def ev(data_com, por_acao=1.0):
    return {"data_com": data_com, "por_acao": por_acao}


def test_pagamento_da_statusinvest_casado_pela_data_com():
    si = [{"data_com": "06/08/2026", "pagamento": "03/09/2026", "valor": 1.98}]
    assert data_de_pagamento(ev("2026-08-06", 1.98), si, 0.5) == ("2026-09-03", STATUSINVEST)


def test_duas_datas_na_mesma_data_com_casa_pelo_valor():
    si = [{"data_com": "01/09/2026", "pagamento": "11/09/2026", "valor": 0.10},
          {"data_com": "01/09/2026", "pagamento": "30/12/2026", "valor": 0.50}]
    assert data_de_pagamento(ev("2026-09-01", 0.501), si, 1.0) == ("2026-12-30", STATUSINVEST)


def test_sem_statusinvest_estima_pela_defasagem_e_sem_defasagem_nao_inventa():
    si = [{"data_com": "30/11/2026", "pagamento": "-", "valor": 0.02}]          # anunciado, ainda sem data
    assert data_de_pagamento(ev("2026-11-30"), si, 1.0) == ("2026-12-30", ESTIMADO)
    assert data_de_pagamento(ev("2026-11-30"), [], None) == ("", "")


def test_meses_atravessa_o_ano():
    assert meses("2025-11", "2026-02") == ["2025-11", "2025-12", "2026-01", "2026-02"]


def _painel_com_datas():
    a = provento_12m([reg("2026-03-02", 1.0), reg("2026-08-03", 0.5, "JRS CAP PROPRIO"), reg("2026-11-30", 0.2)], "ON", DATA)
    b = provento_12m([reg("2026-03-10", 2.0)], "ON", DATA)
    anotar(a, [{"data_com": "02/03/2026", "pagamento": "20/03/2026", "valor": 1.0},
               {"data_com": "03/08/2026", "pagamento": "20/10/2026", "valor": 0.5}], 1.0)
    anotar(b, [], None)
    return _painel(rendas={"TESTA3": a, "TESTB4": b})


def test_calendario_soma_a_renda_liquida_e_separa_o_a_receber():
    rel = _painel_com_datas()
    cal = next(s for s in rel.secoes if s.titulo == "Calendário de pagamento")
    linhas = cal.tabelas[0][2]
    assert [x[0] for x in linhas] == ["2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09",
                                      "2026-10", "sem data"]
    assert linhas[0][1:4] == ["R$ 100,00", "TESTA3", "pago"]
    assert linhas[1][3] == "sem pagamento"
    assert linhas[7][3] == "a receber" and linhas[-1][2] == "TESTB4"
    # 100×1 (mar) + 100×0,5×(1 − 0,175) (out, a receber) + 50×2 (sem data) = líquida anual do painel
    assert _num(rel, "Renda líquida por mês").valor * 12 == pytest.approx(100 + 41.25 + 100)
    assert _num(rel, "A receber da renda").valor == pytest.approx(41.25)
    assert _num(rel, "A receber da renda").nota == "C"                 # a data vem da StatusInvest
    assert _num(rel, "Anunciado com data-com futura").valor == pytest.approx(100 * 0.2)
    pend = cal.tabelas[1][2]
    assert [(x[0], x[1], x[-1]) for x in pend] == [("TESTA3", "2026-08-03", "sim"),
                                                    ("TESTA3", "2026-11-30", "não (data-com futura)")]
    assert pend[1][2:4] == ["2026-12-30", "estimada"]


def test_pdf_do_painel_sai_e_gravar_escreve_md_e_pdf_so_em_pasta_ignorada():
    import shutil
    import uuid
    rel = _painel_com_datas()
    pasta = carteira.SAIDA / f"_teste_{uuid.uuid4().hex[:8]}"         # dentro de RELATORIOS/privado/ (ignorado)
    try:
        md, pdf = carteira.gravar(rel, pasta)
        assert md.read_text(encoding="utf-8").startswith("# Painel da carteira")
        assert pdf.read_bytes()[:5] == b"%PDF-" and pdf.stat().st_size > 3000
    finally:
        shutil.rmtree(pasta, ignore_errors=True)


def test_anunciado_so_na_statusinvest_entra_a_receber_com_nota_c_e_fora_da_renda():
    a = provento_12m([reg("2026-03-02", 1.0)], "ON", DATA)
    anotar(a, [{"data_com": "02/03/2026", "pagamento": "20/03/2026", "valor": 1.0, "tipo": "Dividendo"},
               {"data_com": "30/11/2026", "pagamento": "04/01/2027", "valor": 0.3, "tipo": "Dividendo"},
               {"data_com": "30/11/2026", "pagamento": "04/01/2027", "valor": 9.0, "tipo": "Amortização"}], 1.0, DATA)
    rel = _painel(rendas={"TESTA3": a, "TESTB4": Renda12m(0.0, 0.0)})
    assert _num(rel, "Renda líquida por mês").valor * 12 == pytest.approx(100)          # o anunciado não entra na renda
    n = _num(rel, "Anunciado com data-com futura")
    assert n.valor == pytest.approx(30) and n.nota == "C"
    cal = next(s for s in rel.secoes if s.titulo == "Calendário de pagamento")
    assert cal.tabelas[1][2] == [["TESTA3", "2026-11-30", "2027-01-04", "StatusInvest", "DIVIDENDO", "0,30", "R$ 30,00",
                                  "não (data-com futura; só StatusInvest, C)"]]
    assert _num(rel, "A receber da renda").valor == 0.0 and isinstance(_num(rel, "A receber da renda").valor, float)


# ------------------------------------------------------------------------------ histórico rumo à meta (fase 2, fatia 3)
def _hist_tmp():
    import uuid
    return carteira.HISTORICO.parent / f"_teste_{uuid.uuid4().hex[:8]}" / "renda.jsonl"   # dentro de dados/privado/ (ignorado)


def _limpa(caminho):
    import shutil
    shutil.rmtree(caminho.parent, ignore_errors=True)


def test_resumo_traz_os_numeros_do_painel():
    r = carteira.resumo(_painel())
    assert r["data"] == DATA and r["incompleta"] is False
    assert r["renda_liquida_mensal"] == pytest.approx(193 / 12) and r["pct_meta"] == pytest.approx(193 / 12 / 100)
    assert r["patrimonio"] == pytest.approx(2000) and r["meta_mensal"] == 100.0
    assert carteira.resumo(_painel(rendas={"TESTA3": Renda12m(1.0, 0.0), "TESTB4": "ValueError: x"}))["incompleta"] is True


def test_historico_mesma_data_substitui_e_data_nova_acrescenta():
    a = {**carteira.resumo(_painel()), "data": "2026-10-09"}
    b = carteira.resumo(_painel())
    h = carteira.com_linha(carteira.com_linha([], b), a)
    assert [r["data"] for r in h] == ["2026-10-09", DATA]                   # ordenado por data
    h2 = carteira.com_linha(h, {**b, "renda_liquida_mensal": 1.0})
    assert len(h2) == 2 and h2[-1]["renda_liquida_mensal"] == 1.0           # rodar de novo no mesmo pregão não duplica


def test_historico_ida_e_volta_ausente_e_linha_estragada(tmp_path):
    assert carteira.ler_historico(tmp_path / "nao-existe.jsonl") == []
    cam = _hist_tmp()
    try:
        h = [carteira.resumo(_painel())]
        carteira.escrever_historico(h, cam)
        assert carteira.ler_historico(cam) == h
        cam.write_text(cam.read_text(encoding="utf-8") + "{quebrado\n", encoding="utf-8")
        with pytest.raises(ValueError, match="linha 2"):
            carteira.ler_historico(cam)
    finally:
        _limpa(cam)


def test_historico_so_grava_em_caminho_ignorado(tmp_path):
    with pytest.raises(PermissionError):
        carteira.escrever_historico([carteira.resumo(_painel())], tmp_path / "renda.jsonl")
    assert not (tmp_path / "renda.jsonl").exists()


def test_evolucao_desenha_variacao_barra_e_nao_compara_incompleta():
    base = carteira.resumo(_painel())
    h = [{**base, "data": "2026-10-09", "renda_liquida_mensal": 10.0, "pct_meta": 0.10},
         {**base, "data": "2026-10-15", "renda_liquida_mensal": 15.0, "pct_meta": 0.15},
         {**base, "data": "2026-10-22", "renda_liquida_mensal": 5.0, "pct_meta": 0.05, "incompleta": True}]
    linhas = carteira.evolucao_secao(h).tabelas[0][2]
    assert linhas[0][4] == "—" and linhas[1][4] == "R$ 5,00" and linhas[2][4] == "—"
    assert "(incompleta)" in linhas[2][1]
    assert linhas[1][5] == "###" and carteira.evolucao_secao([{**base, "pct_meta": 3.0}]).tabelas[0][2][0][5] == "#" * carteira.BARRA


def test_painel_registra_depois_de_gravar_e_falha_ao_gravar_nao_suja_o_historico(monkeypatch):
    import uuid
    cam = _hist_tmp()
    pasta = carteira.SAIDA / f"_teste_{uuid.uuid4().hex[:8]}"
    try:
        md, pdf = carteira.painel(_painel_com_datas(), pasta, cam)
        assert "## Evolução rumo à meta" in md.read_text(encoding="utf-8")
        assert [r["data"] for r in carteira.ler_historico(cam)] == [DATA]
        carteira.painel(_painel_com_datas(), pasta, cam)                    # mesmo pregão de novo: continua uma linha
        assert len(carteira.ler_historico(cam)) == 1
        antes = cam.read_bytes()
        monkeypatch.setattr(carteira, "gravar", lambda *a, **k: (_ for _ in ()).throw(OSError("disco cheio")))
        rel = _painel_com_datas()
        rel.data = "2026-10-22"
        with pytest.raises(OSError):
            carteira.painel(rel, pasta, cam)
        assert cam.read_bytes() == antes
    finally:
        import shutil
        _limpa(cam)
        shutil.rmtree(pasta, ignore_errors=True)


def test_historico_nunca_vai_para_o_git():
    import subprocess
    r = subprocess.run(["git", "check-ignore", "-q", "--", str(carteira.HISTORICO)], cwd=RAIZ)
    assert r.returncode == 0
