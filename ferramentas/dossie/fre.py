"""Leitor do FRE da CVM (fonte A) a partir dos ZIPs locais em dados/cvm/fre_{ano}.zip.

LGPD: nunca devolve CPF nem nome de pessoa física. Colunas com CPF são descartadas; acionista ou
parte relacionada pessoa física vira "pessoa física"; nomes de administradores não saem (só órgão/cargo).
Todas as funções leem apenas a versão mais recente (maior VERSAO) do documento do CNPJ no ano.
"""
import csv
import io
import pathlib
import re
import zipfile

PASTA = pathlib.Path(__file__).resolve().parent.parent / "dados" / "cvm"
PF = "pessoa física"
_CPF = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}|\*{3}\.\d{3}\.\d{3}-\*{2}")
# Marcas de pessoa jurídica / entidade; nome sem nenhuma delas e "com cara de gente" vira PF (lado seguro).
_PJ = re.compile(
    r"\b(s\.?\s?a\.?|s/a|ltda\.?|cia\.?|companhia|participa\w*|banco|fundo|fip|fia|holding|eireli|brasil\w*|"
    r"grupo|empresa|sociedade|associa\w*|instituto|funda\w*|cons[oó]rcio|cooperativa|com[eé]rcio|"
    r"ind[uú]stria\w*|servi[cç]os|energia|petr\w+|mineral\w*|log[ií]stica|capital|invest\w*|"
    r"seguros?|previd\w*|trust|bank|inc|corp|llc|ltd|gmbh|plc|sicav|sarl|limited|partners|"
    r"controlad\w*|coligad\w*|acionista\w*|administrador\w*|diretor\w*|conselh\w*|membro|parte|joint|venture|afiliad\w*|"
    r"tesouraria|outros|minorit\w*|governo|uni[aã]o|estado|munic[ií]pio|ações|a[cç][oõ]es)\b",
    re.I,
)
_CONECTOR = {"de", "da", "do", "dos", "das", "e", "di", "del", "von", "van", "bin"}


def _num(s):
    """Número em '44434242.05' ou no formato BR '55.656.814.393,17'; vazio/inválido → None."""
    if s is None:
        return None
    s = str(s).strip()
    if not s:
        return None
    if "," in s:
        s = s.replace(".", "").replace(",", ".")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    try:
        return float(s)
    except ValueError:
        return None


def _digitos(s):
    return re.sub(r"\D", "", s or "")


def _scrub(txt, limite=None):
    """Tira CPF de texto livre e trunca."""
    t = _CPF.sub("[cpf removido]", (txt or "").strip())
    return t[:limite] if limite else t


def _parece_pessoa(nome):
    """Nome sem marca de PJ, 2+ palavras capitalizadas (ou conectores): trata como pessoa física."""
    nome = (nome or "").strip()
    if not nome or _PJ.search(nome) or re.search(r"\d", nome):
        return False
    toks = nome.replace(".", " ").split()
    if len(toks) < 2 or len(toks) > 6:
        return False
    return all(t.lower() in _CONECTOR or t[0].isupper() for t in toks)


def _eh_pf(tipo, doc, nome=""):
    """PF por Tipo_Pessoa, por documento de 11 dígitos ou (sem documento/tipo) por cara de nome próprio."""
    d = len(_digitos(doc))
    if tipo == "PF" or d == 11:
        return True
    if tipo == "PJ" or d == 14:
        return False
    return _parece_pessoa(nome)


def _nome_pj(nome, tipo, doc):
    return PF if _eh_pf(tipo, doc, nome) else _scrub(nome)


def _relacao(txt):
    """Relação com o emissor: texto livre pode citar pessoa ("Fulano de Tal, sócio...")."""
    t = _scrub(txt, 200)
    partes = re.split(r"\s*[,(;]\s*|\s+-\s+", t, maxsplit=1)
    if _parece_pessoa(partes[0]):
        return PF + (", " + partes[1][:80] if len(partes) > 1 else "")
    return _sem_nomes(t)


