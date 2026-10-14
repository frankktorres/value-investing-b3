# Sensibilidade das premissas provisórias (B13: AUD-57/60) e Ke dos alavancados (B14)
*14/10/2026 · só relatório e proposta; nada mudou no motor, na doutrina ou no golden. São hipóteses de método, não recomendação de investimento. Reproduzir: instanciar `Mercado` alternativo e chamar o motor de cada ticker de `universo.GRUPOS` (sem gravar golden). Mercado base de 02/10 (rf real 7,06%, π 6,46%); preços do snapshot vigente.*

## B13 — palavra sob mercado alternativo (AUD-57)
Mudam de palavra **5 dos 41** tickers; os outros 36 mantêm a palavra nos três cenários.

| Ticker | Base (central R$) | π 4% (Focus) | rf real −1 p.p. | rf real +1 p.p. |
|---|---|---|---|---|
| EGIE3 | JUSTA (28,77) | RADAR (34,44) | JUSTA (32,11) | CARA (26,04) |
| ISAE4 | NÃO CONCLUSIVO (25,78) | RADAR (33,08) | JUSTA (28,20) | CARA (23,74) |
| LEVE3 | NÃO CONCLUSIVO (36,31) | JUSTA (36,05) | RADAR (40,33) | NÃO CONCLUSIVO (32,79) |
| SMTO3 | CARA (14,68) | CARA (13,75) | NÃO CONCLUSIVO (17,66) | CARA (12,14) |
| UNIP6 | CARA (47,32) | CARA (45,57) | JUSTA (52,85) | CARA (42,63) |

Leitura: a palavra das financeiras/regulados (EGIE3, ISAE4) é a mais sensível ao mercado; π 4% é o cenário mais favorável. Uma coluna "palavra sob mercado alternativo" no golden (proposta do AUD-57) custaria 3 campos por ticker; **proposta:** gerar este quadro no `rodar_tudo.py` como saída informativa, fora do golden (decisão reversível, não aplicada).
**AUD-60:** BBSE3 e CXSE3 seguem com QUAL(4,3,3,3,3) e solidez 8,0 arbitradas; só se resolve no dossiê de cada uma (B08/Frank decide a ordem).

## B14 — Ke dos muito alavancados
Ke real hoje (Hamada, pesos no ponto fixo, Kd sintético): KLBN11 **54,7%** (nominal 64,7%; D/E de peso 11,4×, DL/EBITDA 3,4×), SUZB3 26,2%, SLCE3 23,3%, SMTO3 22,4%, RANI3 22,1%, VBBR3 19,0%, UGPA3 16,2%; demais ≤ 15,6% (PETR4 13,9%). O "77%" do brief é de antes da v2.6; KLBN11 é NÃO CONCLUSIVO e não decide nada.
Risco: Ke alto derruba o DCF e favorece "CARA" em SUZB3, SMTO3, RANI3 por efeito da estrutura de capital, não do negócio (Hamada re-alavanca beta pelo D/E de mercado; dívida em R$ com Kd sintético ~15–19%).
**Proposta (não aplicada; mudar doutrina exige decisão em `DECISOES.md`):** (1) teto/alarme: sinalizar Ke real > 20% como "Ke extrapolado" no dossiê; (2) mostrar o central também com beta limitado (ex.: teto de D/E de peso 3×) como sensibilidade; (3) KLBN11 permanece sem palavra enquanto o ponto fixo tiver D/E > 5×.
