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
