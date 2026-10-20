"""Contrato da tela v0.2: só traduz o que os motores gravaram — ausente vira None (nunca estimativa), palavra do motor
como está (RADAR inclusive), fatores da régua lidos do motor, carteira só em pasta ignorada. Fixtures sintéticas."""
import json
import subprocess

import pytest

from painel import contrato
from painel.contrato import br_num, classe_cenario, linha_hall, monitor, palavra_codigo
from relatorio.modelo import Numero, Origem, Relatorio, Secao

FAT = {"compra": 0.70, "compra_parcial_qualidade": 0.80, "saida": 1.30, "saida_qualidade": 1.50,
       "escala_regua": [0.5, 1.6]}


def bruta(**kw):
    x = {"tk": "TESTA3", "nome": "Teste SA", "origem": "hall, lote 1", "dossie": False, "data_palavra": "2026-10-02",
         "palavra": "CARA", "palavra_motor": None, "central": 10.0, "nota_central": "B", "fonte_central": "CVM",
         "compra": 7.0, "saida": 13.0, "saida_exc": False, "preco_ref": 12.0, "nota_preco_ref": "A",
         "preco_hoje": 14.0, "pc_hoje": 1.4, "situacao": "≥ SAÍDA", "n_central": 2, "n_informativo": 3,
         "fora_do_hall": False, "na_carteira": False, "avisos": [], "erro": None}
    x.update(kw)
    return x


def num(rotulo, valor, unidade="R$", papel="", nota="A", obs=""):
    return {"rotulo": rotulo, "valor": valor, "unidade": unidade, "papel": papel, "obs": obs, "nota": nota,
            "fonte": "CVM", "origens": [{"fonte": "CVM", "nota": nota, "detalhe": ""}]}


def bruto_emp(secoes):
    return {"tk": "TESTA3", "data": "2026-10-02", "avisos": [], "secoes": secoes}


def secao(titulo, numeros=(), texto=(), tabelas=()):
    return {"titulo": titulo, "numeros": list(numeros), "texto": list(texto), "avisos": [], "tabelas": list(tabelas)}


@pytest.mark.parametrize("s,v", [("R$ 1.234,56", 1234.56), ("12,3%", 0.123), ("1,23×", 1.23), ("—", None), ("", None),
                                 ("sem data", None), (3.5, 3.5), (float("nan"), None), (None, None), ("-2,00", -2.0)])
def test_br_num(s, v):
    assert br_num(s) == (pytest.approx(v) if v is not None else None)


def test_palavra_do_motor_como_esta():
    assert palavra_codigo("NÃO CONCLUSIVO") == "NAO_CONCLUSIVO"
    assert palavra_codigo("RADAR") == "RADAR" and palavra_codigo(None) is None


def test_fatores_vem_do_motor():
    import motor_financeiras as m
    f = contrato.fatores()
    assert (f["compra"], f["saida"], f["saida_qualidade"]) == (m.COMPRA, m.SAIDA_PADRAO, m.SAIDA_QUALIDADE)


def test_linha_hall_traduz_sem_inventar():
    x = linha_hall(bruta(saida_exc=True, saida=15.0), None, None, None, "2026-10-20", 7, FAT)
    assert x["fator_saida"] == 1.5 and x["central_nota"] == "B" and x["metodos_total"] == 5
    # o que o motor não entrega fica None: setor, yield (sem seção de dividendos), série, defasagem
    assert x["setor"] is None and x["yield_sust"] is None and x["yield_nota"] == "—"
    assert x["serie_12m"] is None and x["dias_defasagem"] is None and x["velho"] is False


def test_linha_hall_sem_regua_e_dado_velho():
    x = linha_hall(bruta(palavra="NÃO CONCLUSIVO", central=None, compra=None, saida=None, pc_hoje=None,
                         situacao="sem palavra"), None, [["2026-10-09", 1.0]], "2026-10-01", "2026-10-20", 7, FAT)
    assert x["palavra"] == "NAO_CONCLUSIVO" and x["fator_saida"] is None and x["pc"] is None
    assert x["dias_defasagem"] == 19 and x["velho"] is True          # velho não troca a palavra


