"""Motor de valuation para empresas não financeiras (industrial, serviços, cíclica/commodity) — doutrina v2.0 §11.

Fonte dos números: dados/cvm_series.json (DFP/ITR da CVM, R$ mil) + preço/ações/proventos da StatusInvest.
Tudo em R$ por ação no fim. Convenção: taxas em fração.
"""
from __future__ import annotations

from ltm import ltm_de, ltm_ref_de
import json
import series_vigente
import math
import pathlib
from dataclasses import dataclass, field, replace
from functools import lru_cache
from statistics import median

from credito import FONTE as FONTE_SPREAD, spread_sintetico
from defasagem import defasagem_meses
from inflacao import DEFLATOR, deflator_ltm, deflator_periodo, fator_entre, fator_idade, inflacao_do_ano, reposicao
from juros import juros_do_periodo
from proventos_ex import ajuste_b3
import proventos_hall
from motor_financeiras import (ANOS_ROIC_MINIMO, HORIZONTE, IR_JCP, NOTA_QUALIDADE_MINIMA, ORDEM, PREMIO_KE, TRAVA_PP, Mercado,
                               aplicar_trava, descontar, falta_razao_desconto,
                               interp, liquido_diferido, media_qualitativa, nota_preco, nota_spread, nota_yield, palavra,
                               precos_de_referencia)

AQUI = pathlib.Path(__file__).parent
CVM = series_vigente.carregar_cvm()     # AUD-103: com o LTM da temporada por cima, quando houver
SI = series_vigente.carregar()
# fase 3, fatia 2: DPA/JCP das não financeiras do hall da B3 (A), no carregamento — nenhum lote corrige o SI depois
proventos_hall.aplicar(SI)
ANOS = [str(a) for a in range(2016, 2026)]
LIMITE_QUEBRA = 0.25      # §11.4: divergência entre a mediana de 5 anos e a da janela que levanta suspeita de quebra
JANELA_MINIMA_SAIDA = 10  # §9: a exceção de qualidade exige histórico de ciclo inteiro; janela curta não a permite
ALIQUOTA_MARGINAL = 0.34  # IRPJ 25% + CSLL 9%: a alíquota da perpetuidade quando o benefício tem prazo (§2, v2.3)
LIMIAR_ORIGEM = 0.15      # v2.3: mediana abaixo disto só vale com a origem declarada (até a v2.2 era o piso da alíquota)
ANO_BASE = 2026           # ano da data-base dos preços: a fase do benefício fiscal conta os exercícios cheios depois dele
JANELA_MINIMA_PRECO_MEIO = 7   # v2.3 (§11.1): margem reexpressa ao preço de meio só com janela de 7+ exercícios
MINIMO_ANOS_ALIQUOTA = 3  # v2.3: a mediana de 5 anos da alíquota exige pelo menos 3 exercícios válidos; senão vale 34%
FIM_EXERCICIO = {"SMTO3": 3}  # mês de fechamento do exercício fora do ano-calendário (o resto: dezembro)
ANO_IFRS16 = 2019         # AUD-03: primeiro exercício com o aluguel fora do EBITDA (margem de E&P só a partir dele)
TOL_PONTO_FIXO = 1e-5     # AUD-13: |ΔE/E| que encerra a iteração dos pesos do WACC
MAX_ITER_PONTO_FIXO = 200


@dataclass
class Industrial:
    ticker: str
    nome: str
    perfil: str                    # ciclica | servicos
    preco: float
    n_acoes: float                 # ações (ou units) em circulação
    anos_ciclo: list = field(default_factory=lambda: ANOS)   # janela da margem normalizada (§11.4)
    janela_razao: str = ""         # OBRIGATÓRIO quando anos_ciclo != ANOS: a quebra estrutural e a data (§11.4)
    receita_meio: float | None = None   # R$ mil; None = média dos 3 últimos exercícios + LTM
    aliquota: float | None = None   # alíquota PERPÉTUA explícita; None = regra da v2.3 em `aliquota_regra` (mediana de 5 anos, sem piso)
    # Kd (doutrina §2, v2.4 — AUD-07): custo médio da dívida do RI quando houver; senão rf nominal + spread sintético pela cobertura
    # normalizada (credito.py). `spread_kd` digitado só vale com `spread_fonte`.
    kd_ri: dict | None = None      # {"valor": Kd nominal em R$ a.a. depois dos swaps, "fonte": "...", "data": "aaaa-mm-dd"}
    spread_kd: float | None = None
    spread_fonte: str = ""
    g_real: float = 0.01           # crescimento real perpétuo do cenário base
    jcp_share: float = 0.0
    pl_hist: float | None = None
    qualitativo: dict = field(default_factory=dict)
    desconto_controlador: dict = field(default_factory=lambda: {"tipo": "zero", "razao": ""})
    reproducao_por_acao: float | None = None   # se houver laudo/NAV melhor que o contábil (declarar fonte)
    reproducao_fonte: str = "PL contábil consolidado (custo histórico; ativos biológicos a valor justo)"
    usar_reproducao_como_ancora: bool = True
    anos_pagos_10: int | None = None
    fora_circulo: bool = False
    # Lote 5 (05/10): defaults preservam os lotes anteriores
    outras_liquidas: bool = False        # não recorrente = 3.04.04 + 3.04.05 (empresa que lança ganhos líquidos em 3.04.05)
    anos_outras: list | None = None      # janela da mediana de "outras" (doutrina: 10 anos); None = anos_ciclo
    capex_ciclico: bool | None = None    # regra de capex de commodity; None = perfil == "ciclica"
    deflator: dict | None = None         # ano → fator IPCA até a data-base: margem = EBIT real ÷ receita real média
    outros_passivos: float = 0.0         # R$ mil; passivo OPERACIONAL à frente do acionista fora de 2.01.04/2.02.01 — só na ponte (v2.3)
    outros_passivos_fonte: str = ""      # OBRIGATÓRIO quando outros_passivos ou outros_passivos_financeiros ≠ 0
    declinio_sem_liberacao: bool = False  # g < 0 declarado: o declínio não devolve capital (campo maduro)
    da_receita: float | None = None      # E&P: D&A atual ÷ receita de meio de ciclo → margem = EBITDA mediano − este valor
    # Lote 6 (05/10): defaults preservam os lotes anteriores
    impairment_normalizado: bool = False  # fora do E&P: impairment sai da margem ano a ano e entra a perda mediana de 10 anos (só penaliza)
    receita_meio_fonte: str = ""          # como a receita de meio de ciclo foi obtida (preço de commodity declarado)
    # Lote 4 (05/10): defaults preservam os lotes anteriores
    g1_real: float | None = None          # DCF em 2 estágios: crescimento real dos primeiros anos_g1 anos (compounder; só com ROIC > WACC)
    anos_g1: int = 10
    defasagem_meses: float | None = None  # provento pago N meses depois da data-com → valor presente ao Ke nominal (§6.3); None = medida na StatusInvest (defasagem.py)
    defasagem_fonte: str = ""      # OBRIGATÓRIO quando defasagem_meses é informado: o evento declarado e a data (§6.3)
    # Etapa 5 (07/10, dossiê CMIN3): defaults preservam os lotes anteriores
    fator_preco: dict | None = None       # cíclica de janela curta: ano → preço de meio ÷ preço do ano (R$ de hoje); a margem do ano é reexpressa ao preço de meio
    custo_variavel_preco: float = 0.0     # fração da receita cujo custo acompanha o preço (royalty, minério de terceiros); o resto do custo fica fixo
    # v2.3 (07/10): defaults preservam os lotes anteriores
    controlador_discricionario: bool = False   # peso 2 do controlador na média qualitativa (regra 11, §10)
    controlador_discricionario_fonte: str = ""  # OBRIGATÓRIO quando True: o poder exercido e a fonte
    qualitativo_origem: str = "arbitrada, pré-v4"   # notas do hall até o dossiê do ticker; dossiê grava "regra 11"
    aliquota_fase: dict | None = None     # crédito de IR COM PRAZO (ágio, subvenção): {"ate": 2030, "fonte": "...", "efetiva": opcional}
    aliquota_permanente_fonte: str = ""   # mediana < 15% só vale com a origem PERMANENTE declarada (JCP, regime sem prazo)
    aliquota_fonte: str = ""              # OBRIGATÓRIO com `aliquota` explícita abaixo de 34% (AUD-09)
    aliquota_desde: dict | None = None    # mudança de lei: {"ano": 2024, "fonte": "..."} — a mediana só usa exercícios >= ano (AUD-09)
    trava_razao: str = ""                 # §9 (v2.4): premissa que explica Bogle × Ke fora de ±2 p.p. numa JUSTA; sem ela, NÃO CONCLUSIVO
    outros_passivos_financeiros: float = 0.0   # R$ mil; passivo COM JUROS ou financeiro fora de 2.01.04/2.02.01: entra na DL (v2.3)
    capex_expansao: dict | None = None    # expansão identificada sem receita: {"anos": {ano: R$ mil}, "projeto", "fonte", "nota_fonte", "retorno_projetado"}


