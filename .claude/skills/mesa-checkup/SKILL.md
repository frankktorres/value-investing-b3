---
name: mesa-checkup
description: Check-up mensal SÓ LEITURA da Mesa de Value Investing — números citados nos .md × código, BACKLOG envelhecido, catraca de datas fixas (B32), travas vivas (hooksPath, deny, hooks, piso, catracas). Grava um relatório em docs/checkups/ e mais nada. Neste repositório substitui o /checkup global. Use quando o Frank pedir "checkup" ou pelo agendamento mensal.
---

# /mesa-checkup — só leitura; o relatório é o único arquivo criado

Grava `docs/checkups/AAAA-MM-DD.md` (≤ 60 linhas: 🔴 bloqueia / 🟡 envelhecendo / 🟢 ok, cada achado com arquivo:linha).
Nunca corrige nada: achado vira item do `docs/BACKLOG.md` ou linha do `PENDENTE-FRANK.md` na sessão seguinte.

## 1. Fatos (você coleta)
- `git status -sb`, `git log --oneline -5`, `git log origin/master -1`; ramos `wip/auto` e `claude/*` vivos
  (`git ls-remote --heads origin`).
- Última suíte: `ferramentas/dados/suite_ultima.json` (data, aprovados, pulados). Mais de 7 dias → 🟡.
- **Travas vivas** (cada uma 🔴 se morta):
  - `git config core.hooksPath` = `.githooks` (B37);
  - `.githooks/piso_testes.json`: piso ≤ aprovados da última suíte; se a suíte cresceu, sugerir subir o piso;
  - `.claude/settings.json`: deny de `.env*`, chaves, `git reset --hard`, `git clean`, `push --force`, `_historico/`,
    marcador da suíte; hooks PreToolUse (`trava_config.py`), SessionStart e Stop (`auto_commit.py`, `avisos.py fim`);
  - testes-canário presentes: `ferramentas/tests/test_travas.py`, `test_b37_trava_master.py`, `test_motor_puro.py`,
    `test_docs_caminhos.py`, `test_lotes_sem_data_fixa.py`.
- **Catracas:** `ferramentas/tests/datas_fixas_catraca.json` (B32, prazo 31/01/2027: dias restantes × itens restantes),
  `motor_puro_catraca.json`, `docs_caminhos_catraca.json` — número de hoje e do checkup anterior.
- **BACKLOG envelhecido:** itens abertos com origem > 60 dias, itens sem causa/marco do DNA, contagem por tipo da última
  seção × nº de IDs na tabela.
- **Números citados × código** (agente `varredor` ou `auditor`, em paralelo, com orçamento de ~25 chamadas cada):
  contagem de testes, de tickers do hall, versão da doutrina, caminhos citados em `CLAUDE.md`, `README.md`, `00-DNA.md`.
- `docs/PENDENTE-FRANK.md`: perguntas abertas há mais de 14 dias → 🟡 (lembrar o Frank com a recomendação).

## 2. Relatório
Seções: Travas · Catracas · Suíte · BACKLOG · Docs × código · Pendências do Frank · Comparação com o checkup anterior.
Termine com "Próximo checkup: <data + 1 mês>". Commit só do relatório (suíte inteira verde, trava B37).
