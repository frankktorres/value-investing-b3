# BRIEFING COMPLETO: Mesa de Value Investing B3
*Estado em 23/11/2026. Escrito para outra IA que vai propor melhorias de engenharia, método, produto e processo.*

Este documento não contém dados pessoais da carteira (quantidades, preço médio, valores em R$, corretora). Isso é proposital: há regra de privacidade no projeto. Os tickers aparecem.

As afirmações trazem a fonte (arquivo:linha) ou a origem da medida. Os caminhos partem da raiz do repositório (`VALUE INVESTING/`). Onde um número foi **medido nesta sessão**, o texto diz isso. Os demais vêm de leitura dos arquivos do projeto.

---

## 0. Como usar este documento (para a IA leitora)

**Quem pede.** O dono é um investidor pessoa física (farmacêutico, mestrando em Ciências Farmacêuticas, programa em Python). Ele usa o projeto para decidir compras de ações da B3 para renda passiva (dividendos/JCP) no longo prazo. Quase todo o código e a documentação foram escritos por agentes de IA:
- Claude Code local;
- uma rotina noturna do Claude na nuvem;
- e, em 30–31/10/2026, uma auditoria e "reforma" feitas por outra ferramenta (Antigravity/Gemini).

**O que pedimos.** Uma análise independente e crítica, no nível de um engenheiro de software e de um professor de finanças corporativas sênior, que:
1. aponte debilidades, erros e riscos que não vimos;
2. proponha a **arquitetura-alvo** e um **plano em fases** (o que fazer primeiro, o que cortar);
3. proponha melhorias de **método** (valuation e validação), de **produto/visual** (o usuário final é leigo em engenharia) e de **automação/processo** (o projeto sofre de excesso de documento e de regra);
4. diga onde nossas hipóteses (seção 13) estão erradas.

Formato de resposta desejado está na seção 14.

**Princípios que o dono não abre mão:**
- Nunca inventar dado, fonte ou número.
- Todo número que decide tem de ter fonte primária (nota A/B).
- O sistema nunca executa nem sugere como feita uma ordem de compra ou venda.
- Dados pessoais e segredos nunca vão para o git nem para serviço de terceiros.
- Nada destrutivo sem mostrar antes o que muda.
- Nada entra no ramo principal sem testes verdes.

---

## 1. Resumo executivo

**O que é.** Uma "mesa de análise fundamentalista" com três partes:
1. **Doutrina escrita** (`01-doutrina-value-investing.md`, v2.6.1, 61 KB): filtros, custo de capital, métodos de valuation e régua de decisão.
2. **Motores de valuation em Python** (`ferramentas/`, cerca de 34 mil linhas, 219 arquivos `.py`). Eles calculam para cada empresa um **"central"** (valor intrínseco por ação) e uma **"palavra"**: BARATA / RADAR / JUSTA / CARA / NÃO CONCLUSIVO.
3. **Saídas para o usuário:**
   - relatório Markdown/PDF por empresa;
   - tela web local somente leitura (`127.0.0.1:8765`);
   - painel da carteira e da meta de renda;
   - boletins semanais de preço;
   - boletins da temporada de resultados.

**Universo.** O "hall" tem 41 empresas blue chip da B3, mais 8 com dossiê aprofundado (BLAU3, CMIN3, HYPE3, LEVE3, ALLD3, FESA4, SHUL4, VLID3). Há também uma triagem da B3 inteira (cerca de 110 empresas) que gera fila, sem palavra.

**Stack.** Python 3.14 no Windows 11, com pandas, numpy, reportlab, matplotlib, requests, pytest e hypothesis. Não há banco de dados: os dados ficam em JSON, CSV e ZIPs (cerca de 1,8 GB fora do git). A tela é HTML/CSS/JS puro, sem build. A automação usa o Agendador do Windows e hooks do Claude Code. O repositório fica num GitHub privado. **Não há CI.**

**Maturidade.** É um MVP de uso pessoal. O cálculo é sofisticado: Hamada, ponto fixo do WACC, real × nominal, proveniência por número, testes de propriedade, pré-registro de hipóteses. Mas hoje o projeto está **quebrado e congelado** (seção 10).

### As 12 coisas mais importantes (ordem de gravidade)

1. **🔴 A árvore de trabalho está corrompida desde 31/10/2026 09:23** (medido nesta sessão). São 24 arquivos com a mesma hora de gravação. As linhas que os 10 últimos commits *removeram* foram reinseridas ao lado das novas, como um patch reaplicado em "união".
   - Quatro arquivos `.py` não passam no parser: `ferramentas/conftest.py`, `ferramentas/motor_nao_financeiras.py`, `ferramentas/proventos_ex.py` e `ferramentas/tests/test_oraculo_reconciliacao_sanidade.py`.
   - Nos que ainda fazem parse, um `return` antigo ficou antes do novo. Isso desliga em silêncio as correções PR4-04 (teto de alavancagem) e PR4-05 (deflator) em `premio_alavancado` e `credito_observado`. Também reativa o limiar frágil `1e8` da escala de ações (`lote4_saude_telecom.py:85`).
2. **🔴 A suíte de testes não carrega.** O `pytest` sai com código 4 (IndentationError no `conftest.py:41`; medido nesta sessão).
3. **🔴 As tarefas agendadas falham há 3 semanas sem ninguém perceber.**
   - O monitor de preço de sexta falhou em 06/11, 13/11 e 20/11: o boletim é um traceback.
   - A tarefa diária da temporada de resultados do 3T26 quebrou depois de 31/10 e expirou em 21/11. **Os cerca de 30 ITRs do 3T26 publicados em novembro nunca foram lidos.**
   - A tela mostra dados de 22/10, com cotação de 15/10.
   - Não há alerta que chegue ao dono: nem e-mail, nem push.
4. **🔴 Os 10 commits da "reforma" existem só nesta máquina.** São as correções F1, F5 e PR4-03 a 06 do motor, no ramo `gemini/reforma`, que nunca foi enviado ao GitHub. O backup semanal em bundle no OneDrive é a única cópia externa.
5. **🟠 O `HEAD` do ramo também não está verde.** Rodei a suíte numa worktree limpa do `HEAD` e deu **4 falhas, 1.031 aprovados e 45 pulados**. A worktree não tinha os dados locais, então as falhas podem depender de dado; é preciso confirmar com os dados.
   - Falhas: `g_implicito` devolve `None` para SUZB3/KEPL3, e um teste ainda espera LEVE3 NÃO CONCLUSIVO, mas o PR4-04 mudou a palavra para JUSTA.
   - Os commits do motor entraram sem parecer do agente revisor ("oráculo"), que é obrigatório pelas próprias regras do projeto. O golden foi regravado 4 vezes numa noite.
6. **🟠 Calibração enviesada para CARA.**
   - No golden atual (41 tickers, preço de 02/10, depois do PR4-06): **0 BARATA, 0 RADAR, 4 JUSTA, 34 CARA, 3 NÃO CONCLUSIVO**, com mediana de preço ÷ central de **1,94**.
   - O Ke implícito no preço de quase todo o hall é de 10–14% nominal, **abaixo da própria taxa livre de risco nominal (cerca de 14%)**. Pelo modelo, o mercado inteiro pagaria prêmio de risco negativo.
   - O diagnóstico interno (H9, decomposição Shapley) atribui de 76% a 98% do log(P/C) à **taxa de desconto**.
7. **🟠 Não há validação empírica da régua.**
   - O backtest parou porque o motor sem premissas digitadas reproduziu a palavra em só 70,7% dos casos (o portão era 80%).
   - A validação agora é só prospectiva, com a primeira leitura possível no fim de 2027.
   - Há cerca de 445 premissas digitadas no código: são elas que impedem rodar o modelo em datas passadas sem look-ahead.
8. **🟠 Insumos fracos onde importa.** As 20 financeiras e elétricas têm central com nota de fonte C (premissas digitadas, como `roe_lp`). A carteira real do dono é concentrada justamente em bancos e financeiras.
9. **🟠 Arquitetura de script, não de sistema.**
   - Os dados são carregados no *import* (estado global).
   - Seis "lotes" foram copiados e divergiram (`loteN_*.py`, `gerar_pdf_loteN.py`, `atualizar_hall_loteN.py`: 18 famílias, cerca de 5.500 linhas), com 732 literais numéricos de premissa.
   - `avaliar()` devolve um `dict` sem tipo com mais de 60 chaves, que é o contrato implícito de tudo.
   - Não há `pyproject`, lint, mypy nem CI.
