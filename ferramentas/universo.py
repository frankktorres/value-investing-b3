"""Avalia todos os tickers dos 6 lotes num só lugar (usado por tests/ e rodar_tudo.py).

Cada lote continua sendo a fonte das premissas; aqui só se junta e se extrai um 'instantâneo' comparável.
Importar este módulo carrega os 6 lotes (lote4 lê os ZIPs da CVM; leva alguns segundos).
"""
import lote1_bancos
import lote2_energia
import lote3_agro
import lote4_saude_telecom
import lote5_petroleo
import lote6_quimica
import precos_hall
from lote1_bancos import MK
from motor_financeiras import avaliar as avaliar_fin
from motor_nao_financeiras import avaliar as avaliar_nf

# (lote, empresas, motor): o motor decide a função de avaliação
GRUPOS = [
    (1, lote1_bancos.EMPRESAS, avaliar_fin),
    (2, lote2_energia.EMPRESAS, avaliar_fin),
    (3, lote3_agro.EMPRESAS, avaliar_nf),
    (4, lote4_saude_telecom.EMPRESAS, avaliar_nf),
    (4, [lote4_saude_telecom.ITSA4], avaliar_fin),
    (5, lote5_petroleo.EMPRESAS, avaliar_nf),
    (6, lote6_quimica.EMPRESAS, avaliar_nf),
    (6, [lote6_quimica.EGIE], avaliar_fin),
]

# Campos extras do instantâneo: o que o motor expõe de cada família (None quando não existe)
EXTRAS = ("nota_geral", "vence_rf", "bogle_nom", "cobertura_juros", "fator_defasagem", "dy")


def avaliar_todos():
    """{ticker: {lote, empresa, r}} com o dict completo do motor em r."""
    out = {}
    for lote, empresas, motor in GRUPOS:
        for e in empresas:
            # AUD-67: a data do preço é a do snapshot oficial (precos_hall), não a da taxa (MK.data, AUD-72)
            out[e.ticker] = dict(lote=lote, empresa=e, r=motor(e, MK), data_preco=precos_hall.PRECO_DATA_BR)
    return out


def instantaneo(item):
    """Os números que o golden guarda para um ticker."""
    r = item["r"]
    snap = dict(
        lote=item["lote"], data_preco=item.get("data_preco"),
        central=r["central"], pc=r["pc"], palavra=r["palavra"],
        ancoras={k: v for k, v in r["ancoras"].items()},
        nota_geral=r["notas"]["geral"], vence_rf=r.get("vence_rf"), bogle_nom=r.get("bogle_nom"),
        cobertura_juros=r.get("cobertura_juros"), fator_defasagem=r.get("fator_defasagem"), dy=r.get("dy"),
    )
    return {k: (round(v, 6) if isinstance(v, float) and v == v and abs(v) != float("inf") else v) for k, v in snap.items()} | \
        {"ancoras": {k: round(v, 6) for k, v in snap["ancoras"].items()}}


def instantaneo_todos():
    return {tk: instantaneo(it) for tk, it in sorted(avaliar_todos().items())}
