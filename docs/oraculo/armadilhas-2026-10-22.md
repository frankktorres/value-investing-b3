# Teste das armadilhas do oráculo automático — 2026-10-22

Gerado por `cd ferramentas && python -m oraculo.armadilhas` (docs/ORACULO.md §2). Automático = suíte (golden regravado no worktree; camada 0 não conta) + `python -m oraculo`. Alçada decidida antes de medir.

**Automático: deixou passar 01.**

| # | defeito | camada | alçada | suíte pegou | oráculo pegou (checks) | 1ª falha da suíte | palavras que mudam |
|---|---|---|---|---|---|---|---|
| 01 | zero silencioso novo: lucro ausente vira 0 (Piotroski, Sloan, OE) | 2 | automatico, agente | não | não (—) | — | nenhuma |
| 02 | real × nominal: OE em R$ de hoje capitalizado ao Ke nominal | 1 | automatico, agente | sim | não (—) | FAILED tests\test_hall03.py::test_03_bate_com_o_motor - AssertionError: VIVT3... | FLRY3 CARA → NÃO CONCLUSIVO; UGPA3 CARA → NÃO CONCLUSIVO |
| 03 | sinal invertido na dívida líquida da ponte firma → acionista (EPV) | 1 | automatico, agente | sim | sim (propriedades, sanidade) | FAILED tests\test_b23_petr4_premissas.py::test_ficha_monta_com_a_tabela - Key... | FLRY3 CARA → NÃO CONCLUSIVO; GGBR4 CARA → JUSTA; HYPE3 CARA → NÃO CONCLUSIVO; PETR4 JUSTA → NÃO CONCLUSIVO; RANI3 CARA → NÃO CONCLUSIVO; SMTO3 CARA → NÃO CONCLUSIVO; SUZB3 CARA → NÃO CONCLUSIVO; UGPA3 CARA → NÃO CONCLUSIVO; UNIP6 CARA → NÃO CONCLUSIVO; VBBR3 CARA → NÃO CONCLUSIVO |
| 04 | unidade: ações em milhares da CVM tomadas como unidades (lote 3) | 4 | automatico, agente | sim | sim (reconciliacao) | FAILED tests\test_hall03.py::test_03_bate_com_o_motor - AssertionError: KEPL3... | KEPL3 JUSTA → BARATA; RANI3 CARA → RADAR; VBBR3 CARA → RADAR |
| 05 | régua afrouxada sem registro: BARATA ≤ 0,75 | 1 | automatico, agente | sim | não (—) | FAILED tests\test_aud27_31_formulas.py::test_aud88_borda_da_regua_pertence_a_faixa_de_baixo[0.7001-RADAR] | nenhuma |
| 06 | premissa digitada sem fonte que muda palavra (g real da KEPL3 1% → 3%) | 7 | agente | sim | não (—) | FAILED tests\test_hall03.py::test_03_bate_com_o_motor - AssertionError: KEPL3... | nenhuma |
| 07 | golden regravado sem a camada que provou o valor no motivo | 7 | agente | não | não (—) | — | nenhuma |
| 08 | variante v3 (prêmio 4,5 p.p.) sem linha no §6 do pré-registro | 7 | agente | sim | sim (sanidade) | FAILED tests\test_aud17_ddm_analitico.py::test_ke_do_mercado_do_teste - asser... | ISAE4 NÃO CONCLUSIVO → JUSTA; LEVE3 NÃO CONCLUSIVO → RADAR |
