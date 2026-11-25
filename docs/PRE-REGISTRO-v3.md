# Pré-registro — validação e recalibração do motor (doutrina v3)

Aberto em 22/10/2026 (Fase 0 de `docs/PROMPT-ORACULO-E-CALIBRACAO.md`). Nenhuma palavra, central, golden ou doutrina mudou.
**Aprovado pelo Frank em 22/10/2026**, depois de 5 ajustes: H9 com duas referências, §4.3 com o limite das premissas
digitadas, H11 nova, H8 com todas as financeiras, e a H1 com gabarito de fonte, a H7 com BH e a H10 com `:287`.
Este arquivo é **append-only** depois do "ok" do Frank: hipótese, teste e critério não se reescrevem; correção entra como
emenda datada no fim (§7), com o motivo, e conta como tentativa nova.

## 0. Regras do pré-registro
1. **Antes de rodar.** Toda variante de regra testada (fórmula, premissa, régua) entra aqui com hipótese, teste e critério
   de aceitação **antes** da primeira execução. Variante sem linha no §6 não vale como evidência.
2. **Origem exploratória declarada.** H1–H10 nasceram de olhar os números do diagnóstico de 22/10 (HARKing, Kerr 1998);
   a H11 foi pedida pelo Frank na revisão do pré-registro.
   Por isso a observação que gerou a hipótese **não conta** como confirmação: só conta o teste novo descrito em cada uma
   (propriedade, cálculo independente, fonte externa, outra data). Onde o teste reusa o mesmo dado, o resultado vale como
   "consistente", não como "confirmado".
3. **O número de BARATAs não é critério**, nem a mediana de P/C perto de 1. Calibrar até aparecer compra é overfitting
   (Harvey, Liu & Zhu 2016; Bailey & López de Prado 2014). Critério válido: coerência interna, correção verificável
   (camadas 1–5) e acerto no tempo (camada 6).
4. **Orçamento de tentativas.** Até 3 variantes por item da proposta v3 e **no máximo 24 no total**. Cada execução de
   variante sobre o hall é uma tentativa e entra no §6, inclusive as descartadas. O total entra no deflator da Fase 7
   (Deflated Sharpe/PBO).
5. **Ordem de escolha entre variantes:** (i) solidez conceitual com fonte A/B; (ii) camadas 1–5 verdes; (iii) camada 6,
   quando houver dado. A contagem de palavras resultantes só é **relatada**, nunca usada para escolher.
6. **Mudou palavra → Frank decide** (regra 3 do prompt). Lembrete: `docs/PREMISSAS-B15.md` l.29/31 mantêm a régua congelada
   até a temporada do 3T26; a implementação da v3 (Fase 6) depende de o Frank levantar esse congelamento.

## 1. Baseline congelado
- Commit `9caaf30`. Mercado: `ferramentas/mercado_vigente.json` (data **02/10/2026**: rf real 7,06% no IPCA+ 2050 sem
  cupom, π 6,46% no vértice de 2520 du da ETTJ ANBIMA). Preços: `hall.json` (`preco_hoje`, 22/10).
- Reproduzido em 22/10 (`docs/auditoria/2026-10-22-diagnostico/sens*.py`, executados fora da pasta, sem gravar):

| Cenário (38 tickers dos lotes) | P/C mediano | ≤ 0,70 | ≤ 0,90 | ≤ 1,10 |
|---|---|---|---|---|
| base | 2,03 | 0 | 0 | 2 |
| rf real 5,0% | 1,53 | 0 | 2 | 6 |
| prêmio 3 p.p. | 1,54 | 0 | 2 | 6 |
| π 4% (Focus) | 1,82 | 0 | 1 | 2 |
| Ke real 9% | 1,40 | 0 | 6 | 11 |
| rf 4,5% + prêmio 4 p.p. | 1,33 | 2 | 7 | 14 |
| Industriais (20): base / dívida bruta a mercado / líquida a mercado / sem Hamada | 1,85 / 1,95 / 1,82 / 1,59 | — | 0/0/0/3 | 2/2/3/6 |

- Funil do hall (47): BARATA 1, RADAR 1, JUSTA 4, CARA 36, NÃO CONCLUSIVO 5; 41 com `pc_hoje`, mediana **1,86**, 5 acima
  de 3×. **Confere com o diagnóstico.** Nota: 45 têm `central`; 4 deles não têm `pc_hoje`.
- Fatos novos da Fase 0 (entram como hipóteses):
  - Rf e π são de 02/10 e o preço é de 22/10, o que contraria o `DATA_BASE` de `PREMISSAS-B15` l.20, que manda travar rf e π no dia do preço (H4).
  - A doutrina diz que π é a implícita entre o prefixado e o IPCA+ **do mesmo prazo** (`01` l.53). O arquivo usa o vértice de 10 anos, e a rf vem do título de 2050 (H4).
  - O filtro 1 e a trava de g comparam em termos **nominais**, com o menor ROIC (`01` l.20, l.245). A exceção de saída compara em termos **reais** (`01` l.194). A doutrina não é coerente consigo mesma (H1).
  - WEGE3: m50 (mediana de 10 anos) = 16,2%, contra uma margem EBIT de 19,6% em 2025 (11,4% em 2016). O ROIC contábil é 23,8% e o ROIC a reposição 16,3%, contra um WACC nominal de 19,0%. A trava zera o g real de 2% **e** o g1 de 6,9% do compounder (H1, H6, H7).
  - ITUB4: `roe_lp` 17,58% foi digitado como "mediana 2016–25 (13,2–21,9%)" e não é recalculado do dado (H8).

## 2. Hipóteses

Formato: **enunciado** · *teste que pode refutar* · **critério** (decidido agora) · camada · fase.

### H1 — A trava de g mistura medida real com WACC nominal
O `dcf()` (`motor_nao_financeiras.py:721-722`) libera g só se min(ROIC contábil, ROIC a reposição) > WACC nominal. O ROIC
a reposição corrige o capital pela inflação, então é uma medida aproximadamente **real**, e o WACC é **nominal**. O efeito
é que g = 0 para quase todo industrial, inclusive para compounders.
- *Teste:* (a) teste especificado (camada 1). Um caso sintético com inflação π e ROIC real = WACC real + 3 p.p. A
  **resposta certa vem da fonte, não da hipótese**: o gabarito (cria ou não cria valor, e como ROIC contábil e capital
  a reposição se comportam sob inflação) é tirado de Damodaran (*Investment Valuation*, cap. sobre inflação e retorno sobre
  capital; *Return on Capital (ROC), Return on Invested Capital (ROIC) and Return on Equity (ROE): Measurement and
  Implications*, 2007) e de Greenwald et al. (*Value Investing: From Graham to Buffett and Beyond*, crescimento e
  franquia). Os dois são conferidos pelo `verificador-fonte` antes de virar teste e citados no teste com página e seção.
  Fonte que não for nota A/B → o caso fica "a conferir" e (a) não conta. Depois, rodar a função atual contra esse gabarito.
  (b) No hall, contar os tickers cuja trava muda entre a regra atual e a regra que a fonte indicar, e medir a variação do
  central.
- **Critério.** H1 é **aceita** se (a) a regra atual contraria o gabarito da fonte **e** (b) a trava muda em ≥ 3
  tickers, com |Δcentral| ≥ 10% em pelo menos 3. É **refutada** se (a) concordar com a fonte, ou se (b) der < 3 tickers.
- Camadas 1 e 2 · Fases 2 e 5 (item 3).

### H2 — Hamada com dívida bruta e E do modelo cria realimentação (artefato)
O prêmio é 5 p.p. × [1 + (1−t)·D/E], com D bruta e E = central × ações no ponto fixo (`:632-663`). Um central baixo eleva
D/E, que eleva o Ke, que baixa o central. KLBN11 sai com Ke de 65% e D/E 11,4; a mercado o D/E é 1,6.
- *Teste:* (a) unicidade do ponto fixo: partir de 3 E iniciais (PL, valor de mercado, 3× PL) e verificar se convergem ao
  mesmo central; (b) propriedade: aumentar o caixa com a dívida bruta igual não pode **reduzir** o central; (c) teto:
  Ke nominal por ticker ≤ 30%.
- **Critério.** **Aceita** se qualquer ticker do hall falhar (a) com |Δcentral| > 1% entre os pontos de partida, **ou**
  ≥ 2 tickers violarem (c). **Refutada** se (a), (b) e (c) passarem em todos.
- Camadas 2 e 5 · Fases 2 e 5 (item 2).

### H3 — As âncoras não são independentes
A doutrina usa a mediana das âncoras para diversificar erro (`01` l.268). DDM e P/VP justificado (financeiras) e
EPV/DCF/OE (industriais) partem do mesmo fluxo normalizado e do mesmo Ke. A dispersão dos bancos é ≈ 1,01.
- *Teste:* para cada ticker, a elasticidade de cada âncora a (Ke, fluxo normalizado, g) por diferença finita de ±10%.
  Mede-se o cosseno entre os vetores de elasticidade das âncoras.
- **Critério.** **Aceita** se, em ≥ 70% dos tickers de cada motor, todo par de âncoras tem cosseno ≥ 0,95. **Refutada** se
  ≥ 1 âncora por motor tem cosseno < 0,80 contra as demais na maioria dos tickers.
- Camada 5 · Fases 2 e 5 (item 5).

### H4 — rf e π em horizontes e datas diferentes
A rf é do vértice de 2050 (cerca de 24 anos) e a π do vértice de 10 anos, os dois de 02/10. O preço é de 22/10. A doutrina
pede a implícita do mesmo prazo e no dia do preço.
- *Teste:* recalcular π no vértice da rf (implícita prefixado × IPCA+ de prazo equivalente, mesma data) e rf e π em 22/10.
  Medir Δπ, ΔKe nominal e as palavras que mudam, sem gravar.
