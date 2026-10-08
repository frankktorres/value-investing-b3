# PROMPT DE RECÁLCULO EM LOTE (v1.1, 07/10/2026)
*Use para refazer um lote inteiro de fichas pela doutrina **v2.3** (07/10/2026). Um lote por conversa. Anexe o PDF vigente do lote e substitua `<LOTE>`.*

---

Você é o analista independente de value investing desta mesa. **Recalcule o `<LOTE>`** pela `01-doutrina-value-investing.md` **v2.0**, usando o PDF anexado só como fonte de **fatos** (balanços, proventos, eventos). **Nenhum valor central, nota ou métrica do PDF é reaproveitado sem recalcular.**

**PASSO 1 — Premissas comuns (uma vez, no topo)**
- rf = Tesouro IPCA+ **sem cupom** de vencimento mais longo, taxa de **fechamento** do último dia útil, com URL e vencimento.
- Inflação implícita da curva (prefixado × IPCA+ de prazo próximo), com as duas taxas e a URL; Focus como sensibilidade.
- Ke real, Ke nominal; RF real líquida de IR pela fórmula de 10 anos (doutrina §4); parâmetros fiscais da §4.1.
- Cotações: fechamento do último pregão, data e fonte.

**PASSO 2 — Para cada ticker, a ficha completa de 2 páginas**
1. Círculo de competência (3 linhas).
2. Perfil e métodos ÂNCORA / INFORMATIVO (doutrina §11.2).
3. **Quadro clássico inteiro (doutrina §11.1)**, cada linha com valor, fórmula, insumos com fonte e marca. Inclui lucro projetado 3 anos (consenso e próprio), Graham original e Graham-BR, Bazin original e teto de renda (Bazin calibrado, informativo), Lynch/PEG/PEGY, EY e ROC de Greenblatt, Owner Earnings, EPV real × reprodução, DDM/Gordon ou P/VP justificado, SOTP (holding), DCF 3 cenários com pesos, DCF reverso, TIR real (regulados), Bogle com variação de múltiplo, teste do R$ 1, Piotroski, Altman Z'', Beneish, Sloan.
4. **Tabela de reconstrução do central:** âncora | valor | peso → mediana; dispersão e efeito no veredito.
5. Linha de desconto de controlador (X% em cenários ou Ke — ou zero, porque…).
6. Proventos: yield sustentável, cobertura por caixa, defasagem a valor presente.
7. Veredito pela régua contínua e pela ordem de precedência (doutrina §9); filtros 1–4 (3 de 4 para seguir no hall); **trava de coerência** (JUSTA ⇒ Bogle a ±2 p.p. do Ke nominal); compra 0,70×, justo, saída 1,30×, gatilho; entrada parcial só pela exceção da §9.
8. RF líquida: vence / empate / não pelo ponto médio, com carimbo se o extremo inferior perder para o Tesouro.
9. Notas 30/20/25/25 com a escala única de preço.
10. **De → para** contra a rev. 03/10: valor central, palavra, e a razão — (a) preço, (b) fundamento, (c) **método v1 estava errado** (dizer qual erro do anexo abaixo).

**PASSO 3 — Fechamento do lote**
- Quadro-resumo: ticker | palavra | preço | central | P/C | compra | saída | vence RF (líquida) | nota | pendências resolvidas.
- Para não financeiras: EY e ROC de Greenblatt de cada uma (para o ranking do hall, `03` §3).
- Rode o `04-checklist-anti-erro.md` v2.1 inteiro e liste os itens que falharam e como foram corrigidos.
- Lista "Não encontrado".

**PASSO 4 — Lições da Etapa 5 (dossiês BLAU3, CMIN3, HYPE3, 07/10/2026) que valem para qualquer lote**
- **Desdobramento:** o fator da B3 é percentual (`DESDOBRAMENTO` fator 100 = ×2; multiplicador = 1 + fator/100, conferido no DFP do BBAS3 2024). A B3 repete o mesmo evento por ISIN: deduplicar por (tipo, data-com). `GRUPAMENTO` traz o fator como razão (ex.: 0,1) — não aplicar a regra do desdobramento; conferir à mão.
- **Subvenção de ICMS (crédito outorgado):** a CVM a deixa em "deduções de vendas", isto é, **dentro** da receita e do EBIT. O tamanho só aparece na conciliação da alíquota de IR (efeito ÷ 34%): na HYPE3 ≈ R$ 1,0 bi = 57% do EBIT de 2025. Declarar quanto do EBIT depende dela e normalizar se o benefício tem prazo.
- **Retorno incremental de M&A:** usar o EBIT **ajustado** (sem o excesso de "outras"), não o bruto.
- **Ticker do hall em dossiê:** o dossiê troca a série de proventos só dentro do cálculo do dossiê (`base.isolado`); o golden das 41 não muda.
- **Nota qualitativa:** base mecânica por evidência + ajuste de no máximo ±1 com fonte A/B (regra 11 do `02` v4). Desde a v2.3 o motor faz a média da regra 11 (peso 2 do controlador discricionário, com a razão escrita). No lote refeito, o hall segue com as notas arbitradas ("arbitrada, pré-v4") até o dossiê de cada ticker; peso 2 provisório só onde a interferência consumada está no desconto do lote.

