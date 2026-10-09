# PROJECT BRIEF — Mesa de Value Investing B3
*Versão de 08/10/2026 (rev. Onda 1.3) · gerado por `/brief` · fonte: repositório, memória do projeto e `docs/auditoria/AUDITORIA_2026-10-08.md`*

## 1. Projeto
Mesa de análise fundamentalista da B3 para dividendos/JCP e longo prazo: doutrina escrita (v2.5) + motores de valuation em Python que
dão preço de compra, central e saída (régua 0,70/0,90/1,10/1,30×) para 41 empresas. Público hoje: um investidor pessoa física (uso próprio).

## 2. Estágio
MVP de uso pessoal, maduro no cálculo. Um usuário real, sem terceiros. Prazo externo conhecido: temporada do ITR 3T26 (fim de out–nov/2026,
`ferramentas/temporada.py`). Onda 1 da auditoria em andamento: 1.1 (bb79ba9), 1.2 (49b5f53 + dd9c3c1) e 1.3 (gatilhos) feitas; falta 1.4 (documentos). Meta de longo prazo: SaaS com front-end
(sem prazo).

## 3. Stack
- **Linguagem:** Python 3.14.0 (Windows 11). Sem `requirements.txt`/`pyproject`: versões abaixo são as do ambiente local, não fixadas.
- **Libs usadas no código:** pandas 2.3.3 · numpy 2.3.4 · reportlab 4.4.9 (PDFs dos lotes) · matplotlib 3.10.7 · requests 2.33.0 · pytest 9.0.2.
- **Banco:** nenhum. Dados em JSON/CSV/ZIP em `ferramentas/dados/` e `ferramentas/backtest/dados/` (~2,1 GB fora do git); registros
  append-only em `.jsonl` (`prospectivo/`).
- **Infra:** máquina local; Agendador do Windows (monitor semanal, sexta 08:00); GitHub privado + backup em pendrive. Sem nuvem.
- **APIs/fontes externas:** CVM dados abertos (DFP/ITR/FRE, RAD) — fonte A; B3 COTAHIST e proventos; BCB SGS (IPCA, PTAX); Tesouro
  Transparente (curva IPCA+); FRED (preços de commodities); StatusInvest (scraping, nota C).

## 4. Arquitetura
- **Doutrina e prompts (raiz, `00`–`09`):** regras, hall das 41, checklist anti-erro, diário de decisões — a "especificação".
- **Motores:** `motor_nao_financeiras.py` e `motor_financeiras.py` (quadro clássico: Graham, Bazin, EPV, DCF, OE…, central = mediana); `fiscal.py`.
- **Coleta:** `coletar_cvm.py`, `coletar_macro.py`, `coletar_statusinvest.py`, `proventos_ex.py`, `ltm.py`.
- **Lotes:** `loteN_*.py` (premissas digitadas) → `gerar_pdf_loteN.py`; `rodar_tudo.py` regrava o golden. O quadro do `03` e o hall do
  prompt de sexta são gerados do motor por `hall03.py` (Onda 1.3); preço oficial com data e fonte em `precos_hall.py`.
- **`dossie/`:** anexo mecânico por ticker (FRE, notas por evidência, vereditos). **`triagem/`:** fila de toda a B3, sem veredito.
- **`backtest/`:** ledger point-in-time + COTAHIST (parado no portão do proxy). **`monitor_semanal.py`**, **`temporada.py`**, **`registro_prospectivo.py`**.
- **Testes:** pytest com golden dos 41 tickers: 376 no hall (+1 pulado) + 301 no backtest (08/10, Onda 1.3). Mudança no `Mercado` ou nos motores exige rodar as duas suítes.

## 5. Top 5 gargalos
1. **Insumos e premissas, não fórmulas.** Auditoria de 08/10: 109 achados, 5 ALTO; motores conferem a 0–0,36%, mas insumos movem o central
   em 5–48% (AUD-01 receita nominal × real, `motor_nao_financeiras.py:386`; AUD-02 dividendos fora da DL, `lote4_saude_telecom.py:193`;
   AUD-03 IFRS 16 na PETR4; AUD-04 follow-on ISAE4 — corrigidos na Onda 1.1). Na 1.2 (v2.4) o custo de capital passou a depender da dívida
   (Ke por Hamada, pesos no ponto fixo, Kd sintético): os muito alavancados ficaram com Ke real de 21–27% (KLBN11 77%) — a vigiar.
2. **Premissas digitadas no código e dados em data fixa.** Mercado de 02–06/10, premissas nos `lote*.py`, parte dos dados da StatusInvest (C);
   sem banco nem coleta diária — bloqueia o SaaS.
