"""Juros do período para a cobertura (EBIT ÷ juros): juros efetivamente pagos na DFC; sem a linha, despesa financeira bruta da DRE.

Despesa bruta mistura variação cambial e juros provisionados (06/10: PRIO3, RECV3, PETR4 com dívida em dólar); o caixa pago é o que o credor recebeu.
"""


def juros_do_periodo(d):
    """(valor positivo em R$ mil, fonte) a partir de um período do cvm_series ('anual'[ano] ou 'ltm_2T26')."""
    pagos = d.get("juros_pagos") or 0
    if pagos > 0:
        return pagos, "juros pagos (DFC)"
    return -(d.get("desp_fin") or 0), "despesa financeira bruta (DRE)"
