# TRIAGEM PRELIMINAR E FILA DE ANÁLISE

## 1. O filtro de 7 critérios (entra com ≥ 5)

| # | Critério | Régua |
|---|---|---|
| 1 | Preço | P/L ≤ 10 (≤ 7 conta como ✓✓) |
| 2 | Patrimônio | P/VP ≤ 2, **ou** ≤ ROE/10 |
| 3 | Provento recorrente | Pagou em ≥ 9 dos últimos 10 anos **e** DY 12m ≥ 5% |
| 4 | Rentabilidade | ROE ≥ 15% (média, não pico) |
| 5 | Balanço | DL/EBITDA ≤ 2x ou caixa líquido |
| 6 | Moat | Vantagem identificável e mensurável |
| 7 | Dono | Sem poder discricionário adverso; dividendo pago no ano |

**Por que P/VP ajustado ao ROE:** exigir P/VP ≤ 1 reprovaria Odontoprev (P/VP 6, ROE 45%), Ambev (2,8) e WEG (10). Quem tem ROE de 45% nunca negocia a 1x book.

**Limite da triagem — regra dura:** ela define **a fila**, nunca o veredito. Prova: LEVE3 passou 7/7 e a análise completa deu JUSTA/CARA; UNIP6 passou 5/7 e a análise completa deu ARMADILHA. O filtro não vê queima de caixa, normalização de ciclo nem alavancagem embutida no ROE.

---

## 2. Fila atual (07/09/2026)

### Já analisadas com o prompt completo
LEVE3 (JUSTA/CARA) · EGIE3 (CARA) · UNIP6 (ARMADILHA) · GGBR4 (RADAR)

### Prioridade 1 — pendentes

| Ticker | Setor | Por que está na fila | O que a análise precisa resolver |
|---|---|---|---|
| **ODPV3** | Saúde odontológica | Caixa líquido, ROE 45%, payout ~100%, DPA crescente desde 2010 | P/L 14 é caro? Bradesco como controlador e canal ao mesmo tempo (V4) |
| **DIRR3** | Construção (MCMV) | ROE 30%+, caixa líquido, DY ~7% | Dependência do MCMV é moat ou risco político? Free float e tag along |
| **ALUP11** | Transmissão | TIR real ~12% (vs 6,5% da Taesa), menos dívida, greenfield | Repetir o teste TIR real vs IPCA+ que reprovou a Taesa |

### Prioridade 2 — pendentes

| Ticker | Setor | Ressalva a resolver |
|---|---|---|
| **BRAP4** | Holding (Vale) | SOTP e desconto de holding, como em ITSA4; mono-ativo |
| **VULC3** | Calçados | Só paga desde 2020 — o dividendo é política ou humor do dono? |
| **GRND3** | Calçados | Renda pura sem dívida, mas crescimento zero: é armadilha de caixa? |

### Descartadas na triagem

| Ticker | Motivo |
|---|---|
| AXIA3 (ex-Eletrobras) | V2 consumado (MP 579) + contingência do empréstimo compulsório |
| AURE3 | Prejuízo pós-AES, dívida alta, sem dividendo relevante |
| TOTS3, RENT3, MILS3 | Compounders com DY 2–3%: Fisher compraria, carteira de renda não |
| MULT3, ALOS3, VALE3, SBSP3(*), MOTV3, PASS3, FESA4, CURY3, LREN3, MDIA3, GMAT3, NEOE3 | Reserva: falham em preço, histórico curto ou payout não coberto |

(*) SBSP3 acabou entrando no hall por decisão do investidor e foi analisada no lote 2.

---

## 3. Setores ainda ausentes do hall

| Setor | Candidato natural | Observação |
|---|---|---|
| Shopping centers | MULT3, ALOS3 | ALOS3 tem payout de 154% (venda de ativos) — cuidado |
| Rodovias | MOTV3, ECOR3 | Alavancagem 3–4x é o obstáculo |
| Gás natural regulado | PASS3 (Comgás) | Histórico curto; reavaliar em 2027 |
| Mineração | VALE3, CMIN3 | Vale: P/L normalizado e Samarco/Brumadinho |
| Varejo alimentar | GMAT3 | Yield baixo; entra só se passar de 5% |
| Tecnologia | TOTS3 | Yield 2%: fora da carteira de renda por definição |

---

## 4. Como pedir uma triagem nova

> "Faça uma varredura por [setor / critério] e me diga quais valeriam o prompt completo."

A resposta deve trazer: tabela com os 7 critérios preenchidos por ticker, score, o que falha, e a fila sugerida com a justificativa do que **cada análise completa precisa resolver** — nunca um veredito.
