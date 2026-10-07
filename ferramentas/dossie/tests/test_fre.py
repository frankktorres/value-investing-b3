"""Leitor do FRE (dossie/fre.py) sobre um ZIP sintético: versão mais recente, LGPD, formatos numéricos."""
import io
import json
import re
import zipfile

import pytest

from dossie import fre

CNPJ = "11.111.111/0001-11"
OUTRO = "22.222.222/0001-22"
CPF = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}")
NOMES_PROIBIDOS = ["Joao Carlos Pereira", "Maria Aparecida Souza", "Roberto Alves Lima", "Ana Beatriz Costa"]


def _csv(cols, linhas):
    txt = ";".join(cols) + "\n" + "".join(";".join(l) + "\n" for l in linhas)
    return txt.encode("latin-1")


def _idx(linhas):
    return _csv(["CNPJ_CIA", "DT_REFER", "VERSAO", "DENOM_CIA", "CD_CVM", "CATEG_DOC", "ID_DOC", "DT_RECEB", "LINK_DOC"], linhas)


def _tab(cols, linhas):
    """Tabela com as 5 colunas padrão + as específicas; linha = (cnpj, versao, id_doc, *específicas)."""
    base = ["CNPJ_Companhia", "Data_Referencia", "Versao", "ID_Documento", "Nome_Companhia"]
    return _csv(base + cols, [[c, "2026-12-31", v, i, "EMPRESA SA"] + list(r) for c, v, i, *r in linhas])


