# B45 — Diagnóstico camada a camada: central ≤ 0 e P/C absurdo nas industriais da B36 (26/11/2026)

*Só diagnóstico (DNA §4, causa (b); `senior` SEGUE COM AJUSTES, 26/11). Sem conserto de método, sem tentativa do
pré-registro, sem emenda. Data-base T = 19/11/2026, motor v2.7 congelado, ficha-padrão e insumos do protocolo da B36
(emenda 8). Nada aqui é ordem de compra ou venda.*

**Como reproduzir:** de `ferramentas/`, `python -m b45.diagnostico` (≈ 5 min). Reroda o executor da B36
(`holdout_b36/executor.py`) sem gravar resultado e escreve `docs/b45/camadas.json` (camadas por ano, LTM, âncoras,
ponte, Kd, e os contrafactuais abaixo). As contagens de alcance de E1/E2 saem de `python -m b45.alcance` (`docs/b45/alcance.json`). Todo
número deste relatório sai desses dois JSONs ou da DFP da CVM citada, exceto o marcado "conta à mão". Os
contrafactuais trocam **uma camada por vez** no motor (mesmo Ke: o D/E a mercado não muda) e não são proposta.

**Tickers abertos:** RAIL3, SMFT3, MOVI3, EMBJ3, BEEF3 — registrados em `docs/holdout/TICKERS-TOCADOS.md` (M1).
Nenhum ticker do hall foi aberto como contraste: o hall só entrou por contagem de alcance de dois achados de dado
(abaixo), sem abrir valuation de nenhum.

## 1. Os 5 números reproduzidos

| Ação | Perfil | Preço | Central | P/C | Âncoras (R$/ação) | Ke nom. | D/E mercado | Palavra |
|---|---|---|---|---|---|---|---|---|
| RAIL3 | serviços | 16,80 | **−3,03** | ∞ | DCF 0,00 · EPV −3,03 · OE −4,16 | 24,9% | 1,05 | NÃO CONCLUSIVO |
| SMFT3 | serviços | 17,69 | **0,00** | ∞ | DCF 0,00 · EPV −14,17 · OE 5,43 | 25,5% | 1,38 | NÃO CONCLUSIVO |
| MOVI3 | serviços | 5,64 | **0,00** | ∞ | DCF 0,00 · EPV −27,01 · OE 8,65 | 61,9% | 10,09 | NÃO CONCLUSIVO |
| EMBJ3 | serviços | 110,15 | 3,04 | **36,20** | DCF 4,19 · EPV 3,04 · OE −5,23 | 21,2% | 0,16 | NÃO CONCLUSIVO |
| BEEF3 | cíclica | 3,73 | 0,56 | **6,69** | EPV 0,10 · DCF 0,56 · reprodução 0,73 | 48,5% | 7,88 | NÃO CONCLUSIVO |

Batem com `docs/holdout/B36-2026-11.md` (central −3,03; 0; 0; P/C 36,20; P/C 6,69).

## 2. Mecânica comum (vale para as 5)

| # | Camada | O que acontece | Onde | Nas 5 |
|---|---|---|---|---|
| M1 | **DCF ≡ EPV** | a trava "crescer só com ROIC > WACC" zera o g e o DCF base vira o EPV | `motor_nao_financeiras.py:758-759` | DCF base = EPV nas 5 (ROIC 2,3%–13,1% < WACC nominal 18,8%–24,9%): das 3 âncoras, 2 são o mesmo número (H3) |
| M2 | **Piso zero do DCF ponderado** | cenário < 0 entra como 0 (AUD-53) e a âncora sai **0 publicado como valor** | `:779` | RAIL3, SMFT3, MOVI3: os 3 cenários < 0 → DCF = 0,00; o central de SMFT3 e MOVI3 é exatamente esse 0 (mediana de {0, EPV < 0, OE > 0}) |
| M3 | **Ponte EV → ação** | patrimônio = EV − dívida do desconto + caixa livre − minoritários | `:719-720`, `:742`, `:768` | ponte ÷ EV(EPV): RAIL3 1,26 · SMFT3 3,87 · MOVI3 2,27 · BEEF3 0,99 · EMBJ3 0,40 (quase só minoritários) |
| M4 | **Âncora ≤ 0 publicada** | o central é a mediana de tudo, inclusive âncora ≤ 0; dispersão vira ∞ | `:866`, `:948-950` | 4 de 5 têm âncora ≤ 0 (B47) |
| M5 | **Kd sintético pela cobertura normalizada** | cobertura = receita de meio × (margem mediana + ajuste) ÷ juros do **LTM** | `:658`; `credito.py:36` | numerador de 10 anos contra denominador de 12 meses; SMFT3 sai com **Kd 31,3% > Ke 25,5%** |

