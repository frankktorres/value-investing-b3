# ORÁCULO — o conferente-mor da Mesa

Vigente desde 22/10/2026. É o *effective challenge* do SR 11-7 (Fed/OCC 2011, "Supervisory Guidance on Model Risk
Management"): quem confere o modelo não é quem o fez, tem competência e tem poder de barrar. O contrato de "pronto" está em
`docs/VALIDACAO.md`; as hipóteses estão em `docs/PRE-REGISTRO-v3.md`.

## 1. Duas partes

### (a) Oráculo automático — `python -m oraculo`
- Código em `ferramentas/oraculo/`. Roda as camadas 2–5 (propriedades, reconciliação, sanidade, screens) e, com
  `--diferencial`, a camada 3 (Fase 4).
- Grava `docs/oraculo/AAAA-MM-DD.md` (relatório legível) e acrescenta uma linha em `docs/oraculo/registro.jsonl`:
  `{data, commit, golden_sha, doutrina, checks: {nome: "ok"|"bandeira"|"falha"}, bloqueantes_falhos: [...]}`.
- Sai com código ≠ 0 se algum check **bloqueante** falhar (lista em `docs/VALIDACAO.md` §1).
- Não muda palavra, central, golden nem doutrina. Só lê e relata.

### (b) Oráculo agente — `.claude/agents/oraculo.md`
- Opus, effort high, **somente leitura**.
- **Quando é obrigatório:** só em mudança de **motor, doutrina, golden ou premissa** (de ticker ou de mercado). Coleta
  de dado, tela, relatório e documentação não exigem o agente: neles basta o oráculo automático e, onde a VALIDACAO
  pedir, o `adversario`.
- **O que recebe (e só isso):** o diff (`git diff` ou `git show`), o `docs/PRE-REGISTRO-v3.md`, o `01` vigente e a saída
  do oráculo automático da mudança. **Não recebe a argumentação do autor**: nem mensagem de commit, nem texto do chat, nem
  entrada do `09` escrita para justificar. Quem chama passa só os caminhos, e o agente é instruído a ignorar justificativa
  que apareça no material.
- **Checklist fixo**, com um item por linha e veredito por item:
  1. Solidez conceitual: a premissa bate com a teoria e com uma fonte A/B citada?
  2. Dados: procedência, PIT, unidade (R$ mil × R$), PN/ON, ausente ≠ 0.
  3. Implementação: as camadas 1–5 estão verdes e há um teste que falha antes e passa depois?
  4. Resultados: o que mudou de palavra e por quê, ticker a ticker.
  5. Overfitting: a variante estava no pré-registro antes de rodar, as tentativas foram contadas e o critério foi
     definido antes?
  6. Coerência com os mestres: que princípio, de que autor, a mudança serve ou fere?
- **Veredito:** APROVA / RESSALVA / BLOQUEIA. **BLOQUEIA impede o commit no master** até o Frank decidir. RESSALVA
  entra no `09` com a resposta do autor.

## 2. Validade do próprio oráculo (teste das armadilhas)
Um oráculo que não pega bug plantado não está pronto.
- Conjunto de **mudanças-armadilha**: patches em `ferramentas/oraculo/armadilhas/`, cada um com o defeito, a camada que
  deve pegá-lo e quem deve pegá-lo (automático, agente ou os dois). Os patches são aplicados num `git worktree`
  descartável em pasta temporária, nunca na árvore de trabalho.
- Armadilhas mínimas:
  - zero silencioso novo;
  - real × nominal trocados;
  - sinal invertido na dívida líquida da ponte;
  - unidade R$ mil × R$ nas ações;
  - régua afrouxada sem registro (BARATA ≤ 0,75);
  - premissa digitada sem fonte que muda palavra;
  - golden regravado sem camada no motivo;
  - variante fora do pré-registro.
- **O automático só vale como portão depois de pegar 100% das armadilhas de sua alçada**
  (`python -m oraculo.armadilhas`).
- **O agente só vale depois de pegar 100% das armadilhas de sua alçada**, rodadas às cegas: ele recebe o patch como se
  fosse uma mudança real, sem saber que é armadilha. Até lá o veredito dele é **provisório**: é registrado, mas não conta
  como portão, e a mudança segue o caminho antigo (suíte + `adversario` + "ok" do Frank).
- O resultado do teste das armadilhas entra em `docs/oraculo/registro.jsonl` com `tipo: "armadilhas"`. Ele é refeito
  quando o oráculo ou o agente mudam.

## 3. Segunda opinião
Decisão de doutrina grande (itens 1–4 da proposta v3) vai também ao **comitê B** no Claude Desktop, em modelo
diferente, **sem ver o veredito do primeiro**. Divergência entre os dois → Frank decide, com as duas opiniões lado a lado.

## 4. Fluxo de uma mudança de motor, doutrina, golden ou premissa
1. A variante está no pré-registro (§6) antes de rodar.
2. Teste que falha antes (camada 1 ou 2), depois a implementação.
3. `cd ferramentas && python -m pytest --ignore=backtest -q` e `python -m oraculo` verdes.
4. Agente `oraculo` com o diff, o pré-registro, o `01` e a saída do item 3 → APROVA, RESSALVA ou BLOQUEIA.
5. Lista de palavras que mudam → "ok" do Frank → `09` → golden com `--motivo` citando a camada.