def exigir_declaracoes(emp: Industrial) -> None:
    """Premissa da casa sem fonte escrita não roda (doutrina §11.4 e §6.3). Falha alto, não silenciosa."""
    faltas = []
    if (falta := falta_razao_desconto(emp)):      # AUD-41 (B24)
        faltas.append(falta)
    if list(emp.anos_ciclo) != list(ANOS) and not emp.janela_razao.strip():
        faltas.append(f"janela {emp.anos_ciclo[0]}-{emp.anos_ciclo[-1]} sem janela_razao (§11.4)")
    if emp.da_receita is not None and min(int(x) for x in emp.anos_ciclo) < ANO_IFRS16:
        # AUD-03 (08/10/2026): margem de E&P = EBITDA do ano − D&A ATUAL (com o direito de uso); EBITDA pré-IFRS 16 já desconta o
        # aluguel → contado duas vezes (PETR4 2016–18). Janela só a partir de 2019 (§11.1, linha do DCF)
        faltas.append(f"E&P com janela desde {min(emp.anos_ciclo)}: EBITDA pré-IFRS 16 contra D&A atual com direito de uso (§11.1)")
    if emp.defasagem_meses is not None and not emp.defasagem_fonte.strip():
        faltas.append(f"defasagem_meses={emp.defasagem_meses} sem defasagem_fonte (§6.3)")
    if emp.controlador_discricionario and not emp.controlador_discricionario_fonte.strip():
        faltas.append("controlador_discricionario sem controlador_discricionario_fonte (§10)")
    f = emp.aliquota_fase
    if f is not None:
        if emp.aliquota is not None or emp.aliquota_permanente_fonte.strip():
            faltas.append("aliquota_fase não combina com aliquota explícita nem com aliquota_permanente_fonte (§2)")
        if not isinstance(f.get("ate"), int) or not str(f.get("fonte", "")).strip():
            faltas.append(f"aliquota_fase exige 'ate' (ano, inteiro) e 'fonte': {f}")
        ef = f.get("efetiva")
        if ef is not None and not (isinstance(ef, (int, float)) and 0 <= ef <= ALIQUOTA_MARGINAL):
            faltas.append(f"aliquota_fase 'efetiva' fora de [0, {ALIQUOTA_MARGINAL}]: {ef}")
    if emp.aliquota is not None and emp.aliquota < ALIQUOTA_MARGINAL and not emp.aliquota_fonte.strip():
        # AUD-09: a explícita contornava o mínimo de 3 exercícios e a regra de origem; abaixo de 34% exige a fonte escrita
        faltas.append(f"aliquota explícita {emp.aliquota:.4f} < 34% sem aliquota_fonte (§2)")
    ad = emp.aliquota_desde
    if ad is not None and (not isinstance(ad.get("ano"), int) or not str(ad.get("fonte", "")).strip()):
        faltas.append(f"aliquota_desde exige 'ano' (inteiro) e 'fonte': {ad}")
    if emp.spread_kd is not None and not emp.spread_fonte.strip():
        faltas.append(f"spread_kd={emp.spread_kd} digitado sem spread_fonte (§2; o padrão é o spread sintético)")
    kr = emp.kd_ri
    if kr is not None and not (isinstance(kr.get("valor"), (int, float)) and 0 < kr["valor"] < 0.5
                               and str(kr.get("fonte", "")).strip() and str(kr.get("data", "")).strip()):
        faltas.append(f"kd_ri exige 'valor' (fração, nominal em R$), 'fonte' e 'data': {kr}")
    if (emp.outros_passivos or emp.outros_passivos_financeiros) and not emp.outros_passivos_fonte.strip():
        faltas.append("outros_passivos sem outros_passivos_fonte (§11.1)")
    ce = emp.capex_expansao
    if ce is not None:
        if not (str(ce.get("projeto", "")).strip() and str(ce.get("fonte", "")).strip() and ce.get("nota_fonte") in ("A", "B")):
            faltas.append("capex_expansao exige 'projeto', 'fonte' e 'nota_fonte' A ou B (§11.1)")
        anos_ce = ce.get("anos")
        if not isinstance(anos_ce, dict) or not anos_ce:
            faltas.append("capex_expansao sem 'anos' {ano: R$ mil}")
        else:
            a = CVM.get(emp.ticker, {}).get("anual", {})
            for ano, x in anos_ce.items():
                capex = a.get(ano, {}).get("capex")
                if capex is None or not isinstance(x, (int, float)) or not 0 <= x <= capex:
                    faltas.append(f"capex_expansao {ano}={x} fora de [0, capex do ano={capex}]")
    if faltas:
        raise ValueError(f"{emp.ticker}: " + " · ".join(faltas))


def v(d, k, default=None):
    x = d.get(k)
    return default if x is None else x


def serie(tk):
    return CVM[tk]["anual"], ltm_de(CVM[tk])


def anos_validos(tk, anos):
    a, _ = serie(tk)
    return [x for x in anos if a.get(x, {}).get("receita")]


def divida_liquida(b):
    bruta = v(b, "emprest_cp", 0) + v(b, "emprest_lp", 0) + v(b, "arrendamento", 0)   # IFRS 16 é dívida
    caixa = v(b, "caixa", 0) + v(b, "aplic_cp", 0)
    return bruta, caixa, bruta - caixa


def deflator_exercicio(tk, ano) -> float:
    """R$ do exercício `ano` → R$ de hoje. Exercício fora do ano-calendário (SMTO3, abr–mar) usa os 12 meses dele (adversário,
    08/10/2026: o DEFLATOR do ano de fechamento ficava ~3% baixo)."""
    mes = FIM_EXERCICIO.get(tk, 12)
    return DEFLATOR[str(ano)] if mes == 12 else deflator_periodo(int(ano), mes)


def proventos_ja_ex(emp: Industrial, data_preco: str | None = None) -> dict:
    """Provento já ex que ainda está no caixa do balanço do LTM, em R$ mil (AUD-02, 08/10/2026; regra em proventos_ex.py).

    total = passivo de proventos do balanço − a parte dele ainda não ex na data do preço + aprovados depois do balanço e
    já ex. Entra na dívida líquida e sai do OE, como `outros_passivos_financeiros` (§11.1, v2.3).
    Entre o fim do exercício e a AGO a linha genérica do passivo pode ser o dividendo mínimo PROVISIONADO, que a AGO aprova
    depois do balanço — e aí ele aparece também na parte da B3 (SMTO3 2T26: R$ 69,9 mi nos dois; adversário, 08/10):
      · balanço NO fim do exercício (DFP) com passivo → falha alto: o provisionado pode nem ser ex no preço; decidir à mão;
      · 1º trimestre depois do fim do exercício → conta UMA vez: o maior entre o passivo e os aprovados depois."""
    _, ltm = serie(emp.ticker)
    ref = ltm_ref_de(CVM[emp.ticker])
    balanco = max(v(ltm, "proventos_a_pagar", 0), 0.0)
    mes_bal, fim = 3 * int(ref[0]), FIM_EXERCICIO.get(emp.ticker, 12)
    if balanco and mes_bal == fim:
        raise NotImplementedError(f"{emp.ticker}: LTM {ref} (fim do exercício) com proventos a pagar de R$ {balanco:,.0f} mil — o "
                                  "passivo pode trazer o mínimo obrigatório ainda não aprovado; separar o que é ex antes de rodar (AUD-02)")
    b3 = ajuste_b3(emp.ticker, emp.n_acoes, ref, data_preco=data_preco)
    nao_ex = min(b3["nao_ex"], balanco)
    pos_exercicio = mes_bal == fim % 12 + 3
    total = max(balanco - nao_ex, b3["depois"]) if pos_exercicio else balanco - nao_ex + b3["depois"]
    # o que não é passivo no balanço ainda está DENTRO do PL de 30/06 (o EGIE3 faz o mesmo: lote6, pl − EGIE_DIV_AGO26)
    return dict(balanco=balanco, nao_ex=nao_ex, aprovados_depois=b3["depois"], total=total, pos_exercicio=pos_exercicio,
                no_pl=total - (balanco - nao_ex), ref=ref, eventos=b3["eventos"])


def capital_giro(b):
    return (v(b, "ac", 0) - v(b, "caixa", 0) - v(b, "aplic_cp", 0)) - (v(b, "pc", 0) - v(b, "emprest_cp", 0))


def expansao_do_ano(emp: Industrial, ano) -> float:
    """Capex de expansão IDENTIFICADO no exercício (R$ mil; v2.3) — zero sem declaração."""
    return float(emp.capex_expansao["anos"].get(ano, 0.0)) if emp.capex_expansao else 0.0


def capex_manutencao(tk, ano, anterior, ciclica=False, expansao=0.0):
    """Capex de manutenção = capex − (capital ÷ receita) × Δreceita REAL média de 5 anos; piso zero (doutrina §11.1).

    Adaptação declarada do método de Greenwald: o capital é imobilizado + intangível + biológico LÍQUIDOS do
    exercício (as mesmas contas que formam o capex), não o PPE bruto médio de 5 anos do original — a série da CVM
    só traz o líquido (conta 1.02.03).
    `expansao` (v2.3): capex de projeto identificado (nome, valor e prazo em fonte A/B) e ainda sem receita sai ANTES da regra —
    o Greenwald só enxerga crescimento que já virou receita, e sem isso a obra em andamento contaria como manutenção.
    Δreceita REAL (Etapa 2/F2): a receita antiga entra a preços do exercício corrente antes da subtração. Sem isso,
    em economia inflacionária a inflação viraria "crescimento" e reduziria o capex de manutenção. Não é exigência
    de Greenwald (que não trata inflação) — é coerência com a própria §11.1, que já manda preço de commodity e EPV
    em R$ de hoje. Tudo fica em R$ do exercício, então `cap_rec` (razão do mesmo ano) e o capex seguem compatíveis.
    """
    a, _ = serie(tk)
    d = a[ano]
    if ciclica:
        # commodity: a receita cresce por preço, não por capacidade — todo o capex é manutenção (sem projeto comprovado)
        return (d["capex"] - expansao, 0.0) if d.get("capex") is not None else (None, None)
    if d.get("capex") is None:
        return None, None
    base = str(int(ano) - 5)
    if not a.get(base, {}).get("receita"):
        p = a.get(anterior, {})
        if not p.get("receita"):
            return None, None
        delta = d["receita"] - p["receita"] * fator_entre(anterior, ano)
    else:
        delta = (d["receita"] - a[base]["receita"] * fator_entre(base, ano)) / 5
    cap_rec = (v(d, "imobilizado", 0) + v(d, "intangivel", 0) + v(d, "biologico", 0)) / d["receita"]
    cresc = cap_rec * max(delta, 0)
    return max(d["capex"] - expansao - cresc, 0.0), cresc


