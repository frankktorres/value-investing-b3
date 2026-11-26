# Hold-out B36 — método v2.7 congelado em 20 ações fora do hall (novembro de 2026)

*Gerado por `ferramentas/holdout_b36/relatorio.py` só a partir dos JSONs de `ferramentas/holdout_b36/` (cadastro, tempos dos insumos, resultados). Regra, lista, ficha-padrão, protocolo, critério e previsões: emenda 8 do `docs/PRE-REGISTRO-v3.md`, escrita antes de rodar. Data-base T = 19/11/2026. Nenhum número aqui é ordem de compra ou venda.*

## Resultado: **NÃO PASSOU** (1 de 6 linhas do critério)

| # | Linha do critério (emenda 8) | Limite | Observado | Passou? |
|---|---|---|---|---|
| 1 | rodam sem erro (palavra, NÃO CONCLUSIVO incluso) | ≥ 16 de 20 | 14 | **não** |
| 2 | NÃO CONCLUSIVO entre as que rodam | ≤ 6 | 9 | **não** |
| 3 | Ke nominal > 30% | ≤ 2 | 3 | **não** |
| 4 | valor absurdo (central ≤ 0, P/C < 0,2 ou > 5) | ≤ 2 | 6 | **não** |
| 6 | vazios ÷ insumos não automáticos, mediana das 20 | ≤ 50% | 75% (só as que rodam: 71%) | **não** |
| 7 | tempo por ação (coleta + insumos + avaliação), mediana das 20 | ≤ 20 min | 2,6 min (só as que rodam: 3,4 min) | sim |

**Relatado fora do critério (§0.3):** palavras das que rodam: CARA 4, NÃO CONCLUSIVO 9, RADAR 1; nº de BARATA: 0; P/C mediano das que rodam 3,26 × hall 1,82 (41 do golden); dispersão > 1,8×: 10 (EMBJ3, RADL3, RAIL3, SMFT3, CSNA3, GOAU4, USIM5, MOVI3, AZZA3, BEEF3); erros explícitos do motor: 6; % de insumos automáticos por ação: mediana 43,2% (mín. 40,5%, máx. 55,6%).

## Por ação

Tempo em minutos de relógio: coleta (CVM, B3, StatusInvest) + subagente do protocolo + avaliação. Chamadas = ferramentas usadas pelo subagente (contagem do harness). Classes: automático / pesquisa / vazio (emenda 8: a classe sai do código). "Vazio" = vazios ÷ (pesquisa + vazio).

