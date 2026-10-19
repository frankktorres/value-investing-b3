# 09 — DIÁRIO DE DECISÕES
*Criado em 05/10/2026 (Etapa 1 do `PLANO-DE-MELHORIAS-2026-10.md`, frente F7). Regra de Munger: sem registro da tese, da data e do que provaria o erro, não há aprendizado.*

## Como usar
- Uma entrada por decisão **de compra, venda ou de manter uma posição que estava sob teste** (ex.: acima da saída e mantida). Nunca editar entrada antiga: corrigir com nova entrada que a cita.
- Campos: data · ticker · ação · preço · central/saída da casa na data · tese (3 linhas) · **o que me provaria errado** · data de revisão · execução (preço real, quantidade, imposto — o Frank preenche) · resultado (preenchido na revisão).
- Antes de comprar: passar a lista de vieses do `04` (incentivo, prova social, compromisso, ancoragem no preço pago, disponibilidade de notícia recente).
- Revisão trimestral: classificar cada erro por causa — **dado, método ou viés** — e transformar padrão repetido em mudança de doutrina.
- Preços e centrais são os do hall de 05/10/2026 (fechamento de 02/10, doutrina **v2.2**); saída = 1,30 × central (§9), ou 1,50 × pela exceção de qualidade, que em 05/10/2026 **só a LEVE3** alcança (saída R$ 50,98).

---

## Entradas

### 05/10/2026 — VENDER ITSA4, ABCB4 e RANI3 · MANTER ISAE4
**Contexto.** Recálculo dos 6 lotes (doutrina v2.1). Os três estavam na carteira e acima do preço de saída; ISAE4, também na carteira, abaixo. O Frank delegou a decisão ("decida você"); decidido pela regra de venda do §9 (preço > 1,30 × central), sem exceção de qualidade. **A regra de venda por qualidade (D7 do plano) ainda não existe e não foi usada.**

| Ticker | Ação | Preço 02/10 | Central v2.1 | P/C | Saída 1,30× | Acima da saída |
|---|---|---|---|---|---|---|
| ITSA4 | Vender | R$ 14,67 | R$ 7,11 | 2,06 | R$ 9,24 | +59% |
| ABCB4 | Vender | R$ 26,15 | R$ 13,31 | 1,96 | R$ 17,30 | +51% |
| RANI3 | Vender | R$ 7,94 | R$ 4,87 | 1,63 | R$ 6,34 | +25% |
| ISAE4 | Manter | R$ 28,19 | R$ 24,10 | 1,17 | R$ 31,33 | abaixo (−10%) |

**Tese da venda (comum).** O preço paga mais que o dobro (ITSA4, ABCB4) ou 1,6× (RANI3) o valor que a casa calcula; o retorno esperado de quem compra hoje fica abaixo do Tesouro IPCA+ líquido. Segurar exige acreditar numa premissa que a casa não sustenta.
- **ITSA4:** SOTP R$ 7,33 (Itaú 37,5% ao central de R$ 17,54 por ITUB4) e DDM R$ 6,90; ROE de longo prazo 17,2% contra Ke 19,3%; retorno real implícito 6,4%, abaixo do Tesouro.
- **ABCB4:** Ke implícito 13,3% contra Ke da casa 19,3%; retorno de investimento 13,2%; não vence a renda fixa líquida.
- **RANI3:** ROIC 7,2% abaixo do WACC 15,6% (não cria valor); Ke implícito 14,0%.
- **ISAE4 (manter):** P/C 1,17, abaixo da saída; regulada, DCF regulatório. Pendência: 703 mi de ações (StatusInvest) contra 659 mi na DFP 2025 — com 659 mi seria JUSTA; conferir no RI.

**Destino do dinheiro.** Tesouro IPCA+ 2050; vender no máximo R$ 20 mil por mês de cada papel se houver lucro (isenção de IR em vendas ≤ R$ 20 mil/mês em ações — conferir a regra vigente na doutrina §4.1 antes de executar); se houver prejuízo, a venda não tem esse limite de isenção e o prejuízo compensa ganhos futuros.

**O que me provaria errado** (gatilhos objetivos; qualquer um → reabrir a tese):
- **ITSA4:** o Itaú ser reavaliado para cima do central de R$ 17,54 por evidência de ROE sustentado > 22% (hoje o ROE de longo prazo usado é 17,6%) **ou** a ITSA4 negociar abaixo de R$ 9,24 com o Itaú inalterado (aí a venda terá sido cedo e a recompra, possível).
- **ABCB4:** ROE de 2 anos seguidos acima de 18% com inadimplência 90d < 1% (hoje ROE de longo prazo 12,8%).
- **RANI3:** ROIC acima do WACC por 2 anos seguidos, ou preço de celulose/embalagem que eleve a margem mediana acima de p75 do histórico de forma documentada.
- **Em todos:** o preço cair ≤ 1,30 × central na próxima revisão sem mudança de premissa (a venda teria sido por ruído; a regra, não a decisão, estaria certa — registrar).
- **Custo do erro já conhecido:** vender um negócio bom cedo custa imposto sobre o ganho e o retorno de ficar de fora. Aceito por serem os três de qualidade média e P/C ≥ 1,63.

**Data de revisão:** 05/01/2027 (fecho do 4T26; confere se as três voltaram ao intervalo de compra ou se subiram mais). Revisão extra se a temporada do 3T26 (nov/2026) mudar o central em > 15%.

**Viés a vigiar.** *Ancoragem no preço pago* (não ficar esperando "voltar ao preço médio") e *disponibilidade de notícia recente* (o 1º turno da eleição subiu os preços em 5–11% em 05/10; o central usa 02/10).

**Execução (o Frank preenche):** data · preço real · quantidade · preço médio · lucro/prejuízo · IR devido · Tesouro comprado. *Até a confirmação da venda, a decisão está registrada mas não executada;* ao confirmar, tirar os três da "Carteira" em `PROMPT-AGENTE-NOTICIAS-SEXTA.md` e na cópia de `UPLOAD CLAUDE DESKTOP/`.

**Resultado:** (preencher na revisão).

---

### 05/10/2026 — DECISÕES DE DOUTRINA (Etapa 2 / F2): regra de venda por qualidade e alcance do ROIC a reposição

**Contexto.** Não são decisões de compra ou venda: são duas escolhas que o Frank fez sobre a própria doutrina, na Etapa 2 do
`PLANO-DE-MELHORIAS-2026-10.md`. Ficam aqui porque mudam o preço de saída de toda a carteira daqui para frente.