3. **Régua sem validação empírica.** Backtest parou: proxy reproduziu a palavra em 70,7% (portão ≥ 80%). Validação agora só prospectiva,
   lenta por natureza.
4. **Universo que não gera compra.** Blue chips eficientes: quase tudo JUSTA/CARA, zero compra; triagem de toda a B3 deixou 5 de 104 no portão.
5. **Risco de burocracia.** O projeto paralelo (`analisador/`) morreu por regra nova a cada sessão sem decisão; o próprio repo registra sinais
   da mesma doença. Comitê único (mesma família de modelo; 2º comitê pausado).

## 6. Próximos 3 marcos
1. Onda 1 da auditoria: 1.1, 1.2 e 1.3 feitas → **1.4 documentos** (AUD-19, 35, 36, 69: PDFs dos lotes, pasta de upload, versões
   citadas nos prompts, células do `03` ainda digitadas).
2. Temporada 3T26: `python ferramentas/temporada.py` ao sair o ITR; régua congelada até lá.
3. Etapa 6 / F6 — construção de carteira (tamanho de posição, concentração, caixa); depende de respostas do Frank.

## 7. Restrições
- **Orçamento:** não informado.
- **Hardware:** notebook Windows 11, 20 GB RAM (VS Code + Claude + navegador já usam ~11 GB); disco C com pouco espaço livre (~4,6 GB em 08/10).
- **Dados sensíveis:** sem dados de saúde/pacientes. Dados financeiros pessoais (carteira) — tratar como privados.
- **Regulatório:** hoje uso próprio. Para SaaS com veredito a terceiros, provável enquadramento CVM (analista — Res. CVM 20/2021; consultor —
  Res. CVM 19/2021) — **a confirmar com fonte A**.
- **Licenças:** repo sem LICENSE. Termos de uso da B3 (COTAHIST) e da StatusInvest para redistribuição: não informado.

## 8. Ferramentas usadas / descartadas
- **Usadas:** Claude Code (análise, coleta, agente `adversario`, auditoria multiagente), git + GitHub privado, pytest + golden, reportlab,
  Agendador do Windows.
- **Descartadas/pausadas:** pipeline B3 antigo (extinto em 07/09/2026); `analisador/` (arquivado 08/10 — motor e régua piores, excesso de
  regra); Claude Desktop como 2º comitê e reenvio da pasta de upload (pausados 05–08/10, "não tem ajudado"); Cowork (só lê/escreve pasta, não
  analisa); backtest como validação da régua (portão falhou).

## 9. IA
- **Já usada:** toda a análise e o código via Claude Code; revisão adversarial antes do commit; auditoria multiagente; prompt de agente de
  notícias de sexta no Desktop (estado atual não informado).
- **Poderia entrar:** extração estruturada de FRE/ITR/fatos relevantes (PDF → JSON com fonte); vigia de fatos relevantes do IPE ligado aos
  gatilhos; 2º comitê de outra família de modelo (D14); checagem automática insumo × fonte A/B; consenso/lucro projetado (hoje "não encontrado").

## 10. O que é "melhor" aqui
- **Técnico:** todo número com fonte A/B e data; reproduzível (`rodar_tudo.py` = golden); testes verdes; premissas fora do código; dado fresco.
- **Científico:** sem viés de sobrevivência nem look-ahead; regra declarada antes de medir; o registro prospectivo é que valida ou refuta.
- **Profissional:** gerar decisão (compra/venda) com margem de segurança, não mais regras; simplicidade que se mantém sozinho.
- **Acadêmico:** não informado.

## 11. Perguntas para o Frank
1. Qual o orçamento mensal (APIs, dados pagos, hospedagem)?
2. O SaaS seria só para você ou para terceiros (muda o enquadramento CVM)? Há prazo?
3. Existe objetivo acadêmico (artigo, TCC, pós) ligado ao projeto?
4. O agente de notícias de sexta (Desktop) ainda roda?
5. Aceita fonte de dados paga (ex.: fundamentos com API) para substituir a StatusInvest?
6. Licença pretendida do código (fechado/aberto)?

## 12. O que mudou
Primeira versão.
- 08/10/2026 (Onda 1.2): doutrina v2.4; Onda 1 com 1.1 e 1.2 feitas; contagem de testes; gargalo 1 e marco 1 atualizados.
- 08/10/2026 (Onda 1.3): doutrina v2.5 (regulados por P/VP justificado como proxy declarado); ferramentas novas `hall03.py`,
  `precos_hall.py`, `triagem/erro_proxy.py`; monitor com falha ativa; corte da triagem medido (2,07); testes e marco 1 atualizados.
