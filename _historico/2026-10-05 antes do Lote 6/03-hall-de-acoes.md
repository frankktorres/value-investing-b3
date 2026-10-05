# HALL DE AÇÕES — status e histórico de vereditos
*Atualizado em 04/10/2026 · 41 empresas analisadas (39 no hall + 2 fora) · dados das fichas rev. 03/10/2026, cotações de fechamento de 02/10/2026 (véspera do 1º turno) — atualizar antes de decidir*

**Como usar:** este é o índice vivo. Antes de reanalisar qualquer ticker, leia a linha dele aqui e a ficha correspondente no PDF do lote. Ao reanalisar, atualize a linha e registre a mudança no fim do arquivo.

> **⚠ ALERTA DE MÉTODO (auditoria de 04/10/2026).** Os valores centrais abaixo ainda são os da rev. 03/10, feita pela doutrina v1.0 — **exceto os Lotes 1 (Bancos e Seguridade), 2 (Energia e Saneamento), 3 (Agro e B3) e 5 (Petróleo e Gás), recalculados em 04–05/10 pela v2.0/2.1** (`Banco_Seguridade_rev_04-10-2026.pdf`, contas em `ferramentas/`). **Nenhum deles é reconstruível:** vieram de "valor anterior × fator de Ke", de ajustes avulsos em R$ ou de números mantidos, e o quadro clássico (doutrina v2.0 §11) está incompleto em todos. A **palavra** já foi reenquadrada pela régua contínua v2.0 (≤ 0,70 BARATA · ≤ 0,90 RADAR · ≤ 1,10 JUSTA · > 1,10 CARA), com compra = 0,70× e saída = 1,30× o central. **Nenhuma linha autoriza compra antes do recálculo pelo `08-prompt-recalculo-lote.md`.**
>
> **Base de Ke a usar no recálculo:** a doutrina v2.0 manda o Tesouro IPCA+ **sem cupom** mais longo, no fechamento. Os lotes de 03/10 misturaram o IPCA+ 2050 sem cupom (7,06%) com o IPCA+ 2060 **com juros semestrais** (7,08%), e usaram cotação intradiária.

> **Permanência no hall (doutrina v2.0 §2):** fica quem passa 3 dos filtros 1–4; o preço (filtro 5) decide só a compra. **Candidatas a sair no recálculo** (2 falhas prováveis): **UNIP6** (ROIC 7,7% < WACC; provento não coberto), **BRSR6** (ROE < Ke nominal; controlador com V3 consumado), **KLBN11** (payout 126% com FCF negativo; ROIC a conferir).

**Legenda da coluna Pendências v2:**
- **K**: central calculado a Ke diferente do da casa ("Ke mercado 14%" ou coluna real).
- **T**: trava de coerência falha — JUSTA com retorno esperado bem abaixo do Ke, logo o central está alto demais.
- **S**: preço acima da saída (1,30 × central).
- **M**: mistura de fluxo ou crescimento nominal com taxa real.

---

## 1. Quadro geral por veredito (régua v2.0 sobre os números de 03/10)

### BARATA / OPORTUNIDADE
| Ticker | Setor | Preço 02/10 | Central | P/C | Compra 0,70× | Saída 1,30× | Pendências v2 / motivo |
|---|---|---|---|---|---|---|---|

### RADAR (preço ÷ central entre 0,70 e 0,90)

| Ticker | Setor | Preço 02/10 | Central (v1) | P/C | Compra 0,70× | Saída 1,30× | Vence RF? (v1, bruta) | Pendências v2 |
|---|---|---|---|---|---|---|---|---|
| SMTO3 | Açúcar e etanol | 19,34 | **23,07 (v2)** | 0,84 | 16,15 | 30,00 | Não (v2, líquida) | **recalculado v2.0 (04/10)**; Ke implícito 22,4%; ROIC 8,1% × WACC 15,0%; confiança normal; margem bimodal: BARATA só com margem ≥ 27%; outras receitas não recorrentes de mar/2024 normalizadas |
| TIMS3 | Telecom | 18,55 | 22,50 | 0,82 | 15,75 | 29,25 | Sim (marginal) | Bogle soma recompra ao yield |
| GGBR4 | Siderurgia | 26,10 | 30,80 | 0,85 | 21,56 | 40,04 | Não (dividendo) / Empate (valor) | central = anterior reescalado; EPV e reprodução ausentes |
| VIVT3 | Telecom | 30,14 | 33,80 | 0,89 | 23,66 | 43,94 | Empate | Piotroski sumiu; sem linha de controlador |

