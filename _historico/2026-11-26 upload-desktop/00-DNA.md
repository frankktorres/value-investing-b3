# 00 — DNA da Mesa de Value Investing B3
*Versão 1 · 25/11/2026 · todo chat lê este arquivo primeiro. Muda só com decisão do Frank registrada no `09`.*

Uso próprio, não comercial. Nada aqui é ordem de compra ou venda.

## 1. Visão
Dado **qualquer** ticker da B3, o sistema entrega, atualizado na hora (preço do último pregão + último trimestre
publicado, **com a data de cada número**):

1. **Fatos:** 10 anos de DRE, balanço, DFC e proventos (CVM e B3); ciclo (meio de ciclo, pico, vale); qualidade
   (ROIC × WACC, Piotroski, Altman, Beneish, accruals).
2. **Catálogo de métodos value**, cada um com fonte original nota A/B, fórmula, insumos, **domínio de validade**
   (quando vale; fora dele, "não se aplica", com a razão) e **papel**: *valor*, *qualidade*, *ranking* ou *qualitativo*.
   Piotroski e Greenblatt não dão valor. **O veredito usa só os métodos válidos para aquela empresa.**
3. **Renda fixa líquida de IR** no mesmo horizonte: NTN-B/Tesouro IPCA+, Tesouro Selic/CDI, LCI/LCA, com as alíquotas
   vigentes de dividendos e JCP.
4. **5 pares do setor**, escolhidos por regra escrita (nunca à mão).
5. **Fatos relevantes da CVM (IPE)** como alertas. Alerta nunca muda número em silêncio.
6. **Parecer:** palavra (BARATA/RADAR/JUSTA/CARA/NÃO CONCLUSIVO) + confiança + motivos, explicado ponto a ponto.
   **Regra do veredito (alvo):** a palavra compara o **retorno real implícito da ação, líquido de IR**, com a **renda
   fixa líquida do mesmo horizonte (NTN-B/Tesouro IPCA+) mais o prêmio exigido**. BARATA só se superar com folga; **se
   não supera a renda fixa, nunca é BARATA.**

### 1.1 Regra do veredito — fórmula
Horizonte H = 10 anos, preço P do último pregão, tudo em termos reais (π = inflação implícita da curva, `01` §4).

- **Retorno real implícito líquido da ação (r):** a taxa que iguala o preço aos fluxos do cenário central, já líquidos
  de IR do investidor pessoa física:
  P = Σₜ₌₁..H [ Divₜ × (1 − t_div) + JCPₜ × (1 − t_jcp) ] ÷ (1 + r)ᵗ + [ V_H − 0,15 × (V_H − P ÷ (1 + π)ᴴ) ] ÷ (1 + r)ᴴ,
  com fluxos em R$ de hoje e V_H = valor no fim do horizonte, em R$ de hoje, pelo mesmo método válido. O IR do ganho de
  capital (15%, só na venda, `01` §4.1) incide sobre o ganho **nominal** V_H × (1 + π)ᴴ − P; trazido a R$ de hoje, é
  0,15 × (V_H − P ÷ (1 + π)ᴴ). Usar (V_H − P) subestimaria o imposto e inflaria r. Hoje: t_div = 0 até R$ 50 mil/mês por
  empresa e 10% acima (Lei 15.270/2025); t_jcp = 17,5% (LC 224/2025) — os dois com pontos em aberto no `01` §4.1, a
  fechar na fonte A. **Em aberto:** a isenção de vendas de ações até R$ 20 mil/mês (Receita Federal, fonte A a conferir)
  **não é usada** até ser conferida; o cálculo tributa todo ganho.
- **Renda fixa real líquida (RF):** RF = { [ (1 + n)ᴴ − 1 ] × 0,85 + 1 }^(1/H) ÷ (1 + π) − 1, com n = (1 + rf) × (1 + π)
  − 1 e rf = **Tesouro IPCA+ sem cupom com vencimento mais próximo de H (10 anos)**, taxa de compra da manhã do dia do
  preço. Não o mais longo: ele mistura risco de marcação a mercado e outro horizonte. π da curva no mesmo prazo. (IR
  regressivo, 15% acima de 720 dias, só no resgate — Receita Federal, tabela 2026, nota A conferida em 04/10/2026.) O
  `01` §4 usa hoje o vencimento mais longo para a rf do Ke; a troca entra na mesma mudança de doutrina abaixo.