| # | Ação | Tipo | Palavra | P/C | Ke nominal | Dispersão | Motivo | Tempo (min) | Chamadas | Auto / Pesq / Vazio | % auto | Vazio |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | BPAC11 | banco | CARA | 3,04 | 20,6% | 1,04 | régua do P/C (CARA) | 0,1 + 2,7 + 0,1 = **2,9** | 22 | 10 / 2 / 8 | 50,0% | 80% |
| 2 | EMBJ3 | industrial | NÃO CONCLUSIVO | 36,20 | 21,2% | inf | dispersão das âncoras inf× > 1,8×; valor absurdo (P/C 36,20) | 0,8 + 4,0 + 0,0 = **4,9** | 22 | 15 / 7 / 15 | 40,5% | 68% |
| 3 | EQTL3 | utility | CARA | 2,59 | 20,6% | 1,35 | régua do P/C (CARA) | 0,8 + 1,6 + 0,0 = **2,5** | 17 | 10 / 2 / 6 | 55,6% | 75% |
| 4 | ENEV3 | utility | CARA | 39,95 | 20,6% | 1,00 | régua do P/C (CARA); valor absurdo (P/C > 5) | 0,8 + 1,1 + 0,0 = **1,9** | 13 | 10 / 2 / 6 | 55,6% | 75% |
| 5 | RADL3 | industrial | NÃO CONCLUSIVO | 3,47 | 21,9% | 3,16 | dispersão das âncoras 3,16× > 1,8× | 0,8 + 1,9 + 0,1 = **2,7** | 12 | 16 / 6 / 15 | 43,2% | 71% |
| 6 | RAIL3 | industrial | NÃO CONCLUSIVO | inf | 24,9% | inf | dispersão das âncoras inf× > 1,8×; valor absurdo (central -3,03 ≤ 0) | 0,7 + 3,8 + 0,0 = **4,6** | 26 | 16 / 5 / 16 | 43,2% | 76% |
| 7 | ENGI11 | utility | CARA | 1,81 | 20,6% | 1,20 | régua do P/C (CARA) | 0,8 + 0,9 + 0,0 = **1,7** | 9 | 10 / 2 / 6 | 55,6% | 75% |
| 8 | CSAN3 | industrial | erro | — | — | — | NotImplementedError em proventos_hall.py:207: CSAN3: evento CIS RED CAP sem semântica conferida — ajustar à mão | 0,8 + 0,0 + 0,0 = **0,8** | 0 | 15 / 0 / 22 | 40,5% | 100% |
| 9 | SMFT3 | industrial | NÃO CONCLUSIVO | inf | 25,5% | inf | dispersão das âncoras inf× > 1,8×; valor absurdo (central 0,00 ≤ 0) | 0,7 + 1,8 + 0,0 = **2,5** | 11 | 16 / 5 / 16 | 43,2% | 76% |
| 10 | MBRF3 | industrial | erro | — | — | — | ValueError em base.py:189: MBRF3: sem capital integralizado no FRE 2026 | 0,7 + 0,0 + 0,0 = **0,7** | 0 | 15 / 0 / 22 | 40,5% | 100% |
| 11 | CSNA3 | industrial | NÃO CONCLUSIVO | 1,89 | 62,2% | inf | Ke nominal 62,2% > 30%; dispersão das âncoras inf× > 1,8× | 0,7 + 4,0 + 0,0 = **4,8** | 21 | 16 / 6 / 15 | 43,2% | 71% |
| 12 | GOAU4 | industrial | NÃO CONCLUSIVO | 1,32 | 24,8% | 3,67 | dispersão das âncoras 3,67× > 1,8× | 0,7 + 3,1 + 0,0 = **3,9** | 15 | 16 / 7 / 14 | 43,2% | 67% |
| 13 | USIM5 | industrial | RADAR | 0,55 | 24,1% | 2,28 | régua do P/C (RADAR) | 0,7 + 3,6 + 0,0 = **4,4** | 21 | 16 / 7 / 14 | 43,2% | 67% |
| 14 | TEND3 | industrial | erro | — | — | — | NotImplementedError em proventos_hall.py:207: TEND3: evento INCORPORACAO sem semântica conferida — ajustar à mão | 1,0 + 0,0 + 0,0 = **1,0** | 0 | 15 / 0 / 22 | 40,5% | 100% |
| 15 | NATU3 | industrial | erro | — | — | — | NotImplementedError em proventos_hall.py:207: NATU3: evento INCORPORACAO sem semântica conferida — ajustar à mão | 0,5 + 0,0 + 0,0 = **0,5** | 0 | 15 / 0 / 22 | 40,5% | 100% |
| 16 | MOVI3 | industrial | NÃO CONCLUSIVO | inf | 61,9% | inf | Ke nominal 61,9% > 30%; dispersão das âncoras inf× > 1,8×; valor absurdo (central 0,00 ≤ 0) | 0,7 + 2,9 + 0,0 = **3,6** | 20 | 16 / 6 / 15 | 43,2% | 71% |
| 17 | MRVE3 | industrial | erro | — | — | — | NotImplementedError em proventos_hall.py:207: MRVE3: evento CIS RED CAP sem semântica conferida — ajustar à mão | 0,7 + 0,0 + 0,0 = **0,7** | 0 | 15 / 0 / 22 | 40,5% | 100% |
| 18 | AZZA3 | industrial | NÃO CONCLUSIVO | 0,58 | 25,2% | 3,05 | dispersão das âncoras 3,05× > 1,8× | 0,7 + 3,4 + 0,0 = **4,1** | 27 | 16 / 6 / 15 | 43,2% | 71% |
| 19 | IGTI11 | industrial | erro | — | — | — | ValueError em proventos_hall.py:324: IGTI11: 3 linhas iguais de DIVIDENDO com data-com 2025-04-17 na B3 — parcela ou repetição? Conferir o total na DMPL da CVM e classificar em  | 0,6 + 0,0 + 0,0 = **0,6** | 0 | 15 / 0 / 22 | 40,5% | 100% |
| 20 | BEEF3 | industrial | NÃO CONCLUSIVO | 6,69 | 48,5% | 7,42 | Ke nominal 48,5% > 30%; dispersão das âncoras 7,42× > 1,8×; valor absurdo (P/C 6,69) | 0,5 + 2,5 + 0,1 = **3,2** | 19 | 15 / 7 / 15 | 40,5% | 68% |

## Previsto × observado (previsões da emenda 8, escritas antes de rodar)

