"""Teste das armadilhas do oráculo automático (docs/ORACULO.md §2).

    cd ferramentas && python -m oraculo.armadilhas            # todas; grava docs/oraculo/armadilhas-AAAA-MM-DD.md + registro.jsonl
    python -m oraculo.armadilhas --so 01,04 --manter          # só essas; mantém os worktrees (o agente `oraculo` lê de lá)
Cada patch é aplicado num `git worktree` do HEAD em pasta temporária, nunca na árvore de trabalho. No worktree: o hall.json
(ignorado pelo git) é copiado, os ZIPs da CVM são lidos do repositório principal (ORACULO_DADOS_CVM), o golden é regravado como um
autor faria (a camada 0 não conta) e rodam a suíte (`-x`) e o `python -m oraculo --sem-gravar`. Pegou = algum dos dois saiu ≠ 0.
Para o agente às cegas ficam, fora do worktree, `mudanca.diff` (o diff completo, com o golden) e `saida_oraculo.md`.
Sai com 1 se o automático deixar passar alguma armadilha da sua alçada.
"""
from __future__ import annotations

import concurrent.futures as cf
import datetime as dt
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

from oraculo.armadilhas import ARMADILHAS

AQUI = pathlib.Path(__file__).resolve().parent
FERRAMENTAS = AQUI.parent.parent
RAIZ = FERRAMENTAS.parent
HALL = pathlib.Path("ferramentas/painel/web/dados/hall.json")
SAIDA = RAIZ / "docs" / "oraculo"


def _run(cmd, cwd, env=None, timeout=3600):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def _palavras(golden: dict) -> dict:
    return {tk: d.get("palavra") for tk, d in golden.get("tickers", {}).items()}


