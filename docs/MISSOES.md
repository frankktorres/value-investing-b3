# MISSOES
*Fila de trabalho da rotina autônoma. Cada missão: executável só com o GitHub, uma por turno, com "pronto quando" verificável. Ao terminar, mover para "Feitas" e registrar em `RELATORIO-DIARIO.md`. Fonte: `BACKLOG.md` (tipo executável).*

## Próximas (ordem de prioridade)
*Fila da madrugada (Frank, 21/10 tarde), uma por turno, NESTA ORDEM: **N7 → N1 → N2 → N9 → N10 → N8 → N11 → N3 → N4 → N5**
(a ordem do texto abaixo não manda). N6 feita. Na nuvem não há `ferramentas/dados/`: teste que precisa de
dado bruto pula; teste novo usa fixture pequena. Nenhuma delas muda palavra, central ou golden — se mudar, parar e ir para `wip/auto`.*

**(FEITA 22/10) N1 — Higiene de docs (check-up 21/10).** Corrigir só texto:
- (a) `README.md`: doutrina v2.6 (linhas 2, 9, 50); 8 dossiês (+ALLD3, FESA4, SHUL4, VLID3, linhas 23 e 50); tela v0.2 com Hall/Empresa/Carteira/Monitor (linha 25).
- (b) `PROJECT_BRIEF.md`: §3 fonte Space Grotesk (linha 18); nº de testes atual (linha 37); tela v0.2 (linha 68); fatias 2b e 3 feitas (linha 71); "23 `SEM_RAZAO`" (linha 131). Guardar antes em `_historico/2026-10-21 brief/`.
- (c) `docs/BACKLOG.md`: B04 respondido; B08 feito; linhas B24–B31 para dentro da tabela; recontar o total; "HANDOFF existe em `docs/design/handoff-claude-code/handoff/`"; B15 com 2b e 3 feitas; incluir a tela v0.2 e os itens N1–N5 e D1–D5 deste check-up.
- (d) `03-hall-de-acoes.md`: cabeçalho v2.6; tirar "Candidata a sair: KLBN11" (já NC); a contagem 33/3/5 do `09` é das 41 (36 do hall + 5 fora) — escrever as duas na mesma linha.
- (e) `docs/RELATORIO-DIARIO.md`: mais nova em cima (a entrada da sessão do Frank de 14/10 está no fim).
- (f) `docs/design/handoff-claude-code/PROMPT.md:10`: caminho das capturas = `docs/design/handoff-claude-code/handoff/referencia/capturas/`.

*Pronto quando:* `grep -rn "v2\.5" README.md 03-hall-de-acoes.md` só acha histórico; contagem do BACKLOG = nº de IDs; `pytest --ignore=backtest -q` verde (nada de código mudou).

**(FEITA 22/10) N2 — Testes das regras sem cobertura (check-up 21/10).** Só testes novos, com fixture; código de motor intocado. Cobrir:
- desconto de controlador por cenários (`motor_nao_financeiras.py:827-831`: soma prob × perda, só âncora positiva);
- escala da nota de Preço (`motor_financeiras.py:178-192`, cada degrau);
- saída a 1,50× nunca em financeira (§9);
- DCF reverso `g_implicito` (`motor_nao_financeiras.py:853`: ida e volta preço → g → preço).

*Pronto quando:* testes verdes; golden intacto (`git diff --stat ferramentas/tests/golden.json` vazio); uma linha no `09`. Teste que acha defeito → não corrigir motor; registrar em `PENDENTE-FRANK.md`.

**N3 — Contrato liga o que o motor já calcula (fatia "sem fonte", parte 1).** Em `painel/contrato.py`:
- setor a partir de `backtest/motor/perfil.py` (o mesmo de `triagem/avaliar.py:21`);
- dividendo × JCP por mês no calendário (de `relatorio/carteira.py:139-142`);
- data de cada fonte a partir de `insumos_a.origem`;
- faixa baixo/alto do DCF a partir dos cenários pessimista/otimista (`motor_nao_financeiras.py:740`).