| Ação | Previsto | Observado | Confere? |
|---|---|---|---|
| BPAC11 | roda (motor de banco) | CARA | sim |
| EMBJ3 | erro | NÃO CONCLUSIVO (valor absurdo) | **não** |
| EQTL3 | roda | CARA | sim |
| ENEV3 | valor absurdo (P/C > 5) | CARA (valor absurdo) | sim |
| RADL3 | roda | NÃO CONCLUSIVO | sim |
| RAIL3 | roda | NÃO CONCLUSIVO (valor absurdo) | sim |
| ENGI11 | roda (regulado) | CARA | sim |
| CSAN3 | NÃO CONCLUSIVO | erro (NotImplementedError) | **não** |
| SMFT3 | roda | NÃO CONCLUSIVO (valor absurdo) | sim |
| MBRF3 | NÃO CONCLUSIVO (Ke > 30%) | erro (ValueError) | **não** |
| CSNA3 | roda | NÃO CONCLUSIVO (Ke > 30%) | sim |
| GOAU4 | roda, sem absurdo | NÃO CONCLUSIVO | sim |
| USIM5 | roda | RADAR | sim |
| TEND3 | roda | erro (NotImplementedError) | **não** |
| NATU3 | valor absurdo | erro (NotImplementedError) | **não** |
| MOVI3 | NÃO CONCLUSIVO (Ke > 30%) | NÃO CONCLUSIVO (Ke > 30%, valor absurdo) | sim |
| MRVE3 | roda | erro (NotImplementedError) | **não** |
| AZZA3 | NÃO CONCLUSIVO | NÃO CONCLUSIVO | sim |
| IGTI11 | valor absurdo | erro (ValueError) | **não** |
| BEEF3 | NÃO CONCLUSIVO (Ke > 30%) | NÃO CONCLUSIVO (Ke > 30%, valor absurdo) | sim |

Conferem 13 de 20.

## Por insumo

Quantas das ações de cada grupo tiveram o insumo automático, por pesquisa (protocolo, fonte A/B) ou vazio.


**Industrial** (16 ações)

| Insumo | Automático | Pesquisa | Vazio |
|---|---|---|---|
| séries DFP/ITR (CVM) | 16 | 0 | 0 |
| preço (COTAHIST) | 16 | 0 | 0 |
| ações (ITR) | 16 | 0 | 0 |
| proventos (B3) | 16 | 0 | 0 |
| defasagem (datas StatusInvest) | 16 | 0 | 0 |
| FRE: acionistas | 16 | 0 | 0 |
| FRE: remuneração | 16 | 0 | 0 |
| FRE: partes relacionadas (bruto) | 16 | 0 | 0 |
| nota moat (notas.py) | 16 | 0 | 0 |
| nota ciclo (notas.py) | 16 | 0 | 0 |
| nota gestão — base (notas.py) | 16 | 0 | 0 |
| ficha: ANOS | 16 | 0 | 0 |
| ficha: perfil | 16 | 0 | 0 |
| ficha: outras_liquidas | 16 | 0 | 0 |
| ficha: g_real | 16 | 0 | 0 |
| ma_ruim | 0 | 10 | 6 |
| interferencias | 0 | 10 | 6 |
| partes_rel_sobre_receita | 0 | 9 | 7 |
| tag_along | 0 | 10 | 6 |
| discricionario | 0 | 9 | 7 |
| r1_retido (Q4 da triagem) | 8 | 0 | 8 |
| fisher 1 | 0 | 1 | 15 |
| fisher 2 | 0 | 0 | 16 |
| fisher 3 | 0 | 0 | 16 |
| fisher 4 | 0 | 0 | 16 |
| fisher 5 | 0 | 3 | 13 |
| fisher 6 | 0 | 0 | 16 |
| fisher 7 | 0 | 0 | 16 |
| fisher 8 | 0 | 0 | 16 |
| fisher 9 | 0 | 1 | 15 |
| fisher 10 | 0 | 0 | 16 |
| fisher 11 | 0 | 0 | 16 |
| fisher 12 | 0 | 0 | 16 |
| fisher 13 | 0 | 6 | 10 |
| fisher 14 | 0 | 1 | 15 |
| fisher 15 | 0 | 2 | 14 |
| desconto_controlador | 0 | 0 | 16 |

**Financeira** (4 ações)

| Insumo | Automático | Pesquisa | Vazio |
|---|---|---|---|
| preço (COTAHIST) | 4 | 0 | 0 |
| VPA (StatusInvest) | 4 | 0 | 0 |
| LPA (StatusInvest) | 4 | 0 | 0 |
| ROE de 10 anos (StatusInvest) | 4 | 0 | 0 |
| ROE atual (StatusInvest) | 4 | 0 | 0 |
| DPA de 5 anos (StatusInvest) | 4 | 0 | 0 |
| JCP (StatusInvest) | 4 | 0 | 0 |
| P/L histórico (StatusInvest) | 4 | 0 | 0 |
| anos pagos (StatusInvest) | 4 | 0 | 0 |
| payout | 1 | 3 | 0 |
| prudencial cet1 | 0 | 1 | 0 |
| prudencial inad90 | 0 | 0 | 1 |
| prudencial cobertura | 0 | 0 | 1 |
| nota moat | 0 | 0 | 4 |
| nota gestao | 0 | 0 | 4 |
| nota controlador | 0 | 0 | 4 |
| nota ciclo | 0 | 0 | 4 |
| nota fisher | 0 | 0 | 4 |
| discricionario | 0 | 4 | 0 |
| desconto_controlador | 0 | 0 | 4 |
| solidez (alavancagem CVM) | 3 | 0 | 0 |

