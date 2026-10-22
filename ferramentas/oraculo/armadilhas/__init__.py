"""Validade do próprio oráculo (docs/ORACULO.md §2): mudanças-armadilha com o defeito, a camada e quem tem de pegá-lo.

A alçada foi decidida ANTES de medir (22/10/2026). "automatico" = o portão automático inteiro de docs/VALIDACAO.md §2: a suíte
(`pytest --ignore=backtest`, com o golden regravado no worktree como um autor faria — camada 0 não conta como prova) e o
`python -m oraculo` (camadas 2–5). "agente" = o agente `oraculo`, às cegas. As de processo (fonte, motivo do golden,
pré-registro) não têm número errado para o automático ver: são só do agente.
    python -m oraculo.armadilhas          # aplica cada patch num git worktree temporário e registra em docs/oraculo/
"""
ARMADILHAS = [
    dict(id="01", patch="01_zero_silencioso.patch", defeito="zero silencioso novo: lucro ausente vira 0 (Piotroski, Sloan, OE)",
         camada=2, alcada=("automatico", "agente")),
    dict(id="02", patch="02_real_nominal.patch", defeito="real × nominal: OE em R$ de hoje capitalizado ao Ke nominal",
         camada=1, alcada=("automatico", "agente")),
    dict(id="03", patch="03_sinal_divida_liquida.patch", defeito="sinal invertido na dívida líquida da ponte firma → acionista (EPV)",
         camada=1, alcada=("automatico", "agente")),
    dict(id="04", patch="04_unidade_acoes.patch", defeito="unidade: ações em milhares da CVM tomadas como unidades (lote 3)",
         camada=4, alcada=("automatico", "agente")),
    dict(id="05", patch="05_regua_afrouxada.patch", defeito="régua afrouxada sem registro: BARATA ≤ 0,75",
         camada=1, alcada=("automatico", "agente")),
    dict(id="06", patch="06_premissa_sem_fonte.patch", defeito="premissa digitada sem fonte que muda palavra (g real da KEPL3 1% → 3%)",
         camada=7, alcada=("agente",)),
    dict(id="07", patch="07_golden_sem_camada.patch", defeito="golden regravado sem a camada que provou o valor no motivo",
         camada=7, alcada=("agente",)),
    dict(id="08", patch="08_variante_fora_do_pre_registro.patch", defeito="variante v3 (prêmio 4,5 p.p.) sem linha no §6 do pré-registro",
         camada=7, alcada=("agente",)),
]