**1. Regra de venda por qualidade (D7) — APROVADA como proposta.** Saída a **1,50 × o central** só para não financeira com
**ROIC real > WACC real a custo de reposição em ≥ 8 exercícios**, em janela de pelo menos 10, *e* **nota de Qualidade ≥ 8**; todas as demais seguem 1,30 ×.
Tese quebrada continua saída a qualquer preço. Base: Buffett, cartas de 1988 ("our favorite holding period is forever") e 1989
("we would rather stay put, even if that means slightly lower returns"; o imposto diferido é "an interest-free loan from the U.S.
Treasury") — fonte nota A. Fisher entra como paráfrase nota C (o texto do livro não foi conferido). **Não se aplica a financeira**:
o repositório não tem série de 10 anos de banco ou seguradora.

**Efeito medido no dia da decisão: nenhuma decisão muda, mas um preço de saída muda.** O adversário mostrou que o ROIC de cada
exercício estava sendo comparado nominalmente com o WACC de hoje; corrigido para real contra real (§4), **a LEVE3 passa a ser
elegível** — 8 de 10 exercícios e Qualidade 8,005 — e a saída dela vai de R$ 44,35 para **R$ 50,98**. A ação está a R$ 34,43 com
central R$ 33,99 (JUSTA, P/C 1,01), muito abaixo das duas, então não há decisão a tomar hoje. Dos 31 tickers acima de 1,30 ×
central, só ABEV3 (P/C 1,42) e GGBR4 (1,31) estavam na faixa 1,30–1,50 ×: ABEV3 tem 8 de 10 exercícios mas Qualidade 7,018, e com
o capex de manutenção real a P/C dela foi a 1,51, saindo da faixa; GGBR4 tem 1 de 10 e Qualidade 3,7. WEGE3 tem 4 de 10 e a P/C
4,32 está acima dos dois limites. **A regra é seguro prospectivo** — e foi aprovada sabendo disso.

**Fragilidade da LEVE3, declarada.** Ela entra por 0,005 de nota de Qualidade (8,005 contra o mínimo de 8). Como a nota usa o ROIC
a custo de reposição (28,6% → 24,9%), qualquer revisão da idade média do imobilizado dela pode tirá-la da exceção.

**O que me provaria errado.** Um negócio elegível vendido a 1,50 × que depois cai abaixo de 1,30 × e fica (aí o 1,30 × era melhor);
ou um elegível mantido entre 1,30 × e 1,50 × cujo central é revisado para baixo (aí a régua estava solta, não o preço).
**Revisão:** na próxima vez que a LEVE3 (ou outro elegível) passar de 1,30 × o central, e no kaizen trimestral.

**2. ROIC a custo de reposição trava o crescimento no DCF (D10) — APROVADO.** O menor entre o ROIC contábil e o ROIC a custo de
reposição decide o filtro 1, a nota de Qualidade **e** a trava "crescimento só com ROIC > WACC". A alternativa era usar o ROIC a
reposição só no filtro 1 e na nota, deixando o DCF crescer pelo contábil — rejeitada: crescer exige retorno acima do custo de
capital sobre o capital **a preços de hoje**, que é o que a empresa terá de repor.

**Efeito medido:** um único central afetado, **WEGE3 13,44 → 11,92** (ROIC 29,8% → 18,4% contra WACC 19,1%), e UNIP6 −0,9%.
Nenhuma palavra mudou. A trava é avaliada por cenário (p25/mediana/p75), então o cenário otimista preserva o crescimento e a queda
é gradual — o piso sem crescimento nenhum seria 10,69.

**O que me provaria errado.** A idade média do imobilizado é um proxy (imobilizado líquido ÷ D&A, com a D&A da DFC incluindo
intangível e direito de uso). Se a WEG publicar imobilizado bruto e depreciação acumulada e a idade real divergir muito dos
11,6 anos estimados, o ROIC a reposição muda e a trava pode ter sido acionada por erro de medição, não de economia.
**Revisão:** quando o imobilizado bruto entrar na coleta (pendência da Etapa 3).

### 06/10/2026 — DECISÃO DE MÉTODO (Etapa 3 / F3): backtest parado no portão; validação passa a ser prospectiva

**O que aconteceu.** O backtest 2014–2025 precisava de um motor mecânico (os `lote*.py` trazem premissas digitadas em 2026). O
portão, declarado antes de medir, exigia que esse motor reproduzisse a régua nos 41 do golden: palavra exata ou ±1 nível em ≥ 80%
**e** mediana |ΔP/C| ≤ 0,15. Medido uma única vez: **70,7% e 0,34**. Falhou nos dois, e a falha não depende dos 5 bancos com dado
faltante (contados como acerto, a mediana ainda é 0,26). Antes de medir já se sabia que o critério de palavra discriminava pouco
(34 dos 41 são CARA; "sempre CARA" acerta 38/41) — o portão foi mantido como declarado.

**Decisão (delegada ao Claude pelo Frank).** Aceitar a parada: não redesenhar o motor depois de ver o resultado (seria calibrar no
único ponto com resposta conhecida) e não rodar as fatias 13–15. Em troca, **registro prospectivo**: cada rodada aprovada entra em
`ferramentas/prospectivo/registro.jsonl` (append-only). 1º registro hoje: 41 vereditos, preços de 02/10/2026, doutrina v2.2.

**Consequência declarada.** O prêmio de 5 p.p. e a margem de 30% seguem **sem validação empírica** (D5 aberta). Não há base para
recalibrá-los — nem para afirmar que funcionam.

**O que me provaria errado.** Se, com ≥ 4 datas de registro e 1 ano vencido, BARATA/RADAR não ganharem de CARA nem do Ibovespa
total, a régua não carrega informação e a doutrina tem de mudar. Ao contrário: se o dado público permitir um proxy mecânico que
passe num portão declarado de novo, em amostra que não seja o golden de 05/10/2026, o backtest volta.
**Revisão:** a cada rodada nova (registrar) e em 02/10/2027 (primeira leitura a 1 ano, ainda sem poder decidir sozinha).

### 06/10/2026 — DECISÃO DE MÉTODO (Etapa 4 / F4): triagem de toda a B3 e monitor semanal

**O que aconteceu.** A triagem mecânica (`ferramentas/triagem/`) varreu as 312 companhias com negócio nos 60 pregões até 02/10/2026.
110 passaram liquidez (≥ R$ 0,97 mi/dia), identidade, exclusões do §8 e janela ≥ 7 exercícios. **Só 5 das 104 não financeiras passam
no portão Buffett** (ROIC real > WACC real em ≥ 7 de 10 exercícios, no máximo 1 reprovação entre FCO, DL/EBITDA, R$ 1 retido e
proventos), e só a CMIN3 não sai por preço — e com central rápido não confiável. Fora das blue chips, o retorno sobre capital acima
do custo por uma década é raro na B3.

**Decisões (técnicas, tomadas pelo Claude pela doutrina; o Frank decidiu só a posição típica).**
1. Liquidez pela saída da posição: posição típica **até R$ 50 mil** (Frank) → piso = o do backtest (R$ 500 mil de 2014 pelo IPCA).
2. A fila é **ordenada, não cortada**: com o portão como declarado sairiam 0 a 1 nomes. Camada A = portão; camada B = ≥ 3 de 5 testes,
   com o que reprovou escrito como pergunta para a análise completa. Mesmo papel do `06` antigo ("entra com ≥ 5 de 7"). Decidida
   **depois** da 1ª rodada — declarado no `06` e no config para não parecer régua de antes.
3. Base de ações que mudou > 50% na janela (incorporação, emissão grande, evento sem fator) sai do portão e vai para "avaliar à mão":
   SAUD3 (Odontoprev + incorporação de 2026) entrava na camada A medindo a empresa antiga — achado do `adversario`.
4. A fila de 02/10/2026 entra em `prospectivo/triagem.jsonl` (append-only). Métrica declarada antes: retorno total a 1 ano da fila
   contra Ibovespa total e contra as 41 do hall; leitura com ≥ 4 datas.

**O que me provaria errado.** Se a fila (A+B) não bater o Ibovespa nem o hall em ≥ 4 rodadas com 1 ano vencido, a triagem mecânica
não separa nada e só vale como lista de exclusão (liquidez, §8, RJ). Se a camada B bater a A, o portão Q1 está mal desenhado
(ROIC contábil contra WACC de hoje pune negócio que cresceu investindo).
**Revisão:** depois da temporada do 3T26 (rodar de novo com `--data` do último pregão) e a cada rodada registrada.

### 07/10/2026 — Etapa 5 (F5) fechada: dossiês, registro com `origem` e propagação

**O que aconteceu.** Três dossiês aprovados pelo `adversario` e pelo `verificador-fonte` (BLAU3 e CMIN3 NÃO CONCLUSIVO; HYPE3 CARA, central
R$ 19,27) cumprem o critério do plano (1 saúde + 1 da fila + 1 do hall). O parecer da HYPE3 foi preenchido pelo Claude a pedido do Frank e
assinado como não independente; segunda opinião = comitê B no Desktop.

**Decisões (técnicas).**
1. `registro_prospectivo.py --dossie` grava os vereditos de `dossie/vereditos/*.json` em `prospectivo/registro.jsonl`; a chave passa a ser
   (`origem`, `data_preco`, `ticker`) com `origem` ∈ {hall, dossie}. Linhas antigas sem o campo valem "hall" (arquivo append-only, não reescrito).
   Assim a HYPE3 (hall e dossiê, mesma data) não colide. A triagem segue em arquivo próprio (`triagem.jsonl`).
2. Propagado para `02` (v4), `06` (§8, via gerador `triagem/fila.py`), `08` (Passo 4: desdobramento, subvenção de ICMS, M&A, ticker isolado) e `README`.
   Versões anteriores em `_historico/2026-10-07 antes da Etapa 5/`.

**Fica aberto (⏸ do Frank):** capex de expansão sem receita; desconto de controlador sobre âncora negativa; fatia 7 (notas do hall por
evidência); margem reexpressa no §11.1; `outros_passivos` fora da solidez/ROIC; alíquota com crédito de IR que tem prazo.

### 07/10/2026 — DECISÃO DE MÉTODO: doutrina v2.3 (as 6 pendências acima)

**Quem decidiu.** O Claude, pela doutrina, com o "ok" do Frank ("decida tudo isso baseado no value investing"). A doutrina não
tratava nenhum dos seis casos, então valeu a regra mais conservadora que não mexesse no golden sem necessidade.

**Decisões e efeito medido (golden regravado em duas linhas de log; nenhuma palavra mudou nos 41).**
1. **Alíquota (§2).** O piso de 15% acabou. Benefício permanente (JCP) fica na mediana. Crédito com prazo (ágio, subvenção de ICMS)
   vale só até o fim documentado, em valor presente à parte, e depois 34% na perpetuidade e no WACC. **Achado na implementação:**
   tirar o piso, ao pé da letra, **subiria** o central de TIMS3 (mediana 5,4%) e PRIO3 (11,1%), e a PRIO3 iria a JUSTA. Por isso,
   mediana abaixo de 15% só vale com a origem permanente declarada com fonte; sem ela, 34%. Também o Owner Earnings passa a ser
   refeito à alíquota perpétua quando ela não é a mediana; senão o crédito voltaria à perpetuidade por essa âncora.
   Na revisão do `adversario` a fase foi corrigida: a efetiva conta os anos de crédito (antes saía de um ano só, e um crédito
   maior zerava a fase); o benefício incide sobre o lucro depois dos juros (o WACC já deduz os juros a 34%) e tem teto no crédito
   observado; mediana com menos de 3 anos válidos vale 34%.
   Efeito: HYPE3 19,60 → 17,51; TIMS3 10,53 → 7,96; PRIO3 55,31 → 43,41; ABEV3 só o OE, 9,37 → 7,97 (a subvenção de 2021–23 saiu
   da perpetuidade; a premissa da Lei 14.789/2023 é a do Lote 4, e o texto da lei não abriu no planalto.gov.br em 07/10). Todas seguem CARA.
2. **Desconto de controlador só em âncora > 0 (§5).** Corrigido nos dois motores e na sensibilidade. O Ke implícito e o DCF reverso
   não financeiros passam a usar o valor descontado; o financeiro já usava. Sem efeito no golden.
3. **Média da regra 11 no motor (§10).** Peso 2 do controlador quando discricionário; peso 2 sem razão escrita não roda. No hall,
   critério provisório: interferência consumada já declarada no desconto do lote (BBAS3, BRSR6, CMIG4, SAPR11, PETR4). As notas
   seguem "arbitrada, pré-v4" até o dossiê de cada ticker. A LEVE3 vai primeiro, porque a exceção de saída depende de 0,005 de nota
   arbitrada. Nota geral: −0,04 a −0,10 nos cinco.
4. **Outros passivos (§11.1).** O financeiro (com juros, ou provento a pagar já ex) entra na dívida líquida; o operacional, só na
   ponte. Só a CMIN3 usa: DL/EBITDA 0,17 → 2,33 e ROIC 23,4% → 12,4%. A trava zera o g do DCF (3,89 → 3,40), a dispersão cai de
   3,10 para 2,71 e **a palavra do dossiê sai de NÃO CONCLUSIVO para CARA**.
5. **Capex de expansão (§11.1).** Só o projeto identificado (nome, valor, prazo, fonte A/B, sem receita) sai antes da regra de
   manutenção. Nenhum ticker usa ainda: a CMIN3 tem só o projetado (R$ 13,2 bi em 2025–30) e a BLAU3 não foi refeita.
6. **Margem ao preço de meio (§11.1).** Escrito o que o código faz. O código agora confere perfil cíclico e janela ≥ 7.

**Vereditos novos (registro append-only = data nova).** HYPE3 e CMIN3 em **06/10/2026**, com rf e π do mesmo dia (6,51% e 5,67%,
`ferramentas/dados/mercado_2026-10-06.json`):
- **HYPE3:** central R$ 18,12, P/C 1,49, CARA. O Ke menor sobe o central 5,9% e a alíquota por fase o baixa 11,2%.
- **CMIN3:** central R$ 3,63, P/C 1,36, CARA.

Os vereditos de 02/10 ficam no disco e no registro como histórico da v2.2. O hall **não** é registrado de novo em 02/10, porque o
registro recusa outro valor na mesma data; a v2.3 do hall entra na próxima rodada (Etapa 7).

**Divergência declarada.** O motor reduzido (`backtest/motor/reduzido_nf.py`, usado pela triagem) segue com o piso de 15%. Ele foi
congelado pelo portão de 06/10, e mudá-lo agora seria recalibrar depois de ver o resultado. A triagem só ordena a fila; a alíquota de
cada nome é decidida no dossiê.

**Pendência baixa (`adversario`, sem ticker afetado hoje).** Na regra da mediana com 3 ou 4 anos válidos, os anos de crédito
descartados continuam inteiros no Owner Earnings. Fechar quando algum ticker cair nesse caso: refazer o OE à alíquota perpétua
sempre que um ano sair da mediana.

**O que me provaria errado.**
- Se TIMS3 ou PRIO3 mostrarem, com fonte A/B, benefício permanente (ou com prazo longo) que explique a alíquota baixa, o 34% terá
  subavaliado as duas: o dossiê corrige com `aliquota_permanente_fonte` ou `aliquota_fase`.
- Se a subvenção de Goiás durar até 2032 com fonte, a fase da HYPE3 vai a 2032 (central R$ 19,04, ainda CARA).
- Se o critério provisório de "discricionário" errar num dossiê (controlador sem interferência consumada, mas com poder de fato,
  ou o contrário), o critério muda.

**Revisão:** no dossiê de cada ticker afetado (LEVE3 primeiro, depois TIMS3 e PRIO3) e na rodada da Etapa 7.

### 08/10/2026 — DECISÃO DE MÉTODO: dossiê LEVE3 (perde a exceção de saída) e origem do imposto de TIMS3 e PRIO3

**LEVE3 (dossiê, data-base 06/10/2026).** Central R$ 35,75, P/C 1,02, JUSTA (`DOSSIES/2026-10-08-LEVE3.md`). As notas da regra 11
por evidência — moat 4, gestão 1, controlador 2 (peso 2), ciclo 3, Fisher 2 — substituem no hall as arbitradas (4/3/3/3/3). A
qualidade vai de 8,005 a 7,1 e **a LEVE3 perde a exceção de saída a 1,50×**, que era a única do hall: a saída volta a 1,30 × central
(R$ 44,18 no hall). Era o risco declarado em 05/10: a regra estava apoiada em 0,005 de nota arbitrada.
- A compra de R$ 668 mi do controlador (2024) **não** conta como interferência consumada: preço dentro de dois laudos, comitê
  independente, controlador abstido, minoritários aprovaram. Se a próxima compra do grupo vier sem esse rito, conta.
- Partes relacionadas pelo total (18,3% da receita, como na HYPE3); só as saídas dariam 7,9%. Nenhuma leitura favorável leva a
  qualidade a 8.

**TIMS3: alíquota perpétua 18,3%** (era 34% provisório; 15% de piso até a v2.2). O IR baixo vem de JCP (permanente) e da redução de
75% do IRPJ da SUDENE/SUDAM (laudos de 10 anos por UF, vigência não encontrada nos DFPs → prazo sem fonte = zero). A perpétua é a
mediana 2021–25 sem a SUDENE e sem os itens pontuais, pela conciliação dos DFPs 2022–25 [A]. Central 7,96 → 10,11 (P/C 1,84, CARA).
Risco: autuação de R$ 355,6 mi contra a averbação dos laudos (dez/2025).

**PRIO3: fase até 2032.** O IR baixo vem do uso de prejuízo fiscal (R$ 8,09 bi reconhecidos; uso limitado a 30% do lucro tributável;
96,5% projetados até 2032, DFP 2025 nota 16 [A]). EUA/Luxemburgo e moeda funcional não têm prazo nem permanência com fonte → 34%
depois. Central 43,41 → 49,37 (P/C 1,28, CARA). Ficar em 34% já ignoraria um ativo fiscal de R$ 8 bi no balanço.

**O que me provaria errado.** LEVE3: retorno da compra de 2024 acima do WACC no DFP 2026 (gestão vai a 2; qualidade ~7,5, ainda < 8).
TIMS3: vigência dos laudos com fonte A/B (vira fase com a efetiva até o fim) ou derrota na autuação. PRIO3: o prejuízo fiscal ser
usado mais devagar que o cronograma da administração.
**Revisão:** DFP 2026 (LEVE3, PRIO3); vigência dos laudos SUDENE da TIM.

### 08/10/2026 — DECISÃO: o analisador fica arquivado; entram só as lições

**O que aconteceu.** Auditoria (3 agentes, só leitura) da pasta `analisador/`: outro projeto de value investing na B3, paralelo a
este, com motor próprio, 91 "decisões", 1.523 testes e vereditos para 14 tickers, terminado sem nenhuma compra e com excesso de
processo. O motor e a régua dele são piores que os daqui (baldes em vez de preço de compra/saída, ROIC sem custo de reposição, Ke
diferente). **Decisão do Frank:** congelar (tag `arquivado-2026-10-08`, `analisador/ARQUIVADO.md`, `.venv` apagado; `dados/` e a
história mantidos) e trazer só as lições: seção I do `04` (vieses, inversão de Munger, "não sei" ≠ "é ruim", kd > Ke, escopo e
unidade, número vetado, teste contra documento real).

**Alerta para este projeto.** O analisador morreu de burocracia: regra nova a cada sessão e nenhuma decisão de compra. A partir de
agora a régua fica parada até a temporada do 3T26 (Etapa 7); dossiê novo só quando uma ação chegar perto do preço de compra.
**O que me provaria errado:** se em 3 meses a doutrina tiver crescido mais que o número de decisões de compra/venda registradas
aqui, este projeto está repetindo o analisador.

### 08/10/2026 — CORREÇÃO DE INSUMOS: Onda 1.1 da auditoria (AUD-01, 16, 02, 04, 03) · doutrina v2.3.1

**O que foi feito.** A auditoria de 08/10 (`docs/auditoria/AUDITORIA_2026-10-08.md`) teve verificação branda; cada achado foi
**reproduzido com script antes** de mexer, e cada correção tem teste que falhou no código antigo (`ferramentas/tests/test_onda1_insumos.py`,
14 vermelhos → verdes). Nenhuma regra nova: a doutrina já mandava tudo isso; o código não fazia. Golden regravado por achado
(4 entradas em `tests/golden_log.md`).
1. **AUD-01 + AUD-16 — unidades.** Receita de meio padrão (3 exercícios + 12 meses), Owner Earnings de cada ano e DPA médio iam
   **nominais** para uma taxa **real**: o NOPAT saía ~7,5% baixo. Agora vão a R$ de hoje pelo IPCA antes da média/mediana. Achado novo na
   reprodução: a `receita_media` do FLRY3 tinha o mesmo defeito. 19 tickers; **SUZB3 CARA → JUSTA** (37,12 → 43,59, P/C 1,02) e
   **LEVE3 JUSTA → RADAR** (33,99 → 40,27, P/C 0,86) — a auditoria mediu cada efeito isolado (LEVE3 ficava JUSTA); somados, o DCF passa a
   ser a mediana. KLBN11 +39%, SLCE3 +23%, RANI3 +15%: centrais pequenos com alavancagem.
2. **AUD-02 — provento já ex na dívida.** Só a CMIN3 aplicava, à mão. Agora o motor mede em toda não financeira: passivo de proventos
   do ITR (novo campo do coletor, sem o mínimo obrigatório, a custódia da B3 e provisões) + proventos **aprovados depois de 30/06 e ex até
   02/10** (API da B3, `proventos_ex.py`; a casa já fazia isso à mão no EGIE3). WEGE3 13,98 → 10,91 (−22%, R$ 5,9 bi a pagar), PETR4 −3,5%
   (R$ 25,6 bi), UGPA3 −5%, VBBR3 −7%; nenhuma troca de palavra. LTM de 4º trimestre com passivo de proventos **falha alto** (o DFP pode
   trazer o mínimo obrigatório ainda não aprovado na linha genérica) — decidir na temporada do 4T26.
3. **AUD-04 — ISAE4 pela regra de follow-on (§11.2), igual ao EGIE3.** VPA = (PL de 30/06 + R$ 1,2 bi) ÷ (659 mi + 44 mi ações novas)
   = 33,21; ROE ponderado com o dinheiro novo ao Ke. **CARA 1,17 → JUSTA 1,09** (central 24,10 → 25,78). O texto do lote, que mandava usar
   659 mi, também errava e foi corrigido. Encerra a pendência "conferir no RI" de 05/10, menos o custo da oferta (usado o valor bruto).
4. **AUD-03 — PETR4 com a margem só de 2019–25 (IFRS 16).** A margem de E&P é EBITDA − D&A atual, e a D&A atual tem o direito de uso:
   o EBITDA de 2016–18 contava o aluguel duas vezes (eram as 3 menores margens). Base: §11.1 (DCF) e §11.4.2; a tensão com o §11.4.4
   (cíclica = 10 anos) foi resolvida por escrito: o item 4 proíbe encurtar pelo teste, não por quebra declarada; 7 anos cobrem o vale de
   2020 e o pico de 2022. O motor agora recusa E&P com ano anterior a 2019. Central 49,95 → 62,31, P/C 0,82 — **segue JUSTA** porque a
   dispersão (> 1,8) rebaixa RADAR.

**Dossiês.** Os vereditos salvos de BLAU3 (02/10), HYPE3 e LEVE3 (06/10) não se reproduzem mais pelo método novo; ficam no disco
(registro append-only) e o recálculo na mesma data está fixado em `test_dossie_fichas.py`: LEVE3 35,75 JUSTA → 42,57 **RADAR**
(P/C 0,86), HYPE3 18,12 → 18,35 CARA, BLAU3 8,27 → 8,80 (segue não conclusivo). Veredito novo só com data nova.

**Achados novos (fora do roteiro, registrados para as próximas ondas).**
- A API da B3 devolve vazio para nome de pregão com "/" ("AMBEV S/A", "KLABIN S/A"; só respondem "… SA"): o cache de proventos do
  **backtest** não tem AMBEV nem KLABIN. Backtest parado; corrigir antes de religá-lo.
- O provento aprovado depois do balanço também existe nas **financeiras/utilities** (P/VP sobre o PL de 30/06); só o EGIE3 o desconta.
- O DPA digitado do motor financeiro (`dpa_medio_5a`) segue nominal; move só a renda, não o central.
- O passivo de proventos entra no capital de giro (`pc`); a variação dele mexe no OE do ano — conferir na Onda 1.3.

**O que me provaria errado.** Se o ITR do 3T26 mostrar que os proventos aprovados depois de 30/06 já estavam no passivo de 30/06
(contagem dupla da parte B3), ou se a receita de meio em R$ de hoje fizer o central de cíclicas oscilar com o IPCA mais do que com o
negócio. **Revisão:** temporada do 3T26 (Etapa 7) — rodar `python proventos_ex.py` depois da data do preço de cada rodada.

**Adversário (mesmo dia), 5 defeitos reproduzidos e corrigidos, sem troca de palavra.** (1) SMTO3 contava duas vezes o mínimo
provisionado em 31/03 (rótulo genérico, R$ 69,9 mi) e aprovado na AGO de 03/07: entre o fim do exercício e a AGO o passivo e a B3 trazem o
mesmo dinheiro — no 1º trimestre depois do exercício conta o maior dos dois; no próprio fim do exercício o motor falha alto. (2) O
provento aprovado depois do balanço ainda está no PL de 30/06: ao entrar na DL, sai do PL no capital do ROIC e no valor de reprodução
(como no EGIE3). (3) Data-com no dia do preço ainda não é ex (o fechamento dela carrega o provento). (4) Dossiê usa a data do próprio
preço, não a do hall. (5) O PDF do LEVE3 misturava OE em R$ de hoje com lucro nominal. Junto: o exercício abr–mar da SMTO3 passou a
ser deflacionado pelos próprios 12 meses (o ano-calendário ficava ~3% baixo). **Números finais:** SMTO3 23,07 → 26,58 (RADAR,
**P/C 0,73 — a 0,03 do preço de compra**, R$ 18,61), B3SA3 8,98, WEGE3 10,94; valor de reprodução de PETR4 34,33 → 33,09.
Notas não corrigidas (ver adversário): Kd cobrado sobre provento a pagar na base do benefício fiscal (conservador, pequeno).

### 08/10/2026 — DECISÃO DE MÉTODO: Onda 1.2 da auditoria (Ke, custo da dívida, convenções de mercado) · doutrina v2.4

**Reprodução antes de mexer (script, sem gravar nada).** Os 9 achados reproduziram: AUD-06 (rf 7,06% é a "Taxa Compra Manhã" do
Tesouro Transparente e estava rotulada "fechamento"; com a ANBIMA 7,1377% — NTN-B 2050 *com cupom*, outro instrumento — ISAE4 iria a
CARA e UNIP6 a JUSTA); AUD-78 (rf e π digitados em `lote1_bancos`, `triagem/config` e `backtest/config`, nenhum teste contra
`mercado.json`); AUD-72 (nenhum cálculo de idade do preço no hall; a triagem já tinha); AUD-07 (21 spreads digitados de 0,5 a 2,5 p.p.
sem fonte); AUD-09 (ABEV3 com média de 2 exercícios explícita: 10,89 contra 9,18 pela regra); AUD-18 (reprodução contábil × ROIC a
reposição, por definição); **AUD-08 reproduziu em outros tickers** — a LEVE3 tinha saído de JUSTA na 1.1, mas SUZB3 (Bogle 11,3% × Ke
19,3%) e ISAE4 (17,0%) eram JUSTA com a trava falha; AUD-12/13 por simulação das opções.

**DECISÃO DO FRANK — AUD-12 (Ke igual para todas × ajustado pela dívida).** Opções mostradas, com o efeito no hall (Ke de 02/10):
| Opção | Regra | Palavras que mudavam |
|---|---|---|
| **1. Ke sobe com a dívida (escolhida)** | 5 p.p. = risco do negócio sem dívida; prêmio × [1 + (1 − t) D/E] (Hamada 1972, *J. Finance* 27(2):435-452, sobre Modigliani-Miller 1958 — nota B, texto não aberto) | SMTO3 RADAR → CARA, SUZB3 JUSTA → CARA, LEVE3 RADAR → JUSTA, KLBN11 e SLCE3 CARA → NÃO CONCL., UNIP6 → CARA |
| 2. Ke em torno da média do hall | 5 p.p. na alavancagem mediana; sem dívida ganha Ke menor (WEGE3, ABEV3 +12%) | SMTO3 → JUSTA, SUZB3 → CARA, KLBN11 e SLCE3 → NÃO CONCL., UNIP6 → JUSTA |
| 3. Manter o Ke igual | convenção do §4 + linha de sensibilidade para D/E > 1 | nenhuma |
**Por quê:** é a mais conservadora (nenhuma empresa fica com Ke abaixo de hoje) e corrige o efeito de a dívida baratear o capital
(WACC 14,5% na KLBN11 contra 19,1% na WEGE3). Financeiras ficam nos 5 p.p. fixos (a alavancagem é o negócio).

**DECISÃO DO FRANK — AUD-13 (pesos do WACC a preço de mercado).**
| Opção | Regra | Efeito |
|---|---|---|
| **1. Ponto fixo (escolhida)** | E = central × ações, repetido até parar de mudar | nenhuma palavra com o Ke de hoje; o central deixa de depender do preço |
| 2. Manter preço de mercado | como estava, declarado | nenhuma; o central se move com o preço (SMTO3 25,80/23,07/22,41 a preço ×0,7/1,0/1,3) |
| 3. Pesos contábeis | D e PL do balanço | LEVE3 RADAR → **BARATA**, PRIO3 e SLCE3 CARA → JUSTA (menos conservador) |
Argumento: coerência interna (§11.3 — o P/C não pode comparar o preço com um número que depende do preço); a literatura de pesos-alvo é
nota C (não conferida).

**Diferença entre a prévia e o implementado (declarada).** A prévia calculou o prêmio com o D/E **a preço** e só os pesos no ponto fixo.
O implementado mede o D/E também no ponto fixo (o que a decisão pede: nada depende do preço). Em empresa muito alavancada cujo valor da
casa fica abaixo do preço, isso realimenta: central menor → D/E maior → Ke maior. As **palavras são as mesmas da prévia**, mas os
centrais saem mais baixos: SUZB3 22,04 (prévia 29,16; Ke real 26,7%, D/E 3,65), SMTO3 16,03 (16,97; 21,5%, D/E 2,29), RANI3 3,10
(22,3%, D/E 2,76), SLCE3 7,59 (23,3%, D/E 2,94). A conta converge (amortecida) em 20 dos 21; a RECV3 não tem central positivo.

**Decisões técnicas (minhas, pela doutrina).**
- **AUD-06:** fica a taxa de compra da manhã — é a que o investidor consegue no título sem cupom, e o Tesouro Direto não publica
  fechamento. Mudou o texto do §4 e os rótulos, não o número. ANBIMA com cupom fica como sensibilidade (ISAE4 e UNIP6 trocariam).
- **AUD-78/72:** `ferramentas/mercado_vigente.json` + `mercado.py`; hall, triagem e dossiê leem dele; teste contra `dados/mercado.json`.
  O literal do backtest fica (registro do experimento congelado de 05/10). `rodar_tudo.py` e o monitor imprimem a data e a idade da taxa;
  > 15 dias → "atualizar antes de decidir"; o golden guarda a data do preço.
- **AUD-07:** Kd = custo do RI (`kd_ri`, em reais e depois dos swaps, com fonte) ou rf nominal + spread sintético (Damodaran, jan/2026,
  nota B) pela cobertura **normalizada**. Com a cobertura de 12 meses, a SUZB3 (EBIT de vale de ciclo) caía para B+ e virava CARA
  pelo Kd; com a normalizada nenhuma palavra muda. Juros ÷ dívida bruta (3% a 29%) não mede custo em reais (dívida em dólar, arrendamento).
- **AUD-09:** `aliquota_desde` (Lei 14.789/2023) → ABEV3 com 2 exercícios = 34% até o DFP 2026; explícita < 34% exige fonte (TIMS3 tem).
- **AUD-18:** a reprodução fica no PL contábil (o menor dos dois, como no ROIC); a de reposição é exibida (`reprod_reposicao`).
- **AUD-08:** o "corrige antes de publicar" do §9 virou código: JUSTA pela régua com a trava falha → NÃO CONCLUSIVO até `trava_razao`.

**Efeito no hall (golden regravado em 4 blocos, um motivo por bloco):** SMTO3 RADAR → CARA (26,58 → 16,03); SUZB3 JUSTA → CARA
(43,59 → 22,04); LEVE3 RADAR → NÃO CONCLUSIVO (36,31, P/C 0,95; Bogle 18,6% × Ke 20,7%); **ISAE4 (carteira) JUSTA → NÃO CONCLUSIVO**
(Bogle 17,0% × Ke 19,3%; central 25,78 igual); KLBN11 CARA → NÃO CONCLUSIVO (central 1,72 com Ke real de 77%, D/E 17,4; dispersão 12×); SLCE3 CARA → NÃO CONCLUSIVO (dispersão);
UNIP6 (fora) → CARA 47,32. RANI3 (carteira) 5,59 → 3,10 — já estava acima da saída (P/C 1,42 → 2,56). Ninguém chega ao preço de
compra. ABEV3 deixa de "vencer a RF". Financeiras sem mudança. Dossiês salvos (BLAU3, CMIN3, HYPE3, LEVE3) ficam no disco; o recálculo
na mesma data está fixado em `tests/test_dossie_fichas.py`.

**Pendências.** (1) LEVE3 e ISAE4: o dossiê diz qual premissa diverge (g, payout, P/L final) ou corrige — até lá, sem palavra.
(2) `kd_ri` de cada não financeira pelo RI (começar pelas de D/E > 1: SUZB3, SMTO3, SLCE3, RANI3, KLBN11). (3) Tabela de spread:
reconferir em jan/2027. (4) Triagem e backtest seguem com o Ke fixo (motor reduzido congelado) — declarado no `06`.
(5) Conferir o texto de Hamada 1972 e MM 1958 (hoje nota B por referência).

**O que me provaria errado.** Se o Ke de 21–27% real das muito alavancadas (SUZB3, SLCE3, RANI3, SMTO3) for desmentido pelo mercado de
dívida delas (spread de debênture muito abaixo do sintético) ou se o ponto fixo for instável a pequenas mudanças de margem
(sensibilidade ±2 p.p. na ficha). **Revisão:** temporada do 3T26.

**Adversário (mesmo dia): 5 defeitos reproduzidos e corrigidos, sem troca de palavra.** (1) O ponto fixo partia do PREÇO e desistia
se o primeiro central saísse ≤ 0: a KLBN11 dava −1,44 a R$ 18,62 e +1,72 a R$ 5 — o central voltava a depender do preço, que é o que
o AUD-13 proibiu. Agora parte do patrimônio contábil (sem PL positivo, de E = D) e dá 1,72 a qualquer preço (teste com 3 preços). O
Ke real de 77% da KLBN11 é a fórmula de Hamada com D/E 17,4: o valor da casa quase some sob a dívida, e a palavra é NÃO CONCLUSIVO pela
dispersão. (2) Os PDFs dos lotes 3, 5 e 6 descreviam a trava com o Ke de 19,30%, e o do lote 6 dizia "não se aplica" quando a trava é
justamente a causa do NÃO CONCLUSIVO. Agora usam o Ke da empresa. (3) As sensibilidades dos PDFs (`central_rapido`) usavam Ke de
5 p.p. e pesos a preço (SUZB3 44,36 contra o central 22,04). Agora usam a mesma base do central. (4) O anexo do dossiê mostrava o Ke
de 19,30%; agora mostra o Ke da empresa e o D/E. (5) Dívida sem linha de juros virava AAA em silêncio; agora falha alto.
**Não corrigido:** os PDFs dos lotes não foram regenerados nesta onda (seguem os de 05/10). Os textos fixos de "Ke da casa 19,30%" fora
da trava e das sensibilidades ficam para a Onda 1.4 (documentos).


**Correção depois do commit 49b5f53 (mesmo dia, achado pelo Frank ao rodar o backtest).** `pytest backtest -rf` deu 4 falhas que
passavam no 626ef5a. (1–2) `test_premio_parametrizado`: com o `Mercado` carregando o próprio prêmio (v2.4), `central_ao_ke` ainda
subtraía a constante `PREMIO_KE` e criava `Mercado(rf, pi)` com o prêmio padrão — então a constante voltava a mexer no resultado.
Agora usa `mk.premio` e o repassa (o mesmo na sensibilidade do motor de financeiras); o teste da "porta do prêmio" passou a provar a
porta nova: `avaliar` responde a `mk.premio` e não à constante. (3–4) `test_regua` [ISAE4, LEVE3]: a régua do backtest só vê âncoras
e preço, não tem Bogle nem Ke, logo não tem a trava do §9 — nos dois segue JUSTA, no hall é NÃO CONCLUSIVO. Divergência **declarada**
no teste (`DIVERGE_PELA_TRAVA`, com o motivo), não corrigida: a régua do backtest está congelada. Resultado: backtest **301 passed,
0 failed**; hall 345 passed; golden sem mudança. **Lição:** a suíte do backtest fica fora do `--ignore=backtest` do critério de
pronto — mudança no `Mercado` ou nos motores exige rodar as duas.


### 08/10/2026 — DECISÃO DE MÉTODO: Onda 1.3 da auditoria (decisão e gatilhos) · doutrina v2.5

**Reprodução antes de mexer (script, sem gravar nada).** Os 6 reproduziram, três de forma diferente da auditoria:
- **AUD-43:** no pregão de 06/10, KLBN11 (P/C 10,8) e SLCE3 (2,28), ambas NÃO CONCLUSIVO, saíam **"≥ SAÍDA"** no monitor; a ISAE4
  (carteira, NÃO CONCLUSIVO) sairia "≤ COMPRA" a ≤ R$ 18,04. O exemplo da auditoria (UNIP6) não vale mais: virou CARA e saiu do hall.
- **AUD-37:** exceção no monitor = nenhum boletim (só o `ultimo.log`, ignorado pelo git); código 1 só com download falho **e**
  pregão > 7 dias; o prompt de sexta aceitava um monitor de até 7 dias, ou seja, o da sexta anterior.
- **AUD-77:** as linhas da Onda 1.2 foram editadas à mão; (S) faltava em SUZB3, GGBR4 (26,10 ≥ 24,04) e PRIO3 e sobrava em KLBN11 e
  SLCE3 (NÃO CONCLUSIVO); LEVE3, ISAE4 e SLCE3 mostravam compra/saída, KLBN11 e RECV3 "n.a.". Nenhum teste lia o `03`.
- **AUD-67:** 37 de 41 preços = PREULT do COTAHIST de 02/10. Os 4 restantes vinham de sites (investidor10, StatusInvest, HG Brasil):
  PRIO3 63,35 × 63,01, VBBR3 37,66 × 38,15, UNIP6 56,78 × 57,02, UGPA3 38,51 × 38,61. A divergência de 1–11% da auditoria era contra
  05/10 (data deliberada, não erro).
- **AUD-33 (pior que o relatado):** o 0,34 é a mediana de |ΔP/C| com ∞ nos 6 excluídos, de um portão que o proxy reprovou (limite 0,15).
  O corte 1,44 tirava **4 dos 5 papéis que passam no portão** (TGMA3, INTB3, CURY3, TFCO4). O erro é proporcional: razão proxy ÷ golden
  nos 30 confiáveis com mediana 0,98 e os três maiores 1,65 (WEGE3), 1,68 (FLRY3) e 1,88 (HYPE3).
- **AUD-20 (mais amplo):** a condição do §11.2 ("investimento no FCO") só valia em **TAEE11 e ISAE4**. Na DFP 2025: SBSP3 6.02.01
  −13,74 bi no FCI; CPFE3, CMIG4, SAPR11, CSMG3 no FCI; CPLE3 e EGIE3 mistas. Nenhum código checava; não existe DCF regulatório; a base
  da Sabesp (R$ 70 bi) é nota C.

**DECISÃO DO FRANK — AUD-20 (método dos regulados).**
| Opção | Regra | Efeito |
|---|---|---|
| **1. Ajustar a regra (escolhida)** | v2.5: sem base regulatória **e** WACC regulatório de fonte A/B, P/VP justificado como **proxy declarado** em qualquer posição do investimento; a ficha diz FCO/FCI/misto com as linhas; base nota C só informativa | nenhum central muda |
| 2. Só registrar exceção | 7 de 9 fora da condição, provisoriamente | doutrina diria uma coisa e o motor faria outra em 7 de 9 |
| 3. DCF regulatório de verdade | TIR sobre a base da Arsesp com fonte A, começando pela SBSP3 | onda própria; palavra provavelmente igual (base-paridade ≈ R$ 10,2 contra 28,23) |
**Por quê:** uma exceção que vale para 7 de 9 é a regra; e sem base com fonte A/B não há DCF regulatório que o protocolo de fontes aceite.
Implementado em `lote2_energia.REGULADOS_DFC` (linhas da DFC, classificação calculada delas) e `metodo_regulado()` (texto da ficha),
com teste contra o ZIP da CVM.

**Decisões técnicas (minhas, pela doutrina).**
- **AUD-43:** `monitor_semanal.alerta()` exige a palavra; NÃO CONCLUSIVO → rótulo **"sem palavra"**, sem compra nem saída (§9: a compra
  só vem da palavra final; a trava diz que o central é suspeito, então a saída também é). O boletim destaca "Carteira sem palavra: ISAE4".
- **AUD-37:** falha vira boletim (`> **MONITOR FALHOU**` com o traceback); códigos **20** (dado velho) e **21** (exceção). O teste real
  do `.vbs` mostrou que python ausente também sai com 1 (código do `cmd`) — por isso códigos altos. O `.vbs` abre um aviso na tela
  quando o código ≠ 0. A tarefa **continua Interativa**: o aviso e o agente das 18h do Desktop só existem com a sessão aberta; com S4U a
  falha voltaria a ser silenciosa. Prompt de sexta v1.4: exige o monitor **desta sexta**; ausente/falho/velho vai no topo do boletim.
- **AUD-77:** `ferramentas/hall03.py` gera preço, central, P/C, compra, saída e a marca (S) do quadro geral e o bloco do hall do prompt
  de sexta; regra do (S) = a do monitor (preço ≥ saída e palavra ≠ NÃO CONCLUSIVO). `rodar_tudo.py` avisa quando o `03` diverge.
- **AUD-67:** `ferramentas/precos_hall.py` + `dados/precos_hall_2026-10-02.csv` (data e fonte por ticker); os 4 preços foram para o
  fechamento oficial; o `data_preco` do golden vem do snapshot, não da data da taxa. Golden: só P/C, DY, Bogle e nota dos 4 mudam.
- **AUD-33:** corte = 1,10 × a maior superestimação medida (1,8818) = **2,07**, lido de `triagem/dados/erro_proxy_2026-10-06.csv`
  (extraído da consulta de 06/10, que fica fora do git). Leitura: mesmo com o pior erro observado, o cortado estaria acima de 1,10.
  Amostra pequena e quase toda CARA, então o corte é provisório. Fila de 02/10 regerada (`--sem-registro`): 10 cortados em vez de 15;
  entram TGMA3 (1º, camada A), INTB3, ALUP11, GRND3; saem SYNE3, PNVL3, VALE3, GOAU4. O registro prospectivo **não** foi regravado
  (append-only; a fila de 02/10 fica registrada com a config antiga e o `06` avisa); a próxima triagem registra com a config nova.

**Efeito na carteira.** **ISAE4:** monitor e `03` deixam de mostrar compra e saída ("sem palavra"/n.a.) — antes sairia "≤ COMPRA" a
≤ 18,04; preço oficial já batia; é transmissora, a condição antiga do §11.2 vale, nada muda no método. **ITSA4, ABCB4, RANI3:** CARA e
"≥ SAÍDA" iguais; o (S) já estava certo; preços já eram oficiais. Nenhuma palavra do hall mudou.

**Pendências novas.** (1) O campo `capex` do `cvm_series.json` não pega as linhas de "ativo de contrato" (CPFE3 0,39 contra 5,35 bi;
CMIG4 vazio contra 6,46 bi; CPLE3; CSMG3) — hoje sem efeito, porque o perfil utility não usa capex; Onda 3 (dados). (2) PDFs dos lotes
e cópias do `UPLOAD CLAUDE DESKTOP/` (03, 01, prompt de sexta) seguem defasados — Onda 1.4 (AUD-19, AUD-35). (3) Os
`atualizar_hall_lote*.py` antigos não seguem a regra do (S)/NC; quem manda agora é o `hall03.py` (o teste pega qualquer regressão).

**Achado durante a onda.** `gravar_historico(..., caminho=HISTORICO)` prendia o caminho na definição: os testes que trocam
`HISTORICO` (e a rodada de conferência no scratchpad) gravaram 53 linhas no `ferramentas/monitor/historico.csv` versionado. O
caminho agora é resolvido na chamada, o teste prova que o arquivo real não muda, e o histórico voltou ao do último commit (cópia
das linhas descartadas no scratchpad da sessão; eram só de teste e da conferência, nenhuma rodada de sexta).

**Adversário (sem bloqueio; 7 ressalvas, todas corrigidas com teste).** (1) O §4 do `03` tinha os preços antigos de VBBR3 (P/C
3,62 → 3,66) e UNIP6. (2) A razão 1,88 do corte foi medida contra o golden de 06/10 (régua v2.2); contra o vigente o pior caso é
1,56 (HYPE3) e o corte seria 1,71. **Fica 2,07** (o maior dos dois, que corta menos), declarado no `06`, e um teste manda
recalibrar se a régua vigente passar a dar razão maior que a medida. (3) `hall03` trocava o 1º número de qualquer texto na célula
do central e apagava "(S)" no meio de frase; agora o número tem de abrir a célula e o (S) só conta antes de ";", de "**" ou no fim.
(4) Se o próprio boletim de falha não gravasse, o código saía 1 e o aviso dizia "nem rodou"; agora sai 21 e o log diz por quê.
(5) A falha depois de um boletim já escrito vai **para o topo** dele (o prompt de sexta e o aviso olham a abertura). (6) A ficha
da EGIE3 no PDF do lote 6 também diz onde está o investimento. (7) Restos de nome e comentário.

### 09/10/2026 — DOCUMENTOS: Onda 1.4 da auditoria (AUD-36, 69, 19, 35)

Nenhuma palavra, central ou regra mudou; só documentos e geradores. Cada achado foi reproduzido antes de mexer.

- **AUD-36 (versões citadas).** `08-prompt-recalculo-lote.md` mandava recalcular "pela doutrina v2.0" e o checklist "v2.1"; passou a
  v2.5 / v2.2. Também `05`, `02`, `00`, `README` (v2.3 → v2.5) e a frase do prompt de sexta ("recalculados pela v2.0/2.1"). O "PASSO 5 —
  v2.3" do `08` e o histórico dos lotes ficam: descrevem o que cada versão trouxe.
- **AUD-69 (células digitadas).** Não eram 3: **24 linhas** do quadro do `03` tinham "Ke implícito" ou "retorno de investimento" fora
  do motor (PETR4 20,3 × 21,8; SLCE3 15,9 × 21,1; KLBN11 12,5 × 20,0; as de 05/10 não acompanharam as Ondas 1.1/1.2). `hall03.py`
  agora gera as duas células (só o primeiro de cada na célula; sem valor → "n.d.") e `--corrigir` as reescreveu; teste novo cobre troca,
  "n.d." e idempotência. `hall03.py` sem divergência.
  *Limite:* o texto ao redor (ROIC, DCF reverso, "Ke da casa") ainda é digitado e pode estar mais velho que o número trocado.
- **AUD-19 (PDFs).** Os 6 PDFs reemitidos como `…_rev_09-10-2026.pdf` (v2.5; os antigos ficam na pasta como "versão anterior"); o §5
  do `03` aponta os novos. Conferido no texto: HYPE3 central 16,22 (era 19,60 no PDF velho); LEVE3 agora NÃO CONCLUSIVO, sem a saída
  50,98. **Achado:** `gerar_pdf_lote6.py` quebrava (`KeyError: 'por_metodo'`) porque a ficha NÃO CONCLUSIVO só tinha esse campo para a
  UNIP6 — o gerador estava parado desde a v2.4; `por_metodo` agora vale para todos.
- **AUD-35 (pasta do Desktop).** Decisão: a pasta `UPLOAD CLAUDE DESKTOP/` é só **cópia local**, então foi sincronizada com a raiz
  (9 .md, `COLAR-NO-CAMPO`, 6 PDFs novos; os 6 PDFs e .md antigos foram para `_historico/2026-10-09 antes da onda 1.4/UPLOAD CLAUDE
  DESKTOP/`). O **reenvio ao Claude Desktop continua SUSPENSO** (decisão de 08/10): nada foi enviado; se o Frank retomar o agente de sexta no
  Desktop, basta subir a pasta como está.
- **Testes:** `pytest --ignore=backtest` 377 verdes; motor e `Mercado` intactos, então o backtest não rodou.
- **Adversário (sem bloqueio depois de 4 correções, com teste de texto nos PDFs).** (1) Os PDFs dos lotes 2 e 3 davam compra/saída
  para SLCE3, KLBN11 e ISAE4 (NÃO CONCLUSIVO) e a pergunta "compraria para ganho de capital?" dizia "compra ≤ R$ …": agora "n.a." e
  "sem preço de compra nem de saída (§9)", como o `03` e os lotes 5 e 6. (2) A capa do lote 6 dizia LEVE3 "preço justo" e UNIP6 "sem
  palavra": agora lê a palavra do motor. (3) A ficha da LEVE3 (NC pela trava, dispersão 1,08×) dizia "âncoras discordam > 3×": o motivo
  agora depende da dispersão. (4) A UNIP6 (CARA, dispersão 2,67×) ainda falava como NC; textos corrigidos.
  **Ressalvas aceitas:** `hall03` não reconhece o sinal "−" (U+2212) nem formatos como "≈20,3%" no Ke implícito (hoje nenhum caso); o
  texto dos bancos no PDF/`03` diz "pela v2.0" ao contar o histórico da rev. de 04/10 (data correta, não é regra vigente).

### 09/10/2026 — REPRODUTIBILIDADE: Onda 2, 1ª parte (AUD-38, 73, 109, 108, 17)

Nenhuma palavra, central ou regra mudou (`rodar_tudo.py`: "sem mudanças em relação ao golden", também no clone limpo). Cada achado foi
reproduzido antes de mexer.

- **AUD-38/73 (clone do zero).** Reproduzido: `git archive` + `pytest --ignore=backtest` aborta na coleta (`FileNotFoundError: itr_2026.zip`,
  porque `lote4`/`lote6` abriam o ZIP no import). Agora `derivados_zip.obter()` recalcula dos ZIPs quando existem e, sem eles, lê o
  snapshot versionado `dados/derivados_zip.json` (5 chaves: ações de jun/26 dos lotes 4 e 6, proxy de arrendamento, Itaúsa, base E&P da PRIO3) e avisa em
  stderr; teste confere snapshot = recálculo quando os ZIPs estão no disco. `requirements.txt` (6 libs, versões de 09/10), `bootstrap_dados.py`
  (`--baixar/--verificar/--derivados`) e parágrafo no README. Os 9 testes que dependiam do suplemento da B3 (`backtest/dados`, fora do
  git) agora saem como PULADOS com motivo (`dados_opcionais.py`). Clone limpo: 375 passam, 18 pulados.
  *Decisão:* snapshot em vez de dados de teste fabricados — é o mesmo código sobre os mesmos ZIPs, com o teste de igualdade impedindo a
  defasagem. *Limite:* no clone limpo o parser dos ZIPs não é exercitado (só o snapshot); isso exige `--baixar`.
- **AUD-109 (manifesto).** `manifesto_cvm.py` + `dados/cvm/MANIFESTO.json` (sha256 e tamanho de 77 ZIPs). `temporada.baixar_itr` guarda
  a cópia datada do ZIP anterior em `dados/cvm/_antes/` (ignorada pelo git) e atualiza o manifesto; antes sobrescrevia sem rastro. Teste: ZIPs
  em disco = manifesto. A CVM reescreve arquivos, então diferença é aviso a investigar, não prova de erro.
- **AUD-108 (EOL do golden_sha).** Reproduzido: o sha gravado (`a451c0c2…`) é o do arquivo em CRLF e não bate com o blob do git. Agora
  `registro_prospectivo.sha_arquivo` normaliza CRLF→LF antes do hash (= sha do blob) e `.gitattributes` fixa LF no golden, no registro e nos
  novos JSON. As 41 linhas já gravadas com o sha antigo ficam como estão (append-only) e não são reverificáveis por esse caminho.
- **AUD-17 (teste analítico).** `tests/test_aud17_ddm_analitico.py`: P/VP justificado, g com teto, DDM com ROE constante = Gordon
  (1/0,105) e DDM convergindo com valores de papel (VP 8,6015, terminal 11,6982). Mutações testadas à mão (Ke+g no denominador; desconto
  t−1): ambas derrubam o teste. Motor intacto.
- **Testes:** `pytest --ignore=backtest` 392 verdes + 1 pulado; motor e `Mercado` intactos, o backtest não rodou.
- **Adversário (4 achados; 3 corrigidos).** (1) `import universo` baixava `itr_2026.zip` sozinho pelo `lote5_petroleo.base_ep("PRIO3")`
  (fora do manifesto, e misturava snapshot com ZIP novo): agora é a 5ª chave do snapshot; teste importa `universo` sem ZIP e sem rede.
  (3) `baixar_itr` aceitava HTTP 200 com HTML como ZIP: agora valida `is_zipfile` antes de trocar e de registrar. (4) `--derivados` com ZIPs
  parciais gravava snapshot misto: agora exige as 5 chaves. **(2) Aceito:** re-registrar a rodada de 02/10/v2.2 com o golden CRLF antigo
  levantaria `ValueError` (o sha entra na comparação do hall); o golden mudou desde então, então a rodada nunca mais é regravada. Registrado
  no docstring de `sha_arquivo`. *Fora do escopo, antigo:* `test_veredito_salvo_reproduz` tem 0 casos (todos os vereditos estão em SUPERADOS ou
  no método da Onda 1.1) — não confere nada hoje.

### 09/10/2026 — TESTES QUE DISTINGUEM CERTO DE ERRADO + BACKUP: Onda 2, 2ª parte (AUD-05, 27, 28, 30, 31, 88, 89, 90)

Nenhuma palavra, central ou regra mudou (golden intacto). Cada achado foi reproduzido por mutação antes do teste; os 17 mutantes
abaixo agora morrem em `tests/test_aud27_31_formulas.py` (33 testes, números escritos à mão, sem importar as constantes do motor):
nota de qualidade 8→5, saída 1,50→1,40 e 1,30→1,25, 8 de 10 anos→6, IRRF do JCP 17,5→15% e com sinal trocado, IR do resgate 15→10%,
borda da régua (`<` no lugar de `<=`, 0,70→0,75), sinal da defasagem, ROIC nominal no lugar do real, `LIMIAR_ORIGEM` 0,15→0,10,
`LIMITE_QUEBRA` 0,25→0,40, `JANELA_MINIMA_SAIDA` 10→8, `MINIMO_ANOS_ALIQUOTA` 3→2 e a checagem de NaN do golden.
- **AUD-05 (backup).** O achado dizia "sem remoto"; hoje há remoto privado no GitHub, com `master` igual ao local. Faltava cópia do que
  não se recria: `backup_dados.py` grava no OneDrive um ZIP (180+ arquivos, ~1 MB: `dados/` sem `cvm/`, mais o log append-only e a
  consulta original do proxy) e um `git bundle`. Os 2 GB de ZIPs da CVM e COTAHIST são públicos e voltam pelo `bootstrap_dados.py`.
  `ferramentas/dados/_historico/` (cópia anterior ao AUD-02) entrou no git.
- **AUD-27/28/31/88/90.** `qualifica_saida(anos_serie, anos_acima, nota)` foi extraída do motor (mesma expressão) para ter limiar testável.
  AUD-31: para os 41 tickers o teste refaz fora do motor o fator de defasagem, o yield líquido do JCP (0,175), o Bogle e o Bogle líquido real.
- **AUD-30.** O golden tratava NaN como igual e `palavra(NaN)` dava CARA: agora NaN nunca é igual (nem a outro NaN) e `salvar` recusa NaN.
- **AUD-89.** Skip por falta de dado não é verde: o resumo do pytest diz quantos pularam e `EXIGIR_DADOS=1` transforma skip (inclusive
  de módulo) em falha; xfail continua xfail.
- **Adversário (4 defeitos, todos corrigidos):** o backup deixava de fora `proxy_consultas.log` e `proxy_2026-10-05.json`; destino relativo
  quebrava o bundle; destino dentro de `dados/` entrava no próprio ZIP; o hook tratava xfail como skip e não pegava skip de módulo.
- **Aprendizado:** rodei a suíte enquanto o pytest do backtest ainda corria em segundo plano e deu 9 falhas falsas (ABEV3 e outros);
  sozinha, a suíte passa. Regra de memória reforçada: nunca dois pytest ao mesmo tempo.

### 09/10/2026 — REPRODUTIBILIDADE DE REGISTRO, COLETORES E HISTÓRICO: Onda 2, 3ª parte (AUD-102, 82, 24, 26, 86, 21, 22, 23, 81, 83, 84)

Nenhuma palavra, central ou regra mudou (golden intacto; `cvm_series.json` não foi regravado). Cada achado foi reproduzido por script
antes de mexer (KeyError 'TAEE11' com `series_` parcial; VIVT3 DPA 2026 2,098→0,846 conforme o import; HYPE3 2024 com a linha de
01/02/2024 duplicada na B3; ISAE4/SLCE3/KEPL3/SMTO3 com o LTM refeito contra o comparativo).
- **AUD-102 (registro).** `prospectivo/registro.chain` guarda o sha256 encadeado de cada linha; `registro_prospectivo.py --verificar` e
  `_gravar` recusam registro editado, apagado ou com linha inserida. Limite declarado: quem reescreve registro e corrente juntos passa; o git é a
  segunda trava. Corrente das 47 linhas existentes criada hoje.
- **AUD-82 (preço real).** Rodada nova grava o fechamento do snapshot `precos_hall_<data>.csv` (RECV3 deixa de ficar sem preço). As linhas
  de 02/10 **não foram editadas** (append-only): PRIO3 63,35 (oficial 63,01), UGPA3 38,51 (38,61), UNIP6 56,78 (57,02), VBBR3 37,66 (38,15)
  e RECV3 sem preço (11,20). Reexecutar a rodada de 02/10 agora levanta `ValueError` nesses 5; a rodada nunca é regravada.
- **AUD-24 (série vigente).** `series_vigente.py`: arquivo vigente é constante (`series_2026-10-05.json`) e o carregamento exige 41 tickers;
  `motor_nao_financeiras`, `lote2_energia` e `defasagem` deixaram de pegar o "último da pasta". Trocar a série = editar a constante.
- **AUD-26 (estado do lote 4).** `corrigir_proventos` e `arrendamento_pago_proxy` já eram idempotentes (medido); o efeito por import
  continua (lê SI antes do lote 4 → DPA sem correção), agora documentado e fixado por teste: idempotência e instantâneo dos 41 igual
  importando o lote 4 antes ou depois (subprocessos).
- **AUD-21/22/86 (LTM).** `coletar_cvm.py`: o LTM usa o acumulado do ano anterior **reapresentado** (coluna PENÚLTIMO do ITR corrente) e
  registra `reapresentados` quando difere > 0,5% do ITR original; a SMTO3 (exercício abr–mar) monta FY(mar/26) + YTD abr–jun/26 − YTD
  anterior; componente ausente vira `lacunas` e erro vira `erro` + aviso (antes: `except: pass`). **Os dados não foram regravados — decisão
  do Frank.** Impacto medido se regravar (motor com o LTM novo, só os 4): palavras não mudam; ISAE4 EBIT −3,2% / lucro −5,8%, SLCE3 FCO
  −3,6%, KEPL3 FCO −1,3% (central/P/C iguais à 6ª casa); **SMTO3** receita −4,4%, EBIT −8,2%, FCO −11,3%, central 16,03 → 14,68 (P/C 1,21 → 1,32,
  segue CARA). Lacunas hoje no arquivo: SAPR11 e TIMS3 sem `lucro_controlador`, CMIG4 sem `capex` no LTM.
- **AUD-23 (JCP duplicado).** O dossiê reusa a regra de duplicata do backtest (`sem_repeticao`, 1% dentro de ticker+data-com+tipo): DPA 2024
  da HYPE3 1,2651 → 1,1678 (= StatusInvest); `carregar` grava `divergencias_b3_si` (alerta > 3%). O veredito de HYPE3 de 02/10 não foi
  refeito (dpa5 ~−1,6%); vale na próxima data de dossiê.
- **AUD-81 (macro).** `coletar_macro_fred.py` baixa as 9 séries FRED e a PTAX (SGS 3698), confere a parte comum (divergência = nada gravado,
  `--aceitar-revisoes` para revisão do BLS), guarda o arquivo anterior em `_historico/` e escreve `dados/macro/MANIFESTO_MACRO.json` (URL,
  data de coleta, intervalo, sha256); os 10 arquivos existentes entraram no manifesto como "coleta anterior a 09/10/2026". Os dados macro
  não foram rebaixados.
- **AUD-83/84 (histórico).** `monitor/historico.csv` agora é upsert por (rodada, pregão, ticker) — 164 → 123 linhas, as 41 repetidas eram
  idênticas; original em `_historico/2026-10-09 monitor historico/`. `historico_arquivos.py` (`guardar`/`gravar_texto`) copia o vigente
  para `_historico/AAAA-MM-DD <rótulo>/` antes de regravar: 6 `atualizar_hall_lote*`, `hall03 --corrigir`, `triagem/rodar` (o 06), 6 `gerar_pdf_lote*`
  e o histórico do monitor; só copia quando o conteúdo muda (CRLF×LF não conta).

### 09/10/2026 — DADOS: cvm_series.json regravado com o LTM novo (decisão do Frank, AUD-21/22/86)

Decidido por "ok, regrava" depois da recomendação de não misturar a correção com a temporada 3T26. Antes de gravar, medi os 41 contra o golden:
**nenhuma palavra muda**; 8 mudanças em 2 tickers. **SMTO3** (exercício abr–mar, comparativo reapresentado): central 16,03 → 14,68, P/C 1,21 → 1,32
(segue CARA), âncoras DCF 16,03 → 14,68 e EPV 14,88 → 13,58, nota geral 4,11 → 3,78, cobertura de juros 2,09 → 1,74, Bogle nominal 1,96% → 0,67%.
**UGPA3**: só a cobertura de juros, 3,00 → 2,92. O adversário havia previsto 6 tickers a mais (CMIG4, LEVE3, TAEE11, UGPA3, UNIP6, WEGE3): o LTM
deles mudou no arquivo (12 tickers em `ltm_2T26`), mas medido nos 41 o motor só moveu SMTO3 e UGPA3; central e palavra dos demais ficaram iguais.
- O que mudou no arquivo: `ltm_2T26` em 12 tickers; chaves novas `ltm` e `ltm_ref` nos 31; `proventos_a_pagar` em 307 exercícios que o arquivo antigo
  não tinha. Avisos do coletor: 10 tickers com ITR reapresentado (KEPL3, SLCE3, TAEE11, ISAE4, CMIG4, UGPA3, LEVE3, UNIP6, ABEV3, WEGE3) e
  TIMS3 sem `lucro_controlador` no LTM (lacuna já conhecida).
- Feito: golden regravado (`rodar_tudo.py --motivo`), `hall03.py --corrigir` (03 e bloco do prompt de sexta), PDFs dos lotes 3 e 5 reemitidos;
  anteriores em `_historico/` (cvm_series, hall03, PDFs). Cópia em `UPLOAD CLAUDE DESKTOP/` sincronizada (reenvio ao Desktop segue suspenso).
- Testes: hall 457 passed, 1 skipped. Backtest não rodou: o backtest lê parquets, não o `cvm_series.json`, e os motores não mudaram.
- **Atenção:** o boletim do monitor de 09/10 (`BOLETINS/2026-10-09-monitor.md`) mostra o central antigo da SMTO3 (16,03); não conferi o
  `registro.jsonl`. O registro só acrescenta, e a próxima rodada grava 14,68. A diferença é de dado, não de método.

### 09/10/2026 — SENTINELA PIT, PARIDADE DO MOTOR REDUZIDO E ITR SEM DRE: Onda 2, 4ª parte (AUD-29, 107, 91) — ONDA 2 CONCLUÍDA

Nenhuma palavra, central ou regra mudou (golden intacto). Só testes e uma guarda no coletor.
- **AUD-29.** O sentinela PIT comparava `procedencia()` e `anuais[].contas`; agora compara `anuais` e `ultimo_itr` inteiros (`Exercicio` é dataclass
  congelada: dfc, estado, versão, período) e a amostra é espalhada por todo o intervalo de `cd_cvm`, não as 40 menores. Mutação à mão: voltar ao critério
  antigo faz `test_5c` falhar ("vazamento em dfc passou despercebido").
- **AUD-107.** A máscara de visibilidade (7,5 mi de tuplas Python) virou `MultiIndex.isin`; `test_5` isolado passa em 198 s sem o estouro de 628 MiB.
  `test_mascara_visivel_bate_com_documentos_visiveis` confere a máscara contra a definição por tuplas; mutação (máscara aceitando futuro) falha.
  **Limite declarado:** com a máquina no teto (~11 GB de VS Code/navegador) a suíte inteira do backtest ainda pode estourar memória em cascata
  (9 falhas `MemoryError` numa corrida com outro processo ativo); rodada sozinha: 308 passed em 13 min.
- **AUD-91.** `backtest/tests/test_paridade_nf.py`: empresa sintética nos dois motores (IPCA achatado em 1, receita constante) — margem mediana,
  receita de meio, ajuste de manutenção, alíquota e retirada do excesso de "outras" coincidem; 8 mutações (6 no reduzido, 2 na mesa) morrem.
  **Divergências reais, fixadas e NÃO corrigidas:** (a) alíquota — o reduzido tem piso de 15% e aceita mediana de 1 ano; a mesa v2.3 manda 34% quando a mediana
  < 15% sem origem permanente e quando há < 3 anos válidos; (b) receita de meio — mediana da janela × média dos 3 últimos; (c) ajuste de manutenção —
  a mesa abate o capex de crescimento (Greenwald); o reduzido usa o capex total (cenário com receita crescendo: 0,0 × −0,0207). O backtest está parado e a trava anti-calibração (fatia 12) só admite corrigir o reduzido por prova sintética;
  se o backtest/triagem for retomado, decidir se o reduzido acompanha a v2.3 (o teste `test_divergencias_declaradas_*` vira e avisa).
- **Pendência menor.** `coletar_cvm.main` com SMTO3 e `mes=3` devolvia LTM só com `lacunas`, sem `receita` nem `erro`; agora ITR sem DRE acumulada
  levanta e vira `{"erro": ...}` (teste novo, falha sem a correção).

### 10/10/2026 — LIÇÃO: `dossie.gerar` sem `--data` sobrescreve o veredito vigente (rodada de 10/10 e checkup)
- **O que houve.** Rodada de 10/10: monitor semanal (boletim `BOLETINS/2026-10-10-monitor.md`, histórico em `_historico/2026-10-10 monitor historico/`) e, no passo
  "ver um dossiê", `python -m dossie.gerar HYPE3` **sem `--data`**. O comando grava em `<TK>-<data-base do hall>`, que era a data do dossiê de 02/10: o anexo
  `DOSSIES/dados/HYPE3-2026-10-02.md` e o veredito `dossie/vereditos/HYPE3-2026-10-02.json` foram regravados com o método atual (central 19,27 → 15,99; P/C 1,31 → 1,57;
  doutrina v2.2 → v2.3; palavra seguiu CARA). O registro prospectivo é append-only e confere o sha desse JSON: o próximo `--dossie` falharia.
- **Reparo.** Os dois arquivos foram restaurados do git; a versão regenerada ficou em `_historico/2026-10-10 hype3 regerado pelo passo 4/`. Nenhuma palavra mudou.
- **Lição.** Gerar dossiê "para ver" sem `--data` nova destrói o veredito vigente. Para ver o caso de hoje: `--data <hoje>` (exige `dados/mercado_<data>.json`).
- **Poka-yoke (feito).** `dossie.gerar.ja_registrado(tk, data)` lê `prospectivo/registro.jsonl`; se o veredito (ticker, data-base) já está lá, `gerar` sai com código 2 e a
  mensagem `RECUSADO`, sem gravar nada. Veredito ainda não registrado pode ser regerado (ajuste antes de registrar continua possível). Teste: `dossie/tests/test_gerar_recusa.py`.
- **Documentos alinhados (checkup de 10/10, `docs/auditoria/CHECKUP_2026-10-10.md`).** Cabeçalho do `03` (data do `hall03.py --corrigir`, 09/10), README, prompt de sexta e
  título do `04` com versão/data coerentes; raiz e `UPLOAD CLAUDE DESKTOP/` idênticos (exceto o parágrafo "Clone do zero" do README, só da raiz). Sem mudança de método.

### 10/10/2026 — DECISÃO DE MÉTODO: Onda 3 da auditoria (riscos latentes), doutrina v2.6 — ONDA 3 CONCLUÍDA
**Como foi feito.** Os 48 achados da Onda 3 foram reproduzidos antes de qualquer correção, por scripts no scratchpad (3 subagentes, sem pytest). Todos ainda valiam;
AUD-71, 97 e 55 tinham mudado em parte. Corte proposto e aprovado pelo Frank: corrigir o que é barato e não muda regra; parar (⏸) no que mexe em regra de valuation ou
no texto da doutrina; o resto fica **aceito** com motivo. Cada correção tem teste que **falha com a versão errada** (19 mutações à mão, todas pegas:
`tests/test_onda3_motor.py`, `tests/test_onda3_dados.py`). **Nenhuma palavra mudou nos 41.**

**Corrigidos sem mudar regra.**
- **AUD-11** — banco/utility com ROE ≤ 0 derrubava o motor das financeiras (Bogle complexo, divisão por zero) e P/C negativo saía BARATA com nota de preço 10. Agora: as
  guardas do motor de não financeiras (âncora, central ou LPA normalizado ≤ 0 → NÃO CONCLUSIVO; nota de preço 0).
- **AUD-52** — central ≤ 0 (RECV3) deixava compra e saída negativas e `"pc": Infinity` no golden (JSON inválido). Agora `precos_de_referencia` devolve vazio, o golden grava
  `null` e `golden.salvar` recusa infinito; `registro_prospectivo` e `atualizar_hall_lote5` aceitam o vazio.
- **AUD-46** — preço igual a 0,70 × central dava 0,7000000000000001 e caía em RADAR: `palavra` arredonda o P/C a 9 casas.
- **AUD-54** — DL/EBITDA indefinido (EBITDA normalizado ≤ 0) virava nota 10 na Solidez; agora é a pior nota (`nota_alavancagem`). A cobertura ausente segue com a nota mínima (conservador).
- **AUD-47** — âncora Owner Earnings descartada (OE ausente ou Ke real ≤ g) fica em `ancoras_descartadas`. **AUD-51** — aviso `aliquota_perto_do_limiar` (VIVT3, mediana 15,53%).
- **AUD-85 e AUD-103 (achado maior que o da auditoria).** O `temporada.py` importava os lotes ANTES de injetar o LTM novo: o cache da idade do imobilizado e as premissas que
  os lotes calculam no import (follow-on e solidez do lote 2, receita de meio do E&P, GGBR4/UNIP6, EGIE3) sairiam com o LTM velho no boletim do 3T26. Agora o LTM novo entra
  por `series_vigente.CVM_SOBREPOSTO` antes do import (um carregador só, `carregar_cvm`, com teste que proíbe ler o arquivo por fora), as causas do boletim vêm do arquivo
  oficial e `injetar` limpa o cache. O WEGE3 g1 depende só da StatusInvest e de π (sem efeito no 3T26).
- **AUD-45** — testes de precedência da régua (círculo, dispersão, NC) nos dois motores de produção. **AUD-63** — comentários de campo (roe_inicio é t = 0).
- **AUD-68 (dados).** A CVM entrega 3.11.01 = 0 com lucro ≠ 0 em SBSP3 2023-25, TIMS3 2022-23, KLBN11 2025 e KEPL3 2021: o coletor agora grava "sem dado" (mesma leitura de
  `backtest.motor.base.lucro_controlador`) e as ações do LTM vêm do ITR (SBSP3: 700 mi → 3.507 mi, desdobramento 5:1). `cvm_series.json` corrigido com as duas regras, sem
  recoleta (anterior em `_historico/2026-10-10 aud68 cvm_series/`); o LTM do controlador da SBSP3 (3,2 bi, era só o semestre) virou lacuna. Nenhum número do hall muda.
- **AUD-58 e 61** — fonte (ou falta dela) comentada em cada premissa digitada dos bancos; valores intactos.

**DECISÕES DO FRANK (⏸ de 10/10/2026).**
- **AUD-10** — trava de coerência na **palavra final**: a RADAR que sobe a JUSTA pela dispersão também precisa de Bogle a ±2 p.p. do Ke ou de `trava_razao` (o passo 3b
  dizia "pela régua" e o parágrafo da trava, "se o veredito é JUSTA"). Hoje nenhum ticker no caso.
- **AUD-15** — Owner Earnings pelo lucro do controlador (sem a linha, o consolidado). **AUD-34** — declínio (g < 0) com ROIC < WACC não libera capital (antes o
  "reinvestimento negativo" fazia o DCF subir com o declínio; só a RECV3 tinha o freio). **AUD-53** — cenário de DCF negativo entra como zero.
  Efeito: âncoras OE ABEV3 7,34 → 7,04, WEGE3 11,76 → 11,08, UGPA3 9,11 → 8,69 (as outras < 2%); centrais KLBN11 1,72 → 2,62 (segue NÃO CONCLUSIVO), SUZB3
  22,04 → 22,78, RANI3 3,11 → 3,19, RECV3 −3,67 → 0 (segue NÃO CONCLUSIVO); dossiê LEVE3 de 06/10 refeito 38,37 → 38,45 (palavra igual). Golden regravado com motivo.
- **AUD-42** — entrada parcial numa função só (`entrada_parcial`), com as cinco condições do §9 e o preço ≤ 0,80×; os PDFs testavam subconjuntos (só um o preço, nenhum o círculo).
- **Textos da doutrina alinhados ao motor (v2.6):** AUD-14 (a trava do crescimento é degrau por cenário), AUD-39 (Solidez sem Piotroski/Beneish), AUD-40 (carimbo do
  Tesouro pelo ponto médio), AUD-55 (defasagem da Vibra 8,5 meses).
- **Hall e prompt de sexta** regravados por `hall03.py --corrigir` (SUZB3, RANI3, KLBN11, RECV3).

**ACEITOS (não corrigidos), com motivo e quando reabrir.**
- **Backtest parado (06/10):** AUD-25 (elo ticker→CNPJ só pelo FCA), 79 (parâmetros de contaminação sem consumidor), 80 (sem embargo entre calibração e validação), 97 (portão
  mediu reprodutibilidade; o proxy já imprime os baselines). Reabrir antes de retomar o backtest.
- **Premissas deliberadas, sem troca de palavra:** AUD-50 (ROIC a reposição deflacionado, D7), 56 (ROE lp das utilities na janela longa), 62 (DPA do ITUB4 com extraordinário;
  só DY/Bogle/teto), 70 (PIB real de LP 2%, escolha da casa), 74 (bancos na StatusInvest, nota C, CARA com folga), 104 (prêmio de 5 p.p., D5 aberta), 44 (âncoras de
  bancos/utilities não independentes, consequência do §11.2). Reabrir se algum ticker chegar perto da fronteira por essas premissas.
- **Sensibilidade e comunicação:** AUD-92 (registrar o ponto de virada nas decisões futuras), 93 (quadro Ke ±1 p.p. sem palavra), 94 (central residual de EV − dívida em 6
  tickers), 95 (EGIE3 a 3% da fronteira CARA), 100 (golden com 34 CARA não discrimina por palavra), 101 (cortes da régua sem estudo de sensibilidade), 66 (p25/p75 por posto
  mais próximo — declarar o estimador na próxima revisão da doutrina), 59 (payout terminal implícito quando o teto de g morde).
- **Dados e rolagem:** AUD-71 (só os `fatos_*.json` seguem sem leitor: documentação), 76 (anos literais — rolar antes do DFP 2026, mar/2027), **75** (Amortização e
  Rendimento entram no DPA da StatusInvest: KEPL3 1,07 → 0,76, VIVT3 1,46 → 1,24 se filtrar; só yield/Bazin/nota de renda. Exige regravar a série vigente e decidir
  caso a caso o "Rend. Tributado", que pode ser JCP — fazer na próxima coleta da StatusInvest).
- **AUD-41** — o "20 de 41 com razão vazia" é a razão do desconto de controlador (§5: "sempre declarado, inclusive zero"): hoje são **29** tickers com desconto zero sem
  razão escrita. Escrever as razões é julgamento por ticker (dossiê); os filtros 1–4 seguem sem função no motor e a regra "TIR < rf ⇒ CARA", só em texto. Aceito até o
  dossiê de cada ticker. (No ⏸ de hoje o item foi descrito como "razão de saída do hall" — descrição errada minha; nada foi implementado com base nela.)
- **Pré-registro (decisão do Frank: não mudar agora):** AUD-32 (regra de refutação sem poder), 98 (Ibovespa como comparador), 99 (qual linha do registro vale por rodada).
  Decidir juntos, numa sessão própria, antes da leitura de 2027.

**Revisão adversarial (10/10/2026, sem bloqueio).** Corrigidos: LTM do controlador da KLBN11 (−973 mi, conta com o 2025 zerado) virou lacuna, como na SBSP3
(cópia em `_historico/2026-10-10 aud68 cvm_series/cvm_series.2.json`; teste cobre todo ticker); `backtest/experimento/proxy.py` e `test_regua.py` aceitam o P/C null
do golden; motivos de `entrada_parcial` com vírgula decimal. Ficam registrados: (a) `entrada_parcial` não exige mais confiança "normal" — o §9 não exige; âncora
única (BBSE3) pode ser elegível; os PDFs antigos davam "aplicável" a B3SA3, CPFE3 e CXSE3 já CARA, o que a regra nova corrige; (b) ações do LTM da HYPE3 seguem
as do DFP (632,95 mi contra 703,99 mi no ITR, emissão real) — o central não muda (lote 4 usa as ações do ZIP) e a temporada do 3T26 troca; (c) o OE usa o
consolidado onde o controlador está sem dado (SBSP3, SAPR11, TIMS3 2021–25, KLBN11 2025, KEPL3 2021): série heterogênea, fallback declarado no §11.

## 14/10/2026 — B12, Onda 4 textual (rotina autônoma)
Corrigidos, **sem mudar motor nem palavra** (473 passed, 19 skipped; golden intacto): AUD-96 (rótulos "Ke ±1 p.p." dos PDFs agora dizem "prêmio de Ke" nas não financeiras e "rf real" nas financeiras; comentários dos motores), AUD-65 (texto da PETR4: o p25 de margem é de 2018, Brent ~US$ 71, não de 2016–17), AUD-87 (`encoding="utf-8"` nas leituras de macro de `lote5_petroleo.py`), AUD-48 (`02` lista as 5 condições da entrada parcial; parágrafo da exceção 1,50× no `01` sem o texto de 05/10 duplicado), AUD-105 (contagem de 76 testes datada de 05/10). **Fica aberto:** AUD-64 (tabela única de P/C por premissa na ficha da PETR4) → `BACKLOG.md` B23.

## 14/10/2026 — B24 (AUD-41): razão obrigatória no desconto de controlador
Decisão do Frank de 14/10 (`docs/DECISOES.md`). O §5 manda declarar o desconto "sempre, inclusive zero"; 29 tickers tinham zero com razão vazia. **Motor:**
`motor_financeiras.exigir_razao_desconto` (início do `avaliar` das financeiras) e a mesma falta em `exigir_declaracoes` (não financeiras): razão vazia em qualquer
`tipo` não roda. A função `filtros_1a4` citada na auditoria não existe; a trava ficou junto das outras declarações obrigatórias. **Razões:** só LEVE3 tinha fonte
nota A (D3 do dossiê: FRE 2026, CVM id 158212; DFP 2025 nota 11) e recebeu a razão; os outros 28 recebem o marcador `SEM_RAZAO` = "sem razão documentada" — o texto
das fichas cita só os PDFs de 07/09 e 03/10 ou nada, e não vira fonte. **Palavras: nenhuma mudou** (33 CARA, 5 NÃO CONCLUSIVO, 3 JUSTA antes e depois; golden
intacto; a razão é texto e não entra em número). Suíte 499 passed, 1 skipped. Teste novo trava a contagem de 28 `SEM_RAZAO`; cada fonte A/B achada (FRE) reduz a
conta (BACKLOG B26).
**Revisão adversarial (14/10/2026).** Corrigidos antes do commit: a sensibilidade "sem desconto" do `gerar_pdf_lote2.py` montava razão vazia e derrubaria o PDF do
lote 2 (agora tem razão; teste novo proíbe `"razao": ""` fora do default dos motores); a razão da LEVE3 citava a nota 11 para a compra de 2024 — a fonte é a DFP
2025 nota 13 — e omitia a ressalva do D3 (se a compra contar como interferência consumada, o desconto vira cenários; decisão não tomada). Suíte 500 passed, 1 skipped.

## 14/10/2026 — B25 (AUD-32/98/99): pré-registro da validação prospectiva
Decisão do Frank de 14/10 (`docs/DECISOES.md`), aplicada **antes de qualquer horizonte vencido** (o 1º vence em 02/10/2027). `registro_prospectivo.py` ganha a
avaliação em funções puras (sem preço; o retorno entra como função): (1) **uma linha por (ticker, rodada)**, rodada = `data_preco`; hall e dossiê na mesma rodada →
vale o dossiê (HYPE3 02/10); `retroativa` = registrada depois do pregão (todo o hall de 02/10, registrado em 06/10) e a leitura sem elas é sensibilidade
obrigatória; (2) **comparador = média simples do retorno total do hall** (rodada hall mais recente ≤ a data da linha) no mesmo período; Ibovespa só informativo;
(3) **critério contínuo** = IC de postos (Spearman) entre P/C e retorno excedente por rodada (n ≥ 10), hipótese IC < 0; leitura com ≥ 4 rodadas: "apoia" se a média
< 0 e t ≤ −2, "contraria" se a média ≥ 0, senão "inconclusiva". Horizonte 1 ano (direção em 3). Retorno ausente (None/NaN/inf) sai e é contado, inclusive no
comparador (`hall_sem_retorno`). Gravação, append-only e corrente intactos (`--verificar`: íntegro). **Revisão adversarial:** corrigidos NaN do retorno (a máquina do
backtest marca falta com NaN; um só por rodada virava "apoia" em "contraria"), contagem do hall sem retorno, origem desconhecida e a sensibilidade sem retroativas
(o hall volta quando o dossiê é retroativo). Nenhuma palavra muda (não é motor).

## 19/10/2026 — DECISÃO DE MÉTODO: nota de fonte por campo nas não financeiras do lote (fase 3, fatia 1)
Plano da fase 3 aprovado pelo Frank (`~/.claude/plans/tingly-gliding-flute.md`): trocar a premissa digitada (nota C) por dado oficial, uma fonte por
vez, com data-base fixa (preço/mercado 02/10, LTM 2T26); temporada 3T26 e data-base nova em commits próprios. Fatia 1 = **só a nota, nenhum
número**: `rodar_tudo.py` sem `--motivo` → "sem mudanças em relação ao golden"; **nenhuma palavra mudou** (33 CARA, 3 JUSTA, 5 NÃO CONCLUSIVO).
Regras (em `relatorio/procedencia.py` + `ferramentas/insumos_a.py`): (1) um campo só tem a nota da fonte se o valor que a empresa carrega é o
que o lote registrou da fonte oficial (`insumos_a.registrar/origem`); literal ou valor sobrescrito = C; (2) o central das não financeiras usa o
provento já ex da B3 (A), não o DPA da StatusInvest — provado por teste (mexer no DPA e no `jcp_share` não mexe no central); o DPA C fica só nos
informativos (DY, Bazin, teto, Bogle); (3) o Kd entra nas âncoras de fluxo: sintético = B (Damodaran), `kd_ri`/`spread_kd` sem registro = C;
(4) todo campo de dado do `Industrial` fora do default que chega ao central pesa na nota (`DADO_ANCORA_NF`); julgamento (janela, g, desconto,
QUAL…) não é nota de fonte; teste obriga classificar todo campo novo.
Resultado nos 39 do caminho do lote: centrais **B 11** (ABEV3, B3SA3, FLRY3, KEPL3, KLBN11, RANI3, SMTO3, SUZB3, UGPA3, VBBR3, VIVT3; antes C),
**C 26**, **— 2**. As 8 NF ainda C e o porquê: SLCE3 (NAV das terras digitado, Itaú BBA), TIMS3 (alíquota 18,3% digitada), WEGE3 (g1 medido na
StatusInvest), PETR4/PRIO3/RECV3/GGBR4/UNIP6 (receita de meio pelo índice de commodity do FRED/BLS, sem nota registrada) → fatia 3. As 20
financeiras seguem C/— → fatia 4. Os 8 dossiês passam de A para **B** (mesmo Kd sintético; continuam decidindo).
**Revisão adversarial (19/10):** 2 achados corrigidos antes do commit — o Kd sintético entrava no central sem nota (as 18 que saíam A eram, na
verdade, B) e `receita_meio`/`da_receita`/`aliquota`/`aliquota_fase`/`g1_real` estavam classificados como julgamento, mas são números que chegam
ao central (dado). Achado lateral para a fatia 2b: `dossie/base.py:130` filtra `tipo_acao == "ON"` fixo; FESA4 e SHUL4 são PN.
