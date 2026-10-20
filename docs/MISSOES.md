# MISSOES
*Fila de trabalho da rotina autônoma. Cada missão: executável só com o GitHub, uma por turno, com "pronto quando" verificável. Ao terminar, mover para "Feitas" e registrar em `RELATORIO-DIARIO.md`. Fonte: `BACKLOG.md` (tipo executável).*

## Próximas (ordem de prioridade)
~~1. **B09** — Conferir se `09-diario-de-decisoes.md` e `PROJECT_BRIEF.md` §12 registram a rodada de 10/10 (boletim `2026-10-10-monitor`, pastas em `_historico/`); completar o que faltar. *Pronto quando:* uma linha em cada, `pytest` dos módulos tocados verde.~~
~~2. **B10** — AUD-49: lock de dependências (`requirements.txt` já fixa 6 libs; avaliar `requirements.lock`/hashes) e config da carteira fora do código. *Pronto quando:* clone limpo roda `pip install -r requirements.txt` e `cd ferramentas && python -m pytest --ignore=backtest -q` verde.~~
~~3. **B12** — Onda 4 textual: AUD-96, 64, 65, 48, 105, 87.~~ (feita 14/10; AUD-64 vira B23)
~~4. **B13/B14** — Sensibilidade das premissas provisórias (AUD-57/60) e Ke dos alavancados (KLBN11). Só relatório + proposta; mudar doutrina só com decisão registrada em `DECISOES.md`.~~ (feita 14/10: `docs/SENSIBILIDADE-B13-B14.md`)
~~5. **B24** — AUD-41: `filtros_1a4` exige razão não vazia para desconto de controlador; registrar as 29 razões (só com fonte A/B; sem fonte → marcar "sem razão documentada", não inventar). *Pronto quando:* teste novo + suíte verde, golden explicado ou intacto, registro no `09`.~~ (feita 14/10)
~~6. **B25** — AUD-32/98/99: ajustar `registro_prospectivo.py` ao pré-registro decidido (critério contínuo, comparador = média do hall, uma linha por ticker×rodada). *Pronto quando:* testes verdes e registro no `09`.~~ (feita 14/10)
7. **B11** — StatusInvest: termos em `statusinvest.com.br/condicoes-de-uso` dão 403 — tentar de novo ou o Frank cola o texto (B3 feita 14/10).
8. **B26** — Razão do desconto de controlador com fonte A (FRE) para os 28 com `SEM_RAZAO`; cada uma baixa a contagem do `test_b24`.

~~8b. **B27** — fatia 2 do relatório (quali + PDF).~~ (feita 19/10; faltam fatia 3 = B08/ALLD3 e fatia 4 = adversário + verificador-fonte)

~~9. **B08** — Dossiês FESA4, SHUL4, VLID3.~~ (feita 19/10, ver Feitas)
~~9b. **Fatia 4 do relatório** — `adversario` + `verificador-fonte` no pacote (inclui: margem normalizada da ALLD3 4,0% vs EBIT recorrente 2025 ~3,1%; cenários do desconto de controlador estimados), README, DECISOES.~~ (feita 19/10)
~~9c. **B15 / fase 3, fatia 2** — DPA/JCP StatusInvest → API B3 nas não financeiras do lote.~~ (feita 20/10, ver Feitas)
9f. **B15 / fatia 4** — financeiras (L2 utilities → ITSA4/EGIE3 → L1 bancos/seguradoras; conferir códigos do DFP de IF no ZIP real antes): `vpa`, `lpa_12m`, `roe_lp`, `roe_inicio` da CVM; DPA/JCP/anos pagos da B3; `pl_hist` CVM+COTAHIST; `payout` medido (mediana 5a), valor diferente só como julgamento declarado. Palavra pode mudar → `09` por ticker. Depois da temporada 3T26 (commit próprio, B01). Junto: o relatório das financeiras (`relatorio/quali.py` → `dossie.base.proventos_b3_legado`) e a renda de 12 meses da carteira (`relatorio/renda.py._sem_repeticao`) ainda usam a regra do AUD-23 (linha igual conta uma vez) — classificar os grupos de linhas iguais das financeiras e da carteira na DMPL (`proventos_hall.GRUPOS_CONFERIDOS`) e trocar pelas regras do hall (fatia 2b, 09 de 20/10).
9g. **B15 / fatia 5** — trava final: StatusInvest só para datas (defasagem); zero `lote (digitado)` em campo de dado do central.
10. **B01** — Temporada 3T26: a tarefa de sexta já detecta o ITR (`monitor/temporada.log` + boletim); quando aparecer ticker com 3T26, rodar `temporada.py --gravar` + `rodar_tudo.py --motivo`.

## Em andamento
(nenhuma)

