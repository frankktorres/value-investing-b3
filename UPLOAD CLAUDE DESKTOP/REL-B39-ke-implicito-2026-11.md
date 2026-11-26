# B39 — Ke da Mesa × Ke implícito do mercado (data-base 2026-11-19)

Gerado por `cd ferramentas && python -m b39.relatorio` a partir de `ferramentas/b39/resultado_B39.json` (gerado em 2026-11-25T11:00:16). Regras escritas antes de rodar: `docs/PRE-REGISTRO-v3.md` §7, emendas 9 e 10; conferência das fontes: `docs/b39/FONTES-B39.md`. Medição: não muda motor, doutrina nem golden. Nenhum número aqui é ordem de compra ou venda.

## Veredito do gatilho: **NÃO DISPARA**

Mediana dos Δ = **-2,93 p.p.** (limite: |mediana| > 3,00 p.p., nos dois sentidos; 3 de 3 estimativas).

**Leitura pré-declarada (emenda 11): não dispara; indício só no Ibovespa.** A B35/B46 continua como hipótese, sem prioridade de calibração.

**Saída (emenda 9):** o Ke fica, com este motivo; a causa do "tudo CARA" se procura em outra camada (âncoras, normalização; DNA, causas b–d).

**Versão da emenda 9 (substituída pela 11, mantida ao lado):** DISPARA, mediana -4,89 p.p.; a diferença é só a (i): o ROE histórico nominal era combinado com a π futura da ETTJ; a emenda 11 põe cada ROE em real pelo IPCA do próprio ano e faz Gordon todo em real.

## Mercado (uma data só)

| Insumo | Valor | Fonte |
|---|---|---|
| rf real | 7,86% | Tesouro IPCA+ 2035-05-15 — Tesouro Transparente, PrecoTaxaTesouroDireto.csv, Taxa Compra Manha (nota A) |
| π | 7,1706% | ANBIMA ETTJ, inflação implícita 2520 du (~10 anos) (nota A) |
| s (spread de default, Brasil Ba1) | 2,13% | Damodaran `ctryprem`, atualizada em January 5, 2026 (nota B) |
| ERP total do Brasil | 7,47% | idem (CRP 3,24% + maduro 4,23%) |
| Carteira do Ibovespa | 76 ações | B3, carteira teórica do Ibovespa (GetPortfolioDay), consultada em 25/11/26 (nota A) |
| IPCA (lucro real) | até 2026-09 | SGS 433 (nota A) |

## As três estimativas (Ke real)

| | Estimativa | Ke implícito | Ke da Mesa | Δ | Prêmio implícito (Ke − rf) | Prêmio da Mesa |
|---|---|---|---|---|---|---|
| (i) | Bancos (Gordon real sobre P/VP, ROE real mediano 10a; emenda 11) | 9,93% | 12,86% | -2,93 p.p. | +2,07 p.p. | +5,00 p.p. |
| (i) v. emenda 9 | Bancos (versão da emenda 9: ROE nominal histórico com π futura; substituída) | 7,42% | 12,86% | -5,44 p.p. | -0,44 p.p. | +5,00 p.p. |
| (ii) | Ibovespa agregado (Σ E10 ÷ Σ valor de mercado) | 9,38% | 14,27% | -4,89 p.p. | +1,52 p.p. | +6,41 p.p. |
| (iii) | rf − s + ERP total (Damodaran jan/2026) | 12,84% | 14,27% | -1,42 p.p. | +4,98 p.p. | +6,41 p.p. |

Ke da Mesa: (i) rf + 5 p.p.; (ii) e (iii) rf + o prêmio do índice ponderado pelo valor de mercado (5 p.p. nas financeiras; 5 × [1 + 0,66 × D/E] nas demais, D/E a mercado). (ii) pondera só as que entraram no E10; (iii), todas.

(ii): 74 de 74 companhias do índice com E10 (mínimo de 5 exercícios); cobertura 100,0% do valor de mercado (R$ 4.235,1 bi de R$ 4.235,1 bi) e 100,0% do peso no Ibovespa; Σ E10 = R$ 397,2 bi.

## Sensibilidades (só relatadas; não mudam o gatilho)

| Estimativa | Variante | Ke real | Direção vs. a base |
|---|---|---|---|
| (i) | g real 0% | 10,57% | sobe +0,64 p.p. |
| (i) | g real 2% | 9,29% | desce -0,64 p.p. |
| (i) | ROE LTM no lugar da mediana | 9,02% | desce -0,91 p.p. |
| (i) v. emenda 9 | g real 0% | 8,06% | sobe +0,64 p.p. |
| (i) v. emenda 9 | g real 2% | 6,78% | desce -0,64 p.p. |
| (i) v. emenda 9 | ROE LTM no lugar da mediana | 7,23% | desce -0,19 p.p. |
| (ii) | sem PETR3/PETR4 e VALE3 | 8,02% | desce -1,36 p.p. |
| (ii) | lucro LTM no lugar do E10 | 10,59% | sobe +1,21 p.p. |
| (ii) | Gordon, payout mediano, g real 0% | 5,47% | desce -3,91 p.p. |
| (ii) | Gordon, payout mediano, g real 1% | 6,52% | desce -2,86 p.p. |
| (ii) | Gordon, payout mediano, g real 2% | 7,58% | desce -1,80 p.p. |
| (iii) | sem tirar s (rf real + ERP total) | 15,33% | sobe +2,49 p.p. |

Payout mediano do agregado (dividendos/JCP pagos na DFC ÷ lucro, 2016–2025): 58,3%.

## (i) Bancos

