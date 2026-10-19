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
