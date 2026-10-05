"""Motor de valuation para financeiras (bancos, seguradoras, holdings de seguro) — doutrina v2.0.

Toda conta da ficha sai daqui; o PDF só formata. Fórmulas = 01-doutrina-value-investing.md §4, §6, §9–§11.
Convenção: taxas em fração (0.12 = 12%), valores em R$ por ação.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from statistics import median

PIB_REAL_LP = 0.02          # crescimento real de longo prazo da economia (teto do g perpétuo), declarado
PREMIO_KE = 0.05            # Ke real = rf + 5 p.p.
IR_RESGATE = 0.15           # Tesouro e ganho de capital, > 720 dias
IR_JCP = 0.175              # LC 224/2025
HORIZONTE = 10              # anos, comparação com RF e Bogle


# ---------------------------------------------------------------- mercado
@dataclass
class Mercado:
    rf_real: float              # Tesouro IPCA+ sem cupom mais longo, fechamento
    pi: float                   # inflação implícita
    data: str = ""

    @property
    def ke_real(self): return self.rf_real + PREMIO_KE

    @property
    def ke_nom(self): return (1 + self.ke_real) * (1 + self.pi) - 1

    @property
    def rf_nom(self): return (1 + self.rf_real) * (1 + self.pi) - 1

    @property
    def rf_liq_nom(self):
        return liquido_diferido(self.rf_nom)

    @property
    def rf_liq_real(self): return (1 + self.rf_liq_nom) / (1 + self.pi) - 1

    @property
    def g_teto(self): return (1 + self.pi) * (1 + PIB_REAL_LP) - 1

    @property
    def fator_graham(self): return (1 / self.ke_real) / 8.5


def liquido_diferido(taxa_nom: float, anos: int = HORIZONTE, ir: float = IR_RESGATE) -> float:
    """Taxa anual equivalente líquida quando o IR incide só no resgate."""
    if taxa_nom <= 0:
        return taxa_nom
    bruto = (1 + taxa_nom) ** anos
    return ((bruto - 1) * (1 - ir) + 1) ** (1 / anos) - 1


# ---------------------------------------------------------------- régua e notas
def palavra(pc: float) -> str:
    if pc <= 0.70: return "BARATA"
    if pc <= 0.90: return "RADAR"
    if pc <= 1.10: return "JUSTA"
    return "CARA"


ORDEM = ["BARATA", "RADAR", "JUSTA", "CARA"]

ESCALA_PRECO = [(0.60, 10), (0.65, 9), (0.70, 8), (0.80, 7), (0.90, 6), (1.00, 5),
                (1.10, 4), (1.20, 3), (1.30, 2), (1.40, 1), (1.50, 0)]


def interp(x, pontos):
    """Interpolação linear em lista [(x, y)] ordenada por x; satura nas pontas."""
    if x <= pontos[0][0]: return pontos[0][1]
    if x >= pontos[-1][0]: return pontos[-1][1]
    for (x0, y0), (x1, y1) in zip(pontos, pontos[1:]):
        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)
    return pontos[-1][1]


def nota_preco(pc): return interp(pc, ESCALA_PRECO)


# Rubricas declaradas no apêndice do PDF
def nota_spread(roe_lp, ke_nom):      # qualidade: ROE de longo prazo − Ke nominal (p.p.)
    return interp((roe_lp - ke_nom) * 100, [(-6, 1), (-3, 3), (0, 5), (2, 6), (5, 8), (8, 10)])


def nota_cet1(x):      return interp(x, [(9, 2), (10, 4), (11, 6), (12, 8), (13, 10)])
def nota_inad(x):      return interp(-x, [(-7, 2), (-5, 4), (-4, 6), (-3, 8), (-2, 10)])
def nota_cob(x):       return interp(x, [(100, 3), (150, 6), (200, 8), (250, 10)])
def nota_yield(r):     return interp(r, [(0.3, 1), (0.5, 3), (0.7, 5), (0.9, 7), (1.0, 8), (1.2, 10)])


# ---------------------------------------------------------------- empresa
@dataclass
class Financeira:
    ticker: str
    nome: str
    perfil: str                       # banco | seguradora | holding_seguro
    preco: float
    vpa: float
    lpa_12m: float
    roe_lp: float                     # ROE de longo prazo (normalizado), fração
    roe_inicio: float                 # ROE esperado no ano 1 (guidance/consenso/atual)
    payout: float                     # payout de longo prazo
    dpa_medio_5a: float               # DPA médio 5 anos ajustado, R$
    jcp_share: float = 0.5            # fração dos proventos paga como JCP
    pl_hist: float | None = None      # P/L médio histórico (10a ou o máximo disponível), para Bogle
    desconto_controlador: dict = field(default_factory=lambda: {"tipo": "zero", "razao": ""})
    horizonte_finito: dict | None = None   # seguradora com contrato: {"anos": n, "prob_renovacao": p, "haircut_renov": h}
    prudencial: dict = field(default_factory=dict)   # cet1, inad90, cobertura
    qualitativo: dict = field(default_factory=dict)  # notas 0–5: moat, gestao, controlador, ciclo, fisher
    cobertura_caixa: bool = True
    anos_pagos_10: int = 10
    solidez_manual: float | None = None   # quando o prudencial não se aplica (seguradoras), com razão no texto
    fora_circulo: bool = False


def g_de(emp: Financeira, mk: Mercado, roe: float) -> float:
    """g perpétuo nominal = ROE × retenção (doutrina §11), com teto π + PIB real de LP."""
    return min(roe * (1 - emp.payout), mk.g_teto)


def g_perpetuo(emp: Financeira, mk: Mercado) -> float:
    return g_de(emp, mk, emp.roe_lp)


def pvp_justificado(roe, g, ke):
    return (roe - g) / (ke - g)


def ddm_dois_estagios(emp: Financeira, mk: Mercado, roe_lp: float, anos: int = 5):
    """Dividendos explícitos com ROE convergindo linearmente de roe_inicio a roe_lp; terminal = P/VP justificado."""
    ke = mk.ke_nom
    g = g_de(emp, mk, roe_lp)
    vpa, vp, fluxo = emp.vpa, 0.0, []
    for t in range(1, anos + 1):
        roe_t = emp.roe_inicio + (roe_lp - emp.roe_inicio) * t / anos
        lpa = roe_t * vpa
        d = lpa * emp.payout
        vpa = vpa + lpa - d
        vp += d / (1 + ke) ** t
        fluxo.append((t, roe_t, lpa, d, vpa))
    terminal = vpa * pvp_justificado(roe_lp, g, ke)
    vp += terminal / (1 + ke) ** anos
    return vp, fluxo, terminal


def ddm_contrato_finito(emp: Financeira, mk: Mercado, roe_lp: float):
    """Seguradora cujo lucro depende de contrato com o controlador: fluxo explícito até o fim do contrato,
    depois perpetuidade ponderada pela probabilidade de renovação e pelo haircut de margem na renovação."""
    hf = emp.horizonte_finito
    assert hf is not None
    ke = mk.ke_nom
    n = hf["anos"]
    g = g_de(emp, mk, roe_lp)
    vpa, vp = emp.vpa, 0.0
    lpa = None
    for t in range(1, n + 1):
        frac = min(t / 5, 1.0)
        roe_t = emp.roe_inicio + (roe_lp - emp.roe_inicio) * frac
        lpa = roe_t * vpa
        d = lpa * emp.payout
        vpa = vpa + lpa - d
        vp += d / (1 + ke) ** t
    lpa_pos = lpa * (1 - hf["haircut_renov"])
    d_pos = lpa_pos * emp.payout
    terminal_renov = d_pos * (1 + g) / (ke - g)
    terminal = hf["prob_renovacao"] * terminal_renov + (1 - hf["prob_renovacao"]) * vpa  # sem renovação: devolve o PL
    vp += terminal / (1 + ke) ** n
    return vp


def ancoras(emp: Financeira, mk: Mercado, roe_lp: float) -> dict:
    ke = mk.ke_nom
    g = g_de(emp, mk, roe_lp)
    out = {}
    if emp.horizonte_finito:
        out["DDM até o fim do contrato"] = ddm_contrato_finito(emp, mk, roe_lp)
    else:
        out["P/VP justificado"] = emp.vpa * pvp_justificado(roe_lp, g, ke)
        out["DDM 2 estágios"] = ddm_dois_estagios(emp, mk, roe_lp)[0]
    return out


def projecao(emp: Financeira, anos: int = 3):
    """Lucro projetado próprio: ROE convergindo linearmente de roe_inicio ao roe_lp em 5 anos, sobre o VPA que cresce
    pela retenção. Devolve [(ano, ROE, LPA, DPA, VPA)]."""
    vpa, out = emp.vpa, []
    for t in range(1, anos + 1):
        roe_t = emp.roe_inicio + (emp.roe_lp - emp.roe_inicio) * min(t / 5, 1)
        lpa = roe_t * vpa
        d = lpa * emp.payout
        vpa = vpa + lpa - d
        out.append((t, roe_t, lpa, d, vpa))
    return out


def central_ao_ke(emp: Financeira, mk: Mercado, ke_nom: float) -> float:
    """Valor central (com o desconto de controlador) recalculado a um Ke nominal dado."""
    rf = (1 + ke_nom) / (1 + mk.pi) - 1 - PREMIO_KE
    mk2 = Mercado(rf, mk.pi)
    a = ancoras(emp, mk2, emp.roe_lp)
    dc = emp.desconto_controlador
    if dc["tipo"] == "cenarios":
        ai = ancoras(emp, mk2, emp.roe_lp - dc["delta_roe"])
        a = {k: (1 - dc["peso"]) * a[k] + dc["peso"] * ai[k] for k in a}
    elif dc["tipo"] == "fixo":
        a = {k: v * (1 - dc["pct"]) for k, v in a.items()}
    return median(list(a.values()))


def ke_implicito(emp: Financeira, mk: Mercado) -> float | None:
    """Ke nominal que o preço atual embute (mesmo modelo, mesmo ROE): o retorno que o mercado aceita."""
    lo = g_perpetuo(emp, mk) + 0.002     # piso: o g da própria empresa (o teto deixava TIR baixa sem número)
    hi = 0.60
    try:
        if central_ao_ke(emp, mk, lo) < emp.preco:
            return None            # nem no Ke mínimo o modelo alcança o preço
        for _ in range(80):
            mid = (lo + hi) / 2
            if central_ao_ke(emp, mk, mid) > emp.preco:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    except ZeroDivisionError:
        return None


def avaliar(emp: Financeira, mk: Mercado) -> dict:
    ke, pi = mk.ke_nom, mk.pi
    g = g_perpetuo(emp, mk)
    base = ancoras(emp, mk, emp.roe_lp)

    # desconto de controlador — uma única vez, no valor
    dc = emp.desconto_controlador
    if dc["tipo"] == "cenarios":
        inter = ancoras(emp, mk, emp.roe_lp - dc["delta_roe"])
        anc = {k: (1 - dc["peso"]) * base[k] + dc["peso"] * inter[k] for k in base}
        desc_pct = 1 - sum(anc.values()) / sum(base.values())
    elif dc["tipo"] == "fixo":
        anc = {k: v * (1 - dc["pct"]) for k, v in base.items()}
        desc_pct = dc["pct"]
    else:
        anc, desc_pct = dict(base), 0.0

    vals = list(anc.values())
    nao_conclusivo = any(v <= 0 for v in vals)
    central = median(vals)
    dispersao = max(vals) / min(vals) if not nao_conclusivo else float("inf")
    pc = emp.preco / central

    # palavra com precedência: régua → círculo → dispersão → (carimbos no texto)
    p0 = palavra(pc)
    p = p0
    if emp.fora_circulo and ORDEM.index(p) < ORDEM.index("RADAR"):
        p = "RADAR"
    confianca = "normal"
    if len(vals) == 1:
        confianca = "baixa (âncora única)"
    if nao_conclusivo or dispersao > 3:
        p, confianca = "NÃO CONCLUSIVO", "não conclusivo"
    elif dispersao > 1.8:
        confianca = "baixa"
        if p in ("BARATA", "RADAR"):
            p = ORDEM[ORDEM.index(p) + 1]

    # informativos
    lpa_norm = emp.roe_lp * emp.vpa
    graham_orig = math.sqrt(22.5 * lpa_norm * emp.vpa) if lpa_norm > 0 else None
    graham_br = math.sqrt(22.5 * mk.fator_graham * lpa_norm * emp.vpa) if lpa_norm > 0 else None
    if emp.perfil == "holding_seguro":       # capital-leve: o FCFE é o lucro; o limite é a política de payout
        dpa_fcfe = lpa_norm * emp.payout
    else:                                    # banco: precisa reter g/ROE do lucro para crescer o capital
        dpa_fcfe = lpa_norm * (1 - g / emp.roe_lp) if emp.roe_lp > 0 else 0
    dpa_sust = min(emp.dpa_medio_5a, dpa_fcfe)
    dpa_sust_liq = dpa_sust * (1 - emp.jcp_share * IR_JCP)
    teto_renda = dpa_sust_liq / mk.rf_liq_nom if emp.cobertura_caixa else None
    bazin6 = dpa_sust / 0.06

    # Bogle (10 anos) sobre LPA normalizado
    dy = dpa_sust / emp.preco
    pl_atual = emp.preco / lpa_norm
    pl_final = emp.pl_hist if emp.pl_hist else None
    dmult = (pl_final / pl_atual) ** (1 / HORIZONTE) - 1 if pl_final else 0.0
    bogle_nom = dy + g + dmult
    gc = g + dmult
    dy_liq = dy * (1 - emp.jcp_share * IR_JCP)
    bogle_liq_nom = dy_liq + liquido_diferido(gc) if gc > 0 else dy_liq + gc
    bogle_liq_real = (1 + bogle_liq_nom) / (1 + pi) - 1
    bogle_real = (1 + bogle_nom) / (1 + pi) - 1

    if bogle_liq_real >= mk.rf_liq_real + 0.03: rf = "Sim"
    elif bogle_liq_real >= mk.rf_liq_real + 0.015: rf = "Empate"
    else: rf = "Não"
    carimbo_rf = bogle_liq_real < mk.rf_liq_real

    # mesma conta sem re-rating de múltiplo: só o retorno de investimento
    so_inv_liq_real = (1 + dy_liq + (liquido_diferido(g) if g > 0 else g)) / (1 + pi) - 1
    if so_inv_liq_real >= mk.rf_liq_real + 0.03: rf_inv = "Sim"
    elif so_inv_liq_real >= mk.rf_liq_real + 0.015: rf_inv = "Empate"
    else: rf_inv = "Não"
    so_com_rerating = rf != rf_inv

    trava = None
    if p0 == "JUSTA":
        trava = abs(bogle_nom - ke) <= 0.02

    roe_implicito = emp.roe_lp                               # DCF reverso: r = g(r) + P/VP × (Ke − g(r))
    for _ in range(200):
        g_r = g_de(emp, mk, roe_implicito)
        roe_implicito = g_r + (emp.preco / emp.vpa) * (ke - g_r)

    # sensibilidade do central: Ke ±1 p.p. e ROE_lp ±2 p.p.
    def central_com(ke_shift=0.0, roe_shift=0.0):
        mk2 = Mercado(mk.rf_real + ke_shift, mk.pi)
        a = ancoras(emp, mk2, emp.roe_lp + roe_shift)
        if dc["tipo"] == "cenarios":
            ai = ancoras(emp, mk2, emp.roe_lp + roe_shift - dc["delta_roe"])
            a = {k: (1 - dc["peso"]) * a[k] + dc["peso"] * ai[k] for k in a}
        elif dc["tipo"] == "fixo":
            a = {k: v * (1 - dc["pct"]) for k, v in a.items()}
        return median(list(a.values()))
    sens = {(dk, dr): central_com(dk, dr) for dk in (-0.01, 0, 0.01) for dr in (-0.02, 0, 0.02)}

    # notas
    q = emp.qualitativo
    qual_media = sum(q.values()) / len(q) * 2 if q else 5
    n_qual = 0.5 * nota_spread(emp.roe_lp, ke) + 0.5 * qual_media
    pr = emp.prudencial
    if emp.solidez_manual is not None:
        n_sol = emp.solidez_manual
    else:
        partes = [f(pr[k]) for k, f in (("cet1", nota_cet1), ("inad90", nota_inad), ("cobertura", nota_cob)) if pr.get(k) is not None]
        n_sol = sum(partes) / len(partes) if partes else 5
    n_renda = (0.5 * nota_yield(dy_liq / mk.rf_liq_nom) + 0.25 * (10 if emp.cobertura_caixa else 2)
               + 0.25 * emp.anos_pagos_10)
    n_preco = nota_preco(pc)
    n_geral = 0.30 * n_qual + 0.20 * n_sol + 0.25 * n_renda + 0.25 * n_preco

    fluxo = None
    if not emp.horizonte_finito:
        fluxo = ddm_dois_estagios(emp, mk, emp.roe_lp)[1]

    return dict(
        ke_implicito=ke_implicito(emp, mk), ret_investimento=dy + g, ret_especulativo=dmult,
        rf_sem_rerating=rf_inv, so_inv_liq_real=so_inv_liq_real, so_com_rerating=so_com_rerating,
        pvp_perpetuo=emp.vpa * pvp_justificado(emp.roe_lp, g, ke) if emp.horizonte_finito else None,
        ticker=emp.ticker, ke=ke, g=g, base=base, ancoras=anc, desc_controlador=desc_pct,
        central=central, dispersao=dispersao, confianca=confianca, pc=pc, palavra_regua=p0, palavra=p,
        compra=0.70 * central, saida=1.30 * central, compra_parcial=0.80 * central,
        lpa_norm=lpa_norm, graham_orig=graham_orig, graham_br=graham_br, dpa_sust=dpa_sust,
        dpa_fcfe=dpa_fcfe, dpa_sust_liq=dpa_sust_liq, teto_renda=teto_renda, bazin6=bazin6,
        dy=dy, dy_liq=dy_liq, pl_atual=pl_atual, pl_final=pl_final, dmult=dmult,
        bogle_nom=bogle_nom, bogle_real=bogle_real, bogle_liq_real=bogle_liq_real,
        vence_rf=rf, carimbo_rf=carimbo_rf, trava=trava, roe_implicito=roe_implicito,
        pvp=emp.preco / emp.vpa, pvp_just=pvp_justificado(emp.roe_lp, g, ke), sens=sens,
        notas=dict(qualidade=n_qual, solidez=n_sol, renda=n_renda, preco=n_preco, geral=n_geral),
        fluxo_ddm=fluxo,
    )
