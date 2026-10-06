"""Insumos comuns do motor reduzido: ledger PIT + perfil + contagem de ações + DFC + série real.

Tudo o que os dois motores reduzidos leem passa por `montar`, e só por ele — é o ponto único onde o
teste de não-vazamento confere a procedência (toda `dt_receb` <= T).

Unidades: contas do ledger em R$ MIL (fatos_cvm normaliza); ações em unidades. Valor por papel =
R$ mil × 1000 / papéis.

**Contagem de ações** (a pendência da fatia 10): o FRE dá a contagem na data da AUTORIZAÇÃO de
capital. Um desdobramento entre a autorização e T multiplica as ações sem mudar o capital; sem o
fator, o valor por ação sai N vezes maior e o P/C N vezes menor. Logo:
    papéis(T) = ações_FRE × eventos.fator_entre(ticker, aprovação, T) ÷ ações_por_papel
(`ações_por_papel` = 1 para ON/PN, a composição para unit). Fator NaN (evento sem fator), contagem
ambígua ou sem aprovação -> exclui com motivo; nunca supõe 1.
"""
from __future__ import annotations

import math
import re
import statistics
from dataclasses import dataclass, field, replace
from functools import lru_cache

import pandas as pd

from .. import inflacao_pit
from ..config import PADRAO, Config
from ..ledger.pit import FINANCEIRO, INDUSTRIAL, Exercicio, LedgerPIT, ledger_em
from ..precos.eventos import fator_entre
from .perfil import Perfil, acoes_por_papel, normaliza, perfil_em


# A tabela de eventos nasce do COTAHIST (2014 em diante): antes disso ela não sabe nada.
INICIO_EVENTOS = "2014-01-01"


@dataclass(frozen=True)
class Ano:
    """Um exercício da janela, com as linhas da DFC já somadas e o fator para R$ do ano de T."""
    dt_refer: str
    ano: int
    contas: dict
    da: float                # D&A (6.01), positivo
    capex: float             # aquisição de imobilizado + intangível (6.02), positivo
    dividendos: float        # dividendos + JCP pagos (6.03), positivo
    arrendamento: float      # principal de arrendamento pago (6.03), positivo
    real: float              # multiplica R$ do exercício -> R$ do ano de T (IPCA público em T)

    def c(self, k: str, default: float = 0.0) -> float:
        x = self.contas.get(k)
        return default if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)


@dataclass(frozen=True)
class Insumos:
    ticker: str
    cd_cvm: int
    data_corte: str
    perfil: Perfil
    ledger: LedgerPIT | None
    anos: tuple[Ano, ...] = ()
    balanco: dict = field(default_factory=dict)   # último balanço visível (ITR se mais novo)
    balanco_dt_refer: str = ""
    papeis: float = math.nan                      # ações equivalentes ao papel cotado, em T
    fator_evento: float = math.nan
    por_papel: int | None = None
    fator_inicio: str = ""                        # janela (fator_inicio, T] do fator de evento
    motivo_exclusao: str = ""

    @property
    def excluido(self) -> bool:
        return bool(self.motivo_exclusao)

    def por_acao(self, valor_mil: float) -> float:
        return valor_mil * 1000.0 / self.papeis

    def procedencia(self) -> dict[str, object]:
        l = self.ledger
        return {"ticker": self.ticker, "cd_cvm": self.cd_cvm, "data_corte": self.data_corte,
                "setor": self.perfil.setor, "perfil": self.perfil.perfil,
                "perfil_dt_receb": self.perfil.dt_receb,
                "dt_receb_maxima": l.dt_receb_maxima if l else "",
                "n_exercicios": len(self.anos), "balanco": self.balanco_dt_refer,
                "acoes_fre": l.acoes if l else None, "acoes_aprovacao": l.acoes_aprovacao if l else "",
                "fator_evento": self.fator_evento, "fator_inicio": self.fator_inicio, "por_papel": self.por_papel,
                "papeis": self.papeis, "motivo_exclusao": self.motivo_exclusao}


def _folhas(linhas: tuple[tuple[str, str, float], ...]) -> list[tuple[str, str, float]]:
    cods = {c for c, _, _ in linhas}
    return [(c, d, v) for c, d, v in linhas if not any(o != c and o.startswith(c + ".") for o in cods)]


def soma_dfc(linhas: tuple[tuple[str, str, float], ...], regra: tuple[str, str, str]) -> float:
    """Soma das contas-folha do grupo `regra[0]` cuja descrição casa `regra[1]` e não `regra[2]`."""
    grupo, inclui, exclui = regra
    tot = 0.0
    for c, d, v in _folhas(linhas):
        if not (c == grupo or c.startswith(grupo + ".")):
            continue
        n = normaliza(d)
        if re.search(inclui, n) and not re.search(exclui, n) and not math.isnan(v):
            tot += v
    return tot


def _ano(e: Exercicio, ano_t: int, mes_ipca: str, cfg: Config) -> Ano:
    return Ano(dt_refer=e.dt_refer, ano=e.ano, contas=dict(e.contas),
               da=abs(soma_dfc(e.dfc, cfg.dfc_da)),
               capex=max(-soma_dfc(e.dfc, cfg.dfc_capex), 0.0),
               dividendos=max(-soma_dfc(e.dfc, cfg.dfc_dividendos), 0.0),
               arrendamento=max(-soma_dfc(e.dfc, cfg.dfc_arrendamento), 0.0),
               real=inflacao_pit.fator_entre(e.ano, ano_t, mes_ipca))


