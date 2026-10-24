"""Motor-sombra (oráculo, Fase 4, camada 3): FCFF/FCFE e DDM mínimos, no estilo Damodaran, reescritos a partir da especificação.

Independência PARCIAL (revisor de 23/10): o código é outro, mas segue a mesma especificação do motor (trava de g pelo menor ROIC,
freio da AUD-34, pesos 25/50/25 com piso 0, DDM com ROE convergindo em 5 anos e terminal pelo P/VP justificado). Pega erro de
encanamento (ponte, mediana, desconto, ordem dos cenários), não erro de doutrina; o terminal do 2 estágios reinveste pelo ROIC do
1º estágio, sem convergir ao WACC como em Damodaran — escolha do motor repetida aqui, portanto não conferida.

Não importa `motor_nao_financeiras` nem `motor_financeiras` (nem nada que os importe): recebe números puros e devolve números.
Quem junta os insumos é `oraculo/sombra_rodar.py`; aqui só há conta, para que um erro de composição no motor (ponte firma →
acionista, trava de g, reinvestimento, 2 estágios, ponderação dos cenários, desconto do controlador, mediana) apareça como
divergência entre os dois.

Fórmulas (Damodaran, *Investment Valuation* — FCFF de crescimento estável e DDM; edição e capítulos **a conferir**, princípio 5):
  FCFF₁ = NOPAT × (1 + g) × (1 − g ÷ ROIC)          (reinvestimento = g ÷ ROIC, real com real)
  valor da firma = FCFF₁ ÷ (WACC − g)                 (real)
  EPV = NOPAT ÷ WACC                                   (g = 0, Greenwald)
  FCFE ao acionista = fluxo normalizado ÷ (Ke − g)    (real)
  P/VP justificado = (ROE − g) ÷ (Ke − g); g = ROE × (1 − payout) com teto
  DDM 2 estágios: ROE converge linear em 5 anos; terminal = VPA₅ × P/VP justificado.
Limites declarados: o crédito fiscal com prazo (VP à parte no motor) e o freio do declínio não entram — onde existem, a
divergência é explicada pelo relatório; SOTP e contrato finito ficam fora.
"""
from __future__ import annotations

from statistics import median

TOLERANCIA = 0.02     # PRE-REGISTRO-v3 §3: |Δcentral| ≤ 2% entre motor-sombra e motor, mesmos insumos


def real(x_nom: float, pi: float) -> float:
    return (1 + x_nom) / (1 + pi) - 1


def fcff_estavel(nopat: float, g: float, roic_real: float | None, wacc_real: float) -> float:
    """Valor da firma em crescimento estável (real). Sem ROIC (capital ≤ 0, ou declínio que não libera capital) o
    reinvestimento é zero e o g continua no fluxo."""
    reinv = g / roic_real if (roic_real and g) else 0.0
    return nopat * (1 + g) * (1 - reinv) / (wacc_real - g)


def fcff_dois_estagios(nopat: float, g1: float, anos: int, g: float, roic_real: float, wacc_real: float) -> float:
    vp, x = 0.0, nopat
    for t in range(1, anos + 1):
        x *= 1 + g1
        vp += x * (1 - (g1 / roic_real if (g1 > 0 and roic_real) else 0.0)) / (1 + wacc_real) ** t
    term = x * (1 + g) * (1 - (g / roic_real if (g and roic_real) else 0.0)) / (wacc_real - g)
    return vp + term / (1 + wacc_real) ** anos


def industrial(x: dict) -> dict:
    """Âncoras e central de uma não financeira. `x` = insumos puros (ver `sombra_rodar.insumos_industrial`)."""
    pi, w_nom = x["pi"], x["wacc_nom"]
    w_real, ke_real = real(w_nom, pi), real(x["ke_nom"], pi)
    ponte = x["dl"] + x["minor"]

    def acionista(firma):
        return (firma - ponte) / x["n"]

    def dcf(m):
        nop = x["receita_meio"] * (m + x["ajuste_manut"]) * (1 - x["t"])
        roic = nop / x["cap_inv"] if x["cap_inv"] > 0 else None
        roic_rep = nop / x["cap_rep"] if x["cap_rep"] > 0 else roic
        cria = roic is not None and min(roic, roic_rep) > w_nom      # Greenwald: só cresce com retorno acima do custo
        g = x["g"] if (x["g"] <= 0 or cria) else 0.0
        rr = real(roic, pi) if roic is not None else None
        if g < 0 and (not cria or x.get("declinio_sem_liberacao")):
            rr = None                                                  # declínio sem liberar capital (AUD-34)
        if x.get("g1") is not None:
            return acionista(fcff_dois_estagios(nop, x["g1"] if cria else 0.0, x["anos_g1"], g, rr, w_real))
        return acionista(fcff_estavel(nop, g, rr, w_real))

    cen = {k: dcf(x[k]) for k in ("m25", "m50", "m75")}
    dcf_pond = 0.25 * max(cen["m25"], 0) + 0.5 * max(cen["m50"], 0) + 0.25 * max(cen["m75"], 0)
    nopat = x["receita_meio"] * (x["m50"] + x["ajuste_manut"]) * (1 - x["t"])
    epv = acionista(nopat / w_real)
    anc = {}
    if x["perfil"] == "ciclica":
        anc["EPV"] = epv
        anc["DCF"] = dcf_pond
        if x.get("reproducao") is not None:
            anc["reprodução"] = x["reproducao"]
    else:
        anc["DCF"] = dcf_pond
        anc["EPV"] = epv
        if x.get("oe_norm") and ke_real > x["g"]:
            anc["FCFE (OE)"] = (x["oe_norm"] / (ke_real - x["g"]) - x["passivos_acionista"]) / x["n"]
    return _central(anc, x["desc"])


def financeira(x: dict) -> dict:
    """P/VP justificado + DDM 2 estágios (Damodaran, cap. 13), com o desconto do controlador fixo ou por cenário."""
    def ancoras(roe_lp):
        g = min(roe_lp * (1 - x["payout"]), x["g_teto"])
        pvp = (roe_lp - g) / (x["ke_nom"] - g)
        vpa, vp = x["vpa"], 0.0
        for t in range(1, 6):
            roe_t = x["roe_inicio"] + (roe_lp - x["roe_inicio"]) * t / 5
            lpa = roe_t * vpa
            d = lpa * x["payout"]
            vpa += lpa - d
            vp += d / (1 + x["ke_nom"]) ** t
        ddm = vp + vpa * pvp / (1 + x["ke_nom"]) ** 5
        return {"P/VP justificado": x["vpa"] * pvp, "DDM 2 estágios": ddm}
    base = ancoras(x["roe_lp"])
    dc = x["dc"]
    if dc.get("tipo") == "cenarios":
        inter = ancoras(x["roe_lp"] - dc["delta_roe"])
        anc = {k: (1 - dc["peso"]) * base[k] + dc["peso"] * inter[k] for k in base}
        return _central(anc, 0.0)
    return _central(base, dc.get("pct", 0.0) if dc.get("tipo") == "fixo" else 0.0)


def _central(anc: dict, desc: float) -> dict:
    anc = {k: (v * (1 - desc) if v > 0 else v) for k, v in anc.items()}
    return {"ancoras": anc, "central": median(anc.values())}


def divergencia(sombra: float, motor: float) -> float | None:
    """Δ relativo; os dois zero (central nulo nos dois) = 0; motor zero e sombra não = indefinido (None)."""
    if motor == 0:
        return 0.0 if sombra == 0 else None
    return sombra / motor - 1
