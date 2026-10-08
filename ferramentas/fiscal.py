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
}
