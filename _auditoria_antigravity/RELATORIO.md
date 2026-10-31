# Auditoria Holística — Mesa de Value Investing (B3)

> **Data da Auditoria:** 30/10/2026  
> **Escopo:** Auditoria integral em modo somente-leitura (Engenharia de Software Sênior/Staff + Investidor Fundamentalista Sênior — Dividendos/JCP, Longo Prazo, B3).  
> **Entregáveis complementares:** [`ACHADOS.csv`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/_auditoria_antigravity/ACHADOS.csv) e [`MAPA-PASTAS.md`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/_auditoria_antigravity/MAPA-PASTAS.md).

---

## a. Resumo Executivo (Máx. 1 Página)

### Notas Gerais (0–10)

| Dimensão | Nota | Diagnóstico Sintético |
|---|---:|---|
| **1. Engenharia de Software** | **6,8 / 10** | Excelente arquitetura de procedência (`Numero`/`Origem` A/B/C), privacidade/LGPD (`garantir_ignorado`, `fre.py`) e painel local (`127.0.0.1`), mas comprometida por estado global mutável no import-time (`CVM`/`SI`), silenciamento de dados ausentes (`v(d, k, 0)`), código duplicado nos lotes/PDFs e datas chumbadas. |
| **2. Doutrina e Valuation** | **5,2 / 10** | Doutrina escrita (`01-doutrina-value-investing.md`) bem estruturada, porém a tradução matemática nos motores contém erros graves: mistura de juros nominais (`kd`) em lucro normalizado real (`lpa_norm`), comparação de `roic_rep` real com `w_nom` nominal, dívida bruta no Hamada com espiral de ponto fixo (`Ke = 64,7%` na `KLBN11`), colinearidade de âncoras em bancos e viés sistemático pró-`CARA` (38 de 41 empresas fora de decisão). |
| **3. Validação e Embasamento** | **5,5 / 10** | Raro rigor conceitual (pré-registro v3, hash-chain prospectivo, oráculo com armadilhas), mas o oráculo se auto-mascara nas 38 empresas `CARA`/`NC` (rebaixando falhas a bandeiras com `exit 0`), a Armadilha 02 só foi pega por snapshot estático (`03-hall`), a estatística prospectiva ignora sobreposição de janelas de 365 dias e todas as 20 financeiras/elétricas têm valor central nota C. |
| **4. Operação e Segurança** | **6,5 / 10** | Isolamento exemplar de dados pessoais (zero vazamentos no histórico Git), mas a operação real está com **3 bloqueios ativos hoje**: cotações travadas em `15/10/2026` há 2 semanas (linha de 246 bytes no `COTAHIST_A2026.ZIP`), `auto_commit.py` deletou 25 PDFs direto no `master` (`05e6636`) sem rodar testes e os 3 ramos da rotina noturna estão presos há 7 dias em `conferir_noite.py`. |

### Os 10 Maiores Riscos (Fatos Verificados)
1. **`[F3-01]` Mistura Real vs. Nominal no Lucro Normalizado (`motor_nao_financeiras.py:702, 947`):** Subtrai despesa financeira **nominal** (`kd * dl`, ~18–20% a.a., que embute a amortização inflacionária $\pi \cdot DL$) de NOPAT **real**, subestimando severamente `lpa_norm`, Graham e P/L de empresas alavancadas; em sentido oposto, desconta benefício fiscal nominal fixo por taxa real (`:590, 703, 754`).
2. **`[F3-02]` Trava de Crescimento do DCF Compara ROIC Real com WACC Nominal (`motor_nao_financeiras.py:688-698, 721`):** `roic_rep_c` já tem o imobilizado inflacionado pelo IPCA (sendo retorno real), mas é comparado contra `w_nom` (~19% nominal), zerando o crescimento (`g_ef = 0`) até de compounders como `WEGE3`; além disso, `roic` divide margem de 10 anos pelo capital investido de 2026 (`H6`).
3. **`[F3-03]` Espiral da Morte no Ponto Fixo de Hamada + Dupla Contagem do Desconto (`motor_nao_financeiras.py:609-660`):** Usa dívida **bruta** (ignorando caixa) sobre $E$ calculado pelo próprio valor central já descontado pelo controlador (`A1`), explodindo $K_e$ para **64,7% em `KLBN11`** e **34,3% em `SUZB3`** e alterando `nota_qualidade`.
4. **`[F1-02]` Silenciamento de Dado Contábil Ausente (`motor_nao_financeiras.py:27`, `montar_series.py:48`):** `v(d, k, 0)` converte `None` em `0`, permitindo que o motor emita palavra de decisão mesmo sem D&A (18/21 industriais), imobilizado (16/21), caixa (14/21) ou dívida (14/21).
5. **`[F1-01]` Mutação Global em Tempo de Importação (`lote4_saude_telecom.py:116-125`, `lote6_quimica.py:127-128`):** Importar `lote4` ou `lote6` altera `CVM` e `SI` in-place para `VIVT3`, `WEGE3`, `TIMS3` e `EGIE3`; chamar `avaliar()` sem importar o lote antes produz outro valor justo.
6. **`[F5-01]` Auto-Mascaramento do Oráculo em 92,7% do Hall (`oraculo/reconciliacao.py:16-17, 161, 183`):** Erros de identidade contábil ou de 1000× no número de ações só reprovam se a palavra for `BARATA`/`RADAR`/`JUSTA` (3 de 41 tickers). Se um bug de 1000× nas ações dividir o valor justo por 1000, o ticker vira `CARA` e o erro é rebaixado para simples `"bandeira"` (`exit 0`).
7. **`[F3-04]` Calibração Sistematicamente Enviesada para `CARA` em `motor_financeiras.py` (`H8`, `H9`, `H11`):** Soma prêmio de 5% sobre NTN-B 2050 sem descontar risco soberano (`Ke_real = 12,06%`), compara `roe_lp` nominal histórico com `Ke_nom = 19,30%` de inflação alta, usa `dpa_medio_5a` nominal sem IPCA e modela concessões elétricas reguladas (RAB) como bancos.
8. **`[F6-01]` Congelamento Operacional de Preços em `15/10/2026` (`backtest/cotahist.py:127`):** Uma única linha de 246 bytes (linha `2059663`) no `COTAHIST_A2026.ZIP` da B3 faz o parser abortar o arquivo anual inteiro há 2 semanas (`BOLETINS/2026-10-30-monitor.md`).
9. **`[F6-02]` Push Direto no `master` sem Testes pelo Hook `auto_commit.py` (`.claude/hooks/auto_commit.py:79-80, 162-167`):** Deleções (`"D" in st`) e edições em arquivos não-`.py` vão direto para `origin/master` sem rodar suíte; em `30/10/2026 21:12` (commit `05e6636`), apagou 25 PDFs e as 6 pastas setoriais da raiz, quebrando `gerar_pdf_lote1..6.py`.
10. **`[F4-02]` 100% das Financeiras/Elétricas com Central Nota C e Literatura Primária Não Lida:** Todas as 20 empresas de `motor_financeiras` têm valor central nota C (`134` origens `C_LOTE`), 40/41 notas qualitativas são arbitradas (`pré-v4`) e 9 autores primários da doutrina seguem sem leitura da obra original.

### As 10 Maiores Forças (Com Evidência Verificada)
1. **Rastreamento de Procedência por Valor (`ferramentas/relatorio/modelo.py:1-95`):** Todo número carrega `Origem(nota="A"|"B"|"C", fonte, detalhe)` e propaga automaticamente a pior nota até a palavra final (`test_fase3_procedencia.py`).
2. **Guarda Física e Lógica de Dados Privados (`ferramentas/relatorio/carteira.py:295-314`):** `garantir_ignorado()` executa `git check-ignore -q` antes de gravar qualquer relatório ou JSON pessoal; zero vazamentos em todo o histórico Git (`git log --all --full-history`).
3. **Anonimização Dupla LGPD no FRE (`ferramentas/dossie/fre.py:50-128`):** Filtra pessoas físicas tanto pelo campo estruturado `Tipo_Pessoa` quanto por regex de CPF/nomes antes de persistir qualquer dado societário.
4. **Servidor Local Endurecido (`ferramentas/painel/servir.py:24-69`):** Bind exclusivo em `127.0.0.1` com `SO_EXCLUSIVEADDRUSE`, bloqueio de DNS rebinding via header `Host`, bloqueio de `%00` e NTFS ADS (`::$DATA`), e `Content-Security-Policy: default-src 'self'`.
5. **Ledger Prospectivo Encadeado por SHA-256 (`ferramentas/registro_prospectivo.py:92-122`):** `vereditos.jsonl` e `vereditos.chain` garantem imutabilidade criptográfica das previsões gravadas.
6. **Pré-Registro Explícito com Portão de Falsificação (`docs/PRE-REGISTRO-v3.md`):** O projeto rodou o experimento da proxy em `05/10/2026`, obteve 70,7% (< 80% pré-registrado) e **aceitou a reprovação sem ajustar parâmetros post-hoc**.
7. **Diagnóstico Interno Honesto de Hipóteses (`ferramentas/oraculo/hipoteses.py`, `docs/oraculo/hipoteses-2026-10-22.md`):** O próprio repositório já quantificou os defeitos H1 a H11 com evidência numérica reproduzível.
8. **Troca Atômica de Dados no Monitor (`ferramentas/monitor_semanal.py:91-111`):** Quando o parser recusou o `COTAHIST_A2026.ZIP` novo, `trocar_e_gerar()` restaurou o arquivo anterior sem corromper o estado e estampou `DADO VELHO` no boletim.
9. **Extração Direta de ZIPs Oficiais CVM/B3 (`ferramentas/coletar_cvm.py`, `derivados_zip.py`, `proventos_ex.py`):** Elimina intermediários comerciais para demonstrações contábeis industriais e eventos corporativos no COTAHIST.
10. **Separação Estrita entre Preço Informativo e Veredito Vigente (`ferramentas/painel/exportar.py:1-11`, `monitor_semanal.py`):** Oscilação diária de cotação move apenas o marcador na régua (`P/C hoje`), sem trocar a palavra de decisão sem reavaliação.

---

## b. Mapa do Projeto (Síntese de Viabilidade)

> A tabela detalhada com contagens por extensão e tamanhos consta em [`MAPA-PASTAS.md`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/_auditoria_antigravity/MAPA-PASTAS.md).

| Grupo / Pasta | Arquivos (Disco / Git) | Tamanho Disco | Veredito | Síntese do Motivo |
|---|---:|---:|---|---|
| `00`–`09-*.md`, `CLAUDE.md`, `README.md`, `PROJECT_BRIEF.md` | 15 / 15 | 0,36 MB | **MANTER** (`01`: **CORRIGIR**) | Núcleo normativo claro; alinhar `01-doutrina` com correções matemáticas dos motores. |
| `BOLETINS/`, `DOSSIES/`, `RELATORIOS/`, `scripts/` | 58 / 56 | 1,92 MB | **MANTER** | Saídas auditáveis das rotinas, dossiês e relatórios com isolamento de `RELATORIOS/privado/`. |
| `ferramentas/painel/`, `ferramentas/prospectivo/`, `ferramentas/monitor/` | 203 / 40 | 9,82 MB | **MANTER** | Componentes mais sólidos do projeto (tela somente-leitura e hash-chain prospectivo). |
| `ferramentas/motor_*.py`, `lote*.py`, `dossie/`, `relatorio/`, `triagem/`, `oraculo/`, `tests/`, `backtest/`, `agendador/`, `.claude/` | 1.158 / 241 | 674,40 MB | **CORRIGIR** | Concentram os bugs críticos de valuation (`F3-01..03`), mutação global (`F1-01`), COTAHIST (`F6-01`), `auto_commit` (`F6-02`) e oráculo (`F5-01`). |
| `docs/`, `_historico/`, `UPLOAD CLAUDE DESKTOP/`, `ferramentas/dados/`, `ferramentas/gerar_pdf_lote*.py` | 1.979 / 342 | 1.733,90 MB | **SIMPLIFICAR** | Reduzir duplicação (`_historico/` = 50% do Git; `UPLOAD CLAUDE DESKTOP/` defasado; ~250 linhas clonadas por `gerar_pdf_lote*`). |
| `analisador/`, `ferramentas/atualizar_hall_lote*.py` | 3.731 / 6 | 4.227,87 MB | **ARQUIVAR** | `analisador/` é projeto morto de 4,23 GB no workspace; `atualizar_hall_lote*.py` foi superado por `hall03.py`. |
| `.playwright-mcp/`, `ferramentas/.hypothesis/` | 1.205 / 0 | 7,28 MB | **REMOVER** | Artefatos temporários de navegador e cache de Hypothesis copiado inutilmente para `%TEMP%`. |

