# DOUTRINA — Value Investing aplicado à B3
*Versão 2.6.1 · 21/10/2026 · documento de referência permanente do projeto*

---

## 1. A pergunta que governa tudo

> **A empresa gera retorno sobre o capital acima do custo desse capital, de forma repetível, e eu consigo comprá-la por menos do que ela vale?**

Se a resposta à primeira metade é não, nenhum múltiplo baixo salva. Se a resposta à segunda metade é não, nenhuma qualidade salva. As duas metades são independentes e ambas são obrigatórias.

---

## 2. Os cinco filtros

**Entrada no hall: 3 dos filtros 1 a 4.** O filtro 5 (preço) **não decide quem está no hall — decide a compra**. Sem essa separação, o hall inteiro sairia e voltaria a cada oscilação de preço. Empresa que falha 2 dos filtros 1–4 sai do hall.

| # | Filtro | Régua objetiva | Quem carrega a bandeira |
|---|---|---|---|
| 1 | **Retorno sobre capital** | Não financeira: **ROIC > WACC**, pelo **menor** entre o ROIC contábil e o ROIC a **custo de reposição** (§11.1) — capital a custo histórico contra WACC corrente infla o retorno em economia inflacionária. Financeira (banco, seguradora): **ROE > Ke nominal**. Os dois lados **nominais**. Sempre **no ciclo inteiro**, não no pico | Buffett, Munger, Greenblatt, Li Lu, Fisher |
| 2 | **Balanço que aguenta o ciclo** | Sem depender de refinanciamento; dívida coberta por caixa ou FCF | Graham, Dodd, Schloss, Klarman |
| 3 | **Dono do lado do minoritário** | Controlador sem objetivo diferente do retorno; capital alocado onde rende | Munger, Bolton, Fisher, Marks |
| 4 | **Provento previsível e coberto** | Sai do lucro **e** do caixa, todo ano, sem diferimento criativo | Bazin, Barsi, Bogle |
| 5 | **Preço com margem de segurança** | Preço ≤ 0,70 × valor central; e saber **por que** o mercado erra | Graham, Klarman, Templeton, Marks, Pabrai |

**WACC** = Ke × E/(D+E) + Kd × (1 − IR efetivo) × D/(D+E). **Pesos (v2.4, decisão do Frank em 08/10/2026):** D = dívida bruta do balanço; E = **valor da casa** (valor central × ações), achado por ponto fixo — o central depende do WACC e o WACC do central, então a conta se repete até E parar de mudar. Com o preço no lugar de E, o central mudava quando só o preço mudava e o P/C comparava o preço com um número que dependia dele. Sem central positivo não há ponto fixo (a palavra já é NÃO CONCLUSIVO) e os pesos vão ao preço só para exibir. **Kd** = custo médio da dívida informado no RI, em reais e depois dos swaps, com fonte e data (`kd_ri`); na falta, **rf nominal + spread sintético** pela cobertura de juros **normalizada** (lucro operacional antes do IR de meio de ciclo ÷ juros pagos em 12 meses), pela tabela do §4.1. Spread digitado só com fonte escrita. Juros pagos ÷ dívida bruta não serve: cupom em dólar não é custo em reais e o juro do arrendamento fica fora da linha. **Dívida inclui arrendamentos (IFRS 16).** **IR efetivo (v2.3)** = mediana de 5 anos de −IR ÷ LAIR (anos com taxa entre 0 e 50%), teto de 34%, **sem piso**. Benefício **permanente** (JCP, regime sem prazo) fica na mediana. **Crédito com prazo** (ágio amortizável, subvenção de ICMS) não vai à perpetuidade: a efetiva vale só até o fim declarado com fonte A/B, como valor presente à parte no EPV, no DCF e no Owner Earnings. Depois vale 34%, na perpetuidade **e no WACC**. Prazo sem fonte A/B: vale o primeiro prazo documentado. Na fase, a efetiva é a mediana de 5 anos **com** os anos de crédito, presa entre 0 e 34%. O benefício incide sobre o lucro **depois dos juros** normalizados, porque o WACC já deduz os juros a 34%, e nunca passa do crédito observado em R$. Mediana com menos de 3 anos válidos vale 34%. **Mudança de lei** (ex.: subvenção de ICMS tributada desde 2024) restringe a mediana aos exercícios da lei vigente, com a lei citada; com menos de 3 deles, 34% até completar. **Alíquota explícita abaixo de 34% só com fonte escrita** — ela não contorna o mínimo de 3 anos nem a regra de origem (v2.4). **Mediana abaixo de 15% só vale com a origem permanente declarada com fonte; sem ela, 34%**: benefício de origem e prazo desconhecidos tem prazo zero. Quando a alíquota perpétua não é a mediana observada, o Owner Earnings de cada exercício é refeito a ela. Declarar os números.

**Exceções legítimas, declaradas caso a caso:**
- **Lynch e Fisher** aceitam crescimento sem dividendo (falha o filtro 4).
- **Schloss e Graham** aceitam negócio medíocre a preço absurdo, tipo P/VP < 0,5 com caixa (falha o filtro 1).
- **Templeton e Klarman** compram estatal em pânico (falha o filtro 3), exigindo desconto explícito.
- **Dalio e Bogle** diriam que o hall inteiro é stock-picking e que o núcleo deveria ser IPCA+ e índice. Esta objeção é permanente e por isso o comparativo com renda fixa é obrigatório em toda análise.

**Círculo de competência (Buffett/Munger):** toda análise abre com 3 linhas respondendo "como esta empresa ganha dinheiro daqui a 10 anos, e o que a faria parar". Se a resposta não sair concreta, escrever **"fora do círculo de competência"** — o veredito fica limitado a RADAR, nunca BARATA/OPORTUNIDADE.

---

## 3. Hierarquia quando os critérios conflitam

1. **Sobrevivência** vence retorno. Empresa que pode quebrar não entra, por mais barata.
2. **Caixa** vence lucro contábil. Sempre que os dois divergirem, o caixa manda.
3. **ROIC** vence ROE. ROE alto com alavancagem alta é maquiagem.
4. **Ciclo normalizado** vence trimestre. Cíclica se avalia por meio de ciclo, declarado antes do veredito.
5. **Preço** vence qualidade. A melhor empresa do mundo no preço errado é o pior investimento — por isso a **palavra do veredito parte do preço** (§9) e **nenhuma nota de qualidade a melhora**; ela só pode piorar pelas travas de incerteza do §9 (círculo de competência, dispersão de métodos).

---

## 4. O custo de capital (Ke) e a renda fixa de referência

**Taxa livre de risco (rf):** Tesouro IPCA+ **sem juros semestrais com o vencimento mais longo à venda no Tesouro Direto**, **taxa de compra da manhã** publicada pelo Tesouro Transparente para o **dia do preço**, com o vencimento escrito. É a taxa que o investidor de fato consegue no título; o Tesouro Direto não publica fechamento, e a ANBIMA não traz a NTN-B Principal (a NTN-B com cupom é outro instrumento — só sensibilidade). **Todas as fichas e lotes do mesmo dia usam o mesmo vértice e a mesma taxa**, lidos de um arquivo só (`ferramentas/mercado_vigente.json`, conferido por teste contra a coleta). *(v2.4: até a v2.3.1 o texto dizia "fechamento" e o código já usava a da manhã — AUD-06.)*

