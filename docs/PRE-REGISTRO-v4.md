# Pré-registro v4 — Reforma de Engenharia e Álgebra de Valuation (Doutrina v2.7)

Aberto em 30/10/2026 no ramo `gemini/reforma`, sob carta branca do dono, antes de executar qualquer mudança nos motores de valuation (`motor_nao_financeiras.py`, `motor_financeiras.py`) ou na doutrina (`01-doutrina-value-investing.md`).
O arquivo `docs/PRE-REGISTRO-v3.md` permanece estritamente **append-only** e intocado.

---

## 0. Disciplina Científica e Simetria Direcional

1. **Registro prévio obrigatório:** Nenhuma mudança de motor ou doutrina é rodada sem estar descrita abaixo com (a) defeito identificado, (b) motivo algébrico/contábil, (c) fonte primária/oficial (Nota A/B) e (d) direção e efeito esperado.
2. **Isolamento causal (1 mudança lógica por commit):** Cada grupo coeso de correção algébrica é aplicado, testado e medido isoladamente sobre as 41 empresas do Hall, gerando a tabela antes × depois (`central` e `palavra`) no `09-diario-de-decisoes.md` antes do commit seguinte.
3. **Simetria direcional (corrigir nas duas direções com igual prioridade):**
   - **Erros que favoreciam `BARATA`/`JUSTA` (superestimavam o valor justo ou ocultavam falhas):**
     - `PR4-01` (`F1-02`/`H10`): dado contábil crítico ausente convertido silenciosamente em `0` (`v(d, k, 0)`), permitindo palavra de decisão sem D&A, imobilizado, caixa ou dívida.
     - `PR4-02` (`F5-01`): auto-mascaramento no Oráculo (`reconciliacao.py` e `sanidade.py` ignoravam falhas graves em tickers `CARA`/`NC`).
     - `PR4-05b` (`F3-01b`): desconto de benefícios fiscais nominais fixos (`credito_observado`, ex.: ágio/subvenção a prazo certo) por taxa **real** (`w_real`/`ke_real`) em vez de taxa **nominal** (`w_nom`/`ke_nom`), superestimando o escudo fiscal.
     - `PR4-07c` (`F3-09`): cálculo de `bazin6` mesmo sem cobertura de caixa e ausência de trava `NÃO CONCLUSIVO` quando `lpa_norm <= 0` em industriais.
   - **Erros que favoreciam `CARA` (subestimavam o valor justo ou destruíam capital artificialmente):**
     - `PR4-03` (`F3-03a`/`A1`): desconto do controlador aplicado **dentro** do laço de ponto fixo de `estrutura_de_capital`, inflando $D/E$ e $K_e$ e derrubando `nota_qualidade`.
     - `PR4-04` (`F3-03b`/`H2`): uso de dívida **bruta** (ignorando caixa) em Hamada sobre $E$ realimentado sem teto de alavancagem, gerando espiral da morte ($K_e = 64,7\%$ em `KLBN11`, $34,3\%$ em `SUZB3`) e não-unicidade em `RECV3`.
     - `PR4-05a` (`F3-01a` + `F3-07`): subtração de encargo financeiro **nominal** (`kd * dl`, que embute amortização inflacionária $\pi \cdot DL$) de `nopat` e `lucro_pre_ir` **reais** em `lpa_norm` e `lair_norm`, e soma de D&A nominal histórica sem deflator IPCA em `ebitda_norm`.
     - `PR4-06` (`F3-02`/`H1`+`H6`): comparação de `roic_rep_c` (real) contra `w_nom` (nominal) na trava de crescimento do DCF, e divisão da margem mediana de 10 anos pelo capital investido de 2026 (`H6`).
     - `PR4-07a/b`: em `motor_financeiras.py`, uso de `g` pré-corte após o haircut de 40% na renovação de 2033 da `BBSE3` (`F3-05`, que superestimava o terminal da `BBSE3`!), omissão do desconto do controlador em `roe_implicito` (`F3-06`), e `dpa_medio_5a` nominal sem correção por IPCA nos lotes 1 e 2 (`F3-04d`).

---

## 1. Mudanças Pré-Registradas

