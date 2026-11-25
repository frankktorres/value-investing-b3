# PENDENTE-FRANK
*A rotina escreve aqui só o que trava em decisão, senha, dinheiro ou apagar dados. Frank: responda na linha e mova para `DECISOES.md`. Itens do `BACKLOG.md` tipo "decisão Frank" estão resumidos aqui.*
*O que é do Frank (CLAUDE.md, "Quem decide"): mudar palavra (motor, doutrina, régua, golden), aceitar risco que o `oraculo` bloqueou, gastar dinheiro, apagar/reescrever histórico, mudar o `00-DNA.md`, liberar config de qualidade/travas (`MESA_LIBERA_CONFIG`), senha/chave. Toda pergunta leva **recomendação + porquê em 1 linha**; quem registra segue em outra tarefa.*

## Abertas
| # | Pergunta | Opções / recomendação | Backlog | Desde |
|---|---|---|---|---|
| 11 | **Fechar o furo do `--no-verify` na trava do push (B37).** Hoje `git push --no-verify` (ou mexer no `core.hooksPath`) pula o pre-push; o deny teria que entrar no `.claude/settings.json`, que a trava 4.2 protege — liberar é seu | **Recomendo (a):** abrir uma sessão com `MESA_LIBERA_CONFIG=1` no ambiente e pedir "aplicar o #11": acrescentar ao `deny` `"Bash(*--no-verify*)"`, `"Bash(*core.hooksPath*)"`, `"Bash(*hooksPath=*)"`; pôr `ferramentas/conferir_noite.py` e `ferramentas/tests/test_conferir_noite_travas.py` em `TRAVAS_ARQUIVOS` do `.claude/hooks/trava_config.py`; regravar `travas_hashes.json`. Por quê: 10 min, fecha o critério "não empurra master vermelho". (b) Mais forte, depois: o `trava_master.py` também recusar push que mexa em arquivo de trava sem a liberação | — (pacote de autonomia, senior) | 25/11 |
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
