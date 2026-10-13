# RELATORIO-DIARIO
*Uma entrada por dia/turno, a mais nova em cima: o que foi feito (com commit), decisões tomadas, o que ficou, erros. Máx. 10 linhas por entrada.*

## 13/10/2026 — turno noite (B09, B10)
- Feito: B09 (já registrado, nada a completar) e B10 (carteira em JSON só com tickers; `requirements.lock`). 473 passed, 19 skipped.
- Descobri: `python` padrão da nuvem não tem pytest (use `/usr/bin/python3`); 19 testes pulam por falta de dado da CVM.
- Precisa de você: nada novo. Próxima: B12.

## 13/10/2026 — preparação da rotina na nuvem
- Repo `frankktorres/value-investing-b3` (privado), `master` = `origin/master`.
- Varredura de segredos: arquivo atual e histórico sem tokens/chaves. Tickers da carteira ficam (decisão A, ver `DECISOES.md`).
- Criados: `docs/BACKLOG.md`, `PENDENTE-FRANK.md`, `DECISOES.md`, `MISSOES.md`, este relatório; `CLAUDE.md` ampliado; hooks em `.claude/settings.json`; skill `/fechar`.
- Hook Stop testado de verdade: doc → commit+push em `master`; teste vermelho → só `wip/auto` (árvore intacta); token falso → bloqueado. Suíte base: 491 passed, 1 skipped. Ramo `wip/auto` de teste apagado.
