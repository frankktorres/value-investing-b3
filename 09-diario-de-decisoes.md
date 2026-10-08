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