Os outros métodos seguem `null`. Probabilidade e impacto de risco ficam `null` (nenhum motor calcula; não inventar). Atualizar `docs/DECISOES.md` (linha de 20/10, conflito C).

*Pronto quando:* `painel/tests/test_contrato.py` cobre os 4 campos com fixture; `test_web_estatico.py` verde (sem cálculo no front).

**N4 — Tela Sistema** (`docs/design/handoff-claude-code/handoff/HANDOFF.md:52-53`, captura `06-sistema`). Contrato `web/dados/contrato/sistema.json` com:
- idade de cada dado (COTAHIST, CVM, proventos B3, monitor, temporada);
- último boletim do monitor e da temporada;
- data e motivo do golden;
- nº de testes da última suíte, se houver registro.

Front lê só o contrato. Tira o "Sistema em breve" do `index.html:27`.

*Pronto quando:* `test_contrato` e `test_web_estatico` verdes. Conferência visual fica para o Frank (dia).

**N5 — Contraste dos tokens (etapa 4 da tela v0.2, parte automática).** Teste que lê `ferramentas/painel/web/tokens.css` e calcula a razão de contraste WCAG dos pares texto × fundo nos temas claro e escuro.

*Pronto quando:* teste verde, ou a lista de pares abaixo de 4,5:1 (texto) / 3:1 (texto grande e UI) em `docs/PENDENTE-FRANK.md`, sem trocar cor sozinho (o visual é decisão do Frank).

~~1. **B09** — Conferir se `09-diario-de-decisoes.md` e `PROJECT_BRIEF.md` §12 registram a rodada de 10/10 (boletim `2026-10-10-monitor`, pastas em `_historico/`); completar o que faltar. *Pronto quando:* uma linha em cada, `pytest` dos módulos tocados verde.~~
~~2. **B10** — AUD-49: lock de dependências (`requirements.txt` já fixa 6 libs; avaliar `requirements.lock`/hashes) e config da carteira fora do código. *Pronto quando:* clone limpo roda `pip install -r requirements.txt` e `cd ferramentas && python -m pytest --ignore=backtest -q` verde.~~
~~3. **B12** — Onda 4 textual: AUD-96, 64, 65, 48, 105, 87.~~ (feita 14/10; AUD-64 vira B23)
~~4. **B13/B14** — Sensibilidade das premissas provisórias (AUD-57/60) e Ke dos alavancados (KLBN11). Só relatório + proposta; mudar doutrina só com decisão registrada em `DECISOES.md`.~~ (feita 14/10: `docs/SENSIBILIDADE-B13-B14.md`)
~~5. **B24** — AUD-41: `filtros_1a4` exige razão não vazia para desconto de controlador; registrar as 29 razões (só com fonte A/B; sem fonte → marcar "sem razão documentada", não inventar). *Pronto quando:* teste novo + suíte verde, golden explicado ou intacto, registro no `09`.~~ (feita 14/10)
~~6. **B25** — AUD-32/98/99: ajustar `registro_prospectivo.py` ao pré-registro decidido (critério contínuo, comparador = média do hall, uma linha por ticker×rodada). *Pronto quando:* testes verdes e registro no `09`.~~ (feita 14/10)
*QA de 21/10/2026 (5 frentes: motores, tela/servidor, nuvem/CLIs, dados × CVM/B3, fatos × FRE): N7–N11, na ordem do topo, na mesma regra (uma por turno; golden intacto, senão `wip/auto`).*

