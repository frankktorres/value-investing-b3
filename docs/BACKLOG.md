# BACKLOG — Mesa de Value Investing B3
*Consolidado em 13/10/2026 de: `PLANO-DE-MELHORIAS-2026-10.md`, `PROJECT_BRIEF.md` (§5, §6, §11), `docs/auditoria/AUDITORIA_2026-10-08.md` (Onda 4 e aceitos), `docs/auditoria/CHECKUP_2026-10-10.md`, `09-diario-de-decisoes.md`.*
*Não há PROMPT-MESTRE nem HANDOFF neste repo.*

**Tipos:** `executável` = a rotina na nuvem faz só com o GitHub (sem ZIPs da CVM, sem Agendador) · `decisão Frank` = precisa de resposta, dinheiro ou preferência dele · `local` = só roda na máquina do Frank (dados fora do git, Agendador, OneDrive).
**Prioridade:** P1 (agora/prazo externo) · P2 · P3 · P4 (sem prazo).
**Status:** aberto · em andamento · bloqueado · parado.

| ID | Item | Prio | Status | Tipo | Origem |
|---|---|---|---|---|---|
| B01 | Temporada 3T26: `python ferramentas/temporada.py` quando sair o ITR (fim de out–nov); régua congelada até lá; reemitir só PDFs afetados | P1 | aberto (data externa) | local | Brief §6.2; Plano F8 |
| B02 | Monitor semanal (sexta 08:00, Agendador) → `BOLETINS/AAAA-MM-DD-monitor.md`; ler quem cruzou compra/saída | P1 | rodando | local | README |
| B03 | `registro_prospectivo.py` a cada rodada aprovada (validação da régua é só prospectiva) | P1 | recorrente | local | Brief §5.3 |
| B04 | Etapa 6 / F6 Carteira: §12 da doutrina (tamanho de posição, concentração, caixa, regra de troca ≥ 3 p.p. líquidos) | P2 | bloqueado (respostas do Frank) | decisão Frank | Plano F6 |
| B05 | AUD-41: 29 de 41 tickers com desconto de controlador zero sem razão registrada — dar razão ou exigir razão não vazia no motor (`filtros_1a4`) | P2 | aceito no 09, pendente de decisão | decisão Frank | Auditoria Onda 3 |
| B06 | Pré-registro AUD-32/98/99: critério contínuo (postos P/C × retorno excedente), comparador = média do hall (não Ibovespa), regra de uma linha por (ticker, rodada) | P2 | pendente de decisão | decisão Frank | Auditoria Onda 3 |
| B07 | Perguntas do brief §11: orçamento mensal, SaaS só seu ou de terceiros (enquadramento CVM), objetivo acadêmico, agente de sexta no Desktop ainda roda?, fonte paga no lugar da StatusInvest, licença do código | P2 | aberto | decisão Frank | Brief §11 |
| B08 | Dossiês das finalistas da triagem (5 de 104 passaram no portão; fila em `prospectivo/triagem.jsonl`); parecer de saúde/farma é do Frank | P2 | aberto | decisão Frank | Plano F5 |
| B09 | Registrar no `09` e no brief a rodada de 10/10 (boletim, 2 pastas em `_historico/`) se ainda não estiver | P2 | feito 13/10 (já estava) | executável | Checkup 10/10 |
| B10 | Onda 4 (qualidade): AUD-49 (config da carteira, lock de dependências, requirements) | P2 | feito 13/10 | executável | Auditoria Onda 4 |
| B11 | Onda 4: AUD-106 termos de uso das fontes (B3 COTAHIST, StatusInvest) para redistribuição — só fonte nota A | P3 | aberto (14/10: páginas de termos B3 500 / StatusInvest 403; tentar de novo ou Frank cola o texto) | executável | Auditoria Onda 4 |
| B12 | Onda 4: AUD-96 rótulos, AUD-64/65 fichas, AUD-48/105 textos de documentação, AUD-87 encoding | P3 | feito 14/10 (AUD-64 → B23) | executável | Auditoria Onda 4 |
| B13 | Onda 4: AUD-57/60 premissas provisórias e sensibilidade | P3 | relatório feito 14/10 (propostas pendentes) | executável | Auditoria Onda 4 |
| B14 | Ke real de 21–27% nos muito alavancados (KLBN11 77%): vigiar/revisar o Kd sintético e Hamada | P3 | relatório feito 14/10 (KLBN11 hoje 54,7%) | executável | Brief §5.1 |
| B15 | Premissas digitadas nos `lote*.py` e mercado em data fixa: mover para dados + coleta periódica (bloqueia o SaaS) | P3 | aberto | executável | Brief §5.2 |
| B16 | Confirmar com fonte A o enquadramento CVM (Res. 20/2021 analista; Res. 19/2021 consultor) se houver SaaS | P4 | aberto | executável | Brief §7 |
| B17 | Rumo SaaS (front-end, dados diários, licença) | P4 | parado (sem prazo) | decisão Frank | Brief §2 |
| B18 | 2º comitê de outra família de modelo (D14) e reenvio da pasta de upload ao Desktop | P4 | suspenso ("não tem ajudado") | decisão Frank | Plano F7; memória |
| B19 | Backtest: proxy 70,7% (portão ≥ 80%) — retomar ou abandonar de vez | P4 | parado | decisão Frank | Plano F3 |
| B20 | Backup `backup_dados.py` (OneDrive + git bundle) em dia; disco C com pouco espaço (~4,6 GB) | P3 | recorrente | local | Brief §4, §7 |
| B21 | Suíte do backtest (308 testes, ~13 min) rodar sozinha e com a máquina folgada após mudança em `Mercado`/motores | P3 | sob demanda | local | Brief §4 |
| B23 | AUD-64: tabela única de P/C por premissa (janela IFRS 16, sem desconto de controlador, sem corte de "outras", atuarial, capex LTM) na ficha da PETR4 (`lote5_textos.py`) | P3 | aberto | executável | Auditoria Onda 4 |
| B22 | Executar compras/vendas (ex.: posição em ITSA4 acima da saída) — **nunca pelo Claude** | — | do Frank | decisão Frank | Regra: sem ordem de compra/venda |

## Contagem por tipo
executável: 8 (B09–B16) · decisão Frank: 9 (B04–B08, B17–B19, B22) · local: 5 (B01–B03, B20, B21) · total 22.
