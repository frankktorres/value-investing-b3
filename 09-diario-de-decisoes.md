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

## 20/10/2026 — DECISÃO DE FONTE: DPA/JCP das não financeiras do lote saem da B3, não da StatusInvest (fase 3, fatia 2)
Plano da fase 3 (aprovado em 19/10). O DPA/JCP por ano da data-com das **21 não financeiras dos lotes** (as 19 do caminho do lote + HYPE3 e LEVE3,
que a tela mostra pelo dossiê) vem agora do cache da API pública da B3 (`dados/proventos_hall/`, nota A), por `ferramentas/proventos_hall.py`,
aplicado no carregamento do motor (antes de qualquer lote: o resultado não depende mais da ordem de import, AUD-26). Saíram as correções à mão
`lote4.corrigir_proventos` (VIVT3 sem "Amortização", vírgula da ABEV3) e o ajuste aproximado de GGBR4/UNIP6 pela contagem de ações
(`lote6.ajustar_dpa`; EGIE3, financeira, fica). As financeiras (lote 1, lote 2, ITSA4, EGIE3) seguem na StatusInvest até a fatia 4; a g1 da WEGE3
continua medida na série da StatusInvest até a fatia 3 (por isso o central dela não muda).
Regras (generalizam `dossie.base.proventos_b3`): classe do ticker (`proventos_ex.CLASSE`: PN, PNB, unit); lista fechada de tipos — dividendo,
JCP e rendimento (atualização do dividendo, PETR4) entram, **restituição de capital fica fora (§6.4)**, tipo novo falha alto; data-com de 2016
até a data do preço; eventos em ações = suplemento da B3 + os que a B3 omite e o **FRE da CVM** traz (KEPL3 desdobramento 1:3 de 2022; SLCE3
2019, 2021 e 2023; GGBR4 2023; UNIP6 2018, 2019 e 2022; Klabin +10% em 2024, que nem a B3 nem a tabela de desdobramento do FRE publicam — saiu
do capital integralizado do FRE e foi achada pela conferência das ações da CVM ano a ano, agora teste); provento com data-com até a do evento
(inclusive o mesmo dia) é dividido pelo multiplicador.
**Achado que derruba o AUD-23:** linhas iguais na API (mesma data-com e tipo) são, quase sempre, **parcelas**, e cada linha traz o valor da parcela.
Conferido contra o total declarado na DMPL da CVM (nota A): KLBN11 dez/25 (4 × R$ 0,228/unit = R$ 1,112 bi de intercalares), B3SA3 2025
(R$ 3,024 bi de JCP), PETR4 2024 (R$ 100,9 bi) e 2025, TIMS3 2024 (R$ 1,310 bi de dividendos) e 2025, WEGE3 dez/25 (o extraordinário em 3
parcelas), FLRY3 e RECV3 — a soma bate, a linha única não. Repetição de verdade só na HYPE3 em 01/02/2024 (DMPL = uma linha). Os 14 grupos estão
classificados com a prova em `GRUPOS_CONFERIDOS`; grupo novo falha alto. A StatusInvest às vezes soma as parcelas (KLBN11) e às vezes perde
(PETR4 2024, WEGE3 2025, UGPA3 mar/2024). O dossiê e o backtest ainda usam a regra antiga (`sem_repeticao`) → fatia 2b.
**B3 × StatusInvest, DPA por ação de hoje** (negrito = difere mais de 0,5%; entre parênteses a StatusInvest bruta, antes das correções do lote):

| Ticker | 2021 | 2022 | 2023 | 2024 | 2025 | 2016–25 B3 × SI |
|---|---|---|---|---|---|---|
| SUZB3 | 0,00 | 3,13 | 1,16 | 2,02 | 1,12 | 8,25 × 8,82 |
| KLBN11 | **0,33** (0,37) | **1,36** (1,51) | **1,22** (1,35) | **1,32** (1,37) | **1,68** (1,70) | 8,57 × 9,15 |
| RANI3 | 0,35 | 0,64 | 0,85 | 0,53 | 0,73 | 3,22 × 3,22 |
| B3SA3 | 0,97 | 0,48 | 0,42 | 0,37 | **0,59** (0,45) | 4,48 × 4,33 |
| SMTO3 | 2,33 | 1,13 | 1,24 | 1,35 | 0,46 | 8,67 × 8,99 |
| KEPL3 | **0,28** (1,81) | 1,00 | 0,86 | 0,84 | 0,84 | 3,97 × 5,51 |
| SLCE3 | **0,39** (0,53) | **1,12** (1,39) | **1,10** (1,35) | **0,74** (0,83) | **1,29** (1,45) | 6,26 × 8,99 |
| TIMS3 | 0,43 | 0,58 | 0,91 | **1,14** (0,96) | **2,51** (2,23) | 6,02 × 6,70 |
| VIVT3 | 1,73 | 1,53 | 1,03 | **0,95** (1,40) | **1,05** (1,60) | 13,71 × 14,71 |
| FLRY3 | **0,91** (0,96) | **0,96** (1,00) | 0,43 | 0,70 | **1,68** (1,55) | 8,82 × 8,99 |
| HYPE3 | 1,23 | 1,23 | 1,23 | 1,17 | 1,17 | 11,32 × 11,32 |
| ABEV3 | 0,68 | 0,76 | 0,73 | 0,67 | 1,11 | 6,59 × 6,59 |
| WEGE3 | 0,42 | 0,52 | 0,61 | 0,76 | **2,45** (1,62) | 5,59 × 4,86 |
| PETR4 | 5,65 | 16,77 | 7,32 | **7,90** (6,53) | **3,27** (2,94) | 42,75 × 41,09 |
| PRIO3 | 0,00 | 0,00 | 0,07 | 0,00 | 0,00 | 0,07 × 0,07 |
| RECV3 | 0,00 | 0,78 | 0,99 | 2,75 | 0,90 | 5,42 × 5,42 |
| UGPA3 | 0,64 | 0,58 | 0,35 | **0,65** (0,25) | 1,75 | 7,15 × 6,75 |
| VBBR3 | **1,90** (2,04) | **0,80** (0,86) | **0,78** (0,83) | **1,47** (1,27) | **1,48** (1,58) | 11,10 × 11,66 |
| GGBR4 | **2,44** (3,07) | **2,88** (3,63) | **1,33** (1,61) | **0,78** (0,80) | 0,62 | 8,91 × 10,81 |
| UNIP6 | **12,76** (15,44) | **12,46** (13,95) | **3,16** (3,48) | **4,09** (4,23) | 12,48 | 51,41 × 59,17 |
| LEVE3 | 1,47 | 4,49 | 9,88 | 2,36 | 2,72 | 26,17 × 26,17 |

