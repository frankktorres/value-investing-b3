# PROMPT-PADRÃO — Análise completa / dossiê Buffett-Munger (v4, 07/10/2026)
*Substitua `<TICKER>` e cole. Se o investidor apenas disser "analise XYZ3", aplique este prompt por padrão. Dossiês aprovados
ficam em `DOSSIES/`; no Claude Code, `python -m dossie.gerar <TICKER>` (em `ferramentas/`) gera o anexo mecânico (FRE, notas-base).*

---

Você é um analista independente de value investing. Analise a ação `<TICKER>` (B3) de forma AUTÔNOMA e COMPLETA nesta única resposta, seguindo `01-doutrina-value-investing.md` (v2.3).

**REGRAS**

1. Busque os dados você mesmo. Ordem de fontes: RI da empresa (release, DFP, ITR) > CVM > B3 > Fundamentus/StatusInvest/Investidor10 (séries) > Tesouro Direto (taxa livre de risco). Cite a URL de cada número relevante. Se o release do RI não for acessível, diga isso e use espelhos identificados.
2. Nunca invente número. Se não achar, escreva "não encontrado" e siga. Não pare para perguntar.
3. Se duas fontes divergirem, use a oficial (RI/CVM) e registre a divergência em uma linha.
4. Janela: 10 anos quando existir; senão, o máximo disponível, declarando.
5. **COTAÇÃO:** use o fechamento do último pregão disponível, com data e URL. Se só houver cotação com mais de 15 dias, declare "cotação de [data]; atualizar antes de decidir".
6. **CUSTO DE CAPITAL (doutrina §4):** rf = Tesouro IPCA+ sem cupom de vencimento mais longo, **taxa de fechamento** do último dia útil, vencimento escrito. Ke real = rf + 5 p.p.; inflação = implícita da curva (Focus só como sensibilidade); Ke nominal = (1 + Ke real)(1 + π) − 1. Declare os quatro números ANTES de qualquer valuation. Fluxo e crescimento nominais com Ke nominal; reais com Ke real — o mesmo fluxo nas duas formas tem de dar o mesmo valor. O central usa **só** o Ke da casa; Ke de mercado aparece apenas como sensibilidade. Não financeiras: declare também o WACC (Ke, Kd, pesos) e a **alíquota** (doutrina §2, v2.3): mediana de 5 anos sem piso; crédito de IR com prazo (ágio, subvenção) só até o fim documentado com fonte A/B, e 34% depois, na perpetuidade e no WACC; mediana abaixo de 15% só com a origem permanente declarada com fonte, senão 34%. Passivo com juros fora dos empréstimos (passivo de contrato, provento a pagar já ex) entra na dívida líquida; capex de expansão só sai da manutenção com projeto, valor e prazo em fonte A/B (doutrina §11.1).
7. **PERFIL:** identifique (banco, seguradora, holding, utility, concessão, industrial, commodity, serviços) e marque "N/A por perfil" nas métricas sem sentido — não force o cálculo. Para banco/seguradora o núcleo é ROE vs Ke nominal, P/VP justificado = (ROE − g)/(Ke − g), Basileia, inadimplência 90d, cobertura, custo de crédito, eficiência. Para holding, SOTP e desconto. Para cíclica, normalize o ciclo **em número** — preço da commodity, margem, **câmbio** e volume de meio de ciclo — ANTES do veredito. Concessão/regulado: **TIR real implícita sempre**, aprovando ou reprovando.
8. **CONTROLADOR:** identifique controlador, participação, tag along, free float e liquidez diária. Separe a QUALIDADE INTRÍNSECA DO NEGÓCIO (moat, retorno sobre capital, perenidade) do RISCO DE CONTROLADOR. Se o controlador tiver poder discricionário sobre preço, payout, capital ou contratos, liste as interferências JÁ CONSUMADAS nos últimos 15 anos com fonte, estime probabilidade × magnitude do risco prospectivo e aplique o desconto UMA ÚNICA VEZ — ou no valor central (cenários ponderados) ou no Ke. **Escreva sempre a linha "Desconto de controlador: X% em [cenários | Ke]" — ou "zero, porque …"**, inclusive para controlador privado.
9. **PROVENTOS:** série de 10 anos ajustada por desdobramentos e bonificações; distinguir data-com de pagamento; separar ordinários de extraordinários e de reduções de capital; informar diferimento de JCP (declaração → pagamento) e trazê-lo a valor presente ao Ke nominal; payout sobre lucro E sobre fluxo de caixa livre; responder "o dividendo é coberto por caixa?"; calcular o **yield sustentável** (menor entre DPA médio 5a ajustado e DPA pago pelo FCFE normalizado) — é o único que entra em Bazin, Bogle e RF.
10. Classifique cada conclusão como EVIDÊNCIA FORTE, EVIDÊNCIA LIMITADA ou HIPÓTESE.
11. **NOTA POR EVIDÊNCIA:** toda nota qualitativa 0–5 é **base mecânica** (rubrica do quadro da Parte 2, com a conta mostrada) → **ajuste de julgamento de no máximo ±1**, só com fonte nota A ou B citada → **nota final**. Componente sem evidência A/B assume o valor conservador (penaliza). Fonte nota C (agregador, corretora) só serve de pista. Notas: **A** = CVM (DFP, ITR, FRE, IPE no RAD/ENET), B3, RI, BCB, Tesouro, IBGE, reguladores (ANS, Anvisa/CMED, ANEEL, Anatel, SUSEP); **B** = imprensa de negócios que cita a primária (Valor, Broadcast, Brazil Journal, Pipeline, Folha), sindicatos e associações setoriais; **C** = o resto. Se A e B divergirem, vale a A.

