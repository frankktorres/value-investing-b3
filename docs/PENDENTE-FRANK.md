# PENDENTE-FRANK
*A rotina escreve aqui só o que trava em decisão, senha, dinheiro ou apagar dados. Frank: responda na linha e mova para `DECISOES.md`. Itens do `BACKLOG.md` tipo "decisão Frank" estão resumidos aqui.*

## Abertas
| # | Pergunta | Opções / recomendação | Backlog | Desde |
|---|---|---|---|---|
| 11 | Fase 3 (H10, A1) pronta no ramo `claude/fase3-bugs`. De manhã: `cd ferramentas && python -m pytest --ignore=backtest -q` (golden vai acusar as palavras), `python rodar_tudo.py --motivo "Fase 3: H10 e A1"`, ler o que mudou e dar ok para juntar. | Na nuvem só a PETR4 muda: central 53,48 → 52,87, JUSTA → JUSTA (09 de 23/10). Parecer do oráculo: RESSALVA (ver #12 e BACKLOG O3b) | O3 | 23/10 |
| 12 | Perguntas de doutrina da Fase 3: (a) §2 do `01` (l.26) diz E = "valor central × ações"; com o A1 o E é o central ANTES do desconto de controlador — reescrever o §2? (b) LEVE3: a tela mostra o veredito gravado (JUSTA, 06/10) com a régua suspensa, e o motor de hoje dá NÃO CONCLUSIVO — manter "dossiê vence" ou mostrar a palavra do motor? (c) trava de coerência (§9 3b) só na JUSTA final: estender a BARATA/RADAR? (d) DDM de contrato finito (BBSE3/CXSE3): com g no teto, o dividendo terminal usa o payout da ficha e não o coerente 1 − g ÷ ROE (subavalia) | (a) sim, só texto (recomendado: é o que o §5 já exige); (b) manter (recomendado; some quando o dossiê for refeito com `--data` nova); (c) não por ora (o 01 v2.6 decidiu a JUSTA final; mudar é variante do pré-registro); (d) usar 1 − g ÷ ROE no terminal (recomendado; é a fórmula do P/VP justificado do próprio motor) — muda palavra, vira variante | O3 | 23/10 |
| 4 | Orçamento mensal; SaaS só seu ou de terceiros; objetivo acadêmico; agente de sexta ainda roda?; fonte paga; licença do código | Ver Brief §11 | B07 | 10/10 |

## Só do Frank (a rotina nunca faz)
- Executar qualquer compra ou venda (inclui a posição em ITSA4, acima da saída).
- Senhas, tokens e chaves; apagar dados.
- Temporada 3T26 e monitor de sexta rodam na máquina dele (dados fora do git).

## Respondidas
- **22/10 — #10 (contraste, N5):** (a) contornos de chip ficam como estão; o chip já leva palavra e glifo (WCAG 1.4.11 não se aplica a contorno de reforço) → `DECISOES.md`.
- **21/10 — #8 (B26):** (a) sem controlador nem acordo no FRE = razão válida → `DECISOES.md`.
- **21/10 — #9 (§7):** "ok §7" → doutrina 2.6.1, casos com ano e fonte; nenhum carimbo sai → `DECISOES.md`, `09`.
- **21/10 — #7 (EGIE3):** lido nos ZIPs (nota A): "UBP de 2024" era a venda da TAG (DFP 2024, 3.04.04.02, R$ 1.336,1 mi); a repactuação do UBP é do 2T26 (3.06.01.01, R$ 1.921,5 mi bruto). Rótulos e carimbo corrigidos; nenhum número mudou → `09` de 21/10.
- **19/10 — #1 (B04):** sem mínimo/máximo nem limite de queda; carteira guiada pela palavra; meta de renda mensal (valor fora do git) → `DECISOES.md`.
- **19/10 — #5 (B08):** "você escolhe" → ALLD3, FESA4, SHUL4, VLID3 → `DECISOES.md`.
- **14/10 — #2 (B05):** exigir razão não vazia no motor; razões entram no dossiê → `DECISOES.md`, missão B24.
- **14/10 — #3 (B06):** critério contínuo + comparador = média do hall + uma linha por (ticker, rodada) → `DECISOES.md`, missão B25.
- **14/10 — #6 (B18/B19):** backtest e 2º comitê seguem parados → `DECISOES.md`.
