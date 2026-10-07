"""Testes de qualidade Q1–Q5, NCAV e EY, sobre os `Insumos` do motor reduzido (ledger point-in-time).

Status de cada teste:
  ok      passou
  falha   reprovou
  indet   dado insuficiente — conta como reprovação no portão (sobrevivência vence retorno, §3)
  n/a     não se aplica por estrutura (financeira sem FCO/EBIT; Q4 sem lucro retido) — não conta

Portão: Q1 obrigatório e no máximo `max_reprovacoes_q2_q5` reprovações (falha ou indet) em Q2..Q5.
A régua é a do PLANO F4 ("Qualidade Buffett"); nada aqui é veredito.

Unidades: contas em R$ MIL (ledger); preço em R$ por papel; `i.papeis` em papéis.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from backtest.config import PADRAO as BT
from backtest.inflacao_pit import fator_mes
from backtest.motor import contas
from backtest.motor.base import Ano, Insumos, lucro_controlador, mediana
from backtest.motor.reduzido_nf import aliquota

from .config import PADRAO, ConfigTriagem

OK, FALHA, INDET, NA = "ok", "falha", "indet", "n/a"


@dataclass(frozen=True)
class Teste:
    status: str
    texto: str            # resumo curto que vai para o 06 ("7/10", "DL/EBITDA 1,8", ...)
    valor: float = math.nan

    @property
    def reprovou(self) -> bool:
        return self.status in (FALHA, INDET)


def br(x: float, nd: int = 2) -> str:
    """Número com vírgula decimal (texto do 06)."""
    return f"{x:.{nd}f}".replace(".", ",")


def precisa(n: int, frac: float) -> int:
    """Quantos de `n` exercícios a fração exige (7 de 10 -> 7; 7 de 7 a 0,70 -> 5)."""
    return math.ceil(frac * n - 1e-9)


def _num(d: dict, k: str) -> float | None:
    x = d.get(k)
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return float(x)


def inflacao_do_ano(ano: int, mes_ipca: str) -> float:
    """IPCA dez/(ano−1) -> dez/ano, truncado no último mês público em T."""
    fim = min(f"{ano}-12", mes_ipca)
    ini = f"{ano - 1}-12"
    return fator_mes(ini, fim, mes_ipca) - 1 if ini < fim else 0.0


def _ci(c: dict) -> float | None:
    """Capital investido = PL + dívida bruta (com arrendamento) − caixa e aplicações."""
    pl = _num(c, "pl")
    if pl is None:
        return None
    bruta, caixa, _ = contas.divida_liquida(c)
    return pl + bruta - caixa


def med_outras(anos: tuple[Ano, ...]) -> float | None:
    """Mediana de 'outras receitas' ÷ receita na janela (base do EBIT ajustado, §7 armadilha 1)."""
    validos = [a for a in anos if a.c("receita") > 0]
    med = mediana(contas.outras(a.contas) / a.c("receita") for a in validos)
    return med if math.isfinite(med) else None


def roic_reais(anos: tuple[Ano, ...], mes_ipca: str) -> list[float | None]:
    """ROIC real por exercício: EBIT ajustado × (1 − t) ÷ capital investido médio, Fisher pelo IPCA
    do ano. None = exercício sem dado ou com capital investido <= 0 (não conta na janela)."""
    med_outras_ = med_outras(anos)
    t = aliquota(anos, BT)
    out: list[float | None] = []
    for k, a in enumerate(anos):
        if _num(a.contas, "ebit") is None:
            out.append(None)
            continue
        ci = _ci(a.contas)
        ci_ant = _ci(anos[k - 1].contas) if k > 0 else None
        ci_med = ci if ci_ant is None or ci is None else (ci + ci_ant) / 2
        if ci_med is None or ci_med <= 0:
            out.append(None)
            continue
        nominal = contas.ebit_aj(a.contas, med_outras_) * (1 - t) / ci_med
        out.append((1 + nominal) / (1 + inflacao_do_ano(a.ano, mes_ipca)) - 1)
    return out


def roe_reais(anos: tuple[Ano, ...], mes_ipca: str) -> list[float | None]:
    """ROE real do controlador por exercício (financeiras): lucro ÷ PL controlador médio, Fisher."""
    def plc(c):
        pl = _num(c, "pl")
        return None if pl is None else pl - (_num(c, "nao_controladores") or 0.0)
    out: list[float | None] = []
    for k, a in enumerate(anos):
        lucro = lucro_controlador(a.contas)
        p, p_ant = plc(a.contas), (plc(anos[k - 1].contas) if k > 0 else None)
        base = p if p_ant is None or p is None else (p + p_ant) / 2
        if lucro is None or base is None or base <= 0:
            out.append(None)
            continue
        out.append((1 + lucro / base) / (1 + inflacao_do_ano(a.ano, mes_ipca)) - 1)
    return out


def q1(retornos: list[float | None], barreira: float, nome_barreira: str,
       cfg: ConfigTriagem = PADRAO) -> Teste:
    vals = [r for r in retornos if r is not None]
    n = len(vals)
    if n < cfg.min_exercicios:
        return Teste(INDET, f"{n} exercícios válidos (< {cfg.min_exercicios})")
    acima = sum(r > barreira for r in vals)
    st = OK if acima >= precisa(n, cfg.q1_frac) else FALHA
    return Teste(st, f"{acima}/{n} acima do {nome_barreira} real {br(barreira * 100, 1)}%", acima / n)


def q2(anos: tuple[Ano, ...], cfg: ConfigTriagem = PADRAO) -> Teste:
    fco = [_num(a.contas, "fco") for a in anos]
    vals = [x for x in fco if x is not None]
    n = len(vals)
    if n < cfg.min_exercicios:
        return Teste(INDET, f"FCO em {n} exercícios (< {cfg.min_exercicios})")
    pos = sum(x > 0 for x in vals)
    return Teste(OK if pos >= precisa(n, cfg.q2_frac) else FALHA, f"FCO > 0 em {pos}/{n}", pos / n)


def q3(balanco: dict, ult: Ano, cfg: ConfigTriagem = PADRAO) -> Teste:
    """Dívida líquida do último balanço visível (ITR se mais novo) ÷ EBITDA do último exercício."""
    if not balanco:
        return Teste(INDET, "sem balanço")
    _, _, dl = contas.divida_liquida(balanco)
    if dl <= 0:
        return Teste(OK, "caixa líquido", dl)
    ebit = _num(ult.contas, "ebit")
    if ebit is None:
        return Teste(INDET, "sem EBIT no último exercício")
    ebitda = ebit + ult.da
    if ebitda <= 0:
        return Teste(FALHA, "EBITDA <= 0 com dívida líquida", math.inf)
    r = dl / ebitda
    return Teste(OK if r <= cfg.q3_dl_ebitda else FALHA, f"DL/EBITDA {br(r, 1)}", r)


def retido(anos: tuple[Ano, ...], k: int = 0) -> float:
    """Σ (lucro do controlador − proventos pagos) nos exercícios APÓS o k-ésimo, em R$ mil de T."""
    tot = 0.0
    for a in anos[k + 1:]:
        l = lucro_controlador(a.contas)
        tot += ((l or 0.0) - a.dividendos) * a.real
    return tot


def q4(i: Insumos, preco_t: float, preco_d0: float | None, fator_d0_t: float, infl_d0: float,
       k: int = 0, cfg: ConfigTriagem = PADRAO, papeis_d0: float | None = None) -> Teste:
    """R$ 1 retido (Buffett): Δ valor de mercado real ÷ lucro retido real na janela.

    A janela começa no fim do exercício `k` (D0): 0 normalmente; maior quando o papel só passou a
    negociar depois (IPO). Mesma base de ações dos dois lados (preço de D0 trazido à base de hoje
    pelo fator de eventos). `papeis_d0` (FRE visto em D0, já na base de hoje) entra no valor inicial
    quando conhecido; sem ele usa os papéis de hoje e a emissão/recompra fica só como pendência.
    Lucro acumulado <= 0 na janela -> falha (destruiu capital, não há "retido" a testar). Retido menor que `q4_materialidade` do valor de mercado inicial -> n/a: a razão sobre um
    denominador perto de zero não mede alocação (quem distribui ~100% não tem o que testar).
    """
    if len(i.anos) - k - 1 < cfg.q4_min_exercicios:
        return Teste(INDET, f"janela com preço curta ({len(i.anos) - k - 1} exercícios)")
    if preco_d0 is None or not math.isfinite(preco_d0) or not math.isfinite(fator_d0_t) or fator_d0_t <= 0:
        return Teste(INDET, "sem preço ou fator de evento no início da janela")
    lucro = sum((lucro_controlador(a.contas) or 0.0) * a.real for a in i.anos[k + 1:])
    if lucro <= 0:
        return Teste(FALHA, "prejuízo acumulado na janela", -math.inf)
    ret = retido(i.anos, k)
    base0 = papeis_d0 if papeis_d0 and math.isfinite(papeis_d0) and papeis_d0 > 0 else i.papeis
    vm_t = preco_t * i.papeis / 1000.0
    vm_0 = preco_d0 / fator_d0_t * base0 / 1000.0 * infl_d0
    if ret <= cfg.q4_materialidade * vm_0:
        return Teste(NA, f"retém pouco ({ret / vm_0:.0%} do valor de mercado inicial)"
                     if vm_0 > 0 else "sem valor de mercado inicial")
    r = (vm_t - vm_0) / ret
    n = len(i.anos) - k - 1
    return Teste(OK if r >= cfg.q4_minimo else FALHA,
                 f"R$ 1 retido -> R$ {br(r)} ({n} exerc.)", r)


def q5(anos: tuple[Ano, ...], cfg: ConfigTriagem = PADRAO) -> Teste:
    n = len(anos)
    pagos = sum(a.dividendos > 0 for a in anos)
    return Teste(OK if pagos >= precisa(n, cfg.q5_frac) else FALHA, f"pagou em {pagos}/{n}", pagos / n)


def portao(q: dict[str, Teste], cfg: ConfigTriagem = PADRAO) -> bool:
    if q["Q1"].status != OK:
        return False
    return sum(q[k].reprovou for k in ("Q2", "Q3", "Q4", "Q5")) <= cfg.max_reprovacoes_q2_q5


def ncav_por_acao(i: Insumos) -> float:
    b = i.balanco
    ac, pc, pnc = _num(b, "ac"), _num(b, "pc"), _num(b, "pnc")
    if ac is None or pc is None or pnc is None:
        return math.nan
    return i.por_acao(ac - pc - pnc - (_num(b, "nao_controladores") or 0.0))


def ey(i: Insumos, preco: float) -> float:
    """EBIT AJUSTADO do último exercício (sem o excesso de 'outras receitas' sobre a mediana da
    janela, como o Q1 e o motor) ÷ EV (valor de mercado + dívida líquida + não controladores)."""
    if _num(i.anos[-1].contas, "ebit") is None:
        return math.nan
    ebit = contas.ebit_aj(i.anos[-1].contas, med_outras(i.anos))
    _, _, dl = contas.divida_liquida(i.balanco)
    ev = preco * i.papeis / 1000.0 + dl + (_num(i.balanco, "nao_controladores") or 0.0)
    if ev > 0:
        return ebit / ev
    return math.inf if ebit > 0 else math.nan      # caixa acima do valor de mercado
