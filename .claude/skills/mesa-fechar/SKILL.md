---
name: mesa-fechar
description: Fecha o turno da Mesa de Value Investing — passa o pendente para docs/MISSOES.md, decide o próximo passo pelo DNA (§4 causas, §5 marcos) com o agente senior, commit + push com a suíte inteira verde e entrega o prompt do próximo chat com ▶. Neste repositório substitui o /fechar global. Use quando o Frank disser "/fechar", "/mesa-fechar", "vou parar", "até amanhã", "fechar", "encerrar" ou "próximo chat".
---

# /mesa-fechar — passagem de turno (Mesa de Value Investing)

1. **Estado real:** `git status -sb` e `git log -3 --oneline`. Liste o que mudou nesta sessão (arquivo → motivo, 1 linha).
   Resultado real da última suíte (se nenhuma rodou depois da última mudança, diga isso).
2. **Pendente → `docs/MISSOES.md`:**
   - mova missões concluídas para "Feitas" (com hash do commit);
   - o que ficou pela metade vai para "Em andamento" com: onde parou, próximo passo concreto, "pronto quando";
   - ideias novas entram em `docs/BACKLOG.md` (com tipo executável / decisão Frank / local e a causa ou marco do DNA);
   - reescreva "Passagem de turno" com data de hoje e 2–4 linhas;
   - **carimbe para a noite (desde 26/11/2026)** 0–4 missões seguras (só doc/teste/coleta que NÃO mudam palavra e NÃO
     tocam o que o `docs/ops/rotina/PROTOCOLO.md` §2 proíbe; sem dado local), com a última linha
     `*Carimbo (nuvem):* <ID> · escopo: <caminhos literais entre crases, sem glob> · fonte: <domínio|nenhuma> · pronta: <sha7 do master>`.
     Só a sessão do dia carimba; missão sem carimbo é local. Antes do commit, rode
     `python ferramentas/rotina/checar_rotina.py --base origin/master` (mostra quais missões o portão enxerga) **e**
     `cd ferramentas && python -m rotina.ensaio_nuvem` (suíte sem os dados, como a nuvem; ~4 min → Bash com
     timeout 600000 ou `run_in_background`; sem a linha final VERDE/VERMELHO = não carimbar): vermelho = a noite
     pararia em BASE VERMELHA (1ª noite, 27/11) → consertar antes de carimbar.
3. **Quem decide** (`CLAUDE.md`): decisão reversível tomada → `docs/DECISOES.md` (opção, motivo, como reverter); o que
   é do Frank (palavra, dinheiro, histórico, DNA, liberar trava, senha) → `docs/PENDENTE-FRANK.md` com recomendação.
4. **Próximo passo decidido pelo DNA (não pergunte ao Frank "o que fazer agora"):**
   - candidatos = itens abertos do `docs/BACKLOG.md` ligados à **causa aberta mais cedo na ordem do `docs/00-DNA.md` §4**
     ((a) nível do Ke → (b) domínio → (d) insumos; (c) eventos pode correr em paralelo) e ao marco do §5 que ela destrava;
   - chame o agente `senior` com os candidatos (caminhos, não argumentação) e a pergunta "qual é o próximo passo?";
     ele responde pela ordem do DNA e pela opção conservadora;
   - registre a escolha em `docs/DECISOES.md` (é reversível) numa linha que comece por **"Próximo passo (DNA):"** — causa,
     item escolhido, veredito do `senior`, e se alguma causa fechou ("causa (x) fechada: motivo") — e use-a no prompt do
     item 9. Se o `senior` der PARA porque a escolha é do Frank, vá para `PENDENTE-FRANK.md` e escolha o próximo item que
     não dependa dele.
   - **Ao abrir uma sessão nova**, a última linha "Próximo passo (DNA):" do `DECISOES.md` é o ponto de partida; sem ela,
     a causa aberta é a primeira do §4 que nenhuma linha dessas deu como fechada.
5. **Relatório:** nova entrada no topo de `docs/RELATORIO-DIARIO.md` (máx. 10 linhas).
6. **Brief:** se algo relevante mudou, siga a regra do `CLAUDE.md` (PROJECT_BRIEF.md, versão anterior em `_historico/`).
   **Desktop (sempre, sem decidir se precisa — 26/11/2026):** como último passo de edição, antes da suíte, rodar
   `cd ferramentas && python -m desktop.atualizar` em TODO fecho (quase todo fecho mexe em DECISOES/BACKLOG/brief, que estão
   no `UPLOAD CLAUDE DESKTOP/MANIFESTO.txt`; sem nada mudado ele não troca nada) e avisar o Frank quais arquivos trocar no
   Desktop (a lista sai no fim do MANIFESTO). Sem isso o `test_desktop_upload.py` reprova.
6b. **Rotina da nuvem × repo:** `RemoteTrigger get` em `trig_016wrGPsNHp4dUaVAExNhZyU`; salve o texto do prompt num arquivo
   do scratchpad e rode `cd ferramentas && python -m rotina.nuvem conferir <arquivo> --next-run <next_run_at> --enabled <enabled>`.
   Diferente → `RemoteTrigger update` com o bloco de `python -m rotina.nuvem bloco` e confira de novo. Diga ao Frank
   `Rotina: enabled=… · próxima …` (o `tests/test_rotina.py` reprova se o BOOTSTRAP mudou sem essa conferência).
7. **Varredura (antes do commit):** nenhum arquivo a commitar é `.env*`/chave/token nem traz quantidade, preço médio,
   valor ou corretora da carteira. Se tiver, pare e avise.
8. **Testes + push:** com TODAS as edições acima já feitas, rode a suíte inteira
   (`cd ferramentas && python -m pytest --ignore=backtest -q`, ~10 min, 0 falha e 0 pulado). Verde → `git add` dos caminhos
   específicos (nunca `add .`), commit e `git push origin master`. A trava B37 (`.githooks/pre-push`) recusa o push se a
   árvore do commit não for a da suíte verde: edite nada entre a suíte e o commit; arquivo fora do commit (não rastreado)
   também muda a árvore — commite-o ou mova-o. Vermelho → não vá para o `master`: o hook Stop guarda o snapshot em
   `wip/auto`; diga qual teste falhou. Na nuvem: ramo `claude/*`, nunca `master`.
9. **Resposta final (curta, PT):** o que foi feito, hash do commit, `local = origin/master?`, o que o Frank precisa fazer
   (ou "nada, espere") e o **prompt do próximo chat** num bloco de código para colar:
   - topo: `Abrir em: c:\Users\frank\Documents\VALUE INVESTING`;
   - "Ler primeiro: `docs/00-DNA.md`, `CLAUDE.md`" + 3–6 linhas: objetivo (o passo do item 4, com causa/marco do DNA e o
     veredito do `senior`), arquivos de partida, critério de pronto (conferência, não alvo numérico), e "decisão
     reversível: decide, registra em `docs/DECISOES.md` e segue; só do Frank → `docs/PENDENTE-FRANK.md`";
   - última linha obrigatória: `▶ Modelo | Effort | Plan mode | Thinking | Motivo` pela tabela do `~/.claude/ROTEAMENTO.md`
     (método/doutrina/pré-registro = Opus high com plan mode; executor/infra = Sonnet medium).
