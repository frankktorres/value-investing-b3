# PLANO DE MELHORIAS — Mesa de Value Investing B3
*Versão 1 · 05/10/2026 · escrito ao fim do recálculo dos 6 lotes (doutrina v2.1). Carta branca do Frank para mudar o diretório, desde que embasado
em value investing. Pergunta-guia de cada item: **o que Buffett e Munger fariam?***

---

## 0. Diagnóstico honesto (por que existe este plano)

O sistema hoje faz bem **a metade quantitativa** do value investing: lucro normalizado, EPV × reprodução, ROIC × WACC, Owner Earnings, margem de
segurança e comparação líquida com o Tesouro — tudo reproduzível em `ferramentas/` e revisado por adversário. A outra metade falta ou é fraca.

| # | Deficiência | Evidência concreta | Gravidade |
|---|---|---|---|
| D1 | **Universo errado**: só 41 blue chips, as mais cobertas e eficientes da B3 | 35 das 36 do hall dão JUSTA/CARA; só SMTO3 é RADAR; zero BARATA | Alta — o sistema só sabe dizer "não compre" |
| D2 | **Sem "por que o mercado erra"** (filtro 5 da doutrina) | Nenhuma ficha responde; o veredito é só aritmética de preço | Alta |
| D3 | **Qualitativo raso**: moat, gestão e controlador são notas 0–5 dadas pelo analista, sem evidência | `QUAL(...)` em cada `loteN_*.py` | Alta |
| D4 | **Olhar só para trás**: margem = mediana do passado; consenso "não encontrado" em 41 de 41 | Fichas, linha "Lucro projetado" | Média |
| D5 | **Regra sem validação empírica**: nunca testamos se a régua (Ke = rf + 5 p.p. e compra a 0,70×) teria comprado algo bom em 2016–25 | Não existe backtest | Alta |
| D6 | **Sem construção de carteira**: a doutrina não diz tamanho de posição, concentração, caixa, nem registra a carteira real | `07` não tem posições; doutrina não tem §12 | Alta |
| D7 | **Regra de venda única para tudo** (1,30× o central), igual para Unipar e WEG | doutrina §9 | Média — Buffett/Fisher quase nunca vendem negócio excepcional por preço |
| D8 | **Texto × código divergem** | Doutrina §11.1 diz "demais: média de 5 anos"; o motor usa mediana de 10 | Média |
| D9 | **Viés de inflação no capex de manutenção** | Greenwald usa Δreceita nominal: a inflação vira "crescimento" e reduz o capex de manutenção | Média |
| D10 | **ROIC contábil em economia inflacionária** | Capital a custo histórico infla o ROIC (WEG, ABEV, HYPE) contra um WACC corrente | Média |
| D11 | **Correções que ficaram só num lote** | Defasagem do provento a VP só no Lote 4; cobertura de juros pela despesa bruta em todos | Baixa-média |
| D12 | **Preço parado**: centrais a preço de 02/10, sem rotina de atualização | Hall com nota "atualizar antes de decidir" | Média |
| D13 | **Versionamento por cópia** (`_historico/`), sem git e sem teste automático | Regressão dos lotes conferida à mão nesta sessão | Média |
| D14 | **Comitê único**: o adversário é a mesma família de modelo; o Desktop (2º comitê) está pausado | memória do projeto | Média |
| D15 | **Diário de decisões inexistente**: não há registro de tese, data, preço e "o que me provaria errado" | — | Alta — sem ele não há aprendizado (Munger) |
| D16 | **Vantagem do próprio investidor ignorada**: Frank é farmacêutico e pesquisador | Saúde/farma tratado como qualquer setor | Média — é o círculo de competência mais forte dele |

---

## 1. A ótica: o que Buffett e Munger fariam (princípios que o plano aplica)

*Paráfrases de princípios públicos (cartas da Berkshire, reuniões anuais, "Poor Charlie's Almanack"). Conferir citação literal com o
`verificador-fonte` antes de pôr em documento.*

1. **Círculo de competência** — saber onde termina o que se entende; ficar dentro. → D16, D3.
2. **Ações são pedaços de negócios** — a pergunta é o caixa que o negócio gera por décadas, não o múltiplo. → D3, D4.
3. **Margem de segurança e Sr. Mercado** — o preço é oferta do mercado, não informação sobre valor. → D12 (monitor), D2.
4. **Custo de oportunidade como régua** (Munger): toda compra compete com a melhor alternativa disponível — o Tesouro e a melhor ação já
   na carteira. → já existe (RF líquida); falta a 2ª comparação (D6).