### JUSTA (preço ÷ central entre 0,90 e 1,10)

| Ticker | Setor | Preço 02/10 | Central (v1) | P/C | Compra 0,70× | Saída 1,30× | Vence RF? (v1, bruta) | Pendências v2 |
|---|---|---|---|---|---|---|---|---|
| PETR4 | Petróleo estatal | 51,17 | **51,78 (v2)** | 0,99 | 36,25 | 67,31 | Sim (v2, líquida) | **recalculado v2.1 (05/10)**; Ke implícito 20,3%; ROIC 13,0% × WACC 16,3%; confiança normal; barril de meio de ciclo R$ 406 (≈ US$ 78); desconto de controlador 8% em cenários; ganhos de desinvestimento 2019–22 fora da margem; déficit atuarial fora da ponte (custo já no EBIT); com abandono ou déficit como dívida seria CARA |
| KEPL3 | Agro, bens de capital | 6,78 | **6,63 (v2)** | 1,02 | 4,64 | 8,62 | Sim (v2, líquida) | **recalculado v2.0 (04/10)**; Ke implícito 19,0%; ROIC 15,3% × WACC 17,6%; confiança normal |
| ITSA4 | Holding | 14,67 | 15,45 | 0,95 | 10,81 | 20,09 | Sim (limite) — caso recorrente 9,6%: Empate | SOTP herda o central de ITUB4 (K) |
| FLRY3 | Saúde | 23,50 | 23,70 | 0,99 | 16,59 | 30,81 | Empate | **T**; Graham com LPA antigo; Piotroski "da ficha" |
| HYPE3 | Farmacêutica | 25,16 | 24,70 | 1,02 | 17,29 | 32,11 | Não (limite) | **T**; Piotroski 9/9 "da ficha"; sem linha de controlador |

### CARA (preço ÷ central acima de 1,10)