### PR4-01 (`F1-02` / `H10` + `F1-03` + `F1-05`) — Integridade de Dados: Proibição de Zero Silencioso, Escala de Ações e Cadastro Completo
- **Mudança:**
  1. Em `motor_nao_financeiras.py`, criar `criticos_ausentes(tk, anos)` verificando a presença explícita (não-`None`) de `caixa`, `divida` (`emprest_cp`/`emprest_lp`), `pl`, `lucro`/`lucro_controlador`, `receita`, `da` e `imobilizado` no LTM e de `pl`, `da` e `imobilizado` nos exercícios da janela histórica. Se qualquer conta crítica estiver ausente (`None`), `avaliar()` força `palavra = "NÃO CONCLUSIVO"` com motivo `"não conclusivo (dado crítico ausente: ...)"`. Em `montar_series.py`, não somar `0.0` em eventos de proventos sem valor (`eventos_sem_valor`).
  2. Em `lote4_saude_telecom.py:84`, alinhar o limiar de conversão milhar $\rightarrow$ unidade de ações para `n < 1e7` (consistente com `lote3_agro.py:37` e `dossie/base.py:180`), impedindo multiplicação errônea por 1.000 em empresas com $10\text{M} \le n < 100\text{M}$ ações já em unidades.
  3. Em `proventos_ex.py` e `relatorio/quali.py`, completar `PREGAO`, `CLASSE` e `CADASTRO` (CNPJ + pregão) para as empresas do Hall a partir do `MANIFESTO.json` / CVM (Nota A).
- **Motivo:** `None` significa "não sei", não `R$ 0`. E uma empresa com 50 milhões de ações em unidades não pode ter suas ações multiplicadas por 1.000.
- **Fonte:** CVM (Ofício-Circular/CVM/SEP e estrutura DFP/ITR/FRE — Nota A); Doutrina §1 (`01-doutrina-value-investing.md:19`: dado ausente trava em `NÃO CONCLUSIVO`).
- **Efeito esperado no Hall (41 tickers):** **0 palavras e 0 centrais mudam** (todas as 21 industriais do Hall possuem as contas críticas preenchidas em `cvm_series.json`; a guarda protege contra buracos futuros de ITR/DFP e fecha o `xfail` de `H10`).

---

### PR4-02 (`F5-01` + `F5-06`) — Fim do Auto-Mascaramento no Oráculo
- **Mudança:**
  1. Em `ferramentas/oraculo/reconciliacao.py` e `ferramentas/oraculo/sanidade.py`, erros estruturais graves (escala de ações divergente do FRE em mais de `[0,5; 2,0]`, violação de identidade contábil DFP `Ativo = Passivo + PL`, `central <= 0`, `NaN`/`inf`) passam a ser reportados de forma visível independentemente de a palavra ser `CARA`, mantendo o controle de regressão (`CONHECIDOS`) explícito.
  2. Em `ferramentas/oraculo/reconciliacao.py`, expor `falhas_todas` (além de `falhas` nas palavras de decisão) e reprovar qualquer erro de escala de ações (`acoes_lote`) em **qualquer** empresa do Hall (mesmo `CARA`), pois um erro de 1.000× nas ações transforma uma ação `BARATA` em `CARA` e antes se auto-mascarava!
- **Motivo:** Um verificador que ignora erros de escala quando a saída é `CARA` é cego exatamente para o bug que joga o valor justo para zero.
- **Fonte:** CVM FRE / DFP (Nota A) e `docs/PRE-REGISTRO-v3.md` §4 (Camada 3).
- **Efeito esperado:** O Oráculo passa a bloquear imediatamente qualquer erro de escala de ações (`acoes_lote`) ou corrupção numérica (`NaN`/`inf`) em 100% das 41 empresas do Hall.

---