def rodar_uma(a: dict, base: pathlib.Path, manter: bool) -> dict:
    pasta = base / f"mudanca_{a['id']}"
    repo = pasta / "repo"
    pasta.mkdir(parents=True)
    rc, out = _run(["git", "worktree", "add", "--detach", str(repo), "HEAD"], RAIZ)
    if rc:
        return dict(a, erro=f"worktree: {out[-300:]}")
    try:
        (repo / HALL).parent.mkdir(parents=True, exist_ok=True)
        if (RAIZ / HALL).is_file():
            shutil.copy2(RAIZ / HALL, repo / HALL)
        if (repo / "ferramentas" / "oraculo" / "armadilhas").is_dir():      # às cegas: o agente lê este repositório
            shutil.rmtree(repo / "ferramentas" / "oraculo" / "armadilhas")
        rc, out = _run(["git", "apply", "--whitespace=nowarn", str(AQUI / a["patch"])], repo)
        if rc:
            return dict(a, erro=f"git apply: {out[-300:]}")
        env = dict(os.environ, PYTHONIOENCODING="utf-8", CLAUDE_NO_SUITE_LOG="1",
                   ORACULO_DADOS_CVM=str(FERRAMENTAS / "dados" / "cvm"))
        fer = repo / "ferramentas"
        antes = _palavras(json.loads((FERRAMENTAS / "tests" / "golden.json").read_text(encoding="utf-8")))
        if "tests/golden.json" not in (AQUI / a["patch"]).read_text(encoding="utf-8"):
            rc, out = _run([sys.executable, "-m", "tests.regerar_golden", "--motivo",
                            "mudança em avaliação: golden regravado para a suíte comparar o resto"], fer, env)
            if rc:
                return dict(a, erro=f"golden: {out[-300:]}")
        depois = _palavras(json.loads((fer / "tests" / "golden.json").read_text(encoding="utf-8")))
        trocas = {tk: f"{antes.get(tk)} → {p}" for tk, p in depois.items() if antes.get(tk) != p}
        rc_s, out_s = _run([sys.executable, "-m", "pytest", "--ignore=backtest", "-x", "-q", "-p", "no:cacheprovider",
                            "--tb=line"], fer, env)
        rc_o, out_o = _run([sys.executable, "-m", "oraculo", "--sem-gravar"], fer, env)
        _, diff = _run(["git", "diff", "--", ".", ":(exclude)ferramentas/oraculo/armadilhas"], repo)
        (pasta / "mudanca.diff").write_text(diff, encoding="utf-8", newline="\n")
        (pasta / "saida_oraculo.md").write_text(
            out_o + "\n\n## Suíte (`pytest --ignore=backtest -x`)\n" + "\n".join(out_s.splitlines()[-12:]) +
            "\n\n## Palavras que mudam (golden antes × depois)\n" +
            ("\n".join(f"- {tk}: {t}" for tk, t in sorted(trocas.items())) or "- nenhuma") + "\n", encoding="utf-8", newline="\n")
        falhou = next((x for x in out_s.splitlines() if x.startswith(("FAILED", "ERROR"))), "")
        bloq = next((x for x in out_o.splitlines() if x.startswith("{")), "")
        return dict(a, pegou_suite=rc_s != 0, pegou_oraculo=rc_o != 0, primeira_falha=falhou[:240],
                    oraculo=json.loads(bloq).get("bloqueantes_falhos") if bloq else None, trocas=trocas, pasta=str(pasta))
    finally:
        if not manter:
            _run(["git", "worktree", "remove", "--force", str(repo)], RAIZ)


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    so = set(argv[argv.index("--so") + 1].split(",")) if "--so" in argv else None
    manter, gravar = "--manter" in argv, "--sem-gravar" not in argv
    lista = [a for a in ARMADILHAS if so is None or a["id"] in so]
    base = pathlib.Path(tempfile.mkdtemp(prefix="oraculo_mudancas_"))
    print(f"[armadilhas] {len(lista)} em {base}", flush=True)
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        res = list(ex.map(lambda a: rodar_uma(a, base, manter), lista))
    _run(["git", "worktree", "prune"], RAIZ)
    linhas, deixou = [], []
    for r in res:
        pegou = bool(r.get("pegou_suite") or r.get("pegou_oraculo"))
        if "automatico" in r["alcada"] and not pegou:
            deixou.append(r["id"])
        linhas.append(f"| {r['id']} | {r['defeito']} | {r['camada']} | {', '.join(r['alcada'])} | "
                      + (f"erro: {r['erro']} | | | |" if "erro" in r else
                         f"{'sim' if r['pegou_suite'] else 'não'} | {'sim' if r['pegou_oraculo'] else 'não'} "
                         f"({', '.join(r['oraculo'] or []) or '—'}) | {r['primeira_falha'] or '—'} | "
                         f"{'; '.join(f'{k} {v}' for k, v in sorted(r['trocas'].items())) or 'nenhuma'} |"))
        print(f"[armadilhas] {r['id']}: " + ("ERRO " + r["erro"] if "erro" in r else
                                            f"suíte {'pegou' if r['pegou_suite'] else 'passou'}, oráculo "
                                            f"{'pegou' if r['pegou_oraculo'] else 'passou'} {r.get('oraculo')}"), flush=True)
    erros = [r["id"] for r in res if "erro" in r]
    ok = not deixou and not erros
    hoje = dt.date.today().isoformat()
    md = "\n".join([
        f"# Teste das armadilhas do oráculo automático — {hoje}", "",
        "Gerado por `cd ferramentas && python -m oraculo.armadilhas` (docs/ORACULO.md §2). Automático = suíte (golden regravado no "
        "worktree; camada 0 não conta) + `python -m oraculo`. Alçada decidida antes de medir.", "",
        f"**Automático: {'pegou 100% da sua alçada' if ok else 'deixou passar ' + ', '.join(deixou + erros)}.**", "",
        "| # | defeito | camada | alçada | suíte pegou | oráculo pegou (checks) | 1ª falha da suíte | palavras que mudam |",
        "|---|---|---|---|---|---|---|---|", *linhas, ""])
    if gravar:
        SAIDA.mkdir(parents=True, exist_ok=True)
        (SAIDA / f"armadilhas-{hoje}.md").write_text(md, encoding="utf-8", newline="\n")
        _, commit = _run(["git", "rev-parse", "--short", "HEAD"], RAIZ)
        with open(SAIDA / "registro.jsonl", "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(dict(tipo="armadilhas", data=hoje, commit=commit.strip(), automatico_100=ok,
                                     resultados={r["id"]: dict(alcada=list(r["alcada"]), pegou_suite=r.get("pegou_suite"),
                                                               pegou_oraculo=r.get("pegou_oraculo"), erro=r.get("erro"))
                                                 for r in res}), ensure_ascii=False) + "\n")
    print(md)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
