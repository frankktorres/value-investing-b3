# CHECKLIST ANTI-ERRO
*Rodar integralmente antes de fechar qualquer análise. Cada item aqui já foi um erro cometido nesta mesa.*

---

## A. Dados e fontes

- [ ] **Cotação tem data?** Se tiver mais de 15 dias, escrevi "atualizar antes de decidir"?
  *Erro cometido: 12 das 35 primeiras análises usaram preço de julho em setembro.*
- [ ] Tentei o RI primeiro? Se não abriu, **declarei isso** e identifiquei o espelho?
- [ ] Todo número relevante tem URL?
- [ ] Duas fontes divergiram? Usei a oficial e **registrei a divergência em uma linha**?
  *Padrão frequente: HG/Renova/Investidor10 divergem em P/VP e market cap por misturar classes de ações ou base pré-evento.*
- [ ] Escrevi "não encontrado" onde não achei, em vez de estimar sem avisar?

## B. Custo de capital

- [ ] Declarei o Ke real **antes** do primeiro valuation?
- [ ] Declarei o IPCA assumido e o Ke nominal equivalente?
- [ ] **Não misturei** fluxo em reais correntes com taxa real?
- [ ] É concessão ou regulado? Calculei ou citei a **TIR real implícita** e comparei com o IPCA+?
  *Este teste reprovou a Taesa (6,5% < 7,35%) — sem ele, ela passaria por "boa pagadora".*
- [ ] Registrei a sensibilidade quando o Ke da régua penaliza um ativo de risco baixo?

## C. Ciclo (cíclicas, commodities, distribuidoras)

- [ ] **Declarei a premissa de meio de ciclo ANTES do veredito?** (commodity, margem, câmbio, volume)
- [ ] O múltiplo baixo é de lucro no pico? (Vibra: margem +300% a/a; Petrobras: Brent 104)
- [ ] O múltiplo alto é de lucro no fundo? (Unipar: P/L 18 no fundo; Gerdau: 26,7 → 14,6)
- [ ] Usei o **valor de reprodução** como âncora, já que o lucro do ano não serve?

## D. Proventos — o bloco onde mais se erra

- [ ] **Ajustei por bonificação e desdobramento?**
  *Sabesp: agregadores mostravam 12–13%; o real era 2,4%. Engie: mostravam 5–8%; o real era 3,4%.*
- [ ] Separei **data-com de pagamento**?
- [ ] Medi a **defasagem declaração → pagamento**?
  *Hypera 12–18 meses · Vibra 15–18 · TIM e Vivo ~12 · Fleury parcela até 2 anos · Gerdau 7–31 dias · Unipar 9–11 dias.*
- [ ] Separei **ordinário, extraordinário e redução de capital**?
- [ ] Calculei o payout sobre **lucro E sobre FCFE**?
- [ ] **Respondi textualmente: "o dividendo é coberto por caixa?"**
- [ ] Só usei o Preço Teto de Bazin se a resposta acima foi **sim**?
- [ ] O yield que usei no comparativo com a RF é o **sustentável**, não o reportado?

## E. Controlador

- [ ] Identifiquei controlador, participação, **tag along**, free float e liquidez diária?
- [ ] Avaliei a **qualidade do negócio separadamente** do risco de controlador?
- [ ] Listei as interferências **já consumadas** (15 anos, com fonte) — ou escrevi "nenhuma identificada"?
- [ ] Apliquei o desconto **uma única vez** e **declarei onde** (valor central ou Ke)?
  *Erro cometido: risco político no texto e no gatilho, mas não no número (Cemig, Petrobras); ou no número e de novo no qualitativo (BBSE3, CXSE3).*
- [ ] **Teste de coerência:** estou tratando o mesmo defeito da mesma forma em todas as empresas?

## F. Qualidade do lucro

- [ ] Comparei lucro **contábil vs ajustado**? De onde vem a diferença?
  *Câmbio (Mahle, Suzano), IAS 29 (Argentina), evento societário (Engie/UBP), crédito fiscal (Unipar, Fleury), venda de ativo (Klabin).*
- [ ] ROE alto vem de **alavancagem**? Calculei o **ROIC** e usei ele no comparativo?
- [ ] Comparei ROIC com o WACC — e no **meio do ciclo**, não só hoje?
- [ ] Accruals de Sloan: o lucro está acima ou abaixo do caixa? Por quê?

## G. Veredito

- [ ] As quatro armadilhas foram verificadas uma a uma?
- [ ] O veredito respeita a régua? (≥30% BARATA · 10–30% RADAR · ±10% JUSTA · >15% CARA)
- [ ] Dei preço de compra, justo, saída **e gatilho de invalidação**?
- [ ] Respondi **separadamente** para carteira de proventos e para ganho de capital?
- [ ] Fiz o comparativo com o **Tesouro IPCA+ com 3 p.p. de prêmio**?
- [ ] Ajustei o **tamanho de posição** à liquidez e à ciclicidade?
- [ ] Se há análise anterior: registrei **o que mudou e por quê**?

## H. Autocrítica

- [ ] Escrevi as 5 linhas céticas, com **uma obrigatória sobre o Ke** e **uma sobre o ciclo**?
- [ ] Se alguma linha derrubou o veredito, **corrigi de fato** — em vez de só registrar?
- [ ] Não mudei de ideia por pressão do interlocutor, apenas por mérito do argumento?

---

## Erros históricos desta mesa (para não repetir)

| # | Erro | Onde | Correção que virou regra |
|---|---|---|---|
| 1 | DY de agregador sem ajuste de bonificação | Sabesp, Engie | Regra 9 do prompt |
| 2 | Risco de controlador no texto, não no número | Cemig, Petrobras | Regra 8 + revisão de 07/09 |
| 3 | Mesmo defeito, veredito diferente | BRSR6 vs CMIG4 | Teste de coerência (bloco E) |
| 4 | Cotação desatualizada sem aviso | 12 análises | Regra 5 |
| 5 | Ke real descontando fluxo nominal | várias | Regra 6 |
| 6 | Múltiplo de topo de ciclo tratado como barganha | Vibra, Petrobras | Regra 7 |
| 7 | Triagem preliminar tratada como conclusão | LEVE3 (7/7 → JUSTA/CARA), UNIP6 (5/7 → ARMADILHA) | Triagem define fila, não veredito |
| 8 | Rótulo "estatal" sem interferência consumada | BBSE3, CXSE3, CPFE3 | Vetores V1–V6 da doutrina |
