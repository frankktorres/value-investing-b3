# MISSOES
*Fila de trabalho. Cada missão tem "pronto quando" verificável; ao terminar, mover para "Feitas" e registrar em `RELATORIO-DIARIO.md`. Fonte: `BACKLOG.md`. A rotina da nuvem segue `docs/ops/rotina/PROTOCOLO.md` (só missão carimbada), grava no ramo `claude/*` dela, e o `ferramentas/conferir_noite.py` junta no master de manhã, com os dados locais e o portão da base.*

## Próximas (ordem de prioridade)

*Desde 26/11/2026 a noite segue `docs/ops/rotina/PROTOCOLO.md`: só faz missão com a linha `*Carimbo (nuvem):*` (escopo só com
caminho literal, `fonte:` e `pronta:` = commit do master em que a sessão do dia carimbou), no máximo 4 por noite, e nunca
escreve carimbo. Missão sem carimbo é da sessão do dia (local). O `/mesa-fechar` carimba.*

*Fila de 23/10 (O3 → N12 → O4 → O5), conferida no código em 26/11: O3 superada (ver Feitas); N12, O4, O5, e também N13 e B16,
foram feitas só no ramo hoje arquivado e nunca juntadas → o inventário B67 diz o que portar. Texto antigo das missões:
`_historico/2026-11-26 rotina-nuvem/MISSOES.md`.*

### Da sessão do dia (local, sem carimbo)

**B61 — `ltm_2T26` do hall com ações do DFP (pré-AUD-68): recoletar o container ou estender a catraca da B60.** *(26/11/2026)*
KEPL3, ISAE4, EGIE3, HYPE3 com `ltm_2T26/acoes` ≠ ITR (BACKLOG B61). Dormente hoje (`ltm.py` lê `ltm` antes; só `na_data` lê o
`ltm_2T26`), mas tem de fechar antes da Prova 2 do M1. Recoleta pelo modelo de `ferramentas/b60/recoletar.py` (só `acoes` e
`lucro_controlador` podem mudar); golden igual. *Pronto quando:* teste comparando `acoes` entre os `ltm*` de cada ticker nas 3
séries verde, suíte verde, golden "sem mudanças". Rede da CVM e golden → máquina do Frank. Sonnet low.

**B33 — EGIE3: explicar os ~R$ 2 bi que faltam no PL do 3T26, antes de reavaliar a palavra.** *(23/11/2026)*
O PL do controlador subiu R$ 6,30 bi de 30/06 a 30/09/2026; oferta de jul/26 (R$ 8,36 bi) − dividendo de ago/26 (R$ 770,8 mi, B3) daria R$ 7,59 bi. Conferir no RI do 3T26 (release e ITR) e na DMPL do ITR 3T26 (CVM, nota A) o custo da oferta (gastos com emissão de ações, líquidos de IR) e o dividendo efetivamente pago/declarado no trimestre, e o resultado do 3T26 que entra no PL. Fato com fonte → `ferramentas/dados/eventos_societarios.json` (nunca número no código). Não mudar a palavra: a EGIE3 fica NÃO CONCLUSIVO (trava do §9, decisão do Frank de 23/11) até o Frank ver a conta. *Pronto quando:* a diferença está explicada linha a linha com fonte A/B em `docs/` (ou o resíduo declarado), e a reavaliação proposta está em `PENDENTE-FRANK.md`. Local: precisa do RI/CVM pela rede e grava em `ferramentas/dados/`.

