"""Uma passada por todos os ZIPs da CVM -> dados/fatos_cvm.parquet.

Depois desta fatia, cada data de corte é uma FATIA do parquet e a grade de 288 combinações é
aritmética. Sem isto, cada corte reabriria 33 ZIPs.

Chave: (cd_cvm, categ, dt_refer, versao, ordem_exerc, conta). Nunca ANO — `dfp_2017.zip` tem quatro
DT_REFER distintos, porque exercício social diferente de dezembro existe (SMTO3 fecha em março).
`versao` entra na chave para o ledger poder casar com o índice de DT_RECEB e saber se o número é o
que se via em T.

Dois planos de conta, e isto não é detalhe: o plano de BANCO é outro. Medido em BCO BRASIL,
`3.01` é "Receitas da Intermediação Financeira", não receita de venda — os mapas industriais de
`coletar_cvm.py:35-44` leriam lixo em financeira. Hoje isso não aparece porque `lote1_bancos.py`
tem tudo digitado à mão. O plano financeiro usa só três campos estáveis em qualquer plano: PL
(2.03 menos 2.03.09), lucro do controlador (3.11.01, com 3.11 de reserva) e ações.

AÇÕES — o achado que mudou o desenho desta fatia. `composicao_capital` só existe nos ZIPs de DFP e
ITR de **2020 em diante**; de 2010 a 2019 não há contagem de ações no dado estruturado de DFP/ITR.
Sem ações não há valor por ação, e isso cobriria 12 dos 24 cortes — toda a janela de calibração. A
fonte que cobre o período inteiro é o **FRE** (`fre_cia_aberta_capital_social_{ano}.csv`, desde
2010). Armadilha medida ali: usar `Tipo_Capital = "Capital Emitido"` dá 5,73 bi de ações para o BB
contra 2,87 bi de integralizadas — o dobro exato, que cortaria todo o P/C pela metade. Vale
"Capital Integralizado". Os seis anos em que as duas fontes coexistem (2020-2025) servem de
conferência cruzada, e o teste desta fatia a exige.

As linhas da DFC (D&A, capex, dividendo pago, juros pagos, principal de arrendamento) são
identificadas por DESCRIÇÃO, não por código, então a DFC entra INTEIRA no parquet — não há lista de
códigos que a cubra. É o que o Owner Earnings precisa.
"""
from __future__ import annotations

import io
import re
import zipfile
from pathlib import Path

import pandas as pd

CACHE = Path(__file__).resolve().parent.parent.parent / "dados" / "cvm"
DESTINO = Path(__file__).resolve().parent.parent / "dados"

# Contas por CÓDIGO, que é o que é estável entre empresas e anos. União do que o plano industrial e
# o financeiro precisam. Nomes iguais aos de coletar_cvm.py para a conferência cruzada ser direta.
CONTAS: dict[str, str] = {
    # DRE
    "3.01": "receita", "3.02": "custo", "3.03": "lucro_bruto",
    "3.04.01": "desp_vendas", "3.04.02": "desp_ga",
    "3.04.04": "outras_receitas_op", "3.04.05": "outras_despesas_op",
    "3.05": "ebit", "3.06": "res_fin", "3.06.02": "desp_fin",
    "3.07": "lair", "3.08": "ir", "3.11": "lucro", "3.11.01": "lucro_controlador",
    # LPA — serve de conferência da contagem de ações (acoes ~ lucro_controlador / LPA)
    "3.99.01.01": "lpa_1", "3.99.01.02": "lpa_2",
    # BPA
    "1": "ativo", "1.01": "ac", "1.01.01": "caixa", "1.01.02": "aplic_cp",
    "1.01.03": "receber", "1.01.04": "estoques",
    "1.02": "anc", "1.02.01": "rlp", "1.02.02": "investimentos",
    "1.02.03": "imobilizado", "1.02.04": "intangivel",
    # BPP
    "2": "passivo", "2.01": "pc", "2.01.04": "emprest_cp",
    "2.02": "pnc", "2.02.01": "emprest_lp",
    "2.03": "pl", "2.03.04": "reservas_lucro", "2.03.09": "nao_controladores",
    # IFRS 16: arrendamento é dívida (doutrina §11.1)
    "2.01.04.03": "arrendamento_cp", "2.02.01.03": "arrendamento_lp",
    # DFC (os totais; o detalhe vem das linhas inteiras, abaixo)
    "6.01": "fco", "6.02": "fci", "6.03": "fcf",
}