- **Critério.** **Aceita** (como inconsistência a corrigir) se |Δπ| ≥ 0,50 p.p. **ou** se ao menos 1 palavra muda.
  **Refutada** se |Δπ| < 0,50 p.p. e nenhuma palavra muda. Nos dois casos registra-se a divergência entre a doutrina e o
  código.
- Camada 4 (dado) · Fase 2.

### H5 — O prêmio conta risco-país em dobro
O NTN-B já contém o spread de default soberano. Damodaran tira esse spread da taxa do título local antes de somar ERP madura + CRP. A doutrina
soma 5 p.p. sobre a NTN-B cheia, sem dizer se os 5 p.p. são ERP madura ou ERP + CRP.
- *Teste:* (a) `verificador-fonte` confere o método no texto de Damodaran (*Country Risk*, edição vigente) e lê spread e
  CRP do Brasil na planilha `ctryprem` vigente. (b) Calcular Ke_D = (NTN-B − spread) + β·(ERP madura + CRP) com β = 1 e
  comparar com o Ke real da casa (12,06%).
- **Critério.** **Aceita** se a fonte for nota A/B **e** Ke_casa − Ke_D ≥ 1,0 p.p. **Refutada** se |Ke_casa − Ke_D| < 1,0
  p.p. Nesse caso o nível de cerca de 12% é defensável e o problema está em outra parte. Fonte não confirmada → "a conferir",
  sem efeito.
- Camada 1 (fonte) · Fase 5 (item 2).

### H6 — O ROIC da WEGE3 (e de quem cresce) está subestimado pela construção, não pela empresa
O ROIC do motor = NOPAT normalizado (receita média × **mediana de 10 anos** da margem) ÷ capital **atual**. Numa empresa com
margem em alta, isso põe o numerador do passado sobre o denominador de hoje. O ROIC a reposição soma o imobilizado ×
(IPCA da idade − 1).
- *Teste:* (a) ROIC anual independente, calculado à mão a partir do DFP da CVM: EBIT × (1−t) ÷ (PL + DL médios), sem
  importar o motor. (b) Comparar com o ROIC divulgado pela WEG no RI (fonte A). (c) Reproduzir o "4 de 10 anos" da triagem com
  a definição do (a).
- **Critério.** **Aceita** se o ROIC do motor fica ≥ 5 p.p. abaixo da mediana dos 3 últimos anos do (a) **e** o (a) bate
  com o RI a ±3 p.p. **Refutada** se o motor estiver a ±3 p.p. do (a). Repetir em 2 outros tickers de margem em alta,
  escolhidos pelo teste de tendência da H7 antes de olhar o ROIC.
- Camadas 1 e 4 · Fase 2 (reconciliação) e Fase 4 (âncora externa).

### H7 — A normalização confunde tendência com ciclo
A mediana de 10 anos (`01` l.228, l.276) supõe reversão à média. Numa empresa com margem em tendência estrutural, ela
subestima o fluxo sem que haja ciclo.
- *Teste:* Mann-Kendall nas margens de 10 anos de cada industrial. Como são cerca de 21 testes, a significância é decidida
  com correção de Benjamini-Hochberg (FDR q = 0,05) sobre todos os p-valores da rodada, e não com α = 0,05 por ticker.
  Nos tickers que passarem, comparar m50 com a mediana dos 3 últimos anos.
- **Critério.** **Aceita** se ≥ 3 tickers não cíclicos têm tendência positiva significativa após BH **e** m50 ≥ 2 p.p. abaixo dos 3
  últimos anos. **Refutada** se < 3. A escolha da normalização nova **não** sai daqui: sai da camada 6 (Fase 7).
- Camada 5 · Fase 2 (relatório) e Fase 5 (item 4).

### H8 — O ROE de longo prazo dos bancos está desalinhado do Ke
O `roe_lp` é digitado (ITUB4 17,58%) e comparado com o Ke **nominal** de 19,3%, que embute π de 6,46%. Isso dá P/VP < 1 por
construção para banco de ROE de 20% ou mais.
- *Teste:* (a) recalcular o ROE anual a partir da CVM (lucro do controlador ÷ PL médio) e conferir o `roe_lp` digitado
  (camada 4) de **todas** as empresas com `roe_lp`, não só a ITUB4. Nos lotes de 22/10 são 18 objetos `Financeira`: 10 em
  `lote1_bancos` (bancos, seguradora, holdings de seguro) e 8 utilities em `lote2_energia`. Entram também as dos dossiês,
  com a lista completa gerada pelo script e registrada no relatório. (b) Comparar a mediana do ROE **real**
  (deflacionado pelo IPCA de cada ano) com o Ke real de 12,06%.
- **Critério.** **Aceita** se o `roe_lp` digitado diverge ≥ 1 p.p. do (a) em ≥ 2 empresas, **ou** se o sinal de
  (ROE − Ke) muda entre nominal e real em ≥ 2 empresas. **Refutada** se os dois testes passam em todas.
- Camadas 1 e 4 · Fases 2 e 4.

### H9 — O conservadorismo está empilhado
A taxa (Ke 12% real), o fluxo (mediana, OE com capex de manutenção, o menor ROIC), g = 0, IR 34% e o desconto do controlador
rebaixam o central, cada um por um lado. A régua ainda exige 30% de margem sobre o resultado.
- *Teste:* decomposição de Shapley de log(P/C) por ticker em 5 fatores (taxa, margem, g, alíquota, desconto). Ela é
  feita **duas vezes**, cada uma com uma referência "neutra" pré-registrada, e as duas são relatadas lado a lado:
  - **R-mercado** (o que o preço implica): Ke implícito no preço (DCF reverso); margem LTM; g declarado sem trava;
    alíquota mediana observada; desconto 0.
  - **R-fonte** (o que uma fonte A/B sustenta): Ke de Damodaran (rf local − spread de default + ERP madura + CRP, com β
    setorial de emergentes, da H5); margem do **ciclo completo**, de pico a pico identificado na série e não pela mediana
    fixa de 10 anos; g = taxa de reinvestimento × ROIC; alíquota marginal legal com crédito em VP; desconto 0.
  A R-mercado sozinha é circular, porque toma o preço como verdade. A R-fonte sozinha depende do que ainda está "a
  conferir". Fator sem fonte A/B na R-fonte fica no valor da casa e é marcado.
- **Critério.** É descritiva, não há aceitação por número. Relata-se a fração mediana de cada fator nas duas referências.
  "Empilhamento confirmado" se, nas **duas**, nenhum fator sozinho explica > 50% do log(P/C) mediano. Quando as duas
  divergirem no fator dominante, relata-se a divergência e não se conclui. É a base do item 6 da proposta.
- Camada 5 · Fase 2.

### H10 — Dado ausente vira zero em silêncio (bug)
Em `motor_nao_financeiras.py:176-177,214,250,273-277`, `:287` e `montar_series.py:48`, um campo crítico ausente vira 0 em
vez de NÃO CONCLUSIVO. No `:287` (`idade_e_fator`), sem imobilizado no LTM o capital a reposição fica igual ao contábil sem
aviso, e o ROIC a reposição (usado na trava da H1) deixa de ser o que diz ser. O mesmo acontece em `capital_reposicao` (`:297`).
- *Teste:* propriedade: remover qualquer campo crítico da série (caixa, dívida, PL, lucro, receita, D&A, imobilizado) → a palavra não pode
  ser BARATA, RADAR ou JUSTA e não pode haver número publicado como se fosse medido.
- **Critério.** **Aceita** (bug) se ao menos 1 remoção produzir palavra de decisão. **Refutada** se todas produzirem NÃO
  CONCLUSIVO ou erro explícito.
- Camadas 1 e 2 · Fase 2 (detecção) e Fase 3 (correção).

### H11 — Nas reguladas, o Ke da casa acima do WACC regulatório torna P/VP < 1 estrutural
O regulador fixa o retorno das elétricas (ANEEL) e do saneamento (ARSESP para SBSP3; ARSESP/AGEPAR/ARSAE para os
demais, conforme a concessão) num WACC regulatório real publicado em nota técnica. Se o Ke real da casa (12,06% ou mais,
somando o Hamada) for maior que o custo de capital que a tarifa remunera, então ROE regulado < Ke e o P/VP justificado
fica < 1 **por construção**. Isso vale para qualquer empresa do setor, por melhor que seja, e a palavra passa a refletir a
régua, não a empresa.
- *Teste:* (a) ler o WACC regulatório real vigente (antes e depois de impostos, e o custo de capital próprio implícito)
  na nota técnica de cada regulador. É fonte A, com número, data e página, conferida pelo `verificador-fonte`. (b) Para cada
  utility do hall (TAEE11, ISAE4, CPFE3, CMIG4, CPLE3, SAPR11, CSMG3, SBSP3 e as dos dossiês), comparar Ke real da casa ×
  Ke regulatório real, na mesma base (real, depois de impostos). (c) Comparar o P/VP justificado do motor com o P/VP
  implícito se o Ke fosse o regulatório.
- **Critério.** **Aceita** se o Ke da casa excede o Ke regulatório em ≥ 1,0 p.p. em ≥ 50% das reguladas com nota técnica
  lida. **Refutada** se a diferença for < 1,0 p.p. na maioria. Regulador sem nota técnica lida → "a conferir", fora da
  contagem. Aceitar H11 **não** implica adotar o Ke regulatório: o regulador fixa a remuneração da base, não o retorno
  que o acionista exige pelo preço. A H11 só mostra que, com essa régua, a palavra das reguladas já está decidida antes de
  olhar a empresa. O que fazer com isso vai para a proposta v3 (item 2), com fonte.
- Camadas 1 e 5 · Fases 2 e 5 (item 2).