**(FEITA 22/10) N7 — Motor sem defesa contra dado inválido (ALTA preventiva; hoje os 47 tickers estão limpos).** NaN, ±inf, None ou ≤ 0 têm de virar recusa explícita (NÃO CONCLUSIVO ou `ValueError` com mensagem), nunca palavra ou elegibilidade em silêncio. Pontos reproduzidos pelo QA:
- `motor_financeiras.palavra` (`:86-92`): NaN vira CARA; 0, −1 e −inf viram BARATA.
- `precos_de_referencia` (`:97`): o guarda `central <= 0` não pega NaN.
- `entrada_parcial` (`:111`): NaN em pc, dispersão, notas ou central dá `(True, [])`.
- `descontar` (`:133`): aceita `desc` fora de [0,1].
- `media_qualitativa` (`:142`): aceita nota fora de 0–5 e NaN.
- `nota_preco` (`:192`): NaN dá 0 e −1 dá 10.
- `motor_nao_financeiras.central_de` (`:822`): NaN entra na mediana e o resultado depende da ordem.
- `qualifica_saida` (`:788`): aceita mais anos acima do que a série tem.
- `carimbos.de` (`carimbos.py:25`): falta `.strip().upper()`.
- `relatorio/montar.py:24`: falta `strip`.

*Pronto quando:* teste parametrizado com NaN/inf/None/0/negativo para cada função; golden intacto (`git diff --stat ferramentas/tests/golden.json` vazio); uma linha no `09`.

**N8 — Escala do nº de ações (MÉDIA, investigar primeiro).** A CVM informa a composição do capital em MIL. O `cvm_series.json` da TAEE11 tem 1.033.497 (o certo é 1,033 bi de ações = 344,5 mi units); `dossie/base.py` já corrige isso com q×1000 para a ALLD3. Rastrear se `acoes` da TAEE11 (e de quem mais vier em mil) chega a valor por ação (`lote2_energia.py:104` e o que mais ler `l["acoes"]`).

*Pronto quando:* relatório em `docs/QA-2026-10-21.md` com a lista dos tickers afetados e o efeito. Se chega ao valor: corrigir `coletar_cvm.acoes_em_circulacao`, com teste de fixture, mas SEM regravar `cvm_series.json` (isso é LOCAL, com o Frank) → registrar em `PENDENTE-FRANK.md`.

**(FEITA 22/10) N9 — Robustez do servidor e do front (MÉDIA).**
- `painel/servir.py:57-58`: bind exclusivo; o segundo `painel` na mesma porta tem de falhar com "porta em uso" (hoje no Windows sobem dois e há `ERR_CONNECTION_REFUSED` intermitente).
- `ui.js:58` / `app.js:185`: `hall.json` sem `fatores` dá TypeError e tela quase vazia → faixa de erro amigável.
- `app.js:38`: "está na versão undefined" quando falta `versao`.
- Roteador: hash desconhecido (`#/xyz`, `#/sistema` antes da N4) mostra o Hall sem avisar.

*Pronto quando:* teste de subir dois servidores na mesma porta; `test_web_estatico` cobre o guarda de formato; suíte verde.

**N10 — CLIs com traceback cru (MÉDIA/BAIXA).**
- `temporada.py --trimestre 5T26 | 4T26` e `--simular 9T99`: dão traceback do `ValueError` → `parser.error`, rc 2.
- `triagem/rodar.py:73` `--data 2026-13-40`: valida com `date.fromisoformat` via `type=`.
- Texto do contrato da ALLD3 com ponto decimal ("18.2%", "(0.1048)") em `riscos`/`qualitativo` obs: achar a origem (`relatorio/quali.py`?) e usar o formato BR.

*Pronto quando:* testes das CLIs com argumento inválido (rc 2, sem traceback, nada gravado); suíte verde.

**N11 — Cadastro do relatório (MÉDIA).** `relatorio/quali.py:26` (`CADASTRO`) só tem BBSE3. Por isso EGIE3, PETR4, TAEE11, ITUB4 e SAPR11 dizem "nome de pregão/CNPJ não cadastrado" e ficam sem a série de proventos e o FRE na tela. Ler o pregão de `proventos_ex.PREGAO` (PETR4 = PETROBRAS já existe) e o CNPJ de `triagem/dados/triagem_2026-10-02.csv` (EGIE3 02.474.103/0001-19 conferido no cadastro da CVM). Para TAEE11 (TAESA, units: somar os eventos UNT) e ITUB4 (ITAUUNIBANCO), confirmar o nome de pregão na API da B3 (tradingName) antes de gravar.

