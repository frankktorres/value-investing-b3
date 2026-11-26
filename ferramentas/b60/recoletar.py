"""B60 — recoleta INTEIRA das séries do dossiê coletadas em 02/10 (antes da AUD-68). Uso, de `ferramentas/`:

    python -m b60.recoletar conferir   # recoleta num temporário e mostra o diff campo a campo; não grava nada
    python -m b60.recoletar gravar     # idem e substitui a série dos tickers ALVO (a antiga vai para `_historico/`)

Varredura de 26/11/2026 (hall 31, dossiê 6, B36 19): só a CMIN3 tem `lucro_controlador` = 0 com lucro ≠ 0 (2022–24), e só
CMIN3 e BLAU3 estão no formato antigo (sem `ltm_ref`, coleta de 02/10). As duas são recoletadas pelo coletor de hoje no mesmo
mês do ITR (jun/2026). Diferente da B57 (aditiva), aqui a série é TROCADA: só os campos de ALTERACOES_ESPERADAS podem mudar
de valor; campo novo do formato de hoje (ex.: `proventos_a_pagar`, `ltm`, `ltm_ref`) é acrescentado; qualquer outra
divergência → nada é gravado.
"""
from __future__ import annotations

import json
import pathlib
import shutil
import sys
import tempfile

AQUI = pathlib.Path(__file__).resolve().parent
FERRAMENTAS = AQUI.parent
if str(FERRAMENTAS) not in sys.path:
    sys.path.insert(0, str(FERRAMENTAS))

import coletar_cvm  # noqa: E402

ARQ = FERRAMENTAS / "dossie" / "dados" / "cvm_series_dossie.json"
ALVO = ("CMIN3", "BLAU3")
ANO_ITR, MES = 2026, 6          # o LTM que a série antiga já tem (ltm_2T26)
DATA = "2026-11-26"
# Mudança de VALOR explicada (AUD-68): 3.11.01 = 0 com lucro ≠ 0 vira None (o motor cai no lucro consolidado) e as ações
# do `ltm_2T26` passam a ser as do ITR (o motor da CMIN3 já usava `base.acoes_itr`; 54,27 bi era o DFP lido em unidade errada)
ALTERACOES_ESPERADAS = {
    "CMIN3": {"/anual/2022/lucro_controlador", "/anual/2023/lucro_controlador", "/anual/2024/lucro_controlador",
              "/ltm_2T26/acoes"},
    "BLAU3": set(),
}


def recoletar(tk: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        arq = pathlib.Path(tmp) / "s.json"
        coletar_cvm.main([tk], arq=arq, ano_itr=ANO_ITR, mes=MES)
        return json.loads(arq.read_text(encoding="utf-8"))[tk]


def diff(velho, novo, caminho: str = "") -> tuple[list[str], list[str]]:
    """(valores que mudaram, campos que só a recoleta tem)."""
    mudou, novos = [], []
    for k in sorted(set(velho) | set(novo)):
        c = f"{caminho}/{k}"
        if k not in velho:
            novos.append(c)
        elif k not in novo:
            mudou.append(f"{c}: {velho[k]!r} → <some>")
        elif isinstance(velho[k], dict) and isinstance(novo[k], dict):
            m, n = diff(velho[k], novo[k], c)
            mudou += m
            novos += n
        elif velho[k] != novo[k]:
            mudou.append(f"{c}: {velho[k]!r} → {novo[k]!r}")
    return mudou, novos


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    a = list(argv if argv is not None else sys.argv[1:])
    if a not in (["conferir"], ["gravar"]):
        print(__doc__)
        return 2
    series = json.loads(ARQ.read_text(encoding="utf-8"))
    ok, saida = True, dict(series)
    for tk in ALVO:
        novo = recoletar(tk)
        mudou, novos = diff(series[tk], novo)
        fora = [x for x in mudou if x.split(":")[0] not in ALTERACOES_ESPERADAS[tk]]
        ok &= not fora
        print(f"== {tk}: {len(mudou)} valor(es) mudado(s), {len(novos)} campo(s) novo(s), {len(fora)} fora do esperado")
        for x in mudou:
            print("   ", "FORA" if x in fora else "ok  ", x)
        print("    novos:", ", ".join(novos))
        saida[tk] = novo
    if a[0] == "gravar" and ok:
        hist = ARQ.parent / "_historico"
        hist.mkdir(exist_ok=True)
        destino, n = hist / f"{ARQ.stem}_{DATA}_antes_B60{ARQ.suffix}", 2
        while destino.exists():
            destino, n = hist / f"{ARQ.stem}_{DATA}_antes_B60_{n}{ARQ.suffix}", n + 1
        shutil.copy2(ARQ, destino)
        ARQ.write_text(json.dumps(saida, ensure_ascii=False, indent=1), encoding="utf-8")
        print("gravado; antiga em", destino.name)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