Causas: eventos em ações que a StatusInvest não ajusta (KLBN11 +10% em 2024 e +1% em 2025; SLCE3 ×2,75 desde 2016; FLRY3 +5% em 2023; VBBR3
+7,1% em nov/25; GGBR4 e UNIP6 bonificações); restituição de capital que ela soma (KEPL3 2021, VIVT3 2024–25); parcelas que ela perde (PETR4 2024–25,
WEGE3 2025, B3SA3 2025, TIMS3, FLRY3) ou provento ausente (UGPA3 R$ 0,40 de 07/03/2024); VIVT3 2025 a StatusInvest dividiu o JCP de fev e abr/25
por 4 em vez de 2. As mesmas na HYPE3 e LEVE3 dão o DPA do dossiê (oráculo, teste).
**Efeito no golden (antes → depois), com `--motivo`:** nenhuma palavra, central ou âncora muda (teste: com o DPA da StatusInvest no lugar,
central/âncoras/palavra das 21 são idênticos). 15 mudanças em 7 tickers, só em informativos e na nota de renda: B3SA3 DY 3,29% → 3,45%, Bogle
11,42% → 11,58%; GGBR4 DY 7,87% → 7,36%, Bogle 15,39% → 14,88%, **vence a RF Empate → Não**, nota 4,70 → 4,65; KEPL3 nota 5,70 → 6,20 (DPA médio
sem a restituição passa a caber no caixa); SUZB3 nota 3,32 → 3,26; TIMS3 DY 5,73% → 5,85%, Bogle 13,67% → 13,80%, nota 4,06 → 3,33; UGPA3 DY
2,08% → 2,30%, Bogle 9,60% → 9,83%; WEGE3 DY 1,49% → 1,79%, Bogle 12,83% → 13,13%. A `nota_geral` não estava prevista na missão (só DY/Bogle/RF):
a nota de renda usa o DY líquido, a cobertura do DPA pelo caixa e os anos pagos — consequência direta, não de método.
**Limitação declarada:** "anos pagos" conta só o próprio ticker na B3 — TIMS3 perde 2016–19 (eram da TIM Participações, TIMP3) e SUZB3 2016 (a
PNA, SUZB5); linhagem de código fica no `BACKLOG.md`. Nota de fonte: o DPA das 21 passa de C para A em `procedencia` só se o valor que o motor lê é
o registrado (anti-lavagem testado); DY/Bogle continuam C pela defasagem (datas da StatusInvest) e pelo P/L histórico digitado (fatia 3).
**Revisão adversarial (20/10):** nenhum defeito que mude central, âncora ou palavra (conferidos: ITSA4/EGIE3/lote 2 idênticos, g1 da WEGE3
idêntica, `dossie.isolado`, anti-lavagem da nota, regra do mesmo dia, pares TIMS/VIVT, classe por ISIN, eventos do fim de 2025 contra o DFP).
Corrigidos: (1) o mesmo evento nas duas fontes com a data-com deslocada um pregão entrava 1,1 × 1,1 — agora mesmo tipo a até 45 dias falha
alto (teste); (2) o teste das ações da CVM aceitava evento contado duas vezes (piso 0,5 → 0,92; a maior recompra medida é 0,938) e declara o que
não cobre (SMTO3 2016, SLCE3 2016–19: só o teste local de FRE/COTAHIST). Aceitos: a trava de coerência (§9) usa o Bogle, que usa o DPA — uma
JUSTA pode virar NÃO CONCLUSIVO só pelo DPA; hoje a folga é grande (KEPL3 0,2 p.p. e PETR4 0,6 p.p. do Ke, limite 2 p.p.) e o teste por ticker
pega a próxima; VBBR3 18/04/2024 como parcela tem prova fraca (o JCP bate exato com a DMPL, os dividendos não batem com nenhuma das duas
leituras — fica a mais próxima). Suíte: 723 passed, 0 skipped.

## 20/10/2026 — DECISÃO DE FONTE: o DPA/JCP do dossiê usa as regras do coletor do hall (fase 3, fatia 2b)
`dossie.base.proventos_b3` agora chama `proventos_hall.dpa_jcp(tk, DATA_BASE)` — cache da B3 do hall (`dados/proventos_hall/`, nota A), as mesmas
regras das 21 não financeiras do lote: **(a)** classe do ticker por `proventos_ex.CLASSE` (FESA4 e SHUL4 são PN; o dossiê filtrava ON fixo, e a
PN paga 10% a mais); **(b)** linhas iguais = parcelas que somam, salvo repetição conferida; os grupos dos 8 dossiês foram classificados contra a
DMPL da CVM e estão em `GRUPOS_CONFERIDOS` (grupo novo falha alto) — todos **parcelas**: SHUL4 dez/25 (ON e PN somadas × ações = R$ 100,0 mi =
5.04.06 da DMPL; uma por valor = 65,0), VLID3 2025 (4 parcelas de JCP em fev e 4 em nov: R$ 241,8 mi × 242,3 da DMPL; uma por data = 60,4),
VLID3 2019 (2 × R$ 0,35 = R$ 49,2 mi da DMPL) e 2016 (a DMPL lista três JCP de "R$ 0,23529 por ação"), ALLD3 dez/23 (DMPL 2023 R$ 22,5 mi +
ITR 1T24 R$ 67,5 mi além do JCP de mar/24 = R$ 90 mi = as 2 linhas; acumulado DMPL 2023–1S26 R$ 421,7 mi × linhas somadas 422,6, uma só 377,6);
HYPE3 01/02/2024 segue a única repetição; **(c)** restituição de capital fora (§6.4: HYPE3 2017 R$ 1,30; ALLD3 nov/25 R$ 1,90, que bate com a
5.04.08 da DMPL 2025); **(d)** eventos em ações = suplemento da B3 + os que ela omite e o FRE traz — **SHUL4 bonificações de 04/12/2018 (×1,4) e
15/04/2021 (×2,0)**, achadas pela conferência das ações do DFP do dossiê ano a ano (agora teste; a de 2021 dobrava as ações 2020 → 2021 sem
evento). Data-com até a data do veredito; série desde 2016 (os anos anteriores saem do dicionário — nenhum consumidor do dossiê os lia: motor
2016–25 e 2021–25, relatório 10 anos). Os mesmos eventos (B3 + FRE, `base.eventos`) passam a alimentar `pl_hist` e a diluição do dossiê.
**Achado de carona:** `evidencia.diluicao` não aplicava a escala das ações (`base.escala`): a VLID3 com o DFP 2020 em milhares saía 308% a.a. (o
certo é 2,5% a.a. pela subscrição de 2021 — continua ≥ 2%, a nota não muda). E `PARES_CONFERIDOS` (desdobramento + grupamento na mesma data)
aceitava o par pela data, com qualquer fator; agora exige o produto conferido (LEVE ×3, TIMS ×1, VIVT ×2) — nenhum número do hall muda.
A regra antiga (`sem_repeticao`, restituição somada) fica só em `base.proventos_b3_legado`, que o relatório das financeiras usa até a fatia 4
(9f), em `relatorio/renda.py` (renda de 12 meses da carteira) e no backtest (B29).
**Antes → depois, DPA por ação de hoje no veredito mais recente de cada dossiê** (negrito = muda; entre parênteses o de antes):

