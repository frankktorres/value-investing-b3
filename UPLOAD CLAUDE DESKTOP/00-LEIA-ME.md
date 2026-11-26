# Mesa de Value Investing — LEIA-ME do projeto no Claude Desktop

Esta pasta é **cópia gerada** do repositório da Mesa (`python -m desktop.atualizar`, ou `ATUALIZAR.bat`). O Desktop serve para **consulta e conversa**; método, números e palavra só valem do repositório (motor em Python, suíte verde, commit no `master`). Se algo aqui contradizer o repo, vale o repo.

## O que fazer no Desktop

1. Campo **Instruções** do projeto: apagar o texto antigo e colar o de `COLAR-NO-CAMPO-INSTRUCOES.txt`.
2. **Conhecimento** do projeto: subir os arquivos que o gerador listou como NOVO ou TROCAR (apagar a versão antiga de mesmo nome antes) e apagar os que ele listou como SAIU. A lista exata fica no fim do `MANIFESTO.txt` (que não sobe).
3. Não subir `MANIFESTO.txt` nem `COLAR-NO-CAMPO-INSTRUCOES.txt`.

## Ordem de leitura sugerida

`00-DNA.md` → `00-O-QUE-MUDOU.md` → `02-MAPA-DA-MESA.md` → `01-doutrina-value-investing.md` → o resto sob demanda.

## Arquivos

| Arquivo | O que é | Origem no repo |
|---|---|---|
| `00-LEIA-ME.md` | Este guia: o que é cada arquivo e o que trocar no Desktop | gerado por `ferramentas/desktop/atualizar.py` |
| `00-O-QUE-MUDOU.md` | O que entrou e o que saiu desde 21/10/2026 (última carga do Desktop) | gerado por `ferramentas/desktop/atualizar.py` |
| `02-MAPA-DA-MESA.md` | Arquitetura: motores, oráculo, agentes, quem decide, travas, skills, rotinas, fluxo de método | gerado por `ferramentas/desktop/atualizar.py` |
| `COLAR-NO-CAMPO-INSTRUCOES.txt` | Texto do campo Instruções do projeto (colar, não subir) | gerado por `ferramentas/desktop/atualizar.py` |
| `00-DNA.md` | Norte do projeto: visão, princípios, onde estamos, as 4 causas da B36 e os marcos M1–M5. Ler antes de qualquer conversa sobre rumo | `docs/00-DNA.md` (cópia exata) |
| `00-CONFIGURACAO-DO-PROJETO.md` | Configuração antiga do projeto (10/10). As instruções vigentes são as do COLAR-NO-CAMPO-INSTRUCOES.txt | `00-CONFIGURACAO-DO-PROJETO.md` (cópia exata) |
| `01-doutrina-value-investing.md` | Doutrina vigente (método, filtros, régua, quadro clássico) | `01-doutrina-value-investing.md` (cópia exata) |
| `02-prompt-analise-completa.md` | Roteiro do dossiê de um ticker | `02-prompt-analise-completa.md` (cópia exata) |
| `03-hall-de-acoes.md` | Hall: palavra, preço e central de cada empresa (gerado pelo motor) | `03-hall-de-acoes.md` (cópia exata) |
| `04-checklist-anti-erro.md` | Checklist obrigatório antes de fechar uma análise | `04-checklist-anti-erro.md` (cópia exata) |
| `05-prompt-reavaliacao.md` | Roteiro de reavaliação após resultado ou premissa nova | `05-prompt-reavaliacao.md` (cópia exata) |
| `06-triagem-e-fila.md` | Triagem de toda a B3 e fila (gerado; sem palavra) | `06-triagem-e-fila.md` (cópia exata) |
| `07-perfil-do-investidor.md` | Perfil e prioridades do investidor | `07-perfil-do-investidor.md` (cópia exata) |
| `08-prompt-recalculo-lote.md` | Roteiro de recálculo de um lote | `08-prompt-recalculo-lote.md` (cópia exata) |
| `PRE-REGISTRO-v3.md` | Pré-registro: hipóteses, critérios e emendas, escritos ANTES de rodar | `docs/PRE-REGISTRO-v3.md` (cópia exata) |
| `BACKLOG.md` | Fila de itens (abertos e feitos), com prioridade e origem | `docs/BACKLOG.md` (cópia exata) |
| `DECISOES.md` | Decisões tomadas (opção, motivo, como reverter) | `docs/DECISOES.md` (cópia exata) |
| `PENDENTE-FRANK.md` | O que só o Frank decide, com recomendação | `docs/PENDENTE-FRANK.md` (cópia exata) |
| `PROJECT_BRIEF.md` | Resumo técnico do projeto: stack, ferramentas, gargalos, ADRs | `PROJECT_BRIEF.md` (cópia exata) |
| `REL-B36-holdout-2026-11.md` | Relatório da B36: o motor v2.7 em 20 ações de fora (NÃO PASSOU) | `docs/holdout/B36-2026-11.md` (cópia exata) |
| `REL-B39-ke-implicito-2026-11.md` | Relatório da B39: Ke da Mesa × Ke implícito (não dispara) | `docs/b39/B39-2026-11.md` (cópia exata) |
| `REL-B46-ke-acima-30-2026-11.md` | Relatório da B46: Ke > 30% (NÃO CONCLUSIVA) | `docs/b46/B46-2026-11.md` (cópia exata) |
| `REL-B46-tentativa-8-2026-11.md` | B46, tentativa 8/24, depois da B57 | `docs/b46/B46-2026-11-t8.md` (cópia exata) |
| `REL-B57-fontes-x2-altman.md` | B57: fontes do X2 do Z'' (2.03.04 + 2.03.05); o resultado está no PRE-REGISTRO §6 | `docs/b57/FONTES-B57.md` (cópia exata) |
| `PACOTE-AUTONOMIA-2026-11-25.md` | Pacote de autonomia: agentes, travas 4.x, skills mesa-*, quem decide | `docs/research/2026-11-25-pacote-autonomia.md` (cópia exata) |
| `PROMPT-AGENTE-NOTICIAS-SEXTA.md` | Tarefa agendada do Desktop (sexta): boletim de notícias | `PROMPT-AGENTE-NOTICIAS-SEXTA.md` (cópia exata) |

## Fora do Desktop (de propósito)

- Dados brutos (`ferramentas/dados/`), séries, golden e carteira com valores: ficam na máquina/no git.
- PDFs dos lotes de 09/10/2026: calculados antes da doutrina v2.7 (D/E a mercado); números superados. O relatório atual de um ticker sai do repo (`relatorio <TK>`).
- `09-diario-de-decisoes.md` (162 KB, histórico); as decisões vigentes estão em `DECISOES.md`.

> Nada aqui é recomendação de investimento.