def aluguel_principal(emp: Industrial, ano, anterior, kd_real):
    """Amortização do passivo de arrendamento (IFRS 16) que sai do OE — só o PRINCIPAL (doutrina §11.1: "sem juros").

    O juro já está dentro do lucro líquido; descontar a linha cheia o contaria duas vezes. Duas situações, decididas
    pelo DADO e não por lista:
      · linha de principal (a maioria, e KLBN11, que tem a despesa de juros de arrendamento em linha própria na DFC):
        desconta integralmente — o juro está em outro lugar;
      · linha que a PRÓPRIA empresa declara como "principal e juros pagos" (UGPA3, 6.03.07): o juro é estimado pelo
        saldo médio do passivo de arrendamento × Kd **REAL** e devolvido. O Kd nominal é o de hoje (rf de ~15%) e
        aplicá-lo a saldos de 2019–21, quando a Selic era 2%, devolvia juro demais e INFLAVA o OE — o oposto de
        conservador (achado do adversário em 05/10/2026). O Kd real é um limite inferior do juro, então o principal
        descontado é um limite superior: erra para o lado que penaliza.
    Limite declarado: quando a empresa não reporta o passivo de arrendamento no balanço estruturado (ABEV3: a conta
    2.01.04.03/2.02.01.03 vem zerada), o juro não é estimável e a linha sai inteira — conservador, pode contar o juro
    duas vezes. Série coletada antes de 06/10/2026 não tem os campos → 0 (sem efeito).
    """
    a, _ = serie(emp.ticker)
    d, p = a[ano], a.get(anterior, {})
    limpo = max(v(d, "arrendamento_pago", 0), 0)
    misto = max(v(d, "arrendamento_pago_com_juros", 0), 0)
    if not misto:
        return limpo
    saldos = [v(x, "arrendamento_saldo", 0) for x in (d, p) if v(x, "arrendamento_saldo", 0) > 0]
    juros = (sum(saldos) / len(saldos)) * kd_real if saldos else 0.0
    return limpo + max(misto - juros, 0.0)


@lru_cache(maxsize=None)
def idade_e_fator(tk):
    """(idade média do imobilizado, fator do IPCA dessa idade). Memoizado: `avaliar` chama `valores` ~90 vezes."""
    a, ltm = serie(tk)
    da = v(ltm, "da", 0) or max((v(a[x], "da", 0) for x in a), default=0)
    return reposicao(v(ltm, "imobilizado", 0), da)


def capital_reposicao(tk, cap_inv):
    """Capital investido com o imobilizado a custo de reposição aproximado (doutrina §11.1, Etapa 2/F2).

    Capital contábil + imobilizado × (IPCA da idade média − 1). Só o imobilizado é corrigido: intangível e goodwill
    estão a preço de aquisição e não têm custo de reposição definido; o capital de giro já está a preços de hoje.
    """
    _, ltm = serie(tk)
    idade, fator = idade_e_fator(tk)
    return idade, cap_inv + v(ltm, "imobilizado", 0) * (fator - 1)


def owner_earnings_ano(emp: Industrial, ano, anterior, kd_real, ciclica=False, t_retributar=None):
    """OE do exercício. `t_retributar` (v2.3): quando a alíquota perpétua não é a mediana observada (explícita, fase de crédito
    com prazo, mediana < 15% sem origem), o lucro do ano é refeito a essa alíquota — senão o crédito vencido ou temporário
    ficaria na perpetuidade do OE. Lucro a t = LAIR × (1 − t); o ajuste é −(IR + t × LAIR), com IR negativo = despesa."""
    a, _ = serie(emp.ticker)
    d, p = a[ano], a.get(anterior, {})
    cm, _ = capex_manutencao(emp.ticker, ano, anterior, ciclica, expansao_do_ano(emp, ano))
    if cm is None or d.get("lucro") is None or d.get("da") is None or not p:
        return None
    # AUD-15 (v2.6): o OE é fluxo do ACIONISTA da controladora — lucro do controlador, como EPV e DCF descontam os minoritários;
    # sem a linha (zerada na CVM, AUD-68) fica o consolidado
    lucro = d["lucro_controlador"] if d.get("lucro_controlador") is not None else d["lucro"]
    if t_retributar is not None:
        if d.get("lair") is None or d.get("ir") is None:
            return None             # sem a linha do imposto não dá para retributar: o ano sai (nada silencioso)
        lucro -= d["ir"] + t_retributar * d["lair"]
    dwc = capital_giro(d) - capital_giro(p)
    # IFRS 16: a D&A somada de volta inclui a depreciação do direito de uso, então o aluguel pago é custo do negócio e sai
    return lucro + d["da"] - cm - max(dwc, 0) - aluguel_principal(emp, ano, anterior, kd_real)


# ---------------------------------------------------------------- qualidade contábil
def altman_z2(d):
    at = d["ativo"]
    x1 = (v(d, "ac", 0) - v(d, "pc", 0)) / at
    x2 = v(d, "reservas_lucro", 0) / at
    x3 = v(d, "ebit", 0) / at
    x4 = v(d, "pl", 0) / (v(d, "pc", 0) + v(d, "pnc", 0))
    z = 3.25 + 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
    zona = "segura" if z > 5.85 else ("cinzenta" if z >= 4.15 else "perigo")
    return z, zona


def piotroski(d, p):
    roa, roa0 = d["lucro"] / d["ativo"], p["lucro"] / p["ativo"]
    alav = v(d, "emprest_lp", 0) / d["ativo"]
    alav0 = v(p, "emprest_lp", 0) / p["ativo"]
    liq, liq0 = d["ac"] / d["pc"], p["ac"] / p["pc"]
    mb, mb0 = v(d, "lucro_bruto", 0) / d["receita"], v(p, "lucro_bruto", 0) / p["receita"]
    giro, giro0 = d["receita"] / d["ativo"], p["receita"] / p["ativo"]
    acoes_ok = not (d.get("acoes") and p.get("acoes") and d["acoes"] > p["acoes"] * 1.005)
    crit = [roa > 0, v(d, "fco", 0) > 0, roa > roa0, v(d, "fco", 0) > d["lucro"], alav < alav0, liq > liq0, acoes_ok,
            mb > mb0, giro > giro0]
    return sum(crit), crit


def beneish(d, p):
    try:
        dsri = (v(d, "receber", 0) / d["receita"]) / (v(p, "receber", 0) / p["receita"])
        gm0 = v(p, "lucro_bruto", 0) / p["receita"]
        gm1 = v(d, "lucro_bruto", 0) / d["receita"]
        gmi = gm0 / gm1
        aq = lambda x: 1 - (v(x, "ac", 0) + v(x, "imobilizado", 0)) / x["ativo"]
        aqi = aq(d) / aq(p)
        sgi = d["receita"] / p["receita"]
        dep = lambda x: v(x, "da", 0) / (v(x, "da", 0) + v(x, "imobilizado", 0))
        depi = dep(p) / dep(d)
        sga = lambda x: -(v(x, "desp_vendas", 0) + v(x, "desp_ga", 0)) / x["receita"]
        sgai = sga(d) / sga(p)
        tata = (d["lucro"] - v(d, "fco", 0)) / d["ativo"]
        lev = lambda x: (v(x, "pc", 0) + v(x, "pnc", 0)) / x["ativo"]
        lvgi = lev(d) / lev(p)
        m = (-4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi + 0.115 * depi - 0.172 * sgai
             + 4.679 * tata - 0.327 * lvgi)
        return m
    except (ZeroDivisionError, TypeError):
        return None


def sloan(d, p):
    return (d["lucro"] - v(d, "fco", 0)) / ((d["ativo"] + p["ativo"]) / 2)


# ---------------------------------------------------------------- valuation
def ebit_aj(d, med_outras=None, liquidas=False):
    """EBIT sem o excesso de 'outras receitas operacionais' (3.04.04) acima da mediana de 10 anos da própria empresa, em % da
    receita — lucro não recorrente (armadilha 1 da doutrina §7); só penaliza. O ganho de valor justo de ativo biológico NÃO é
    retirado: a exaustão o devolve no ciclo (retirar só o ganho penalizaria duas vezes); é exibido na ficha."""
    if med_outras is None or not d.get("receita"):
        return d["ebit"]
    excesso = max(outras(d, liquidas) - med_outras * d["receita"], 0)
    return d["ebit"] - excesso


def outras(d, liquidas=False):
    # líquidas: 3.04.04 + 3.04.05 sem o impairment (tratado à parte) — empresa que lança ganhos de venda de ativo em 3.04.05
    # só o impairment lançado DENTRO de 3.04.05 sai de 'outras' (GGBR4 lança em 3.04.03; antes de 05/10 o coletor não separava → fallback)
    imp = v(d, "impairment_outras", v(d, "impairment", 0))
    return v(d, "outras_receitas_op", 0) + ((v(d, "outras_despesas_op", 0) - imp) if liquidas else 0)


def mediana_outras(tk, anos, liquidas=False):
    a, _ = serie(tk)
    xs = [outras(a[x], liquidas) / a[x]["receita"] for x in anos if a.get(x, {}).get("receita")]
    return median(xs) if xs else 0.0


