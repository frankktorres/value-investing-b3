"""Texto qualitativo das fichas do Lote 4. Números entre chaves vêm do motor no momento da geração do PDF.
Fontes: [CVM] DFP/ITR; [FRE] formulário de referência 2026 (posição acionária); [SI] StatusInvest; PDF 06/09 e 03/10 (eventos, proventos declarados,
defasagens, gatilhos, agenda — extraídos em dados/fatos_lote4.json; fontes primárias listadas lá)."""

AGENDA = ("3T26 entre 21/10 (WEGE3) e 10/11 (VIVT3) — datas de agregador, não confirmadas no RI · 25/10 2º turno · 03–04/11 Copom · "
          "out–nov: MP do Imposto Seletivo (pós-eleição) · LC 224/2025: JCP a 17,5% e o risco de fim do JCP (atinge ABEV3, HYPE3, ITSA4, TIMS3, VIVT3)")

ANTES = {"TIMS3": ("RADAR", 22.50), "VIVT3": ("RADAR", 33.80), "ITSA4": ("JUSTA", 15.45), "FLRY3": ("JUSTA", 23.70), "HYPE3": ("JUSTA", 24.70),
         "ABEV3": ("CARA", 13.75), "WEGE3": ("CARA", 33.20)}

FILTROS_FALHA_1 = ("1 falha (ROIC {roic} < WACC {wacc}, no ciclo); 2 passa (DL/EBITDA com arrendamento {dl_ebitda}×); 3 passa (sem interferência "
                   "consumada); 4 passa ({f4}) → 3 de 4: segue no hall.")