- **Ke real = rf + prêmio.** Financeira (banco, seguradora, holding de seguros, concessão avaliada pelo motor de financeiras): prêmio de **5 p.p.** fixo — a alavancagem é o próprio negócio. **Não financeira (v2.4, decisão do Frank em 08/10/2026): os 5 p.p. são o risco do negócio SEM dívida, e a dívida soma risco ao acionista** — prêmio = 5 p.p. × [1 + (1 − t) × D/E] (Hamada, *Journal of Finance* 27(2):435-452, 1972, sobre Modigliani-Miller 1958 — nota B: referência conferida, texto não aberto), com t = alíquota perpétua (§2), D = dívida bruta e E no ponto fixo (§2). Nenhuma empresa fica com prêmio abaixo de 5 p.p. Com o Ke fixo, quanto mais dívida mais barato ficava o capital (WACC 14,5% na KLBN11 contra 19,1% na WEGE3). O mesmo Ke da empresa vale em tudo: âncoras, Owner Earnings, defasagem do provento, trava do §9, sensibilidade e Ke/g implícitos.
- **Inflação (π):** a **implícita da curva** (Tesouro Prefixado de prazo mais próximo × Tesouro IPCA+ do mesmo prazo: π = (1+pré)/(1+IPCA+) − 1). O Focus entra só como sensibilidade, declarada.
- **Ke nominal = (1 + Ke real) × (1 + π) − 1.**
- **Nunca misture:** fluxo em reais correntes → Ke nominal; fluxo real → Ke real. Crescimento (g) segue a mesma regra: g nominal com Ke nominal, g real com Ke real. **Um mesmo fluxo descontado nas duas formas tem de dar o mesmo valor**; se der diferente, há erro.
- **Uma só coluna decide:** o valor central é sempre calculado ao Ke da casa. "Ke de mercado" (ex.: 14%) aparece apenas como **sensibilidade**, em linha própria, e nunca entra no central nem no veredito.
- **Sensibilidade obrigatória:** quando o Ke da régua penalizar demais um ativo de risco baixo (utility AAA, empresa com caixa líquido), registre explicitamente o veredito ao Ke que o mercado atribui — sem mudar a régua.
- **Concessões e regulados:** calcule ou cite a **TIR real implícita** (bruta, antes do IR do investidor) ao preço atual **sempre** — aprovando ou reprovando — e compare com duas réguas brutas: **rf** (piso absoluto: TIR < rf = o ativo perde até para o título sem risco, CARA independentemente do resto) e **Ke real** (TIR ≥ Ke real ⇔ preço ≤ valor justo). Esse teste reprovou Taesa (6,5% < IPCA+ 7,35%) e aprovou Cemig na conta pura (15,3%); vale igualmente para Sabesp, Copasa, ISA e Alupar. A RF líquida abaixo serve só ao "vence a RF?", nunca à TIR.

**Renda fixa de referência — sempre líquida de IR, horizonte de 10 anos:**

- n = taxa nominal do Tesouro IPCA+ da rf = (1 + rf) × (1 + π) − 1.
- O IR do Tesouro sem cupom incide sobre o ganho **nominal**, **só no resgate** (15% acima de 2 anos). Logo:
  **RF real líquida = { [ (1+n)¹⁰ − 1 ] × 0,85 + 1 }^(1/10) ÷ (1 + π) − 1.**
  *Exemplo ilustrativo (números redondos, não de mercado): rf 7,00%, π 4,50% → n 11,82% → RF real líquida ≈ 5,87% a.a.; RF nominal líquida ≈ 10,63%; Ke real 12,00%, Ke nominal 17,04%.* O atalho "rf × 0,85" (5,95%) erra para cima e está proibido; tributar o nominal todo ano subestima, e só vale para título com cupom.
- **Retorno da ação, também líquido:** dividendo × (1 − alíquota de dividendos aplicável) + JCP × (1 − alíquota de JCP) + crescimento, com o ganho de capital tributado no fim (15%, diferido como acima). Alíquotas vigentes na tabela de parâmetros (§4.1).
- **"Vence a RF?"** pelo ponto médio do retorno real líquido esperado:
  - **Sim**: ≥ RF real líquida + 3 p.p.
  - **Empate**: entre RF real líquida + 1,5 p.p. e + 3 p.p.
  - **Não**: abaixo de RF real líquida + 1,5 p.p.
  - Se o **ponto médio** do retorno real líquido ficar abaixo da própria RF real líquida, acrescentar o carimbo **"perde para o Tesouro no cenário ruim"** (v2.6, AUD-40: é o que o motor calcula — não existe faixa do retorno; o "extremo inferior da faixa" do texto antigo não tinha conta por trás).

### 4.1 Parâmetros vigentes (atualizar com fonte quando mudarem)

| Parâmetro | Valor | Fonte / data de conferência |
|---|---|---|
| IR Tesouro Direto | Regressivo: 22,5% (≤ 180 d) · 20% (181–360) · 17,5% (361–720) · **15% (> 720 d)**; título sem cupom: só no resgate/vencimento | Receita Federal, tabelas 2026 (gov.br/receitafederal/…/tabelas/2026) — conferido 04/10/2026. A MP 1.303/2025 (alíquota única) perdeu eficácia segundo fontes não oficiais; a tabela regressiva segue publicada pela Receita |
| IRRF sobre JCP | **17,5%** (LC 224/2025; era 15%) | Notícias Senado/Câmara 29/12/2025 — conferido 04/10/2026. **Em aberto:** data exata de vigência e se há prazo final (busca citou "até 31/12/2027") — confirmar no texto da LC antes de usar em horizonte longo |
| Dividendos (pessoa física) | Isento até **R$ 50 mil/mês por empresa pagadora**; acima, retenção de **10%** (Lei 15.270/2025, vigente desde jan/2026). IRPF mínimo para renda > R$ 600 mil/ano | Receita Federal, notícia de ago/2026 — conferido 04/10/2026. **Em aberto:** se os 10% incidem sobre todo o valor ou só o excedente, e a regra de transição de lucros apurados até 2025 |
| Spread de crédito sintético (Kd na falta do RI, §2) | Cobertura → spread: < 0,2 D 19% · < 0,65 C 16% · < 0,8 CC 12,61% · < 1,25 CCC 8,85% · < 1,5 B− 5,09% · < 1,75 B 3,21% · < 2 B+ 2,75% · < 2,25 BB 1,84% · < 2,5 BB+ 1,38% · < 3 BBB 1,11% · < 4,25 A− 0,89% · < 5,5 A 0,78% · < 6,5 A+ 0,70% · < 8,5 AA 0,55% · ≥ 8,5 AAA 0,40% | Damodaran, *Ratings, Interest Coverage Ratios and Default Spread*, empresas não financeiras grandes, dados de jan/2026 (pages.stern.nyu.edu/~adamodar/…/ratings.html) — conferido 08/10/2026; **nota B** (base do autor). Atualizar em janeiro |
| Ganho de capital em ações (à vista) | **15%** sobre o ganho líquido; isento se as vendas de ações no mês somarem ≤ **R$ 20 mil** | Receita Federal, página de isenções de renda variável — conferido 04/10/2026 |

*Na prática desta mesa (investidor pessoa física, proventos abaixo de R$ 50 mil/mês por empresa): dividendo líquido = bruto; JCP líquido = bruto × 0,825.*

---

## 5. Os seis vetores de risco de controlador

Nunca dizer apenas "estatal é ruim". Identificar **qual** vetor está em jogo, se já foi consumado e quanto vale.

| Vetor | O que o controlador faz | Reversível? |
|---|---|---|
| **V1** | Preço/tarifa abaixo do econômico | Sim, mas o dano ao caixa é permanente |
| **V2** | Confisco regulatório (regulador vinculado ao dono) | Só na justiça, em anos |
| **V3** | Alocação forçada de capital (crédito dirigido, compra de ativo do dono) | Não — o capital já saiu |
| **V4** | Renegociação de contrato com a controladora (comissão, exclusividade, prazo) | Sim, mas redefine o valor perpétuo |
| **V5** | Payout como instrumento fiscal (corta ou infla) | Sim, bidirecional |
| **V6** | Mudança de controle imposta (federalização, incorporação) | Binário |

**Regra de aplicação — a mais violada:**
1. Listar as interferências **já consumadas** nos últimos 15 anos, com fonte.
2. Estimar probabilidade × magnitude do risco prospectivo.
3. Aplicar o desconto **uma única vez**: ou em cenários ponderados no valor central, ou no Ke. **Declarar qual, com o número.** Toda ficha tem a linha "Desconto de controlador: X% em [cenários | Ke] — ou zero, porque [nenhuma interferência consumada]". Controlador privado também recebe a linha (ex.: "zero — sem conflito identificado"). **O desconto incide só sobre âncora positiva (v2.3).** Âncora ≤ 0 fica como está e continua tornando o veredito não conclusivo (§11.3); multiplicar um valor negativo por (1 − desconto) o melhoraria. O Ke implícito e o DCF reverso comparam o preço com o valor **já descontado**.
4. Avaliar a **qualidade intrínseca do negócio separadamente** do dono. Uma empresa pode ter moat 8 e controlador 2.
5. Depois de aplicado no valor, o risco **não volta** a descontar o retorno esperado, a nota ou o veredito.

**Precedentes da casa (dano consumado vs risco prospectivo):**

| Empresa | Consumado | Desconto aplicado |
|---|---|---|
| Petrobras | Preços 2011–14; imposto de exportação 2026 | Cenários ponderados (~8% no central) |
| Cemig | MP 579 (2012); corte de dividendo e venda de ativos (2016) | 40% × cenário federalização |
| Sanepar | Agepar destinou R$ 4,4 bi à tarifa (2026) | 15% adicional (o confisco já estava no fluxo) |
| Banrisul | Compra da folha do Estado por R$ 1,23 bi | 35% |
| BB Seguridade / Caixa Seguridade | **Nenhuma em 13 e 11 anos** | **Zero** — o risco é V4, já no DDM |
| CPFL (State Grid) / Engie (França) / Mahle / Gerdau | **Nenhuma** | **Zero** |

