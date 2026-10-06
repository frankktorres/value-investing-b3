"""Os cinco testes de não-vazamento — o portão da fatia 6 e a defesa central do estudo.

Quatro deles são checagem de PROCEDÊNCIA: toda data de recebimento, todo mês de IPCA e toda
contagem de ações usada tem de ser anterior ao corte. O quinto trunca as fontes em T e exige
resultado idêntico.

CORREÇÃO IMPORTANTE (06/10/2026, achado do adversário). A primeira versão deste arquivo afirmava
que o sentinela "é o único que prova ausência de look-ahead". **Era falso, e o teste era uma
tautologia.** Ele truncava o índice por `dt_receb <= T`, que é exatamente o filtro que
`documentos_visiveis` já aplica: truncar era idempotente, o DataFrame saía byte-idêntico e o teste
comparava X com X. Pior, ele não perturbava `_fatos()` nem `_acoes()`, que é de onde vêm os
VALORES. Provado por injeção: um vazamento real (valores vindos das linhas PENULTIMO do documento
do ano seguinte) passava pelo sentinela e pela `auditoria()` sem alarme.

O que o sentinela prova AGORA, e só isto: a SELEÇÃO do ledger — quais exercícios, qual linha de
ações, qual mês de IPCA, e os valores que saem — não muda quando se remove das fontes tudo o que
tem referência posterior a T. `test_5b` injeta um vazamento e exige que o sentinela o PEGUE, para
o teste não voltar a ser vácuo.

O que NENHUM teste pode provar, e que fica declarado: que os valores são os ORIGINAIS, pré-
reapresentação. A CVM serve uma única versão por (cd_cvm, dt_refer) — a última —, então o número
original é irrecuperável do dado aberto. A defesa disponível é outra e é medida: o estado
`contaminado` marca os exercícios cuja versão vista em T é menor que a servida hoje (~1% dos
casos), e `test_parquet_tem_uma_versao_por_exercicio` mostra que não há escolha de versão a errar.
"""
from __future__ import annotations

import pandas as pd
import pytest

from backtest.calendario import mes_ipca_disponivel
from backtest.config import PADRAO
from backtest.ledger import indice_cvm as ic
from backtest.ledger import pit

pytestmark = pytest.mark.skipif(
    not (pit.DADOS / "fatos_cvm.parquet").exists(),
    reason="fatos_cvm.parquet ausente — rode `python -m backtest.ledger.fatos_cvm`")

NEOENERGIA = 15539
BCO_BRASIL = 1023
AMOSTRA_DATAS = ("2014-06-30", "2017-06-30", "2020-12-31", "2025-06-30")


@pytest.fixture(scope="module")
def amostra() -> list[pit.LedgerPIT]:
    """Ledgers de várias companhias em várias datas — base dos testes de procedência."""
    saida = []
    for d in AMOSTRA_DATAS:
        vis = ic.documentos_visiveis("dfp", d)
        cds = sorted(set(vis["cd_cvm"].dropna().astype(int)))[:60]
        for cd in cds:
            l = pit.ledger_em(cd, d)
            if l is not None:
                saida.append(l)
    assert len(saida) > 100, f"amostra pequena demais: {len(saida)} ledgers"
    return saida


# ----------------------------------------------------------- 1. balanço publicado antes de T
def test_1_todo_exercicio_usado_foi_recebido_antes_do_corte(amostra) -> None:
    for l in amostra:
        for e in l.anuais:
            assert e.dt_receb <= l.data_corte, \
                f"cd {l.cd_cvm}@{l.data_corte}: {e.dt_refer} recebido em {e.dt_receb}"
        if l.ultimo_itr:
            assert l.ultimo_itr.dt_receb <= l.data_corte, \
                f"cd {l.cd_cvm}@{l.data_corte}: ITR recebido em {l.ultimo_itr.dt_receb}"


def test_1b_o_itr_do_proprio_trimestre_nao_entra() -> None:
    """Medido: o ITR de 30/06/2014 do BB chegou em 14/08/2014. Em T=30/06 vale o 1T."""
    l = pit.ledger_em(BCO_BRASIL, "2014-06-30", pit.FINANCEIRO)
    assert l is not None and l.ultimo_itr is not None
    assert l.ultimo_itr.dt_refer == "2014-03-31", \
        f"esperava o ITR do 1T, veio {l.ultimo_itr.dt_refer}"