@pytest.fixture
def pasta(tmp_path):
    ano = 2026
    arqs = {
        f"fre_cia_aberta_{ano}.csv": _idx([
            [CNPJ, "2026-12-31", "1", "EMPRESA SA", "1", "FRE WEB", "100", "2026-05-01", "http://x/100"],
            [CNPJ, "2026-12-31", "2", "EMPRESA SA", "1", "FRE WEB", "200", "2026-06-01", "http://x/200"],
            [CNPJ, "2026-12-31", "10", "EMPRESA SA", "1", "FRE WEB", "300", "2026-07-01", "http://x/300"],
            [OUTRO, "2026-12-31", "1", "OUTRA SA", "2", "FRE WEB", "900", "2026-05-02", "http://x/900"],
        ]),
        f"fre_cia_aberta_remuneracao_total_orgao_{ano}.csv": _tab(
            ["Data_Fim_Exercicio_Social", "Total_Remuneracao", "Orgao_Administracao", "Total_Remuneracao_Orgao"], [
                (CNPJ, "1", "100", "2025-12-31", "999", "Diretoria", "999"),                          # versão antiga
                (CNPJ, "10", "300", "2025-12-31", "55.656.814.393,17", "Diretoria Estatutária", "5.000,50"),  # BR
                (CNPJ, "10", "300", "2025-12-31", "55.656.814.393,17", "Conselho de Administração", "1000.25"),
                (CNPJ, "10", "300", "2024-12-31", "7000", "Diretoria Estatutária", "7000.00"),
                (OUTRO, "1", "900", "2025-12-31", "1", "Diretoria", "1"),
            ]),
        f"fre_cia_aberta_transacao_parte_relacionada_{ano}.csv": _tab(
            ["Parte_Relacionada", "Tipo_Pessoa", "Documento_Parte_Relacionada", "Relacao_Emissor", "Data_Transacao",
             "Objeto_Contrato", "Montante_Envolvido", "Saldo_Existente", "Natureza_Razao_Operacao",
             "Posicao_Contratual_Emissor"], [
                (CNPJ, "1", "100", "Fornecedora Antiga Ltda.", "", "", "Coligada", "2020-01-01", "x", "1", "1", "x", "Devedor"),
                (CNPJ, "10", "300", "Holding Familiar S.A.", "", "", "Controladora", "2025-12-31", "A" * 300,
                 "44434242.05", "2.668,51", "B" * 300, "Credor"),
                (CNPJ, "10", "300", "Joao Carlos Pereira", "", "123.456.789-01", "Joao Carlos Pereira, sócio majoritário",
                 "2025-12-31", "Aluguel do imóvel CPF 123.456.789-01", "1000", "", "Aluguel", "Devedor"),
            ]),
        f"fre_cia_aberta_posicao_acionaria_{ano}.csv": _tab(
            ["Acionista", "Tipo_Pessoa_Acionista", "CPF_CNPJ_Acionista", "Acionista_Relacionado",
             "Percentual_Acao_Ordinaria_Circulacao", "Percentual_Acao_Preferencial_Circulacao",
             "Percentual_Total_Acoes_Circulacao", "Acionista_Controlador", "Participante_Acordo_Acionistas"], [
                (CNPJ, "1", "100", "Antigo S.A.", "PJ", "99.999.999/0001-99", "", "100", "0", "100", "N", "N"),
                (CNPJ, "10", "300", "Holding Familiar S.A.", "PJ", "33.333.333/0001-33", "", "50.5", "0", "50.5", "S", "S"),
                (CNPJ, "10", "300", "Roberto Alves Lima", "PF", "987.654.321-00", "", "20", "0", "20", "S", "N"),
                (CNPJ, "10", "300", "Roberto Alves Lima", "PF", "987.654.321-00", "Holding Familiar S.A.", "5", "0", "5", "N", "N"),
                (CNPJ, "10", "300", "Outros", "", "", "", "29,5", "0", "29,5", "N", "N"),
            ]),
        f"fre_cia_aberta_distribuicao_capital_{ano}.csv": _tab(
            ["Quantidade_Acionistas_PF", "Quantidade_Acionistas_PJ", "Quantidade_Acionistas_Investidores_Institucionais",
             "Percentual_Acoes_Ordinarias_Circulacao", "Percentual_Acoes_Preferenciais_Circulacao",
             "Percentual_Total_Acoes_Circulacao"], [
                (CNPJ, "1", "100", "1", "1", "1", "1.0", "0", "1.0"),
                (CNPJ, "10", "300", "17570", "67", "136", "29.5", "0", "29.5"),
            ]),
        f"fre_cia_aberta_administrador_membro_conselho_fiscal_{ano}.csv": _tab(
            ["Orgao_Administracao", "Nome", "CPF", "Cargo_Eletivo_Ocupado", "Data_Inicio_Primeiro_Mandato",
             "Eleito_Controlador"], [
                (CNPJ, "1", "100", "Conselho de Administração", "Fulano Antigo", "000.000.000-00", "Conselheiro", "2000-01-01", "N"),
                (CNPJ, "10", "300", "Conselho de Administração", "Maria Aparecida Souza", "111.222.333-44", "Presidente", "2010-04-30", "S"),
                (CNPJ, "10", "300", "Conselho de Administração", "Ana Beatriz Costa", "555.666.777-88", "Conselheiro", "2015-04-30", "N"),
                (CNPJ, "10", "300", "Diretoria", "Roberto Alves Lima", "987.654.321-00", "Diretor Presidente", "2018-01-02", ""),
            ]),
        f"fre_cia_aberta_relacao_familiar_{ano}.csv": _tab(
            ["Nome_Administrador", "CPF_Administrador", "Cargo_Administrador", "Nome_Pessoa_Relacionada",
             "CPF_Pessoa_Relacionada", "Nome_Emissor_Pessoa_Relacionada", "CNPJ_Emissor_Pessoa_Relacionada",
             "Cargo_Pessoa_Relacionada", "Tipo_Parentesco"], [
                (CNPJ, "10", "300", "Maria Aparecida Souza", "111.222.333-44", "Presidente do Conselho",
                 "Ana Beatriz Costa", "555.666.777-88", "Holding Familiar S.A.", "33.333.333/0001-33", "Diretora", "Irmã"),
            ]),
    }
    p = tmp_path / f"fre_{ano}.zip"
    with zipfile.ZipFile(p, "w") as z:
        for nome, dados in arqs.items():
            z.writestr(nome, dados)
    return tmp_path


# ------------------------------------------------------------------ _num
@pytest.mark.parametrize("s,esperado", [
    ("44434242.05", 44434242.05), ("55.656.814.393,17", 55656814393.17), ("2.668,51", 2668.51),
    ("1.234.567", 1234567.0), ("0,5", 0.5), ("-10.5", -10.5), ("", None), (None, None), ("  ", None), ("abc", None),
])
def test_num_aceita_os_dois_formatos(s, esperado):
    assert fre._num(s) == esperado