---

## 6. Proventos — como se lê um yield de verdade

Um DY de agregador não é informação até passar por seis testes:

1. **Ajuste por bonificação e desdobramento.** Erros já encontrados: Sabesp (agregadores mostravam 12–13%; o real era 2,4% após a bonificação de 5:1) e Engie (mostravam 5–8%; o real era 3,4% após a bonificação de 40%).
2. **Data-com vs pagamento.** Mede-se por data-com para comparar; por pagamento para saber quando o caixa entra.
3. **Defasagem.** Hypera paga o JCP 15–21 meses depois; Vibra, ~8,5 (medida; o texto até a v2.5 dizia 15–18 — AUD-55); Vivo, 7–14; TIM, ~4 (2026; era ~12); Fleury parcela em até 2 anos. Mahle (1–6 meses), Gerdau (7–31 dias) e Unipar (9–11 dias) são as boas práticas. **A defasagem tem custo: o provento é trazido a valor presente ao Ke nominal** (pagar R$ 1 em 18 meses vale ~R$ 0,79 a Ke 16,6%), não ao IPCA. **De onde vem o prazo:** o padrão é a **defasagem medida** (média ponderada pelo valor de data-com → pagamento nos eventos dos 3 últimos anos). Um prazo informado à mão só vale com **evento declarado e fonte escrita** (campo `defasagem_fonte`) — calendário de JCP ou dividendo já anunciado, com a data; sem fonte o motor **não roda**. Prospectivo declarado vence o histórico: HYPE3 18 meses (JCP de 2026 pago até 31/12/2027), VIVT3 10, FLRY3 9, WEGE3 9, TIMS3 4. ABEV3 usava 6 meses sem evento declarado e passou ao medido (1,5 mês) em 05/10/2026.
4. **Ordinário vs extraordinário vs redução de capital.** Vivo distribuiu R$ 1,25/ação como redução de capital — legítimo, mas não é lucro. Ambev antecipou 2025 por razão fiscal.
5. **Payout sobre lucro E sobre FCFE.** Klabin paga com venda de terras; Unipar pagou 270% do lucro em 2025, com o caixa caindo à metade em 2023–25; Copel eleva a alavancagem-alvo para pagar extras.
6. **A pergunta final: o dividendo é coberto por caixa?** Só "sim" habilita o Preço Teto de Bazin.

**Yield sustentável — o único que entra em conta.** É o menor entre (a) o DPA médio de 5 anos ajustado e (b) o DPA que o FCFE normalizado paga. A parte paga com dívida, venda de ativo ou caixa acumulado é exibida, mas não entra no Bazin, no Bogle, no comparativo com a RF nem no "vence a RF". **Vale igual para todo setor** — utility que paga extra com dívida segue a mesma regra da química que paga acima do FCFE.

---

## 7. As quatro armadilhas de valor (verificar em toda análise)

| Armadilha | Como detectar | Caso da casa |
|---|---|---|
| **Lucro não recorrente** | Contábil ≫ ajustado; câmbio, IAS 29, crédito fiscal, venda de ativo | Sanepar (precatório de IRPJ R$ 2,06 bi, 2025), Engie (venda da TAG R$ 1,34 bi em 2024; repactuação do UBP R$ 1,92 bi no 2T26), Mahle (resultado financeiro +R$ 122 mi em 2023; IAS 29) |
| **Dividendo não coberto por caixa** | Payout > FCFE; caixa caindo; dívida subindo | **Unipar** (270% do lucro em 2025), Klabin (venda de terras) |
| **ROE inflado por alavancagem** | ROE alto com ROIC baixo | Mahle (ROE 70%, ROIC ~33%, 2025), Unipar (ROE 27%, ROIC ~12%, 2025) |
| **Múltiplo baixo em topo de ciclo** | P/L baixo com margem em recorde | Vibra (EBIT +277% a/a no 2T26), Petrobras (Brent US$ 114 em set/2026, EIA) |

**Mesmo defeito, mesmo tratamento:** payout acima do FCFE por 2+ anos com dívida subindo gera o mesmo carimbo em qualquer empresa (Unipar e Klabin incluídas). Se uma recebe e a outra não, a ficha explica a diferença em número.

*Casos da casa: CVM (DFP/ITR, nota A) e EIA; ano, conta e cálculo no `09` de 21/10/2026. ROIC "~" = EBIT × 0,66 ÷ (PL + dívida − caixa), aproximação da conferência, não o número do motor.*

**Placar limpo até hoje:** apenas **GGBR4** teve zero das quatro.

---

## 8. Setores a evitar por estrutura econômica

Evita-se o **setor** quando a estrutura impede retorno acima do custo de capital de forma repetível:

- **Aviação** — custo fixo alto, receita em real e custo em dólar, produto sem diferenciação.
- **Educação superior privada** — receita dependente de crédito estudantil; EAD comoditizou.
- **E-commerce puro e tecnologia sem lucro** — ativo é o time; competição por capital, não por retorno.
- **Empresas em recuperação judicial** — o acionista está atrás de todo o passivo.
- **Resseguro e seguradoras monoline sem escala** — um evento zera anos de lucro.

**Não são setores a evitar** — são empresas a evitar dentro deles: construção, frigorífico, varejo, commodities, petróleo, siderurgia, papel. Aí o que separa é custo de produção, alavancagem e alocação de capital.

---

## 9. Régua do veredito

A palavra **parte** da razão preço ÷ valor central (calculado conforme §11). A régua é contínua — não há faixa sem nome.

| Palavra | Preço ÷ valor central | Leitura |
|---|---|---|
| **BARATA** | ≤ 0,70 | margem de segurança ≥ 30% |
| **RADAR** | > 0,70 e ≤ 0,90 | desconto de 10% a 30% |
| **JUSTA** | > 0,90 e ≤ 1,10 | ±10% |
| **CARA** | > 1,10 | prêmio acima de 10% |
| **OPORTUNIDADE** | BARATA **e** catalisador identificado, com data | — |

**Ordem de aplicação (precedência fixa):**
1. Palavra pela régua acima.
2. Fora do círculo de competência → teto RADAR.
3. Dispersão das âncoras > 1,8× → desce um nível no lado favorável (BARATA → RADAR → JUSTA); JUSTA e CARA não mudam. Dispersão > 3× ou âncora ≤ 0 → **NÃO CONCLUSIVO** (sem palavra).
3b. **Trava de coerência (v2.4; v2.6):** JUSTA **final** — depois do círculo e da dispersão (v2.6, AUD-10, decisão do Frank: até a v2.5 só a JUSTA da régua; a RADAR que subia a JUSTA pela dispersão escapava) — com o retorno de Bogle fora de ±2 p.p. do Ke nominal da empresa → **NÃO CONCLUSIVO**, até a ficha escrever qual premissa diverge (`trava_razao`).
4. Carimbos (ARMADILHA, defeito estrutural, OPORTUNIDADE).

**A compra só é autorizada pela palavra FINAL:** BARATA/OPORTUNIDADE → compra até o preço de compra; qualquer outra palavra → sem compra, salvo a exceção escrita abaixo. Ex.: P/C 0,65 com dispersão 2× vira RADAR — compra **bloqueada**.

**ARMADILHA é carimbo, não faixa.** Aplica-se quando o múltiplo parece baixo (P/L ou P/VP abaixo da mediana dos pares ou do próprio histórico de 10 anos) **e** há defeito estrutural: dividendo não coberto, ativo em declínio ou controlador extraindo valor. Formato: "RADAR — ARMADILHA". Se o preço já está acima do valor central, a palavra é **CARA** com a anotação "defeito estrutural: [qual]" — não ARMADILHA.

