# Mesa de Value Investing — handoff de design (front end local, somente leitura)

## 0. Como usar esta pasta
- `referencia/capturas/*.png`: alvo visual de cada tela (Hall, Empresa, Carteira em escuro; Hall e Empresa em claro; folha do sistema).
- `referencia/Mesa-de-Value-telas.html`: as mesmas telas num arquivo só, abre com duplo clique.
- `referencia/telas/*.dc.html` + `support.js`: fontes dos mockups. Usam um runtime de prototipagem. **Use só como referência de estrutura, CSS e textos. Não porte o runtime.** Para ver rodando: `python3 -m http.server` na pasta e abrir `Main.dc.html`.
- `tokens.css`: tokens oficiais (claro e escuro). Use como está.
- Todos os dados dos mockups são **ilustrativos** (tickers reais com números inventados). Nada ali é saída dos motores.

## 1. Produto
Painel web local que mostra o que os motores Python já calculam: hall de ~41 empresas com uma palavra cada, relatório por empresa, painel da carteira e da meta de renda, monitor semanal. Uso pessoal, mas com cara de produto profissional (terminal de pesquisa fintech, não app de corretora). Idioma: português do Brasil. Números no formato BR (R$ 1.234,56; 12,3%).

## 2. Regras que não podem quebrar
1. **O front não calcula nada de valuation.** Central, compra, saída, P/C, palavra, sensibilidade, renda estimada, % da meta, falta: tudo vem pronto dos motores. O front formata e exibe.
2. **Sem comparativo com renda fixa, sem projeção de renda, sem data estimada de cruzamento da meta, sem faixa de cenários na carteira.**
3. **Nunca parecer ordem de compra ou venda**: sem botões comprar/vender, sem verde/vermelho de trading. Palavras: BARATA (turquesa), JUSTA (só contorno), CARA (âmbar), NÃO CONCLUSIVO (tracejado com hachura).
4. **Cor nunca é o único sinal**: toda palavra tem texto + glifo (▼ BARATA, = JUSTA, ▲ CARA, ◌ NÃO CONCLUSIVO) + forma de preenchimento.
5. **Nota de fonte em todo número** (discreta, sempre visível): **A** oficial (CVM, B3) = quadrado sólido; **B** primária com ressalva = contorno; **C** agregador = tracejado; **—** sem fonte = pontilhado. Só A e B embasam decisão. Número com nota C ou "—" fica cinza com sublinhado pontilhado. Premissa de julgamento: linha hachurada + etiqueta JULGAMENTO. Hachura = "menos firme", em todo o sistema.
6. **Régua**: central = mediana dos métodos marcados "central" (informativos ficam fora). Compra = 0,70× o central. Saída = 1,30× o central, ou 1,50× quando a empresa passa na exceção de qualidade. Escala visual fixa de 50% a 160% do central, igual em todas as linhas. BARATA se preço ≤ compra; CARA se preço ≥ saída; JUSTA entre as duas; NÃO CONCLUSIVO quando não há central firme (régua vira caixa tracejada "sem central firme · só informativo"). Os fatores 0,70/1,30/1,50 e a lista de exceções devem vir do motor, não ficar fixos no front.
7. **Dado velho** = último pregão com mais de 7 dias: selo "velho" e linha mais clara. A palavra **não** vira NÃO CONCLUSIVO por idade.
8. **NÃO CONCLUSIVO e "premissa de julgamento" são estados de primeira classe**, não erro.
9. **Privacidade**: dados pessoais (quantidades, valores da carteira) ficam locais. Botão "Ocultar valores" na barra de topo troca valores em R$ por "•••" (percentuais da meta continuam). Barra lateral mostra "Local · somente leitura".
10. **Sensibilidade WACC × g** só como grade de valores pré-calculados, rotulada "pré-calculado". Nada é recalculado no front.
11. Acessibilidade: texto ≥ 4,5:1 de contraste, elementos gráficos ≥ 3:1, `<button>` e `<a>` reais, `aria-label` em ícones, gráficos com `role="img"` e descrição. Alvos de toque de 44 px no celular.
12. Sem emoji. Sem gradientes decorativos. Sem sombras em cartões (só popover).

