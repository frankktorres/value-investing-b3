"""Registro de procedência por campo dos lotes do hall (fase 3, fatia 1 — 19/10/2026).

O lote calcula o insumo a partir de uma fonte oficial (CVM, B3) e passa o valor por `registrar`; o relatório
(`relatorio/procedencia.py`) só dá a nota da fonte ao campo se o valor que a empresa carrega é o MESMO que foi registrado
(`origem`). Literal digitado, valor sobrescrito depois ou campo nunca registrado → `None`, e o relatório cai na nota C do
lote. A nota nunca sobe por omissão: sem registro não há fonte.
"""
from __future__ import annotations

import math

from relatorio.modelo import Origem

_REG: dict[tuple[str, str], tuple[object, Origem]] = {}


def _num(x) -> float:
    if isinstance(x, bool):
        raise TypeError("booleano não é número de fonte")
    return float(x)


def _congela(v):
    """Número → float; {chave: número} → {str: float} (cópia: mudar o dict da empresa depois não muda o registro)."""
    if isinstance(v, dict):
        return {str(k): _num(x) for k, x in v.items()}
    return _num(v)


def _igual(a, b) -> bool:
    if isinstance(a, dict) or isinstance(b, dict):
        return (isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys()
                and all(_igual(a[k], b[k]) for k in a))
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=0.0)


def registrar(tk: str, campo: str, valor, origem: Origem):
    """Guarda (valor, origem) do campo do ticker e devolve o valor sem mexer nele. Valor: número ou {chave: número}."""
    _REG[(tk, campo)] = (_congela(valor), origem)
    return valor


def origem(tk: str, campo: str, usado) -> Origem | None:
    """A origem registrada, só se `usado` é o valor registrado; senão None (o chamador decide a nota de fallback)."""
    reg = _REG.get((tk, campo))
    if reg is None or usado is None:
        return None
    try:
        return reg[1] if _igual(_congela(usado), reg[0]) else None
    except (TypeError, ValueError):
        return None


ACOES_DFP = lambda ano, unit: Origem(
    "CVM (ações)", "A", f"CVM, composição do capital do DFP {ano}, sem tesouraria"
    + (f"; em units ({unit:g} ações por unit)" if unit and unit != 1 else "") + " (lote3_agro.acoes)")
IPCA_BCB = Origem("BCB (IPCA)", "A", "BCB, SGS 433 (IPCA mensal, dados/macro/ipca_mensal.json, coletar_macro.py): deflator "
                  "anual até a data-base")
ACOES_ITR_JUN26 = Origem("CVM (ações)", "A", "CVM, composição do capital do ITR de 30/06/2026, sem tesouraria (snapshot "
                         "derivados_zip quando o ZIP falta)")
