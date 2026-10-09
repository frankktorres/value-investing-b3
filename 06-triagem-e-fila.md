# TRIAGEM E FILA DE ANÁLISE

*Gerado por `python -m triagem.rodar` em 2026-10-08 — **não editar à mão** (a próxima rodada sobrescreve;
o histórico fica em `_historico/` e em `prospectivo/triagem.jsonl`). Config `44f2e051e4af14db`.*

**Regra dura (vale desde 07/09):** a triagem define **a fila**, nunca o veredito. Prova antiga: LEVE3 passou 7/7 e a análise
completa deu JUSTA/CARA; UNIP6 passou 5/7 e deu ARMADILHA. Aqui não existe palavra: o central rápido é o do motor reduzido da
Etapa 3, cujo erro **medido** contra a régua completa é de **±0,34 de P/C na mediana** (|ΔP/C| nos 41 do hall,
consulta única de 06/10/2026; o portão do proxy pedia ≤ 0,15 e reprovou) e chega a **1,88×** o P/C
da régua de 06/10 (v2.2) no pior caso entre os 30 com central confiável (1,56× contra a régua vigente).
A D5 continua aberta: nenhuma régua desta mesa tem validação empírica.

## 1. Como a fila é feita

**Data:** preços de fechamento de **2026-10-02** (COTAHIST, B3) · rf 7.06% real (Tesouro IPCA+ 15/08/2050, taxa de compra da manhã (Tesouro Transparente, mercado_vigente.json)) · π 6.46% ·
Ke real = rf + 5% fixo — rf e π os mesmos do hall; o prêmio diverge do hall desde a v2.4 (o hall ajusta pela alavancagem; o motor reduzido está congelado).

**Universo:** toda ação/unit com negócio nos 60 pregões até T, **uma linha por companhia** (a classe mais líquida).
**Liquidez mínima R$ 0,97 mi/dia** = maior entre o piso do backtest (R$ 500 mil de mai/2014 corrigidos pelo
IPCA) e o volume que permite vender uma posição de R$ 50.000 em 5 pregões com até
10% do volume (posição típica declarada pelo Frank em 06/10/2026).

**Exclusões (doutrina §8 e §2), nesta ordem:** liquidez · sem identidade na CVM · recuperação judicial/extrajudicial,
falência ou liquidação (FCA `Situação do emissor` ou CODBDI de recuperação no último pregão) · setores a evitar (educação;
aviação e resseguro por ticker; tecnologia sem lucro) · já analisada no hall · sem DFP · menos de 7
exercícios · último DFP atrasado.

**Qualidade (Buffett), sobre o ledger point-in-time da CVM:**

| Teste | Régua | Filtro |
|---|---|---|
| Q1 | ROIC real (contábil, Fisher pelo IPCA do ano) > WACC real de hoje em ≥ 70% dos exercícios; financeira: ROE real > Ke real | 1 |
| Q2 | FCO > 0 em ≥ 80% dos exercícios | 2 |
| Q3 | DL/EBITDA ≤ 2,5 no último balanço, ou caixa líquido | 2 |
| Q4 | R$ 1 retido virou ≥ R$ 1,00 de valor de mercado (real; ações de D0 pelo FRE quando há); prejuízo acumulado reprova; n/a se o retido < 10% do valor inicial | 3 (alocação) |
| Q5 | pagou provento em ≥ 80% dos exercícios | 4 |

✓ passou · ✗ reprovou · ? dado insuficiente (conta como reprovação) · – não se aplica.
**Portão (camada A):** Q1 ✓ e no máximo 1 reprovação em Q2–Q5. **Camada B:** ≥ 3 testes ✓,
fora do portão — entra para a análise completa resolver o que reprovou. A fila ordena por camada, nº de ✓ e preço
(média dos percentis do EY de Greenblatt e do P/C proxy; sem central confiável o P/C conta como mediano).

