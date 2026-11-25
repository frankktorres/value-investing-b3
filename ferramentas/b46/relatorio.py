"""B46 — lê `b46/resultado_B46.json` pela regra da emenda 12 e gera `docs/B46` só do JSON. Uso, de `ferramentas/`:

    python -m b46.relatorio

Nada aqui recalcula o motor: só confere (C1–C4) e resume. A leitura (PASSA / FALHA / NÃO CONCLUSIVA) é a pré-declarada.
"""
from __future__ import annotations

import json
import pathlib
import statistics as st
import sys

AQUI = pathlib.Path(__file__).resolve().parent
FERRAMENTAS = AQUI.parent
if str(FERRAMENTAS) not in sys.path:
    sys.path.insert(0, str(FERRAMENTAS))

from b46 import calculo as C  # noqa: E402

ENTRADA = AQUI / "resultado_B46.json"
SAIDA = FERRAMENTAS.parent / "docs" / "b46" / "B46-2026-11.md"
TOL_KE = 1e-9
TOL_ANC = 1e-9
LIMITE_PRECO = 0.005
FRACAO_C3 = 2 / 3
ORDEM_I = ("AAA", "AA", "A+", "A", "A-", "BBB", "BB+", "BB", "B+", "B", "B-", "CCC", "CC", "C", "D")


def _ok(x: dict | None) -> bool:
    return bool(x) and x.get("erro") is None and isinstance(x.get("central"), (int, float))


def _rel(a: float, b: float) -> float:
    return abs(a - b) / abs(b) if b else abs(a - b)


def industriais(res: dict) -> list[dict]:
    return [l for l in res["linhas"] if not l["financeira"]]


def c1(res: dict) -> dict:
    """Conferência da mecânica: Ke, π e âncoras recalculados à parte a partir do que o JSON registrou."""
    falhas = []
    for l in industriais(res):
        c, d = l.get("completo"), l.get("de")
        if not (_ok(c) and _ok(d)):
            continue
        tk = l["tk"]
        ke = C.ke_nominal(c["rf_real"], c["pi_inflacao"], c["t"], c["de_cont"])
        if abs(ke - c["ke_nom"]) > TOL_KE:
            falhas.append(f"{tk}: Ke {c['ke_nom']:.6f} ≠ fórmula {ke:.6f}")
        if c.get("rating_i") is not None and abs(C.pi_de_classe(c["rating_i"]) - c["pi_i"]) > 1e-12:
            falhas.append(f"{tk}: π (i) não bate com a Tabela 5")
        if c.get("rating_ii") is not None and abs(C.pi_de_classe(c["rating_ii"]) - c["pi_ii"]) > 1e-12:
            falhas.append(f"{tk}: π (ii) não bate com a Tabela 5")
        if c.get("z") is not None and C.rating_altman(c["z"]) != c["rating_ii"]:
            falhas.append(f"{tk}: rating (ii) não bate com o slide 26")
        if abs(C.pi_combinado(c["pi_i"], c.get("pi_ii")) - c["pi"]) > 1e-12:
            falhas.append(f"{tk}: π combinado não é a média")
        esperado = C.ancoras_com_pi(c["anc_sem_pi"], c["pi"])
        if set(esperado) != set(c["anc_com_pi"]) or any(_rel(c["anc_com_pi"][k], esperado[k]) > TOL_ANC for k in esperado):
            falhas.append(f"{tk}: âncoras com π ≠ sem π × (1 − π)")
        if set(c["anc_sem_pi"]) != set(d["anc_sem_pi"]) or any(_rel(c["anc_sem_pi"][k], d["anc_sem_pi"][k]) > TOL_ANC
                                                                for k in d["anc_sem_pi"]):
            falhas.append(f"{tk}: âncoras sem π do modo completo ≠ as do modo só D/E")
    return dict(passou=not falhas, falhas=falhas)


def _no_limite(novo: float, antes: float) -> bool:
    """C2a: o central muda no máximo 0,5%. Sem mudança nenhuma passa, inclusive com central ≤ 0 (0 → 0); com central ≤ 0 e
    alguma mudança, a variação relativa não se define e reprova. (25/11: a 1ª versão reprovava todo central ≤ 0, mais que o
    texto da emenda 12 — erro do leitor, corrigido e declarado no relatório.)"""
    if abs(novo - antes) <= 1e-9:
        return True
    return antes > 0 and _rel(novo, antes) <= LIMITE_PRECO