5. **Inversão** — "diga-me onde vou morrer e não irei lá": antes de comprar, escrever como se perde 50%. → D2, D3, D15.
6. **Fosso durável** com prova: ROIC acima do custo **por muitos anos**, não uma nota. → D3, D10.
7. **Gestão honesta e boa alocadora de capital** — o teste do R$ 1 retido, recompra abaixo do valor, aquisição que rende. → D3.
8. **Concentração com convicção** (Buffett) × **diversificação contra ignorância** — tamanho da posição proporcional à margem e à certeza. → D6.
9. **Raramente vender um negócio excepcional** (Buffett/Fisher); vender o medíocre quando o preço passa do valor. → D7.
10. **Checklists e o "latticework" de modelos mentais**; lista de vieses (incentivo, prova social, compromisso, ancoragem). → D15, `04`.
11. **Aprender com os erros publicamente** (relatórios de Buffett admitem os erros). → D15, revisão trimestral.
12. **Não fazer nada é uma posição** — caixa no Tesouro enquanto não houver barganha. → já é a regra; formalizar em §12.

---

## 2. Frentes de trabalho

Cada frente: **objetivo · o que fazer (técnico) · pronto quando · modelo/effort**. A ordem de execução está na seção 3.

### F1 — Fundação: git, testes e regressão automática (D13, D11)
**Objetivo:** nenhuma mudança de método pode alterar um central sem que se saiba qual e por quê.
- `git init` local no diretório (sem remoto; `.gitignore` para `ferramentas/dados/cvm/*.zip`, `dados/raw/`, PDFs grandes opcionais). Os
  Invioláveis 1 e 4 seguem: nada de segredo; `_historico/` continua até o git ter um mês de uso.
- `ferramentas/tests/test_regressao.py` (pytest): para cada ticker do hall, central, P/C, palavra e âncoras gravados em
  `tests/golden.json`; o teste falha se algo mudar mais de R$ 0,01 sem o golden ser regenerado de propósito
  (`python -m tests.regerar_golden --motivo "..."`, que grava o motivo no log).
- `ferramentas/rodar_tudo.py`: roda os 6 lotes, compara com o golden e imprime "o que mudou e por quê".
- Propagar já: defasagem do provento a valor presente nos Lotes 1, 2, 3, 5, 6 (campo `defasagem_meses` do motor; a Financeira ainda não tem);
  cobertura de juros por **juros pagos** (DFC) em vez da despesa financeira bruta.
- **Pronto quando:** `pytest` verde; `rodar_tudo.py` reproduz o hall de 05/10 (exceto as mudanças declaradas) e o diff fica no registro do `03`.
- **Modelo:** Sonnet medium (mecânico com testes); a decisão de quais métricas propagar já está tomada.

### F2 — Coerência do método (D8, D9, D10, D7)
**Objetivo:** texto da doutrina = código; vieses de inflação fora.
- **D8:** decidir uma regra só para não cíclicas. Proposta: **mediana de 10 anos com teste de quebra estrutural** (se a mediana dos últimos 5
  anos difere > 25% da de 10 por mudança documentada — aquisição, IFRS 16, lei —, usa-se a janela pós-quebra, declarada). Atualizar §11.1 e o motor.
- **D9:** Greenwald com **Δreceita real** (receita deflacionada pelo IPCA) e capital também em reais de hoje.
- **D10:** ROIC com **capital a custo de reposição aproximado** (imobilizado corrigido pelo IPCA pela idade média = bruto ÷ depreciação anual),
  exibido ao lado do contábil; filtro 1 decide pelo menor dos dois (conservador).
- **D7 (proposta, decisão de doutrina):** regra de venda por **qualidade**: negócio com ROIC > WACC em ≥ 8 de 10 anos e nota de qualidade ≥ 8
  vende só acima de **1,50×** o central ou com tese quebrada; os demais seguem 1,30×. Base: Buffett/Fisher (vender o excepcional custa imposto
  e o reinvestimento a taxa pior). **Pedir o "ok" do Frank** — é preferência dele sobre a própria doutrina.
- Rodar tudo de novo (F1 mostra o diff) e emitir os PDFs com a nova revisão.
- **Pronto quando:** doutrina v2.2 publicada com histórico; golden regenerado com motivo; nenhum texto da doutrina contradiz o motor (o
  agente `auditor` confere).