def test_metodos_separa_central_de_informativo_e_baixo_alto_none():
    b = bruto_emp([secao("Preço justo por método", [
        num("DCF — fluxo de caixa", 9.0, papel="central"), num("Graham", 8.0, papel="informativo", nota="C"),
        num("Bogle — retorno", 0.12, "%", "informativo"), num("Valor central (mediana)", 9.0)])])
    met, ind = contrato.metodos(b)
    assert [m["nome"] for m in met] == ["DCF", "Graham"] and [i["nome"] for i in ind] == ["Bogle"]
    assert met[0]["entra_no_central"] and not met[1]["entra_no_central"]
    assert met[0]["baixo"] is None and met[0]["alto"] is None and met[0]["descricao"] == "fluxo de caixa"


def test_sensibilidade_grade_do_motor_base_e_tom():
    tab = {"titulo": "Central com Ke × margem", "cabecalho": ["Ke \\ margem", "-2 p.p.", "+0 p.p.", "+2 p.p."],
           "linhas": [["-1 p.p.", "30,00", "21,00", "16,00"], ["+0 p.p.", "12,00", "10,00", "—"]]}
    s = contrato.sensibilidade(bruto_emp([secao("Sensibilidade do valor central", tabelas=[tab])]), 14.0, FAT, 1.3)
    assert s["base"] == [1, 1] and s["valores"][1] == [12.0, 10.0, None]
    assert s["classe"][0] == ["bem_acima", "bem_acima", "acima"]       # 14 ≤ 0,7×21 = 14,7
    assert s["classe"][1] == ["abaixo", "bem_abaixo", None]            # 14 < 1,3×12; 14 ≥ 1,3×10
    assert contrato.sensibilidade(bruto_emp([]), 14.0, FAT, 1.3) is None
    assert classe_cenario(10.0, None, 0.7, 1.3) is None


def test_premissas_qualitativo_riscos():
    b = bruto_emp([
        secao("Premissas de julgamento (método, não dado)", texto=["Perfil do motor: utility.", "Texto solto"]),
        secao("Vantagem competitiva (moat)", [num("Nota de moat (0–5)", 4, "", nota="—"), num("ROE", 0.2, "%")]),
        secao("Riscos e bandeiras", [num("Payout acima de 100%", 0.75, "%", obs="ok"),
                                     num("Valor central depende de C", "C", obs="DISPARA — só A/B")])])
    p = contrato.premissas(b)
    assert p[0] == {"nome": "Perfil do motor", "valor": "utility", "tipo": "julgamento", "nota": None, "efeito": None}
    assert p[1]["nome"] == "Texto solto" and p[1]["valor"] is None
    q = {x["eixo"]: x for x in contrato.qualitativo(b)}
    assert q["moat"]["nota_eixo"]["valor"] == 4 and q["moat"]["nota_eixo"]["escala"] == [0, 5]
    assert len(q["moat"]["numeros"]) == 1 and q["gestao"]["nota_eixo"] is None
    r = contrato.riscos(b)["itens"]
    assert [x["disparou"] for x in r] == [False, True] and r[0]["probabilidade"] is None


def test_proventos_tabela_do_dossie():
    tab = {"titulo": "Proventos por exercício (data-com) — fonte: B3", "cabecalho": ["Ano", "DPA total", "JCP", "%"],
           "linhas": [["2025", "R$ 0,79", "R$ 0,36", "45,1%"], ["2026 (parcial)", "R$ 0,23", "R$ 0,23", "100,0%"]]}
    p = contrato.proventos(bruto_emp([secao("Dividendos e JCP", tabelas=[tab])]))
    assert p["historico"][0] == {"ano": "2025", "parcial": False, "total": 0.79, "jcp": 0.36,
                                 "dividendos": pytest.approx(0.43)}
    assert p["historico"][1]["parcial"] and p["yield_proj"] is None and p["anos_seguidos"] is None
    assert contrato.proventos(bruto_emp([]))["historico"] is None