| Dossiê | 2021 | 2022 | 2023 | 2024 | 2025 | 2016–25 depois × antes | DY (informativo) |
|---|---|---|---|---|---|---|---|
| ALLD3 (15/10) | 0,76 | 0,92 | **0,97** (0,48) | 2,37 | **0,74** (2,64) | 5,76 × 7,17 | 16,62% = |
| BLAU3 (02/10) | 0,19 | 0,65 | 0,32 | 0,28 | 0,79 | 2,24 × 2,24 | 0,00% = |
| CMIN3 (06/10) | 0,47 | 0,92 | 0,78 | 0,74 | 0,44 | 3,35 × 3,35 | 0,00% = |
| FESA4 (15/10) | **0,21** (0,19) | **1,36** (1,24) | **0,69** (0,62) | **0,53** (0,48) | **0,73** (0,66) | 4,89 × 4,44 | 8,69% = |
| HYPE3 (06/10) | 1,23 | 1,23 | 1,23 | 1,17 | 1,17 | 11,32 × 12,62 (2017 sem a restituição) | 3,95% = |
| LEVE3 (06/10) | 1,47 | 4,49 | 9,88 | 2,36 | 2,72 | 26,17 × 26,17 | 12,20% = |
| SHUL4 (15/10) | **0,09** (0,08) | **0,22** (0,20) | **0,29** (0,27) | **0,48** (0,43) | **0,63** (0,41) | 1,96 × 1,92 (2016–20 caem: eventos do FRE) | 5,79% → 6,85% |
| VLID3 (15/10) | 0,00 | 0,29 | 1,22 | 1,78 | **3,08** (0,77) | 9,26 × 6,39 | 4,59% → 7,06% |

(DY = DPA sustentável, limitado pelo FCFE por ação; nas que não mudam o teto é o caixa.) **Efeito nos vereditos, recalculados na mesma data:**
nenhum central, P/C, palavra ou desconto muda nos 10 JSON de `dossie/vereditos/`. Única nota que muda: **SHUL4 15/10, gestão 0 → 1** (a
"diluição" de 14,8% a.a. era a bonificação de 2021 que faltava; CAGR das ações certo −0,03% a.a.), média da regra 11 1,83 → 2,00, palavra CARA
igual. O JSON salvo fica (registro append-only); o recálculo na mesma data está fixado em `test_dossie_fichas.CORRIGIDO_FATIA_2B`. Veredito novo
só com `--data` nova; nenhum foi gerado. Golden do hall intacto. Testes: `tests/test_fase3_proventos_dossie.py` (PN, parcelas, repetição,
restituição, eventos do FRE, grupos dos 8 dossiês, ações × eventos, diluição) e o oráculo da fatia 2 passou a comparar o hall com a regra antiga. Suíte: 747 passed, 0 failed.
**Revisão adversarial (20/10):** nenhum defeito reproduzido — provas dos 7 grupos refeitas na DMPL (ALLD3: os R$ 67,5 mi do 1T24 só
se explicam com 2 parcelas), data-base sempre pelo `na_data`/`c["data"]`, nenhum consumidor lê DPA antes de 2016, sem vazamento para o hall,
ISIN da PN certo, consumidores intactos. Aceito e declarado: a renda de 12 meses da carteira (`relatorio/renda.py`) segue a regra antiga e
subconta parcelas (VLID3 0,74 × 1,87 em 15/10) — docstring corrigida, troca na fatia 4 (9f).

## 20/10/2026 — Fase 3, fatia 3 (B15/9e): literais de dado das não financeiras → dado oficial registrado
Cada campo passou a ser calculado de fonte oficial e registrado em `insumos_a` (a nota só sobe se o valor usado é o registrado; literal por cima → C):
1. **Preço** — os lotes 3–6 leem `precos_hall.preco(tk)` (snapshot do COTAHIST de 02/10, A); a procedência do preço da NF do lote deixou de ser A
   incondicional. Os 21 literais eram iguais ao snapshot: nenhum número muda. Financeiras (ITSA4, EGIE3, lotes 1–2) seguem digitadas até a fatia 4.
2. **Receita de meio** — PETR4/PRIO3/RECV3 (`receita_meio` e `da_receita`: CVM × Brent EIA/DCOILBRENTEU × PTAX BCB × IPCA, A), GGBR4 (PPI BLS
   WPU1017, A), UNIP6 (PPI BLS soda A + WPU0662, página do FRED não aberta na conferência → **B**). `verificador-fonte` 20/10: o FRED espelha
   EIA/BLS/FMI sem transformar — a nota é a da fonte primária. Número não muda.