## Feitas
- **B15 / fase 3, fatia 3** (20/10): preço (`precos_hall.preco`), receita de meio PETR4/PRIO3/RECV3/GGBR4/UNIP6 (CVM × EIA/BLS, `verificador-fonte`), alíquota TIMS3 (CVM + nota 8.d), g1 WEGE3 (CVM + B3, 3 parcelas do extraordinário), NAV SLCE3 (fato relevante 15/06/2026: 27,12 → 27,72), `pl_hist` das NF por `pl_historico` (CVM + COTAHIST; SMTO3 em março; janela 2020–25, B30) e `preco_minerio` no insumo do CMIN3 — tudo em `insumos_a`; 19/19 NF do lote com central A/B (eram 11), C do lote 158 → 134; golden: 11 mudanças em 10 tickers (Bogle e a âncora de reprodução da SLCE3), 0 palavras; tabela no `09`.
- **B15 / fase 3, fatia 2b** (20/10): `dossie.base.proventos_b3` → `proventos_hall.dpa_jcp` (classe PN da FESA4/SHUL4, parcelas × repetição conferidas na DMPL — 7 grupos novos, todos parcelas —, restituição de capital fora, eventos do FRE: SHUL4 2018 e 2021); `base.eventos` (B3 + FRE) no `pl_hist` e na diluição; diluição com a escala das ações (VLID3 308% → 2,5% a.a.); `PARES_CONFERIDOS` exige o produto; 0 palavras/centrais; SHUL4 15/10 gestão 0 → 1 (fixado no teste); tabela antes/depois no `09`.
- **B15 / fase 3, fatia 2** (20/10): `proventos_hall.py` — DPA/JCP das 21 NF dos lotes da API da B3 (classe, tipos fechados, data-com ≤ preço, eventos B3 + FRE, parcelas × repetição conferidas na DMPL); saíram `lote4.corrigir_proventos` e o ajuste aproximado GGBR4/UNIP6; golden regravado (15 mudanças em 7 tickers, só DY/Bogle/vence RF/nota geral; 0 palavras); tabela B3 × StatusInvest no `09`.
- **B08/FESA4, SHUL4, VLID3** (19/10): fichas + coleta CVM 2016–25 + insumos A/B (FRE 2026, DFP, IPE) + mercado de 15/10; vereditos 15/10: **FESA4 RADAR** (6,23 × central 7,62, P/C 0,82), **SHUL4 CARA** (5,00 × 3,90, P/C 1,28), **VLID3 CARA** (18,85 × 16,61, P/C 1,14); `relatorio` gera PDF dos três; suíte 546 passed; golden intacto. B08 fechada (4 de 4).
- **Fatia 4 do relatório (9b)** (19/10): adversário (4 defeitos corrigidos, 2 aceitos) + verificador-fonte (só OE/Buffett confere em fonte A; Graham/Bazin/EPV nota C; cortes do quali = heurística); margem ALLD3 2025 conferida na CVM; suíte 543 passed; palavra e golden intactos.
- **B08/ALLD3** (19/10, fatia 3): ficha + coleta CVM 2019–25 + insumos A/B + mercado de 15/10; veredito ALLD3 15/10 **BARATA** (preço 6,30, central 14,91, P/C 0,42; notas moat 0, gestão 1, controlador 5, ciclo 3, fisher 1; desconto 1%); `relatorio ALLD3` gera PDF; suíte 543 passed; golden intacto.
- **B27** (19/10): `relatorio/quali.py` (6 blocos) + `render_pdf.py`; `relatorio BBSE3` e `HYPE3` geram PDF; suíte 542 passed, 1 skipped; golden intacto.
- **B24** (14/10): motor exige razão no desconto de controlador; 28 "sem razão documentada", LEVE3 com fonte A; nenhuma palavra mudou (33 CARA, 5 NC, 3 JUSTA).
- **B25** (14/10): pré-registro contínuo (IC de postos, média do hall, 1 linha por ticker×rodada) em `registro_prospectivo.py`.
- **B23** (14/10): tabela de P/C por premissa da PETR4 no gerador do lote 5; PDF não reemitido (outros campos informativos mudaram desde 09/10).
- **B15** (14/10): `docs/PREMISSAS-B15.md` (inventário + proposta; nada movido).
- **B11** (14/10): termos da B3 lidos (nota A) em `docs/TERMOS-DE-USO-FONTES.md`; StatusInvest segue 403.
- **B13/B14** (14/10): relatório `docs/SENSIBILIDADE-B13-B14.md` (5 de 41 mudam de palavra sob mercado alternativo; Ke KLBN11 54,7%). Só proposta.
- **B11** (14/10) **parcial/bloqueado pela rede**: `b3.com.br/pt_br/termos-de-uso` devolve erro 500 e `statusinvest.com.br/termos-de-uso` 403 (proxy/site). Sem fonte nota A lida, nada afirmado; segue aberto no BACKLOG.
- **B12** (14/10): AUD-96/65/87/48/105 corrigidos, citados no `09`; AUD-64 → B23. Suíte 473 passed, 19 skipped, golden intacto.
- **B09** (13/10): conferido — `09` (10/10, linhas 598–607 e 610+) e brief §12 já registravam boletim `2026-10-10-monitor` e pastas em `_historico/`; nada a completar. Suíte: 473 passed, 19 skipped.
- **B10** (13/10): `carteira_tickers.json` (só tickers) lido por `monitor_semanal.py`; `requirements.lock` criado (hashes não adotados, ver `DECISOES.md`). Suíte verde. Clone limpo em Python 3.13 instalou e rodou; 3.14 não testado na nuvem.

## Passagem de turno
*A skill `/fechar` reescreve esta seção: o que ficou pendente, onde parou, próximo passo.*
- 13/10/2026: infraestrutura da rotina criada (hooks, backlog, skill). Nada em andamento.
- 14/10/2026 (fim do dia): B24, B25, B23, B15 e B11 (parte B3) feitas e publicadas (f03636e, 9bde979, 8d780f8); nada em andamento. Próximas executáveis: B11 (StatusInvest, 403), B26 (FRE nota A para os 28 `SEM_RAZAO`). Marco seguinte é local: ITR 3T26 (`temporada.py`, B01), que também reemite o PDF do lote 5 com a tabela da B23.
