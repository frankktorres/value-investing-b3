---
name: mesa-kaizen
description: Revisão mensal das REGRAS da Mesa de Value Investing — regra que ninguém cumpre sai (ou vira trava), erro que se repetiu vira trava com canário. Só leitura + um relatório com propostas; quem muda regra é o Frank. Neste repositório substitui o /kaizen global. Use quando o Frank pedir "kaizen" ou pelo agendamento mensal.
---

# /mesa-kaizen — revisão mensal das regras

O `/mesa-checkup` olha os **fatos** (travas vivas, catracas, docs × código); o kaizen olha as **regras**: as que
atrapalham, as que ninguém cumpre e os erros que voltaram. **Só leitura + um relatório** em `docs/kaizen/AAAA-MM-DD.md`
(≤ 60 linhas). Mudar regra (CLAUDE.md, DNA, doutrina, travas) é do Frank: cada proposta vai para `docs/PENDENTE-FRANK.md`
com recomendação e o porquê em 1 linha.

## O que ler (nesta ordem; leitura ampla → `varredor` com orçamento)
1. `docs/DECISOES.md` e `docs/RELATORIO-DIARIO.md` do último mês: decisões revertidas, mesma decisão tomada duas vezes,
   "reversível" que na verdade mudou palavra.
2. `git log --since="1 month ago" --format="%h %s"`: commits de conserto do mesmo tipo de erro (ex.: unidade, PIT,
   ausente → zero, data fixa, push vermelho). **Erro que apareceu 2 vezes vira proposta de trava com canário.**
3. `CLAUDE.md`, `.claude/agents/senior.md` (26 checagens), `.claude/skills/mesa-*`: para cada regra, houve no mês um caso
   em que ela foi seguida? E um em que foi furada? Regra sem caso nenhum e sem trava = candidata a sair ou a virar trava.
4. Último relatório do `/mesa-checkup` (pasta docs/checkups): achados 🔴/🟡 repetidos de um mês para o outro.
5. `docs/PENDENTE-FRANK.md`: pergunta parada > 30 dias = a rotina está travando no Frank; propor decisão padrão.

## Relatório
Tabela: regra ou erro · evidência (hash/arquivo:linha) · proposta (manter / tirar / virar trava + canário) · quem decide.
Termine com as 3 propostas de maior valor/custo e "Próximo kaizen: <data + 1 mês>". Commit só do relatório.