**O veredito é sempre acompanhado de:**
- **Preço de compra = 0,70 × valor central.** É o único preço que autoriza compra.
- **Exceção escrita (Buffett: "empresa excelente a preço justo"; no motor, `entrada_parcial` — regra única desde a v2.6, AUD-42):** se nota de Qualidade ≥ 8, Solidez ≥ 7, **zero** armadilhas, dentro do círculo de competência e dispersão ≤ 1,8×, autoriza-se **uma 1ª parcela de no máximo 1/3 da posição pretendida** a preço ≤ 0,80 × valor central. Fora dessa exceção não existe "aceitável", "ok a X" ou "começar em Y" acima do preço de compra.
- **Preço justo** = valor central.
- **Preço de saída = 1,30 × valor central**, recalculado toda vez que o central muda. Tese quebrada (gatilho acionado) é saída a qualquer preço.
- **Exceção de qualidade na saída (1,50 × valor central).** Não financeira com **ROIC real > WACC real a custo de reposição em ≥ 8 exercícios**, em janela de **pelo menos 10 exercícios**, *e* **nota de Qualidade ≥ 8** vende só acima de **1,50 ×** o central — ou com tese quebrada, a qualquer preço. Os dois lados em termos **reais** (§4): o ROIC de um exercício é nominal daquele ano e o WACC é o de hoje, então comparar nominal com nominal reprovava quase todo exercício antigo. **Janela declarada curta não permite a exceção**: "8 exercícios" não tem referente numa janela de 5 a 7 anos, e 5 anos não são um ciclo (§2) — ficam fora TIMS3, VIVT3, FLRY3, PRIO3, RECV3, UGPA3 e VBBR3. Todas as demais seguem 1,30 ×. **Não se aplica a financeira**: o repositório não tem série de 10 anos de banco ou seguradora (entram por campos escalares), então não há como medir o critério. Base — Buffett, carta de 1988: *"when we own portions of outstanding businesses with outstanding managements, our favorite holding period is forever"*; carta de 1989: *"we would rather stay put, even if that means slightly lower returns"*, e o imposto diferido é *"an interest-free loan from the U.S. Treasury that comes due only at our election"*. O argumento **não é** o imposto: na mesma carta de 1989 Buffett escreve que não adotou a estratégia de longo prazo por causa dessa matemática. Fisher (*Common Stocks and Uncommon Profits*, "When to Sell") dá três razões para vender e nenhuma é preço — **paráfrase, fonte nota C** (texto primário não conferido). Decisão do Frank em 05/10/2026, registrada no diário (09): é preferência dele sobre a própria doutrina. Em 08/10/2026 **nenhum** ticker é elegível: a LEVE3, única em 05/10 (8 de 10 exercícios, Qualidade 8,005 arbitrada), perdeu a exceção com as notas por evidência do dossiê (Qualidade 7,1). Em 05/10/2026 **um** ticker era elegível: **LEVE3** (8 de 10 exercícios, Qualidade 8,005 — no limite), cuja saída passa de R$ 44,35 para **R$ 50,98**; a ação está a R$ 34,43 com central R$ 33,99 (JUSTA, P/C 1,01), muito abaixo de qualquer das duas, então **nenhuma decisão muda hoje**. O único na faixa 1,30–1,50 × era ABEV3, que reprova pela Qualidade (7,018) apesar dos 8 de 10 exercícios — e com o capex de manutenção real a P/C dela foi a 1,51, saindo da faixa. **Fragilidade declarada:** a LEVE3 entra por 0,005 de nota; se o ROIC a reposição dela cair, ela sai.
- **Gatilho que invalida a tese**, verificável e com data quando houver.
- **Resposta separada** para carteira de proventos e para ganho de capital.

**Trava de coerência (obrigatória):** se o veredito é JUSTA, o retorno esperado nominal de Bogle (§11) ao preço atual tem de ficar a **±2 p.p. do Ke nominal**. Fora disso, uma das duas contas está errada: a ficha diz qual premissa diverge (g, payout, múltiplo final) e corrige antes de publicar. **Desde a v2.4 o motor aplica a regra (passo 3b):** sem a premissa escrita a palavra é NÃO CONCLUSIVO — antes a trava era só um campo, e uma JUSTA saía com ela falha (AUD-08). Corolário: **ação JUSTA que "não vence a RF" indica valor central errado**, porque ao Ke da casa ela renderia o Ke.

---

## 10. Notas numéricas das fichas (0–10)

| Dimensão | Peso | O que mede |
|---|---|---|
| Qualidade do negócio | 30% | Moat, Fisher, gestão, ROIC × WACC no ciclo |
| Solidez / balanço | 20% | Não financeira: DL/EBITDA normalizada, cobertura de juros e Altman Z'' (média simples; DL/EBITDA indefinida = pior nota). Financeira: prudencial (CET1, inadimplência, cobertura) ou nota declarada. Piotroski e Beneish são exibidos (qualidade do lucro), **não** entram na nota (v2.6, AUD-39) |
| Renda (proventos) | 25% | Yield sustentável, cobertura por caixa, recorrência, defasagem |
| Preço (margem de segurança) | 25% | Escala abaixo |

**Escala única da nota de Preço** (preço ÷ valor central): ≤ 0,60 → 10 · 0,65 → 9 · 0,70 → 8 · 0,80 → 7 · 0,90 → 6 · 1,00 → 5 · 1,10 → 4 · 1,20 → 3 · 1,30 → 2 · 1,40 → 1 · ≥ 1,50 → 0 (interpolar linearmente entre os pontos).

A nota resume; **não decide**. A palavra do veredito vem só da régua do §9.

Qualitativo interno usa 0–5 (moat, Fisher, gestão, controlador, ciclo, Templeton, Dhandho, círculo de competência), com peso dobrado no controlador quando houver poder discricionário. **O motor aplica o peso desde a v2.3**: média = (moat + gestão + c × controlador + ciclo + Fisher) ÷ (4 + c), com c = 2 se discricionário (regra 11 do `02` v4); peso 2 sem a razão escrita não roda. No hall, as notas seguem **arbitradas ("arbitrada, pré-v4")** até o dossiê de cada ticker. Até lá, c = 2 vale onde a interferência consumada já está declarada no desconto do lote (BBAS3, BRSR6, CMIG4, SAPR11, PETR4), como critério provisório. O peso não é desconto novo (§5, item 5): a nota não decide a palavra.

---

## 11. Quadro clássico e regra do valor central

### 11.1 O quadro (obrigatório em toda análise **e em toda reavaliação**)

Cada linha traz: valor, fórmula, insumos com fonte, e a marca **ÂNCORA**, **INFORMATIVO** ou **N/A por perfil**. Nunca copiar número de ficha anterior sem recalcular ("da ficha" é proibido).