| Ticker | Setor | Preço 02/10 | Central | P/C | Compra 0,70× | Saída 1,30× | Pendências v2 / motivo |
|---|---|---|---|---|---|---|---|
| PRIO3 | E&P | 63,35 | **55,31 (v2)** | 1,15 | 38,72 | 71,91 | **recalculado v2.1 (05/10)**; Ke implícito 17,8%; ROIC 13,8% × WACC 17,4%; confiança normal; barril de meio de ciclo R$ 406 (≈ US$ 78); base 1S26 (Peregrino); com imposto de exportação permanente o central cai ~50% |
| UGPA3 | Distribuição | 38,51 | **18,96 (v2)** | 2,03 | 13,28 | 24,65 | **recalculado v2.1 (05/10)**; Ke implícito 13,4%; ROIC 10,8% × WACC 16,7%; confiança normal; EBIT real 2021–25; nem a margem de guerra permanente justifica o preço (S) |
| ISAE4 | Transmissão | 28,19 | **24,10 (v2)** | 1,17 | 16,87 | 31,34 | **recalculado v2.1 (05/10)**; TIR real implícita 10,4% (Tesouro 7,06%; Ke real 12,06%); com 659 mi ações (DFP 2025) seria JUSTA — conferir follow-on no RI |
| CPFE3 | Utility | 48,09 | **31,22 (v2)** | 1,54 | 21,85 | 40,58 | **recalculado v2.1 (05/10)**; TIR real implícita 8,6% (Tesouro 7,06%; Ke real 12,06%) (S) |
| CMIG4 | Utility estatal | 11,41 | **7,21 (v2)** | 1,58 | 5,04 | 9,37 | **recalculado v2.1 (05/10)**; TIR real implícita 8,4% (Tesouro 7,06%; Ke real 12,06%); desconto de controlador 17,7% (S) |
| TAEE11 | Transmissão | 42,85 | **26,74 (v2)** | 1,60 | 18,72 | 34,77 | **recalculado v2.1 (05/10)**; TIR real implícita 7,2% (Tesouro 7,06%; Ke real 12,06%) (S) |
| SAPR11 | Saneamento estatal | 35,21 | **18,30 (v2)** | 1,92 | 12,81 | 23,79 | **recalculado v2.1 (05/10)**; TIR real implícita 7,3% (Tesouro 7,06%; Ke real 12,06%); desconto de controlador 15,0% (S) |
| SBSP3 | Saneamento | 28,23 | **7,05 (v2)** | 4,00 | 4,94 | 9,17 | **recalculado v2.1 (05/10)**; TIR real implícita 4,7% (Tesouro 7,06%; Ke real 12,06%) — **rende menos que o Tesouro** (S) |
| CSMG3 | Saneamento | 56,25 | **11,25 (v2)** | 5,00 | 7,88 | 14,63 | **recalculado v2.1 (05/10)**; TIR real implícita 0,9% (Tesouro 7,06%; Ke real 12,06%) — **rende menos que o Tesouro** (S) |
| CPLE3 | Utility | 16,61 | **3,19 (v2)** | 5,21 | 2,23 | 4,14 | **recalculado v2.1 (05/10)**; TIR real implícita 0,8% (Tesouro 7,06%; Ke real 12,06%) — **rende menos que o Tesouro** (S) |
| SUZB3 | Celulose | 44,35 | **37,94 (v2)** | 1,17 | 26,56 | 49,33 | **recalculado v2.0 (04/10)**; Ke implícito 17,7%; ROIC 7,7% × WACC 14,8%; confiança normal |
| SLCE3 | Agro, terras | 17,20 | **10,69 (v2)** | 1,61 | 7,48 | 13,89 | **recalculado v2.0 (04/10)**; Ke implícito 15,9%; ROIC 7,9% × WACC 15,3%; confiança baixa; CARA mesmo com o NAV de terras de terceiro; arrendamento de terras (IFRS 16) na dívida (S) |
| RANI3 | Embalagem | 7,94 | **4,87 (v2)** | 1,63 | 3,41 | 6,34 | **recalculado v2.0 (04/10)**; Ke implícito 14,0%; ROIC 7,2% × WACC 15,6%; confiança normal (S) |
| B3SA3 | Infraestrutura de mercado | 19,00 | **9,23 (v2)** | 2,06 | 6,46 | 12,00 | **recalculado v2.0 (04/10)**; Ke implícito 13,5%; ROIC 25,1% × WACC 18,2%; confiança normal (S) |
| KLBN11 | Papel | 18,62 | **5,06 (v2)** | 3,68 | 3,55 | 6,58 | **recalculado v2.0 (04/10)**; Ke implícito 12,5%; ROIC 6,7% × WACC 14,5%; confiança baixa (S) |
| BBSE3 | Seguridade | 40,45 | **23,36 (v2)** | 1,73 | 16,35 | 30,37 | **recalculado v2.0 (04/10)** (S); Ke implícito 12,8% vs Ke da casa 19,3%; retorno de investimento 13,5%; vence RF: Não |
| BRBI11 | Banco de investimento | 15,14 | **8,29 (v2)** | 1,83 | 5,80 | 10,77 | **recalculado v2.0 (04/10)** (S); Ke implícito 12,0% vs Ke da casa 19,3%; retorno de investimento 12,0%; vence RF: Não |
| BBAS3 | Banco estatal | 23,72 | **12,51 (v2)** | 1,90 | 8,76 | 16,26 | **recalculado v2.0 (04/10)** (S); Ke implícito 14,2% vs Ke da casa 19,3%; retorno de investimento 15,6%; vence RF: Sim só com re-rating do múltiplo (sem ele: Não); falha filtros 1 (ROE < Ke) e 3 (controlador) → **sai do hall pela v2.0 §2** (aguarda confirmação) |
| ABCB4 | Banco de atacado | 26,15 | **13,31 (v2)** | 1,96 | 9,32 | 17,30 | **recalculado v2.0 (04/10)** (S); Ke implícito 13,3% vs Ke da casa 19,3%; retorno de investimento 13,2%; vence RF: Não |
| BBDC4 | Banco | 19,23 | **9,59 (v2)** | 2,00 | 6,72 | 12,47 | **recalculado v2.0 (04/10)** (S); Ke implícito 12,6% vs Ke da casa 19,3%; retorno de investimento 12,0%; vence RF: Não |
| BRSR6 | Banco estatal RS | 15,92 | **6,84 (v2)** | 2,33 | 4,79 | 8,89 | **recalculado v2.0 (04/10)** (S); Ke implícito 12,2% vs Ke da casa 19,3%; retorno de investimento 13,5%; vence RF: Não; defeito estrutural (folha do RS, V3); falha filtros 1 e 3 → **sai do hall pela v2.0 §2** (aguarda confirmação) |
| PSSA3 | Seguradora | 49,47 | **20,13 (v2)** | 2,46 | 14,09 | 26,17 | **recalculado v2.0 (04/10)** (S); Ke implícito 12,8% vs Ke da casa 19,3%; retorno de investimento 12,2%; vence RF: Não |
| ITUB4 | Banco | 44,83 | **17,54 (v2)** | 2,56 | 12,28 | 22,80 | **recalculado v2.0 (04/10)** (S); Ke implícito 11,8% vs Ke da casa 19,3%; retorno de investimento 11,6%; vence RF: Não |
| CXSE3 | Seguridade | 20,41 | **7,79 (v2)** | 2,62 | 5,45 | 10,12 | **recalculado v2.0 (04/10)** (S); Ke implícito 10,0% vs Ke da casa 19,3%; retorno de investimento 9,3%; vence RF: Não |
| EGIE3 | Geração | 30,70 | 26,70 | 1,15 | 18,69 | 34,71 | TIR "não recalculada"; payout 100% → 55% |
| ABEV3 | Bebidas | 15,84 | 13,75 | 1,15 | 9,62 | 17,88 | sem normalização do lucro; sem linha de controlador |
| LEVE3 | Autopeças | 34,43 | 29,70 | 1,16 | 20,79 | 38,61 | Graham com LPA de pico (normalizado → R$ 26,2) |
| UNIP6 | Química | 56,78 | 37,00 | 1,53 | 25,90 | 48,10 | **S**; **defeito estrutural:** payout 240% do lucro com queima de caixa; caixa 653 mi × 1,4 bi não reconciliado. Era "ARMADILHA" — P/L 24 não é múltiplo baixo |
| WEGE3 | Bens de capital | 51,45 | 33,20 | 1,55 | 23,24 | 43,16 | **S M** (g 12% nominal a Ke real); Bogle sem compressão de múltiplo a P/L 34; melhor empresa do hall |

