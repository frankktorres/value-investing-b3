# Prompt — Oráculo, protocolo de validação e recalibração do motor (doutrina v3)

> Colar no chat novo: "Leia `docs/PROMPT-ORACULO-E-CALIBRACAO.md` e execute a partir da Fase 0."
> ▶ Opus | high | Plan mode: sim | Thinking: padrão | Motivo: desenho de regra + arquitetura de validação que muda palavra de investimento

## Papel
Você é o engenheiro-chefe de validação da Mesa de Value Investing (B3, dividendos/JCP, longo prazo). Missão dupla:
(1) construir um **sistema de oráculos** que prove, com rigor de validação de modelo (SR 11-7) e de teste de software
(problema do oráculo), que o que o projeto calcula está correto; (2) usar esse sistema para **confirmar ou refutar** o
diagnóstico de 22/10 e propor a recalibração da doutrina — **sem afrouxar a régua para fabricar compras**.

## Leitura de partida (nesta ordem; não releia o que já leu)
1. `CLAUDE.md` e `README.md`.
2. `docs/auditoria/2026-10-22-diagnostico/DIAGNOSTICO.md` (funil, causas com arquivo:linha, bugs, lacunas, estado dos testes)
   e os scripts `sens*.py` da mesma pasta (reproduzem os números sem gravar nada).
3. `01-doutrina-value-investing.md` (v2.6.1), `04-checklist-anti-erro.md`, últimas 3 entradas do `09-diario-de-decisoes.md`,
   `docs/DECISOES.md`, `docs/PREMISSAS-B15.md`.
4. Código: `ferramentas/motor_financeiras.py`, `ferramentas/motor_nao_financeiras.py`, `ferramentas/golden.py`,
   `ferramentas/tests/test_regressao.py`, `ferramentas/prospectivo/`.
Leitura ampla vai para subagente (`Explore`/`varredor`), no máximo 3 em paralelo, com orçamento de chamadas no prompt.

## Princípios invioláveis desta tarefa
1. **O número de BARATAs não é critério de sucesso.** Critério é coerência interna, correção verificável e, no tempo,
   acerto. Calibrar até "aparecer compra" é overfitting (Harvey, Liu & Zhu 2016; Bailey & López de Prado 2014).
2. **Pré-registro antes de olhar o resultado.** Toda variante de regra testada entra em `docs/PRE-REGISTRO-v3.md` com
   hipótese, critério de aceitação e contagem de tentativas, *antes* de rodar. Variante não registrada não vale.
3. **Mudou palavra → decisão do Frank.** Motor, doutrina, golden ou premissa: só com testes verdes, parecer do oráculo,
   registro no `09` e "ok" explícito do Frank. Bug inequívoco (ex.: zero silencioso) você corrige, mas mostra antes
   quais palavras mudam e registra.
4. Nada destrutivo; versão substituída vai para `_historico/`. `git add` de caminhos específicos. Golden só com
   `rodar_tudo.py --motivo`. Nunca `dossie.gerar` sem `--data` nova. Nunca sugerir ordem de compra/venda.
5. Afirmação de fonte (Damodaran, Graham, SR 11-7, papers): conferir com `verificador-fonte` ou WebFetch; só nota A/B embasa
   decisão; referência não confirmada fica marcada "a conferir". Biblioteca (Hypothesis, pytest, mutmut): Context7.

## Fases (cada uma é uma fatia: entrega pequena, testada, commitada; ⏸ = parar e esperar o Frank)

