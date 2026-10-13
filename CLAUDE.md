# Mesa de Value Investing — B3

Leitura de partida: `README.md`. Doutrina vigente: `01-doutrina-value-investing.md`.
Pasta de histórico (versões substituídas): `_historico/`.

## Visão e stack
Mesa de análise fundamentalista da B3 (dividendos/JCP, longo prazo, uso pessoal): doutrina escrita (`01`) + motores de
valuation em Python (`ferramentas/`) → palavra por ticker (BARATA/JUSTA/CARA/NÃO CONCLUSIVO). Python 3.14, pandas/numpy/
reportlab/pytest; sem banco; dados brutos fora do git (`ferramentas/dados/`). Branch principal: `master`.

## Como rodar e testar
- `pip install -r requirements.txt` · `cd ferramentas && python -m pytest --ignore=backtest -q` (roda sem os ZIPs da CVM;
  skips por dado ausente aparecem com `-rs`). Suíte do `backtest/` (~13 min): só local, sozinha.
- `python rodar_tudo.py --motivo "..."` regrava o golden; só com motivo e decisão registrada.

## Rotina autônoma (nuvem, só enxerga o GitHub)
- Fila: `docs/MISSOES.md` (uma missão por turno) ← `docs/BACKLOG.md` (só tipo "executável"). Diário: `docs/RELATORIO-DIARIO.md`.
- **Decisão reversível = decide, registra em `docs/DECISOES.md` e segue.** Só parar (e escrever em `docs/PENDENTE-FRANK.md`) em:
  senha/chave, dinheiro, apagar dados. **Nunca executar nem sugerir como feita ordem de compra/venda.**
- Na nuvem os hooks de auto-commit não rodam (`CLAUDE_CODE_REMOTE`): rode os testes, `git add` de caminhos específicos,
  commit e `git push origin master` você mesmo; testes vermelhos → ramo `wip/auto`, nunca `master`.
- Mexer em motor/doutrina/golden muda palavra de investimento: só com teste verde e registro no `09`.

## O que não fazer
- Segredo (`.env*`, chaves, tokens) e dados pessoais (quantidade, preço médio, valores, corretora da carteira) no git.
  Tickers da carteira ficam (decisão de 13/10, `docs/DECISOES.md`).
- `git add .`, `push --force`, reescrever histórico, apagar arquivo (versão antiga vai para `_historico/`).
- Rodar `python -m dossie.gerar <TICKER>` sem `--data` nova (sobrescreve o veredito vigente).
- Prettier/formatador em arquivo existente; inventar dado, fonte ou número (só fonte nota A/B embasa decisão).
- `analisador/` está arquivado (fora do git); backtest parado.

## Turno dia/noite
- **Dia (Frank presente):** ele decide; a rotina não roda. Ao fim, `/fechar` (ou "vou parar" / "até amanhã") passa o pendente
  para `docs/MISSOES.md` e dá push.
- **Noite (Frank ausente, nuvem):** `git pull --ff-only` → ler `MISSOES.md` e `PENDENTE-FRANK.md` (respostas novas viram
  decisões) → executar a 1ª missão executável → testes → commit/push → entrada no `RELATORIO-DIARIO.md`. Travou em
  senha/dinheiro/apagar → registrar em `PENDENTE-FRANK.md` e passar à próxima missão.

## Regra permanente: PROJECT_BRIEF.md

Ao final de toda sessão em que algo relevante mudou, atualize o `PROJECT_BRIEF.md`: gargalo resolvido ou novo,
dependência adicionada/removida/atualizada, marco concluído, ferramenta adotada ou descartada, decisão de
arquitetura (ADR). Edite só as seções afetadas, atualize a data do topo e registre a mudança em uma linha na
seção 12. Antes de sobrescrever, guarde a versão anterior em `_historico/AAAA-MM-DD brief/PROJECT_BRIEF.md`
(como o `/brief` já faz). O commit segue a regra atual do repositório.