## 3. Tolerâncias e limiares pré-registrados (Fases 2–4)
| Check | Limiar |
|---|---|
| Balanço: ativo − (passivo + PL) | ≤ 0,5% do ativo ou R$ 1 mil |
| DFC: caixa inicial + FCO + FCI + FCF + variação cambial − caixa final | ≤ 1% do caixa final ou R$ 1 mil |
| Lucro da DRE × lucro da DMPL | ≤ 0,5% |
| Dividendos da DMPL × DFC | ≤ 10% (diferença de competência × caixa é esperada; acima disso, bandeira) |
| Ações × LPA (lucro ÷ ações − LPA) | ≤ 2% |
| Ke nominal por ticker | ≤ 30% (acima disso, alarme de artefato) |
| Motor-sombra × motor, mesmos insumos | \|Δcentral\| ≤ 2%; acima disso, investigar e explicar |
| Insumo × RI/2ª fonte (LPA, VPA, DPA, DL, ações) | ≤ 2% |
| Propriedades (Hypothesis) | 0 contraexemplos em 500 exemplos por propriedade, seed fixa |
| Teste do oráculo (armadilhas) | pega 100% dos bugs plantados |
| Mutation score de base | só medir e registrar; a meta vem na Fase 4, depois da medida |

## 4. Critérios globais para uma v3 ser aceitável (antes de qualquer número da v3)
1. As camadas 1–5 estão verdes, todas as propriedades da §2 do prompt passam e nenhum Ke fica acima de 30%.
2. Cada mudança cita uma fonte A/B e o mestre que ela serve. Os conservadorismos ficam num lugar só, declarado (item 6).
3. **Discriminação histórica (Fase 7). Limite declarado:** o motor de hoje depende de cerca de 445 premissas digitadas
   (`roe_lp`, `g_real`, `g1_real`, `payout`, `kd_ri`, desconto, janela, fase de crédito…). Elas foram escritas em 2026, não
   existem nas datas passadas, e o portão do proxy (que tenta substituí-las pelo dado) já **falhou** (70,7% contra 80%;
   `docs/DECISOES.md` l.13). Rodar "a régua v3" no passado com premissas de 2026 é olhar para o futuro (look-ahead). Por
   isso fica pré-registrado:
   - **3a. Exigência de derivação.** Toda premissa que, no teste de sensibilidade de ±20% da Fase 5, **muda a palavra** de
     ao menos 1 ticker precisa ser derivada do dado PIT por regra escrita (ex.: `roe_lp` = mediana do ROE da CVM até a data;
     g = reinvestimento × ROIC até a data) para entrar na v3. Premissa que muda palavra e não pode ser derivada fica de fora
     da v3 ou entra como julgamento declarado. Nesse segundo caso, o ticker é excluído do teste histórico e o motivo é
     listado.
   - **3b. Escopo do critério histórico.** O critério de discriminação vale **para a régua v3 com premissas derivadas
     (3a)**, rodada no ledger PIT. Se a 3a não for cumprida para algum item, o critério histórico vale **só para o proxy**
     e é relatado como "evidência sobre o proxy, não sobre o motor". Nesse caso a validação do motor fica só com a parte
     prospectiva (§4.4–4.5).
   - **3c. Critério (só onde 3b permite).** Datas: fim de 2016, 23/03/2020, fim de 2022, fim de 2024. Se a fração de BARATA
     for 0 em **todas**, inclusive em mar/2020, a régua não discrimina e é **reprovada**. Se for > 50% em alguma data que
     não seja mar/2020, a régua é frouxa e também é reprovada. Antes de usar o proxy de novo, o portão dele (≥ 80% de
     concordância com o motor nos tickers atuais) precisa passar com as premissas derivadas da 3a. Sem isso, nada histórico
     vale.
4. **Relação com o retorno (Fase 7):** postos de P/C × retorno total em 3 anos com IC de Spearman < 0, relatado com o
   intervalo e deflacionado por 24 tentativas. Com poucas observações só se relata; não se conclui.
5. Probabilidade explícita por palavra no prospectivo, com Brier score. Só se relata até haver ≥ 4 rodadas vencidas.

## 5. Ainda a conferir (sem efeito até nota A/B)
Damodaran, *Country Risk* (edição 2025/26) e planilha `ctryprem` (jan/2026); spread e CRP do Brasil; ROIC divulgado pela
WEG; ROE recorrente do Itaú; Kerr 1998 (HARKing); Barr et al. 2015; Harvey, Liu & Zhu 2016; Bailey & López de Prado 2014.

## 6. Registro de tentativas (append-only)
| # | Data | Hipótese/item | Variante | Executada sobre | Resultado (resumo) | Commit |
|---|---|---|---|---|---|---|
| 0 | 22/10/2026 | baseline | sens.py, sens2.py (diagnóstico) | 38 tickers | reproduzido (§1) | 9caaf30 |
| 1 | 22/10/2026 | H1 (b) | **variante, conta 1/24:** trava "mesma base" (contábil × WACC nominal **e** reposição × WACC real) | 21 industriais | trava muda em 2 (ABEV3, WEGE3), \|Δcentral\| ≥ 10% em 0 → (b) não cumprido; (a) sem gabarito lido → **a conferir** | 9e9e8ac + `oraculo/hipoteses.py` |
| 2 | 22/10/2026 | H2 (a) | **variante, conta 2/24:** ponto fixo partindo de PL, valor de mercado e 3×PL | 21 industriais | RECV3 > 1% entre partidas; (b) caixa ↑ nunca baixa o central; (c) Ke > 30% em 4 → **aceita** | idem |
| 3 | 22/10/2026 | H3 | teste (não conta): elasticidades ±10% a Ke, fluxo e g; cosseno entre âncoras | 20 industriais, 17 financeiras | financeiras: 100% dos pares ≥ 0,95 (aceita); industriais: 0% ≥ 0,95 e nenhuma âncora < 0,80 na maioria (inconclusiva) → **mista** | idem |
| 4 | 22/10/2026 | H4 | **variante, conta 3/24:** rf e π de 15/10 (fonte A mais perto do preço; 22/10 não coletado), data do preço do lote | 39 dos lotes | Δπ −0,71 p.p., ΔKe −1,13 p.p.; LEVE3 e ISAE4 NÃO CONCLUSIVO → JUSTA → **aceita**; vértice da π no prazo da rf: a conferir (dado) | idem |
| 5 | 22/10/2026 | H5 | teste (não conta): ctryprem de 05/01/2026 (nota A) | — | Ke_D 12,40% × casa 12,06% (−0,34 p.p.) → **refutada (provisória**: método sem página do paper) | idem |
| 6 | 22/10/2026 | H6 | teste (não conta): ROIC pelo DFP, leitor próprio | WEGE3, LEVE3, B3SA3 | motor 14,6 / 11,7 / 0,0 p.p. abaixo da mediana 2023–25; RI da WEG não lido em fonte A → **a conferir** | idem |
| 7 | 22/10/2026 | H7 | teste (não conta): Mann-Kendall + BH q = 0,05 | 21 industriais | só WEGE3 significativa → **refutada**. A 1ª execução usou a margem ORDENADA (erro de código, não variante) e foi descartada | idem |
| 8 | 22/10/2026 | H8 | teste (não conta): ROE pelo DFP 2017–25 | 18 Financeira | roe_lp a ≥ 1 p.p. em 5 (BBSE3, BRSR6, CMIG4, CPFE3, CXSE3); sinal muda em 3 (CMIG4, ITUB4, PSSA3) → **aceita** | idem |
| 9 | 22/10/2026 | H9 R-mercado | **variante, conta 4/24:** Shapley com Ke implícito, margem LTM, g sem trava, alíquota mediana, desconto 0 | 18 industriais | taxa 76%, margem 23% → dominante taxa | idem |
| 10 | 22/10/2026 | H9 R-fonte | **variante, conta 5/24:** Ke de Damodaran (β = 1, marcado), alíquota 34%, desconto 0; margem e g da casa (marcados) | 20 industriais | taxa 98% → **empilhamento não confirmado** nas duas | idem |
| 11 | 22/10/2026 | H10 | teste (não conta): tira o campo de todos os períodos | 21 industriais | caixa 14, dívida 14, PL 9, D&A 18, imobilizado 16 com palavra de decisão; lucro e receita 0 → **aceita (bug)** | idem |
| 12 | 22/10/2026 | H11 | conferência de fonte (não conta) | 8 reguladas | nenhuma nota técnica lida no primário → **a conferir** | idem |
| 13 | 24/11/2026 | H2 (correção, emenda 3) | **variante, conta 6/24:** D/E a mercado (preço da data-base), D = dívida bruta com arrendamentos + outros passivos financeiros (= ponte), sem ponto fixo; Ke nominal > 30% → NÃO CONCLUSIVO | 21 industriais (3T26, preço de 19/11) | Ke > 30%: 5 → 1 (SMTO3 30,3%, D/E 2,18 a mercado); palavra muda só na SMTO3 (CARA → NÃO CONCLUSIVO); RANI3, SUZB3, SLCE3 seguem NÃO CONCLUSIVO por dispersão > 3, KLBN11 e RECV3 por EPV < 0 | B34 |

Nota das linhas 1–12: as variantes rodaram três vezes no mesmo código. As duas primeiras execuções quebraram antes de gravar (a
H7 com tipo do numpy; depois a pasta de saída inexistente). Como as variantes são determinísticas, cada uma conta uma vez.
Relatório: `docs/oraculo/hipoteses-2026-10-22.md` (e `.json`).

## 7. Emendas
1. **22/10/2026 — definições de relatório da camada 5, sem efeito em palavra.**
   - **Compounder:** mediana do ROIC real anual do motor (`roic_serie`) ≥ 10% e no máximo 2 anos < 5%, **ou** ROIC contábil
     atual ≥ 15%. A segunda via existe porque a série anual da WEGE3 sai com 1,2% em 2016 e < 10% até 2022, o que é suspeito
     pela H6. "Compounder caro" = compounder com P/C > 2.
   - **Ke implícito:** o `ke_implicito` do motor é **nominal** e é calculado ao preço do lote. A distância é medida como
     Ke nominal da casa − Ke implícito.
   - **Escala de ações:** quando lucro ÷ ações ÷ LPA ≈ 1000, o check vira `acoes_escala`. A série guarda ações em
     unidades para uns tickers e em milhares para outros: WEGE3 em unidades, KEPL3 e TAEE11 em milhares. O
     `lote4_saude_telecom.py:150` contorna isso com a heurística `< 1e7`. Fica como bandeira; a correção vai para a Fase 3.
   - **Ke acima de 30% na baseline:** KLBN11 64,7%, SUZB3 34,3%, SLCE3 31,3% e SMTO3 30,3% (RANI3 29,97%, logo abaixo) são
     alarmes conhecidos ligados à H2. Entram na lista de conhecidos do `oraculo/sanidade.py`, que é uma catraca e só encolhe.
