# DECISOES
*Registro de decisões reversíveis tomadas pela rotina (decide, registra, segue) e das respondidas pelo Frank. Formato: data · decisão · motivo · como reverter. Decisões de doutrina vão ao `09-diario-de-decisoes.md`, não aqui.*

| Data | Decisão | Quem | Motivo | Reverter |
|---|---|---|---|---|
| 13/10/2026 | Branch principal é `master` (não `main`); hooks e CLAUDE.md usam `master` | Frank | Já existe assim no GitHub | — |
| 13/10/2026 | Manter no repo privado os tickers da carteira (sem quantidade, preço, valor ou corretora) | Frank (opção A) | Rotina precisa saber o que é carteira; reescrever histórico quebraria hall e diário | Mover para `carteira.local.md` ignorado + `filter-repo` (precisa "ok" explícito) |
| 13/10/2026 | Stop-hook: testes passam → commit+push em `master`; falham ou não há teste mapeado para código → ramo `wip/auto` (sem mexer na árvore) | Claude | Regra "nada na principal sem testes verdes" | Remover o hook `Stop` de `.claude/settings.json` |
| 13/10/2026 | Dados que dependem dos ZIPs da CVM/backtest são tipo `local`, não rodam na nuvem | Claude | Nuvem só enxerga o GitHub | — |