DEMONSTRACOES = ("DRE", "BPA", "BPP")          # filtradas por código + por descrição
DFC_INTEIRA = ("DFC_MI", "DFC_MD")             # entram inteiras (linhas por descrição)

# Campos cujo CÓDIGO depende do plano de contas e que portanto NÃO podem ser lidos por código.
# Medido no BCO BRASIL FY2014 consolidado:
#   industrial            banco
#   2.03 = PL             2.03 = "Passivos Financeiros ao Custo Amortizado" (R$ 1,1 TRILHÃO)
#   2.03.09 = minorit.    2.08 = "Patrimônio Líquido Consolidado" (R$ 85,4 bi, o certo)
#   3.11 = lucro          3.09 = "Lucro/Prejuízo Consolidado do Período"
#   3.11.01 = controlador 3.09.01 = "Atribuído a Sócios da Empresa Controladora"
# Ler `2.03` como PL de banco dava PL = 86% do ativo. A descrição identifica o campo; o código não.
# Estas linhas entram no parquet ADEMAIS das da lista de códigos, e o ledger decide qual usar.
POR_DESCRICAO: dict[str, str] = {
    "pl_desc": r"^patrim[ôo]nio l[íi]quido( consolidado)?$",
    "nao_controladores_desc": r"^participa[çc][õo]es? .*n[ãa]o controladores?$|^.*de n[ãa]o controladores$",
    "lucro_desc": r"^lucro[/ ]?preju[íi]zo (consolidado |l[íi]quido )?d[oa] (per[íi]odo|exerc[íi]cio)$",
    "lucro_controlador_desc": r"^atribu[íi]d[oa] a s[óo]cios d[ae] (empresa )?controladora$",
    # IFRS 16: o arrendamento tem de ser achado ONDE ESTIVER, porque nem toda empresa o lança
    # dentro de 2.01.04/2.02.01. Ver a regra de dupla contagem em pit._contas_de.
    "arrendamento_desc": r"arrendamento|loca[çc][ãa]o|ifrs ?16|direito de uso",
}
_RE_DESC = {k: re.compile(v, re.I) for k, v in POR_DESCRICAO.items()}


def _ler(z: zipfile.ZipFile, nome: str) -> pd.DataFrame | None:
    alvo = [n for n in z.namelist() if n.lower().endswith(nome.lower())]
    if not alvo:
        return None
    d = pd.read_csv(io.BytesIO(z.read(alvo[0])), sep=";", encoding="latin-1", dtype=str)
    return d if not d.empty else None


ESCALAS = {"MIL": 1.0, "UNIDADE": 0.001}


def _escala(d: pd.DataFrame) -> pd.Series:
    """A CVM declara a escala por linha: MIL ou UNIDADE. Normaliza tudo para R$ MIL.

    LEVANTA em escala desconhecida, em vez de assumir MIL. Tratar escala nova como MIL seria erro
    silencioso de 1000x. Varrido em dfp_{2011,2016,2021,2025}: só MIL (317.558 linhas) e UNIDADE
    (8.210), e MOEDA só REAL — então hoje isto nunca dispara; a questão é o dia em que disparar.
    """
    esc = d.get("ESCALA_MOEDA")
    if esc is None:
        return pd.Series(1.0, index=d.index)
    limpa = esc.str.upper().str.strip()
    desconhecidas = set(limpa.dropna().unique()) - set(ESCALAS)
    if desconhecidas:
        raise ValueError(f"ESCALA_MOEDA desconhecida: {sorted(desconhecidas)} — definir o fator "
                         "antes de usar, nunca assumir MIL (erro de 1000x)")
    return limpa.map(ESCALAS).astype(float)


