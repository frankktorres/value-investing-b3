"""VLID3 (Valid Soluções) — ficha do dossiê · data-base 15/10/2026 · doutrina v2.6 · mesmo motor do hall.

Premissas declaradas ANTES do veredito (doutrina §11.4, §6.3; 02 regra 4):
  · Janela 2016–2025 (10 exercícios, a da doutrina; DFP com DRE completo na CVM em todos os anos). Sem quebra estrutural
    declarada: a janela é a do hall.
  · Perfil "servicos": cartões, identificação e serviços de autenticação (não commodity): capex de manutenção pelo Greenwald com Δreceita real.
  · "Outras" líquidas (3.04.04 + 3.04.05) pela mediana da janela, como BLAU3/HYPE3/ALLD3.
  · Alíquota pela regra geral (mediana de 5 anos). Kd = rf nominal + spread sintético pela cobertura (v2.4); g real 1%
    (só vale se ROIC > WACC) — os mesmos do hall.
  · Ações: composição do capital do ITR de jun/2026 (CVM), sem tesouraria (todas as classes).
  · P/L histórico de fim de exercício com fonte A (`base.pl_hist`).
  · Defasagem do provento MEDIDA (datas da StatusInvest, C só para datas), como nos outros dossiês.
  · Qualitativo: NUNCA digitado — vem de `notas.py` sobre a evidência (02 v4, regra 11) pelo `gerar.py`.
"""
from __future__ import annotations

from dossie import base
from motor_nao_financeiras import ANOS as ANOS_HALL, Industrial

TK = "VLID3"
ANOS = list(ANOS_HALL)          # 2016–2025


def empresa(qualitativo: dict | None = None, desconto_controlador: dict | None = None, **sobrepor) -> Industrial:
    base.carregar(TK, dia_statusinvest="2026-10-19")      # 1ª coleta da StatusInvest (só datas de pagamento) de VLID3
    kw = dict(
        outras_liquidas=True, g_real=0.01,
        jcp_share=base.jcp_share(TK), pl_hist=base.pl_hist(TK),
        defasagem_meses=base.defasagem(TK),
        defasagem_fonte="datas de pagamento da StatusInvest (C, só datas), média ponderada pelo valor",
        desconto_controlador=desconto_controlador or {"tipo": "zero", "razao": "pendente: D3 do dossiê"},
        qualitativo=qualitativo or {},
    )
    kw.update(sobrepor)
    return Industrial(TK, "Valid Soluções", "servicos", preco=base.preco(TK), n_acoes=base.acoes_itr(TK), **kw)
