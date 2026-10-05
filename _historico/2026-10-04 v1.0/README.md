# Mesa de Value Investing — B3
*Projeto de apoio à análise fundamentalista · v1.0 · 07/09/2026*

## Ordem de leitura

| Arquivo | Quando usar |
|---|---|
| `00-CONFIGURACAO-DO-PROJETO.md` | **Primeiro.** Nome, descrição e instruções para colar no Claude Desktop |
| `01-doutrina-value-investing.md` | Referência permanente: filtros, hierarquia, Ke, vetores de controlador, armadilhas, régua do veredito |
| `02-prompt-analise-completa.md` | Toda análise nova de um ticker |
| `03-hall-de-acoes.md` | Índice vivo das 38 empresas com veredito, preços e histórico de revisões |
| `04-checklist-anti-erro.md` | **Obrigatório** antes de fechar qualquer análise |
| `05-prompt-reavaliacao.md` | Quando sair DRE nova ou mudar premissa |
| `06-triagem-e-fila.md` | Para avaliar candidatas novas e definir a fila |
| `07-perfil-do-investidor.md` | Calibragem de tom, prioridades e postura |

## Fluxos de trabalho

**Analisar uma ação nova**
`06-triagem` (se ainda não estiver na fila) → `02-prompt` → `04-checklist` → atualizar `03-hall`

**Reavaliar após resultado**
`03-hall` (ficha anterior) → `05-prompt-reavaliacao` → `04-checklist` → atualizar `03-hall` + registro de revisões

**Ampliar o hall**
`06-triagem` → fila por prioridade → `02-prompt` um a um

**Fechar um lote em PDF**
Conjunto de análises completas → fichas de 2 páginas por empresa (veredito, notas 0–10, quantitativo, proventos, comparativo com renda fixa, valuation multi-modelo, qualitativo 0–5, buy & hold, riscos e gatilhos)

## Princípio que governa o projeto

> Mantenha o próprio julgamento. Corrija por mérito, nunca por pressão. Diga "não encontrado" sem constrangimento. E lembre que a melhor empresa do mundo, no preço errado, é o pior investimento.

## Aviso

Nada aqui é recomendação de investimento. É análise independente, com fontes citadas e incertezas declaradas, para apoiar decisão própria.