### NÃO CONCLUSIVO (âncora ≤ 0 ou âncoras discordam mais de 3× — doutrina §11.3; sem preço de compra)

| Ticker | Setor | Preço 02/10 | Mediana das âncoras | P/C | Compra 0,70× | Saída 1,30× | Pendências v2 / motivo |
|---|---|---|---|---|---|---|---|
| RECV3 | E&P onshore | 11,20 | **≤ 0 (v2)** | n.a. | n.a. | n.a. | **recalculado v2.1 (05/10)**; Ke implícito n.d.; ROIC 2,4% × WACC 16,7%; confiança não conclusivo; barril de meio de ciclo R$ 406 (≈ US$ 78); EPV -0,16 · DCF -1,46 · reprodução 15,13 — as âncoras de lucro são ≤ 0 no meio de ciclo; **defeito estrutural:** produção em declínio (−11% a/a) com ROIC abaixo do WACC |

---

## 2. As que vencem a renda fixa (classificação v1, bruta de IR)

TIMS3 · ITSA4 (limite) · CPFE3 (pelo ponto médio é Empate) — lotes ainda v1. **Lote 1 recalculado (v2.0, líquido de IR): nenhuma** — BBAS3 só venceria com re-rating do múltiplo

Pela v2.0, a comparação passa a ser **líquida de IR** (RF real líquida ≈ 5,97% em 02/10; JCP líquido × 0,825). Reclassificar no recálculo. Nenhuma delas tem 30% de margem ao preço atual.