O "preço implica" abaixo é NOPAT normalizado do motor ÷ (valor de mercado + ponte): o retorno real que o mercado aceita
sobre o lucro que o motor enxerga, contra o WACC real que o motor exige.

## 3. Causa por ticker

Colunas = as camadas pedidas na B45. "Fora do domínio" usa a condição do próprio modelo no DNA §1.2.

| Ação | Âncora ≤ 0 / fora do domínio | Ponte de dívida | Margem não normalizada | Minoritários | Outras camadas | Causa dominante |
|---|---|---|---|---|---|---|
| **RAIL3** | DCF 0 (M2) e EPV −3,03: FCFF > 0, o negativo nasce na ponte. OE −4,16: OE < 0 em 6 de 9 anos, mediana dos 5 últimos −1,17 bi — **fora do domínio** (OE > 0) | EV(EPV) 21,96 bi < DL 27,35 bi + minor. 0,22 bi (1,26×). Preço implica NOPAT/EV 4,0% × WACC real 10,8% | m50 26,3%, 5 anos 27,2%, LTM 35,2%: margem **não** é a causa (margem 5a → −2,55) | 0,22 bi, irrelevante | ajuste de manutenção −4,46% da receita (`:519-525`): capex de expansão (6,1 bi em 2025 × D&A 2,2 bi) sem `capex_expansao` na ficha-padrão conta como manutenção; zerá-lo dá EPV ≈ −0,61 (**conta à mão** sobre `camadas.json`, sem refazer Kd) — ainda < 0. Kd 17,1% (BB) × 16,2% pela cobertura LTM (A−) → −2,64 | **Resíduo não explicado pelas camadas medidas** (nem as três juntas, −2,03, tiram o sinal; ponte > EV). Candidatos, não medidos aqui: a trava de crescimento ROIC > WACC (`:758-759`, H3 — causa (b)) ou o nível do Ke (causa (a), fechada); nenhum contrafactual mexeu no Ke |
| **SMFT3** | DCF 0 (M2) → **central 0**. EPV −14,17. OE 5,43 > 0 (no domínio) | EV(EPV) 3,02 bi × ponte 11,69 bi (3,87×; 6,8 bi de arrendamento IFRS 16). Preço implica NOPAT/EV 1,9% × WACC real 14,5% | **Sim.** m50 9,6% × 5 anos 20,7% (`quebra_suspeita` = True, medida e não usada, `:534-538`); receita 0,64 bi (2016) → 7,24 bi (2025), 11×; 2020–21 com margem −31% e −22%. Margem 5a → EPV −8,50 | 0,05 bi, irrelevante | **Kd 31,3% > Ke 25,5%**: cobertura normalizada 0,41 (rating C) contra 1,27 pelo EBIT LTM (B−, Kd 20,4%) → EPV −12,36. As três juntas: EPV −1,02 | **Normalização de 10 anos numa empresa que cresceu 11×** (tendência lida como ciclo, H7), que contamina também o Kd (M5) |
| **MOVI3** | DCF 0 (M2) → **central 0**. EPV −27,01. OE 8,65 > preço — **falso: erro de dado** (§4, E1); com a frota no capex o OE vai a −2,16 e o EPV a −30,95 | EV(EPV) 9,03 bi × ponte 20,48 bi (2,27×) | **Sim.** m50 13,6% × 5 anos 21,1% (`quebra_suspeita` = True); margem 5a → EPV −15,14 | 0 | **Ke 61,9%** (Hamada com D/E 10,09, `:679`) — já sai NÃO CONCLUSIVO pela H2 (`:1037`). Kd 27,9% (CC, cobertura 0,70) × 20,4% pelo LTM (B−) → EPV −18,15. As três juntas: central 0,69 (P/C 8,17) | **Alavancagem extrema** (D/E 10 → Ke e ponte) + margem de 10 anos; o único "valor positivo" era artefato do capex |
| **EMBJ3** | OE −5,23: OE < 0 em 7 de 9 anos — **fora do domínio**. DCF 4,19 > EPV 3,04 só pela assimetria do piso (pessimista −12,06 → 0; otimista 10,67) | caixa líquido (DL −0,52 bi): ponte não é a causa | **Sim, a maior.** m50 2,68% × LTM 9,49%; janela 2016–25 com 2019 (operação descontinuada), 2020 (pandemia) e 2022. O ajuste de "outras" (`:428`) usa a mediana da própria empresa, que é **negativa** (−4,62% da receita): todo ano com menos despesa "outra" vira "não recorrente" e sai — a mediana EBIT/receita bruta é 3,98% e a ajustada 2,68%. Margem 5a → 4,23; 2019 reapresentado (E2) → 5,62 | **Eve:** minoritários 1,94 bi a valor contábil = 47% de EV(EPV) + caixa líquido (4,11 bi); sem eles o EPV seria 5,77. O prejuízo operacional da Eve entra 100% na margem consolidada e não é separável nos dados estruturados da CVM (Eve é listada na NYSE): **não avaliado** | Kd 24,1% (CCC, cobertura 0,95) × 16,0% pelo LTM (A+). Preço implica NOPAT/EV **0,56%**. As três juntas: P/C 20,1 | **Margem de meio de ciclo** (crises de 2019–22 + regra de "outras" com mediana negativa) × ausência de crédito de crescimento; minoritários dobram o efeito. Nenhuma camada sozinha traz o P/C para perto de 5 |
| **BEEF3** | EPV 0,10 ≈ 0 (patrimônio é uma "lasca": EV/(EV − ponte) ≈ 164×, 1% no EV ≈ 164% no EPV). Reprodução 0,73 = PL contábil, PL < 0 em 2018–19 | EV(EPV) 15,95 bi × ponte 15,85 bi (0,99×) | Margem estável (m50 7,7%, 5a 7,6%): **não** é a causa. **Receita de meio × dívida de hoje:** receita de meio 46,1 bi (3 exercícios + LTM, `:507-508`) × LTM 56,2 bi; a receita salta 61% em 2025 e a dívida bruta vai de 21,6 bi (2023) a 30,1 bi (2024) — a ponte já é da empresa maior, o lucro ainda é da menor. Com a receita LTM: **central 7,13 (P/C 0,52)** | 0,61 bi, pequeno | **Ke 48,5%** (D/E 7,88) → NÃO CONCLUSIVO pela H2. Sem linha de juros pagos na DFC (a Minerva só tem "Encargos financeiros" 3,17 bi no 6.01.01.08) → o motor usa a despesa financeira bruta 4,66 bi com câmbio (`juros.py:12`, fallback documentado) → CC | **Descasamento receita de meio × balanço depois de salto de porte** (evento; aquisição a conferir no IPE) sobre uma ponte de 0,99×: o P/C passa de 6,69 a 0,52 trocando só a receita |

