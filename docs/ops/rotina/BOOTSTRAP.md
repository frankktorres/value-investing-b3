# Texto publicado na nuvem (rotina "VALUE B3 – noturno", trig_016wrGPsNHp4dUaVAExNhZyU)

O bloco abaixo é LITERAL: é o que está no campo de comando da rotina. Mudou aqui → atualizar na nuvem (RemoteTrigger
`update`) no mesmo dia e gravar a conferência com `cd ferramentas && python -m rotina.nuvem conferir <texto devolvido pelo get>`
(o teste `tests/test_rotina.py` compara o hash deste bloco com `docs/ops/rotina/nuvem.json`). O `/mesa-fechar` confere.
Regras da noite NÃO entram aqui: vão em `docs/ops/rotina/PROTOCOLO.md`. Versão anterior do comando (5 mil caracteres, só na
nuvem até 26/11/2026): `_historico/2026-11-26 rotina-nuvem/comando-nuvem-ate-2026-11-26.md`.

```text
ROTINA NOTURNA DA MESA DE VALUE INVESTING (B3). Trabalhe sem pedir OK. Nunca faça push no master nem abra PR: commit e push só no ramo claude/* desta sessão. Nunca execute nem apresente como feita ordem de compra ou venda.

TRAVA DE SOBREPOSIÇÃO (fazer ANTES de tudo): rode `git fetch --all --prune`. Para cada OUTRO ramo origin/claude/* (não o desta sessão) com commit fora do master (`git rev-list --count origin/master..<ramo>` maior que 0) e cujo último commit tem menos de 24 h, NÃO trabalhe. Exceção, e só ela: essa contagem é 1, `git diff --name-only origin/master...<ramo>` (três pontos) lista SÓ docs/RELATORIO-DIARIO.md e o topo desse relatório no ramo tem "rotina pulada", "BASE VERMELHA" ou "AMBIENTE QUEBRADO"; esse ramo não conta. Fora da exceção: escreva no topo de docs/RELATORIO-DIARIO.md (acima do primeiro bloco "## ") o bloco "## AAAA-MM-DD · Rotina na nuvem (ramo <este ramo>)" com 1 linha ("rotina pulada: rodada anterior não juntada — <ramo>"), commit só desse arquivo, push e encerre. Motivo: a junção no master é feita de manhã no PC do Frank (ferramentas/conferir_noite.py, com os dados locais); trabalhar por cima de rodada não juntada gera duplicata e conflito.

DEPOIS DA TRAVA: abra docs/ops/rotina/PROTOCOLO.md da origin/master (`git show origin/master:docs/ops/rotina/PROTOCOLO.md`) e siga-o INTEIRO, na ordem, como se fosse este comando. Ele é o comando desta rotina (versionado no git; esta mensagem só aponta para ele) e começa pelo PRÉ-VOO, que é obrigatório.

Se o arquivo não existir ou não abrir: escreva o mesmo bloco com 1 linha ("rotina pulada: PROTOCOLO.md ausente na origin/master"), commit + push e encerre.
```