---

## 3. Ranking Greenblatt (Fórmula Mágica) — não financeiras

*Vazio. Será preenchido no recálculo pelo `08`: EY = EBIT ÷ EV e ROC = EBIT ÷ (capital de giro líquido + imobilizado líquido), posição em cada um, soma das posições, ordem final. Bancos, seguradoras e holdings ficam fora (N/A por perfil).*

| Posição | Ticker | EY | Rank EY | ROC | Rank ROC | Soma |
|---|---|---|---|---|---|---|
| — | — | — | — | — | — | — |

---

## 4. Fora do hall (analisadas e descartadas)

| Ticker | Última ficha (03/10) | Motivo |
|---|---|---|
| VBBR3 | R$ 37,66 · **central 14,66 (v2.1, 05/10; P/C 2,57)** | Redundante com UGPA3 e pior em dívida, Comerc e diferimento de JCP (14–18 meses); EBIT real 2020–25 sem créditos tributários; só a margem de guerra permanente justificaria o preço |
| SANB11 | R$ 28,09 · central 18,71 pelo fundamental (v2, P/C 1,50); permuta implícita R$ 28,11 | O preço é cupom de permuta, não empresa; stub ilíquido no pós-OPA; ROE < Ke |

---

## 5. Índice dos PDFs de fichas

| Lote | Conteúdo | Pasta / arquivo vigente | Versão anterior |
|---|---|---|---|
| 1 | Bancos e seguridade (10) | `BANCOS E SEGURIDADE/Banco_Seguridade_rev_04-10-2026.pdf` **(v2.0)** | `…_rev_03-10-2026.pdf`, `…_rev_07-09-2026.pdf` |
| 2 | Energia elétrica e saneamento (8) | `ENERGIA ELÉTRICA E SANEAMENTO/Energia_Saneamento_rev_05-10-2026.pdf` **(v2.1)** | `…_rev_03-10-2026.pdf`, `…_rev_07-09-2026.pdf` |
| 3 | Papel e celulose, infraestrutura, agro (7) | `AGRO E B3/Infra_Agro_rev_04-10-2026.pdf` **(v2.0)** | `…_rev_03-10-2026.pdf`, `…_rev_06-09-2026.pdf` |
| 4 | Saúde, telecom, blue chips (7) | `SAÚDE, TELECOM E BLUECHIPS/Saúde_Telecom_Bluechips_rev_03-10-2026.pdf` | `…_rev_06-09-2026.pdf` |
| 5 | Petróleo, gás e combustíveis (5) | `PETROLEO E GÁS/Petroleo_Gas_rev_05-10-2026.pdf` **(v2.1)** | `…_rev_03-10-2026.pdf`, `…_rev_06-09-2026.pdf` |
| 6 | Química e metalurgia: LEVE3, EGIE3, UNIP6, GGBR4 (4) | `QUÍMICA E METALÚRGIA/Química_Metalúrgia_rev_03-10-2026.pdf` | `…_rev_07-09-2026.pdf` |

*As versões de 06–07/09 trazem quadro clássico mais completo (Graham, Bazin, EPV, Piotroski) que as de 03/10 — úteis como insumo, nunca como valor.*

---

## 6. Registro de revisões

