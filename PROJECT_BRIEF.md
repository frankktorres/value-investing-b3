# PROJECT BRIEF — Mesa de Value Investing B3
*Versão de 19/10/2026 (rev. fase 1 do relatório, fatia 2; doutrina v2.6) · gerado por `/brief` · fonte: repositório, memória do projeto e `docs/auditoria/AUDITORIA_2026-10-08.md`*

## 1. Projeto
Mesa de análise fundamentalista da B3 para dividendos/JCP e longo prazo: doutrina escrita (v2.6) + motores de valuation em Python que
dão preço de compra, central e saída (régua 0,70/0,90/1,10/1,30×) para 41 empresas. Público hoje: um investidor pessoa física (uso próprio).

## 2. Estágio
MVP de uso pessoal, maduro no cálculo. Um usuário real, sem terceiros. Prazo externo conhecido: temporada do ITR 3T26 (fim de out–nov/2026,
`ferramentas/temporada.py`). Onda 1 da auditoria concluída: 1.1 (bb79ba9), 1.2 (49b5f53 + dd9c3c1), 1.3 (gatilhos) e 1.4 (documentos) feitas; Onda 2 concluída (reprodutibilidade AUD-38/73/108/109/17/102/82/24/26/86/21–23/81/83/84, backup AUD-05 e testes que distinguem certo de errado AUD-27/28/30/31/88/89/90/29/107/91); Onda 3 concluída em 10/10 (riscos latentes, doutrina v2.6; 22 corrigidos, 26 aceitos com motivo no `09`). Meta de longo prazo: SaaS com front-end
(sem prazo).

## 3. Stack
- **Linguagem:** Python 3.14.0 (Windows 11). `requirements.txt` na raiz fixa as 6 libs abaixo (09/10/2026); sem `pyproject`.
- **Libs usadas no código:** pandas 2.3.3 · numpy 2.3.4 · reportlab 4.4.9 (PDFs dos lotes) · matplotlib 3.10.7 · requests 2.33.0 · pytest 9.0.2.
- **Banco:** nenhum. Dados em JSON/CSV/ZIP em `ferramentas/dados/` e `ferramentas/backtest/dados/` (~2,1 GB fora do git); registros
  append-only em `.jsonl` (`prospectivo/`).
- **Infra:** máquina local; Agendador do Windows (monitor semanal, sexta 08:00); GitHub privado + backup em pendrive. Sem nuvem.
- **APIs/fontes externas:** CVM dados abertos (DFP/ITR/FRE, RAD) — fonte A; B3 COTAHIST e proventos; BCB SGS (IPCA, PTAX); Tesouro
  Transparente (curva IPCA+); FRED (preços de commodities); StatusInvest (scraping, nota C).

## 4. Arquitetura
- **Doutrina e prompts (raiz, `00`–`09`):** regras, hall das 41, checklist anti-erro, diário de decisões — a "especificação".
- **Motores:** `motor_nao_financeiras.py` e `motor_financeiras.py` (quadro clássico: Graham, Bazin, EPV, DCF, OE…, central = mediana); `fiscal.py`.
- **Reprodutibilidade (Onda 2):** `bootstrap_dados.py` (receita: `--baixar`, `--verificar`, `--derivados`), `manifesto_cvm.py` (sha256 dos 77 ZIPs em `dados/cvm/MANIFESTO.json`), `derivados_zip.py` (os lotes 4 e 6 usam o snapshot `dados/derivados_zip.json` quando os ZIPs não estão no disco) e `dados_opcionais.py` (skip explícito do que depende do suplemento da B3). Clone limpo roda `pytest --ignore=backtest`.
- **Backup (AUD-05):** o git tem remoto privado (GitHub `frankktorres/value-investing-b3`); `backup_dados.py` grava em `OneDrive/Backups/value-investing` um ZIP datado do que não se recria (`dados/` sem `cvm/`, mais `proxy_consultas.log` e `proxy_*.json` do backtest) e um `git bundle`. Os ZIPs da CVM e o COTAHIST são públicos e voltam pelo `bootstrap_dados.py`, então não entram.
- **Coleta:** `coletar_cvm.py`, `coletar_macro.py`, `coletar_statusinvest.py`, `proventos_ex.py`, `ltm.py`.
- **Lotes:** `loteN_*.py` (premissas digitadas) → `gerar_pdf_loteN.py`; `rodar_tudo.py` regrava o golden. O quadro do `03` e o hall do
  prompt de sexta são gerados do motor por `hall03.py` (Onda 1.3); preço oficial com data e fonte em `precos_hall.py`.
