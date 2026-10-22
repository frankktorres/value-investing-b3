"""Oráculo automático (docs/ORACULO.md §1a): camadas 2–5 numa rodada só, sem mudar palavra.

    cd ferramentas && python -m oraculo              # rastreabilidade + propriedades (perfil curto) + reconciliação + sanidade
    python -m oraculo --completo                     # propriedades com 500 exemplos também nos industriais (emenda 2)
    python -m oraculo --sem-gravar                   # só imprime (usado pelas armadilhas, que rodam num worktree)
Grava docs/oraculo/AAAA-MM-DD.md e uma linha em docs/oraculo/registro.jsonl. Sai com 1 se algum check BLOQUEANTE falhar
(docs/VALIDACAO.md §1): rastreabilidade, propriedades, reconciliação com "falha" (identidade contábil quebrada em ticker com
palavra de decisão) e os alarmes de artefato da sanidade (não finito, Ke > 30% fora dos conhecidos).
"""
from __future__ import annotations

import collections
import datetime as dt
import hashlib
import json
import os
import pathlib
import re
import subprocess
import sys

AQUI = pathlib.Path(__file__).resolve().parent
FERRAMENTAS = AQUI.parent
RAIZ = FERRAMENTAS.parent
SAIDA = RAIZ / "docs" / "oraculo"
GOLDEN = FERRAMENTAS / "tests" / "golden.json"
DOUTRINA = RAIZ / "01-doutrina-value-investing.md"
PROPRIEDADES = "tests/test_oraculo_propriedades.py"
BLOQUEANTES = ("rastreabilidade", "propriedades", "reconciliacao", "sanidade")


def _commit() -> str:
    try:
        r = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=RAIZ, capture_output=True, text=True, timeout=30)
        sujo = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=RAIZ, capture_output=True,
                              text=True, timeout=30).stdout.strip()
        return r.stdout.strip() + ("+mudanças" if sujo else "")
    except (OSError, subprocess.SubprocessError):
        return "?"


def _doutrina() -> str:
    m = re.search(r"Versão\s+([\d.]+)", DOUTRINA.read_text(encoding="utf-8")[:500])
    return m.group(1) if m else "?"


def rastreabilidade() -> dict:
    from oraculo import rastreabilidade as R
    from oraculo.matriz import LACUNAS_MAX, REGRAS
    probs = R.verificar(REGRAS, LACUNAS_MAX)
    atual = R.SAIDA.read_text(encoding="utf-8").splitlines() if R.SAIDA.is_file() else []
    if atual != R.gerar_md(REGRAS).splitlines():
        probs.append("docs/RASTREABILIDADE.md desatualizado; rode `python -m oraculo.rastreabilidade`")
    return dict(status="falha" if probs else "ok", problemas=probs, regras=len(REGRAS), lacunas=LACUNAS_MAX)


