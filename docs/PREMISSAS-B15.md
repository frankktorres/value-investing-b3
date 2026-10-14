# B15 — premissas digitadas e mercado em data fixa (14/10/2026)

**Escopo:** só relatório e proposta. Nenhum código foi movido e nenhuma palavra mudou. A decisão está em `DECISOES.md`.

## O que já está em dados
| Insumo | Onde | Data | Coleta |
|---|---|---|---|
| rf e π | `ferramentas/mercado_vigente.json` (AUD-78), conferido contra `dados/mercado.json` | 02/10/2026 | `coletar_macro.py` / `coletar_macro_fred.py` (local) |
| Preço de fechamento | `dados/precos_hall_2026-10-02.csv` (COTAHIST); `tests/test_precos_hall.py` confere | 02/10/2026 | `precos_hall.py` (local) |
| DFP/ITR (receita, EBIT, capex, ações…) | `dados/cvm_series.json` + ZIPs da CVM | DFP 2025 + LTM 2T26 | `coletar_cvm.py`, `temporada.py` (local) |
| Proventos, ROE, DY | `dados/series_*.json`, `proventos_hall/` (StatusInvest, nota C) | 04–05/10/2026 | `coletar_statusinvest.py` (local) |

## O que continua digitado nos `lote*.py`
Inventário gerado com `dataclasses.fields` × default dos 41 tickers do `universo.GRUPOS`: **445 campos fora do default**, de 4 (RANI3) a 15 (TIMS3) por ticker. Uma parte já é calculada a partir de dados (`acoes()`, `jcp()`, `pl_hist()`, `receita_ep()`), mas o valor fica no código do lote.

| Classe | Campos (nº de tickers) | Natureza |
|---|---|---|
| **Mercado em data fixa** | `preco` (41, literal em 35 linhas); `DATA_BASE = "02/10/2026"` em `lote1_bancos.py` trava rf/π no dia do preço | Medido. O literal repete o CSV do snapshot. |
| **Medido e digitado** (financeiras) | `vpa`, `lpa_12m` (20), `dpa_medio_5a` (20), `jcp_share` (20), `pl_hist` (20), `prudencial` (6), `anos_pagos_10` (2) | Medido. Vários com nota C ou sem fonte (AUD-58/61). |
| **Julgamento da casa** | `roe_lp`, `roe_inicio`, `payout` (20); `g_real` (3), `g1_real`; `receita_meio` (6); `qualitativo` (41); `desconto_controlador` (41); `solidez_manual` (14); `anos_ciclo`/`janela_razao` (10); `outras_liquidas` (12); `capex_ciclico` (4); `defasagem_meses` (5); `aliquota*` (3); `horizonte_finito`, `sotp`, `reproducao_por_acao` | Premissa com razão escrita. Não é coleta: muda por decisão. |

## Proposta (não aplicada)
1. **Preço e data do mercado saem do lote.** Cada lote passa a ler `precos_hall.ler()` e `mercado.vigente()`, sem literal, e `DATA_BASE` vem de `precos_hall.PRECO_DATA`. Um pregão novo vira 1 CSV + 1 JSON. O golden muda só em `pc`/palavra, por causa do preço, e isso já é o que o monitor de sexta mede.
2. **Medidos e digitados vão para `dados/premissas_medidas.json`**, com fonte e nota por campo. Prioridade: os que a CVM dá (`vpa`, `lpa_12m` pela DFP/ITR). `dpa_medio_5a` sai da série de proventos.
3. **Julgamento da casa vai para `ferramentas/premissas/<lote>.json` versionado**, um registro por ticker com valor + razão + fonte + data, lido por um carregador único. O `lote*.py` fica só com regra e textos. É o que destrava o SaaS (B17): premissa vira dado auditável e editável sem mexer em código.
4. **Oráculo:** cada passo só entra com o golden **idêntico** (`rodar_tudo.py` sem `--motivo`). Uma migração por lote, um commit por lote, começando pelo lote 3 (menor, 7 tickers).
5. **Coleta periódica:** o Agendador já roda o monitor às sextas (B02). Acrescentar `coletar_macro` + snapshot de preço antes dele, gravando `mercado_<data>.json` e `precos_hall_<data>.csv`. A régua segue congelada até a temporada 3T26 (B01).

**Por que não foi movido agora:** são 6 lotes com textos que citam os mesmos números, e mover um lote só deixaria dois padrões convivendo. O SaaS está parado (B17) e a régua está congelada até o ITR do 3T26. Item 1 tem efeito imediato e é pequeno; os itens 2–3 são a migração grande.
