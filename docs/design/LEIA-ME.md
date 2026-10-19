# Design da tela (Claude Design, 19/10/2026)

`mesa-de-value-telas.zip`: mockups do Claude Design (Hall, Empresa, Carteira, Sistema; claro e escuro), `tokens.css` e
`support.js` (runtime próprio do Design, React embutido, formato `.dc.html`). Para ver: descompactar fora do repo,
`python -m http.server 8000` na pasta e abrir `http://localhost:8000/Main.dc.html`.

É **referência visual**, não código do produto:
- os dados são ilustrativos e o mockup recalcula a palavra pelo P/C de hoje — a tela de verdade mostra a palavra
  **vigente** (veredito gravado ou golden) e nunca recalcula;
- o código da tela está em `ferramentas/painel/web/` (HTML/CSS/JS sem build), com o `tokens.css` copiado daqui e o token
  RADAR acrescentado;
- itens do mockup que o motor não calcula ficaram fora (renda fixa, projeção da carteira, data de cruzamento da meta,
  sparkline de 12 meses, yield projetado) até o motor fornecer o dado com fonte.
