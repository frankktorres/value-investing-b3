"""Motor de valuation para empresas não financeiras (industrial, serviços, cíclica/commodity) — doutrina v2.0 §11.

Fonte dos números: dados/cvm_series.json (DFP/ITR da CVM, R$ mil) + preço/ações/proventos da StatusInvest.
Tudo em R$ por ação no fim. Convenção: taxas em fração.
"""
from __future__ import annotations

import json
import math
import pathlib
from dataclasses import dataclass, field
from functools import lru_cache
from statistics import median

from defasagem import defasagem_meses
from inflacao import fator_entre, fator_idade, inflacao_do_ano, reposicao
from juros import juros_do_periodo
from motor_financeiras import (ANOS_ROIC_MINIMO, HORIZONTE, IR_JCP, NOTA_QUALIDADE_MINIMA, ORDEM, Mercado, interp,
                               liquido_diferido, nota_preco, nota_spread, nota_yield, palavra, precos_de_referencia)

AQUI = pathlib.Path(__file__).parent
CVM = json.loads((AQUI / "dados" / "cvm_series.json").read_text(encoding="utf-8"))
SI = json.loads(sorted((AQUI / "dados").glob("series_*.json"))[-1].read_text(encoding="utf-8"))
ANOS = [str(a) for a in range(2016, 2026)]
LIMITE_QUEBRA = 0.25      # §11.4: divergência entre a mediana de 5 anos e a da janela que levanta suspeita de quebra
JANELA_MINIMA_SAIDA = 10  # §9: a exceção de qualidade exige histórico de ciclo inteiro; janela curta não a permite


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
    aliquota: float | None = None   # None = alíquota efetiva mediana (−IR/LAIR) dos últimos 5 exercícios, entre 15% e 34%
    spread_kd: float = 0.02        # Kd nominal = rf nominal + spread
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
    outros_passivos: float = 0.0         # R$ mil; passivo de dívida fora de 2.01.04/2.02.01 (ex.: déficit atuarial)
    outros_passivos_fonte: str = ""
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


def exigir_declaracoes(emp: Industrial) -> None:
    """Premissa da casa sem fonte escrita não roda (doutrina §11.4 e §6.3). Falha alto, não silenciosa."""
    faltas = []
    if list(emp.anos_ciclo) != list(ANOS) and not emp.janela_razao.strip():
        faltas.append(f"janela {emp.anos_ciclo[0]}-{emp.anos_ciclo[-1]} sem janela_razao (§11.4)")
    if emp.defasagem_meses is not None and not emp.defasagem_fonte.strip():
        faltas.append(f"defasagem_meses={emp.defasagem_meses} sem defasagem_fonte (§6.3)")
    if faltas:
        raise ValueError(f"{emp.ticker}: " + " · ".join(faltas))


def v(d, k, default=None):
    x = d.get(k)
    return default if x is None else x


def serie(tk):
    return CVM[tk]["anual"], CVM[tk]["ltm_2T26"]


def anos_validos(tk, anos):
    a, _ = serie(tk)
    return [x for x in anos if a.get(x, {}).get("receita")]


def divida_liquida(b):
    bruta = v(b, "emprest_cp", 0) + v(b, "emprest_lp", 0) + v(b, "arrendamento", 0)   # IFRS 16 é dívida
    caixa = v(b, "caixa", 0) + v(b, "aplic_cp", 0)
    return bruta, caixa, bruta - caixa


def capital_giro(b):
    return (v(b, "ac", 0) - v(b, "caixa", 0) - v(b, "aplic_cp", 0)) - (v(b, "pc", 0) - v(b, "emprest_cp", 0))


def capex_manutencao(tk, ano, anterior, ciclica=False):
    """Capex de manutenção = capex − (capital ÷ receita) × Δreceita REAL média de 5 anos; piso zero (doutrina §11.1).

    Adaptação declarada do método de Greenwald: o capital é imobilizado + intangível + biológico LÍQUIDOS do
    exercício (as mesmas contas que formam o capex), não o PPE bruto médio de 5 anos do original — a série da CVM
    só traz o líquido (conta 1.02.03).
    Δreceita REAL (Etapa 2/F2): a receita antiga entra a preços do exercício corrente antes da subtração. Sem isso,
    em economia inflacionária a inflação viraria "crescimento" e reduziria o capex de manutenção. Não é exigência
    de Greenwald (que não trata inflação) — é coerência com a própria §11.1, que já manda preço de commodity e EPV
    em R$ de hoje. Tudo fica em R$ do exercício, então `cap_rec` (razão do mesmo ano) e o capex seguem compatíveis.
    """
    a, _ = serie(tk)
    d = a[ano]
    if ciclica:
        # commodity: a receita cresce por preço, não por capacidade — todo o capex é manutenção (sem projeto comprovado)
        return (d["capex"], 0.0) if d.get("capex") is not None else (None, None)
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
    return max(d["capex"] - cresc, 0.0), cresc


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


