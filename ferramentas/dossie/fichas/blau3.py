"""BLAU3 (Blau Farmacêutica) — ficha do dossiê · data-base 02/10/2026 · doutrina v2.2 · mesmo motor e mercado do hall.

Premissas declaradas ANTES do veredito (doutrina §11.4, §6.3; 02 regra 4):
  · Janela 2017–2025 (9 exercícios): o 1º DFP com DRE na CVM é o de 2017 (registro pré-IPO; IPO em abr/2021). É o máximo
    disponível, não uma janela escolhida. Margem EBIT de 26–33% até 2022 e 18–24% de 2023 em diante; a mediana de 5 anos
    (2021–25) fica ~10% abaixo da de 9 — abaixo do limite de 25% do §11.4, então sem janela pós-quebra.
  · Perfil "servicos" (farma de marca/hospitalar, não commodity): capex de manutenção pelo Greenwald com Δreceita real.
  · "Outras" líquidas (3.04.04 + 3.04.05), como HYPE3 no lote 4: 2023 traz +R$ 118 mi em outras que a bruta trataria pela metade.
  · Alíquota: mediana de 5 anos de −IR/LAIR entre 15% e 34% (default do motor; ~24%).
  · Kd = rf nominal + 1,5 p.p. (o mesmo spread da HYPE3); g real perpétuo de 1% no cenário base.
  · Ações: composição do capital do ITR de jun/2026 (CVM), sem tesouraria — já depois da bonificação de 30% (data-com
    05/01/2026, B3). Proventos da B3 divididos por 1,30 antes dessa data (dossie/base.py).
  · Defasagem do provento: medida nas datas de pagamento da StatusInvest (fonte C usada só para datas; a B3 não publica
    a data de pagamento na API usada) — o JCP da Blau é declarado no trimestre e pago no ano seguinte.
  · Qualitativo: NUNCA digitado — vem de `notas.py` sobre a evidência (02 v4, regra 11) pelo `gerar.py`.
"""
from __future__ import annotations

from dossie import base
from motor_nao_financeiras import Industrial

TK = "BLAU3"
ANOS = [str(a) for a in range(2017, 2026)]
RAZAO_JANELA = ("1º DFP com DRE na CVM é 2017 (registro pré-IPO; IPO abr/2021): janela = o máximo disponível "
                "(02 regra 4), não uma quebra estrutural")


def empresa(qualitativo: dict | None = None, desconto_controlador: dict | None = None) -> Industrial:
    base.carregar(TK)
    return Industrial(
        TK, "Blau Farmacêutica", "servicos", preco=base.preco(TK), n_acoes=base.acoes_itr(TK),
        anos_ciclo=ANOS, anos_outras=ANOS, janela_razao=RAZAO_JANELA, outras_liquidas=True,
        spread_kd=0.015, g_real=0.01, jcp_share=base.jcp_share(TK), pl_hist=base.pl_hist(TK),
        defasagem_meses=base.defasagem(TK),
        defasagem_fonte="datas de pagamento da StatusInvest (C, só datas), média ponderada pelo valor, data-com 2016–25",
        desconto_controlador=desconto_controlador or {"tipo": "zero", "razao": "pendente: D3 do dossiê (FRE 2026)"},
        qualitativo=qualitativo or {},
    )