10. **🟠 O golden é *characterization test*.** Ele prova estabilidade, não correção; cobre só 12 campos e foi regravado 18 vezes. "Regravar" virou sinônimo de "aceitar".
11. **🟡 O produto não explica.**
    - A tela mostra veredito, régua e métodos, mas não diz *por que* em linguagem leiga.
    - Faltam histórico de fundamentos, comparação entre empresas, alertas reais e um mobile usável.
    - O melhor texto do projeto, a tese dos dossiês, não aparece na tela.
12. **🟡 Processo burocrático e com várias IAs.**
    - São 47 `.md` ativos (cerca de 870 KB) de processo e status, todos congelados desde 22/10.
    - Três linhas de trabalho de IA divergentes (Claude local, Claude na nuvem, Gemini) corrigem a mesma coisa de formas diferentes. Os ramos `claude/*` da nuvem estão parados desde 23–24/10, com conflito garantido com `gemini/reforma`.
    - Regras como "oráculo obrigatório" e "ok do dono" não são impostas por código.

---

## 2. O dono, o objetivo e o que "bom" significa

**Perfil** (`07-perfil-do-investidor.md`):
- Horizonte longo; a prioridade declarada são proventos recorrentes.
- Value investing clássico: preço contra valor intrínseco, margem de segurança, vantagem competitiva, geração de caixa.
- A comparação é sempre com o **Tesouro IPCA+ longo, líquido de IR** dos dois lados.
- Quer respostas em português, diretas, técnicas, com tabelas. A incerteza deve ser dita "com todas as letras".
- Estuda Buffett, Munger, Graham, Fisher, Lynch, Klarman, Greenblatt, Bazin, Barsi, Marks, Pabrai e outros, mas "nenhum é patrono". Questionar é método: a IA deve sustentar o julgamento por mérito, não ceder por pressão.

**Meta financeira pessoal.** Existe um alvo de renda mensal com dividendos/JCP; o valor fica fora deste documento. A carteira real é pequena e concentrada em financeiras (tickers em `ferramentas/carteira_tickers.json`, que é versionado por decisão de 13/10).

**O que ele disse que quer** (19/10, irritado com o excesso de processo): **"um programa pra mim"**, baseado nas fórmulas dos grandes investidores (quali + quanti), que gere **relatório por empresa** e que possa um dia virar **SaaS com front-end** (sem prazo). Ele não quer decidir detalhe técnico nem lembrar datas: "apenas faça o que tem que ser feito".

**O que "melhor" significa aqui** (`PROJECT_BRIEF.md` §10):
- **Técnico:** todo número com fonte A/B e data; reproduzível; testes verdes; premissas fora do código; dado fresco.
- **Científico:** sem viés de sobrevivência nem look-ahead; regra declarada antes de medir.
- **Profissional:** gerar decisão (compra/venda) com margem de segurança, não mais regras; simplicidade que se mantém sozinha.

---

## 3. O que o sistema faz, ponta a ponta

```
FONTES (todas grátis)                          ARMAZENAMENTO (sem banco)
CVM dados abertos: DFP/ITR/FRE/FCA/IPE (A) ─┐   ferramentas/dados/cvm/*.zip  (~1,7 GB, fora do git; MANIFESTO.json sha256 no git)
B3: COTAHIST (preço), API de proventos (A) ─┤   ferramentas/dados/cvm_series.json (650 KB, no git: 31 NF × 2016–2025 × 51 campos + LTM)
BCB SGS (IPCA, PTAX), Tesouro (curva IPCA+)─┤   ferramentas/dados/proventos_hall/<TK>.json, macro/*.csv, mercado*.json, fatos_*.json
FRED/BLS (commodities)                     ─┤   ferramentas/dados/raw/<data>/ (StatusInvest, fora do git) → series_AAAA-MM-DD.json
StatusInvest (scraping, nota C)            ─┘   ferramentas/backtest/dados/ (690 MB, fora do git)
            │
            ▼
PREMISSAS DIGITADAS (loteN_*.py: 6 lotes setoriais; ~445 campos fora do default; 732 literais numéricos)
            │
            ▼
MOTORES  motor_nao_financeiras.py (1.104 LOC no HEAD)  ·  motor_financeiras.py (528 LOC)
  Ke/WACC (rf NTN-B + 5 p.p. × Hamada; ponto fixo) → âncoras por perfil (DCF, EPV, OE, DDM, P/VP justificado, SOTP…)
  → central = mediana das âncoras → dispersão → régua (P/C) → trava 3b → carimbos de armadilha → palavra + notas 0–10
            │
            ├─► golden (tests/golden.json, 41 tickers, 12 campos) ← rodar_tudo.py --motivo
            ├─► 03-hall-de-acoes.md (gerado em parte por hall03.py) + PDFs por lote (gerar_pdf_loteN.py, reportlab)
            ├─► relatorio <TK> → RELATORIOS/<TK>-<data>.md/.json/.pdf (nota A/B/C/— por número)
            ├─► relatorio CARTEIRA → RELATORIOS/privado/ (ignorado pelo git)
            ├─► painel --exportar (~100 s) → painel/web/dados/*.json → tela em 127.0.0.1:8765
            ├─► monitor_semanal.py (Agendador, sexta 08:00) → BOLETINS/AAAA-MM-DD-monitor.md
            ├─► temporada.py (ITR novo → recoleta LTM → compara com golden) → BOLETINS/…-temporada.md
            ├─► registro_prospectivo.py → prospectivo/registro.jsonl (append-only, cadeia sha256)
            └─► oraculo/ (rastreabilidade regra↔teste, reconciliação contábil, sanidade econômica, hipóteses H1–H11)
```

**Pontos de entrada:**
- Na raiz: `relatorio.cmd <TK>` e `painel.cmd`.
- Em `ferramentas/`: `python -m relatorio|painel|oraculo`, `python -m dossie.gerar <TK> --data AAAA-MM-DD` e `python -m triagem.rodar`.
- Scripts: `python rodar_tudo.py --motivo "..."`, `temporada.py`, `monitor_semanal.py`, `conferir_noite.py` e `bootstrap_dados.py --baixar|--verificar|--derivados`.

São 36 arquivos com `__main__` ou argparse. Os `.cmd` usam o `python` global, sem venv.

---

## 4. Método (doutrina v2.6.1; v2.7 em preparação)

### 4.1 Pergunta-mãe e filtros (`01:8`, `01:16-24`)
A pergunta-mãe é: "ROIC > custo de capital, de forma repetível, **e** preço < valor?" Os filtros:
- **F1, retorno sobre capital.** Não financeira: o **menor** entre o ROIC contábil e o ROIC a custo de reposição tem de superar o WACC ao longo do ciclo. Financeira: ROE > Ke nominal.
- **F2:** balanço que aguenta o ciclo.
- **F3:** controlador alinhado com o minoritário.
- **F4:** provento coberto por lucro e caixa.
- **F5:** preço ≤ 0,70 × central. Este é o filtro de compra.

Para ficar no hall bastam 3 dos 4 primeiros.
- **Exceções nomeadas:** Lynch/Fisher (crescimento sem dividendo), Schloss/Graham (P/VP < 0,5), Templeton/Klarman (estatal em pânico).
- **Círculo de competência:** fora dele, o teto é RADAR.
- **Setores evitados:** aviação, educação superior, e-commerce sem lucro, empresas em RJ e resseguro sem escala.

**Hierarquia.** Sobrevivência > caixa > ROIC > ciclo normalizado > preço. As notas de qualidade **só pioram** a palavra, nunca a melhoram (`01:44`).

### 4.2 Custo de capital (`01:50-58`)
- **rf:** NTN-B (IPCA+) sem cupom, o vencimento mais longo (2050), na taxa da manhã. Base de 02/10/2026: **7,06% real**.
- **π:** inflação implícita da curva, **6,46%**. O Focus (cerca de 4%) entra só como sensibilidade.
- **Ke real.** Nas financeiras é rf + 5 p.p. fixos. Nas não financeiras (desde a v2.4) é rf + 5 p.p. × [1 + (1−t)·D/E], por Hamada.
  - Os 5 p.p. são tratados como prêmio **desalavancado**.
  - O E é o "valor da casa" (central × ações), achado por **ponto fixo**: o Ke depende do central, e o central depende do Ke.
  - Sem dívida, o Ke real é 12,06% e o nominal 19,30%.
