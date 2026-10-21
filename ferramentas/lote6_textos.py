"""Texto qualitativo das fichas do Lote 6. Números entre chaves vêm do motor no momento da geração do PDF.
Fontes: [CVM] DFP/ITR; [SI] StatusInvest; [BLS]/[BCB]/[IBGE] índices de preço, câmbio e IPCA; PDF 07/09 e 03/10 (controle, ativos, contratos,
gatilhos, partes relacionadas — extraídos em dados/fatos_lote6.json; fontes primárias listadas lá)."""

AGENDA = ("3T26 entre o fim de outubro e o início de novembro (datas não verificadas no material) · 03–04/11 Copom · "
          "EUA–Canadá: retaliação canadense desde 08/09 e cota de 4 Mt sem acordo (GGBR4) · dez/2026: janela de 12m sem provento da UNIP6 · "
          "pagamento do dividendo de 20/08 da EGIE3 ainda sem data")

ANTES = {"GGBR4": ("RADAR", 30.80), "UNIP6": ("CARA (defeito estrutural; era ARMADILHA)", 37.00), "LEVE3": ("CARA", 29.70), "EGIE3": ("CARA", 26.70)}

T = {
"GGBR4": dict(
    circulo="Siderúrgica de aço longo por forno elétrico a sucata no Brasil, nos EUA/Canadá e na América do Sul, mais aços especiais. Ganha com o "
            "spread aço − sucata e com a proteção tarifária dos EUA (≈ 76% do EBITDA vem da América do Norte [PDF 03/10]); pararia com aço "
            "importado abaixo do custo no Brasil e com o fim do ciclo de tarifas nos EUA.",
    controlador="Desconto de controlador: zero — Metalúrgica Gerdau (família Gerdau Johannpeter), sem interferência consumada em 15 anos "
                "[PDF 03/10]. Tag along da PN não confirmado no estatuto (StatusInvest mostra 100%).",
    sustentam=["Valor de reprodução (PL contábil) R$ {reprod}/ação: o preço está a {pvp}× o livro",
               "DL/EBITDA {dl_ebitda}× (normalizado {dl_ebitda_norm}×) e Altman Z'' {altman} (zona {altman_zona}) [CVM]",
               "Com o aço dos 12m como permanente (índice {idx12m}, meio = 100) o central iria a R$ {p12m}"],
    ameacam=["ROIC de meio de ciclo {roic} contra WACC {wacc}: o EPV (R$ {epv}) fica abaixo do livro — o real reinvestido vale menos que um real",
             "EBIT de 12m sem a baixa de ativos (R$ {ebit_ltm} bi) contra R$ {ebit_meio} bi de meio de ciclo: o aço americano dos 12m está {acima_meio} acima do meio",
             "Baixas de ativo (impairment) de R$ 2,9 bi em 2016, R$ 1,1 bi em 2017 e R$ 2,0 bi em 2025 [CVM] — capital mal alocado de forma repetida"],
    gatilho="EBITDA da América do Norte −25% em 2 trimestres, margem EBITDA consolidada < 14% por 2 trimestres, DL/EBITDA > 1,5×, ou fim das "
            "tarifas da seção 232 nos EUA.",
    renda="Não. Yield sustentável líquido {dy_liq}; o provento acompanha o ciclo do aço.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}. A tese da rev. 03/10 era de valor patrimonial (P/VP < 1), mas com ROIC "
            "abaixo do custo de capital o livro não é piso — o EPV fica abaixo dele.",
    de_para="A rev. 03/10 (R$ 30,80) era o central de 07/09 reescalado por Gordon (+2,7%), DCF de FCFE com LPA normalizado de R$ 2,26, sem EPV, sem "
            "reprodução e sem preço de aço declarado. Agora: receita de 12m ao aço de meio de ciclo (índice BLS em R$ de hoje; fator {fator}), margem "
            "EBIT mediana de 10 anos sem as baixas de cada ano (impairment mediano como custo) e as três âncoras de cíclica. Razão (c): método v1 "
            "sem conta reproduzível.",
    autocritica=["O índice é o preço ao produtor dos EUA (BLS), não o vergalhão no Brasil — onde o aço chinês derrubou o preço; o proxy pode "
                 "superestimar o meio de ciclo da operação Brasil e subestimar o efeito da tarifa nos EUA.",
                 "Tarifa de 50% da seção 232 permanente: com o aço dos 12m o central seria R$ {p12m}; com o aço de ago/26 (índice {idx_ult}), R$ {p_ult}.",
                 "O PL em reais inclui ágio de aquisições nos EUA ao câmbio de hoje: a reprodução pelo livro sobe com o dólar.",
                 "O DCF pondera a margem p25 ({m25}) a 25%; com margem +2 p.p. o central iria a R$ {sens_m_mais}.",
                 "Ações ON e PN somadas ao preço da PN (mesmo tratamento da PETR4); ON e PN têm os mesmos proventos."],
    nao_encontrado="Preço do vergalhão e da bobina no Brasil (R$/t) em série longa; volumes por operação; tag along da PN no estatuto; data do 3T26."),
"UNIP6": dict(
    circulo="Maior produtora de cloro-soda e PVC do Mercosul (Cubatão e Santo André no Brasil; Bahía Blanca na Argentina), com 63% da energia "
            "autoproduzida [PDF 03/10]. Ganha com o spread de cloro-soda e PVC e com custo de energia; pararia com PVC asiático importado abaixo do "
            "custo e com energia cara.",
    controlador="Desconto de controlador: zero — Vila Velha S.A. (família Geyer, 57% das ON) [PDF 03/10], sem interferência consumada. O tag along "
                "da PNB pode ser 0% (não confirmado no formulário de referência) e a política de distribuir acima do lucro com dívida subindo é "
                "decisão do controlador — fica como defeito estrutural (§7), não como desconto.",
    sustentam=["ROIC de meio de ciclo {roic} contra WACC {wacc}: com a cesta de preços de meio de ciclo o negócio paga o custo de capital",
               "EPV R$ {epv} e DCF R$ {dcf}: as âncoras de lucro ficam perto do preço",
               "Cesta soda/PVC dos 12m no índice {idx12m} (meio = 100): o preço da commodity está abaixo do meio de ciclo"],
    ameacam=["Defeito estrutural: R$ {div25} mi pagos em 2025 contra lucro de R$ {lucro25} mi; dívida bruta de R$ {div22} bi (2022) para R$ {div_bruta} bi "
             "(jun/26); nenhum provento em 2026 [CVM][PDF 03/10]",
             "Cobertura de juros {cobertura}× e DL/EBITDA {dl_ebitda}× [CVM]",
             "Valor de reprodução (PL) R$ {reprod}/ação: o preço é {pvp}× o livro — o livro foi distribuído"],
    gatilho="DL/EBITDA > 3,5×, cobertura de juros < 1,2× por 2 trimestres, nova distribuição acima do lucro com dívida subindo, ou margem EBIT "
            "< 10% por 4 trimestres.",
    renda="Não. O provento médio de 5 anos (R$ {dpa5}) supera o FCFE normalizado (R$ {fcfe}); em 2026 não houve provento.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}. As âncoras discordam {dispersao}× (pelo lucro de meio de ciclo o preço fica "
            "perto do valor; pelo livro, bem acima). Defeito estrutural: dividendo não coberto por caixa.",
    de_para="A rev. 03/10 (R$ 37) era o DCF de FCFE de 07/09 reescalado (+2,5%); em 04/10 o carimbo ARMADILHA virou CARA com defeito estrutural "
            "(P/L 24 não é múltiplo baixo). Agora: receita de 12m à cesta de meio de ciclo (fator {fator}), margem EBIT mediana de 2017–25 e as três "
            "âncoras de cíclica, com preço e margem na mesma janela ({janela}). EPV e DCF sobem (a margem dos 12m, 11,7%, está perto da mínima da série); a reprodução cai (PL distribuído). Razão (c).",
    autocritica=["A margem mediana ({m50}) supera a de 2023–25 ({m3a}); com ela o central (mediana) iria a R$ {c3a}. O PVC asiático pode ter "
                 "rebaixado o meio de ciclo de forma permanente.",
                 "A dispersão das âncoras ({dispersao}×) está abaixo do corte de 3× (§11.3), mas perto: acima dele a palavra deixa de existir. O índice dos EUA (soda + resinas, 50/50) não é o preço realizado no Mercosul.",
                 "Reprodução pelo livro subestima o custo de construir uma planta de cloro-soda hoje; laudo de reposição não encontrado — com ele "
                 "a dispersão das âncoras mudaria.",
                 "Argentina em IAS 29 (hiperinflação) distorce receita e EBIT da Indupa ano a ano.",
                 "Ações ON, PNA e PNB somadas ao preço da PNB."],
    nao_encontrado="Preço realizado de soda e PVC (R$/t) e volumes; tag along da PNB no formulário de referência; reconciliação do caixa "
                   "(653 mi × 1,4 bi); data do 3T26."),
"LEVE3": dict(
    circulo="Fabricante de componentes de motor (pistões, anéis, bronzinas), filtros e gerenciamento térmico para montadoras e reposição "
            "(~36% da receita) [PDF 03/10], controlada pela MAHLE alemã. Ganha com escala, tecnologia licenciada e a reposição da frota a combustão; "
            "pararia com a eletrificação da frota brasileira ou com a controladora capturando margem por preço de transferência.",
    controlador="Desconto de controlador: zero — Grupo MAHLE (61%), Novo Mercado, tag along 100% [PDF 03/10]. A MAHLE é fornecedora, cliente e "
                "licenciadora (R$ 569 mi + marca R$ 7,9 mi em partes relacionadas [PDF 07/09]) — vetor V4 prospectivo, não consumado: vira gatilho.",
    sustentam=["ROIC normalizado {roic} contra WACC {wacc}: o negócio cria valor (único do lote)",
               "DL/EBITDA {dl_ebitda}× e Altman Z'' {altman} (zona {altman_zona}) [CVM]",
               "O preço embute Ke de {ke_impl} — acima do Ke da casa; as três âncoras concordam ({dispersao}×)"],
    ameacam=["Margem EBIT de 12m ({m_ltm}) acima da mediana de 10 anos ({m50}): com a de 12m permanente o central iria a R$ {c_ltm}",
             "Dívida bruta de R$ {div21} bi (2021) para R$ {div_bruta} bi (jun/26) com payout alto: parte do provento foi financiada [CVM]",
             "Partes relacionadas com a controladora e eletrificação de longo prazo; com g real zero o central iria a R$ {g0}"],
    gatilho="Margem EBITDA < 17% por 2 trimestres, reposição caindo > 8% a/a por 2 trimestres, DL/EBITDA > 1,8×, payout > 100% do lucro ajustado "
            "ou OPA de fechamento pela MAHLE.",
    renda="Pode manter. Yield sustentável líquido {dy_liq}; o DPA médio de 5 anos (R$ {dpa5}) inclui o extraordinário de 2023 — sem ele, "
          "R$ {dpa_sem_extra}, abaixo do FCFE normalizado (R$ {fcfe}).",
    capital="Não como compra nova: {palavra} ({pc}× o central); compra ≤ R$ {compra}. Exceção de 1ª parcela: {excecao}.",
    de_para="A rev. 03/10 (R$ 29,70) era o central de 07/09 reescalado por Gordon (+2,4%), DCF de FCFE com Ke de IPCA 4%. Agora: margem EBIT "
            "mediana de 10 anos sobre a receita média de 2023–25 + 12m, capex de manutenção por Greenwald, IR efetivo de {aliquota} e três âncoras "
            "(DCF, EPV, Owner Earnings). O central sobe porque o ROIC acima do WACC passa a valer no DCF e o EPV entra em termos reais. Razão (c).",
    autocritica=["IR efetivo de {aliquota} (mediana de 5 anos, com JCP e incentivos); a 34% o central cairia para R$ {c34}.",
                 "Trava de coerência: {trava_txt}",
                 "A margem de 2016 (0,7%) puxa o p25; com margem −2 p.p. o central iria a R$ {sens_m_menos}.",
                 "A receita de 2024–25 inclui as aquisições de 2024 [PDF 07/09]: a média de 3 anos mistura perímetros (viés contra a LEVE3).",
                 "Owner Earnings sai do lucro reportado de 2021–25 (margens acima da mediana); com o lucro normalizado a âncora cai a R$ {oe_alt} e o "
                 "central vai a R$ {c_oe} — ainda JUSTA."],
    nao_encontrado="Covenants; volumes OEM/reposição/exportação; preço de transferência com a MAHLE; data do 3T26."),
"EGIE3": dict(
    circulo="Maior geradora privada do país (11,3 GW: 7,0 GW hídricos e 4,2 GW eólicos/solares), 3.205 km de transmissão, 17,5% da TAG e 40% de "
            "Jirau [PDF 07/09]. Ganha com contratos de 10–15 anos e RAP de transmissão; pararia com preço baixo na recontratação (1.624 MWm "
            "descontratados em 2030) e curtailment persistente (20% no 2T26).",
    controlador="Desconto de controlador: zero — ENGIE S.A. (~69%), Novo Mercado, tag along 100%. A compra de 40% de Jirau, financiada pelo "
                "follow-on de R$ 8,36 bi, passou por comitê independente com aprovação só dos minoritários [PDF 07/09] — V4 prospectivo; o preço "
                "pago entra como sensibilidade (Jirau rendendo menos que o Ke), não como desconto.",
    sustentam=["ROE de longo prazo do negócio existente {roe_old_lp} (mediana 2017–25 sem não recorrentes)",
               "TIR real implícita {tir} contra rf real {rf} e Ke real {ke_real}",
               "Contratos de ~13 anos e RAP de transmissão (Asa Branca/Graçã: +R$ 577 mi/ano) [PDF 07/09]"],
    ameacam=["Se Jirau render só a rf nominal, o central cai para R$ {jirau_rf}; se não render nada, R$ {jirau_zero}",
             "O JUSTA está no fio: vira CARA com ROE do negócio existente abaixo de {roe_virada} (mediana {roe_old_lp}; média {roe_media} → R$ {central_media}; 12m {roe_old_ini} → R$ {central_roe_atual})",
             "DL/EBITDA {dl_ebitda}× com capex de transmissão e curtailment de 20% [CVM][PDF 03/10]"],
    gatilho="Atraso de Asa Branca/Graçã, curtailment > 20% por mais 2 trimestres, DL/EBITDA > 4×, ou recontratação de 2030 abaixo de R$ 180/MWh.",
    renda="Pode manter; compra nova só ≤ R$ {compra}. Yield sustentável líquido {dy_liq}; payout mínimo de 55%.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}.",
    de_para="A rev. 03/10 (R$ 26,70) era o central de 07/09 reescalado, com TIR de 9,0–9,4% calculada a Ke de IPCA 4%. Agora: método de regulado do "
            "Lote 2 (P/VP justificado + DDM), ROE de longo prazo limpo do ganho da venda da TAG em 2024, patrimônio de jun/26 − dividendo de ago/26 + follow-on de "
            "jul/26 e 1.416 mi de ações. Razão (c).",
    autocritica=["O ROE de longo prazo vem de anos com payout ~100% (PL pequeno); com payout de 55% o PL cresce e o ROE tende a cair — com o ROE "
                 "de 12m o central seria R$ {central_roe_atual}.",
                 "Jirau ao Ke é premissa neutra; o preço pago à controladora não foi auditado aqui.",
                 "g nominal {g} (teto π + 2% real) supõe que o reinvestimento rende o ROE de longo prazo; transmissão nova rende menos.",
                 "TAG (17,5%) entra pelo lucro de equivalência, sem SOTP.",
                 "Bonificação de 40% (dez/25) ajustada à mão nos proventos da StatusInvest."],
    nao_encontrado="Preço pago por Jirau e TIR do negócio; GSF; preço por contrato; covenants; data do 3T26."),
}