def margem_ao_preco_meio(emp: Industrial, por_ano: dict) -> dict:
    """Margem de cada ano reexpressa ao preço de meio de ciclo (cíclica cuja janela não cobre um ciclo inteiro).

    A doutrina manda margem mediana do ciclo × receita ao preço de meio de 10 anos. Quando a janela de margem é curta e cai
    num período de preço alto (CMIN3: DRE só de 2019–25, com o pico de 2021), a mediana leva o preço alto embutido e,
    aplicada à receita de meio, conta o preço duas vezes. Aqui a receita do ano vai ao preço de meio (× f) e o custo fica:
      margem' = 1 − v − (1 − margem − v) ÷ f,
    v = custo que acompanha o preço (royalty, compra de terceiros), em fração da receita; o restante do custo é fixo no ano.
    f = 1 devolve a margem original. Ano sem fator falha alto (nada silencioso).
    Doutrina v2.3 (§11.1): só cíclica, com dossiê próprio e janela de pelo menos 7 exercícios (abaixo disso a mediana não
    tem ciclo para normalizar). O dossiê é processo (02/08); o perfil e a janela o código confere."""
    if emp.perfil != "ciclica":
        raise ValueError(f"{emp.ticker}: fator_preco só vale para perfil 'ciclica' (§11.1), não '{emp.perfil}'")
    if len(por_ano) < JANELA_MINIMA_PRECO_MEIO:
        raise ValueError(f"{emp.ticker}: fator_preco exige janela >= {JANELA_MINIMA_PRECO_MEIO} exercícios, veio {len(por_ano)}")
    if emp.deflator or emp.da_receita is not None:
        raise ValueError(f"{emp.ticker}: fator_preco não combina com deflator nem com da_receita (E&P)")
    v_ = emp.custo_variavel_preco
    if not 0 <= v_ < 1:
        raise ValueError(f"{emp.ticker}: custo_variavel_preco fora de [0, 1): {v_}")
    falta = [x for x in por_ano if not (isinstance(emp.fator_preco.get(x), (int, float)) and math.isfinite(emp.fator_preco[x])
                                       and emp.fator_preco[x] > 0)]      # NaN e inf passavam por "not f or f <= 0" (adversário, 07/10)
    if falta:
        raise ValueError(f"{emp.ticker}: fator_preco sem valor positivo para {falta}")
    return {x: 1 - v_ - (1 - m - v_) / emp.fator_preco[x] for x, m in por_ano.items()}


def premissas_operacionais(emp: Industrial):
    a, ltm = serie(emp.ticker)
    anos = anos_validos(emp.ticker, emp.anos_ciclo)
    liq = emp.outras_liquidas
    mo = mediana_outras(emp.ticker, emp.anos_outras or anos, liq)
    if emp.deflator:
        # receita indexada a preço de commodity (distribuição): a margem % cai quando o combustível sobe e o EBIT por volume
        # não muda — normaliza-se o EBIT em R$ de hoje (IPCA), expresso sobre a receita real média do período
        rec_real = sum(a[x]["receita"] * emp.deflator[x] for x in anos) / len(anos)
        por_ano = {x: ebit_aj(a[x], mo, liq) * emp.deflator[x] / rec_real for x in anos}
    elif emp.da_receita is not None:
        # E&P: o preço do barril move a margem EBITDA; a D&A (exaustão das reservas, inclusive as compradas) segue o portfólio atual
        # impairment sai do EBITDA ano a ano (baixa de capital, não custo do ano), mas a perda MEDIANA de 10 anos fica como custo
        # recorrente — quem baixa ativo quase todo ano investe mal de forma habitual (só penaliza)
        imp_rec = max(0.0, median(-v(a[x], "impairment", 0) / a[x]["receita"] for x in anos))
        por_ano = {x: (ebit_aj(a[x], mo, liq) + v(a[x], "da", 0) - v(a[x], "impairment", 0)) / a[x]["receita"] - emp.da_receita - imp_rec
                   for x in anos}
    elif emp.impairment_normalizado:
        # baixa de ativo concentrada num ano (GGBR4 2025) não é custo daquele ano; a perda mediana de 10 anos fica como custo recorrente
        imp_rec = max(0.0, median(-v(a[x], "impairment", 0) / a[x]["receita"] for x in anos))
        por_ano = {x: (ebit_aj(a[x], mo, liq) - v(a[x], "impairment", 0)) / a[x]["receita"] - imp_rec for x in anos}
    else:
        por_ano = {x: ebit_aj(a[x], mo, liq) / a[x]["receita"] for x in anos}
    if emp.fator_preco is not None:
        por_ano = margem_ao_preco_meio(emp, por_ano)
    margens = sorted(por_ano.values())
    m50 = median(margens)
    m25 = margens[max(0, round(0.25 * (len(margens) - 1)))]
    m75 = margens[min(len(margens) - 1, round(0.75 * (len(margens) - 1)))]
    ult = [x for x in anos][-3:]
    # AUD-01 (08/10/2026): cada receita vai a R$ de hoje ANTES da média — margem × receita é descontada ao WACC REAL contra
    # dívida e capital de hoje (§11.1, EPV "em R$ de hoje"). Até aqui a média era nominal e o NOPAT saía ~7,5% baixo.
    # SMTO3 (exercício abr–mar): os 12 meses do exercício (deflator_exercicio).
    extra = ([] if abs(ltm["receita"] - a[ult[-1]]["receita"]) < 1        # SMTO3: LTM = último exercício
             else [ltm["receita"] * deflator_ltm(ltm_ref_de(CVM[emp.ticker]))])
    rec = emp.receita_meio or (rec_real if emp.deflator else
                               (sum(a[x]["receita"] * deflator_exercicio(emp.ticker, x) for x in ult) + sum(extra)) / (len(ult) + len(extra)))
    # Greenwald: lucro sustentável = EBIT + D&A − capex de manutenção. Só penaliza (min 0): D&A acima do capex de
    # manutenção pode ser subinvestimento temporário. Mediana dos 5 últimos exercícios, em % da receita.
    if ciclico(emp):
        # commodity: receita cresce por preço; projetos de expansão (Cerrado, Puma II, Gaia) não identificados um a um →
        # capex de manutenção = mediana de 10 anos de capex/receita (dilui os picos de projeto) contra a mediana de D&A/receita
        cx = [(a[x]["capex"] - expansao_do_ano(emp, x)) / a[x]["receita"] for x in anos if a[x].get("capex") is not None]
        dd = ([emp.da_receita] if emp.da_receita is not None else
              [a[x]["da"] / a[x]["receita"] for x in anos if a[x].get("da") is not None])
        aj = min(0.0, median(dd) - median(cx)) if cx and dd else 0.0
    else:
        ajs = []
        for i in range(max(1, len(anos) - 5), len(anos)):
            cm, _ = capex_manutencao(emp.ticker, anos[i], anos[i - 1], expansao=expansao_do_ano(emp, anos[i]))
            da = a[anos[i]].get("da")
            if cm is not None and da is not None:
                ajs.append(min(0.0, da - cm) / a[anos[i]]["receita"])
        aj = median(ajs) if ajs else 0.0
    nao_rec = {x: outras(a[x], liq) - mo * a[x]["receita"] for x in anos
               if outras(a[x], liq) - mo * a[x]["receita"] > 0.03 * a[x]["receita"]}
    imp = imp_rec if (emp.da_receita is not None or emp.impairment_normalizado) and not emp.deflator else 0.0
    # §11.4 (quebra estrutural): mede a divergência entre a mediana dos 5 últimos exercícios e a da janela inteira.
    # Só MEDE e sinaliza — a janela nunca troca sozinha, porque "mudança documentada" é julgamento, não cálculo, e em
    # cíclica a janela curta pegaria exatamente o pico que o §2 proíbe (por isso o sinal não vale para cíclica).
    # O corte é o PERFIL, não `ciclico()`: este último também é True por `capex_ciclico` (regra de capex de rede em
    # telecom e distribuição), e isso desligaria o alarme em empresa de serviço — achado do adversário em 05/10/2026.
    m50_5 = median(sorted(por_ano[x] for x in anos[-5:]))
    div = (m50_5 - m50) / abs(m50) if m50 else 0.0
    return dict(margens=margens, m25=m25, m50=m50, m75=m75, receita_meio=rec, anos=anos, ajuste_manut=aj, med_outras=mo, nao_rec=nao_rec,
                impairment_recorrente=imp, m50_5a=m50_5, divergencia_janela=div,
                quebra_suspeita=bool(abs(div) > LIMITE_QUEBRA and emp.perfil != "ciclica"))


def ciclico(emp: Industrial):
    return emp.perfil == "ciclica" if emp.capex_ciclico is None else emp.capex_ciclico


def _anos_com_imposto(emp: Industrial) -> list:
    """Os 5 últimos exercícios da janela com LAIR > 0 e a linha do IR; com `aliquota_desde`, só os da lei vigente (AUD-09)."""
    a, _ = serie(emp.ticker)
    desde = int(emp.aliquota_desde["ano"]) if emp.aliquota_desde else 0
    return [x for x in anos_validos(emp.ticker, emp.anos_ciclo)[-5:]
            if int(x) >= desde and a[x].get("lair") and a[x]["lair"] > 0 and a[x].get("ir") is not None]


def mediana_efetiva(emp: Industrial) -> float | None:
    """Mediana de −IR ÷ LAIR dos 5 últimos exercícios da janela (LAIR > 0). Anos fora de [0, 50%] não representam o normal
    (crédito maior que o imposto, ou LAIR quase zero). Menos de MINIMO_ANOS_ALIQUOTA anos dentro → None (adversário, 07/10:
    com 1 ou 2 anos a "mediana" é um ano só, e os anos de crédito descartados ficariam inteiros no OE)."""
    a, _ = serie(emp.ticker)
    tx = [-a[x]["ir"] / a[x]["lair"] for x in _anos_com_imposto(emp)]
    tx = [x for x in tx if 0 <= x <= 0.5]
    return median(tx) if len(tx) >= MINIMO_ANOS_ALIQUOTA else None