- **Kd:** o do RI, depois dos swaps. Sem ele, rf nominal + spread sintético de Damodaran pela cobertura de juros (nota B).
- **IR efetivo:** mediana de 5 anos, com teto de 34%. O benefício fiscal com prazo é calculado como valor presente à parte.
- **"Uma só coluna decide":** o Ke "de mercado" aparece só como sensibilidade.
- **Real × nominal** (`01:55`): fluxo real com taxa real e fluxo nominal com taxa nominal. EPV e OE são reais; DDM e P/VP justificado são nominais. Foram necessários **3 PRs seguidos** (PR4-04, 05 e 06) para corrigir inconsistências dessa regra.

### 4.3 Métodos e âncoras (`01:225-271`)
**Métodos calculados:**
- Graham (original, BR e revisado), Bazin (original e teto de renda), Lynch/PEG, Greenblatt (só ranking).
- Owner Earnings, EPV real (Greenwald), valor de reprodução.
- DDM/Gordon, P/VP justificado = (ROE−g)/(Ke−g), SOTP.
- DCF em 3 cenários, DCF reverso, TIR real implícita, Bogle.
- Piotroski, Altman Z'', Beneish e Sloan aparecem só como bandeira.

**Âncoras por perfil** (só elas formam o central):

| Perfil | Âncoras |
|---|---|
| Banco | P/VP justificado + DDM |
| Seguradora | DDM + P/VP justificado |
| Holding | SOTP + DDM |
| Utility (regulada) | DDM + P/VP justificado como *proxy* declarado do DCF regulatório (não há base de ativos regulatória, RAB, modelada) |
| Industrial | DCF + EPV + OE/(Ke−g) |
| Cíclica | EPV de meio de ciclo + DCF normalizado + valor de reprodução |

- **Central = mediana das âncoras.** Com 2 âncoras, é a média.
- **Dispersão:** maior ÷ menor acima de 1,8× desce um nível no lado favorável; acima de 3×, ou com qualquer âncora ≤ 0, a palavra é NÃO CONCLUSIVO.
- **Trava de g no DCF:** só há crescimento se o ROIC superar o WACC, avaliado por cenário. Como degrau, ela gera descontinuidade: a WEGE3 sobe 36% no central com 0,1 p.p. de margem.
- **Lucro normalizado:** mediana de 10 exercícios.

### 4.4 Régua e palavra (`01:166-198`)

| Palavra | Preço ÷ central (P/C) |
|---|---|
| BARATA | ≤ 0,70 |
| RADAR | 0,70 a 0,90 |
| JUSTA | 0,90 a 1,10 |
| CARA | > 1,10 |
| OPORTUNIDADE | BARATA com catalisador datado |

- **Compra até 0,70×; saída a 1,30×.**
- **Exceção de saída a 1,50×** para empresas de qualidade (ROIC real > WACC real em ≥ 8 de 10 anos e Qualidade ≥ 8). Nenhum ticker é elegível hoje.
- **Entrada parcial:** até 1/3 da posição a ≤ 0,80×, com condições.
- **Ordem de aplicação:** régua → círculo → dispersão → **trava 3b** (JUSTA com retorno de Bogle fora de ±2 p.p. do Ke vira NÃO CONCLUSIVO) → carimbos de armadilha (§7; fonte única em `ferramentas/carimbos.py`).
- **Notas 0–10:** Qualidade 30%, Solidez 20%, Renda 25%, Preço 25%. A nota resume, não decide.
- **Nota de fonte de cada número:**
  - **A:** CVM, B3, RI, BCB, Tesouro, IBGE e reguladores.
  - **B:** imprensa que cita a fonte primária; Damodaran.
  - **C:** o resto, incluindo agregadores e premissa digitada.
  - Vale a pior nota entre os insumos.

### 4.5 Controlador e proventos
- **Desconto de controlador:** seis vetores, aplicado **uma única vez**, só sobre âncora positiva. A linha do desconto é obrigatória mesmo com zero. Precedentes: PETR4 cerca de 8%, BRSR6 35%, SAPR11 15%. Ainda há **23 tickers sem razão documentada** para o desconto.
- **Yield sustentável:** o menor entre o DPA médio de 5 anos e o DPA que o FCFE normalizado paga. O DPA/JCP das não financeiras vem da API da B3 (nota A).

### 4.6 Versões
- v1.0 em 07/09/2026; v2.0 a v2.6 entre 04/10 e 10/10, depois de auditorias; **v2.6.1 em 21/10**, a vigente.
- A **v2.7** está em preparação no ramo `gemini/reforma` (`docs/PRE-REGISTRO-v4.md`). PR4-01 a PR4-06 estão no código; **o PR4-07 (financeiras) não foi feito**.
- **O texto do `01` não foi atualizado:** ainda fala em "dívida bruta", e o código já usa a dívida líquida. Os prompts `02`, `05` e `08` citam a v2.5.

---

## 5. Engenharia: código, dados e testes

### 5.1 Inventário (medido por agente nesta sessão)

| Pacote | Arquivos .py | LOC | Papel |
|---|---|---|---|
| raiz `ferramentas/` | 60 | 11.542 | motores, lotes, coletores, utilitários |
| `backtest/` | 43 | 6.668 | ledger point-in-time + COTAHIST (parado) |
| `tests/` | 47 | 6.283 | suíte principal + golden |
| `relatorio/` | 18 | 2.600 | relatório MD/PDF por empresa e CARTEIRA |
| `dossie/` | 20 | 2.381 | anexo mecânico do dossiê (FRE, notas, vereditos) |
| `painel/` | 13 | 1.904 (+ cerca de 1.540 de JS/CSS) | exportação JSON + servidor local + tela |
| `oraculo/` | 9 | 1.753 | rastreabilidade, reconciliação, sanidade, hipóteses |
| `triagem/` | 9 | 1.321 | fila da B3 inteira |

**Maiores arquivos:**

| Arquivo | LOC |
|---|---|
| `motor_nao_financeiras.py` | 1.104 |
| `gerar_pdf_lote6.py` | 675 |
| `oraculo/hipoteses.py` | 644 |
| `gerar_pdf_lote4.py` | 584 |
| `relatorio/quali.py` | 534 |
| `painel/contrato.py` | 533 |
| `motor_financeiras.py` | 528 |

**Funções gigantes:**
- `motor_nao_financeiras.avaliar` (162 linhas), `valores` (122, com o `dcf` aninhado) e `motor_financeiras.avaliar` (146).
- `ficha` nos geradores de PDF: entre 117 e 184 linhas em cada um dos 6.
- `avaliar()` devolve um **dict sem tipo com mais de 60 chaves**, consumido pelo painel, pelo relatório e pelo golden.

### 5.2 Dívida técnica concreta
- **Estado global no import.** `motor_nao_financeiras.py:29-40` carrega `CVM`, `SI` e `derivados_zip.json` ao ser importado, com `ANOS = 2016..2025` fixo. `lote1_bancos.py:17` faz `MK = mercado.vigente()` no import.
  - A auditoria F1-01 achou que importar o lote 4 ou o lote 6 **mudava dicionários globais**: o resultado de `avaliar()` dependia da ordem de import. Foi corrigido só em parte.