**B32 — Zerar a catraca de anos fixos nos lotes (prazo 31/01/2027, antes do DFP 2026).** *(23/11/2026)*
Datas de mês/dia/trimestre nos lotes já estão zeradas (tolerância zero em `tests/test_lotes_sem_data_fixa.py`). Restam os anos:
`range(2016, 2026)`/`range(2021, 2026)` → janela a partir do último exercício do DFP na série (`CVM[tk]["anual"]`); chaves
`"2024"/"2025"` → os 2 últimos exercícios; `dfp_2025.zip`, `itr_2025.zip`, `fre_2026.zip` → do ano do LTM (`ltm.ano_de`); início
de janela com quebra estrutural (ex. PETR4 2019, RECV3 2020) é fato: vai para dado com `janela_razao`, não para o código.
Junto, antes do DFP 2026: ler o balanço pelo DFP quando o LTM for 4T (`ltm.zip_itr("4T26")` falha alto hoje — ações e
holding dos lotes 4 e 6 e ITSA4). Uma fatia por lote; golden idêntico em cada uma (refatoração pura). *Pronto quando:* `tests/datas_fixas_catraca.json` com 0 em
todos os lotes, suíte verde com `EXIGIR_DADOS=1` e `python rodar_tudo.py` "sem mudanças". Local (ZIPs, golden).

- **9f — B15 / fatia 4 (financeiras)** e **9g — B15 / fatia 5 (trava final):** abertas, local (mexem em motor/palavra; os
  VPA/LPA dos bancos já foram absorvidos pela B32). Texto completo no `_historico/2026-11-26 rotina-nuvem/MISSOES.md`.
- **B11 (resto) — StatusInvest:** termos dão 403 na nuvem; bloqueado até o Frank colar o texto.
- **Rede bloqueada na nuvem (22/10):** `b3.com.br` (API de listadas) e `gov.br`/`conteudo.cvm.gov.br` devolviam 403/ENOTFOUND;
  o pré-voo da noite mede de novo e grava em `/tmp/mesa_prevoo_rede.json`.

## Em andamento
(nenhuma)

## Feitas
- **B67** (28/11, claude/keen-babbage-4aepwn): `docs/INVENTARIO-RAMOS-2026-10.md` — 32 commits: 13 portar, 16 superado, 3 conflita; nenhum código portado.
- **B16** (28/11, claude/keen-babbage-4aepwn): `docs/ENQUADRAMENTO-CVM-B16.md` trazido do ramo arquivado, citações internas conferidas (fonte A não relida).
- **Rotina noturna no molde do UNION** (26/11, 8a92e08): `docs/ops/rotina/` (BOOTSTRAP conferido na nuvem + PROTOCOLO), pré-voo,
  portão `ferramentas/rotina/checar_rotina.py`, `conferir_noite` com PROTEGIDOS ampliado + portão da base (patch do Frank),
  canários; rotina enabled (Sonnet 5.5, próxima 2026-11-27T07:40Z); ConferirNoite religada (rc 0 à mão, próxima 27/11 07:15);
  ramos de outubro → `arquivo/2026-10-*`; piso B37 1399. Suíte 1427.
