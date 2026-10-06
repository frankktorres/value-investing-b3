"""Motor reduzido para banco, seguradora e utility — três âncoras que leem coisas diferentes.

  · P/VP justificado  = VPA × (ROE_lp − g)/(Ke − g)                         (estoque × retorno)
  · DDM 2 estágios    = ROE convergindo do último ITR anualizado ao ROE_lp em 5 anos, terminal
                        P/VP justificado (só é ângulo distinto quando ROE_inicio ≠ ROE_lp — que é
                        quando importa)
  · Lucro normalizado = mediana do lucro controlador REAL da janela / ações / Ke real — o único
                        que não usa o PL.

O que hoje é digitado no lote1_bancos.py sai do ledger: `roe_lp` = mediana da janela,
`roe_inicio` = ITR, `payout` = 1 − retenção observada (dividendos + JCP PAGOS na DFC ÷ lucro,
mediana, recortada em [0, 1]). Ke nominal e g_teto vêm do `MercadoBT` — nunca de `Mercado`, que
fixa o prêmio em 5 p.p.

`pvp_justificado`, `g_de` e `ddm_dois_estagios` são CÓPIAS das de motor_financeiras.py, que não
pode ser importado aqui (puxa `defasagem`). `tests/test_reduzido.py` exige resultado idêntico ao
original.
"""
from __future__ import annotations

import math

from ..config import PADRAO, Config
from ..mercado_bt import MercadoBT
from .base import Insumos, itr_lucro_anualizado, lucro_controlador, mediana


def pvp_justificado(roe: float, g: float, ke: float) -> float:
    return (roe - g) / (ke - g)


def g_de(roe: float, payout: float, g_teto: float) -> float:
    """g perpétuo nominal = ROE × retenção, com teto π + PIB real de LP (motor_financeiras.g_de)."""
    return min(roe * (1 - payout), g_teto)


def ddm_dois_estagios(vpa: float, roe_inicio: float, roe_lp: float, payout: float, ke: float,
                      g_teto: float, anos: int = 5) -> float:
    """Cópia de motor_financeiras.ddm_dois_estagios, com os campos como argumento."""
    g = g_de(roe_lp, payout, g_teto)
    vp = 0.0
    for t in range(1, anos + 1):
        roe_t = roe_inicio + (roe_lp - roe_inicio) * t / anos
        lpa = roe_t * vpa
        d = lpa * payout
        vpa = vpa + lpa - d
        vp += d / (1 + ke) ** t
    terminal = vpa * pvp_justificado(roe_lp, g, ke)
    return vp + terminal / (1 + ke) ** anos


def _pl_controlador(c: dict) -> float | None:
    pl = c.get("pl")
    if pl is None or (isinstance(pl, float) and math.isnan(pl)):
        return None
    nc = c.get("nao_controladores") or 0.0
    return float(pl) - (0.0 if isinstance(nc, float) and math.isnan(nc) else float(nc))


def _lucro_controlador(a) -> float | None:
    return lucro_controlador(a.contas)


def premissas(i: Insumos) -> dict[str, float]:
    """ROE por ano (sobre o PL controlador médio), roe_lp, roe_inicio, payout, VPA, lucro real."""
    roes, payouts, lucros_reais = [], [], []
    pl_ant = None
    for a in i.anos:
        pl = _pl_controlador(a.contas)
        lc = _lucro_controlador(a)
        if pl is not None and lc is not None:
            base = (pl + pl_ant) / 2 if pl_ant is not None else pl
            if base > 0:
                roes.append(lc / base)
            if lc > 0:
                payouts.append(min(max(a.dividendos / lc, 0.0), 1.0))
        if lc is not None:
            lucros_reais.append(lc * a.real)
        pl_ant = pl
    roe_lp = mediana(roes)
    pl_bal = _pl_controlador(i.balanco)
    lc_itr = itr_lucro_anualizado(i)
    roe_inicio = (lc_itr / pl_bal) if (lc_itr is not None and pl_bal and pl_bal > 0) else (
        roes[-1] if roes else math.nan)
    return {"roe_lp": roe_lp, "roe_inicio": roe_inicio,
            "payout": mediana(payouts) if payouts else 0.0,
            "pl_controlador": pl_bal if pl_bal is not None else math.nan,
            "vpa": i.por_acao(pl_bal) if pl_bal is not None else math.nan,
            "lucro_real_mediano": mediana(lucros_reais), "n_roe": float(len(roes))}


def ancoras(i: Insumos, mk: MercadoBT, cfg: Config = PADRAO) -> tuple[dict[str, float], dict]:
    """(âncoras R$ por papel, premissas). Âncora não calculável sai como NaN -> o proxy a vê."""
    p = premissas(i)
    ke, g_teto = mk.ke_nom, mk.g_teto
    nomes = cfg.ancoras_financeira
    # Banco cujo exercício veio sem lucro some da janela em silêncio (BEES3 2022-23: n_roe 6 de
    # 10). Exige janela mínima de ROE e o lucro do último exercício.
    sem_base = p["n_roe"] < cfg.janela_min or _lucro_controlador(i.anos[-1]) is None
    if sem_base or not all(math.isfinite(p[k]) for k in ("roe_lp", "roe_inicio", "vpa")):
        return {n: math.nan for n in nomes}, p
    g = g_de(p["roe_lp"], p["payout"], g_teto)
    p["g"] = g
    pvp = p["vpa"] * pvp_justificado(p["roe_lp"], g, ke)
    ddm = ddm_dois_estagios(p["vpa"], p["roe_inicio"], p["roe_lp"], p["payout"], ke, g_teto)
    lucro_norm = i.por_acao(p["lucro_real_mediano"]) / mk.ke_real
    return dict(zip(nomes, (pvp, ddm, lucro_norm))), p