## 4. Erros de dado achados (prioridade)

| # | Achado | Prova | Alcance | O que foi feito |
|---|---|---|---|---|
| E1 | **Compra de frota no caixa operacional não entra no capex.** O coletor só lê capex em 6.02 (`coletar_cvm.py:246`, `RE_CAPEX`). A MOVI3 lança a frota em 6.01.03.03 "Compra de Ativo Imobilizado para Locação": 10,27 bi em 2025 (8,9–11,2 bi em 2023–24) contra capex lido de 0,25 bi. O OE soma a depreciação da frota (2,43 bi) e não desconta a compra → âncora OE 8,65 > preço | DFP 2025, DFC_MI consolidada; `camadas.json` → `MOVI3.frota_fco_por_ano`, `variante_frota` | 22 empresas da B3 nas DFP 2016–2025 (DFC MI/MD, consolidada e individual; locadoras e logística de frota); **nenhuma linha do hall/dossiês** → golden não muda (`alcance.json`) | **Corrigido no coletor** (`coletar_cvm.py:58`, `RE_FROTA_FCO`: qualquer compra de imobilizado/veículo/frota em 6.01 — o `adversario` mostrou MOVI3 2016–18, JSL e ARMAC com "Compra de Imobilizado" sem "locação"): com a linha, `capex` = None (não avaliado) e o valor vai para `capex_frota_fco`, com a linha na auditoria; teste `tests/test_b45_capex_frota.py`. A série da B36 **não** foi recoletada (hold-out congelado). A regra de capex **líquido** de frota (compra − custo dos carros vendidos: 3,8–5,3 bi/ano em 2021–25) é método → B63. Limites: LTM de locadora fica sem `capex` sem aviso de lacuna (`combinar_ltm`) e `gerar_pdf_lote5.py:101` quebraria (KeyError) — nenhum ticker do lote 5 tem a linha; linha pequena (Locamérica, "acessórios para veículos") também anula o capex → B63 |
| E2 | **Série anual usa a DFP original, não a reapresentada.** A EMBJ3 2019 vem da DFP 2019 (aviação comercial como operação descontinuada: receita 10,47 bi, EBIT −0,64 bi); a DFP 2020 reapresenta 2019 com receita 21,80 bi e EBIT −0,31 bi. É o AUD-21 (já tratado no LTM) faltando no anual. Nuance: o 2018 "reapresentado" pela DFP 2019 é o distorcido (7,89 bi) — "pegar sempre a versão mais nova" não basta | DFP 2019 e 2020, DRE_con, ÚLTIMO × PENÚLTIMO | **18 tickers do hall/dossiês** com receita ou EBIT reapresentados > 0,5% (PETR4 2018 −11%, UGPA3 2020 −15% no EBIT, VLID3 2021 −27% na receita, LEVE3, CPLE3, RANI3…) → **muda golden** | **Não corrigido: é do Frank** (muda palavra potencialmente) → `PENDENTE-FRANK.md` #16 e B62. Efeito na EMBJ3 (2019 reapresentado, "outras" do ano na mediana): central 3,04 → 5,62, P/C 19,6 — não explica o absurdo |

