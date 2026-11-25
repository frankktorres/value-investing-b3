"""B57 — recoleta ADITIVA da conta 2.03.05 (lucros/prejuízos acumulados) nas séries da CVM. Uso, de `ferramentas/`:

    python -m b57.recoletar conferir   # recoleta num arquivo temporário e compara; não grava nada
    python -m b57.recoletar gravar     # idem e, se todo campo antigo for idêntico, grava SÓ o campo novo

Emenda 13 do `docs/PRE-REGISTRO-v3.md`. Recoleta pelo próprio `coletar_cvm.main` (mesmo ZIP do cache, mesmo mês do ITR que
a série já tem) e prova que a recoleta é aditiva: todo valor que a série antiga tem sai IDÊNTICO na recoleta. Qualquer
divergência → nada é gravado e o relatório diz onde. Grava só `lucros_acumulados` nos containers que a série antiga já tem
(`anual/<ano>`, `ltm`, `ltm_<ref>`); chave nova do formato atual do coletor (ex.: `ltm_ref` nas séries antigas) não entra.
A versão anterior de cada arquivo vai para `dados/_historico/` (`_historico/` da pasta do arquivo).
"""
from __future__ import annotations

import contextlib
import json
import math
import pathlib
import shutil
import sys
import tempfile

AQUI = pathlib.Path(__file__).resolve().parent
FERRAMENTAS = AQUI.parent
if str(FERRAMENTAS) not in sys.path:
    sys.path.insert(0, str(FERRAMENTAS))

import coletar_cvm  # noqa: E402

CAMPO = "lucros_acumulados"
ANO_ITR = 2026
MES = {"1T": 3, "2T": 6, "3T": 9}
ARQUIVOS = {
    "hall": FERRAMENTAS / "dados" / "cvm_series.json",
    "dossie": FERRAMENTAS / "dossie" / "dados" / "cvm_series_dossie.json",
    "b36": FERRAMENTAS / "holdout_b36" / "dados" / "cvm_series_holdout.json",
}
DATA = "2026-11-25"


def trimestres(reg: dict) -> tuple[str, list[str]]:
    """(trimestre principal, todos os trimestres guardados). Principal = `ltm_ref`; no formato antigo (sem `ltm_ref`), o único
    `ltm_<ref>`. Cada `ltm_<ref>` guardado é recoletado no próprio mês. Ambíguo, ausente ou de outro ano → erro explícito."""
    refs = sorted(k[4:] for k in reg if k.startswith("ltm_") and k[4:6] in MES and isinstance(reg[k], dict))
    principal = reg.get("ltm_ref") or (refs[0] if len(refs) == 1 else None)
    if principal is None or principal not in refs:
        raise ValueError(f"trimestre do LTM ambíguo ou ausente: ltm_ref={reg.get('ltm_ref')!r}, guardados={refs}")
    fora = [r for r in refs if not r.endswith(f"{ANO_ITR % 100:02d}")]
    if fora:
        raise ValueError(f"LTM de {fora}, recoleta só para {ANO_ITR}")
    return principal, refs


@contextlib.contextmanager
def _contexto(grupo: str, tk: str):
    if grupo != "b36":
        yield
        return
    from holdout_b36 import executor as X
    with X.registrado(X.cadastro()[tk]):     # põe o código CVM do ticker em `coletar_cvm.EMPRESAS` só no bloco
        yield


def recoletar(grupo: str, tk: str, mes: int) -> dict:
    with tempfile.TemporaryDirectory() as tmp, _contexto(grupo, tk):
        arq = pathlib.Path(tmp) / "s.json"
        coletar_cvm.main([tk], arq=arq, ano_itr=ANO_ITR, mes=mes)
        return json.loads(arq.read_text(encoding="utf-8"))[tk]      # ida e volta pelo JSON: chaves de ano como texto


def _igual(a, b) -> bool:
    if isinstance(a, float) and isinstance(b, float) and math.isnan(a) and math.isnan(b):
        return True
    if isinstance(a, dict) and isinstance(b, dict):
        return all(k in b and _igual(a[k], b[k]) for k in a)        # só o que a série ANTIGA tem precisa bater
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_igual(x, y) for x, y in zip(a, b))
    return a == b