| Método | Fórmula da casa | Observação |
|---|---|---|
| **Lucro projetado (3 anos)** | LPA consenso (fonte, nº de casas) **e** LPA próprio = receita projetada × margem líquida ÷ nº de ações; mostrar a diferença | Base de PEG, Graham revisado, Bogle e DCF |
| **Lucro normalizado (Klarman)** | Cíclica: margem mediana do ciclo × receita de meio de ciclo; demais: **mediana da janela do ciclo (10 anos) sem não recorrentes** — janela mais curta só por quebra estrutural declarada (§11.4). 'Outras receitas operacionais' acima da mediana de 10 anos da empresa (em % da receita) são tratadas como não recorrentes — se a empresa lança ganhos (venda de ativo, compra vantajosa, crédito tributário) em 'outras despesas' (3.04.05), usa-se 3.04.04 + 3.04.05 sem o impairment. **Preço de commodity declarado antes do veredito:** média de 10 anos do preço em R$ de hoje (ex.: barril = Brent × câmbio, corrigido pelo IPCA). **E&P:** receita do período-base (volume atual) × preço de meio ÷ preço do período; margem = EBITDA sem impairment mediano − D&A atual ÷ receita de meio − impairment mediano se for perda recorrente. **Distribuição com receita indexada a commodity:** EBIT em R$ de hoje (IPCA), mediana do perímetro comparável. **Déficit atuarial** só entra na ponte se o custo atuarial não estiver no EBIT. **Sem preço em R$/t com fonte A/B por API** (aço, soda, PVC): índice de preço ao produtor (BLS) × câmbio, corrigido pelo IPCA, declarado como proxy, com os pesos da cesta escritos; **receita de meio** = receita de 12m × preço de meio ÷ preço dos 12m. **Impairment de cíclica** (não só E&P): sai da margem ano a ano e entra a perda mediana de 10 anos (só penaliza); o impairment só é descontado de "outras despesas" se estiver lançado nelas. **Cíclica de janela curta: margem ao preço de meio (v2.3, CMIN3).** Quando a janela de margem não cobre um ciclo e cai num período de preço alto, a mediana leva o pico embutido e, aplicada à receita de meio, conta o preço duas vezes. Então cada ano é reexpresso ao preço de meio: margem' = 1 − v − (1 − margem − v) ÷ f, com f = preço de meio ÷ preço do ano (R$ de hoje) e v = fração da receita cujo custo acompanha o preço (royalty, compra de terceiros); f = 1 devolve a margem original. **Só cíclica, só com dossiê próprio e janela de pelo menos 7 exercícios**; não combina com deflator nem com a regra do E&P (o motor confere perfil, janela e combinação, e falha alto) | Entra em Graham, EPV e P/L de triagem |
| **Fator Brasil (f)** | f = (1 ÷ Ke real) ÷ 8,5 | Graham usava P/L 8,5 para empresa sem crescimento; ao Ke da casa esse P/L é 1/Ke real (= Gordon com g = inflação). Ex.: Ke real 12% → f = 0,98 |
| **Graham original** | √(22,5 × LPA × VPA) | INFORMATIVO |
| **Graham-BR** | √(22,5 × f × LPA **normalizado** × VPA) | Com Ke real ~12% fica quase igual ao original: o defeito histórico da mesa foi usar **lucro de pico**, não a constante |
| **Graham revisado-BR** | V = LPA normalizado × (8,5 + 2g) × f, g = crescimento **real** em % a.a. dos próximos 7–10 anos | Em g = 0 dá 1/Ke real × LPA — coerente com o Gordon |
| **7 critérios do defensivo** | tamanho, liquidez corrente ≥ 2, lucro positivo 10 anos, dividendos 20 anos, LPA +1/3 em 10 anos, P/L ≤ 15 × f, P/L × P/VP ≤ 22,5 × f | Placar x/7 |
| **Bazin original** | DPA sustentável ÷ 6% | INFORMATIVO |
| **Teto de renda (Bazin calibrado)** | DPA sustentável **líquido** (JCP × 0,825) ÷ yield nominal líquido da RF de referência (§4) | **INFORMATIVO em todo perfil.** Acima deste preço a renda sem crescimento perde para o Tesouro; não é valor justo (o DPA dividido por taxa abaixo do Ke superavalia). Só se "coberto por caixa = sim" |
| **Lynch** | Categoria (crescimento lento, stalwart, crescimento rápido, cíclica, recuperação, ativo oculto) + PEG = P/L ÷ g LPA (%) e PEGY = P/L ÷ (g + DY) | PEG só para stalwart e crescimento rápido; g nominal descontado da inflação implícita para comparar com 1,0 |
| **ROIC a custo de reposição** | NOPAT normalizado ÷ (PL + dívida líquida + imobilizado × (IPCA da idade média − 1)); **idade média ≈ imobilizado líquido ÷ D&A anual**, limitada a 1–15 anos | **Exibido ao lado do contábil, e o MENOR dos dois decide** o filtro 1 (§2), a nota de Qualidade e a trava do crescimento no DCF. Sob depreciação linear e safras uniformes, líquido ÷ D&A = vida útil ÷ 2 = idade média. **Aproximação declarada:** a D&A da DFC inclui amortização de intangível e do direito de uso, o que subestima a idade — a correção sai conservadora; só o imobilizado é corrigido (intangível e goodwill estão a preço de aquisição e não têm custo de reposição definido). Coerente com o "valor de reprodução" que a casa já usa como âncora de cíclica (Greenwald, nota C: texto primário não conferido) |
| **Greenblatt** | EY = EBIT ÷ EV; ROC = EBIT ÷ (capital de giro líquido + imobilizado líquido) | Vale como **posição no ranking do hall** (03), não como número solto; N/A para financeiras |
| **Owner Earnings (Buffett)** | Lucro líquido **do controlador** (v2.6, AUD-15: o OE é fluxo do acionista da controladora, como EPV e DCF descontam os minoritários; sem a linha na CVM, o consolidado) + D&A + outros não caixa − capex de manutenção − Δ capital de giro necessário | Capex de manutenção — **serviços/industrial**: capex total − (imobilizado + intangível + biológico ÷ receita) × Δreceita **REAL média de 5 anos**, **piso zero**. A receita do ano-base entra a preços do exercício corrente (IPCA, série SGS 433 do BCB desde 1980): sem isso a inflação virava "crescimento" e reduzia o capex de manutenção. Deflacionar **não** é exigência de Greenwald (o método não trata inflação) — é coerência com este mesmo §11.1, que já manda preço de commodity e EPV em R$ de hoje. **Adaptação declarada:** a casa usa imobilizado + intangível + biológico **líquidos do exercício**; o método original usa PPE **bruto** em média de anos anteriores (fonte secundária, nota C — o livro não foi conferido). A série da CVM só traz o líquido (conta 1.02.03); conferir o texto primário e coletar o bruto fica como pendência. **Cíclica/commodity**: a receita cresce por preço, não por capacidade — capex de manutenção = **mediana de 10 anos de capex ÷ receita** (dilui projetos de expansão não identificados), comparada à mediana de D&A ÷ receita. Quando o capex de manutenção supera a D&A, a diferença **sai do lucro normalizado** (só penaliza). **Capex de expansão identificado (v2.3):** só o projeto nomeado, com valor e prazo em fonte A/B e ainda sem receita, sai do capex antes da regra (Greenwald ou mediana de commodity), pelo campo `capex_expansao`. O resto continua manutenção. O retorno do projeto só entra no valor quando virar receita (conservador); o retorno projetado é só exibido. **Telecom**: capex de rede = manutenção (reposição tecnológica; a receita cresce por preço), pela regra de commodity. **IFRS 16**: o aluguel pago (amortização do passivo de arrendamento, DFC de financiamento, **sem juros**) sai do OE em **todos** os perfis — a D&A somada de volta inclui o direito de uso. O juro já está no lucro líquido, então o que sai é só o **principal**, decidido pelo dado e não por lista: linha de principal sai inteira; linha que a **própria empresa** declara como "principal e juros" (UGPA3 6.03.07, LEVE3) tem o juro estimado pelo **saldo médio do passivo de arrendamento × Kd REAL** e devolvido. O Kd nominal é o de hoje (rf de ~15%) e aplicá-lo a saldos de 2019–21, quando a Selic era 2%, devolveria juro demais e **inflaria** o OE; o Kd real é limite inferior do juro, logo o principal descontado é limite superior — erra para o lado que penaliza. **Limite declarado:** quando a empresa não reporta o passivo de arrendamento no balanço estruturado da CVM (ABEV3: 2.01.04.03 e 2.02.01.03 vêm zeradas), o juro não é estimável e a linha sai inteira — conservador, pode contar o juro duas vezes. Consequência medida em 05/10/2026: o OE de SMTO3 e SLCE3 fica negativo (aluguel de terra e parceria agrícola) e o provento deixa de ser "coberto". D&A só como proxy rotulado. Mostrar OE yield e OE ÷ (Ke real − g real), em R$ de hoje: **o OE de cada exercício (e o DPA de cada ano) vai a R$ de hoje pelo IPCA antes da mediana** — fluxo nominal capitalizado a taxa real subestima o valor (v2.3.1) |
| **EPV (Greenwald)** | Lucro operacional normalizado após IR, em R$ de hoje ÷ **WACC real** − dívida líquida; WACC real = (1 + WACC nominal) ÷ (1 + π) − 1. **Receita de meio padrão** (sem preço de commodity declarado) = média de 3 exercícios + 12 meses, **cada um levado a R$ de hoje pelo IPCA antes da média** (os 12 meses pela média do índice do período) — v2.3.1 | Supõe lucro constante **em termos reais** (dividir lucro de hoje por taxa nominal supõe encolher à inflação). Comparar com valor de reprodução: EPV > reprodução = há moat. **Outros passivos (v2.3).** Passivo com juros ou financeiro fora das contas de empréstimo é dívida: passivo de contrato com componente de financiamento, provento a pagar já ex. **Provento já ex (v2.3.1, auditoria 08/10/2026):** é todo provento que o preço já descontou e o caixa do balanço ainda guarda — o passivo de proventos do balanço (menos o que ainda não for ex na data do preço) **mais** o aprovado depois da data do balanço com data-com até a data do preço (API da B3); medido do dado em toda não financeira, não digitado (`proventos_ex.py`). Ele entra na dívida líquida: ponte, DL/EBITDA, capital do ROIC, EV e juros normalizados. Passivo operacional à frente do acionista entra só na ponte. Os dois saem do Owner Earnings. O WACC fica com a dívida do balanço (conservador). **Crédito de IR com prazo:** valor presente à parte, ver §2 |
| **Valor de reprodução** (âncora de cíclica, v2.4) | PL contábil consolidado − não controladores − provento já ex que está no PL, por ação; laudo/NAV melhor só com fonte | É o **menor** entre o contábil e o de reposição — a mesma regra conservadora do ROIC (§2). A reprodução a custo de reposição (imobilizado × (IPCA da idade média − 1), a correção do ROIC a reposição) é **exibida, não decide**: a auditoria de 08/10 não demonstrou que ela seja a medida mais correta (AUD-18) |
| **DDM / Gordon** | P = D₁ ÷ (Ke − g), g ≤ g sustentável = ROE × (1 − payout) | Real com real, nominal com nominal |
| **P/VP justificado** | (ROE − g) ÷ (Ke − g), tudo nominal; ROE normalizado | Bancos e seguradoras; regulados, como proxy do DCF regulatório (§11.2) |
| **SOTP** | Soma das partes a valor justo da casa − desconto de holding declarado | Holdings. Participação que a casa avalia (ex.: Itaú na ITSA4) entra ao central dela **recalculado ao mesmo Ke**, com a quantidade de ações do FRE; as demais a valor contábil (conservador); desconto = custo da holding capitalizado (G&A ÷ Ke real), declarado |
| **DCF (3 cenários)** | FCFF ao WACC (ou FCFE ao Ke), premissas explícitas; perpetuidade g ≤ PIB nominal de longo prazo. Valor de geração: FCFF = NOPAT × (1 + g) × (1 − g ÷ ROIC) | Pesos dos cenários declarados. **Crescimento só entra se o MENOR dos dois ROIC (contábil e a custo de reposição) > WACC** (Greenwald, conteúdo confere em fonte secundária): crescer exige retorno acima do custo de capital sobre o capital **a preços de hoje**, que é o que a empresa terá de repor. Senão g = 0 e o DCF converge para o EPV. A trava é avaliada **por cenário** (p25, mediana, p75): **em cada cenário é um degrau** (g inteiro ou zero) e só a ponderação dos três suaviza — perto da fronteira o DCF de um cenário salta (WEGE3: +36% no DCF base com 0,1 p.p. de margem; o central, +5%) (v2.6, AUD-14; até a v2.5 o texto dizia "gradual"). **Declínio (g < 0) com ROIC < WACC não devolve capital** (reinvestimento zero, o freio que antes só a RECV3 declarava): com ROIC pequeno o "reinvestimento negativo" g ÷ ROIC fazia o DCF subir com o declínio (v2.6, AUD-34). **Cenário com valor negativo entra como zero** na ponderação dos três (o acionista não deve além do que pôs; v2.6, AUD-53). **Compounder** (ROIC > WACC com folga): 2 estágios — g real de 10 anos = ROE mediano de 5 anos × retenção recorrente, deflacionado; depois g ≤ PIB real; o DCF reverso devolve o g de 10 anos. **IFRS 16**: arrendamento é dívida e a margem usa só a janela em que o aluguel já saiu do EBIT (2019+). Ganho de valor justo de ativo biológico fica no EBIT (a exaustão o devolve no ciclo), exibido como risco de qualidade do lucro |
| **DCF reverso** | g implícito que iguala o DCF ao preço atual, ao Ke da casa | O "segundo nível" de Marks em número: o que o mercado já precifica |
| **TIR real implícita** | TIR dos fluxos contratuais/regulados ao preço atual | Concessões e regulados, sempre |
| **Bogle** | Retorno nominal = DY sustentável + g LPA + variação de múltiplo [(P/L final ÷ P/L atual)^(1/10) − 1]; real = (1 + nominal) ÷ (1 + π) − 1 | P/L atual e final sobre **LPA normalizado** (lucro corrente negativo não entra); P/L final = normalizado de 10 anos ou dos pares; recompra só entra se não estiver já no g. LPA normalizado ≤ 0 → Bogle e trava de coerência N/A, veredito NÃO CONCLUSIVO |
| **Teste do R$ 1 retido** | Δ valor de mercado ÷ lucro retido em 5–10 anos | ≥ 1 = gestão cria valor |
| **Qualidade do lucro** | ROIC (contábil **e** a custo de reposição, o menor valendo) × WACC; accruals de Sloan; Piotroski F (0–9); Altman Z'' (não financeiras); Beneish M (> −1,78 = alerta) | Recalcular a cada ficha |

