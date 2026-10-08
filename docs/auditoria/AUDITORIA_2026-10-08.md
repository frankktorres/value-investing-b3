# Auditoria técnica integral — 2026-10-08

Auditoria somente leitura do projeto VALUE INVESTING (ferramentas/, docs da raiz, backtest, triagem, dossiês, rotinas). Cada achado foi reproduzido por um verificador independente. Nenhum arquivo do projeto foi alterado, exceto este relatório.

## 1. Sumário executivo

- **Estado geral:** as contas do motor estão certas. Refiz do zero PETR4, SBSP3, ITUB4 e WEGE3 sem usar o código do motor e o valor central bateu com diferença de 0,00% a 0,36% (só arredondamento de insumo). Os testes rápidos passam (301) e o `rodar_tudo` reproduz o golden. Nenhum erro de aritmética foi encontrado.
- **O risco real está nos insumos e nas escolhas de método**, não nas fórmulas. Foram confirmados 109 achados: 0 críticos, 5 altos, 33 médios, 71 baixos. Nenhum faz nascer uma compra errada hoje; vários mexem no valor central em 5% a 48% e em palavras de fronteira.
- **Os 5 problemas mais graves:**
  1. **AUD-01** — a receita de meio de ciclo é média em reais antigos (nominal) enquanto o resto está em reais de hoje: valor central subestimado em 13 empresas (SUZB3 muda de CARA para JUSTA).
  2. **AUD-02** — R$ 5,9 bi de dividendos a pagar da WEGE3 ficam fora da dívida líquida; o central cairia 22% pela regra da própria doutrina v2.3.
  3. **AUD-03** — na PETR4 o aluguel é contado duas vezes em 3 dos 10 anos da margem (regra IFRS 16 da doutrina não aplicada): erro conservador, esconde um possível RADAR.
  4. **AUD-04** — ISAE4: o valor patrimonial por ação mistura o patrimônio de antes do follow-on com as ações de depois; pela regra da casa a palavra passaria de CARA para JUSTA.
  5. **AUD-05** — o repositório não tem cópia remota: o registro prospectivo (evidência que não se refaz) e 2 GB de dados existem num só disco.
- **Confiança no veredito atual do hall: MÉDIA.** Alta nas contas e na decisão de vender ITSA4 e ABCB4 (robustas a qualquer perturbação simples) e no fato de que "nenhuma compra hoje" se sustenta. Média porque 12 a 13 empresas estão a menos de um ponto de uma premissa de trocar de palavra (SMTO3, EGIE3, ISAE4, SUZB3, PETR4, KEPL3, LEVE3 e outras), os insumos de mercado são de 02/10 e vários insumos digitados não têm fonte A/B. Baixa para o número exato do valor central das alavancadas (KLBN11, SLCE3, SUZB3, RANI3).
- **Próximo passo sugerido:** Onda 1 do roteiro (seção 6), começando por AUD-05 (backup, esforço pequeno), AUD-01 e AUD-02.

## 2. Tabela de achados confirmados

Ordenada por severidade final (após verificação). Dimensões: D1 doutrina/régua, D2 cálculo, D3 dados, D4 engenharia, D5 testes, D6 estatística/método, D7 documentação, D9 operação/reprodutibilidade, D10 prontidão SaaS/ficha. Esforço: P pequeno, M médio, G grande. Quando a severidade do revisor foi alterada pelos verificadores, está indicada (ex.: ALTO→MÉDIO). Não há achado CRÍTICO.