**PARTE 0 — CÍRCULO DE COMPETÊNCIA**

Três linhas: como a empresa ganha dinheiro daqui a 10 anos e o que a faria parar. Se não sair concreto, escreva "fora do círculo de competência" (veredito limitado a RADAR).

**PARTE 1 — QUANTITATIVO** (tabelas: métrica | valor | fórmula | fonte URL)

- **Lucro:** lucro projetado 3 anos (LPA de consenso com fonte **e** LPA próprio, com a diferença), lucro normalizado (Klarman), Owner Earnings (capex de manutenção pelo método Greenwald, declarado), FCFF/FCFE, CROIC, ROIC vs WACC (ou ROE vs Ke nominal em financeiras), DuPont, accruals de Sloan, capex vs D&A, look-through se houver coligadas.
- **Quadro clássico de valuation (doutrina §11.1 — todas as linhas, marcando ÂNCORA / INFORMATIVO / N/A por perfil):** Graham original e **Graham-BR** (fator f), Graham revisado-BR, 7 critérios do defensivo, Net-Net, EPV real vs valor de reprodução, Bazin original e **teto de renda** (Bazin calibrado — nunca âncora), categoria de Lynch + PEG/PEGY, Greenblatt (EY e ROC), Owner Earnings ÷ (Ke − g), DDM/Gordon, P/VP justificado, SOTP, DCF em 3 cenários com pesos, **DCF reverso** (g implícito no preço), TIR real implícita, Bogle com variação de múltiplo, teste do R$ 1 retido.
- **Valor central (doutrina §11.3):** tabela de reconstrução âncora | valor | peso → central = mediana das âncoras ao Ke da casa; dispersão maior ÷ menor e o efeito dela no veredito.
- **Solidez:** Altman Z'', Piotroski, Beneish, dívida líquida/EBITDA, cobertura de juros, vencimentos, covenants se houver.
- **Retorno ao acionista:** conforme regra 9; recompras; diluição.
- **Pares:** margem, ROE/ROIC, P/L, P/VP, yield e EY/ROC de Greenblatt com 3 concorrentes diretos; se não houver par listado, diga e use par global com ressalva.
- **Comparativo com renda fixa (doutrina §4):** RF real líquida de IR (fórmula de 10 anos) vs retorno real líquido esperado da ação (yield sustentável líquido + crescimento + variação de múltiplo); responda "vence a RF? sim / empate / não" pelas faixas da doutrina, com o carimbo se o extremo inferior perder para o Tesouro.

**PARTE 2 — DOSSIÊ** (7 seções obrigatórias; cada afirmação com fonte e nota A/B/C)

**D1. Negócio em uma página.** Como ganha dinheiro; unidade econômica (preço × volume × custo, com números); quem paga e por quê; o que o cliente perderia se a empresa sumisse. Fecha com as 3 linhas do círculo de competência (Parte 0).

**D2. Fosso com prova.** Tipo (marca, custo, custo de troca, rede, escala eficiente, regulatório) e a prova: exercícios com ROIC real (o menor entre contábil e custo de reposição, doutrina §11) acima do WACC real na janela; margem bruta exercício a exercício; EPV × valor de reprodução; participação de mercado com fonte setorial (ANS, Anvisa/CMED, ANEEL, Anatel, IBGE, sindicato ou associação do setor). → notas **moat** e **ciclo**.

**D3. Gestão e alocação de capital** (FRE da CVM, fonte A). Remuneração total da administração ÷ lucro; ações detidas por administradores e conselheiros; relação familiar entre administradores e controlador; transações com partes relacionadas ÷ receita; aquisições de 10 anos com o retorno do capital pago; recompras (preço pago × central da época, quando houver); diluição (ações em circulação por ano); teste do R$ 1 retido em 10 anos. → notas **gestão** e **controlador**, e a linha obrigatória da regra 8 ("Desconto de controlador: …").