def divergencias(velho: dict, novo: dict, caminho: str = "") -> list[str]:
    out = []
    for k, va in velho.items():
        c = f"{caminho}/{k}"
        if k not in novo:
            out.append(f"{c}: some na recoleta")
        elif isinstance(va, dict) and isinstance(novo[k], dict):
            out += divergencias(va, novo[k], c)
        elif not _igual(va, novo[k]):
            out.append(f"{c}: {va!r} → {novo[k]!r}")
    return out


def acrescentar(velho: dict, novo: dict) -> tuple[dict, list[str]]:
    """Cópia da série antiga com o CAMPO onde a recoleta o tem; devolve também a lista de containers sem o campo."""
    out = json.loads(json.dumps(velho))
    sem = []
    alvos = [("anual", a) for a in velho.get("anual", {})] + [(k, None) for k in velho if k == "ltm" or k.startswith("ltm_")
                                                               and isinstance(velho[k], dict)]
    for k, a in alvos:
        dv = out[k][a] if a else out[k]
        dn = (novo.get(k) or {}).get(a) if a else novo.get(k)
        if not isinstance(dv, dict) or not dv or dv.get("erro"):
            continue                            # ano sem demonstração / LTM com erro: nada a acrescentar
        if not isinstance(dn, dict) or dn.get(CAMPO) is None:
            sem.append(f"{k}/{a}" if a else k)
            continue
        dv[CAMPO] = dn[CAMPO]
    return out, sem


def processar(grupo: str, gravar: bool) -> dict:
    arq = ARQUIVOS[grupo]
    series = json.loads(arq.read_text(encoding="utf-8"))
    rel, saida = {}, {}
    for tk, reg in series.items():
        try:
            principal, refs = trimestres(reg)
            novos = {r: recoletar(grupo, tk, MES[r[:2]]) for r in refs}
            novo = dict(novos[principal])
            for r in refs:                       # cada `ltm_<ref>` comparado com a recoleta do próprio trimestre
                novo[f"ltm_{r}"] = novos[r][f"ltm_{r}"]
        except Exception as x:          # noqa: BLE001 — registra a falha com a razão; o arquivo não é gravado
            rel[tk] = dict(erro=f"{type(x).__name__}: {x}")
            continue
        div = divergencias(reg, novo)
        out, sem = acrescentar(reg, novo)
        rel[tk] = dict(divergencias=div, sem_campo=sem)
        saida[tk] = out
    ok = all(not r.get("erro") and not r["divergencias"] for r in rel.values())
    if gravar and ok:
        hist = arq.parent / "_historico"
        hist.mkdir(exist_ok=True)
        shutil.copy2(arq, hist / f"{arq.stem}_{DATA}_antes_B57{arq.suffix}")
        arq.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
    return dict(arquivo=str(arq), aditiva=ok, gravado=bool(gravar and ok), tickers=rel)


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    a = list(argv if argv is not None else sys.argv[1:])
    if a[:1] not in (["conferir"], ["gravar"]):
        print(__doc__)
        return 2
    grupos = a[1:] or list(ARQUIVOS)
    rel = {g: processar(g, a[0] == "gravar") for g in grupos}
    (AQUI / "recoleta_B57.json").write_text(json.dumps(rel, ensure_ascii=False, indent=1), encoding="utf-8")
    for g, r in rel.items():
        ruins = {tk: x for tk, x in r["tickers"].items() if x.get("erro") or x["divergencias"]}
        sem = {tk: x["sem_campo"] for tk, x in r["tickers"].items() if x.get("sem_campo")}
        print(f"{g}: aditiva={r['aditiva']} gravado={r['gravado']} tickers={len(r['tickers'])} "
              f"com problema={len(ruins)} containers sem o campo={sum(len(v) for v in sem.values())}")
        for tk, x in ruins.items():
            print("  ", tk, x.get("erro") or x["divergencias"][:5])
    return 0 if all(r["aditiva"] for r in rel.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
