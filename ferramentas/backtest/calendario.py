"""Datas: cortes, horizontes, último pregão <= T, e o mês de IPCA que já era público em T.

Princípio: nenhuma tabela de feriados escrita à mão. O calendário de pregões é INJETADO, e a
fonte dele é o próprio COTAHIST — o conjunto de valores do campo DATA no arquivo anual *é* o
calendário de negociação da B3, autoritativo e offline. Isso importa de verdade nos 12 cortes de
31/12: a B3 não tem sessão no dia 31, então o preço daquele corte é o do último pregão do ano, e
descobrir qual é por tabela de feriado seria errar em silêncio.

Nada aqui olha para depois da data de corte.
"""
from __future__ import annotations

import bisect
from dataclasses import dataclass
from datetime import date

from .config import Config


def _d(iso: str) -> date:
    return date.fromisoformat(iso)


@dataclass(frozen=True)
class Calendario:
    """Pregões efetivos, em ISO e ordenados. Vem do COTAHIST (fatia 8)."""
    pregoes: tuple[str, ...]

    def __post_init__(self) -> None:
        if list(self.pregoes) != sorted(self.pregoes):
            raise ValueError("pregões têm de vir ordenados")

    def ultimo_ate(self, data: str) -> str | None:
        """Último pregão com data <= `data`. None se o calendário começa depois."""
        i = bisect.bisect_right(self.pregoes, data)
        return self.pregoes[i - 1] if i else None

    def primeiro_desde(self, data: str) -> str | None:
        i = bisect.bisect_left(self.pregoes, data)
        return self.pregoes[i] if i < len(self.pregoes) else None

    def negociou_em(self, data: str) -> bool:
        i = bisect.bisect_left(self.pregoes, data)
        return i < len(self.pregoes) and self.pregoes[i] == data

    def quantos_entre(self, de: str, ate: str) -> int:
        """Pregões em (de, ate] — usado pela média de liquidez de 60 pregões."""
        return bisect.bisect_right(self.pregoes, ate) - bisect.bisect_right(self.pregoes, de)

    def janela_anterior(self, data: str, n: int) -> tuple[str, str] | None:
        """Os `n` pregões que terminam em (ou antes de) `data`. Devolve (primeiro, último)."""
        fim = bisect.bisect_right(self.pregoes, data)
        if fim < n:
            return None
        return self.pregoes[fim - n], self.pregoes[fim - 1]


def horizonte_fim(data_corte: str, anos: int) -> str:
    """Data nominal de T+h anos. O pregão efetivo sai de Calendario.ultimo_ate."""
    d = _d(data_corte)
    try:
        return d.replace(year=d.year + anos).isoformat()
    except ValueError:                       # 29/02 -> 28/02; nenhum corte cai aí, mas é barato
        return d.replace(year=d.year + anos, day=28).isoformat()


def horizonte_cabe(data_corte: str, anos: int, ultimo_dado: str) -> bool:
    """O horizonte termina dentro do dado que existe? Falso = célula sem observação, não zero."""
    return horizonte_fim(data_corte, anos) <= ultimo_dado


def mes_de(data: str) -> str:
    return data[:7]


def mes_ipca_disponivel(data_corte: str) -> str:
    """Último mês de IPCA já publicado em T.

    O IPCA do mês m sai por volta do dia 8–12 de m+1. Regra conservadora: m é público em T ⟺
    T >= dia 15 de m+1. Nos cortes de fim de mês (30/06 e 31/12) isso dá o mês ANTERIOR: em
    30/06/2014, o IPCA de maio/2014. Em data no começo do mês (o proxy roda em 05/10/2026) dá DOIS
    meses antes — em 05/10 o IPCA de setembro ainda não saiu. A regra antiga supunha fim de mês e
    entregava o mês anterior a qualquer data: look-ahead de ~10 dias, pequeno, silencioso e fácil.
    """
    d = _d(data_corte)
    recua = 1 if d.day >= 15 else 2
    ano, mes = d.year, d.month - recua
    if mes < 1:
        ano, mes = ano - 1, mes + 12
    return f"{ano}-{mes:02d}"


def janela_de(data_corte: str, cfg: Config) -> str:
    """'calibracao' | 'validacao' | 'fora' — qual metade do experimento."""
    if cfg.janela_calibracao[0] <= data_corte <= cfg.janela_calibracao[1]:
        return "calibracao"
    if cfg.janela_validacao[0] <= data_corte <= cfg.janela_validacao[1]:
        return "validacao"
    return "fora"


def estrato_de(n_exercicios: int, cfg: Config) -> tuple[int, int] | None:
    """Em que estrato de janela do ciclo cai um ledger com `n_exercicios`."""
    for lo, hi in cfg.estratos:
        if lo <= n_exercicios <= hi:
            return (lo, hi)
    return None