- **O3** (superada, conferida em 26/11): H10 refeito no master em 4bb5f34 (`motor_nao_financeiras.py`, "dado crítico
  ausente" → NÃO CONCLUSIVO), A1 fechado pelo H2 (B34, 24/11); os commits do ramo `arquivo/2026-10-fase3-bugs` ficam
  superados (inventário B67).
- **10 / B01** (24/11, B34): temporada 3T26 juntada no master.
- **B45 só diagnóstico** (26/11): `ferramentas/b45/diagnostico.py` reproduz os 5 números da B36 e abre as camadas
  (`docs/b45/camadas.json`); quadro causa por ticker × emenda 8 em `docs/b45/B45-diagnostico-2026-11-26.md`. Erro de dado E1
  (frota no FCO fora do capex) corrigido no coletor, hall intacto; E2 (série anual sem reapresentação, 18 do hall) → PENDENTE #16.
  Registro de tickers tocados do M1 criado. Novos B62–B66. Nenhuma palavra mudou.
- **Pasta do Desktop** (26/11, c2f7b07): `ferramentas/desktop/atualizar.py` + `ATUALIZAR.bat` regeram `UPLOAD CLAUDE DESKTOP/` (21 cópias exatas + LEIA-ME, MAPA, O QUE MUDOU, instruções; MANIFESTO com sha256); `test_desktop_upload.py` (cópia/fonte × MANIFESTO, segredo); PDFs de 09/10 e versões de 21/10 em `_historico/2026-11-26 upload-desktop/`; linha no `mesa-fechar`. Suíte 1399.
- **B60** (26/11, 7474afd): séries do dossiê CMIN3 e BLAU3 (pré-AUD-68) recoletadas (`b60/recoletar.py`); palavras iguais; centrais na data CMIN3 3,6317→3,5987 (provento sai da dívida bruta do WACC), BLAU3 8,1372→7,6457 (provento já ex na DL); catraca `test_b60_series_pos_aud68.py`; resíduo do hall → B61. `adversario`: sem dupla contagem. Suíte 1339.
- **B57** (25/11, emenda 13 2c7c87a → f96cb7b, d955857): X2 do Z'' = (2.03.04 + 2.03.05) ÷ ativo, 2.03.05 ausente → erro explícito; séries do hall, dossiês e B36 recoletadas só com o campo novo; golden igual. B46 tentativa 8/24 → **NÃO CONCLUSIVA** (C3 15/24), hipótese encerrada. `adversario` 1 grave (ltm_2T26 do hall) corrigido; `senior` SEGUE COM AJUSTES; `oraculo` BLOQUEIA por processo (commit da emenda com a ficha de fontes) → Frank: #13 A (exceção pontual em `ordem.py`) e #14 (causa (a) fechada). Suíte 1333 verde.
- **B46** (25/11, emenda 12 5461a47 → e8a039b): "separar a dificuldade" (Damodaran 2009) pré-registrada e rodada sobre o conjunto de desenvolvimento, tentativa 7/24 → **NÃO CONCLUSIVA** (C3 15/24; o π da cobertura e o do Z'' discordam). Nada implantado; motor, doutrina e golden intocados. `oraculo` RESSALVA, `senior` SEGUE COM AJUSTES (aplicados), `adversario` 2 defeitos do executor corrigidos com re-execução igual; B57 nova. Suíte 1324 verde.
- **B40** (25/11, b2b9d60): `CIS RED CAP` com semântica conferida (×1, ação nova em `recebe`, fora do DPA; fonte A = FRE `capital_social_reducao` de Cosan 2014, MRV 2018, GPA 2020); CSAN3/MRVE3 rodam (NÃO CONCLUSIVO); B55/B56 novos; PENDENTE #12 respondido (B46 sim, B35 até o HOLD-OUT 2). Suíte 1302 verde.
- **Pacote de autonomia** (25/11, `docs/research/2026-11-25-pacote-autonomia.md`): agente `senior` + "Quem decide" (2b5d810); B37 trava do push (f879b4d); agentes adaptados (d86b7fb); travas 4.2–4.6 (dcc9a5f); skills `mesa-*` (04513d3); B51/B52 (540a325). `senior`: PARA → 8 achados corrigidos → SEGUE COM AJUSTES; resta o #11 do `PENDENTE-FRANK.md` (`--no-verify`). Fumaça: escolha pela causa (a) com o `senior` OK; push vermelho barrado no clone OK
- **B34** (24/11, com o Frank): defeito H2 corrigido — D/E a mercado (preço da data-base × ações), sem ponto fixo; D = dívida bruta com arrendamentos + outros passivos financeiros, a mesma da ponte; Ke nominal > 30% → NÃO CONCLUSIVO (doutrina v2.7). Golden regravado (SMTO3 CARA → NC; PRIO3/UNIP6 → NC pela trava). Dossiês recalculados na data (point-in-time). Oráculo sem BLOQUEIA; suíte verde com `EXIGIR_DADOS=1`; 3T26 juntado no master. Ver `09` de 24/11.
- **Q01** (backlog, 22/10): `gerar_pdf_lote1.py` cai para a Liberation Sans (métricas da Arial) quando a Arial do Windows não existe; `test_b23` e `test_carimbos` voltam a coletar na nuvem (suíte 963 passed, 42 skipped, sem `--ignore`). PDFs do Windows inalterados.
- **N5** (22/10, noite): `painel/tests/test_contraste_tokens.py` — texto ≥ 4,5:1 e séries ≥ 3:1 nos dois temas passam; contornos abaixo de 3:1 listados (teste fixa a lista) e em `PENDENTE-FRANK.md` #10; nenhuma cor trocada.
- **N4** (22/10, noite): `painel/sistema.py` + `sistema.json` + `telas/sistema.js` (rota `#/sistema`); registro da suíte pelo `conftest`; `test_sistema.py`, `test_web_estatico`. Conferência visual: Frank (dia).
- **N3** (22/10, noite): contrato com setor (triagem/FCA), dividendo × JCP por mês, data por fonte (`Origem.data`) e faixa do DCF (pessimista/otimista); front lê só o contrato; testes em `painel/tests/test_contrato.py`; `DECISOES.md` 22/10. Falta conferir visualmente no navegador (Frank, dia); o `contrato/` local precisa de `painel --exportar` para regerar.
- **N11** (22/10, noite, parcial): `CADASTRO` com CNPJ de EGIE3, PETR4, TAEE11, ITUB4 e SAPR11 (da triagem de 02/10) e pregão da PETR4 (`proventos_ex.PREGAO`); **b3.com.br devolve 403 na nuvem** → pregão de EGIE3, TAEE11, ITUB4, SAPR11 ficou `None` (não se chuta); o FRE já aparece, a série de proventos desses 4 segue com aviso. **Local (Frank/dia):** conferir `tradingName` na API da B3 (TAEE11 = TAESA?, ITUB4 = ITAUUNIBANCO?, EGIE3, SAPR11) e preencher. `tests/test_n11_cadastro_relatorio.py`.
- **N8** (22/10, noite): investigado — o nº de ações em mil NÃO chega ao valor por ação (cada leitor reescala; financeiras usam VPA/LPA da StatusInvest; só o follow-on da ISAE4 lê cru, em unidades). Relatório em `docs/QA-2026-10-21.md`; `tests/test_n8_escala_acoes.py`; nada a regravar.
- **N10** (22/10, noite): `temporada.py` e `triagem/rodar.py` validam argumento (rc 2, sem traceback, nada gravado); ponto decimal do dossiê vinha de `dossie/notas.py` → `_br()`; `tests/test_n10_clis_argumento_invalido.py`. Vereditos já gravados mantêm o texto antigo até a próxima geração.
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
*A skill `/mesa-fechar` reescreve esta seção: o que ficou pendente, onde parou, próximo passo.*
- 26/11/2026 (rotina noturna): no master (8a92e08 + fecho); nada em andamento. 1ª noite em 27/11 04:40 BRT com B67 e B16
  carimbadas (só doc). De manhã: `ferramentas/monitor/conferir.log` e o topo do `RELATORIO-DIARIO.md` (1ª junção real pela
  B37). Próximo passo (DNA) segue o de hoje: causa (b), desenho do conserto do domínio + pré-registro (última linha
  "Próximo passo (DNA):" do `DECISOES.md`).
- 26/11/2026 (B45 diagnóstico): no master (este commit); nada em andamento. Causa por ticker em `docs/b45/`; E1 corrigido no
  coletor, E2 → PENDENTE #16. Próximo passo (DNA): desenho + pré-registro do conserto da (b) em Opus high com plan mode (ver a
  última linha "Próximo passo (DNA):" do `DECISOES.md`).