- **`dossie/`:** anexo mecânico por ticker (FRE, notas por evidência, vereditos). **`triagem/`:** fila de toda a B3, sem veredito.
- **`backtest/`:** ledger point-in-time + COTAHIST (parado no portão do proxy). **`monitor_semanal.py`**, **`temporada.py`**, **`registro_prospectivo.py`**.
- **Testes:** pytest com golden dos 41 tickers: 458 no hall (09/10, Onda 2 concluída; `EXIGIR_DADOS=1` transforma skip em falha) + 308 no backtest (09/10; rodar SOZINHO, ~13 min, e com a máquina folgada: a suíte inteira estoura memória se algo mais estiver aberto). Mudança no `Mercado` ou nos motores exige rodar as duas suítes.

## 5. Top 5 gargalos
1. **Insumos e premissas, não fórmulas.** Auditoria de 08/10: 109 achados, 5 ALTO; motores conferem a 0–0,36%, mas insumos movem o central
   em 5–48% (AUD-01 receita nominal × real, `motor_nao_financeiras.py:386`; AUD-02 dividendos fora da DL, `lote4_saude_telecom.py:193`;
   AUD-03 IFRS 16 na PETR4; AUD-04 follow-on ISAE4 — corrigidos na Onda 1.1). Na 1.2 (v2.4) o custo de capital passou a depender da dívida
   (Ke por Hamada, pesos no ponto fixo, Kd sintético): os muito alavancados ficaram com Ke real de 21–27% (KLBN11 77%) — a vigiar.
2. **Premissas digitadas no código e dados em data fixa.** Mercado de 02–06/10, premissas nos `lote*.py`, parte dos dados da StatusInvest (C);
   sem banco nem coleta diária — bloqueia o SaaS. Inventário e proposta de migração em `docs/PREMISSAS-B15.md` (445 campos fora do default; nada movido).
3. **Régua sem validação empírica.** Backtest parou: proxy reproduziu a palavra em 70,7% (portão ≥ 80%). Validação agora só prospectiva,
   lenta por natureza. Pré-registro fixado em 14/10 (B25): IC de postos P/C × retorno excedente sobre a média do hall; 1ª leitura possível em out/2027.
4. **Universo que não gera compra.** Blue chips eficientes: quase tudo JUSTA/CARA, zero compra; triagem de toda a B3 deixou 5 de 104 no portão.
5. **Risco de burocracia.** O projeto paralelo (`analisador/`) morreu por regra nova a cada sessão sem decisão; o próprio repo registra sinais
   da mesma doença. Comitê único (mesma família de modelo; 2º comitê pausado).

## 6. Próximos 4 marcos
1. Onda 1 da auditoria concluída (1.1 a 1.4: PDFs reemitidos em v2.5, pasta de upload sincronizada, versões dos prompts, Ke/retorno do `03` gerados
   pelo motor) → **Onda 2 (concluída):** feitos clone do zero (AUD-38/73), manifesto dos ZIPs (109), EOL do golden_sha (108), teste analítico do DDM (17), backup (05), testes de fórmula/limiar/NaN/ROIC real/bordas/skip (27, 28, 30, 31, 88, 89, 90) e, na 3ª parte, registro com corrente (102), preço real (82), série vigente (24), estado do lote 4 (26), coletor do LTM (21, 22, 86), JCP duplicado (23), coletor FRED/PTAX (81) e histórico (83, 84); e, na 4ª parte, sentinela PIT comparando o `Exercicio` inteiro e sem estouro de memória (29, 107) e paridade do motor reduzido × mesa (91). `cvm_series.json` já foi regravado com o LTM novo.
