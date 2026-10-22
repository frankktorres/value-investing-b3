# Pré-registro — validação e recalibração do motor (doutrina v3)

Aberto em 22/10/2026 (Fase 0 de `docs/PROMPT-ORACULO-E-CALIBRACAO.md`). Nenhuma palavra, central, golden ou doutrina mudou.
Este arquivo é **append-only** depois do "ok" do Frank: hipótese, teste e critério não se reescrevem; correção entra como
emenda datada no fim (§7), com o motivo, e conta como tentativa nova.

## 0. Regras do pré-registro
1. **Antes de rodar.** Toda variante de regra testada (fórmula, premissa, régua) entra aqui com hipótese, teste e critério
   de aceitação **antes** da primeira execução. Variante sem linha no §6 não vale como evidência.
2. **Origem exploratória declarada.** H1–H10 nasceram de olhar os números do diagnóstico de 22/10 (HARKing, Kerr 1998).
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
- *Teste:* (a) teste especificado (camada 1). Num caso sintético com inflação π, uma empresa com ROIC real = WACC real + 3 p.p. precisa
  ser classificada "cria valor" pelas duas versões coerentes (real × real; nominal contábil × nominal). Rodar a função
  atual. (b) No hall, contar os tickers cuja trava muda entre a regra atual e a regra real × real e medir a variação do
  central.
- **Critério.** H1 é **aceita** se (a) a regra atual classifica errado o caso sintético **e** (b) a trava muda em ≥ 3
  tickers, com |Δcentral| ≥ 10% em pelo menos 3. É **refutada** se (a) passa, ou se (b) dá < 3 tickers.
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
- *Teste:* Mann-Kendall nas margens de 10 anos de cada industrial (α = 0,05). Nos tickers com tendência significativa,
  comparar m50 com a mediana dos 3 últimos anos.
- **Critério.** **Aceita** se ≥ 3 tickers não cíclicos têm tendência positiva significativa **e** m50 ≥ 2 p.p. abaixo dos 3
  últimos anos. **Refutada** se < 3. A escolha da normalização nova **não** sai daqui: sai da camada 6 (Fase 7).
- Camada 5 · Fase 2 (relatório) e Fase 5 (item 4).

### H8 — O ROE de longo prazo dos bancos está desalinhado do Ke
O `roe_lp` é digitado (ITUB4 17,58%) e comparado com o Ke **nominal** de 19,3%, que embute π de 6,46%. Isso dá P/VP < 1 por
construção para banco de ROE de 20% ou mais.
- *Teste:* (a) recalcular o ROE anual a partir da CVM (lucro do controlador ÷ PL médio) e conferir o `roe_lp` digitado
  (camada 4). (b) Comparar a mediana do ROE **real** (deflacionado pelo IPCA de cada ano) com o Ke real de 12,06%.
- **Critério.** **Aceita** se o `roe_lp` digitado diverge ≥ 1 p.p. do (a) em ≥ 2 bancos, **ou** se o sinal de (ROE − Ke)
  muda entre nominal e real em ≥ 2 bancos. **Refutada** se os dois testes passam.
- Camadas 1 e 4 · Fases 2 e 4.

### H9 — O conservadorismo está empilhado
A taxa (Ke 12% real), o fluxo (mediana, OE com capex de manutenção, o menor ROIC), g = 0, IR 34% e o desconto do controlador
rebaixam o central, cada um por um lado. A régua ainda exige 30% de margem sobre o resultado.
- *Teste:* decomposição de Shapley de log(P/C) por ticker em 5 fatores. Cada fator vai do valor da casa ao valor
  "neutro" pré-registrado: Ke implícito no preço; margem LTM; g declarado sem trava; alíquota mediana observada; desconto 0.
- **Critério.** É descritiva, não há aceitação por número. Relata-se a fração mediana de cada fator. "Empilhamento
  confirmado" se nenhum fator sozinho explica > 50% do log(P/C) mediano. Base para o item 6 da proposta.
- Camada 5 · Fase 2.

### H10 — Dado ausente vira zero em silêncio (bug)
Em `motor_nao_financeiras.py:176-177,214,250,273-277` e `montar_series.py:48`, um campo crítico ausente vira 0 em vez de
NÃO CONCLUSIVO.
- *Teste:* propriedade: remover qualquer campo crítico da série (caixa, dívida, PL, lucro, receita, D&A) → a palavra não pode
  ser BARATA, RADAR ou JUSTA e não pode haver número publicado como se fosse medido.
- **Critério.** **Aceita** (bug) se ao menos 1 remoção produzir palavra de decisão. **Refutada** se todas produzirem NÃO
  CONCLUSIVO ou erro explícito.
- Camadas 1 e 2 · Fase 2 (detecção) e Fase 3 (correção).

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
3. **Discriminação histórica (Fase 7):** a régua v3 roda no ledger PIT em 4 datas (fim de 2016, 23/03/2020, fim de 2022, fim
   de 2024). Se a fração de BARATA for 0 em **todas**, inclusive em mar/2020, a régua não discrimina e é **reprovada**. Se
   for > 50% em alguma data que não seja mar/2020, a régua é frouxa e também é reprovada.
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

## 7. Emendas
(nenhuma)
