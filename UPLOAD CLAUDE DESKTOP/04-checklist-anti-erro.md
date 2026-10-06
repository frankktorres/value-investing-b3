# CHECKLIST ANTI-ERRO (v2, 04/10/2026)
*Rodar integralmente antes de fechar qualquer análise ou reavaliação. Cada item aqui já foi um erro cometido nesta mesa.*

---

## A. Dados e fontes

- [ ] **Cotação tem data?** Se tiver mais de 15 dias, escrevi "atualizar antes de decidir"?
  *Erro cometido: 12 das 35 primeiras análises usaram preço de julho em setembro.*
- [ ] Tentei o RI primeiro? Se não abriu, **declarei isso** e identifiquei o espelho?
- [ ] Todo número relevante tem URL?
- [ ] Duas fontes divergiram? Usei a oficial e **registrei a divergência em uma linha**?
  *Padrão frequente: HG/Renova/Investidor10 divergem em P/VP e market cap por misturar classes de ações ou base pré-evento.*
- [ ] Escrevi "não encontrado" onde não achei, em vez de estimar sem avisar?
- [ ] Nenhuma métrica foi copiada "da ficha anterior" sem recalcular (Piotroski, Altman, Graham com LPA velho)?
  *Erro cometido: Piotroski 9/9 de HYPE3 e FLRY3 "da ficha"; Graham de FLRY3 com o LPA antigo.*

## B. Custo de capital

- [ ] A rf é o **Tesouro IPCA+ sem cupom de vencimento mais longo**, taxa de **fechamento**, vencimento escrito — e é **a mesma em todos os lotes do dia**?
  *Erro cometido: 03/10 usou IPCA+ 2050 em Energia e Bancos e 2060 em Química e Petróleo; taxa intradiária da véspera da eleição.*
- [ ] Declarei Ke real, **inflação implícita da curva** e Ke nominal **antes** do primeiro valuation?
  *Erro cometido: IPCA de 4% abaixo do Focus (4,99% / 4,31%), inflando o retorno real.*
- [ ] **Não misturei** fluxo ou crescimento em reais correntes com taxa real? O mesmo fluxo nas duas formas dá o mesmo valor?
  *Erro cometido: "DCF a Ke real" ~35% acima do nominal em Química, Saúde e Agro; WEGE3 com g 12% nominal a Ke real.*
- [ ] **O central saiu da coluna do Ke da casa?** Ke de mercado só como sensibilidade?
  *Erro cometido: ITUB4 e PSSA3 a "Ke mercado 14%"; BBSE3, CXSE3, PRIO3, RECV3, UGPA3, VBBR3 na coluna real.*
- [ ] Não financeira: declarei **WACC** (Ke, Kd, pesos) e comparei **ROIC × WACC**? Financeira: **ROE × Ke nominal**? EPV e Owner Earnings em termos **reais** (WACC real, R$ de hoje)?
- [ ] É concessão ou regulado? Calculei a **TIR real implícita — mesmo que aprove** — e comparei com a rf bruta (piso) e com o Ke real?
  *Este teste reprovou a Taesa (6,5% < 7,35%). Erro cometido: TIR usada só quando reprovava (TAEE11, ISAE4), omitida em SBSP3 e CSMG3.*
- [ ] Registrei a sensibilidade quando o Ke da régua penaliza um ativo de risco baixo?

## C. Ciclo (cíclicas, commodities, distribuidoras)

- [ ] **Declarei a premissa de meio de ciclo em número ANTES do veredito?** (commodity, margem, **câmbio**, volume)
  *Erro cometido: petróleo sem câmbio de meio de ciclo; KLBN11 trocou EBITDA de 9 para 8 bi sem declarar.*
- [ ] O múltiplo baixo é de lucro no pico? (Vibra: margem +300% a/a; Petrobras: Brent 104)
- [ ] O múltiplo alto é de lucro no fundo? (Unipar: P/L 18 no fundo; Gerdau: 26,7 → 14,6)
- [ ] Usei o **valor de reprodução** e o **EPV de meio de ciclo** como âncoras, já que o lucro do ano não serve?
- [ ] Graham calculado com **lucro normalizado**, não de pico?
  *Erro cometido: LEVE3 com LPA de pico 5,14 (normalizado 4,3).*
- [ ] Nenhum cenário "normalizado" soma trimestre de topo?
  *Erro cometido: PETR4 base com "+1 tri de topo".*

## D. Proventos — o bloco onde mais se erra

- [ ] **Ajustei por bonificação e desdobramento?**
  *Sabesp: agregadores mostravam 12–13%; o real era 2,4%. Engie: mostravam 5–8%; o real era 3,4%.*
- [ ] Separei **data-com de pagamento**?
- [ ] Medi a **defasagem declaração → pagamento** e trouxe a **valor presente pelo Ke nominal**?
  *Hypera 12–18 meses · Vibra 15–18 · TIM e Vivo ~12 · Fleury parcela até 2 anos · Gerdau 7–31 dias · Unipar 9–11 dias.*