# ------------------------------------------------------------- 2. nenhum preço posterior a T
def test_2_o_ledger_nao_carrega_preco() -> None:
    """O preço entra na avaliação, não no ledger; o de T+h só via retorno.ate (fatia 10).

    Teste estrutural de propósito: se um dia alguém puser preço aqui, isto quebra e obriga a
    pensar de onde ele veio.
    """
    l = pit.ledger_em(NEOENERGIA, "2020-06-30")
    assert l is not None
    campos = set(l.procedencia())
    for e in l.anuais:
        campos |= set(e.contas)
    proibidos = {c for c in campos if "preco" in c or "cotac" in c or "fechamento" in c}
    assert not proibidos, f"o ledger carrega preço: {proibidos}"


# --------------------------------------------------------------- 3. IPCA do mês anterior a T
def test_3_ipca_usado_e_sempre_anterior_ao_mes_do_corte(amostra) -> None:
    """O IPCA do mês m sai ~dia 10 de m+1; os cortes são fim de mês, logo vale o mês anterior."""
    for l in amostra:
        assert l.mes_ipca < l.data_corte[:7], \
            f"cd {l.cd_cvm}@{l.data_corte}: usaria IPCA de {l.mes_ipca}"
        assert l.mes_ipca == mes_ipca_disponivel(l.data_corte)


def test_3b_o_indice_pit_recusa_mes_futuro() -> None:
    from backtest import inflacao_pit

    with pytest.raises(ValueError, match="não era público"):
        inflacao_pit.indice_mes("2020-12", mes_ipca_disponivel("2020-06-30"))


# --------------------------------------------- 4. contagem de ações pública em T (risco #5)
def test_4_acoes_sao_publicas_em_T(amostra) -> None:
    for l in amostra:
        if l.acoes is None:
            continue
        assert l.acoes_dt_receb <= l.data_corte, \
            f"cd {l.cd_cvm}@{l.data_corte}: ações recebidas em {l.acoes_dt_receb}"
        assert l.acoes > 0, f"cd {l.cd_cvm}: contagem de ações não positiva ({l.acoes})"


def test_4b_acoes_de_2014_nao_sao_as_de_hoje() -> None:
    """Se a contagem fosse a de 2026, empresa que emitiu ações daria o mesmo número nas duas datas.

    Usar `n_acoes` de hoje contra preço de 2015 erra o valor de mercado por todo o fator de
    emissão/split acumulado — é o risco #5 da lista de look-ahead.
    """
    mudou = 0
    vis = ic.documentos_visiveis("dfp", "2014-06-30")
    for cd in sorted(set(vis["cd_cvm"].dropna().astype(int)))[:120]:
        velho, novo = pit.ledger_em(cd, "2014-06-30"), pit.ledger_em(cd, "2025-06-30")
        if velho and novo and velho.acoes and novo.acoes and velho.acoes != novo.acoes:
            mudou += 1
    assert mudou >= 5, \
        f"só {mudou} companhias mudaram de contagem entre 2014 e 2025 — a série pode estar congelada em uma data"


# ----------------------------------------- 5. O SENTINELA: truncar as fontes e exigir igualdade
def _limpar_caches() -> None:
    for f in (pit._fatos, pit._acoes, pit._por_companhia, pit._visiveis):
        f.cache_clear()


def _rodar_truncado(cds: list[int], data_corte: str) -> dict[int, "pit.LedgerPIT | None"]:
    """Remonta os ledgers com as fontes de VALOR truncadas em T.

    Perturba o que a versão antiga não perturbava:
      · `_fatos()` sem NENHUMA linha de documento que não estivesse entregue em T — o conjunto de
        (cd_cvm, dt_refer) vem de `documentos_visiveis`. É esta a chave: truncar por `ano_zip` era
        grosseiro demais, porque o documento do exercício FY2016 mora em `dfp_2016.zip` e
        sobrevivia a `ano_zip <= 2016` mesmo tendo sido entregue só em março de 2017 — e era por
        exatamente aí que o vazamento injetado passava;
      · `_acoes()` sem linha de `dt_receb` ou `aprovacao` posterior a T.
    E limpa os QUATRO caches lru: deixar qualquer um quente fazia o truncamento não chegar.

    A versão original truncava `indexar` por `dt_receb <= T`, que é o MESMO filtro de
    `documentos_visiveis` — idempotente, logo comparava X com X.
    """
    fatos_orig, acoes_orig = pit._fatos, pit._acoes
    try:
        fatos_cheio, acoes_cheio = fatos_orig(), acoes_orig()
        permitidos = set()
        for categ in ("dfp", "itr"):
            v = ic.documentos_visiveis(categ, data_corte)
            permitidos |= {(categ, int(c), str(d)) for c, d in zip(v["cd_cvm"], v["dt_refer"])}
        chave = list(zip(fatos_cheio["categ"], fatos_cheio["cd_cvm"].astype(int),
                         fatos_cheio["dt_refer"].astype(str)))
        visivel = pd.Series([k in permitidos for k in chave], index=fatos_cheio.index)
        fatos_pit = fatos_cheio[visivel]
        pit._fatos = lambda: fatos_pit                                           # type: ignore[assignment]
        pit._acoes = lambda: acoes_cheio[                                        # type: ignore[assignment]
            (acoes_cheio["dt_receb"] <= data_corte)
            & (acoes_cheio["aprovacao"].fillna("") <= data_corte)]
        pit._por_companhia.cache_clear()
        pit._visiveis.cache_clear()
        return {cd: pit.ledger_em(cd, data_corte) for cd in cds}
    finally:
        pit._fatos, pit._acoes = fatos_orig, acoes_orig                          # type: ignore[assignment]
        _limpar_caches()