### 11.2 Métodos ÂNCORA por perfil

| Perfil | Âncoras (decidem o central) | Informativos (exibidos) |
|---|---|---|
| Banco | P/VP justificado · DDM | Graham-BR, teto de renda, Bogle |
| Seguradora | DDM · P/VP justificado | teto de renda, Graham-BR |
| Holding | SOTP · DDM | teto de renda |
| Utility / concessão / saneamento | DDM · DCF regulatório (TIR real sobre a base regulatória). **Sem base regulatória e WACC regulatório com fonte A/B** — ou quando a contabilidade de concessão (ICPC 01/IFRS 15) põe o investimento dentro do FCO —, o DCF regulatório é o **P/VP justificado sobre o patrimônio** (proxy da base regulatória), **declarado como proxy**, onde quer que o investimento esteja na DFC (v2.5). A ficha escreve onde ele está (FCO, FCI ou misto, com as linhas da DFC); base regulatória nota C entra só como informativa (paridade valor da firma ÷ base), nunca como âncora. **Emissão de ações depois do balanço** (follow-on): patrimônio + caixa captado, dinheiro novo rendendo o Ke (VPL zero), com sensibilidade se render menos | teto de renda, Graham-BR, EPV (N/A se o FCO não medir o caixa do negócio) |
| Industrial / serviços / consumo | DCF · EPV · Owner Earnings ÷ (Ke real − g real) | Graham-BR, Graham revisado-BR, teto de renda, PEG |
| Cíclica / commodity | EPV de meio de ciclo · DCF normalizado · valor de reprodução | Graham-BR com lucro normalizado, teto de renda |

*Graham-BR e teto de renda nunca são âncora: o primeiro ignora a estrutura de capital e o crescimento, o segundo é piso de renda, não valor.*

### 11.3 Regra do valor central

1. Todas as âncoras são calculadas **ao Ke da casa** (§4).
2. **Valor central = mediana das âncoras.** Pesos diferentes só com justificativa escrita em uma linha.
3. **Dispersão** = maior âncora ÷ menor âncora. Acima de **1,8×**: "confiança baixa" e o veredito desce um nível (BARATA → RADAR → JUSTA). Acima de **3×**: **"não conclusivo por discordância de método"** — mostra a margem por método e não emite palavra. **Âncora ≤ 0** (valor de equity negativo ou nulo) → não conclusivo, com a razão escrita. Perfil com menos de 2 âncoras calculáveis → declarar "âncora única" e confiança baixa.
4. **Proibido:** valor central obtido por "valor anterior × fator de Ke", por soma de ajustes avulsos em R$ ("+8 −2 +1"), número redondo sem conta, ou central fora do intervalo das âncoras.
5. Toda ficha traz a tabela de reconstrução: âncora | valor | peso → central. Quem lê tem de conseguir refazer a conta.


### 11.4 Janela do ciclo e quebra estrutural

1. **Janela padrão: 10 exercícios** (ciclo inteiro). A margem normalizada é a **mediana** dessa janela, nunca a média de 5 anos nem o pico.
2. **Janela mais curta só por quebra estrutural declarada**, com o evento e a data escritos no campo `janela_razao` do motor — adoção de IFRS 16 (2019), IPO, cisão, aquisição que muda o perímetro, mudança de lei, exercício social deslocado. Sem razão escrita o motor **não roda** (levanta erro). Janelas em uso em 05/10/2026: TIMS3, VIVT3 e FLRY3 2019–25 (IFRS 16); PETR4 2019–25 (IFRS 16, desde 08/10/2026 — ver item 4); PRIO3 2019–25 (perímetro operado); RECV3 2020–25 (IPO em set/2020); UGPA3 2021–25 (Oxiteno e Extrafarma descontinuadas); VBBR3 2020–25 (gestão privada desde jul/2019); UNIP6 2017–25 (Indupa consolidada em dez/2016); SMTO3 2017–26 (exercício abr–mar).
3. **Teste de quebra (medido, nunca automático).** O motor compara a mediana dos **5 últimos exercícios** com a da janela inteira. Divergência acima de **25%** levanta `quebra estrutural SUSPEITA`, que aparece na ficha — mas **a janela não troca sozinha**: "mudança documentada" é julgamento, e trocar sem documento tornaria o central infalsificável.
4. **O teste não se aplica a cíclica.** Lá a janela de 10 anos é obrigatória: usar os 5 últimos anos de uma commodity é pegar exatamente o pico que o §2 proíbe. Em 05/10/2026 os únicos tickers acima dos 25% eram cíclicos (KEPL3 +69,7%, GGBR4 +52,8%, RANI3 +52,4%); entre as não cíclicas o máximo era WEGE3 com +19,9%, seguida de LEVE3 (+11,5%) — nenhuma levanta o alarme. O corte é o **perfil declarado**, não a regra de capex: `capex_ciclico` também é verdadeiro por capex de rede (telecom, distribuição) e desligaria o alarme em empresa de serviço. **Cíclica com quebra contábil (v2.3.1, 08/10/2026):** o item 4 proíbe encurtar a janela pelo *teste* de divergência, não por quebra declarada do item 2. Em E&P a margem é EBITDA do ano − D&A **atual**, e a D&A atual já traz a depreciação do direito de uso: EBITDA pré-IFRS 16 (que desconta o aluguel) contaria o aluguel duas vezes. Logo E&P usa só 2019+ (o motor recusa ano anterior); 7 exercícios cobrem vale (2020) e pico (2022) do Brent — a mesma régua mínima de 7 anos da margem ao preço de meio. O preço de meio da receita continua em 10 anos.

