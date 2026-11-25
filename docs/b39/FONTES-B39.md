# B39 — conferência das fontes contra a emenda 9 (antes de qualquer conta)

Data do acesso: 25/11/2026. Nenhum número da B39 foi calculado antes desta conferência. Os arquivos baixados ficam fora do git
e podem ser baixados de novo pelas URLs abaixo. Protocolo de nota: `~/.claude/PESQUISA.md` (A = dado oficial primário;
B = texto do autor aberto e lido).

## Fontes abertas

| # | Fonte | O que foi aberto | Nota |
|---|---|---|---|
| D1 | Damodaran, *Country Default Spreads and Risk Premiums*, `pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html` | Página inteira, "Last updated: January 5, 2026" (cópia baixada em 25/11/2026) | B |
| D2 | Damodaran, *Country Risk: Determinants, Measures and Implications — The 2024 Edition* (jul/2024), `pdfiles/papers/countryrisk2024formatted.pdf` | Texto inteiro (pdftotext); p. 101 e Tabela 30 | B |
| D3 | Damodaran, *What is the riskfree rate? A Search for the Basic Building Block* (dez/2008), `pdfiles/papers/riskfreerate.pdf` | Texto inteiro; seção "The Solution" | B |
| D4 | Damodaran, `pdfiles/blog/CountryRisk2025.pdf` | É a apresentação de slides de jul/2025, não o paper. O paper "2025 Edition" não está no site do autor; o SSRN 4896539 recusou o acesso (403) | não serve de base |
| S1 | Campbell & Shiller, *Valuation Ratios and the Long-Run Stock Market Outlook: An Update*, NBER WP 8221 (2001), `nber.org/papers/w8221.pdf` | Texto inteiro (pdftotext); p. 8–10 e nota 9 | B |
| S2 | Campbell & Shiller (1998), *Journal of Portfolio Management* 24(2):11–26 | Só a referência (RePEc/NBER: "update of our earlier paper (1998)"); o texto não foi aberto | referência conferida |
| S3 | Shiller, *Irrational Exuberance* | Não aberto. O shillerdata.com só cita "the average of the real earnings per share used in the CAPE ratio" | não serve de base |

## Conferência item por item

| Item da emenda 9 | Texto da fonte | Resultado |
|---|---|---|
| (iii) s = spread de default soberano por rating, ERP total do Brasil em jan/2026 | D1, linha Brazil: "Ba1 · 2.13% (Adj. Default Spread) · 3.24% (Country Risk Premium) · 7.47% (Equity Risk Premium) · 34.00% · CDS 2.21% · 7.59%". O ERP maduro implícito é 7,47 − 3,24 = 4,23%, igual ao dos países Aaa. "To get the default spreads by sovereign rating, I use the CDS spreads and compute the average CDS spread by rating." | **CONFERE.** s = 2,13% (coluna "Adj. Default Spread"); ERP total = 7,47% (coluna "Equity Risk Premium") |
| (iii) Tirar s da taxa do título em moeda local antes de somar o ERP total | D2, p. 101: "estimating the default spread for the government, using either the sovereign rating or the CDS market, and then subtracting that default spread from the government bond rate to get to a risk-free rate". A Tabela 30 dá o caso do real: "Brazilian Reai 11.83% · Ba2 · 2.83% · 9.00%". D3: "the danger of building it into the riskfree rate is that the risk may end up being double counted … we can strip this default spread from the rate to arrive at an estimate of the riskfree rate in that currency" | **CONFERE** na regra. **DIVERGE na citação:** a emenda cita a "edição 2025", e o texto aberto é o da edição 2024 + D3 |
| (iii) Título indexado à inflação de governo com risco de default | D3 só trata o TIPS (EUA, sem default) como rf real: "markets without inflation-indexed, default-free securities". Não há regra para um título indexado de governo com risco de default | **SILÊNCIO.** A emenda converte a NTN-B em nominal (n) e tira s dela. É uma extensão nossa, coerente com a regra do D2/D3, e é declarada como tal |
| (ii) E10 = média de 10 anos dos lucros reais; P = preço real; mínimo de 5 exercícios | S1, p. 9: "Following their advice we smooth earnings by taking an average of real earnings over the past ten years", com o preço "real stock price". Graham & Dodd (1934, p. 452), citado em S1: "not less than five years, preferably seven or ten years" | **CONFERE**, e o mínimo de 5 tem a mesma origem |
| (ii) Ke real implícito = E10 ÷ P, com o "princípio do CAPE (Shiller)" como fonte | S1 usa o P/E10 só como **preditor em regressão**: "the ratio is a good forecaster of ten-year growth in stock prices, with an R2 statistic of 30%". O texto não diz que E10/P é o retorno esperado ou um custo de capital | **DIVERGE na atribuição.** De Shiller vem só a construção do E10. A leitura "E10/P = Ke real, sem crescimento" é o EPV reverso da Mesa (âncora EPV, `01`), não um resultado de Shiller |
| (ii) Fonte "Campbell & Shiller (1998) e *Irrational Exuberance*" | O que foi aberto é o S1 (a atualização de 2001 do mesmo artigo). O S2 só teve a referência conferida e o S3 não foi aberto | **DIVERGE na citação:** a base passa a ser o S1 (nota B) |
| Gatilho com 2 estimativas | A emenda 9 já diz: "com 2 que saem, vale a mediana das 2 (a média)" | Literal, nada a mudar |
| Ajustes do Frank (25/11): Gordon do banco todo em nominal e depois para real; E10 agregado = Σ E10 ÷ Σ valor de mercado | A emenda 9 já diz "Ke nominal = (ROE − g) ÷ (P/VP) + g … g nominal = (1 + g real) × (1 + π) − 1" e "E10 = soma das médias; P = soma dos valores de mercado" | Literal; os dois ajustes viram testes |

## Consequência
Nenhuma divergência muda conta, insumo ou gatilho. Todas são de citação ou de atribuição, e vão para a **emenda 10**
(`docs/PRE-REGISTRO-v3.md` §7), em commit próprio, antes de rodar.