Não são erro de coleta, mas são **vazio silencioso** (princípio 2 do DNA), registrados no BACKLOG:
- **EMBJ3 — P/L histórico de 1 ano.** O COTAHIST só tem EMBJ3 em 2025–26 (antes, EMBR3); o código não falha (por isso a
  previsão "erro" da emenda 8 não se confirmou) e calcula o P/L histórico só com 2025 (32,8; `dossie/base.py:177-180`).
  Não mexe no central (entra no Bogle/trava). → B64 (causa c).
- **Ajuste de manutenção = 0 quando nenhum ano tem capex** (`motor_nao_financeiras.py:525`): com a correção E1, as
  locadoras passam a cair aqui — o OE sai "não avaliado" (certo), mas o EPV fica sem a penalidade, no padrão. → B65.

## 5. Previsto (emenda 8) × achado

| Ação | Previsão da emenda 8 | Observado | Causa achada | Previsão acertou a causa? |
|---|---|---|---|---|
| RAIL3 | roda ("evento pequeno diante da base") | roda; central −3,03 | Ke × alavancagem (ponte 1,26× do EV) | acertou "roda"; o absurdo não estava previsto e não é evento |
| SMFT3 | roda ("sem quebra de base visível no IPE") | roda; central 0 | janela de 10 anos numa empresa que cresceu 11× + Kd sintético > Ke + piso do DCF | acertou "roda"; a quebra existe, só não no IPE — o motor a mede (`quebra_suspeita`) e não usa |
| MOVI3 | NÃO CONCLUSIVO (Ke > 30%), "dívida alta e emissão de ações" | NÃO CONCLUSIVO (Ke 61,9%); central 0 | D/E 10,09 → Ke e ponte; OE inflado por dado (E1) | **acertou a causa** (alavancagem); não previu o erro de capex |
| EMBJ3 | **erro** (série de preço curta pelo código novo) | roda; P/C 36,2 | margem de meio + regra de "outras" + Eve + sem crescimento | **errou**: o código encolhe a janela do P/L em silêncio em vez de falhar (B64); o absurdo vem da margem |
| BEEF3 | NÃO CONCLUSIVO (Ke > 30%), "PL pequeno diante da dívida" | NÃO CONCLUSIVO (Ke 48,5%); P/C 6,69 | ponte 0,99× (lasca de patrimônio) + receita de meio anterior ao salto de porte | **acertou a causa** (PL pequeno × dívida); o salto de receita de 2025 não estava na lista de eventos |