def aliquota_regra(emp: Industrial) -> tuple[float, str]:
    """(alíquota PERPÉTUA, regra) — doutrina §2, v2.3 (07/10/2026). A perpétua vale no WACC, no NOPAT, no ROIC e no OE.

    · explícita: premissa do lote com razão escrita (ABEV3: só os anos depois da Lei 14.789/2023);
    · fase: crédito de IR COM PRAZO (ágio amortizável, subvenção de ICMS) → 34% na perpetuidade e no WACC; a alíquota efetiva
      só vale até o fim do benefício, como valor presente à parte (`fase_fiscal`, `beneficio_fiscal`);
    · mediana: benefício PERMANENTE (JCP, regime sem prazo) fica na mediana efetiva de 5 anos, teto 34%, SEM piso (o piso de
      15% da v2.2 acabou);
    · mediana abaixo de 15% sem a origem declarada (`aliquota_permanente_fonte`) → 34%: benefício de origem e prazo
      desconhecidos tem prazo zero. Sem isso, tirar o piso SUBIRIA o central de quem tem crédito temporário (TIMS3, PRIO3);
    · sem_dado: menos de 3 exercícios com taxa entre 0 e 50% nos 5 últimos → 34% e OE refeito (mesmo tratamento do sem_origem).
    """
    if emp.aliquota is not None:
        return emp.aliquota, "explicita"
    if emp.aliquota_fase:
        return ALIQUOTA_MARGINAL, "fase"
    m = mediana_efetiva(emp)
    if m is None:
        return ALIQUOTA_MARGINAL, "sem_dado"
    if m >= LIMIAR_ORIGEM:
        return min(m, ALIQUOTA_MARGINAL), "mediana"
    if emp.aliquota_permanente_fonte.strip():
        return m, "permanente"
    return ALIQUOTA_MARGINAL, "sem_origem"


def aliquota(emp: Industrial):
    return aliquota_regra(emp)[0]


def fase_fiscal(emp: Industrial) -> tuple[float, int] | None:
    """(alíquota efetiva da fase, exercícios cheios restantes depois de ANO_BASE) do crédito com prazo; None sem fase.

    A efetiva é a declarada ou a mediana de 5 anos COM os anos de crédito (taxa negativa: é justamente o benefício que a fase
    mede), presa entre 0 e 34%. Sem o corte em zero, um crédito maior nunca dá valor menor (adversário, 07/10: com o corte, a
    HYPE3 ficava com um ano só e um crédito um pouco maior zerava a fase). Menos de 3 anos com LAIR > 0 → efetiva 34%
    (benefício zero, conservador)."""
    f = emp.aliquota_fase
    if not f:
        return None
    ef = f.get("efetiva")
    if ef is None:
        a, _ = serie(emp.ticker)
        tx = [-a[x]["ir"] / a[x]["lair"] for x in _anos_com_imposto(emp)]
        tx = [x for x in tx if x <= 0.5]
        ef = median(tx) if len(tx) >= MINIMO_ANOS_ALIQUOTA else None
    ef = ALIQUOTA_MARGINAL if ef is None else min(max(ef, 0.0), ALIQUOTA_MARGINAL)
    return ef, max(int(f["ate"]) - ANO_BASE, 0)


def credito_observado(emp: Industrial) -> float:
    """Crédito de IR observado por ano (R$ mil, a preços do último exercício): mediana de 34% × LAIR + IR (IR negativo =
    despesa) nos 5 últimos anos com LAIR > 0. É o teto do benefício anual da fase: o modelo nunca supõe crédito maior que o
    que a empresa de fato teve (adversário, 07/10)."""
    a, _ = serie(emp.ticker)
    anos = _anos_com_imposto(emp)
    if not anos:
        return 0.0
    ult = anos[-1]
    return max(median((ALIQUOTA_MARGINAL * a[x]["lair"] + a[x]["ir"]) * fator_entre(x, ult) for x in anos), 0.0)


def beneficio_fiscal(emp: Industrial, lair_norm: float, taxa: float) -> float:
    """Valor presente (R$ mil) do crédito com prazo: Σ_{t=1..N} min(LAIR normalizado × (perpétua − efetiva), crédito
    observado) ÷ (1 + taxa)^t.

    A base é o lucro DEPOIS dos juros normalizados (lucro operacional pré-IR − Kd × dívida líquida): o WACC já dá a dedução
    dos juros a 34%, e o benefício sobre o lucro antes dos juros a contaria de novo (adversário, 07/10: R$ 1,34/ação na
    HYPE3). O teto é o crédito que a empresa de fato teve (`credito_observado`). Sem crescimento do benefício e sem o
    trimestre corrente (conservador); zero sem fase ou com base ≤ 0."""
    fase = fase_fiscal(emp)
    if not fase or lair_norm <= 0:
        return 0.0
    ef, n = fase
    anual = min(lair_norm * (aliquota(emp) - ef), credito_observado(emp))
    return sum(anual / (1 + taxa) ** t for t in range(1, n + 1))


def custo_divida(emp: Industrial, mk: Mercado, op: dict | None = None) -> dict:
    """Kd nominal (doutrina §2, v2.4 — AUD-07): o custo médio do RI (`kd_ri`) quando declarado; senão rf nominal + spread.
    O spread é o digitado com fonte ou, por padrão, o sintético pela cobertura NORMALIZADA = lucro operacional pré-IR de meio de
    ciclo ÷ juros do período (LTM). Normalizada porque o EBIT de 12 meses de cíclica no vale ou no pico mudaria o rating a cada
    trimestre (com o LTM a SUZB3 caía para B+ e a KLBN11 para B)."""
    if emp.kd_ri:
        return dict(kd=float(emp.kd_ri["valor"]), origem="RI", spread=None, rating=None, cobertura=None,
                    fonte=emp.kd_ri["fonte"])
    if emp.spread_kd is not None:
        return dict(kd=mk.rf_nom + emp.spread_kd, origem="spread declarado", spread=emp.spread_kd, rating=None,
                    cobertura=None, fonte=emp.spread_fonte)
    _, ltm = serie(emp.ticker)
    op = op or premissas_operacionais(emp)
    juros, _f = juros_do_periodo(ltm)
    if juros <= 0 and divida_liquida(ltm)[0] > 0:
        # adversário (08/10): dívida sem linha de juros virava AAA em silêncio — falha alto, como as outras premissas sem fonte
        raise ValueError(f"{emp.ticker}: dívida bruta > 0 sem juros no período ({_f}); declarar kd_ri ou spread_kd com spread_fonte")
    cob = op["receita_meio"] * (op["m50"] + op["ajuste_manut"]) / juros if juros > 0 else None
    sp, rating = spread_sintetico(cob)
    return dict(kd=mk.rf_nom + sp, origem="sintético", spread=sp, rating=rating, cobertura=cob, fonte=FONTE_SPREAD)


def wacc(emp: Industrial, mk: Mercado, ke_nom=None, kd=None, e_peso=None):
    """WACC nominal. O peso do acionista é `e_peso` (R$ mil; o valor da casa no ponto fixo, AUD-13); sem ele, o preço."""
    _, ltm = serie(emp.ticker)
    bruta, caixa, dl = divida_liquida(ltm)
    e = emp.preco * emp.n_acoes / 1000 if e_peso is None else e_peso     # R$ mil
    d = bruta
    ke = ke_nom if ke_nom is not None else mk.ke_nom
    kd = custo_divida(emp, mk)["kd"] if kd is None else kd
    w = ke * e / (e + d) + kd * (1 - aliquota(emp)) * d / (e + d)
    return w, kd, e, d


def premio_alavancado(d: float, e: float, t: float) -> float:
    """Prêmio do Ke real pela alavancagem (doutrina §4, v2.4 — AUD-12, decisão do Frank em 08/10/2026): os 5 p.p. são o risco do
    negócio SEM dívida e a dívida soma risco ao acionista — Hamada (1972), Journal of Finance 27(2):435-452, sobre Modigliani-Miller:
    prêmio = 5 p.p. × [1 + (1 − t) × D/E]. D = dívida bruta do WACC, E = valor da casa (ponto fixo), t = alíquota perpétua."""
    return PREMIO_KE * (1 + (1 - t) * d / e)


def estrutura_de_capital(emp: Industrial, mk: Mercado) -> dict:
    """Ponto fixo dos pesos do WACC (doutrina §2, v2.4 — AUD-13, decisão do Frank em 08/10/2026).

    O peso do acionista é o valor que a casa calcula (central × ações), não o preço: com o preço, o central mudava quando só o
    preço mudava, e o P/C comparava o preço com um número que dependia dele. Como o central depende do peso e do Ke (que depende de
    D/E), repete-se valores() → central → E com amortecimento até |ΔE/E| < TOL_PONTO_FIXO. Sem central positivo (equity ≤ 0 pela
    casa) não há ponto fixo: os pesos e o Ke ficam no patrimônio contábil, só para exibir — a palavra já é NÃO CONCLUSIVO.

    A iteração PARTE do patrimônio contábil, não do preço (adversário, 08/10): partindo do preço, a KLBN11 desistia ou achava raiz
    conforme o preço — o central voltava a depender dele. Sem PL positivo, parte de E = D (D/E = 1)."""
    _, ltm = serie(emp.ticker)
    d = divida_liquida(ltm)[0]
    t = aliquota(emp)
    desc = desconto_pct(emp)
    pl = v(ltm, "pl", 0) - v(ltm, "nao_controladores", 0)
    e0 = pl if pl > 0 else max(d, 1.0)
    e = e0
    for i in range(1, MAX_ITER_PONTO_FIXO + 1):
        mk_e = replace(mk, premio=premio_alavancado(d, e, t))
        central = central_de(descontar(valores(emp, mk_e, e_peso=e)["anc"], desc))[0]
        if central <= 0:
            return dict(mk=replace(mk, premio=premio_alavancado(d, e0, t)), e_peso=e0, iteracoes=i,
                        ponto_fixo=False, nota="sem central positivo: pesos e Ke no patrimônio contábil, só para exibir")
        e_novo = central * emp.n_acoes / 1000
        if abs(e_novo / e - 1) < TOL_PONTO_FIXO:
            return dict(mk=replace(mk, premio=premio_alavancado(d, e_novo, t)), e_peso=e_novo, iteracoes=i, ponto_fixo=True,
                        nota=f"ponto fixo em {i} iterações")
        e = 0.5 * e + 0.5 * e_novo
    raise RuntimeError(f"{emp.ticker}: pesos do WACC sem ponto fixo em {MAX_ITER_PONTO_FIXO} iterações (último E {e:.0f})")


