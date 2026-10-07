# Mesa de Value Investing — B3
*Projeto de apoio à análise fundamentalista · doutrina v2.2 · 05/10/2026*

## Ordem de leitura

| Arquivo | Quando usar |
|---|---|
| `00-CONFIGURACAO-DO-PROJETO.md` | **Primeiro.** Nome, descrição e instruções para colar no Claude Desktop |
| `01-doutrina-value-investing.md` | Referência permanente (v2.2): filtros, hierarquia, Ke e RF líquida, vetores de controlador, proventos, armadilhas, régua contínua, notas, **quadro clássico e regra do valor central** |
| `02-prompt-analise-completa.md` | Toda análise nova de um ticker: o **dossiê** (v4, 07/10/2026) |
| `03-hall-de-acoes.md` | Índice vivo das 41 empresas com veredito, preços, pendências e histórico de revisões |
| `04-checklist-anti-erro.md` | **Obrigatório** antes de fechar qualquer análise (v2, 18 erros históricos) |
| `05-prompt-reavaliacao.md` | Quando sair DRE nova ou mudar premissa (v2: quadro clássico inteiro recalculado) |
| `06-triagem-e-fila.md` | Para avaliar candidatas novas e definir a fila |
| `07-perfil-do-investidor.md` | Calibragem de tom, prioridades e postura |
| `08-prompt-recalculo-lote.md` | Refazer um lote inteiro pela doutrina v2.2, com os erros da auditoria de 04/10 por lote |
| `PROMPT-AGENTE-NOTICIAS-SEXTA.md` | Tarefa agendada do Desktop (sexta 18h): Boletim Value com fatos que mudam valor, risco ou proventos |

## Fluxos de trabalho

**Analisar uma ação nova**
`06-triagem` (se ainda não estiver na fila) → `02-prompt` (dossiê; no Claude Code, `cd ferramentas && python -m dossie.gerar <TICKER>` gera o anexo mecânico) → `04-checklist` → dossiê aprovado em `DOSSIES/` + atualizar `03-hall` → `python registro_prospectivo.py --dossie` (registra o veredito com `origem` "dossie")

**Reavaliar após resultado**
`03-hall` (ficha anterior) → `05-prompt-reavaliacao` → `04-checklist` → atualizar `03-hall` + registro de revisões

**Recalcular um lote pela v2.2** *(os 6 lotes recalculados em 04–05/10/2026; Etapas 1 e 2 do plano de melhorias concluídas)*
PDF do lote → `08-prompt-recalculo-lote` → `04-checklist` → novo PDF `…_rev_DD-MM-AAAA.pdf` → atualizar `03-hall` (inclusive ranking Greenblatt)

**Ampliar o hall**
`cd ferramentas && python -m triagem.rodar` (regera o `06` com a fila de toda a B3; não editar o `06` à mão) → fila por camada → `02-prompt` um a um

**Preço da semana**
O Agendador roda `ferramentas/monitor_semanal.py` toda sexta às 08:00 (tarefa `ValueInvesting-MonitorSemanal`) → `BOLETINS/AAAA-MM-DD-monitor.md` com quem cruzou compra ou saída → `05-prompt-reavaliacao` antes de qualquer decisão. Reinstalar: `ferramentas/agendador/instalar_tarefa.ps1`.

**Fechar um lote em PDF**
Conjunto de análises completas → fichas de 2 páginas por empresa (veredito, notas 0–10, quadro clássico, tabela de reconstrução do central, proventos, comparativo com renda fixa líquida, qualitativo 0–5, buy & hold, riscos e gatilhos)

## Ferramentas (cálculo reproduzível)

`ferramentas/` tem os motores de valuation (`motor_financeiras.py` e `motor_nao_financeiras.py`, fórmulas da doutrina v2.2), os coletores (`coletar_cvm.py` — DFP/ITR da CVM, fonte A — e `coletar_statusinvest.py`), as premissas e textos dos 6 lotes (`loteN_*.py`), os geradores de PDF (`gerar_pdf_loteN.py`) e os atualizadores do hall (`atualizar_hall_loteN.py`). Refazer um lote: `cd ferramentas && python gerar_pdf_loteN.py`. `dossie/` (anexo mecânico do dossiê: FRE, notas-base por evidência, vereditos em `dossie/vereditos/`; dossiês aprovados: BLAU3, CMIN3, HYPE3), `triagem/` (fila de toda a B3, sem veredito) e `monitor_semanal.py` (preço semanal do hall) reusam o ledger point-in-time e o COTAHIST de `backtest/`. `registro_prospectivo.py` guarda o veredito do dia, append-only, com `origem` ("hall" ou "dossie") na chave. Os dados brutos ficam em `ferramentas/dados/` (não sobem para o Desktop).

## Pasta de upload

`UPLOAD CLAUDE DESKTOP/` é **cópia** (gerada em 04/10/2026) do que vai para o projeto no Claude Desktop: os .md acima, os 6 PDFs vigentes e `COLAR-NO-CAMPO-INSTRUCOES.txt`. Os originais são os desta raiz — ao alterar qualquer arquivo, recopiar a pasta inteira e re-subir.

## Histórico

Versões substituídas ficam em `_historico/` (a v1.0 de 07/09/2026 está em `_historico/2026-10-04 v1.0/`).

## Princípio que governa o projeto

> Mantenha o próprio julgamento. Corrija por mérito, nunca por pressão. Diga "não encontrado" sem constrangimento. E lembre que a melhor empresa do mundo, no preço errado, é o pior investimento.

## Aviso

Nada aqui é recomendação de investimento. É análise independente, com fontes citadas e incertezas declaradas, para apoiar decisão própria.