def test_5_sentinela_truncar_as_fontes_em_T_nao_muda_a_selecao() -> None:
    """Remover o futuro das fontes de VALOR não pode mudar o ledger de T.

    Não prova que os valores são os originais pré-reapresentação (impossível: a CVM serve uma só
    versão). Prova que o ledger não alcança linha de referência posterior a T — que é por onde um
    vazamento de valor entraria. `test_5b` prova que este teste não é vácuo.
    """
    for data_corte in ("2016-06-30", "2019-12-31", "2022-06-30"):
        vis = ic.documentos_visiveis("dfp", data_corte)
        cds = sorted(set(vis["cd_cvm"].dropna().astype(int)))[:40]
        normais = {cd: pit.ledger_em(cd, data_corte) for cd in cds}
        truncados = _rodar_truncado(cds, data_corte)

        for cd in cds:
            a, b = normais[cd], truncados[cd]
            if a is None and b is None:
                continue
            assert a is not None and b is not None, f"cd {cd}@{data_corte}: um sumiu com o truncamento"
            assert a.procedencia() == b.procedencia(), (
                f"cd {cd}@{data_corte}: truncar o futuro MUDOU a seleção.\n"
                f"  normal:    {a.procedencia()}\n  truncado:  {b.procedencia()}")
            assert [e.contas for e in a.anuais] == [e.contas for e in b.anuais], \
                f"cd {cd}@{data_corte}: as CONTAS mudaram com o truncamento"


def test_5b_o_sentinela_pega_um_vazamento_injetado() -> None:
    """Meta-teste: injeta look-ahead de VALOR e exige que o sentinela falhe.

    Sem isto o sentinela já foi tautologia uma vez — truncava pelo mesmo predicado que
    `documentos_visiveis` aplica e aprovou um vazamento real injetado pelo adversário. Este teste é
    o que impede a regressão: se alguém enfraquecer `_rodar_truncado`, aqui quebra.

    O vazamento imita o do adversário: os valores passam a vir das linhas PENULTIMO do documento do
    ano SEGUINTE — reapresentação publicada depois de T —, com a procedência intacta.
    """
    data_corte = "2016-06-30"
    vis = ic.documentos_visiveis("dfp", data_corte)
    cds = sorted(set(vis["cd_cvm"].dropna().astype(int)))[:40]
    original = pit._contas_de
    mudou = 0

    def contas_vazando(g, dt_refer, plano, so_acumulado=False):
        nonlocal mudou
        contas, conjunto, ini, meses, amb = original(g, dt_refer, plano, so_acumulado)
        ano = int(dt_refer[:4])
        futuro = g[g["dt_refer"].str.startswith(str(ano + 1), na=False)
                   & (g["ordem_exerc"] == "PENULTIMO") & g["campo"].notna()]
        for campo, grupo in futuro.groupby("campo"):
            novo = float(grupo["valor"].iloc[0])
            if str(campo) in contas and contas[str(campo)] != novo:
                contas[str(campo)] = novo
                mudou += 1
        return contas, conjunto, ini, meses, amb

    try:
        pit._contas_de = contas_vazando                   # type: ignore[assignment]
        _limpar_caches()
        normais = {cd: pit.ledger_em(cd, data_corte) for cd in cds}
        truncados = _rodar_truncado(cds, data_corte)
    finally:
        pit._contas_de = original                         # type: ignore[assignment]
        _limpar_caches()

    assert mudou > 0, "a injeção não alterou valor nenhum — o próprio meta-teste ficou vácuo"
    diferiu = any(
        normais[cd] is not None and truncados[cd] is not None
        and [e.contas for e in normais[cd].anuais] != [e.contas for e in truncados[cd].anuais]
        for cd in cds)
    assert diferiu, (
        f"o sentinela NÃO pegou um vazamento de valor injetado em {mudou} contas. "
        "Voltou a ser tautologia: conferir se _rodar_truncado perturba _fatos()/_acoes() e limpa "
        "os quatro caches lru.")


