"""Relatório do hold-out B36 (pré-registro v3, emenda 8), gerado só dos JSONs. Uso, de `ferramentas/`:

    python -m holdout_b36.relatorio            # grava docs/holdout/B36-2026-11.md

Lê `cadastro.json` (tempo da coleta), `tempos_insumos.json` (relógio e chamadas do subagente do protocolo),
`resultados/<TK>.json` (palavra, P/C, Ke, classes dos insumos) e `tests/golden.json` (P/C do hall, só para comparar).
Não roda motor nem executor; não escreve nada além do relatório.
"""
from __future__ import annotations

import json
import pathlib
import statistics as st
import sys

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
SAIDA = RAIZ / "docs" / "holdout" / "B36-2026-11.md"
GOLDEN = AQUI.parent / "tests" / "golden.json"

# Critério de "passou" da emenda 8 (linha 5 retirada antes de rodar)
LIM = dict(rodam=16, nc=6, ke30=2, absurdo=2, vazio_pct=50.0, minutos=20.0)
DISPERSAO = 1.8

# Previsões da emenda 8, escritas antes de rodar (texto literal + teste do observado)
PREVISTO = {
    "AZZA3": "NÃO CONCLUSIVO", "NATU3": "valor absurdo", "MBRF3": "NÃO CONCLUSIVO (Ke > 30%)", "EMBJ3": "erro",
    "CSAN3": "NÃO CONCLUSIVO", "GOAU4": "roda, sem absurdo", "IGTI11": "valor absurdo",
    "MOVI3": "NÃO CONCLUSIVO (Ke > 30%)", "ENEV3": "valor absurdo (P/C > 5)", "BEEF3": "NÃO CONCLUSIVO (Ke > 30%)",
    "RAIL3": "roda", "BPAC11": "roda (motor de banco)", "ENGI11": "roda (regulado)", "MRVE3": "roda",
    "RADL3": "roda", "TEND3": "roda", "CSNA3": "roda", "USIM5": "roda", "SMFT3": "roda", "EQTL3": "roda",
}


def absurdo(r: dict) -> bool:
    c, pc = r.get("central"), r.get("pc")
    return r.get("erro") is None and ((c is not None and c <= 0) or (pc is not None and (pc < 0.2 or pc > 5)))


def ke30(r: dict) -> bool:
    return r.get("erro") is None and r.get("ke_nom") is not None and r["ke_nom"] > 0.30


def nc(r: dict) -> bool:
    return r.get("erro") is None and r.get("palavra") == "NÃO CONCLUSIVO"


def confere(prev: str, r: dict) -> bool:
    if prev == "erro":
        return r.get("erro") is not None
    if prev.startswith("NÃO CONCLUSIVO"):
        return nc(r) and (ke30(r) if "Ke > 30%" in prev else True)
    if prev.startswith("valor absurdo"):
        return absurdo(r) and ((r.get("pc") or 0) > 5 if "P/C > 5" in prev else True)
    if prev == "roda, sem absurdo":
        return r.get("erro") is None and not absurdo(r)
    return r.get("erro") is None            # "roda", "roda (…)"


def observado(r: dict) -> str:
    if r.get("erro"):
        return f"erro ({r['erro']['tipo']})"
    s = r["palavra"]
    extras = [x for x, f in (("Ke > 30%", ke30(r)), ("valor absurdo", absurdo(r))) if f]
    return s + (f" ({', '.join(extras)})" if extras else "")


def motivo(r: dict) -> str:
    if r.get("erro"):
        e = r["erro"]
        return f"{e['tipo']} em {e['onde']}: {e['mensagem'][:140]}".replace("|", "/").replace("\n", " ")
    if r["palavra"] != "NÃO CONCLUSIVO":
        return f"régua do P/C ({r['palavra']})"
    m = []
    if ke30(r):
        m.append(f"Ke nominal {100 * r['ke_nom']:.1f}% > 30%")
    if r.get("dispersao") is not None and r["dispersao"] > DISPERSAO:
        m.append(f"dispersão das âncoras {r['dispersao']:.2f}× > {DISPERSAO}×")
    if absurdo(r):
        m.append("valor absurdo")
    if not m:
        m.append(f"trava do método (régua: {r.get('palavra_regua')})")
    return "; ".join(m)


def nao_auto(r: dict) -> tuple[int, int]:
    c = r["contagem"]
    return c["pesquisa"], c["vazio"]


