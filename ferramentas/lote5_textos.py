"""Texto qualitativo das fichas do Lote 5. Números entre chaves vêm do motor no momento da geração do PDF.
Fontes: [CVM] DFP/ITR; [SI] StatusInvest; [EIA]/[BCB]/[IBGE] séries de Brent, câmbio e IPCA; PDF 06/09 e 03/10 (fatos de produção, política de
preços, subvenção, imposto de exportação — extraídos em dados/fatos_lote5.json; fontes primárias listadas lá)."""

AGENDA = ("04/10 1º turno e 25/10 2º turno (pesos de cenário da PETR4) · revisão mensal da subvenção ao diesel (MP 1.391) · "
          "~07/11 fim da prorrogação do imposto de exportação de 12% · produção de setembro (PRIO3, RECV3) em outubro · "
          "3T26 em novembro (datas não encontradas no material) · 03–04/11 Copom")

ANTES = {"PETR4": ("CARA", 39.00), "PRIO3": ("JUSTA", 58.00), "RECV3": ("JUSTA (aviso ARMADILHA)", 12.30), "UGPA3": ("CARA", 31.00),
         "VBBR3": ("CARA", 29.00)}

T = {
"PETR4": dict(
    circulo="Maior produtora de petróleo do país: pré-sal de custo de extração ~US$ 9/bbl [PDF 03/10], refino quase monopolista e gás. "
            "Ganha com barril alto e custo baixo; pararia com preço doméstico abaixo da paridade por anos ou capex desviado para projetos sem retorno "
            "— os dois já aconteceram (2011–14).",
    controlador="Desconto de controlador: {desc} em cenários ponderados, não no Ke (tabela abaixo). Consumado: preços abaixo da paridade em "
                "2011–14 (V1); diesel abaixo da paridade de importação desde mar/26, hoje compensado em parte pela subvenção da União (R$ 1,00/l, "
                "MP 1.391) [PDF 03/10]; imposto de exportação de 12% em 2026; capex crescente em refino e fertilizantes (V3); extraordinários de "
                "2021–23 e corte de 2015–17 (V5). Sem o desconto o central seria R$ {sem_desc}.",
    sustentam=["Margem de meio de ciclo de {m50} (EBITDA mediano de 10 anos − D&A atual − impairment recorrente), com pré-sal a ~US$ 9/bbl de extração",
               "Dívida líquida/EBITDA {dl_ebitda}× (normalizado {dl_ebitda_norm}×) e cobertura de juros {cobertura}× [CVM]",
               "Distribuindo todo o lucro de meio de ciclo (LPA R$ {lpa_norm}) o retorno é ≈ Ke: o preço paga o barril de meio de ciclo, não o de guerra"],
    ameacam=["Sensibilidade ao barril: a Brent US$ 70 permanente o central cai para R$ {b70}; a US$ 60, R$ {b60}",
             "Provisão de abandono de R$ 153,7 bi [CVM]: tratada como dívida (líquida de IR), o central cai para R$ {abandono} — CARA",
             "Pesos de cenário dependem da eleição de 04 e 25/10; preço doméstico abaixo da paridade desde mar/26 [PDF 03/10]"],
    gatilho="Política de dividendos (45% do FCF com dívida bruta < US$ 75 bi) alterada, realização efetiva abaixo da paridade por 2 trimestres "
            "sem subvenção, ou capex anual acima de US$ 25 bi com fatia de refino/fertilizantes crescente.",
    renda="Não como compra nova: o DPA de 5 anos (R$ {dpa5}) vem de anos de Brent alto e extraordinários; no meio de ciclo o yield cai. "
          "Quem já tem pode manter — está no justo.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}.",
    de_para="A rev. 03/10 (R$ 39) era DCF de Brent US$ 70 sem câmbio declarado e somava '+1 tri de topo' no cenário base. Agora o barril de meio de "
            "ciclo vem de 10 anos de Brent × câmbio em reais de hoje (R$ {barril}/bbl, ≈ US$ {brent_eq}), com arrendamentos (FPSOs) na dívida, "
            "ganhos de desinvestimento de 2019–22 fora da margem e o mesmo desconto de ~8% em cenários. Razão (c): método v1 sem conta reproduzível.",
    autocritica=["A palavra depende do barril: a US$ 70 permanente seria CARA (R$ {b70}); a US$ 90, R$ {b90}. O preço embute Ke de {ke_impl}.",
                 "O DCF pondera margem p25 ({m25}, 25º percentil da margem EBIT dos 10 anos — é de 2018, Brent ~US$ 71, e não dos anos de petróleo barato) a 25%; sem esse peso o central iria ao EPV (R$ {epv}).",
                 "Impairment recorrente ({imp_rec} da receita, mediana de 10 anos) entra como custo; pela regra de margem EBIT do Lote 3 o central seria R$ {regra_ebit}. "
                 "Déficit atuarial fora da ponte porque o custo já está no EBIT; se ele também fosse dívida, R$ {com_atuarial}.",
                 "Abandono fora da ponte é a premissa mais frágil: a D&A mediana supera o capex mediano, mas a onda de descomissionamento da Bacia de Campos "
                 "pode exigir caixa antes da D&A — com abandono como dívida, R$ {abandono}.",
                 "Ações ON e PN somadas ao preço da PN; a ON costuma negociar com prêmio — o valor por PN pode estar levemente subestimado."],
    nao_encontrado="Produção e reservas 1P/2P atuais; desembolso de abandono previsto no plano de negócios; % da dívida em dólar; crack spread; "
                   "realização efetiva por produto no 3T26."),
"PRIO3": dict(
    circulo="Maior independente de E&P do país: compra campos maduros offshore (Frade/Wahoo, Albacora Leste, Peregrino) e corta custo — lifting "
            "~US$ 9/bbl no 2T26 [PDF 03/10]. Ganha com barril alto e aquisição barata; pararia com M&A caro, declínio sem reposição ou tributo "
            "sobre exportação (vende quase tudo para fora).",
    controlador="Desconto de controlador: zero — corporação sem controlador definido (Tanure como referência), sem interferência consumada. "
                "O imposto de exportação (12%, prorrogado até ~07/11) é risco regulatório, mostrado como sensibilidade, não como desconto.",
    sustentam=["Produção 2T26 de 172 kbpd (+72% a/a) e ~187 kbpd em setembro [PDF 03/10]; com 187 kbpd o central iria a R$ {vol187}",
               "Margem EBITDA mediana desde Frade (2019–25) de ~65% — custo de extração entre os menores do país",
               "Preço embute Ke de {ke_impl} — quase o Ke da casa: o mercado paga o justo, não mais que isso"],
    ameacam=["Imposto de exportação de 12% permanente: central R$ {imposto}",
             "Brent: a US$ 70 permanente o central cai para R$ {b70}; a US$ 60, R$ {b60}",
             "Zero dividendo (política adiada), cobertura de juros {cobertura}× (juros pagos) e dívida líquida de R$ {dl_bi} bi [CVM]"],
    gatilho="Produção abaixo de 150 kbpd por 2 trimestres, dívida líquida/EBITDA acima de 2× por M&A caro, ou imposto de exportação tornado permanente.",
    renda="Não. Não paga dividendo; o retorno depende de reinvestir em aquisições.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}. Só ficaria JUSTA com produção de 187 kbpd sustentada E Brent acima do meio de ciclo.",
    de_para="A rev. 03/10 (R$ 58) era 'central declarado' sem pesos, com Brent US$ 70 e produção de 185 kbpd. Agora: volume do 1S26 a barril de meio "
            "de ciclo, D&A atual (exaustão do Peregrino comprado) e ganhos de compra vantajosa de 2019–20 fora da margem. Razão (c): método v1 sem conta.",
    autocritica=["A janela 2019–25 tem barril médio ~11% acima do meio de ciclo: a margem mediana pode estar alta, não baixa.",
                 "Pela regra do Lote 3 (margem EBIT de 10 anos, base 12m) o central seria R$ {regra_ebit} — a palavra é a mesma.",
                 "O 1S26 tem o imposto de exportação dentro da receita se ele for deduzido dela; se cair em novembro, a base sobe até 12%.",
                 "A D&A atual (Peregrino a preço de compra) é o custo de repor reservas; se novas aquisições forem mais baratas, o valor sobe.",
                 "Cobertura de juros {cobertura}× (EBIT ÷ juros pagos na DFC) — a dívida cresceu com o M&A; vigiar."],
    nao_encontrado="Reservas 1P/2P e vida útil; hedge; dívida bruta e caixa pela empresa; produção oficial de setembro; data do 3T26."),
"RECV3": dict(
    circulo="Produtora onshore de campos maduros (Bahia e Potiguar) com gás relevante. Ganha revitalizando campos que a Petrobras vendeu; "
            "pararia se o declínio natural vencer o capex — a produção caiu 11% a/a no 2T26 e está ~5% abaixo da certificação 1P [PDF 03/10].",
    controlador="Desconto de controlador: zero — sem controlador definido (free float 93,6% [PDF 06/09]), sem interferência consumada.",
    sustentam=["Valor de reprodução (PL contábil) R$ {reprod}/ação: o preço (R$ 11,20) está abaixo do livro",
               "Dívida líquida baixa: DL/EBITDA {dl_ebitda}× [CVM]; Altman Z'' {altman} (zona {altman_zona})",
               "Brent a US$ 90 permanente levaria o central a R$ {b90}"],
    ameacam=["ROIC normalizado {roic} contra WACC {wacc}: o EPV é R$ {epv} — cada real investido vale bem menos que um real; o livro não é valor",
             "Capex mediano acima da D&A em {aj_txt}: mesmo investindo mais que a depreciação, a produção cai",
             "Dividendo médio acima do FCFE normalizado (Owner Earnings negativo) — parcelas de 2027–28 dependem do caixa"],
    gatilho="Produção abaixo de 23 kboe/d por 2 meses, revisão da certificação para baixo, ou parcelas de dividendo de 2027–28 adiadas.",
    renda="Não. O dividendo não é coberto pelo fluxo normalizado.",
    capital="Não. Sem palavra pela regra: no meio de ciclo o lucro, depois do capex que só freia o declínio, não paga o custo de capital "
            "(EPV ≈ zero); só o livro sustenta o preço.",
    de_para="A rev. 03/10 (JUSTA, R$ 12,30) somava DCF de 24 kboe/d estável e EV/EBITDA de 3,5× sem capex de manutenção. Agora: margem EBITDA mediana − "
            "D&A atual ({da_pct} da receita) − capex acima da D&A, e declínio de 3% real ao ano. Razão (c): método v1 sem capex e sem declínio.",
    autocritica=["Com produção estabilizada (g = 0) o central iria a R$ {g0} — ainda muito abaixo do preço.",
                 "O livro (R$ {reprod}) inclui a compra do Potiguar; com ROIC de {roic} o ativo não rende o custo de capital (Greenwald: vale o EPV).",
                 "Hedges limitam o ganho com Brent alto [PDF 03/10]; a sensibilidade ao Brent supõe captura de 70% e pode exagerar.",
                 "Série curta (2020–25): o meio de ciclo de 6 anos é frágil.",
                 "Na rev. 03/10 o aviso de ARMADILHA estava certo; o central é que estava alto."],
    nao_encontrado="Reservas 2P e vida útil; lifting cost; posição de hedge; produção de setembro."),
"UGPA3": dict(
    circulo="Holding de distribuição: Ipiranga (combustíveis, ~76% do EBITDA [PDF 06/09]), Ultragaz (GLP, nº 1), Ultracargo (tancagem) e Hidrovias. "
            "Ganha com escala logística e margem por m³; pararia com margem de distribuição achatada por importador/sonegador ou GLP com preço controlado.",
    controlador="Desconto de controlador: zero — Ultra S.A. (famílias fundadoras), Novo Mercado, sem conflito identificado.",
    sustentam=["Dívida líquida/EBITDA {dl_ebitda}× e Altman Z'' {altman} (zona {altman_zona}) [CVM]",
               "ROC de {roc}: negócio de pouco capital fixo",
               "Recompras contínuas e proventos pagos em todos os anos da série [SI]"],
    ameacam=["EBIT de 12m (R$ {ebit_ltm} bi) contra R$ {ebit_meio} bi normalizado: a margem Ipiranga do 2T26 (R$ 451/m³) é o dobro da normal [PDF 03/10]",
             "Mesmo com a margem de guerra permanente o central seria R$ {guerra} — abaixo do preço",
             "ROIC normalizado {roic} contra WACC {wacc}: crescer não cria valor"],
    gatilho="Margem Ipiranga abaixo de R$ 200/m³ por 2 trimestres (confirma o meio de ciclo) ou, em alta, venda de fatia da Ipiranga a ≥ 7× EBITDA.",
    renda="Não. Yield sustentável líquido {dy_liq}.",
    capital="Não. {palavra} ({pc}× o central); compra ≤ R$ {compra}.",
    de_para="A rev. 03/10 (R$ 31) era DCF com pico caindo até 2028 e EV/EBITDA de 5,5–6× sobre EBITDA normalizado de R$ 7,3–8,4 bi. Agora: EBIT real "
            "mediano de 2021–25 (perímetro sem Oxiteno/Extrafarma), arrendamentos na dívida e capex de manutenção. Razão (c): v1 com múltiplo sem conta.",
    autocritica=["A Hidrovias entra inteira na dívida desde 2025, mas o seu EBIT só aparece em parte da janela — viés contra a UGPA3 (não quantificado com fonte).",
                 "A margem de 2021 (pós-pandemia, estoque) puxa o p25; com margem +2 p.p. o central iria a R$ {sens_m_mais} — a escala de ±2 p.p. é grande para margem de 3%.",
                 "Pela margem por m³ do PDF (R$ 170–220) o EBITDA normalizado seria R$ 7,3–8,4 bi; o daqui (EBIT real + D&A) fica perto de R$ 6,5 bi.",
                 "O preço embute Ke de {ke_impl}; o mercado aposta que a margem de guerra dura.",
                 "Rumor Chevron/Ipiranga sem fato relevante desde mar/26 — fora do valor."],
    nao_encontrado="Volume da Ipiranga (m³) e margem do 3T26; EBIT da Hidrovias por ano; participação do controlador."),
"VBBR3": dict(
    circulo="Maior distribuidora de combustíveis (~8 mil postos, marca Petrobras licenciada) + Comerc (energia renovável). Ganha com escala "
            "e suprimento; pararia com margem por m³ normalizada e Comerc consumindo caixa.",
    controlador="Desconto de controlador: zero — corporação sem controlador desde 2021, sem interferência consumada.",
    sustentam=["Maior rede e embandeiramentos recorde [PDF 03/10]; ROC de {roc}",
               "Altman Z'' {altman} (zona {altman_zona})",
               "Créditos tributários de 2020, 2023 e 2024 (3.04.05) já retirados da margem normalizada — o número é limpo"],
    ameacam=["EBIT de 12m R$ {ebit_ltm} bi contra R$ {ebit_meio} bi normalizado; margem do 2T26 R$ 436–456/m³ [PDF 03/10]",
             "Só com a margem de guerra permanente o central (R$ {guerra}) passaria do preço",
             "Comerc com prejuízo ajustado no 2T26; JCP pago 14–18 meses depois da data-com [PDF 03/10]"],
    gatilho="Margem ≤ R$ 300/m³ por 4 trimestres com oferta global normalizada (confirma CARA); Comerc com lucro ajustado positivo por 2 trimestres (revisar).",
    renda="Não. Yield sustentável líquido {dy_liq} e JCP com até 18 meses de atraso.",
    capital="Não — e fica fora do hall (redundante com UGPA3). {palavra} ({pc}× o central).",
    de_para="A rev. 03/10 (R$ 29) somava DCF com pico até 2028 e EV/EBITDA de 6×; o EPV dela (R$ 11–16) já apontava abaixo. Agora: EBIT real mediano "
            "de 2020–25 sem créditos tributários, Comerc na dívida. Razão (c): v1 com múltiplo sem conta.",
    autocritica=["A Comerc (consolidada em 2025) traz dívida inteira e EBIT só no fim da janela — viés contra a VBBR3.",
                 "A série de DPA anterior a nov/25 não está ajustada pela bonificação de 7,11% — o DPA médio está levemente alto.",
                 "Mudança de auditor em 02/10: teor não lido [PDF 03/10].",
                 "Com margem +2 p.p. o central iria a R$ {sens_m_mais} — escala grande para margem de 3%.",
                 "O preço embute Ke de {ke_impl}."],
    nao_encontrado="Volume (m³) e margem do 3T26; termos da licença da marca Petrobras; EBIT da Comerc por ano."),
}