3. **CMIN3 (dossiê)** — a série do minério (FMI PIORECRUSDM via FRED, nota **A** pela conferência; o docstring dizia B) virou o insumo
   `preco_minerio` de `dossie/insumos/CMIN3.json`, exigido por `fichas/cmin3.minerio()` (sem ele, falha alto) e visto por `_insumos_dossie`.
   Central do CMIN3 segue B (Kd sintético); nada muda.
4. **Alíquota TIMS3** — `fiscal.tims3_aliquota`: 2024–25 calculadas = (IR registrado + incentivo SUDENE/SUDAM) ÷ LAIR, IR e LAIR dos dados
   abertos da CVM e o incentivo da nota 8.d da DFP 2025 (R$ 333,4 mi e R$ 442,1 mi; conferida no PDF do RI hoje): 22,1% e 15,1%, iguais às lidas
   em 08/10. 2021–23 seguem as lidas em 08/10 (19,3% · 4,5% · 18,3%; itens pontuais não estão nos dados abertos). Mediana 18,3% = antes.
   PRIO3 `aliquota_fase` (e HYPE3) ganharam `nota_fonte: "A"` declarada (o prazo vem do DFP; a efetiva da fase já era da CVM).
5. **g1 WEGE3** — `g1_sustentavel` com ROE = lucro ÷ PL do controlador (CVM), LPA da CVM e DPA da B3 sem as **3** parcelas do extraordinário de
   19/12/2025 (pela StatusInvest só saía a 1ª, arredondada em 0,4128): g1 real 6,874% → 6,876%, ROE 28,37% (= StatusInvest), payout 51,43% →
   51,42%. Central não muda na precisão do golden.
