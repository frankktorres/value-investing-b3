# RELATORIO-DIARIO
*Uma entrada por dia/turno, a mais nova em cima: o que foi feito (com commit), decisões tomadas, o que ficou, erros. Máx. 10 linhas por entrada.*

## 14/10/2026 — B24, B25, B23, B15, B11 (sessão do Frank)
- B24: o motor exige razão no desconto de controlador. 28 tickers ficaram com "sem razão documentada" e a LEVE3 com FRE nota A. **Nenhuma palavra mudou.**
- B25: pré-registro contínuo no `registro_prospectivo.py`: IC de postos P/C × retorno excedente, média do hall, uma linha por ticker×rodada.
- O adversário rodou nas duas. Achou e corrigiu: PDF do lote 2 que quebraria, citação errada da LEVE3, NaN do retorno que invertia a leitura.
- B23: tabela de P/C por premissa da PETR4 no gerador. O PDF não foi reemitido, porque outros campos informativos mudaram desde 09/10.
- B15: relatório `docs/PREMISSAS-B15.md` (445 campos digitados). Proposta de migração, nada movido.
- B11: termos da B3 lidos (só uso pessoal; dados históricos livres para distribuidor). StatusInvest segue 403.
- Suíte: 517 passed, 1 skipped (+ testes da B23). Precisa de você: colar os termos da StatusInvest (opcional).

## 14/10/2026 — turno noite (B12)
- Feito: B12 (AUD-96/65/87/48/105; só texto, rótulos e encoding). 473 passed, 19 skipped; nenhuma palavra mudou.
- Descobri: AUD-64 pede tabela nova na ficha da PETR4 — virou B23. Rodou no ramo `claude/keen-babbage-7m0ksr`, não `master`.
- Também: B13/B14 → `docs/SENSIBILIDADE-B13-B14.md` (5/41 mudam de palavra com π 4% ou rf ±1 p.p.; Ke KLBN11 54,7%). B11 travou: termos B3 (500) e StatusInvest (403) inacessíveis.
- Precisa de você: nada urgente; se quiser B11, cole os termos de uso.

## 13/10/2026 — turno noite (B09, B10)
- Feito: B09 (já registrado, nada a completar) e B10 (carteira em JSON só com tickers; `requirements.lock`). 473 passed, 19 skipped.
- Descobri: `python` padrão da nuvem não tem pytest (use `/usr/bin/python3`); 19 testes pulam por falta de dado da CVM.
- Precisa de você: nada novo. Próxima: B12.

## 13/10/2026 — preparação da rotina na nuvem
- Repo `frankktorres/value-investing-b3` (privado), `master` = `origin/master`.
- Varredura de segredos: arquivo atual e histórico sem tokens/chaves. Tickers da carteira ficam (decisão A, ver `DECISOES.md`).
- Criados: `docs/BACKLOG.md`, `PENDENTE-FRANK.md`, `DECISOES.md`, `MISSOES.md`, este relatório; `CLAUDE.md` ampliado; hooks em `.claude/settings.json`; skill `/fechar`.
- Hook Stop testado de verdade: doc → commit+push em `master`; teste vermelho → só `wip/auto` (árvore intacta); token falso → bloqueado. Suíte base: 491 passed, 1 skipped. Ramo `wip/auto` de teste apagado.