---

## c. Achados por Fase (Ordenados por Gravidade)

### FASE 0 — Inventário e Higiene do Repositório

- **`[F0-01] [MÉDIO]` [`ferramentas/oraculo/armadilhas/__main__.py:45,83,91`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/oraculo/armadilhas/__main__.py#L45-L91) — 16 worktrees órfãos deixados em `%TEMP%/oraculo_mudancas_*`**
  - **Evidência:** `git worktree list` retorna 16 worktrees ativos em `C:/Users/frank/AppData/Local/Temp/oraculo_mudancas_3nxcne50/mudanca_01..08/repo` e `..._vygrp3nn/mudanca_01..08/repo` (commit `9e9e8ac`).
  - **Impacto:** Polui `.git/worktrees/`, impede garbage collection de objetos Git e acumula diretórios temporários.
  - **Correção sugerida:** Executar `git worktree prune` e limpar pastas `oraculo_mudancas_*` órfãs no início de `armadilhas/__main__.py`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F0-02] [BAIXO]` [`UPLOAD CLAUDE DESKTOP/01-doutrina-value-investing.md:1`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/UPLOAD%20CLAUDE%20DESKTOP/01-doutrina-value-investing.md#L1) — Pasta `UPLOAD CLAUDE DESKTOP/` defasada em relação à raiz**
  - **Evidência:** SHA-256 diverge da raiz em `01-doutrina-value-investing.md` (61.073 vs 60.953 bytes), `02-prompt-analise-completa.md` (parado em 09/10 vs 14/10), `03-hall-de-acoes.md` (21/10 vs 22/10) e `README.md` (5.183 vs 8.297 bytes); os 6 PDFs são de 09/10 e falta `09-diario-de-decisoes.md`.
  - **Impacto:** Uso da pasta no Claude Desktop alimenta o modelo com regras e Hall desatualizados.
  - **Correção sugerida:** Automatizar a sincronização em `rodar_tudo.py` ou gerar pacote de upload sob demanda sem duplicar arquivos no Git.
  - **Esforço:** P — **Confiança:** alta.

- **`[F0-03] [BAIXO]` [`analisador/ARQUIVADO.md:1`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/analisador/ARQUIVADO.md#L1) e `.playwright-mcp/` — 4,24 GB de arquivos mortos/temporários no workspace ativo**
  - **Evidência:** `analisador/` ocupa 4.227,82 MB (3.725 arquivos, sendo 4.197,45 MB em `analisador/dados/`); `.playwright-mcp/` ocupa 6,64 MB (67 arquivos `.png`/`.yml`/`.log`).
  - **Impacto:** Consome 63,6% do espaço em disco da pasta do projeto e lentifica buscas/indexação.
  - **Correção sugerida:** Mover `analisador/` para arquivo morto externo ao workspace e remover `.playwright-mcp/`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F0-04] [BAIXO]` [`ferramentas/historico_arquivos.py:1-35`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/historico_arquivos.py#L1-L35) — `_historico/` versiona 182 arquivos (15,67 MB = 50% do tamanho do Git) duplicando o `git log`**
  - **Evidência:** `git ls-files _historico` lista 182 arquivos (58 subpastas, incluindo backups diários de `PROJECT_BRIEF.md` e 23 PDFs antigos).
  - **Impacto:** Incha o repositório Git com cópias completas de arquivos já versionados no histórico de commits.
  - **Correção sugerida:** Confiar no `git log` / tags Git para arquivos rastreados, ou ignorar `_historico/` no `.gitignore` mantendo-o apenas no backup local/OneDrive.
  - **Esforço:** P — **Confiança:** alta.

- **`[F0-05] [BAIXO]` [`.gitignore:1-40`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/.gitignore#L1-L40) — `ferramentas/.hypothesis/` (1.138 arquivos) ausente do `.gitignore` da raiz**
  - **Evidência:** `.gitignore` ignora `.pytest_cache/` (linha 3), mas não `.hypothesis/`. Como `conferir_noite.py:68` usa `git status --ignored -s`, ele enxerga `.hypothesis/` como dado local ignorado e copia seus 1.138 arquivos para cada worktree temporária.
  - **Impacto:** Lentidão de I/O em `conferir_noite.py` e risco de rastreamento acidental se o `.gitignore` interno do Hypothesis for removido.
  - **Correção sugerida:** Adicionar `.hypothesis/` ao `.gitignore` da raiz e à tupla `FORA` em `conferir_noite.py:35`.
  - **Esforço:** P — **Confiança:** alta.

---

### FASE 1 — Arquitetura e Código

- **`[F1-01] [CRÍTICO]` [`ferramentas/lote4_saude_telecom.py:116-125`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/lote4_saude_telecom.py#L116-L125) e [`ferramentas/lote6_quimica.py:127-128`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/lote6_quimica.py#L127-L128) — Mutação in-place dos dicionários globais `CVM` e `SI` em tempo de importação altera o resultado de `avaliar()` conforme a ordem de `import`**
  - **Evidência:** `lote4_saude_telecom.py:116-125` executa no nível do módulo `for tk in ("VIVT3", "WEGE3", "TIMS3"): ... CVM[tk]["anos"][a]["arrendamento_pago"] = ...`; `lote6_quimica.py:127-128` executa `SI["EGIE3"]["dpa_por_ano"] = ...` no import.
  - **Impacto:** Chamar `motor_nao_financeiras.avaliar(emp)` para `VIVT3`, `WEGE3` ou `TIMS3` sem antes importar `lote4_saude_telecom` calcula `owner_earnings_ano` sem subtrair `arrendamento_pago` (IFRS 16), mudando a âncora `oe` e o valor central.
  - **Tentativa de refutação (ceticismo obrigatório):** Verificamos se `dossie/base.py` ou `motor_nao_financeiras.py` já injetam `arrendamento_pago` por conta própria. Não injetam: `dossie/base.py:165` apenas lê `a.get("arrendamento_pago")` se já estiver no JSON ou em `CVM`, e `painel/exportar.py:67` contorna o problema importando todos os `lote1..6` no topo. Qualquer script/teste que importe apenas `motor_nao_financeiras` obtém números diferentes. **Refutação rejeitada; achado confirmado.**
  - **Correção sugerida:** Mover a derivação de `arrendamento_pago` (e ajuste de DPA por bonificação da `EGIE3`) para `montar_series.py` / `series_vigente.py` (ou para dentro de `motor_nao_financeiras.py`), tornando `CVM` e `SI` imutáveis em tempo de execução.
  - **Esforço:** P — **Confiança:** alta.

- **`[F1-02] [CRÍTICO]` [`ferramentas/motor_nao_financeiras.py:27,176-177,214,250,273-277,287,297`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_nao_financeiras.py#L27) e [`ferramentas/montar_series.py:48`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/montar_series.py#L48) — Helper `v(d, k, 0)` e `montar_series.py` convertem `None`/conta ausente em `0` silenciosamente, gerando palavra de decisão mesmo sem contas críticas**
  - **Evidência:** `def v(d, k, padrao=0): x = d.get(k); return padrao if x is None else x` (`motor_nao_financeiras.py:27`) e `return 0.0` em `montar_series.py:48`. Conforme medido em `docs/oraculo/hipoteses-2026-10-22.md:16` (H10) e pelo teste `@pytest.mark.xfail` em `test_oraculo_propriedades.py:473`, apagar `da` mantém palavra de decisão em 18/21 industriais, `imobilizado` em 16/21, `caixa` em 14/21, `divida` em 14/21 e `pl` em 9/21.
  - **Impacto:** Se uma empresa mudar o código de uma conta na DFP/ITR ou se um campo vier `None`, o motor assume dívida zero, depreciação zero ou imobilizado zero e emite veredito (`BARATA`/`JUSTA`/`CARA`) em vez de `NÃO CONCLUSIVO`.
  - **Tentativa de refutação:** Verificamos se `oraculo/reconciliacao.py` bloqueia esse erro. Não bloqueia nas 38 empresas `CARA`/`NC` (vira `"bandeira"`) nem faz parte de `avaliar()`. **Refutação rejeitada; achado confirmado.**
  - **Correção sugerida:** Distinguir `None` (dado não apurado) de `0.0` (saldo contábil zero verificado na DFP) desde `montar_series.py`, exigindo presença de `receita`, `ebit`, `lair`, `lucro`, `pl`, `imobilizado`, `caixa`, `divida_cp`, `divida_lp`, `da`, `fco` e `capex` no último exercício; na ausência de qualquer um deles, retornar `palavra = "NÃO CONCLUSIVO"` com alerta explícito.
  - **Esforço:** M — **Confiança:** alta.

- **`[F1-03] [ALTO]` [`ferramentas/lote3_agro.py:37`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/lote3_agro.py#L37), [`ferramentas/lote4_saude_telecom.py:84,150`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/lote4_saude_telecom.py#L84) e [`ferramentas/lote6_quimica.py:102`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/lote6_quimica.py#L102) — Heurísticas divergentes e frágeis de escala do número de ações (`composicao_capital` CVM em unidades vs. milhares)**
  - **Evidência:** `lote3_agro.py:37` e `lote4_saude_telecom.py:150` usam `if n < 1e7: n *= 1000`; `lote4_saude_telecom.py:84` (`acoes_liquidas_2025`) usa `return n * 1000 if n < 1e8 else n`; `lote6_quimica.py:102` não aplica multiplicador algum; `dossie/base.py:180` compara `abs(math.log10(candidato / acoes_fre))`.
  - **Impacto:** Na regra `n < 1e8` de `lote4:84`, qualquer companhia com menos de 100 milhões de ações já informadas em unidades (ex.: small/mid caps como `ALLD3`, `LEVE3`, `FESA4`, `SHUL4`, `VLID3`) teria seu número de ações multiplicado por 1.000, dividindo o valor justo por 1.000.
  - **Correção sugerida:** Unificar a leitura de ações em uma única função em `series_vigente.py` ou `derivados_zip.py` que valide a escala contra o FRE (`acoes_fre`) e contra `valor_mercado / preco`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F1-04] [ALTO]` [`ferramentas/gerar_pdf_lote4.py:46-50`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/gerar_pdf_lote4.py#L46-L50) e `gerar_pdf_lote1..6.py` — Duplicação de ~250 linhas entre geradores de PDF, omissão do desconto do controlador em `central_rapido` do Lote 4 e quebra de todos os 6 scripts por deleção das pastas de saída**
  - **Evidência:** Em `gerar_pdf_lote4.py:46-50`, `central_rapido(emp, **kw)` calcula `ec = estrutura_de_capital(emp, MK)` **antes** de aplicar `**kw` em `emp2` e retorna `median(v["anc"].values())` **sem multiplicar por `(1 - desc_de(emp2))`** (diferente de `gerar_pdf_lote5.py:54` e `gerar_pdf_lote6.py:55`). Além disso, todos os 6 scripts apontam `SAIDA` para as pastas setoriais da raiz apagadas no commit `05e6636` e falham com `FileNotFoundError`.
  - **Impacto:** A tabela de sensibilidade do PDF do Lote 4 ignora o desconto do controlador e os pesos recalculados de capital; e nenhum dos 6 PDFs setoriais pode ser regerado hoje.
  - **Correção sugerida:** Extrair o motor comum de geração de PDF de lotes para um único módulo parametrizado, usar `avaliar(emp2)["central"]` em `central_rapido` e criar `SAIDA.parent.mkdir(parents=True, exist_ok=True)` (ou consolidar em `RELATORIOS/`).
  - **Esforço:** M — **Confiança:** alta.

- **`[F1-05] [ALTO]` [`ferramentas/proventos_ex.py:31-40`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/proventos_ex.py#L31-L40) e [`ferramentas/relatorio/quali.py:29-34`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/relatorio/quali.py#L29-L34) — Tabelas `PREGAO`, `CLASSE` e `CADASTRO` incompletas (restritas aos 6 tickers atuais da carteira)**
  - **Evidência:** `proventos_ex.py:31-40` cadastra apenas 6 tickers em `PREGAO`/`CLASSE` (`BBAS3`, `BBSE3`, `ABCB4`, `ITSA4`, `ISAE4`, `RANI3`). Outras 14 financeiras/elétricas do Hall (`ITUB4`, `BBDC4`, `BRSR6`, `SANB11`, `BPAC11`, `PINE4`, `B3SA3`, `CXSE3`, `TAEE11`, `EGIE3`, `CPFE3`, `CMIG4`, `CPLE3`, `EQTL3`, `NEOE3`, `SAPR11`, `CSMG3`, `SBSP3`) não estão em `PREGAO` nem em `CLASSE` (`CLASSE.get(tk, "ON")` assume `"ON"` por padrão, errando PNs e Units como `TAEE11`, `SAPR11`, `SANB11`). Em `relatorio/quali.py:29-34`, `CADASTRO` tem apenas 6 empresas do Hall (35 de 41 ficam com `"CNPJ não cadastrado em relatorio/quali.py"` na seção Governança).
  - **Impacto:** Adicionar qualquer outro banco, seguradora ou elétrica do Hall à carteira quebra `python -m relatorio CARTEIRA` ou calcula dividendos de Unit/PN com fator de classe errado; 85% do Hall não tem seção de governança FRE no relatório.
  - **Correção sugerida:** Preencher `PREGAO`, `CLASSE` e `CADASTRO` para todos os 41 tickers do Hall (derivando classe ON/PN/UNIT automaticamente do sufixo 3/4/5/6/11 e composição do `MANIFESTO.json`).
  - **Esforço:** M — **Confiança:** alta.

- **`[F1-06] [MÉDIO]` [`ferramentas/defasagem.py:11,14`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/defasagem.py#L11-L14), [`ferramentas/motor_nao_financeiras.py:38,198,260,583,811,937-939`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_nao_financeiras.py#L937-L939) e [`ferramentas/dossie/base.py:222,254`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/dossie/base.py#L222-L254) — Datas e anos chumbados (`2026-10-05`, `"2025"`, `ANO_BASE = 2026`) que ignoram `na_data()`**
  - **Evidência:** `defasagem.py:11,14` fixa `DATA_BASE = datetime(2026, 10, 5)` e `ANOS = ("2023", "2024", "2025")`; `motor_nao_financeiras.py:937-938` fixa `ult, pen = ("2026", "2025") if emp.ticker == "SMTO3" else ("2025", "2024")`.
  - **Impacto:** Na virada para as DFPs de 2026 (ou ao rodar `dossie.gerar --data` em outra data-base), `defasagem.py` continuará medindo atraso contra `05/10/2026` e o motor continuará lendo `"2025"` como último ano até edição manual em múltiplos arquivos.
  - **Correção sugerida:** Derivar `ult` e `pen` dinamicamente de `sorted(a.keys())[-1]` e ler a data-base ativa do contexto `na_data()` / `mercado_vigente.json`.
  - **Esforço:** M — **Confiança:** alta.

- **`[F1-07] [MÉDIO]` [`ferramentas/motor_nao_financeiras.py:866-879`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_nao_financeiras.py#L866-L879) — Bisseções de `ke_implicito` e `g_implicito` retornam silenciosamente a borda quando não há raiz no intervalo**
  - **Evidência:** Em `_bissecao(f, lo, hi)` (`:866-879`), se `f(lo)` e `f(hi)` têm o mesmo sinal, o laço converge para `lo` ou `hi` e retorna esse limite sem verificar se `abs(f(mid)) < tol`. Para `KLBN11` (cujo `Ke` no modelo é 64,7% > `hi = 0.50`), `ke_implicito` retorna `0.50` (`50,0%`) falso no `golden.json`.
  - **Impacto:** Exibe `Ke implícito` ou `g implícito` enganoso no relatório/painel quando a solução real está fora de `[6%, 50%]` ou `[-15%, Ke - 1,5%]`.
  - **Correção sugerida:** Testar mudança de sinal `f(lo) * f(hi) <= 0` antes da bisseção (ou validar `abs(f(mid) - alvo) / alvo < 0.02` ao final), retornando `None` quando não houver raiz no domínio.
  - **Esforço:** P — **Confiança:** alta.

- **`[F1-08] [ELOGIO]` [`ferramentas/relatorio/modelo.py:1-95`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/relatorio/modelo.py#L1-L95) e [`ferramentas/relatorio/procedencia.py:1-120`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/relatorio/procedencia.py#L1-L120) — Rastreamento algébrico de procedência (`Numero` + `Origem` A/B/C)**
  - **Evidência:** A classe `Numero` encapsula valor, unidade e tupla de `Origem(nota, fonte, detalhe)`, e `pior(*origens)` propaga a pior nota (A > B > C) das folhas até as âncoras e o valor central (`test_fase3_procedencia.py`).
  - **Impacto:** Impede que um insumo nota C se disfarce de nota A após passar por fórmulas intermediárias.
  - **Correção sugerida:** Manter e estender para 100% dos campos auxiliares.
  - **Esforço:** P — **Confiança:** alta.

---

### FASE 2 — Testes e Reprodutibilidade

#### Resultado Real da Suíte Executada Nesta Auditoria
Executamos `python -m pytest --rootdir=. -c NUL --ignore=backtest -q -rs` em `ferramentas/`:
- **Resultado no ambiente sandboxed (`task-20`):** **`1041 passed, 9 failed, 2 xfailed, 9 errors in 961.55s (0:16:01)`**.
  - As **8 falhas** em `painel/tests/test_servir.py` (`PermissionError: [WinError 10013]` ao conectar em socket TCP loopback) e os **9 erros + 1 falha** em `tests/test_conferir_noite.py` (`git clone` local bloqueado no sandbox) decorrem das restrições de socket/processo do sandbox.
  - Na execução via `python -m oraculo` (que roda `pytest --ignore=backtest -q` sem as suítes de painel/backtest): **`1091 passed, 1 failed, 1 xfailed in 248.4s`**, onde a falha foi um **`XPASS(strict)` estocástico** em `test_desconto_do_controlador_so_no_valor_industrial` (`[F2-02]`), enquanto em `task-20` o mesmo teste deu `xfail` (`x.x`), comprovando na prática a flakiness da suíte!

- **`[F2-01] [ALTO]` [`ferramentas/conftest.py:1`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/conftest.py#L1) e [`ferramentas/oraculo/__main__.py:61`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/oraculo/__main__.py#L61) — Ausência de `pyproject.toml` ou `pytest.ini` no repositório quebra a descoberta de `rootdir` do `pytest`**
  - **Evidência:** Ao rodar `cd ferramentas && python -m pytest --ignore=backtest -q`, o `pytest` sobe a árvore de diretórios até `C:\Users\frank\pyproject.toml`, falhando com `PermissionError: [Errno 13] Permission denied: 'C:\\Users\\frank\\pyproject.toml'` em ambientes restritos ou herdando configurações globais alheias ao projeto.
  - **Impacto:** Quebra reprodutibilidade entre máquinas/ambientes e derruba a etapa `suite` de `python -m oraculo`.
  - **Correção sugerida:** Criar `ferramentas/pytest.ini` (mesmo vazio ou com `[pytest]\ntestpaths = tests dossie/tests painel/tests`) para ancorar o `rootdir` em `ferramentas/`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F2-02] [ALTO]` [`ferramentas/tests/test_oraculo_propriedades.py:33,473,499`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/tests/test_oraculo_propriedades.py#L473-L510) — Flakiness estocástica por `@pytest.mark.xfail(strict=True)` combinado com `max_examples=6` sem `@seed` fixo**
  - **Evidência:** No perfil padrão `"curto"` (`N_IND = 12` empresas sorteadas por `max_examples = 6` na linha 33), `test_desconto_do_controlador_so_no_valor_industrial` (`:499`) só falha quando o Hypothesis sorteia uma empresa alavancada e um desconto grande o suficiente para mudar `nota_qualidade`. Na nossa execução de `python -m oraculo`, os 6 exemplos sorteados não mudaram a nota, gerando `XPASS(strict)` e **reprovando a suíte**; já em `task-20`, os 6 exemplos sorteados geraram `xfail`.
  - **Impacto:** A suíte principal e o oráculo falham ou passam aleatoriamente sem nenhuma mudança de código.
  - **Correção sugerida:** Adicionar `@seed(...)` determinístico ou `@example(...)` explícito com o contraexemplo conhecido (ex.: `KLBN11` / `SUZB3` com `pct=0.25`) em todo teste `@given` marcado com `xfail(strict=True)` — ou corrigir logo os bugs `A1` e `H10` no motor.
  - **Esforço:** P — **Confiança:** alta.

- **`[F2-03] [ALTO]` [`ferramentas/tests/test_oraculo_propriedades.py:67-69`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/tests/test_oraculo_propriedades.py#L67-L69) — Fixture `_rapido()` desliga `ke_implicito` e `g_implicito` em todos os testes de propriedade**
  - **Evidência:** `monkeypatch.setattr(M, "ke_implicito", lambda *_: None)` e `monkeypatch.setattr(M, "g_implicito", lambda *_: None)` com `autouse=True` (`:65-69`).
  - **Impacto:** `test_sem_nan_nem_inf_industrial` (`:311`) jamais exercita as bisseções de `ke_implicito` e `g_implicito`, ocultando o bug `[F1-07]` (retorno silencioso da borda `0.50` na `KLBN11`).
  - **Correção sugerida:** Remover `autouse=True` de `_rapido()` para `test_sem_nan_nem_inf_industrial` (ou criar um teste de propriedade específico para `ke_implicito` e `g_implicito`).
  - **Esforço:** P — **Confiança:** alta.

- **`[F2-04] [ALTO]` [`ferramentas/golden.py:13-20,52`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/golden.py#L13-L20) — `golden.json` monitora apenas 12 campos resumidos das 41 empresas do Hall e ignora as 6 empresas exclusivas de `dossie/`**
  - **Evidência:** `CAMPOS_NUM` e `CAMPOS_TXT` (`golden.py:13-20`) não incluem `compra`, `compra_parcial`, `saida`, `saida_por_qualidade`, `roic`, `roic_reposicao`, `wacc`, `ke_nom_emp`, `ke_implicito`, `g_implicito`, `piotroski`, `beneish`, `altman`, `sloan`; além disso, `ALLD3`, `BLAU3`, `CMIN3`, `FESA4`, `SHUL4` e `VLID3` não estão no `golden.json`. Na linha 52, `a == b` avalia `inf == inf` como `True`.
  - **Impacto:** Regressões nos preços-gatilho (`compra`/`saida`), no WACC/ROIC ou nos 6 dossiês fora do Hall passam despercebidas pelo teste de regressão `test_golden.py`.
  - **Correção sugerida:** Incluir `compra`, `saida`, `roic`, `roic_reposicao`, `wacc`, `ke_nom_emp` em `CAMPOS_NUM`, adicionar os 6 tickers de `dossie/` ao golden e rejeitar `math.isinf(a)` em `_mudou()`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F2-05] [ALTO]` [`ferramentas/oraculo/matriz.py:1-220`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/oraculo/matriz.py#L1-L220) e [`ferramentas/oraculo/rastreabilidade.py:34-45`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/oraculo/rastreabilidade.py#L34-L45) — 60 de 190 regras calculáveis da doutrina (31,6%) sem teste específico e verificação puramente sintática**
  - **Evidência:** A matriz declara 36 regras com ` status="lacuna"` (`LACUNAS_MAX = 36` em `rastreabilidade.py:21`) e 24 regras em `camada=0` (cobertas apenas pelo `golden.json`). Além disso, `rastreabilidade.py:34-45` apenas verifica se o nome `def test_...` existe na AST do arquivo, sem checar se o teste está marcado com `xfail` ou se executa asserções reais.
  - **Impacto:** Quase um terço das regras calculáveis da doutrina não possui teste unitário ou de propriedade dedicado.
  - **Correção sugerida:** Converter progressivamente as 36 lacunas e 24 regras de camada 0 em testes de camada 1/2 e descontar testes `xfail` da contagem de regras cobertas.
  - **Esforço:** M — **Confiança:** alta.

- **`[F2-06] [MÉDIO]` [`ferramentas/conftest.py:45-50`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/conftest.py#L45-L50) e [`ferramentas/painel/sistema.py:86-98`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/painel/sistema.py#L86-L98) — `suite_ultima.json` registra suíte limpa mesmo quando 42 testes de dados são pulados sem `EXIGIR_DADOS=1`**
  - **Evidência:** Existem 42 chamadas `pytest.skip` dependentes de ZIPs CVM/COTAHIST/PDFs. Sem `EXIGIR_DADOS=1`, `conftest.py` grava `suite_ultima.json` com `failed: 0` e `painel/sistema.py` não gera aviso quando `skipped > 0`.
  - **Impacto:** A tela `Sistema` pode exibir suíte saudável mesmo quando os testes de integridade de dados brutos não rodaram.
  - **Correção sugerida:** Exibir aviso explícito em `painel/sistema.py` quando `suite.get("skipped", 0) > 0`.
  - **Esforço:** P — **Confiança:** alta.

---

### FASE 3 — Doutrina e Valuation (Visão de Investidor Fundamentalista Sênior)

- **`[F3-01] [CRÍTICO]` [`ferramentas/motor_nao_financeiras.py:575-591,702-703,712,754,947`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_nao_financeiras.py#L947) — Mistura de juros nominais (`kd`) em lucro normalizado real (`lpa_norm` e `lair_norm`) e desconto real sobre benefício fiscal nominal fixo**
  - **Evidência:** Na linha 947, `lucro_norm = r["nopat"] - r["kd"] * r["dl"] * (1 - r["aliquota"])` (e na linha 702, `lair_norm = lucro_pre_ir - kd * max(dl, 0.0)`), onde `nopat` e `lucro_pre_ir` estão em reais constantes de hoje (deflacionados por IPCA), mas `kd` (~18–20% a.a.) é **nominal** (inclui $\pi = 6,46\%$ de inflação, que economicamente corresponde à amortização real do principal da dívida pela inflação, $\pi \cdot DL$, e não a despesa real perpétua). Em sentido inverso, `beneficio_fiscal()` (`:590-591`) soma créditos fiscais fixos em reais nominais correntes (ex.: ágio da `HYPE3` até 2030) descontados à taxa **real** `w_real` (`:703, 712`) e `ke_real` (`:754`), enquanto `credito_observado` (`:575`) deflaciona apenas até `ult` (`2025`) em vez de hoje.
  - **Impacto:** Para toda empresa industrial com dívida líquida positiva (`KLBN11`, `SUZB3`, `LEVE3`, `SMTO3`, `SLCE3`, `MOVI3`/`VAMO3`), subtrair `kd` nominal de `nopat` real subestima drasticamente `lpa_norm`, distorcendo 3 das 5 âncoras (Graham, Graham-BR, Graham revisado), o P/L normalizado, o teto `dmult` (`<= 2.0 * g_mult`) e o retorno de Bogle. Já o benefício fiscal nominal descontado a taxa real superestima o valor presente do escudo fiscal.
  - **Tentativa de refutação:** Verificamos se a doutrina (`01:194`) prescreve `kd` nominal sobre `nopat` real intencionalmente como margem de segurança extra. Não: a Doutrina §4 (`01:55`) proíbe expressamente: *"Nunca misture: fluxo em reais correntes → Ke nominal; fluxo real → Ke real"*. Misturar `nopat` real com encargo nominal viola a identidade contábil em moeda constante. **Refutação rejeitada; achado confirmado.**
  - **Correção sugerida:** Usar custo real da dívida `kd_real = (1 + kd) / (1 + pi) - 1` (ou adicionar o ganho inflacionário sobre a dívida líquida $\pi \cdot DL$) no cálculo de `lucro_norm` e `lair_norm` em moeda constante; e descontar fluxos nominais fixos de `beneficio_fiscal` por `w_nom` / `ke_nom` (deflacionando `credito_observado` até hoje).
  - **Esforço:** M — **Confiança:** alta.

- **`[F3-02] [CRÍTICO]` [`ferramentas/motor_nao_financeiras.py:688-698,721,733`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_nao_financeiras.py#L688-L733) — Trava de crescimento do DCF compara `roic_rep_c` (já ajustado pela inflação no denominador) contra `w_nom` nominal (`H1`), e `roic` divide margem de 10 anos pelo capital investido de 2026 (`H6`)**
  - **Evidência:** Em `:694-698`, `cap_rep` multiplica o imobilizado pelo IPCA acumulado na idade média da planta (`fator_inflacao`), reduzindo `roic_rep_c = nop / cap_rep` a uma taxa real (conforme reconhecido em `01-doutrina-value-investing.md:249`: *"Como o denominador já sobe com a inflação, o ROIC de reposição funciona na prática como retorno real"*). Apesar disso, a linha 721 exige `min(roic_c, roic_rep_c) > w_nom` (~19% nominal!) para permitir `g > 0`. Além disso, as linhas 688–692 calculam `roic = nop / cap_inv` combinando margem mediana de 10 anos × receita média de 3 anos no numerador com o capital investido do **último ano (`2025`/LTM)** no denominador (`H6`).
  - **Impacto:** Na `WEGE3`, `roic` cai de 38,5% (DFP ano a ano) para 23,8% (`H6`), e `roic_rep_c` (16,3%) fica abaixo de `w_nom` (19,0%), zerando `g_ef = 0` e `g1e = 0` no DCF da maior compounder industrial da B3 (`docs/oraculo/hipoteses-2026-10-22.md:7,12`).
  - **Tentativa de refutação:** Verificamos se `roic_rep_c` reavalia o lucro pela inflação além do deflator normal. Não: o numerador `nop` é idêntico ao de `roic_c`, enquanto o denominador `cap_rep` absorve 4–8 anos de IPCA acumulado. Compará-lo a `w_nom` duplica a exigência inflacionária. **Refutação rejeitada; achado confirmado.**
  - **Correção sugerida:** (1) Calcular o ROIC histórico ano a ano (`nopat_t / cap_inv_t`) e tomar a mediana do ciclo; (2) comparar `roic_rep_c` contra `w_real` (ou comparar `roic_c` nominalizado contra `w_nom`).
  - **Esforço:** M — **Confiança:** alta.

- **`[F3-03] [CRÍTICO]` [`ferramentas/motor_nao_financeiras.py:609-660`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_nao_financeiras.py#L609-L660) — Fórmulas de Hamada e WACC usam dívida BRUTA sobre $E$ do ponto fixo (já descontado pelo controlador), criando espiral da morte em empresas alavancadas (`H2`) e dupla contagem do desconto do controlador (`A1`)**
  - **Evidência:** `premio_alavancado(d, e, t)` (`:609-614`) e `estrutura_de_capital` (`:621, 653`) usam `bruta` (dívida bruta, ignorando `caixa`!). No laço de ponto fixo (`:648-655`), `c = median(v["anc"].values()) * (1 - desc)` e `e = max(c * n, 1e-6)` realimentam `d / e`.
  - **Impacto:** (1) Uma empresa com R$ 10 bi de dívida bruta e R$ 10 bi em caixa (dívida líquida zero) sofre penalização de $K_e$ como se fosse alavancada; (2) quando `bruta` é alta, a queda do valor central reduz $E$, que explode $D/E$ e joga $K_e$ para **64,7% na `KLBN11`**, **34,3% na `SUZB3`**, **31,3% na `SLCE3`** e **30,3% na `SMTO3`**, com não-unicidade de ponto fixo em `RECV3` (`H2a`); (3) o desconto do controlador `desc` dentro do ponto fixo reduz $E$, aumenta $K_e$ e derruba `nota_qualidade` (`A1`, violando `01:103, 105`).
  - **Tentativa de refutação:** Verificamos se o teto de $D/E$ ou `max(e, 1e-6)` evita a explosão. Não há teto para $D/E$: em `KLBN11`, $D/E$ converge acima de 4,5× e $K_e$ atinge 64,7% a.a. **Refutação rejeitada; achado confirmado.**
  - **Correção sugerida:** (1) Usar dívida **líquida** `max(dl, 0.0)` em Hamada (Damodaran, *Applied Corporate Finance*: cash-adjusted beta/leverage); (2) retirar `(1 - desc)` de dentro do laço de `estrutura_de_capital`, aplicando o desconto do controlador uma única vez na saída; (3) limitar $D/E$ ao intervalo setorial razoável ou usar ponderação com valor de mercado/PL contábil para garantir contração única.
  - **Esforço:** M — **Confiança:** alta.

- **`[F3-04] [ALTO]` [`ferramentas/motor_financeiras.py:242-333,432`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_financeiras.py#L242-L333) e `lote1_bancos.py` / `lote2_energia.py` — Viés sistemático pró-`CARA` (34 `CARA` e 4 `NC` em 41 tickers): `Ke_real = 12,06%` sem expurgo de CDS soberano (`H9`), `roe_lp` nominal histórico comparado a `Ke_nom = 19,30%`, `dpa_medio_5a` nominal sem IPCA e concessões elétricas avaliadas sem RAB (`H11`)**
  - **Evidência:** (1) `Ke_real = 7,06% + 5,00% = 12,06%` (`Ke_nom = 19,30%`) soma ERP cheio sobre a NTN-B 2050 sem descontar o risco soberano (~2–2,5 p.p.) já embutido na NTN-B (`H9` explica 76%–98% da distância ao preço de mercado); (2) em `motor_financeiras.py:278`, `pvp_justificado = (roe_lp - g) / (ke - g)` compara `roe_lp` mediano de 2016–2025 (quando a inflação média foi ~4,5%) contra `ke = 19,30%` (que embute $\pi = 6,46\%$), forçando $P/VP < 1$ para quase todo banco/elétrica; (3) em `lote1_bancos.py` e `lote2_energia.py:45-47`, `dpa_medio_5a` é média **nominal** 2021–2025 sem deflacionar por IPCA (diferente de `motor_nao_financeiras.py:957`), subestimando dividendos em ~12%–18%; (4) elétricas/saneamento (`lote2_energia.py`, `EGIE3`) são modeladas em `motor_financeiras` sem indenização da RAB no terminal (`H11`).
  - **Impacto:** O sistema classifica 92,7% do Hall fora de decisão e jamais encontra `BARATA` (0 em 41), não apenas por conservadorismo, mas por assimetria inflacionária entre numerador e denominador.
  - **Correção sugerida:** (1) Deflacionar `dpa_medio_5a` pelo IPCA em todas as financeiras/elétricas; (2) alinhar a inflação implícita de `roe_lp` à inflação $\pi$ embutida em `Ke_nom` (trabalhando em termos reais: $ROE_{\text{real}}$ vs. $K_{e,\text{real}}$); (3) separar modelo de concessão regulada (WACC regulatório + RAB terminal) de bancos; (4) revisar a decomposição de $R_f$ na NTN-B (expurgo parcial de prêmio soberano/liquidez).
  - **Esforço:** G — **Confiança:** alta.

- **`[F3-05] [ALTO]` [`ferramentas/motor_financeiras.py:291,296-333`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_financeiras.py#L291-L333) — Colinearidade de 100% entre `P/VP justificado` e `DDM 2 estágios` (`H3`) e erro de `g` pós-renovação / âncora única em `ddm_contrato_finito` (`BBSE3`)**
  - **Evidência:** `ddm_2_estagios` (`:282-293`) usa `pvp_justificado` (`:291`) como valor terminal no ano 5, resultando em similaridade de cosseno $\ge 0,95$ e dispersão mediana de `1,01` em 100% dos bancos/elétricas (`H3`). Já em `ddm_contrato_finito` (`:296-326`, usado para `BBSE3`), aplica-se corte de 40% no lucro no ano 7 (`lpa_pos = lpa * 0.60`, reduzindo o ROE pós-renovação de 65% para 39%, o que com payout de 85% suporta $g_{\text{pos}} = 39\% \times 15\% = 5,85\%$), mas a linha 315 perpetua o `g` **pré-corte** (`6,89%`) em `terminal_renov = d_pos * (1 + g) / (ke - g)`. Além disso, `ancoras()` retorna apenas 1 âncora para `BBSE3`, rebaixando `confianca` para `"baixa (âncora única)"` contra a Doutrina §11.2 (`01:257`).
  - **Impacto:** Falsa sensação de confirmação cruzada em bancos/elétricas e erro algébrico na perpetuidade pós-2033 da `BBSE3` (empresa da carteira!).
  - **Correção sugerida:** Em `ddm_contrato_finito`, recalcular `g_pos = min(roe_pos * (1 - payout), g_teto)` após aplicar `corte_renovacao`, e adicionar a 2ª âncora prevista em `01:257` (P/L histórico ajustado pelo corte).
  - **Esforço:** M — **Confiança:** alta.

- **`[F3-06] [ALTO]` [`ferramentas/motor_financeiras.py:474-477`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_financeiras.py#L474-L477) — `roe_implicito` ignora o desconto do controlador, violando a Doutrina §5 (`01:103`)**
  - **Evidência:** A linha 476 calcula `roe_implicito = g_r + (emp.preco / emp.vpa) * (ke - g_r)` usando `emp.vpa` bruto, enquanto `01-doutrina-value-investing.md:103` determina: *"O Ke implícito e o DCF reverso comparam o preço com o valor **já descontado**"*.
  - **Impacto:** Para toda financeira/elétrica com desconto de controlador (`BBAS3`, `SANB11`, `BRSR6`, `CMIG4`, `CSMG3`, `SAPR11`, `NEOE3`, `EQTL3`, `CPFE3`), o `roe_implicito` reportado subestima o ROE que o mercado exige da operação.
  - **Correção sugerida:** Dividir `emp.preco` por `(emp.vpa * (1 - desc_pct))` em `motor_financeiras.py:476`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F3-07] [ALTO]` [`ferramentas/motor_nao_financeiras.py:925-926`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_nao_financeiras.py#L925-L926) — `ebitda_norm` soma EBIT real de hoje com D&A nominal histórica sem deflacionar por IPCA**
  - **Evidência:** `da_med = median([a[x]["da"] for x in r["op"]["anos"][-3:] ...])` lê `a[x]["da"]` em reais nominais de 2023–2025 e soma diretamente a `r["op"]["receita_meio"] * r["m"]` (que está em reais constantes de 2026).
  - **Impacto:** Subestima `ebitda_norm`, infla `dl_ebitda_norm` e penaliza indevidamente `nota_solidez`.
  - **Correção sugerida:** Deflacionar `a[x]["da"]` por `DEFLATOR[x]` (ou usar a mediana da razão `da / receita` multiplicada por `receita_meio`).
  - **Esforço:** P — **Confiança:** alta.

- **`[F3-08] [MÉDIO]` [`ferramentas/motor_nao_financeiras.py:317-319`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_nao_financeiras.py#L317-L319) — Truncamento assimétrico `max(dwc, 0)` em `owner_earnings_ano`**
  - **Evidência:** A linha 319 subtrai `max(dwc, 0)` a cada ano antes de extrair a mediana de 5 anos.
  - **Impacto:** Penaliza anos de expansão de giro e descarta anos de liberação de giro do mesmo ciclo operacional, enviesando Owner Earnings para baixo em empresas cíclicas.
  - **Correção sugerida:** Calcular a variação líquida média/mediana do capital de giro ao longo do ciclo completo antes de truncar, ou usar `dwc` simétrico na mediana plurianual.
  - **Esforço:** P — **Confiança:** alta.

- **`[F3-09] [MÉDIO]` [`ferramentas/triagem/qualidade.py:81-116`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/triagem/qualidade.py#L81-L116) e [`ferramentas/motor_nao_financeiras.py:961,993-994`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_nao_financeiras.py#L961-L994) — Divergências adicionais entre doutrina escrita e código**
  - **Evidência:** (1) `triagem/qualidade.py:81-99` usa ROIC contábil (sem custo de reposição) e compara todos os anos de 2016–2025 contra o WACC de 2026; (2) `motor_nao_financeiras.py:993-994` calcula `peg` e `pegy` com `g_nom` em vez de `g_real` (`01:236`) e sofre `ZeroDivisionError` se `g_nom == 0`; (3) `bazin6` (`:961` e `motor_financeiras.py:441`) é calculado mesmo quando `cobertura_caixa` é `False` (`01:129`); (4) `motor_nao_financeiras.py` não força `NÃO CONCLUSIVO` quando `lpa_norm <= 0` (`matriz.py:D11.1.52`).
  - **Impacto:** Inconsistências entre o que a doutrina afirma fazer e o que os números exibidos nos relatórios refletem.
  - **Correção sugerida:** Usar `g_real` com guarda `g_real > 0` em `peg`/`pegy`, condicionar `bazin6` a `coberto == True` e forçar `NÃO CONCLUSIVO` quando `lpa_norm <= 0`.
  - **Esforço:** P — **Confiança:** alta.

---

### FASE 4 — Embasamento Científico e Qualidade das Fontes

- **`[F4-01] [ALTO]` [`01-doutrina-value-investing.md:18-30,180-255`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/01-doutrina-value-investing.md#L18-L30) e [`docs/PRE-REGISTRO-v3.md:20-35`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/docs/PRE-REGISTRO-v3.md#L20-L35) — Literatura primária declarada como não lida (Nota C) para 9 autores da doutrina e 5 referências de validação**
  - **Evidência:** Estão marcados como texto primário não conferido: Greenwald (*Value Investing*, 2001), Fisher (*Common Stocks*, 1958), Bazin (*Faça Fortuna com Ações*, 1992), Bogle (*Little Book*, 2017), Piotroski (2000), Altman (1968/1995), Beneish (1999), Sloan (1996), Damodaran (*Investment Valuation* / *Return on Capital*, 2007), além de Barr (2015), Kerr (1998), Harvey/Liu/Zhu (2016), Bailey & López de Prado (2014) e Fed SR 11-7 (2011). (Apenas Graham 1949/1973 e Mauboussin 2001/2014 têm conferência primária registrada).
  - **Impacto:** Fórmulas atribuídas a esses autores (ex.: ajuste de reposição em Greenwald, Altman Z'' para mercados emergentes, Beneish M-Score de 8 variáveis reduzido na tela) carecem de verificação contra o artigo original.
  - **Correção sugerida:** Conferir prioritariamente os papers curtos de acesso aberto (Piotroski 2000, Beneish 1999, Sloan 1996, Altman 1995, Damodaran 2007 e SR 11-7) ou remover a atribuição nominal onde a regra for adaptação autoral da Mesa.
  - **Esforço:** G — **Confiança:** alta.

- **`[F4-02] [ALTO]` [`ferramentas/tests/test_fase3_procedencia.py:309`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/tests/test_fase3_procedencia.py#L309) e [`ferramentas/dossie/notas.py:1-60`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/dossie/notas.py#L1-L60) — Todas as 20 empresas financeiras/elétricas do Hall têm valor central Nota C (`134` origens `C_LOTE`), 40/41 notas qualitativas são arbitradas (`pré-v4`) e 23/41 têm `SEM_RAZAO` no desconto do controlador**
  - **Evidência:** `C_LOTE_NAS_ANCORAS_MAXIMO = 134` em `test_fase3_procedencia.py:309`; em 5 de 18 financeiras/elétricas com DFP disponível (`BBSE3`, `BRSR6`, `CMIG4`, `CPFE3`, `CXSE3`), o `roe_lp` digitado nos lotes diverge em $\ge 1\text{ p.p.}$ da mediana CVM (`H8`). Em `dossie/notas.py`, apenas `ALLD3` tem decomposição auditada v4 das notas qualitativas; 40 de 41 tickers do Hall usam notas arbitradas.
  - **Impacto:** Viola a regra-mãe do `CLAUDE.md:33` (*"só fonte nota A/B embasa decisão"*) para metade do Hall (incluindo 5 das 6 posições da carteira pessoal: `BBAS3`, `BBSE3`, `ABCB4`, `ITSA4`, `ISAE4`).
  - **Correção sugerida:** Migrar `roe_lp`, `vpa`, `lpa_12m` e `payout` das 20 financeiras/elétricas para extração direta das DFPs/ITRs da CVM e preencher a decomposição v4 de `notas.py` começando pelos 6 tickers da carteira.
  - **Esforço:** G — **Confiança:** alta.

- **`[F4-03] [MÉDIO]` [`01-doutrina-value-investing.md:229`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/01-doutrina-value-investing.md#L229) e [`ferramentas/motor_financeiras.py:72`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/motor_financeiras.py#L72) — "Fator Brasil" $f = (1 / K_{e,\text{real}}) / 8,5$ não tem fonte na literatura e resulta em $f = 0,975 \approx 1,0$**
  - **Evidência:** Como $1 / 8,5 = 11,76\%$, para $K_{e,\text{real}} = 12,06\%$ tem-se $f = 8,29 / 8,5 = 0,9755$ (desconto de apenas 2,4% sobre o múltiplo americano de Graham!), porque compara o inverso de $K_{e,\text{real}}$ total (12,06%) com o múltiplo base de crescimento zero de Graham (8,5), que na edição de 1973 era modulado por $4,4 / Y$ (taxa de bonds AAA).
  - **Impacto:** A âncora `graham_br` é praticamente idêntica à `graham` original (`~97,5%`), não cumprindo o propósito declarado na doutrina de ajustar Graham ao juro brasileiro.
  - **Correção sugerida:** Substituir por $f = 4,4 / (100 \cdot R_{f,\text{real}})$ (fórmula original de Graham 1974 aplicada ao juro real) ou remover a âncora duplicada `graham_br`, mantendo apenas `graham_revisado` (que já usa $4,4 / (100 \cdot R_{f,\text{real}})$!).
  - **Esforço:** P — **Confiança:** alta.

- **`[F4-04] [MÉDIO]` [`01-doutrina-value-investing.md:78`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/01-doutrina-value-investing.md#L78) e [`ferramentas/fiscal.py:13`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/fiscal.py#L13) — Alíquota de 17,5% sobre JCP (LC 224/2025) modelada em perpetuidade sem leitura da lei**
  - **Evidência:** `01:78` registra explicitamente que o texto da LC 224/2025 no Planalto não foi lido (apenas Agência Senado/Câmara) e que há dúvida aberta sobre vigência temporária até `31/12/2027`.
  - **Impacto:** Afeta a renda líquida de JCP da carteira (`relatorio/renda.py:16`) e a equivalência dividendo vs. JCP em perpetuidade.
  - **Correção sugerida:** Conferir o texto integral da LC 224/2025 no Portal da Legislação do Planalto e documentar os artigos exatos em `fiscal.py`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F4-05] [ALTO]` [`ferramentas/dados/mercado_vigente.json:1-15`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/dados/mercado_vigente.json#L1-L15) e [`01-doutrina-value-investing.md:53`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/01-doutrina-value-investing.md#L53) — Descasamento de maturidades (NTN-B 2050 de ~24 anos combinada com inflação implícita ANBIMA de 10 anos) e curva parada em `02/10/2026` (`H4`)**
  - **Evidência:** `01:53` exige *"título prefixado de mesmo prazo (LTN / NTN-F)"*, mas `coletar_macro.py` combina o juro real da NTN-B 2050 com a inflação implícita de 2.520 dias úteis (10 anos) da ANBIMA. Além disso, atualizar `mercado_vigente.json` de `02/10/2026` ($\pi = 6,46\%$) para `15/10/2026` ($\pi = 5,75\%$) muda a palavra de `LEVE3` e `ISAE4` de `NÃO CONCLUSIVO` para `JUSTA` (`H4`).
  - **Impacto:** Inconsistência na estrutura a termo da taxa de desconto e sensibilidade de vereditos à data de captura da curva.
  - **Correção sugerida:** Parear NTN-B 2035 (10 anos) com a inflação implícita de 10 anos da ANBIMA (mesmo duration de ~10 anos) ou usar a inflação implícita do vértice longo, e suavizar por média móvel de 20 pregões para evitar troca de palavra por ruído diário de curva.
  - **Esforço:** P — **Confiança:** alta.

---

### FASE 5 — Validação (Oráculo, Pré-Registro e Backtest)

- **`[F5-01] [CRÍTICO]` [`ferramentas/oraculo/reconciliacao.py:16-17,161,183`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/oraculo/reconciliacao.py#L16-L17) e [`ferramentas/oraculo/sanidade.py:17,113`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/oraculo/sanidade.py#L17) — Auto-mascaramento do Oráculo: falhas graves nas 38 empresas `CARA`/`NÃO CONCLUSIVO` (92,7% do Hall) são rebaixadas para `"bandeira"` não-bloqueante (`exit 0`)**
  - **Evidência:** `DECISAO = ("BARATA", "RADAR", "JUSTA")` (`reconciliacao.py:17` e `sanidade.py:17`). Na linha 161 de `reconciliacao.py`, `"falha" if p in DECISAO else "bandeira"`; na linha 183, `"ok": len(falhas) == 0`. Hoje, apenas 3 empresas do Hall (`ABCB4`, `BBAS3`, `ITSA4`) são `JUSTA`; para as outras 38 empresas (incluindo todas as 21 industriais!), qualquer violação de identidade contábil ou erro de 1000× nas ações vira `"bandeira"` e `python -m oraculo` retorna `OK (0 falhas)`.
  - **Impacto:** Se um bug multiplicar o número de ações de uma ação `BARATA` por 1.000, o valor justo cai 1.000×, o P/C sobe 1.000× e a palavra muda para `CARA` — **o que automaticamente rebaixa o erro de `"falha"` para `"bandeira"` e faz o oráculo passar com código 0!**
  - **Tentativa de refutação:** Verificamos se `armadilhas` ou `test_oraculo_propriedades.py` impedem esse auto-mascaramento em produção. Na Armadilha 01 (`01_unidade_acoes.patch`), que aplica exatamente um fator de 1.000× em `B3SA3`, o próprio `docs/oraculo/armadilhas-2026-10-22.md` mostra que `B3SA3` já era `CARA` e continuou `CARA`, ou seja, toda empresa `CARA` fica imune a falhas bloqueantes de reconciliação/sanidade. **Refutação rejeitada; achado confirmado.**
  - **Correção sugerida:** Remover o filtro `if p in DECISAO` para erros estruturais (escala de ações, identidade contábil DFP, `central <= 0`, `NaN`/`inf`), tratando-os como `"falha"` bloqueante em **todas** as 47 empresas (Hall + Dossiês).
  - **Esforço:** P — **Confiança:** alta.

- **`[F5-02] [ALTO]` [`ferramentas/oraculo/armadilhas/__main__.py:61-70`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/oraculo/armadilhas/__main__.py#L61-L70) — Falso "100% de detecção automática" nas armadilhas: Armadilha 02 (`02_real_nominal.patch`) escapou do Oráculo e só quebrou o diff estático de `03-hall-de-acoes.md`**
  - **Evidência:** `armadilhas/__main__.py:62` regrava `golden.json` na worktree para que a Camada 0 não conte como detecção, **mas esquece de regravar `03-hall-de-acoes.md`** (`hall03.py --corrigir`). Na Armadilha 02 (descontar Owner Earnings real por `Ke` nominal), `docs/oraculo/armadilhas-2026-10-22.md:10` registra `pegou_oraculo: false` e `pegou_suite: true (test_hall03.py::test_03_bate_com_o_motor)`, que é exatamente um snapshot estático de Camada 0!
  - **Impacto:** A taxa real de detecção sem snapshots estáticos (Camadas 1–3 + Oráculo) é de **7/8 (87,5%)**, e não 8/8 (100%). O Oráculo não detecta quando uma âncora real é descontada por taxa nominal.
  - **Correção sugerida:** Executar `hall03.py --corrigir` junto com `golden.gravar` em `armadilhas/__main__.py:62` para medir a detecção genuína de Camadas 1–3, e adicionar um teste de propriedade que verifique a invariância real/nominal de cada âncora.
  - **Esforço:** P — **Confiança:** alta.

- **`[F5-03] [ALTO]` [`ferramentas/registro_prospectivo.py:221-224,333-349`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/registro_prospectivo.py#L221-L224) — Desenho estatístico inválido na validação prospectiva (janelas de 365 dias sobrepostas tratadas como independentes e $t_{\text{crítico}} = 2,0$ com $gl = 3$)**
  - **Evidência:** `avaliar_ic()` (`:333-349`) agrupa vereditos por `data_preco` (com $n \ge 10$) e calcula $t = \bar{x} / (s / \sqrt{K})$ assumindo independência entre as $K$ rodadas, embora cada rodada meça retorno acumulado de `HORIZONTE_DIAS = 365` (`:30`). Rodadas trimestrais ou mensais compartilham 75% a 92% dos mesmos dias de pregão, gerando forte autocorrelação serial (Hansen-Hodrick / Newey-West) que infla a estatística $t$ em ~2× a 3×. Além disso, para `RODADAS_MIN = 4` ($gl = 3$), $t = -2,0$ corresponde a $p = 9,2\%$ unicaudal (e não 5%, que exige $t_{3; 0,05} = -2,353$), e o filtro `N_MIN_IC = 10` exclui todas as rodadas de dossiês individuais (`n = 1..6`).
  - **Impacto:** O sistema pode declarar a doutrina "validada estatisticamente" com falsos positivos gerados pela repetição da mesma carteira em datas próximas.
  - **Correção sugerida:** Exigir espaçamento mínimo de 365 dias entre rodadas independentes no teste $t$ padrão (ou medir o IC sobre retornos **não-sobrepostos** entre a rodada $k$ e a rodada $k+1$), usar o quantil exato de Student $t_{K-1; 0,05}$ e avaliar dossiês em painel empilhado com erro-padrão clusterizado por data.
  - **Esforço:** M — **Confiança:** alta.

- **`[F5-04] [MÉDIO]` [`ferramentas/triagem/avaliar.py:98`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/triagem/avaliar.py#L98) e [`ferramentas/triagem/erro_proxy.py:1-74`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/triagem/erro_proxy.py#L1-L74) — Módulo de produção `triagem/` usa o motor reduzido pré-v2.3 que já foi reprovado no portão pré-registrado**
  - **Evidência:** O experimento de `05/10/2026` reprovou o motor reduzido (`70,7%` de acordo vs. meta de `80%`, $|\Delta \text{P/C}|$ mediano de `0,34` vs. meta de `0,15`, perdendo para o chute trivial `"tudo CARA"` que acerta `92,7%` em ±1 nível). Mesmo assim, `triagem/avaliar.py:98` continua chamando `reduzido.avaliar()` e `reduzido_nf.avaliar()` (que não têm corte de ROIC < WACC, usam $g$ fixo de 2% e margens sem normalização de ciclo) para ranquear a fila de estudo em `06-triagem-e-fila.md`.
  - **Impacto:** Candidatas da B3 podem ser descartadas ou mal ranqueadas na triagem por um motor sabidamente divergente da doutrina v2.6.
  - **Correção sugerida:** Atualizar `reduzido_nf.py` e `reduzido.py` com as regras da v2.6 (trava ROIC < WACC e normalização de margem) ou rodar diretamente `motor_nao_financeiras` sobre `cvm_series.json` na triagem.
  - **Esforço:** M — **Confiança:** alta.

- **`[F5-05] [MÉDIO]` [`docs/VALIDACAO.md:16-19`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/docs/VALIDACAO.md#L16-L19) e [`docs/ORACULO.md:10-11`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/docs/ORACULO.md#L10-L11) — Documentação de validação afirma a existência de módulos e métricas que não existem no repositório**
  - **Evidência:** `docs/VALIDACAO.md:16-19` lista `ferramentas/oraculo/sombra.py`, `ferramentas/oraculo/insumos_externos.py`, `ferramentas/oraculo/screens.py` e Brier score prospectivo; `docs/ORACULO.md:10-11` documenta `python -m oraculo --diferencial`. Nenhum desses arquivos ou flags existe em `ferramentas/oraculo/`.
  - **Impacto:** Induz o leitor ou agente autônomo a acreditar que há validação diferencial externa e Brier score operando quando ainda são itens de backlog (`B10`, `B12`).
  - **Correção sugerida:** Marcar esses itens como `[PLANEJADO / BACKLOG]` em `docs/VALIDACAO.md` e `docs/ORACULO.md`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F5-06] [MÉDIO]` [`ferramentas/oraculo/__main__.py:180,204-209`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/oraculo/__main__.py#L180-L209) — `python -m oraculo` grava arquivos em `docs/oraculo/` por padrão, contradizendo `docs/ORACULO.md:15` ("Só lê e relata")**
  - **Evidência:** Sem a flag `--sem-gravar`, `oraculo/__main__.py:204-209` cria `docs/oraculo/<hoje>.md` e adiciona linha ao arquivo versionado `docs/oraculo/registro.jsonl`.
  - **Impacto:** Suja o working tree do Git em execuções de verificação/auditoria.
  - **Correção sugerida:** Tornar `--sem-gravar` o comportamento padrão e exigir `--gravar` explícito quando se desejar persistir relatório no Git.
  - **Esforço:** P — **Confiança:** alta.

---

### FASE 6 — Operação, Segurança, Privacidade e Rotina Autônoma

- **`[F6-01] [CRÍTICO]` [`ferramentas/backtest/cotahist.py:127`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/backtest/cotahist.py#L127) — Parser do COTAHIST aborta o arquivo anual inteiro por causa de 1 linha de 246 bytes (`linha 2059663`), congelando todos os preços de 2026 em `15/10/2026` há 2 semanas**
  - **Evidência:** `ferramentas/monitor/ultimo.log:2` registra: `"COTAHIST 2026: falhou: parser recusou o arquivo novo (ValueError: COTAHIST 2026 linha 2059663: 246 bytes, esperado 245); mantido o anterior"`; `BOLETINS/2026-10-30-monitor.md:1` alerta `"DADO VELHO: o último pregão é de 2026-10-15, 15 dias antes de hoje"`.
  - **Impacto:** Monitor semanal, relatório da carteira pessoal e tela web estão operando há 15 dias com cotações congeladas em `15/10/2026`.
  - **Tentativa de refutação:** Verificamos se a linha `2059663` corrompe todo o arquivo da B3. Não: na codificação do COTAHIST da B3, linhas com 1 byte extra ocorrem quando a B3 grava um caractere acentuado em UTF-8 (2 bytes) no campo textual `NOMRES` `[27:39]` ou `ESPECI` `[39:49]` (frequentemente em BDRs, opções ou mercado fracionário `TPMERC != 010`). Como `cotahist.py:127` checa `len(bruta) != 245` **antes** de filtrar `tip != b"01"` e `bruta[24:27] != b"010"`, uma única linha irrelevante derruba os 2 milhões de registros do ano. **Refutação rejeitada; achado confirmado.**
  - **Correção sugerida:** Em `cotahist.py:126-141`, filtrar primeiro `tip == b"01"` e `bruta[10:12]` / `bruta[24:27]` (ou, se `len(bruta) > 245`, tentar decodificar UTF-8 → Latin-1 para reidratar os 245 caracteres posicionais), emitindo apenas aviso para linhas fora do universo.
  - **Esforço:** P — **Confiança:** alta.

- **`[F6-02] [CRÍTICO]` [`.claude/hooks/auto_commit.py:79-80,162-167`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/.claude/hooks/auto_commit.py#L79-L80) — O hook `Stop` faz commit e push direto em `origin/master` sem rodar testes quando apenas arquivos não-`.py` mudam ou quando arquivos são deletados (`'D' not in st`)**
  - **Evidência:** Na linha 79, `py = [c.replace("\\", "/") for st, c in itens if c.endswith(".py") and "D" not in st]`; nas linhas 162–167, se `not testes` (`sem código alterado`), `destino` continua `"master"` e o script faz `git commit` + `git push origin master` direto! Foi exatamente assim que, em `30/10/2026 21:12` (commit `05e6636`), o `auto_commit.py` comitou a deleção de 25 PDFs das 6 pastas setoriais da raiz direto no `master` sem rodar nenhum teste, quebrando `gerar_pdf_lote1..6.py` e `test_gerar_pdfs.py`.
  - **Impacto:** Qualquer deleção acidental de arquivos (inclusive `.py` ou PDFs) ou edição em JSONs de insumos (`mercado_vigente.json`, `cvm_series.json`, `01-doutrina-value-investing.md`, `03-hall-de-acoes.md`) vai direto para `origin/master` sem passar por testes nem por `wip/auto`.
  - **Tentativa de refutação:** Verificamos se `auto_commit.py` checa `PROTEGIDOS` (`01-doutrina`, `golden.json`). Não checa (`PROTEGIDOS` só existe em `conferir_noite.py:34`, não em `auto_commit.py`!). **Refutação rejeitada; achado confirmado.**
  - **Correção sugerida:** Em `auto_commit.py`: (1) se houver qualquer deleção (`any("D" in st for st, _ in itens)`) ou arquivo em `PROTEGIDOS`, desviar obrigatoriamente para `wip/auto`; (2) rodar `test_hall03.py` / `test_golden.py` sempre que `.json` ou `.md` da raiz/dados mudarem.
  - **Esforço:** P — **Confiança:** alta.

- **`[F6-03] [ALTO]` [`ferramentas/conftest.py:18-21`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/conftest.py#L18-L21) e [`ferramentas/conferir_noite.py:95-107`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/conferir_noite.py#L95-L107) — `EXIGIR_DADOS=1` converte `@pytest.mark.skipif(os.name == "nt")` em falha (`ERROR`), bloqueando a junção matinal das rodadas da nuvem, e `conferir_noite.py` usa `-rs` (omitindo nomes de falhas do log)**
  - **Evidência:** `ferramentas/monitor/conferir.log:4` mostra: `"origin/claude/keen-babbage-vf5kor: suíte da junção com dados locais — 1090 passed, 2 xfailed, 1 error in 427.01s ... VERMELHO"`. O `1 error` vem de `painel/tests/test_servir.py:93` (`@pytest.mark.skipif(os.name == "nt", reason="TIME_WAIT/SO_REUSEADDR: semântica POSIX (N13)")`), que `conftest.py:18` transforma em falha porque `EXIGIR_DADOS == "1"` converte **qualquer** `rep.skipped` (sem distinguir skip por falta de dado de `skipif` de plataforma!). Além disso, `conferir_noite.py:100` passa `-rs` (que só lista `SKIPPED`), deixando `falhas` na linha 105 sempre vazia para `FAILED`/`ERROR`.
  - **Impacto:** O ramo `origin/claude/keen-babbage-vf5kor` (que está 100% verde!) vem sendo rejeitado todas as manhãs desde 24/10 por um falso erro de plataforma no Windows, desperdiçando 21 minutos diários às 07:15.
  - **Correção sugerida:** Em `conftest.py:18`, só converter `rep.skipped` quando o motivo não for de sistema operacional (`"semântica POSIX"` / `os.name == "nt"`); em `conferir_noite.py:100`, trocar `-rs` por `-ra`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F6-04] [ALTO]` [`ferramentas/conferir_noite.py:34,116-135`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/conferir_noite.py#L116-L135) — Impasse estrutural para missões de motor na nuvem e reexecução diária infinita dos mesmos SHAs reprovados**
  - **Evidência:** `conferir.log:2-7` mostra `origin/claude/fase3-bugs` e `origin/claude/keen-babbage-bvjh9h` falhando todos os dias nos mesmos 12 testes do golden (~14 min/dia) porque alteram o motor sem poder alterar `golden.json` (`PROTEGIDOS`). `conferir_noite.py` não registra o SHA já testado de cada ramo.
  - **Impacto:** Mais de 20 minutos de CPU gastos todas as manhãs às 07:15 re-testando exatamente os mesmos commits sem progresso.
  - **Correção sugerida:** Persistir em `ferramentas/monitor/conferidos.json` o par `(ramo, sha) -> (rc, resumo)` para pular ramos cujo SHA não mudou desde a última conferência.
  - **Esforço:** P — **Confiança:** alta.

- **`[F6-05] [MÉDIO]` [`ferramentas/conferir_noite.py:35-36,68-73`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/conferir_noite.py#L35-L36) — `dados_locais()` copia dados privados (`carteira.local.json` e `dados/privado/`) e `.hypothesis/` para `%TEMP%\noite-*`**
  - **Evidência:** A tupla `FORA` (`conferir_noite.py:35`) não exclui `ferramentas/carteira.local.json`, `ferramentas/dados/privado` nem `ferramentas/.hypothesis`.
  - **Impacto:** Copia dados financeiros pessoais para `%TEMP%` a cada ramo testado (com risco de permanecerem lá se o processo sofrer kill/timeout) e copia 1.138 arquivos inúteis do Hypothesis.
  - **Correção sugerida:** Incluir `"ferramentas/carteira.local.json"`, `"ferramentas/dados/privado"` e `"ferramentas/.hypothesis"` em `FORA`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F6-06] [MÉDIO]` [`.claude/hooks/auto_commit.py:8,143-147`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/.claude/hooks/auto_commit.py#L143-L147) — `python .claude/hooks/auto_commit.py --dry` trava indefinidamente no terminal esperando EOF em `sys.stdin`**
  - **Evidência:** A linha 144 executa `json.load(sys.stdin)` antes de checar `if DRY:` ou `sys.stdin.isatty()`.
  - **Impacto:** Inviabiliza o teste manual do hook documentado no próprio cabeçalho do arquivo.
  - **Correção sugerida:** Ler `sys.stdin` apenas quando `not DRY and not sys.stdin.isatty()`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F6-07] [MÉDIO]` [`ferramentas/coletar_statusinvest.py:36-40,47-58`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/coletar_statusinvest.py#L36-L40) — Falta de validação HTTP/JSON no scraper da StatusInvest**
  - **Evidência:** Na linha 36, `r = requests.post(...)` grava `alvo.write_text(r.text)` sem verificar `r.status_code == 200` nem se o corpo é JSON válido.
  - **Impacto:** Respostas 403/503 da Cloudflare/StatusInvest são salvas como `{tk}_indicadores.json` no cache, corrompendo coletas futuras.
  - **Correção sugerida:** Verificar `r.status_code == 200` e `json.loads(r.text)` antes de gravar o arquivo em disco.
  - **Esforço:** P — **Confiança:** alta.

- **`[F6-08] [MÉDIO]` [`ferramentas/agendador/instalar_tarefas_noite.ps1:17-19`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/agendador/instalar_tarefas_noite.ps1#L17-L19) — Tarefa `ValueInvesting-TemporadaDiaria` expira em `2026-11-21T23:59:59`**
  - **Evidência:** `$diaria.EndBoundary = "2026-11-21T23:59:59"` (`:18`).
  - **Impacto:** A verificação diária de ITRs/DFPs deixará de rodar silenciosamente após 21/11/2026.
  - **Correção sugerida:** Remover o `EndBoundary` fixo do Agendador e controlar a janela de temporada dentro de `temporada.py`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F6-09] [MÉDIO]` [`ferramentas/backup_dados.py:17-20`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/backup_dados.py#L17-L20) — Ausência de backup local/criptografado para `carteira.local.json` e `dados/privado/renda.jsonl`**
  - **Evidência:** `EXCLUIR = {"cvm", "privado"}` protege corretamente o OneDrive de receber dados privados, mas não há rotina que salve cópia criptografada ou local de `carteira.local.json` e `renda.jsonl`.
  - **Impacto:** Perda irreversível do histórico de evolução da renda mensal em caso de falha do SSD local.
  - **Correção sugerida:** Adicionar geração de arquivo `.zip` criptografado (ou cópia para destino seguro local) para `carteira.local.json` e `dados/privado/`.
  - **Esforço:** P — **Confiança:** alta.

- **`[F6-10] [ELOGIO]` [`ferramentas/relatorio/carteira.py:295-314`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/relatorio/carteira.py#L295-L314), [`ferramentas/dossie/fre.py:50-128`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/dossie/fre.py#L50-L128) e [`ferramentas/painel/servir.py:24-69`](file:///c:/Users/frank/Documents/VALUE%20INVESTING/ferramentas/painel/servir.py#L24-L69) — Engenharia de privacidade, LGPD e segurança local exemplar**
  - **Evidência:** `garantir_ignorado()` impede por construção a gravação de dados pessoais em caminhos rastreáveis pelo Git; `fre.py` aplica dupla filtragem de CPFs/nomes; `servir.py` restringe conexões a `127.0.0.1` com `SO_EXCLUSIVEADDRUSE`, bloqueio de DNS rebinding e NTFS ADS.
  - **Impacto:** Zero vazamentos de dados pessoais em todo o histórico do repositório.
  - **Correção sugerida:** Manter como padrão arquitetural.
  - **Esforço:** P — **Confiança:** alta.

---

## d. Parecer do Engenheiro de Software Sênior / Staff

1. **O que o projeto faz extraordinariamente bem:** Para um sistema de autor único construído de forma iterativa, a disciplina de **rastreabilidade de procedência** (`relatorio/modelo.py`), **blindagem de dados privados** (`garantir_ignorado` + `fre.py`), **desacoplamento somente-leitura do painel web** (`painel/servir.py` + `contrato.py`) e **governança operacional documentada** (`DECISOES.md`, `PRE-REGISTRO-v3.md`, `hipoteses.py`) está acima do padrão de muitas equipes profissionais de engenharia financeira.
2. **Onde a arquitetura sofre:** O núcleo mais antigo (`motor_nao_financeiras.py`, `motor_financeiras.py`, `lote1..6.py` e `gerar_pdf_lote1..6.py`) cresceu por acumulação de scripts procedurais:
   - **Estado global mutável no import-time (`[F1-01]`):** `CVM` e `SI` são dicionários globais mutados quando `lote4` e `lote6` são importados. Isso viola a transparência referencial de `avaliar()`.
   - **Silenciamento de `None` como `0` (`[F1-02]`):** O helper `v(d, k, 0)` mascara falhas de extração contábil e transforma ausência de informação em premissa contábil otimista (dívida zero) ou pessimista (depreciação/caixa zero).
   - **Acoplamento temporal estático (`[F1-06]`):** Datas como `2026-10-05` e anos como `"2025"` estão chumbados em dezenas de pontos, impedindo que o sistema avance para 2027 ou rode em modo point-in-time limpo.
   - **Automação frágil nos cantos (`[F6-01]`, `[F6-02]`, `[F6-03]`):** O parser `cotahist.py` abortar 2 milhões de linhas por 1 byte extra na linha `2059663`, o `conftest.py` transformar `@pytest.mark.skipif(os.name == "nt")` em erro fatal sob `EXIGIR_DADOS=1`, e o `auto_commit.py` dar push de deleções em massa direto no `master` mostram que os guardrails de automação precisam de filtros mais precisos.

---

## e. Parecer do Investidor Fundamentalista Sênior (Dividendos/JCP, Longo Prazo, B3)

### Diagnóstico Metodológico e Econômico
1. **A doutrina escrita (`01-doutrina-value-investing.md`) é madura e coerente com o investidor de renda em ações no Brasil**, exigindo cobertura de dividendos por fluxo de caixa livre, ajuste de JCP por imposto, normalização de ciclo e desconto por risco de governança/controlador.
2. **Porém, os motores atuais (`motor_nao_financeiras.py` e `motor_financeiras.py`) sofrem de um severo desalinhamento inflacionário (Real vs. Nominal) e de alavancagem:**
   - Em empresas industriais (`motor_nao_financeiras.py`), o motor opera receitas e NOPAT em **moeda constante (real)**, mas subtrai juros **nominais** (`kd * dl`) em `lpa_norm` (`[F3-01]`) e compara o ROIC a custo de reposição (que já é **real**) contra o WACC **nominal** (~19%) para liberar crescimento no DCF (`[F3-02]`). Somado ao Hamada calculado sobre dívida **bruta** dentro de um ponto fixo que realimenta o próprio valor central já descontado pelo controlador (`[F3-03]`), o motor destrói artificialmente o valor justo de qualquer empresa industrial que use dívida de longo prazo (como `KLBN11` com $K_e = 64,7\%$ ou `SUZB3` com $K_e = 34,3\%$) ou que tenha imobilizado antigo relevante (`WEGE3` travada com $g = 0$).
   - Em bancos, seguradoras e elétricas (`motor_financeiras.py`), o motor compara `roe_lp` nominal histórico (2016–2025, inflação média menor) com um $K_{e,\text{nom}} = 19,30\%$ inflado pela NTN-B 2050 sem expurgo de risco soberano (`7,06% + 5,00% = 12,06%` real) e pela inflação implícita de `02/10/2026` (`6,46%`), além de usar `dpa_medio_5a` nominal sem correção pelo IPCA (`[F3-04]`) e tratar concessões elétricas reguladas (com RAB corrigida por IPCA/IGP-M) como se fossem bancos sem ativo reversível (`H11`).
3. **É método conservador ou erro de calibração ter 0 `BARATA`, 3 `JUSTA`, 34 `CARA` e 4 `NC` em 41 empresas?**
   - **É majoritariamente erro de calibração e de consistência real/nominal**, como provam os próprios diagnósticos internos `H1`, `H2`, `H6`, `H8`, `H9` e `H11`. Um método conservador aplica margem de segurança explícita (25% a 40%) sobre um valor central justo e sem viés; quando o próprio valor central já embute penalizações duplicadas de inflação e alavancagem, a margem de segurança é contada duas ou três vezes, cegando o investidor para boas oportunidades em empresas de qualidade com dívida bem estruturada ou concessões indexadas à inflação.

### Resposta Direta: Eu confiaria dinheiro real nestes vereditos hoje? Sob que condições?
- **Hoje: NÃO confiaria dinheiro real de forma autônoma nos vereditos numéricos atuais**, pelos seguintes motivos objetivos:
  1. **Risco de falso `CARA` (custo de oportunidade severo e alerta falso de saída):** Os bugs `[F3-01]`, `[F3-02]`, `[F3-03]` e `[F3-04]` comprimem artificialmente o valor central de industriais alavancadas, compounders intensivas em capital e elétricas/bancos, podendo acionar alertas falsos de `SAÍDA` (P/C > gatilho de saída) em excelentes geradoras de dividendos da carteira.
  2. **Risco de falso `BARATA`/`JUSTA` por dado ausente (`[F1-02]`):** O silenciamento `v(d, k, 0)` permite que uma falha de extração de dívida ou Capex em novo ITR produza um valor central inflado sem travar em `NÃO CONCLUSIVO`.
  3. **Insumos Nota C nas financeiras/elétricas (`[F4-02]`):** 5 das 6 posições da carteira pessoal (`BBAS3`, `BBSE3`, `ABCB4`, `ITSA4`, `ISAE4`) dependem de insumos `C_LOTE` (`roe_lp`, `payout`, `vpa`, `lpa_12m`) e têm `dpa_medio_5a` nominal sem IPCA; e a `BBSE3` tem erro na taxa `g` pós-renovação de 2033 (`[F3-05]`).
- **Sob que condições eu confiaria dinheiro real neste sistema?**
  1. **Condição 1 (Consistência Real vs. Nominal):** Corrigir `lpa_norm`/`lair_norm` para usar custo real da dívida (`kd_real`), comparar `roic_rep_c` contra `w_real`, deflacionar `dpa_medio_5a` e `da_med` pelo IPCA e descontar benefícios fiscais nominais por taxa nominal.
  2. **Condição 2 (Hamada e Ponto Fixo):** Trocar dívida bruta por dívida líquida no Hamada e retirar o desconto do controlador de dentro do laço de ponto fixo (`A1`).
  3. **Condição 3 (Bloquear Dado Ausente e Auto-Mascaramento):** Eliminar `v(d, k, 0)` para contas obrigatórias (forçando `NÃO CONCLUSIVO`) e fazer o Oráculo reprovar erros de reconciliação/sanidade em **todas** as empresas (não apenas nas 3 `JUSTA`).
  4. **Condição 4 (Insumos Nota A nas Financeiras/Elétricas):** Extrair `roe_lp`, `vpa`, `lpa` e `dpa` dos 6 tickers da carteira (e das 20 financeiras/elétricas) diretamente das DFPs/ITRs da CVM, corrigindo o `g_pos` pós-corte da `BBSE3`.

---

## f. Lacunas: O Que Não Deu Para Verificar e Por Quê

1. **Conteúdo dos arquivos privados (`ferramentas/carteira.local.json`, `RELATORIOS/privado/*`, `ferramentas/dados/privado/renda.jsonl`, `ferramentas/monitor/carteira.log`):** Não abertos por força da regra inviolável de segurança e privacidade da missão (apenas existência, tamanho e proteção por `git check-ignore` foram verificados).
2. **Execução da suíte completa do `backtest/` (~13 minutos):** Não executada em cumprimento estrito à regra inviolável da missão (*"Nunca rode o `backtest/` (13 min)"*); os módulos `backtest/cotahist.py`, `backtest/motor/reduzido.py`, `reduzido_nf.py` e `experimento/proxy.py` foram auditados integralmente por inspeção estática e leitura dos logs/relatórios.
3. **Textos integrais dos Termos de Uso da StatusInvest e texto oficial da LC 224/2025 no Planalto:** Sem envio de requisições externas fora do escopo autorizado; verificado via registros documentais do próprio repositório (`docs/TERMOS-DE-USO-FONTES.md:19-20` e `01-doutrina-value-investing.md:78`).

---

## g. Plano de Ação Priorizado — Top 15 Correções

| Ordem | ID | Ação Corretiva | Arquivo(s) Alvo | Esforço | Dependências |
|---:|---|---|---|---|---|
| **1** | `F6-01` | Tolerar/normalizar linhas fora do universo ou com caracteres UTF-8 (>245 bytes) em `cotahist.py:127` para destravar imediatamente as cotações de 2026 (congeladas em `15/10/2026`). | `ferramentas/backtest/cotahist.py` | **P** | Nenhuma |
| **2** | `F6-02` | Blindar `.claude/hooks/auto_commit.py`: nunca fazer push direto no `master` quando houver deleções (`"D" in st`) ou arquivos protegidos/JSONs de dados, e corrigir `--dry` (`sys.stdin.isatty()`). | `.claude/hooks/auto_commit.py` | **P** | Nenhuma |
| **3** | `F6-03` / `F2-01` | Criar `ferramentas/pytest.ini`, corrigir `conftest.py:18` para não transformar `@pytest.mark.skipif(os.name == "nt")` em erro sob `EXIGIR_DADOS=1`, e trocar `-rs` por `-ra` em `conferir_noite.py:100`. | `ferramentas/pytest.ini`, `ferramentas/conftest.py`, `ferramentas/conferir_noite.py` | **P** | Nenhuma |
| **4** | `F6-05` / `F0-05` | Adicionar `carteira.local.json`, `dados/privado` e `.hypothesis` em `FORA` do `conferir_noite.py:35` e `.hypothesis/` no `.gitignore` da raiz; podar os 16 worktrees órfãos (`F0-01`). | `ferramentas/conferir_noite.py`, `.gitignore` | **P** | Nenhuma |
| **5** | `F1-01` | Eliminar a mutação in-place de `CVM` e `SI` no import de `lote4_saude_telecom.py:116-125` e `lote6_quimica.py:127-128`, movendo a lógica para a carga de `motor_nao_financeiras.py` / `series_vigente.py`. | `ferramentas/motor_nao_financeiras.py`, `lote4_saude_telecom.py`, `lote6_quimica.py` | **P** | Nenhuma |
| **6** | `F5-01` / `F5-06` | Remover o filtro `if p in DECISAO` para falhas estruturais em `oraculo/reconciliacao.py` e `sanidade.py` (para que erros em empresas `CARA`/`NC` não sejam mascarados) e tornar `--sem-gravar` padrão em `oraculo/__main__.py`. | `ferramentas/oraculo/reconciliacao.py`, `sanidade.py`, `__main__.py` | **P** | Nenhuma |
| **7** | `F2-02` / `F2-03` | Tornar `test_oraculo_propriedades.py` determinístico (adicionando `@example` explícito nos testes `xfail`) e testar `ke_implicito`/`g_implicito` com validação de mudança de sinal em `_bissecao` (`F1-07`). | `ferramentas/tests/test_oraculo_propriedades.py`, `motor_nao_financeiras.py` | **P** | Item 5 |
| **8** | `F1-04` | Corrigir `central_rapido` em `gerar_pdf_lote4.py:46-50` (aplicar `1 - desc_de(emp2)` e recalcular `ec`) e adicionar `SAIDA.parent.mkdir(parents=True, exist_ok=True)` em `gerar_pdf_lote1..6.py`. | `ferramentas/gerar_pdf_lote1..6.py` | **P** | Nenhuma |
| **9** | `F3-06` / `F3-09` | Aplicar `(1 - desc_pct)` ao VPA em `roe_implicito` (`motor_financeiras.py:476`), usar `g_real` com guarda `> 0` em `peg`/`pegy` (`motor_nao_financeiras.py:993`), condicionar `bazin6` a `coberto` e forçar `NC` se `lpa_norm <= 0`. | `ferramentas/motor_financeiras.py`, `motor_nao_financeiras.py` | **P** | Nenhuma |
| **10** | `F1-02` | Substituir `v(d, k, 0)` por verificação explícita de contas críticas obrigatórias em `motor_nao_financeiras.py` e `montar_series.py`, retornando `NÃO CONCLUSIVO` quando faltar dado contábil essencial. | `ferramentas/motor_nao_financeiras.py`, `montar_series.py` | **M** | Item 6 |
| **11** | `F3-01` / `F3-07` | Corrigir a mistura Real vs. Nominal em `motor_nao_financeiras.py`: usar custo real da dívida em `lucro_norm`/`lair_norm`, descontar `beneficio_fiscal` nominal por taxa nominal e deflacionar `da_med` por IPCA em `ebitda_norm`. | `ferramentas/motor_nao_financeiras.py` | **M** | Item 10 + Regravar Golden |
| **12** | `F3-02` | Calcular ROIC ano a ano (`nopat_t / cap_inv_t`) antes da mediana (`H6`) e comparar `roic_rep_c` (real) contra `w_real` na trava de crescimento do DCF (`H1`). | `ferramentas/motor_nao_financeiras.py` | **M** | Item 11 + Regravar Golden |
| **13** | `F3-03` | Usar dívida líquida `max(dl, 0.0)` em Hamada e retirar `(1 - desc)` de dentro do laço de ponto fixo (`A1`), eliminando a espiral da morte em `KLBN11`/`SUZB3`/`SLCE3`/`SMTO3`. | `ferramentas/motor_nao_financeiras.py` | **M** | Item 12 + Regravar Golden |
| **14** | `F3-05` / `F3-04` | Corrigir `g_pos` pós-haircut na renovação de `ddm_contrato_finito` (`BBSE3`), deflacionar `dpa_medio_5a` nos lotes 1 e 2 pelo IPCA, alinhar `roe_lp` vs. `Ke` em termos reais e separar modelo de concessão elétrica (RAB). | `ferramentas/motor_financeiras.py`, `lote1_bancos.py`, `lote2_energia.py` | **G** | Regravar Golden |
| **15** | `F4-02` / `F1-05` / `F5-03` | Completar `PREGAO`/`CLASSE` (`proventos_ex.py`) e `CADASTRO` (`relatorio/quali.py`) para todo o Hall, migrar insumos das 20 financeiras/elétricas para DFP CVM (Nota A) e corrigir a autocorrelação de janelas em `registro_prospectivo.py`. | `ferramentas/proventos_ex.py`, `relatorio/quali.py`, `registro_prospectivo.py` | **G** | Item 14 |

---

## O Que Mais Temi Errar Nesta Auditoria (5 Linhas)
1. **Confundir conservadorismo deliberado da doutrina com bug matemático:** Por isso separamos escolhas legítimas (margem de segurança de 25%–40%, corte de 40% na renovação da `BBSE3`) de erros algébricos comprovados (juro nominal subtraído de NOPAT real, `roic_rep` real comparado a `w_nom` nominal e desconto do controlador dentro do ponto fixo).
2. **Repassar achado de sub-agente sem conferência primária no código:** Dois trechos reportados inicialmente por sub-agente (sobre uma suposta inversão de `g_real`/`g_nom` em `dcf_1_estagio` e um suposto `return 0` em `fiscal.py`) foram refutados ao lermos `motor_nao_financeiras.py:725-762` e `fiscal.py:30-35` linha a linha e excluídos do relatório.
3. **Violar acidentalmente a regra de privacidade ao auditar a carteira e o painel:** Garantimos que nenhum arquivo em `carteira.local.json`, `RELATORIOS/privado/` ou `ferramentas/dados/privado/` fosse aberto, auditando toda a segurança exclusivamente pelo código de `carteira.py`, `contrato.py`, `servir.py` e metadados de caminho.
4. **Sujar o repositório durante os testes:** Identificamos que `python -m oraculo` grava em `docs/oraculo/` por padrão (`[F5-06]`), documentamos essa mutação e garantimos a limpeza de artefatos transitórios.
5. **Subestimar falhas silenciosas de infraestrutura que já estavam afetando a operação diária:** A leitura cruzada dos logs reais (`monitor/ultimo.log`, `monitor/conferir.log` e `git log -n 5`) revelou os 3 bloqueios operacionais ativos hoje (`COTAHIST 2026` travado em `15/10`, deleção dos 25 PDFs pelo `auto_commit.py` e falha de `EXIGIR_DADOS=1` no Windows).