*Pronto quando:* teste de `_cadastro` para os 5; a série aparece no relatório quando o dado local existir (na nuvem, só o cadastro e o teste).

7. **B11** (resto) — StatusInvest: termos dão 403 na nuvem — bloqueado até o Frank colar o texto (B3 feita 14/10). Não é missão de turno.
~~8. **B26** — Razão do desconto de controlador com fonte A (FRE) para os 28 com `SEM_RAZAO`.~~ (feita 20/10: 28 → 23, ver Feitas)

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
- **N9** (22/10, noite): `servir.py` bind exclusivo + mensagem "porta em uso"; `app.js` com guardas de `versao`, `fatores` e hash desconhecido; testes em `test_servir` e `test_web_estatico`. Falta só a conferência no navegador no Windows (Frank, dia).
- **N2** (22/10, noite): `tests/test_n2_regras_sem_cobertura.py` (27 casos: desconto por cenários, escala de Preço, saída 1,30× em financeira, ida e volta do `g_implicito`); nenhum defeito; golden intacto (`09` de 22/10).
- **N1** (22/10, noite): README (v2.6.1, 8 dossiês, tela v0.2), brief (fonte Space Grotesk, tela, fatias 2b e 3; cópia em `_historico/2026-10-22 brief/`), BACKLOG (47 IDs, B24–B31 na tabela, N/D/T novos), `03-hall` (cabeçalho v2.6.1, KLBN11 já NC, contagem das 41), `RELATORIO-DIARIO` (mais nova em cima), caminhos do `PROMPT.md` do handoff. Só texto; golden intacto. Nº de testes do brief: atualizado no fim da sessão.
- **N7** (22/10, noite): motor recusa NaN/±inf/None/0/negativo (`palavra`, `nota_preco`, `precos_de_referencia`, `entrada_parcial`, `descontar`, `media_qualitativa`, `central_de`, `qualifica_saida`; `carimbos.de` e `relatorio.caso` com strip/upper); `tests/test_n7_dado_invalido.py`; golden intacto (`09` de 22/10).
- **N6** (21/10, dia): "Ocultar valores" não vaza mais o DY líquido 12m nem o patrimônio (`carteira.js`, `pessoal(...)`); hall/empresa já usavam `pessoal(`; teste `test_carteira_valor_em_texto_respeita_ocultar`; conferido no navegador com Ocultar ligado (só •••).
- **B26** (20/10): razão do desconto de controlador pelo FRE 2026 em PRIO3, KEPL3, RECV3, VBBR3, B3SA3 (28 → 23 `SEM_RAZAO`); 0 palavras; golden intacto (`09` de 20/10).
- **B30 + B31** (20/10): `pl_historico.mediana` cobre 2016–19 pelo LPA básico da classe (DRE 3.99; travas: ações implícitas a ±25% da 1ª composição, evento ambíguo até a entrega do DFP → ano fora); golden: Bogle de 8 tickers, 0 palavras; dossiês FESA4/SHUL4/VLID3/HYPE3/LEVE3 mudam só o P/L. TIMS3 2021–23 conferidas nos PDFs do RI (19,32/4,50/18,29%); WPU0662 conferida no BLS → UNIP6 receita de meio A. Adversário: 3 achados corrigidos.
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
- 21/10/2026 (dia, check-up): D1 temporada blindada (hash do ZIP, 404 = 0, aviso no .vbs), D2 `carimbos.py` na exceção dos 0,80×, backup sem `privado/`, D4 Agendador (TemporadaDiaria 06:30 de 22/10 a 21/11; BackupSemanal domingo 07:30). Fila da madrugada: **N1 → N5** (no topo de "Próximas"). Suíte 833 passed.