### PR4-03 (`F3-03a` / `A1`) — Desconto do Controlador Fora do Ponto Fixo do WACC
- **Mudança:** Em `ferramentas/motor_nao_financeiras.py:648, 654` (`estrutura_de_capital`), calcular `c = median(v["anc"].values())` **sem** multiplicar por `(1 - desc)` dentro do laço de ponto fixo dos pesos $D/E$, mantendo o desconto do controlador `(1 - desc)` aplicado uma única vez às âncoras e ao valor central final (`avaliar`).
- **Motivo:** A Doutrina §5 (`01:103, 105`) estabelece que o desconto do controlador incide **uma única vez** sobre o valor industrial para proteger contra risco de governança/expropriação, e não muda a estrutura de capital física da firma nem o seu ROIC/WACC operacional (`nota_qualidade`). Aplicá-lo dentro de `estrutura_de_capital` encolhia $E$, inflava $D/E$ e $K_e$, e penalizava a `PETR4` duas vezes.
- **Fonte:** Doutrina §5 (`01-doutrina-value-investing.md:103, 105`); Damodaran (*Applied Corporate Finance*, 4th ed., cap. 4 e *The Value of Control*, 2005 — Nota A/B: descontos de governança/falta de controle ajustam o valor das ações para o minoritário, não a alavancagem financeira da firma).
- **Efeito esperado no Hall (41 tickers):** Apenas **1 ticker** muda o valor central: `PETR4` (`central` passa de `R$ 53,48` para `R$ 52,87`, `-1,14%`, porque sem o desconto de 10% no ponto fixo o peso $E/(D+E)$ sobe de `0,602` para `0,625`, elevando levemente o WACC onde $K_e > K_d(1-t)$). **0 palavras mudam** (`PETR4` segue `CARA`). Fecha o `xfail` `test_desconto_do_controlador_so_no_valor_industrial` e a lacuna `D5.09`.

---

### PR4-04 (`F3-03b` / `H2`) — Dívida Líquida em Hamada e Estabilização do Ponto Fixo do WACC
- **Mudança:** Em `ferramentas/motor_nao_financeiras.py:609-660`:
  1. Substituir a dívida bruta (`bruta`) pela **dívida líquida positiva** `d = max(dl, 0.0)` tanto no prêmio de alavancagem de Hamada (`premio_alavancado`) quanto nos pesos de dívida do WACC em `estrutura_de_capital`.
  2. Impor teto econômico de alavancagem `DE_MAX = 2.0` ($D/E \le 2,0$, equivalente a $D/(D+E) \le 66,7\%$) no multiplicador de Hamada `premio_alavancado`, evitando a espiral de realimentação onde $E \to 0 \Rightarrow D/E \to \infty \Rightarrow K_e \to \infty$ e garantindo contração única (unicidade de ponto fixo em 100% dos tickers, incluindo `RECV3`).
- **Motivo:**
  1. Uma empresa que emite dívida bruta e mantém o recurso em caixa (ex.: para fazer frente ao cronograma de amortização) não tem o risco operacional/financeiro da dívida bruta: o caixa (ativo de risco zero) compensa a dívida (dívida líquida = dívida bruta − caixa). Usar dívida bruta violava a propriedade monotônica `H2(b)` (reter caixa com dívida bruta constante reduzia ou distorcia o valor) e levava `KLBN11` a $K_e = 64,73\%$ e `SUZB3` a $K_e = 34,27\%$.
  2. Quando o ponto fixo realimentava $D/E$ sem teto sobre o valor central, criava-se multiplicidade de raízes (`RECV3` convergia para `R$ 15,61` partindo do PL e `R$ 16,80` partindo do preço de mercado, `H2a`) e $K_e > 30\%$ em 4 empresas (`H2c`).
- **Fonte:** Damodaran (*Applied Corporate Finance*, 4th ed., cap. 4, "Cash and Beta / Net Debt Ratio", e *Investment Valuation*, 3rd ed., cap. 8 — Nota A/B: quando a dívida é deduzida do caixa para formar o Enterprise Value no numerador, a relação de alavancagem consistente em Hamada e no WACC sobre o negócio operacional é a Dívida Líquida).
- **Efeito esperado no Hall (41 tickers):** Reduz os $K_e$ artificiais de `KLBN11` (`64,7% -> ~24,5%`), `SUZB3` (`34,3% -> ~24,5%`), `SLCE3` (`31,3% -> ~21,6%`) e `SMTO3` (`30,3% -> ~22,2%`), elimina a não-unicidade de `RECV3` e reduz o contador `CONHECIDOS` de `oraculo/sanidade.py` de `(1, 4)` para `(0, 0)`.

---

