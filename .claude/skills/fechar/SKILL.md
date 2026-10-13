---
name: fechar
description: Fecha o turno deste projeto passando o pendente para docs/MISSOES.md e dando push. Use quando o Frank disser "/fechar", "vou parar", "até amanhã", "fechar", "encerrar" ou "próximo chat".
---

# /fechar — passagem de turno (Mesa de Value Investing)

1. **Estado real:** `git status -sb` e `git log -3 --oneline`. Liste o que mudou nesta sessão (arquivo → motivo, 1 linha).
2. **Pendente → `docs/MISSOES.md`:**
   - mova missões concluídas para "Feitas" (com hash do commit);
   - o que ficou pela metade vai para "Em andamento" com: onde parou, próximo passo concreto, "pronto quando";
   - ideias novas entram em `docs/BACKLOG.md` (com tipo executável / decisão Frank / local);
   - reescreva "Passagem de turno" com data de hoje e 2–4 linhas.
3. **Frank:** o que depende dele (senha, dinheiro, decisão) → `docs/PENDENTE-FRANK.md`; decisão reversível tomada → `docs/DECISOES.md`.
4. **Relatório:** nova entrada no topo de `docs/RELATORIO-DIARIO.md` (máx. 10 linhas).
5. **Brief:** se algo relevante mudou, siga a regra do `CLAUDE.md` (PROJECT_BRIEF.md).
6. **Testes + push:** rode `cd ferramentas && python -m pytest --ignore=backtest -q` (ou só os módulos tocados). Verde → `git add` dos caminhos específicos (nunca `add .`), commit e `git push origin master`. Vermelho → não vá para `master`: commit no ramo `wip/auto` (o hook Stop faz isso) e diga qual teste falhou. Na nuvem faça você mesmo, o hook está desligado.
7. **Varredura:** antes do commit, confira que nenhum arquivo staged é `.env*`/chave/token nem traz quantidade, preço médio, valor ou corretora da carteira. Se tiver, pare e avise.
8. **Resposta final (curta, PT):** o que foi feito, hash do commit, `local = origin/master?`, o que o Frank precisa fazer (ou "nada, espere").
