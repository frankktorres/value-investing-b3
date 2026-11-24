# Protocolo fixo dos insumos — hold-out B36 (emenda 8 do `docs/PRE-REGISTRO-v3.md`)

O mesmo texto vale para as 20 ações. Só `{TICKER}`, `{CNPJ}`, `{CD_CVM}`, `{TIPO}` e `{NOME_PREGAO}` mudam. Quem roda: 1 subagente
Sonnet (`general-purpose`) por ação, com **teto de 25 chamadas de ferramenta**. Não se reescreve o protocolo durante a B36.

---

Você levanta os insumos não mecânicos de **{TICKER}** (CNPJ {CNPJ}, código CVM {CD_CVM}, tipo {TIPO}, pregão {NOME_PREGAO})
para o hold-out B36 da Mesa de Value Investing. Repositório: `c:\Users\frank\Documents\VALUE INVESTING`.

**Regras fixas**
1. Teto: **25 chamadas de ferramenta** no total. Ao chegar a 23, pare e grave o que tiver.
2. Só vale fonte **A** (documento oficial: CVM — FRE, IPE, DFP, ITR, estatuto; B3) ou **B** (RI da própria empresa). Sem fonte
   A/B, **não grave o campo** (fica vazio; o método usa o padrão). Não invente número, não estime sem documento.
3. Roteiro, nesta ordem: (a) FRE 2026 — `ferramentas/dados/cvm/fre_2026.zip` (CSVs estruturados por CNPJ) e, se precisar do
   texto, o FRE na RAD; (b) IPE — `ferramentas/dados/cvm/ipe_cia_aberta_2017.zip` … `_2026.zip` (títulos e links dos fatos
   relevantes, comunicados, assembleias, estatuto); (c) estatuto social vigente (IPE); (d) DFP 2025 e suas notas (RAD/CVM).
   Documento baixado vai para `ferramentas/dados/cvm/docs/{NOME_PREGAO}/` (pasta ignorada pelo git).
4. **Proibido** olhar preço, cotação, valuation, P/L, recomendação, notícia de imprensa ou relatório de corretora.
5. Não edite nada fora de `ferramentas/holdout_b36/insumos/{TICKER}.json`. Não rode o motor nem o executor.

**O que levantar** (formato de cada campo: `{"valor": ..., "fonte": "documento, data, item/nota, trecho curto", "nota_fonte": "A"|"B"}`;
modelo completo em `ferramentas/dossie/insumos/ALLD3.json`; regras de nota em `ferramentas/dossie/notas.py`)

Para tipo `industrial`:
- `ma_ruim` (bool): aquisição > 20% do ativo destruiu valor (baixa contábil, venda com perda) nos 10 anos.
- `interferencias` (int): nº de interferências do controlador **consumadas** contra o minoritário (fato relevante/decisão).
- `partes_rel_sobre_receita` (fração): transações com partes relacionadas ÷ receita líquida do último exercício.
- `tag_along` (fração, 0–1): o do estatuto para a classe {TICKER}.
- `discricionario` (bool): o controlador exerce poder discricionário documentado (acordo, golden share, voto especial).
- `fisher.respostas`: lista de **exatamente 15** respostas `"sim"`/`"nao"`/`"sem"` às 15 perguntas de Fisher (ordem e texto
  das perguntas: `fisher.itens` do `ALLD3.json`; a nota sai de `notas.fisher`); `"sem"` quando não houver documento A/B. Ponha em
  `fisher.itens` uma linha por pergunta com a fonte.
- `desconto_controlador`: `{"tipo": "zero"|"fixo"|"cenarios", "razao": "...", ...}` no formato do `ALLD3.json`. Sem evidência A/B
  de risco de controlador, grave `{"tipo": "zero", "razao": "SEM_RAZAO"}`.

Para tipo `banco` ou `utility` (motor de financeiras, como o hall):
- `payout_politica`: só se houver política de dividendos formal (estatuto/política aprovada) com o payout mínimo/alvo.
- `qualitativo`: `{"valor": {"moat": 0–5, "gestao": 0–5, "controlador": 0–5, "ciclo": 0–5, "fisher": 0–5}, ...}` — cada nota
  só com documento A/B que a sustente (critério do `notas.py`); nota sem documento fica fora do dicionário.
- `prudencial` (só banco): `{"valor": {"cet1": %, "inad90": %, "cobertura": %}}` do ITR/relatório de Pilar 3 do 3T26.
- `discricionario`: como no industrial. `desconto_controlador`: só `{"tipo": "zero", "razao": "SEM_RAZAO"}` ou
  `{"tipo": "fixo", "pct": fração, "razao": "interferência consumada, documento e data"}` (formato do `lote1_bancos.py`).

**Grave** `ferramentas/holdout_b36/insumos/{TICKER}.json` com os campos achados e mais
`"_meta": {"protocolo": "B36 v1", "chamadas": <nº usado>, "fim": "<AAAA-MM-DDTHH:MM>", "nao_achado": [<campos sem fonte>]}`.
Responda em até 10 linhas: campos achados, campos vazios e nº de chamadas.
