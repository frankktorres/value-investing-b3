"""Camada 5 — sanidade econômica do universo e contraste com screens acadêmicos (docs/VALIDACAO.md §1).

Só relata e não muda palavra. Duas coisas bloqueiam (`bloqueantes`): número não finito no que vira palavra, e Ke nominal
acima do teto pré-registrado (30%, PRE-REGISTRO-v3 §3), salvo se o alarme já for conhecido e ligado a uma hipótese
(`CONHECIDOS`). A lista de conhecidos é uma catraca: só pode encolher.
Os screens (Piotroski F, Altman Z'' de emergentes, Beneish M, accruals de Sloan, Greenblatt EBIT/EV + ROC) vêm do motor
de não financeiras. Viram bandeira vermelha só em palavra de compra; a implementação independente deles é da Fase 4.
"""
from __future__ import annotations

import importlib
import json
import math
import pathlib
import statistics

AQUI = pathlib.Path(__file__).resolve().parent
FERRAMENTAS = AQUI.parent
HALL = FERRAMENTAS / "painel" / "web" / "dados" / "hall.json"
LOTES = ("lote1_bancos", "lote2_energia", "lote3_agro", "lote4_saude_telecom", "lote5_petroleo", "lote6_quimica")
KE_TETO = 0.30
COMPRA = ("BARATA", "RADAR")
PIOTROSKI_FRACO = 3            # F ≤ 3 (Piotroski 2000, JAR 38)
BENEISH_LIMIAR = -1.78         # M > −1,78 = provável manipulador (Beneish 1999, FAJ 55(5))
# alarme de Ke conhecido na baseline de 22/10/2026, com a hipótese que o explica; sai daqui quando a Fase 6 corrigir
CONHECIDOS = {"KLBN11": "H2", "SUZB3": "H2", "SLCE3": "H2", "SMTO3": "H2"}


def empresas() -> dict:
    out = {}
    for m in LOTES:
        for e in importlib.import_module(m).EMPRESAS:
            out[e.ticker] = e
    return out


def precos_hall() -> dict[str, float]:
    if not HALL.is_file():
        return {}
    return {e["tk"]: e["preco_hoje"] for e in json.loads(HALL.read_text(encoding="utf-8"))["empresas"] if e.get("preco_hoje")}


def _finito(x) -> bool:
    return isinstance(x, (int, float)) and math.isfinite(x)


def avaliar_universo(mk=None) -> list[dict]:
    """Uma linha por ticker dos lotes: o que o motor diz e os números de sanidade. P/C ao preço do hall (como a tela)."""
    import mercado
    import motor_financeiras as F
    import motor_nao_financeiras as M
    mk = mk or mercado.vigente()
    precos = precos_hall()
    linhas = []
    for tk, e in sorted(empresas().items()):
        fin = isinstance(e, F.Financeira)
        try:
            r = (F if fin else M).avaliar(e, mk)
        except Exception as ex:          # erro explícito do motor é NÃO CONCLUSIVO legítimo, não falha do oráculo
            linhas.append(dict(ticker=tk, erro=f"{type(ex).__name__}: {ex}"[:160]))
            continue
        central = r.get("central")
        preco = precos.get(tk, e.preco)
        ke_nom = r.get("ke") if fin else r.get("ke_nom_emp")
        ke_nom = float(ke_nom) if ke_nom is not None else None
        anc = r.get("ancoras") or {}
        linha = dict(
            ticker=tk, financeira=fin, palavra=r.get("palavra"), central=_num(central), preco=preco,
            pc=preco / central if _finito(central) and central > 0 else None,
            ke_nom=ke_nom, ke_real=_num(r.get("ke_real_emp")) if not fin else (1 + ke_nom) / (1 + mk.pi) - 1 if ke_nom else None,
            ke_implicito=_num(r.get("ke_implicito")), dispersao=_num(r.get("dispersao")),
            nao_finitos=[k for k, v in [("central", central), ("pc", r.get("pc"))] + [(f"anc:{k}", v) for k, v in anc.items()]
                         if isinstance(v, float) and not math.isfinite(v) and not (k == "pc" and v == math.inf)],
            lpa_norm=_num(r.get("lpa_norm")),
        )
        if not fin:
            linha.update(roic=_num(r.get("roic")), roic_filtro=_num(r.get("roic_filtro")), wacc=_num(r.get("wacc")),
                         roic_anos_acima=r.get("roic_anos_acima"), roic_serie=r.get("roic_serie"), roic_anos_total=r.get("roic_anos_total"), g_real=e.g_real,
                         piotroski=r.get("piotroski"), altman=_num(r.get("altman")), altman_zona=r.get("altman_zona"),
                         beneish=_num(r.get("beneish")), sloan=_num(r.get("sloan")), ey=_num(r.get("ey")), roc=_num(r.get("roc")))
        linhas.append(linha)
    return linhas