| ID | Dim | Sev | arquivo:linha | Descrição | Evidência (verificador) | Impacto na decisão | Correção sugerida | Esf |
|---|---|---|---|---|---|---|---|---|
| AUD-01 | D2 | ALTO | ferramentas/motor_nao_financeiras.py:386 | receita_meio padrão é média NOMINAL de 3 exercícios + LTM, enquanto todo o resto está em R$ de hoje (doutrina 11.1 linha 236) | expB_receita_real.py: SUZB3 central 37,12→43,60 (+17,4%), CARA→JUSTA; KLBN11 +48,5%; RANI3 +15,6%; SLCE3 +22,9% | Central subestimado 4% a 48% em 13 tickers; saída de SUZB3 sobe 17% | Deflacionar cada receita por inflacao.DEFLATOR antes da média (ou declarar nominal); regravar golden | P |
| AUD-02 | D2 | ALTO | ferramentas/lote4_saude_telecom.py:193 | Dividendos/JCP a pagar de R$ 5,93 bi fora da dívida líquida da WEGE3, contra a regra v2.3 (só CMIN3 usa o campo) | ITR 2T26: 2.01.05.02.01 = 2.468.860 + 2.02.02.02.07 = 3.464.232 (R$ mil); com outros_passivos_financeiros=5,933 bi: central 11,918→9,280 (−22,1%), compra 8,34→6,50, saída 15,49→12,06 | Palavra segue CARA (P/C 5,54); preços de compra/saída 22% acima da regra | Preencher outros_passivos_financeiros com fonte e regravar golden; varrer outros tickers | P |
| AUD-03 | D2/D3 | ALTO | ferramentas/lote5_petroleo.py:117 | PETR4: EBITDA pré-IFRS 16 (2016-18) menos D&A pós-IFRS 16: aluguel descontado 2x em 3 dos 10 anos; doutrina 11.1 manda usar só 2019+ | evid_ifrs16/sens: EBITDA/rec 31,0%→46,4% de 2018 a 2019; margens 11,3/11,8/14,8% as três menores; central +9,6% a +23,9%, P/C 0,988→0,90/0,80 | Erro conservador; JUSTA só se mantém pela dispersão; pode esconder RADAR | Janela 2019-25 com janela_razao IFRS 16, ou somar aluguel ao EBITDA 2016-18 | M |
| AUD-04 | D2/D3 | ALTO | ferramentas/lote2_energia.py:103 | ISAE4: VPA 31,51 = PL do 2T26 (antes do follow-on de R$ 1,2 bi) ÷ ações pós-follow-on; regra §11.2 (aplicada no EGIE3) não aplicada | s13_followon: com a regra, VPA 33,21, ROE lp 16,81%, central 25,78 (+7%), P/C 1,094 JUSTA (golden: CARA 1,17) | Muda CARA→JUSTA; a correção sugerida no texto do lote (659 mi) também está errada | Aplicar pl_new no ISAE4; corrigir lote2_textos.py:50 e o hall | P |
| AUD-05 | D9 | ALTO | PLANO-DE-MELHORIAS-2026-10.md:60 | Repositório sem remoto: código, golden, registro prospectivo (append-only) e 2 GB de dados só existem em um disco | git remote vazio; 594 objetos soltos, 0 packs; ferramentas/dados 1,4 GB, backtest/dados 674 MB | Perda de disco = perda da validação prospectiva e do histórico de decisões | Backup periódico (bundle ou remoto privado) e cópia dos dados fora do C: | P |
| AUD-06 | D1 | MÉDIO (ALTO→MÉDIO) | ferramentas/lote1_bancos.py:14 | rf do Ke é a taxa de COMPRA DA MANHÃ do Tesouro Transparente (intradiária), rotulada "fechamento" (motor_financeiras.py:33, gerar_pdf_lote4.py:480); doutrina §4 proíbe intradiária | mercado.json:10; ANBIMA fechamento 7,1377%; variante C: SLCE3 CARA→NÃO CONCLUSIVO, UNIP6 NÃO CONCLUSIVO→JUSTA; Ke −24 pb (misturado com troca de π) | Sem efeito em compra/saída; 2 palavras trocam por degrau de dispersão | Usar fechamento com data escrita, ou mudar §4 e corrigir rótulos | P |
| AUD-07 | D1 | MÉDIO (ALTO→MÉDIO) | ferramentas/motor_nao_financeiras.py:525 | Kd = rf nominal + spread digitado por ticker (0,5 a 2,5 p.p., sem fonte); não existe campo para o custo médio do RI (regra primária §2) | Kd −2 p.p.: SUZB3 +34,3% CARA→RADAR; SMTO3 +28% RADAR→BARATA; juros/dívida bruta 3% a 5,6% contra Kd usado 15,5% | Palavra de SUZB3, SMTO3, SLCE3 depende de spread sem fonte; viés conservador | Campo kd_ri com fonte; spread declarado; sensibilidade na ficha | M |
| AUD-08 | D1 | MÉDIO | ferramentas/motor_nao_financeiras.py:810 | Trava de coerência §9 é só flag: LEVE3 sai JUSTA com trava=False (diferença Bogle−Ke de 3,93 p.p. > 2) e "Não vence a RF"; hall diz "por pouco / 2,3 p.p." | s3: LEVE3 bogle_nom 0,1537 ke_nom 0,1930 trava=False vence_rf Não | Sem compra/saída; contradição que a doutrina manda corrigir antes de publicar | Trava rebaixa a palavra, ou documentar a exceção no 09 | P |
| AUD-09 | D1 | MÉDIO | ferramentas/lote4_saude_telecom.py:188 | ABEV3: alíquota explícita com 2 exercícios contorna mínimo de 3 anos e regra de origem v2.3 (motor:453-454 sem checagem) | s4: central 10,50 (20,74%) contra 8,92 (34% pela regra); CARA nos dois | Central +17,7% acima da regra; premissa Lei 14.789 pendente no 09 | Exigir aliquota_fonte e mínimo de anos | P |
| AUD-10 | D1 | MÉDIO | ferramentas/motor_financeiras.py:369 | Trava calculada só se a palavra da régua (antes da dispersão) é JUSTA, não a final | sintetico.py B: palavra_final JUSTA, trava=None | Nenhum ticker hoje (latente) | Calcular sobre a palavra final | P |
| AUD-11 | D1 | MÉDIO | ferramentas/motor_financeiras.py:347 | Sem a guarda "LPA normalizado ≤ 0 → NÃO CONCLUSIVO": TypeError (complexo); com central ≤ 0, P/C negativo, BARATA e nota de preço 10 | tb_neg.py: TypeError na linha 353; palavra(−0,5)=BARATA, nota_preco=10 | Banco/utility com prejuízo derruba o rodar_tudo dos 41 | Replicar guardas do motor NF + teste | P |
| AUD-12 | D2 | MÉDIO (ALTO→MÉDIO) | ferramentas/motor_nao_financeiras.py:526 | Ke fixo (rf+5 p.p.) em todas as empresas: o WACC cai com a alavancagem (14,5% KLBN11 contra 19,1% WEGE3) | expC (Ke realavancado, sensibilidade): SMTO3 −32,9% RADAR→CARA; PETR4 e LEVE3 JUSTA→CARA; KLBN11 central −0,74 | Consequência de convenção deliberada (§4), não bug; a palavra de SMTO3, PETR4, LEVE3 depende dela | Decidir e registrar no 09; mostrar sensibilidade para D/E > 1 | M |
| AUD-13 | D2 | MÉDIO | ferramentas/motor_nao_financeiras.py:522 | WACC pesa E pelo preço: central varia com o preço, compra/saída não são ponto fixo | expF: SMTO3 preço×0,7 central 25,80, ×1,0 23,07, ×1,3 22,41; KLBN11 7,64/4,98/3,14 | Efeito sobre o preço de compra é conservador; sem troca de palavra | Estrutura de capital-alvo ou ponto fixo | M |
| AUD-14 | D2 | MÉDIO | ferramentas/motor_nao_financeiras.py:579 | Trava de crescimento "cria" é degrau binário por cenário; doutrina e comentário dizem "gradual" (falso) | expA: WEGE3 margem 0,168→0,169: DCF base 11,07→15,05 (+36%), mas central só +5,1% (OE amortece) | Só WEGE3 e ABEV3 perto do degrau; sem troca de palavra | Interpolar g efetivo, ou exibir central com e sem trava; corrigir o texto | M |
| AUD-15 | D2 | MÉDIO | ferramentas/motor_nao_financeiras.py:542 | oe_val usa lucro consolidado e não deduz minoritários, ao contrário de EPV/DCF | expF/expC: KLBN11 oe_val 11,49→8,65 com lucro do controlador; nenhum central muda hoje | Latente; direção do valor contábil dos minoritários não demonstrada | Usar lucro_controlador no OE; documentar critério do NCI | M |
| AUD-16 | D2 | MÉDIO | ferramentas/motor_nao_financeiras.py:601 | Owner Earnings (e DPA) em R$ nominal de cada ano, capitalizados a Ke real | expC 1a: LEVE3 central 33,99→36,76 (+8,2%), P/C 1,01→0,94; FLRY3 confiança baixa→normal | Só onde OE é a âncora do meio; sem troca de palavra | Multiplicar cada OE por DEFLATOR[ano] antes da mediana | P |
| AUD-17 | D2 | MÉDIO | ferramentas/motor_financeiras.py:186 | DDM 2 estágios e P/VP justificado sem nenhum teste analítico; só regressão contra golden gerado pelo motor (circular) | grep em tests/: nenhuma linha; fórmula hoje correta (0,000%) | Latente: erro de fórmula seria gravado no golden sem alarme | Teste com caso mínimo calculado à mão | P |
| AUD-18 | D2/D3 | MÉDIO (ALTO→MÉDIO) | ferramentas/motor_nao_financeiras.py:613 | Âncora "valor de reprodução" é PL contábil a custo histórico, enquanto o ROIC usa capital a custo de reposição | sens3: PETR4 reprodução 34,33→86,21; central 51,78→57,28, P/C 0,893 RADAR (por 0,007) | A alternativa proposta é escolha do auditor, não demonstrada mais correta; escolha declarada no código | Definir fórmula na doutrina 11.1 ou tratar reprodução como piso informativo | M |
| AUD-19 | D2/D3 | MÉDIO (ALTO→MÉDIO) | 03-hall-de-acoes.md:141 | PDFs vigentes dos Lotes 4, 5 e 6 (rev. 05/10, v2.2) não foram reemitidos após a v2.3; hall §5 os indica como vigentes | pdftotext: HYPE3 central 19,60 (hall 17,51); LEVE3 saída 50,98 "1,50x" (motor 44,18, 1,30x) | Palavra não muda; saída da LEVE3 15% maior no PDF | Reemitir PDFs ou marcar no §5 "anterior à v2.3" | P |
| AUD-20 | D2/D3 | MÉDIO | ferramentas/lote2_energia.py:3 | P/VP justificado usado no lugar do DCF regulatório sem a condição do §11.2: na Sabesp o capex (R$ 13,74 bi) está no FCI | DFP 2025: 6.01 FCO 8.361.115; 6.02.01 −13.740.392; LTM FCO−capex −8.186 mi | Não muda palavra (CARA); central pode estar subestimado (RAB nota C) | Calcular DCF regulatório ou registrar a exceção | M |
| AUD-21 | D3 | MÉDIO | ferramentas/coletar_cvm.py:321 | LTM = FY + 1S26 − 1S25 do ITR 2025 original, não o comparativo reapresentado do ITR 2026 | t6: ISAE4 EBIT +9,9% lucro +17,4%; SLCE3 FCO −49%; KEPL3 FCO +5,7% | Sem efeito demonstrado hoje; cresce no 3T26 | Usar comparativo do ITR corrente ou alertar divergência > 0,5% | M |
| AUD-22 | D3 | MÉDIO | ferramentas/coletar_cvm.py:306 | SMTO3: fluxos do LTM congelados em mar/2026 e rotulados 2T26; não avançam em 3T26 | t10: LTM receita == anual[2026]; caixa ITR 56.789 contra 95.263 | SMTO3 é o único RADAR; fluxo 6–9 meses atrás do balanço | LTM = FY(mar/26) + YTD novo − YTD anterior; rotular pela data real | M |
| AUD-23 | D3/D2 | MÉDIO | ferramentas/dossie/base.py:277 | Dossiê soma linhas duplicadas de JCP da B3 sem a deduplicação do backtest: DPA 2024 de HYPE3 inflado | dup3: HYPE3 2024 B3 1,2651 contra StatusInvest 1,1678; duas linhas idênticas de 01/02/2024 | ~+1,6% no dpa5 da HYPE3; sem troca de palavra; latente para próximos dossiês | Reusar regra de duplicata; conferir B3 contra StatusInvest (alerta > 3%) | P |
| AUD-24 | D3/D4 | MÉDIO | ferramentas/motor_nao_financeiras.py:25 | sorted(glob("series_*.json"))[-1] (também lote2:22, defasagem:20): um series_ parcial novo derruba o import de todos os lotes | cópia com series_2026-10-07.json de 2 tickers: KeyError 'TAEE11' em lote2_energia.py:83 | Falha ruidosa dos 41; sem veredito errado | Constante/manifesto do arquivo vigente; validar cobertura no import | P |
| AUD-25 | D3/D6 | MÉDIO (ALTO→MÉDIO) | ferramentas/backtest/ledger/identidade.py:19 | Elo ticker→CNPJ só via FCA descarta em silêncio 9% a 13% do universo líquido em 2015-16 (2 a 3% depois); docstrings dizem "sem viés de sobrevivência" | v.py: 2016-06-30 universo 142, 13 sem CNPJ; 2015 22 de 173 (12,7%); mistura mortos, renomeados e vivos | Não afeta a mesa; afeta validade do backtest se retomado | Mapear também pelo cadastro cia_aberta/ISIN; medir a perda por corte | M |
| AUD-26 | D4 | MÉDIO | ferramentas/lote4_saude_telecom.py:126 | Importar lote4 reescreve os dicts SI/CVM compartilhados (DPA e arrendamento_pago): resultado depende da ordem de import | ver-R10-01: VIVT3 DPA 2026 2,098→0,846; arrendamento 2025 0→3.304.692 | Hoje todos os caminhos passam por universo; latente para dossiê novo | Função idempotente no carregamento do motor + teste | M |
| AUD-27 | D5 | MÉDIO | ferramentas/tests/test_metodo_f2.py:239 | Limiares de saída e da exceção de qualidade (1,30; 1,50; nota 8; 8 de 10) sem teste independente: testes importam as constantes do motor | Mutação NOTA_QUALIDADE_MINIMA 8→5 sobrevive a 248+43 testes (ABEV3 saída 13,65→15,75, LEVE3 44,18→50,98) | Gatilho de venda pode mudar sem teste vermelho | Escrever números da doutrina à mão; guardar compra/saída no golden | P |
| AUD-28 | D5 | MÉDIO | ferramentas/tests/test_metodo_f2.py:267 | Teste "ROIC real contra real" passa pelo motivo errado: a mutação serie_roic=nominal sobrevive | efeito_M16: 18 de 21 tickers mudam a contagem (SUZB3 1→5, ABEV3 8→10) | Critério 8/10 da exceção de saída sem proteção | Exigir valor exato recomputado com a fórmula do motor | P |
| AUD-29 | D5 | MÉDIO | ferramentas/backtest/tests/test_pit_nao_vaza.py:197 | Sentinela PIT só compara procedencia() e anuais[].contas: vazamento em dfc ou no ITR passa; amostra = 40 menores cd_cvm | cego_sentinela.py: dois ledgers com dfc e ITR diferentes passam; grep sem .dfc | Não altera ticker; reduz o valor do selo PIT | Comparar Exercicio inteiro; estender test_5b | P |
| AUD-30 | D5 | MÉDIO | ferramentas/golden.py:39 | Golden aceita NaN: _difere devolve False; palavra(NaN)="CARA" (palavra de 34 dos 41) | nan_golden.py: central/pc/dy/bogle/nota/âncora → 0 mudanças detectadas | NaN em ticker CARA passa sem alerta | Tratar NaN explicitamente; validar finitos | P |
| AUD-31 | D5 | MÉDIO | ferramentas/motor_financeiras.py:60 | IR do JCP, IR do resgate, defasagem, renda sustentável e dispersão só protegidos pelo golden (prova "igual", não "certo") | grep 0; M06 (sinal do IR): 22 falhas novas, todas só em test_regressao | Regravar golden com --motivo deixa passar qualquer número | Testes de fórmula à mão; um ticker recalculado em planilha | M |
| AUD-32 | D6 | MÉDIO (ALTO→MÉDIO) | 09-diario-de-decisoes.md:105 | Regra de refutação pré-registrada sem poder: 1 RADAR contra 34 CARA | d_poder.py: MDE 126 p.p./data (1 vs 34); regra com 4 datas dispara 50% sob H0 e 34% com +5 p.p. reais | Diário já admite que a leitura de 2027 não decide sozinha | Critério contínuo (IC de postos de P/C × retorno excedente) | M |
| AUD-33 | D6/D1 | MÉDIO | ferramentas/triagem/config.py:64 | Corte da fila (P/C proxy > 1,44) justificado com a mediana do erro (0,34), que não é limite | corte.py: proxy superestima > 0,34 em 7 de 34 (HYPE3 1,28→2,42; PRIO3 1,15→1,49); proxy 23/41 contra "sempre CARA" 34/41 | Papel barato pode ser cortado por ruído; 15 cortados nunca re-testados | Corte por quantil do erro ou só ordenar; corrigir a frase do 06 | P |
| AUD-34 | D6/D3 | MÉDIO | ferramentas/motor_nao_financeiras.py:580 | g ≤ 0 com ROIC < WACC faz o DCF explodir; DCF reverso imprime "≤ −5%" por artefato | s8: KLBN11 DCF(g=0) 3,79, (−0,3%) 39,43, (−5%) 357,65; PETR4 g −0,5% JUSTA→RADAR | Latente (só RECV3 tem o freio); PDFs leem "preço embute contração" | declinio_sem_liberacao como padrão para g < 0; corrigir texto | M |
| AUD-35 | D7 | MÉDIO | UPLOAD CLAUDE DESKTOP/03-hall-de-acoes.md:34 | Pasta de upload defasada em 4 arquivos (03, 01, README, prompt de notícias) | cmp: DIFERE nos 4; LEVE3 saída 50,98 contra 44,18; prompt "PRIO3 30,38" contra 34,56 | Agente de sexta do Desktop recebe gatilhos errados (−12% compra, +15% saída) | Reenviar ou colocar aviso DEFASADA no README e no prompt | P |
| AUD-36 | D7 | MÉDIO | 08-prompt-recalculo-lote.md:6 | Cabeçalho diz v2.3, instrução operacional diz "pela doutrina v2.0"; prompt de notícias cita fallback "v2.0/2.1" | sed 6p do 08: "…01-doutrina-value-investing.md **v2.0**" | Chat novo recalcularia lote com regra antiga | Trocar v2.0 por v2.3 | P |
| AUD-37 | D9 | MÉDIO (ALTO→MÉDIO) | ferramentas/monitor_semanal.py:260 | Monitor semanal sem alerta ativo de falha; prompt do agente não exige data do boletim = sexta; tarefa "Interativo apenas" | schtasks: Logon interativo, último resultado 0; return 1 só se download falhou E pregão > 7 dias | Boletim velho pode ser lido como atual (mitigado por -StartWhenAvailable) | Exigir data da sexta no prompt; sentinela de falha; log anexado | P |
| AUD-38 | D9/D3 | MÉDIO (ALTO→MÉDIO) | ferramentas/lote4_saude_telecom.py:67 | Clone do zero não roda rodar_tudo nem pytest: lote4/lote6 abrem ZIPs da CVM (ignorados pelo git) no import; sem requirements nem bootstrap | git archive: FileNotFoundError itr_2026.zip; pytest "Interrupted: 1 error during collection" | ZIPs são recoletáveis; falta receita, manifesto e leitura preguiçosa | requirements.txt, README de bootstrap, import tolerante com mensagem | M |
| AUD-39 | D1 | BAIXO | ferramentas/motor_nao_financeiras.py:829 | Nota de Solidez ignora Piotroski e Beneish que o §10 manda incluir (lote2 usa só alavancagem e cobertura) | n_sol = (alav_n + z_n + cob_n)/3; lote2:79 (a+c)/2 | Só nota geral | Incluir ou corrigir o §10 | P |
| AUD-40 | D1 | BAIXO | ferramentas/motor_financeiras.py:360 | Carimbo "perde para o Tesouro no cenário ruim" implementado no ponto médio, sem faixa | carimbo_rf = bogle_liq_real < rf_liq_real; PDF diz "ponto médio" | Informativo | Calcular faixa ou reescrever §4 | M |
| AUD-41 | D1 | BAIXO | ferramentas/atualizar_hall_lote1.py:13 | Filtros de entrada do hall, linha de desconto de controlador e "TIR < rf ⇒ CARA" sem enforcement no motor | FORA_DO_HALL literal; 20 de 41 com razão vazia; regra TIR só em texto de PDF | Nenhum hoje | Função filtros_1a4; exigir razão não vazia | M |
| AUD-42 | D1 | BAIXO (MÉDIO→BAIXO) | ferramentas/gerar_pdf_lote1.py:325 | Entrada parcial (0,80×) não existe no motor; cada PDF reimplementa condições diferentes | grep: lotes 1/3/5 testam só qualidade/solidez/confiança; lote 6 tem dicionário de bloqueios | Nenhum ticker ≤ 0,80× (menor é SMTO3 0,838) | entrada_parcial_elegivel() no motor + teste | M |
| AUD-43 | D1 | BAIXO (MÉDIO→BAIXO) | ferramentas/monitor_semanal.py:114 | alerta() ignora a palavra final: UNIP6 (NÃO CONCLUSIVO) emitiria "≤ COMPRA" a R$ 37 | finais.py: alerta(37,00)="≤ COMPRA" | Rótulo induz compra onde a doutrina proíbe (texto manda rodar o 05) | Passar a palavra final ao alerta | P |
| AUD-44 | D1 | BAIXO (MÉDIO→BAIXO) | ferramentas/motor_financeiras.py:238 | Âncoras de bancos/utilities não são independentes: dispersão 1,00–1,13 em 18 tickers; EGIE3 depende de um só modelo | dump_universo: ITUB4 1,07 … SAPR11 1,13; P/VP justificado 28,39 e DDM 29,15 em EGIE3 | Consequência do §11.2; sem efeito (18 CARA) | Âncora independente ou sensibilidade a ROE lp | G |
| AUD-45 | D1 | BAIXO | ferramentas/motor_financeiras.py:311 | Precedência da régua (círculo, dispersão, NC) sem teste nos motores de produção; três cópias; golden não grava dispersão/trava | grep fora_circulo em tests/: 0; diferencial de 144 combinações: 0 divergências | Risco de deriva futura | Função única de régua; dispersão no golden | M |
| AUD-46 | D1 | BAIXO | ferramentas/motor_financeiras.py:69 | Fronteiras da régua em ponto flutuante: preço de compra cai em RADAR em ~5% dos casos | sintetico C: 0,70×c/c = 0,7000000000000001 | Desprezível (centavos) | round(pc, 9); arredondar compra para baixo | P |
| AUD-47 | D1 | BAIXO (PARCIAL) | ferramentas/motor_nao_financeiras.py:624 | Âncora Owner Earnings some sem aviso se oe_norm falsy ou Ke real ≤ g; confiança segue "normal" com 2 âncoras (conforme §11.3) | finais.py 3: TIMS3 g_real 0,20: 3→2 âncoras, normal | Nenhum hoje | Registrar âncora descartada | P |
| AUD-48 | D1 | BAIXO | 02-prompt-analise-completa.md:81 | 02 lista só 3 dos 5 critérios da entrada parcial; doutrina linha 190 mantém texto de 05/10 (saída 50,98) ao lado do de 08/10 | grep dos dois textos | Risco de o comitê B aplicar a exceção sem checar círculo e dispersão | Alinhar o 02 ao §9; limpar o parágrafo | P |
| AUD-49 | D10 | BAIXO (MÉDIO→BAIXO) | ferramentas/monitor_semanal.py:39 | Prontidão SaaS: carteira em código, registro sem lock, sem requirements, dados sem versão fixada | ls requirements.txt: inexistente; CARTEIRA literal na linha 39 (não 47) | Nenhum na decisão atual | Requirements, config fora do git, lock/SQLite | M |
| AUD-50 | D2 | BAIXO (MÉDIO→BAIXO) | ferramentas/motor_nao_financeiras.py:657 | ROIC a reposição deflacionado pela inflação do ano (questão aberta: "dupla contagem" é interpretação) | expG V2: SUZB3 anos>WACC 1→5, ABEV3 8→10, B3SA3 6→7; saída por qualidade False em todos | Nenhum hoje; D7 decidida após revisão adversarial | Registrar a premissa no diário | M |
| AUD-51 | D2 | BAIXO (MÉDIO→BAIXO) | ferramentas/motor_nao_financeiras.py:460 | Degrau da alíquota em 15%: VIVT3 (15,53%) a 0,5 p.p. do salto para 34% | viv.py: VIVT3 17,28→13,41 (−22,4%), CARA nos dois lados | Regra deliberada (diário 156-159); falta alerta de proximidade | Alerta quando a mediana ficar a menos de 1 p.p. de 15% | P |
| AUD-52 | D2 | BAIXO | ferramentas/motor_nao_financeiras.py:843 | RECV3 (NÃO CONCLUSIVO) deixa compra/saída negativas no dict, nota geral numérica e "Infinity" no golden.json | expD: compra −0,11, saída −0,20, nota geral 2,76; golden.json:460 "pc": Infinity | Só para consumidor futuro sem guarda | compra/saída None se central ≤ 0; inf como null | P |
| AUD-53 | D2 | BAIXO | ferramentas/motor_nao_financeiras.py:595 | Cenário de DCF negativo entra na ponderação sem piso em zero | expD g: KLBN11 pessimista −1,84; com piso central 4,98→5,44 (+9,3%) | Só KLBN11; continua CARA | max(cenário, 0) antes de ponderar | P |
| AUD-54 | D2 | BAIXO | ferramentas/motor_nao_financeiras.py:826 | DL/EBITDA ausente vira nota máxima e cobertura ausente vira mínima; âncora OE some sem sinalizar | leitura L751, L826-828 | Latente, só nota | dl_ebitda None → alav_n = 1 | P |
| AUD-55 | D2 | BAIXO (PARCIAL) | ferramentas/defasagem.py:35 | Só VBBR3 usa defasagem medida (8,5 meses) e a doutrina L125 ainda cita "Vibra 15-18" | defasagem.py; golden fvp FLRY3 0,876 (9 meses declarados) | Texto desatualizado; DY de VBBR3 informativo | Reconciliar texto ou declarar prazo da VBBR3 | P |
| AUD-56 | D2 | BAIXO (MÉDIO→BAIXO) | ferramentas/lote2_energia.py:26 | ROE lp das utilities = mediana bruta 2016-25 sem teste de quebra; só EGIE3 limpa não recorrentes | s12: janela 2023-25 → CMIG4 CARA 1,58→JUSTA 1,02; SBSP3 central 7,05→13,47 | Janela recente não demonstrada mais correta; escolha conservadora | Declarar janela por ticker; sensibilidade | M |
| AUD-57 | D2 | BAIXO (MÉDIO→BAIXO) | ferramentas/motor_financeiras.py:41 | π implícito 6,46% com ROE nominal fixo: π 4% (Focus) leva ITUB4 de 17,54 a 22,39 (+28%); sensibilidade fora do golden | s6: ISAE4 CARA→JUSTA, EGIE3 JUSTA→RADAR em π 4% | Escolha deliberada (§4); lacuna de cobertura | Coluna de palavra sob mercado alternativo no golden | P |
| AUD-58 | D2 | BAIXO | ferramentas/lote1_bancos.py:53 | Premissas digitadas divergem do coletado sem justificativa: dpa_medio_5a BRBI11 1,628 (SI 1,302), CXSE3 1,000 (SI 0,849), cobertura ABCB4, horizonte_finito BBSE3 | s2_compara | Nenhum na palavra | Comentar fonte de cada premissa | P |
| AUD-59 | D2 | BAIXO (PARCIAL) | ferramentas/motor_financeiras.py:173 | Quando o teto de g morde (7 tickers), o terminal assume payout implícito diferente do digitado | s10 T4: SBSP3 payout 0,05/0,25/0,80 → central 6,68/7,05/9,36 | Limitação de documentação | Exibir payout terminal implícito | P |
| AUD-60 | D2 | BAIXO (PARCIAL) | ferramentas/lote1_bancos.py:60 | BBSE3 e CXSE3 com QUAL(4,3,3,3,3) e solidez 8,0 idênticos ("arbitrada, pré-v4") | grep | Só nota geral; pendência declarada | Revisar no dossiê | P |
| AUD-61 | D2 | BAIXO | ferramentas/lote1_bancos.py:26 | payout 0,60 do ITUB4 sem fonte primária; comentário (58%) diverge do fatos_B (69,4%) | S6: payout 0,37→0,694 muda central −3,2% a +1,9% | Nenhum | Citar política do RI ou marcar nota C | P |
| AUD-62 | D2 | BAIXO | ferramentas/lote1_bancos.py:24 | dpa_medio_5a do ITUB4 (2,069) mistura ordinário e extraordinário, embora o campo diga "ajustado" | DPA 2021-25: 0,909; 1,018; 1,257; 2,413; 4,750; JCP média 1,174 | Só DY/Bogle/teto de renda | Separar ordinário e extra | M |
| AUD-63 | D2 | BAIXO | ferramentas/motor_financeiras.py:151 | Comentários de campo divergem do uso (roe_inicio "ano 1" é t=0; "2T26 ~22%" contra 24,3% no fatos_B) | S4: ROE 12m como ano 1: central 17,54→17,68 (+0,8%) | Nenhum | Corrigir comentários | P |
| AUD-64 | D2/D10 | BAIXO (PARCIAL) | ferramentas/lote5_textos.py:35 | Ficha de PETR4 expõe Brent, atuarial e abandono, mas não as outras sensibilidades (janela IFRS 16, sem desconto de controlador, sem corte de "outras") que levam P/C a 0,80–0,91 | sens/sens2/sens6: 0,963; 0,926; 0,909; 0,882; atuarial 1,133; capex LTM 1,276 | Lacuna de documentação | Tabela única de P/C por premissa | P |
| AUD-65 | D2/D10 | BAIXO | ferramentas/lote5_textos.py:36 | Texto diz que o p25 vem de "2016-17 com Brent ~US$ 50"; o p25 é 2018 (Brent US$ 71) | sens2: margens (2017 11,3; 2016 11,8; 2018 14,8) | Erro de explicação | Gerar o texto a partir dos anos reais | P |
| AUD-66 | D2/D3 | BAIXO (PARCIAL) | ferramentas/motor_nao_financeiras.py:382 | p25/p75 por posto mais próximo com n=10 (3º e 8º valor); estimador não definido na doutrina | sens_PETR4: percentil linear central 51,78→53,16 (+2,7%) | Palavra igual | Declarar estimador | P |
| AUD-67 | D2/D3 | BAIXO (MÉDIO→BAIXO) | ferramentas/lote6_quimica.py:159 | Preços digitados sem fonte/data nem teste; L2, L4–L6 divergem 1–11% do snapshot de 05/10; EGIE3 vira CARA (1,14) com o preço novo | s9_universo/s8_egie: EGIE3 JUSTA 1,07→CARA 1,14; payout 0,8 → CARA 1,217 | Preços de 02/10 são deliberados (diário L9/L42, PLANO D12) | preco_data/preco_fonte + teste contra series | P |
| AUD-68 | D2/D3 | BAIXO (MÉDIO→BAIXO) | ferramentas/dados/cvm_series.json | SBSP3: lucro_controlador 0/inconsistente e ações pré-split (700 mi contra 3.494 mi) | s4_sbsp: anual 2023-25 lucro_controlador 0,0; LTM 3.196.215 contra lucro 8.057.470 | Latente (lote 2 não usa); armadilha para o 3T26 | Corrigir coletor e testar CVM×digitado | M |
| AUD-69 | D2/D3 | BAIXO (MÉDIO→BAIXO) | 03-hall-de-acoes.md:57 | Ke implícito/retorno digitados divergem do motor: PETR4 20,3% (motor 19,43%), BBDC4 12,0% (11,61%), PSSA3 12,2% (11,78%) | cmp_hall2.py | Sem efeito em palavra/central | Regenerar células do motor | P |
| AUD-70 | D2/D4 | BAIXO (MÉDIO→BAIXO) | ferramentas/motor_financeiras.py:14 | PIB real de LP 2% (teto de g) e payout 25% de SBSP3 (nota C) sem fonte A/B | PIB 1%/3%: +6,4%/−7,8%; payout 52%: +14,8% | Sem efeito na palavra CARA | Citar fonte ou registrar como escolha da casa | P |
| AUD-71 | D3 | BAIXO | ferramentas/dados/mercado.json:1 | Dados sem leitor: fatos_*.json (7), mercado.json e ZIPs IPE não são lidos por nenhum código | grep: só docstrings e strings de PDF | Fonte documentada e valor usado podem divergir sem alarme | Teste de conferência ou marcar como só documentação | P |
| AUD-72 | D3 | BAIXO (MÉDIO→BAIXO) | ferramentas/lote1_bancos.py:14 | Sem regra de idade do preço no código (regra dos 15 dias só em prosa); com mercado de 06/10 ISAE4, SUZB3 e EGIE3 mudam de palavra | s6_idade_preco; grep date.today em motor/rodar_tudo/universo: 0 | Defasagem documentada (PLANO D12); hall tem aviso estático | data_preco no golden e aviso calculado | M |
| AUD-73 | D3 | BAIXO (MÉDIO→BAIXO) | ferramentas/coletar_cvm.py:327 | cvm_series.json versionado em formato antigo (só ltm_2T26); sem requirements, manifesto de hash nem receita de reconstrução do zero | keys de PETR4; git ls-files requirements: 0; recoleta de 4 tickers bateu campo a campo | Reprodutibilidade parcial; veredito reproduzível pelo git | requirements, README de reconstrução, sha256 dos ZIPs | M |
| AUD-74 | D3 | BAIXO (MÉDIO→BAIXO) | ferramentas/lote1_bancos.py:23 | Valuation de bancos/utilities repousa em StatusInvest (nota C) sem cruzamento com a CVM | s4_vpa: ITUB4 19,75 contra 18,87 implícito; ISAE4 31,51 contra CVM 33,63 | Bancos CARA com folga; fonte declarada no docstring | Conferir PL/ações no ITR; rotular nota C | M |
| AUD-75 | D3 | BAIXO (MÉDIO→BAIXO) | ferramentas/montar_series.py:46 | Proventos da StatusInvest: lacuna vira 0, Amortização e Rendimento entram no DPA, SBSP3 com payout 2–11% | t4/s2_amort: KEPL3 Amortização 1,53 (2021); SBSP3 central 7,05 igual com dpa_medio_5a 0,417 a 2,0 | Só DY/Bogle/teto informativos | Filtrar tipos; ausência = sem dado | M |
| AUD-76 | D3 | BAIXO (MÉDIO→BAIXO) | ferramentas/coletar_cvm.py:292 | Anos e datas literais (2025/2026, 2T26, range(2016, 2026)) espalhados; rolagem anual manual e silenciosa | grep -c: 6/3/9/4/6/5; PRIO3 ações +1,5% | Sem efeito hoje | Derivar ano base do último DFP | M |
| AUD-77 | D3 | BAIXO | 03-hall-de-acoes.md:58 | Flag (S) ausente na linha do GGBR4: preço 26,10 acima da saída 25,93 | cmp_hall3: DIVERGE GGBR4 esperado S=True escrito=False | Só relevante com posição | Acrescentar (S) ou gerar automaticamente | P |
| AUD-78 | D3/D4 | BAIXO (MÉDIO→BAIXO) | ferramentas/lote1_bancos.py:14 | rf e π são literais digitados (3 arquivos), sem coletor nem teste contra mercado.json; monitor não declara a data da taxa | sens_mercado: 39 de 40 centrais variam > 5% com a taxa de 06/10; ISAE4 e SUZB3 CARA→JUSTA | Snapshot deliberado e rotulado; ausência de aviso de idade | Ler rf/π de arquivo único; imprimir data da taxa | M |
| AUD-79 | D3/D6 | BAIXO (MÉDIO→BAIXO) | ferramentas/backtest/config.py:86 | regra_contaminacao e contaminacao_tolerancia (config) sem nenhum consumidor; flag de reapresentação nunca usada | grep: só config.py:86-87 | Backtest parado; sem efeito | Implementar a regra ou remover os parâmetros | P |
| AUD-80 | D3/D6 | BAIXO (MÉDIO→BAIXO) | ferramentas/backtest/config.py:90 | Calibração (até 2020) e validação (2021-25) se sobrepõem pelos horizontes de 1/3/5 anos; sem embargo | grep embargo/purg: 0 | Latente (nada calibrado ainda) | Embargo de 5 anos e bootstrap em blocos | P |
| AUD-81 | D3/D9 | BAIXO (MÉDIO→BAIXO) | ferramentas/lote5_petroleo.py:36 | PTAX (SGS 3698) e 9 séries FRED versionadas sem coletor nem data de coleta | grep de URLs: só leitores | Execução reproduzível; atualização/auditoria sem comando | coletar_macro_fred.py com checagem de sobreposição | M |
| AUD-82 | D3/D9 | BAIXO (PARCIAL) | ferramentas/registro_prospectivo.py:55 | Registro deriva preço de pc×central arredondados e grava None para RECV3 (preço real 11,20 existe) | preco None: [(RECV3, None, NÃO CONCLUSIVO)] | RECV3 fora do cálculo de retorno | Gravar Empresa.preco real | P |
| AUD-83 | D4 | BAIXO (MÉDIO→BAIXO) | ferramentas/monitor_semanal.py:220 | monitor/historico.csv acumula linhas duplicadas (append sem chave) | 123 linhas: 82 + 41; ABCB4 28,82 duas vezes | Sem leitor ainda | Upsert por (rodada, pregão, ticker) | P |
| AUD-84 | D4 | BAIXO (PARCIAL) | ferramentas/atualizar_hall_lote4.py:129 | atualizar_hall, gerar_pdf e triagem/rodar sobrescrevem arquivo vigente sem copiar o anterior para o histórico (inviolável 4) | grep write_text/SAIDA; nenhuma referência a _historico | Git protege só o commitado | Copiar para _historico antes de gravar | P |
| AUD-85 | D4 | BAIXO (MÉDIO→BAIXO) | ferramentas/motor_nao_financeiras.py:214 | lru_cache de idade_e_fator obsoleto se avaliar antes de temporada.injetar no mesmo processo | c.py: depois de injetar (cache) (10,976; 1,7561); sem cache (15,0; 2,2873) | Nenhum fluxo atual ativa | cache_clear em injetar | P |
| AUD-86 | D4 | BAIXO (MÉDIO→BAIXO) | ferramentas/coletar_cvm.py:313 | Coletor engole exceções (except Exception: pass no SMTO3), omite campos do LTM com componente None; motor trata ausente como 0 | leitura L313, L317-326; ltm_utilizavel barra erro total | Latente para o 3T26 | Checagem de completude do LTM | M |
| AUD-87 | D4 | BAIXO | ferramentas/lote5_petroleo.py:42 | read_text() sem encoding em 6 chamadas (macro) | JSONs ASCII hoje | Nenhum | encoding="utf-8" | P |
| AUD-88 | D5 | BAIXO (MÉDIO→BAIXO) | ferramentas/tests/test_regressao.py:36 | Palavra da régua (0,70/0,90/1,10) sem teste de borda no motor da mesa; docstring promete coerência P/C×palavra que não é checada | M01 (<=1,10→<1,10) e M02 (0,70→0,75) sobrevivem | Palavra dos 41 segue no golden | Teste parametrizado nas bordas | P |
| AUD-89 | D5 | BAIXO (MÉDIO→BAIXO) | ferramentas/backtest/tests/test_pit_nao_vaza.py:36 | Os 16 testes do portão PIT são pulados em silêncio (saída 0) sem o parquet; 25 pulados nos 4 arquivos | checkout limpo: 148 passed, 25 skipped | "Verde" pode ser "não executado" | Exigir dado por variável de ambiente | P |
| AUD-90 | D5 | BAIXO | ferramentas/motor_nao_financeiras.py:30 | LIMIAR_ORIGEM (0,15→0,10) e LIMITE_QUEBRA (0,25→0,40) sobrevivem a tudo; JANELA_MINIMA_SAIDA e MINIMO_ANOS_ALIQUOTA só a unitária pega | mutacoes_E.log N1–N4 | Nenhum ticker muda hoje | Testes nas bordas | P |
| AUD-91 | D5 | BAIXO (PARCIAL) | ferramentas/backtest/tests/test_reduzido.py:57 | Sem teste de paridade entre o motor reduzido (backtest/triagem) e motor_nao_financeiras da mesa; só funções financeiras (cópia de fonte) | mutacoes_bt.log: M01–M13, M15, M16 sobrevivem; M14 morre | Efeito só se backtest/triagem forem recalibrados | Paridade com entradas sintéticas | M |
| AUD-92 | D6 | BAIXO (ALTO→BAIXO) | 09-diario-de-decisoes.md:14 | Vender RANI3 e manter ISAE4 estão a ~12% de uma premissa da inversão; gatilhos do diário mais frouxos que o ponto de virada | v2.py: margens ×1,12 → RANI3 P/C 1,277; só mediana ×1,12 → 1,401; ISAE4 ROE lp ×0,92 → 1,312 | Diário já prevê revisão extra se central mudar > 15%; ITSA4/ABCB4 robustos | Registrar o ponto de virada em cada decisão | P |
| AUD-93 | D6 | BAIXO (MÉDIO→BAIXO) | ferramentas/gerar_pdf_lote3.py:192 | Quadro "Ke ±1 p.p." mostra R$ sem palavra e sem choque de rf; vários tickers viram com < 1 p.p. de rf (SMTO3 +0,7, EGIE3 +0,4, KEPL3, PETR4 +0,8) | s2/s3/s7 | Lacuna de comunicação; nenhuma palavra errada hoje | Palavra por célula e choque de rf | M |
| AUD-94 | D6 | BAIXO (MÉDIO→BAIXO) | ferramentas/motor_nao_financeiras.py:586 | Central de KLBN11, SLCE3, SUZB3, RANI3, VBBR3, UGPA3 é resíduo de EV menos dívida: 1 p.p. move 20–60%; ficha imprime centavos | s4/s6b: KLBN11 pc(+1 p.p.) 10,46; rf +0,4 p.p. → NÃO CONCLUSIVO | Falsa precisão; "sem compra" é robusto | Mostrar faixa e alerta DL/EV > 0,4 | P |
| AUD-95 | D6 | BAIXO (MÉDIO→BAIXO) | ferramentas/lote6_quimica.py:157 | EGIE3 JUSTA (1,067) a 3% da fronteira CARA: depende de ROE lp com dinheiro novo ao Ke, teto de g e payout | s5: ROE lp −0,6 p.p. / rf +0,4 p.p. / prêmio +8% → CARA | Premissas deliberadas; sensibilidade prometida não localizada | Mostrar faixa de ROE lp | P |
| AUD-96 | D6 | BAIXO (PARCIAL) | ferramentas/motor_nao_financeiras.py:819 | "Ke ±1 p.p." tem dois significados (financeiras movem rf; não financeiras só o Ke do acionista, Kd fixo) | motor_fin:380 contra motor_nf:819 | Só rótulo; efeito comparável, exceto SMTO3 | Rotular "prêmio" e "rf" | P |
| AUD-97 | D6 | BAIXO (MÉDIO→BAIXO) | ferramentas/backtest/experimento/proxy.py:1 | Portão do proxy mediu reprodutibilidade, não validade; "sempre CARA" passa o critério de palavra; limiar 0,15 = 8,6% do P/C mediano | a_portao: 23 exatas, 29 a ±1 nível (70,73%), mediana do erro absoluto de P/C 0,3401; sempre CARA 34/38; Spearman 0,677 | Parada foi decisão registrada; critério fraco já admitido | Se retomar: baseline trivial e métrica em log | P |
| AUD-98 | D6 | BAIXO (MÉDIO→BAIXO) | ferramentas/registro_prospectivo.py:28 | Ibovespa como comparador é enviesado a favor do hall (+7,2 p.p. médio em 23 cortes retroativos); sem regra de delisting | d_poder: SD 6,2 p.p.; hall perde do Ibov em 2 de 23 | Pergunta primária é ordinal (interna ao hall) | Comparador primário = média do hall | P |
| AUD-99 | D6 | BAIXO (MÉDIO→BAIXO) | ferramentas/prospectivo/registro.jsonl:42 | Registro sem regra de qual linha vale por (ticker, rodada): HYPE3 3 linhas, LEVE3 2, CMIN3 2 com palavras diferentes; hall registrado 2 pregões depois do preço | b_registro: 47 linhas, 43 tickers; registrado_em 06/10 (41), 07/10 (5), 08/10 (1) | Documentado no diário; sem prova de retroatividade | Regra de uma linha por rodada; marcar retroativas | P |
| AUD-100 | D6 | BAIXO (MÉDIO→BAIXO) | ferramentas/tests/golden.json:1 | 34 de 41 CARA e 0 BARATA: o teste por palavra não discrimina; a informação está no P/C contínuo | P/C hall min 0,838 mediana 1,75 max 5,21 | Sem prova de viés sistemático | Usar IC de postos do P/C | P |
| AUD-101 | D6 | BAIXO (PARCIAL) | 01-doutrina-value-investing.md:169 | Cortes 0,90/1,10/1,30/1,50 sem estudo de sensibilidade; com central ±10%, 8 tickers trocam de palavra | ver-R8-02/s.py: EGIE3, ISAE4, KEPL3, LEVE3, PETR4, SMTO3, SUZB3, UNIP6 | Escolhas documentadas (D5 aberta) | Tabela de sensibilidade da palavra | P |
| AUD-102 | D6/D1 | BAIXO (MÉDIO→BAIXO) | ferramentas/registro_prospectivo.py:98 | Registro "append-only" é convenção: adulteração do passado passa; só colisão na mesma data é detectada | h_adulteracao: ABEV3 CARA→BARATA e 5 tickers apagados; data nova 2027-01-04 aceita com 41 linhas | Autor único; git só com adições | Hash encadeado ou teste contra HEAD | M |
| AUD-103 | D6/D3 | BAIXO | ferramentas/lote4_saude_telecom.py:152 | EGIE3 (roe_lp) e WEGE3 (g1) carregam constantes calculadas no import com o Mercado de 02/10 | s9 C: EGIE3 mercado 06/10 central 32,37 contra 31,37 refeito (+3,2%) | Sem troca de palavra | Calcular dentro de avaliar() | M |
| AUD-104 | D6/D5 | BAIXO (ALTO→BAIXO) | ferramentas/motor_financeiras.py:15 | "Zero compras" é função do prêmio de 5 p.p. sem validação: BARATA só com prêmio ≤ 2 p.p.; 23 palavras mudam entre prêmio 0 e 5 | s7/s13: prêmio 0%: BARATA 5; 2%: 1 (SMTO3); ±1 p.p. muda 2 a 6 tickers | Premissa deliberada e já declarada aberta (D5, diário 103) | Mostrar "palavra por prêmio" na ficha | M |
| AUD-105 | D7 | BAIXO | 01-doutrina-value-investing.md:286 | Contagens históricas de testes desatualizadas (76, 451; hoje 301+301) | grep | Nenhum | Prefixar com data | P |
| AUD-106 | D8/D10 | BAIXO (MÉDIO→BAIXO) | ferramentas/coletar_statusinvest.py:14 | User-Agent de navegador (Chrome/128) contra endpoint interno do StatusInvest, sem registro de termos de uso | git grep User-Agent; sem verify=False nem shell=True | Sem efeito em veredito; risco só no rumo SaaS | Documentar termos; trocar StatusInvest por CVM nas séries | M |
| AUD-107 | D9 | BAIXO (MÉDIO→BAIXO) | ferramentas/backtest/tests/test_pit_nao_vaza.py:168 | test_5 (sentinela PIT) cai por MemoryError (628 MiB) na suíte completa; isolado passa em 4m17s | pytest_backtest.log linha 98; reexecução isolada: 1 passed | Vermelho espúrio indistinguível de vazamento; test_5b passou | Máscara vetorizada/merge; marcar como pesado | M |
| AUD-108 | D9 | BAIXO (MÉDIO→BAIXO) | ferramentas/registro_prospectivo.py:115 | golden_sha depende de CRLF do working tree (autocrlf=true, sem .gitattributes): não corresponde a nenhum blob | sha.py: 12b9b74 LF 5b76f8ee… CRLF a451c0c2… (o gravado) | Perda de verificabilidade em outra máquina | Normalizar EOL antes do hash e -text no .gitattributes | P |
| AUD-109 | D9/D3 | BAIXO (MÉDIO→BAIXO) | ferramentas/temporada.py:50 | ZIPs da CVM (itr_2026) alimentam o golden fora do git e sem manifesto; temporada.baixar_itr sobrescreve | sha256 0e1ef742…; sem MANIFESTO em dados/cvm | Só reapresentação do ITR de junho mudaria; golden acusaria sem apontar a causa | MANIFESTO.json com sha256 e cópia datada | M |