_TRATAMENTO = re.compile(r"\b(?:[OoAa]s?\s+)?S(?:r|ra|rs|ras)\.?\s+[A-ZÀ-Ý][\wÀ-ÿ'.-]*"
                         r"(?:\s+(?:d[aeo]s?|e|[A-ZÀ-Ý][\wÀ-ÿ'.-]*))*")


def _sem_tratamento(t):
    """Cargo em texto livre ("O Sr. Fulano de Tal é ..."): troca o tratamento + nome por "pessoa física"."""
    return _TRATAMENTO.sub(PF, _scrub(t)) if t else t


def _nomes_pf(cnpj, ano, pasta):
    """Nomes de pessoa física citados no próprio documento (administradores, relação familiar, acionistas PF):
    a 2ª camada da LGPD apaga qualquer um deles que tenha escapado nos textos livres."""
    doc = documento(cnpj, ano, pasta)
    if doc is None:
        return set()
    nomes = set()
    for tab, cols in (("administrador_membro_conselho_fiscal", ("Nome",)),
                      ("relacao_familiar", ("Nome_Administrador", "Nome_Pessoa_Relacionada")),
                      ("membro_comite", ("Nome",))):
        for r in _ler(ano, tab, pasta):
            if r.get("ID_Documento") == doc["id_doc"]:
                nomes.update((r.get(c) or "").strip() for c in cols)
    for r in _ler(ano, "posicao_acionaria", pasta):
        if r.get("ID_Documento") == doc["id_doc"] and _eh_pf(r.get("Tipo_Pessoa_Acionista"), r.get("CPF_CNPJ_Acionista"), r.get("Acionista")):
            nomes.add((r.get("Acionista") or "").strip())
    return {n for n in nomes if len(n) >= 5}


def _apagar(obj, nomes):
    if isinstance(obj, str):
        for n in nomes:
            if n.lower() in obj.lower():
                obj = re.sub(re.escape(n), PF, obj, flags=re.I)
        return obj
    if isinstance(obj, dict):
        return {k: _apagar(v, nomes) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_apagar(v, nomes) for v in obj]
    return obj


def _sem_nomes(t):
    """Texto livre: corta antes de enumerar pessoas ("os Srs. ...", "Sr.", "Sra.")."""
    return re.split(r"\(?\bos?\s+sr[s]?\.?|\bsr[a]?\.?\s", t, maxsplit=1, flags=re.I)[0].rstrip(" (,;-")


# ------------------------------------------------------------------ acesso ao ZIP
def _caminho(ano, pasta):
    return pathlib.Path(pasta) / f"fre_{ano}.zip"


def _ler(ano, nome, pasta):
    """Linhas (dict) de um CSV do ZIP; [] se o ZIP ou o CSV não existir."""
    p = _caminho(ano, pasta)
    if not p.exists():
        return []
    csv.field_size_limit(10**9)
    with zipfile.ZipFile(p) as z:
        alvo = f"fre_cia_aberta_{nome}_{ano}.csv" if nome else f"fre_cia_aberta_{ano}.csv"
        if alvo not in z.namelist():
            return []
        with z.open(alvo) as f:
            return list(csv.DictReader(io.TextIOWrapper(f, encoding="latin-1", newline=""), delimiter=";"))


def documento(cnpj, ano, pasta=PASTA):
    """Linha do índice com a MAIOR versão do CNPJ naquele ZIP, ou None."""
    alvo = _digitos(cnpj)
    melhor = None
    for r in _ler(ano, "", pasta):
        if _digitos(r.get("CNPJ_CIA")) != alvo:
            continue
        v = int(_num(r.get("VERSAO")) or 0)
        if melhor is None or v > melhor[0]:
            melhor = (v, r)
    if melhor is None:
        return None
    v, r = melhor
    return {"cnpj": r["CNPJ_CIA"], "dt_refer": r["DT_REFER"], "versao": v, "id_doc": r["ID_DOC"],
            "dt_receb": r["DT_RECEB"], "link": r["LINK_DOC"]}


