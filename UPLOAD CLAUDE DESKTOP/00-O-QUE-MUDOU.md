# O que mudou desde 21/10/2026 (última carga do Desktop)

## Entrou

- **Doutrina 2.7 (24/11/2026)** no lugar da 2.6.1 (H2: D/E a mercado, sem ponto fixo). Os PDFs de lote de 09/10 saíram desta pasta.
- **`00-DNA.md`** (25/11): norte do projeto, princípios, as 4 causas da B36 e os marcos M1–M5.
- **Pré-registro v3** com emendas: método escolhido pela fonte antes de rodar; um hold-out vale uma vez.
- **Pacote de autonomia** (25/11): agentes `senior`, `adversario`, `oraculo`, `verificador-fonte`, `varredor`; regra "Quem decide"; travas B37 e 4.2–4.6; skills `mesa-*`.
- **3T26** gravado no `master` (24/11).

## Saiu ou mudou de papel

- **`claude tools/` fora do repositório** (notas de outro projeto; movida, não apagada).
- **Hook `Stop` só guarda snapshot em `wip/auto`** (24/11): não commita mais no `master`; commit no `master` é explícito, com a suíte inteira verde (trava B37).
- **`/fechar` → `/mesa-fechar`** (e `/fatia`, `/checkup`, `/kaizen` → `mesa-*`): a skill global de mesmo nome sombreia a do projeto.
- **B36 contaminada:** as 20 ações do hold-out já foram vistas; servem para desenvolver, não para provar. A prova é o M1 (hold-out 2 + hold-out no tempo).
- **Causa (a) do DNA fechada "como está, com motivo"** (25/11): Ke > 30% sai NÃO CONCLUSIVO pela H2 e é medido no M1; B39 não disparou, B46 NÃO CONCLUSIVA.
- **B35 parada** (Kd que reage à alavancagem): sem prioridade depois do fechamento da causa (a).
- **Desktop**: passa a ser consulta/conversa; método, números e palavra só valem do repositório.

## Itens do BACKLOG fechados desde 21/10 (lidos de `BACKLOG.md`)

- **D1** (21/10): Check-up 21/10: temporada blindada (sem download no `--gravar`, hash do ZIP, 404 = 0, aviso no .vbs)
- **D2** (21/10): Check-up 21/10: `carimbos.py` fonte única das armadilhas na exceção dos 0,80×
- **D4** (21/10): Check-up 21/10: Agendador (TemporadaDiaria 06:30 de 22/10 a 21/11; BackupSemanal domingo 07:30) e backup sem `privado/`
- **D5** (21/10): Tela v0.2: "anos seguidos com provento" por `proventos_hall.anos_seguidos` (B3, nota A)
- **N6** (21/10): "Ocultar valores" sem vazar DY líquido nem patrimônio
- **N1** (22/10): Higiene de docs (README, brief, BACKLOG, 03-hall, relatório diário, PROMPT do handoff)
- **N10** (22/10): CLIs com traceback cru (`temporada.py`, `triagem/rodar.py`) e ponto decimal no texto da ALLD3
- **N14** (22/10): Rota `#/` caía em "página não existe" depois da N9
- **N2** (22/10): Testes das regras sem cobertura (desconto por cenários, escala de Preço, saída 1,50× em financeira, DCF reverso)
- **N3** (22/10): Contrato liga o que o motor já calcula (setor, dividendo × JCP por mês, data das fontes, faixa do DCF)
- **N4** (22/10): Tela Sistema (`sistema.json`: idade dos dados, boletins, golden, testes)
- **N5** (22/10): Contraste WCAG dos tokens da tela (parte automática da etapa 4)
- **N7** (22/10): Motor recusa dado inválido (NaN/inf/None/0/negativo)
- **N8** (22/10): Escala do nº de ações (CVM em mil; TAEE11) — investigar `acoes`
- **N9** (22/10): Robustez do servidor (porta em uso) e do front (hall sem `fatores`, `versao`, hash desconhecido)
- **Q01** (22/10): `gerar_pdf_lote*.py` registram a fonte `C:/Windows/Fonts/arial.ttf` ao importar: `test_b23_petr4_premissas` e `test_carimbos` não coletam fora do Windows — fal…
- **B34** (24/11): Próxima tarefa (decisão do Frank, 23/11)
- **B36** (25/11): Hold-out antes de qualquer calibração nova (B35 incluída; pré-registro, emenda 7): congelar o método v2.7 (commit do merge do 3T26) e rodá-lo em 20 ações de fo…
- **B37** (25/11): Trava pre-push: bloquear `git push` no `master` sem a suíte verde (`cd ferramentas && python -m pytest --ignore=backtest -q`), no modelo do `.githooks/trava_ma…
- **B40** (25/11): Falha da B36 (erro): evento societário CIS RED CAP (cisão com redução de capital) sem semântica conferida em `proventos_hall.py:207` — CSAN3 e MRVE3 param com …
- **B57** (25/11): Z'' de Altman com X2 sem prejuízos acumulados (achado do `adversario` na B46): o `altman_z2` usa só `reservas_lucro` (conta 2.03.04) no X2 = lucros retidos ÷ a…
- **B60** (26/11): Série antiga do dossiê CMIN3 (coleta de 02/10, antes da AUD-68): `lucro_controlador` = 0 em 2022–24 (a coleta de hoje dá None = sem dado) e ações do `ltm_2T26`…

Próximo passo vigente: em `DECISOES.md`, a linha "Próximo passo (DNA)" mais recente (perto do fim).
