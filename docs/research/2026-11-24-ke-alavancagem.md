# Fichas de fonte — D/E do Ke e pesos do WACC (missão B34, H2) — 24/11/2026

Protocolo: `~/.claude/PESQUISA.md` §4. Texto aberto localmente (PDF do site do autor baixado em 24/11/2026 e extraído com
pypdf; o WebFetch devolvia o PDF comprimido). A 3ª ed. (`valn3ed/ch8.pdf`) dá 404 — por isso nota **B** (edição antiga).

## F1 — Pesos a valor de mercado, não contábil
- **Pergunta:** os pesos do WACC (e o D/E do beta alavancado) usam valor de mercado ou contábil?
- **Fonte:** Damodaran, A. *Investment Valuation*, 2ª ed. (Wiley, 2002), cap. 8 "Estimating Risk Parameters and Costs of Financing".
- **URL:** https://pages.stern.nyu.edu/~adamodar/pdfiles/valn2ed/ch8.pdf · **acesso:** 24/11/2026
- **p. 47:** "weights used should be based upon market value and not book value. This is so because the cost of capital
  measures the cost of issuing securities – stocks as well as bonds – to finance projects and these securities are issued at
  market value, not at book value."
- **p. 49 ("Book Value versus Market Value Debt ratios"):** "There are three standard arguments against using market value and
  none of them are convincing." Sobre o contábil ser mais conservador: "an assumption not based on fact".
- **p. 50:** "The market value of equity is generally the number of shares outstanding times the current stock price."
- **Primária?** sim (autor). **Conflito:** não. **Confere com:** página de definições do autor (D/E setorial = dívida ÷ valor de
  mercado do patrimônio), https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/variable.htm (jan/2026, lida pelo
  `verificador-fonte` via WebFetch — resumo de modelo auxiliar, não texto bruto).
- **Nota B** — primária, edição de 2002 (a vigente não abre). **Aplica-se:** `01` §2 (pesos) e §4 (Hamada); `estrutura_de_capital`.

## F2 — D/E corrente no beta bottom-up
- **Fonte:** idem, cap. 8, **p. 24:** "bottom-up betas use the current debt to equity ratio. If a firm plans to change its debt to
  equity ratio in the future, the beta can be adjusted to show these changes."
- **Fórmula (p. 21, Ilustração 8.3):** "Levered Beta = Unlevered Beta (1 + (1 - tax rate) (Debt/Equity))", com D/E "using market
  values for debt and equity".
- **Nota B.** **Aplica-se:** E = preço da data-base × ações (sem média de preço — decisão do Frank, 24/11).

## F3 — Dívida bruta, não líquida
- **Fonte:** idem, cap. 15 "Firm Valuation: Cost of Capital and APV Approaches", https://pages.stern.nyu.edu/~adamodar/pdfiles/valn2ed/ch15.pdf
- **p. 24:** "In general, we would recommend using gross debt rather than net debt for two other reasons. First, the net debt can
  be a negative number, if cash exceeds the gross debt. [...] Second, maintaining a stable net debt ratio in a growing firm will
  require that cash balances increase as the firm value increases."
- **p. 24 (quadro):** com dívida bruta, "Cash is added to value of operating assets and net debt is subtracted out to get to
  equity value" — a ponte soma o caixa e desconta a dívida bruta.
- **Cap. 8, p. 51:** "It is generally safer to value a firm based upon gross debt outstanding and to add the cash balance
  outstanding to the value of operating assets [...] In general, using net debt ratios will overstate the value of riskier firms."
- **Nota B.** **Aplica-se:** tira "dívida líquida" da Fase 5 item 2 (`docs/PROMPT-ORACULO-E-CALIBRACAO.md`); D = dívida bruta com
  arrendamentos nos pesos, no Hamada e na ponte (mesma dívida).

## F4 — Iteração dos pesos (opção B, não escolhida)
- **Fonte:** idem, cap. 15, **pp. 7–8** ("Market Value Weights, Cost of Capital and Circular Reasoning"): "Every textbook is
  categorical that the weights in the cost of capital calculation be market value weights. [...] To those who are bothered by
  this inconsistency, there is a way out. You could do a conventional valuation using market value weights [...] then use the
  estimated values of debt and equity from the valuation to re-estimate the cost of capital."
- Defesa dos pesos a mercado (p. 7): "if you went out and bought all of the debt and equity in a publicly traded firm, you would
  pay current market value and not your estimated value and your cost of capital reflects this."
- **Ressalva:** o trecho trata dos pesos; não diz se o beta realavancado entra no laço (onde nasce o H2).
- **Nota B.**

## NÃO VERIFICADO
- Koller, Goedhart, Wessels (McKinsey), *Valuation* — estrutura-alvo e circularidade: livro pago, não aberto.
- Planilha de betas por setor de **emergentes** (Damodaran, jan/2026): não aberta (só a dos EUA).

## F5 — Prazo do ITR (recálculo do dossiê na data, point-in-time)
- **Pergunta:** a partir de quando o LTM de um trimestre já estava publicado?
- **Fonte:** CVM, Resolução CVM nº 80/2022 (texto consolidado), art. 31, II — p. 21 do PDF.
- **URL:** https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/001/resol080consolid.pdf · **acesso:** 24/11/2026
  (baixado e extraído com pypdf).
- **Trecho:** "II – entregue pelo emissor no prazo de 45 (quarenta e cinco) dias contados da data de encerramento de cada
  trimestre." § 3º: "O formulário de informações trimestrais – ITR referente ao último trimestre de cada exercício não precisa
  ser apresentado."
- **Primária?** sim (regulador). **Nota A.** **Aplica-se:** `ltm.PRAZO_ITR_DIAS`, `ltm.ref_na_data` (o 4T/DFP falha alto).

## F6 — Divulgação do IPCA (corte do "R$ de hoje" na data) — nota C, convenção conservadora
- **Afirmação:** o IBGE divulga o IPCA do mês M no mês M + 1 (setembro/2026 em 09/10/2026; outubro/2026 em 12/11/2026).
- **Status:** NÃO VERIFICADO no primário: o release do IBGE e o calendário deram HTTP 403 (busca do `verificador-fonte`, só
  snippet) — **nota C**.
- **Uso:** só para não olhar o futuro: na data D o motor usa o IPCA até o mês D − 2 (`inflacao.mes_publicado_em`), que já saiu
  mesmo que a divulgação atrase até o fim do mês seguinte. Não embasa palavra; é corte de dado. A conferir no release.
