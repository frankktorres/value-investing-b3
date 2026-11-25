# Fichas de fonte — B46 (emenda 12 do `docs/PRE-REGISTRO-v3.md`) — 25/11/2026

Protocolo: `~/.claude/PESQUISA.md` §4. PDFs e planilhas baixados do site do autor em 25/11/2026 e lidos localmente (pypdf;
xlrd numa pasta temporária, sem dependência nova no repositório). Os números das planilhas usados estão em
`ferramentas/b46/insumos/` (JSON com URL, data e nota).

## F1 — Hamada supõe dívida sem risco de mercado
- **Fonte:** Damodaran, *Investment Valuation*, 2ª ed. (2002), cap. 8, p. 20, nota 8.
  https://pages.stern.nyu.edu/~adamodar/pdfiles/valn2ed/ch8.pdf (acesso 25/11/2026)
- **Trecho:** "If all the firm's risk is borne by the stockholders (i.e., the beta of debt is zero) and debt has a tax benefit
  to the firm, then, βL = βu (1 + (1 − t) D/E)". Nota 8: "If debt has market risk (i.e., its beta is greater than zero), the
  original formula can be modified to take it into account. If the beta of debt is βD, the beta of equity can be written as:
  βL = βu [1 + (1 − t) D/E] − βD (1 − t) D/E".
- **Nota B** (primária, edição antiga). **Uso:** mostra o domínio do Hamada; a opção A (β_D > 0) caiu por falta de fonte para
  o β_D (emenda 12).

## F2 — D/E de dificuldade na perpetuidade é incoerente; separar a dificuldade
- **Fonte:** Damodaran, A. *Valuing Distressed and Declining Companies*, Stern School of Business, jun/2009.
  https://pages.stern.nyu.edu/~adamodar/pdfiles/papers/NewDistress.pdf (acesso 25/11/2026)
- **p. 14:** "Many declining and distressed companies have debt ratios that are vastly higher than the industry average and are
  not sustainable in the long term or compatible with a going concern. Thus, the valuation of an airline that uses a market
  debt to capital ratio of 90% and leaves it at that value, while assuming that the airline will return to financial health is
  being internally inconsistent."
- **p. 37:** "Note, though, that it is reasonable to re-estimate debt to equity ratios and tax rates for future years based upon
  our expectations for the firm and adjust the beta to reflect these changes." Nota 12: "Some analysts, for instance, prefer a
  more complete version that allows debt to carry systematic risk and have a beta."
- **p. 38:** "As we make our forecasts for future years and build in our expectations of improvements in profitability, we
  should adjust the debt ratio towards more reasonable levels. The conventional practice of using target debt ratios for the
  entire valuation period (which reflect industry averages or the optimal mix) can lead to misleading estimates of value for
  firms that are significantly over levered." — "Firm Value = Going concern value * (1-πDistress) + Distress sale value *
  πDistress".
- **p. 39:** going concern "we make the assumption that debt ratios will, in fact, decrease over time, if the firm is over
  levered"; tratar como saudável já hoje "will overstate firm value by assuming that the return to financial health is both
  painless and imminent".
- **p. 41–42, Tabela 5** ("Bond Rating and Probability of Default – 1971 - 2007", Altman 2007), 10 anos: AAA 0,07% · AA 0,51% ·
  A+ 0,57% · A 0,66% · A- 5,00% · BBB 7,54% · BB 19,63% · B+ 28,25% · B 36,80% · B- 42,12% · CCC 59,02% · CC 66,6% · C+ 75,16% ·
  C 81,03% · C- 87,16%. p. 42: "table 5 measures the likelihood of default on a bond, but it does not indicate whether the
  defaulting firm goes out of business. Many firms continue to operate as going concerns after default."
- **Nota B** (primária, working paper do autor). **Uso:** mecanismo e π da emenda 12.

## F3 — D/E a mercado por indústria, emergentes
- **Fonte:** Damodaran, *Cost of equity and capital (updateable)*, Emerging Markets, `waccemerg.xls`, aba "Industry Averages",
  coluna "D/(D+E)"; atualizado em 05/01/2026. https://pages.stern.nyu.edu/~adamodar/pc/datasets/waccemerg.xls
- **Definição (aba "Variables & FAQ"):** "Total Debt (including lease debt)/ (Total Debt (including lease debt)+ Market Cap),
  aggregated across all firms in group" — a mesma dívida do motor (bruta com arrendamentos, `divida_do_desconto`).
- **Classificação:** `indname.xls`, aba "By company name", 249 linhas "BOVESPA:" (indústria por ticker).
  https://pages.stern.nyu.edu/~adamodar/pc/datasets/indname.xls
- **Nota B** (dado do autor). Ex.: Steel 0,3373 (D/E 0,509) · Transportation 0,3703 (0,588) · Food Processing 0,2754 (0,380) ·
  Retail (Automotive) 0,4269 (0,745) · Homebuilding 0,4132 (0,704).

## F4 — Z'' e rating equivalente
- **Fonte:** Altman, E. I., *50 Years of Altman Z-Score: what have we learned and the applications in financial and managerial
  markets* (apresentação, LSE / Systemic Risk Centre), slides 25–26; a mesma tabela está em *The Evolution & Applications of
  the Altman Z-Score Family of Models & Global Credit Markets* (Hofstra). Lidos em 25/11/2026 (PDF baixado pelo
  `verificador-fonte`, texto extraído com pypdf).
- **Slide 25:** "Z'' = 3.25 + 6.56X1 + 3.26X2 + 6.72X3 + 1.05X4"; X1 = (ativo circulante − passivo circulante) ÷ ativo total;
  X2 = lucros retidos ÷ ativo; X3 = EBIT ÷ ativo; X4 = PL contábil ÷ passivo total — **confere** com `altman_z2`
  (`ferramentas/motor_nao_financeiras.py`).
- **Slide 26, "US Bond Rating Equivalents Based on Z''-Score Model", coluna "Median 2013 Z''-Score":** AAA/AA+ 8,80 · AA/AA- 8,40 ·
  A+ 8,22 · A 6,94 · A- 6,12 · BBB+ 5,80 · BBB 5,75 · BBB- 5,70 · BB+ 5,65 · BB 5,52 · BB- 5,07 · B+ 4,81 · B 4,03 · B- 3,74 ·
  CCC+ 2,84 · CCC 2,57 · CCC- 1,72 · CC/D 0,05 ("Sources: Compustat, Company Filings and S&P").
- **Nota B** (apresentação do autor, não o artigo revisado). A coluna de 2006 não é monotônica (AA/AA- 7,78 > AAA/AA+ 7,51); por
  isso a emenda 12 usa a de 2013.
- **Secundária não usada:** IMF WP 2019/093, Text Table 1 (nota C; faixas atribuídas a Altman 2005 com uma lacuna 8,15–8,5).

## NÃO VERIFICADO
- Altman (2005), *Emerging Markets Review* 6:311–323 (EM Score; artigo pago, não aberto).
- Schaefer & Strebulaev (2008), betas de dívida por rating (não aberto; por isso a opção A caiu).
- Rating de agência em escala global das empresas da Mesa (3ª estimativa do π sugerida pelo `senior`): sem fonte A mecânica.
