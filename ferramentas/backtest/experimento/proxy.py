"""Fatia 12 — erro de proxy: o motor reduzido representa a régua de hoje?

Roda o motor reduzido em `cfg.proxy_data` (05/10/2026) nos 41 do golden, com o MESMO mercado do
golden (rf 7,06%, π 6,46%) e o MESMO preço (pc × central), para que o erro medido seja só do
motor. Compara palavra e P/C.

PORTÃO (config.py, declarado antes de medir; mantido pelo Frank em 06/10/2026):
    palavra exata ou a ±1 nível em >= `proxy_concordancia_min` dos 41  E
    mediana de |ΔP/C| <= `proxy_delta_pc_max`.
Falhou -> o backtest PARA e reporta que o motor mecânico não representa a régua. Nunca
enriquecer o motor até passar: seria calibrar no único ponto onde a resposta é conhecida.

Regras de contagem, declaradas antes da 1ª rodada:
  · denominador = 41 sempre; papel excluído (holding, janela curta, sem ações, unit sem
    composição, evento sem fator, âncora indisponível) conta como ERRO e |ΔP/C| = ∞;
  · ±1 nível pela ordem BARATA < RADAR < JUSTA < CARA; NÃO CONCLUSIVO só acerta NÃO CONCLUSIVO;
  · |ΔP/C| com P/C infinito dos dois lados = 0; de um lado só = ∞.

Baselines impressos ao lado (decisão de 06/10/2026): 34 dos 41 são CARA, então "sempre CARA"
acerta ±1 em 38/41 — o critério de palavra quase não discrimina; quem discrimina é o ΔP/C. Também
o acerto nos 7 não-CARA e um central ingênuo (VPA controlador).

Trava anti-calibração: cada rodada vai para `dados/proxy_consultas.log` (append-only) com o hash
da config e o hash dos arquivos de `motor/`; o relatório imprime quantas consultas houve.
Mudança no motor depois da 1ª medição só com bug provado em teste SINTÉTICO.

Este é o único módulo do backtest autorizado a ler `golden.json` (test_isolamento.ISENTOS_GOLDEN).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path

from ..config import PADRAO, Config, hash_config
from ..mercado_bt import MercadoBT
from ..motor import base, regua
from ..motor.perfil import cd_cvm_do_cnpj
from ..motor.reduzido import Resultado, avaliar

RAIZ = Path(__file__).resolve().parent.parent
GOLDEN = RAIZ.parent / "tests" / "golden.json"
DADOS = RAIZ / "dados"
LOG = DADOS / "proxy_consultas.log"


# ------------------------------------------------------------------------- regras do portão
def comparar(g_palavra: str, g_pc: float, p_palavra: str | None, p_pc: float | None
             ) -> tuple[bool, bool, float]:
    """(exata, dentro de ±1 nível, |ΔP/C|). `p_palavra` None = papel excluído."""
    if p_palavra is None or p_pc is None:
        return False, False, math.inf
    exata = p_palavra == g_palavra
    um = exata or (g_palavra in regua.NIVEL and p_palavra in regua.NIVEL
                   and abs(regua.NIVEL[g_palavra] - regua.NIVEL[p_palavra]) <= 1)
    gi, pi_ = math.isinf(g_pc), math.isinf(p_pc)
    delta = 0.0 if (gi and pi_) else math.inf if (gi or pi_) else abs(p_pc - g_pc)
    return exata, um, delta


def portao(linhas: list[dict], cfg: Config = PADRAO) -> dict[str, object]:
    n = len(linhas)
    um = sum(l["um_nivel"] for l in linhas)
    exata = sum(l["exata"] for l in linhas)
    med = statistics.median(l["delta_pc"] for l in linhas) if linhas else math.inf
    conc = um / n if n else 0.0
    return {"n": n, "exata": exata, "um_nivel": um, "concordancia": conc,
            "mediana_delta_pc": med,
            "criterio_palavra": conc >= cfg.proxy_concordancia_min,
            "criterio_pc": med <= cfg.proxy_delta_pc_max,
            "passou": conc >= cfg.proxy_concordancia_min and med <= cfg.proxy_delta_pc_max}


def baselines(linhas: list[dict]) -> dict[str, object]:
    """O que acertaria um proxy sem informação — para ler o portão com a régua certa."""
    n = len(linhas)
    cara = [comparar(l["golden_palavra"], l["golden_pc"], regua.CARA, 1.0) for l in linhas]
    nao_cara = [l for l in linhas if l["golden_palavra"] != regua.CARA]
    ing = [comparar(l["golden_palavra"], l["golden_pc"], l.get("ingenuo_palavra"),
                    l.get("ingenuo_pc")) for l in linhas]
    avaliados = [l for l in linhas if l["proxy_dispersao"] is not None]
    nao_degenera = sum(l["proxy_dispersao"] > 1.0 + 1e-9 for l in avaliados)
    return {
        "sempre_cara_exata": sum(c[0] for c in cara), "sempre_cara_um_nivel": sum(c[1] for c in cara),
        "nao_cara_n": len(nao_cara),
        "nao_cara_exata": sum(l["exata"] for l in nao_cara),
        "nao_cara_um_nivel": sum(l["um_nivel"] for l in nao_cara),
        "ingenuo_vpa_um_nivel": sum(c[1] for c in ing),
        "ingenuo_vpa_mediana_delta_pc": statistics.median(c[2] for c in ing) if n else math.inf,
        "dispersao_maior_que_1": f"{nao_degenera}/{len(avaliados)}",
        "nao_degeneracao_ok": bool(avaliados) and nao_degenera / len(avaliados) >= 0.90,
    }


# ------------------------------------------------------------------------- execução
def carregar_golden() -> dict:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))["tickers"]


def hash_motor() -> str:
    h = hashlib.sha256()
    for f in sorted((RAIZ / "motor").glob("*.py")):
        h.update(f.name.encode())
        h.update(f.read_bytes())
    return h.hexdigest()[:16]


def _precos_e_eventos(tickers: list[str], cfg: Config):
    """Preços e eventos em ações só dos papéis do golden (a tabela inteira não cabe na RAM)."""
    from .. import cotahist
    from ..precos import eventos as ev_mod, espinha, ibov as ibov_mod, proventos_b3
    precos = espinha.precos_acoes()
    precos = precos[precos["ticker"].isin(tickers)].copy()
    ev = ev_mod.construir(precos, ibov_mod.serie(), proventos_b3.carregar_suplemento(), cfg=cfg)
    return precos, cotahist.calendario(), ev


def linha(tk: str, g: dict, r: Resultado | None, motivo: str, ingenuo_vpa: float | None,
          preco: float, cfg: Config) -> dict:
    v = r.veredito if r else None
    p_pal = v.palavra if v else None
    p_pc = v.pc if v else None
    exata, um, delta = comparar(g["palavra"], g["pc"], p_pal, p_pc)
    ing_pc = preco / ingenuo_vpa if ingenuo_vpa and ingenuo_vpa > 0 else None
    return {
        "ticker": tk, "lote": g["lote"], "golden_palavra": g["palavra"], "golden_pc": g["pc"],
        "golden_central": g["central"], "golden_ancoras": g["ancoras"], "preco": preco,
        "perfil": r.insumos.perfil.perfil if r else "", "setor": r.insumos.perfil.setor if r else "",
        "motivo_exclusao": motivo,
        "proxy_ancoras": r.ancoras if r else {}, "proxy_central": v.central if v else None,
        "proxy_pc": p_pc, "proxy_palavra": p_pal, "proxy_dispersao": v.dispersao if v else None,
        "exata": exata, "um_nivel": um, "delta_pc": delta,
        "ingenuo_pc": ing_pc,
        "ingenuo_palavra": regua.palavra_da_escala(ing_pc, cfg) if ing_pc else None,
        "premissas": {k: x for k, x in (r.premissas.items() if r else ()) if isinstance(x, float)},
        "procedencia": r.insumos.procedencia() if r else {},
    }


def rodar(cfg: Config = PADRAO) -> list[dict]:
    from ..ledger.identidade import _cnpj_do_ticker_em, mapa_ticker_cnpj
    golden = carregar_golden()
    T = cfg.proxy_data
    mk = MercadoBT(T, cfg.proxy_rf_real, cfg.proxy_pi, 0.05, fonte="mercado do golden")
    cnpjs = _cnpj_do_ticker_em(mapa_ticker_cnpj(), T)
    precos, cal, eventos = _precos_e_eventos(sorted(golden), cfg)
    out = []
    for tk in sorted(golden):
        g = golden[tk]
        # Preço = o do golden (pc × central). Com central <= 0 o golden não guarda preço (pc = ∞):
        # aí vale o PREULT do COTAHIST no último pregão <= T, marcado na linha.
        if math.isfinite(g["pc"]):
            preco, fonte_preco = g["pc"] * g["central"], "golden"
        else:
            from ..precos.retorno import preco_de_corte
            preco, dia = preco_de_corte(precos, tk, T, cal)
            fonte_preco = f"cotahist {dia}"
        cnpj = cnpjs[tk]
        cd = cd_cvm_do_cnpj(cnpj) if cnpj else None
        if cd is None:
            out.append(linha(tk, g, None, "sem_identidade", None, preco, cfg))
            continue
        i = base.montar(cd, tk, cnpj, T, eventos, cfg)
        r = avaliar(i, mk, preco, cfg) if math.isfinite(preco) else Resultado(
            i, motivo_exclusao="preco_golden_indefinido")
        vpa = None
        if not i.excluido:
            pl = i.balanco.get("pl")
            nc = i.balanco.get("nao_controladores") or 0.0
            if pl is not None and math.isfinite(pl):
                vpa = i.por_acao(pl - (nc if math.isfinite(nc) else 0.0))
        out.append(linha(tk, g, r, r.motivo_exclusao, vpa, preco, cfg) | {"fonte_preco": fonte_preco})
    return out


def _f(x, nd=2) -> str:
    if x is None:
        return "—"
    if isinstance(x, float) and math.isinf(x):
        return "∞"
    return f"{x:.{nd}f}"


def relatorio(linhas: list[dict], cfg: Config = PADRAO, consultas: int | None = None) -> str:
    pt, bl = portao(linhas, cfg), baselines(linhas)
    s = [f"PROXY em {cfg.proxy_data} — config {hash_config(cfg)} · motor {hash_motor()}"
         + (f" · consulta nº {consultas}" if consultas else ""), ""]
    s.append(f"{'ticker':8} {'perfil':10} {'golden':15} {'pc_g':>6}  {'proxy':15} {'pc_p':>6} "
             f"{'|Δ|':>6} {'disp':>5}  motivo")
    for l in linhas:
        s.append(f"{l['ticker']:8} {l['perfil']:10} {l['golden_palavra']:15} {_f(l['golden_pc']):>6}  "
                 f"{(l['proxy_palavra'] or '—'):15} {_f(l['proxy_pc']):>6} {_f(l['delta_pc']):>6} "
                 f"{_f(l['proxy_dispersao']):>5}  {l['motivo_exclusao']}")
    s += ["",
          f"palavra exata: {pt['exata']}/{pt['n']} · ±1 nível: {pt['um_nivel']}/{pt['n']} "
          f"= {pt['concordancia']:.1%} (mín. {cfg.proxy_concordancia_min:.0%}) "
          f"-> {'ok' if pt['criterio_palavra'] else 'FALHOU'}",
          f"mediana |ΔP/C|: {_f(pt['mediana_delta_pc'], 3)} (máx. {cfg.proxy_delta_pc_max}) "
          f"-> {'ok' if pt['criterio_pc'] else 'FALHOU'}",
          f"PORTÃO: {'PASSOU' if pt['passou'] else 'FALHOU — PARAR: o motor reduzido não representa a régua'}",
          "",
          "baselines (sem informação):",
          f"  sempre CARA: exata {bl['sempre_cara_exata']}/{pt['n']}, ±1 {bl['sempre_cara_um_nivel']}/{pt['n']}",
          f"  nos {bl['nao_cara_n']} não-CARA do golden: exata {bl['nao_cara_exata']}, ±1 {bl['nao_cara_um_nivel']}",
          f"  central ingênuo = VPA controlador: ±1 {bl['ingenuo_vpa_um_nivel']}/{pt['n']}, "
          f"mediana |ΔP/C| {_f(bl['ingenuo_vpa_mediana_delta_pc'], 3)}",
          f"  não-degeneração (dispersão > 1,0): {bl['dispersao_maior_que_1']} "
          f"-> {'ok' if bl['nao_degeneracao_ok'] else 'FALHOU'} (alvo 90%)"]
    return "\n".join(s)


def _registrar(pt: dict, cfg: Config) -> int:
    DADOS.mkdir(exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"quando": dt.datetime.now().isoformat(timespec="seconds"),
                            "config": hash_config(cfg), "motor": hash_motor(),
                            "passou": pt["passou"], "concordancia": pt["concordancia"],
                            "mediana_delta_pc": pt["mediana_delta_pc"]}) + "\n")
    return sum(1 for _ in LOG.open(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    argparse.ArgumentParser(description="Erro de proxy do motor reduzido (fatia 12)").parse_args(argv)
    cfg = PADRAO
    linhas = rodar(cfg)
    pt = portao(linhas, cfg)
    n = _registrar(pt, cfg)
    (DADOS / f"proxy_{cfg.proxy_data}.json").write_text(
        json.dumps({"config": hash_config(cfg), "motor": hash_motor(), "portao": pt,
                    "baselines": baselines(linhas), "linhas": linhas},
                   ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")           # console cp1252 não tem Δ nem ∞
    print(relatorio(linhas, cfg, n))
    return 0 if pt["passou"] else 2


def reimprimir(cfg: Config = PADRAO) -> str:
    """Relatório a partir do JSON gravado — reler NÃO é nova consulta ao golden."""
    j = json.loads((DADOS / f"proxy_{cfg.proxy_data}.json").read_text(encoding="utf-8"))
    for l in j["linhas"]:
        for k in ("golden_pc", "proxy_pc", "delta_pc", "proxy_dispersao", "ingenuo_pc"):
            if isinstance(l.get(k), str):
                l[k] = float(l[k])
    n = sum(1 for _ in LOG.open(encoding="utf-8"))
    return relatorio(j["linhas"], cfg, n)


if __name__ == "__main__":
    sys.exit(main())