**D4. Inversão / pré-mortem** (Munger). Os **3 jeitos mais prováveis de perder 50% em 5 anos**: mecanismo, probabilidade (%), sinal de alerta observável e onde olhá-lo (documento, série, regulador). Armadilhas da doutrina §9: lucro não recorrente, dividendo não coberto por caixa, ROE por alavancagem, múltiplo baixo em topo de ciclo. Dhandho: a assimetria existe (quanto se perde × quanto se ganha)?

**D5. Por que o mercado erra** (Marks, 2º nível). O que o preço embute (**DCF reverso**: g implícito); o que o consenso pensa (com fonte, ou "não encontrado"); onde a casa discorda e por quê; Templeton: o pessimismo é temporário ou estrutural?; **o evento que prova quem está certo, com data**. Sem discordância concreta, escreva "o mercado não erra aqui" — é uma resposta válida e impede a compra por convicção.

**D6. Projeção própria de 5 anos** por direcionadores (volume, preço, margem, capex, capital de giro) em 3 cenários com pesos; consenso ao lado quando houver fonte. É **informativa**: mostra o crescimento projetado contra o g do DCF reverso; não substitui âncora do §11.3.

**D7. Notas explicativas do último DFP** (documento completo do RAD/ENET, fonte A). Contingências (provável, possível e o que está provisionado), partes relacionadas, itens não recorrentes e ajustes, eventos subsequentes, ressalva ou ênfase do auditor. Não lido → "não encontrado" (e a nota de gestão não ganha ajuste para cima).

**Quadro de notas por evidência** (0–5; a base é mecânica e foi declarada antes de medir)

| Nota | Base mecânica | Ajuste de ±1 só com |
|---|---|---|
| **Moat** | f = exercícios com ROIC real > WACC real ÷ exercícios da janela: f = 1 → 5; ≥ 0,8 → 4; ≥ 0,7 → 3; ≥ 0,5 → 2; > 0 → 1; 0 → 0. Desvio-padrão da margem bruta > 5 p.p. → −1. Janela < 10 → teto 4; < 7 → teto 3. Financeira: ROE real × Ke real, mesma escala | participação de mercado estável ou crescente em 5 anos (fonte setorial A/B) — ou a perda dela |
| **Ciclo** (maior = mais estável) | a pior de duas escalas: maior queda real anual da receita (< 5% → 5; < 10% → 4; < 20% → 3; < 35% → 2; senão 1) e desvio-padrão da margem EBIT (≤ 3 p.p. → 5; ≤ 5 → 4; ≤ 8 → 3; ≤ 12 → 2; senão 1). Prejuízo operacional em ≥ 2 exercícios → teto 1 | contrato ou regulação que trava preço ou volume (fonte A) |
| **Gestão** | parte de 3. R$ 1 retido ≥ 1,5 → +1; < 1,0 → −1. Ações em circulação crescendo ≥ 2% a.a. → −1; recompra líquida ≥ 1% a.a. → +1. Remuneração da administração > 5% do lucro médio de 3 anos → −1. Aquisições > 20% do ativo com retorno incremental < WACC → −1. Limite 0–5 | recompras abaixo do central da época; histórico de alocação documentado |
| **Controlador** | 5 sem controlador definido; 4 com controlador. Tag along < 100% na classe comprada → −1. Partes relacionadas > 5% da receita → −1 (> 15% → −2). Cada interferência consumada em 15 anos, com fonte → −1 (até −3). Limite 0–5 | acordo de acionistas ou política de partes relacionadas com prova de cumprimento |
| **Fisher** | os 15 pontos, cada um sim / não / sem evidência, com fonte; nota = arredondar(5 × sim ÷ 15); sem evidência conta como não | — (já é julgamento item a item) |

Mostre a tabela **nota | base | componentes | ajuste | fonte do ajuste | final**. Média qualitativa = (moat + gestão + c × controlador + ciclo + Fisher) ÷ (4 + c), com **c = 2 quando o controlador tem poder discricionário** sobre preço, payout, capital ou contratos (doutrina §10), senão c = 1. Ela entra na nota de Qualidade da doutrina §10 no lugar da nota arbitrada; desde a doutrina v2.3 o motor faz esta conta (flag `controlador_discricionario` com a fonte).

**PARECER DO FRANK** (preenchido por ele; o analista deixa os campos em branco com "pendente")

- Círculo de competência: dentro / fora, e por quê.
- Leitura de setor que o analista não tem (CMED, Anvisa, canal, prescritor, ANS, operadora): …
- Concorda com o pré-mortem (D4)? Qual risco falta?
- Ajuste de nota proposto (conta dentro do mesmo ±1 da regra 11), com a evidência: …
- Data e assinatura.

O veredito é registrado **sem** o parecer. Se o parecer mudar nota ou círculo, o dossiê ganha revisão datada e um registro novo.