def grupo_acima(l: dict) -> bool:
    """C2: D/E a mercado ÷ 1,3 > D/E da indústria (acima do limite nos dois choques de preço)."""
    c = l.get("completo") or {}
    return _ok(c) and c["de_mercado"] / 1.3 > c["de_ind"]


def c2(res: dict) -> dict:
    falhas, abaixo, grupo = [], [], []
    for l in industriais(res):
        c = l.get("completo")
        if not _ok(c):
            continue
        ch = l["choques"]
        if grupo_acima(l):
            grupo.append(l["tk"])
            for n in ("preco_0.7", "preco_1.3"):
                x = ch[n]
                if not _ok(x) or not _no_limite(x["central"], c["central"]):
                    falhas.append(f"{l['tk']}: {n} muda o central ({c['central']} → {x.get('central')}) {x.get('erro') or ''}")
            x = ch["divida_1.1"]
            if not _ok(x) or x["central"] > c["central"] + 1e-9:
                falhas.append(f"{l['tk']}: dívida +10% sobe o central ({c['central']} → {x.get('central')}) {x.get('erro') or ''}")
        else:
            x = ch["divida_1.1"]
            if _ok(x) and x["central"] > c["central"] + 1e-9:
                abaixo.append(f"{l['tk']}: dívida +10% sobe o central {100 * (x['central'] / c['central'] - 1):+.2f}%")
    pis = [C.pi_de_classe(r) for r in ORDEM_I]
    pis_z = [C.pi_de_classe(r) for r, _ in C.ALTMAN_2013]
    if not all(a <= b for a, b in zip(pis, pis[1:])) or not all(a <= b for a, b in zip(pis_z, pis_z[1:])):
        falhas.append("π cai com rating pior numa das escalas (C2c)")
    return dict(passou=not falhas, falhas=falhas, grupo=grupo, abaixo_relatado=abaixo)


def c3(res: dict) -> dict:
    base = [l for l in industriais(res) if _ok(l.get("completo")) and l["completo"]["de_mercado"] > l["completo"]["de_ind"]]
    conc = [l["tk"] for l in base if l["completo"]["concordam"]]
    n = len(base)
    return dict(passou=n > 0 and len(conc) >= FRACAO_C3 * n, n=n, concordam=conc,
                discordam=[l["tk"] for l in base if not l["completo"]["concordam"]])


def c4(res: dict) -> dict:
    """Todo industrial sai com número no modo completo ou com a razão; nenhum vazio sem razão."""
    sem_razao, nao_avaliados = [], []
    for l in industriais(res):
        c = l.get("completo") or {}
        if _ok(c):
            if c.get("pi_ii") is None and not c.get("falta_ii"):
                sem_razao.append(f"{l['tk']}: π (ii) vazio sem razão")
            continue
        e = c.get("erro") or {}
        if not e.get("mensagem"):
            sem_razao.append(f"{l['tk']}: sem número e sem razão")
        else:
            nao_avaliados.append(f"{l['tk']}: {e['tipo']}: {e['mensagem']}")
    return dict(passou=not sem_razao, sem_razao=sem_razao, nao_avaliados=nao_avaliados)


def leitura(r1: dict, r2: dict, r3: dict, r4: dict) -> str:
    if not (r1["passou"] and r2["passou"] and r4["passou"]):
        return "FALHA"
    return "PASSA" if r3["passou"] else "NÃO CONCLUSIVA"


def _pct(x, casas=1):
    return "—" if x is None else f"{100 * x:.{casas}f}%".replace(".", ",")


def _num(x, casas=2):
    return "—" if not isinstance(x, (int, float)) else f"{x:.{casas}f}".replace(".", ",")


def _d(a, b):
    return f"{100 * (a / b - 1):+.1f}%".replace(".", ",") if isinstance(a, (int, float)) and isinstance(b, (int, float)) and b > 0 else "—"


