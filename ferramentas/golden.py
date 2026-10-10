"""Golden da regressão: grava, carrega e compara o instantâneo dos 41 tickers.

Uma mudança de método só passa se o diff for declarado: `python -m tests.regerar_golden --motivo "..."`.
"""
import json
import math
import pathlib

AQUI = pathlib.Path(__file__).parent
GOLDEN = AQUI / "tests" / "golden.json"
LOG = AQUI / "tests" / "golden_log.md"

# tolerância absoluta por campo (R$ para valores por ação; fração para taxas)
TOL = {"central": 0.01, "ancoras": 0.01, "pc": 0.005, "nota_geral": 0.05,
       "bogle_nom": 0.0005, "dy": 0.0005, "fator_defasagem": 0.0005, "cobertura_juros": 0.05}
EXATOS = ("palavra", "vence_rf", "lote", "data_preco")
ROTULO = {"central": "central", "pc": "P/C", "palavra": "palavra", "ancoras": "âncora", "nota_geral": "nota geral",
          "vence_rf": "vence a RF", "bogle_nom": "Bogle nominal", "dy": "yield sustentável",
          "cobertura_juros": "cobertura de juros", "fator_defasagem": "fator de defasagem", "lote": "lote",
          "data_preco": "data do preço"}


def carregar():
    return json.loads(GOLDEN.read_text(encoding="utf-8"))["tickers"]


def salvar(snap, motivo):
    ruins = [(tk, k) for tk, d in snap.items() for k, x in d.items() if _nan(x)
              or (k == "ancoras" and any(_nan(y) for y in x.values()))]
    if ruins:
        raise ValueError(f"golden com NaN não é gravado (AUD-30): {ruins}")
    from datetime import datetime
    GOLDEN.parent.mkdir(exist_ok=True)
    GOLDEN.write_text(json.dumps({"motivo": motivo, "tickers": snap}, ensure_ascii=False, indent=1, sort_keys=True,
                                     allow_nan=False),   # AUD-52: Infinity também não entra
                      encoding="utf-8")
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"- {datetime.now():%Y-%m-%d %H:%M} — {motivo}\n")


def _nan(x):
    return isinstance(x, float) and math.isnan(x)


def _difere(campo, a, b):
    if _nan(a) or _nan(b):             # NaN nunca é igual a nada (AUD-30): nem a outro NaN, nem a si mesmo
        return True
    if a is None or b is None:
        return a is not b
    if campo in EXATOS or isinstance(a, str):
        return a != b
    if a == b:                       # inf == inf
        return False
    return abs(a - b) > TOL[campo]


def comparar(golden, atual):
    """Lista de mudanças [(ticker, rótulo, antes, depois)]; vazio = idêntico dentro da tolerância."""
    mud = []
    for tk in sorted(set(golden) | set(atual)):
        if tk not in atual:
            mud.append((tk, "ticker", "no golden", "ausente agora"))
            continue
        if tk not in golden:
            mud.append((tk, "ticker", "ausente no golden", "novo"))
            continue
        g, a = golden[tk], atual[tk]
        for campo in g.keys() | a.keys():
            if campo == "ancoras":
                for nome in sorted(g["ancoras"].keys() | a["ancoras"].keys()):
                    x, y = g["ancoras"].get(nome), a["ancoras"].get(nome)
                    if _difere("ancoras", x, y):
                        mud.append((tk, f"âncora {nome}", x, y))
            elif _difere(campo, g.get(campo), a.get(campo)):
                mud.append((tk, ROTULO.get(campo, campo), g.get(campo), a.get(campo)))
    return mud


def formatar(mud):
    def f(x):
        return f"{x:.4f}" if isinstance(x, float) else str(x)
    return "\n".join(f"  {tk:7} {rot:22} {f(x)} → {f(y)}" for tk, rot, x, y in mud)
