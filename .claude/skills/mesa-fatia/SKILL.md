---
name: mesa-fatia
description: Uma entrega pequena, completa e provada na Mesa de Value Investing — pré-registro (se mexe em método) → teste que falha → mudança → suíte inteira → senior → oráculo (se motor/doutrina/golden/premissa) → commit + push. Neste repositório substitui o /fatia global. Use ao começar feature, correção, conserto de executor ou hipótese de causa do DNA.
---

# /mesa-fatia — uma fatia da Mesa

Uma fatia = UM objetivo, UM chat, UM commit (mais o commit próprio do pré-registro, antes, quando houver). Escopo
cresceu → pare e divida.

## 0. Antes de escrever código
1. `docs/00-DNA.md` §6: em que **causa** (§4) e **marco** (§5) a fatia entra? Se em nenhum, escreva por que vale agora.
2. **Já existe?** Grep (ou agente `varredor`) pelo nome da função/campo/premissa. Metade do retrabalho é reconstruir.
3. **Há opções?** Chame o `senior` com as opções **antes** de ver qualquer tabela de palavras/resultado. Reversível →
   `docs/DECISOES.md` e segue; do Frank → `docs/PENDENTE-FRANK.md` e faça outra coisa.
4. **Mexe em método** (motor, doutrina, régua, golden, premissa, critério)? Então:
   - hipótese, fonte A/B (lida, `[LIDO data]` + trecho; `verificador-fonte` confere), previsão de onde vai falhar e
     critério de aceitação vão como **emenda do `docs/PRE-REGISTRO-v3.md` em commit próprio, antes** de rodar;
   - medir e mudar são sessões diferentes: gatilho disparado = proposta com ⏸ ao Frank, não conserto na hora;
   - mudança de palavra é do Frank (CLAUDE.md, "Quem decide").
   Executor/infra sem tocar motor/ficha/protocolo: sem pré-registro, mas com teste de equivalência (golden igual).

## 1. Provar primeiro
1. Teste que **falha sem a mudança** (rode e veja vermelho) — de qual camada (1–5, `docs/VALIDACAO.md`)?
2. Esperado calculado à mão ou por fonte, **nunca** importando a constante do motor (tautologia).
3. Dado ausente → "não avaliado" com razão; nunca `x or 0`, `.get(x, 0)` ou padrão silencioso.

## 2. Mudar
- Só o escopo. Regra genérica, nunca exceção por ticker. Nada de data fixa no código (catraca B32).
- Config de teste, travas, catracas e golden são protegidos (trava 4.2): precisa mudar → `PENDENTE-FRANK.md`.

## 3. Provar depois
1. Suíte **inteira** (`cd ferramentas && python -m pytest --ignore=backtest -q`, ~10 min, 0 falha, 0 pulado), depois da
   **última** mudança. Prova em 3 pontos: o teste novo falha sem a correção, passa na base, passa depois.
2. `python rodar_tudo.py` (sem `--motivo`): o diff do golden é o esperado? Mudou palavra → do Frank; regravar golden só com
   `GOLDEN_REGRAVAR=1` e motivo citando a camada (trava 4.3), depois do oráculo.
3. Lógica importante → agente `adversario` (só o que ele reproduzir conta).
4. Motor/doutrina/golden/premissa → `python -m oraculo` + agente `oraculo` (APROVA/RESSALVA/BLOQUEIA) e registro no `09`.
5. Agente `senior` sobre o diff: SEGUE / SEGUE COM AJUSTES / PARA.

## 4. Fechar
- Commit (Conventional Commits em PT, `git add` de caminhos específicos) **e** push juntos. A trava B37 recusa push no
  `master` se a árvore do commit não for a da suíte verde.
- `/mesa-fechar`.