def test_parquet_tem_uma_versao_por_exercicio() -> None:
    """Não há escolha de versão a errar: o parquet serve uma só por (cd_cvm, dt_refer, conjunto).

    Complemento honesto do sentinela. O valor original pré-reapresentação é irrecuperável, mas o
    ledger não escolhe entre versões — recebe a única que existe, e o estado `contaminado` diz
    quando essa única é posterior ao que se via em T.
    """
    f = pit._fatos()
    dfp = f[f["categ"] == "dfp"]
    g = dfp.groupby(["cd_cvm", "dt_refer", "conjunto", "campo"], dropna=True)["versao"].nunique()
    assert int((g > 1).sum()) == 0, f"{int((g > 1).sum())} grupos com mais de uma versão no parquet"


# ------------------------------------------------------------------------ auditoria e janelas
# --------------------------------------------- testes de VALOR (os que faltavam por completo)
def test_pl_de_banco_nao_e_passivo() -> None:
    """O plano de contas de banco é outro: `2.03` lá é "Passivos Financeiros ao Custo Amortizado".

    Lendo por código, o PL do BB saía R$ 1,106 TRILHÃO (86% do ativo) e o lucro vinha ausente —
    as duas âncoras financeiras erradas por ordens de grandeza em toda a janela de calibração.
    Valores conferidos no BPP do FY2014: 2.08 "Patrimônio Líquido Consolidado" = 85.440.036.
    """
    l = pit.ledger_em(BCO_BRASIL, "2015-06-30", pit.FINANCEIRO)
    assert l is not None
    e = [x for x in l.anuais if x.dt_refer == "2014-12-31"][0]
    assert e.contas["pl"] == pytest.approx(85_440_036, rel=1e-9)
    assert e.contas["lucro"] == pytest.approx(13_343_496, rel=1e-9)
    assert e.contas["lucro_controlador"] == pytest.approx(11_853_096, rel=1e-9)
    assert 0.03 <= e.contas["pl"] / e.contas["ativo"] <= 0.25, \
        "PL/ativo de banco fora da faixa plausível — provável leitura do plano errado"


def test_pl_lido_por_descricao_bate_com_o_codigo_de_cada_plano() -> None:
    """Varre a leitura por descrição contra o código correto de CADA plano.

    A primeira versão deste teste exigia PL/ativo <= 0,6 em qualquer companhia lida sob o plano
    financeiro, e falhou com razão: uma industrial legitimamente tem PL/ativo de 0,78, e o plano
    financeiro não se aplica a ela. A pergunta certa não é o nível do indicador, é se a leitura
    por DESCRIÇÃO devolve o mesmo número que o código correto do plano daquela companhia —
    `2.03` onde o plano é industrial, `2.08` onde é de instituição financeira.
    """
    f = pit._fatos()
    bpp = f[(f["categ"] == "dfp") & (f["bloco"] == "BPP") & (f["ordem_exerc"] == "ULTIMO")
            & (f["conjunto"] == "con") & (f["campo_desc"] == "pl_desc")]
    por_codigo = bpp.groupby("codigo").size().sort_values(ascending=False)
    assert "2.03" in por_codigo.index and "2.08" in por_codigo.index, (
        f"esperava PL em 2.03 (industrial) e 2.08 (financeiro); veio {dict(por_codigo.head())}")

    divergentes, n = [], 0
    for (cd, dt), g in bpp.groupby(["cd_cvm", "dt_refer"]):
        if len(g) != 1:
            continue
        n += 1
        esperado = float(g["valor"].iloc[0])
        l = pit.ledger_em(int(cd), "2026-06-30", pit.FINANCEIRO)
        if l is None:
            continue
        e = [x for x in l.anuais if x.dt_refer == dt]
        if e and e[0].contas.get("pl") is not None \
                and abs(e[0].contas["pl"] - esperado) > max(1.0, abs(esperado) * 1e-9):
            divergentes.append((int(cd), dt, e[0].contas["pl"], esperado))
        if n >= 400:
            break
    assert not divergentes, f"PL lido por descrição divergiu do valor da própria linha: {divergentes[:5]}"