def fmt(x, nd=2, pct=False):
    if x is None:
        return "—"
    return f"{100 * x:.1f}%".replace(".", ",") if pct else f"{x:.{nd}f}".replace(".", ",")


def montar() -> str:
    cad = {c["ticker"]: c for c in json.loads((AQUI / "cadastro.json").read_text(encoding="utf-8"))}
    tempos = json.loads((AQUI / "tempos_insumos.json").read_text(encoding="utf-8"))
    res = {tk: json.loads((AQUI / "resultados" / f"{tk}.json").read_text(encoding="utf-8")) for tk in cad}
    hall = [v["pc"] for v in json.loads(GOLDEN.read_text(encoding="utf-8"))["tickers"].values() if v.get("pc") is not None]

    linhas, por_acao = [], {}
    for tk in sorted(cad, key=lambda t: cad[t]["ordem"]):
        r, c = res[tk], cad[tk]
        seg_col = sum((c.get("coleta") or {}).get("segundos", {}).values())
        ti = tempos.get(tk, {})
        seg = seg_col + ti.get("segundos", 0.0) + r.get("segundos_avaliacao", 0.0)
        p, v = nao_auto(r)
        vpct = 100 * v / (p + v) if p + v else 0.0
        por_acao[tk] = dict(min=seg / 60, vpct=vpct)
        n = r["contagem"]
        linhas.append(
            f"| {c['ordem']} | {tk} | {c['tipo']} | {r.get('palavra') or 'erro'} | {fmt(r.get('pc'))} | "
            f"{fmt(r.get('ke_nom'), pct=True)} | {fmt(r.get('dispersao'))} | {motivo(r)} | "
            f"{fmt(seg_col / 60, 1)} + {fmt(ti.get('segundos', 0) / 60, 1)} + {fmt(r.get('segundos_avaliacao', 0) / 60, 1)} = "
            f"**{fmt(seg / 60, 1)}** | {ti.get('chamadas', 0)} | {n['automatico']} / {n['pesquisa']} / {n['vazio']} | "
            f"{fmt(n['pct_automatico'], 1)}% | {fmt(vpct, 0)}% |")

    ok = [r for r in res.values() if r.get("erro") is None]
    n_rodam, n_nc = len(ok), sum(nc(r) for r in ok)
    n_ke, n_abs = sum(ke30(r) for r in ok), sum(absurdo(r) for r in ok)
    med_v = st.median(x["vpct"] for x in por_acao.values())
    med_v_ok = st.median(por_acao[r["ticker"]]["vpct"] for r in ok) if ok else None
    med_min = st.median(x["min"] for x in por_acao.values())
    med_min_ok = st.median(por_acao[r["ticker"]]["min"] for r in ok) if ok else None
    crit = [
        ("1", "rodam sem erro (palavra, NÃO CONCLUSIVO incluso)", f"≥ {LIM['rodam']} de 20", f"{n_rodam}", n_rodam >= LIM["rodam"]),
        ("2", "NÃO CONCLUSIVO entre as que rodam", f"≤ {LIM['nc']}", f"{n_nc}", n_nc <= LIM["nc"]),
        ("3", "Ke nominal > 30%", f"≤ {LIM['ke30']}", f"{n_ke}", n_ke <= LIM["ke30"]),
        ("4", "valor absurdo (central ≤ 0, P/C < 0,2 ou > 5)", f"≤ {LIM['absurdo']}", f"{n_abs}", n_abs <= LIM["absurdo"]),
        ("6", "vazios ÷ insumos não automáticos, mediana das 20", f"≤ {fmt(LIM['vazio_pct'], 0)}%",
         f"{fmt(med_v, 0)}% (só as que rodam: {fmt(med_v_ok, 0)}%)", med_v <= LIM["vazio_pct"]),
        ("7", "tempo por ação (coleta + insumos + avaliação), mediana das 20", f"≤ {fmt(LIM['minutos'], 0)} min",
         f"{fmt(med_min, 1)} min (só as que rodam: {fmt(med_min_ok, 1)} min)", med_min <= LIM["minutos"]),
    ]
    passou = all(x[4] for x in crit)

    # por insumo
    tab: dict[tuple[str, str], dict[str, int]] = {}
    for r in res.values():
        grupo = "industrial" if r["tipo"] == "industrial" else "financeira"
        for i in r["insumos"]:
            d = tab.setdefault((grupo, i["insumo"]), {"automatico": 0, "pesquisa": 0, "vazio": 0})
            d[i["classe"]] += 1

    pcs = [r["pc"] for r in ok if r.get("pc") is not None]
    pct_auto = [r["contagem"]["pct_automatico"] for r in res.values()]
    disp = [r for r in ok if r.get("dispersao") is not None and r["dispersao"] > DISPERSAO]
    palavras = {}
    for r in ok:
        palavras[r["palavra"]] = palavras.get(r["palavra"], 0) + 1

    o = []
    o.append("# Hold-out B36 — método v2.7 congelado em 20 ações fora do hall (novembro de 2026)\n")
    o.append("*Gerado por `ferramentas/holdout_b36/relatorio.py` só a partir dos JSONs de `ferramentas/holdout_b36/` "
             "(cadastro, tempos dos insumos, resultados). Regra, lista, ficha-padrão, protocolo, critério e previsões: emenda 8 "
             "do `docs/PRE-REGISTRO-v3.md`, escrita antes de rodar. Data-base T = 19/11/2026. Nenhum número aqui é ordem de "
             "compra ou venda.*\n")
    o.append(f"## Resultado: **{'PASSOU' if passou else 'NÃO PASSOU'}** "
             f"({sum(x[4] for x in crit)} de {len(crit)} linhas do critério)\n")
    o.append("| # | Linha do critério (emenda 8) | Limite | Observado | Passou? |\n|---|---|---|---|---|")
    o += [f"| {a} | {b} | {c} | {d} | {'sim' if e else '**não**'} |" for a, b, c, d, e in crit]
    o.append("\n**Relatado fora do critério (§0.3):** "
             f"palavras das que rodam: {', '.join(f'{k} {v}' for k, v in sorted(palavras.items()))}; "
             f"nº de BARATA: {palavras.get('BARATA', 0)}; "
             f"P/C mediano das que rodam {fmt(st.median(pcs) if pcs else None)} × hall {fmt(st.median(hall))} "
             f"(41 do golden); dispersão > {fmt(DISPERSAO, 1)}×: {len(disp)} ({', '.join(r['ticker'] for r in disp) or '—'}); "
             f"erros explícitos do motor: {20 - n_rodam}; % de insumos automáticos por ação: mediana "
             f"{fmt(st.median(pct_auto), 1)}% (mín. {fmt(min(pct_auto), 1)}%, máx. {fmt(max(pct_auto), 1)}%).\n")

    o.append("## Por ação\n")
    o.append("Tempo em minutos de relógio: coleta (CVM, B3, StatusInvest) + subagente do protocolo + avaliação. "
             "Chamadas = ferramentas usadas pelo subagente (contagem do harness). Classes: automático / pesquisa / vazio "
             "(emenda 8: a classe sai do código). \"Vazio\" = vazios ÷ (pesquisa + vazio).\n")
    o.append("| # | Ação | Tipo | Palavra | P/C | Ke nominal | Dispersão | Motivo | Tempo (min) | Chamadas | Auto / Pesq / Vazio | "
             "% auto | Vazio |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    o += linhas

    o.append("\n## Previsto × observado (previsões da emenda 8, escritas antes de rodar)\n")
    o.append("| Ação | Previsto | Observado | Confere? |\n|---|---|---|---|")
    acertos = 0
    for tk in sorted(cad, key=lambda t: cad[t]["ordem"]):
        k = confere(PREVISTO[tk], res[tk])
        acertos += k
        o.append(f"| {tk} | {PREVISTO[tk]} | {observado(res[tk])} | {'sim' if k else '**não**'} |")
    o.append(f"\nConferem {acertos} de 20.\n")

    o.append("## Por insumo\n")
    o.append("Quantas das ações de cada grupo tiveram o insumo automático, por pesquisa (protocolo, fonte A/B) ou vazio.\n")
    for grupo in ("industrial", "financeira"):
        itens = [(k[1], v) for k, v in tab.items() if k[0] == grupo]
        if not itens:
            continue
        o.append(f"\n**{grupo.capitalize()}** ({sum(1 for r in res.values() if (r['tipo'] == 'industrial') == (grupo == 'industrial'))} ações)\n")
        o.append("| Insumo | Automático | Pesquisa | Vazio |\n|---|---|---|---|")
        o += [f"| {n} | {v['automatico']} | {v['pesquisa']} | {v['vazio']} |" for n, v in itens]
    o.append("")
    return "\n".join(o) + "\n"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(montar(), encoding="utf-8")
    print("gravado", SAIDA)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