- **Modelo:** Opus high, **plan mode** (desenho de regra).

### F3 — Validação empírica: backtest point-in-time (D5)
**Objetivo:** saber se a régua funciona antes de confiar nela com dinheiro.
- Dados: DFP/ITR da CVM desde 2011 (já é a fonte) + **COTAHIST da B3** (série histórica oficial de cotações, fonte A, arquivo anual gratuito em
  b3.com.br) — preço de fechamento ajustado por proventos e eventos.
- Para cada 30/06 e 31/12 de 2014 a 2025: recalcular o central de cada empresa **só com o que se sabia na data** (balanços já publicados;
  Ke com a rf daquela data — Tesouro Transparente tem a série). Sem olhar o futuro.
- Medir: quantas vezes a régua deu BARATA; retorno de 1, 3 e 5 anos das BARATA × RADAR × JUSTA × CARA × Ibovespa × Tesouro IPCA+;
  taxa de acerto das saídas a 1,30×. Sensibilidade: prêmio do Ke de 3, 4, 5 e 6 p.p.; compra a 0,60/0,70/0,80×.
- **Resultado esperado de decisão:** manter, recalibrar ou trocar o prêmio de 5 p.p. e a margem de 30% — com número, não com opinião.
  Cuidado com o viés de sobrevivência (incluir empresas que deixaram de existir: o cadastro da CVM tem as canceladas) e com o sobreajuste
  (calibrar em 2014–20 e validar em 2021–25).
- **Pronto quando:** relatório `BACKTEST-2014-2025.pdf` com a tabela de retornos por palavra e a recomendação para a doutrina.
- **Modelo:** Opus high, plan mode (desenho), depois Sonnet medium (coleta/execução).

### F4 — Universo e triagem de toda a B3 (D1, D12)
**Objetivo:** pescar onde estão os peixes — médias e pequenas, pouco cobertas.
- Universo: cadastro da CVM (`cad_cia_aberta.csv`) + valores mobiliários do FCA (tickers) → todas as companhias com ação negociada. Liquidez
  mínima pelo COTAHIST (ex.: média de 60 dias ≥ R$ 2 mi/dia — calibrar com o tamanho da posição do Frank).
- Exclusões estruturais (doutrina §8): recuperação judicial, setores a evitar, menos de 7 anos de demonstrações.
- **Triagem quantitativa automática** (reusa `coletar_cvm.py` + `motor_nao_financeiras.py` em modo "rápido"):
  - Qualidade Buffett: ROIC > WACC em ≥ 7 de 10 anos; FCO positivo em ≥ 8 de 10; DL/EBITDA ≤ 2,5 ou caixa líquido; teste do R$ 1 retido ≥ 1.
  - Preço: central rápido (DCF/EPV/OE ao Ke da casa) ÷ preço; EY de Greenblatt; Graham net-net (NCAV) num balde separado ("deep value").
  - Saída: `06-triagem-e-fila.md` gerado por script com a fila ranqueada e o motivo de cada exclusão. A triagem nunca dá veredito (regra do `06`).
- **Monitor de preço semanal**: script com COTAHIST/fechamento de sexta → P/C de todo o hall → alerta quando preço ≤ compra ou ≥ saída;
  rodar pelo Agendador do Windows (schtasks + VBS oculto, ver MAQUINA.md) e anexar ao prompt de notícias.
- **Pronto quando:** fila com as 20 melhores fora do hall, cada uma com o que a análise completa precisa resolver; monitor rodando sozinho.
- **Modelo:** Opus high, plan mode (critérios); Sonnet medium (coleta e script).

### F5 — Profundidade qualitativa: o dossiê Buffett/Munger (D2, D3, D4, D16)
**Objetivo:** só depois da triagem, analisar poucas empresas a fundo, como dono.
- Novo `02-prompt-analise-completa.md` v3, com seções obrigatórias e evidência de fonte A/B:
  1. **Negócio em uma página**: como ganha dinheiro, unidade econômica (preço × volume × custo), quem paga e por quê.
  2. **Fosso com prova**: tipo (marca, custo, troca, rede, escala eficiente, regulatório) + **ROIC acima do WACC por quantos anos** + margem
     bruta estável + participação de mercado (fonte setorial: ANS, Anatel, Anvisa/CMED, ANEEL, Sindicatos, IBGE).
  3. **Gestão e alocação de capital** (FRE da CVM, fonte A): remuneração × lucro, ações dos administradores, partes relacionadas, histórico
     de aquisições (retorno do capital pago), recompras (preço pago × central da época), teste do R$ 1 retido em 10 anos.
  4. **Inversão / pré-mortem**: os 3 jeitos mais prováveis de perder 50% em 5 anos, com probabilidade e sinal de alerta.
  5. **Por que o mercado erra** (Marks, 2º nível): o que o preço embute (DCF reverso), o que o consenso pensa, onde a casa discorda e qual
     evento prova quem está certo, com data.
  6. **Projeção própria de 5 anos** por direcionadores (volume, preço, margem, capex) com 3 cenários — consenso quando houver fonte.
  7. Leitura das **notas explicativas** do último DFP (contingências, partes relacionadas, ajustes) — a CVM publica o ZIP do documento.
