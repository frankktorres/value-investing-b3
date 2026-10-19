"""ALLD3 (Allied Tecnologia) — ficha do dossiê · data-base 15/10/2026 · doutrina v2.6 · mesmo motor do hall.

Premissas declaradas ANTES do veredito (doutrina §11.4, §6.3; 02 regra 4):
  · Janela 2019–2025 (7 exercícios): o 1º DFP com DRE na CVM é o de 2019 (registro na CVM em 25/11/2020, IPO em
    abr/2021). É o máximo disponível, não uma janela escolhida.
  · Perfil "servicos" (distribuição e varejo de eletrônicos, não commodity): capex de manutenção pelo Greenwald com
    Δreceita real.
  · "Outras" líquidas (3.04.04 + 3.04.05) pela mediana da janela, como BLAU3/HYPE3: 2025 traz R$ 369 mi de outras
    receitas não recorrentes (DFP 2025 nota 24) que entrariam cheias no EBIT de um ano só.
  · Alíquota pela regra geral (mediana de 5 anos). Kd = rf nominal + spread sintético pela cobertura (v2.4); g real 1%
    (só vale se ROIC > WACC) — os mesmos do hall.
  · Ações: composição do capital do ITR de jun/2026 (CVM), sem tesouraria.
  · P/L histórico de fim de exercício com fonte A (`base.pl_hist`).
  · Defasagem do provento MEDIDA (datas da StatusInvest, C só para datas), como nos outros dossiês.
  · Qualitativo: NUNCA digitado — vem de `notas.py` sobre a evidência (02 v4, regra 11) pelo `gerar.py`.
"""
from __future__ import annotations

from dossie import base
from motor_nao_financeiras import Industrial

TK = "ALLD3"
ANOS = [str(a) for a in range(2019, 2026)]
RAZAO_JANELA = ("1º DFP com DRE na CVM é 2019 (registro CVM nov/2020; IPO abr/2021): janela = o máximo disponível "
                "(02 regra 4), não uma quebra estrutural")


def empresa(qualitativo: dict | None = None, desconto_controlador: dict | None = None, **sobrepor) -> Industrial:
    base.carregar(TK, dia_statusinvest="2026-10-19")      # 1ª coleta da StatusInvest (só datas de pagamento) da ALLD3
    kw = dict(
        anos_ciclo=ANOS, anos_outras=ANOS, janela_razao=RAZAO_JANELA, outras_liquidas=True,
        g_real=0.01, jcp_share=base.jcp_share(TK), pl_hist=base.pl_hist(TK),
        defasagem_meses=base.defasagem(TK),
        defasagem_fonte="datas de pagamento da StatusInvest (C, só datas), média ponderada pelo valor",
        desconto_controlador=desconto_controlador or {"tipo": "zero", "razao": "pendente: D3 do dossiê"},
        qualitativo=qualitativo or {},
    )
    kw.update(sobrepor)
    return Industrial(TK, "Allied Tecnologia", "servicos", preco=base.preco(TK), n_acoes=base.acoes_itr(TK), **kw)
