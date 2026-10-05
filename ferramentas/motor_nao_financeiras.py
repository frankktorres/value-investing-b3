"""Motor de valuation para empresas não financeiras (industrial, serviços, cíclica/commodity) — doutrina v2.0 §11.

Fonte dos números: dados/cvm_series.json (DFP/ITR da CVM, R$ mil) + preço/ações/proventos da StatusInvest.
Tudo em R$ por ação no fim. Convenção: taxas em fração.
"""
from __future__ import annotations

import json
import math
import pathlib
from dataclasses import dataclass, field
from statistics import median

from motor_financeiras import (HORIZONTE, IR_JCP, ORDEM, Mercado, interp, liquido_diferido, nota_preco, nota_spread,
                               nota_yield, palavra)

AQUI = pathlib.Path(__file__).parent
CVM = json.loads((AQUI / "dados" / "cvm_series.json").read_text(encoding="utf-8"))
SI = json.loads(sorted((AQUI / "dados").glob("series_*.json"))[-1].read_text(encoding="utf-8"))
ANOS = [str(a) for a in range(2016, 2026)]


@dataclass
class Industrial:
    ticker: str
    nome: str
    perfil: str                    # ciclica | servicos
    preco: float
    n_acoes: float                 # ações (ou units) em circulação
    anos_ciclo: list = field(default_factory=lambda: ANOS)   # janela da margem normalizada
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
    defasagem_meses: float = 0.0          # provento pago N meses depois da data-com: trazido a valor presente ao Ke nominal (doutrina §6.3)


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
    """Greenwald (doutrina §11.1): capex − (capital ÷ receita) × Δreceita média de 5 anos; piso zero.
    Capital = imobilizado + intangível + ativo biológico (as mesmas contas que formam o capex)."""
    a, _ = serie(tk)
    d = a[ano]
    if ciclica:
        # commodity: a receita cresce por preço, não por capacidade — todo o capex é manutenção (sem projeto comprovado)
        return (d["capex"], 0.0) if d.get("capex") is not None else (None, None)
    base = str(int(ano) - 5)
    if d.get("capex") is None or not a.get(base, {}).get("receita"):
        p = a.get(anterior, {})
        if not p.get("receita"):
            return None, None
        delta = d["receita"] - p["receita"]
    else:
        delta = (d["receita"] - a[base]["receita"]) / 5
    if d.get("capex") is None:
        return None, None
    cap_rec = (v(d, "imobilizado", 0) + v(d, "intangivel", 0) + v(d, "biologico", 0)) / d["receita"]
    cresc = cap_rec * max(delta, 0)
    return max(d["capex"] - cresc, 0.0), cresc


def owner_earnings_ano(tk, ano, anterior, ciclica=False):
    a, _ = serie(tk)
    d, p = a[ano], a.get(anterior, {})
    cm, _ = capex_manutencao(tk, ano, anterior, ciclica)
    if cm is None or d.get("lucro") is None or d.get("da") is None or not p:
        return None
    dwc = capital_giro(d) - capital_giro(p)
    # IFRS 16: a D&A somada de volta inclui a depreciação do direito de uso; o aluguel pago (amortização do passivo de arrendamento,
    # DFC de financiamento) é custo do negócio e sai (05/10). Série coletada antes de 05/10 não tem o campo → 0 (sem mudança)
    return d["lucro"] + d["da"] - cm - max(dwc, 0) - v(d, "arrendamento_pago", 0)


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


