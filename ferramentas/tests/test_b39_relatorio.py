"""B39 — relatório gerado só do JSON (sem dados) e conferências de identidade/parse que não precisam de rede."""
import json
import pathlib
import re

import pytest

from b39 import calculo as c
from b39 import relatorio as rel
from b39.insumos import damodaran_linha, escolher_rf, linhas_tesouro

RAIZ = pathlib.Path(__file__).resolve().parents[1]


def _resultado(deltas):
    est = {k: {"nome": k, "ke_real": 0.12, "ke_mesa_real": 0.12 - (d or 0), "sens": {}} for k, d in deltas.items()}
    est["ii"].update(n=50, n_indice=73, cobertura_vm=0.9, cobertura_peso_ibov=0.88, soma_e10=1e8, soma_vm=1e9, vm_total=1.1e9,
                     payout_mediano=0.5)
    est["ii"]["sens"] = {"sem_petr_vale": 0.11, "gordon_g_1%": 0.13}
    return {"data_base": "2026-11-19", "gerado_em": "x", "mes_ipca": "2026-09",
            "mercado": {"rf_real": 0.0786, "rf_titulo": "Tesouro IPCA+ 2035-05-15", "rf_fonte": "TT", "pi": 0.071706, "pi_fonte": "ETTJ",
                        "damodaran": {"atualizado": "January 5, 2026", "rating_moodys": "Ba1", "s_adj_default_spread": 0.0213,
                                      "crp": 0.0324, "erp_total": 0.0747, "erp_maduro_implicito": 0.0423, "url": "u"},
                        "ibov": {"n": 76, "data_da_carteira_b3": "25/11/26", "fonte": "B3"}},
            "estimativas": est, "deltas": deltas, "gatilho": c.gatilho(deltas),
            "bancos": [{"ticker": "ITUB4", "n_roes": 10, "roe_normalizado": 0.2, "pvp": 2.0, "ke_real": 0.13, "dt_refer_ultimo": "2026-09-30"},
                       {"ticker": "BRBI11", "n_roes": 4, "roe_normalizado": None, "pvp": 1.5, "fora": "menos de 5 exercícios",
                        "dt_refer_ultimo": "2026-09-30"}],
            "empresas": [{"no_indice": True, "e10": None, "vm": 5e6, "part": 0.01, "tickers": ["XPTO3"], "cnpj": "1", "nome": "XPTO",
                          "n_exercicios_e10": 3, "avisos": ["ITR reapresentado"], "nota_vm": ""}]}


def test_relatorio_dispara_traz_so_proposta_com_pausa():
    md = rel.montar(_resultado({"i": 0.05, "ii": 0.04, "iii": 0.01}))
    assert "**DISPARA**" in md and "⏸" in md and "+4,00 p.p." in md
    assert "XPTO" in md and "3 exercícios com lucro" in md and "BRBI11" in md and "fora: menos de 5" in md
    assert "ordem de compra" in md


def test_relatorio_nao_dispara_e_nao_conclusiva():
    assert "**NÃO DISPARA**" in rel.montar(_resultado({"i": 0.01, "ii": -0.02, "iii": 0.0}))
    md = rel.montar(_resultado({"i": 0.05, "ii": None, "iii": None}))
    assert "**NÃO CONCLUSIVA**" in md and "faltou: ii, iii" in md


def test_relatorio_deterministico():
    r = _resultado({"i": 0.05, "ii": 0.04, "iii": 0.01})
    assert rel.montar(json.loads(json.dumps(r))) == rel.montar(r)


def test_direcao_da_sensibilidade():
    assert rel.direcao(0.13, 0.12).startswith("sobe +1,00")
    assert rel.direcao(0.11, 0.12).startswith("desce -1,00")
    assert rel.direcao(None, 0.12) == "—"


def test_relatorio_gravado_bate_com_o_json():
    """Idempotência: o .md no git é exatamente o que o JSON no git gera."""
    if not (rel.ENTRADA.exists() and rel.SAIDA.exists()):
        pytest.skip("B39 ainda não rodada")
    r = json.loads(rel.ENTRADA.read_text(encoding="utf-8"))
    assert rel.SAIDA.read_text(encoding="utf-8").replace("\r\n", "\n") == rel.montar(r)


