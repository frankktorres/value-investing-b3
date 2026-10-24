# RELATORIO-DIARIO
*Uma entrada por dia/turno, a mais nova em cima: o que foi feito (com commit), decisões tomadas, o que ficou, erros. Máx. 10 linhas por entrada.*

## 24/10/2026 — madrugada, sábado (junção de 23/10 + O4b, N12b, O3b inventário + check-up)
- **Fiz:** juntei `claude/fase3-bugs` e `claude/keen-babbage-vf5kor` no ramo (be2e5c5; conflito no `09` e §6 do PRE-REGISTRO, mantidos os dois lados). O4b (FEITA parcial): 16 testes nos itens 9–20, 26 de 29 mutações mortas, 3 equivalentes (d227e49, 0d21ec3). N12b (FEITA parcial): datas de fonte composta, 155 → 165 de 342 na nuvem (4f065e5, bc5652e). O3b: só inventário, 0 de 21 expostas (77779dd). Check-up: `node --check` ok, oráculo (só as bandeiras H2 conhecidas), skips todos por dado local. Suíte: 4 failed (PETR4, herdados do A1), 1069 passed, 45 skipped. Isso é na nuvem, sem os testes de dados; o conferidor da manhã confirma.
- **Auditoria:** 4 confirmados, 0 rebaixados (O4b, N12b, O3b inventário, suíte; nenhum número do motor mudou entre be2e5c5 e HEAD, `instantaneo_todos` idêntico).
- **Descobri:** no Ke da própria empresa o DCF reverso dá "n.a." em 19 de 21 industriais (ROIC < WACC, trava de Greenwald); o golden mata os mutantes de `vence_rf`, e o mutmut provavelmente não o ligou por causa do fixture de sessão.
- **Ressalvas do revisor:** O4b (5) e N12b (4) corrigidas na hora (0d21ec3, bc5652e); a da auditoria (texto da linha O4b) também foi corrigida. O resto continua no BACKLOG O4b/N12b/O3b.
- **Rede bloqueada:** `www.gov.br` (curl 56); `sistemaswebb3-listados.b3.com.br` 403; Tesouro 429.
- **Precisa de você:** PENDENTE #11 e #12. Com o fase3-bugs dentro, este ramo só fica verde depois de `rodar_tudo.py --motivo "Fase 3: H10 e A1"`. Na tela, olhar a coluna "data" (P/L histórico deve ganhar data com o COTAHIST local).
- **Ramo:** `claude/keen-babbage-bvjh9h` (contém os dois ramos de 23/10).

## 23/10/2026 — noite (O3, N12, O4, O5 + backlog N13, B16, O3b, N12b, O4b)
- **Fiz:** O3 H10+A1 (+parte do O3b) no ramo `claude/fase3-bugs` (parcial: 4 testes da PETR4 vermelhos de propósito, golden não regravado; parecer do oráculo RESSALVA); N12 data das fontes 27 → 155 de 341 no contrato; O5 motor-sombra 36/38 iguais (HYPE3/PRIO3 = crédito fiscal); O4 mutmut parcial (936 de 5.504; nota 0,80 fin / 0,74 não fin); N13; B16 (Res. CVM 19/20 lidas); O4b/N12b/O3b em parte. Suíte da sessão 1047 passed, 44 skipped (na nuvem, sem os testes de dados; o conferidor da manhã confirma).
- **Auditoria:** 7 confirmados, 0 rebaixados (O3 e O4 confirmados como parciais).
- **Descobri:** só a PETR4 muda com o A1 (central 53,48 → 52,87, JUSTA igual); EBIT ausente já falha alto; financeira com dispersão > 3× não tinha teste (O4b).
- **Ressalvas do revisor:** oráculo O3 → PENDENTE #12 e BACKLOG O3b; N12 (LTM declarado, `_iso`) e O5 (crédito conferido no central) corrigidas na hora; O4 números corrigidos; resto em N12b/O4b.
- **Rede bloqueada:** `www.gov.br` (curl 56); `sistemaswebb3-listados.b3.com.br` 403; Tesouro 429. CVM e BCB abertos.
- **Precisa de você:** PENDENTE #11 (rodar `rodar_tudo.py --motivo "Fase 3: H10 e A1"` e dar ok ao `claude/fase3-bugs`) e #12 (4 perguntas de doutrina); ao juntar os dois ramos, o fim do `09` e o §6 do PRE-REGISTRO conflitam (os dois acrescentam linhas: manter as duas); olhar na tela a coluna "data" das fontes.
- **Ramo:** `claude/keen-babbage-vf5kor` (N12, O4, O5, backlog) e `claude/fase3-bugs` (O3, espera o Frank).

