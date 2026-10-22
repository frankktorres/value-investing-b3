# VALIDAÇÃO — contrato de "pronto" da Mesa

Vigente desde 22/10/2026 (Fase 1 de `docs/PROMPT-ORACULO-E-CALIBRACAO.md`; hipóteses em `docs/PRE-REGISTRO-v3.md`).
Vale para toda mudança daqui em diante, de dia e na rotina da nuvem. O conferente (oráculo) está em `docs/ORACULO.md`.

**Princípio.** Teste verde prova só o que o teste afirma. Para cada número que muda uma palavra, o projeto tem de dizer
**como sabe que ele está certo** (camadas 1–6) e **quem duvidou dele** (camada 7). Com o golden, o projeto sabe que o
número **não mudou**, não que ele está certo.

## 1. As 7 camadas de oráculo (Barr et al. 2015, IEEE TSE 41(5), "The Oracle Problem in Software Testing")

| # | Camada | O que prova | Onde mora | Comando | Bloqueia? |
|---|---|---|---|---|---|
| 1 | **Especificado** | O caso foi calculado à mão ou tirado do livro (Damodaran, Graham) e o número esperado está escrito no teste, **sem importar constantes do motor** | `ferramentas/tests/test_*.py` (ex.: `test_aud27_31_formulas.py`, `test_aud17_ddm_analitico.py`) | `cd ferramentas && python -m pytest --ignore=backtest -q` | sim |
| 2 | **Propriedade / metamórfico** | Leis que valem para qualquer entrada: monotonicidade (Ke ↑ ⇒ central não sobe), invariância (unidade, desdobramento, permutação), dado ausente ⇒ nunca palavra de decisão, sem NaN/inf, g < Ke | `ferramentas/tests/test_oraculo_propriedades.py` (Hypothesis, seed fixa) | idem + `python -m oraculo` | sim |
| 3 | **Diferencial** | Um motor-sombra independente (outro arquivo, sem importar o motor) chega ao mesmo central com os mesmos insumos; os insumos batem com o RI e com uma 2ª fonte | `ferramentas/oraculo/sombra.py`, `ferramentas/oraculo/insumos_externos.py` (Fase 4) | `python -m oraculo --diferencial` | sim, para fórmula |
| 4 | **Reconciliação contábil** | O dado da CVM fecha: ativo = passivo + PL; o DFC fecha com a variação do caixa; DRE = DMPL; dividendos DMPL ≈ DFC; ações × LPA | `ferramentas/oraculo/reconciliacao.py` | `python -m oraculo` | bandeira por ticker; bloqueia se a divergência for em campo crítico de ticker com palavra de decisão |
| 5 | **Sanidade econômica** | O universo faz sentido: P/L implícito do central, Ke implícito no preço, distribuição do P/C, Ke ≤ 30%, compounders decompostos, screens acadêmicos (Piotroski, Altman Z'', Beneish, Sloan, Greenblatt) | `ferramentas/oraculo/sanidade.py`, `ferramentas/oraculo/screens.py` | `python -m oraculo` | alarme de artefato bloqueia (Ke > 30%, NaN); o resto é relatório |
| 6 | **Resultado** | No tempo, a palavra acerta: ledger PIT (só com premissas derivadas, §4.3 do pré-registro) e registro prospectivo com probabilidade e Brier | `ferramentas/prospectivo/`, `ferramentas/backtest/` | `python registro_prospectivo.py` (por rodada) | não (só relata até ≥ 4 rodadas vencidas) |
| 7 | **Desafio independente** | Alguém que não escreveu a mudança tenta derrubá-la sem ver a argumentação do autor | agente `oraculo` (`.claude/agents/oraculo.md`), `adversario`, comitê B (Desktop) | ver `docs/ORACULO.md` | BLOQUEIA impede o master |

Teste que só confere "não quebra" ou só repete o golden é **camada 0**: conta como regressão, não como prova.

## 2. Definição de pronto por tipo de mudança

✔ = obrigatória · ◐ = obrigatória se a mudança tocar o que a camada cobre · — = não se aplica