def _normalizar(d: pd.DataFrame, bloco: str, conjunto: str) -> pd.DataFrame:
    saida = pd.DataFrame({
        "cd_cvm": pd.to_numeric(d["CD_CVM"], errors="coerce").astype("Int64"),
        "dt_refer": d["DT_REFER"],
        "versao": pd.to_numeric(d["VERSAO"], errors="coerce").astype("Int64"),
        "ordem_exerc": d["ORDEM_EXERC"].str.upper().str.replace("Ú", "U").str.replace("Ê", "E"),
        "dt_ini_exerc": d.get("DT_INI_EXERC"),
        "dt_fim_exerc": d.get("DT_FIM_EXERC"),
        "codigo": d["CD_CONTA"].str.strip(),
        "descricao": d["DS_CONTA"].str.strip(),
        "valor": pd.to_numeric(d["VL_CONTA"], errors="coerce") * _escala(d),
        "bloco": bloco,
        "conjunto": conjunto,                   # "con" (consolidado) ou "ind" (individual)
    })
    return saida.dropna(subset=["cd_cvm", "versao", "valor"])


def fatos_de_zip(categ: str, ano: int) -> pd.DataFrame:
    """Todos os fatos de um ZIP: contas da lista (DRE/BPA/BPP) + a DFC inteira."""
    caminho = CACHE / f"{categ}_{ano}.zip"
    if not caminho.exists():
        return pd.DataFrame()
    partes = []
    with zipfile.ZipFile(caminho) as z:
        for bloco in DEMONSTRACOES:
            for conjunto in ("con", "ind"):
                d = _ler(z, f"{categ}_cia_aberta_{bloco}_{conjunto}_{ano}.csv")
                if d is None:
                    continue
                cod = d["CD_CONTA"].str.strip()
                desc = d["DS_CONTA"].str.strip()
                mantem = cod.isin(CONTAS)
                for re_ in _RE_DESC.values():                 # linhas que a descrição identifica
                    mantem |= desc.str.contains(re_, na=False)
                d = d[mantem]
                if not d.empty:
                    partes.append(_normalizar(d, bloco, conjunto))
        for bloco in DFC_INTEIRA:
            for conjunto in ("con", "ind"):
                d = _ler(z, f"{categ}_cia_aberta_{bloco}_{conjunto}_{ano}.csv")
                if d is not None:
                    partes.append(_normalizar(d, bloco, conjunto))
    if not partes:
        return pd.DataFrame()
    out = pd.concat(partes, ignore_index=True)
    out["categ"] = categ
    out["ano_zip"] = ano
    out["campo"] = out["codigo"].map(CONTAS)
    # `campo_desc`: o campo que a DESCRIÇÃO identifica, independente do plano de contas. É o que
    # permite ler PL e lucro de banco (2.08 / 3.09) sem confundir com os códigos industriais.
    out["campo_desc"] = pd.NA
    for campo, re_ in _RE_DESC.items():
        bate = out["descricao"].str.contains(re_, na=False) & out["campo_desc"].isna()
        out.loc[bate, "campo_desc"] = campo
    return out