# ------------------------------------------------------------------ parse dos insumos (texto fixo, sem rede)
def test_damodaran_linha_do_brasil():
    html = "<p>Last updated: January 5, 2026</p><tr><td>Brazil</td><td>Ba1</td><td>2.13%</td><td>3.24%</td><td>7.47%</td>" \
           "<td>34.00%</td><td>2.21%</td><td>7.59%</td></tr>"
    d = damodaran_linha(html)
    assert d["atualizado"] == "January 5, 2026" and d["rating_moodys"] == "Ba1"
    assert d["s_adj_default_spread"] == pytest.approx(0.0213) and d["erp_total"] == pytest.approx(0.0747)
    assert d["crp"] == pytest.approx(0.0324) and d["cds"] == pytest.approx(0.0221)


def test_rf_ipca_sem_cupom_mais_proximo_de_10_anos():
    csv = ("Tipo Titulo;Data Vencimento;Data Base;Taxa Compra Manha;Taxa Venda Manha;PU Compra Manha;PU Venda Manha;PU Base Manha\n"
           "Tesouro IPCA+;15/05/2035;19/11/2026;7,86;7,98;1;1;1\n"
           "Tesouro IPCA+;15/08/2040;19/11/2026;7,54;7,66;1;1;1\n"
           "Tesouro IPCA+ com Juros Semestrais;15/05/2037;19/11/2026;7,72;7,84;1;1;1\n"
           "Tesouro IPCA+;15/05/2035;18/11/2026;7,90;7,98;1;1;1\n")
    ls = linhas_tesouro(csv, "2026-11-19")
    assert len(ls) == 3
    rf = escolher_rf(ls, "2026-11-19")
    assert rf["vencimento"] == "2035-05-15" and rf["taxa_compra_manha"] == pytest.approx(0.0786)


def test_bancos_e_financeiras_batem_com_o_lote1():
    """A lista de bancos da (i) é a do hall (lote1_bancos, tipo "banco") + BPAC11; as financeiras de 5 p.p. incluem as seguradoras."""
    from b39 import rodar
    src = (RAIZ / "lote1_bancos.py").read_text(encoding="utf-8")
    bancos = set(re.findall(r'Financeira\("([A-Z0-9]+)",\s*"[^"]*",\s*"banco"', src))
    seg = set(re.findall(r'Financeira\("([A-Z0-9]+)",\s*"[^"]*",\s*"seguradora', src))
    assert bancos | {"BPAC11"} == set(rodar.BANCOS)
    assert seg <= rodar.FINANCEIRAS_MESA


# ------------------------------------------------------------------ regressões do adversário (25/11)
def test_lucro_fin_controlador_zerado_cai_no_lucro_consolidado():
    import pandas as pd
    from b39.cvm import lucro_fin
    linhas = pd.DataFrame({"conjunto": "con", "ordem_exerc": "ULTIMO", "bloco": "DRE", "dt_ini_exerc": "2022-01-01",
                           "descricao": ["Lucro ou Prejuízo Líquido Consolidado do Período",
                                         "Atribuído aos Sócios da Empresa Controladora"], "valor": [789718.0, 0.0]})
    assert lucro_fin(linhas) == 789718.0                      # ABCB4 2022: 3.11.01 = 0 não é lucro zero
    linhas.loc[1, "valor"] = 700000.0
    assert lucro_fin(linhas) == 700000.0                      # controlador preenchido vence


def test_valor_de_mercado_prefere_a_unit():
    from b39.rodar import valor_mercado
    acoes = {"on": 100.0, "pn": 200.0}
    vm, nota = valor_mercado(acoes, {"on": 2.83, "pn": None}, unit=("IGTI11", 21.85, 3.0))
    assert vm == pytest.approx(300 / 3 * 21.85 / 1000) and "unit" in nota
    vm, nota = valor_mercado(acoes, {"on": 10.0, "pn": None})
    assert vm == pytest.approx(3.0) and "PN sem pregão" in nota