def valores(emp: Industrial, mk: Mercado, ke_nom=None, margem=None, g_real=None, g1=None, e_peso=None):
    """Âncoras ao Ke dado. Retorna dict de valores por ação e insumos. g1 sobrepõe emp.g1_real (DCF reverso de 2 estágios).
    `e_peso` = peso do acionista no WACC (ponto fixo, AUD-13); None = preço (uso avulso, sensibilidades dos PDFs)."""
    a, ltm = serie(emp.ticker)
    op = premissas_operacionais(emp)
    cdiv = custo_divida(emp, mk, op)
    w_nom, kd, e_w, d = wacc(emp, mk, ke_nom, kd=cdiv["kd"], e_peso=e_peso)
    e = emp.preco * emp.n_acoes / 1000      # valor de mercado (EV do Greenblatt, porte); o peso do WACC é e_w
    w_real = (1 + w_nom) / (1 + mk.pi) - 1
    ke = ke_nom if ke_nom is not None else mk.ke_nom
    ke_real = (1 + ke) / (1 + mk.pi) - 1
    bruta, caixa, dl = divida_liquida(ltm)
    # v2.3: passivo com juros/financeiro fora das contas de empréstimo é dívida — entra na DL e, por ela, na ponte, no DL/EBITDA,
    # no capital do ROIC, no EV e nos juros normalizados. O WACC fica com a dívida do balanço (peso menor de Kd = conservador).
    # AUD-02: o provento já ex que ainda está no caixa é o mesmo tipo de passivo financeiro, medido do dado (não digitado)
    prov = proventos_ja_ex(emp, mk.data or None)
    dl += emp.outros_passivos_financeiros + prov["total"]
    minor = v(ltm, "nao_controladores", 0) + emp.outros_passivos   # direitos à frente do acionista (operacional) só na ponte
    n = emp.n_acoes / 1000     # mil ações → valores em R$ mil / mil ações = R$/ação
    m = margem if margem is not None else op["m50"]
    gr = emp.g_real if g_real is None else g_real
    t_ef, t_regra = aliquota_regra(emp)          # perpétua (v2.3); o crédito com prazo entra à parte, em valor presente
    lucro_pre_ir = op["receita_meio"] * (m + op["ajuste_manut"])
    nopat = lucro_pre_ir * (1 - t_ef)
    cap_inv = v(ltm, "pl", 0) - prov["no_pl"] + dl     # provento aprovado depois do balanço sai do PL ao entrar na DL
    idade_imob, cap_rep = capital_reposicao(emp.ticker, cap_inv)
    roic = nopat / cap_inv if cap_inv > 0 else None
    # capital contábil negativo corrigido pela inflação pode virar positivo minúsculo e explodir o ROIC a reposição:
    # sem capital contábil positivo não há ROIC nenhum (achado do adversário em 05/10/2026)
    roic_rep = nopat / cap_rep if (cap_inv > 0 and cap_rep > 0) else None
    # doutrina §2: o filtro 1, a nota de qualidade e a trava do crescimento usam o MENOR dos dois (conservador)
    roic_filtro = min(x for x in (roic, roic_rep) if x is not None) if roic is not None else None
    roic_real = (1 + roic) / (1 + mk.pi) - 1 if roic else None

    # base do crédito com prazo: lucro depois dos juros normalizados (v2.3); caixa líquido não aumenta a base (o caixa rende
    # rf, não Kd — adversário, 07/10)
    lair_norm = lucro_pre_ir - kd * max(dl, 0.0)
    benef_firma = beneficio_fiscal(emp, lair_norm, w_real)
    epv_firma = nopat / w_real + benef_firma
    epv = (epv_firma - dl - minor) / n

    g1_ = emp.g1_real if g1 is None else g1

    def dcf(mg):
        pre = op["receita_meio"] * (mg + op["ajuste_manut"])
        nop = pre * (1 - t_ef)
        bf = beneficio_fiscal(emp, pre - kd * max(dl, 0.0), w_real)   # crédito com prazo (v2.3): VP à parte, zero sem fase
        roic_c = nop / cap_inv if cap_inv > 0 else None
        # Greenwald: crescimento só tem valor se o ROIC supera o custo de capital (os dois nominais, doutrina §2).
        # Abaixo disso g = 0 e o DCF converge para o EPV; acima, reinvestimento = g real ÷ ROIC.
        # Etapa 2/F2: a trava usa o MENOR dos dois ROIC — crescer exige retorno acima do WACC sobre o capital a
        # preços de hoje, que é o que a empresa terá de repor. O reinvestimento segue pelo ROIC contábil (é o
        # capital que ela de fato emprega). A trava é avaliada POR CENÁRIO: é um degrau em cada cenário (AUD-14), e só a
        # ponderação dos três suaviza.
        roic_rep_c = nop / cap_rep if cap_rep > 0 else None
        cria = roic_c is not None and min(roic_c, roic_rep_c if roic_rep_c is not None else roic_c) > w_nom
        g_ef = gr if (gr <= 0 or cria) else 0.0   # só zera crescimento positivo
        # reinvestimento = g REAL ÷ ROIC REAL (Fisher) — real com real (doutrina §4); até 05/10 dividia pelo ROIC nominal (adversário do Lote 4)
        roic_r = (1 + roic_c) / (1 + mk.pi) - 1 if roic_c is not None else None
        # AUD-34 (v2.6): declínio com ROIC < WACC não devolve capital por padrão — o "reinvestimento negativo" g ÷ ROIC com ROIC
        # pequeno fazia o DCF explodir (KLBN11: 3,79 em g = 0 e 357 em g = −5%); antes só a RECV3 tinha o freio declarado
        freio = g_ef < 0 and (emp.declinio_sem_liberacao or not cria)
        reinv = g_ef / roic_r if (g_ef != 0 and roic_r and not freio) else 0.0
        if g1_ is None:
            fcff1 = nop * (1 + g_ef) * (1 - reinv)
            return (fcff1 / (w_real - g_ef) + bf - dl - minor) / n
        # 2 estágios (compounder): NOPAT cresce g1 real por anos_g1 anos reinvestindo g1 ÷ ROIC; depois, Gordon com g_ef
        g1e = g1_ if cria else 0.0
        vp, nop_t = 0.0, nop
        for t in range(1, emp.anos_g1 + 1):
            nop_t *= 1 + g1e
            vp += nop_t * (1 - (g1e / roic_r if g1e > 0 else 0.0)) / (1 + w_real) ** t
        terminal = nop_t * (1 + g_ef) * (1 - reinv) / (w_real - g_ef)
        return (vp + terminal / (1 + w_real) ** emp.anos_g1 + bf - dl - minor) / n
    dcf_c = {"pessimista": dcf(op["m25"]), "base": dcf(m), "otimista": dcf(op["m75"])}
    # AUD-53 (v2.6): cenário negativo entra como zero (o acionista não deve além do que pôs) — antes puxava a média para baixo
    dcf_pond = 0.25 * max(dcf_c["pessimista"], 0) + 0.5 * max(dcf_c["base"], 0) + 0.25 * max(dcf_c["otimista"], 0)

    oes = []
    anos = op["anos"]
    t_oe = t_ef if t_regra in ("explicita", "fase", "sem_origem", "sem_dado") else None   # v2.3: OE à alíquota perpétua
    for i in range(1, len(anos)):
        x = owner_earnings_ano(emp, anos[i], anos[i - 1], (1 + kd) / (1 + mk.pi) - 1, ciclico(emp), t_oe)
        if x is not None:
            oes.append((anos[i], x * deflator_exercicio(emp.ticker, anos[i])))   # AUD-16: em R$ de hoje antes da mediana (capitalizado ao Ke REAL)
    oe_recentes = [x for _, x in oes[-5:]]
    oe_norm = median(oe_recentes) if oe_recentes else None
    # fluxo do acionista: o crédito com prazo incide sobre o lucro depois dos juros normalizados, ao Ke real
    benef_acao = beneficio_fiscal(emp, lair_norm, ke_real)
    # o OE é fluxo do acionista (depois dos juros da DL do balanço): os dois outros passivos saem por inteiro
    oe_val = ((oe_norm / (ke_real - gr) + benef_acao - emp.outros_passivos - emp.outros_passivos_financeiros - prov["total"]) / n
              if oe_norm and ke_real > gr else None)

    reprod = (emp.reproducao_por_acao if emp.reproducao_por_acao else
              (v(ltm, "pl", 0) - prov["no_pl"] - v(ltm, "nao_controladores", 0)) / n)
    # AUD-18 (v2.4): a âncora fica no PL contábil — é o MENOR dos dois, a mesma regra conservadora do ROIC (§2). A reprodução a
    # custo de reposição (imobilizado corrigido pelo IPCA da idade média, a mesma correção do ROIC) é só exibida.
    reprod_reposicao = (None if emp.reproducao_por_acao else
                        reprod + (cap_rep - cap_inv) / n if (cap_inv > 0 and cap_rep > 0) else None)

    anc = {}
    if emp.perfil == "ciclica":
        anc["EPV de meio de ciclo"] = epv
        anc["DCF normalizado (3 cenários)"] = dcf_pond
        if emp.usar_reproducao_como_ancora:
            anc["Valor de reprodução"] = reprod
    else:
        anc["DCF (3 cenários)"] = dcf_pond
        anc["EPV"] = epv
        if oe_val:
            anc["Owner Earnings ÷ (Ke − g)"] = oe_val
    # AUD-47: a âncora OE que some (OE normalizado ausente/zero ou Ke real ≤ g) fica registrada — a confiança segue a §11.3
    descartadas = ([] if emp.perfil == "ciclica" or oe_val else
                   ["Owner Earnings ÷ (Ke − g): " + ("OE normalizado ausente ou zero" if not oe_norm else "Ke real ≤ g")])
    return dict(anc=anc, ancoras_descartadas=descartadas, op=op, wacc=w_nom, wacc_real=w_real, kd=kd, kd_info=cdiv, e=e, e_peso=e_w, d=d, dl=dl, bruta=bruta, caixa=caixa,
                minor=minor, nopat=nopat, roic=roic, epv=epv, dcf=dcf_c, dcf_pond=dcf_pond, oe=oes, oe_norm=oe_norm,
                oe_val=oe_val, reprod=reprod, reprod_reposicao=reprod_reposicao, cap_inv=cap_inv, n=n, m=m, gr=gr, aliquota=t_ef, aliquota_regra=t_regra,
                aliquota_mediana=mediana_efetiva(emp), aliquota_fase=fase_fiscal(emp), beneficio_fiscal_acao=benef_firma / n,
                outros_passivos_financeiros=emp.outros_passivos_financeiros, proventos_ja_ex=prov, capex_expansao=emp.capex_expansao,
                roic_reposicao=roic_rep, roic_filtro=roic_filtro, cap_inv_reposicao=cap_rep, idade_imobilizado=idade_imob)