### PR4-05 (`F3-01` + `F3-07`) — Consistência Real vs. Nominal Simétrica (`kd_real` no Lucro Normalizado, Desconto Nominal em `beneficio_fiscal` e Deflator em `ebitda_norm`)
- **Mudança (nas duas direções):**
  1. **Direção A (corrigindo subestimação de `lpa_norm` e `lair_norm`):** Em `motor_nao_financeiras.py:702, 947`, substituir `kd` nominal pelo **custo real da dívida** `kd_real = (1 + kd) / (1 + mk.pi) - 1` ao deduzir encargos financeiros da dívida líquida sobre `nopat` e `lucro_pre_ir` (que estão em moeda constante de hoje). NaDRE nominal, a despesa financeira $K_{d,\text{nom}} \cdot DL$ compõe-se do juro real $K_{d,\text{real}} \cdot DL$ mais a recomposição inflacionária do principal $\pi \cdot DL$ (que é contrabalançada pelo ganho monetário real da erosão inflacionária do passivo líquido $\pi \cdot DL$). Subtrair $K_{d,\text{nom}} \cdot DL$ de um NOPAT real contava a inflação como despesa real perpétua.
  2. **Direção B (corrigindo superestimação de `beneficio_fiscal`):** Em `motor_nao_financeiras.py:575-591, 703, 712, 754`, corrigir `credito_observado` para deflacionar até hoje (`DEFLATOR[ult] * deflator_ltm(emp.ticker)` quando aplicável ao fluxo base) e, para benefícios fiscais de **prazo finito fixados em moeda nominal histórica** (amortização fiscal de ágio / créditos fiscais sem indexação por IPCA, como `HYPE3` até 2030), descontar pela taxa **nominal** (`w_nom` na firma, `ke_nom` no acionista) em vez da taxa real (`w_real`/`ke_real`).
  3. **Direção C (`F3-07`, `ebitda_norm` em moeda constante):** Em `motor_nao_financeiras.py:925-926`, deflacionar a D&A histórica de cada exercício `x` por `DEFLATOR[x]` (`a[x]["da"] * DEFLATOR[x]`) antes de tomar a mediana de 3 anos somada ao EBIT normalizado real.
- **Motivo:** Cumprir rigorosamente a regra áurea da Doutrina §4 (`01:55`): *"Nunca misture: fluxo em reais correntes → Ke nominal; fluxo real → Ke real"*.
- **Fonte:** Damodaran (*Investment Valuation*, 3rd ed., cap. 10, "Inflation and Valuation: Real vs. Nominal Cash Flows", e *Return on Capital*, 2007 — Nota A/B); CPC 00 / IAS 29 (ganho/perda monetária líquida sobre passivos monetários sob inflação).
- **Efeito esperado no Hall (41 tickers):** Sobe o `lpa_norm` (e as âncoras de Graham / P/L) das industriais com dívida líquida positiva (`KLBN11`, `SUZB3`, `CSAN3`/`RAIZ4`, `SMTO3`, `SLCE3`, `LEVE3`), reduz levemente o valor presente do benefício fiscal a prazo fixo (`HYPE3`), e corrige `dl_ebitda_norm` em todas as industriais.

---

### PR4-06 (`F3-02` / `H1` + `H6`) — Trava de Crescimento do DCF na Mesma Base Real e ROIC Mediano Ano a Ano
- **Mudança:**
  1. Em `motor_nao_financeiras.py:721`, comparar `roic_rep_c` (cujo denominador `cap_rep` já incorpora a inflação acumulada na idade da planta, sendo retorno real) contra `w_real` (WACC real) e `roic_c` (retorno real corrente sobre capital investido corrente) contra `w_real`, eliminando a comparação assimétrica de taxa real contra `w_nom` (~19% nominal).
  2. Em `motor_nao_financeiras.py:688-692` (`H6`), calcular `roic` como a **mediana dos ROICs anuais efetivos** da janela (`nopat_t / cap_inv_t` de cada exercício com capital investido positivo, complementado pelo retorno normalizado sobre o capital corrente quando a série histórica de capital for incompleta), deixando de dividir o NOPAT da receita média de 10 anos pelo capital expandido de 2026.
