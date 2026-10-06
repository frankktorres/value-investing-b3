"""Porta única do motor reduzido: insumos de T -> âncoras -> régua.

Âncora não calculável (NaN) exclui o papel com motivo — a régua nunca vê NaN, que passaria pelas
comparações `<= 0` como se fosse número válido.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from ..config import PADRAO, Config
from ..mercado_bt import MercadoBT
from . import reduzido_fin, reduzido_nf
from .base import Insumos
from .regua import Veredito, avaliar_bt


@dataclass(frozen=True)
class Resultado:
    insumos: Insumos
    ancoras: dict = field(default_factory=dict)
    premissas: dict = field(default_factory=dict)
    veredito: Veredito | None = None
    motivo_exclusao: str = ""


def avaliar(i: Insumos, mk: MercadoBT, preco: float, cfg: Config = PADRAO) -> Resultado:
    if i.excluido:
        return Resultado(i, motivo_exclusao=i.motivo_exclusao)
    if i.perfil.motor == "fin":
        anc, prem = reduzido_fin.ancoras(i, mk, cfg)
    else:
        anc, prem = reduzido_nf.ancoras(i, mk, preco, cfg)
    if not anc or any(not math.isfinite(x) for x in anc.values()):
        return Resultado(i, anc, prem, motivo_exclusao="ancora_indisponivel")
    return Resultado(i, anc, prem, avaliar_bt(anc, preco, cfg))