2. **22/10/2026 — perfil das propriedades, limiar de escala de ações e alçada das armadilhas; escrita antes de rodar as
   armadilhas e as H1–H11, sem efeito em palavra.**
   - **Perfil das propriedades (§3, "500 exemplos").** Uma avaliação de industrial custa cerca de 0,2 s, ou 0,06 s sem os Ke e
     g implícitos, que não entram em central nem em palavra e por isso são trocados por `None` nas propriedades. Cada exemplo
     custa duas avaliações. Financeira: 500 exemplos sempre. Industrial: 12 exemplos na suíte do dia a dia (perfil curto) e
     500 só com `python -m oraculo --completo` (`ORACULO_PERFIL=completo`). O critério do §3 só conta como cumprido na
     rodada `--completo`. O perfil curto é regressão rápida.
   - **Ações do lote × DFP (camada 4, `acoes_lote`).** Até 2%: ok (o limiar de ações × LPA do §3). Acima disso: bandeira. Se
     a razão fica fora de [0,5; 2], é erro de escala (R$ mil × unidade) e vira falha quando o ticker tem palavra de decisão.
     A palavra é a que o motor dá na rodada, não a do hall.
   - **Alçada do automático nas armadilhas** (`docs/ORACULO.md` §2), decidida antes de medir. O automático é o portão
     inteiro da `VALIDACAO` §2: a suíte, com o golden regravado no worktree como um autor faria (a camada 0 não conta), mais
     o `python -m oraculo`. São dele as armadilhas de número (zero silencioso, real × nominal, sinal da DL, unidade das
     ações, régua). As de processo (premissa sem fonte, motivo do golden, variante fora do pré-registro) são só do agente.
   - **H10 em duas partes.** Os campos que já viram recusa explícita (lucro, receita) formam uma propriedade estrita: um
     zero novo neles quebra a suíte. Os outros ficam num xfail estrito com catraca (`H10_ABERTOS`), e o campo sai da lista
     quando a Fase 3 o fechar.
   - **Achado A1 (camada 2; não é hipótese testada).** Nos industriais, o desconto do controlador entra no E do ponto fixo
     do WACC (`estrutura_de_capital`) e volta como Ke maior, pelo Hamada, e como nota de qualidade diferente. Isso contraria
     o §5 do `01` ("o risco não volta a descontar retorno, nota ou veredito"). Fica como xfail estrito até a decisão do Frank
     na Fase 3. Nos lotes de hoje só um industrial tem desconto diferente de zero: a **PETR4**, que é JUSTA. O efeito na
     palavra dela é medido na Fase 3, como variante pré-registrada. Aqui nada muda.
   - **Contagem de tentativas (§0.4).** Entra no §6 toda execução das H1–H11. Conta no orçamento de 24 só a execução que
     calcula central ou palavra sob uma regra ou um dado alternativos (H1b, H2a, H4, H9). Teste de propriedade, conferência
     de fonte e estatística descritiva não contam.