def _linhas(cnpj, ano, tabela, pasta):
    """(doc, linhas da tabela só do id_doc mais recente) ou (None, [])."""
    doc = documento(cnpj, ano, pasta)
    if doc is None:
        return None, []
    return doc, [r for r in _ler(ano, tabela, pasta) if r.get("ID_Documento") == doc["id_doc"]]


def _fonte(doc, ano, tabela):
    return {"arquivo": f"fre_{ano}.zip", "tabela": tabela, "versao": doc["versao"],
            "id_doc": doc["id_doc"], "link": doc["link"]}


def _pacote(cnpj, ano, tabela, pasta, f):
    """Aplica f(linhas) e devolve {"dados","fonte"}; None se não há documento."""
    doc, linhas = _linhas(cnpj, ano, tabela, pasta)
    if doc is None:
        return None
    return {"dados": f(linhas), "fonte": _fonte(doc, ano, tabela)}


# ------------------------------------------------------------------ tabelas
def remuneracao(cnpj, ano, pasta=PASTA):
    """{exercício: {órgão: valor, "total": soma dos órgãos, "total_informado": Total_Remuneracao}}."""
    def f(linhas):
        out = {}
        for r in linhas:
            ex = (r.get("Data_Fim_Exercicio_Social") or "")[:4]
            d = out.setdefault(ex, {"total": 0.0, "total_informado": _num(r.get("Total_Remuneracao"))})
            v = _num(r.get("Total_Remuneracao_Orgao"))
            org = r.get("Orgao_Administracao") or "?"
            d[org] = (d.get(org) or 0.0) + (v or 0.0)
            d["total"] += v or 0.0
        return out
    return _pacote(cnpj, ano, "remuneracao_total_orgao", pasta, f)


def partes_relacionadas(cnpj, ano, pasta=PASTA):
    """Transações com partes relacionadas; PF anonimizada, texto livre truncado em 200 caracteres."""
    def f(linhas):
        return [{
            "parte": _nome_pj(r.get("Parte_Relacionada"), r.get("Tipo_Pessoa"), r.get("Documento_Parte_Relacionada")),
            "relacao": _relacao(r.get("Relacao_Emissor")),
            "data": r.get("Data_Transacao"),
            "objeto": _scrub(r.get("Objeto_Contrato"), 200),
            "montante": _num(r.get("Montante_Envolvido")),
            "saldo": _num(r.get("Saldo_Existente")),
            "natureza": _scrub(r.get("Natureza_Razao_Operacao"), 200),
            "posicao": r.get("Posicao_Contratual_Emissor"),
        } for r in linhas]
    return _pacote(cnpj, ano, "transacao_parte_relacionada", pasta, f)


def acionistas(cnpj, ano, pasta=PASTA):
    """Acionistas de 1º nível (sem Acionista_Relacionado); PF vira "pessoa física"."""
    def f(linhas):
        return [{
            "acionista": _nome_pj(r.get("Acionista"), r.get("Tipo_Pessoa_Acionista"), r.get("CPF_CNPJ_Acionista")),
            "tipo_pessoa": r.get("Tipo_Pessoa_Acionista") or None,
            "pct_on": _num(r.get("Percentual_Acao_Ordinaria_Circulacao")),
            "pct_pn": _num(r.get("Percentual_Acao_Preferencial_Circulacao")),
            "pct_total": _num(r.get("Percentual_Total_Acoes_Circulacao")),
            "controlador": r.get("Acionista_Controlador") == "S",
            "acordo": r.get("Participante_Acordo_Acionistas") == "S",
        } for r in linhas if not (r.get("Acionista_Relacionado") or "").strip()]
    return _pacote(cnpj, ano, "posicao_acionaria", pasta, f)


def tem_controlador(lista):
    """True/False pela lista de `acionistas()["dados"]`; None se a lista está vazia (o FRE não informou o 1º nível —
    não é prova de capital pulverizado; achado do adversário em 07/10/2026)."""
    if not lista:
        return None
    return any(a.get("controlador") for a in lista)


