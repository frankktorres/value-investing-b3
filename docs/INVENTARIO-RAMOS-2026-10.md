# Inventário dos ramos de outubro não juntados (B67)

*Rotina noturna de 28/11/2026 (só doc; nenhum código portado). Base comparada: `origin/master` 5f4dad5; base dos ramos: 595388f (22/10).*
*Fontes: `git log --reverse origin/master..origin/arquivo/2026-10-keen-babbage-bvjh9h` (32 commits, contém o `-vf5kor` pelo merge be2e5c5)
e `…/arquivo/2026-10-fase3-bugs` (4 commits: e62e0a5, 0dec510, b87784e, 296da7a — os mesmos shas do primeiro; não há commit exclusivo
do `-fase3-bugs`). Total: **32 commits distintos**.*

Classes: **portar** (o master não tem o equivalente; diz o que precisa) · **superado** (o master já tem, ou o arquivo é de controle
/ medida velha; cita a prova) · **conflita** (colide com algo do master; diz com quê).
Prova do master: arquivo:linha em `origin/master` (5f4dad5). Não rodei os testes do ramo antigo contra o master (a nuvem não pôde criar a
cópia de trabalho): "portar" abaixo é por **ausência do arquivo/trecho no master**, não por teste.

| sha | missão | o que fez | classe | prova / o que precisa |
|---|---|---|---|---|
| e62e0a5 | O3 | H10 (dado crítico ausente → NÃO CONCLUSIVO) e A1 (desconto do controlador fora do ponto fixo) no motor; relatório do oráculo 23/10 | superado | H10 = 4bb5f34 (`motor_nao_financeiras.py:191-208`, `:1032-1035`); A1 = H2/B34 (c108bce; `motor_nao_financeiras.py:683`, desconto do controlador em `:73`/`:871`). `docs/oraculo/2026-10-23.md` ausente no master, mas é relatório de uma medida velha |
| 0dec510 | O3 | `09`, PRE-REGISTRO §6 (6/24), PENDENTE #11/#12 com o parecer RESSALVA | conflita | numeração: no master #11/#12 são outros itens e o orçamento está em 8/24 (`PRE-REGISTRO-v3.md` §6 linhas 14–15 = B46). Só descrito; não renumerar nem editar `PENDENTE-FRANK.md` |
| e188aaa | N12 | data de cada fonte (COTAHIST, CVM DFP/ITR, ações, proventos B3, FRE, mercado) no contrato: 27 → 136 de 341 | portar | `ferramentas/tests/test_n12_data_das_fontes.py` ausente no master; `procedencia.py` do master sem o tratamento (`:130-136` só mercado); `insumos_a.py:70-95` já tem `data=` em parte. Precisa: **local** (ZIPs) e golden "sem mudanças" |
| d52a453 | N12 | ressalvas do revisor (LTM só com trimestre declarado, `_iso` valida data, `calendar`) | portar | junto com e188aaa (mesmos arquivos) |
| 571ed62 | O5 | pré-registro da tolerância do motor-sombra (§6 linha 15) | conflita | a linha 15 do §6 no master é a B46 8/24 (`PRE-REGISTRO-v3.md`, emenda 13). Pré-registro é "Só do Frank": reescrever com outro número de linha |
| 1de5574 | O5 | motor-sombra FCFF/FCFE e DDM, só relatório (36 de 38 iguais) | portar | `ferramentas/oraculo/sombra.py`, `sombra_rodar.py` e `test_oraculo_sombra.py` ausentes no master; a B51 (segunda implementação, `BACKLOG.md:60`) cobre Gordon/DDM/P/VP/EPV mas não FCFF/FCFE → cobre em parte. Precisa: oráculo (método) e dados locais para rodar |
| 96a58bc | N13 | `SO_REUSEADDR` fora do Windows (reabrir em TIME_WAIT) | conflita | `painel/servir.py:60-68` no master (N9) fixa `allow_reuse_address = False` e usa `SO_EXCLUSIVEADDRUSE` só no Windows; a mudança do ramo reescreve o mesmo trecho. Portar à mão, só não-Windows; sem golden. O BACKLOG N13 (`:95`) diz "só local, com a suíte do Windows" (ERROR em `test_reabrir_logo_depois_de_fechar_com_conexao_atendida` na junção de 23/11): instruções diferentes para o mesmo item — decide a sessão do dia |
| b1dadb7 | O5 | ressalvas do revisor: crédito fiscal conferido no central, independência parcial declarada | portar | junto com 1de5574 (mesmos arquivos); `09` e `PRE-REGISTRO` do commit: ver conflita acima |
| b798676 | B16 | `docs/ENQUADRAMENTO-CVM-B16.md` (Res. CVM 19 e 20/2021 lidas na fonte) | portar | arquivo ausente no master; é a missão B16 da mesma noite |
| 94e196c | B16 | citação da frase da meta corrigida (`carteira.py`, não DECISOES) | portar | junto com b798676 |
| b87784e | O3b | PL, D&A e imobilizado ausentes num exercício da janela → NÃO CONCLUSIVO | superado | `CRITICOS_ANO` em `motor_nao_financeiras.py:195-208` (introduzido em 4bb5f34) |
| 296da7a | O3b | testes negativos e motivo conferido; rigidez da D&A no `09` | superado | mesmo trecho; `09` é doc de decisão (não portar à noite) |
| 3aaf137 | N12b | data do cache da B3 também no provento já ex | portar | `procedencia.py` do master sem o trecho; junto com N12 (local, golden) |
| 9575518 | O3b | `montar_series` não soma 0 por provento sem valor; `eventos_sem_valor` | superado | `montar_series.py:43-51`, `:68`; `tests/test_o3b_montar_series.py` existe no master |
| c49c8fa | — | MISSOES/BACKLOG: O3 parcial, N12 e O5 feitas, N13 e B16 | superado | doc de controle; a fila foi reescrita em 26/11 (`_historico/2026-11-26 rotina-nuvem/MISSOES.md`) |
| fb11ff8 | N12b | COTAHIST da carteira com a data do pregão | portar | `relatorio/carteira.py` + teste; local (carteira); sem golden de palavra |
| 121eda4 | O3b | BACKLOG: juros e proventos conferidos (já falham alto) | superado | doc de controle |
| c7cc45d | — | cópia do brief de 22/10 em `_historico` | superado | histórico de um brief já substituído; o master tem briefs mais novos |
| a437420 | O4 | teste de mutação (mutmut 3.8.0, parcial 936/5.504): relatório, `requirements-dev.txt`, `.gitignore` | superado (= não portar o relatório; o master não o tem) | o relatório mediu o motor antes da B34/B57 (arquivo:linha dos sobreviventes não vale); `requirements-dev.txt` e `docs/oraculo/mutacao-2026-10-23.md` ausentes no master — se a mutação for refeita, é medida nova |
| e43aaec | O4b | testes que matam os sobreviventes 1–3 e 5–8 do motor das financeiras | portar | `tests/test_o4b_mutantes_financeiras.py` ausente no master; os testes só valem se passarem no master (motor das financeiras mexeu depois: verificar em máquina com ZIPs) |
| e784424 | O4 | MISSOES: O4 feita parcial | superado | doc de controle |
| 3c67fe2 | — | relatório da noite de 23/10 (auditoria 7/0) | superado | relatório diário; o master tem os de 27/11 e 28/11 |
| be2e5c5 | — | merge do `-vf5kor` no `-bvjh9h` | superado | sem conteúdo próprio |
| d227e49 | O4b | testes dos sobreviventes 9–20 (26 de 27 mortas à mão) e investigação golden × mutmut | portar | `tests/test_o4b_mutantes_parte2.py` ausente; mesma ressalva de e43aaec |
| 4f065e5 | N12b | data das fontes compostas e séries macro: 155 → 173 de 342 | portar | `lote4/5/6`, `pl_historico.py`, `insumos_a.py`; local, golden "sem mudanças" |
| 0d21ec3 | O4b | script das mutações no repo (29: 26 mortas, 3 equivalentes), contagens sem a PETR4 | portar | `scripts/o4b_mutacoes_manuais.py` ausente; junto com d227e49 |
| 77779dd | O3b | BACKLOG: inventário dos `v(..., 0)` fora da guarda (0 de 21 expostos) | superado | doc de controle |
| c678463 | — | oráculo 24/10 (check-up de sábado) | superado | `docs/oraculo/` do master tem rodadas de 23–25/11 (`2026-11-23.md` … `-25.md`); relatório velho |
| bc5652e | N12b | janela de 12 m na data do Brent/PPI, P/L histórico só com o ano lido | portar | junto com 4f065e5 (mesmos arquivos); local, golden |
| 583099b | — | DECISOES: data de fonte composta e junção das rodadas não conferidas | superado | doc de controle |
| 0db4c49 | — | brief: rodada de 24/10 | superado | `PROJECT_BRIEF.md` do master é mais novo; cópia de `_historico` só do ramo |
| 52295c1 | — | relatório de 24/10 (auditoria 4/0) e linha O4b | superado | relatório diário |

## Contagem por classe (32 commits)
- **portar: 13** — N12/N12b (e188aaa, d52a453, 3aaf137, fb11ff8, 4f065e5, bc5652e: **6**, local + golden "sem mudanças"), O5 (1de5574, b1dadb7: **2**,
  oráculo), B16 (b798676, 94e196c: **2**, é a missão B16), O4b (e43aaec, d227e49, 0d21ec3: **3**, local para conferir).
- **superado: 16** — e62e0a5, b87784e, 296da7a, 9575518, c49c8fa, 121eda4, c7cc45d, a437420, e784424, 3c67fe2, be2e5c5, 77779dd, c678463, 583099b, 0db4c49, 52295c1.
- **conflita: 3** — 0dec510 (numeração PENDENTE #11/#12 e orçamento 6/24 × 8/24), 571ed62 (linha 15 do §6 já é da B46), 96a58bc (N9 em `servir.py:60-68`).

## O que não revisei
- Não rodei os testes do ramo antigo contra o master; "portar" = ausência no master, "superado" = trecho achado no master.
- N13 (96a58bc) classificado só pelo texto do commit e pelo `servir.py` do master; não testei reabrir a porta em TIME_WAIT.
