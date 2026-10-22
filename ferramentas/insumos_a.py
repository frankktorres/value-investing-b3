"""Registro de procedência por campo dos lotes do hall (fase 3, fatia 1 — 19/10/2026).

O lote calcula o insumo a partir de uma fonte oficial (CVM, B3) e passa o valor por `registrar`; o relatório
(`relatorio/procedencia.py`) só dá a nota da fonte ao campo se o valor que a empresa carrega é o MESMO que foi registrado
(`origem`). Literal digitado, valor sobrescrito depois ou campo nunca registrado → `None`, e o relatório cai na nota C do
lote. A nota nunca sobe por omissão: sem registro não há fonte.
"""
from __future__ import annotations

import math

from precos_hall import PRECO_DATA
from relatorio.modelo import Origem

_REG: dict[tuple[str, str], tuple[object, Origem]] = {}


def _num(x) -> float:
    if isinstance(x, bool):
        raise TypeError("booleano não é número de fonte")
    return float(x)


def _congela(v):
    """Número → float; {chave: número ou texto} → {str: float | str} (cópia: mudar o dict da empresa depois não muda o registro).
    Texto só dentro de dict (o prazo do crédito fiscal: {"ate": 2032, "fonte": "..."}) e comparado igual, letra a letra."""
    if isinstance(v, dict):
        return {str(k): (x if isinstance(x, str) else _num(x)) for k, x in v.items()}
    return _num(v)


def _igual(a, b) -> bool:
    if isinstance(a, dict) or isinstance(b, dict):
        return (isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys()
                and all(_igual(a[k], b[k]) for k in a))
    if isinstance(a, str) or isinstance(b, str):
        return a == b
    return math.isclose(a, b, rel_tol=1e-12, abs_tol=0.0)


def registrar(tk: str, campo: str, valor, origem: Origem):
    """Guarda (valor, origem) do campo do ticker e devolve o valor sem mexer nele. Valor: número ou {chave: número ou texto}."""
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
RECEITA_CVM = Origem("CVM DFP/ITR", "A", "CVM, receita líquida do DFP/ITR (LTM) em R$ de hoje (IPCA, BCB): média dos "
                     "exercícios declarados no lote (receita_media)")
ACOES_ITR_JUN26 = Origem("CVM (ações)", "A", "CVM, composição do capital do ITR de 30/06/2026, sem tesouraria (snapshot "
                         "derivados_zip quando o ZIP falta)", data="2026-06-30")
PRECO_COTAHIST = Origem("COTAHIST", "A", "B3, COTAHIST, fechamento (PREULT) do pregão da data-base — snapshot versionado "
                        "dados/precos_hall_<data>.csv (precos_hall.preco)", data=PRECO_DATA)
RECEITA_MEIO_BRENT = Origem("CVM + EIA/BCB", "A", "receita e D&A do DFP/ITR (CVM) × barril de meio de ciclo ÷ barril do período-base: Brent "
                            "(EIA, série DCOILBRENTEU via FRED, sem transformação) × PTAX média mensal (BCB SGS 3698), IPCA (BCB SGS 433) — "
                            "lote5_petroleo.base_ep; nota da série conferida pelo verificador-fonte em 20/10/2026")
RECEITA_MEIO_ACO = Origem("CVM + BLS/BCB", "A", "receita 12m do ITR (CVM) × aço de meio de ciclo ÷ aço dos 12m: BLS PPI WPU1017 (via FRED, "
                          "sem transformação) × PTAX (BCB SGS 3698), IPCA (BCB SGS 433) — lote6_quimica.indice; nota conferida em 20/10/2026")
RECEITA_MEIO_CLORO = Origem("CVM + BLS/BCB", "A", "receita 12m do ITR (CVM) × cesta soda/PVC de meio de ciclo ÷ cesta dos 12m: BLS PPI "
                            "PCU3251803251804 e WPU0662 (Thermoplastic Resins and Plastics Materials, NSA; FRED e API v1 do BLS "
                            "conferidos em 20/10/2026 — B31: os meses publicados batem com o CSV, salvo as revisões dos preliminares "
                            "de mai–ago/2026) × PTAX, IPCA (BCB) — lote6_quimica.indice")


def _aliquota_tims3():
    import fiscal
    return Origem("CVM + DFP (conciliação)", "A", fiscal.TIMS3_FONTE)


ALIQUOTA_TIMS3 = _aliquota_tims3()
G1_CVM = Origem("CVM + B3", "A", "g do 1º estágio = ROE mediano 2021–25 (lucro e PL do controlador, DFP/CVM) × (1 − payout recorrente "
                "mediano: DPA por data-com da B3 sem o extraordinário ÷ LPA do DFP), deflacionado pela π implícita (ANBIMA) — "
                "lote4_saude_telecom.g1_sustentavel")
NAV_SLCE3 = Origem("SLC (fato relevante)", "A", "SLC Agrícola, fato relevante 'Portfólio de Terras: Atualização 2026' (15/06/2026): NAV "
                   "R$ 13.824 mi ÷ 498.745.930 ações; terras avaliadas pela Deloitte (terra nua, NBR 14653), demais itens contábeis "
                   "de 31/03/2026 (lote3_agro.SLCE3_NAV_MI)", data="2026-06-15")
PL_HIST_CVM = Origem("CVM + COTAHIST", "A", "P/L histórico: mediana dos anos com 0 < P/L < 40 de fechamento do fim do exercício (B3, "
                     "COTAHIST) × ações do DFP ÷ lucro do controlador (CVM) — pl_historico.do_hall")
ALIQUOTA_FASE_DFP = Origem("DFP/release (prazo do crédito)", "A", "prazo do crédito de IR declarado em fiscal.ALIQUOTA_FASE com a fonte "
                           "no próprio campo (DFP/release da companhia); a alíquota efetiva da fase é a mediana da CVM (motor)")