### 2.1 Detalhe dos achados ALTO (nenhum CRÍTICO)

Em todos os cinco, revisor e verificador concordaram na severidade ALTO (sem divergência). Nenhum é CRÍTICO porque nenhuma palavra de compra ou venda muda hoje.

#### AUD-01 — receita de meio nominal (motor_nao_financeiras.py:384-387)

- **Descrição completa:** sem `receita_meio` explícita e sem `deflator`, a receita de meio é a média simples da receita nominal dos 3 últimos exercícios (2023-25) mais o LTM. O resultado é multiplicado pela margem e descontado ao WACC real, contra dívida líquida e capital de hoje. A doutrina (01-doutrina §11.1, linha 236) define o EPV com lucro "em R$ de hoje". O motor deflaciona nos ramos `deflator` (L363), E&P (receita_ep) e no Δreceita do capex (L179-181), mas não neste. As receitas de 2023/24/25 entram com 14,6%/9,8%/4,5% a menos que em R$ de agosto/2026 (DEFLATOR 1,1459/1,0980/1,0455). O NOPAT sai ~7,5% baixo e a alavancagem amplifica no patrimônio. Grep de "nominal" e "R$ de hoje" no diário e no PLANO só acha D9 e o ROIC por exercício: não há decisão deliberada.
- **Comando:** `cd ferramentas && PYTHONIOENCODING=utf-8 python <scratchpad>/auditoria/R3-motor-nf/expB_receita_real.py` (rodado pelo verificador; sem escrita no repo).
- **Saída literal (verificador):** `deflator LTM 1.0234 DEFLATOR 2023/24/25 [1.1459, 1.098, 1.0455]`; `SUZB3 46.27 49.74 7.5 | 37.12 -> 43.60 +17.4 | 1.19 -> 1.02 | CARA -> JUSTA <== MUDA PALAVRA`; `KLBN11 +48.5%`; `RANI3 +15.6%`; `SLCE3 +22.9%`; `HYPE3 +11.9%`; `TIMS3 +11.3%`; `VIVT3 +9.0%`; `LEVE3 +9.1% (JUSTA mantida, P/C 0.93)`; `SMTO3 +9.5% (RADAR mantido, 0.84->0.77)`; `B3SA3 +4.0%`; `ABEV3 +7.0%`; `WEGE3 +6.8%`; `KEPL3 +8.1%`. Só SUZB3 muda de palavra.
- **Outros locais:** motor_nao_financeiras.py:384-387 (ult/extra/rec); 01-doutrina:236; mesmo viés no Owner Earnings e no DPA (AUD-16). Tickers: SUZB3, KLBN11, RANI3, B3SA3, SMTO3, KEPL3, SLCE3, TIMS3, VIVT3, HYPE3, ABEV3, WEGE3, LEVE3.
- **Observação do verificador:** os extremos (KLBN11 +48,5%) vêm de central pequeno com alavancagem, não de erro maior na receita (que é ~7,5% em todos).