def qualifica_saida(anos_serie: int, anos_acima: int, nota_qualidade: float) -> bool:
    """§9, exceção de saída a 1,50×: série com ao menos 10 exercícios, ROIC real > WACC real em 8 deles e nota de qualidade ≥ 8."""
    if anos_serie < 0 or anos_acima < 0 or anos_acima > anos_serie:      # N7: mais anos acima do que a série tem é dado impossível
        raise ValueError(f"qualifica_saida: anos acima ({anos_acima}) fora de 0..{anos_serie} (anos da série)")
    return (anos_serie >= JANELA_MINIMA_SAIDA and anos_acima >= ANOS_ROIC_MINIMO
            and nota_qualidade >= NOTA_QUALIDADE_MINIMA)


def roic_por_ano(emp: Industrial, w_real, t_ef, med_outras):
    """Série de ROIC a custo de reposição por exercício e quantos superaram o WACC — REAL contra REAL (§4, §9).

    ROIC do exercício = EBIT ajustado × (1 − alíquota) ÷ (PL + dívida líquida do próprio exercício, com o
    imobilizado corrigido para os preços daquele exercício pela mesma idade média). Entra na exceção de venda por
    qualidade; é o ROIC realizado, não o normalizado de `valores`.

    O ROIC de um exercício é nominal DAQUELE ano (IPCA de 3,2% a 9,3% na janela) e o WACC é o de hoje (rf nominal de
    ~15%): comparar os dois nominalmente reprovava quase todo exercício antigo. Deflaciona-se cada ROIC pela inflação
    do próprio exercício e compara-se com o WACC real — o mesmo "real com real" que o §4 já exige no reinvestimento
    do DCF. Achado do adversário em 05/10/2026 (invertia a contagem em 8 dos 21 tickers).
    """
    a, _ = serie(emp.ticker)
    idade, _ = idade_e_fator(emp.ticker)
    serie_roic, acima = {}, 0
    for x in anos_validos(emp.ticker, emp.anos_ciclo):
        d = a[x]
        _, _, dl = divida_liquida(d)
        ci = v(d, "pl", 0) + dl
        if ci <= 0:
            continue
        ci += v(d, "imobilizado", 0) * (fator_idade(x, idade) - 1)
        nominal = ebit_aj(d, med_outras, emp.outras_liquidas) * (1 - t_ef) / ci
        serie_roic[x] = (1 + nominal) / (1 + inflacao_do_ano(x)) - 1
        acima += serie_roic[x] > w_real
    return serie_roic, acima


def central_de(anc):
    vals = list(anc.values())
    ruins = [k for k, x in anc.items() if not isinstance(x, (int, float)) or isinstance(x, bool) or not math.isfinite(x)]
    if not vals or ruins:    # N7: NaN na mediana depende da ordem das âncoras
        raise ValueError(f"central_de: âncora(s) inválida(s) (NaN/inf/ausente): {ruins or 'nenhuma âncora'}")
    return median(vals), vals


def desconto_pct(emp: Industrial) -> float:
    """§5: desconto de controlador declarado — fixo ou Σ prob × perda dos cenários; zero no mais."""
    dc = emp.desconto_controlador
    return (dc.get("pct", 0.0) if dc["tipo"] == "fixo" else
            sum(c["prob"] * c["perda"] for c in dc["cenarios"]) if dc["tipo"] == "cenarios" else 0.0)


def ke_implicito(emp, mk, e_peso=None):
    # o preço se compara ao central COM o desconto (§5: uma única vez, no valor) — até a v2.2 este cálculo o ignorava
    desc = desconto_pct(emp)
    lo, hi = mk.g_teto + 0.003, 0.60
    f = lambda k: central_de(descontar(valores(emp, mk, ke_nom=k, e_peso=e_peso)["anc"], desc))[0]
    try:
        if f(lo) < emp.preco:
            return None
        for _ in range(70):
            mid = (lo + hi) / 2
            if f(mid) > emp.preco:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    except ZeroDivisionError:
        return None


def g_implicito(emp, mk, e_peso=None):
    """DCF reverso: crescimento real perpétuo que iguala o DCF base ao preço (margem mediana, Ke da casa).
    Com DCF de 2 estágios: o g real dos primeiros anos_g1 anos (perpetuidade fixa). DCF com o desconto de controlador (§5)."""
    desc = desconto_pct(emp)
    dcf_base = lambda **kw: descontar({"b": valores(emp, mk, e_peso=e_peso, **kw)["dcf"]["base"]}, desc)["b"]
    if emp.g1_real is not None:
        lo, hi = 0.0, 0.40
        f = lambda g: dcf_base(g1=g)
        if f(hi) < emp.preco:
            return None
        if f(lo) > emp.preco:
            return lo - 1e-9
        for _ in range(70):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if f(mid) > emp.preco else (mid, hi)
        return (lo + hi) / 2
    lo, hi = -0.05, min(0.08, valores(emp, mk, e_peso=e_peso)["wacc_real"] - 0.002)
    f = lambda g: dcf_base(g_real=g)
    if f(hi) < emp.preco:
        return None
    if f(lo) > emp.preco:
        return lo - 1e-9     # abaixo do piso: o PDF mostra "≤ −5%"
    for _ in range(70):
        mid = (lo + hi) / 2
        if f(mid) > emp.preco:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def nota_alavancagem(dl_ebitda_norm: float | None) -> float:
    """Nota 1–10 da DL/EBITDA normalizada na Solidez. Indefinida (EBITDA normalizado ≤ 0) é o pior caso, não "sem dívida":
    antes o ausente virava 0 e a nota 10 (AUD-54)."""
    if dl_ebitda_norm is None:
        return 1
    return interp(-dl_ebitda_norm, [(-5, 1), (-4, 3), (-3, 5), (-2, 7), (-1, 9), (0, 10)])