- **Saúde e farma primeiro** (círculo do Frank): ODPV3, HYPE3, FLRY3, RADL3, RDOR3, HAPV3, DASA3, BLAU3 — ele avalia CMED, canal e Anvisa
  melhor que qualquer agregador; a ficha tem campo "parecer do Frank".
- Notas de qualidade passam a ser **derivadas de evidência** (ex.: moat 5 = ROIC > WACC em 10/10 anos e margem estável; 1 = < 5/10), não
  arbitradas.
- **Pronto quando:** 3 dossiês completos (1 saúde, 1 da fila F4, 1 do hall para comparar) aprovados pelo adversário e pelo `verificador-fonte`.
- **Modelo:** Opus high (cada dossiê); plan mode só para o template.

### F6 — Construção de carteira e venda (D6, D7)
**Objetivo:** a doutrina diz o que comprar; falta dizer quanto e quando trocar.
- Nova **§12 da doutrina — Carteira**: tamanho máximo por posição; 1ª parcela ≤ 1/3 (já existe na exceção §9); concentração por setor e por
  controlador; caixa = Tesouro IPCA+ quando não há BARATA; troca só quando a nova tem retorno esperado ≥ 3 p.p. acima da atual **depois de
  imposto**; rebalanceamento só por tese, não por calendário.
- Regras de tamanho com base em margem e convicção (Kelly fracionado conservador, ≤ 1/4 do Kelly) — **parâmetros pessoais (patrimônio,
  limite por posição, liquidez de saída) são do Frank**: perguntar.
- `07-perfil` ganha: carteira real (ticker, quantidade, preço médio, data), horizonte, necessidade de renda mensal, tolerância a queda.
- Relatório trimestral estilo Berkshire: **valor intrínseco da carteira** (Σ quantidade × central) × valor de mercado; lucro "look-through";
  o que mudou nos centrais e por quê.
- **Pronto quando:** §12 aprovada pelo Frank; carteira registrada; 1º relatório trimestral (após o 3T26).
- **Modelo:** Opus high, plan mode.

### F7 — Disciplina de decisão e aprendizado (D15, D14)
**Objetivo:** errar menos e aprender com cada erro.
- `09-diario-de-decisoes.md`: cada compra/venda com data, preço, central, tese em 3 linhas, **o que me provaria errado**, data de revisão.
  Primeira entrada: a venda de ITSA4, ABCB4 e RANI3 (05/10/2026).
- Checklist de decisão no `04`: a lista de vieses de Munger aplicada antes de comprar (incentivo, prova social, compromisso, ancoragem no preço
  pago, disponibilidade de notícia recente).
- Revisão trimestral do diário: acertos e erros por causa (dado, método, viés), virando mudança de doutrina quando for padrão.
- 2º comitê: quando o Desktop voltar, rodar o mesmo dossiê lá (modelo diferente); até lá, o adversário + `verificador-fonte` em toda BARATA.
- **Modelo:** Sonnet medium.

### F8 — Temporada de resultados (D12)
- `ferramentas/temporada.py`: baixa o ITR novo da CVM, recoleta os tickers que publicaram, roda os lotes, compara com o golden e gera um
  boletim "quem mudou de palavra e por quê"; reemite só os PDFs afetados.
- Primeira execução: 3T26 (fim de outubro a meados de novembro).
- **Modelo:** Sonnet medium.

---

## 3. Ordem de execução (um chat por etapa)