- **Copia e diverge.** Os 6 `gerar_pdf_loteN` têm similaridade de 0,15 a 0,49 entre si, e os 6 `atualizar_hall_loteN` de 0,22 a 0,56. As mesmas funções (`capa`, `ficha`, `preencher`, `main`) aparecem reimplementadas em cada um. Os lotes importam uns dos outros.
- **Premissas no código.** São 732 literais numéricos nos 6 `loteN_*.py` e cerca de 445 campos fora do default (inventário em `docs/PREMISSAS-B15.md`). Há datas fixas no código (F1-06), como `ano = "2026" if tk == "SMTO3"`.
- **Empacotamento.** Não há `pyproject`. Os imports dependem do diretório corrente e de `sys.path.insert` (7 vezes). O `requirements.txt` tem 7 pinos; o `requirements.lock` foi medido em Python 3.13 na nuvem, mas o uso local é 3.14.
- **Qualidade estática.** 40% das funções têm alguma anotação de tipo. Não há mypy, ruff nem pre-commit.
- **Unidades.** O motor trabalha em R$ mil, mas a quantidade de ações vem em unidades ou em milhares conforme o formulário da CVM. A escala é inferida por heurística (`reescalar_acoes`: escala log contra o FRE ou limiar de 2e7). Não há tipos de unidade. Real e nominal convivem no mesmo escopo (`ke`, `ke_real`, `w_nom`, `w_real`, `kd`, `kd_real`), que é exatamente o tipo de erro que se repetiu.
- **Windows.** O console é cp1252 (`sys.stdout.reconfigure` espalhado). O repositório mistura LF e CRLF (`core.autocrlf=true`). O backup aponta para o OneDrive. O agendamento usa `.vbs`/`.ps1` com caminho fixo do Python.
- **Desempenho.** O motor é chamado de novo dentro do laço do ponto fixo e na grade de sensibilidade. A exportação do painel leva cerca de 100 s. A suíte do backtest leva cerca de 13 min e estoura memória se houver outros programas abertos (a máquina tem 20 GB de RAM, cerca de 11 GB já usados por VS Code, Claude e navegador; o disco C está com pouco espaço).

### 5.3 Dados
- **No git** ficam 88 arquivos de `dados/`: `cvm_series.json`, `MANIFESTO.json` com 77 sha256, `derivados_zip.json`, `mercado_vigente.json`, fatos, macro e proventos. O `.git` tem 18 MB e o repositório 729 arquivos, incluindo 40 PDFs versionados.
- **Fora do git:**
  - ZIPs da CVM (cerca de 1,7 GB). A CVM reescreve os arquivos, por isso o sha muda e existe `_antes/`.
  - Scraping da StatusInvest.
  - `backtest/dados/` (690 MB).
  - Dados privados (`carteira.local.json`, `dados/privado/`, `RELATORIOS/privado/`), todos ignorados.
- **Clone do zero:** `pytest --ignore=backtest` roda sem os ZIPs, e o que depende deles sai como *skip* com motivo. Com `EXIGIR_DADOS=1`, o skip vira falha.
- **Não há esquema** (JSON Schema/pydantic) para nenhum arquivo de dados.

### 5.4 Testes
- São 72 arquivos `test_*.py` e 853 `def test_`, com 77 `parametrize`. A última suíte completa registrada (30/10) teve **1.059 aprovados**.
- **Cobertura temática:** auditorias numeradas (AUD-xx), escala de ações, dado inválido, CLIs, reprodutibilidade, coletores com HTTP falso, monitor, temporada, triagem, painel (contrato e contraste WCAG), PIT sem vazamento no backtest e oráculo.
- **Propriedades:** 25 `@given` do Hypothesis em `tests/test_oraculo_propriedades.py`, como "desconto só no valor" e monotonicidades. Há um único `xfail(strict=True)`, ligado ao H10, que precisa ser reavaliado porque o H10 foi corrigido.
- **Golden** (`tests/golden.json` + `golden.py`):
  - 41 tickers, com tolerâncias de R$ 0,01 no central, 0,005 no P/C e 0,05 na nota.
  - Os campos `palavra`, `vence_rf`, `lote` e `data_preco` são comparados exatos.
  - `rodar_tudo.py --motivo` regrava e anota em `golden_log.md`.
  - **Prós:** pega qualquer deriva.
  - **Contras:** o golden é gerado pelo próprio motor, então prova estabilidade e não correção; cobre só 12 campos; foi regravado 18 vezes.
- **O que não é testado:**
  - conteúdo dos PDFs;
  - o texto gerado no `03-hall`;
  - coleta real em rede;
  - idempotência das tarefas agendadas;
  - esquema dos JSON;
  - o hook `auto_commit.py`;
  - testes de mutação. O mutmut está planejado (missão O4), não feito.
- **Rastreabilidade** (`docs/RASTREABILIDADE.md`): 213 regras da doutrina, 190 calculáveis, 155 com teste e 35 lacunas. A "catraca" impede o número de lacunas de subir.

---

## 6. Validação científica (o calcanhar de Aquiles)

- **Backtest (parado).** O "portão do proxy" exigia que o motor mecânico, sem as premissas digitadas, reproduzisse a palavra (exata ou ±1 nível) em ≥ 80% dos casos, com mediana de |ΔP/C| ≤ 0,15. **Mediu 70,7% e 0,34.** O backtest não foi enriquecido, para não calibrar contra o golden. As premissas digitadas impedem rodar em datas passadas sem look-ahead.
- **Registro prospectivo** (`ferramentas/prospectivo/registro.jsonl`, com cadeia sha256): 51 vereditos, quase todos de 02/10.
  - Critério pré-registrado em 14/10: correlação de postos entre P/C e retorno excedente sobre a média do hall, em retorno total de 1 ano.
  - Exige ≥ 4 rodadas vencidas e n ≥ 10, então **não há leitura antes do fim de 2027**.
  - A auditoria F5-03 aponta que janelas de 365 dias sobrepostas estão sendo contadas como independentes.
  - Probabilidade por palavra e escore de Brier estão previstos, não implementados.
- **Pré-registro v3** (22/10, append-only): hipóteses H1–H11 sobre o motor, com orçamento de 24 tentativas.

| Hipótese | Resultado |
|---|---|
| H2, espiral de Hamada | aceita |
| H4, rf e π em prazos diferentes | aceita |
| H8, ROE de longo prazo dos bancos digitado diverge do DFP | aceita |
| H10, dado ausente vira zero e ainda gera palavra | aceita (bug) |
| H5, risco-país em dobro | refutada |
| H7, tendência confundida com ciclo | refutada, exceto WEGE3 |
| H1, H6, H11 | a conferir |
| H3, âncoras não independentes | mista: nas financeiras, o cosseno entre DDM e P/VP é ≥ 0,95 |
| H9, conservadorismo empilhado | a taxa domina |

- **Pré-registro v4** (30/10, pela Antigravity). Troca "não mexer sem critério" por **"simetria direcional"**: corrigir com a mesma prioridade os erros que favoreciam BARATA e os que favoreciam CARA. Gerou PR4-01 a PR4-06.
  - **Desvio do registro:** o PR4-04 foi pré-registrado com `DE_MAX = 2,0` e implementado com **2,5**.
  - O PR4-06 implementou a H1 sem que ela tivesse sido aceita.
  - O v4 não tem orçamento de tentativas.
- **"Oráculo"** (`docs/VALIDACAO.md`, `docs/ORACULO.md`, agente `.claude/agents/oraculo.md`). São 7 camadas, inspiradas em Barr et al. (2015) e na SR 11-7 do Fed:

| # | Camada | Situação |
|---|---|---|
| 1 | Especificação | existe |
| 2 | Propriedades (Hypothesis) | existe |
| 3 | Motor-sombra independente | **não existe** |
| 4 | Reconciliação contábil | existe |
| 5 | Sanidade econômica | existe |
| 6 | Resultado | só prospectivo |
| 7 | Agente cego ao autor | **provisório**: só vale depois de pegar 100% das armadilhas plantadas |

---

## 7. Produto: o que o usuário final vê

**Tela** (`ferramentas/painel/web/`): vanilla JS com módulos ES, sem framework nem build, cerca de 1.540 linhas, fontes locais.
- O servidor é `http.server` em 127.0.0.1, só GET/HEAD, com checagem de Host contra DNS rebinding, CSP `default-src 'self'` e `no-store`.
- Navegação por hash: `#/hall`, `#/empresa/TK`, `#/carteira`, `#/monitor`, `#/sistema`.
- A tela não calcula nada, só lê o JSON exportado.
- **Ações (Hall):**
  - cartões por veredito com contagem;
  - tabela de 11 colunas: régua mini, cotação, preço justo, margem, "compra até", DY sustentável, "Supera RF?", sparkline de 12 meses e marca de carteira;
  - filtro "só fonte A/B" e ordenação por um *select* de 4 opções.
  - Distribuição na tela (exportação de 22/10, antes do PR4): 47 empresas, sendo 36 CARA, 5 NC, 4 JUSTA, 1 BARATA (ALLD3) e 1 RADAR (FESA4).
- **Empresa:**
  - cabeçalho com veredito e 5 números;
  - régua grande;
  - preço justo por método, num eixo comum (cheio = entra no central; vazado = informativo);
  - grade de sensibilidade;
  - fundamentos em 5 eixos;
  - riscos e premissas (as de julgamento hachuradas);
  - dividendos de 10 anos e fontes.