- **Prêmio exigido (p):** o prêmio do Ke da casa (`01` §4: 5 p.p., × Hamada nas não financeiras), sujeito à causa (a).
- **Palavra:** r < RF → **nunca BARATA** (CARA ou NÃO CONCLUSIVO); r ≈ RF + p → JUSTA; **BARATA só se r ≥ RF + p + f**,
  com a folga f fixada no pré-registro antes de rodar (proposta: f = 3 p.p., o "vence a RF: sim" do `01` §4).
- **Fonte do conceito:** retorno implícito comparado ao título sem risco — Damodaran, *Investment Valuation* (prêmio
  implícito; nota B quando a página for aberta) e Graham, *The Intelligent Investor* (rendimento da ação × do título; a
  abrir). A tributação vem da Receita Federal (nota A).
- **Estado:** a régua de hoje é P/C (`01` §9). Trocar por esta é **mudança de doutrina**: pré-registro → teste → oráculo
  → `09`, dentro dos marcos M1/M3. Até lá vale o §9.

### 1.2 Catálogo (estado em 25/11/2026)
"Fonte a abrir" é ponteiro, não prova: só vira A/B quando o texto primário for lido (`~/.claude/PESQUISA.md`).
O domínio abaixo é a condição **do próprio modelo**; o texto final sai da fonte, não do resultado da B36.

| Método | Papel | Fonte a abrir (nota hoje) | Domínio (condição do modelo) | Hoje no código |
|---|---|---|---|---|
| Graham original / Graham-BR | valor (informativo) | Graham, *The Intelligent Investor* (—) | LPA normalizado > 0, VPA > 0, não financeira | quadro `01` §11.1 |
| Graham revisado-BR | valor (informativo) | Graham, 1974 (—) | idem + g real declarado | quadro |
| 7 critérios do defensivo | qualidade (placar) | *The Intelligent Investor* (—) | empresa grande, histórico longo | quadro |
| Bazin / teto de renda | renda (teto, não valor) | Bazin, *Faça Fortuna com Ações* (—) | provento coberto por caixa | informativo |
| Barsi | renda/qualidade | texto primário não localizado (C) | a definir | **não existe** |
| Lynch / PEG / PEGY | ranking (não valor) | Lynch, *One Up on Wall Street*, 1989 (—) | stalwart ou crescimento rápido, g > 0 | quadro |
| DDM / Gordon | valor | Gordon, 1959 (—) | **paga provento** com payout estável; g < Ke | âncora fin./regulado |
| P/VP justificado | valor | derivado do Gordon (—) | ROE normalizado estável; banco, seguradora, regulado | âncora |
| DCF 3 cenários + reverso | valor | Damodaran, *Investment Valuation*, 2002 (B) | FCFF de meio de ciclo > 0; g só com ROIC > WACC | âncora industrial |
| EPV + reprodução | valor | Greenwald et al., 2001 (C) | lucro operacional normalizado > 0 | âncora ind./cíclica |
| Owner earnings | valor | Buffett, carta de 1986 (—) | capex de manutenção estimável; OE > 0 | âncora industrial |
| NCAV (net-net) | valor (piso) | Graham, *Security Analysis* (—) | não financeira; ativo circulante relevante | **só na triagem** |
| SOTP | valor | — | holding com participações avaliáveis | só ITSA4 |
| TIR regulada | valor/teste | — | fluxo contratual/regulado | regulados |
| Bogle | retorno esperado (coerência) | Bogle (—) | LPA normalizado > 0 | trava `01` §9 |
| Lucro normalizado (Klarman) | insumo, não valor | Klarman, *Margin of Safety*, 1991 (—) | janela de ciclo | insumo |
| Greenblatt | ranking (não valor) | *The Little Book That Beats the Market*, 2005 (—) | não financeira, EBIT > 0 | ranking do hall |
| Piotroski F | qualidade (não valor) | Piotroski, *JAR* 38, 2000 (—) | não financeira, 2 exercícios | exibido |
| Altman Z'', Beneish M, Sloan | qualidade/alerta | 1995, 1999, 1996 (—) | não financeira | exibido |
| R$ 1 retido | qualidade da gestão | Buffett (—) | ≥ 5 exercícios | quadro |
| **Lentes qualitativas:** fosso competitivo (Buffett/Munger), ciclo e risco (Howard Marks), 15 pontos (Fisher) | **qualitativo, não valor** | cartas de Buffett; Marks, *The Most Important Thing*, 2011; Fisher, *Common Stocks and Uncommon Profits*, 1958 (todas a abrir; Fisher hoje C) | toda empresa, com evidência A/B por item | notas 0–5 arbitradas ou do dossiê; Fisher quase todo vazio na B36 |