| Banco | Exercícios | ROE real mediano | ROE nominal mediano | P/VP | Ke real (emenda 11) | Ke real (v. emenda 9) | Último balanço |
|---|---|---|---|---|---|---|---|
| ITUB4 | 10 | 12,4% | 17,5% | 1,95 | 6,87% | 5,43% | 2026-09-30 |
| BBDC4 | 10 | 8,2% | 13,6% | 0,71 | 11,03% | 8,06% | 2026-09-30 |
| BBAS3 | 10 | 8,6% | 13,4% | 0,43 | 18,95% | 12,34% | 2026-09-30 |
| ABCB4 | 10 | 8,7% | 13,6% | 0,79 | 10,80% | 7,40% | 2026-09-30 |
| BRSR6 | 10 | 5,0% | 11,7% | 0,50 | 9,06% | 7,45% | 2026-09-30 |
| BRBI11 | 5 | 14,6% | 22,1% | 1,27 | 11,71% | 11,14% | 2026-09-30 |
| SANB11 | 10 | 6,6% | 12,3% | 0,81 | 7,96% | 5,67% | 2026-09-30 |
| BPAC11 | 10 | 12,1% | 18,2% | 2,37 | 5,69% | 4,93% | 2026-06-30 |

## (ii) Fora do agregado (declarado)

Nenhuma.

Avisos de dado:

- ABEV3: composição em milhares (× 1000; referência do ledger 15,484,664,889)
- ASAI3: composição em milhares (× 1000; referência do ledger 1,354,393,401)
- AURE3: composição em milhares (× 1000; referência do ledger 1,050,377,974)
- AXIA3: composição em milhares (× 1000; referência do ledger 2,874,657,070)
- BRAP4: composição em milhares (× 1000; referência do ledger 393,096,610)
- BPAC11: ITR 2026-09-30 entregue até T, sem números no CSV da CVM: usado o 2026-06-30
- CXSE3: composição em milhares (× 1000; referência do ledger 3,000,000,000)
- CMIG4: composição em milhares (× 1000; referência do ledger 2,861,781,895)
- CSMG3: composição em milhares (× 1000; referência do ledger 380,253,069)
- CYRE3: composição em milhares (× 1000; referência do ledger 453,446,450)
- EMBJ3: composição em milhares (× 1000; referência do ledger 740,465,044)
- ENEV3: composição em milhares (× 1000; referência do ledger 1,944,391,265)
- ITSA4: composição em milhares (× 1000; referência do ledger 11,213,686,845)
- ITUB4: composição em milhares (× 1000; referência do ledger 11,026,869,192)
- LREN3: composição em milhares (× 1000; referência do ledger 1,006,845,095)
- MRVE3: composição em milhares (× 1000; referência do ledger 562,835,771)
- NATU3: composição em milhares (× 1000; referência do ledger 1,374,557,657)
- SANB11: composição em milhares (× 1000; referência do ledger 7,498,531,051)
- TAEE11: composição em milhares (× 1000; referência do ledger 1,033,496,721)
- TEND3: composição em milhares (× 1000; referência do ledger 122,578,152)
- TIMS3: DFP 2024-12-31: consolidado zerado, usado o individual
- TIMS3: DFP 2025-12-31: consolidado zerado, usado o individual
- VALE3: composição em milhares (× 1000; referência do ledger 4,439,159,764)
- VBBR3: composição em milhares (× 1000; referência do ledger 1,198,563,531)
- YDUQ3: composição em milhares (× 1000; referência do ledger 274,088,851)
- BRSR6: composição em milhares (× 1000; referência do ledger 408,974,477)
- CPLE3: PN sem pregão: preço da ON
- ENGI11: pela unit ENGI11 (5 ações por unit)
- IGTI11: pela unit IGTI11 (3 ações por unit)
- KLBN11: pela unit KLBN11 (5 ações por unit)
- SBSP3: PN sem pregão: preço da ON
- SANB11: pela unit SANB11 (2 ações por unit)
- TAEE11: pela unit TAEE11 (3 ações por unit)
- ABCB4: ON sem pregão: preço da PN
- BRBI11: pela unit BRBI11 (3 ações por unit)

## Simplificações e vieses declarados (emendas 9 e 10)

- t = 34% para todas no Hamada (o motor usa a alíquota perpétua de cada uma): o prêmio sai no mínimo e o Ke da Mesa erra para baixo, o lado de **não** disparar quando o Ke da Mesa é alto demais.
- D = empréstimos e financiamentos (CP + LP) + arrendamento lançado fora deles, do último ITR. Os "outros passivos financeiros" da ficha de cada empresa não existem para o índice inteiro e ficam em zero: o prêmio sai mais baixo, o mesmo lado do item anterior.
- (ii) Sobrevivência: só os componentes de hoje. Holdings e controladas listadas (ITSA4/ITUB4, BRAP4/VALE3, GOAU4/GGBR4) entram as duas, como no próprio índice: lucro e valor de mercado contados dos dois lados.
- (ii) E10 ÷ P é o EPV reverso da Mesa, não um resultado de Shiller (emenda 10): sem crescimento, subestima o Ke quando o crescimento cria valor. As linhas de Gordon dão o tamanho.
- (i) Emenda 11: ROE real do exercício pelo IPCA de jan–dez do próprio ano (SGS 433); ROE LTM real pelo IPCA dos mesmos 12 meses.
- (ii) Lucro real: cada exercício levado a R$ do último IPCA publicado em T pelo índice médio dos 12 meses do exercício (`inflacao.deflator_periodo`).
- (iii) Tirar s de uma NTN-B levada a nominal é extensão da Mesa: o Damodaran não trata título indexado de governo com risco de default (emenda 10).
- Valor de mercado = ações ON e PN do último ITR (sem tesouraria) × o preço de fechamento de cada classe em T (COTAHIST); uma classe sem pregão usa o preço da outra (avisado acima).