6. **NAV SLCE3** — o R$ 27,12 atribuído ao Itaú BBA não foi encontrado pelo verificador; a própria SLC publica o NAV (fato relevante "Portfólio
   de Terras: Atualização 2026", 15/06/2026: terras avaliadas pela Deloitte, R$ 13,53 bi; NAV R$ 13.824 mi ÷ 498.745.930 ações = **R$ 27,72**, A).
   Âncora de reprodução 27,12 → 27,72; central (7,59) e palavra (NÃO CONCLUSIVO) iguais.
7. **P/L histórico** — `pl_historico.do_hall`: fechamento do fim do exercício (COTAHIST) × ações do DFP ÷ lucro do controlador (CVM), mediana dos
   anos com 0 < P/L < 40 — a conta do dossiê, agora num módulo só; SMTO3 no fechamento de **março** (exercício abr–mar). Snapshot
   `pl_hist.<TK>` em `dados/derivados_zip.json` para clone sem COTAHIST. **Decisão (reversível):** janela 2020–25 — o DFP antes de 2020 não traz a
   composição do capital (a CVM não tem `acoes` 2016–19); é a mesma janela que o dossiê já usa. Estender com o LPA básico da DRE 2016–19 fica
   no BACKLOG. A StatusInvest errava a TIMS3 de 2023–25 (P/L 29/26/26 × 15/11/12 pela CVM: lucro do controlador zerado no consolidado).

**Antes → depois** (golden regravado com `--motivo`; 11 mudanças em 10 tickers, **0 trocas de palavra**, nenhum central, P/C ou vence-RF muda):

| Ticker | P/L hist. antes (fonte) | depois (CVM+COTAHIST) | Bogle nominal antes → depois | Palavra |
|---|---|---|---|---|
| ABEV3 | 19,16 (SI) | 15,36 | 15,37% → 13,12% | CARA = |
| B3SA3 | 20,3 (literal) | 16,67 | 11,58% → 9,63% | CARA = |
| FLRY3 | 18,62 (SI) | 17,34 | 9,13% → 8,43% | CARA = |
| HYPE3 (hall) | 13,88 (SI) | 13,57 | 9,79% → 9,56% | CARA = |
| LEVE3 (hall) | 7,60 (SI) | 6,98 | 18,63% → 17,80% | NÃO CONCLUSIVO = |
| SLCE3 | 10,6 (literal) | 9,89 | −7,86% → −8,44% | NÃO CONCLUSIVO = |
| SMTO3 | 9,7 (literal) | 9,21 (março) | 0,67% → 0,19% | CARA = |
| TIMS3 | 19,24 (SI) | 13,56 | 13,80% → 10,34% | CARA = |
| VIVT3 | 15,43 (SI) | 16,04 | 11,33% → 11,72% | CARA = |
| WEGE3 | 33,01 (SI) | 36,64 | 13,13% → 14,15% | CARA = |

**Procedência:** as 19 não financeiras do caminho do lote passam a ter o central A/B (eram 11; GGBR4, PETR4, PRIO3, RECV3, SLCE3, TIMS3, UNIP6 e
WEGE3 saíram de C); insumos C do lote nas âncoras 158 → 134. Trava de `tests/test_fase3_procedencia.py` subiu (`CENTRAIS_AB_MINIMO` 19,
`C_LOTE_NAS_ANCORAS_MAXIMO` 134), com testes de cada campo (registro + literal por cima → C, SMTO3 em março, TIM × CVM, 3 parcelas da WEGE3,
CMIN3 sem o insumo falha). Nenhuma ordem de compra ou venda decorre desta mudança.
**Revisão adversarial (20/10):** 3 defeitos reproduzidos, todos corrigidos, nenhum mudava número: **(1)** `--derivados` passou a exigir o COTAHIST
do backtest (sem os parquets, nem o snapshot da CVM regravava) → `CHAVES_CVM` exigidas, `CHAVES_COTAHIST` tudo-ou-nada e mantidas sem o
COTAHIST (teste); **(2)** `aliquota_fase` com nota declarada no próprio dict ficava A mesmo alterado (prazo 2045, fonte inventada) → o prazo agora é
REGISTRADO (`insumos_a` aceita texto dentro do dict, comparado igual) e a nota declarada saiu do `fiscal.py`; **(3)** bonificação com data-com no
último pregão do ano (SLCE3 30/12/2021 e 30/12/2025) entrava com ações novas e preço "com" → a regra usa o dia do fechamento usado
(`data_com >= pregão`); mediana da SLCE3 igual (os dois anos estavam nas pontas). O dossiê passou a usar a mesma conta (`base.pl_hist` →
`pl_historico.mediana`); os 10 vereditos recalculados não mudam (`test_dossie_fichas`). Texto da SLCE3 que ainda dizia "NAV de terceiro" corrigido.

## 20/10/2026 — B30 e B31: P/L histórico 2016–19 pelo LPA; TIMS3 2021–23 e WPU0662 conferidas na fonte
**B30 — decisão de método (reversível).** `pl_historico.mediana` (hall e dossiê, a mesma função) passa a cobrir 2016–19: o DFP antes de 2020 não
traz a composição do capital, então P/L do ano = fechamento (COTAHIST) ÷ **LPA básico da classe do ticker** (DRE 3.99.01.xx do mesmo DFP;
consolidado, ou individual se o consolidado faltar ou vier zerado — VLID3 2016–17). Três travas, todas por exclusão do ano (nada inventado):
(a) as ações implícitas (lucro ÷ LPA) ficam a menos de 25% das ações do 1º DFP com composição, levadas à base de preço do ano pelos eventos entre
os dois fechamentos; (b) evento com data-com no fechamento ou depois e aprovado até a entrega do DFP (DT_RECEB) deixa ambíguo se o LPA veio
reexpresso (CPC 41 §64) → ano fora; (c) LPA ≤ 0 → fora. 2020+ não muda (mesma conta, conferido `==`).
**Conferência LPA × ações 2020–25** (`test_lpa_basico_da_cvm_confere_com_lucro_sobre_acoes_2020_25`): nos 10 do hall, LPA × ações ÷ lucro fica
em 1 ± 5% em todos os anos com LPA, exceto TIMS3 2020 (0,105: erro de escala da CVM — a trava (a) o rejeitaria) e FLRY3 2022–23 (1,14 e 1,13:
média ponderada após a fusão com o Pardini, dentro da trava). Desdobramentos/bonificações de 2016–19 (SMTO3 dez/16, FLRY3 jun/17, WEGE3 abr/18,
SHUL4, SLCE3 abr/19) aparecem nas ações implícitas e passam na trava. TIMS3 não ganha anos (o ticker era TIMP3 antes de 2020: sem preço).
Declarado, não corrigido: em 2016–19 o P/L é o da classe; em 2020+ é preço × todas as ações — com PN de dividendo 10% maior, 3–7% de diferença
(FESA4, SHUL4, VIVT3 enquanto havia PN).

**Antes → depois** (golden regravado com `--motivo`; 8 mudanças em 8 tickers, só o Bogle, **0 trocas de palavra**, nenhum central muda):

| Ticker | P/L hist. 2020–25 | 2016–25 | Bogle nominal antes → depois | Palavra |
|---|---|---|---|---|
| ABEV3 | 15,36 | 19,15 | 13,12% → 15,36% | CARA = |
| B3SA3 | 16,67 | 18,92 (2018–25; BVMF3 antes) | 9,63% → 10,88% | CARA = |
| FLRY3 | 17,34 | 21,02 | 8,43% → 10,33% | CARA = |
| HYPE3 (hall) | 13,57 | 15,40 | 9,56% → 10,81% | CARA = |
| LEVE3 (hall) | 6,98 | 7,60 | 17,80% → 18,63% | NÃO CONCLUSIVO = |
| SLCE3 | 9,89 | 10,34 | −8,44% → −8,07% | NÃO CONCLUSIVO = |
| SMTO3 | 9,21 | 11,08 (março) | 0,19% → 1,91% | CARA = |
| TIMS3 | 13,56 | 13,56 (sem preço 2016–19) | = | CARA = |
| VIVT3 | 16,04 | 16,07 | = (abaixo da precisão do golden) | CARA = |
| WEGE3 | 36,64 | 32,99 | 14,15% → 13,12% | CARA = |

**Dossiê** (mesma função; veredito vigente não regerado — só com `--data` nova): FESA4 7,49 → 6,96, SHUL4 7,97 → 8,48, VLID3 7,70 → 12,08,
HYPE3 13,57 → 15,40, LEVE3 6,98 → 7,60; ALLD3/BLAU3 iguais (listadas depois de 2019), CMIN3 sem P/L. Recalculados com desconto zero: palavra e
central iguais nos 5 (o P/L só entra no Bogle). Nota do `pl_hist` segue A (valor registrado). Snapshot `pl_hist.*` de `derivados_zip.json`
regravado; `do_hall` agora exige também os DFP 2016–19 para recalcular.

**B31 — conferência na fonte.** (1) **TIMS3 2021–23**: conciliação do IR nas DFPs da TIM (RI, api.mziq.com: DFP 2022 p.145, DFP 2023 p.81, DFP
2024 nota 8.d p.73) — (despesa − SUDENE − pontuais) ÷ LAIR = **19,32% · 4,50% · 18,29%**: CONFERE as lidas em 08/10. Pontuais: 2021 venda da
I-Systems (−335,9 mi), Selic do indébito (+534,8 mi), reversão TIM Nordeste (+87,6 mi); 2022 prejuízo fiscal não reconhecido da Cozani
(−130,0 mi, efeito da aquisição — sem tirá-lo 2022 seria 12,1% e a mediana 2021–25 continuaria 18,3%). JCP fica. LAIR e IR batem com a CVM.
(2) **WPU0662** (UNIP6): FRED = "PPI by Commodity: … Thermoplastic Resins and Plastics Materials", BLS, NSA; API v1 do BLS: 28 dos 33 meses
publicados iguais ao CSV; mai–ago/2026 eram preliminares e foram revisados (até +1,2%) — vintage do CSV, troca na coleta do 3T26.
`RECEITA_MEIO_CLORO` B → **A** (o campo); o central do UNIP6 segue B pelo Kd sintético — métricas da trava iguais (19 centrais A/B, 134 C nas
âncoras), nada a subir.
**Revisão adversarial (20/10, duas passadas):** 2 defeitos e 1 fragilidade reproduzidos, todos corrigidos antes do golden: **(1)** LPA consolidado
zerado não caía no individual (VLID3 2016–17) → cai; **(2)** a referência de ações exigia lucro > 0 (VLID3 2020 em prejuízo jogava a ref para
2021) → só ações e preço; **(3)** bonificação pequena entre o fechamento e a entrega do DFP passava pela trava com LPA reexpresso → ano fora pela
regra (b). Também: viés de classe declarado e o teste do snapshot passou a exigir os DFP 2016–19. 2ª passada: os 5 fechados, nenhum defeito novo;
2020+ idêntico (`==`). Aceito: dossiê com COTAHIST e sem os DFP 2016–19 falha alto (o bootstrap baixa os dois). Suíte: 760 passed. Nenhuma ordem de compra ou venda decorre desta mudança.

## 20/10/2026 — B26: razão do desconto de controlador pelo FRE 2026 (28 → 23 `SEM_RAZAO`)
Leitura do FRE 2026 (`dossie/fre.py`, LGPD-safe: PF anonimizada) para os 28 tickers. **Critério (decidido pelo Claude, reversível):** só vira razão o que o FRE
*prova*. Ele diz **quem** é o controlador e as partes relacionadas do ano, mas não prova que ele **não interferiu** em 15 anos (§5, regra 1); então "controlador X
com Y%" não substitui `SEM_RAZAO` (seria o marcador disfarçado). Ficam de fora também o campo "controlador" vazio contradito pela tabela de partes relacionadas
(SANB11, CSMG3, SBSP3, CPLE3: citam acionista controlador ou o Estado) e a UGPA3 (acordo de acionistas Ultra+Parth, 32,7%). **Razão escrita (5):** PRIO3 (id 161257),
KEPL3 (161068), RECV3 (161485), VBBR3 (159172), B3SA3 (161005): FRE 2026 sem acionista marcado controlador, sem acordo de acionistas, lista de acionistas não vazia
e sem parte relacionada "controlador"; sem dono que o exerça, os vetores V1-V6 não se aplicam; não cobre risco de gestão. Os outros 23 seguem "sem razão
documentada" (razão de verdade exige dossiê com D3, como LEVE3). `test_b24`: 28 → 23 e confere o id do FRE de cada uma das 5. **Palavras: nenhuma mudou**
(33 CARA, 3 JUSTA, 5 NÃO CONCLUSIVO); golden intacto (a razão é texto). Suíte 760 passed. Nenhuma ordem de compra ou venda decorre desta mudança.

## 21/10/2026 — Check-up: armadilha na exceção dos 0,80× (D2), temporada blindada (D1), backup sem `privado/`
**D2 (regra de compra, §9 "zero armadilhas"):** o relatório (`relatorio/quanti.py`) e os PDFs dos lotes 1, 3, 4 e 5 chamavam `entrada_parcial` sem
os carimbos; só o lote 6 os passava. Novo registro único `ferramentas/carimbos.py`: os casos da tabela do §7 (Sanepar SAPR11, Engie EGIE3, Mahle LEVE3,
Unipar UNIP6, Klabin KLBN11, Vibra VBBR3, Petrobras PETR4) + defeitos estruturais escritos (BRSR6 controlador; RECV3 produção em declínio com ROIC < WACC),
cada um com o lugar onde está escrito; o lote 6 mantém a lista própria de LEVE3/UNIP6. **Critério (Claude, reversível):** caso da casa do §7 entra como
está; tirar exige registrar aqui por que a armadilha acabou. **Efeito medido:** nos 9, a exceção já saía "não" por nota/palavra — a armadilha só se
soma ao motivo; **nenhuma elegibilidade, palavra, central ou golden mudou** (a exceção não entra no golden). `tests/test_carimbos.py` (inclui o
relatório real da UNIP6). **D1:** `temporada.py --gravar` não baixa mais; só grava se o sha256 do ZIP do cache = o do último boletim real do trimestre
(o boletim passa a citar o hash); 404 do arquivo do ano ainda não publicado sai 0 (adversário: 1T27 em abril daria aviso falso toda sexta);
`monitor_semanal.vbs` avisa falha da temporada e do painel da carteira (antes silenciosa), aviso 50 → 30 min (limite de 1 h da tarefa). Simulação real
2T26: 6 min 17 s, 31 publicaram, nenhuma mudança. **Backup:** `backup_dados.py` levava `dados/privado/` (carteira, desde 19/10) ao OneDrive — agora
excluída (inviolável 2). Adversário: 1 defeito (404) corrigido; mapeamento §7 → ticker e todos os chamadores conferidos. Nenhuma ordem de compra ou venda decorre desta mudança.

## 21/10/2026 (tarde) — PENDENTE #7: o "UBP R$ 1,3 bi" da EGIE3 era a venda da TAG; casos do §7 com ano e fonte (proposta, #9)
**#7 (EGIE3), lido nos ZIPs da CVM (nota A, consolidado, CD_CVM 17329):** o repo chamava de "UBP de 2024" o não recorrente limpo do ROE de longo
prazo. São dois eventos: **(1) DFP 2024, conta 3.04.04.02 "Alienação de participação societária em controlada em conjunto" = R$ 1.336,1 mi** (venda
da TAG; outras receitas operacionais) — é isso que `lote6_quimica.roe_limpo` tira (outras receitas acima da mediana, após IR de 34%); **(2) ITR 2T26,
conta 3.06.01.01 "Repactuação do UBP" = R$ 1.921,5 mi** (receita financeira, no trimestre; ≈ R$ 1,27 bi após 34% — origem provável do "R$ 1,3 bi"
da imprensa). Corrigido só o rótulo: `03-hall:33` (e a cópia do Desktop), `atualizar_hall_lote6.py:35`, `lote6_textos.py:115`,
`gerar_pdf_lote6.py:612`, docstring de `lote6_quimica.py:133`, e o carimbo EGIE3 em `carimbos.py` ("venda da TAG em 2024; repactuação do UBP no
2T26, R$ 1,92 bi bruto"). **Nenhum número, palavra, central ou golden mudou** (o cálculo já tirava a conta certa; o 2T26 não entra na janela
2017–25). Observação para a temporada 3T26: o lucro 12m da EGIE3 (R$ 3,96 bi no LTM 2T26) carrega a repactuação; o patrimônio de jun/26 também.
O §7 da doutrina ainda diz "Engie (UBP R$ 1,3 bi)" — entra na proposta do #9 abaixo.

**#9 — casos do §7 (proposta; a doutrina NÃO foi alterada, aguarda o Frank):** DFP/ITR locais (CVM, nota A); ROE = lucro do controlador ÷ PL
final; ROIC ≈ EBIT × 0,66 ÷ (PL + dívida bruta − caixa) (aproximação desta conferência, não do motor).
- Sanepar: **DFP 2025 (individual), 3.04.04.01 "Receita Precatórios – Ação Judicial IRPJ" = R$ 2.055,8 mi**, compensada em parte por 3.04.05.03
  "Provisão Passivo Regulatório" −R$ 1.541,8 mi. Carimbo vale em 2026.
- Engie: ver #7 (TAG 2024 R$ 1.336,1 mi; UBP 2T26 R$ 1.921,5 mi). Carimbo vale em 2026.
- Mahle "R$ 121 mi": **DFP 2023, 3.06 Resultado financeiro = +R$ 121,8 mi** (+ ganho de variação monetária/IAS 29 em 3.04.05.03: R$ 70,9 mi
  2023, 116,7 mi 2024, 61,4 mi 2025). "ROE 77% / ROIC 30%" não reproduz exato em nenhum ano: ROE 82,0% (2023), 70,3% (2024), 70,5% (2025);
  ROIC ≈ 37% / 39% / 33%; dívida bruta R$ 1,66 bi × PL ≈ R$ 0,86 bi em 2025. Os dois carimbos valem em 2026.
- Unipar "240% do lucro": 2025 dá **270%** (DFC 6.03.03 dividendos pagos R$ 1.319,7 mi ÷ lucro do controlador R$ 488,6 mi, DFP 2025); caixa
  R$ 2,14 bi (2023) → R$ 1,07 bi (2025) = "metade em 3 anos" confere; dívida R$ 2,06 → 3,53 bi. "ROE 20% / ROIC 7,7%": 2024 dá ROE 19,7%,
  ROIC ≈ 11,6%; 2025 ROE 26,9%, ROIC ≈ 12,3%. Os dois carimbos valem em 2026.
- Vibra "+300% a/a": **ITR 2T26 × 2T25: EBIT R$ 3.861 mi × R$ 1.023 mi (+277%)**; margem bruta 8,89% no 2T26, a maior da série trimestral
  2022–26. Carimbo de topo de ciclo vale em 2026 (é atual, não de 2023).
- Petrobras "Brent 104": EIA RBRTE (nota A) — média 2022 US$ 100,93, set/2026 US$ 114,16 (números do QA de 21/10; nesta tarde a página da EIA
  não abriu para reconferir). Margem bruta LTM 2T26 50,6% × pico 52,7% (2023). Carimbo vale em 2026.
**Proposta de texto do §7** (aplicar só com o ok do Frank): trocar os casos por "Sanepar (precatório IRPJ R$ 2,06 bi, 2025), Engie (venda da TAG
R$ 1,34 bi em 2024; UBP R$ 1,92 bi no 2T26), Mahle (resultado financeiro +R$ 122 mi em 2023; IAS 29)" / "Unipar (270% do lucro em 2025)" /
"Mahle (ROE 70%, ROIC ~33%, 2025), Unipar (ROE 27%, ROIC ~12%, 2025)" / "Vibra (EBIT +277% a/a no 2T26), Petrobras (Brent US$ 114 em set/2026,
EIA)", com "(DFP/ITR CVM)" na legenda. **Nenhum carimbo sai.** Nenhuma ordem de compra ou venda decorre desta entrada.

