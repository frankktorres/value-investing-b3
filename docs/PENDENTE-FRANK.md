# PENDENTE-FRANK
*A rotina escreve aqui só o que trava em decisão, senha, dinheiro ou apagar dados. Frank: responda na linha e mova para `DECISOES.md`. Itens do `BACKLOG.md` tipo "decisão Frank" estão resumidos aqui.*
*O que é do Frank (CLAUDE.md, "Quem decide"): mudar palavra (motor, doutrina, régua, golden), aceitar risco que o `oraculo` bloqueou, gastar dinheiro, apagar/reescrever histórico, mudar o `00-DNA.md`, liberar config de qualidade/travas (`MESA_LIBERA_CONFIG`), senha/chave. Toda pergunta leva **recomendação + porquê em 1 linha**; quem registra segue em outra tarefa.*

## Abertas
| # | Pergunta | Opções / recomendação | Backlog | Desde |
|---|---|---|---|---|
| 13 | **Trava de ordem (emenda 7) reprova para sempre o commit 2c7c87a**: a emenda 13 (B57) foi commitada junto com `docs/b57/FONTES-B57.md` (fichas de fonte, sem código), e o `oraculo/ordem.py` exige pré-registro sozinho; a emenda 13 não conta como registrada e todo commit que a cita reprova. A regra foi escrita antes do resultado (2c7c87a vem antes do motor no git), mas a trava não tem como saber. Erro do Claude, 25/11. **O `oraculo` BLOQUEIA por isso** (conteúdo aprovado): a B57 inteira (motor, coletor, séries, B46 8/24, docs) está no ramo **`b57-x2-altman`**, fora do `master`; golden igual, nenhuma palavra muda. Com a sua decisão, a exceção entra e o ramo junta no `master` | **(A, recomendo)** exceção pontual em `ordem.py` que amarra o SHA completo de 2c7c87a **e** o conjunto exato de arquivos extras `{docs/b57/FONTES-B57.md}`; a emenda 13 passa a contar como registrada; canários: outro SHA com o mesmo arquivo reprova, e 2c7c87a com outro conjunto reprova — conserta só este caso. (B) aceitar `docs/b*/FONTES-*.md` junto do pré-registro sempre: afrouxa a regra. (C) deixar a falha para sempre: um portão bloqueante vermelho em toda rodada esconde a próxima falha real. (D) mover o `CORTE` para 2c7c87a: perde a reconferência de b07482a..2c7c87a. Mexer em trava = `MESA_LIBERA_CONFIG=1` (seu) | B57 | 25/11 |
| 14 | **Fechar a causa (a) do DNA §4 "como está, com motivo"?** Sem hipótese autorizada aberta: B39 não disparou, B46 encerrada (7/24 e 8/24 NÃO CONCLUSIVAS), B35 fora até o HOLD-OUT 2 (#12) | **Sim, recomendo** (`senior`, 25/11): o Ke > 30% já sai NÃO CONCLUSIVO pela regra da H2 (emenda 3) e é medido no M1 (critério "Ke > 30% ≤ 1"); seguir para (b) e (c). Não: escolher nova hipótese para o π (outra emenda, gasta tentativa) | B39, B46, B35 | 25/11 |
| 4 | Orçamento mensal; SaaS só seu ou de terceiros; objetivo acadêmico; agente de sexta ainda roda?; fonte paga; licença do código | Ver Brief §11 | B07 | 10/10 |

## Só do Frank (a rotina nunca faz)
- Executar qualquer compra ou venda (inclui a posição em ITSA4, acima da saída).
- Senhas, tokens e chaves; apagar dados.
- Temporada 3T26 e monitor de sexta rodam na máquina dele (dados fora do git).

## Respondidas
- **25/11 — #12 (B46 + B35):** B46 **sim**; B35 **não** (a B39 corrigida não disparou; fica até o HOLD-OUT 2) → `DECISOES.md`, `BACKLOG.md`.
- **22/10 — #10 (contraste, N5):** (a) contornos de chip ficam como estão; o chip já leva palavra e glifo (WCAG 1.4.11 não se aplica a contorno de reforço) → `DECISOES.md`.
- **21/10 — #8 (B26):** (a) sem controlador nem acordo no FRE = razão válida → `DECISOES.md`.
- **21/10 — #9 (§7):** "ok §7" → doutrina 2.6.1, casos com ano e fonte; nenhum carimbo sai → `DECISOES.md`, `09`.
- **21/10 — #7 (EGIE3):** lido nos ZIPs (nota A): "UBP de 2024" era a venda da TAG (DFP 2024, 3.04.04.02, R$ 1.336,1 mi); a repactuação do UBP é do 2T26 (3.06.01.01, R$ 1.921,5 mi bruto). Rótulos e carimbo corrigidos; nenhum número mudou → `09` de 21/10.
- **19/10 — #1 (B04):** sem mínimo/máximo nem limite de queda; carteira guiada pela palavra; meta de renda mensal (valor fora do git) → `DECISOES.md`.
- **19/10 — #5 (B08):** "você escolhe" → ALLD3, FESA4, SHUL4, VLID3 → `DECISOES.md`.
- **14/10 — #2 (B05):** exigir razão não vazia no motor; razões entram no dossiê → `DECISOES.md`, missão B24.
- **14/10 — #3 (B06):** critério contínuo + comparador = média do hall + uma linha por (ticker, rodada) → `DECISOES.md`, missão B25.
- **14/10 — #6 (B18/B19):** backtest e 2º comitê seguem parados → `DECISOES.md`.