**Lentes qualitativas aparecem no parecer como motivos e alertas, nunca como número.** Não entram no valor central,
não sobem nem descem palavra por nota; item sem evidência A/B fica "não avaliado".

## 2. Princípios (valem acima de qualquer regra da doutrina)
1. **Zero erro silencioso.** Todo número sai com fonte, data e conta conferível. Erro explícito é aceitável; número
   errado sem aviso, nunca.
2. **Dado ausente = "não avaliado".** Nunca zero, nunca o padrão do método sem aviso. O que não foi avaliado aparece no
   parecer e diz o que deixou de pesar.
3. **Regra genérica, nunca exceção por ticker.** Se uma empresa precisa de regra própria, a regra está errada ou o caso
   está fora do domínio do método ("não se aplica").
4. **Método escolhido pela fonte, antes de ver o resultado.** Fórmula, domínio e limiar vêm do texto primário A/B e
   entram no pré-registro antes de rodar (`docs/PRE-REGISTRO-v3.md` §0). Contagem de BARATA nunca é critério.
5. **Todo conserto provado fora da amostra.** Conserto se desenvolve no conjunto de desenvolvimento (hall + dossiês +
   as 20 da B36, e os anos 2016–2020) e só vale quando passa em hold-out que ninguém viu (§5, M1). Um hold-out vale
   **uma vez**.

## 3. Onde estamos (25/11/2026)
**O que a B36 provou** (`docs/holdout/B36-2026-11.md`): o motor v2.7, congelado, **não generaliza**. Em 20 ações fora
do hall escolhidas por liquidez: rodam 14 (limite ≥ 16); NÃO CONCLUSIVO 9 de 14 (≤ 6); Ke nominal > 30% em 3 (≤ 2);
valor absurdo em 6 (≤ 2); vazios medianos 75% (≤ 50%); só o tempo passou (2,6 min ≤ 20). 0 BARATA, P/C mediano 3,26
contra 1,82 do hall, dispersão > 1,8× em 10 de 14 (6 infinitas), 43% dos insumos saem de código.
Leitura: a Mesa funciona nas 41 que foram ajustadas à mão; fora delas, para em evento societário, publica valor
absurdo ou fica sem palavra.

| Visão | Hoje | Falta |
|---|---|---|
| Qualquer ticker | 41 do hall + 6 dossiês + executor da B36; triagem de toda a B3 só com proxy | rodar sem ajuste por ticker (M1, M2) |
| Atualizado na hora | preço e LTM por rodada (`temporada.py`), data-base fixa; VPA/LPA das financeiras digitados do 2T26 (B32) | coleta por pedido; nenhuma data digitada |
| 10 anos de DRE/BP/DFC/proventos | séries da CVM automáticas (16/16 na B36); proventos da B3 param em evento (B40–B43); financeiras via StatusInvest (C) | eventos societários; financeiras pela CVM |
| Fonte e data por número | procedência por campo (`insumos_a`); `Origem.data` preenchida em 27 de 466 (N12) | data em 100% dos números |
| Catálogo com domínio | âncoras por **perfil** (`01` §11.2), não por condição da empresa; várias fontes nota C/—; sem Barsi; NCAV só na triagem | domínio por método; fontes A/B |
| Veredito contra a renda fixa | régua por P/C (`01` §9); "vence a RF?" só exibido | regra do §1.1 pré-registrada e implantada |
| Renda fixa líquida | só Tesouro IPCA+ (rf); JCP 17,5% e dividendo 10% > R$ 50 mil com pontos em aberto (`01` §4.1) | Selic/CDI, LCI/LCA; alíquotas fechadas na fonte A |
| 5 pares | não há regra (pares à mão em `lote4`) | regra escrita + código |
| Fatos relevantes (IPE) | títulos baixados e lidos à mão na B36 | alerta automático, sem mexer em número |
| Parecer explicado | palavra + régua + carimbos; `relatorio <TK>` (MD/PDF) só para hall/dossiês | qualquer ticker; confiança, motivos e "não avaliado" explícitos |
| Point-in-time | corte pelo prazo legal do ITR (45 dias), não pela entrega real (DT_RECEB); backtest parado (proxy 70,7%) | corte por DT_RECEB e premissas derivadas do dado |
| Tela | `painel` (127.0.0.1): Hall, Empresa, Carteira, Monitor, Sistema; só lê | qualquer ticker |
| Dado ausente | protocolo da B36 grava vazio = padrão do método (fere o princípio 2); H10 (zero silencioso) — estado a conferir | "não avaliado" em todo o fluxo |