def montar(cd_cvm: int, ticker: str, cnpj: str, data_corte: str, eventos: pd.DataFrame,
           cfg: Config = PADRAO, *, perfil: Perfil | None = None,
           ledger: LedgerPIT | None = None, por_papel: int | None = None,
           fre: pd.DataFrame | None = None) -> Insumos:
    """Tudo o que se sabia em T para avaliar `ticker`. Os keywords existem para o teste injetar."""
    p = perfil or perfil_em(cd_cvm, data_corte, cfg)
    base = Insumos(ticker=ticker, cd_cvm=cd_cvm, data_corte=data_corte, perfil=p, ledger=None)
    if p.motivo_exclusao:
        return _com(base, motivo_exclusao=p.motivo_exclusao)
    l = ledger or ledger_em(cd_cvm, data_corte, FINANCEIRO if p.plano == "financeiro" else INDUSTRIAL,
                            cfg)
    if l is None:
        return _com(base, motivo_exclusao="sem_ledger")
    base = _com(base, ledger=l)
    if l.n_exercicios < cfg.janela_min:
        return _com(base, motivo_exclusao="janela_curta")
    if not l.acoes or l.acoes <= 0 or l.acoes_ambiguo or not l.acoes_aprovacao:
        return _com(base, motivo_exclusao="acoes_indisponiveis")
    if l.acoes_dt_receb > data_corte or l.acoes_aprovacao > data_corte:
        raise AssertionError(f"contagem de ações posterior a T em {cd_cvm}: vazamento")
    # A janela do fator começa na ENTREGA do FRE, não na aprovação: a linha cuja aprovação é a
    # própria AGE do desdobramento já traz a contagem pós-evento, e o FRE seguinte reexpressa
    # contagens antigas mantendo a data velha (MGLU 2024: 7,39 bi num FRE, 739 M no outro).
    # Começar na aprovação aplicava o evento duas vezes — IRBR3 2024-06 saía BARATA com 30x de
    # erro nas ações (adversario, 06/10/2026). O que o FRE entregue já mostra está na contagem.
    inicio = max(l.acoes_aprovacao, l.acoes_dt_receb)
    if inicio < INICIO_EVENTOS and _evento_fre_sem_preco(cnpj, inicio, fre):
        return _com(base, motivo_exclusao="evento_antes_do_cotahist")
    fator = fator_entre(eventos, ticker, inicio, data_corte)
    if not math.isfinite(fator) or fator <= 0:
        return _com(base, fator_evento=fator, motivo_exclusao="evento_sem_fator")
    n = por_papel if por_papel is not None else acoes_por_papel(ticker, cnpj, data_corte)
    if not n:
        return _com(base, fator_evento=fator, motivo_exclusao="unit_sem_composicao")

    ano_t = int(data_corte[:4])
    anos = tuple(_ano(e, ano_t, l.mes_ipca, cfg) for e in l.anuais)
    ultimo = l.anuais[-1]
    bal, bal_ref = dict(ultimo.contas), ultimo.dt_refer
    if l.ultimo_itr is not None and l.ultimo_itr.dt_refer > ultimo.dt_refer:
        bal, bal_ref = dict(l.ultimo_itr.contas), l.ultimo_itr.dt_refer
    return _com(base, anos=anos, balanco=bal, balanco_dt_refer=bal_ref, fator_inicio=inicio,
                papeis=l.acoes * fator / n, fator_evento=fator, por_papel=n)


@lru_cache(maxsize=1)
def _fre_eventos() -> pd.DataFrame:
    from ..precos.eventos import eventos_fre
    return eventos_fre()


def _evento_fre_sem_preco(cnpj: str, inicio: str, fre: pd.DataFrame | None = None) -> bool:
    """Desdobramento/grupamento/bonificação aprovado no FRE entre `inicio` e 2014 — época sem
    COTAHIST, logo sem data ex nem fator na tabela: o fator sairia 1 em silêncio. Exclui."""
    f = _fre_eventos() if fre is None else fre
    return bool(((f["cnpj"] == cnpj) & (f["aprovacao"] > inicio)
                 & (f["aprovacao"] < INICIO_EVENTOS)).any())


def lucro_controlador(c: dict) -> float | None:
    """Lucro do controlador; cai para o lucro total quando a linha do controlador vem 0 ou vazia
    com lucro != 0 (5,4% dos exercícios industriais trazem 3.11.01 = 0: BPAN4 2021-23)."""
    def num(k):
        x = c.get(k)
        return None if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)
    lc, l = num("lucro_controlador"), num("lucro")
    if lc is None or (lc == 0 and l):
        return l
    return lc


def itr_lucro_anualizado(i: "Insumos") -> float | None:
    l = i.ledger
    if l is None or l.ultimo_itr is None or not l.anuais or l.ultimo_itr.dt_refer <= l.anuais[-1].dt_refer:
        return None
    x = lucro_controlador(l.ultimo_itr.contas)
    return None if x is None else x * 12.0 / max(l.ultimo_itr.periodo_meses, 1)


def _com(i: Insumos, **kw) -> Insumos:
    return replace(i, **kw)


def mediana(xs) -> float:
    xs = [x for x in xs if x is not None and math.isfinite(x)]
    return statistics.median(xs) if xs else math.nan