**PASSO 5 — Doutrina v2.3 (07/10/2026), conferir em cada ticker**
- **Alíquota (§2):** mediana de 5 anos sem piso. Abaixo de 15%, declarar a origem: permanente (JCP, regime sem prazo; `aliquota_permanente_fonte`) ou crédito com prazo (`aliquota_fase` com o ano final e a fonte A/B). Sem origem declarada, o motor usa 34% (TIMS3 e PRIO3 estão assim até o dossiê). O Owner Earnings é refeito à alíquota perpétua.
- **Desconto de controlador (§5):** só sobre âncora positiva; âncora ≤ 0 continua NÃO CONCLUSIVO.
- **Outros passivos (§11.1):** com juros ou financeiro (passivo de contrato) em `outros_passivos_financeiros`; o **provento já ex** (passivo de proventos do balanço + aprovado depois do balanço e ex até a data do preço) o motor soma sozinho (`proventos_ex.py`, v2.3.1) — não digitar de novo (entra na dívida líquida, no DL/EBITDA e no ROIC); operacional em `outros_passivos` (só ponte). Fonte obrigatória.
- **Capex de expansão (§11.1):** só projeto nomeado, com valor e prazo em fonte A/B e sem receita (`capex_expansao`); o resto é manutenção.
- **Margem ao preço de meio (§11.1):** só cíclica com dossiê e janela ≥ 7 exercícios (`fator_preco`).

---

## Anexo — erros específicos da auditoria de 04/10/2026 a corrigir por lote

**Lote 1 — Bancos e Seguridade** — ✅ **RECALCULADO em 04/10/2026 no Claude Code** (`BANCOS E SEGURIDADE/Banco_Seguridade_rev_04-10-2026.pdf`, doutrina v2.0); os itens abaixo ficam como histórico.
- ITUB4 e PSSA3 com central a "Ke mercado 14%"; BBSE3 e CXSE3 na coluna real. Recalcular ao Ke da casa (a estimativa da auditoria leva as quatro a CARA).
- BBAS3: P/VP justificado (13 − 4)/(16,56 − 4) = 0,716 × VPA 31,76 = R$ 22,75, não 23,50; DY fwd de 4,4% exige ROE de 11%, enquanto a ficha fala em ROE 2026e de ~9%.
- BRBI11: DPA 1,42 exige ROE de 22%; com ROAE de 17,5% o DPA é ~1,11 (yield 7,3%); g de 5–7% com payout de 85% é incompatível (sustentável ~2,6%).
- CXSE3 g 9,5%; BBDC4 g 8–10%; ITUB4 e PSSA3 g 8% — limitar a ROE × retenção.
- BBSE3: crescimento somado a fluxo finito até 2033; "Ke pela metade" sem base.
- SANB11: ARMADILHA → JUSTA só por preço, com ROE < Ke mantido.
- Linhas de controlador ausentes: CXSE3, SANB11; BBAS3 "já no ROE normalizado" sem número.
- Retorno real esperado abaixo do Ke em todas as JUSTA (trava).

**Lote 2 — Energia e Saneamento** — ✅ **RECALCULADO em 05/10/2026 no Claude Code** (`ENERGIA ELÉTRICA E SANEAMENTO/Energia_Saneamento_rev_05-10-2026.pdf`, doutrina v2.2); os itens abaixo ficam como histórico.
- Centrais por ajustes avulsos em R$ (CPFE3 "47+8−2+1"; "−R$ 1 de opcionalidade"); DCF, EPV, Graham e Bazin sumiram em relação a 07/09.
- TIR real calculada só quando reprova (TAEE11, ISAE4); calcular também SBSP3, CSMG3, CPFE3, CPLE3, CMIG4, SAPR11.
- Yield declarado (pago com dívida) usado como sustentável em TAEE11, CPFE3 e CPLE3.
- CMIG4: risco do dono nos cenários 40/60 e de novo no retorno "ponderado".
- SAPR11: dizer onde entra o haircut de 15%.
- Real a partir do nominal por subtração simples (CMIG4) × composto (CPFE3).
- SBSP3: resolver a dúvida de desdobramento/bonificação (Yahoo 0,528 × 0,106) antes de qualquer yield.
- ISAE4: DY 12m inclui RBSE; CMIG4: DY 12m parcial.
- Preços "anteriores" de julho/agosto chamados de "ficha de 07/09".