| Etapa | Frente | Por que nesta ordem | Modelo · effort · plan mode |
|---|---|---|---|
| 1 | F1 Fundação + F7 diário | Sem teste e sem diário, qualquer melhoria seguinte é cega | Sonnet · medium · não |
| 2 | F2 Coerência do método | Corrige o motor antes de usá-lo em escala | Opus · high · **sim** |
| 3 | F3 Backtest | Valida (ou recalibra) a régua antes de sair procurando compra | Opus · high · **sim** (desenho) → Sonnet · medium (execução) |
| 4 | F4 Universo + monitor | Com a régua validada, varrer toda a B3 | Opus · high · **sim** (critérios) → Sonnet · medium |
| 5 | F5 Dossiês (saúde primeiro) | Profundidade só nas finalistas | Opus · high · sim no template |
| 6 | F6 Carteira | Depende de saber o que há para comprar | Opus · high · **sim** + respostas do Frank |
| 7 | F8 Temporada 3T26 | Data externa (out–nov) | Sonnet · medium · não |

**O que fica com o Frank** (dinheiro e preferências pessoais): parâmetros de carteira (F6), regra de venda por qualidade (F2/D7), parecer de
saúde/farma nos dossiês (F5) e executar compras e vendas.

---

## 4. Prompts prontos

**Etapa 1 — Fundação**
```
Execute a Etapa 1 do PLANO-DE-MELHORIAS-2026-10.md (F1 Fundação + F7 diário), no diretório VALUE INVESTING.
Leia o plano, a memória "Mesa v2.1 + recálculo dos lotes" e ferramentas/ (motores, lote1–6, gerar_pdf_lote1–6).
1) git init local com .gitignore (zips da CVM, dados/raw); commit inicial do estado de 05/10.
2) tests/golden.json + test_regressao.py (pytest) com central, P/C, palavra e âncoras dos 41 tickers; rodar_tudo.py com diff "o que mudou e por quê".
3) Propagar: defasagem do provento a VP em todos os lotes (Financeira ganha o campo); cobertura de juros por juros pagos (DFC).
   Rodar o diff, atualizar o hall e o registro, reemitir só os PDFs que mudarem; adversário antes de fechar.
4) Criar 09-diario-de-decisoes.md com a 1ª entrada (venda de ITSA4, ABCB4, RANI3 em 05/10/2026, preços e saídas do hall).
Decida as premissas técnicas sozinho pela doutrina; só me pergunte o que envolver comprar ou vender.
▶ Sonnet | medium | Plan mode: não | Thinking: padrão | Motivo: mecânico com testes; decisões já tomadas no plano
```

**Etapa 2 — Coerência do método**
```
Execute a Etapa 2 do PLANO-DE-MELHORIAS-2026-10.md (F2: D8 janela da margem, D9 capex de manutenção com Δreceita real, D10 ROIC a custo de
reposição, D7 proposta de venda por qualidade). Comece em plan mode: mostre a regra nova, a base (Greenwald, Buffett/Fisher) e o efeito
estimado em cada lote antes de mudar o motor. Use a regressão da Etapa 1 para provar o diff. Doutrina → v2.2 com histórico.
A regra de venda por qualidade (D7) só entra com o meu "ok". Adversário antes de fechar; verificador-fonte nas citações.
▶ Opus | high | Plan mode: sim | Thinking: padrão | Motivo: desenho de regra que muda todos os centrais
```

**Etapa 3 — Backtest**
```
Execute a Etapa 3 do PLANO-DE-MELHORIAS-2026-10.md (F3, backtest point-in-time 2014–2025 com CVM + COTAHIST da B3).
Plan mode primeiro: universo sem viés de sobrevivência, datas de corte, ajuste de proventos, rf histórica, divisão calibração 2014–20 /
validação 2021–25. Depois execute e gere BACKTEST-2014-2025.pdf com retorno por palavra e a recomendação para o prêmio do Ke e a margem de
compra. Não mude a doutrina sem me mostrar o resultado.
▶ Opus | high | Plan mode: sim | Thinking: padrão | Motivo: desenho experimental; erro de look-ahead invalida tudo
```

---

## 5. Riscos do próprio plano (inversão)

- **Sobreajuste no backtest** — calibrar a régua até ela "acertar" o passado. Defesa: amostra fora do período e poucas variações testadas.
- **Complexidade que ninguém mantém** — Munger: simplicidade. Defesa: cada frente termina com um script único e um teste; o que não for usado
  em 3 meses sai.
- **Falsa precisão** — centrais com centavos sobre premissas incertas. Defesa: toda ficha mostra a faixa (sensibilidade) e a palavra decide,
  não o centavo.
- **Mais dado ≠ mais acerto** — o diário (F7) mede se as melhorias melhoraram decisões; se não, voltar atrás.
