# Diagnóstico do motor — 22/10/2026 (somente leitura; nenhuma palavra mudou)

Pergunta: "só 1 de 40+ é comprável" é rigor legítimo ou erro estrutural?
**Veredito: misto, com erro estrutural de calibração dominante.** A margem de 30% não é o gargalo; o gargalo é o
**nível do valor central**, que sai perto de metade do preço de mercado para quase todo o hall.

Evidência reproduzível: `sens.py`, `sens2.py`, `sens3.py` (nesta pasta) leem os `lote*.py`, `hall.json` e
`mercado_vigente.json` e chamam `motor_*.avaliar` sem gravar nada. Saída em `sens_out.json`. Baseline conferido
(ITUB4 2,76; WEGE3 4,43). **Números a reconferir no chat de execução antes de qualquer decisão.**

## 1. Funil (hall, preço de 22/10, 47 empresas)
BARATA 1 (ALLD3, P/C 0,42) · RADAR 1 (FESA4 0,82) · JUSTA 4 · CARA 36 · NÃO CONCLUSIVO 5.
Dos 41 com P/C: mediana **1,86** (financeiras/reguladas 2,17; demais 1,49); 5 acima de 3×.
Exemplos: WEGE3 central R$ 11,08 vs preço 49,09 (4,43×); ITUB4 17,54 vs 48,35 (2,76×); SBSP3 7,05 vs 31,87 (4,52×).
Triagem (06): 110 avaliadas, 5 passam no portão A; 17/20 da fila reprovam no Q1 (ROIC real > WACC real ≥ 70% dos anos).

## 2. Causas, por peso (arquivo:linha)
1. **Fluxo subestimado (maior resíduo).** Mesmo com Ke real 9% a mediana fica em 1,40.
   - Gate de crescimento `motor_nao_financeiras.py:721-722`: g = 1% real só se min(ROIC contábil, ROIC reposição)
     > WACC **nominal**; senão g = 0. Compara ROIC contábil (quase nominal) com WACC nominal 16–19% → g = 0 para quase todos.
   - WEGE3 com ROIC real > WACC real em só 4 de 10 anos → **suspeito de erro de cálculo** (WEG é compounder de ROIC alto; conferir).
   - Bancos/reguladas: ROE_lp = mediana 10 anos (ITUB4 17,6% vs 21,5–24% atual) < Ke nominal 19,3% → P/VP < 1 por construção.
   - DDM e P/VP justificado usam o mesmo ROE e Ke: dispersão ≈ 1,01 — âncoras **não independentes** (a mediana não diversifica erro).
2. **Taxa.** Ke real = rf 7,06% (NTN-B 2050 spot tratada como perpétua) + 5 p.p. fixos, beta 1 para todos (`motor_financeiras.py:15`).
   - Hamada sobre **dívida bruta** e **E do próprio modelo** (ponto fixo, `motor_nao_financeiras.py:632-663`): realimentação →
     KLBN11 Ke 65% (D/E 11,4), SUZB3 34% (D/E 3,5 no modelo vs 1,8 a mercado). Artefato, não risco.
   - π implícita 6,46% (vértice 10a) vs Focus 3,5–4,3%; rf em 2050 e π em 10a: horizontes diferentes.
   - Hipótese a conferir: o NTN-B já embute o spread de default soberano; Damodaran manda tirá-lo da rf local antes de somar
     ERP + CRP. Para beta 1 o nível ~12% real pode ser defensável; o problema é beta único + Hamada + fluxo.
3. **Empilhamento de conservadorismo.** Preço ≤ 0,70 × (fluxo normalizado para baixo ÷ 12% real, g = 0) ⇒ earnings yield
   real ≈ 17% (P/L ≤ 6). Mediana 10a, OE com capex de manutenção, ROIC pelo menor, 34% de IR sem fonte, desconto de controlador.
   Cada uma defensável; juntas deslocam o central. Só existem regras que **rebaixam** a palavra (`01:44`); nenhuma sobe.
4. **Ponto, não faixa.** Incerteza vira veto (dispersão > 1,8×) em vez de intervalo (Klarman: valor é faixa).

Sensibilidade (38 tickers, P/C mediana / nº ≤ 0,90 / nº ≤ 1,10): base 2,03/0/2 · rf 5% 1,53/2/6 · prêmio 3 p.p. 1,54/2/6 ·
Ke real 9% 1,40/6/11 · rf 4,5% + prêmio 4 p.p. 1,33/7/14 · π 4% 1,82/1/2 · sem Hamada (industriais) 1,85→1,59.
Margem 25% em vez de 30%: **nenhuma palavra muda**.

## 3. Bugs e inconsistências concretas
- LEVE3: `hall.json` exibe JUSTA com central nulo; motor atual dá NÃO CONCLUSIVO (central 38,45) — palavra velha exibida como vigente.
- Zero silencioso: `motor_nao_financeiras.py:176-177,214,250,273-277` (`v(d,"caixa",0)` etc.) e `montar_series.py:48`
  (`e["valor"] or 0`) — dado ausente vira 0 em vez de NÃO CONCLUSIVO.
- Hamada com dívida bruta penaliza quem tem caixa (`:646`).
- Trava de coerência Bogle só atua sobre JUSTA, não sobre CARA (`:988`).
- Payout fixo no DDM vs g terminal limitado a 8,6% (`motor_financeiras.py:266,279`).
- Hall mistura palavra de 02/10 com P/C de hoje.

## 4. Doutrina vs mestres (lacunas)
Cobre bem: margem de segurança, qualidade de lucro/caixa, controlador, Ke real sem misturar nominal, DCF reverso, ciclo,
yield sustentável. Lacunas: (crítica) faixa de valor e cenário de estresse/perda permanente (Klarman, Marks, Pabrai);
(crítica) compounders estruturalmente impossíveis de comprar — viola Buffett/Munger/Fisher/Miller ("empresa maravilhosa a
preço justo"); (importante) NCAV/valor de ativos (Graham, Schloss); Beneish/Sloan só exibidos, não bloqueiam; cronograma e
moeda da dívida não lidos das notas; crescimento de DPA 10a e TRR de Neff ausentes; recompra/diluição não rastreadas;
qualitativo mistura "sem evidência" com "evidência negativa" (Fisher 15 pontos).

## 5. Testes hoje (1016 passam, 0 pulam localmente)
Golden prova **estabilidade**, não correção (congela erro). Correção só onde a conta foi refeita à mão
(`test_aud27_31_formulas.py`, `test_aud17_ddm_analitico.py`). Não há: propriedades/metamórficos, teste diferencial,
âncora externa de valor, reconciliação BP (ativo = passivo + PL) ou DFC (fecha com variação de caixa), mutation testing,
matriz doutrina→função→teste. O portão do backtest mediu proxy vs motor (não motor vs realidade) e falhou (70,7% / 0,34).