- **Carteira** (privada, com "Ocultar valores"): renda mensal, % da meta, evolução, calendário de 12 meses e régua por posição. A concentração por setor aparece como "sem fonte".
- **Alertas (Monitor):** quem entrou ou saiu da faixa de compra ou venda na semana.
- **Status dos dados:** idade de cada fonte, golden e última suíte. É uma tela de engenharia, mostrada ao usuário.
- **Visual:** tema escuro por padrão, paleta "azul-noite + violeta/ciano" (v0.3) com pares WCAG declarados. BARATA é turquesa e CARA âmbar, de propósito sem verde/vermelho de corretora. Gráficos em SVG e CSS feitos à mão, sem biblioteca e sem tooltip real. O dono quer o vocabulário do Investidor10 e do Status Invest, com cara "tech", menos poluição e jargão interno só em dica.

**Saídas em texto:**
- **Relatório por ticker** (`RELATORIOS/<TK>-<data>.md/.pdf`): quase só tabelas "Item | Valor | Papel | Nota | Fonte", com a coluna Fonte repetindo a mesma string longa em cada linha. O jargão é pesado (Ke, EPV Greenwald, Owner Earnings, "Bogle líquido real") e vaza texto interno do motor. Os "comentários do analista" estão marcados "a escrever" (a pasta `relatorio/textos/` não existe). O PDF não tem capa, resumo nem gráfico, e as notas C saem em vermelho, contra o próprio design system.
- **Dossiê** (`DOSSIES/`, ex. `2026-10-07-HYPE3.md`): é **o melhor conteúdo do projeto**, com tese, fosso, gestão, pré-mortem, "por que o mercado erra", projeção, autocrítica e parecer do dono. **Não aparece na tela.**
- **Boletins:** o monitor de 30/10 lista cerca de 32 linhas todas "≥ SAÍDA", e é ruído. **Os de 06/11, 13/11 e 20/11 são só um traceback Python.** A temporada mostra floats crus com ponto decimal americano e instruções de linha de comando.

**Principais debilidades de produto** (avaliação de designer de produto de fintech):
1. O frescor dos dados é invisível e está quebrado: a tela está um mês defasada e nenhum selo global avisa.
2. O veredito não explica o "porquê" em uma frase leiga.
3. Não há histórico de fundamentos na tela (receita, lucro, margens, ROIC × WACC, dívida por ano), nem o preço justo ao longo do tempo.
4. Não há comparação entre empresas, screener, ordenação por coluna nem watchlist "mais perto de virar compra".
5. Os alertas são fracos: não há notificação, alerta por preço nem aviso de "publicou ITR, veja o que mudou".
6. O jargão é explicado só em `title`, que não funciona no toque nem no teclado.
7. A nota de fonte em todo número vira ruído, e falta uma "confiança do veredito" agregada.
8. O mobile é pobre: o Hall corta 7 colunas e a Empresa esconde o gráfico de métodos.
9. Na tela Empresa, os 7 cartões têm o mesmo peso, sem um bloco principal com veredito, uma frase, três números e confiança.
10. Problemas de engenharia que afetam o uso:
    - re-render total da página a cada clique (perde foco e scroll);
    - `aria-live` no `<main>` inteiro;
    - estado de filtro fora da URL;
    - erro mostrado como "rode painel --exportar".

**Para virar SaaS (meta de longo prazo, sem prazo) falta:**
- backend/API e banco;
- autenticação e multiusuário;
- atualização automática com SLA de frescor;
- onboarding e glossário;
- gráficos históricos, screener e alertas por canal;
- PWA;
- **enquadramento regulatório**: provavelmente CVM Res. 20/2021 (analista) ou 19/2021 (consultor), a confirmar com fonte A;
- **licença de dados**: a B3 exige licença para redistribuir, e os termos da StatusInvest estão bloqueados (403). Ver `docs/TERMOS-DE-USO-FONTES.md`.

---

## 8. Operação, automação e governança das IAs

**Hooks do Claude Code** (`.claude/settings.json`):
- `defaultMode: bypassPermissions`; o *deny* cobre só `git push --force*` e `rm -rf*`.
- SessionStart: `git pull --ff-only`.
- Stop: `.claude/hooks/auto_commit.py`, com timeout de 1.000 s. Ele faz:
  1. não age na nuvem;
  2. **sai sem fazer nada se o ramo não for `master`** (`auto_commit.py:164`);
  3. varre segredo e um regex de dado pessoal;
  4. escolhe o destino. Com deleção ou arquivo protegido (golden, doutrina, `03`), vai para o ramo `wip/auto`, que já tem 38 commits nunca revisados. Com testes dos módulos alterados verdes, ou sem código alterado, vai para `master` + push.
- **Problemas do hook:**
  - Antes da reforma, ele fazia push no `master` sem teste quando havia deleção. Foi assim que o commit `05e6636` apagou 25 PDFs (já corrigido).
  - As mensagens dizem só "auto: N arquivo(s)" (27 commits `auto:`).
  - `commit_master` commita no HEAD atual e faz push do `master`.
  - A versão no disco está corrompida e roda os testes duas vezes.
  - Usa `--untracked-files=all`, e `livros/` (302 MB, um PDF de 216 MB, acima do limite do GitHub) e `claude tools/` (notas de outro projeto) **não estão no `.gitignore`**. Se alguém fizer checkout do `master` com a árvore suja, isso pode ser commitado.

**Agentes de IA disponíveis:** `oraculo` (Opus, revisor cego, obrigatório em motor, doutrina, golden ou premissa), `adversario`, `testador`, `documentador`, `varredor`, `verificador-fonte` e `auditor`. Skills: `/fechar`, `/brief`, `/revisar`, `/fatia`, `/checkup` e `/kaizen`.

**Rotina noturna na nuvem (Claude).**
- Pega a primeira missão de `docs/MISSOES.md`, executa, testa e faz push num ramo `claude/*`, nunca no `master`.
- Regra: "decisão reversível = decide, registra e segue; só para em senha, dinheiro ou apagar dados".
- A rede da nuvem **bloqueia b3.com.br e conteudo.cvm.gov.br**, e cerca de 42 testes pulam por falta de dados lá.
- **Impasse estrutural:** toda correção de motor muda o golden, e o golden só pode ser regravado localmente com ok do dono. Os ramos `claude/fase3-bugs` (4 commits), `keen-babbage-vf5kor` (18) e `keen-babbage-bvjh9h` (32) estão parados desde 23–24/10. A rotina parece parada desde então.

**`conferir_noite.py`** (Agendador, 07:15 todo dia):
- Monta uma worktree do `origin/master`, faz o merge do ramo da nuvem, copia os dados locais e roda tudo com `EXIGIR_DADOS=1`.
- Junta no `master` só se estiver verde e sem golden nem doutrina.
- Na prática, retesta os mesmos 3 ramos parados todo dia (7–8 min cada) e sai com código 30 (vermelho).
- Num incidente em 22/10, o teste dele rodou no repositório real e apagou 3 ramos.

**Agendador do Windows (estado real):**

| Tarefa | Quando | Último resultado |
|---|---|---|
| MonitorSemanal | sexta 08:00 | 21 (falha) |
| ConferirNoite | diária 07:15 | 30 |
| BackupSemanal | domingo 07:30 | 0 (ok; zip + git bundle no OneDrive) |
| TemporadaDiaria | 22/10 a 21/11 | 1, **expirada** |

Depende de máquina ligada, sessão aberta e do caminho do Python gravado na instalação. A falha vira um aviso na tela que some em 30 min.

**Várias IAs, padrões incompatíveis.**
- Claude local: português, commits `auto:`, oráculo, fila MISSOES/RELATORIO.
- Claude na nuvem: ramos `claude/*`.
- Gemini/Antigravity (30–31/10): conventional commits **com a identidade git do dono** e sem trailer, LaTeX nos documentos, IDs próprios (F1-xx, PR4-xx) que não batem com os do DECISOES. Não atualizou MISSOES, BRIEF, RELATORIO nem PENDENTE, e não chamou o oráculo.
- Resultado: a mesma correção (H10/A1) existe em duas linhas divergentes.

