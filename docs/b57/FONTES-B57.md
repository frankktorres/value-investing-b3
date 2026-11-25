# Fichas de fonte — B57 (emenda 13 do `docs/PRE-REGISTRO-v3.md`) — 25/11/2026

Protocolo: `~/.claude/PESQUISA.md` §4. Textos baixados em 25/11/2026 numa pasta temporária e lidos localmente (HTML → texto;
PDF → pypdf). O planalto.gov.br recusou a conexão (curl e PowerShell); a lei foi lida na cópia oficial da Câmara dos Deputados.

## F1 — Onde a lei guarda o lucro retido (Lei 6.404/1976, norma atualizada)
- **Fonte:** Câmara dos Deputados, Legislação Informatizada, Lei nº 6.404/1976, "norma atualizada".
  https://www2.camara.leg.br/legin/fed/lei/1970-1979/lei-6404-15-dezembro-1976-368447-normaatualizada-pl.html
  [LIDO 25/11/2026]. **Nota A** (texto legal oficial).
- **Art. 178 §2º, III** (inciso acrescido pela MP 449/2008, convertida na Lei 11.941/2009): "patrimônio líquido, dividido em
  capital social, reservas de capital, ajustes de avaliação patrimonial, reservas de lucros, ações em tesouraria e prejuízos
  acumulados."
- **Art. 182 §4º:** "Serão classificados como reservas de lucros as contas constituídas pela apropriação de lucros da companhia."
- **Art. 189:** "Do resultado do exercício serão deduzidos, antes de qualquer participação, os prejuízos acumulados e a provisão
  para o Imposto sobre a Renda." **Parágrafo único:** "o prejuízo do exercício será obrigatoriamente absorvido pelos lucros
  acumulados, pelas reservas de lucros e pela reserva legal, nessa ordem."
- **Art. 202 §2º** (redação da Lei 10.303/2001): "Quando o estatuto for omisso e a assembléia-geral deliberar alterá-lo para
  introduzir norma sobre a matéria, o dividendo obrigatório não poderá ser inferior a 25% (vinte e cinco por cento) do lucro
  líquido ajustado nos termos do inciso I deste artigo."
- **Art. 202 §6º** (acrescido pela Lei 10.303/2001): "Os lucros não destinados nos termos dos arts. 193 a 197 deverão ser
  distribuídos como dividendos."
- **Leitura:** o lucro que a companhia guardou ao longo da vida está nas reservas de lucros; o que ainda não foi apropriado, e o
  prejuízo não absorvido, estão em lucros/prejuízos acumulados. No fim do exercício o saldo positivo tem de ser destinado
  (§6º), então no DFP a conta fica em zero ou negativa; no ITR ela traz o resultado do ano ainda sem destino.
- **Conferência anterior** do `verificador-fonte` (WebFetch, resumo; nota B) apontou o mesmo conteúdo e citou "alínea d" — o
  texto vigente é o **inciso III**.

## F2 — Plano de contas padronizado da CVM (dados abertos, DFP/ITR)
- **Fonte:** CVM, dados abertos, `dfp_cia_aberta_2025.zip` e `itr_cia_aberta_2026.zip` (cache em `ferramentas/dados/cvm/`).
  **Nota A.** Medido em 25/11/2026 (código lido em `CD_CONTA`, descrição em `DS_CONTA`):
  - DFP 2025, BPP consolidado, último exercício: 2.03.04 = "Reservas de Lucros" e 2.03.05 = "Lucros/Prejuízos Acumulados" em
    429 de 429 companhias com esse plano (os 4 bancos usam outro plano: 2.03.04/2.03.05 são passivos financeiros).
  - ITR 30/09/2026: das que têm 2.03.04 = "Reservas de Lucros", 396 de 396 (consolidado) e 599 de 599 (individual) têm
    2.03.05 = "Lucros/Prejuízos Acumulados", nenhuma com valor vazio. DFP 2025 individual: 632 de 632.

## F3 — Definição do X2 de Altman: lucros retidos incluem os prejuízos
- **Fonte:** Altman, E. I. *Revisiting Credit Scoring Models in a Basel 2 Environment*, NYU Stern, working paper 02-41 (2002).
  https://archive.nyu.edu/bitstream/2451/26485/2/02-41.pdf [LIDO 25/11/2026, pypdf]. **Nota B** (texto do autor, não revisado
  por pares).
- **Trecho (seção do Z-Score, X2):** "Retained earnings (RE) is the term used to describe the account that reports the total
  amount of reinvested earnings and/or losses of a firm over its entire life. The account is also referred to as earned
  surplus." — "This measure of cumulative profitability over time is what we referred to earlier as a 'new' ratio."
- **Trecho (Z''):** "Z" = 6.56 (X1) + 3.26 (X2) + 6.72 (X3) + 1.05 (X4)" — "In the emerging market (EM) model, we added a
  constant term of +3.25 so as to standardize the scores with a score of zero (0) equated to a D (default) rated bond."
- **Com a F4 da B46** (`docs/b46/FONTES-B46.md`, slides 25–26 do *50 Years of Altman Z-Score*, nota B): X2 = lucros retidos ÷
  ativo total. Confere com o motor; o que diverge é o insumo (só 2.03.04).

## Ainda a conferir (sem efeito na emenda 13)
- Se a 2.03.04 da CVM já desconta ações em tesouraria em alguma subconta (ex.: 2.03.04.09) — recompra grande baixaria o X2.
- Prejuízo absorvido por reserva de capital ou redução de capital (Lei 6.404, arts. 173 e 200) some da 2.03.05: viés do X2.
- Se o "retained earnings" de um balanço trimestral nos EUA inclui o lucro do ano corrente (fonte A a abrir; US GAAP).