## 4. As 4 causas da B36, em ordem
Cada causa: hipótese pré-registrada antes de rodar → conserto no conjunto de desenvolvimento → camadas 1–5 verdes →
oráculo. **Nenhuma é provada nas 20 da B36** (contaminadas); a prova é o M1.

| # | Causa | Itens | O que fecha | Por que nesta ordem |
|---|---|---|---|---|
| a | **Nível do Ke** | B39 (Ke da Mesa × Ke implícito, X = 3 p.p., já pré-registrada), B46 (Ke > 30%), B35 (Kd que reage à alavancagem), B14 | o Ke mede o risco que o mercado cobra, ou fica como está com motivo; fixa o prêmio p do §1.1 | move todo P/C; mexer em âncora antes seria trabalhar sobre um Ke que pode mudar |
| b | **Domínio de validade por método** | B45 (central ≤ 0, P/C absurdo), B47 (dispersão com âncora ≤ 0), parte "DDM de quem não distribui" da B44 | cada método devolve **valor**, **não se aplica (razão)** ou **não avaliado (dado)**; central = mediana das válidas; dispersão só entre válidas | sem isso o valor absurdo vira palavra (ENEV3 CARA com P/C 39,95) |
| c | **Eventos societários** | B40 (cisão com redução de capital), B41 (incorporação), B42 (capital fora do FRE), B43 (provento repetido, unit) | regra genérica com fonte A por tipo de evento; o que não tiver semântica conferida para **explícito** (não chuta) | 6 de 20 param aqui; é dado, não calibração — pode correr em paralelo a (a) e (b) sem gastar tentativa do pré-registro |
| d | **Redesenho dos insumos manuais** | B44 (payout = mediana medida; piso estatutário não é política), B48 (teto imposto pelo orquestrador, tag along, Fisher, `discricionario`, quali das financeiras), B32 (digitados das financeiras, prazo 31/01/2027) | insumo é automático ou "não avaliado"; leitura humana só onde muda a palavra, com fonte A/B; lentes qualitativas só como motivo | depende de (b): o domínio diz quais insumos importam para cada método |

Fora das causas: **B37** (trava pre-push no `master`) é pré-requisito do princípio 1 — fazer quando o Frank pedir;
**B38** (conferência da B36 em 19/11/2027) segue como validação no tempo; manutenção do hall (B01–B03, B33) corre à parte.

## 5. Marcos até a visão
Um marco só fecha com o critério cumprido e medido por código. Números marcados "proposta" são fixados pelo Frank na
emenda do pré-registro, **antes** de rodar.

**M1 — Motor generaliza.** Só roda depois de (a)–(d) fechadas no conjunto de desenvolvimento. **Duas provas, as duas
obrigatórias:**

*Prova 1 — HOLD-OUT 2 (ações novas).*
- **Escolha:** `holdout_b36/selecionar.py` com data-base nova T2, mesma regra (liquidez de 250 pregões, ≥ 10 DFPs, um
  papel por CNPJ, exclusões mecânicas) e exclusão ampliada: hall, dossiês, fila do `06`, triagem manual, **as 20 da B36** e
  todo ticker tocado durante os consertos (registro append-only de tickers tocados). Lista e critério em commit próprio
  antes de rodar.
