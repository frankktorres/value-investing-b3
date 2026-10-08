---
description: Atualiza o PROJECT_BRIEF.md (insumo do relatório semanal de tecnologias/ferramentas/métodos)
---

Analise este repositório inteiro (código, README, CLAUDE.md, docs, issues/TODOs, dependências) e crie ou atualize o arquivo
PROJECT_BRIEF.md na raiz. Ele vai alimentar um relatório semanal automático que sugere tecnologias, ferramentas e métodos para melhorar
este projeto. Seja factual: o que não souber, escreva "não informado" e liste no final como pergunta para mim.

Leitura ampla vai para subagente (`Explore`/`varredor`); use também a memória do projeto e o relatório de auditoria mais recente em
`docs/auditoria/`. Versões de libs: as do código e do ambiente (`pip list`), dizendo se estão fixadas ou não.

ANTES DE SOBRESCREVER: se já existir um PROJECT_BRIEF.md, copie-o para `_historico/AAAA-MM-DD brief/PROJECT_BRIEF.md` (data de hoje) e
use-o para preencher a seção 12.

REGRAS: no máximo ~1,5 página. NUNCA inclua segredos, chaves, URLs internas (inclusive a do repositório remoto), dados de pacientes ou
dados pessoais (posições da carteira, nomes de terceiros, dispositivos pessoais). Português.

ESTRUTURA:
1. Projeto: nome, objetivo e público (2 linhas)
2. Estágio: ideia / MVP / produção; usuários reais?; prazos conhecidos
3. Stack: linguagens, libs principais (com versão), banco, infra/hospedagem, APIs externas
4. Arquitetura: módulos principais em 5–10 linhas
5. Top 5 gargalos atuais (técnicos, científicos, de produto ou de negócio), do mais crítico ao menos crítico, com evidência no código
   quando houver
6. Próximos 3 marcos do roadmap
7. Restrições: orçamento, hardware, LGPD/dados sensíveis, regulatório (Anvisa, ANPD, CFF, CVM etc.), licenças
8. Ferramentas já usadas e já descartadas (com motivo, se houver registro)
9. Onde IA já é usada e onde poderia entrar
10. O que significa "melhor" para este projeto: critérios técnicos, científicos, acadêmicos e profissionais
11. Perguntas para o Frank (o que você não conseguiu inferir)
12. O que mudou desde a última versão deste brief (se existir uma anterior; se não, escreva "primeira versão")

Ao terminar, imprima o PROJECT_BRIEF.md completo. Não faça commit sem o Frank pedir.