**Lote 3 — Infra e Agro** — ✅ **RECALCULADO em 05/10/2026 no Claude Code** (`AGRO E B3/Infra_Agro_rev_05-10-2026.pdf`, doutrina v2.2); os itens abaixo ficam como histórico.
- Centrais redondos "mantidos" (SUZB3 55, KLBN11 19, RANI3 10, KEPL3 8, SLCE3 18); KEPL3 acima do DCF e do EPV; SLCE3 = NAV de terceiro × (1 − 33%).
- "DCF a Ke real" ~35% acima do nominal (mistura de g real com Ke nominal); central acima do DCF nominal em 7/7.
- KLBN11: payout 126% e FCF negativo — aplicar o mesmo tratamento do UNIP6 (doutrina §7); meio de ciclo trocado de 9 para 8 bi sem declarar.
- KEPL3, SLCE3, RANI3: meio de ciclo sem número; SUZB3 soma a dívida da Arbex sem o EBITDA dela.
- RANI3 "Empate via FCF" com retorno de provento abaixo do Tesouro.
- B3SA3 sobe o central por 1 mês de volume; Bogle soma recompra.
- Graham, Bazin, Piotroski, Altman, PEG, Fórmula Mágica e teste do R$ 1 sumiram em relação a 06/09.

**Lote 4 — Saúde, Telecom e Blue Chips** — ✅ **RECALCULADO em 05/10/2026 no Claude Code** (`SAÚDE, TELECOM E BLUECHIPS/Saude_Telecom_Bluechips_rev_05-10-2026.pdf`, doutrina v2.2); os itens abaixo ficam como histórico.
- Centrais = anterior × fator de Ke.
- WEGE3: g de 12% (nominal) descontado a Ke real; Bogle a P/L 34 sem compressão de múltiplo.
- FLRY3: Graham com LPA antigo (com LPA 1,29 e VPA 9,92 dá ~R$ 17,0); Piotroski 9/9 de HYPE3 e FLRY3 "da ficha".
- TIMS3 e B3SA3: recompra somada ao yield e ao g.
- Linha de controlador ausente: HYPE3, VIVT3, ABEV3, FLRY3.
- ITSA4: "Sim (limite)" com caso recorrente de 9,6% (empate); SOTP herda o central de ITUB4 a Ke 14%.
- Altman (WEGE3), Piotroski (VIVT3, ITSA4) sumiram.

**Lote 5 — Petróleo e Gás** — ✅ **RECALCULADO em 05/10/2026 no Claude Code** (`PETROLEO E GÁS/Petroleo_Gas_rev_05-10-2026.pdf`, doutrina v2.2); os itens abaixo ficam como histórico.
- PRIO3, RECV3, UGPA3 e VBBR3 com central na coluna real; RECV3 central acima dos dois modelos, sem pesos.
- PETR4: cenário "normalizado" soma "+1 tri de topo"; faixa "< R$ 34 → JUSTA" está errada (34/39 = 0,87 é RADAR); pesos 25/60/15 dão 40,2, não ≈41.
- Sem câmbio de meio de ciclo (só Brent 70).
- PRIO3 "Não" com ponto médio de empate.
- Defasagem do JCP do VBBR3 a IPCA em vez de Ke.
- Saídas de PETR4, UGPA3 e VBBR3 não acompanharam o central.

**Lote 6 — Química e Metalurgia** — ✅ **RECALCULADO em 05/10/2026 no Claude Code** (`QUÍMICA E METALÚRGIA/Quimica_Metalurgia_rev_05-10-2026.pdf`, doutrina v2.2); os itens abaixo ficam como histórico.
- Centrais = anterior × 1,024–1,027 e acima do DCF ao Ke nominal (+5% a +9%) sem regra de ponderação.
- LEVE3: Graham com LPA de pico (5,14; normalizado 4,3 → R$ 26,2).
- EGIE3: TIR "não recalculada"; Bazin "não habilitado" × LEVE3 "com ressalva" — mesma regra para os dois.
- UNIP6: caixa 653 mi × 1,4 bi não reconciliado; "RADAR ≤ R$ 37" = preço igual ao central.
- Altman, Piotroski, Beneish, Sloan, PEG e Fórmula Mágica sumiram em relação a 07/09; EPV sumiu em EGIE3, UNIP6 e GGBR4.