### Fase 0 — Plano e pré-registro (plan mode)
- Reproduza o baseline do diagnóstico com `sens.py` e confirme ou corrija os números do funil e da sensibilidade.
- Escreva `docs/PRE-REGISTRO-v3.md`: hipóteses H1…Hn (ex.: "H1: o gate de g compara ROIC contábil com WACC nominal e zera g
  de forma indevida"; "H2: Hamada sobre dívida bruta e E do modelo cria realimentação"; "H3: as âncoras não são
  independentes"; "H4: rf/π em horizontes diferentes"; "H5: o NTN-B já contém o spread de default e o prêmio de 5 p.p.
  conta risco-país em dobro"; "H6: ROIC da WEGE3 está mal calculado"), o teste que refuta cada uma e o critério de aceitação.
- ⏸ Mostrar o plano e o pré-registro ao Frank.

### Fase 1 — Constituição da validação (`docs/VALIDACAO.md`) e do oráculo (`docs/ORACULO.md`)
`docs/VALIDACAO.md` é o contrato de "pronto" do projeto daqui em diante. Deve ter:
- **Definição de pronto por tipo de mudança** (fórmula, regra de doutrina, premissa de ticker, coleta de dado, tela,
  relatório): quais camadas de prova são obrigatórias em cada uma e o comando que roda cada camada.
- **As 7 camadas de oráculo** (Barr et al. 2015, IEEE TSE): (1) especificado: caso calculado à mão ou caso de livro
  (Damodaran, Graham), sem importar constantes do motor; (2) propriedade/metamórfico com Hypothesis; (3) diferencial:
  motor-sombra independente e fonte externa; (4) reconciliação contábil; (5) sanidade econômica do universo; (6) resultado:
  base histórica PIT + registro prospectivo com Brier score; (7) desafio humano/agente independente.
- **Matriz de rastreabilidade** `§ da doutrina → função → teste(s) → camada`, gerada por script e testada (regra
  sem teste = falha). Pode ficar em `docs/RASTREABILIDADE.md`, gerada por `ferramentas/oraculo/rastreabilidade.py`.
- Regra do golden: prova **estabilidade**, nunca correção; toda regravação cita qual camada provou a correção do novo valor.
- Política de dado ausente: campo crítico ausente → NÃO CONCLUSIVO, nunca 0.

`docs/ORACULO.md` define o "engenheiro-mor":
- **Quando é obrigatório:** toda mudança em motor, doutrina, golden, premissa com fonte, coleta CVM; toda rodada de palavras.
- **Duas partes:** (a) o *oráculo automático* (`python -m oraculo` em `ferramentas/oraculo/`) roda as camadas 2–5 e grava
  `docs/oraculo/AAAA-MM-DD.md` + linha em `docs/oraculo/registro.jsonl` (sha do golden, sha do commit, resultado por
  check); devolve código de saída ≠ 0 se algum check bloqueante falhar; (b) o *oráculo agente*
  (`.claude/agents/oraculo.md`, Opus, effort high, somente leitura) faz o *effective challenge* do SR 11-7: recebe só o
  diff, o pré-registro, a doutrina e a saída do oráculo automático (não a argumentação do autor) e responde
  APROVA / RESSALVA / BLOQUEIA com checklist fixo: solidez conceitual (premissa ↔ teoria ↔ fonte A/B), dados (procedência,
  PIT, unidade, PN/ON), implementação (camadas 1–5 verdes), resultados (o que mudou de palavra e por quê), overfitting
  (tentativas contadas, critério definido antes), coerência com os mestres (qual princípio de qual autor a mudança
  serve ou fere). BLOQUEIA impede o commit no master até o Frank decidir.
- Para decisão de doutrina grande: segunda opinião em modelo diferente (comitê B no Claude Desktop), sem ver o veredito do
  primeiro.
- Teste do próprio oráculo: um conjunto de mudanças-armadilha (bug plantado em branch descartável) que ele **tem** de
  pegar. Oráculo que não pega bug plantado não está pronto.

### Fase 2 — Oráculo automático (camadas 2, 4 e 5), sem mudar palavra
Em `ferramentas/oraculo/` (+ testes em `ferramentas/tests/test_oraculo_*.py`). Hypothesis entra em `requirements.txt` e no
lock. Registrar no `PROJECT_BRIEF.md`.
- **Propriedades e metamórficos** (sobre `avaliar` dos dois motores, com entradas geradas):
  valor central não cresce quando Ke sobe; não cai quando lucro/FCF/DPA sobe (tudo igual); não depende do preço;
  invariante a escala de unidade (R$ mil × R$) e a desdobramento (ações × k, valores por ação ÷ k); permutar tickers não
  muda nada; preço ↑ nunca melhora a palavra; dado crítico ausente nunca gera BARATA/RADAR/JUSTA; saída sem NaN/inf;
  g < Ke sempre na perpetuidade.
- **Reconciliação contábil** por ticker e exercício (CVM DFP/ITR): ativo total = passivo + PL (tolerância de
  arredondamento); DFC: caixa inicial + FCO + FCI + FCF + variação cambial = caixa final; lucro da DRE = lucro na DMPL;
  dividendos da DMPL ≈ DFC; ações em circulação coerentes com o LPA. Divergência → bandeira no relatório.
- **Sanidade econômica do universo** (só relatório, não muda palavra): P/L implícito do central vs 1/(Ke−g) sobre o lucro
  reportado; Ke implícito no preço (DCF reverso) vs Ke do modelo; distribuição de P/C do hall; lista de "compounders"
  (ROIC alto e estável em 10 anos) com P/C > 2 e o motivo decomposto (taxa × fluxo × g × normalização); Ke por ticker
  acima de um teto plausível (ex.: 30% nominal) = alarme de artefato.
- **Contraste com screens acadêmicos** (bandeira, nunca palavra): Piotroski F, Altman Z'' (versão emergentes), Beneish M,
  accruals de Sloan, Greenblatt (EBIT/EV + ROC). BARATA com F ≤ 3, M > −1,78 ou Z'' em zona de risco = bandeira vermelha.
- Commit e push ao fim da fase.

### Fase 3 — Bugs inequívocos (camada 1 + correção)
Zero silencioso (`motor_nao_financeiras.py:176-177,214,250,273-277`, `montar_series.py:48`) → NÃO CONCLUSIVO; LEVE3
com palavra velha no `hall.json`; trava de coerência só em JUSTA; payout × g terminal no DDM. Para cada um: teste que
falha antes e passa depois, lista das palavras que mudam, parecer do oráculo agente, entrada no `09`. ⏸ se mudar palavra.

### Fase 4 — Oráculo diferencial e força da suíte (camadas 3 e "teste do teste")
- **Motor-sombra**: implementação independente e mínima (outro arquivo, sem importar o motor) de FCFF/FCFE e DDM no
  estilo Damodaran, para os 41 tickers; divergência acima da tolerância pré-registrada = investigar e explicar.
- **Âncora externa de insumos**: LPA, VPA, DPA, dívida líquida, ações de cada ticker contra RI/CVM e uma segunda fonte
  (Status Invest/Fundamentus, respeitando `docs/TERMOS-DE-USO-FONTES.md`); só os insumos, não o valor justo.
- **Mutation testing** nos dois motores: medir a nota de mutação de base e listar os mutantes sobreviventes.
  Atenção: o mutmut 3 não roda nativo no Windows. Use WSL, a nuvem (Linux) ou `cosmic-ray` e registre a escolha.

### Fase 5 — Proposta da doutrina v3 (só proposta; ⏸ Frank decide)
Com as fases 2–4 como evidência, escreva `docs/PROPOSTA-DOUTRINA-v3.md`. Para cada item, dê: hipótese do pré-registro,
evidência medida, opção A/B/C, efeito em P/C e nas palavras dos 47 (tabela), fonte A/B e o mestre que embasa. Itens mínimos:
1. **Faixa de valor** (P10/P50/P90 por cenários ou Monte Carlo sobre g, margem e Ke) e palavra pela posição do preço na
   faixa (Klarman; Damodaran, *Probabilistic Approaches*). A dispersão vira largura da faixa, não veto.
2. **Ke**: rf normalizada vs spot (e o mesmo vértice para rf e π); spread de default soberano (Damodaran, `ctryprem`, versão
   vigente lida da planilha); beta setorial bottom-up desalavancado (Damodaran, betas por setor de emergentes); Hamada sobre
   **dívida líquida** e **E a mercado**, com teto e sem ponto fixo.
3. **Crescimento**: gate real × real (ROIC real vs WACC real), por ROIC incremental e reinvestimento (g = taxa de
   reinvestimento × ROIC); compounder deixa de ser estruturalmente incomprável (Buffett/Munger, Fisher, Bill Miller).
4. **Normalização**: ROE/margem do ciclo com critério explícito (mediana de 10 anos vs ciclo completo vs peso no
   recente), testada pela camada 6, nunca escolhida pelo número de compras.
5. **Âncoras independentes**: pelo menos uma que não parta do mesmo NOPAT e Ke (múltiplo histórico próprio, earnings
   yield real vs NTN-B, NCAV/valor de ativos de Graham/Schloss como piso).
6. **Empilhamento**: decidir conscientemente onde mora o conservadorismo (taxa **ou** margem **ou** fluxo), sem contá-lo em
   dobro; registrar a escolha.
7. **Risco de perda permanente**: cenário de estresse (EBITDA −40%, refinanciamento fechado) com cronograma e moeda da
   dívida lidos das notas explicativas (Marks, Klarman, Pabrai).
8. **Vetos de contabilidade**: Beneish/Sloan passam de bandeira a bloqueio de BARATA (Beneish 1999; Sloan 1996).
9. **Proventos**: CAGR de DPA em 10 anos, recompra/diluição líquida, TRR de Neff e PEGY como informativos (Barsi, Bazin, Neff,
   Bogle).
10. **Qualitativo**: separar "sem evidência" de "evidência negativa" (Fisher, 15 pontos) e mostrar a nota como intervalo.
O oráculo agente revisa a proposta inteira. Comitê B no Desktop para os itens 1–4. ⏸ Frank escolhe por item.

### Fase 6 — Implementação da v3 aprovada
Uma fatia por item aprovado: teste primeiro (camadas 1–2), implementação, oráculo automático verde, oráculo agente
APROVA, `rodar_tudo.py --motivo "v3 item N"`, `09` com antes × depois das palavras, `01` versionado (antiga em
`_historico/`), `PROJECT_BRIEF.md` (seção 12).

### Fase 7 — Validação de resultado (camada 6)
- **Base histórica PIT** (ledger da Etapa 3): rodar a régua v3 em datas passadas (ex.: 2016, mar/2020, 2022, 2024) e medir
  a fração BARATA por data vs juro real e o retorno total em 3 anos de BARATA × JUSTA × CARA; deflacionar pelo número de
  variantes testadas (Deflated Sharpe/PBO). Se der ≈ 0 BARATA em todas as datas, inclusive em mar/2020, a régua não
  discrimina e isso é falha.
- **Prospectivo**: cada palavra ganha probabilidade explícita (ex.: "P(retorno total 3a ≥ Ke) = 70%") no
  `prospectivo/registro.jsonl`; Brier score e curva de calibração a cada rodada (Brier 1950; Tetlock). Poucas observações
  → só relatar, não concluir.

## Entregáveis finais
`docs/PRE-REGISTRO-v3.md`, `docs/VALIDACAO.md`, `docs/ORACULO.md`, `docs/RASTREABILIDADE.md`, `.claude/agents/oraculo.md`,
`ferramentas/oraculo/` + testes, `docs/oraculo/` (relatórios + registro), `docs/PROPOSTA-DOUTRINA-v3.md`, motor-sombra,
entradas no `09` e no `PROJECT_BRIEF.md`.

## Ritmo
Um chat não comporta tudo. Neste primeiro chat: Fases 0 → 1 → 2. Feche com `/fechar` e entregue o prompt do próximo chat
(Fases 3–4), terminando com a linha ▶. Contexto acima de ~150k → fechar antes.
Antes de dizer "pronto" em qualquer fase: rodar `cd ferramentas && python -m pytest --ignore=backtest -q` e
`python -m oraculo` e mostrar o resultado real.

## Referências-base (conferir antes de citar como decisão)
SR 11-7 (Fed/OCC 2011) e Res. CMN 4.557/2017 art. 9º · Barr et al. 2015 IEEE TSE 41(5) · Chen et al. 2018 ACM CSUR 51(1) ·
Claessen & Hughes 2000 (QuickCheck) / Hypothesis · McKeeman 1998 · Jia & Harman 2011 IEEE TSE 37(5) · Harvey, Liu & Zhu 2016
RFS 29(1) · Bailey & López de Prado 2014 JPM 40(5) · Bailey et al. 2017 J. Comp. Finance 20(4) · Hou, Xue & Zhang 2020 RFS
33(5) · Piotroski 2000 JAR · Novy-Marx 2013 JFE · Asness, Frazzini & Pedersen 2019 RAST · Altman 1968 JF · Beneish 1999 FAJ ·
Sloan 1996 TAR · Asness 2003 JPM ("Fight the Fed Model") · Damodaran, `ctryprem` (jan/2026) e *Probabilistic Approaches* ·
Klarman 1991 · Marks 2011 · Graham, *O Investidor Inteligente* · Greenblatt 2005 · Brier 1950 · Tetlock 2015.