- **Recurso escasso:** em 19/11 eram 62 elegíveis; sem as 20 da B36 sobram ~42. Cada hold-out gasta 20 → cabem ~2 nessas
  regras. Por isso o HOLD-OUT 2 não roda antes de as 4 causas fecharem.
- **Critério (proposta):** rodam sem erro ≥ 18/20 ("não avaliado" com razão conta como rodou); NÃO CONCLUSIVO ≤ 6 das que
  rodam; Ke nominal > 30% ≤ 1; central ≤ 0 publicado como valor = 0 e P/C fora de [0,2; 5] ≤ 1; insumos automáticos,
  mediana ≥ 80%; vazio silencioso = 0; tempo mediano ≤ 20 min incluindo a orquestração. Relatados, não critério: nº de
  BARATA, P/C mediano, dispersão.

*Prova 2 — hold-out no tempo (point-in-time, sem gastar tickers).*
- **Corte:** cada data-base só enxerga o documento já **entregue** à CVM naquela data (`DT_RECEB` dos dados abertos), o
  preço do COTAHIST até a data e a macro como publicada até a data; premissa só derivada do dado PIT por regra escrita
  (`PRE-REGISTRO-v3` §4.3a). Nenhuma premissa digitada em 2026.
- **Desenvolver em 2016–2020, julgar uma vez em 2021–2025.** Regras, domínios e limiares se ajustam só com as
  data-bases de 2016–2020; o período 2021–2025 roda uma vez, com o método congelado em commit próprio antes.
- **Contaminação declarada:** os números de 2021–2025 das 41 do hall já foram vistos (o golden usa 2016–2025). A prova 2
  vale como teste do **método congelado**, não como período virgem; isso fica escrito na emenda.
- **Critério (proposta):** sentinela PIT verde (zero dado com `DT_RECEB` posterior à data-base); em cada data-base de
  2021–2025, as mesmas linhas de erro, NÃO CONCLUSIVO, Ke > 30% e valor absurdo da prova 1; discriminação do
  `PRE-REGISTRO-v3` §4.3c (BARATA nem 0 em todas as datas, nem > 50% numa data fora de crise); postos de P/C × retorno
  total excedente com IC de Spearman relatado (§4.4), deflacionado pelas tentativas.

**M2 — Ticker → relatório automático.** `relatorio <TK>` para qualquer ticker do universo da triagem, sem digitação.
Aceite (proposta): em 10 tickers sorteados por regra (seed fixa, fora dos hold-outs): 100% dos números com fonte e data
(teste por código); 10 anos de DRE/BP/DFC/proventos ou "janela curta" declarada; cada método do catálogo com valor, "não se
aplica" ou "não avaliado"; lentes qualitativas só como motivo/alerta; preço do último pregão e último ITR publicado;
≤ 5 min da chamada ao PDF; catraca de digitados do fluxo = 0.

**M3 — Renda fixa, pares e veredito contra a RF.** Tabela líquida de IR (IPCA+, Selic/CDI, LCI/LCA) com taxa do dia,
fonte A e alíquota vigente conferida; 3 casos refeitos à mão batem ao centavo; regra do §1.1 implantada (r, RF, p, f
exibidos no parecer; teste: r < RF nunca sai BARATA). Pares: regra escrita (setor da CVM + porte), 5 por ticker,
determinística (mesma entrada → mesmos pares, teste).

**M4 — Notícias.** IPE coletado todo dia útil; fato relevante novo de ticker acompanhado vira alerta no relatório/tela em
≤ 1 dia útil; teste prova que ingerir IPE não muda nenhum número (golden igual); evento societário do IPE vira pendência
da causa (c).

**M5 — Tela.** `painel` abre qualquer ticker a partir do relatório do M2; a tela não calcula; conferido no navegador
(Playwright).

## 6. Como usar este arquivo
- Antes de propor tarefa: em que marco e causa ela entra? Se em nenhum, explicar por que vale a pena agora.
- Mudança de motor, doutrina, golden ou premissa: pré-registro → teste → oráculo → registro no `09` (CLAUDE.md).
- Este arquivo muda só por decisão do Frank; versão anterior vai para `_historico/`.