- **Motivo:** Em `WEGE3`, dividir a margem e a receita históricas pelo capital de 2026 derrubava o ROIC de `38,5%` para `23,8%` (`H6`), e comparar `roic_rep_c` (`16,3%` real) contra `w_nom` (`19,0%` nominal) zerava o crescimento (`g_ef = 0`) de uma empresa que reinveste com ROIC real muito acima do WACC real (`11,8%`).
- **Fonte:** Damodaran (*Return on Capital (ROC), Return on Invested Capital (ROIC) and Return on Equity (ROE): Measurement and Implications*, SSRN 1105499, jul. 2007, pp. 14–22 e 38–42 — Nota A: consistência temporal entre numerador e denominador do ROIC e consistência inflacionária entre ROIC real ajustado por inflação e WACC real).
- **Efeito esperado no Hall (41 tickers):** Conforme já medido em `H1(b)` (`docs/oraculo/hipoteses-2026-10-22.md:8`), destrava `g_ef > 0` na âncora DCF de `WEGE3` e `ABEV3` e corrige o indicador `roic` reportado nas industriais em crescimento, com impacto controlado no `central` (mediana de 5 âncoras).

---

### PR4-07 (`F3-04d`, `F3-05`, `F3-06`, `F3-08`, `F3-09`, `F1-07`) — Correções Algébricas em `motor_financeiras.py` e Alinhamento Fino Doutrina–Código
- **Mudança:**
  1. **`F3-05` (`ddm_contrato_finito` da `BBSE3`, `motor_financeiras.py:296-326`):** Após aplicar `corte_renovacao` (`40%`) ao lucro no ano `emp.ano_renovacao - ANO_BASE` (`lpa_pos = lpa * (1 - emp.corte_renovacao)`), recalcular a taxa de crescimento perpétuo pós-renovação `g_pos = g_de(emp, mk, emp.roe_lp * (1 - emp.corte_renovacao))` em vez de perpetuar o `g` pré-corte. *(Nota de simetria: esta correção **reduz** o valor central da `BBSE3` de `R$ 26,41` para `R$ 25,67`, corrigindo um erro que favorecia `BARATA`/`JUSTA`!)*.
  2. **`F3-06` (`roe_implicito`, `motor_financeiras.py:474-477`):** Aplicar `(1 - desc_pct)` ao VPA em `roe_implicito`: `vpa_desc = emp.vpa * (1 - desc_pct)`, cumprindo a Doutrina §5 (`01:103`).
  3. **`F3-04d` (`dpa_medio_5a` em `lote1_bancos.py` e `lote2_energia.py`):** Deflacionar os dividendos por ação de 2021–2025 pelo `DEFLATOR` do IPCA ao calcular `dpa_medio_5a`, alinhando os lotes 1 e 2 à mesma moeda constante já usada em `motor_nao_financeiras.py:957`.
  4. **`F3-08` (`owner_earnings_ano`, `motor_nao_financeiras.py:317-319`):** Em `owner_earnings`, usar a variação real de capital de giro `dwc` ao longo dos exercícios da janela de 5 anos (sem truncar `max(dwc, 0)` ano a ano antes da mediana quando o ciclo tem liberação compensatória, limitando apenas na mediana quinquenal `max(median(dwcs), 0.0)` para não criar caixa perpétuo artificial de liquidação de estoque).
  5. **`F3-09` + `F1-07`:**
     - Em `motor_nao_financeiras.py:993-994`, calcular `peg` e `pegy` usando `g_real` (em pontos percentuais, com guarda `g_real > 1e-6`), conforme `01:236`.
     - Em `motor_nao_financeiras.py:961` e `motor_financeiras.py:441`, retornar `bazin6 = None` quando `not coberto` (`01:129`: Bazin exige cobertura de caixa).
     - Em `motor_nao_financeiras.py:969`, forçar `palavra = "NÃO CONCLUSIVO"` quando `lpa_norm <= 0` (`matriz.py:D11.1.52`).
     - Em `motor_nao_financeiras.py:866-879` (`_bissecao`), retornar `None` quando não houver mudança de sinal no intervalo `[lo, hi]` (evitando retornar falsamente `50,0%` quando $K_e$ está fora do domínio).
- **Motivo:** Eliminar todas as contradições entre a Doutrina (`01-doutrina-value-investing.md`) e o código executável.
- **Fonte:** Doutrina §§4, 5, 6, 11 (`01-doutrina-value-investing.md`); Damodaran (*Investment Valuation*, cap. 14 — DDM com mudança de ROE em estágio terminal exige recalcular $g_{\text{terminal}} = ROE_{\text{terminal}} \times b$).
- **Efeito esperado:** Corrige o terminal da `BBSE3`, o `roe_implicito` das estatais/controladas, o `bazin6` em moeda constante dos lotes 1 e 2, o `peg`/`pegy` real e elimina falsas raízes nas bisseções.
