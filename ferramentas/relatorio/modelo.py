"""Número com fonte e nota, seção e relatório.

Nota da fonte (doutrina §2, regra 1 do 02; escala A/B/C do `~/.claude/PESQUISA.md`):
  A = primária oficial (CVM, B3/COTAHIST, Tesouro, ANBIMA, BCB); B = primária com ressalva (RI, documento da companhia);
  C = agregador sem fonte primária (StatusInvest) ou campo não conferido; "—" = digitado/arbitrado sem fonte numérica.
O número derivado herda a PIOR nota dos insumos e nunca é promovido. Só A/B embasa decisão: o relatório mostra o C e o "—"
marcados, em vez de escondê-los.
"""
from __future__ import annotations

from dataclasses import dataclass, field

NOTAS = ("A", "B", "C", "—")
SEM_FONTE = "—"


@dataclass(frozen=True)
class Origem:
    fonte: str                        # nome curto, o que vai na coluna (ex.: "CVM DFP/ITR")
    nota: str
    detalhe: str = ""                 # descrição completa, na legenda de fontes do relatório

    def __post_init__(self):
        if self.nota not in NOTAS:
            raise ValueError(f"nota de fonte inválida: {self.nota!r} (vale {NOTAS})")
        if not self.fonte.strip():
            raise ValueError("origem sem fonte escrita")


def pior(origens) -> str:
    """A pior nota entre as origens; sem origem nenhuma = sem fonte (nunca A por omissão)."""
    return max((o.nota for o in origens), key=NOTAS.index, default=SEM_FONTE)


def decide(nota: str) -> bool:
    return nota in ("A", "B")


@dataclass
class Numero:
    rotulo: str
    valor: float | str | None
    unidade: str = ""                 # "R$", "%", "x", "" — só formatação
    origens: tuple[Origem, ...] = ()
    papel: str = ""                   # "central" (entra na mediana) | "informativo" | "" (resultado/indicador)
    obs: str = ""

    @property
    def nota(self) -> str:
        return pior(self.origens)

    @property
    def fonte(self) -> str:
        vistas = []
        for o in self.origens:
            if o.fonte not in vistas:
                vistas.append(o.fonte)
        return "; ".join(vistas) or "sem fonte"


@dataclass
class Secao:
    titulo: str
    numeros: list[Numero] = field(default_factory=list)
    texto: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    tabelas: list[tuple[str, list[str], list[list[str]]]] = field(default_factory=list)   # (título, cabeçalho, linhas)


@dataclass
class Relatorio:
    tk: str
    nome: str
    data: str                         # data-base do preço e do mercado (AAAA-MM-DD)
    origem: str                       # "dossiê" | "hall, lote N"
    palavra: str
    secoes: list[Secao] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)

    def numeros(self):
        for s in self.secoes:
            yield from s.numeros

    def fontes(self) -> dict[str, Origem]:
        """Legenda: nome curto → origem (a primeira vista), na ordem em que aparecem."""
        out = {}
        for n in self.numeros():
            for o in n.origens:
                out.setdefault(o.fonte, o)
        return out