| Data | Ticker | De → Para | Motivo |
|---|---|---|---|
| 07/09/2026 | BRSR6 | RADAR → **ARMADILHA** | Interferência consumada (folha do RS) não estava no valor; desconto de 35% aplicado |
| 07/09/2026 | SAPR11 | JUSTA → **CARA** | Faltava o risco prospectivo (RTP 2029, eleição); desconto de 15% |
| 07/09/2026 | CMIG4 | RADAR → **JUSTA** | TIR de 15,3% da XP não descontava o Propag; cenários ponderados 40/60 |
| 07/09/2026 | PETR4 | JUSTA → **JUSTA (para CARA)** | V1/V5 estava só no gatilho; cenários ponderados |
| 07/09/2026 | BBAS3 | qualidade 5,0 → 6,5 | A franquia é do negócio; o problema é o dono. Entrada única a 16 |
| 07/09/2026 | CXSE3 | justo 18 → 19 | Rótulo estatal indevido retirado (sem interferência consumada) |
| 07/09/2026 | BBSE3, CPFE3 | notas de controlador | Rótulo corrigido; preços inalterados |
| 03/10/2026 | 41 tickers | rev. dos PDFs | Ke 12,35% → 12,08% real; preços de 02/10. Mudanças de palavra nos PDFs: CPFE3 JUSTA → RADAR; HYPE3, FLRY3, SMTO3, SLCE3 RADAR → JUSTA; RECV3 RADAR → JUSTA (aviso ARMADILHA); VIVT3 JUSTA → RADAR; ISAE4 CARA → JUSTA; ABEV3, B3SA3, CPLE3, LEVE3, PETR4, UGPA3 JUSTA → CARA; SANB11 ARMADILHA → JUSTA (stub) |
| 04/10/2026 | todos | régua v2.0 aplicada | Auditoria: régua contínua; compra 0,70× e saída 1,30× recalculadas sobre o central de 03/10; pendências K/T/S/M marcadas; centrais pendentes de recálculo pelo `08` |
| 04/10/2026 | BRSR6, UNIP6 | ARMADILHA → **CARA (defeito estrutural)** | ARMADILHA vira carimbo de múltiplo baixo; as duas estão 50% acima do central |
| 04/10/2026 | BBAS3 | "JUSTA / RADAR" → **JUSTA** | P/C 1,01; palavra dupla não existe na régua |
| 04/10/2026 | SANB11, VBBR3 | saíram das tabelas de veredito | Já estavam "fora do hall"; a duplicidade inflava a contagem |
| 04/10/2026 | Lote 1 (10) | recalculado pela v2.0 | Ke nominal 19,30% (IPCA+ 2050 sem cupom 7,06% + 5 p.p.; inflação implícita 6,46%). Todos CARA: P/C de 1,50× a 2,62×. Razão (c): a rev. 03/10 calculava o justo a Ke de mercado 14% ou na coluna real e supunha IPCA de 4%. BBAS3 e BRSR6 falham 2 filtros (1 e 3) |
| 04/10/2026 | Lote 3 (7) | recalculado pela v2.0 | Demonstrações da CVM (10 anos), margem de meio de ciclo, capex de manutenção descontado do lucro, arrendamentos na dívida. RADAR: SMTO3 · JUSTA: KEPL3 · CARA: SUZB3, RANI3, SLCE3, B3SA3, KLBN11. Razão (c): a rev. 03/10 usava números redondos e múltiplos de EBITDA sem capex de manutenção |
| 05/10/2026 | Lote 2 (8) | recalculado pela v2.1 | Regulados por P/VP justificado (patrimônio como proxy da base) + DDM, TIR real implícita sempre. Todos CARA (P/C 1,17–5,21); CPLE3, CSMG3 e SBSP3 rendem menos que o Tesouro. Razão (c): a rev. 03/10 usava ajustes avulsos e inflação de 4% |
| 05/10/2026 | Lote 5 (5) | recalculado pela v2.1 | Barril de meio de ciclo declarado (média de 10 anos do Brent × câmbio em R$ de hoje = R$ 406/bbl, ≈ US$ 78); E&P por EBITDA mediano − D&A atual; distribuidoras por EBIT real; PETR4 com 8% de desconto de controlador em cenários. JUSTA: PETR4 · CARA: PRIO3, UGPA3 · NÃO CONCLUSIVO: RECV3 · VBBR3 fora do hall (CARA 2,57). Razão (c): a rev. 03/10 usava Brent US$ 70 sem câmbio, múltiplos sem capex e '+1 tri de topo' |