**Documentação de processo.**
- 47 `.md` ativos (cerca de 870 KB); 222 `.md` rastreados no total (cerca de 3,9 MB).
- Os maiores: `09-diario-de-decisoes.md` 131 KB, relatório da Antigravity 93 KB, auditoria de 08/10 88 KB, doutrina 61 KB, `RASTREABILIDADE` 61 KB.
- MISSOES, BACKLOG, PENDENTE-FRANK, DECISOES, RELATORIO-DIARIO, `09`, PROJECT_BRIEF e `golden_log` registram a mesma coisa em lugares diferentes. **Nenhum reflete a realidade desde 22/10**: o MISSOES diz "em andamento: nenhuma".
- O projeto irmão anterior (`analisador/`) **morreu de excesso de regra**, e o próprio repositório registra sinais da mesma doença.

---

## 9. Linha do tempo

| Data (2026) | Evento |
|---|---|
| set | Começo no Claude Desktop (prompts 00–09). Pipeline antigo extinto em 07/09. |
| 04–05/10 | Auditoria dos PDFs; doutrina v2.0–2.2; 6 lotes recalculados; commit raiz e golden. |
| 06/10 | Backtest: ledger PIT pronto; **portão do proxy falha** (70,7%); validação passa a ser prospectiva. |
| 07/10 | Doutrina v2.3; dossiês BLAU3, CMIN3, HYPE3. |
| 08/10 | **Auditoria 1** (Claude): 109 achados (0 críticos, 5 altos). "As contas do motor estão certas; o problema são os insumos." Doutrina v2.4/2.5 (Hamada, ponto fixo, Kd sintético). `analisador/` arquivado. |
| 09–10/10 | Ondas 2 e 3: reprodutibilidade, backup, testes, blindagem; doutrina v2.6. |
| 13–14/10 | Passagem para Claude Code + GitHub + rotina na nuvem; fila MISSOES/BACKLOG; pré-registro do prospectivo. |
| 19–20/10 | Produto: `relatorio <TK>`, `relatorio CARTEIRA`, tela v0.2; fase 3 "dados vivos" (proveniência por campo, proventos da B3, 19/19 não financeiras com central A/B); dossiês ALLD3 (BARATA), FESA4, SHUL4, VLID3. |
| 21/10 | QA integral (833 testes); doutrina 2.6.1; tarefas do Agendador. |
| 22/10 | 40 commits: rodada da nuvem N1–N11, `conferir_noite.py`, tela v0.3; **diagnóstico do motor**: a mediana P/C de 1,86 é erro de calibração, não da margem; oráculo fases 0–2; pré-registro v3 e H1–H11 (bugs H10 e A1 achados). |
| 23–24/10 | Últimas rodadas da nuvem (ramos `claude/*`, **nunca juntados**). |
| 30/10 | **Auditoria 2** (Antigravity/Gemini): 49 achados (7 críticos, 19 altos, 17 médios, 4 baixos, 2 elogios); notas: engenharia 6,8, doutrina 5,2, validação 5,5, operação 6,5. Veredito do "investidor": "hoje NÃO confiaria dinheiro real". O commit `auto:` 05e6636 apaga 25 PDFs no `master`. |
| 30/10 23:10 – 31/10 00:19 | **10 commits da "reforma"** no ramo local `gemini/reforma`: Parte A (operacional), pré-registro v4, F1-02/03/05, F5-01, PR4-03 a 06. Golden regravado 4 vezes; palavras mudam (KLBN11 NC → CARA; LEVE3 NC → JUSTA). |
| 31/10 09:23 | **Corrupção da árvore de trabalho** (24 arquivos). |
| 06, 13, 20/11 | Monitor de sexta falha (traceback). |
| 21/11 | Tarefa da temporada 3T26 expira sem ter lido os ITRs de novembro. |
| 23/11 | Este briefing. |

---

## 10. Estado exato em 23/11/2026

- **Git** (medido nesta sessão):
  - Ramo `gemini/reforma`, HEAD `7cb5622` (31/10), 10 commits à frente do `master`, que é igual a `origin/master` (`05e6636`, 30/10).
  - **`gemini/reforma` não existe no remoto**, que tem `master`, `wip/auto` e 3 `claude/*`.
  - Nenhum commit em nenhum ramo desde 31/10.
- **Árvore de trabalho:**
  - 24 arquivos modificados (+135/−4), corrompidos. Incluem `03-hall-de-acoes.md`, `_auditoria_antigravity/ACHADOS.csv` e `RELATORIO.md` (com duplicatas), `PRE-REGISTRO-v4.md`, `dados/cvm/MANIFESTO.json`, o hook e 18 `.py`.
  - Não rastreados: 4 boletins, `livros/` (302 MB), `claude tools/` (notas de **outro projeto**, que tem dado de saúde) e dois `.txt` (lista de tickers e de investidores de referência).
- **Testes** (medido nesta sessão):
  - Na árvore atual: **não carregam** (código 4).
  - No HEAD limpo, sem dados locais: **4 falharam, 1.031 aprovados, 45 pulados**, em 4 min 37 s.
  - A última suíte completa registrada é de 30/10: 1.059 aprovados.
- **Temporada 3T26:** de 25/10 a 31/10 só a WEGE3 tinha publicado (0 trocas de palavra). Depois disso nada foi lido; o `--gravar` nunca rodou. A régua estava "congelada até a temporada", que passou.
- **Mercado:** rf e π de 02/10; tela com cotação de 15/10; golden com preço de 02/10.
- **Inconsistências no `03-hall`:** o cabeçalho diz "33 CARA · 3 JUSTA · 5 NC"; LEVE3 aparece em JUSTA e em NC; KLBN11 aparece em CARA e em NC.
- **Pendência do dono aberta desde 10/10:** orçamento, SaaS para quem, objetivo acadêmico, agente de notícias, fonte paga, licença.

**Plano de recuperação que propomos (contestar se houver melhor):**
1. **Salvar antes de tudo:** push do `gemini/reforma` para o remoto e cópia (`git diff > _historico/…patch`) dos 24 arquivos corrompidos.
2. Confirmar arquivo a arquivo que o diff é só a pré-imagem reinserida. O agente de código confirmou o padrão em todos os `.py`; os `.md`, o CSV e o MANIFESTO precisam ser olhados. Depois, restaurar para o HEAD com `git checkout -- <arquivos>`, cópia já guardada.
3. Rodar a suíte com os dados locais e corrigir as 4 falhas do HEAD, ou confirmar que dependem de dado.
4. Passar a reforma pelo `oraculo`, decidir as palavras que mudaram e juntar no `master`.
5. Rodar a temporada 3T26 completa, o monitor e a exportação da tela.
6. Decidir o destino dos 3 ramos `claude/*`: rebase sobre a reforma ou descarte com registro.
7. Pôr `livros/` e `claude tools/` no `.gitignore` ou movê-los para fora do repositório.

---

## 11. Catálogo de problemas por área

Severidade: **P0** quebra ou perde dado agora; **P1** compromete a decisão de investimento; **P2** qualidade, escala ou custo.

### Engenharia
| # | Sev | Problema | Evidência |
|---|---|---|---|
| E1 | P0 | Árvore corrompida; 4 `.py` não passam no parser; correções do motor desligadas em silêncio | `git diff`; `conftest.py:41`; `motor_nao_financeiras.py`, `premio_alavancado`/`credito_observado` |
| E2 | P0 | Ramo com as correções só local, sem push | `git ls-remote` |
| E3 | P0 | Não há CI; "verde" depende do PC do dono e de hooks | sem `.github/`; `auto_commit.py`; `conferir_noite.py` |
| E4 | P1 | Estado global carregado no import; resultado dependente da ordem de import (F1-01 parcial) | `motor_nao_financeiras.py:29-40`; `lote1_bancos.py:17` |
| E5 | P1 | Real × nominal e unidades (R$ mil, ações em mil ou unidade) por convenção, sem tipos; erro recorrente | PR4-04/05/06; `reescalar_acoes` |
| E6 | P1 | Contrato implícito: `avaliar()` devolve dict com mais de 60 chaves | motor; painel/contrato.py; golden |
| E7 | P1 | Golden circular, 12 campos, regravado 18 vezes | `tests/golden.json`; `golden_log.md` |
| E8 | P2 | 18 famílias copiadas e divergentes (lotes, PDFs, atualizadores), cerca de 5.500 LOC | difflib 0,15–0,56 |
| E9 | P2 | Premissas digitadas no código (445 campos / 732 literais) | `docs/PREMISSAS-B15.md` |
| E10 | P2 | Sem pyproject, lint, mypy, venv; lock em outro Python | `requirements.lock` em 3.13 |
| E11 | P2 | Sem esquema para os dados; StatusInvest por scraping | `dados/` |
| E12 | P2 | Desempenho: motor dentro do ponto fixo e da sensibilidade; export de 100 s; backtest estoura RAM | — |
| E13 | P2 | Acoplamento ao Windows (cp1252, `.vbs`, OneDrive, CRLF) | — |