- 26/11/2026 (B60 + Desktop): no master (7474afd, c2f7b07); nada em andamento. B60 fechada sem mudar palavra; B61 aberta (ações do
  `ltm_2T26` do hall, P2). Pasta do Desktop agora gerada: todo fecho que mexe em doc do MANIFESTO roda `python -m desktop.atualizar`.
  Próximo passo: ver a última linha "Próximo passo (DNA):" do `DECISOES.md`.
- 25/11/2026 (B57): no master (d955857); nada em andamento. Causa (a) **fechada** pelo Frank (#14). Próximo passo (DNA): **B60**
  (erro de dado no dossiê CMIN3: recoletar e mostrar o diff da palavra, que é do Frank), depois o **diagnóstico da B45** (causa (b),
  sem conserto nem tentativa); B41 (causa (c)) em paralelo. Falta atualizar o texto do DNA §3/§4 com a (a) fechada (decisão já no `09`).
  Ver a última linha "Próximo passo (DNA):" do `DECISOES.md`.
- 25/11/2026 (B46): tentativa 7/24 NÃO CONCLUSIVA, no master (e8a039b); nada em andamento. Causa (a) segue aberta: o D/E da
  indústria resolve o Ke, mas o π não é identificável e foi medido com o defeito do X2 do Z'' (B57). Próximo passo (DNA): **B57**
  (dado do Z'' que o motor usa na nota de solidez — mexe no motor: oráculo e `09`); em paralelo, sem gastar tentativa, causa (c)
  B41. Rodar a B46 de novo depois da B57 = tentativa 8/24. Ver a última linha "Próximo passo (DNA):" do `DECISOES.md`.
- 25/11/2026 (B40): cisão com redução de capital resolvida e no master (b2b9d60); nada em andamento. Próximo passo (DNA):
  causa (a), **B46 sozinha** (Ke > 30%), hipótese pré-registrada em commit próprio antes de rodar (tentativa 7/24); em paralelo,
  sem gastar tentativa, causa (c) B41 (INCORPORACAO). Ver a última linha "Próximo passo (DNA):" do `DECISOES.md`.
- 25/11/2026 (pacote de autonomia): a Mesa agora decide o reversível sozinha (`senior` + `DECISOES.md`) e não empurra master
  sem suíte verde (B37). Pendente do Frank: #11 (`--no-verify`) e #12 (autorizar B35 + B46). Próximo passo (DNA), enquanto o
  #12 não sai: causa (c), B40 (cisão com redução de capital, fonte A) — ver a linha "Próximo passo (DNA):" do `DECISOES.md`.
- 13/10/2026: infraestrutura da rotina criada (hooks, backlog, skill). Nada em andamento.
- 14/10/2026 (fim do dia): B24, B25, B23, B15 e B11 (parte B3) feitas e publicadas (f03636e, 9bde979, 8d780f8); nada em andamento. Próximas executáveis: B11 (StatusInvest, 403), B26 (FRE nota A para os 28 `SEM_RAZAO`). Marco seguinte é local: ITR 3T26 (`temporada.py`, B01), que também reemite o PDF do lote 5 com a tabela da B23.
- 21/10/2026 (dia, check-up): D1 temporada blindada (hash do ZIP, 404 = 0, aviso no .vbs), D2 `carimbos.py` na exceção dos 0,80×, backup sem `privado/`, D4 Agendador (TemporadaDiaria 06:30 de 22/10 a 21/11; BackupSemanal domingo 07:30). Fila da madrugada: **N1 → N5** (no topo de "Próximas"). Suíte 833 passed.
- 22/10/2026 (fim do dia): oráculo Fase 2 feita (9e9e8ac) + H1–H11 como relatório (`oraculo/hipoteses.py`, `docs/oraculo/`).
  Achados que mudam palavra: H10 (zero silencioso) e A1 (desconto do controlador no Ke). Fila da madrugada de 23/10:
  **O3 (ramo `claude/fase3-bugs`) → N12 → O4 → O5**. De manhã o Frank confere o ramo da Fase 3 (golden) e dá o ok.
