# BACKLOG — Mesa de Value Investing B3
*Consolidado em 13/10/2026 de: `PLANO-DE-MELHORIAS-2026-10.md`, `PROJECT_BRIEF.md` (§5, §6, §11), `docs/auditoria/AUDITORIA_2026-10-08.md` (Onda 4 e aceitos), `docs/auditoria/CHECKUP_2026-10-10.md`, `09-diario-de-decisoes.md`.*
*Não há PROMPT-MESTRE neste repo. O HANDOFF da tela existe em `docs/design/handoff-claude-code/handoff/`.*

**Tipos:** `executável` = a rotina na nuvem faz só com o GitHub (sem ZIPs da CVM, sem Agendador) · `decisão Frank` = precisa de resposta, dinheiro ou preferência dele · `local` = só roda na máquina do Frank (dados fora do git, Agendador, OneDrive).
**Prioridade:** P1 (agora/prazo externo) · P2 · P3 · P4 (sem prazo).
**Status:** aberto · em andamento · bloqueado · parado.

| ID | Item | Prio | Status | Tipo | Origem |
|---|---|---|---|---|---|
| B01 | Temporada 3T26: `python ferramentas/temporada.py` quando sair o ITR (fim de out–nov); régua congelada até lá; reemitir só PDFs afetados | P1 | aberto (data externa) | local | Brief §6.2; Plano F8 |
| B02 | Monitor semanal (sexta 08:00, Agendador) → `BOLETINS/AAAA-MM-DD-monitor.md`; ler quem cruzou compra/saída | P1 | rodando | local | README |
| B03 | `registro_prospectivo.py` a cada rodada aprovada (validação da régua é só prospectiva) | P1 | recorrente | local | Brief §5.3 |
| B04 | Etapa 6 / F6 Carteira: §12 da doutrina (tamanho de posição, concentração, caixa, regra de troca ≥ 3 p.p. líquidos) | P2 | respondido 19/10 (PENDENTE #1: sem mínimo/máximo nem limite de queda; carteira guiada pela palavra; meta de renda mensal) → `DECISOES.md` | decisão Frank | Plano F6 |
| B05 | AUD-41: 29 de 41 tickers com desconto de controlador zero sem razão registrada — dar razão ou exigir razão não vazia no motor (`filtros_1a4`) | P2 | decidido 14/10 → missão B24 | executável | Auditoria Onda 3 |
| B06 | Pré-registro AUD-32/98/99: critério contínuo (postos P/C × retorno excedente), comparador = média do hall (não Ibovespa), regra de uma linha por (ticker, rodada) | P2 | decidido 14/10 → missão B25 | executável | Auditoria Onda 3 |
| B07 | Perguntas do brief §11: orçamento mensal, SaaS só seu ou de terceiros (enquadramento CVM), objetivo acadêmico, agente de sexta no Desktop ainda roda?, fonte paga no lugar da StatusInvest, licença do código | P2 | aberto | decisão Frank | Brief §11 |
| B08 | Dossiês das finalistas da triagem (5 de 104 passaram no portão; fila em `prospectivo/triagem.jsonl`); parecer de saúde/farma é do Frank | P2 | feito 19/10 (ALLD3, FESA4, SHUL4, VLID3; PENDENTE #5) | decisão Frank | Plano F5 |
| B09 | Registrar no `09` e no brief a rodada de 10/10 (boletim, 2 pastas em `_historico/`) se ainda não estiver | P2 | feito 13/10 (já estava) | executável | Checkup 10/10 |
| B10 | Onda 4 (qualidade): AUD-49 (config da carteira, lock de dependências, requirements) | P2 | feito 13/10 | executável | Auditoria Onda 4 |
| B11 | Onda 4: AUD-106 termos de uso das fontes (B3 COTAHIST, StatusInvest) para redistribuição — só fonte nota A | P3 | B3 feita 14/10 (`docs/TERMOS-DE-USO-FONTES.md`); StatusInvest bloqueado (403) | executável | Auditoria Onda 4 |
| B12 | Onda 4: AUD-96 rótulos, AUD-64/65 fichas, AUD-48/105 textos de documentação, AUD-87 encoding | P3 | feito 14/10 (AUD-64 → B23) | executável | Auditoria Onda 4 |
| B13 | Onda 4: AUD-57/60 premissas provisórias e sensibilidade | P3 | relatório feito 14/10 (propostas pendentes) | executável | Auditoria Onda 4 |
| B14 | Ke real de 21–27% nos muito alavancados (KLBN11 77%): vigiar/revisar o Kd sintético e Hamada | P3 | relatório feito 14/10 (KLBN11 hoje 54,7%) | executável | Brief §5.1 |
| B15 | Premissas digitadas nos `lote*.py` e mercado em data fixa: mover para dados + coleta periódica (bloqueia o SaaS) | P3 | relatório 14/10 (`docs/PREMISSAS-B15.md`); **fase 3 em execução** (plano `~/.claude/plans/tingly-gliding-flute.md`): fatia 1 feita 19/10 (procedência por campo), fatias 2, 2b e 3 feitas (20/10: DPA/JCP da B3, bug PN do dossiê, literais das NF); faltam 4 (financeiras) e 5 (trava) em `MISSOES.md` | executável | Brief §5.2 |
| B16 | Confirmar com fonte A o enquadramento CVM (Res. 20/2021 analista; Res. 19/2021 consultor) se houver SaaS | P4 | aberto | executável | Brief §7 |
| B17 | Rumo SaaS (front-end, dados diários, licença) | P4 | parado (sem prazo) | decisão Frank | Brief §2 |
| B18 | 2º comitê de outra família de modelo (D14) e reenvio da pasta de upload ao Desktop | P4 | suspenso ("não tem ajudado") | decisão Frank | Plano F7; memória |
| B19 | Backtest: proxy 70,7% (portão ≥ 80%) — retomar ou abandonar de vez | P4 | parado | decisão Frank | Plano F3 |
| B20 | Backup `backup_dados.py` (OneDrive + git bundle) em dia; disco C com pouco espaço (~4,6 GB) | P3 | recorrente | local | Brief §4, §7 |
| B21 | Suíte do backtest (308 testes, ~13 min) rodar sozinha e com a máquina folgada após mudança em `Mercado`/motores | P3 | sob demanda | local | Brief §4 |
| B23 | AUD-64: tabela única de P/C por premissa (janela IFRS 16, sem desconto de controlador, sem corte de "outras", atuarial, capex LTM) na ficha da PETR4 (`lote5_textos.py`) | P3 | feito 14/10 no gerador (`gerar_pdf_lote5.py`); PDF reemite na temporada | executável | Auditoria Onda 4 |
| B22 | Executar compras/vendas (ex.: posição em ITSA4 acima da saída) — **nunca pelo Claude** | — | do Frank | decisão Frank | Regra: sem ordem de compra/venda |
| B24 | AUD-41 implementar: motor exige razão não vazia no desconto de controlador (decisão 14/10) | P2 | feito 14/10 | executável | B05 |
| B25 | AUD-32/98/99 implementar: pré-registro contínuo, comparador = média do hall, uma linha por ticker×rodada (decisão 14/10) | P2 | feito 14/10 | executável | B06 |
| B26 | Razão do desconto de controlador com fonte A (FRE de cada empresa) para os 28 tickers com `SEM_RAZAO`; cada uma achada baixa a contagem do `test_b24` | P3 | feito 20/10: 5 achadas (28→23); os 23 restantes ficam sem razão (o FRE identifica o controlador, não prova ausência de interferência) | executável | B24 |
| B28 | Linhagem de código nos proventos da B3: TIMS3 perde 2016–19 (TIM Participações, TIMP3) e SUZB3 2016 (PNA, SUZB5) nos "anos pagos"; casar o predecessor (cache do backtest tem `TIM PART S/A`) com a razão de troca conferida no FRE | P3 | aberto | local | 09 de 20/10 (fatia 2) |
| B29 | Backtest: `sem_repeticao` (AUD-23) junta linhas iguais da B3 que são PARCELAS (DMPL: KLBN11, PETR4, B3SA3, TIMS3, WEGE3…) — o retorno total do ledger subconta provento; revisar antes de religar o backtest | P4 | aberto | local | 09 de 20/10 (fatia 2) |
| B30 | P/L histórico das NF (`pl_historico`) começa em 2020: o DFP antes de 2020 não traz a composição do capital; estender 2016–19 pelo LPA básico da DRE (conta 3.99, dados abertos da CVM) e conferir que o hall e o dossiê mudam juntos (Bogle; palavra só via trava da JUSTA) | P3 | feito 20/10 (09) | executável | B15 |
| B31 | Conferir na fonte as alíquotas ajustadas da TIMS3 de 2021–23 (DFP 2022–24, nota 8.d/35; lidas em 08/10, a mediana 18,3% é a de 2023) e a série WPU0662 (BLS) do UNIP6 — hoje B; achada → A | P3 | feito 20/10 (09) | executável | B15 |
| B27 | Relatório por empresa, fatia 2 (quali + PDF) | P2 | feito 19/10 | executável | Roteiro de 19/10 |
| T01 | Tela v0.2: Hall, Empresa, Carteira e Monitor (HANDOFF em `docs/design/handoff-claude-code/handoff/`); falta Sistema (N4) | P2 | feita 20–21/10 | executável | Brief §5 |
| D1 | Check-up 21/10: temporada blindada (sem download no `--gravar`, hash do ZIP, 404 = 0, aviso no .vbs) | P2 | feito 21/10 | executável | `DECISOES.md` 21/10 |
| D2 | Check-up 21/10: `carimbos.py` fonte única das armadilhas na exceção dos 0,80× | P2 | feito 21/10 | executável | `DECISOES.md` 21/10 |
| D4 | Check-up 21/10: Agendador (TemporadaDiaria 06:30 de 22/10 a 21/11; BackupSemanal domingo 07:30) e backup sem `privado/` | P2 | feito 21/10 | local | Brief |
| D5 | Tela v0.2: "anos seguidos com provento" por `proventos_hall.anos_seguidos` (B3, nota A) | P3 | feito 21/10 | executável | `DECISOES.md` 21/10 |
| N1 | Higiene de docs (README, brief, BACKLOG, 03-hall, relatório diário, PROMPT do handoff) | P3 | feito 22/10 | executável | Check-up 21/10 |
| N2 | Testes das regras sem cobertura (desconto por cenários, escala de Preço, saída 1,50× em financeira, DCF reverso) | P2 | feito 22/10 | executável | Check-up 21/10 |
| N3 | Contrato liga o que o motor já calcula (setor, dividendo × JCP por mês, data das fontes, faixa do DCF) | P3 | feito 22/10 (conferência visual pendente) | executável | Check-up 21/10 |
| N4 | Tela Sistema (`sistema.json`: idade dos dados, boletins, golden, testes) | P3 | feito 22/10 (conferência visual pendente) | executável | HANDOFF |
| N5 | Contraste WCAG dos tokens da tela (parte automática da etapa 4) | P3 | feito 22/10 (contornos → PENDENTE #10) | executável | Check-up 21/10 |
| N6 | "Ocultar valores" sem vazar DY líquido nem patrimônio | P2 | feito 21/10 | executável | QA 21/10 |
| N7 | Motor recusa dado inválido (NaN/inf/None/0/negativo) | P2 | feito 22/10 | executável | QA 21/10 |
| N8 | Escala do nº de ações (CVM em mil; TAEE11) — investigar `acoes` | P3 | feito 22/10 (não chega ao valor) | executável | QA 21/10 |
| N9 | Robustez do servidor (porta em uso) e do front (hall sem `fatores`, `versao`, hash desconhecido) | P3 | feito 22/10 (conferência no navegador pendente) | executável | QA 21/10 |
| N10 | CLIs com traceback cru (`temporada.py`, `triagem/rodar.py`) e ponto decimal no texto da ALLD3 | P3 | feito 22/10 | executável | QA 21/10 |
| N11 | Cadastro do relatório (`relatorio/quali.py` CADASTRO só com BBSE3) | P3 | parcial 22/10: CNPJ dos 5 feito; pregão de EGIE3/TAEE11/ITUB4/SAPR11 a conferir na API da B3 (403 na nuvem) | local | QA 21/10 |
| Q01 | `gerar_pdf_lote*.py` registram a fonte `C:/Windows/Fonts/arial.ttf` ao importar: `test_b23_petr4_premissas` e `test_carimbos` não coletam fora do Windows — fallback (Liberation/DejaVu) ou mover para função | P3 | aberto | executável | N4 (22/10) |

## Contagem por tipo
local: 9 (B01, B02, B03, B20, B21, B28, B29, D4, N11) · decisão Frank: 7 (B04, B07, B08, B17, B18, B19, B22) · executável: 32 (B05, B06, B09, B10, B11, B12, B13, B14, B15, B16, B23, B24, B25, B26, B30, B31, B27, T01, D1, D2, D5, N1, N2, N3, N4, N5, N6, N7, N8, N9, N10, Q01) · total 48 (= nº de IDs na tabela).