### Método e validação
| # | Sev | Problema |
|---|---|---|
| M1 | P1 | Ke inflado: os 5 p.p. calibrados como prêmio de mercado (β = 1, H5) e depois tratados como desalavancado e realavancados por Hamada. O beta médio do hall fica acima de 1, com viés sistemático para CARA. E vem do ponto fixo (circular). DE_MAX arbitrário (2,0 registrado, 2,5 implementado). |
| M2 | P1 | rf à vista de 7,06% real (pico de juros) tratada como perpétua; π implícita de 6,46% contra Focus de cerca de 4%. O Ke implícito do mercado sai abaixo da rf: a palavra mede "ação × NTN-B no pico", não a empresa. |
| M3 | P1 | Âncoras não independentes: DDM e P/VP saem do mesmo ROE e Ke (cosseno ≥ 0,95); EPV, DCF e OE saem do mesmo NOPAT. A mediana de 2 vira média. Falta âncora independente (múltiplo histórico, NCAV, earnings yield contra NTN-B). |
| M4 | P1 | Financeiras: `roe_lp` digitado diverge do DFP (H8); `dpa_medio_5a` sem IPCA; PR4-07 não feito. Reguladas: Ke da casa de cerca de 12% real contra WACC regulatório de cerca de 8–10% (nota C); sem base de ativos regulatória (RAB); P/VP < 1 por construção (H11 não lida). |
| M5 | P1 | Compounders incompráveis: mediana de 10 anos e "menor dos dois ROIC" punem tendência (WEGE3 com P/C 4,4; ROIC do motor 12–15 p.p. abaixo do DFP, H6). |
| M6 | P1 | Assimetria: dispersão e trava só rebaixam; nenhuma regra sobe a palavra; incerteza vira veto em vez de faixa. |
| M7 | P1 | Validação: nenhum parâmetro (5 p.p., 0,70×, 1,30×) tem base em retorno; prospectivo com n pequeno, um regime de juros, janelas sobrepostas e comparador que só mede ordenação. |
| M8 | P1 | Governança do método: mudanças de 30/10 sem oráculo, com desvio do pré-registro, golden regravado em massa, palavras mudadas sem ok explícito. |
| M9 | P2 | Falsa precisão: centrais em centavos, fronteiras (KEPL3 1,10; ISAE4 1,09), DCF com degraus. |
| M10 | P2 | Viés de universo: 41 blue chips pré-selecionadas; a única BARATA é small cap via dossiê (ALLD3), onde o dado é pior. |
| M11 | P2 | Adaptações nota C: capex de manutenção pelo imobilizado líquido, ROIC a reposição por idade média, spread de Damodaran (EUA) sobre rf brasileira, commodity por proxy BLS × câmbio. |

### Produto
P1 frescor invisível e quebrado · P1 veredito sem explicação leiga · P1 tese do dossiê fora da tela · P2 sem histórico, comparação, screener ou watchlist · P2 alertas sem canal · P2 mobile · P2 PDF sem cara de produto · P2 jargão e excesso de proveniência · P2 tela "Status dos dados" de engenharia para o usuário.

### Processo e operação
P0 falha silenciosa por 23 dias, sem escalonamento · P1 várias IAs sem contrato comum (identidade git, IDs, documentos, oráculo) · P1 impasse nuvem × golden (ramos parados) · P1 documentos de status redundantes e congelados · P2 regras não impostas por código · P2 tarefas com data fixa (EndBoundary 21/11) · P2 `wip/auto` com 38 commits nunca revisados · P2 diretório de trabalho misturado (`livros/`, `claude tools/` de outro projeto).

---

## 12. Restrições

- **Pessoa:** um usuário, uso próprio, sem equipe. Não quer decidir detalhe técnico.
- **Orçamento:** não informado. Pergunta aberta: aceita API de dados paga?
- **Máquina:** notebook Windows 11, 20 GB de RAM, disco C apertado. Jobs longos morrem se o VS Code fechar; o `git commit` às vezes pendura por WMI.
- **Dados:** só fontes gratuitas hoje. A nuvem do Claude não acessa B3/CVM.
- **Privacidade:** a carteira real (quantidades, preço médio, valores) nunca vai para o git nem para serviço de terceiros.
- **Regulatório:** hoje é uso próprio. Veredito para terceiros provavelmente exige enquadramento CVM, ainda não confirmado com fonte A.
- **Licença:** o repositório não tem LICENSE. A redistribuição de dados da B3 exige licença.

---

## 13. Nossas hipóteses (o engenheiro sênior desta sessão). Contestem.

1. **Arquitetura-alvo** em camadas, com um pacote instalável (`pyproject`) e "dados como produto":
   - **(a) ingestão:** coletores idempotentes que gravam **Parquet/DuckDB** com esquema e proveniência (fonte, data, sha, nota) por linha;
   - **(b) premissas:** fora do código, em YAML ou tabela, cada uma com origem, nota, data e responsável;
   - **(c) domínio de valuation:** funções puras, sem I/O e sem estado global, com tipos para unidade (R$ mil, ações) e base (real/nominal) via dataclasses ou pydantic. O resultado de `avaliar()` vira um modelo tipado e versionado;
   - **(d) apresentação:** relatório, PDF e tela consomem o mesmo contrato tipado. Os 6 lotes viram **configuração**, não código.
2. **CI no GitHub Actions** com um snapshot de dados derivado e versionado (pequeno, sem os ZIPs), para que a suíte rode fora da máquina. Mais ruff, mypy e testes de mutação no motor. O hook de auto-commit e a rotina noturna passam a abrir **PR**, nunca a escrever no `master`.
3. **Golden → testes de oráculo independentes:** reconciliação contra o DFP, motor-sombra escrito por outra pessoa ou IA a partir só da doutrina, e propriedades. O golden fica só como detector de deriva, com diff legível e aprovação explícita.
4. **Método:**
   - prêmio por beta setorial bottom-up (Damodaran emergentes) em vez de "5 p.p. desalavancado";
   - rf normalizada (média de 10 anos da NTN-B longa, ou a curva inteira) e π e rf no mesmo vértice;
   - valor em **faixa** (P10/P50/P90 por simulação das premissas), com a palavra pela posição do preço na faixa;
   - uma âncora independente;
   - financeiras com ROE derivado do DFP;
   - reguladas com base de ativos regulatória (RAB) e WACC da ANEEL/ARSESP;
   - e **separar veredito absoluto de ranking relativo** (o ranking é útil mesmo com o nível enviesado).
5. **Validação:** em vez de esperar 2027, reconstruir as premissas como **funções de dados point-in-time** (sem digitação) para religar o backtest. Escore de Brier e calibração por palavra. Janelas não sobrepostas.
6. **Produto:**
   - na tela Empresa, um bloco principal com veredito, uma frase-tese, três números e a confiança;
   - a tese do dossiê na tela;
   - gráficos históricos de 10 anos;
   - watchlist "distância até a compra";
   - selo global de frescor;
   - alertas por e-mail ou push (Agendador ou GitHub Actions);
   - glossário em popover acessível;
   - PDF de 1 página com cara de produto.
7. **Processo:**
   - **um** arquivo de estado (`STATUS.md`, gerado por script a partir do git, dos testes e dos boletins) no lugar de 8 documentos manuais;
   - um contrato único para qualquer IA (identidade git própria, trailer, IDs, checklist de PR);
   - **heartbeat:** "não houve boletim válido em 8 dias" vira alerta no celular;
   - menos regras escritas, mais regras impostas por código.

---

## 14. O que pedimos à IA leitora (formato da resposta)