def gerar(res: dict) -> str:
    r1, r2, r3, r4 = c1(res), c2(res), c3(res), c4(res)
    lei = leitura(r1, r2, r3, r4)
    ind = industriais(res)
    o = ["# B46 — Ke > 30% nas muito alavancadas: variante \"separar a dificuldade\" (emenda 12)", "",
         "*Gerado por `ferramentas/b46/relatorio.py` só a partir de `ferramentas/b46/resultado_B46.json`. Regra, critério, leitura e "
         "previsões: emenda 12 do `docs/PRE-REGISTRO-v3.md`, commitada antes de rodar. Fontes: `docs/b46/FONTES-B46.md`. O motor não "
         "mudou. Nada aqui é ordem de compra ou venda.*", "",
         f"## Leitura pela regra: **{lei}**", "",
         "C1 e C2 são conferência de mecânica; **só o C3 testa a hipótese**. PASSA = mecânica certa + π mensurável, não \"valor "
         "certo\"; a prova é o HOLD-OUT 2 (ajuste do Frank, 25/11).", "",
         "**Nota de execução (declarada).** A 1ª geração deste relatório deu **FALHA** por erro do leitor: o C2a reprovava todo "
         "central ≤ 0, mesmo sem nenhuma mudança com o preço (RECV3, SMFT3, CSNA3 e MOVI3 com 0 → 0; RAIL3 e MRVE3 com o mesmo "
         "negativo). O texto da emenda 12 é \"mudam o central em no máximo 0,5%\"; o leitor foi corrigido para o texto, com teste "
         "(`tests/test_b46_relatorio.py`), sem mudar regra nem limite. A classe muda (FALHA = a variante não sai; NÃO CONCLUSIVA = a "
         "B46 segue aberta); nas duas, nada é implantado. Depois do `adversario`, a medição rodou de novo com dois consertos para o "
         "texto da emenda: o choque de dívida passou a multiplicar também os outros passivos financeiros (na CMIN3 o D subia só "
         "4,1%) e, sem o rating (i), vale só o π (ii) (\"com uma só, vale a única\"; nenhum caso nesta rodada).", "",
         "**Limite do C1:** o π é conferido com a mesma tabela que o produziu (conferência do encanamento); a tabela em si é "
         "conferida pelo teste à mão (`tests/test_b46_calculo.py`, contra a Tabela 5 e o slide 26). O Ke é conferido de verdade "
         "(sai do motor, a fórmula é refeita à parte).", "",
         "**Fora do hall dos lotes:** EGIE3 e ITSA4 estão no `hall.json` mas não nos lotes de `oraculo/sanidade.py` (emenda 12).", "",
         "| Linha | O que confere | Resultado |", "|---|---|---|",
         f"| C1 | Ke, π e âncoras recalculados à parte | {'passou' if r1['passou'] else '**não** — ' + '; '.join(r1['falhas'][:5])} |",
         f"| C2 | preço ×0,7/×1,3 e dívida +10% no grupo acima do limite ({len(r2['grupo'])}); π monotônico | "
         f"{'passou' if r2['passou'] else '**não** — ' + '; '.join(r2['falhas'][:5])} |",
         f"| C3 | \\|π(i) − π(ii)\\| ≤ 20 p.p. em ≥ 2/3 das sobrealavancadas | {len(r3['concordam'])} de {r3['n']} "
         f"({'passou' if r3['passou'] else '**não**'}) |",
         f"| C4 | nenhum vazio sem razão | {'passou' if r4['passou'] else '**não** — ' + '; '.join(r4['sem_razao'])} |", ""]
    perto = []
    for l in industriais(res):
        c = l.get("completo") or {}
        if not _ok(c) or not c["de_mercado"] > c["de_ind"]:
            continue
        if c.get("pi_ii") is not None and abs(abs(c["pi_i"] - c["pi_ii"]) - C.CONCORDANCIA) <= 0.05:
            perto.append(f"{l['tk']} |Δπ| {100 * abs(c['pi_i'] - c['pi_ii']):.2f} p.p.".replace('.', ',', 1))
        if c["de_mercado"] / c["de_ind"] <= 1.05:
            perto.append(f"{l['tk']} D/E a mercado só {_pct(c['de_mercado'] / c['de_ind'] - 1, 1)} acima do da indústria")
    o += ["**Discordam no π (C3):** " + (", ".join(r3["discordam"]) or "nenhuma"), "",
          "**Fragilidade do C3 (relatada; ressalva do `oraculo`):** casos a ≤ 5 p.p. do limite de 20 p.p. ou com D/E a mercado "
          "a ≤ 5% do da indústria: " + ("; ".join(perto) or "nenhum") + ".", "",
          "**Não avaliados (com a razão):** " + ("; ".join(r4["nao_avaliados"]) or "nenhum"), "",
          "**Abaixo do limite, dívida +10% sobe o central (relatado, previsto em parte — efeito H2):** "
          + ("; ".join(r2["abaixo_relatado"]) or "nenhum"), ""]
    ke_b = [l["base"]["ke_nom"] for l in ind if _ok(l.get("base"))]
    ke_c = [l["completo"]["ke_nom"] for l in ind if _ok(l.get("completo"))]
    pcs = lambda m: [l[m]["pc"] for l in ind if _ok(l.get(m)) and isinstance(l[m].get("pc"), (int, float)) and l[m]["pc"] < 1e9]
    pal = lambda m, p: sum(1 for l in ind if _ok(l.get(m)) and l[m]["palavra"] == p)
    o += ["## Relatado fora do critério (§0.3)", "",
          f"- Ke nominal > 30%: motor de hoje {sum(1 for k in ke_b if k > 0.30)} de {len(ke_b)}; variante "
          f"{sum(1 for k in ke_c if k > 0.30)} de {len(ke_c)} (quase por construção).",
          f"- P/C mediano dos industriais: hoje {_num(st.median(pcs('base')) if pcs('base') else None)}; variante "
          f"{_num(st.median(pcs('completo')) if pcs('completo') else None)}.",
          f"- BARATA: hoje {pal('base', 'BARATA')}; variante {pal('completo', 'BARATA')}. RADAR: {pal('base', 'RADAR')} → "
          f"{pal('completo', 'RADAR')}. JUSTA: {pal('base', 'JUSTA')} → {pal('completo', 'JUSTA')}. NÃO CONCLUSIVO: "
          f"{pal('base', 'NÃO CONCLUSIVO')} → {pal('completo', 'NÃO CONCLUSIVO')}.", ""]
    pares = [(l["completo"]["pi_i"], l["completo"]["pi_ii"]) for l in ind if _ok(l.get("completo")) and l["completo"].get("pi_ii") is not None]
    if pares:
        o += [f"- Viés (i) × (ii) (hipótese do `senior`: juros nominais em R$): π (i) > π (ii) em "
              f"{sum(1 for a, b in pares if a > b)} de {len(pares)}; mediana de π (i) − π (ii) = "
              f"{_pct(st.median(a - b for a, b in pares))}.", ""]
    for grupo, titulo in (("hall", "Hall (todos; financeiras: não se aplica)"), ("dossie", "Dossiês"), ("b36", "B36 (só descrevem a falha)")):
        o += [f"## {titulo}", "",
              "| Ação | Indústria | D/E mercado → cont. | Ke hoje → var. | Rating (i) · Z'' → (ii) | π (i) · (ii) → π | "
              "Palavra hoje → var. | P/C hoje → var. | Δ central: parte D/E · parte π |",
              "|---|---|---|---|---|---|---|---|---|"]
        for l in [x for x in res["linhas"] if x["grupo"] == grupo]:
            if l["financeira"]:
                o.append(f"| {l['tk']} | financeira — não se aplica | | | | | | | |")
                continue
            b, d, c = l.get("base") or {}, l.get("de") or {}, l.get("completo") or {}
            if not _ok(c):
                e = c.get("erro") or b.get("erro") or {}
                o.append(f"| {l['tk']} | não avaliado | | {_pct(b.get('ke_nom'))} | | | {b.get('palavra') or '—'} | "
                         f"{_num(b.get('pc'))} | {e.get('tipo', '')}: {e.get('mensagem', '')[:120]} |")
                continue
            mud = " **(muda)**" if b.get("palavra") != c.get("palavra") else ""
            o.append(f"| {l['tk']} | {c['industria']} | {_num(c['de_mercado'])} → {_num(c['de_cont'])} | "
                     f"{_pct(b.get('ke_nom'))} → {_pct(c['ke_nom'])} | {c['rating_i']} · {_num(c.get('z'))} → {c.get('rating_ii') or '—'} | "
                     f"{_pct(c['pi_i'])} · {_pct(c.get('pi_ii'))} → {_pct(c['pi'])} | {b.get('palavra')} → {c['palavra']}{mud} | "
                     f"{_num(b.get('pc'))} → {_num(c.get('pc'))} | {_d(d.get('central'), b.get('central'))} · "
                     f"{_d(c.get('central'), d.get('central'))} |")
        o.append("")
    return "\n".join(o) + "\n"


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    res = json.loads(ENTRADA.read_text(encoding="utf-8"))
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(gerar(res), encoding="utf-8")
    print(SAIDA)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