T = {
"TIMS3": dict(
    circulo="Operadora móvel do oligopólio de três (dividiu a Oi Móvel em 2022), com fibra e B2B. Ganha com ARPU que acompanha a inflação sobre a "
            "base pós-paga e com capex caindo para ~13% da receita [PDF 03/10]; pararia com guerra de preço entre as três ou com espectro novo "
            "(edital de 6 GHz) exigindo capex fora do ciclo.",
    controlador="Desconto de controlador: zero — TIM Brasil Serviços e Participações (Telecom Italia) com 67,8% [FRE]; a Poste Italiane (estatal "
                "italiana) virou controladora indireta em 18/09/2026 [PDF 03/10]. Nenhuma interferência consumada; o risco prospectivo (V4/V5: "
                "contratos com o grupo, payout) fica no gatilho. Tag along aos minoritários pela troca indireta: sem posição da CVM — é opção, não desconto.",
    receita_base="média 2023–25 + 12m",
    lynch="stalwart lento — PEG informativo",
    sens_extra=[("c_greenwald", "Capex por Greenwald (parte do capex como expansão)")],
    filtros=FILTROS_FALHA_1.replace("{f4}", "proventos ≤ Owner Earnings; JCP pago em ~4 meses"),
    sustentam=["Margem EBIT dos 12m {m_ltm} contra mediana 2019–25 de {m50}: com a margem de hoje permanente, central R$ {c_ltm} (P/C {pc_ltm})",
               "Owner Earnings mediano R$ {oe_bi} bi/ano, já com o aluguel pago, cobre os proventos [CVM]",
               "Piotroski {piot}/9; Altman Z'' {altman} ({altman_zona})"],
    ameacam=["ROIC {roic} contra WACC {wacc}: crescer não cria valor (DCF reverso n.a.)",
             "Arrendamento de R$ {arr} bi na dívida (torres e lojas) — aluguel pago de R$ {arr_pago} bi em 12m [CVM]",
             "O preço embute Ke de {ke_impl} ({ke_impl_real} real) — praticamente o Tesouro IPCA+ ({rf_real}) com risco de ação"],
    gatilho="corte do guidance de remuneração de 2026 (R$ 5,3–5,5 bi), capex > 16% da receita, DL/EBITDA com arrendamento > 1,3× ou ARPU móvel "
            "caindo a/a [PDF 03/10].",
    renda="Não. Yield sustentável a valor presente, líquido: {dy_liq}; retorno real líquido esperado {bogle_real} não vence a RF.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}.",
    de_para="A rev. 03/10 (R$ 22,50) era o central de 07/09 × fator de Ke, com DCF de FCFE a Ke 12–16,6% e Bazin 'fwd total' somando recompra ao "
            "yield; o arrendamento entrava no EV/EBITDA mas não no valor. Agora: margem EBIT mediana 2019–25 sem não recorrentes, arrendamento como "
            "dívida, capex de rede como manutenção e as três âncoras de serviços ao Ke de {ke_nom}. Razão (c): fator de Ke e recompra somada ao yield.",
    autocritica=["A margem subiu depois da Oi (2023–25: 19,8% → 23,8% [CVM]); se for estrutural, o central iria a R$ {c_ltm} — ainda CARA.",
                 "Capex de rede como manutenção é conservador; por Greenwald o central seria R$ {c_greenwald}.",
                 "Os 12m misturam o consolidado de 2026 (a TIM voltou a consolidar) com o individual de 2025 — diferença de receita < 1%.",
                 "Alíquota no piso de 15% (benefício regional + JCP): se o JCP acabar, o lucro cai e o central também.",
                 "Kd = rf + 1 p.p.; o peso da dívida financeira é pequeno — o grosso da dívida é arrendamento."],
    agenda="03/11 3T26 (não confirmado) · dez/26 declaração do 4T (cumprimento do guidance; precisa concentrar ~R$ 1,3/ação [PDF 03/10]) · "
           "22/01/2027 pagamento do JCP de set/26",
    nao_encontrado="Posição da CVM sobre tag along após a troca de controle na Itália; confirmação do guidance no RI; LPA de consenso; FCFE oficial."),

"VIVT3": dict(
    circulo="Líder do móvel pós-pago e maior rede de fibra do país, com B2B; a concessão do fixo virou autorização. Ganha com ARPU indexado e "
            "escala; pararia com corte de payout sem recompra (a política de 2027 não foi encontrada) ou com perda judicial do 700 MHz.",
    controlador="Desconto de controlador: zero — Telefónica S.A. e controladas (~76% [PDF 03/10]; 39,3% diretos pelo FRE 2026), sem interferência "
                "consumada. O payout de 100% do lucro até 2026 é política da controlada, não extração.",
    receita_base="média 2023–25 + 12m",
    lynch="stalwart lento — PEG informativo",
    sens_extra=[("c_greenwald", "Capex por Greenwald (parte do capex como expansão)")],
    nota_proventos=" — sem a redução de capital (R$ 1,25 em 2026)",
    filtros=FILTROS_FALHA_1.replace("{f4}", "proventos ≤ Owner Earnings; JCP pago em 7–14 meses, no valor presente"),
    sustentam=["Sem arrendamento a Vivo tem caixa líquido (R$ 3,79 bi [PDF 03/10]); com ele, DL/EBITDA {dl_ebitda}×",
               "Margem EBIT estável: p25 {m25} · mediana {m50} · p75 {m75} (2019–25) — o central é pouco sensível à margem",
               "Owner Earnings mediano R$ {oe_bi} bi/ano cobre o provento recorrente"],
    ameacam=["ROIC {roic} contra WACC {wacc}: a base de ativos (ágios de Telesp/GVT) rende abaixo do custo",
             "Yield recorrente a valor presente {dy}: a redução de capital de jul/26 não é lucro (§6.4)",
             "Recompra aprovada e zero ações recompradas em jan–jul/26; política de payout de 2027 não encontrada [PDF 03/10]"],
    gatilho="receita móvel < 4% por 2 trimestres, capex > 18% da receita, corte de payout sem recompra equivalente ou DL/EBITDA com arrendamento "
            "> 1,5× [PDF 03/10].",
    renda="Não. Yield sustentável a valor presente, líquido: {dy_liq}; JCP pago até 14 meses depois.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}.",
    de_para="A rev. 03/10 (R$ 33,80) era o central de 07/09 + R$ 0,80 de Ke, com DCF de FCFE a g real 1% e Bazin de até R$ 42,50 somando a redução "
            "de capital. Agora: margem 2019–25, arrendamento como dívida, Owner Earnings com o aluguel pago e capex de rede como manutenção. "
            "Razão (c): fator de Ke e provento não recorrente no yield.",
    autocritica=["O aluguel pago da Vivo é proxy (parcela circulante do passivo de arrendamento do ano anterior): a DFC junta arrendamento e "
                 "empréstimos numa linha só; limitada ao principal pago menos a dívida financeira que vencia. Afeta só o Owner Earnings, uma das três âncoras.",
                 "Por Greenwald (parte do capex como expansão) o central seria R$ {c_greenwald}.",
                 "Com a margem dos 12m ({m_ltm}) permanente, R$ {c_ltm} — CARA em qualquer caso.",
                 "O preço embute Ke de {ke_impl} ({ke_impl_real} real), menos de 1 p.p. acima do Tesouro.",
                 "Benefícios tributários pontuais (créditos de PIS/Cofins de 2018 e 2021) saíram como não recorrentes; outros podem ter ficado."],
    agenda="10/11 3T26 (não confirmado) · 12/11 Telefónica 9M26 · política de payout de 2027 (sem data) · 30/04/2027 pagamento dos JCPs de 2026",
    nao_encontrado="Release no RI (403 no PDF 03/10); política de 2027; participação total da Telefónica; recompras de ago–set."),

"FLRY3": dict(
    circulo="Medicina diagnóstica (Fleury, a+, Pardini e marcas regionais) com laboratório de apoio. Ganha com marca premium e escala do "
            "laboratório central; pararia com a verticalização das operadoras e pressão de preço dos planos.",
    controlador="Desconto de controlador: zero — controle compartilhado por médicos fundadores e Bradesco Seguros [PDF 03/10; FRE], sem "
                "interferência consumada.",
    receita_base="média de 2024, 2025 e 12m — perímetro com o Pardini",
    lynch="stalwart lento — PEG informativo",
    sens_extra=[],
    filtros=FILTROS_FALHA_1.replace("{f4}", "pagos ≤ Owner Earnings no acumulado 2020–25, mas o DPA médio supera o FCFE normalizado em ~7% e o "
                                            "dividendo de dez/25 sai em 3 parcelas até set/2027 — no limite"),
    sustentam=["Margem EBIT dos 12m {m_ltm}; com ela permanente, central R$ {c_ltm}",
               "DL/EBITDA {dl_ebitda}× com arrendamento (covenant 3,0× [PDF 03/10])",
               "Altman Z'' {altman} ({altman_zona}); Piotroski {piot}/9 [CVM]"],
    ameacam=["ROIC {roic} contra WACC {wacc}: o Pardini (2023) veio com ágio de R$ 6 bi pago em ações [PDF 03/10]",
             "DPA médio 5a R$ {dpa5} acima do FCFE normalizado R$ {fcfe} — o sustentável é o menor",
             "O preço embute Ke de {ke_impl} ({ke_impl_real} real)"],
    gatilho="crescimento orgânico < 7% por 2 trimestres, margem EBITDA < 24%, DL/EBITDA > 2× por aquisição ou nova emissão de ações para "
            "aquisição [PDF 03/10].",
    renda="Não. Yield sustentável a valor presente, líquido: {dy_liq}; dividendo parcelado em até 2 anos.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}.",
    de_para="A rev. 03/10 (R$ 23,70) era o central de 07/09 só reescalado pelo Ke, com DCF de FCFE a g real 3,5%, Graham com o LPA antigo e "
            "Piotroski 9/9 'da ficha'. Agora: margem 2019–25, receita do perímetro atual, arrendamento como dívida, Piotroski calculado ({piot}/9). "
            "Razão (c): fator de Ke e números da ficha anterior.",
    autocritica=["A margem de 2023–25 já carrega a amortização do intangível do Pardini (não caixa); somá-la de volta subiria o central.",
                 "Receita base sem 2023 (5 meses de Pardini) — se a sinergia render, o EBIT sobe; o motor não projeta sinergia.",
                 "Alíquota de {aliquota}; a dívida nova (debêntures de R$ 1,8 bi em ago/26 [PDF]) entra só no próximo balanço.",
                 "Com margem +2 p.p. o central iria a R$ {sens_m_mais}.",
                 "A linha de aluguel pago (R$ 0,43 bi em 2025) pode incluir juros, que já saem do lucro — mantida inteira (conservador); sem os juros o provento passaria a coberto."],
    agenda="05/11 3T26 (não confirmado) · 02/09/2027 3ª parcela do dividendo de dez/25 · fechamento da Unilab",
    nao_encontrado="Fato relevante da Unilab; recompra nova; guidance; percentual exato de cada parte do controle."),

"HYPE3": dict(
    circulo="Farmacêutica de marcas (OTC, similares, prescrição) e genéricos, com preço regulado pela CMED. Ganha com portfólio de marcas e "
            "distribuição; pararia com reajuste da CMED abaixo da inflação por anos (2026: média 2,47%, o menor em 20 anos [PDF 03/10]) e com "
            "nova piora do capital de giro.",
    controlador="Desconto de controlador: zero — João Alves de Queiroz Filho (25,9%) e Maiorem (13,3%), com acordo [FRE 2026]; sem extração "
                "consumada registrada. O JCP pago 15–21 meses depois sem correção [PDF 03/10] é custo do provento (valor presente, §6.3), não do valor.",
    receita_base="média 2023–25 + 12m",
    lynch="crescimento lento — PEG informativo",
    sens_extra=[("c34", "Alíquota de 34% em vez do piso de 15%")],
    filtros=FILTROS_FALHA_1.replace("{f4}", "pagos (R$ 0,6–0,8 bi/ano) ≤ Owner Earnings; JCP pago 15–21 meses depois — custo de {fvp} no valor presente"),
    sustentam=["Margem EBIT de 32–33% em 2016–23 [CVM]; mediana {m50}",
               "Owner Earnings mediano R$ {oe_bi} bi/ano acima dos proventos pagos",
               "Altman Z'' {altman} ({altman_zona}); Piotroski {piot}/9 [CVM]"],
    ameacam=["ROIC {roic} contra WACC {wacc}: a dívida líquida foi de R$ 0,8 bi (2020) a R$ {dl} bi com as aquisições [CVM]",
             "Margem de 2024–25 em 23–25%: com a margem dos 12m ({m_ltm}) o central seria R$ {c_ltm}",
             "Alíquota no piso de 15% (mediana negativa); a 34% o central iria a R$ {c34}"],
    gatilho="sell-out abaixo do mercado por 2 trimestres, prazo de recebimento > 75 dias ou DL/EBITDA > 2,8× [PDF 03/10].",
    renda="Não. Yield sustentável a valor presente, líquido: {dy_liq} — o JCP declarado em 2026 só entra em caixa até 31/12/2027.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}. É a menos cara do lote.",
    de_para="A rev. 03/10 (R$ 24,70) era o central de 07/09 + R$ 0,70 de Ke, com DCF de FCFE a g real 3% e Piotroski 9/9 'da ficha'. Agora: margem "
            "mediana de 10 anos sem não recorrentes (2019–20), Owner Earnings e EPV ao Ke de {ke_nom}, defasagem do JCP no valor presente. "
            "Razão (c): fator de Ke e números da ficha anterior.",
    autocritica=["A mediana de 10 anos ({m50}) supõe a volta ao patamar de 32%; com a margem dos 12m o central seria R$ {c_ltm}.",
                 "Alíquota: a mediana de 5 anos é negativa (créditos, JCP, subvenção) e a doutrina manda o piso de 15%; a 34%, R$ {c34}.",
                 "Semavy (semaglutida, lançado em 04/09) sem venda reportada e com propaganda proibida pela Anvisa em 28/09 [PDF 03/10] — fora do número.",
                 "O ROIC inclui o intangível de marcas compradas; sem ele seria ~25–30% [PDF 06/09], mas o acionista pagou esse intangível.",
                 "O preço embute Ke de {ke_impl} — a mais perto de JUSTA no lote, mas a 1,10× ainda não chega."],
    agenda="27/10 3T26 (1º dado do Semavy) · 31/12/2026 prazo do JCP de 2025 · 31/12/2027 prazo dos JCPs de 2026",
    nao_encontrado="Vendas do Semavy; data de pagamento do JCP de 2025; recompras; covenants da dívida."),

"ABEV3": dict(
    circulo="Maior cervejaria da América Latina (Brasil, Canadá, LAS e CAC), com marcas e distribuição próprias. Ganha com escala e custo; "
            "pararia com Imposto Seletivo alto (alíquota não definida; 5 p.p. = −4,2% do EBITDA, BofA [PDF 03/10]) ou perda contínua de volume.",
    controlador="Desconto de controlador: zero — AB InBev (~62% [PDF 03/10]) sem interferência consumada; contratos de licença com a controladora "
                "(V4) já estão no EBIT histórico. ON com tag along de 80% (não é Novo Mercado).",
    receita_base="média 2023–25 + 12m",
    lynch="stalwart — PEG informativo",
    sens_extra=[("c_aliq_motor", "Alíquota pela mediana 2021–25 (piso de 15%)")],
    filtros="1 passa (ROIC {roic} > WACC {wacc}); 2 passa (caixa líquido); 3 passa; 4 passa (proventos ≤ Owner Earnings; 2025 antecipado por "
            "razão fiscal) → 4 de 4.",
    sustentam=["ROIC {roic} acima do WACC {wacc}: cria valor no ciclo",
               "Dívida líquida R$ {dl} bi (caixa líquido); Altman Z'' {altman} ({altman_zona})",
               "Owner Earnings mediano R$ {oe_bi} bi/ano"],
    ameacam=["Margem EBIT caiu de 37% (2016) para 22–27% (2021–25) [CVM]; o p25 ({m25}) já é o patamar recente",
             "O preço embute Ke de {ke_impl} ({ke_impl_real} real)",
             "Alíquota subiu com a tributação da subvenção (24% em 2024, 18% em 2025 [CVM]); Imposto Seletivo a partir de 2027"],
    gatilho="volume de Cerveja Brasil negativo por 2 trimestres, margem EBITDA < 30%, alíquota efetiva > 25% ou Imposto Seletivo > 5 p.p. [PDF 03/10].",
    renda="Não. Yield sustentável a valor presente, líquido: {dy_liq}; retorno real líquido esperado {bogle_real}.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}.",
    de_para="A rev. 03/10 (R$ 13,75) partia de R$ 14,00 + R$ 0,36 de Ke − R$ 0,61 de erro próprio. Agora: margem mediana de 10 anos, alíquota "
            "pós-subvenção, Owner Earnings com o aluguel pago e as três âncoras ao Ke de {ke_nom}. Razão (c): ajuste avulso em R$.",
    autocritica=["A margem mediana de 10 anos ({m50}) inclui 2016–19 (34–37%), que pode não voltar; o p25 ({m25}) é o patamar de 2021–24.",
                 "Alíquota de {aliquota} (média 2024–25); pela mediana de 5 anos com piso de 15% o central seria R$ {c_aliq_motor}.",
                 "EBIT em reais inclui a Argentina (hiperinflação, IAS 29) e o Canadá — câmbio move o lucro sem mudar o negócio.",
                 "O Imposto Seletivo ficou fora do número (sem alíquota).",
                 "Com caixa líquido, o Ke da casa pesa: o mercado precifica a {ke_impl} ({ke_impl_real} real) — é a sensibilidade de Ke de mercado (§4)."],
    agenda="06/10 3ª parcela do JCP de 2025 · 29/10 3T26 · dez/26 declaração anual de proventos · fev–mar/2027 início do Imposto Seletivo",
    nao_encontrado="Alíquota do Imposto Seletivo; novo programa de recompra; FCF oficial de 12m; participação exata da AB InBev."),

"WEGE3": dict(
    circulo="Motores elétricos, transmissão e distribuição (transformadores), automação, tintas e geração; ~60% da receita fora do Brasil "
            "[PDF 03/10]. Ganha com engenharia, escala e verticalização; pararia com perda de repasse (tarifa de 37,5% EUA/México [PDF 03/10]) "
            "ou fim do ciclo de transformadores e data centers.",
    controlador="Desconto de controlador: zero — famílias fundadoras via WPA [FRE 2026], sem conflito identificado.",
    receita_base="média 2023–25 + 12m",
    lynch="stalwart / crescimento — PEG informativo",
    sens_extra=[("c_m5", "Margem mediana de 5 anos (2021–25) em vez de 10"), ("g1_0", "Sem 1º estágio (g real 2% desde já)"),
                ("g1_12", "1º estágio a 12% real por 10 anos")],
    filtros="1 passa (ROIC {roic} > WACC {wacc}); 2 passa (caixa líquido); 3 passa; 4 passa (proventos ≤ Owner Earnings; extraordinário de "
            "dez/25 em 3 parcelas até 2028) → 4 de 4.",
    sustentam=["ROIC {roic} contra WACC {wacc}: o melhor negócio do lote",
               "Caixa líquido; Altman Z'' {altman} ({altman_zona})",
               "Crescimento sustentável de 1º estágio {g1} real (ROE {roe5} × retenção)"],
    ameacam=["O preço exige g real de {g_impl} ao ano por 10 anos (DCF reverso) — a casa usa {g1}",
             "P/L 12m {pl_ltm}× e Ke implícito {ke_impl} ({ke_impl_real} real)",
             "Receita do 2T26 −0,6% a/a; Brasil −4,9% [PDF 03/10] — 2026 'ano de transição'"],
    gatilho="(invalida o CARA) receita > 15% a/a por 2 trimestres com margem EBITDA ≥ 22% [PDF 03/10]; ou preço ≤ R$ {compra}.",
    renda="Não. Yield sustentável a valor presente, líquido: {dy_liq}.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}. Mesmo com 12% real por 10 anos o central fica em R$ {g1_12}.",
    de_para="A rev. 03/10 (R$ 33,20) descontava g de 12% NOMINAL a Ke REAL de 12,08% (o erro do anexo do 08) e usava P/L 34 sem compressão. "
            "Agora: DCF em 2 estágios com g real {g1} a WACC real, EPV e Owner Earnings sem crescimento, ao Ke de {ke_nom}. Razão (c): mistura de "
            "nominal com real.",
    autocritica=["A margem mediana de 10 anos ({m50}) fica abaixo do patamar de 2023–25 (~20%); com a de 5 anos ({m5}) o central iria a R$ {c_m5}.",
                 "O g de 1º estágio ({g1}) é a regra ROE × retenção; a WEG entregou mais (com câmbio a favor). A 12% real: R$ {g1_12}.",
                 "EPV e Owner Earnings não carregam crescimento — por isso ficam abaixo do DCF; o central é a mediana.",
                 "Com caixa líquido, o Ke da casa pesa: o mercado precifica a {ke_impl} ({ke_impl_real} real) — sensibilidade de Ke de mercado (§4).",
                 "O Bogle usa o P/L mediano de 10 anos como final; a compressão de múltiplo que um compounder sofre ao amadurecer não está nele."],
    agenda="21/10 3T26 (não confirmado) · 10/03/2027 JCPs de 2026 · 11/08/2027 2ª parcela do extraordinário",
    nao_encontrado="Carteira de pedidos; FCF/FCO oficiais do 2T26; investimento em transformadores no México em 2026."),

"ITSA4": dict(
    circulo="Holding das famílias Setubal e Villela: {pct_itau} do Itaú (≈ 90% do lucro) mais Alpargatas, Dexco, Motiva, Aegea, Copa Energia e NTS. "
            "Ganha com os dividendos do Itaú; pararia com o fim do JCP (atinge banco e holding) ou com mais capital em não financeiras de retorno baixo.",
    controlador="Desconto de controlador: zero — famílias Setubal e Villela com acordo [FRE 2026], sem extração consumada. A alocação em não "
                "financeiras (aporte de R$ 732 mi na Aegea em ago/26; Fitch B+ [PDF 03/10]) já está no valor contábil delas e no ROE da holding.",
    filtros="1 falha (ROE de longo prazo {roe_lp} < Ke nominal {ke_nom}); 2 passa (caixa R$ {caixa} bi ≥ dívida R$ {divida} bi na holding); 3 passa; "
            "4 passa (dividendos do Itaú cobrem os pagos) → 3 de 4: segue no hall.",
    sustentam=["Holding com caixa R$ {caixa} bi contra dívida R$ {divida} bi [CVM, controladora]",
               "ROE de 12m {roe_ini} [CVM]",
               "Yield sustentável líquido {dy_liq}, coberto pelos dividendos do Itaú"],
    ameacam=["O valor vem do Itaú, e a ITUB4 está {itub_pc}× o central da casa (Lote 1): a perna Itaú vale R$ {itau_ps} por ação do banco",
             "ROE de longo prazo {roe_lp} abaixo do Ke nominal {ke_nom}",
             "Retorno real implícito {tir}, abaixo do Tesouro IPCA+ ({rf_real}): ao preço de hoje perde até para o título sem risco"],
    gatilho="fim do JCP sem compensação, desconto de holding > 25% por 2 trimestres ou novo aporte relevante em não financeira deficitária [PDF 03/10].",
    renda="Não para compra nova. Yield sustentável líquido {dy_liq}; retorno real líquido esperado {bogle_real}.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}. Na carteira: o preço está acima da saída (R$ {saida}).",
    de_para="A rev. 03/10 (R$ 15,45) era o SOTP com o Itaú no justo de 03/10 (ITUB4 R$ 45,40, calculado a Ke de mercado de 14%/coluna real) × 0,85. "
            "Agora: Itaú no central do Lote 1 v2.0 (R$ {itau_ps} por ação do banco, ao mesmo Ke), participação pelo FRE ({acoes_itau} mi de ações), "
            "demais participações a valor contábil e DDM como 2ª âncora. Razão (c): o SOTP herdava o ITUB4 a Ke de 14%.",
    autocritica=["A ITSA4 herda o veredito do ITUB4: se o Lote 1 estiver errado, este também está.",
                 "Demais participações a valor contábil (R$ {outras} bi); com o valor de mercado do RI de 31/08 (R$ 16,6 bi, marcado [H] no PDF) o SOTP iria a R$ {outras_merc}.",
                 "PIS/Cofins sobre o JCP recebido (~R$ 860 mi/ano [PDF 03/10]) descontado por 15 meses (R$ {pis} bi a valor presente); se a mudança de 2027 atrasar, o custo sobe.",
                 "Desconto de holding = G&A capitalizado (R$ {custo} bi) + PIS/Cofins; o mercado aplica {desc_merc} sobre o Itaú a mercado.",
                 "A fatia na IUPAR é econômica (66,53%; a Cia. E. Johnston tem o resto) — sem prêmio de controle no valor."],
    agenda="03/11 Itaú 3T26 · 09/11 Itaúsa 3T26 (não confirmado) · 30/11 data-com do JCP trimestral",
    nao_encontrado="Dívida bruta oficial da holding no RI; SOTP de setembro no RI; custo da holding no RI; percentual de cada não financeira."),
}