## 21/10/2026 (tarde, 2) — Frank: #8 = (a); #9 = "ok §7" → doutrina 2.6.1
**#8:** sem controlador nem acordo no FRE = razão válida do desconto de controlador (§5); fica como o B26 fez (PRIO3, KEPL3, RECV3, VBBR3, B3SA3).
Nada recalculado. **#9:** a proposta da entrada anterior foi aplicada ao §7 (e ao exemplo da Unipar no §6, item 5) e ao checklist `04` (Engie:
TAG 2024, UBP 2T26), nas cópias do Desktop também; doutrina 2.6 → **2.6.1** (só exemplos; nenhuma regra, carimbo, palavra, central ou golden
mudou); versão anterior em `_historico/2026-10-21 doutrina v2.6/`. Nenhuma ordem de compra ou venda decorre desta entrada.

## 22/10/2026 — N7: motor recusa dado inválido (nenhuma palavra, central ou golden mudou)
`motor_financeiras`: `palavra` e `nota_preco` recusam P/C NaN, None, 0 e negativo (+inf segue válido: central ≤ 0 → NÃO CONCLUSIVO);
`precos_de_referencia` devolve sem preço para central NaN/±inf/None; `entrada_parcial` devolve `(False, ["dado inválido…"])` para NaN/None/inf em
pc, dispersão, central ou notas; `descontar` exige desconto em [0, 1]; `media_qualitativa` exige notas em 0–5. `motor_nao_financeiras`:
`central_de` recusa âncora NaN/inf/vazia; `qualifica_saida` recusa mais anos acima do que a série tem. `carimbos.de` e `relatorio.caso` aceitam
ticker com espaço/minúscula. Teste novo `tests/test_n7_dado_invalido.py`; no `test_aud88` saiu o caso `pc = 0 → BARATA` (preço 0 não é dado).
Golden intacto; 867 passed, 42 skipped. Nenhuma ordem de compra ou venda decorre desta entrada.