1. **Diagnóstico independente:** o que está errado ou arriscado que este documento não viu ou subestimou. Ranqueie por impacto na decisão de investimento e no esforço de manutenção.
2. **Arquitetura-alvo** com diagrama, esquema de dados e contrato de `avaliar()`, além de um **plano de migração incremental**, sem reescrever tudo de uma vez e com os testes verdes a cada passo. Diga o que **apagar ou arquivar**.
3. **Método:** respostas fundamentadas às perguntas da seção 15, com fontes acadêmicas ou de mercado nota A/B (Damodaran, McKinsey Valuation, Greenwald, Koller, papers) e como testar cada mudança sem *overfitting* (sem calibrar "para aparecer compra").
4. **Produto e visual:** wireframes em texto ou ASCII das telas Hall, Empresa e Alertas, priorizados, para um usuário leigo, e o relatório/PDF ideal de uma página.
5. **Automação e processo:** CI, alertas, agendamento robusto, governança de várias IAs, redução de documentos. O que um time profissional de quant/fintech faria com um dev solo.
6. **Plano em fases** (30, 60 e 90 dias), com critério de pronto mensurável por fase e o que cortar.
7. **Ferramentas e dados:** o que adotar (ex. DuckDB, Parquet, pydantic, ruff, mypy, mutmut, GitHub Actions, Observable/Plot, uPlot, ECharts, fonte de dados paga), com custo e trade-off.

Seja direto e discorde de nós quando for o caso.

---

## 15. Perguntas abertas de método (para a IA opinar)

1. Os 5 p.p. de prêmio são alavancado (β = 1) ou desalavancado? Manter Hamada? E a mercado ou no ponto fixo? Teto de D/E 2,0 ou 2,5, com que fonte? Ou beta setorial bottom-up?
2. rf à vista ou normalizada? π implícita ou Focus? Mesmo vértice para os dois?
3. Valor como faixa (P10/P50/P90) no lugar da dispersão como veto?
4. Qual âncora independente incluir para não financeiras e para financeiras?
5. Normalização: mediana de 10 anos, ciclo pico a pico ou peso no recente? Como não punir compounders sem abrir porta a otimismo?
6. Financeiras: ROE de longo prazo derivado do DFP (como?). Reguladas: base de ativos regulatória (RAB) e WACC regulatório?
7. Onde mora o conservadorismo (taxa, fluxo ou margem) sem contar em dobro?
8. Como validar com n pequeno e um só regime de juros? Vale religar o backtest com premissas derivadas point-in-time?
9. Beneish e Sloan devem passar de bandeira a veto de BARATA? Estresse de dívida (cronograma, moeda)?
10. Construção de carteira: hoje não há regra de tamanho de posição, concentração nem troca (o dono decidiu não ter limite). O que é mínimo razoável para um investidor de dividendos?

---

## Anexo A: mapa de arquivos-chave

| Caminho | O que é |
|---|---|
| `README.md`, `PROJECT_BRIEF.md` (22/10) | Visão geral e brief (desatualizado) |
| `CLAUDE.md` | Regras para agentes neste repositório |
| `01-doutrina-value-investing.md` | Doutrina v2.6.1 (a especificação) |
| `02`…`08-*.md` | Prompts (dossiê, reavaliação, triagem, recálculo de lote), checklist anti-erro, perfil |
| `03-hall-de-acoes.md` | Índice das 41 com veredito (parte gerada por `hall03.py`) |
| `09-diario-de-decisoes.md` | Diário de decisões (131 KB) |
| `docs/DECISOES.md`, `MISSOES.md`, `BACKLOG.md`, `PENDENTE-FRANK.md`, `RELATORIO-DIARIO.md` | Fila e estado (congelados em 22/10) |
| `docs/PRE-REGISTRO-v3.md`, `v4.md`, `VALIDACAO.md`, `ORACULO.md`, `RASTREABILIDADE.md` | Validação |
| `docs/auditoria/AUDITORIA_2026-10-08.md`, `docs/auditoria/2026-10-22-diagnostico/DIAGNOSTICO.md` | Auditoria 1 e diagnóstico do motor |
| `_auditoria_antigravity/RELATORIO.md`, `ACHADOS.csv` | Auditoria 2 (só no ramo local) |
| `ferramentas/motor_nao_financeiras.py`, `motor_financeiras.py` | Motores |
| `ferramentas/lote{1..6}_*.py`, `*_textos.py`, `gerar_pdf_lote*.py`, `atualizar_hall_lote*.py` | Premissas, textos, PDFs, atualização do 03 |
| `ferramentas/universo.py`, `rodar_tudo.py`, `golden.py`, `tests/golden.json` | Montagem e regressão |
| `ferramentas/coletar_*.py`, `proventos_hall.py`, `precos_hall.py`, `temporada.py`, `monitor_semanal.py` | Coleta e rotinas |
| `ferramentas/relatorio/`, `painel/`, `dossie/`, `triagem/`, `oraculo/`, `backtest/` | Pacotes |
| `ferramentas/agendador/`, `conferir_noite.py`, `.claude/settings.json`, `.claude/hooks/auto_commit.py`, `scripts/cloud_setup.sh` | Automação |
| `RELATORIOS/`, `DOSSIES/`, `BOLETINS/` | Saídas |
| `docs/design/` | Design system e handoff da tela |

## Anexo B: glossário
- **Hall:** as 41 empresas acompanhadas.
- **Lote:** grupo setorial com premissas em código (1 bancos, 2 energia, 3 agro, 4 saúde/telecom, 5 petróleo, 6 química).
- **Dossiê:** análise aprofundada aprovada.
- **Central:** valor intrínseco por ação, a mediana das âncoras.
- **Âncora:** método que entra no central.
- **P/C:** preço ÷ central.
- **Régua:** faixas de P/C que dão a palavra.
- **Palavra:** BARATA / RADAR / JUSTA / CARA / NÃO CONCLUSIVO.
- **Trava 3b:** regra que torna a JUSTA incoerente com o retorno de Bogle em NÃO CONCLUSIVO.
- **Carimbo/armadilha:** marca de §7 (lucro não recorrente, dividendo sem caixa, ROE por alavancagem, múltiplo baixo em topo de ciclo).
- **Nota A/B/C/—:** qualidade da fonte do número.
- **Golden:** fotografia dos resultados dos 41 usada como teste de regressão.
- **Ponto fixo:** iteração em que o Ke depende do valor E e o valor depende do Ke.
- **Hamada:** realavancagem do prêmio pelo D/E.
- **LTM:** últimos 12 meses.
- **DFP/ITR/FRE/FCA/IPE:** formulários da CVM (anual, trimestral, referência, cadastral, eventuais).
- **COTAHIST:** arquivo de cotações históricas da B3.
- **JCP:** juros sobre capital próprio.
- **DY:** dividend yield.
- **Bogle:** retorno esperado = yield + crescimento.
- **EPV:** earnings power value (Greenwald).
- **OE:** owner earnings (Buffett).
- **DDM:** modelo de desconto de dividendos.
- **Oráculo:** conjunto de verificações independentes + agente revisor cego.
- **Pré-registro:** hipótese e critério fixados antes de medir.
- **Temporada:** janela de publicação dos resultados trimestrais.

## Anexo C: números-chave

| Indicador | Valor |
|---|---|
| Código | 219 `.py` / 34.452 LOC |
| Testes | 72 arquivos / 853 funções; 1.059 casos (30/10) |
| Rastreabilidade | 213 regras / 35 lacunas |
| Dados | ~1,8 GB fora do git; `.git` 18 MB; 136 commits na linhagem do HEAD (27 `auto:`) |
| Golden (02/10, pós-PR4-06) | 0 BARATA / 0 RADAR / 4 JUSTA / 34 CARA / 3 NC; P/C mediano 1,94 |
| Tela (22/10) | 47 empresas; 1 BARATA (ALLD3), 1 RADAR (FESA4), 4 JUSTA, 36 CARA, 5 NC |
| Sensibilidade do P/C mediano | 2,03 base → 1,40 com Ke real de 9% → 1,33 com rf 4,5% + prêmio 4 p.p. |
| Backtest | portão 70,7% (meta 80%); ΔP/C 0,34 (meta 0,15) |
| Auditorias | 08/10: 109 achados (0 críticos, 5 altos). 30/10: 49 (7 críticos, 19 altos) |
| Premissas digitadas | ~445 campos; 732 literais nos lotes; 23 tickers com desconto de controlador sem razão |