# ------------------------------------------------------------------ documento / versão
def test_documento_pega_a_maior_versao_numerica(pasta):
    d = fre.documento(CNPJ, 2026, pasta)
    assert d["versao"] == 10 and d["id_doc"] == "300"       # 10 > 2 (comparação numérica, não de texto)
    assert d["link"] == "http://x/300" and d["dt_receb"] == "2026-07-01" and d["dt_refer"] == "2026-12-31"


def test_documento_aceita_cnpj_sem_pontuacao_e_devolve_none_se_ausente(pasta):
    assert fre.documento("11111111000111", 2026, pasta)["id_doc"] == "300"
    assert fre.documento("99.999.999/0001-99", 2026, pasta) is None
    assert fre.documento(CNPJ, 2010, pasta) is None          # ZIP inexistente
    assert fre.resumo(CNPJ, 2010, pasta) is None


def test_so_a_versao_mais_recente_e_lida(pasta):
    r = fre.remuneracao(CNPJ, 2026, pasta)
    assert 999.0 not in [v for ex in r["dados"].values() for v in ex.values()]
    assert r["fonte"] == {"arquivo": "fre_2026.zip", "tabela": "remuneracao_total_orgao", "versao": 10,
                          "id_doc": "300", "link": "http://x/300"}
    assert all(p["parte"] != "Fornecedora Antiga Ltda." for p in fre.partes_relacionadas(CNPJ, 2026, pasta)["dados"])
    assert all(a["acionista"] != "Antigo S.A." for a in fre.acionistas(CNPJ, 2026, pasta)["dados"])
    assert fre.free_float(CNPJ, 2026, pasta)["dados"]["n_pf"] == 17570


# ------------------------------------------------------------------ tabelas
def test_remuneracao_soma_orgaos_e_confere_com_total_informado(pasta):
    d = fre.remuneracao(CNPJ, 2026, pasta)["dados"]
    assert d["2025"]["Diretoria Estatutária"] == 5000.50              # formato BR
    assert d["2025"]["Conselho de Administração"] == 1000.25          # formato ponto
    assert d["2025"]["total"] == pytest.approx(6000.75)
    assert d["2025"]["total_informado"] == 55656814393.17             # BR com milhares
    assert d["2024"]["total"] == 7000.0


def test_partes_relacionadas_formatos_e_truncamento(pasta):
    ps = fre.partes_relacionadas(CNPJ, 2026, pasta)["dados"]
    h = next(p for p in ps if p["parte"] == "Holding Familiar S.A.")
    assert h["montante"] == 44434242.05 and h["saldo"] == 2668.51     # ponto e BR
    assert len(h["objeto"]) == 200 and len(h["natureza"]) == 200
    assert h["relacao"] == "Controladora" and h["posicao"] == "Credor" and h["data"] == "2025-12-31"


def test_parte_relacionada_pf_vira_pessoa_fisica_e_cpf_sai_do_texto(pasta):
    ps = fre.partes_relacionadas(CNPJ, 2026, pasta)["dados"]
    pf = next(p for p in ps if p["parte"] == "pessoa física")
    assert "Joao" not in pf["relacao"] and pf["relacao"].startswith("pessoa física")
    assert not CPF.search(json.dumps(pf))


def test_acionistas_so_primeiro_nivel_e_pf_anonimizada(pasta):
    ac = fre.acionistas(CNPJ, 2026, pasta)["dados"]
    assert len(ac) == 3                                                # a linha de 2º nível não entra
    nomes = [a["acionista"] for a in ac]
    assert "pessoa física" in nomes and "Roberto Alves Lima" not in nomes
    assert "Holding Familiar S.A." in nomes and "Outros" in nomes     # PJ e "Outros" ficam
    h = next(a for a in ac if a["acionista"] == "Holding Familiar S.A.")
    assert h["controlador"] is True and h["acordo"] is True and h["pct_total"] == 50.5 and h["tipo_pessoa"] == "PJ"
    o = next(a for a in ac if a["acionista"] == "Outros")
    assert o["pct_on"] == 29.5 and o["controlador"] is False         # '29,5' em formato BR


