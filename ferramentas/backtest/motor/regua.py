"""A régua da doutrina v2.2 (§9 e §11.3) com os números de `config` — âncoras -> palavra.

Os dois motores de hoje repetem a mesma lógica (motor_financeiras.py:280-292 e
motor_nao_financeiras.py:536-546) com os números como constante de módulo. Aqui ela existe uma vez,
lendo `Config`, para que o hash da configuração amarre também a régua.

Ordem (doutrina :175-181): palavra pela escala de P/C → teto RADAR fora do círculo → dispersão.
  · central = mediana das âncoras; central <= 0 -> P/C infinito;
  · alguma âncora <= 0, ou dispersão (max/min) > disp_inconclusivo -> NÃO CONCLUSIVO;
  · dispersão > disp_desce -> confiança baixa, e só o lado favorável desce um nível
    (BARATA -> RADAR -> JUSTA); JUSTA e CARA não mudam.

O portão da fatia 11 é `tests/test_regua.py`: alimentada com as âncoras do golden e o preço
`pc × central`, esta função tem de devolver a palavra e o central dos 41 tickers.
"""
from __future__ import annotations

import math
import statistics
from dataclasses import dataclass

from ..config import PADRAO, Config

BARATA, RADAR, JUSTA, CARA = "BARATA", "RADAR", "JUSTA", "CARA"
NAO_CONCLUSIVO = "NÃO CONCLUSIVO"
# Nível ordinal para o "±1 nível" do portão do proxy. NÃO CONCLUSIVO não tem nível: só acerta NC.
NIVEL = {BARATA: 0, RADAR: 1, JUSTA: 2, CARA: 3}
_DESCE = {BARATA: RADAR, RADAR: JUSTA}


@dataclass(frozen=True)
class Veredito:
    central: float
    dispersao: float
    pc: float
    palavra_escala: str      # só a escala de P/C, antes de círculo e dispersão
    palavra: str             # a palavra final — a única que autoriza compra
    confianca: str           # "normal" | "baixa"
    nao_conclusivo: bool


def palavra_da_escala(pc: float, cfg: Config = PADRAO) -> str:
    if pc <= cfg.palavra_barata:
        return BARATA
    if pc <= cfg.palavra_radar:
        return RADAR
    if pc <= cfg.palavra_justa:
        return JUSTA
    return CARA


def avaliar_bt(ancoras: dict[str, float], preco: float, cfg: Config = PADRAO,
               fora_circulo: bool = False) -> Veredito:
    """Âncoras (R$ por ação, já com qualquer desconto) e preço -> veredito da régua."""
    vals = [float(x) for x in ancoras.values()]
    if not vals:
        return Veredito(math.nan, math.inf, math.inf, NAO_CONCLUSIVO, NAO_CONCLUSIVO, "baixa", True)
    central = statistics.median(vals)
    algum_nao_positivo = any(x <= 0 for x in vals)
    dispersao = math.inf if algum_nao_positivo else max(vals) / min(vals)

    if central <= 0:
        pc = math.inf
        p0 = NAO_CONCLUSIVO
    else:
        pc = preco / central
        p0 = palavra_da_escala(pc, cfg)

    p = p0
    if fora_circulo and p == BARATA:
        p = RADAR
    confianca = "normal"
    nc = algum_nao_positivo or dispersao > cfg.disp_inconclusivo or p0 == NAO_CONCLUSIVO
    if nc:
        p = NAO_CONCLUSIVO
        confianca = "baixa"
    elif dispersao > cfg.disp_desce:
        confianca = "baixa"
        p = _DESCE.get(p, p)
    return Veredito(central=central, dispersao=dispersao, pc=pc, palavra_escala=p0, palavra=p,
                    confianca=confianca, nao_conclusivo=nc)
