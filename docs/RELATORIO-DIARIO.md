# RELATORIO-DIARIO
*Uma entrada por dia/turno, a mais nova em cima: o que foi feito (com commit), decisões tomadas, o que ficou, erros. Máx. 10 linhas por entrada.*

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