def test_tem_controlador():
    assert fre.tem_controlador([{"controlador": False}, {"controlador": True}]) is True
    assert fre.tem_controlador([{"controlador": False}]) is False
    # lista vazia = o FRE não informou o 1º nível, não prova capital pulverizado (adversário, 07/10/2026)
    assert fre.tem_controlador([]) is None and fre.tem_controlador(None) is None


def test_free_float(pasta):
    ff = fre.free_float(CNPJ, 2026, pasta)["dados"]
    assert ff == {"pct_on_circulacao": 29.5, "pct_pn_circulacao": 0.0, "pct_total_circulacao": 29.5,
                  "n_pf": 17570.0, "n_pj": 67.0, "n_institucionais": 136.0}


def test_administradores_sem_nome_e_com_resumo_por_orgao(pasta):
    r = fre.administradores(CNPJ, 2026, pasta)
    lista = r["dados"]["lista"]
    assert len(lista) == 3 and {a["cargo"] for a in lista} == {"Presidente", "Conselheiro", "Diretor Presidente"}
    assert next(a for a in lista if a["cargo"] == "Presidente")["eleito_controlador"] is True
    assert all(set(a) == {"orgao", "cargo", "eleito_controlador", "inicio_primeiro_mandato"} for a in lista)
    assert r["dados"]["resumo"] == {"Conselho de Administração": {"n": 2, "eleitos_controlador": 1},
                                    "Diretoria": {"n": 1, "eleitos_controlador": 0}}
    for nome in NOMES_PROIBIDOS:
        assert nome not in json.dumps(r, ensure_ascii=False)


def test_relacao_familiar(pasta):
    rf = fre.relacao_familiar(CNPJ, 2026, pasta)["dados"]
    assert rf == [{"cargo_administrador": "Presidente do Conselho", "cargo_pessoa_relacionada": "Diretora",
                   "emissor_pessoa_relacionada": "Holding Familiar S.A.", "parentesco": "Irmã"}]


def test_tag_along_nao_existe_no_fre():
    assert fre.tag_along(CNPJ, 2026) is None


# ------------------------------------------------------------------ LGPD no resumo inteiro
def test_resumo_nao_vaza_cpf_nem_nome_de_pessoa(pasta):
    r = fre.resumo(CNPJ, 2026, pasta)
    s = json.dumps(r, ensure_ascii=False)
    assert not CPF.search(s)
    for nome in NOMES_PROIBIDOS:
        assert nome not in s
    assert r["documento"]["id_doc"] == "300" and r["tem_controlador"] is True and r["tag_along"] is None
    assert set(r) >= {"documento", "remuneracao", "partes_relacionadas", "acionistas", "free_float",
                      "administradores", "relacao_familiar", "tem_controlador", "tag_along"}


def test_tabela_ausente_no_zip_devolve_dados_vazios(tmp_path):
    p = tmp_path / "fre_2026.zip"
    with zipfile.ZipFile(p, "w") as z:
        z.writestr("fre_cia_aberta_2026.csv", _idx([[CNPJ, "2026-12-31", "1", "E", "1", "FRE WEB", "1", "2026-01-01", "l"]]))
    assert fre.partes_relacionadas(CNPJ, 2026, tmp_path)["dados"] == []
    assert fre.free_float(CNPJ, 2026, tmp_path)["dados"] is None
    assert fre.resumo(CNPJ, 2026, tmp_path)["tem_controlador"] is None


def test_sem_tratamento_apaga_nome_em_cargo():
    t = fre._sem_tratamento("O Sr. Benjamin Steinbruch é Presidente do Conselho de Administração")
    assert "Steinbruch" not in t and "Benjamin" not in t and "Presidente do Conselho" in t


def test_apagar_nomes_do_documento_em_qualquer_campo():
    saida = fre._apagar({"a": [{"x": "Contrato com Maria Souza Lima, diretora"}]}, {"Maria Souza Lima"})
    assert "Maria" not in str(saida) and fre.PF in str(saida)