## 6. O que o diagnóstico separa (para a sessão do conserto — não é proposta)

1. **Domínio (causa b), genérico, nas 5:** âncora ≤ 0 hoje entra como valor (M2, M4). Três situações diferentes saem com
   o mesmo número: (i) FCFF > 0 mas patrimônio ≤ 0 na ponte (RAIL3, SMFT3, MOVI3 — o modelo funciona, o acionista não
   tem valor a esse Ke); (ii) OE ≤ 0 (RAIL3, EMBJ3 — fora da condição do modelo); (iii) dado que impede a âncora (MOVI3
   capex). A B47 depende de separar as três.
2. **Âncoras não independentes (H3):** com o g zerado, DCF base = EPV nas 5; a mediana de 3 é, de fato, de 2 — e o piso
   do DCF ponderado cria uma terceira âncora artificial (0 ou a assimetria da EMBJ3).
3. **Normalização (H7):** `quebra_suspeita` acende em SMFT3 e MOVI3 e não muda nada; a regra de "outras" com mediana
   negativa penaliza ano normal (EMBJ3); a receita de meio não acompanha salto de porte (BEEF3).
4. **Kd sintético (B35/B66):** numerador normalizado × juros de 12 meses; Kd acima do Ke (SMFT3); juros sem linha na
   DFC caem na despesa bruta com câmbio (BEEF3).
5. **Fora da (b):** Ke por alavancagem (MOVI3, BEEF3 — causa (a), fechada "como está"). RAIL3 fica negativa mesmo com
   todas as camadas medidas trocadas; o resíduo pode ser a trava de crescimento (H3, que é da (b)) ou o nível do Ke (a) —
   não foi separado aqui.

Sensibilidade que o conserto precisa respeitar: com ponte ≈ EV (BEEF3), qualquer regra de domínio que só olhe o sinal
do central troca palavra com 1% de variação no EV — o domínio da ponte precisa de margem, não de sinal.

## 7. Limites (o que não revisei)
- Eve: perda operacional e participação da Embraer não lidas (fora dos dados estruturados da CVM); só o NCI contábil.
- Variante E2 da EMBJ3: as contas 3.04.04/05 reapresentadas de 2019 não foram lidas (ficaram na mediana).
- BEEF3: a natureza do salto de receita/dívida (aquisição) não foi conferida no IPE.
- Nenhum ticker do hall foi rodado como contraste de valuation; o hall só entrou na contagem de alcance de E1 e E2.