def premissas_operacionais(emp: Industrial):
    a, ltm = serie(emp.ticker)
    anos = anos_validos(emp.ticker, emp.anos_ciclo)
    liq = emp.outras_liquidas
    mo = mediana_outras(emp.ticker, emp.anos_outras or anos, liq)
    if emp.deflator:
        # receita indexada a preço de commodity (distribuição): a margem % cai quando o combustível sobe e o EBIT por volume
        # não muda — normaliza-se o EBIT em R$ de hoje (IPCA), expresso sobre a receita real média do período
        rec_real = sum(a[x]["receita"] * emp.deflator[x] for x in anos) / len(anos)
        margens = sorted(ebit_aj(a[x], mo, liq) * emp.deflator[x] / rec_real for x in anos)
    elif emp.da_receita is not None:
        # E&P: o preço do barril move a margem EBITDA; a D&A (exaustão das reservas, inclusive as compradas) segue o portfólio atual
        # impairment sai do EBITDA ano a ano (baixa de capital, não custo do ano), mas a perda MEDIANA de 10 anos fica como custo
        # recorrente — quem baixa ativo quase todo ano investe mal de forma habitual (só penaliza)
        imp_rec = max(0.0, median(-v(a[x], "impairment", 0) / a[x]["receita"] for x in anos))
        margens = sorted((ebit_aj(a[x], mo, liq) + v(a[x], "da", 0) - v(a[x], "impairment", 0)) / a[x]["receita"] - emp.da_receita - imp_rec
                         for x in anos)
    elif emp.impairment_normalizado:
        # baixa de ativo concentrada num ano (GGBR4 2025) não é custo daquele ano; a perda mediana de 10 anos fica como custo recorrente
        imp_rec = max(0.0, median(-v(a[x], "impairment", 0) / a[x]["receita"] for x in anos))
        margens = sorted((ebit_aj(a[x], mo, liq) - v(a[x], "impairment", 0)) / a[x]["receita"] - imp_rec for x in anos)
    else:
        margens = sorted(ebit_aj(a[x], mo, liq) / a[x]["receita"] for x in anos)
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
    return dict(margens=margens, m25=m25, m50=m50, m75=m75, receita_meio=rec, anos=anos, ajuste_manut=aj, med_outras=mo, nao_rec=nao_rec,
                impairment_recorrente=imp)


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
    roic = nopat / cap_inv if cap_inv > 0 else None
    roic_real = (1 + roic) / (1 + mk.pi) - 1 if roic else None

    epv_firma = nopat / w_real
    epv = (epv_firma - dl - minor) / n

    g1_ = emp.g1_real if g1 is None else g1

    def dcf(mg):
        nop = op["receita_meio"] * (mg + op["ajuste_manut"]) * (1 - t_ef)
        roic_c = nop / cap_inv if cap_inv > 0 else None
        # Greenwald: crescimento só tem valor se o ROIC supera o custo de capital (os dois nominais, doutrina §2).
        # Abaixo disso g = 0 e o DCF converge para o EPV; acima, reinvestimento = g real ÷ ROIC.
        cria = roic_c is not None and roic_c > w_nom
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
        x = owner_earnings_ano(emp.ticker, anos[i], anos[i - 1], ciclico(emp))
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
                oe_val=oe_val, reprod=reprod, cap_inv=cap_inv, n=n, m=m, gr=gr, aliquota=t_ef)


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
    juros = -v(ltm, "desp_fin", 0)
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
    fvp = (1 + mk.ke_nom) ** (-emp.defasagem_meses / 12)   # defasagem: provento a valor presente ao Ke nominal (§6.3)
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

    # notas
    q = emp.qualitativo
    qual = sum(q.values()) / len(q) * 2 if q else 5
    n_qual = 0.5 * nota_spread(r["roic"] or 0, r["wacc"]) + 0.5 * qual
    alav_n = interp(-(dl_ebitda_norm if dl_ebitda_norm is not None else 0), [(-5, 1), (-4, 3), (-3, 5), (-2, 7), (-1, 9), (0, 10)])
    z_n = {"segura": 10, "cinzenta": 6, "perigo": 2}[zona]
    cob_n = interp(cobertura or 0, [(1, 1), (2, 3), (3, 5), (5, 8), (8, 10)])
    n_sol = (alav_n + z_n + cob_n) / 3
    anos_pagos = emp.anos_pagos_10 if emp.anos_pagos_10 is not None else sum(1 for x in range(2016, 2026) if dpa.get(str(x), 0) > 0)
    n_renda = 0.5 * nota_yield(dy_liq / mk.rf_liq_nom) + 0.25 * (10 if coberto else 2) + 0.25 * anos_pagos
    n_preco = nota_preco(pc) if central > 0 else 0
    n_geral = 0.30 * n_qual + 0.20 * n_sol + 0.25 * n_renda + 0.25 * n_preco

    return dict(r, ancoras=anc, central=central, dispersao=disp, confianca=conf, pc=pc, palavra_regua=p0, palavra=p,
                compra=0.7 * central, saida=1.3 * central, compra_parcial=0.8 * central, desc_controlador=desc,
                ebitda_ltm=ebitda_ltm, ebitda_norm=ebitda_norm, dl_ebitda=dl_ebitda, dl_ebitda_norm=dl_ebitda_norm,
                cobertura_juros=cobertura, ey=ey, roc=roc, altman=z, altman_zona=zona, piotroski=pf, piotroski_crit=pf_crit,
                beneish=mb, sloan=sl, ano_qualidade=ult, lpa_norm=lpa_norm, vpa=vpa, graham_orig=graham_orig,
                graham_br=graham_br, graham_rev=graham_rev, dpa5=dpa5, fcfe_acao=fcfe_acao, dpa_sust=dpa_sust,
                coberto=coberto, dpa_sust_liq=dpa_sust_liq, teto_renda=teto, dpa_sust_vp=dpa_sust_vp, fator_defasagem=fvp, bazin6=bazin6, dy=dy, dy_liq=dy_liq,
                g_nom=g_nom, pl_atual=pl_atual, pl_final=pl_final, dmult=dmult, bogle_nom=bogle_nom,
                bogle_liq_real=bogle_liq_real, so_inv_liq_real=so_inv_liq_real, vence_rf=rf, rf_sem_rerating=rf_inv,
                so_com_rerating=rf != rf_inv, carimbo_rf=bogle_liq_real < mk.rf_liq_real, trava=trava, peg=peg, pegy=pegy,
                ke_implicito=ke_implicito(emp, mk), g_implicito=g_implicito(emp, mk), sens=sens,
                notas=dict(qualidade=n_qual, solidez=n_sol, renda=n_renda, preco=n_preco, geral=n_geral),
                ret_investimento=dy + g_nom, ret_especulativo=dmult, ticker=emp.ticker)