#### AUD-02 — dividendos a pagar da WEGE3 fora da dívida líquida (lote4_saude_telecom.py:193)

- **Descrição completa:** a doutrina v2.3 (§11.1 linha 236; diário linha 172 item 4) manda o provento a pagar já ex entrar na dívida líquida (campo `outros_passivos_financeiros`, motor:541 e :610). O diário registra que "só a CMIN3 usa". O ITR 2T26 da WEGE3 mostra Dividendos e JCP a Pagar R$ 2,469 bi no circulante e Dividendos a pagar R$ 3,464 bi no não circulante (total R$ 5,933 bi, R$ 1,41/ação; o extraordinário de dez/2025 em 3 parcelas até 2028 é a parte não corrente). O caixa de R$ 8,8 bi ainda guarda esse dinheiro: DL subestimada, equity superestimado. O lote 4 não preenche o campo e não há decisão registrada de excluir.
- **Comando:** `bpp_div.py | grep -n ividend; comparar_WEGE3.py | tail -15; grep -n outros_passivos_financeiros motor_nao_financeiras.py lote*.py; sed -n 193,196p lote4_saude_telecom.py`.
- **Saída literal:** `2.01.05.02.01 Dividendos e JCP a Pagar 2,468,860 ; 2.02.02.02.07 Dividendos a pagar 3,464,232 (R$ mil)`; `BASE ... central 11.918 P/C 4.317 CARA compra 8.34 saída 15.49`; `V1 dividendos a pagar na DL (§11.1 v2.3) DCF 9.212 EPV 9.280 OE 11.316 | central 9.280 P/C 5.544 CARA compra 6.50 saída 12.06`; o motor rodado com `outros_passivos_financeiros=5.933 bi` reproduz V1 (variação −22,1%, confere True).
- **Outros locais:** 01-doutrina §11.1 linha 236; 09-diario:172; motor:541,610. Outros tickers com provento declarado a pagar não foram varridos (ver seção 4).
- **Ressalva:** a parte corrente (R$ 2,47 bi) pode incluir JCP ainda sem data-com; conferir se o provento já está ex na data-base (preço de 02/10).