**Preço, sem palavra:** P/C proxy = preço ÷ central rápido (EPV de meio de ciclo, Owner Earnings, reprodução). "(n/c)" =
não confiável (âncora ≤ 0 ou dispersão > 3,0). Sai da fila quem tem central confiável e
**P/C proxy > 2,07** (= 1,10 × 1,8818, a maior superestimação do P/C
medida no proxy entre os 30 confiáveis do hall contra a régua de 06/10 (v2.2) — `triagem/dados/erro_proxy_2026-10-06.csv`;
contra a régua vigente o pior caso é 1,5578× e o corte seria 1,71: fica o
maior, que corta menos): mesmo com o pior erro
observado ficaria acima de 1,10. Amostra pequena e quase toda CARA: o corte é provisório e só tira o que
está claramente caro. Até 08/10/2026 o corte era 1,10 + 0,34 (a mediana, que não é limite) e
tirava 4 dos 5 papéis que passam no portão (AUD-33). EY = EBIT ajustado (sem o excesso de outras receitas, §7) ÷ (valor
de mercado + dívida líquida).

**Divergência declarada (doutrina v2.3, 07/10/2026):** o motor reduzido da triagem segue com a alíquota da v2.2 (mediana de 5 anos presa entre 15% e 34%), porque está congelado pelo portão do backtest de 06/10. A v2.3 (sem piso; crédito com prazo por fase; abaixo de 15% sem origem declarada = 34%) vale no hall e no dossiê; a alíquota de cada nome da fila é decidida na análise completa.

**Funil:** 312 companhias negociadas → 110 avaliadas (104 não financeiras,
6 financeiras) → **5 passam no portão** · 38 na camada B ·
10 fora por preço.

> **Registro prospectivo:** a fila de 2026-10-02 está em `prospectivo/triagem.jsonl` com a config `929faf4f4d56c5b1`, não com esta (`44f2e051e4af14db`). O registro é append-only: a fila acima não substitui a registrada; a próxima data de triagem registra com a config vigente.

## 2. Fila (20)

| # | Ticker | Camada | Setor (FCA) | Preço | P/C proxy | EY | Q1 Q2 Q3 Q4 Q5 |
|---|---|---|---|---|---|---|---|
| 1 | **TGMA3** | A | Serviços Transporte e Logística | 39,50 | 1,69 | 12,4% | ✓ ✓ ✓ ✓ ✓ |
| 2 | **CMIN3** | A | Extração Mineral | 4,97 | 0,70 (n/c) | 17,9% | ✓ ✓ ✓ – ✓ |
| 3 | **INTB3** | A | Comércio (Atacado e Varejo) | 15,98 | 1,50 | 9,1% | ✓ ✓ ✓ ✗ ✓ |
| 4 | **TOTS3** | B | Comunicação e Informática | 35,35 | 3,80 (n/c) | 4,8% | ✗ ✓ ✓ ✓ ✓ |
| 5 | **ALLD3** | B | Comércio (Atacado e Varejo) | 5,28 | 0,32 | 28,2% | ✗ ✓ ✓ ✗ ✓ |
| 6 | **VLID3** | B | Comunicação e Informática | 17,97 | 0,82 | 18,8% | ✗ ✓ ✓ ✗ ✓ |
| 7 | **POMO4** | B | Máquinas, Equipamentos, Veículos e Peças | 4,33 | 0,95 (n/c) | 19,7% | ✗ ✓ ✓ ✗ ✓ |
| 8 | **RIAA3** | B | Têxtil e Vestuário | 7,57 | 1,09 (n/c) | 16,6% | ✗ ✓ ✓ ✗ ✓ |
| 9 | **LAVV3** | B | Construção Civil, Mat. Constr. e Decoração | 11,51 | 2,27 (n/c) | 15,5% | ✓ ✗ ✓ ✗ ✓ |
| 10 | **MDNE3** | B | Construção Civil, Mat. Constr. e Decoração | 25,85 | 2,95 (n/c) | 15,4% | ✗ ✓ ✓ ✓ ✗ |
| 11 | **BLAU3** | B | Farmacêutico e Higiene | 10,82 | 1,51 (n/c) | 13,3% | ✗ ✓ ✓ ✗ ✓ |
| 12 | **SHUL4** | B | Metalurgia e Siderurgia | 4,70 | 0,82 | 10,5% | ✗ ✓ ✓ ✗ ✓ |
| 13 | **LREN3** | B | Comércio (Atacado e Varejo) | 11,76 | 1,13 | 13,6% | ✗ ✓ ✓ ✗ ✓ |
| 14 | **VULC3** | B | Têxtil e Vestuário | 13,87 | 1,53 (n/c) | 12,5% | ✗ ✓ ✓ ✓ ✗ |
| 15 | **MILS3** | B | Serviços Transporte e Logística | 16,03 | 1,20 (n/c) | 12,5% | ✗ ✓ ✓ ✓ ✗ |
| 16 | **CYRE3** | B | Construção Civil, Mat. Constr. e Decoração | 27,99 | 5,97 (n/c) | 11,8% | ✗ ✗ ✓ ✓ ✓ |
| 17 | **ALUP11** | B | Emp. Adm. Part. - Energia Elétrica | 33,51 | 1,64 | 12,8% | ✗ ✓ ✗ ✓ ✓ |
| 18 | **MGLU3** | B | Comércio (Atacado e Varejo) | 7,61 | 0,77 (n/c) | 10,1% | ✗ ✓ ✓ ✓ ✗ |
| 19 | **FESA4** | B | Metalurgia e Siderurgia | 5,75 | 0,67 | 0,4% | ✗ ✓ ✓ ✗ ✓ |
| 20 | **GRND3** | B | Têxtil e Vestuário | 4,03 | 1,06 | 8,7% | ✗ ✓ ✓ ✗ ✓ |