## 3. Direção visual (o que as capturas mostram)
- **Fintech escura**: fundo azul-noite `#070B12`, cartões `#0E1520` com borda de 1 px e leve realce interno, fundo da área de conteúdo com pontilhado discreto. Modo claro equivalente (`#F3F6FB`). Tema escuro é o padrão; botão alterna e a escolha persiste em `localStorage`.
- **Shell**: menu lateral de 220 px (logo, seções ANÁLISE: Hall, Empresa, Carteira, Monitor; SISTEMA: Sistema) com ícones de traço 16 px; rodapé do menu com o bloco "Local · somente leitura · cotação/demonstrações". Barra de topo: contexto (caixa alta mono), busca (`/` foca), Ocultar valores, alternar tema. Abaixo de ~850 px o menu vira linha no topo.
- **Tipografia**: Space Grotesk (títulos, KPIs, números grandes), IBM Plex Sans (texto e números, com `font-variant-numeric: tabular-nums lining-nums`), IBM Plex Mono (tickers, rótulos em caixa alta com +0,09em, notas de fonte). Escala: KPI 34/38, título de página 30/33, seção 17/20, tabela 13/18, legenda 12/16, rótulo mono 11/13.
- **Raios** 4/8/12. **Espaço** base 4 (4, 8, 12, 16, 24, 32). Chips em pílula. Marcador de preço na régua com brilho leve no escuro.
- Fontes via Google Fonts (ou empacotar localmente se o painel precisar rodar offline; prefira local).

## 4. Telas
### Hall
- Título, subtítulo, **5 abas-cartão** (TODAS, BARATA, JUSTA, CARA, NÃO CONCLUSIVO) com contagem e %, e **barra de distribuição** abaixo. Clicar filtra.
- Barra de ferramentas: Ordenar por (P/C, Yield, Ticker, Dado mais velho), checkbox "Só central com fonte A ou B", contador "Exibindo X de 41".
- **Tabela** (div grid com roles ARIA de tabela; cabeçalho fixo): Empresa (ticker mono + nome · setor, selo "velho"), Palavra, Régua, Preço, Compra, Central (+nota, "n métodos"), Saída (+ "exc. 1,50×" quando aplicável), P/C, Yield (+nota), sparkline 12 meses com linha tracejada do central, Carteira (peso, mascarável). Linha com 44 px de altura mínima. Ticker leva à Empresa.
- Legenda sob a tabela: régua, notas A/B/C/—, "Só A e B embasam decisão".
### Empresa
- Cabeçalho: ticker mono grande + nome, chip da palavra, 4 tiles (Preço, Central, P/C, Yield proj.) com notas. Sub-navegação por âncoras (Valuation, Sensibilidade, Premissas, Qualitativo, Proventos, Fontes).
- **Régua grande** com rótulos: hoje (acima), compra/central/saída (abaixo) e valores.
- **Valuation por método**: faixas horizontais (baixo–base–alto) em eixo comum com linhas verticais de hoje, compra, central e saída. Métodos que entram no central: barra sólida + ponto cheio. Informativos (grupo separado): barra hachurada tracejada + ponto vazado. Coluna direita: valor-base e faixa.
- **Sensibilidade do DCF**: grade 5×5 de valores prontos, célula base com contorno grosso, tom frio/quente conforme valor do cenário contra o preço de hoje (4 níveis), etiqueta "pré-calculado".
- **Premissas**: tabela ordenada por efeito no central, com tipo (Julgamento hachurado / Derivada / Oficial), nota e mini-barra ±.
- **Qualitativo**: 5 cartões (negócio, dívida, governança, dividendos, riscos). Avaliação em 5 "pips" cinza com rótulo, texto-base e nota. Riscos como lista "probabilidade · impacto" em palavras.
- Lateral: Leitura da régua (palavra + frase + métodos no central + com fonte A/B), Proventos (histórico empilhado dividendos/JCP, barra tracejada = projeção, yield, payout, anos seguidos), Na carteira (mascarável), Fontes e frescor (fonte, data, nota).
### Carteira
- 4 KPIs: Renda mensal estimada (nota), Meta de renda (% + barra), Falta (R$/mês), Papéis. Gráfico "Evolução rumo à meta" só com renda estimada passada e linha da meta (eixo vira % da meta quando valores estão ocultos). Lista "Posição de cada papel na régua" (régua mini, peso, renda/ano). Calendário de proventos (12 meses, barras empilhadas dividendo/JCP). Próximos pagamentos (hachurado = estimado, nota = declarado/estimado). Concentração por setor.
### Monitor (rascunho; só aparece na folha do sistema)
- Quatro listas: "Entraram na compra" e "Entraram na saída" (semana), cada linha com régua mini mostrando círculo vazado (semana anterior) e traço (hoje), P/C anterior → atual. Rodapé recolhido "Sem mudança: N papéis". Sem botões de ação; cada linha leva à Empresa.
### Sistema
- Folha de estilo: palavras (claro/escuro), simulação de daltonismo, notas, tokens, tipografia, espaço/raio, anatomia e estados da régua, estados vazios/erro/velho/sem fonte, navegação e grid.