#### AUD-03 — margem de PETR4 mistura EBITDA pré-IFRS 16 com D&A pós (lote5_petroleo.py:117)

- **Descrição completa:** para E&P a margem é (EBITDA sem impairment, mediana de 10 anos) − D&A atual, sobre receita de meio (motor:369-371). A D&A atual (R$ 87,6 bi LTM, 16,3% da receita de meio) inclui a depreciação do direito de uso, mas o EBITDA de 2016-18 é anterior ao IFRS 16 e já carrega o aluguel como custo. Nos 3 anos o aluguel entra duas vezes e a margem sai subestimada (11,3%, 11,8%, 14,8%, as três menores). A doutrina §11.1 (linha 240) manda usar só 2019+ com IFRS 16, e TIMS3, VIVT3 e FLRY3 já o fazem. PETR4 usa 2016-25 sem `janela_razao`; a tensão com o §11.4 item 4 (10 anos obrigatório em cíclica) fica sem resolução escrita.
- **Comando:** `python <scratchpad>/auditoria/C4-recalc-PETR4/{evid_ifrs16,sens_PETR4,sens2_PETR4}.py`.
- **Saída literal:** `2018 arrendamento 0.7 divida total 326.9 | EBITDA/rec (ebit+da) 31.0% | D&A/rec 12.5%`; `2019 arrendamento 96.2 ... EBITDA/rec 46.4% | D&A/rec 19.4% | pagto arrend./rec 6.8%`; `2025 arrendamento 238.5 ... 46.2%`; `margens ordenadas: [(2017, 11.3), (2016, 11.8), (2018, 14.8), (2024, 25.1), (2019, 25.7), ...]`; `base EPV 57.28 DCF 51.78 Rep 34.33 | central 51.78 P/C 0.988 JUSTA`; `2016-18 + aluguel pago de 2019 somado: DCF 56.76 | central 56.76 P/C 0.901`; janela 2019-25: DCF 65,71, central 64,14, P/C 0,798, compra 44,90, saída 83,38.
- **Outros locais:** motor:369-371; doutrina linhas 240 e 272-273. A extensão às demais cíclicas foi **refutada** pelo verificador (elas usam EBIT): o defeito é só da PETR4.
- **Observação:** erro conservador; a palavra final segue JUSTA só porque a dispersão (1,91x) rebaixa um nível.

#### AUD-04 — VPA do ISAE4 sem o caixa do follow-on (lote2_energia.py:103)

- **Descrição completa:** `F('ISAE4')` pega vpa/lpa do StatusInvest: VPA 31,51 = PL controlador 22,159 bi (CVM, 2T26) ÷ 703,3 mi de ações (pós follow-on de jul/26: R$ 1,2 bi a R$ 27, ~6,7% de diluição, em fatos_lote2.json). O PL ainda não tem os R$ 1,2 bi e o denominador já tem as ações novas: VPA e ROE de partida subestimados. O §11.2 manda "patrimônio + caixa captado, dinheiro novo rendendo o Ke (VPL zero)", e `lote6_quimica.egie()` faz isso para o EGIE3. O texto do lote (lote2_textos.py:50) e o hall diagnosticam errado como "703 mi × 659 mi" e sugerem 659 mi, o que também erra.
- **Comando:** `python <scratchpad>/auditoria/R4-motor-fin-premissas/s13_followon.py` (e s3_cvm.py).
- **Saída literal:** `ISAE4 CVM 2T26: acoes 658,9 mi | PLctrl 22.159.430 | VPAcvm 33,63 VPAdig 31,51 (-6,3%)`; `ISAE4 atual: vpa 31.51 central 24.10 P/C 1.169 CARA`; `ISAE4 regra follow-on (PL+R$1,2bi)/703,3 mi: vpa 33.21 roe_lp 0.1681 roe_ini 0.1305 central 25.78 P/C 1.094 JUSTA`; `Com VPA 33,63 (659 mi): central 25.73, P/C 1.096 JUSTA`.
- **Outros locais:** lote2_textos.py:50; 03-hall (linha ISAE4); 09-diario:29 (pendência "conferir no RI", aberta desde 05/10); lote2_energia.py:87.
- **Ressalvas do verificador:** a pendência é conhecida e sinalizada (não é silenciosa); a palavra é frágil (a 0,006 da fronteira 1,10; com o preço do snapshot de 05/10, 30,17, o P/C volta a 1,170).

#### AUD-05 — repositório sem remoto (PLANO-DE-MELHORIAS-2026-10.md:60)

- **Descrição completa:** `git remote` vazio; objeto store com 594 objetos soltos e 0 packs (10,7 MiB). O PLANO decidiu "git init local (sem remoto)" como bootstrap, não como dispensa de backup. `prospectivo/registro.jsonl` e `triagem.jsonl` são "evidência, não cache" (docstring) e não se reconstroem. Os dados ignorados (ferramentas/dados 1,4 GB; backtest/dados 674 MB) também não têm cópia.
- **Comando:** `git remote -v; echo "remotes: $(git remote | wc -l)"; git count-objects -vH | head -5; du -sh ferramentas/dados ferramentas/backtest/dados`.
- **Saída literal:** `remotes: 0`; `count: 594`; `size: 10.69 MiB`; `in-pack: 0`; `packs: 0`; `1.4G ferramentas/dados`; `674M ferramentas/backtest/dados`.
- **Outros locais:** .gitignore:8; docstring de cotahist.py (~12 GB livres em C:). O verificador não checou backups fora do repo (OneDrive, disco externo). Não há dado pessoal no repo (inviolável 2 respeitado).
- **Observação:** severidade ALTO mantida pela irreversibilidade, no limite inferior da faixa.

## 3. Recálculo independente dos centrais (D2)

Para quatro tickers refiz o valor central do zero, sem importar o motor, a partir de fórmulas da doutrina/livro-texto e dos dados brutos (ZIPs da CVM, séries, mercado.json), e comparei com o motor e com `tests/golden.json`. Valores em R$/ação.

### 3.1 PETR4 (cíclica E&P: EPV de meio de ciclo, DCF de 3 cenários, valor de reprodução; desconto de controlador 8%)

| Item | Âncora/motor | Independente | Dif % | Causa da diferença |
|---|---|---|---|---|
| EPV de meio de ciclo (após desconto) | 57,279987 | 57,279412 | −0,001 | π digitado 6,46% contra 6,4593% recalculado da ETTJ |
| DCF normalizado (3 cenários) | 51,779491 | 51,778956 | −0,001 | idem; g efetivo 0 nos 3 cenários (ROIC < WACC 16,3%) |
| Valor de reprodução (PL − minoritários, após desconto) | 34,330295 | 34,330295 | 0 | idêntico |
| Valor central (mediana = DCF) | 51,779491 | 51,778956 | −0,001 | idem |
| Ke nominal (Fisher) | 0,192991 | 0,192983 | −0,004 | só π |
| WACC nominal | 0,16304 | 0,16303 | −0,004 | propagação de π |
| Barril de meio de ciclo (R$/bbl) | 405,697 | 405,697 | 0 | Brent FRED × PTAX BCB 3698 deflacionado |
| Margem EBITDA−D&A mediana | 0,27306 | 0,27306 | 0 | p25 14,82% e p75 32,25% também idênticos |
| Ke implícito | 0,19426 | 0,19425 | −0,005 | hall (03:36) ainda mostra 20,3% (AUD-69) |