2. Temporada 3T26: `python ferramentas/temporada.py` ao sair o ITR; régua congelada até lá.
3. **Onda 3 da auditoria — CONCLUÍDA em 10/10/2026 (doutrina v2.6).** Motor blindado (guardas de NÃO CONCLUSIVO nas financeiras, sem preço negativo nem Infinity, fronteira da régua, LTM da temporada chegando às premissas calculadas no import); decisões do Frank: trava na palavra final, OE do controlador, freio do declínio, cenário negativo como zero, entrada parcial numa função só; 26 aceitos com motivo (`09`). Pendente de decisão própria: pré-registro (AUD-32/98/99) e razões do desconto zero em 29 tickers (AUD-41). Onda 4 (qualidade e rumo SaaS) a abrir.
4. Etapa 6 / F6 — construção de carteira (tamanho de posição, concentração, caixa); depende de respostas do Frank.
5. **Roteiro de 19/10 (produto):** fase 1 = `relatorio <TICKER>` (PDF por empresa, quanti + quali, fonte por número) — fatias 1
   e 2 feitas (f1bb010 preço/veredito; 20f7818 quali 6 blocos + PDF, BBSE3 e HYPE3); faltam ALLD3 (B08) e revisão (adversário + verificador-fonte). Depois: painel da carteira e da meta
   (fase 2), dados vivos sem premissa digitada (fase 3), triagem contínua (fase 4), SaaS.

## 7. Restrições
- **Orçamento:** não informado.
- **Hardware:** notebook Windows 11, 20 GB RAM (VS Code + Claude + navegador já usam ~11 GB); disco C com pouco espaço livre (~4,6 GB em 08/10).
- **Dados sensíveis:** sem dados de saúde/pacientes. Dados financeiros pessoais (carteira) — tratar como privados.
- **Regulatório:** hoje uso próprio. Para SaaS com veredito a terceiros, provável enquadramento CVM (analista — Res. CVM 20/2021; consultor —
  Res. CVM 19/2021) — **a confirmar com fonte A**.
- **Licenças:** repo sem LICENSE. B3 (lido, nota A): site só para uso pessoal; dados históricos/fim de dia livres para distribuidor/redistribuidor
  (Política de Market Data v3.0.4, §7.9–7.10) — SaaS exige enquadramento. StatusInvest: termos bloqueados (403). Ver `docs/TERMOS-DE-USO-FONTES.md`.

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
- 08/10/2026 (Onda 1.2): doutrina v2.4; Onda 1 com 1.1 e 1.2 feitas; contagem de testes; gargalo 1 e marco 1 atualizados.
- 08/10/2026 (Onda 1.3): doutrina v2.5 (regulados por P/VP justificado como proxy declarado); ferramentas novas `hall03.py`,
  `precos_hall.py`, `triagem/erro_proxy.py`; monitor com falha ativa; corte da triagem medido (2,07); testes e marco 1 atualizados.
- 09/10/2026 (Onda 1.4): `hall03.py` também gera Ke implícito/retorno do `03`; 6 PDFs reemitidos (rev. 09-10-2026, v2.5); pasta de upload
  sincronizada (reenvio ao Desktop segue suspenso); gerador do lote 6 corrigido (`por_metodo`); estágio e marco 1 atualizados.