## 5. Estados
- Vazio por filtro ("Nenhuma empresa com esse filtro" + Limpar filtros). Carteira sem posições. Carregando (blocos hachurados).
- Erro de leitura: faixa neutra com borda forte e ícone "!": "Não foi possível ler <arquivo>. Exibindo a última leitura válida (data)". Nunca vermelho.
- Dado velho: ver regra 7. Sem fonte: valor visível, cinza, nota "—", fora do central.

## 6. Grid e responsividade
≥1280 px: 12 colunas, margem 24, gutter 16–20; Empresa com lateral de 340–360. 768–1279: 8 colunas, lateral desce, tabela rola na horizontal com ticker e palavra fixos. <768: 4 colunas, tabela do hall vira lista de cartões (ticker, palavra, régua, P/C; resto em "detalhes"). Teclado: `/` busca, `g h` `g c` `g m` navegam, ↑↓ percorrem o hall, Enter abre.

## 7. Contrato de dados (proposta; adapte ao que os motores já geram)
```
hall.json: { gerado_em, cotacao_em, demonstracoes_ref: "2T26",
  empresas: [{ ticker, nome, setor, palavra: "BARATA|JUSTA|CARA|NAO_CONCLUSIVO",
    preco, preco_nota, compra, central, central_nota, saida, fator_saida: 1.3|1.5,
    metodos_central, metodos_total, pc, yield_proj, yield_nota,
    serie_12m: [..24 pontos..], ultimo_pregao, dias_defasagem, peso_carteira|null }] }
empresa/<TICKER>.json: { cabecalho..., metodos: [{ nome, descricao, entra_no_central, baixo, base, alto, nota }],
  sensibilidade: { wacc: [], g: [], valores: [[]], classe: [[]], base: [i,j] },
  premissas: [{ nome, valor, tipo: "julgamento|derivada|oficial", nota, efeito }],
  qualitativo: [{ eixo, nivel: 1-5, rotulo, texto, nota }], riscos: [...],
  proventos: { historico: [{ano, dividendos, jcp}], yield_proj, payout, anos_seguidos },
  fontes: [{ nome, data, nota }] }
carteira.json: { renda_mensal_estimada, nota, meta, pct_meta, falta, n_papeis,
  renda_12m: [{mes, valor}], calendario: [{mes, dividendos, jcp}],
  pagamentos: [{data, ticker, tipo, valor, status: "declarado|estimado", nota}], posicoes: [{ticker, peso, renda_ano}] }
monitor.json: { semana, entraram_compra: [{ticker, pc_anterior, pc_atual}], entraram_saida: [...], sem_mudanca }
```
Campo ausente = `null`; a interface exibe "—" com nota "sem fonte". Nunca preencher com estimativa do front.

## 8. Critérios de aceite
- Cada tela confere com a captura (estrutura, tokens, densidade) nos dois temas.
- Nenhum cálculo de valuation no front (buscar por multiplicações de preço/central, medianas, projeções).
- Contraste conferido: texto ≥ 4,5:1, gráficos ≥ 3:1, nos dois temas.
- Nenhuma cor verde/vermelha de trading, nenhum botão de ação de compra/venda.
- Ocultar valores esconde todo valor em R$ e peso da carteira, em todas as telas.
- Números em formato BR, tabulares e alinhados à direita.
- Funciona offline e sem enviar dados para fora.