def avaliar(emp: Industrial, mk: Mercado) -> dict:
    exigir_declaracoes(emp)
    a, ltm = serie(emp.ticker)
    # v2.4 (AUD-12/13): Ke da empresa pela alavancagem e pesos do WACC no ponto fixo; daqui em diante TODO uso do Ke
    # (âncoras, OE, defasagem, trava, sensibilidade, Ke/g implícitos) é o da empresa
    ec = estrutura_de_capital(emp, mk)
    mk, ep = ec["mk"], ec["e_peso"]
    r = valores(emp, mk, e_peso=ep)
    desc = desconto_pct(emp)
    anc = descontar(r["anc"], desc)      # v2.3: só em âncora > 0 (a ≤ 0 continua forçando NÃO CONCLUSIVO)
    central, vals = central_de(anc)
    nao_conc = any(x <= 0 for x in vals)
    disp = max(vals) / min(vals) if not nao_conc else float("inf")
    pc = emp.preco / central if central > 0 else float("inf")
    p0 = palavra(pc) if central > 0 else "NÃO CONCLUSIVO"
    p = p0
    if emp.fora_circulo and p in ("BARATA",):
        p = "RADAR"
    conf = "normal" if len(vals) > 1 else "baixa (âncora única)"
    if nao_conc or disp > 3:
        p, conf = "NÃO CONCLUSIVO", "não conclusivo"
    elif disp > 1.8:
        conf = "baixa"
        if p in ("BARATA", "RADAR"):
            p = ORDEM[ORDEM.index(p) + 1]

    n = r["n"]
    ebitda_ltm = ebit_aj(ltm, r["op"]["med_outras"], emp.outras_liquidas) + v(ltm, "da", 0)
    ebitda_norm = r["op"]["receita_meio"] * r["m"] + (r["op"]["receita_meio"] * emp.da_receita if emp.da_receita is not None else
                                                      median([a[x]["da"] for x in r["op"]["anos"][-3:] if a[x].get("da")] or [0]))
    dl_ebitda = r["dl"] / ebitda_ltm if ebitda_ltm > 0 else None
    dl_ebitda_norm = r["dl"] / ebitda_norm if ebitda_norm > 0 else None
    juros, juros_fonte = juros_do_periodo(ltm)
    cobertura = v(ltm, "ebit", 0) / juros if juros > 0 else None

    ev = r["e"] + r["dl"]
    ey = v(ltm, "ebit", 0) / ev if ev > 0 else None
    roc_base = max(capital_giro(ltm), 0) + v(ltm, "imobilizado", 0)
    roc = v(ltm, "ebit", 0) / roc_base if roc_base > 0 else None

    ult, pen = "2025", "2024"
    if emp.ticker == "SMTO3":
        ult, pen = "2026", "2025"
    d1, d0 = a[ult], a[pen]
    z, zona = altman_z2(ltm if ltm.get("ativo") else d1)
    pf, pf_crit = piotroski(d1, d0)
    mb = beneish(d1, d0)
    sl = sloan(d1, d0)

    # lucro normalizado por ação (para Graham, Lynch, Bogle): NOPAT normalizado − juros líquidos normalizados após IR
    lucro_norm = r["nopat"] - r["kd"] * r["dl"] * (1 - r["aliquota"])   # dívida líquida negativa (caixa) soma receita financeira
    lpa_norm = lucro_norm / n
    vpa = (v(ltm, "pl", 0) - r["proventos_ja_ex"]["no_pl"] - v(ltm, "nao_controladores", 0)) / n
    graham_orig = math.sqrt(22.5 * lpa_norm * vpa) if lpa_norm > 0 and vpa > 0 else None
    graham_br = math.sqrt(22.5 * mk.fator_graham * lpa_norm * vpa) if lpa_norm > 0 and vpa > 0 else None
    g_real_pct = 100 * r["gr"]
    graham_rev = lpa_norm * (8.5 + 2 * g_real_pct) * mk.fator_graham if lpa_norm > 0 else None

    dpa = SI[emp.ticker]["dpa_por_ano_datacom"]
    # AUD-16: DPA de cada ano da data-com em R$ de hoje — é comparado ao OE (já em R$ de hoje) e vira yield sobre o preço de hoje
    dpa5 = sum(dpa.get(str(x), 0) * DEFLATOR[str(x)] for x in range(2021, 2026)) / 5
    fcfe_acao = (r["oe_norm"] / n) if r["oe_norm"] else 0
    dpa_sust = min(dpa5, max(fcfe_acao, 0))
    coberto = dpa5 <= fcfe_acao
    bazin6 = dpa_sust / 0.06 if dpa_sust > 0 else None

    g_nom = (1 + r["gr"]) * (1 + mk.pi) - 1
    if emp.g1_real is not None:
        # Bogle de 10 anos: o LPA cresce g1 nos anos_g1 primeiros anos (dentro do horizonte), não o g perpétuo
        g1n = (1 + emp.g1_real) * (1 + mk.pi) - 1
        k = min(emp.anos_g1, HORIZONTE)
        g_nom = ((1 + g1n) ** k * (1 + g_nom) ** (HORIZONTE - k)) ** (1 / HORIZONTE) - 1
    meses = emp.defasagem_meses if emp.defasagem_meses is not None else defasagem_meses(emp.ticker)
    fvp = (1 + mk.ke_nom) ** (-meses / 12)   # defasagem: provento a valor presente ao Ke nominal (§6.3)
    dpa_sust_vp = dpa_sust * fvp
    dpa_sust_liq = dpa_sust_vp * (1 - emp.jcp_share * IR_JCP)
    teto = dpa_sust_liq / mk.rf_liq_nom if (coberto and dpa_sust > 0) else None
    dy = dpa_sust_vp / emp.preco
    pl_atual = emp.preco / lpa_norm if lpa_norm > 0 else None
    pl_final = emp.pl_hist
    dmult = (pl_final / pl_atual) ** (1 / HORIZONTE) - 1 if (pl_final and pl_atual) else 0.0
    bogle_nom = dy + g_nom + dmult
    dy_liq = dy * (1 - emp.jcp_share * IR_JCP)
    gc = g_nom + dmult
    bogle_liq_nom = dy_liq + (liquido_diferido(gc) if gc > 0 else gc)
    bogle_liq_real = (1 + bogle_liq_nom) / (1 + mk.pi) - 1
    so_inv_liq_real = (1 + dy_liq + liquido_diferido(g_nom)) / (1 + mk.pi) - 1

    def cls(x):
        return "Sim" if x >= mk.rf_liq_real + 0.03 else ("Empate" if x >= mk.rf_liq_real + 0.015 else "Não")
    rf, rf_inv = cls(bogle_liq_real), cls(so_inv_liq_real)
    trava = abs(bogle_nom - mk.ke_nom) <= TRAVA_PP if p == "JUSTA" else None    # AUD-10 (v2.6): palavra final
    p_trava = aplicar_trava(p0, p, trava, emp.trava_razao)
    if p_trava != p:
        p, conf = p_trava, "não conclusivo (trava de coerência, §9)"

    peg = (pl_atual / (100 * g_nom)) if pl_atual else None
    pegy = (pl_atual / (100 * (g_nom + dy))) if pl_atual else None

    # sensibilidade: Ke do acionista ±1 p.p. (prêmio; Kd fixo; rf não move — difere das financeiras, AUD-96) × margem ±2 p.p.
    sens = {}
    for dk in (-0.01, 0, 0.01):
        for dm in (-0.02, 0, 0.02):
            vv = valores(emp, mk, ke_nom=mk.ke_nom + dk, margem=r["m"] + dm, e_peso=ep)["anc"]
            sens[(dk, dm)] = central_de(descontar(vv, desc))[0]

    # notas — o spread usa o MENOR dos dois ROIC (doutrina §2: capital a custo histórico infla o retorno);
    # o qualitativo é a média da regra 11 (v2.3): controlador com peso 2 quando discricionário
    qual = media_qualitativa(emp.qualitativo, emp.controlador_discricionario) * 2
    n_qual = 0.5 * nota_spread(r["roic_filtro"] or 0, r["wacc"]) + 0.5 * qual
    alav_n = nota_alavancagem(dl_ebitda_norm)
    z_n = {"segura": 10, "cinzenta": 6, "perigo": 2}[zona]
    cob_n = interp(cobertura or 0, [(1, 1), (2, 3), (3, 5), (5, 8), (8, 10)])
    n_sol = (alav_n + z_n + cob_n) / 3
    anos_pagos = emp.anos_pagos_10 if emp.anos_pagos_10 is not None else sum(1 for x in range(2016, 2026) if dpa.get(str(x), 0) > 0)
    n_renda = 0.5 * nota_yield(dy_liq / mk.rf_liq_nom) + 0.25 * (10 if coberto else 2) + 0.25 * anos_pagos
    n_preco = nota_preco(pc) if central > 0 else 0
    n_geral = 0.30 * n_qual + 0.20 * n_sol + 0.25 * n_renda + 0.25 * n_preco

    # §9 — exceção de venda por qualidade (Buffett 1988/1989): só com retorno acima do custo de capital em 8 de 10
    # exercícios A CUSTO DE REPOSIÇÃO e nota de qualidade ≥ 8. Tese quebrada continua saída a qualquer preço.
    serie_roic, anos_roic = roic_por_ano(emp, r["wacc_real"], r["aliquota"], r["op"]["med_outras"])
    # a exceção exige histórico de CICLO: janela declarada curta (quebra estrutural) não a permite, porque "8 de 10"
    # não tem referente numa janela de 5 ou 6 exercícios — e 5 anos não são um ciclo (§2)
    por_qualidade = qualifica_saida(len(serie_roic), anos_roic, n_qual)
    return dict(r, ancoras=anc, central=central, dispersao=disp, confianca=conf, pc=pc, palavra_regua=p0, palavra=p,
                **precos_de_referencia(central, por_qualidade), desc_controlador=desc,
                roic_serie=serie_roic, roic_anos_acima=anos_roic, roic_anos_total=len(serie_roic),
                ebitda_ltm=ebitda_ltm, ebitda_norm=ebitda_norm, dl_ebitda=dl_ebitda, dl_ebitda_norm=dl_ebitda_norm,
                cobertura_juros=cobertura, cobertura_fonte=juros_fonte, ey=ey, roc=roc, altman=z, altman_zona=zona, piotroski=pf, piotroski_crit=pf_crit,
                beneish=mb, sloan=sl, ano_qualidade=ult, lpa_norm=lpa_norm, vpa=vpa, graham_orig=graham_orig,
                graham_br=graham_br, graham_rev=graham_rev, dpa5=dpa5, fcfe_acao=fcfe_acao, dpa_sust=dpa_sust,
                coberto=coberto, dpa_sust_liq=dpa_sust_liq, teto_renda=teto, dpa_sust_vp=dpa_sust_vp, fator_defasagem=fvp, defasagem_meses=meses, bazin6=bazin6, dy=dy, dy_liq=dy_liq,
                g_nom=g_nom, pl_atual=pl_atual, pl_final=pl_final, dmult=dmult, bogle_nom=bogle_nom,
                bogle_liq_real=bogle_liq_real, so_inv_liq_real=so_inv_liq_real, vence_rf=rf, rf_sem_rerating=rf_inv,
                so_com_rerating=rf != rf_inv, carimbo_rf=bogle_liq_real < mk.rf_liq_real, trava=trava, peg=peg, pegy=pegy,
                ke_implicito=ke_implicito(emp, mk, ep), g_implicito=g_implicito(emp, mk, ep), sens=sens,
                ke_real_emp=mk.ke_real, ke_nom_emp=mk.ke_nom, premio_ke=mk.premio, de_peso=r["d"] / ep,
                ponto_fixo=ec["ponto_fixo"], ponto_fixo_nota=ec["nota"],
                # AUD-51: mediana efetiva a menos de 1 p.p. do limiar de 15% (degrau deliberado da v2.3 para 34%) — só aviso
                aliquota_perto_do_limiar=(r["aliquota_regra"] in ("mediana", "permanente", "sem_origem")
                                          and r["aliquota_mediana"] is not None
                                          and abs(r["aliquota_mediana"] - LIMIAR_ORIGEM) < 0.01),
                notas=dict(qualidade=n_qual, solidez=n_sol, renda=n_renda, preco=n_preco, geral=n_geral),
                qualitativo_origem=emp.qualitativo_origem, controlador_peso=2 if emp.controlador_discricionario else 1,
                ret_investimento=dy + g_nom, ret_especulativo=dmult, ticker=emp.ticker)