## 22/10/2026 — manhã (conferência da rodada da noite, sessão do Frank)
- Conferi a rodada com os dados locais: 1.004 passed. A única falha era a tela exportada antes da N3 (regerada: verde). Nenhuma palavra mudou; agora está provado. Junção no master: f28a76d.
- Falhas da rodada: (1) gravou em `claude/*` e não no master, porque a nuvem só faz push nesse ramo; (2) a "data da fonte" da N3 só existe em 27 de 466 fontes → N12; (3) parou com 27 min de sessão e pulou o foco do dia (o prompt limitava a 2 itens do backlog); (4) a rede bloqueia a B3 (proxy 403) e o `conteudo.cvm.gov.br` (DNS).
- Corrigido: `conferir_noite.py` + tarefa 07:15; prompt da rotina revisto; `scripts/cloud_setup.sh`; rota `#/` (N14); manifesto não regrava a data sem ZIP novo (era o commit de ruído diário); registro da suíte com `-p`; EOL fixo do `erro_proxy_*.csv`. PENDENTE #10 = (a).
- Incidente: o 1º teste do `conferir_noite` rodou no repo real (default do `cwd` preso na definição) e enviou a mesma junção já conferida, apagando 3 ramos `claude/*` já contidos no master. Nada se perdeu; corrigido, e o teste agora trava se apontar para o repo real.
- Precisa de você: registrar a tarefa ConferirNoite; liberar domínios da B3/CVM na rede do ambiente da nuvem.

## 22/10/2026 — noite (N1–N5, N7–N11, Q01)
- Fiz: todas as missões abertas (N7, N1, N2, N9, N10, N8, N11 parcial, N3, N4, N5) + Q01 do backlog; suíte 963 passed, 42 skipped; nenhuma palavra, central ou golden mudou. Tudo na branch `claude/keen-babbage-k1rlj3` (não na `master`).
- Descobri: ações "em mil" (N8) não chegam ao valor; o ponto decimal da ALLD3 vinha de `dossie/notas.py`; b3.com.br e gov.br dão 403 na nuvem (B16 e pregões da N11 ficam sem fonte A).
- Precisa de você: PENDENTE #10 (contornos de chip abaixo de 3:1); conferir no navegador Sistema, calendário JCP e servidor; pregão de EGIE3/TAEE11/ITUB4/SAPR11 na API da B3; revisar/mesclar a branch.

## 14/10/2026 — B24, B25, B23, B15, B11 (sessão do Frank)
- B24: o motor exige razão no desconto de controlador. 28 tickers ficaram com "sem razão documentada" e a LEVE3 com FRE nota A. **Nenhuma palavra mudou.**
- B25: pré-registro contínuo no `registro_prospectivo.py`: IC de postos P/C × retorno excedente, média do hall, uma linha por ticker×rodada.
- O adversário rodou nas duas. Achou e corrigiu: PDF do lote 2 que quebraria, citação errada da LEVE3, NaN do retorno que invertia a leitura.
- B23: tabela de P/C por premissa da PETR4 no gerador. O PDF não foi reemitido, porque outros campos informativos mudaram desde 09/10.
- B15: relatório `docs/PREMISSAS-B15.md` (445 campos digitados). Proposta de migração, nada movido.
- B11: termos da B3 lidos (só uso pessoal; dados históricos livres para distribuidor). StatusInvest segue 403.
- Suíte: 517 passed, 1 skipped (+ testes da B23). Precisa de você: colar os termos da StatusInvest (opcional).

## 14/10/2026 — turno noite (B12)
- Feito: B12 (AUD-96/65/87/48/105; só texto, rótulos e encoding). 473 passed, 19 skipped; nenhuma palavra mudou.
- Descobri: AUD-64 pede tabela nova na ficha da PETR4 — virou B23. Rodou no ramo `claude/keen-babbage-7m0ksr`, não `master`.
- Também: B13/B14 → `docs/SENSIBILIDADE-B13-B14.md` (5/41 mudam de palavra com π 4% ou rf ±1 p.p.; Ke KLBN11 54,7%). B11 travou: termos B3 (500) e StatusInvest (403) inacessíveis.
- Precisa de você: nada urgente; se quiser B11, cole os termos de uso.

## 13/10/2026 — turno noite (B09, B10)
- Feito: B09 (já registrado, nada a completar) e B10 (carteira em JSON só com tickers; `requirements.lock`). 473 passed, 19 skipped.
- Descobri: `python` padrão da nuvem não tem pytest (use `/usr/bin/python3`); 19 testes pulam por falta de dado da CVM.
- Precisa de você: nada novo. Próxima: B12.

## 13/10/2026 — preparação da rotina na nuvem
- Repo `frankktorres/value-investing-b3` (privado), `master` = `origin/master`.
- Varredura de segredos: arquivo atual e histórico sem tokens/chaves. Tickers da carteira ficam (decisão A, ver `DECISOES.md`).
- Criados: `docs/BACKLOG.md`, `PENDENTE-FRANK.md`, `DECISOES.md`, `MISSOES.md`, este relatório; `CLAUDE.md` ampliado; hooks em `.claude/settings.json`; skill `/fechar`.
- Hook Stop testado de verdade: doc → commit+push em `master`; teste vermelho → só `wip/auto` (árvore intacta); token falso → bloqueado. Suíte base: 491 passed, 1 skipped. Ramo `wip/auto` de teste apagado.