- **Ke:** motor 0,192991, independente 0,192983. **Central:** 51,7795 contra 51,7790 (−0,001%). **Palavra:** JUSTA nos três (motor, independente, golden); P/C 0,98823; compra 36,25; saída 67,31; dispersão 1,67.
- **Conclusão:** o motor reproduz o central; todos os insumos conferem com a CVM bruta (diferença máxima absoluta 0 em receita, EBIT, LAIR, IR, D&A, capex, impairment, outras e arrendamento 2016-25, LTM e balanço de 30/06/26). As diferenças de método (não de conta) que deslocam o P/C para a fronteira RADAR são AUD-03 (IFRS 16), AUD-18 (reprodução) e AUD-07 (Kd); todas conservadoras. No sentido oposto, a hipótese de o juro do déficit atuarial estar fora do EBIT levaria a CARA (1,13; seção 4).
- **Scripts:** `scratchpad/auditoria/C4-recalc-PETR4/recalc_PETR4.py` (independente), `comparar_PETR4.py`; auxiliares sens_PETR4, sens2_PETR4, sens3_reproducao, sens4_kd, sens5_pi, sens6_capex, evid_ifrs16, evid_passivos.

### 3.2 SBSP3 (utility de saneamento: P/VP justificado + DDM 2 estágios)

| Item | Motor | Independente | Dif % | Causa |
|---|---|---|---|---|
| Ke real (rf 7,06% + 5 p.p.) | 0,1206 | 0,1206 | 0 | bate |
| Ke nominal (Fisher) | 0,192991 | 0,192983 | −0,004 | π 6,46% arredondado |
| g perpétuo (teto π + PIB real 2%) | 0,085892 | 0,085885 | −0,008 | idem |
| P/VP justificado | 7,073726 | 7,041605 | −0,454 | com premissas digitadas: 0,000%; a diferença vem de ROE lp CVM 14,443% (SI 14,5%) e VPA ex-tesouraria 12,882 (motor 12,817) |
| DDM 2 estágios | 7,028915 | 7,009961 | −0,270 | mesma causa; teste real × nominal §4: 0,0000% |
| Central (mediana) | 7,05132 | 7,025783 | −0,362 | soma das duas; compra 4,94 contra 4,92; saída 9,17 contra 9,13 |

- **Ke:** motor 0,192991, independente 0,192983. **Central e palavra:** CARA nos dois (P/C 4,0035 motor; 4,0181 independente; mesmas premissas: 4,0035). TIR real implícita 4,6550% nos dois.
- **Conclusão:** aritmética correta (0,000% com as mesmas premissas; golden idêntico). CARA é robusta (continua CARA em Ke de mercado 14%, ROE lp = ROE 12m, mercado de 06/10, RAB-paridade). O que não é robusto é o número: o central varia de R$ 4,09 a R$ 21,18 só com o ROE lp, e as duas âncoras não são independentes (AUD-44). Achados de método: AUD-20 (condição do §11.2 falsa), AUD-70 (PIB 2% e payout 25% sem fonte), AUD-06 (rf), AUD-72 (mercado de 02/10; com 06/10 o central subiria ~21,6%).
- **Scripts:** `scratchpad/auditoria/C2-recalc-SBSP3/` — `recalc_SBSP3.py` (independente), `comparar_SBSP3.py`, extras_SBSP3, verifica_preco_mercado, dfc_sbsp3, payout_2025.

### 3.3 ITUB4 (banco: P/VP justificado + DDM 2 estágios)

| Item | Motor | Independente | Dif % | Causa |
|---|---|---|---|---|
| P/VP justificado (VPA × 0,8599x) | 16,982287 | 16,982287 | 0 | fórmula de livro-texto, g = 7,032% (abaixo do teto 8,589%) |
| DDM 2 estágios (5 anos, ROE 21,5%→17,58%, terminal = VPA5 × P/VP just.) | 18,098095 | 18,098095 | 0 | VPA5 28,563; terminal 24,560 (56% do valor) |
| Central (mediana) | 17,540191 | 17,540191 | 0 | bate com o golden; P/C 2,556; compra 12,28; saída 22,80 |
| Ke nominal (Fisher) | 0,192991 | 0,192991 | 0 | (1+0,0706+0,05)×(1,0646)−1; Ke implícito 11,7847% nos dois |

- **Ke:** 0,192991 nos dois. **Central e palavra:** 17,5402 nos dois, CARA (P/C 2,556). Maior diferença entre as linhas: 0,000000%.
- **Conclusão:** motor correto; CARA só vira JUSTA no caso extremo combinado (Ke de mercado 14% e ROE lp = 21,5% perpétuo). Achados: AUD-17 (nenhum teste analítico), AUD-06/AUD-78 (convenção de rf e π), AUD-61/62/63 (premissas e comentários). Insumos (ROE lp 17,58%, VPA 19,75, ROE 12m 21,5%) são StatusInvest e conferem exatamente com a série baixada.
- **Scripts:** `scratchpad/auditoria/C1-recalc-ITUB4/recalc_ITUB4.py` (independente), `comparar_ITUB4.py`, hall_check, vpa_bancos, explora_fatos.

### 3.4 WEGE3 (perene: DCF 2 estágios em 3 cenários, EPV, Owner Earnings)

| Item | Motor | Independente | Dif % | Causa |
|---|---|---|---|---|
| DCF (3 cenários ponderado; pess 8,375 / base 10,694 / otim 17,909) | 11,917946 | 11,917946 | 0 | bate |
| EPV | 10,693816 | 10,693816 | 0 | bate |
| Owner Earnings ÷ (Ke − g) | 12,730406 | 12,730406 | 0 | OE normalizado R$ 5,374 bi |
| Central (mediana) | 11,917946 | 11,917946 | 0 | P/C 4,317; compra 8,34; saída 15,49 |

- **Ke:** 0,1206 (real) nos dois. **Central e palavra:** 11,92, CARA nos dois. Insumos: alíquota 16,47%, margem mediana 16,25%, ROIC 29,8% (reposição 18,4%), g1 real 6,874%, DL −2,966 bi, 4.195.830 mil ações.
- **Conclusão:** conta correta com diferença zero. A única divergência é de insumo: dividendos a pagar (R$ 5,933 bi) fora da DL (AUD-02; central 9,28 se incluídos). O restante são sensibilidades (AUD-14 degrau de crescimento; defasagem de 9 meses tem fonte).
- **Scripts:** `scratchpad/auditoria/C3-recalc-WEGE3/` — `recalc_WEGE3.py`, `comparar_WEGE3.py`, bpp_div, extrai_cvm; `scan_div_pagar.py` tem erro de escala e não deve ser usado.

### 3.5 Conclusão geral e causa das diferenças

As contas dos motores (Ke por Fisher, g, P/VP justificado, DDM, EPV, DCF, OE, régua, compra e saída) reproduzem por caminho independente com diferença de 0,000% a 0,36%. As poucas diferenças vêm de (a) π digitado com 4 casas (6,46%) contra o exato da ETTJ, (b) insumos que o recálculo refez direto da CVM em vez da StatusInvest. Os erros encontrados estão em insumos omitidos (AUD-02, AUD-04), unidades de fluxo (AUD-01, AUD-16) e escolhas de método (AUD-03, AUD-07, AUD-12, AUD-18), não na aritmética.

## 4. Suspeitas não confirmadas

Nenhum achado foi rebaixado a suspeita na verificação (0 rebaixados). Abaixo: (a) os 4 candidatos refutados e (b) as 79 hipóteses dos revisores que ficaram sem prova, agrupadas por dimensão, com o que faltaria para confirmar. Não são achados.

### 4.1 Candidatos refutados na verificação (4)

- **R9-05** (NÃO CONCLUSIVO por dispersão > 3 como "gatilho de faca" em UNIP6 3,04 e SLCE3 2,91): regra explícita na doutrina §9 e implementada como escrita; descontinuidade é inerente a faixa. Voto dos verificadores: refutado.
- **R4-07** (P/C de 4 a 5 em CPLE3, CSMG3, SBSP3 como saturação de ROE < Ke): o próprio achado reconhece método autorizado (§11.2) e bem aplicado; só risco de leitura.
- **R6-09** (coletar_cvm com plano industrial devolvendo "2.03" errado para banco): premissa falsa no código atual; a triagem usa o ledger PIT com plano financeiro separado; risco puramente hipotético.
- **R5-04** ("só com re-rating" omitiria LEVE3): LEVE3 é "Não" em vence_rf, então está corretamente fora da lista.

### 4.2 Rebaixadas na verificação

Nenhuma. Todos os 113 verificados saíram como CONFIRMADO ou PARCIAL (com severidade e descrição corrigidas, ver tabela); 4 foram refutados.

### 4.3 Hipóteses dos revisores (79), por dimensão

**D1 — doutrina e régua**
- Hall inteiro em mercado de 02/10 enquanto existe o de 06/10 (viraria 2 palavras): falta decidir a periodicidade de reexecução (relacionado a AUD-72/78).
- Defasagem do provento não entra nas âncoras DDM de financeiras/utilities (§6.3): falta confirmar com o Frank se vale para o DDM e medir ~5–10%.
- Kd em reais aplicado a dívida em dólar (SUZB3, KLBN11, PETR4, PRIO3): falta a composição da dívida por moeda nas notas dos DFP.
- "Yield sustentável" usa OE como proxy do FCFE e DPA nominal médio: falta o FCFE real por ticker.
- Degraus de dispersão (SLCE3 2,91, UNIP6 3,04) a ~3% do corte: decidir se a ficha mostra a distância ao corte.
- Círculo de competência nunca aplicado (fora_circulo=False nos 41; não há lista de tickers dentro/fora): falta entrada no 07/09.
- "Valor de reprodução" das 11 cíclicas parece livro e decide a mediana: faltam fórmula por lote e sensibilidade excluindo a âncora.
- Teste de quebra estrutural (§11.4) quase vazio em janelas curtas e compara faixas sobrepostas: decidir comparar 5 últimos contra anteriores.
- Dois centrais de LEVE3 coexistem (33,99 golden; 35,75 dossiê de 08/10): decidir qual é a referência operacional.
- Qualidade da exceção 1,50× é "arbitrada, pré-v4" em 20 de 21: faltam os dossiês de ABEV3 e B3SA3.

**D2 — cálculo e premissas**
- Atuarial de PETR4 dentro do EBIT? Saldos conferem (R$ 92,45 bi) e o DFC traz R$ 9,744 bi de resultado atuarial; falta a nota de benefícios pós-emprego da DFP 2025 (fonte A). Se o juro estiver fora do EBIT, PETR4 vira CARA (1,13).
- Abandono (R$ 153,7 bi) fora da ponte: falta cronograma de desembolso do descomissionamento.
- Pesos de cenário de controlador (50/35/15) anteriores ao 1º turno de 04/10: falta o resultado e nova estimativa.
- Preço de PETR4 R$ 51,17 vem de agregador; StatusInvest 05/10 = 54,40 (P/C 1,05): falta fechamento B3 da data de uso.
- Capex de manutenção de E&P pela mediana de 10 anos (12,2%) contra capex LTM 20,3%: central 40,10 (CARA) se tudo fosse manutenção; faltam dados de manutenção × expansão.
- cria/reinv com ROIC contra WACC em convenções diferentes (experimento parcial inconclusivo): falta variante coerente e decisão do Frank.
- Capex de manutenção usa Δreceita de 1 ano quando falta base de 5 (TIMS3, FLRY3): falta rodar ano a ano.
- Passivos de desmobilização e atuarial de PETR4/PRIO3 fora da ponte: ler as notas da DFP 2025.
- Caixa da B3SA3 pode incluir ativos de garantia de câmara: abrir a nota de caixa do ITR 2T26.
- OE ÷ (Ke − g) usa g real sem trava de ROIC: rodar com g=0 onde cria é falso.
- Kd nominal sobre fluxo real em lair_norm/lucro_norm e caixa líquido remunerado a Kd (ABEV3): rodar com kd real e rf no caixa.
- Docstring de idade_media diz que subestimar a idade é conservador; sinal parece invertido: refazer ROIC de reposição só com D&A do imobilizado.
- Preços do motor (02/10) divergem do snapshot de 05/10 em até 11%: confirmar com o Frank que é deliberado.
- Sem guarda explícita Ke > g em pvp_justificado/ddm_contrato_finito: rodar com rf_real = −3,01% e g no teto.
- VPA de BBDC4 (17,11) e ABCB4 (27,85) possivelmente pré-diluição: PL e ações do CVM/RI.
- roe_inicio de SBSP3 (17,8%) vem de LTM com possível ganho não recorrente: decompor o lucro 2024–26.
- DPA_CVM do ISAE4 2024 (1,88) preenche lacuna do SI por base caixa: conferir a data-com.
- Fragilidade do central de RECV3 (±20% no ajuste leva a +3,55/−3,86): conferir a mediana de capex/receita e capex_expansao.
- HYPE3 com g_real −0,5% cai 27% enquanto PETR4/KLBN11 sobem: decompor os cenários.
- Payout digitado diverge da mediana DPA/LPA em 4 de 10 financeiros (ITUB4 0,60 contra 0,37; BBSE3 0,90 contra 0,63): conferir no RI.
- Teto de g (π + PIB real) morde em 7 financeiras e torna o payout irrelevante no P/VP justificado: decidir se o teto corta ROE ou aumenta payout.
- 20 de 40 tickers com prêmio implícito sobre a NTN-B ≤ 0 (ITUB4 Ke implícito real 5,0%; CPLE3 0,8%): sintoma de calibração; só a validação prospectiva ou o backtest resolve.
- As duas âncoras do banco não são independentes (ITUB4: ROE lp 17,58%→21,5% leva o central de 17,54 a 23,81): decidir 3ª âncora ou sensibilidade.
- ROE lp nominal 2016-25 contra Ke com π 6,46% (regime diferente): comparar ROE real com Ke real.
- Centrais fixados com rf/π de 02/10 contra preços novos no monitor (ITUB4 +13,4% com mercado 06/10): rodar nos 41 e listar quem cruza.
- VPA de ITUB4 19,75 contra 19,5 (fatos_B) e 18,87 implícito: PL e ações do ITR 2T26.
- Varredura de dividendos a pagar nos demais tickers (ABEV3, HYPE3, VIVT3) não feita (script com erro de escala): somar 2.01.05.02.01 e 2.02.02.02.07 do ITR por ticker.
- Data-base de 02/10 contra mercado de 06/10 muda o central de WEGE3 em +13% (DCF +27%): documentar a sensibilidade.
- DCF de WEGE3 muito dependente do g1 de 6,87% real (sem ele, 10,76; −9,7%): conferir pesos dos cenários.
- ROE lp de SBSP3 (14,5%, metade da era estatal) decide a TIR "abaixo do Tesouro": ROE regulatório permitido (Arsesp) e teste de quebra para financeiras/utilities.
- Possível follow-on ou emissão de SBSP3 posterior ao balanço: fato relevante de jul–out/2026.
- RAB R$ 70–79 bi vem de PDF de 03/10 (nota C): base regulatória oficial da Arsesp.
- Beneish: except (ZeroDivisionError, TypeError) devolve None em silêncio: rodar com receita 0.

