# Temporada 3T26 — 2026-10-27

- ZIP lido: `itr_2026.zip` sha256 `eaac6b78aaf0dc38f337158480e401f2606057760694dd37c8d16da784f71881`.
- Publicaram o ITR de 3T26: **1** (WEGE3).
- Ainda sem ITR de 3T26: 30 (ABEV3, B3SA3, CMIG4, CPFE3, CPLE3, CSMG3, EGIE3, FLRY3, GGBR4, HYPE3, ISAE4, ITSA4, KEPL3, KLBN11, LEVE3, PETR4, PRIO3, RANI3, RECV3, SAPR11, SBSP3, SLCE3, SMTO3, SUZB3, TAEE11, TIMS3, UGPA3, UNIP6, VBBR3, VIVT3).
- Fora da coleta CVM (premissas manuais/StatusInvest; não mudam com o ITR): ABCB4, BBAS3, BBDC4, BBSE3, BRBI11, BRSR6, CXSE3, ITUB4, PSSA3, SANB11.

## Resultado

8 mudanças em 1 tickers; **0 trocas de palavra**.

### Todas as mudanças (central, âncoras, P/C…)

| Ticker | Campo | Antes | Depois | Por quê (LTM) |
|---|---|---|---|---|
| WEGE3 | Bogle nominal | 0.1312 | 0.1329 | receita +1.5% · margem EBIT -0.2 p.p. · dívida bruta -25.9% · lucro +0.3% |
| WEGE3 | âncora DCF (3 cenários) | 11.0863 | 10.0902 | receita +1.5% · margem EBIT -0.2 p.p. · dívida bruta -25.9% · lucro +0.3% |
| WEGE3 | âncora EPV | 10.0517 | 10.1635 | receita +1.5% · margem EBIT -0.2 p.p. · dívida bruta -25.9% · lucro +0.3% |
| WEGE3 | âncora Owner Earnings ÷ (Ke − g) | 11.0815 | 11.6092 | receita +1.5% · margem EBIT -0.2 p.p. · dívida bruta -25.9% · lucro +0.3% |
| WEGE3 | nota geral | 5.2045 | 5.1217 | receita +1.5% · margem EBIT -0.2 p.p. · dívida bruta -25.9% · lucro +0.3% |
| WEGE3 | cobertura de juros | 37.3465 | 30.3555 | receita +1.5% · margem EBIT -0.2 p.p. · dívida bruta -25.9% · lucro +0.3% |
| WEGE3 | central | 11.0815 | 10.1635 | receita +1.5% · margem EBIT -0.2 p.p. · dívida bruta -25.9% · lucro +0.3% |
| WEGE3 | P/C | 4.6429 | 5.0622 | receita +1.5% · margem EBIT -0.2 p.p. · dívida bruta -25.9% · lucro +0.3% |

### PDFs a reemitir

Lotes com ticker afetado: `python gerar_pdf_lote4.py`.

---
O golden **não** é regravado por esta ferramenta. Para aceitar a coleta nova: `python temporada.py --gravar` (não baixa; recusa se o ZIP do cache não for o deste boletim) e depois `python rodar_tudo.py --motivo "3T26: …"` (o motivo vai para `tests/golden_log.md`). Antes da palavra nova valer, `05-prompt-reavaliacao` para quem trocou.