3. **24/11/2026 — correção do H2 (Fase 5 item 2, só a alavancagem do Ke e os pesos do WACC); decidida pelo Frank pela fonte e
   pela lógica, escrita ANTES de calcular qualquer palavra sob a regra nova.**
   - **Regra escolhida (opção A).** Um D/E só, a valor de mercado, usado no prêmio de Hamada e nos pesos do WACC, **sem ponto
     fixo**: E = preço da data-base × ações (todas as classes; sem média de preço); D = a mesma dívida que a ponte do valor da
     firma desconta (dívida bruta com arrendamentos + outros passivos financeiros). A ponte soma o caixa. Fonte: Damodaran,
     *Investment Valuation* 2ª ed., cap. 8 pp. 21, 24, 47, 49–51 e cap. 15 p. 24 — nota B (edição de 2002; fichas em
     `docs/research/2026-11-24-ke-alavancagem.md`). Revisa o AUD-13 (E = valor da casa no ponto fixo).
   - **"Dívida líquida" sai** da Fase 5 item 2: a fonte recomenda dívida bruta ("using net debt ratios will overstate the value
     of riskier firms", cap. 8 p. 51).
   - **Sem teto na fórmula** (não há fonte A/B para o número). Ke nominal > 30% continua conferência: vira NÃO CONCLUSIVO, sem
     nova mudança de método.
   - **Efeito conhecido, aceito antes da tabela.** O central passa a depender do preço por um passo (sem laço): preço cai → D/E
     sobe → Ke sobe → valor justo cai. Esse erro joga contra comprar; é aceito (Frank, 24/11). O simétrico, declarado na
     proposta: preço sobe → D/E cai → valor justo sobe (menos conservador do lado da venda).
   - **Testes do H2 sob a regra nova.** (a) o Ke e os pesos não dependem do central (margem ±10% não muda Ke nem D/E) — o laço
     some por construção, então "pontos de partida" não se aplica; (b) caixa ↑ com dívida bruta igual não reduz o central;
     (c) Ke nominal ≤ 30% em todo o hall é conferência, não alvo. Mais um teste de coerência: o D do desconto (Hamada e pesos)
     é o mesmo D que a ponte subtrai, e o fluxo não desconta o arrendamento uma segunda vez.
   - **Achado A1** (desconto do controlador no E do ponto fixo) deixa de existir: o E não vem mais do central.
   - **Contagem (§0.4):** a execução da regra nova sobre o hall é tentativa e conta **6/24** (linha 13 do §6).
4. **24/11/2026 — medição, sem decisão: a direção do efeito declarada na emenda 3 está errada na maioria do hall.**
   - Medido com o preço × 0,7 / 1 / 1,3 (resto igual), regra da emenda 3: em 17 dos 21 industriais o central **sobe** quando o
     preço cai (o peso da dívida no WACC cresce e Kd × (1 − t) < Ke; esse canal vence a alta do Ke pelo Hamada). Seguem a direção
     declarada só B3SA3, LEVE3 e RANI3; RECV3 sem central. Preço −30% → central de +0,2% (ABEV3) a +14% (SUZB3).
   - O efeito real favorece comprar, o oposto da premissa da aceitação ("joga contra comprar"). Fica com o Frank; não é
     tentativa nova (não muda regra nem palavra).
5. **24/11/2026 — decisão do Frank sobre a emenda 4: mantém a opção A (correção da direção declarada).**
   - **A direção declarada na emenda 3 estava errada.** Lá: "preço cai → D/E sobe → Ke sobe → valor justo cai; joga contra
     comprar". Medido (emenda 4): é o **oposto** na maioria do hall — o efeito é **a favor da compra**, até +14% no central numa
     queda de 30% do preço (SUZB3). O erro foi da proposta, que olhou só o canal do Ke e não o dos pesos do WACC.
   - **Manter A não foi decisão tomada por resultado.** A foi escolhida pela fonte (Damodaran, cap. 8 p. 47: pesos a mercado),
     antes de qualquer tabela; a medição corrige a descrição do efeito, não a escolha. Nenhuma palavra muda em relação à tabela
     de 24/11.
   - **Teste:** "favorece comprar" não é propriedade desejada. O teste fixa a regra econômica — com Kd × (1 − t) < Ke, mais
     dívida no peso baixa o WACC — e o efeito medido fica como observação, não como alvo.
   - **Remédio para depois, fora desta tentativa:** custo da dívida que sobe com a alavancagem (`docs/BACKLOG.md` B35), com
     hipótese pré-registrada antes de rodar.
6. **24/11/2026 — correções de fato da emenda 4/5 e da linha 13 do §6, apontadas pelo agente `oraculo` (parecer BLOQUEIA); sem
   decisão nova.**
   - **Tamanho do efeito do preço:** o máximo medido numa queda de 30% é **+18,8% na KLBN11** (SUZB3 +14%, PETR4/PRIO3/UNIP6 ~+7%), não
     "+14%" como nas emendas 4 e 5: a medição foi lida só até a SUZB3.
   - **Palavras:** além da SMTO3 no hall, o H2 muda o recálculo do dossiê **ALLD3 (15/10) de BARATA → RADAR** (dispersão 2,17 > 1,8);
     a linha 13 do §6 ("palavra muda só na SMTO3") está incompleta. Decisão do Frank no `09` (aceita RADAR no recálculo; o veredito
     salvo fica).
   - **Prova de ordem:** a emenda 3 e a linha 13 entraram no **mesmo commit** (c108bce) que o motor e o golden. A ordem dentro da
     sessão foi emenda 3 → motor → tabela, mas o git não a prova; a regra do §0.1 pede o registro antes da execução, e a prova
     independente disso não existe. Declarado; aceite do risco é do Frank.
   - **"Pronto quando" do B34:** escrito em 23/11 como "Ke ≤ 30% em todo o hall"; o Frank o redefiniu em 24/11, antes de qualquer
     tabela, como conferência ("se algum passar, vira NÃO CONCLUSIVO, sem mexer de novo no método"). Fica registrado aqui.
7. **24/11/2026 — aceite do risco pelo Frank, trava de ordem pelo git e congelamento até o hold-out; escrita e commitada SOZINHA,
   antes do commit que corrige o motor (Graham).**
   - **Aceite por escrito (Frank, 24/11, resposta ao parecer BLOQUEIA):** aceita o risco de a emenda 3 não ter prova de ordem no
     git (mesmo commit c108bce do motor e do golden) e de a opção A ter sido mantida depois de a premissa da aceitação cair.
   - **Registro honesto da ordem.** A opção A foi escolhida pela fonte, **antes** da tabela de palavras. A decisão de **manter** A,
     depois de a premissa ("joga contra comprar") se mostrar falsa (emenda 4), veio **depois** de ver a tabela e se apoia só na
     fonte (Damodaran, cap. 8 p. 47). Nenhuma compra nova surgiu: zero BARATA no hall antes e depois; as palavras que o H2 mudou
     só desceram (SMTO3 CARA → NÃO CONCLUSIVO no hall; recálculo do dossiê ALLD3 BARATA → RADAR). LEVE3 e PETR4 em RADAR vêm da
     gravação do 3T26 (23/11), antes do B34.
   - **Trava nova (vale daqui em diante; corte no commit b07482a).** Emenda do pré-registro vai num **commit próprio** — só
     arquivos `docs/PRE-REGISTRO-*.md` — **antes** do commit de motor, lote ou golden que a usa; esse commit cita "emenda N" na
     mensagem. O `python -m oraculo` confere pelo git (check `ordem`, bloqueante): commit que mistura pré-registro com outro
     arquivo, ou commit de motor/lote/golden que cita uma emenda que nenhum commit anterior (só de pré-registro) acrescentou,
     reprova.
   - **Graham (ressalva do parecer).** O fator f do Graham-BR e do Graham revisado usava o Ke **alavancado** da empresa; com o D/E
     a mercado, o preço vazava para eles (Graham-BR −8% e revisado −15% na SMTO3 com o preço −30%). O `01` §11 manda o Ke da casa
     ("Graham-BR ignora a estrutura de capital"). Correção de código para a regra escrita, não variante: Graham não é âncora,
     nenhum central nem palavra muda; **não conta** no orçamento (§0.4). O lucro normalizado (Klarman) e o Graham original não
     se mexiam com o preço (medido).
   - **Congelamento.** Antes de qualquer calibração nova, o método v2.7 fica congelado e roda num **hold-out** de 20 ações fora
     dos 41 do hall, que ninguém olhou; a lista é registrada (commit próprio, como esta emenda) antes de rodar (`docs/BACKLOG.md`
     B36).
   - **Financeiras.** Os VPA/LPA dos 10 bancos e seguradoras, digitados do 2T26 e usados com o preço de 19/11, entram na catraca
     de datas fixas (`tests/datas_fixas_catraca.json`, `contabil_digitado`), mesmo prazo: 31/01/2027 (B32). Limite conhecido até lá.
8. **24/11/2026 — hold-out B36: regra de escolha, lista das 20, ficha-padrão, protocolo e critério de "passou"; escrita e
   commitada SOZINHA, antes de rodar qualquer ação.** Método v2.7 congelado no commit d70abb7 (motor, doutrina e golden
   iguais aos do master e5ce4ef).
   - **Regra de escolha (mecânica, `ferramentas/holdout_b36/selecionar.py`, commit d70abb7, rodada uma vez em 24/11).**
     (1) T = 19/11/2026, último pregão do COTAHIST; ações e units do mercado à vista. (2) Liquidez = média do VOLTOT nos 250
     pregões até T, dia sem negócio = zero. (3) Um papel por CNPJ (o mais líquido) e as exclusões mecânicas da triagem: sem
     identidade na CVM, recuperação/falência (FCA + CODBDI), §8 (educação, AZUL, GOLL, IRBR), piso de liquidez. (4) ≥ 10
     exercícios de DFP visíveis na CVM em T, com demonstração no ZIP. (5) Fora, por CNPJ, o que gente já olhou: os 41 do
     golden, os 6 dossiês (ALLD3, BLAU3, CMIN3, FESA4, SHUL4, VLID3), a fila do `06` de 08/10 (20) e a triagem manual de
     07/09 (`NOTAS_06_ANTIGO`, 22). (6) As 20 mais líquidas; empate pela ordem alfabética. O seletor não lê preço, central,
     P/C nem Q1–Q5 (teste `test_holdout_b36_selecionar.py`). Funil: 351 linhas (uma por CNPJ, mais os tickers sem identidade); 124 abaixo do piso, 76 já olhadas, 39
     sem identidade, 35 com menos de 10 DFPs, 8 §8, 7 em recuperação; 62 elegíveis.
   - **Contaminação residual, declarada.** O `06` (saída de máquina) mostra o P/C proxy de ~150 tickers, entre eles parte
     destas 20; ninguém escolheu por ele, e a regra não o lê.
   - **Lista (ordem de liquidez, R$ mi/dia; setor da FCA):** 1 BPAC11 661,9 (bancos) · 2 EMBJ3 466,3 (máquinas e veículos) ·
     3 EQTL3 381,4 (energia elétrica) · 4 ENEV3 314,9 (energia elétrica) · 5 RADL3 223,2 (comércio) · 6 RAIL3 211,0
     (holding — transporte e logística) · 7 ENGI11 173,7 (holding — energia elétrica) · 8 CSAN3 169,5 (agricultura — açúcar e
     álcool) · 9 SMFT3 163,7 (lazer) · 10 MBRF3 162,3 (alimentos) · 11 CSNA3 102,8 (siderurgia) · 12 GOAU4 99,6 (holding —
     siderurgia) · 13 USIM5 96,8 (siderurgia) · 14 TEND3 88,6 (construção) · 15 NATU3 84,9 (higiene) · 16 MOVI3 78,0
     (transporte e logística) · 17 MRVE3 74,6 (construção) · 18 AZZA3 74,3 (vestuário) · 19 IGTI11 74,0 (holding — comércio,
     shoppings) · 20 BEEF3 73,5 (alimentos).
   - **Caminho por tipo, pelo setor da FCA (como o hall):** "Bancos" → `motor_financeiras.Financeira` perfil `banco`
     (BPAC11); setor com "Energia Elétrica" ou "Saneamento" → `Financeira` perfil `utility`, método de regulado do §11.2,
     igual ao `lote2_energia.F` (EQTL3, ENEV3, ENGI11); o resto → `motor_nao_financeiras.Industrial` pelo `dossie.gerar`
     (16). Holding ("Emp. Adm. Part.") roda pelo consolidado do seu setor, sem SOTP (limite declarado; o hall faz SOTP só na
     ITSA4); se o caminho falhar, conta como erro.
   - **Ficha-padrão, igual para todas (não se ajusta por ação).** Industrial: `ANOS` = os 10 últimos exercícios do DFP
     (2016–2025); perfil `ciclica` se o setor da FCA for siderurgia/metalurgia, agricultura, alimentos, papel e celulose,
     petróleo e gás, mineração ou química (CSAN3, MBRF3, CSNA3, GOAU4, USIM5, BEEF3), `servicos` no resto; `outras_liquidas`
     = sim e `g_real` = 1% (os do hall e dos dossiês); `desconto_controlador` pelo protocolo; cíclica **sem** normalização de
     preço própria (a CMIN3 tem; aqui fica como limite declarado). Financeira (banco e regulado): VPA, LPA, ROE atual e de 10
     anos, P/L histórico, DPA de 5 anos, JCP e anos pagos lidos **por código** da StatusInvest, como o `lote2_energia.F` faz
     no hall (nota C, declarada); payout = mediana de 5 anos desses dados, salvo política formal com fonte A/B achada pelo
     protocolo; solidez do regulado pela alavancagem da CVM (`lote2_energia.solidez`); notas qualitativas e prudencial do
     banco só pelo protocolo, senão vazias.
   - **Protocolo dos insumos (fixo).** Um subagente Sonnet por ação, teto de 25 chamadas, roteiro único: FRE 2026, IPE,
     estatuto e DFP 2025, nesta ordem. Pede os insumos do dossiê: M&A ruim, interferências, partes relacionadas ÷ receita,
     tag along, controlador discricionário, as 15 respostas de Fisher, o desconto de controlador (tipo, razão, cenários) e,
     nas financeiras, as notas qualitativas e o prudencial (CET1, inadimplência 90, cobertura). Só fonte A/B vale; o que não
     achar fica vazio (padrão do método). Desconto sem evidência A/B = `zero` com `SEM_RAZAO`, como 23 do hall.
   - **Classes de cada insumo, fixadas aqui:** **automático** = sai de CVM, B3, COTAHIST, StatusInvest ou da regra padrão por
     código, sem leitura (séries, FRE estruturado, proventos, notas mecânicas de moat/ciclo/gestão, R$ 1 retido da triagem,
     itens da ficha-padrão); **pesquisa** = valor digitado a partir de leitura com fonte A/B (insumo do subagente, correção de
     dado); **vazio** = não achado, ficou no padrão do método. "Digitada à mão" = pesquisa. A classe sai do código (de onde o
     valor veio), não de rótulo.
   - **Critério de "passou" (todos):** (1) rodam sem erro (sai palavra, NÃO CONCLUSIVO incluso) ≥ 16 de 20; (2) NÃO
     CONCLUSIVO, entre as que rodam, ≤ 6; (3) Ke nominal > 30% ≤ 2; (4) valor absurdo (central ≤ 0, P/C < 0,2 ou > 5) ≤ 2;
     (6) vazios por ação: mediana ≤ 50% dos insumos não automáticos do seu tipo; (7) tempo por ação (relógio, do cadastro
     ao veredito): mediana ≤ 20 min. **A linha (5) foi retirada antes de rodar (Frank, 24/11):** com ~22 insumos não
     automáticos por industrial e ~15 por financeira, "≤ 25 digitadas" passaria sempre. No lugar entra o **% de insumos
     automáticos por ação, relatado fora do critério**: mede a distância até "qualquer ação", não a qualidade do método.
     Também só relatados (§0.3): dispersão > 1,8×, P/C mediano contra o do hall, nº de BARATA, erros explícitos do motor e a
     tabela por ação automático × pesquisa × vazio.
   - **Eventos societários e previsões, escritos antes de rodar.** Fonte: títulos dos fatos relevantes do IPE 2017–2026 e
     tickers por CNPJ na FCA `valor_mobiliario` (CVM, nota A). O FRE estruturado (`fre_2026.zip`) não traz a seção de
     reorganizações; o texto do FRE não foi lido, e 2016 fica sem IPE no disco. Previsão = o que deve sair e por quê; o
     relatório compara previsto × observado.

     | Ação | Evento nos 10 anos (IPE/FCA) | Previsão | Por quê |
     |---|---|---|---|
     | AZZA3 | Incorporou Reserva (2020), Vicenza (2023) e o Grupo Soma (2024; nome Azzas 2154); código ARZZ3 → AZZA3; reorganização em 09/2026 | **NÃO CONCLUSIVO** | A janela de 10 anos mistura a Arezzo sozinha com a Arezzo + Soma: ações e receita real saltam em 2024, a diluição pesa na gestão e a margem mediana é de outra empresa |
     | NATU3 | Natura &Co (2019, Avon) e incorporação da Natura &Co pela Natura Cosméticos (06/2025); linha nova de NATU3 na FCA em 07/2025 | **valor absurdo** | DFP de 2016–24 é a operadora sem a holding; ações e preço de antes de 2025 são de outra entidade (NTCO3/NATU3): número por ação incoerente na janela |
     | MBRF3 | Marfrig consolida a BRF desde 2022 e a incorporou em 2025 (MBRF); código MRFG3 → MBRF3 | **NÃO CONCLUSIVO** (Ke > 30%) | Dívida alta com o D/E a mercado no Hamada (v2.7) e minoritários grandes até 2025 |
     | EMBJ3 | Código EMBR3 → EMBJ3; Eve (2022) segue consolidada com minoritários; cisão interna da Yaborã (2021) | **erro** | A série de preço do COTAHIST pelo código novo é curta: fechamento de fim de ano, "listado desde" e P/L histórico dependem do ticker |
     | CSAN3 (holding) | Reorganização com a Cosan Limited (2021), desdobramento (2021), Raízen por equivalência | **NÃO CONCLUSIVO** | Holding alavancada sem SOTP: dívida da holding + perdas da Raízen na equivalência derrubam o lucro normalizado e sobem o Ke |
     | GOAU4 (holding) | Nenhuma reorganização; consolida a Gerdau com minoritários grandes | **roda, sem absurdo** | O motor desconta os minoritários (AUD-15); sem SOTP não há desconto de holding, e a palavra deve ficar perto da GGBR4 do hall |
     | IGTI11 (holding) | 2021: a Jereissati (JPSA3, mesmo CNPJ) incorporou a Iguatemi e virou Iguatemi S.A. (IGTI11, unit) | **valor absurdo** | DFP de antes de 2021 é a holding com minoritários; preço e ações são de JPSA3 e depois da unit |
     | MOVI3 | Reorganização do grupo JSL (2020), incorporação da CS Frotas (2021), cisão de controlada (2024) | **NÃO CONCLUSIVO** (Ke > 30%) | Locadora com dívida alta e emissão de ações na janela |
     | ENEV3 | Incorporou a Parnaíba (2018), Focus (2022) e ativos do BTG (2024, com follow-on) | **valor absurdo** (P/C > 5) | O método de regulado vive de payout e DDM, e a Eneva quase não distribui |
     | BEEF3 | Mato Grosso Bovinos (2017), Athena Foods (2020), units BEEF11 (2025) | **NÃO CONCLUSIVO** (Ke > 30%) | PL pequeno diante da dívida: D/E a mercado alto |
     | RAIL3 | Incorporação de ações da Malha Norte (2023–25) | roda | Evento pequeno diante da base |
     | BPAC11 | Reorganização (2017), desdobramento (2021), incorporação de ações (2025); units sem ligação na FCA (`IDENTIDADE_MANUAL`) | roda (motor de banco) | Banco com dados da StatusInvest pelo mesmo código do hall |
     | ENGI11 | Incorporações entre controladas (2017–26) | roda (regulado) | Eventos internos ao grupo |
     | MRVE3 | Cisão da LOG (2018) | roda | A cisão encolhe a base no início da janela, sem quebra depois |
     | RADL3, TEND3, CSNA3, USIM5, SMFT3, EQTL3 | Só eventos pequenos ou desdobramentos nos títulos do IPE (SMFT3: mudança de controle em 2026) | roda | Sem quebra de base visível no IPE |
   - **Congelamento e consertos.** Ninguém ajusta motor, doutrina, golden, ficha-padrão nem protocolo durante a B36; falha
     de método vira item novo no BACKLOG, sem conserto. No piloto (as primeiras ações), consertar o **executor**
     (`holdout_b36/rodar.py`, cadastro, coleta) é permitido só se não tocar motor, ficha-padrão nem protocolo e se o teste de
     equivalência (ALLD3 pelo executor = `dossie.gerar`) seguir verde; cada conserto vai no `09` com o motivo.
   - **Conferência prospectiva (B38), registrada antes de rodar:** em **19/11/2027**, para cada uma das 20, retorno total de
     12 meses (19/11/2026 → 19/11/2027; preço do COTAHIST + proventos pela data-ex da B3) contra o Ibovespa (retorno total)
     e a NTN-B (IPCA+ do mesmo prazo, Tesouro), cruzado com a palavra da B36. Leitura pré-declarada: retorno excedente médio
     por palavra (CARA × não CARA), descritivo, sem teste de significância (n = 20); a média das 20 também é relatada como
     comparador (regra do B25). Não se antecipa a data.
   - **Orçamento (§0.4):** não conta como tentativa: não há variante de regra.
9. **25/11/2026 — B39: Ke da Mesa × Ke implícito do mercado — triangulação, protocolo e gatilho; escrita e commitada SOZINHA,
   antes de rodar qualquer conta.** Origem: hipótese do `docs/BACKLOG.md` B39 (commit 144c8b0, 24/11) com os acréscimos do
   Frank de 25/11. Nada da B39 foi rodado. Esta emenda **substitui** o teste e a regra de gatilho escritos no B39; ficam o
   X = 3 p.p., os dois sentidos e o motivo dos 3 p.p. (ruído de ~2 p.p. do Ke implícito; −3 p.p. sobem o valor perpétuo ~33%,
   mais de uma faixa da régua; 60% do prêmio fixo de 5 p.p.).
   - **Tudo em termos reais, com a mesma rf.** rf = Tesouro IPCA+ sem cupom com vencimento mais próximo de 10 anos, taxa de
     compra da manhã (Tesouro Transparente), e π = implícita da curva no mesmo prazo, como no DNA §1.1 — lidas uma vez, no dia
     da execução, e usadas nas três estimativas e no Ke da Mesa. O `01` §4 ainda usa o vértice mais longo no Ke; aqui o Ke da
     Mesa é refeito com o de 10 anos, para a diferença medir só o prêmio. Nominal → real sempre por (1 + x) ÷ (1 + π) − 1.
     **X = 3 p.p. passa a valer no Ke real** (no B39 era o nominal; a diferença é o fator 1 + π, ~0,15 p.p., abaixo do ruído).
     Preço, rf, π e balanço (último ITR/DFP na CVM) de uma data só, registrada.
   - **(i) Bancos** — os bancos do hall + BPAC11. Ke nominal = (ROE − g) ÷ (P/VP) + g, com **ROE normalizado = mediana de 10
     exercícios** (lucro do controlador ÷ PL médio do controlador, DFP da CVM), **não o LTM**; P/VP = preço do dia ÷ VPA do
     último balanço; g nominal = (1 + g real) × (1 + π) − 1, g real = 1% (o do B39). Banco com menos de 10 exercícios: mediana
     dos disponíveis, mínimo 5; abaixo, fora (declarado). Estimativa (i) = mediana dos bancos. **Sensibilidade (só relatada):**
     ROE LTM no lugar da mediana; g real 0% e 2%.
   - **(ii) Ibovespa agregado — princípio do CAPE (Shiller).** Componentes da carteira teórica do Ibovespa (B3) na data. Para
     cada um, lucro líquido do controlador dos 10 últimos exercícios (DFP), levado a R$ de hoje pelo IPCA (SGS 433) e tirada a
     **média de 10 anos** (mínimo 5 exercícios; abaixo, fora — declarado), **não o lucro de um ano**. E10 = soma das médias;
     P = soma dos valores de mercado (preço do dia × ações de todas as classes). Ke real implícito = E10 ÷ P: o EPV reverso
     (valor = lucro normalizado ÷ Ke, sem crescimento), o mesmo princípio da âncora EPV da Mesa. Viés declarado: só os
     componentes de hoje (sobrevivência). **Sensibilidade (só relatada):** sem PETR3/PETR4 e VALE3; lucro LTM; Gordon com o
     payout mediano de 10 anos do agregado e g real 0/1/2% [Ke = payout × E10 × (1 + g) ÷ P + g]. Fonte do princípio: Campbell
     & Shiller (1998), *Journal of Portfolio Management* 24(2), e Shiller, *Irrational Exuberance* — **fonte a abrir**; nota B
     só depois de aberta.
   - **(iii) rf + prêmio total do Brasil (Damodaran).** ERP total do Brasil (maduro + risco-país) e spread de default soberano
     (s) da tabela `ctryprem` de jan/2026 (Damodaran, NYU Stern; página salva com a data; **fonte a abrir**, nota B quando
     aberta). Ke nominal R$ = n − s + ERP, n = (1 + rf) × (1 + π) − 1; Ke real = (1 + Ke nominal) ÷ (1 + π) − 1. **Por que
     tirar s:** o método do Damodaran tira o spread de default da taxa do título soberano em moeda local antes de somar o ERP
     total — o risco-país já está dentro da NTN-B e de novo no CRP, e sem o desconto conta duas vezes (*Country Risk:
     Determinants, Measures and Implications*, edição 2025 — a abrir; se o texto aberto disser outra coisa, vale o texto e o
     desvio vai ao relatório). **Sensibilidade (só relatada):** sem tirar s (rf real da NTN-B + ERP total, a forma literal).
   - **Ke da Mesa de cada comparação (rf de 10 anos nos dois lados).** (i): rf + 5 p.p. (prêmio fixo das financeiras, `01` §4).
     (ii) e (iii) medem o mercado inteiro: rf + o prêmio da Mesa aplicado ao índice = média dos prêmios dos componentes
     ponderada pelo valor de mercado — 5 p.p. nas financeiras; 5 × [1 + (1 − 0,34) × D/E] nas demais, D/E a mercado na regra da
     v2.7 (dívida bruta + arrendamentos + outros passivos financeiros do último balanço ÷ valor de mercado do dia). t = 34% para
     todos (simplificação declarada: o motor usa a perpétua de cada uma; com 34% o prêmio sai no mínimo e o Ke da Mesa erra
     para baixo — o lado de **não** disparar quando o Ke da Mesa é alto demais).
   - **Regra de gatilho (escrita antes de rodar).** Δₖ = Ke real implícito ₖ − Ke real da Mesa ₖ, k = i, ii, iii. **Dispara se
     |mediana(Δᵢ, Δᵢᵢ, Δᵢᵢᵢ)| > 3 p.p.**, nos dois sentidos. Estimativa que não sai (insumo sem fonte A/B; menos da metade do
     valor de mercado do índice com 5 exercícios) não é trocada por outra: com 2 que saem, vale a mediana das 2 (a média), e o
     relatório diz qual faltou; com menos de 2, a B39 fica **NÃO CONCLUSIVA** e nada muda. Sensibilidades não mudam o gatilho;
     vão ao lado, com a direção de cada uma. **Dispara** → o nível do Ke/prêmio entra na calibração (B35, com a B46), tentativa
     contada no orçamento de 24 (§0.4), e o prêmio p do DNA §1.1 sai dessa calibração. **Não dispara** → o Ke fica, com este
     motivo, e a causa do "tudo CARA" se procura em outra camada (âncoras, normalização; DNA, causas b–d).
   - **Insumos e execução.** Cada número com fonte e data: CVM DFP/ITR, carteira teórica da B3, Tesouro Transparente, IPCA SGS
     433 (nota A); Damodaran e Shiller (nota B depois de abertos). Nenhum número digitado sem fonte. Script em `ferramentas/`
     com teste, saída em JSON e relatório gerado só do JSON (como o da B36), registrado no `09`.
   - **Congelamento:** motor, doutrina e golden não mudam por causa da B39 antes do relatório.
   - **Orçamento (§0.4):** a medição não conta como tentativa (não há variante de regra); a calibração que ela disparar, sim.
10. **25/11/2026 — B39: correção de citação e de atribuição da emenda 9, depois de abrir as fontes; escrita e commitada SOZINHA,
   antes de rodar qualquer conta.** A conferência item por item está em `docs/b39/FONTES-B39.md`. Nada muda em conta,
   insumo, sensibilidade ou gatilho.
   - **(iii) Fonte do "tirar s".** O paper "2025 Edition" não está aberto ao público (o `CountryRisk2025.pdf` do site são os
     slides; o SSRN recusou o acesso). Valem os textos abertos: *Country Risk … The 2024 Edition*, p. 101 e Tabela 30
     ("subtracting that default spread from the government bond rate to get to a risk-free rate"; real 11,83% − 2,83% = 9,00%),
     e *What is the riskfree rate?* (dez/2008), "The Solution" (o risco "may end up being double counted"). Nota B nos dois.
     A regra da emenda 9 confere. A `ctryprem` de 5/1/2026 confere: Brasil Ba1, s = 2,13% ("Adj. Default Spread"), ERP total
     = 7,47% (CRP 3,24% + maduro 4,23%). Nota B.
   - **(iii) Título indexado.** O Damodaran não trata título indexado de governo com risco de default. Levar a NTN-B a
     nominal (n) e tirar s é extensão da Mesa, coerente com a regra, e fica declarado assim.
   - **(ii) Atribuição.** De Campbell & Shiller vem só a **construção** do E10 (média de 10 anos dos lucros reais ÷ preço
     real; mínimo de 5 pela citação de Graham & Dodd, 1934, p. 452). A fonte aberta é o NBER WP 8221 (2001), a atualização do
     artigo de 1998 (nota B). Do artigo de 1998 só a referência foi conferida, e o *Irrational Exuberance* não foi aberto.
     Lá o P/E10 é preditor em regressão; o texto **não** diz que E10/P seja o retorno esperado. A leitura "Ke real = E10 ÷ P"
     é o EPV reverso da Mesa (âncora EPV do `01`), com o viés de quem ignora o crescimento: se o crescimento cria
     valor (retorno sobre o reinvestido > Ke), o E10/P **subestima** o Ke (a sensibilidade de Gordon da emenda 9 mostra o
     tamanho).
   - **Sem mudança (já literal na emenda 9):** com 2 estimativas, vale a média das 2. Gordon do banco todo em nominal e
     depois para real. Agregado do índice = Σ E10 ÷ Σ valor de mercado, nunca a média dos E/P individuais.
11. **25/11/2026 — B39: errata de coerência da estimativa (i), pelo princípio "tudo real" da emenda 9; escrita e commitada
   SOZINHA, antes de recalcular.** A emenda 9 manda tudo em termos reais com a mesma π, e a (i) misturava duas inflações. O
   ROE mediano é histórico (2016–2025, IPCA médio de ~5% a.a.), e o g nominal usava a π futura da ETTJ (7,17%). Isso supõe uma
   queda de ~2 p.p. no ROE real e saía como sinal: prêmio implícito dos bancos de −0,44 p.p., um Ke abaixo da rf real. Não é
   escolha nova de método; é a correção da mistura.
   - **Correção:** ROE real de cada exercício = (1 + ROE nominal) ÷ (1 + IPCA do próprio ano) − 1, com o IPCA de jan–dez do
     ano (produto das variações mensais da SGS 433, nota A). ROE normalizado = mediana dos ROE reais (os mesmos 10 exercícios,
     mínimo 5). Gordon todo em real: **Ke real = g real + (ROE real − g real) ÷ (P/VP)**, g real = 1%, P/VP do mesmo jeito.
     Sensibilidades iguais (g real 0% e 2%), e o ROE LTM real usa o IPCA dos mesmos 12 meses.
   - **Nada mais muda:** (ii), (iii), o Ke da Mesa, X = 3 p.p. e a regra do gatilho são os da emenda 9.
   - **Versão antiga mantida:** o relatório mostra as duas versões da (i) e o gatilho nas duas, lado a lado. O que vale é a
     desta emenda.
   - **Leitura pré-declarada:** se a mediana corrigida ficar com |valor| ≤ 3 p.p., o resultado é "não dispara; indício só no
     Ibovespa". A B35/B46 continua como hipótese, sem prioridade de calibração.
   - **Orçamento (§0.4):** não conta como tentativa (correção de coerência, sem variante de regra).
12. **25/11/2026 — B46: Ke > 30% nas muito alavancadas — hipótese "separar a dificuldade" (Damodaran, 2009), regra,
   critério e previsões; escrita e commitada SOZINHA, antes de rodar a variante.** Origem: `docs/BACKLOG.md` B46 (falha da B36:
   CSNA3 62,2%, MOVI3 61,9%, BEEF3 48,5%; depois da B40, CSAN3 38,8% e MRVE3 32,3%). Autorizada pelo Frank sem a B35
   (`docs/PENDENTE-FRANK.md` #12). Fontes, trechos e notas: `docs/b46/FONTES-B46.md`. Origem exploratória (§0.2): a hipótese
   nasceu de olhar as 5 ações; elas **descrevem** a falha e não provam o conserto (a prova é o HOLD-OUT 2, DNA §5).
   - **Mecanismo.** O motor avalia a empresa como **continuidade** (margem de meio de ciclo, perpetuidade) e desconta essa
     perpetuidade com o D/E a mercado do preço deprimido. Damodaran (*Valuing Distressed and Declining Companies*, 2009, p. 14)
     chama isso de "internally inconsistent"; a receita dele (p. 37–39) é separar: valor = continuidade × (1 − π) + venda forçada
     × π, com a continuidade a um D/E sustentável e π a probabilidade de calote (Tabela 5, p. 41–42, de Altman 2007). O Hamada
     do motor ainda supõe dívida sem risco (Damodaran, *Investment Valuation* 2ª ed., cap. 8 p. 20, nota 8), enquanto o WACC
     cobra a mesma dívida a Kd de CC (27,9% em MOVI3 e BEEF3, acima do próprio Ke desalavancado).
   - **Opções vistas antes de qualquer tabela; escolha do `senior`: B.** A — Conine (β_D > 0): cai porque o β_D não tem fonte
     aberta (pelo spread do motor, β_D > 1 em CC; a tabela de Schaefer & Strebulaev não foi aberta). **Contaminação
     declarada:** o autor estimou de cabeça a A com β_D ~0,3 e viu 4 das 5 seguirem > 30% antes de escrever esta emenda.
     B' — B só nas sobrealavancadas: degrau no limiar sem fonte. C — Hamada "não se aplica" com rating ≤ B-: só esconde a linha
     "Ke > 30%" do M1.
   - **Regra da variante (B, uma regra para todo industrial; o motor não muda nesta tentativa).**
     (1) **Continuidade:** D/E_cont = min(D/E a mercado, D/E da indústria), um D/E só no prêmio de Hamada e nos pesos do WACC
     (regra da emenda 3). D/E da indústria = D/(D+E) da indústria em Damodaran, `waccemerg.xls` (Emerging Markets, 05/01/2026;
     dívida com arrendamentos ÷ dívida + valor de mercado, a definição do motor), levado a D/E. Indústria pelo `indname.xls` do
     Damodaran: o ticker; senão a mesma raiz de 4 letras com indústria única; senão **não avaliado** (razão no relatório, sem
     trocar por outra regra). A ponte segue subtraindo a dívida real; o Kd fica o de hoje (B35 fora — conservador).
     (2) **π, duas estimativas:** (i) rating sintético da cobertura normalizada (a conta do `custo_divida`, `credito.py`,
     calculada também quando há `kd_ri`; dívida > 0 sem juros → não avaliado) → Tabela 5; (ii) Z'' de emergentes do motor
     (`altman_z2`, mesmo período do `avaliar`; campo ausente → não avaliado) → rating equivalente pela coluna **2013** da tabela
     "US Bond Rating Equivalents Based on Z''-Score Model" (Altman, *50 Years of Altman Z-Score*, slide 26; a mais recente e a
     única monotônica): a melhor classe cuja mediana ≤ Z''; abaixo de 0,05 → CC/D. Classe sem linha na Tabela 5 → a pior
     seguinte que existe (AAA/AA+ → AA, AA/AA- → A+, BBB+ → BBB, BBB- → BB, BB+ → BB, BB- → B+, CCC+ → CCC, CCC- → CC); D e
     CC/D → π = 1. **π = média das duas**; com uma só, vale a única, marcada, e ela não conta como concordante no C3. Agência
     (3ª estimativa sugerida pelo `senior`): fora, sem fonte A mecânica — declarado. A (ii) não usa juros: a diferença (i) × (ii)
     mede o viés de dividir o lucro por juros nominais em R$ numa tabela de empresas dos EUA (hipótese do `senior`).
     (3) **Acionista:** cada âncora de continuidade (DCF, EPV, Owner Earnings) × (1 − π); o valor de reprodução (de ativo, não
     de continuidade) fica fora do π. Ramo de dificuldade = 0. **Direção nos dois sentidos:** fica acima da fórmula literal do
     Damodaran quando a venda forçada é menor que a dívida (lá o acionista sai negativo) e abaixo quando é maior; e a Tabela 5
     mede calote, não fechamento ("Many firms continue to operate as going concerns after default", p. 42), o que puxa o π
     para cima (conservador).
     (4) **Vieses declarados:** D/E sustentável desde t = 1, sem trajetória (a p. 38–39 diz que isso superestima a
     continuidade); o calote entra duas vezes (Kd de CC no WACC + π), o que é conservador; o relatório separa o efeito de cada
     parte. CSAN3 (holding) cai em "Retail (Automotive)": classificação duvidosa, prevista aqui e não corrigida depois.
   - **Critério (sobre o conjunto de desenvolvimento: industriais do hall, os 6 dossiês e os industriais da B36).**
     **C1 — conferência:** o Ke da variante de cada ticker = (1 + rf real + 5 p.p. × [1 + (1 − t) × D/E_cont]) × (1 + i) − 1
     recalculado à parte (aqui i = inflação implícita da curva, 7,17%; no resto desta emenda π é a probabilidade de calote); π = Tabela 5 pela classe; cada âncora de continuidade do modo completo = a do modo "só D/E" × (1 − π)
     e a reprodução igual. **C2 — propriedades**, choque fixo: (2a) no grupo com D/E a mercado ÷ 1,3 > D/E da indústria (fica
     acima do limite nos dois choques), preço × 0,7 e × 1,3 mudam o central em no máximo 0,5%; (2b) nesse grupo, dívida bruta
     +10% com juros +10% (caixa e preço fixos) nunca sobe o central; abaixo do limite a direção não é prevista (efeito H2, o
     Kd não reage) e é só relatada; (2c) π não cai com rating pior (nas duas escalas). **C3 — π mensurável:** |π(i) − π(ii)|
     ≤ 20 p.p. (≈ uma faixa da régua, que tem faixas de 0,20 no P/C) em ≥ 2/3 dos industriais avaliados com D/E a mercado >
     D/E da indústria; ticker desse grupo com uma estimativa só **fica no denominador como não concordante**. **C4:** zero "não avaliado" silencioso; erro novo (ex.: dívida sem juros com `kd_ri`) listado com razão.
   - **O que cada linha prova (ajuste do Frank, 25/11):** C1 e C2 são **conferência de mecânica** (o C2a passa por construção
     no grupo acima do limite); **só o C3 testa a hipótese**. "PASSA" = mecânica certa + π mensurável, **não** "valor certo";
     a prova continua sendo o HOLD-OUT 2.
   - **Leitura pré-declarada:** C1–C4 cumpridos → **PASSA** → proposta ⏸ ao Frank (implantar é mudança de doutrina; prova no
     HOLD-OUT 2). C1 falha, C2 falha fora do previsto ou C4 falha → **FALHA** (a variante não sai). C3 não cumprido → **NÃO
     CONCLUSIVA**: o π não é identificável com as fontes de hoje; nada a implantar, a B46 segue aberta com o motivo. **FALHA
     prevalece sobre NÃO CONCLUSIVA** quando as duas ocorrem.
   - **Só relatado (§0.3):** nº de Ke > 30% (quase por construção; não é critério), palavras, P/C mediano, nº de BARATA,
     Δcentral por ticker separado em parte do D/E e parte do π. **O relatório mostra o hall dos lotes do motor** (39: 21
     industriais + 18 financeiras e reguladas do motor de financeiras, em que a variante não se aplica; EGIE3 e ITSA4, que
     estão no `hall.json` mas não nos lotes de `oraculo/sanidade.py`, ficam fora e o relatório diz isso): palavras que mudariam e Δcentral por ticker nas duas partes; ticker do hall com palavra mudada vai ao
     `docs/PENDENTE-FRANK.md` junto com a proposta (ajuste do Frank).
   - **Insumos fixados antes de rodar** (motor de hoje, mercado de 19/11/2026: rf real 7,56%, π 7,17%). Formato: ticker —
     indústria (D/E da indústria) · D/E a mercado · rating (i). O Z'' e o π (ii) **não** foram calculados antes deste commit
     (o C3 fica cego).
     Hall: ABEV3 Beverage (Alcoholic) (0,026) · 0,01 · AAA; B3SA3 Financial Svcs. (Non-bank & Insurance) (1,166) · 0,21 · A-;
     FLRY3 Healthcare Support Services (0,616) · 0,55 · BB; HYPE3 Drugs (Pharmaceutical) (0,106) · 0,50 · B+; KEPL3 Machinery
     (0,122) · 0,30 · A-; LEVE3 Auto Parts (0,184) · 0,33 · AAA; PRIO3 Oil/Gas (Production and Exploration) (0,315) · 0,51 · A;
     RANI3 Packaging & Container (0,421) · 1,39 · CCC; RECV3 Oil/Gas (Production and Exploration) (0,315) · 1,12 · C; SLCE3
     Farming/Agriculture (0,578) · 1,33 · B+; SMTO3 Food Processing (0,380) · 2,18 · BB; SUZB3 Paper/Forest Products (1,011) ·
     1,54 · BB+; TIMS3 Telecom (Wireless) (0,300) · 0,30 · BB+; UGPA3 Retail (Automotive) (0,745) · 0,59 · B+; VBBR3 Retail
     (Automotive) (0,745) · 0,56 · B; VIVT3 Telecom. Services (0,326) · 0,19 · A-; WEGE3 Electrical Equipment (0,161) · 0,02 ·
     AAA; **sem indústria no indname (não avaliados):** GGBR4, KLBN11, PETR4, UNIP6. Dossiês: ALLD3 Computer Services (0,102) ·
     0,88 · A; BLAU3 Drugs (Biotechnology) (0,084) · 0,34 · A-; CMIN3 Steel (0,509) · 0,82 · AA; VLID3 Publishing & Newspapers
     (0,107) · 0,51 · BB; **sem indústria:** FESA4, SHUL4. B36: EMBJ3 Aerospace/Defense (0,120) · 0,16 · CCC; RADL3 Retail
     (Special Lines) (0,195) · 0,37 · BBB; RAIL3 Transportation (Railroads) (0,376) · 1,05 · BB; CSAN3 Retail (Automotive)
     (0,745) · 5,14 · B+; SMFT3 Recreation (0,236) · 1,38 · C; CSNA3 Steel (0,509) · 11,75 · B-; MOVI3 Transportation (0,588) ·
     10,09 · CC; MRVE3 Homebuilding (0,704) · 3,31 · CCC; AZZA3 Apparel (0,260) · 1,30 · BBB; BEEF3 Food Processing (0,380) ·
     7,88 · CC; **sem indústria:** GOAU4, USIM5; **erro no motor de hoje (fora, com a razão):** MBRF3 (capital no FRE), TEND3 e
     NATU3 (incorporação, B41), IGTI11 (provento repetido, B43).
   - **Previsões (escritas antes de rodar).** Ke nominal da continuidade (à mão, t do motor): CSNA3 22,4% · MOVI3 23,0% · BEEF3
     22,0% · CSAN3 23,3% · MRVE3 23,1%; π (i) = 42,12% · 66,6% · 66,6% · 28,25% · 59,02%. Nenhum industrial avaliado fica com Ke
     > 30% (por construção). C1, C2a, C2b e C2c passam. **C3: sem confiança; inclino a "não cumprido"**: o rating (i) dá CCC à
     EMBJ3 e C à RECV3 e à SMFT3, e a hipótese do `senior` (juros nominais em R$) diz que o (i) sai pior que o (ii) na maioria;
     se for assim, a leitura é NÃO CONCLUSIVA. Direção esperada das palavras: o D/E da indústria sobe o central da maioria
     das sobrealavancadas e o π o derruba onde o rating é B ou pior; o saldo por ticker não é previsto.
   - **Execução:** `ferramentas/b46/` (`calculo.py` puro, com teste de esperado à mão; `rodar.py` com a variante por
     `mock.patch`, como `oraculo/hipoteses.py`; `relatorio.py` gera `docs/b46/B46-2026-11.md` só do JSON). Motor, doutrina e
     golden não mudam.
   - **Orçamento (§0.4):** a execução da variante sobre o conjunto de desenvolvimento conta **7/24** (linha 14 do §6, escrita
     depois de rodar).