def _num(x):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return None
    return x


def _compounder(l: dict) -> bool:
    """ROIC alto e estável (PRE-REGISTRO-v3, emenda 1): mediana do ROIC real anual do motor ≥ 10% e no máximo 2 anos < 5%,
    OU ROIC contábil atual ≥ 15%. A 2ª via existe porque a série anual é suspeita de subestimar (H6)."""
    s = [x for x in (l.get("roic_serie") or {}).values() if x is not None]
    estavel = len(s) >= 5 and statistics.median(s) >= 0.10 and sum(x < 0.05 for x in s) <= 2
    return estavel or (l.get("roic") or 0) >= 0.15


def checks(linhas: list[dict]) -> dict:
    """Bloqueantes, bandeiras e o resumo do universo."""
    ok = [l for l in linhas if "erro" not in l]
    bloq, band = [], []
    for l in ok:
        if l["nao_finitos"]:
            bloq.append(f"{l['ticker']}: não finito em {', '.join(l['nao_finitos'])}")
        if l["ke_nom"] is not None and l["ke_nom"] > KE_TETO:
            msg = f"{l['ticker']}: Ke nominal {l['ke_nom']:.1%} > teto {KE_TETO:.0%}"
            (band if l["ticker"] in CONHECIDOS else bloq).append(
                msg + (f" (conhecido, {CONHECIDOS[l['ticker']]})" if l["ticker"] in CONHECIDOS else ""))
        if l.get("palavra") in COMPRA and not l["financeira"]:
            if l.get("piotroski") is not None and l["piotroski"] <= PIOTROSKI_FRACO:
                band.append(f"{l['ticker']}: {l['palavra']} com Piotroski F = {l['piotroski']} (≤ 3)")
            if l.get("beneish") is not None and l["beneish"] > BENEISH_LIMIAR:
                band.append(f"{l['ticker']}: {l['palavra']} com Beneish M = {l['beneish']:.2f} (> −1,78)")
            if l.get("altman_zona") and "risco" in str(l["altman_zona"]).lower():
                band.append(f"{l['ticker']}: {l['palavra']} com Altman Z'' na zona de risco ({l['altman']:.2f})")
    for tk in CONHECIDOS:
        if not any(l["ticker"] == tk and l["ke_nom"] is not None and l["ke_nom"] > KE_TETO for l in ok):
            bloq.append(f"catraca: {tk} saiu do alarme de Ke; tire-o de CONHECIDOS no mesmo commit")
    pcs = sorted(l["pc"] for l in ok if l["pc"])
    q = statistics.quantiles(pcs, n=4) if len(pcs) >= 4 else [None] * 3
    compounders = [l for l in ok if not l["financeira"] and _compounder(l) and (l["pc"] or 0) > 2]
    resumo = dict(
        n=len(linhas), n_erro=len(linhas) - len(ok), pc_mediana=statistics.median(pcs) if pcs else None,
        pc_q1=q[0], pc_q3=q[2], acima_3x=sum(p > 3 for p in pcs),
        # o Ke implícito do motor é NOMINAL (busca em ke_nom), calculado ao preço do lote
        ke_gap_mediano=statistics.median([l["ke_nom"] - l["ke_implicito"] for l in ok
                                          if l["ke_nom"] is not None and l["ke_implicito"] is not None]) if ok else None,
        compounders_caros=[dict(ticker=l["ticker"], pc=round(l["pc"], 2), roic=l.get("roic"), roic_filtro=l.get("roic_filtro"),
                                wacc=l.get("wacc"), ke_real=l["ke_real"], ke_implicito=l["ke_implicito"], g_real=l.get("g_real"))
                           for l in compounders],
    )
    return dict(bloqueantes=bloq, bandeiras=band, resumo=resumo)
