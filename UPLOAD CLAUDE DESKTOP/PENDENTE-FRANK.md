# PENDENTE-FRANK
*A rotina escreve aqui só o que trava em decisão, senha, dinheiro ou apagar dados. Frank: responda na linha e mova para `DECISOES.md`. Itens do `BACKLOG.md` tipo "decisão Frank" estão resumidos aqui.*
*O que é do Frank (CLAUDE.md, "Quem decide"): mudar palavra (motor, doutrina, régua, golden), aceitar risco que o `oraculo` bloqueou, gastar dinheiro, apagar/reescrever histórico, mudar o `00-DNA.md`, liberar config de qualidade/travas (`MESA_LIBERA_CONFIG`), senha/chave. Toda pergunta leva **recomendação + porquê em 1 linha**; quem registra segue em outra tarefa.*

## Abertas
| # | Pergunta | Opções / recomendação | Backlog | Desde |
|---|---|---|---|---|
| 16 | **Série anual: usar a DFP reapresentada?** (B45, achado E2) A série anual pega cada exercício da DFP original; quando a empresa reapresenta (operação descontinuada, erro, mudança de política), o motor usa o número velho. Afeta 18 do hall/dossiês (receita ou EBIT > 0,5%) → **muda golden** | **Recomendo sim, com regra:** usar o comparativo da DFP seguinte (como o AUD-21 já faz no LTM), exceto quando a diferença vier de operação descontinuada que depois foi desfeita (EMBJ3 2018) — a regra e a lista dos 18 vão a um pré-registro antes de regravar o golden. Responda "ok #16" ou "não #16" | B62 | 26/11 |
| 4 | Orçamento mensal; SaaS só seu ou de terceiros; objetivo acadêmico; agente de sexta ainda roda?; fonte paga; licença do código | Ver Brief §11 | B07 | 10/10 |

## Só do Frank (a rotina nunca faz)
- Executar qualquer compra ou venda (inclui a posição em ITSA4, acima da saída).
- Senhas, tokens e chaves; apagar dados.
- Temporada 3T26 e monitor de sexta rodam na máquina dele (dados fora do git).

## Respondidas
- **26/11 — #18 (rede da nuvem):** feito pelo Frank → ambiente "VALUE B3" em Limitado, com `*.cvm.gov.br`, `*.b3.com.br`,
  `api.bcb.gov.br`, `www.tesourotransparente.gov.br`, `fred.stlouisfed.org`, `statusinvest.com.br` e `www.gov.br` (o único que
  faltava); o pré-voo da noite confere em `/tmp/mesa_prevoo_rede.json`.
- **26/11 — #17 (piso da B37):** "ok #17" → `.githooks/piso_testes.json` de 1279 para 1399 (contagem do master desde 700f17b); o hook só deixa subir.
- **26/11 — #15 (texto do DNA):** "ok #15" → DNA §4 linha (a) marcada FECHADA (#14) e §3 com "causa aberta: (b)"; versão anterior em `_historico/2026-11-26 DNA antes do #15/`.
- **25/11 — #13 (trava de ordem):** "ok #13 A" → exceção pontual em `ferramentas/oraculo/ordem.py` (SHA completo de 2c7c87a + `{docs/b57/FONTES-B57.md}`), com canários em `tests/test_oraculo_ordem.py`; a B57 vai ao `master` → `DECISOES.md`, `09`.
- **25/11 — #14 (causa (a)):** "ok #14" → causa (a) do DNA §4 fechada "como está, com motivo" (Ke > 30% sai NÃO CONCLUSIVO pela H2 e é medido no M1); segue para (b) e (c) → `DECISOES.md`, `09`; texto do DNA §3/§4 a atualizar.
- **25/11 — #12 (B46 + B35):** B46 **sim**; B35 **não** (a B39 corrigida não disparou; fica até o HOLD-OUT 2) → `DECISOES.md`, `BACKLOG.md`.
- **22/10 — #10 (contraste, N5):** (a) contornos de chip ficam como estão; o chip já leva palavra e glifo (WCAG 1.4.11 não se aplica a contorno de reforço) → `DECISOES.md`.
- **21/10 — #8 (B26):** (a) sem controlador nem acordo no FRE = razão válida → `DECISOES.md`.
- **21/10 — #9 (§7):** "ok §7" → doutrina 2.6.1, casos com ano e fonte; nenhum carimbo sai → `DECISOES.md`, `09`.
- **21/10 — #7 (EGIE3):** lido nos ZIPs (nota A): "UBP de 2024" era a venda da TAG (DFP 2024, 3.04.04.02, R$ 1.336,1 mi); a repactuação do UBP é do 2T26 (3.06.01.01, R$ 1.921,5 mi bruto). Rótulos e carimbo corrigidos; nenhum número mudou → `09` de 21/10.
- **19/10 — #1 (B04):** sem mínimo/máximo nem limite de queda; carteira guiada pela palavra; meta de renda mensal (valor fora do git) → `DECISOES.md`.
- **19/10 — #5 (B08):** "você escolhe" → ALLD3, FESA4, SHUL4, VLID3 → `DECISOES.md`.
- **14/10 — #2 (B05):** exigir razão não vazia no motor; razões entram no dossiê → `DECISOES.md`, missão B24.
- **14/10 — #3 (B06):** critério contínuo + comparador = média do hall + uma linha por (ticker, rodada) → `DECISOES.md`, missão B25.
- **14/10 — #6 (B18/B19):** backtest e 2º comitê seguem parados → `DECISOES.md`.