- [ ] Separei **ordinário, extraordinário e redução de capital**?
- [ ] Calculei o payout sobre **lucro E sobre FCFE**?
- [ ] **Respondi textualmente: "o dividendo é coberto por caixa?"**
- [ ] Usei o **yield sustentável** (menor entre DPA médio 5a e DPA pago pelo FCFE) — **igual em todo setor**?
  *Erro cometido: Química usou o sustentável; Energia usou o declarado com parte paga por dívida (TAEE11, CPFE3, CPLE3).*
- [ ] Teto de renda (Bazin calibrado: DPA líquido ÷ RF nominal líquida) só com "coberto = sim" e **nunca como âncora**? Bazin 6% só como informativo?

## E. Controlador

- [ ] Identifiquei controlador, participação, **tag along**, free float e liquidez diária?
- [ ] Avaliei a **qualidade do negócio separadamente** do risco de controlador?
- [ ] Listei as interferências **já consumadas** (15 anos, com fonte) — ou escrevi "nenhuma identificada"?
- [ ] Escrevi a linha **"Desconto de controlador: X% em [cenários | Ke]" — ou "zero, porque …"**, inclusive para controlador privado?
  *Erro cometido: CXSE3, SANB11, HYPE3, VIVT3, ABEV3, FLRY3 sem linha; SAPR11 sem dizer onde entrou o haircut.*
- [ ] Apliquei o desconto **uma única vez**, sem voltar a descontar o retorno esperado?
  *Erros cometidos: risco político no texto e no gatilho, mas não no número (Cemig, Petrobras); ou no número e de novo no qualitativo (BBSE3, CXSE3); CMIG4 com cenários 40/60 e retorno "ponderado" descontado de novo.*
- [ ] **Teste de coerência:** estou tratando o mesmo defeito da mesma forma em todas as empresas?
  *Erro cometido: KLBN11 (payout 126%, FCF negativo) JUSTA; UNIP6 pelo mesmo defeito ARMADILHA.*

## F. Qualidade do lucro e quadro clássico

- [ ] Comparei lucro **contábil vs ajustado**? De onde vem a diferença?
  *Câmbio (Mahle, Suzano), IAS 29 (Argentina), evento societário (Engie/UBP), crédito fiscal (Unipar, Fleury), venda de ativo (Klabin).*
- [ ] ROE alto vem de **alavancagem**? Calculei o **ROIC** e usei ele no comparativo?
- [ ] Comparei ROIC com o WACC — e no **meio do ciclo**, não só hoje?
- [ ] Accruals de Sloan: o lucro está acima ou abaixo do caixa? Por quê?
- [ ] **O quadro clássico (doutrina §11.1) está completo**, cada linha com valor, fórmula e ÂNCORA / INFORMATIVO / N/A?
  *Erro cometido: rev. 03/10 com zero menções a Graham, Bazin, EPV e Piotroski em Bancos, Energia, Agro e Petróleo; Owner Earnings, Sloan, Beneish e Lynch nunca entregues.*
- [ ] **Lucro projetado 3 anos** (consenso com fonte **e** próprio)?
  *Erro cometido: só 3 de 41 fichas tinham LPA forward, todas de terceiros.*
- [ ] **DCF reverso** feito — qual crescimento o preço exige?
- [ ] Bogle inclui a **variação de múltiplo** e não soma recompra que já está no g?
  *Erro cometido: WEGE3 a P/L 34 com g 12% por 10 anos sem compressão de múltiplo; TIMS3 e B3SA3 somando recompra ao yield e ao g.*
- [ ] g perpétuo ≤ g sustentável (ROE × retenção) e ≤ PIB nominal de longo prazo?
  *Erro cometido: CXSE3 g 9,5%; BRBI11 g 5–7% com payout 85% (sustentável ~2,6%).*

## G. Veredito

- [ ] **Valor central = mediana das âncoras ao Ke da casa**, com tabela de reconstrução? Nenhum "anterior × fator", "+8 −2 +1" ou número redondo?
  *Erro cometido: centrais de 03/10 por fator de Ke (Saúde, Química), ajustes em R$ (Energia) e números "mantidos" (SUZB3 55, RANI3 10, KEPL3 8).*
- [ ] Dispersão das âncoras calculada? > 1,8× rebaixou um nível? > 3× = não conclusivo?
- [ ] As quatro armadilhas foram verificadas uma a uma?
- [ ] A palavra respeita a **régua contínua**? (≤ 0,70 BARATA · ≤ 0,90 RADAR · ≤ 1,10 JUSTA · > 1,10 CARA) ARMADILHA só como carimbo?
  *Erro cometido: ISAE4 +12% CARA e CPLE3 +13% JUSTA; PETR4 +17% JUSTA; BRSR6 +50% e UNIP6 P/L 24 como ARMADILHA.*