def acoes_de_fre(ano: int) -> pd.DataFrame:
    """Ações integralizadas do FRE — a única fonte que cobre 2010-2019. **Precisão em aberto.**

    `Tipo_Capital = "Capital Integralizado"` é o campo certo: para o BB em 2022 dá 2.865.417.020,
    idêntico ao `composicao_capital` da DFP do mesmo ano. ("Capital Autorizado" é o teto estatutário
    e dá 10x isso; "Capital Subscrito" coincide com o integralizado quando tudo foi pago.)

    DUAS armadilhas medidas, as duas tratadas aqui:

    1. A tabela carrega o HISTÓRICO de autorizações de capital, uma linha por
       `Data_Autorizacao_Aprovacao`. O BB em 2022 tem duas linhas de Capital Integralizado:
       2.865.417.020 (aprovação de 2023-04-27) e 286.541.720 (aprovação de 2015-04-28) — um décimo,
       aparentemente um dígito a menos na própria entrega. Pegar linha arbitrária é erro silencioso
       de 10x. A regra é: a autorização mais recente com data <= corte. 312 companhia-anos têm mais
       de um valor distinto, e esses saem com `acoes_ambiguo=True`.
    2. `Data_Referencia` do FRE é **01/01** (3720 de ~3800 linhas em 2022), ou seja, o FRE do ano
       Y+1 descreve o fim do ano Y. Comparar FRE de Y com `composicao_capital` de Y compara datas a
       um ano de distância.

    **PENDÊNCIA RESOLVIDA NA FATIA 8 (06/10/2026; `ledger/diagnostico_acoes.py`).** Os 58,4% eram
    sobretudo erro de UNIDADE DA REFERÊNCIA, não do FRE: o `composicao_capital` da DFP vem em
    MILHARES em ~27% das companhia-anos (BRB 2020: 28.014 contra 28.014.650 no FRE). Medido em
    companhia-anos de 2020-24 (refeito após o `adversario`, que achou 2022 fora da janela do FRE e
    um mapa ticker->CNPJ com lixo da FCA): sem corrigir a unidade o FRE concorda em 58,4%; aceitando
    razão 1 ou 1000, em 86,7%; entre as 485 empresa-anos ACIMA do piso de liquidez, em 93,2%
    (tolerância 1%; a 1ª medição, com a janela errada, dava 86,0% e 94,0%). Das três hipóteses: (a) como formulada — discordância
    concentrada em ilíquida — REFUTADA pelo critério declarado (a causa dominante é a unidade); (b)
    somar ON+PN rende só +0,4 p.p. (resolve casos como o BB 2023, com `Quantidade_Total_Acoes`=0);
    (c) não foi necessária. Resíduo de ~7% nas líquidas: arredondamento de milhares acima de 1%,
    desdobramento entre a aprovação e 31/12, e o BB 2021 (linha de 2015 com um dígito a menos,
    que é o dado de verdade em T e fica com `acoes_ambiguo`). O ledger usa só o FRE — nunca o
    `composicao_capital` — logo o erro de unidade não contamina o P/C; mas qualquer uso futuro do
    `composicao_capital` precisa normalizar a unidade primeiro.
    """
    caminho = CACHE / f"fre_{ano}.zip"
    if not caminho.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(caminho) as z:
        cap = _ler(z, f"fre_cia_aberta_capital_social_{ano}.csv")
        cab = _ler(z, f"fre_cia_aberta_{ano}.csv")
    if cap is None or cab is None:
        return pd.DataFrame()
    cap = cap[cap["Tipo_Capital"].str.strip().str.lower() == "capital integralizado"]
    if cap.empty:
        return pd.DataFrame()
    d = pd.DataFrame({
        "cnpj": cap["CNPJ_Companhia"],
        "dt_refer": cap["Data_Referencia"],
        "versao": pd.to_numeric(cap["Versao"], errors="coerce").astype("Int64"),
        "aprovacao": cap["Data_Autorizacao_Aprovacao"].fillna(""),
        "acoes_on": pd.to_numeric(cap["Quantidade_Acoes_Ordinarias"], errors="coerce"),
        "acoes_pn": pd.to_numeric(cap["Quantidade_Acoes_Preferenciais"], errors="coerce"),
        "acoes_total": pd.to_numeric(cap["Quantidade_Total_Acoes"], errors="coerce"),
    }).dropna(subset=["acoes_total"])
    # Armadilha 1: a tabela é histórico de autorizações. Marca quem tem mais de um valor distinto
    # para o mesmo documento, e mantém TODAS as linhas — a escolha da válida é do ledger, que sabe
    # a data de corte e aplica "última autorização <= T".
    distintos = d.groupby(["cnpj", "dt_refer", "versao"])["acoes_total"].transform("nunique")
    d["acoes_ambiguo"] = distintos > 1
    # DT_RECEB vem do cabeçalho: sem ele não há como saber se a contagem era pública em T.
    cab = cab.rename(columns={"CNPJ_CIA": "cnpj", "DT_REFER": "dt_refer", "VERSAO": "versao",
                              "DT_RECEB": "dt_receb", "CD_CVM": "cd_cvm"})
    cab["versao"] = pd.to_numeric(cab["versao"], errors="coerce").astype("Int64")
    cab["cd_cvm"] = pd.to_numeric(cab["cd_cvm"], errors="coerce").astype("Int64")
    d = d.merge(cab[["cnpj", "dt_refer", "versao", "dt_receb", "cd_cvm"]],
                on=["cnpj", "dt_refer", "versao"], how="left")
    d["fonte_acoes"] = "FRE"
    d["ano_zip"] = ano
    return d.dropna(subset=["cd_cvm", "dt_receb"])