---

## Histórico de versões

| Versão | Data | O que mudou e por quê |
|---|---|---|
| 1.0 | 07/09/2026 | Versão original |
| **2.0** | **04/10/2026** | Auditoria de 04/10 dos 12 PDFs. Ke com vértice fixo, taxa de fechamento e inflação implícita; RF líquida de IR com fórmula correta; uma só coluna de Ke decide (§4) · Filtro 1 separa ROIC×WACC de ROE×Ke; círculo de competência (§2) · Desconto de controlador sempre declarado, inclusive zero (§5) · Defasagem a valor presente pelo Ke; yield sustentável igual para todo setor (§6) · Mesmo defeito, mesmo carimbo (§7) · Régua contínua (fim do buraco de 10–15%), ARMADILHA como carimbo, exceção única de entrada parcial, saída = 1,30 × central, trava de coerência JUSTA ⇒ retorno ≈ Ke (§9) · Pesos 30/20/25/25 e escala única de nota de preço (§10) · Quadro clássico obrigatório com Graham-BR, Bazin calibrado, Lynch, Greenblatt em ranking, Owner Earnings, EPV, DCF reverso, lucro projetado; âncoras por perfil; central = mediana das âncoras (§11) |
| **2.0 (rev.)** | **04/10/2026** | Revisão adversarial no mesmo dia: entrada no hall = 3 dos filtros 1–4, preço só decide a compra (§2) · ROE × Ke **nominal** (§2) · TIR comparada à rf bruta (piso) e ao Ke real, não à RF líquida (§4) · exemplo numérico ilustrativo, sem a base com cupom e o IPCA de 4% (§4) · ordem de precedência régua → círculo → dispersão → carimbos, compra só pela palavra final (§9) · Graham-BR pelo fator f = (1/Ke real)/8,5, já que a escala 4,4/Y nominal subavaliava (§11) · Bazin calibrado vira "teto de renda", **informativo** em todo perfil, com DPA líquido · EPV e Owner Earnings em termos reais · capex de manutenção com piso zero · Bogle sobre LPA normalizado · âncora ≤ 0 = não conclusivo; holding com DDM como 2ª âncora |
| **2.1** | **04/10/2026** | Recálculo do Lote 3 (não financeiras) e revisão adversarial: dívida inclui arrendamento IFRS 16; IR efetivo mediano no WACC; capex de manutenção em cíclica pela mediana de 10 anos de capex/receita (Greenwald só em serviços/industrial); crescimento no DCF só com ROIC > WACC; ganho de valor justo biológico mantido no EBIT e exibido; outras receitas operacionais acima da mediana de 10 anos = não recorrentes (achado: SMTO3 mar/2024 R$ 1,45 bi); regulados com investimento no FCO (ICPC 01): DCF regulatório = P/VP justificado sobre o patrimônio (§2, §11.1, §11.2) · **Complemento 05/10 (Lote 5, Petróleo e Gás, revisão adversarial):** barril de meio de ciclo = média de 10 anos de Brent × câmbio em R$ de hoje; E&P por EBITDA mediano − D&A atual (exaustão do portfólio de hoje), impairment recorrente como custo; distribuidoras por EBIT real (IPCA); ganhos em 3.04.05 tratados como não recorrentes; déficit atuarial fora da ponte quando o custo já está no EBIT; declínio declarado (g < 0) não libera capital; amortização de custo de captação não é D&A (§11.1) · **Complemento 05/10 (Lote 6, Química e Metalurgia):** commodity sem preço em R$/t por API → índice BLS × câmbio em R$ de hoje, declarado como proxy; impairment de cíclica normalizado como no E&P e só descontado de "outras despesas" quando lançado nelas (achado: GGBR4 lança em 3.04.03); custo de transação e AVP de debêntures não são D&A; follow-on depois do balanço soma o caixa ao patrimônio (§11.1, §11.2) · **Complemento 05/10 (Lote 4, Saúde/Telecom/Blue chips):** IFRS 16 — margem só de 2019 em diante quando o arrendamento está na dívida, e Owner Earnings sem o aluguel pago; telecom com capex de rede como manutenção; compounder por DCF em 2 estágios (g real = ROE × retenção por 10 anos, depois ≤ PIB real); SOTP de holding com a participação avaliada pela casa ao central dela no mesmo Ke e custo da holding capitalizado; alíquota com mudança de lei (subvenção de ICMS tributada desde 2024) usa só os anos pós-lei; defasagem do provento a valor presente aplicada no motor (§6.3) (§11.1) |
| **2.2** | **05/10/2026** | **Etapa 2 (F2) do plano de melhorias — coerência do método.** **§11.4 nova (janela do ciclo):** padrão de 10 exercícios pela mediana (o texto dizia "média de 5 anos" e o motor usava a mediana da janela — D8); janela curta só com quebra estrutural declarada por escrito, e o motor mede a divergência de 5 × 10 anos e sinaliza acima de 25% sem trocar a janela sozinho; o teste não vale para cíclica (§2: no ciclo inteiro, não no pico). Sem efeito numérico — nomeia e exige o motivo das janelas que já estavam em uso. **§11.1 capex de manutenção com Δreceita REAL** (IPCA, SGS 433 do BCB desde 1980 — D9): a inflação deixava de virar "crescimento"; declarado que deflacionar não é exigência de Greenwald (o método não trata inflação) e que a fórmula da casa usa imobilizado líquido do exercício, não PPE bruto médio — adaptação, fonte do livro pendente (nota C). Efeito: central de ABEV3 11,13 → 10,50 e de LEVE3 36,76 → 33,99 (pelo Owner Earnings). **§11.1 ROIC a custo de reposição** (idade média ≈ imobilizado líquido ÷ D&A, limitada a 1–15 anos, corrigido pelo IPCA — D10), exibido ao lado do contábil; **o menor dos dois decide o filtro 1 (§2), a nota de Qualidade e a trava do crescimento no DCF**. Efeito: WEGE3 ROIC 29,8% → 18,4% contra WACC 19,1%, central 13,44 → 11,92; UNIP6 (17,7% → 9,4%) −0,9%; PETR4 13,0% → 6,8% e SLCE3 7,9% → 4,5%; nota de qualidade cai em quase todas. **§9 exceção de qualidade na saída (1,50 ×)** com ROIC > WACC a reposição em ≥ 8 de 10 exercícios e Qualidade ≥ 8, base Buffett 1988/1989 (nota A), Fisher como paráfrase (nota C) — decisão do Frank; **só a LEVE3 é elegível** (8 de 10 exercícios e Qualidade 8,005), e a R$ 34,43 nenhuma decisão muda (D7). **§11.1 aluguel pago do IFRS 16 sai do OE em todos os perfis, só o principal**, com o juro estimado pelo saldo × Kd quando a própria empresa declara a linha como "principal e juros" (UGPA3, LEVE3) e limite declarado quando a empresa não reporta o passivo (ABEV3) — fecha a pendência dos Lotes 3/5/6 da Etapa 1; o OE de SMTO3 e SLCE3 fica negativo e o provento deixa de ser coberto. **§6.3 defasagem do provento:** a medida é o padrão e o valor manual só vale com evento declarado e fonte escrita — fecha a pendência do Lote 4 (ABEV3 6 → 1,5 mês; os outros cinco têm calendário declarado e ficam). **Revisão adversarial no mesmo dia:** o ROIC por exercício passou a ser comparado real contra real (§4) — o nominal de 2017 contra o WACC nominal de 2026 invertia a contagem em 8 dos 21 tickers e é o que torna a LEVE3 elegível; a exceção de saída passou a exigir janela de 10 exercícios; o juro do arrendamento passou ao Kd real; o alarme de quebra passou a usar o perfil em vez de `capex_ciclico`; ROIC a reposição vira indefinido sem capital contábil positivo. Nenhuma palavra mudou nos 41 tickers; golden regravado com motivo nas duas rodadas; **76 testes verdes**, 29 deles unitários das regras novas (§2, §6, §9, §11.1, §11.4) |
| **2.3** | **07/10/2026** | **As 6 pendências da Etapa 5 (dossiês), decididas pelo Claude pela doutrina com o "ok" do Frank.** **§2 alíquota por fase, sem piso de 15%:** benefício permanente na mediana; crédito com prazo (ágio, subvenção) com a efetiva só até o fim documentado, em valor presente à parte, e 34% na perpetuidade e no WACC; mediana < 15% sem origem permanente declarada = 34%. Sem esta última regra, tirar o piso **subiria** o central de TIMS3 (mediana 5,4%) e PRIO3 (11,1%), e a PRIO3 iria a JUSTA. Owner Earnings refeito à alíquota perpétua quando ela não é a mediana. Efeito: HYPE3 19,60 → 17,51 (fase até 2030; o benefício incide sobre o lucro depois dos juros e tem teto no crédito observado — revisão do adversário), TIMS3 10,53 → 7,96, PRIO3 55,31 → 43,41, ABEV3 só o OE (9,37 → 7,97). **§5 desconto de controlador só em âncora > 0** (o `x × (1 − desc)` melhorava a negativa) e Ke implícito/DCF reverso contra o valor descontado; sem efeito no golden. **§10 média da regra 11 no motor** (controlador com peso 2 quando discricionário; no hall, provisoriamente onde a interferência consumada está no desconto do lote); nota geral de BBAS3, BRSR6, CMIG4, SAPR11, PETR4 cai 0,04–0,10. **§11.1 outros passivos com juros na dívida líquida** (operacional só na ponte): CMIN3 DL/EBITDA 0,17 → 2,33, ROIC 23,4% → 12,4%, a trava zera o g do DCF e a palavra sai de NÃO CONCLUSIVO para CARA. **§11.1 capex de expansão identificado** (fonte A/B, sem receita) sai antes da regra de manutenção; nenhum ticker usa ainda. **§11.1 margem ao preço de meio** escrita como regra (só cíclica, dossiê, janela ≥ 7). Nenhuma palavra mudou nos 41; a HYPE3 e a CMIN3 ganharam dossiê novo com data-base de 06/10 (registro append-only). O motor reduzido da triagem e do backtest **segue com o piso de 15%** (congelado pelo portão de 06/10), divergência declarada no `06`. 21 testes novos (`tests/test_doutrina_v23.py`) · **Complemento 08/10:** origem do imposto declarada com fonte A — TIMS3 18,3% (JCP fica; SUDENE sem vigência com fonte sai; central 10,11) e PRIO3 com fase até 2032 pelo prejuízo fiscal (central 49,37); dossiê LEVE3 (JUSTA, 35,75): notas por evidência 4/1/2/3/2 levadas ao hall, qualidade 7,1 e **fim da exceção de saída** (nenhum ticker elegível); eventos em ações com GRUPAMENTO (fator = razão) e classe pelo ISIN do ticker |
| **2.3.1** | **08/10/2026** | **Onda 1.1 da auditoria de 08/10 — correção de aplicação, nenhuma regra nova.** Cada achado foi reproduzido antes. **Unidades (§11.1):** a receita de meio padrão, o Owner Earnings e o DPA médio iam nominais para uma taxa real; agora vão a R$ de hoje pelo IPCA antes da média/mediana (AUD-01/16; a doutrina já dizia "em R$ de hoje"). **Provento já ex (§11.1):** a regra da v2.3 vira medição automática em toda não financeira — passivo de proventos do balanço + aprovados depois do balanço e ex até a data do preço (B3) (AUD-02; só a CMIN3 aplicava, à mão). **Follow-on (§11.2):** aplicado ao ISAE4 como no EGIE3 (AUD-04). **IFRS 16 em E&P (§11.4):** E&P só com margem de 2019+; resolve a tensão com o item 4 (AUD-03). Palavras: SUZB3 e ISAE4 CARA → JUSTA; LEVE3 JUSTA → RADAR. Ver `09` |
| **2.4** | **08/10/2026** | **Onda 1.2 da auditoria de 08/10 — Ke, custo da dívida e convenções de mercado; cada achado reproduzido antes.** **§4 Ke pela alavancagem (AUD-12) e §2 pesos no ponto fixo (AUD-13) — decisões do Frank**, entre 3 opções cada, com a tabela de efeito (ver `09`): prêmio = 5 p.p. × [1 + (1 − t) D/E] nas não financeiras, E = valor da casa. **§2 Kd (AUD-07):** RI quando houver; senão rf nominal + spread sintético pela cobertura normalizada (§4.1), no lugar do spread digitado sem fonte. **§2 alíquota (AUD-09):** explícita < 34% só com fonte; mudança de lei restringe a mediana (ABEV3 → 34%). **§4 rf (AUD-06):** taxa de compra da manhã, o rótulo "fechamento" estava errado; rf e π num arquivo só (AUD-78); aviso de idade > 15 dias calculado (AUD-72). **§9 trava (AUD-08)** vira passo 3b. **§11.1 reprodução (AUD-18)** declarada: contábil decide, reposição exibida. Palavras: SMTO3 RADAR → CARA; SUZB3 JUSTA → CARA; LEVE3 e ISAE4 → NÃO CONCLUSIVO (trava); KLBN11 e SLCE3 CARA → NÃO CONCLUSIVO; UNIP6 (fora do hall) → CARA. A triagem e o backtest (motor reduzido congelado) seguem com o Ke fixo de 5 p.p., divergência declarada no `06` |
| **2.5** | **08/10/2026** | **Onda 1.3 da auditoria de 08/10 — decisão e gatilhos; cada achado reproduzido antes.** **§11.2 regulados (AUD-20) — decisão do Frank** entre 3 opções (regra nova, exceção no 09, DCF regulatório de verdade): a condição "investimento no FCO (ICPC 01)" que justificava o P/VP justificado só valia em TAEE11 e ISAE4 (na DFP 2025, SBSP3 tem 6.02.01 −13,7 bi no FCI; CPFE3, CMIG4, SAPR11 e CSMG3 também no FCI; CPLE3 e EGIE3 mistas). Regra nova: sem base regulatória **e** WACC regulatório com fonte A/B, o DCF regulatório é o P/VP justificado como **proxy declarado**, em qualquer posição do investimento; a ficha diz FCO/FCI/misto com as linhas da DFC (`lote2_energia.REGULADOS_DFC`, testado contra o ZIP da CVM); base nota C só informativa. Nenhum central muda. **§9 aplicada fora do motor (sem regra nova):** o monitor semanal e o `03` não dão compra nem saída a NÃO CONCLUSIVO (AUD-43, AUD-77). Ver `09` |
| **2.6** | **10/10/2026** | **Onda 3 da auditoria de 08/10 — riscos latentes; decisões do Frank em 10/10, cada achado reproduzido antes.** **§9 trava (AUD-10)** na palavra final. **§11 DCF:** declínio com ROIC < WACC sem liberação de capital (AUD-34) e cenário negativo como zero (AUD-53); **OE pelo lucro do controlador** (AUD-15). **§9 entrada parcial** numa função só do motor, com as cinco condições e o preço (AUD-42; os PDFs testavam subconjuntos). Textos alinhados ao motor: trava do crescimento é degrau por cenário (AUD-14), Solidez sem Piotroski/Beneish (AUD-39), carimbo do Tesouro pelo ponto médio (AUD-40), defasagem da Vibra 8,5 meses (AUD-55). **Nenhuma palavra mudou nos 41**; mudam âncoras OE (ABEV3 7,34 → 7,04; WEGE3 11,76 → 11,08; UGPA3 9,11 → 8,69), o central da KLBN11 (1,72 → 2,62, segue NÃO CONCLUSIVO), SUZB3 (22,04 → 22,78), RANI3 (3,11 → 3,19) e RECV3 (−3,67 → 0, segue NÃO CONCLUSIVO, sem preço de compra/saída). Ver `09` (10/10/2026) |
| 2.6.1 | 21/10/2026 | Só os casos da casa do §7 (e o exemplo do §6): ano e fonte CVM/EIA em cada um, números refeitos (Unipar 270% em 2025; Mahle ROE 70%/ROIC ~33%; Vibra +277% é o 2T26; "UBP de 2024" era a venda da TAG). Nenhuma regra nem carimbo mudou (PENDENTE #9, ok do Frank) |