- [ ] Apliquei a **ordem de precedência** (régua → círculo de competência → dispersão/âncora ≤ 0 → carimbos) e só autorizei compra pela **palavra final**?
- [ ] A empresa passa **3 dos filtros 1–4** (senão sai do hall)?
- [ ] **Trava de coerência:** se JUSTA, o retorno de Bogle está a ±2 p.p. do Ke nominal?
  *Erro cometido: ITUB4, BBSE3, PSSA3, ABCB4 JUSTA com retorno nominal 12–15% vs Ke 16,6%; BBAS3 JUSTA com retorno real 4,3%.*
- [ ] Dei preço de compra (0,70×), justo, **saída (1,30× — ou 1,50× pela exceção de qualidade do §9)** e gatilho de invalidação?
  *Erro cometido: saídas de 1,17× a 2× sem regra, paradas quando o justo mudava.*
- [ ] Entrada parcial **só** pela exceção escrita (Qualidade ≥ 8, Solidez ≥ 7, zero armadilhas; ≤ 1/3 a ≤ 0,80×)?
  *Erro cometido: "aceitável/1ª parcela" com margem de 10–22% em ITUB4, TIMS3, GGBR4, KEPL3, CSMG3 e outros.*
- [ ] Notas pelos pesos 30/20/25/25 e pela **escala única** de preço?
- [ ] Respondi **separadamente** para carteira de proventos e para ganho de capital?
- [ ] Fiz o comparativo com a **RF real líquida de IR** (fórmula de 10 anos) e classifiquei pelo ponto médio?
  *Erros cometidos: "rf × 0,85" como atalho; RANI3 "Empate" com retorno abaixo do Tesouro; PRIO3 "Não" com ponto médio de empate.*
- [ ] Ajustei o **tamanho de posição** à liquidez e à ciclicidade?
- [ ] Se há análise anterior: registrei **o que mudou e por quê**, com preço anterior da **data da ficha anterior**?
  *Erro cometido: Energia e Petróleo compararam com preços de julho/agosto chamando de "ficha de 07/09".*

## H. Autocrítica

- [ ] Escrevi as 5 linhas céticas, com **uma obrigatória sobre o Ke**, **uma sobre o ciclo** e **uma sobre o crescimento implícito (DCF reverso)**?
- [ ] Se alguma linha derrubou o veredito, **corrigi de fato** — em vez de só registrar?
- [ ] Não mudei de ideia por pressão do interlocutor, apenas por mérito do argumento?

---

## Erros históricos desta mesa (para não repetir)

| # | Erro | Onde | Correção que virou regra |
|---|---|---|---|
| 1 | DY de agregador sem ajuste de bonificação | Sabesp, Engie | Regra 9 do prompt |
| 2 | Risco de controlador no texto, não no número | Cemig, Petrobras | Regra 8 + revisão de 07/09 |
| 3 | Mesmo defeito, veredito diferente | BRSR6 vs CMIG4; KLBN11 vs UNIP6 | Teste de coerência (bloco E) |
| 4 | Cotação desatualizada sem aviso | 12 análises | Regra 5 |
| 5 | Ke real descontando fluxo nominal | várias; WEGE3 e "DCF a Ke real" em 03/10 | Regra 6; doutrina §4 |
| 6 | Múltiplo de topo de ciclo tratado como barganha | Vibra, Petrobras | Regra 7 |
| 7 | Triagem preliminar tratada como conclusão | LEVE3 (7/7 → JUSTA/CARA), UNIP6 (5/7 → ARMADILHA) | Triagem define fila, não veredito |
| 8 | Rótulo "estatal" sem interferência consumada | BBSE3, CXSE3, CPFE3 | Vetores V1–V6 da doutrina |
| 9 | Quadro clássico abandonado na reavaliação | 4 dos 6 lotes de 03/10 | Prompt 05 v2 §4; bloco F |
| 10 | Valor central caixa-preta (fator de Ke, ajuste em R$, número redondo) | rev. 03/10, todos os lotes | Doutrina §11.3; bloco G |
| 11 | Central calculado a Ke diferente do declarado | ITUB4, PSSA3, BBSE3, CXSE3, PRIO3, RECV3, UGPA3, VBBR3 | Doutrina §4 "uma só coluna decide" |
| 12 | Régua com buraco 10–15% e ARMADILHA fora da definição | ISAE4 × CPLE3 × ABEV3; PETR4; BRSR6; UNIP6 | Régua contínua (doutrina §9) |
| 13 | JUSTA com retorno esperado abaixo do Ke | Bancos e seguradoras de 03/10 | Trava de coerência |
| 14 | Compra "aceitável" sem margem de segurança | 15+ fichas | Exceção única de entrada parcial |
| 15 | Saída sem regra | todos os lotes | Saída = 1,30 × central; 1,50 × só com ROIC > WACC a custo de reposição em ≥ 8 de 10 exercícios e Qualidade ≥ 8 (§9) |
| 16 | Vértice da rf trocado entre lotes; taxa intradiária; IPCA abaixo do mercado | rev. 03/10 | Doutrina §4 |
| 17 | Yield declarado (pago com dívida) no lugar do sustentável | Energia 03/10 | Doutrina §6 |
| 18 | TIR real usada só quando reprova | TAEE11/ISAE4 × SBSP3/CSMG3 | TIR sempre (regra 7) |