| Tipo de mudança | 1 | 2 | 3 | 4 | 5 | 6 | 7 | Também |
|---|---|---|---|---|---|---|---|---|
| **Fórmula do motor** (`motor_*.py`, `inflacao`, `fiscal`, `credito`, `juros`, `defasagem`) | ✔ teste que falha antes | ✔ | ◐ sombra, se a fórmula existe nela | — | ✔ | — | ✔ agente `oraculo` | lista de palavras que mudam; `09`; golden com `--motivo` citando a camada |
| **Regra de doutrina** (`01`) | ✔ | ✔ | ◐ | — | ✔ | ✔ registrar variante e tentativas no pré-registro | ✔ agente + comitê B se for item grande | `01` versionado (antigo em `_historico/`); "ok" do Frank; `09` |
| **Premissa de ticker** (`lote*.py`, dossiê: `g_real`, `roe_lp`, `payout`, `kd_ri`, desconto, janela) | ◐ | ✔ (a régua roda) | ◐ insumo × RI | ◐ | ✔ | — | ✔ agente | fonte A/B citada na linha; derivável do dado? (pré-registro §4.3a) |
| **Coleta de dado** (`coletar_cvm.py`, `montar_series.py`, macro, B3) | ✔ caso real conferido no documento da CVM/B3 (`04` l.144) | ✔ dado ausente ⇒ nunca 0 | ✔ 2ª fonte | ✔ | ✔ | — | ◐ `adversario` | `python -m oraculo` verde; procedência gravada |
| **Golden** (regravação) | ✔ a camada que provou o novo valor | ✔ | ◐ | — | ✔ | — | ✔ agente | `rodar_tudo.py --motivo "<camada N provou X>"`; nunca regravar para "ficar verde" |
| **Tela** (`painel/`) | ◐ | — | — | — | — | — | — | Playwright: abrir, conferir, captura em `.playwright-mcp/`; tela só lê |
| **Relatório / PDF / dossiê** | ◐ número impresso = número do motor | — | — | — | — | — | — | `dossie.gerar` só com `--data` nova |
| **Só documentação** | — | — | — | — | — | — | — | `python -m oraculo.rastreabilidade --verificar` se mexeu no `01` |

Em toda linha valem também: suíte inteira verde (`cd ferramentas && python -m pytest --ignore=backtest -q`), rastreabilidade
verde (§3), e na nuvem os testes que pulam sem dado viram pendência do `conferir_noite.py`.

## 3. Matriz de rastreabilidade
- Fonte da verdade: `ferramentas/oraculo/matriz.py` (uma linha por regra do `01`: § → funções → testes → camada).
- Gerada em `docs/RASTREABILIDADE.md` por `cd ferramentas && python -m oraculo.rastreabilidade` e conferida por
  `tests/test_oraculo_rastreabilidade.py`, que **falha** se:
  1. uma seção do `01` não tem nenhuma linha;
  2. uma regra calculável não tem teste **e** não está na lista de lacunas declaradas;
  3. uma função ou um teste citado não existe;
  4. o número de lacunas **sobe** (catraca: só pode cair; quando cai, baixa-se o teto no mesmo commit);
  5. o `.md` gerado está desatualizado em relação à matriz.
- Regra sem teste = falha. A lacuna declarada é dívida com prazo: cada uma diz qual fase a fecha.

## 4. Regra do golden
- O golden (`ferramentas/tests/golden.json`) prova **estabilidade**, nunca correção. Ele congela o erro junto com o acerto.
- Toda regravação diz no `--motivo` **qual camada (1–5) provou que o valor novo está certo** e qual teste é. "Atualizei
  porque mudou" não é motivo.
- Regravar golden muda palavra publicada: segue a linha "Golden" da §2, com "ok" do Frank e `09`.

## 5. Política de dado ausente
- **Campo crítico ausente → NÃO CONCLUSIVO, nunca 0.** Campo crítico = qualquer insumo que entra numa âncora, no Ke, na
  ponte firma→acionista ou na régua: receita, EBIT, lucro, D&A, PL, caixa, dívida (bruta, CP, LP), imobilizado,
  ações, proventos, juros, preço, rf, π.
- Ausente ≠ zero. Só vale 0 quando a fonte diz 0 (ex.: CVM informa a linha com valor 0). A procedência fica gravada.
- `v(d, campo, 0)`, `x or 0` e `.get(campo, 0)` em campo crítico são proibidos em código novo. Os existentes estão
  listados na H10 do pré-registro e saem na Fase 3.
- O oráculo automático tem uma propriedade que remove cada campo crítico e exige NÃO CONCLUSIVO ou erro explícito.

## 6. O que não é prova
- O número de BARATAs, a mediana de P/C perto de 1, ou "o resultado parece razoável".
- Um teste que importa a constante do motor para calcular o esperado (é tautologia).
- Um golden verde.
- A concordância do autor consigo mesmo: a camada 7 recebe só o diff, o pré-registro, a doutrina e a saída do oráculo.

## Referências (a conferir antes de citar como decisão)
Barr, Harman, McMinn, Shahbaz & Yoo 2015, IEEE TSE 41(5):507-525 · Chen et al. 2018, ACM CSUR 51(1) (metamórfico) ·
Claessen & Hughes 2000 (QuickCheck) · SR 11-7 (Fed/OCC 2011) · Res. CMN 4.557/2017 art. 9º.