### O que cada análise completa precisa resolver

- **TGMA3** (A; Q1 7/10 acima do WACC real 11,5%; Q2 FCO > 0 em 10/10; Q3 DL/EBITDA 0,1; Q4 R$ 1 retido -> R$ 2,69 (9 exerc.); Q5 pagou em 9/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - ROIC medido é o contábil: conferir a custo de reposição (D10)
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
- **CMIN3** (A; Q1 7/7 acima do WACC real 10,3%; Q2 FCO > 0 em 6/7; Q3 DL/EBITDA 0,2; Q4 retém pouco (-1% do valor de mercado inicial); Q5 pagou em 7/7)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - ROIC medido é o contábil: conferir a custo de reposição (D10)
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
  - janela de 7 exercícios: quebra estrutural ou histórico curto (§11.4)
- **INTB3** (A; Q1 6/7 acima do WACC real 11,3%; Q2 FCO > 0 em 6/7; Q3 caixa líquido; Q4 R$ 1 retido -> R$ -5,01 (4 exerc.); Q5 pagou em 7/7)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - alocação (R$ 1 retido -> R$ -5,01 (4 exerc.)): o capital retido rendeu?
  - ROIC medido é o contábil: conferir a custo de reposição (D10)
  - âncoras divergem (2,7×)
  - janela de 7 exercícios: quebra estrutural ou histórico curto (§11.4)
- **TOTS3** (B; Q1 4/10 acima do WACC real 10,9%; Q2 FCO > 0 em 10/10; Q3 DL/EBITDA 2,1; Q4 R$ 1 retido -> R$ 5,29 (9 exerc.); Q5 pagou em 10/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (4/10 acima do WACC real 10,9%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
  - ações variaram +17% na janela (emissão/recompra): Q4 aproximado
  - descartada 07/09: compounder com DY 2–3% (Fisher compraria, carteira de renda não)
- **ALLD3** (B; Q1 2/7 acima do WACC real 9,5%; Q2 FCO > 0 em 7/7; Q3 DL/EBITDA 0,2; Q4 R$ 1 retido -> R$ -4,94 (4 exerc.); Q5 pagou em 7/7)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (2/7 acima do WACC real 9,5%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - alocação (R$ 1 retido -> R$ -4,94 (4 exerc.)): o capital retido rendeu?
  - janela de 7 exercícios: quebra estrutural ou histórico curto (§11.4)
  - ações variaram +21% na janela (emissão/recompra): Q4 aproximado
- **VLID3** (B; Q1 2/10 acima do WACC real 10,3%; Q2 FCO > 0 em 10/10; Q3 DL/EBITDA 0,3; Q4 R$ 1 retido -> R$ -3,05 (9 exerc.); Q5 pagou em 10/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (2/10 acima do WACC real 10,3%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - alocação (R$ 1 retido -> R$ -3,05 (9 exerc.)): o capital retido rendeu?
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
  - ações variaram +12% na janela (emissão/recompra): Q4 aproximado
- **POMO4** (B; Q1 3/10 acima do WACC real 9,8%; Q2 FCO > 0 em 10/10; Q3 DL/EBITDA 1,2; Q4 R$ 1 retido -> R$ 0,42 (9 exerc.); Q5 pagou em 10/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (3/10 acima do WACC real 9,8%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - alocação (R$ 1 retido -> R$ 0,42 (9 exerc.)): o capital retido rendeu?
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
  - outras classes negociadas (POMO3): escolher a classe, tag along
- **RIAA3** (B; Q1 1/10 acima do WACC real 8,9%; Q2 FCO > 0 em 10/10; Q3 DL/EBITDA 0,8; Q4 R$ 1 retido -> R$ -0,75 (9 exerc.); Q5 pagou em 10/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (1/10 acima do WACC real 8,9%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - alocação (R$ 1 retido -> R$ -0,75 (9 exerc.)): o capital retido rendeu?
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
- **LAVV3** (B; Q1 6/7 acima do WACC real 9,9%; Q2 FCO > 0 em 2/7; Q3 DL/EBITDA 1,1; Q4 R$ 1 retido -> R$ -0,87 (5 exerc.); Q5 pagou em 7/7)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - caixa (FCO > 0 em 2/7): o lucro vira caixa?
  - alocação (R$ 1 retido -> R$ -0,87 (5 exerc.)): o capital retido rendeu?
  - ROIC medido é o contábil: conferir a custo de reposição (D10)
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - janela de 7 exercícios: quebra estrutural ou histórico curto (§11.4)
- **MDNE3** (B; Q1 1/10 acima do WACC real 10,5%; Q2 FCO > 0 em 8/10; Q3 DL/EBITDA 0,4; Q4 R$ 1 retido -> R$ 1,40 (5 exerc.); Q5 pagou em 2/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (1/10 acima do WACC real 10,5%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - proventos (pagou em 2/10): a política de dividendo é recorrente?
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
  - ações variaram +23% na janela (emissão/recompra): Q4 aproximado
- **BLAU3** (B; Q1 6/9 acima do WACC real 10,3%; Q2 FCO > 0 em 9/9; Q3 caixa líquido; Q4 R$ 1 retido -> R$ -4,79 (4 exerc.); Q5 pagou em 9/9)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (6/9 acima do WACC real 10,3%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - alocação (R$ 1 retido -> R$ -4,79 (4 exerc.)): o capital retido rendeu?
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - janela de 9 exercícios: quebra estrutural ou histórico curto (§11.4)
  - ações variaram +21% na janela (emissão/recompra): Q4 aproximado
- **SHUL4** (B; Q1 3/10 acima do WACC real 10,2%; Q2 FCO > 0 em 9/10; Q3 caixa líquido; Q4 R$ 1 retido -> R$ 0,88 (9 exerc.); Q5 pagou em 10/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (3/10 acima do WACC real 10,2%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - alocação (R$ 1 retido -> R$ 0,88 (9 exerc.)): o capital retido rendeu?
  - âncoras divergem (2,3×)
- **LREN3** (B; Q1 4/10 acima do WACC real 10,9%; Q2 FCO > 0 em 10/10; Q3 DL/EBITDA 0,4; Q4 R$ 1 retido -> R$ -1,66 (9 exerc.); Q5 pagou em 10/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (4/10 acima do WACC real 10,9%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - alocação (R$ 1 retido -> R$ -1,66 (9 exerc.)): o capital retido rendeu?
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
  - reserva 07/09: falhava em preço, histórico curto ou payout não coberto
- **VULC3** (B; Q1 6/10 acima do WACC real 11,1%; Q2 FCO > 0 em 10/10; Q3 DL/EBITDA 0,7; Q4 R$ 1 retido -> R$ 1,79 (9 exerc.); Q5 pagou em 6/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (6/10 acima do WACC real 11,1%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - proventos (pagou em 6/10): a política de dividendo é recorrente?
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
  - fila 07/09: só paga desde 2020 — o dividendo é política ou humor do dono?
- **MILS3** (B; Q1 4/10 acima do WACC real 9,6%; Q2 FCO > 0 em 8/10; Q3 DL/EBITDA 1,4; Q4 R$ 1 retido -> R$ 5,37 (9 exerc.); Q5 pagou em 5/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (4/10 acima do WACC real 9,6%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - proventos (pagou em 5/10): a política de dividendo é recorrente?
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
  - descartada 07/09: compounder com DY 2–3% (Fisher compraria, carteira de renda não)
- **CYRE3** (B; Q1 0/10 acima do WACC real 9,8%; Q2 FCO > 0 em 6/10; Q3 DL/EBITDA 2,0; Q4 R$ 1 retido -> R$ 1,72 (9 exerc.); Q5 pagou em 10/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (0/10 acima do WACC real 9,8%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - caixa (FCO > 0 em 6/10): o lucro vira caixa?
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
  - outras classes negociadas (CYRE4): escolher a classe, tag along
- **ALUP11** (B; Q1 2/10 acima do WACC real 8,4%; Q2 FCO > 0 em 8/10; Q3 DL/EBITDA 2,9; Q4 R$ 1 retido -> R$ 4,84 (9 exerc.); Q5 pagou em 10/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (2/10 acima do WACC real 8,4%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - balanço (DL/EBITDA 2,9): a dívida se paga sem refinanciar?
  - ações variaram +16% na janela (emissão/recompra): Q4 aproximado
  - holding: EBIT inclui equivalência — SOTP e desconto de holding
  - concessão/regulado: TIR real implícita contra rf e Ke (§4)
  - outras classes negociadas (ALUP4 ALUP3): escolher a classe, tag along
  - fila 07/09: repetir o teste TIR real vs IPCA+ que reprovou a Taesa
- **MGLU3** (B; Q1 4/10 acima do WACC real 8,9%; Q2 FCO > 0 em 8/10; Q3 DL/EBITDA 2,1; Q4 R$ 1 retido -> R$ 1,24 (9 exerc.); Q5 pagou em 7/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (4/10 acima do WACC real 8,9%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - proventos (pagou em 7/10): a política de dividendo é recorrente?
  - central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo
  - margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)
  - ações variaram +30% na janela (emissão/recompra): Q4 aproximado
- **FESA4** (B; Q1 4/10 acima do WACC real 11,2%; Q2 FCO > 0 em 10/10; Q3 caixa líquido; Q4 R$ 1 retido -> R$ 0,37 (9 exerc.); Q5 pagou em 10/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (4/10 acima do WACC real 11,2%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - alocação (R$ 1 retido -> R$ 0,37 (9 exerc.)): o capital retido rendeu?
  - outras classes negociadas (FESA3): escolher a classe, tag along
  - reserva 07/09: falhava em preço, histórico curto ou payout não coberto
- **GRND3** (B; Q1 2/10 acima do WACC real 11,9%; Q2 FCO > 0 em 10/10; Q3 caixa líquido; Q4 R$ 1 retido -> R$ -1,06 (9 exerc.); Q5 pagou em 8/10)
  - filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos
  - retorno sobre capital (2/10 acima do WACC real 11,9%): mostrar ROIC a reposição/ciclo acima do WACC ou descartar
  - alocação (R$ 1 retido -> R$ -1,06 (9 exerc.)): o capital retido rendeu?
  - âncoras divergem (1,9×)
  - fila 07/09: renda pura sem dívida, mas crescimento zero: é armadilha de caixa?

## 3. Financeiras — dado incompleto, conferir à mão

O ledger da CVM perde o lucro de bancos em parte dos anos (regex de descrição, defeito conhecido da Etapa 3, não corrigido). Q2, Q3, NCAV e EY não se aplicam.

| # | Ticker | Camada | Setor (FCA) | Preço | P/C proxy | EY | Q1 Q2 Q3 Q4 Q5 |
|---|---|---|---|---|---|---|---|
| 1 | **BMEB4** | B | Bancos | 60,92 | — | — | ? – – ✓ ✓ |
| 2 | **QUAL3** | B | Seguradoras e Corretoras | 1,69 | 0,43 (n/c) | — | ✗ – – – ✓ |
| 3 | **BPAC11** | B | Bancos | 66,02 | — | — | ✗ – – ? ✓ |
| 4 | **BMGB4** | B | Bancos | 6,59 | 3,87 | — | ✗ – – – ✓ |
| 5 | **WIZC3** | B | Seguradoras e Corretoras | 8,19 | 0,27 (n/c) | — | ✗ – – ✗ ✗ |
| 6 | **PINE4** | B | Bancos | 12,63 | — | — | ✗ – – ✗ ✗ |

## 4. Deep value — Graham net-net (fora da fila)

Preço ≤ 67% do NCAV por ação (ativo circulante − passivo total − minoritários). Dispensa o Q1 (exceção de Graham/Schloss no §2), não as exclusões. Construtora/incorporadora: o AC é estoque de imóveis e o NCAV superestima.

| Ticker | Setor | Preço | NCAV/ação | Q1 Q2 Q3 Q4 Q5 |
|---|---|---|---|---|
| **MTRE3** | Construção Civil, Mat. Constr. e Decoração | 3,51 | 5,34 | ✗ ✗ ✗ – ✓ |

## 5. Avaliar à mão — sem central rápido ou com quebra estrutural

Quebra estrutural = a base de ações mudou mais de 50% entre o início da janela e T (emissão grande, incorporação, ou evento em ações que a tabela de eventos não capturou — variações de milhares de % são esse último caso) ou o ativo do ITR mais novo passa de 3,0× o do último DFP. Os exercícios por ação não comparam com o preço de hoje, então nem o portão nem o central valem: a análise começa por reconstruir a base.

| Ticker | Setor | Motivo | Q1 Q2 Q3 Q4 Q5 |
|---|---|---|---|
| **ENGI11** | Emp. Adm. Part. - Energia Elétrica | quebra estrutural: base de ações +71% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✗ ✓ ✓ |
| **GFSA3** | Construção Civil, Mat. Constr. e Decoração | quebra estrutural: base de ações +99882% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✗ ✗ ✗ ✗ |
| **RAIL3** | Emp. Adm. Part. - Serviços Transporte e Logística | quebra estrutural: base de ações +173% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✗ ✓ ✓ |
| **LIGT3** | Emp. Adm. Part. - Energia Elétrica | quebra estrutural: base de ações +690% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✗ ✗ ✗ |
| **BRAP4** | Emp. Adm. Part. - Extração Mineral | ancora_indisponivel | ✗ ✓ ✓ ✗ ✓ |
| **MBRF3** | Alimentos | acoes_indisponiveis | ✗ ✓ ✗ ? ✗ |
| **ENEV3** | Energia Elétrica | quebra estrutural: base de ações +200% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✗ ✓ ✗ |
| **ALOS3** | Emp. Adm. Part. - Comércio (Atacado e Varejo) | quebra estrutural: base de ações +560% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✓ ✓ ✓ |
| **RDOR3** | Serviços médicos | quebra estrutural: base de ações +144% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✗ ✓ – ✓ |
| **PGMN3** | Comércio (Atacado e Varejo) | quebra estrutural: base de ações +111% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✓ ✗ ✗ |
| **SMFT3** | Brinquedos e Lazer | quebra estrutural: base de ações +2665% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✗ ✓ ✓ |
| **OPCT3** | Petróleo e Gás | quebra estrutural: base de ações +137% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✓ – ✗ |
| **CVCB3** | Hospedagem e Turismo | quebra estrutural: base de ações +291% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✗ ✓ ✗ ✗ |
| **SOJA3** | Alimentos | quebra estrutural: base de ações +1432% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✓ ✗ ✗ ✓ ✗ |
| **ORVR3** | Saneamento, Serv. Água e Gás | quebra estrutural: base de ações +92% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✗ ✗ ✗ |
| **AZZA3** | Têxtil e Vestuário | quebra estrutural: base de ações +133% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✓ ✗ ✓ |
| **RENT3** | Serviços Transporte e Logística | quebra estrutural: base de ações +55% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✗ ✗ ✓ ✓ |
| **MOVI3** | Serviços Transporte e Logística | quebra estrutural: base de ações +88% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✗ ✗ ✓ ✓ |
| **HBOR3** | Construção Civil, Mat. Constr. e Decoração | quebra estrutural: base de ações +160% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✗ ✗ ✗ ✗ |
| **CSAN3** | Agricultura (Açúcar, Álcool e Cana) | quebra estrutural: base de ações +144% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✗ ✗ ✓ |
| **SAUD3** | Serviços médicos | quebra estrutural: base de ações +414% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✓ ✓ ✓ ✓ ✓ |
| **MYPK3** | Máquinas, Equipamentos, Veículos e Peças | quebra estrutural: base de ações +62% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✗ – ✓ |
| **AZEV3** | Construção Civil, Mat. Constr. e Decoração | quebra estrutural: base de ações +41094% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ? ✗ ✗ ✗ ✗ |
| **DASA3** | Serviços médicos | quebra estrutural: base de ações +302% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✗ ✗ ✓ |
| **BEEF3** | Alimentos | quebra estrutural: base de ações +317% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✓ ✓ ✗ ✗ ✗ |
| **NATU3** | Farmacêutico e Higiene | quebra estrutural: base de ações +59% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✓ ✗ ✓ |
| **POSI3** | Comunicação e Informática | quebra estrutural: base de ações +62% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✗ ✓ ✗ ✗ |
| **FRAS3** | Máquinas, Equipamentos, Veículos e Peças | quebra estrutural: base de ações +124% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✓ ✓ ✓ |
| **TASA4** | Máquinas, Equipamentos, Veículos e Peças | quebra estrutural: base de ações +166% na janela (emissão, incorporação ou evento sem fator: o histórico por ação não compara) | ✗ ✓ ✗ ✗ ✗ |

## 6. Fora da fila por preço (P/C proxy > 2,07 com central confiável)

ALOS3 (2,10), CURY3 (2,28), MULT3 (2,50), BMOB3 (2,58), DIRR3 (2,67), EQTL3 (2,93), RDOR3 (2,93), RADL3 (4,46), IGTI11 (4,60), TFCO4 (17,24)

## 7. Excluídas

| Motivo | Nº |
|---|---|
| liquidez abaixo do piso | 118 |
| já analisada (hall) | 41 |
| sem identidade na CVM | 17 |
| menos de 7 exercícios | 10 |
| setor a evitar (§8) | 9 |
| recuperação/falência/liquidação | 7 |

| Ticker | Motivo | Detalhe |
|---|---|---|
| AUAU3 | menos de 7 exercícios | 3 exercícios |
| AURE3 | menos de 7 exercícios | 5 exercícios |
| AZTE3 | menos de 7 exercícios | 3 exercícios |
| CBAV3 | menos de 7 exercícios | 6 exercícios |
| DESK3 | menos de 7 exercícios | 6 exercícios |
| FIQE3 | menos de 7 exercícios | 6 exercícios |
| GGPS3 | menos de 7 exercícios | 6 exercícios |
| MATD3 | menos de 7 exercícios | 6 exercícios |
| PLPL3 | menos de 7 exercícios | 6 exercícios |
| TTEN3 | menos de 7 exercícios | 6 exercícios |
| AMER3 | recuperação/falência/liquidação | FCA: Em Recuperação Judicial ou Equivalente |
| BHIA3 | recuperação/falência/liquidação | CODBDI 08 no último pregão |
| BRKM5 | recuperação/falência/liquidação | CODBDI 07 no último pregão |
| ONCO3 | recuperação/falência/liquidação | CODBDI 07 no último pregão |
| PCAR3 | recuperação/falência/liquidação | CODBDI 07 no último pregão |
| PMAM3 | recuperação/falência/liquidação | FCA: Em Recuperação Judicial ou Equivalente |
| RAIZ4 | recuperação/falência/liquidação | FCA: Em Recuperação Extrajudicial |
| AMAR3 | sem identidade na CVM |  |
| B1003 | sem identidade na CVM |  |
| CTAX3 | sem identidade na CVM |  |
| EPAR3 | sem identidade na CVM |  |
| EQPA3 | sem identidade na CVM |  |
| EQPA5 | sem identidade na CVM |  |
| EQPA7 | sem identidade na CVM |  |
| HAGA3 | sem identidade na CVM |  |
| HAGA4 | sem identidade na CVM |  |
| LUXM4 | sem identidade na CVM |  |
| MAPT3 | sem identidade na CVM |  |
| MAPT4 | sem identidade na CVM |  |
| MLAS3 | sem identidade na CVM | CNPJ sem código CVM único |
| NORD3 | sem identidade na CVM |  |
| OBTC3 | sem identidade na CVM |  |
| PLAS3 | sem identidade na CVM |  |
| WDCN3 | sem identidade na CVM |  |
| ANIM3 | setor a evitar (§8) | §8: educação superior privada (receita dependente de crédito estudantil) |
| AZUL3 | setor a evitar (§8) | §8: aviação |
| CASH3 | setor a evitar (§8) | §8: tecnologia sem lucro (lucro mediano <= 0) |
| COGN3 | setor a evitar (§8) | §8: educação superior privada (receita dependente de crédito estudantil) |
| CSED3 | setor a evitar (§8) | §8: educação superior privada (receita dependente de crédito estudantil) |
| IRBR3 | setor a evitar (§8) | §8: resseguro (um evento zera anos de lucro) |
| SEER3 | setor a evitar (§8) | §8: educação superior privada (receita dependente de crédito estudantil) |
| VTRU3 | setor a evitar (§8) | §8: educação superior privada (receita dependente de crédito estudantil) |
| YDUQ3 | setor a evitar (§8) | §8: educação superior privada (receita dependente de crédito estudantil) |

**Já analisadas no hall (41; ver `03`):** ABCB4, ABEV3, B3SA3, BBAS3, BBDC4, BBSE3, BRBI11, BRSR6, CMIG4, CPFE3, CPLE3, CSMG3, CXSE3, EGIE3, FLRY3, GGBR4, HYPE3, ISAE4, ITSA4, ITUB4, KEPL3, KLBN11, LEVE3, PETR4, PRIO3, PSSA3, RANI3, RECV3, SANB11, SAPR11, SBSP3, SLCE3, SMTO3, SUZB3, TAEE11, TIMS3, UGPA3, UNIP6, VBBR3, VIVT3, WEGE3.

## 8. Como pedir uma triagem nova

> "Rode a triagem (`cd ferramentas && python -m triagem.rodar`) e me diga quais da fila valeriam o prompt completo."

Cada análise completa parte das pendências da seção 2 e usa o `02-prompt-analise-completa.md` (v4: o **dossiê**; no Claude Code,
`cd ferramentas && python -m dossie.gerar <TICKER>` gera o anexo mecânico). O veredito só existe depois dele — e entra no registro
prospectivo com `python registro_prospectivo.py --dossie` (`origem` "dossie"; ticker que também está no hall não colide).
Dossiês aprovados em 07/10/2026: BLAU3, CMIN3 (ambos NÃO CONCLUSIVO) e HYPE3 (CARA).