def propriedades(completo: bool) -> dict:
    env = dict(os.environ, PYTHONIOENCODING="utf-8", CLAUDE_NO_SUITE_LOG="1")
    if completo:
        env["ORACULO_PERFIL"] = "completo"
    r = subprocess.run([sys.executable, "-m", "pytest", PROPRIEDADES, "-q", "-p", "no:cacheprovider", "--tb=line", "-rfEx"],
                       cwd=FERRAMENTAS, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    linhas = [x for x in r.stdout.splitlines() if x.strip()]
    contagem = {k: int(n) for n, k in re.findall(r"(\d+) (passed|failed|xfailed|xpassed|error|errors|skipped)", r.stdout)}
    falhas = [x for x in linhas if x.startswith(("FAILED", "ERROR", "XPASS"))]
    return dict(status="ok" if r.returncode == 0 else "falha", perfil="completo (500)" if completo else "curto (emenda 2)",
                contagem=contagem, falhas=falhas, resumo=linhas[-1] if linhas else "")


def reconciliacao(palavras: dict | None) -> dict:
    from oraculo import reconciliacao as R
    if not any(R.CACHE.glob("dfp_*.zip")):
        return dict(status="sem_dado", nota="sem dados/cvm/dfp_*.zip (checkout sem os ZIPs da CVM)", linhas=[])
    linhas = R.rodar(palavras=palavras)
    por = collections.Counter((r["check"], r["status"]) for r in linhas)
    falhas = [r for r in linhas if r["status"] == "falha"]
    bandeiras = [r for r in linhas if r["status"] == "bandeira"]
    return dict(status="falha" if falhas else ("bandeira" if bandeiras else "ok"), por_check=por, falhas=falhas,
                bandeiras=bandeiras, n=len(linhas))


def sanidade() -> dict:
    from oraculo import sanidade as S
    linhas = S.avaliar_universo()
    c = S.checks(linhas)
    st = "falha" if c["bloqueantes"] else ("bandeira" if c["bandeiras"] else "ok")
    return dict(status=st, **c, erros=[l for l in linhas if "erro" in l],
                palavras={l["ticker"]: l.get("palavra") for l in linhas if "erro" not in l})


def _pct(x):
    return "—" if x is None else f"{x:.1%}".replace(".", ",")


def _num(x, casas=2):
    return "—" if x is None else f"{x:.{casas}f}".replace(".", ",")


def relatorio(hoje: str, meta: dict, res: dict) -> str:
    L = [f"# Oráculo automático — {hoje}", "",
         f"Commit `{meta['commit']}` · golden `{meta['golden_sha']}` · doutrina {meta['doutrina']} · "
         f"gerado por `cd ferramentas && python -m oraculo{' --completo' if meta['completo'] else ''}`. Só lê e relata; "
         "nenhuma palavra, central, golden ou doutrina muda (docs/ORACULO.md §1a).", "",
         "| Check | Camada | Status | Bloqueia? |", "|---|---|---|---|"]
    camada = dict(rastreabilidade="§3 matriz", propriedades="2", reconciliacao="4", sanidade="5")
    for k in BLOQUEANTES:
        L.append(f"| {k} | {camada[k]} | **{res[k]['status']}** | {'sim' if res[k]['status'] == 'falha' else 'não'} |")
    for k in BLOQUEANTES:
        if "erro" in res[k]:
            L += ["", f"## {k}: o conferente quebrou", f"- {res[k]['erro']}"]
    ok = {k: v for k, v in res.items() if "erro" not in v}
    if "rastreabilidade" in ok:
        L += _rastreabilidade(ok["rastreabilidade"])
    if "propriedades" in ok:
        L += _propriedades(ok["propriedades"])
    if "reconciliacao" in ok:
        L += _reconciliacao(ok["reconciliacao"])
    if "sanidade" in ok:
        L += _sanidade(ok["sanidade"])
    return "\n".join(L) + "\n"


def _rastreabilidade(ra):
    L = ["", "## Rastreabilidade", f"{ra['regras']} regras, {ra['lacunas']} lacunas declaradas (catraca)."]
    L += [f"- PROBLEMA: {p}" for p in ra["problemas"]] or ["- sem problemas"]
    return L


def _propriedades(pr):
    L = ["", "## Propriedades (camada 2)", f"Perfil {pr['perfil']} · {pr['resumo']}"]
    L += [f"- {x}" for x in pr["falhas"]]
    if pr["contagem"].get("xfailed"):
        L.append("- xfail estrito esperado (bug conhecido, corrige na Fase 3): H10 (dado crítico ausente vira 0 em silêncio) e "
                 "achado A1 (desconto do controlador volta no Ke dos industriais)")
    return L


def _reconciliacao(rc):
    L = ["", "## Reconciliação contábil (camada 4)"]
    if rc["status"] == "sem_dado":
        L.append(f"- {rc['nota']}")
    else:
        checks = sorted({c for c, _ in rc["por_check"]})
        stats = ("ok", "bandeira", "falha", "sem_dado")
        L += [f"{rc['n']} conferências (ticker × exercício × check).", "",
              "| check | " + " | ".join(stats) + " |", "|---|" + "---|" * len(stats)]
        for c in checks:
            L.append(f"| {c} | " + " | ".join(str(rc["por_check"].get((c, s), 0)) for s in stats) + " |")
        for titulo, lst in (("Falhas (bloqueiam)", rc["falhas"]), ("Bandeiras", rc["bandeiras"])):
            if not lst:
                continue
            L += ["", f"**{titulo}** ({len(lst)}):"]
            por_tk = collections.defaultdict(list)
            for r in lst:
                por_tk[r["ticker"]].append(f"{r['check']} {r['ano']} ({_pct(r['dif_rel'])})")
            L += [f"- {tk}: " + ", ".join(v[:8]) + (f" … +{len(v) - 8}" if len(v) > 8 else "") for tk, v in sorted(por_tk.items())]
    return L


def _sanidade(sa):
    rs = sa["resumo"]
    L = ["", "## Sanidade econômica (camada 5)",
          f"{rs['n']} empresas dos lotes ({rs['n_erro']} com erro explícito do motor) · P/C mediano {_num(rs['pc_mediana'])} "
          f"(Q1 {_num(rs['pc_q1'])}, Q3 {_num(rs['pc_q3'])}) · {rs['acima_3x']} acima de 3× · "
          f"Ke nominal da casa − Ke implícito (mediana) {_pct(rs['ke_gap_mediano'])}"]
    L += [f"- BLOQUEANTE: {b}" for b in sa["bloqueantes"]]
    L += [f"- bandeira: {b}" for b in sa["bandeiras"]]
    L += [f"- erro explícito: {l['ticker']}: {l['erro']}" for l in sa["erros"]]
    if rs["compounders_caros"]:
        L += ["", "Compounders caros (emenda 1: ROIC alto e estável, P/C > 2):", "",
              "| ticker | P/C | ROIC contábil | menor ROIC | WACC nom. | Ke real | Ke implícito | g real |", "|---|---|---|---|---|---|---|---|"]
        for c in rs["compounders_caros"]:
            L.append(f"| {c['ticker']} | {_num(c['pc'])} | {_pct(c['roic'])} | {_pct(c['roic_filtro'])} | {_pct(c['wacc'])} | "
                     f"{_pct(c['ke_real'])} | {_pct(c['ke_implicito'])} | {_pct(c['g_real'])} |")
    return L


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    completo, gravar = "--completo" in argv, "--sem-gravar" not in argv
    if str(FERRAMENTAS) not in sys.path:
        sys.path.insert(0, str(FERRAMENTAS))
    hoje = dt.date.today().isoformat()
    meta = dict(commit=_commit(), golden_sha=hashlib.sha256(GOLDEN.read_bytes()).hexdigest()[:12], doutrina=_doutrina(),
                completo=completo)
    res = {}
    # a sanidade roda antes da reconciliação: a palavra que decide se uma divergência bloqueia é a do motor agora
    for nome, f in (("rastreabilidade", rastreabilidade), ("propriedades", lambda: propriedades(completo)),
                    ("sanidade", sanidade), ("reconciliacao", lambda: reconciliacao(res.get("sanidade", {}).get("palavras")))):
        print(f"[oráculo] {nome}…", flush=True)
        try:
            res[nome] = f()
        except Exception as ex:           # o conferente que quebra é falha, nunca "ok" por omissão
            res[nome] = dict(status="falha", erro=f"{type(ex).__name__}: {ex}")
        print(f"[oráculo] {nome}: {res[nome]['status']}", flush=True)
    falhos = [k for k in BLOQUEANTES if res[k]["status"] == "falha"]
    linha = dict(data=hoje, commit=meta["commit"], golden_sha=meta["golden_sha"], doutrina=meta["doutrina"],
                 perfil="completo" if completo else "curto", checks={k: res[k]["status"] for k in BLOQUEANTES},
                 bloqueantes_falhos=falhos)
    try:
        md = relatorio(hoje, meta, res)
    except Exception as ex:
        md = f"# Oráculo automático — {hoje}\n\nrelatório não montado ({type(ex).__name__}: {ex})\n{json.dumps(linha, ensure_ascii=False)}\n"
    if gravar:
        SAIDA.mkdir(parents=True, exist_ok=True)
        (SAIDA / f"{hoje}.md").write_text(md, encoding="utf-8", newline="\n")
        with open(SAIDA / "registro.jsonl", "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(linha, ensure_ascii=False) + "\n")
        print(f"[oráculo] gravado docs/oraculo/{hoje}.md e uma linha em docs/oraculo/registro.jsonl")
    else:
        print(md)
    print(json.dumps(linha, ensure_ascii=False))
    return 1 if falhos else 0


if __name__ == "__main__":
    raise SystemExit(main())