def owner_earnings_ano(emp: Industrial, ano, anterior, kd_real, ciclica=False):
    a, _ = serie(emp.ticker)
    d, p = a[ano], a.get(anterior, {})
    cm, _ = capex_manutencao(emp.ticker, ano, anterior, ciclica)
    if cm is None or d.get("lucro") is None or d.get("da") is None or not p:
        return None
    dwc = capital_giro(d) - capital_giro(p)
    # IFRS 16: a D&A somada de volta inclui a depreciação do direito de uso, então o aluguel pago é custo do negócio e sai
    return d["lucro"] + d["da"] - cm - max(dwc, 0) - aluguel_principal(emp, ano, anterior, kd_real)


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
    f = 1 devolve a margem original. Ano sem fator falha alto (nada silencioso)."""
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
    extra = [] if abs(ltm["receita"] - a[ult[-1]]["receita"]) < 1 else [ltm["receita"]]   # SMTO3: LTM = último exercício
    rec = emp.receita_meio or (rec_real if emp.deflator else
                               (sum(a[x]["receita"] for x in ult) + sum(extra)) / (len(ult) + len(extra)))
    # Greenwald: lucro sustentável = EBIT + D&A − capex de manutenção. Só penaliza (min 0): D&A acima do capex de
    # manutenção pode ser subinvestimento temporário. Mediana dos 5 últimos exercícios, em % da receita.
    if ciclico(emp):
        # commodity: receita cresce por preço; projetos de expansão (Cerrado, Puma II, Gaia) não identificados um a um →
        # capex de manutenção = mediana de 10 anos de capex/receita (dilui os picos de projeto) contra a mediana de D&A/receita
        cx = [a[x]["capex"] / a[x]["receita"] for x in anos if a[x].get("capex") is not None]
        dd = ([emp.da_receita] if emp.da_receita is not None else
              [a[x]["da"] / a[x]["receita"] for x in anos if a[x].get("da") is not None])
        aj = min(0.0, median(dd) - median(cx)) if cx and dd else 0.0
    else:
        ajs = []
        for i in range(max(1, len(anos) - 5), len(anos)):
            cm, _ = capex_manutencao(emp.ticker, anos[i], anos[i - 1])
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


def aliquota(emp: Industrial):
    if emp.aliquota is not None:
        return emp.aliquota
    a, _ = serie(emp.ticker)
    tx = [-a[x]["ir"] / a[x]["lair"] for x in anos_validos(emp.ticker, emp.anos_ciclo)[-5:]
          if a[x].get("lair") and a[x]["lair"] > 0 and a[x].get("ir") is not None]
    tx = [x for x in tx if 0 <= x <= 0.5]       # anos com crédito fiscal (alíquota negativa) não representam o normal
    return min(max(median(tx), 0.15), 0.34) if tx else 0.34


def wacc(emp: Industrial, mk: Mercado, ke_nom=None):
    _, ltm = serie(emp.ticker)
    bruta, caixa, dl = divida_liquida(ltm)
    e = emp.preco * emp.n_acoes / 1000      # R$ mil
    d = bruta
    ke = ke_nom if ke_nom is not None else mk.ke_nom
    kd = mk.rf_nom + emp.spread_kd
    w = ke * e / (e + d) + kd * (1 - aliquota(emp)) * d / (e + d)
    return w, kd, e, d


def valores(emp: Industrial, mk: Mercado, ke_nom=None, margem=None, g_real=None, g1=None):
    """Âncoras ao Ke dado. Retorna dict de valores por ação e insumos. g1 sobrepõe emp.g1_real (DCF reverso de 2 estágios)."""
    a, ltm = serie(emp.ticker)
    op = premissas_operacionais(emp)
    w_nom, kd, e, d = wacc(emp, mk, ke_nom)
    w_real = (1 + w_nom) / (1 + mk.pi) - 1
    ke = ke_nom if ke_nom is not None else mk.ke_nom
    ke_real = (1 + ke) / (1 + mk.pi) - 1
    bruta, caixa, dl = divida_liquida(ltm)
    minor = v(ltm, "nao_controladores", 0) + emp.outros_passivos   # direitos à frente do acionista na ponte firma → equity
    n = emp.n_acoes / 1000     # mil ações → valores em R$ mil / mil ações = R$/ação
    m = margem if margem is not None else op["m50"]
    gr = emp.g_real if g_real is None else g_real
    t_ef = aliquota(emp)
    nopat = op["receita_meio"] * (m + op["ajuste_manut"]) * (1 - t_ef)
    cap_inv = v(ltm, "pl", 0) + dl
    idade_imob, cap_rep = capital_reposicao(emp.ticker, cap_inv)
    roic = nopat / cap_inv if cap_inv > 0 else None
    # capital contábil negativo corrigido pela inflação pode virar positivo minúsculo e explodir o ROIC a reposição:
    # sem capital contábil positivo não há ROIC nenhum (achado do adversário em 05/10/2026)
    roic_rep = nopat / cap_rep if (cap_inv > 0 and cap_rep > 0) else None
    # doutrina §2: o filtro 1, a nota de qualidade e a trava do crescimento usam o MENOR dos dois (conservador)
    roic_filtro = min(x for x in (roic, roic_rep) if x is not None) if roic is not None else None
    roic_real = (1 + roic) / (1 + mk.pi) - 1 if roic else None

    epv_firma = nopat / w_real
    epv = (epv_firma - dl - minor) / n

    g1_ = emp.g1_real if g1 is None else g1

    def dcf(mg):
        nop = op["receita_meio"] * (mg + op["ajuste_manut"]) * (1 - t_ef)
        roic_c = nop / cap_inv if cap_inv > 0 else None
        # Greenwald: crescimento só tem valor se o ROIC supera o custo de capital (os dois nominais, doutrina §2).
        # Abaixo disso g = 0 e o DCF converge para o EPV; acima, reinvestimento = g real ÷ ROIC.
        # Etapa 2/F2: a trava usa o MENOR dos dois ROIC — crescer exige retorno acima do WACC sobre o capital a
        # preços de hoje, que é o que a empresa terá de repor. O reinvestimento segue pelo ROIC contábil (é o
        # capital que ela de fato emprega). A trava é avaliada POR CENÁRIO, então o efeito é gradual.
        roic_rep_c = nop / cap_rep if cap_rep > 0 else None
        cria = roic_c is not None and min(roic_c, roic_rep_c if roic_rep_c is not None else roic_c) > w_nom
        g_ef = gr if (gr <= 0 or cria) else 0.0   # só zera crescimento positivo
        # reinvestimento = g REAL ÷ ROIC REAL (Fisher) — real com real (doutrina §4); até 05/10 dividia pelo ROIC nominal (adversário do Lote 4)
        roic_r = (1 + roic_c) / (1 + mk.pi) - 1 if roic_c is not None else None
        reinv = g_ef / roic_r if (g_ef != 0 and roic_r and not (g_ef < 0 and emp.declinio_sem_liberacao)) else 0.0
        if g1_ is None:
            fcff1 = nop * (1 + g_ef) * (1 - reinv)
            return (fcff1 / (w_real - g_ef) - dl - minor) / n
        # 2 estágios (compounder): NOPAT cresce g1 real por anos_g1 anos reinvestindo g1 ÷ ROIC; depois, Gordon com g_ef
        g1e = g1_ if cria else 0.0
        vp, nop_t = 0.0, nop
        for t in range(1, emp.anos_g1 + 1):
            nop_t *= 1 + g1e
            vp += nop_t * (1 - (g1e / roic_r if g1e > 0 else 0.0)) / (1 + w_real) ** t
        terminal = nop_t * (1 + g_ef) * (1 - reinv) / (w_real - g_ef)
        return (vp + terminal / (1 + w_real) ** emp.anos_g1 - dl - minor) / n
    dcf_c = {"pessimista": dcf(op["m25"]), "base": dcf(m), "otimista": dcf(op["m75"])}
    dcf_pond = 0.25 * dcf_c["pessimista"] + 0.5 * dcf_c["base"] + 0.25 * dcf_c["otimista"]

    oes = []
    anos = op["anos"]
    for i in range(1, len(anos)):
        x = owner_earnings_ano(emp, anos[i], anos[i - 1], (1 + kd) / (1 + mk.pi) - 1, ciclico(emp))
        if x is not None:
            oes.append((anos[i], x))
    oe_recentes = [x for _, x in oes[-5:]]
    oe_norm = median(oe_recentes) if oe_recentes else None
    oe_val = (oe_norm / (ke_real - gr) - emp.outros_passivos) / n if oe_norm and ke_real > gr else None

    reprod = emp.reproducao_por_acao if emp.reproducao_por_acao else (v(ltm, "pl", 0) - v(ltm, "nao_controladores", 0)) / n

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
    return dict(anc=anc, op=op, wacc=w_nom, wacc_real=w_real, kd=kd, e=e, d=d, dl=dl, bruta=bruta, caixa=caixa,
                minor=minor, nopat=nopat, roic=roic, epv=epv, dcf=dcf_c, dcf_pond=dcf_pond, oe=oes, oe_norm=oe_norm,
                oe_val=oe_val, reprod=reprod, cap_inv=cap_inv, n=n, m=m, gr=gr, aliquota=t_ef,
                roic_reposicao=roic_rep, roic_filtro=roic_filtro, cap_inv_reposicao=cap_rep, idade_imobilizado=idade_imob)


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
    return median(vals), vals


def ke_implicito(emp, mk):
    lo, hi = mk.g_teto + 0.003, 0.60
    f = lambda k: central_de(valores(emp, mk, ke_nom=k)["anc"])[0]
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


def g_implicito(emp, mk):
    """DCF reverso: crescimento real perpétuo que iguala o DCF base ao preço (margem mediana, Ke da casa).
    Com DCF de 2 estágios: o g real dos primeiros anos_g1 anos (perpetuidade fixa)."""
    if emp.g1_real is not None:
        lo, hi = 0.0, 0.40
        f = lambda g: valores(emp, mk, g1=g)["dcf"]["base"]
        if f(hi) < emp.preco:
            return None
        if f(lo) > emp.preco:
            return lo - 1e-9
        for _ in range(70):
            mid = (lo + hi) / 2
            lo, hi = (lo, mid) if f(mid) > emp.preco else (mid, hi)
        return (lo + hi) / 2
    lo, hi = -0.05, min(0.08, valores(emp, mk)["wacc_real"] - 0.002)
    f = lambda g: valores(emp, mk, g_real=g)["dcf"]["base"]
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


def avaliar(emp: Industrial, mk: Mercado) -> dict:
    exigir_declaracoes(emp)
    a, ltm = serie(emp.ticker)
    r = valores(emp, mk)
    anc = dict(r["anc"])
    dc = emp.desconto_controlador
    desc = (dc.get("pct", 0.0) if dc["tipo"] == "fixo" else
            sum(c["prob"] * c["perda"] for c in dc["cenarios"]) if dc["tipo"] == "cenarios" else 0.0)
    anc = {k: x * (1 - desc) for k, x in anc.items()}
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
    vpa = (v(ltm, "pl", 0) - v(ltm, "nao_controladores", 0)) / n
    graham_orig = math.sqrt(22.5 * lpa_norm * vpa) if lpa_norm > 0 and vpa > 0 else None
    graham_br = math.sqrt(22.5 * mk.fator_graham * lpa_norm * vpa) if lpa_norm > 0 and vpa > 0 else None
    g_real_pct = 100 * r["gr"]
    graham_rev = lpa_norm * (8.5 + 2 * g_real_pct) * mk.fator_graham if lpa_norm > 0 else None

    dpa = SI[emp.ticker]["dpa_por_ano_datacom"]
    dpa5 = sum(dpa.get(str(x), 0) for x in range(2021, 2026)) / 5
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
    trava = abs(bogle_nom - mk.ke_nom) <= 0.02 if p0 == "JUSTA" else None

    peg = (pl_atual / (100 * g_nom)) if pl_atual else None
    pegy = (pl_atual / (100 * (g_nom + dy))) if pl_atual else None

    # sensibilidade: WACC via Ke ±1 p.p. × margem ±2 p.p.
    sens = {}
    for dk in (-0.01, 0, 0.01):
        for dm in (-0.02, 0, 0.02):
            vv = valores(emp, mk, ke_nom=mk.ke_nom + dk, margem=r["m"] + dm)["anc"]
            sens[(dk, dm)] = central_de({k: x * (1 - desc) for k, x in vv.items()})[0]

    # notas — o spread usa o MENOR dos dois ROIC (doutrina §2: capital a custo histórico infla o retorno)
    q = emp.qualitativo
    qual = sum(q.values()) / len(q) * 2 if q else 5
    n_qual = 0.5 * nota_spread(r["roic_filtro"] or 0, r["wacc"]) + 0.5 * qual
    alav_n = interp(-(dl_ebitda_norm if dl_ebitda_norm is not None else 0), [(-5, 1), (-4, 3), (-3, 5), (-2, 7), (-1, 9), (0, 10)])
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
    por_qualidade = (len(serie_roic) >= JANELA_MINIMA_SAIDA and anos_roic >= ANOS_ROIC_MINIMO
                     and n_qual >= NOTA_QUALIDADE_MINIMA)
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
                ke_implicito=ke_implicito(emp, mk), g_implicito=g_implicito(emp, mk), sens=sens,
                notas=dict(qualidade=n_qual, solidez=n_sol, renda=n_renda, preco=n_preco, geral=n_geral),
                ret_investimento=dy + g_nom, ret_especulativo=dmult, ticker=emp.ticker)