def acoes_de_composicao(categ: str, ano: int) -> pd.DataFrame:
    """Ações integralizadas menos tesouraria, do `composicao_capital` da DFP/ITR (2020+).

    Serve de conferência cruzada do FRE nos anos em que as duas fontes coexistem. Keyed por CNPJ:
    este CSV não traz CD_CVM.
    """
    caminho = CACHE / f"{categ}_{ano}.zip"
    if not caminho.exists():
        return pd.DataFrame()
    with zipfile.ZipFile(caminho) as z:
        cap = _ler(z, f"{categ}_cia_aberta_composicao_capital_{ano}.csv")
    if cap is None:
        return pd.DataFrame()
    tot = pd.to_numeric(cap["QT_ACAO_TOTAL_CAP_INTEGR"], errors="coerce")
    tes = pd.to_numeric(cap.get("QT_ACAO_TOTAL_TESOURO"), errors="coerce").fillna(0)
    d = pd.DataFrame({
        "cnpj": cap["CNPJ_CIA"], "dt_refer": cap["DT_REFER"],
        "versao": pd.to_numeric(cap["VERSAO"], errors="coerce").astype("Int64"),
        "acoes_integralizadas": tot, "acoes_tesouraria": tes,
        "acoes_total": tot - tes,
    }).dropna(subset=["acoes_total"])
    d["fonte_acoes"] = f"{categ}_composicao"
    d["ano_zip"] = ano
    return d


def construir(anos: range | None = None) -> dict[str, Path]:
    """Materializa fatos_cvm.parquet, acoes_fre.parquet e acoes_composicao.parquet."""
    from .indice_cvm import anos_em_disco

    DESTINO.mkdir(parents=True, exist_ok=True)
    saidas: dict[str, Path] = {}

    partes = []
    for categ in ("dfp", "itr"):
        for ano in (anos or anos_em_disco(categ)):
            d = fatos_de_zip(categ, ano)
            if not d.empty:
                partes.append(d)
                print(f"  {categ}_{ano}: {len(d)} fatos", flush=True)
    fatos = pd.concat(partes, ignore_index=True)
    p = DESTINO / "fatos_cvm.parquet"
    fatos.to_parquet(p, index=False)
    saidas["fatos"] = p
    print(f"fatos_cvm.parquet: {len(fatos)} linhas - {fatos['cd_cvm'].nunique()} companhias "
          f"- dt_refer {fatos['dt_refer'].min()} a {fatos['dt_refer'].max()}")

    fre = [acoes_de_fre(a) for a in range(2010, 2027)]
    fre = pd.concat([x for x in fre if not x.empty], ignore_index=True)
    p = DESTINO / "acoes_fre.parquet"
    fre.to_parquet(p, index=False)
    saidas["acoes_fre"] = p
    print(f"acoes_fre.parquet: {len(fre)} linhas - {fre['cd_cvm'].nunique()} companhias "
          f"- dt_refer {fre['dt_refer'].min()} a {fre['dt_refer'].max()}")

    comp = [acoes_de_composicao(c, a) for c in ("dfp", "itr") for a in range(2020, 2027)]
    comp = [x for x in comp if not x.empty]
    if comp:
        comp = pd.concat(comp, ignore_index=True)
        p = DESTINO / "acoes_composicao.parquet"
        comp.to_parquet(p, index=False)
        saidas["acoes_composicao"] = p
        print(f"acoes_composicao.parquet: {len(comp)} linhas (conferência cruzada 2020+)")
    return saidas


if __name__ == "__main__":
    construir()