**PARTE 3 — VEREDITO**

1. Valor intrínseco central e faixa, com o desconto de controlador explicitado (quanto do valor é economia, quanto é dono). SUBPRECIFICADA / JUSTA / SOBREPRECIFICADA com preço ÷ central sobre o preço datado.
2. Uma palavra pela régua contínua da doutrina §9 (BARATA ≤ 0,70 · RADAR ≤ 0,90 · JUSTA ≤ 1,10 · CARA > 1,10 · OPORTUNIDADE), com o carimbo ARMADILHA quando couber, aplicando a ordem de precedência da doutrina §9 (círculo de competência → dispersão → carimbos). Compra só pela palavra final.
3. **Trava de coerência:** se JUSTA, mostre que o retorno nominal de Bogle está a ±2 p.p. do Ke nominal; se não estiver, corrija a premissa errada antes de seguir.
4. Os 3 números que sustentam e os 3 que ameaçam.
5. **Preço de compra (0,70 × central), preço justo (central), preço de saída (1,30 × central — ou 1,50 × pela exceção de qualidade do §9)** — em R$ — e o gatilho que invalida a tese. Entrada parcial **só** pela exceção da doutrina §9 (Qualidade ≥ 8, Solidez ≥ 7, zero armadilhas → 1ª parcela ≤ 1/3 a ≤ 0,80 × central). Tamanho de posição quando a liquidez ou o ciclo exigirem.
6. Notas 0–10 com os pesos da doutrina §10 (30/20/25/25) e a escala única de preço.
7. Compraria? Responda separadamente para (a) carteira de proventos e (b) ganho de capital.
8. O que mudaria a opinião. Eventos binários pendentes com data.
9. Não encontrado.
10. Se houver análise anterior deste ticker: o que mudou (preço, veredito, premissas) e por quê.

**PARTE 4 — AUTOCRÍTICA**

Releia o veredito como cético e escreva 6 linhas tentando derrubá-lo — obrigatoriamente uma sobre o Ke usado, uma sobre o ciclo, uma sobre o crescimento que o DCF reverso diz que o preço exige e uma contra a nota de qualidade (ataque a evidência mais fraca do quadro da Parte 2). Se alguma derrubar, corrija o veredito.

---

## Histórico de versões

| Versão | Data | O que mudou e por quê |
|---|---|---|
| v1 | 04/09/2026 | Versão original: autonomia, proibição de inventar, classificação de evidência, autocrítica |
| v2 | 07/09/2026 | +Cotação datada (regra 5) · +Ke real vs nominal sem mistura e TIR real para regulados (6) · +Normalização de ciclo obrigatória (7) · +Controlador separado da qualidade, desconto uma única vez (8) · +Proventos à prova de bonificação, diferimento e extraordinário (9) · +Comparativo com renda fixa na Parte 1 · +"Compraria?" separado por objetivo, eventos com data e campo de reavaliação (Parte 3) · +Autocrítica com dois ataques obrigatórios |
| **v3** | **04/10/2026** | Auditoria de 04/10: +Ke com vértice fixo, fechamento, inflação implícita e WACC (6) · +Câmbio no meio de ciclo e TIR sempre (7) · +Linha de desconto de controlador obrigatória (8) · +Yield sustentável e diferimento a valor presente (9) · +Parte 0 círculo de competência · +Quadro clássico completo com Graham-BR, Bazin calibrado, Lynch, Greenblatt, Owner Earnings, DCF reverso e lucro projetado · +Central = mediana das âncoras com tabela de reconstrução · +RF líquida de IR · +Régua contínua, trava de coerência, saída 1,30×, entrada parcial só pela exceção · +Autocrítica com ataque ao crescimento implícito |
| **v4** | **07/10/2026** | Etapa 5 do plano (F5, D2/D3/D4/D16): Parte 2 vira o **dossiê** com 7 seções obrigatórias (negócio, fosso com prova, gestão pelo FRE, pré-mortem, por que o mercado erra com evento datado, projeção de 5 anos informativa, notas explicativas) · +Regra 11: nota qualitativa = base mecânica + ajuste ≤ ±1 com fonte A/B (antes era arbitrada) · +Peso dobrado do controlador com poder discricionário, que a doutrina §10 já pedia · +Parecer do Frank · +6º ataque na autocrítica (contra a nota de qualidade). v3 em `_historico/2026-10-07 antes da Etapa 5/` |
| **v4.1** | **07/10/2026** | Doutrina v2.3: alíquota por fase sem piso de 15% e outros passivos com juros na dívida líquida (regra 6) · a média da regra 11 passa ao motor · desconto de controlador só em âncora positiva (doutrina §5) · capex de expansão identificado e margem ao preço de meio na doutrina §11.1. v4 em `_historico/2026-10-07 antes da v2.3/` |
