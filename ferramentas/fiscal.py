"""Créditos de IR com prazo declarados (doutrina v2.3, §2) — fonte única para o hall (lotes) e para o dossiê (fichas).

Cada entrada vira `Industrial(aliquota_fase=...)`: até `ate` vale a alíquota efetiva (mediana de 5 anos, presa entre 0 e 34%);
depois, 34% na perpetuidade e no WACC. O benefício da fase entra em valor presente à parte (`motor_nao_financeiras.beneficio_fiscal`).
Prazo sem fonte A/B não entra: a fase acaba no PRIMEIRO prazo documentado (conservador).
"""

ALIQUOTA_FASE = {
    "HYPE3": {
        "ate": 2030,
        "fonte": "ágio amortizável fiscalmente até 2030, R$ 475 mi restantes (release 4T25, p. 11) [A]; a subvenção de ICMS de Goiás "
                 "termina com a reforma tributária, mas a EC 132/2023 e a LC 214/2025 não foram conferidas na fonte (planalto.gov.br "
                 "recusou a conexão em 07/10/2026) → a fase acaba no 1º prazo documentado, 2030",
        "nota_fonte": "A",        # fase 3, fatia 3: nota declarada (procedencia._origem_do_dado); a efetiva da fase vem da CVM
    },
    # PRIO3 (08/10/2026): o IR baixo vem do uso de prejuízo fiscal acumulado — crédito FINITO: base de R$ 28,8 bi, crédito de
    # R$ 9,39 bi, R$ 8,09 bi reconhecidos (inclui os R$ 6,37 bi da Forte reconhecidos em 2024), uso limitado a 30% do lucro
    # tributável por ano; a administração projeta 96,5% realizados até 2032. O resto (alíquotas reduzidas EUA/Luxemburgo, efeito
    # da moeda funcional em dólar) não tem prazo nem permanência com fonte → 34% depois da fase. Conciliação da alíquota efetiva:
    # DFP 2022 nota 30, 2023 nota 25, 2024 nota 26, 2025 nota 27 [A].
    "PRIO3": {
        "ate": 2032,
        "fonte": "PRIO DFP 2025 nota 16 (p. impressas 78–79): cronograma de realização dos prejuízos fiscais, R$ 8,09 bi "
                 "reconhecidos, 96,5% até 2032 — projeção da administração [A]",
        "nota_fonte": "A",
    },
}

# TIMS3 (08/10/2026): a mediana de 5 anos de −IR ÷ LAIR é 5,4% por JCP (permanente) + redução de 75% do IRPJ da SUDENE/SUDAM
# (laudos de 10 anos por UF, renováveis; vigência por UF não encontrada nos DFPs → prazo sem fonte = zero, doutrina §2).
# Perpétua = mediana 2021–25 da alíquota sem a SUDENE e sem os itens pontuais, pela conciliação da alíquota efetiva dos DFPs
# consolidados (2023–25 nota 8.d; 2022 nota 35; 2021 pela controladora) [A].
# Fase 3, fatia 3 (20/10/2026): 2024–25 CALCULADOS — IR registrado e LAIR da CVM (dados abertos, `ir`/`lair`) + o incentivo
# SUDENE/SUDAM da conciliação (DFP 2025 nota 8.d, R$ mil, conferida no PDF do RI em 20/10/2026); 2021–23 = alíquotas ajustadas
# lidas em 08/10 nas DFPs 2022–24 (os itens pontuais de 2021–22 não estão nos dados abertos).
# Risco: autuação de R$ 355,6 mi (dez/2025) contesta a averbação dos laudos (DFP 2025, contingências, item viii).
TIMS3_SUDENE = {"2024": 333_359, "2025": 442_136}
TIMS3_AJUSTADA_LIDA = {"2021": 0.193, "2022": 0.045, "2023": 0.183}
TIMS3_FONTE = ("conciliação da alíquota efetiva das DFPs da TIM: 2024–25 = (IR registrado + incentivo SUDENE/SUDAM) ÷ LAIR, IR e LAIR "
               "dos dados abertos da CVM e o incentivo da nota 8.d da DFP 2025 (conferida 20/10/2026); 2021–23 da nota 8.d (DFP 2024), "
               "nota 35 (DFP 2022) e controladora (2021), lidas em 08/10/2026; mediana 2021–25 (fiscal.tims3_aliquota)")


def tims3_ajustada(cvm_anual: dict) -> dict[str, float]:
    """Alíquota sem SUDENE por ano: 2024–25 calculadas da CVM + nota; 2021–23 as lidas na conciliação."""
    out = dict(TIMS3_AJUSTADA_LIDA)
    for ano, sudene in TIMS3_SUDENE.items():
        d = cvm_anual[ano]
        out[ano] = (-d["ir"] + sudene) / d["lair"]
    return out


def tims3_aliquota(cvm_anual: dict) -> float:
    """Mediana 2021–25 da alíquota ajustada, arredondada a 0,1 p.p. (a precisão da conciliação lida)."""
    import statistics as st
    return round(st.median(tims3_ajustada(cvm_anual).values()), 3)