def free_float(cnpj, ano, pasta=PASTA):
    """Distribuição do capital: % em circulação (ON, PN, total) e nº de acionistas por tipo."""
    def f(linhas):
        if not linhas:
            return None
        r = linhas[0]
        return {
            "pct_on_circulacao": _num(r.get("Percentual_Acoes_Ordinarias_Circulacao")),
            "pct_pn_circulacao": _num(r.get("Percentual_Acoes_Preferenciais_Circulacao")),
            "pct_total_circulacao": _num(r.get("Percentual_Total_Acoes_Circulacao")),
            "n_pf": _num(r.get("Quantidade_Acionistas_PF")),
            "n_pj": _num(r.get("Quantidade_Acionistas_PJ")),
            "n_institucionais": _num(r.get("Quantidade_Acionistas_Investidores_Institucionais")),
        }
    return _pacote(cnpj, ano, "distribuicao_capital", pasta, f)


def administradores(cnpj, ano, pasta=PASTA):
    """Administradores sem nome: {"lista": [{orgao, cargo, eleito_controlador, inicio_primeiro_mandato}],
    "resumo": {órgão: {"n", "eleitos_controlador"}}}."""
    def f(linhas):
        lista = [{
            "orgao": r.get("Orgao_Administracao"),
            "cargo": r.get("Cargo_Eletivo_Ocupado"),
            "eleito_controlador": r.get("Eleito_Controlador") == "S",
            "inicio_primeiro_mandato": r.get("Data_Inicio_Primeiro_Mandato") or None,
        } for r in linhas]
        resumo = {}
        for a in lista:
            d = resumo.setdefault(a["orgao"], {"n": 0, "eleitos_controlador": 0})
            d["n"] += 1
            d["eleitos_controlador"] += a["eleito_controlador"]
        return {"lista": lista, "resumo": resumo}
    return _pacote(cnpj, ano, "administrador_membro_conselho_fiscal", pasta, f)


def relacao_familiar(cnpj, ano, pasta=PASTA):
    """Parentescos entre administradores e pessoas ligadas ao emissor, sem nomes de pessoa física."""
    def f(linhas):
        def emissor(r):
            nome = r.get("Nome_Emissor_Pessoa_Relacionada")
            return PF if _parece_pessoa(nome) else _nome_pj(nome, "", r.get("CNPJ_Emissor_Pessoa_Relacionada"))
        return [{
            "cargo_administrador": _sem_tratamento(r.get("Cargo_Administrador")),
            "cargo_pessoa_relacionada": _sem_tratamento(r.get("Cargo_Pessoa_Relacionada")),
            "emissor_pessoa_relacionada": emissor(r),
            "parentesco": r.get("Tipo_Parentesco"),
        } for r in linhas]
    return _pacote(cnpj, ano, "relacao_familiar", pasta, f)


def tag_along(cnpj, ano, pasta=PASTA):
    """Sempre None: nenhuma das 36 tabelas do FRE (conferido em fre_2025.zip e fre_2026.zip) traz
    tag along por classe — nenhuma coluna ou texto contém "tag along". O dossiê pega do estatuto/FCA."""
    return None


def resumo(cnpj, ano, pasta=PASTA):
    """Tudo junto; None se o CNPJ não tem FRE no ano."""
    doc = documento(cnpj, ano, pasta)
    if doc is None:
        return None
    ac = acionistas(cnpj, ano, pasta)
    return _apagar({
        "documento": doc,
        "remuneracao": remuneracao(cnpj, ano, pasta),
        "partes_relacionadas": partes_relacionadas(cnpj, ano, pasta),
        "acionistas": ac,
        "tem_controlador": tem_controlador(ac["dados"]),
        "free_float": free_float(cnpj, ano, pasta),
        "administradores": administradores(cnpj, ano, pasta),
        "relacao_familiar": relacao_familiar(cnpj, ano, pasta),
        "tag_along": tag_along(cnpj, ano, pasta),
    }, _nomes_pf(cnpj, ano, pasta))