**D3 — dados e coletores**
- coletar_cvm engole exceções e grava {'erro': ...}: provocar falha controlada numa cópia.
- acoes_jun26 usa .iloc[-1] em vez da maior VERSAO: achar ticker com duas versões no composicao_capital.
- IPCA "médio do ano" de 2026 é parcial (8 meses) e SMTO3 usa exercício abr/25–mar/26 rotulado 2026: medir o efeito no central.
- Páginas da StatusInvest raspadas por regex de HTML: descobrir quem consome vpa_implicito/n_acoes_implicito.
- ISAE4: ações CVM 9% abaixo da implícita da StatusInvest (possível bonificação de 10%): fato relevante/FRE.
- SBSP3: LPA anual não ajustado ao desdobramento enquanto o DPA aparenta estar: DPA 2021–25 em fonte A.
- Efeito do LTM reapresentado no veredito não demonstrado (variáveis fixadas no import não refeitas): reavaliar numa cópia com o JSON corrigido.
- Consolidado × individual: `buscar` cai para o individual sem marcar no JSON: registrar con/ind e listar quem usou "ind".
- VERSAO tratada como texto (max('9','10') = '9'): máximo hoje é 5; checar arquivos 2010–2015.
- Hall × PDFs: TIR real das utilities no hall contra o motor diverge 5–9 p.p. (provável mapeamento de campo errado no script do revisor): identificar o campo exato.
- Textos fixos de lote*_textos.py com números digitados envelhecem (caso HYPE3/LEVE3): varredura sistemática de números contra o motor.
- DOSSIES/*.md e BOLETINS/*.md não conferidos linha a linha: comparar com o golden na data-base.
- PDF do Lote 1 (rev. 04/10): central/compra/saída corretos; nada crítico.
- DT_RECEB com defasagem extrema (318 de 14.008; 83 versões originais > 400 dias): cruzar com o ITR/DFP seguinte.
- Ajustes retroativos de eventos (última versão do FRE vence; suplemento B3 baixado em 2026): comparar fatores de versão antiga e nova.
- Contagem de ações do FRE usa data de aprovação, não efetivação (concordância 86,7% geral, 93,2% acima do piso): medir o impacto no P/C.
- Triagem/monitor herdam o ledger? (em T=hoje não há contaminação): grep de imports de backtest.* em triagem/ e monitor.
- Fila da triagem usa Q1 com o WACC de hoje contra 10 anos de ROIC passado: recalcular com WACC histórico.

**D4/D5 — engenharia e testes**
- Falha transitória de coleta do pytest durante a mutação M06 (provável harness concorrente): reproduzir com saída completa.
- test_dossie_fichas só aplicado a 4 mutações: rodar contra B01, B04, M02, N1, N3.
- Pico real do test_5 em 2022-06-30 não medido (estimativa 5–7 GB): rodar isolado com ≥ 10 GB livres.
- Fixtures do FRE: cabeçalho conferido em 3 de 7 tabelas: comparar as 4 restantes.
- Arquivos de teste lidos só por nome/docstring (test_triagem_regras, test_isolamento, test_cotahist, test_indice_cvm, test_perfil, test_proxy, test_notas, test_registro_prospectivo): mutação dirigida na triagem e no registro.
- Duplicação de motor entre ferramentas/motor_* e backtest/motor (triagem): comparar funções homólogas nos 41.
- Teste de código morto inconclusivo (AST restrito): repetir incluindo gerar_pdf/atualizar_hall.

**D6 — estatística e método**
- Aprovação da métrica de retorno do registro depende de retorno.py, sem avaliador prospectivo no repo: executar quando existir.
- Triagem: triagem.jsonl (20 linhas) sem poder nem grupo de controle: ler o diário 113–135 e calcular o poder.
- proxy.py, reduzido*.py e testes do backtest não lidos linha a linha (70,7%/0,34 reproduzidos a partir do JSON): rodar test_proxy.
- Teste de adulteração do registro: ler tests/test_registro_prospectivo.py.

**D7/D9/D10 — documentação, operação e SaaS**
- monitor: ultimos_precos pega o último registro sem exigir que seja do pregão (latente; hoje os 41 negociaram em 06/10).
- coletar_cvm.py e temporada.py baixam sem retentativa: simular falha na cópia.
- Carteira e avaliações enviadas a serviço de terceiros no fluxo Desktop (dado financeiro pessoal, não de saúde): decisão explícita do Frank sobre o que sai da máquina.
- Pre-commit/CI e ambiente reproduzível: o caminho C:\Python314 está gravado na tarefa agendada; testar reinstalação.
- Heurística de LGPD do FRE decide "pessoa física" por lista de termos de PJ (nomes como "Carlos Eduardo Brasil" saem como PJ, em claro): rodar a lista dos 163 e conferir os dossiês; trata-se de administradores de companhia aberta (dado público).
- Distribuição degenerada de vereditos (34 de 41 CARA): comparar Ke da casa (12,06% real) com retorno histórico da B3 e rodar a régua em outras datas.

## 5. Pontos fortes

O que está bem feito e deve ser preservado:

- **Contas reprodutíveis.** Recálculo independente de PETR4, SBSP3, ITUB4 e WEGE3 com diferença de 0,000% a 0,36%; Fisher exato em toda a ponte real/nominal; teste do §4 (fluxo nominal ao Ke nominal = fluxo deflacionado ao Ke real) fecha em 0,0000%. Todos os insumos de PETR4 reproduzem da CVM bruta com diferença zero; o barril de meio de ciclo (R$ 405,697) bate em 6 dígitos.
- **Golden e regressão.** 41 tickers com palavra exata, âncoras, notas e log de motivos (`golden_log.md`); regravação exige `--motivo`; `rodar_tudo` sai com código 1 se houver diff e reproduziu "sem mudanças"; `test_regressao` confere central = mediana das âncoras. Matou 14 das 16 mutações de motor testadas.
- **Guarda-corpos do motor.** `exigir_declaracoes` derruba janela curta sem razão, defasagem sem fonte, controlador discricionário sem fonte, alíquota por fase mal formada, passivos e capex de expansão sem fonte; `descontar()` não melhora âncora ≤ 0; NÃO CONCLUSIVO sai das regras escritas; benefício fiscal com prazo evita crédito duplo.
- **Régua e precedência fiéis ao §9**, em três cópias que concordam (diferencial de 144 combinações: 0 divergências); `precos_de_referencia` é fonte única; exceção de saída 1,50× implementada como escrita e excluindo financeiras.
- **Dados.** Preços digitados batem com o COTAHIST de 02/10 em 37 de 41 tickers; ROE lp, pl_hist e VPA de ITUB4 e de 6 de 8 utilities amarrados à série/CVM; `cvm_series.json` reproduz idêntico a partir dos ZIPs (SUZB3, PETR4, CMIG4, TIMS3, WEGE3); seleção de contas por CD_CONTA com versão máxima, conversão de escala e fallback documentado; ações do Lote 3/5 diferem ≤ 1,5% do ITR de jun/26.
- **Hall × golden.** Zero divergências de central, P/C, palavra, preço, compra e saída em 36 tickers; Greenblatt idêntico; os PDFs recalculam do motor (37 de 41 com valores atuais); as 7 cópias do UPLOAD não defasadas são byte a byte idênticas aos originais.
- **Coleta e macro.** `coletar_macro` só grava se a sobreposição com a série antiga conferir; `cotahist.ler_ano` falha alto e o monitor troca o ZIP de forma atômica com devolução do anterior; correções de dados de terceiros (ABEV3, EGIE3, VIVT3, GGBR4/UNIP6) são estreitas, documentadas e autodesativáveis.
- **Registro prospectivo.** Append-only com chave (origem, data_preco, ticker), recusa de valor divergente na mesma data, sha do golden e doutrina em cada linha, 5 commits só de adições; triagem com registro análogo e CSV completo versionado como grupo de controle.
- **Backtest/PIT.** Disponibilidade por DT_RECEB observado, IPCA point-in-time com erro em vez de silêncio, contagem de ações com dupla filtragem por data, preço do sinal nominal separado do ajuste de resultado, universo sem sobrevivência na camada de preços; sentinela PIT com meta-teste (test_5b) e história honesta no docstring; portão do proxy declarado antes de medir, com baselines impressos e parada aceita sem recalibrar.
- **Honestidade metodológica.** Diário registra o portão, aceita a falha e declara que prêmio de 5 p.p. e margem de 30% seguem sem validação; autocrítica explícita nos textos de lote (SBSP3, PETR4).
- **Robustez das conclusões.** 21 de 41 palavras não mudam em nenhuma perturbação simples; 16 seguem CARA mesmo com prêmio 0; vender ITSA4 e ABCB4 é robusto; mercado real de 02 a 06/10 mudou só 2 palavras; sem exceções em 20.368 avaliações de sensibilidade e sem anomalias de monotonia.
- **Operação e higiene.** Monitor agendado via VBS oculto com `-StartWhenAvailable`; testes de monitor, registro e temporada usam tmp_path/monkeypatch; sem `verify=False`, sem `shell=True`, subprocess com lista de argumentos, timeouts nas chamadas `requests`; sem segredo nem CPF na árvore nem no `git log -p`; anonimização LGPD do FRE em duas camadas com teste; mercado sem arquivo falha alto em `dossie/base`.
- **Organização.** Dados derivados pequenos no git e brutos grandes ignorados com regra explícita; dados `mercado_*.json` com URL, data e nota A; testes com conta escrita à mão onde existem (fator de preço, motor reduzido); suíte rápida de 94 s.

## 6. Roteiro de correção em ondas

Proposta, sem execução. Qualquer mudança que mexa em central ou palavra exige regravar o golden com `--motivo`, rodar `adversario` antes do commit (regra do Frank) e, para afirmações de fonte, `verificador-fonte`.

### Onda 1 — o que pode errar o veredito hoje

1. **Unidades e insumos que movem o central:** AUD-01 (receita de meio em R$ de hoje) e AUD-16 (OE e DPA deflacionados); AUD-02 (dividendos a pagar da WEGE3; depois varrer os demais, ver seção 4); AUD-04 (follow-on do ISAE4 e o texto do lote); AUD-03 (janela IFRS 16 da PETR4).
2. **Convenções de mercado e custo de capital:** AUD-06 (rf fechamento), AUD-78 (rf e π lidos de um arquivo, com data), AUD-72 (idade do preço), AUD-07 (Kd com fonte), AUD-12 e AUD-13 (decidir e registrar o Ke fixo e o peso a preço de mercado), AUD-09 (alíquota da ABEV3), AUD-18 (fórmula da reprodução), AUD-08 (trava de coerência da LEVE3).
3. **Decisão e gatilhos:** AUD-43 (monitor ignora a palavra final), AUD-37 (monitor sem alerta de falha), AUD-33 (corte da triagem), AUD-67 e AUD-77 (preço/flag do hall), AUD-20 (condição do §11.2 na Sabesp).
4. **Documentos que levam a decisão errada:** AUD-19, AUD-35, AUD-36, AUD-69.

### Onda 2 — reprodutibilidade e testes que escondem erro

1. **Fazer primeiro (esforço pequeno): AUD-05** (backup do repositório e dos dados).
2. **Reprodutibilidade:** AUD-38 e AUD-73 (requirements, bootstrap, import tolerante), AUD-109 (manifesto sha256 dos ZIPs), AUD-108 (EOL do golden_sha), AUD-102 (integridade do registro), AUD-82 (preço real no registro), AUD-24 (series vigente), AUD-26 e AUD-86 (estado compartilhado e coletor), AUD-21, AUD-22 e AUD-23 (LTM e proventos), AUD-81 (coletor FRED e PTAX), AUD-83 (histórico do monitor), AUD-84 (histórico antes de sobrescrever).
3. **Testes que não distinguem certo de errado:** AUD-17, AUD-27, AUD-28, AUD-30, AUD-31 (fórmulas, limiares, NaN, ROIC real), AUD-88 e AUD-90 (bordas), AUD-29 e AUD-107 (sentinela PIT), AUD-89 (skip silencioso), AUD-91 (paridade do motor reduzido).

### Onda 3 — riscos latentes

- **Motor:** AUD-10, AUD-11, AUD-14, AUD-15, AUD-34, AUD-39, AUD-47, AUD-50, AUD-51, AUD-52, AUD-53, AUD-54, AUD-55, AUD-56, AUD-59, AUD-63, AUD-66, AUD-85, AUD-103, AUD-25.
- **Dados e premissas:** AUD-58, AUD-61, AUD-62, AUD-68, AUD-70, AUD-71, AUD-74, AUD-75, AUD-76.
- **Método e estatística:** AUD-32, AUD-92, AUD-93, AUD-94, AUD-95, AUD-97, AUD-98, AUD-99, AUD-100, AUD-101, AUD-104, AUD-79, AUD-80.
- **Doutrina e régua:** AUD-40, AUD-41, AUD-42, AUD-44, AUD-45, AUD-46.

### Onda 4 — qualidade e rumo SaaS

AUD-49 (config da carteira, lock, requirements), AUD-106 (termos de uso das fontes), AUD-96 (rótulos), AUD-57 e AUD-60 (premissas provisórias e sensibilidade), AUD-64 e AUD-65 (fichas), AUD-48 e AUD-105 (textos de documentação), AUD-87 (encoding).

## 7. Métricas da auditoria

| Métrica | Valor |
|---|---|
| Arquivos lidos (únicos) | 276 |
| Candidatos brutos | 147 |
| Duplicatas absorvidas | 34 |
| Verificados | 113 |
| Confirmados | 109 (CRÍTICO 0 · ALTO 5 · MÉDIO 33 · BAIXO 71) |
| Rebaixados a suspeita | 0 |
| Refutados (descartados) | 4 |
| Taxa de descarte (refutados / verificados) | 3,5% (4 de 113) |
| Taxa de não confirmação ((refutados + rebaixados) / verificados) | 3,5% |
| Suspeitas dos revisores sem prova | 79 (seção 4) |
| Agentes que falharam | nenhum |

Observação: muitos "confirmados" foram PARCIAIS na verificação (fato reproduzido, descrição ou severidade corrigida). Nove achados caíram de ALTO para MÉDIO (AUD-06, 07, 12, 18, 19, 25, 32, 37, 38), dois de ALTO para BAIXO (AUD-92, 104) e dezenas de MÉDIO para BAIXO; as colunas de severidade da seção 2 já trazem o valor final.

### Testes rodados (números reais da base)

- `cd ferramentas && python -m pytest --ignore=backtest -q` → **301 passed em 94 s** (Python 3.14.0).
- `cd ferramentas && python -m pytest backtest -q` (sozinho) → **300 passed, 1 failed em 971,6 s (16 min)**: `backtest/tests/test_pit_nao_vaza.py::test_5_sentinela_truncar_as_fontes_em_T_nao_muda_a_selecao` caiu com `numpy MemoryError: Unable to allocate 628. MiB for an array with shape (11, 7483140) and data type object` (linha 168). Isolado, o mesmo teste passa (1 passed em 4m17s); ver AUD-107.
- `cd ferramentas && python rodar_tudo.py` → "41 tickers · CARA 34 · JUSTA 4 · NÃO CONCLUSIVO 2 · RADAR 1" e "sem mudanças em relação ao golden." (21 s, saída 0).
- `git status` limpo depois de tudo. Sem requirements.txt nem pyproject.toml. 300 arquivos versionados; ~19,7 mil linhas de Python em ferramentas/ (162 arquivos).
- Em cópia de HEAD sem os dados ignorados: `rodar_tudo.py` dá FileNotFoundError e o pytest aborta na coleta (AUD-38). Mutações aplicadas só em cópia: 30 (R11), com placar de sobreviventes nos AUD-27, 28, 31, 88, 90.

### Descartados (4)

- **R9-05** — NÃO CONCLUSIVO por dispersão > 3 é regra explícita do §9, implementada como escrita.
- **R4-07** — P/C de 4–5 em CPLE3/CSMG3/SBSP3 é método autorizado (§11.2); só risco de leitura.
- **R6-09** — plano de contas industrial em banco: a triagem não passa banco por coletar_cvm; risco hipotético.
- **R5-04** — LEVE3 está corretamente fora da lista "só com re-rating" (vence_rf = Não).

## Anexo A — Mapa do diretório, pontos de escrita e dados externos

### A.1 Mapa de ferramentas/ (git ls-files: 162 arquivos)

- **Dados de entrada:** `dados/cvm/*.zip` (git-IGNORADO, 1,4 GB, 77 ZIPs: dfp 2010-26, itr 2011-26, fre/fca 2010-26, ipe 2017-26) lido por coletar_cvm, backtest/baixar_cvm e temporada (que sobrescreve itr_AAAA.zip); `dados/cvm_series.json` (versionado, 31 tickers); `dados/raw/<dia>/` (ignorado) → `dados/series_<dia>.json` (versionado; lido por `sorted(glob)[-1]`); `dados/macro/` (versionado; só o IPCA tem coletor); `mercado*.json`, `fatos_*.json` (versionados, sem leitor em código); `backtest/dados/` (ignorado, 674 MB: COTAHIST 2014-26, proventos, índices CVM, fatos_cvm.parquet de 7,48 M linhas, retornos, proxy).
- **Núcleo de cálculo (41 tickers):** `motor_financeiras.py` (427 linhas), `motor_nao_financeiras.py` (856), `lote1_bancos` a `lote6_quimica` (lote4 e lote6 leem ZIPs no import), `universo.py` (junta os 6 lotes), `golden.py`, `rodar_tudo.py`, `tests/golden.json`.
- **Rotinas:** `monitor_semanal.py` (sexta 08:00 pelo Agendador, via VBS oculto), `temporada.py` (3T26 em diante), `registro_prospectivo.py`, `gerar_pdf_lote1..6` e `atualizar_hall_lote1..6`.
- **triagem/** (1.386 linhas; fila da B3 sem veredito): config, universo, avaliar, qualidade, fila, registro, rodar; depende de backtest.{cotahist, precos, ledger.pit, motor, config}.
- **dossie/** (1.347 linhas): base, fre, notas, evidencia, gerar, docs_cvm (curl + pdftotext), fichas blau3/cmin3/hype3/leve3.
- **backtest/** (3,4 mil linhas, parado desde o portão do proxy): config, calendario, cotahist, inflacao_pit, ledger/*, motor/*, precos/*, experimento/proxy; reaproveitado vivo por triagem e monitor.
- **Testes:** tests/ (9 arquivos), dossie/tests (3), backtest/tests (11; 301 testes, ~16 min, ~4 GB).
- **Faltas:** requirements/pyproject, .gitattributes, remoto git, coletores de PTAX/FRED/Tesouro/ANBIMA/Focus, manifesto de hash dos ZIPs.

### A.2 Pontos de escrita

| Script | Grava em | Gatilho |
|---|---|---|
| rodar_tudo.py --motivo; tests/regerar_golden.py | tests/golden.json (sobrescreve), tests/golden_log.md (append) | manual; sem a flag só imprime o diff (exit 1 se mudou); motivo ≥ 15 caracteres |
| registro_prospectivo.py | prospectivo/registro.jsonl (append-only, LF) | manual por rodada; erro se a chave existir com outro valor |
| triagem/rodar.py | 06-triagem-e-fila.md (sobrescreve), cópia em UPLOAD CLAUDE DESKTOP, triagem/dados/triagem_T.csv, prospectivo/triagem.jsonl (append, desligável) | manual por rodada |
| monitor_semanal.py | backtest/dados/cotahist/COTAHIST_A<ano>.ZIP (+.novo/.anterior/.rejeitado) e precos_<ano>.parquet; BOLETINS/AAAA-MM-DD-monitor.md (sobrescreve); monitor/historico.csv (append sem dedupe); monitor/ultimo.log | Agendador ValueInvesting-MonitorSemanal, sexta 08:00; manual (--sem-download/--hoje) |
| temporada.py | dados/cvm/itr_<ano>.zip (sobrescreve, exceto --simular), BOLETINS/*-temporada[-simulacao].md, pasta temporária nunca removida; com --gravar: dados/cvm_series.json (só ltm*) | manual na temporada de resultados |
| coletar_cvm.py | dados/cvm/{dfp,itr}_<ano>.zip e dados/cvm_series.json (merge, sem backup) | manual; chamado por temporada em subprocessos |
| coletar_statusinvest.py; montar_series.py | dados/raw/<hoje>/…; dados/series_<dia>.json (sobrescreve; vira o "último") | manual por rodada de lote |
| coletar_macro.py | dados/macro/ipca_mensal.json (só se a sobreposição conferir) | manual |
| atualizar_hall_lote1..6.py | 03-hall-de-acoes.md (regex e write_text no mesmo caminho, sem backup; lote3 "rodar uma vez") | manual após recálculo |
| gerar_pdf_lote1..6.py | PDFs fixos por lote (rev. 04 e 05-10-2026), sobrescrevem | manual |
| lote*_*.py (__main__) | nada (só imprimem) | seguro de rodar |
| dossie/gerar.py; dossie/docs_cvm.py | DOSSIES/dados/<TK>-<data>.md e dossie/vereditos/<TK>-<data>.json; dados/cvm/docs/<NOME>/… | manual por dossiê |
| backtest/{baixar_cvm, cotahist, precos/ibov, precos/proventos_b3, ledger/*, precos/retorno, experimento/proxy}.py | dados/cvm/*.zip; backtest/dados/* (cotahist, ibov, proventos, índices, fatos_cvm, relatorio_pit, retornos, proxy_consultas.log append, proxy_<data>.json) | manual; backtest parado |
| agendador/instalar_tarefa.ps1 | registra a tarefa no Agendador do Windows (fora do repo) | manual, uma vez |

### A.3 Dados externos e nota da fonte

| Fonte | Nota | Usado em | Versionado | Reconstrução |
|---|---|---|---|---|
| CVM DFP/ITR | A | coletar_cvm → cvm_series.json; lote4:67-126; lote6:92; ledger PIT; temporada | não (ZIPs) | `coletar_cvm.py` e `backtest.baixar_cvm` existem; falta manifesto de hash (itr_2026 é sobrescrito) |
| CVM FRE e FCA | A | dossie/fre, dossie/base, identidade, perfil, triagem/universo | não | `python -m backtest.baixar_cvm` |
| CVM IPE | A | só baixado; nenhum código lê (AUD-71) | não | `backtest.baixar_cvm` |
| CVM RAD (PDFs de notas) | A | dossie/docs_cvm (BLAU3, CMIN3, HYPE3, LEVE3, PRIO3, TIMS3) | não | `dossie.docs_cvm` (curl + pdftotext) |
| B3 COTAHIST | A | backtest/cotahist, monitor, triagem | não | `python -m backtest.cotahist`; monitor baixa o ano corrente |
| B3 proventos (dinheiro e suplemento) | B | backtest/precos/proventos_b3, retorno, dossie/base | não | `python -m backtest.precos.proventos_b3` (API não documentada, retry no código) |
| B3 Ibovespa diário | B | backtest/precos/ibov → benchmark e destino de deslistagem | não | `python -m backtest.precos.ibov` |
| StatusInvest | C | coletar_statusinvest → series_<dia>.json: ROE/LPA/VPA, DPA por data-com, JCP | sim (derivado); cru ignorado | scripts existem; página raspada por regex; agregador, nunca fato isolado |
| BCB SGS 433 (IPCA) | A | inflacao.py, lote5/6, inflacao_pit | sim | `coletar_macro.py` com checagem de sobreposição; série até 08/2026 |
| BCB SGS 3698 (PTAX) | A | lote5:42, lote6:54, cmin3 | sim | sem comando (AUD-81) |
| FRED (Brent EIA, CPI BLS, PPI BLS, minério FMI) | A (EIA/BLS) e B (FMI) | lote5, lote6, cmin3 | sim | sem coletor; sem data de coleta (AUD-81) |
| Tesouro Transparente (IPCA+ 2050 sem cupom, compra da manhã) → rf real | A | lote1_bancos.MK (rf 7,06%); triagem/config.py:78 | sim | manual; nenhum script coleta (AUD-06, AUD-78) |
| ANBIMA ETTJ (vértice ~10 anos) → π | A | lote1_bancos.MK (π 6,46%); triagem/config.py:79 | sim | manual (AUD-78) |
| BCB Focus e Selic | A | só sensibilidade MK_FOCUS e textos de PDF | sim | manual |
| PDFs e fichas anteriores, RI das empresas | B/C | fatos_*.json e lote*_textos.py (sem leitor em código) | sim | sem comando; extraído à mão |
