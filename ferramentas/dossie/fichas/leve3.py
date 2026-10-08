"""LEVE3 (MAHLE Metal Leve) — ficha do dossiê · doutrina v2.3 · mesmo motor do hall.

LEVE3 já está no hall (Lote 6): as demonstrações vêm da MESMA série da CVM do hall (`cvm_series.json`, DFP 2016–25 + ITR
2T26). O dossiê troca, só em memória e só dentro do `gerar.calcular` (`base.isolado`), os proventos da StatusInvest pelos
da B3 (fonte A) — o golden de 41 não vê a troca.

Premissas declaradas ANTES do veredito (doutrina §11.4, §6.3; 02 regra 4):
  · Janela 2016–2025 (10 exercícios, a da doutrina; a mesma do hall). Sem quebra estrutural declarada.
  · Perfil "servicos" (autopeças industrial, como no hall): capex de manutenção pelo Greenwald com Δreceita real.
  · "Outras" líquidas (3.04.04 + 3.04.05), como no hall.
  · Receita de base = default do motor (média de 2023, 2024, 2025 e 12m até jun/2026).
  · Alíquota pela regra geral da v2.3 (mediana de 5 anos; a da LEVE3 fica acima de 15%, sem fase).
  · Kd = rf nominal + 1,5 p.p.; g real 1% (só vale se ROIC > WACC) — os mesmos do hall.
  · Ações: composição do capital do ITR de jun/2026 (CVM), sem tesouraria.
  · P/L histórico de fim de exercício com fonte A (`base.pl_hist`).
  · Defasagem do provento MEDIDA (datas da StatusInvest, C só para datas), como nos outros dossiês.
  · Qualitativo: NUNCA digitado — vem de `notas.py` sobre a evidência (02 v4, regra 11) pelo `gerar.py`.
"""
from __future__ import annotations

from dossie import base
from motor_nao_financeiras import ANOS as ANOS_HALL, Industrial

TK = "LEVE3"
ANOS = list(ANOS_HALL)          # 2016–2025


def empresa(qualitativo: dict | None = None, desconto_controlador: dict | None = None, **sobrepor) -> Industrial:
    base.carregar(TK)
    kw = dict(
        outras_liquidas=True, spread_kd=0.015, g_real=0.01,
        jcp_share=base.jcp_share(TK), pl_hist=base.pl_hist(TK),
        defasagem_meses=base.defasagem(TK),
        defasagem_fonte="datas de pagamento da StatusInvest (C, só datas), média ponderada pelo valor",
        desconto_controlador=desconto_controlador or {"tipo": "zero", "razao": "pendente: D3 do dossiê"},
        qualitativo=qualitativo or {},
    )
    kw.update(sobrepor)
    return Industrial(TK, "MAHLE Metal Leve", "servicos", preco=base.preco(TK), n_acoes=base.acoes_itr(TK), **kw)
