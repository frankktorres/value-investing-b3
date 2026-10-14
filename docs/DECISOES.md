# DECISOES
*Registro de decisões reversíveis tomadas pela rotina (decide, registra, segue) e das respondidas pelo Frank. Formato: data · decisão · motivo · como reverter. Decisões de doutrina vão ao `09-diario-de-decisoes.md`, não aqui.*

| Data | Decisão | Quem | Motivo | Reverter |
|---|---|---|---|---|
| 13/10/2026 | Branch principal é `master` (não `main`); hooks e CLAUDE.md usam `master` | Frank | Já existe assim no GitHub | — |
| 13/10/2026 | Manter no repo privado os tickers da carteira (sem quantidade, preço, valor ou corretora) | Frank (opção A) | Rotina precisa saber o que é carteira; reescrever histórico quebraria hall e diário | Mover para `carteira.local.md` ignorado + `filter-repo` (precisa "ok" explícito) |
| 13/10/2026 | Stop-hook: testes passam → commit+push em `master`; falham ou não há teste mapeado para código → ramo `wip/auto` (sem mexer na árvore) | Claude | Regra "nada na principal sem testes verdes" | Remover o hook `Stop` de `.claude/settings.json` |
| 13/10/2026 | Dados que dependem dos ZIPs da CVM/backtest são tipo `local`, não rodam na nuvem | Claude | Nuvem só enxerga o GitHub | — |
| 13/10/2026 | B10: `requirements.lock` sem hashes (só `pip freeze` do fechamento transitivo, referência); lista de tickers da carteira em `ferramentas/carteira_tickers.json` | Claude | Uso pessoal, sem deploy; hashes travariam wheels por plataforma (Windows do Frank vs nuvem) | Apagar o lock e voltar `CARTEIRA` para o código |
| 14/10/2026 | B05/AUD-41: o motor passa a exigir razão não vazia para desconto de controlador; as 29 razões entram nos dossiês. Implementação = missão B24 (muda motor → teste verde + registro no `09`) | Frank (aceitou a recomendação) | Zero sem razão é afirmação sem fonte | Voltar o campo a opcional no `filtros_1a4` |
| 14/10/2026 | B06/AUD-32/98/99: pré-registro com critério contínuo (postos P/C × retorno excedente), comparador = média do hall (não Ibovespa), uma linha por (ticker, rodada). Implementação = missão B25 | Frank (aceitou a recomendação) | Validação só prospectiva precisa de critério fixo antes do resultado | Reabrir no `09` antes da próxima rodada |
| 14/10/2026 | B18/B19: backtest (proxy 70,7% < portão 80%) e 2º comitê/Desktop continuam parados | Frank (aceitou a recomendação) | Portão falhou; comitê "não tem ajudado" | Reabrir com decisão explícita |
| 14/10/2026 | B24: a trava da razão do desconto de controlador fica em `exigir_declaracoes`/`exigir_razao_desconto` (a função `filtros_1a4` não existe); sem fonte A/B a razão é o marcador `SEM_RAZAO` ("sem razão documentada"), 28 tickers; só LEVE3 com fonte A (D3 do dossiê) | Claude | Não inventar razão; o texto das fichas só cita PDFs próprios (sem nota A/B) | Trocar o marcador pela razão com fonte; tirar a chamada do motor |
