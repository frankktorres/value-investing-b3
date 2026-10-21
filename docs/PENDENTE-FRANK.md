# PENDENTE-FRANK
*A rotina escreve aqui só o que trava em decisão, senha, dinheiro ou apagar dados. Frank: responda na linha e mova para `DECISOES.md`. Itens do `BACKLOG.md` tipo "decisão Frank" estão resumidos aqui.*

## Abertas
| # | Pergunta | Opções / recomendação | Backlog | Desde |
|---|---|---|---|---|
| 7 | **EGIE3, carimbo "lucro não recorrente (UBP R$ 1,3 bi)"**: o repo chama de "UBP de 2024" (`03-hall:33`, `lote6_textos.py:115`, `gerar_pdf_lote6.py:612`); a imprensa (nota C, só pista) põe uma repactuação de UBP de R$ 1,3 bi no **2T26**, e o não recorrente de 2024 foi a venda da TAG. | Recomendo: eu leio o ITR 2T26 e o DFP 2024 da Engie (ZIPs locais) numa sessão de dia e corrijo ano e conta; o carimbo fica até lá (é conservador) | QA 21/10 | 21/10 |
| 8 | **Critério do B26**: o FRE 2026 confirma (conferido em 21/10, nota A) zero controlador e zero acordo em PRIO3, KEPL3, RECV3, VBBR3 e B3SA3. A pergunta é de julgamento: acionista relevante sem controle formal (ex.: RECV3, maior fora do free float ~19,6%) conta como "dono" para o §5? | (a) manter: sem controlador nem acordo no FRE = razão válida (recomendado; é o que a CVM registra); (b) exigir também nenhum acionista > X% | QA 21/10 | 21/10 |
| 9 | **Casos do §7 sem ano nem fonte**: "Brent 104" (EIA: média 2022 = 100,93; set/2026 = 114,16), Vibra "+300% a/a", Mahle "R$ 121 mi / ROE 77% / ROIC 30%", Unipar "240% do lucro". Os carimbos em `carimbos.py` dependem deles | Recomendo: sessão de dia lê os DFP (ZIPs locais), põe ano e fonte em cada caso e decide se o carimbo ainda vale em 2026; mexer no §7 = registro no `09` | QA 21/10 | 21/10 |
| 4 | Orçamento mensal; SaaS só seu ou de terceiros; objetivo acadêmico; agente de sexta ainda roda?; fonte paga; licença do código | Ver Brief §11 | B07 | 10/10 |

## Só do Frank (a rotina nunca faz)
- Executar qualquer compra ou venda (inclui a posição em ITSA4, acima da saída).
- Senhas, tokens e chaves; apagar dados.
- Temporada 3T26 e monitor de sexta rodam na máquina dele (dados fora do git).

## Respondidas
- **19/10 — #1 (B04):** sem mínimo/máximo nem limite de queda; carteira guiada pela palavra; meta de renda mensal (valor fora do git) → `DECISOES.md`.
- **19/10 — #5 (B08):** "você escolhe" → ALLD3, FESA4, SHUL4, VLID3 → `DECISOES.md`.
- **14/10 — #2 (B05):** exigir razão não vazia no motor; razões entram no dossiê → `DECISOES.md`, missão B24.
- **14/10 — #3 (B06):** critério contínuo + comparador = média do hall + uma linha por (ticker, rodada) → `DECISOES.md`, missão B25.
- **14/10 — #6 (B18/B19):** backtest e 2º comitê seguem parados → `DECISOES.md`.
