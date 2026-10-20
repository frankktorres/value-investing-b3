# Prompt para colar no Claude Code (VS Code)

**Modelo: Opus · Effort: Alto**
(Se o repo for grande e a etapa 1 pedir muita leitura, comece em Alto e só suba para Máximo se travar.)

Antes de colar: copie esta pasta (`handoff/`) para dentro do repositório, por exemplo em `docs/design/`.

---

Leia `docs/design/HANDOFF.md` inteiro e depois olhe as imagens em `docs/design/referencia/capturas/` (são o alvo visual) e `docs/design/tokens.css`.

Objetivo: criar a primeira interface da Mesa de Value Investing, um painel web local e somente leitura, no estilo das capturas (fintech escura, menu lateral, régua de preço). O front só exibe o que os motores Python já calculam. Ele não calcula valuation.

Faça em etapas, parando ao fim de cada uma para eu validar:

1. Explore o repositório (motores, saídas em JSON/CSV/PDF, como rodam hoje) e me diga em até 15 linhas: o que cada motor já entrega, o que falta para alimentar as quatro telas, e qual stack mais simples você recomenda. Não escreva código ainda.
2. Crie a camada de dados: um script que lê as saídas dos motores e grava `hall.json`, `empresa/<TICKER>.json`, `carteira.json` e `monitor.json` seguindo o contrato do HANDOFF (adapte aos campos reais). Onde o motor não entrega um campo, grave `null` e a interface mostra "—" com nota "sem fonte". Não invente valores.
3. Implemente o shell (menu lateral, barra de topo, tema escuro/claro, Ocultar valores) e as telas na ordem Hall, Empresa, Carteira, Monitor, usando os tokens de `tokens.css`.
4. Compare cada tela com a captura correspondente, lado a lado, e corrija diferenças. Rode a checagem de contraste dos tokens.

Regras que não podem quebrar estão na seção 2 do HANDOFF. Se algo no HANDOFF conflitar com o que os motores realmente fazem, pare e me pergunte em vez de decidir sozinho.