def test_arrendamento_nao_entra_duas_vezes_na_divida() -> None:
    """`2.01.04.03` é SUBCONTA de `2.01.04`; somar os dois dobrava a dívida no pior caso.

    Medido pelo adversário: mediana de 7,8% de inflação da dívida bruta, p90 61%, máximo 100%.
    `coletar_cvm.extras_bp:150-165` evita isso de propósito e a cópia tinha perdido a regra.
    Para a dívida só entra arrendamento lançado FORA de 2.01.04/2.02.01.
    """
    from backtest.motor.contas import divida_liquida

    l = pit.ledger_em(2437, "2025-06-30")
    assert l is not None
    e = [x for x in l.anuais if x.dt_refer == "2023-12-31"][0]
    assert divida_liquida(e.contas)[0] == pytest.approx(60_997_037, rel=1e-9)

    vis = ic.documentos_visiveis("dfp", "2024-06-30")
    negativos, invertidos, n = 0, 0, 0
    for cd in sorted(set(vis["cd_cvm"].dropna().astype(int)))[:200]:
        L = pit.ledger_em(cd, "2024-06-30")
        if L is None:
            continue
        for x in L.anuais:
            a, s = x.contas.get("arrendamento", 0.0), x.contas.get("arrendamento_saldo", 0.0)
            if a or s:
                n += 1
                negativos += a < 0 or s < 0
                invertidos += abs(a) > abs(s) + 1
    assert n > 100, f"amostra pequena: {n} exercícios com arrendamento"
    assert negativos == 0, f"{negativos} arrendamentos negativos — a regex pegou DRE/DFC, não BPP"
    assert invertidos <= 2, f"{invertidos} casos com a parte maior que o saldo (impossível)"


def test_itr_declara_o_periodo_do_fluxo() -> None:
    """No ITR cada conta de fluxo tem duas linhas ULTIMO: acumulada no ano e trimestre isolado.

    Medido: em 11.469 de 11.614 ITRs de 2T/3T a ÚLTIMA linha do CSV é o trimestre, então deixar a
    ordem decidir entregava o trimestre com o nome do fluxo anual — erro silencioso de ~4x para
    quem montasse LTM. Agora fica a acumulada, e o período vai declarado no Exercicio.
    """
    l = pit.ledger_em(BCO_BRASIL, "2015-06-30", pit.FINANCEIRO)
    assert l is not None and l.ultimo_itr is not None
    itr = l.ultimo_itr
    assert itr.dt_refer == "2015-03-31"
    assert itr.dt_ini_exerc.startswith("2015-01"), \
        f"o fluxo do ITR tem de ser o acumulado do ano, começou em {itr.dt_ini_exerc}"
    assert itr.periodo_meses == 3, f"1T = 3 meses, veio {itr.periodo_meses}"
    assert all(e.periodo_meses == 12 for e in l.anuais), "exercício anual tem de ter 12 meses"


def test_auditoria_nao_acha_vazamento_na_amostra(amostra) -> None:
    vazamentos = [(l.cd_cvm, l.data_corte, p) for l in amostra
                  for p in pit.auditoria(l) if p.startswith(("VAZAMENTO", "CORRUPÇÃO"))]
    assert not vazamentos, f"auditoria achou vazamento: {vazamentos[:5]}"


def test_janela_respeita_o_teto_de_dez_e_cresce_com_a_data() -> None:
    """A contagem de exercícios por corte tem de bater com a aritmética do config.

    A asserção é sobre a MEDIANA, não o máximo. Medido: em 2014-06-30 a mediana é 4, como o config
    prevê, mas há companhia com 5 — é quem mudou de exercício social e tem dois DT_REFER no mesmo
    ano-calendário. Isso é correto e é justamente por isso que a chave é (cd_cvm, dt_refer) e não
    ano; afirmar sobre o máximo tornaria o teste frágil a um caso legítimo.
    """
    import statistics

    from backtest.config import EXERCICIOS_POR_CORTE

    for d in ("2014-06-30", "2016-06-30", "2020-06-30", "2025-06-30"):
        vis = ic.documentos_visiveis("dfp", d)
        cds = sorted(set(vis["cd_cvm"].dropna().astype(int)))[:80]
        ns = [l.n_exercicios for cd in cds if (l := pit.ledger_em(cd, d)) is not None]
        assert ns, f"nenhum ledger em {d}"
        assert max(ns) <= PADRAO.janela_max, f"{d}: janela acima do teto de 10 ({max(ns)})"
        assert statistics.median(ns) == EXERCICIOS_POR_CORTE[d], (
            f"{d}: mediana de {statistics.median(ns)} exercícios, o config prevê "
            f"{EXERCICIOS_POR_CORTE[d]} — a aritmética da disponibilidade mudou")