## 22/10/2026 — N2: testes das regras sem cobertura (só testes; motor, palavra e golden intactos)
`tests/test_n2_regras_sem_cobertura.py`: desconto de controlador por cenários (Σ prob × perda; só âncora > 0), cada degrau da escala da nota de
Preço (e saturação), saída a 1,30× em financeira (nunca 1,50×, §9) e DCF reverso `g_implicito` com ida e volta preço → g → preço (SUZB3, KEPL3,
PETR4, esta com cenários). Nenhum defeito achado. Suíte 894 passed, 42 skipped. Nenhuma ordem de compra ou venda decorre desta entrada.

## 22/10/2026 — N9: servidor exclusivo e guardas do front da tela (nenhuma palavra, central ou golden mudou)
`painel/servir.py`: bind exclusivo (`SO_EXCLUSIVEADDRUSE` no Windows, sem `SO_REUSEADDR`); o 2º `painel` na mesma porta sai com "Porta N em uso". `web/app.js`: contrato sem `versao`
→ faixa de erro (não mais "versão undefined"); `hall.json` sem `fatores`/`escala_regua`/`empresas` → faixa "está incompleto" (não mais TypeError e tela vazia); hash desconhecido →
"Página não encontrada" (não cai calado no Hall; a rota Sistema entra na lista quando a N4 existir). Testes: dois servidores na mesma porta (Linux) e guardas estáticos do front. Conferência no
navegador (Windows, 2 servidores; hall.json truncado) fica para o Frank — a nuvem não tem navegador de teste.

