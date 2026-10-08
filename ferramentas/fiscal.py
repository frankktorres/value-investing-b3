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
    },
}

# TIMS3 (08/10/2026): a mediana de 5 anos de −IR ÷ LAIR é 5,4% por JCP (permanente) + redução de 75% do IRPJ da SUDENE/SUDAM
# (laudos de 10 anos por UF, renováveis; vigência por UF não encontrada nos DFPs → prazo sem fonte = zero, doutrina §2).
# Perpétua = mediana 2021–25 da alíquota sem a SUDENE e sem os itens pontuais, pela conciliação da alíquota efetiva dos DFPs
# consolidados (2023–25 nota 8.d; 2022 nota 35; 2021 pela controladora) [A]: 19,3% (2021) · 4,5% (2022) · 18,3% (2023) · 22,1% (2024) · 15,1% (2025).
# Risco: autuação de R$ 355,6 mi (dez/2025) contesta a averbação dos laudos (DFP 2025, contingências, item viii).
TIMS3_ALIQUOTA = 0.183
