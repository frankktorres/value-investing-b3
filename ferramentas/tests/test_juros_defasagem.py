"""Testes unitários de juros pagos (regex do coletor, fallback) e da defasagem medida."""
import coletar_cvm as c
import defasagem
from juros import juros_do_periodo


def _pagos(txt):
    return bool(c.RE_JUROS_PAGOS.search(txt)) and not c.RE_JUROS_NAO.search(txt)


def test_linhas_de_juros_pagos_entram():
    for txt in ("Juros pagos sobre empréstimos e financiamentos", "Amortizações de juros de financiamentos",
                "Empréstimos, Financiamentos e Debêntures - Juros e Derivativos Pagos",
                "Financiamentos e debêntures - Juros e derivativos (pagos) ou recebidos",   # UGPA3 no ITR
                "Encargos de dívidas e debêntures pagos", "Pagamento por Empréstimos - Juros"):
        assert _pagos(txt), txt


def test_linhas_que_nao_sao_custo_de_divida_ficam_fora():
    for txt in ("Dividendos e juros sobre o capital próprio pagos", "Juros recebidos de aplicações financeiras",
                "Juros sobre capital próprio recebidos", "Pagamento de principal e juros - arrendamentos",
                "Despesas com Juros"):
        assert not _pagos(txt), txt


def test_fallback_para_despesa_bruta():
    assert juros_do_periodo({"juros_pagos": 500.0, "desp_fin": -900.0}) == (500.0, "juros pagos (DFC)")
    assert juros_do_periodo({"juros_pagos": 0.0, "desp_fin": -900.0}) == (900.0, "despesa financeira bruta (DRE)")
    assert juros_do_periodo({})[0] == 0


def test_defasagem_ponderada_e_nao_pago_conta_como_atrasado():
    ev = lambda com, pag, v, t="JCP": {"data_com": com, "pagamento": pag, "valor": v, "tipo": t}
    si = {"X": {"eventos": [ev("01/03/2025", "01/05/2025", 1.0),            # 2 meses
                            ev("01/03/2025", "01/09/2025", 1.0),            # 6 meses
                            ev("01/03/2025", "01/03/2025", 1.0, "Amortização"),   # fora
                            ev("01/03/2026", "01/05/2026", 9.0)]},          # fora da janela 2023–25
          "Y": {"eventos": [ev("05/10/2024", "-", 1.0)]}, "Z": {"eventos": []}}
    assert defasagem.defasagem_meses("X", si) == 4.0
    assert defasagem.defasagem_meses("Y", si) == 24.0     # 05/10/2024 → 05/10/2026
    assert defasagem.defasagem_meses("Z", si) == 0.0
