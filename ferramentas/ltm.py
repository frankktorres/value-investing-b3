"""Acesso ao LTM de uma empresa do cvm_series.json, independente do trimestre coletado.

O coletor grava o LTM em três chaves: "ltm" (genérica), "ltm_ref" (ex.: "3T26") e "ltm_<ref>" (ex.: "ltm_3T26").
A série antiga só tem "ltm_2T26": é o último recurso.
"""


def ltm_de(reg):
    if "ltm" in reg:
        return reg["ltm"]
    return reg["ltm_2T26"]


def ltm_ref_de(reg):
    """Rótulo do trimestre do LTM ("2T26", "3T26"...); a série antiga sem "ltm_ref" é 2T26."""
    if "ltm_ref" in reg:
        return reg["ltm_ref"]
    return "2T26"
