"""HYPE3 (Hypera Pharma) — ficha do dossiê · data-base 02/10/2026 · doutrina v2.2 · mesmo motor e mercado do hall.

HYPE3 já está no hall (Lote 4): as demonstrações vêm da MESMA série da CVM do hall (`cvm_series.json`, DFP 2016–25 + ITR
2T26). O dossiê troca, só em memória e só dentro do `gerar.calcular` (`base.isolado`), os proventos da StatusInvest pelos
da B3 (fonte A) — o golden de 41 não vê a troca.

Premissas declaradas ANTES do veredito (doutrina §11.4, §6.3; 02 regra 4):
  · Janela 2016–2025 (10 exercícios, a da doutrina; a mesma do hall). As aquisições de 2020–22 (Buscopan, Takeda, Sanofi)
    mudaram o porte, não o modelo (farma de marca, MIP + prescrição + similares/genéricos): sem janela pós-quebra.
  · Perfil "servicos" (farma de marca, não commodity): capex de manutenção pelo Greenwald com Δreceita real (como BLAU3).
  · "Outras" líquidas (3.04.04 + 3.04.05), como no hall.
  · Receita de base = default do motor (média de 2023, 2024, 2025 e 12m até jun/2026): 2024–25 têm a receita deprimida
    pela redução do estoque no canal (otimização de capital de giro, FR 18/10/2024), e o 12m já mostra a volta; a média
    não escolhe nenhum dos dois extremos.
  · Alíquota (doutrina §2, v2.3): crédito de IR COM PRAZO (ágio amortizável até 2030; subvenção de ICMS até a reforma, prazo
    não conferido na fonte) → efetiva até 2030 e 34% depois, na perpetuidade e no WACC; a declaração é a do hall (`fiscal.py`).
    Até a v2.2 (dossiê de 02/10): piso de 15% para sempre.
  · Kd = rf nominal + 1,5 p.p.; g real 1% (só vale se ROIC > WACC) — os mesmos do hall.
  · Ações: composição do capital do ITR de jun/2026 (CVM), sem tesouraria = 704,0 mi, já depois do aumento de capital
    privado de 70,6 mi de ações a R$ 21,25 (homologado em 31/03/2026, IPE) — o balanço de jun/2026 já tem o caixa dele.
  · P/L histórico de fim de exercício com fonte A (`base.pl_hist`: COTAHIST × ações do DFP ÷ lucro do controlador).
  · Defasagem do provento MEDIDA (datas da StatusInvest, C só para datas), como BLAU3 e CMIN3 — o hall usa 18 meses
    declarados (divergência registrada no dossiê).
  · Qualitativo: NUNCA digitado — vem de `notas.py` sobre a evidência (02 v4, regra 11) pelo `gerar.py`.
"""
from __future__ import annotations

from dossie import base
from fiscal import ALIQUOTA_FASE
from motor_nao_financeiras import ANOS as ANOS_HALL, Industrial

TK = "HYPE3"
ANOS = list(ANOS_HALL)          # 2016–2025


def empresa(qualitativo: dict | None = None, desconto_controlador: dict | None = None, **sobrepor) -> Industrial:
    base.carregar(TK)
    kw = dict(
        outras_liquidas=True, aliquota_fase=ALIQUOTA_FASE[TK], spread_kd=0.015, g_real=0.01,
        jcp_share=base.jcp_share(TK), pl_hist=base.pl_hist(TK),
        defasagem_meses=base.defasagem(TK),
        defasagem_fonte="datas de pagamento da StatusInvest (C, só datas), média ponderada pelo valor; JCP declarado no "
                        "trimestre e pago até o fim do ano seguinte",
        desconto_controlador=desconto_controlador or {"tipo": "zero", "razao": "pendente: D3 do dossiê"},
        qualitativo=qualitativo or {},
    )
    kw.update(sobrepor)
    return Industrial(TK, "Hypera Pharma", "servicos", preco=base.preco(TK), n_acoes=base.acoes_itr(TK), **kw)