## 22/10/2026 — N10: CLIs sem traceback e vírgula decimal nas notas do dossiê (nenhuma palavra, central ou golden mudou)
`temporada.py --trimestre/--simular` com rótulo inválido (5T26, 4T26, 9T99) e `triagem/rodar.py --data` inexistente (2026-13-40) saem com rc 2 e mensagem de uso, antes de qualquer
download ou gravação (`type=` do argparse). O ponto decimal do texto da ALLD3 ("18.2%", "(0.1048)") vinha de `dossie/notas.py` (componentes das notas, `f"{x:.4f}"`):
20 pontos passaram a `_br()` (vírgula). Só o texto; as notas e a palavra não mudam. Os `dossie/vereditos/*.json` já gravados mantêm o texto antigo até a próxima geração com `--data`
nova (não regerados: sobrescreveria o veredito vigente). Testes: `tests/test_n10_clis_argumento_invalido.py`. Suíte 909 passed, 42 skipped.

## 22/10/2026 — N11: cadastro do relatório (nenhuma palavra, central ou golden mudou)
`relatorio/quali.py` `CADASTRO` passou de 1 para 6 tickers: CNPJ de EGIE3, PETR4, TAEE11, ITUB4 e SAPR11 (`triagem_2026-10-02.csv`) abre o FRE (governança, remuneração) no relatório;
pregão só da PETR4 (já usado no hall). Os pregões de EGIE3, TAEE11, ITUB4 e SAPR11 ficam `None`: a API da B3 responde 403 na nuvem e nome de pregão não se chuta (decisão: sem
dado conferido, o bloco de proventos avisa em vez de inventar). N8: nº de ações em mil não chega ao valor (ver `docs/QA-2026-10-21.md`). Suíte 930 passed, 42 skipped.

## 22/10/2026 — N3: contrato da tela liga o que o motor já calcula (nenhuma palavra, central ou golden mudou)
`relatorio.modelo.Origem` ganha `data` (AAAA-MM-DD, "" = não sabe) e `Numero` ganha `baixo`/`alto`; `quanti.secao_preco` preenche a faixa do DCF com os cenários pessimista e otimista do motor
(com o desconto de controlador, só em valor > 0 — igual ao valor da âncora); `calendario_secao` ganha as colunas Dividendos e JCP (líquidos); `painel/contrato.py` lê `setor` da triagem,
`data` de cada fonte e os pares baixo/alto e dividendos/jcp. Front: setor na linha do Hall, data na lista de fontes, barra do calendário empilhada dividendo × JCP (Ocultar mantém uma barra só).
Probabilidade/impacto de risco, tipo/efeito de premissa, yield projetado e concentração por setor da carteira seguem sem fonte. Conferência visual no navegador fica para o Frank (dia). Suíte 937 passed, 42 skipped.

## 22/10/2026 — N4: tela Sistema (nenhuma palavra, central ou golden mudou)
`painel/sistema.py` grava `web/dados/contrato/sistema.json` (chamado por `contrato.gerar`): idade de COTAHIST (último pregão do hall), CVM (`MANIFESTO.json`), proventos da B3 (o arquivo mais antigo de
`dados/proventos_hall/`), monitor (última rodada do `historico.csv`) e temporada (último `BOLETINS/*-temporada.md`); último boletim do monitor e da temporada; data (`golden_log.md`) e motivo (`golden.json`) do
golden; e a última suíte — registro novo: `conftest.pytest_sessionfinish` grava `dados/suite_ultima.json` (ignorado pelo git; só suíte completa, ≥ 400 testes, sem caminho/`-k`/`-m`; leva os argumentos usados).
Ausente = `null` + "sem registro". Front: rota `#/sistema` (`telas/sistema.js`), menu sem o "em breve". Conferência visual no navegador fica para o Frank (dia). Suíte 949 passed, 42 skipped.
Achado: `tests/test_b23_petr4_premissas.py` e `tests/test_carimbos.py` não coletam na nuvem (fonte `C:/Windows/Fonts/arial.ttf` nos `gerar_pdf_lote*`) — vai ao BACKLOG.

## 22/10/2026 — N5: contraste dos tokens da tela (nenhuma cor, palavra ou golden mudou)
`painel/tests/test_contraste_tokens.py` calcula a razão WCAG dos pares de `web/tokens.css` nos temas claro e escuro: todo texto (`--ink`…`--nc-fg` sobre `--bg/--sf/--sf2` e sobre o fundo do próprio chip)
passa de 4,5:1 (o menor é `--ink3` sobre `--sf2` no claro, 5,09) e as séries do gráfico de 3:1. Contornos abaixo de 3:1 (`--ln2` e os `*-ln` dos chips): lista fixada no teste e em `PENDENTE-FRANK.md` #10 —
trocar cor é decisão visual do Frank. Nenhuma ordem de compra ou venda decorre desta entrada.

## 22/10/2026 — Q01: PDFs dos lotes importáveis fora do Windows (nenhuma palavra, central ou golden mudou)
`gerar_pdf_lote1.py` registrava `C:/Windows/Fonts/arial*.ttf` ao importar, e por isso `test_b23_petr4_premissas` e `test_carimbos` não coletavam na nuvem. Agora usa a Arial do Windows se existir e,
senão, a Liberation Sans (métricas idênticas) — só para o módulo importar; PDF gerado fora do Windows não é o vigente. Suíte inteira sem `--ignore`: 963 passed, 42 skipped.
