"""O caso de um ticker: empresa (premissas), resultado do motor, mercado, preço e de onde veio.

Ordem: ticker com ficha de dossiê → o dossiê (veredito revisado, regra 11, dados A da CVM/B3); senão, ticker do hall → o
lote. Os dois chamam o MESMO motor; nada aqui recalcula conta. A data-base do dossiê é a do último veredito gravado
(`dossie/vereditos/<TK>-<data>.json`); a do lote é a do hall (`precos_hall.PRECO_DATA`).
"""
from __future__ import annotations

import importlib
import json
import pathlib

AQUI = pathlib.Path(__file__).resolve().parent
VEREDITOS = AQUI.parent / "dossie" / "vereditos"


def datas_do_dossie(tk: str) -> list[str]:
    return sorted(p.stem[len(tk) + 1:] for p in VEREDITOS.glob(f"{tk}-*.json"))


def veredito_gravado(tk: str, data: str) -> dict | None:
    arq = VEREDITOS / f"{tk}-{data}.json"
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else None


def _do_dossie(tk: str, data: str | None) -> dict:
    from dossie import base, gerar
    data = data or (datas_do_dossie(tk) or [base.DATA_BASE])[-1]
    with base.na_data(data) as d, base.isolado(tk):      # proventos do dossiê não vazam para os lotes (base.isolado)
        c = gerar._calcular(tk)
        emp = importlib.import_module(gerar.FICHAS[tk]).empresa()
        mk, preco = base.mercado(d), base.preco(tk, d)
    return dict(tk=tk, origem="dossiê", lote=None, empresa=emp, r=c["r"], mk=mk, preco=preco, data=d, dossie=c,
                financeira=False, gravado=veredito_gravado(tk, d))


def _do_lote(tk: str) -> dict:
    import precos_hall
    import universo
    it = universo.avaliar_todos()[tk]
    emp = it["empresa"]
    return dict(tk=tk, origem=f"hall, lote {it['lote']}", lote=it["lote"], empresa=emp, r=it["r"], mk=universo.MK,
                preco=emp.preco, data=precos_hall.PRECO_DATA, dossie=None, financeira=hasattr(emp, "roe_lp"), gravado=None)


def caso(tk: str, data: str | None = None) -> dict:
    tk = tk.strip().upper()
    from dossie import gerar
    if tk in gerar.FICHAS:
        return _do_dossie(tk, data)
    import universo
    tks = {e.ticker for _, emps, _ in universo.GRUPOS for e in emps}
    if tk not in tks:
        raise KeyError(f"{tk}: fora do hall (41) e sem ficha de dossiê — precisa de ficha em dossie/fichas/ "
                       f"(coleta CVM, CNPJ, insumos com fonte A/B) antes do relatório")
    if data:
        raise ValueError(f"{tk} é do hall: a data-base é a do hall ({__import__('precos_hall').PRECO_DATA}); "
                         "outra data só com ficha de dossiê")
    return _do_lote(tk)
