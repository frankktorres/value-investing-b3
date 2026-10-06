"""Motor reduzido para não-financeira — três âncoras, cada uma lendo uma demonstração diferente.

  · EPV de meio de ciclo        DRE + BPP: receita real mediana da janela × margem EBIT mediana
                                (com ajuste de manutenção só penalizando) × (1 − t), capitalizada
                                ao WACC real; menos dívida líquida e não-controladores.
  · Owner Earnings capitalizado DFC: mediana de 5 anos de lucro + D&A − capex de manutenção −
                                ΔCG positivo − principal de arrendamento, ÷ (Ke real − g real).
  · Valor de reprodução         estoque: PL controlador + imobilizado reexpresso pela idade
                                média (IPCA público em T). A única SEM Ke no denominador — é o que
                                impede a dispersão ≈ 1 por construção e torna a sensibilidade ao
                                prêmio interpretável.

DCF fica fora: com g mecânico ele converge ao EPV e vira cópia (plano da Etapa 3, "âncoras com
ângulos realmente diferentes"). O perfil (cíclica/serviços) NÃO muda as fórmulas — §11.4 manda a
janela inteira para todos —; o teste de ciclicidade (max/min margem > 2,5) só registra se
discorda do perfil do FCA.

Tudo em R$ do ano de T (`Ano.real`), com o IPCA público em T. Capex de manutenção pelo método
Greenwald da doutrina (D9): capex − (imobilizado/receita do ano anterior) × Δreceita REAL positiva.
"""
from __future__ import annotations

import math

from ..config import PADRAO, Config
from ..mercado_bt import MercadoBT
from .. import inflacao_pit
from . import contas
from .base import Ano, Insumos, lucro_controlador, mediana
from .perfil import CICLICA


def _c(d: dict, k: str) -> float:
    x = d.get(k)
    return 0.0 if x is None or (isinstance(x, float) and math.isnan(x)) else float(x)


def aliquota(anos: tuple[Ano, ...], cfg: Config) -> float:
    """Mediana de −IR/LAIR nos 5 últimos anos com LAIR > 0, em [15%, 34%]; sem dado: fallback."""
    ts = [-a.c("ir") / a.c("lair") for a in anos[-5:] if a.c("lair") > 0]
    t = mediana(ts)
    return cfg.aliquota_efetiva_fallback if not math.isfinite(t) else min(max(t, 0.15), 0.34)


def capex_manutencao(anos: tuple[Ano, ...]) -> list[float | None]:
    """Greenwald por ano (R$ reais do ano de T); None no 1º ano (sem Δreceita)."""
    out: list[float | None] = [None]
    for ant, a in zip(anos, anos[1:]):
        rec_ant = ant.c("receita") * ant.real
        if rec_ant <= 0:
            out.append(None)
            continue
        cresc = max(a.c("receita") * a.real - rec_ant, 0.0)
        intens = ant.c("imobilizado") * ant.real / rec_ant
        capex = a.capex * a.real
        out.append(min(max(capex - intens * cresc, 0.0), capex))
    return out


def premissas(i: Insumos, cfg: Config = PADRAO) -> dict[str, float]:
    anos = i.anos
    rec = [a.c("receita") for a in anos]
    validos = [a for a, r in zip(anos, rec) if r > 0]
    # EBIT sem o excesso de 'outras receitas' acima da mediana da janela (§7, armadilha 1).
    med_outras = mediana(contas.outras(a.contas) / a.c("receita") for a in validos)
    med_outras = med_outras if math.isfinite(med_outras) else None
    margens = [contas.ebit_aj(a.contas, med_outras) / a.c("receita")
               for a in validos if "ebit" in a.contas]
    p: dict[str, float] = {
        "receita_meio": mediana(a.c("receita") * a.real for a in validos),
        "margem": mediana(margens),
        "da_rec": mediana(a.da / a.c("receita") for a in validos),
        "capex_rec": mediana(a.capex / a.c("receita") for a in validos),
        "aliquota": aliquota(anos, cfg),
    }
    p["ajuste_manut"] = (min(0.0, p["da_rec"] - p["capex_rec"])
                         if math.isfinite(p["da_rec"]) and math.isfinite(p["capex_rec"]) else 0.0)
    pos = [m for m in margens if math.isfinite(m)]
    ciclico_medido = bool(pos) and (min(pos) <= 0 or max(pos) / min(pos) > cfg.ciclicidade_razao_margem)
    p["ciclicidade_diverge"] = float(ciclico_medido != (i.perfil.perfil == CICLICA))

    # Owner Earnings: 5 últimos anos, reais
    manut = capex_manutencao(anos)
    oes = []
    for k in range(max(1, len(anos) - 5), len(anos)):
        a, ant = anos[k], anos[k - 1]
        if manut[k] is None:
            continue
        lucro = lucro_controlador(a.contas)
        if lucro is None:
            continue
        dcg = (contas.capital_giro(a.contas) * a.real - contas.capital_giro(ant.contas) * ant.real)
        oes.append(lucro * a.real + a.da * a.real - manut[k] - max(dcg, 0.0)
                   - a.arrendamento * a.real)
    p["owner_earnings"] = mediana(oes)
    return p


def ancoras(i: Insumos, mk: MercadoBT, preco: float, cfg: Config = PADRAO
            ) -> tuple[dict[str, float], dict]:
    """(âncoras R$ por papel, premissas). `preco` entra só no peso do equity no WACC."""
    p = premissas(i, cfg)
    nomes = cfg.ancoras_nao_financeira
    bal = i.balanco
    bruta, _, dl = contas.divida_liquida(bal)
    minor = _c(bal, "nao_controladores")
    t = p["aliquota"]

    # WACC nominal com E a mercado (R$ mil) e kd = rf nominal + spread; depois real.
    e = preco * i.papeis / 1000.0
    d = max(bruta, 0.0)
    kd = mk.rf_nom + cfg.spread_kd
    w = (mk.ke_nom * e + kd * (1 - t) * d) / (e + d) if e + d > 0 else mk.ke_nom
    w_real = (1 + w) / (1 + mk.pi) - 1
    p.update(wacc_nom=w, wacc_real=w_real)

    epv = math.nan
    if all(math.isfinite(p[k]) for k in ("receita_meio", "margem")) and w_real > 0:
        nopat = p["receita_meio"] * (p["margem"] + p["ajuste_manut"]) * (1 - t)
        p["nopat"] = nopat
        epv = i.por_acao(nopat / w_real - dl - minor)

    oe = math.nan
    if math.isfinite(p["owner_earnings"]) and mk.ke_real > cfg.g_real_oe:
        oe = i.por_acao(p["owner_earnings"] / (mk.ke_real - cfg.g_real_oe))

    reproducao = math.nan
    pl = bal.get("pl")
    if pl is not None and not (isinstance(pl, float) and math.isnan(pl)):
        imob = _c(bal, "imobilizado")
        ultimo = i.anos[-1]
        idade = inflacao_pit.idade_media(imob, ultimo.da)
        f = inflacao_pit.fator_idade(int(i.data_corte[:4]), idade, i.ledger.mes_ipca)
        p.update(idade_imobilizado=idade, fator_idade=f)
        reproducao = i.por_acao(float(pl) - minor + imob * (f - 1))
    return dict(zip(nomes, (epv, oe, reproducao))), p