- 09/10/2026 (Onda 2, 1ª parte): requirements, bootstrap, snapshot dos derivados de ZIP, manifesto sha256 dos ZIPs, sha do golden sem EOL, teste analítico do DDM/P/VP justificado; stack, arquitetura e marcos atualizados.
- 09/10/2026 (Onda 2, 2ª parte): backup (AUD-05); testes de fórmula, limiares, NaN no golden, ROIC real e bordas (AUD-27/28/30/31/88/90); skip vira falha com `EXIGIR_DADOS=1` (AUD-89); `qualifica_saida` extraída do motor; stack, arquitetura e marcos atualizados.
- 09/10/2026 (Onda 2, 4ª parte): sentinela PIT compara `Exercicio` inteiro (dfc e ITR) com máscara vetorizada; `backtest/tests/test_paridade_nf.py` (motor reduzido × mesa) fixa a divergência da alíquota v2.3; `coletar_cvm.main` marca erro quando o ITR do mês não tem DRE. Onda 2 concluída.
- 09/10/2026 (Onda 2, 3ª parte): registro prospectivo com corrente sha256 e preço oficial; série vigente explícita; coletor do LTM (comparativo reapresentado, SMTO3 abr–mar, lacunas visíveis); dossiê sem JCP duplicado; `coletar_macro_fred.py` + manifesto macro; `historico_arquivos.py` (versão anterior vai para `_historico/` antes de regravar); histórico do monitor em upsert; gargalo/estágio/marco atualizados.
- 09/10/2026 (dados): `cvm_series.json` regravado com o LTM novo (decisão do Frank); nenhuma palavra mudou, SMTO3 central 16,03 → 14,68 (segue CARA); golden, 03, prompt de sexta e PDFs dos lotes 3 e 5 regravados.
- 10/10/2026 (checkup e rodada): monitor semanal rodado (boletim de 10/10, histórico em upsert); `python -m dossie.gerar HYPE3` sem `--data` sobrescreveu o veredito de 02/10 (restaurado do git, cópia em `_historico/2026-10-10 hype3 regerado pelo passo 4/`); poka-yoke: `gerar` recusa regravar veredito já registrado no prospectivo (`dossie/tests/test_gerar_recusa.py`); cabeçalhos do `03`, README, prompt de sexta e `04` alinhados; Onda 3 aberta como marco 3.
- 10/10/2026 (Onda 3): doutrina v2.6 (AUD-10 trava na palavra final; AUD-15/34/53 OE do controlador, freio do declínio, DCF sem cenário negativo; AUD-42 `entrada_parcial`); `series_vigente.carregar_cvm` + `CVM_SOBREPOSTO` (o LTM do 3T26 chega às premissas do import, AUD-103/85); coletor da CVM sem lucro do controlador zerado e com ações do ITR (AUD-68); golden, 03 e prompt de sexta regravados; nenhuma palavra mudou; estágio e marco 3 atualizados.
- 13/10/2026 (rotina na nuvem): carteira do monitor saiu do código para `ferramentas/carteira_tickers.json` (só tickers); `requirements.lock` (fechamento transitivo, referência) ao lado de `requirements.txt`; rodada de 10/10 conferida (já registrada no `09` e acima).
- 14/10/2026 (rotina, B24/B25/B23/B15/B11): motor exige razão no desconto de controlador (28 com "sem razão documentada", LEVE3 com FRE nota A; nenhuma palavra mudou); pré-registro contínuo no `registro_prospectivo.py`; tabela de P/C por premissa da PETR4 no gerador do lote 5 (PDF não reemitido); relatório B15; termos da B3 lidos, StatusInvest 403.
- 19/10/2026 (fase 1, fatia 1): pacote `ferramentas/relatorio/` + `relatorio.cmd` → `RELATORIOS/<TK>-<data>.md`, vista dos motores com nota A/B/C/— por número; BBSE3 CARA com central apoiado em premissa arbitrada (AUD-58); marco 5 aberto.
- 19/10/2026 (fase 1, fatia 2): `relatorio/quali.py` (moat, gestão, dívida, governança, dividendos, riscos; FRE e proventos B3 por ticker) + `render_pdf.py`; `relatorio BBSE3|HYPE3` geram PDF; cortes de risco fora da doutrina marcados "a conferir"; 542 testes verdes, golden intacto; B27 feita.