def test_carteira_traduz_tabelas_do_relatorio():
    o = (Origem("carteira local", "B"),)
    rel = Relatorio("CARTEIRA", "Painel", "2026-10-15", "x", "—", secoes=[
        Secao("Meta de renda", numeros=[Numero("Meta (R$ por mês)", 100.0, "R$", o),
                                         Numero("Renda líquida por mês (média de 12 meses)", 25.0, "R$", o),
                                         Numero("Meta atingida", 0.25, "%", o), Numero("Falta por mês", 75.0, "R$", o)]),
        Secao("Posições na régua da doutrina", tabelas=[("Posições (maior valor primeiro)", [""] * 11,
              [["TESTA3", "1", "R$ 14,00", "R$ 14,00", "100,0%", "CARA", "R$ 10,00", "1,40×", "R$ 7,00", "R$ 13,00",
                "na saída ou acima"]])]),
        Secao("Renda", tabelas=[("Renda de 12 meses", [""] * 7,
              [["TESTA3", "1,00", "0,00", "7,1%", "R$ 1,00", "R$ 0,90", "—"], ["Total", "", "", "", "", "", ""]])]),
        Secao("Calendário de pagamento", tabelas=[
            ("Pagamento por mês", [""] * 5, [["2026-11", "R$ 0,90", "TESTA3", "a receber", "estimada"]]),
            ("A receber (pagamento depois de 2026-10-15)", [""] * 8,
             [["TESTA3", "2026-10-01", "sem data", "sem data", "JCP", "0,50", "R$ 0,41", "sim"]])])])
    linhas = {"TESTA3": linha_hall(bruta(), None, None, None, "2026-10-20", 7, FAT)}
    c = contrato.carteira(rel, linhas, [])
    assert c["pct_meta"]["valor"] == 0.25 and c["falta"]["valor"] == 75.0 and c["n_papeis"] == 1
    p = c["posicoes"][0]
    assert p["peso"] == pytest.approx(1.0) and p["renda_liquida_ano"] == 0.9 and p["central"] == 10.0
    assert c["calendario"][0]["dividendos"] is None and c["calendario"][0]["liquido"] == 0.9
    assert c["pagamentos"][0]["data"] is None and c["pagamentos"][0]["na_renda_12m"] is True
    assert c["setores"] is None and c["patrimonio"]["valor"] is None      # ausente no relatório → None


def test_monitor_entrou_e_saiu():
    def r(rod, tk, alerta, pc):
        return {"rodada": rod, "pregao": rod, "ticker": tk, "preco": "10", "central": "10", "pc": pc, "alerta": alerta}
    m = monitor([r("2026-10-09", "A", "", "0.8"), r("2026-10-09", "B", "≥ SAÍDA", "1.4"), r("2026-10-09", "C", "", "1"),
                 r("2026-10-16", "A", "≤ COMPRA", "0.69"), r("2026-10-16", "B", "", "1.2"), r("2026-10-16", "C", "", "1"),
                 r("2026-10-16", "D", "", "1")])
    assert [x["ticker"] for x in m["entraram_compra"]] == ["A"] and m["entraram_compra"][0]["pc_anterior"] == 0.8
    assert [x["ticker"] for x in m["sairam_saida"]] == ["B"] and m["sem_mudanca"] == 1 and m["novos"] == ["D"]
    assert monitor([])["rodada"] is None


def test_real_contrato_sem_valor_inventado():
    """Com os dados locais: todo campo do contrato que o motor não dá é None, e a palavra é a do exportador."""
    hall_p = contrato.DESTINO / "hall.json"
    if not hall_p.exists():
        pytest.skip("sem web/dados/contrato (rode python -m painel.contrato)")
    h = json.loads(hall_p.read_text(encoding="utf-8"))
    bruto = {x["tk"]: x for x in json.loads((contrato.DADOS / "hall.json").read_text(encoding="utf-8"))["empresas"]}
    assert subprocess.run(["git", "check-ignore", "-q", "--", str(contrato.PRIVADO / "carteira.json")],
                          cwd=contrato.DADOS).returncode == 0
    pessoais = {"peso", "peso_carteira", "renda_liquida_ano", "renda_bruta_ano", "preco_medio", "quantidade", "meta"}
    for e in h["empresas"]:
        assert not pessoais & set(e), e["ticker"]                     # hall sem dado pessoal (fica em privado/)
        assert e["setor"] is None
        assert e["palavra"] == palavra_codigo(bruto[e["ticker"]]["palavra"])
        assert e["central"] == bruto[e["ticker"]]["central"] and e["compra"] == bruto[e["ticker"]]["compra"]
