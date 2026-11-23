"""Verificador de datas fixas no código dos lotes (23/11/2026; usado por `test_lotes_sem_data_fixa.py`).

Lê a árvore do código (AST): comentário e docstring não contam; string com espaço é prosa (fonte, razão) e só conta se
parecer código (tem "==" ou "DT_").
  · ZERO — tolerância zero (quebra calada a cada trimestre novo):
      - string com data de mês/dia/trimestre em qualquer posição: "2025-07", "precos_2026-06-30.csv", "02/10/2026",
        "30/06/26", "06/2026", "jul/26", "3T26", "2026Q2", "20260630", e pedaço de f-string "-06-30";
      - número AAAAMM ou AAAAMMDD válido (202606, 20260630);
      - chamada ou tupla/lista com ano seguido de mês: itr_ytd(tk, 2026, 6), date(2026, 6, 30), ("2025", "12", "01");
      - comparação de mês "01"–"12" com fatia de data (df["DT_REFER"].str[5:7] == "06");
      - nome com mês+ano ou trimestre: EGIE_DIV_AGO26, acoes_jun26=..., N_3T26.
  · ANO — número inteiro 2010–2035 ou string sem espaço com ano ("2025", "itr_2026.zip"): catraca que só cai
    (`datas_fixas_catraca.json`; missão B32, prazo 31/01/2027, antes do DFP 2026).
"""
from __future__ import annotations

import ast
import pathlib
import re

AQUI = pathlib.Path(__file__).resolve().parent.parent
MESES = "jan|fev|mar|abr|mai|jun|jul|ago|set|out|nov|dez"
_ANO = r"20[1-3]\d"
ZERO = [re.compile(p, re.I) for p in (
    rf"{_ANO}-[01]\d",                                   # AAAA-MM(-DD) em qualquer posição
    r"(?<!\d)[0-3]?\d/[01]?\d/(\d{2}|\d{4})(?!\d)",      # dd/mm/aa(aa)
    rf"(?<!\d)(0[1-9]|1[0-2])/{_ANO}(?!\d)",             # mm/aaaa
    rf"(?<![a-z])({MESES})/(20)?[1-3]\d(?!\d)",          # jul/26, jul/2026
    r"(?<![a-z0-9])[1-4]T[1-3]\d(?![0-9])",              # 3T26
    rf"{_ANO}Q[1-4]",                                    # 2026Q2
    rf"(?<!\d){_ANO}[01]\d[0-3]\d(?!\d)",                # 20260630
    rf"(?<![a-z])({MESES})_?(2\d|3[0-5])(?![a-z0-9])",   # acoes_jun26, AGO26
    r"^[-/][01]\d([-/][0-3]\d)?$",                       # pedaço de f-string: f"{ano}-06-30"
)]
ANO = re.compile(r"(?<!\d)20[1-3]\d(?!\d)")
NOME = [re.compile(rf"(?<![a-z])({MESES})_?(2\d|3[0-5])(?![a-z0-9])", re.I), re.compile(r"(?<![a-z0-9])[1-4]T[1-3]\d(?![0-9])", re.I)]
_MES = re.compile(r"^(0[1-9]|1[0-2])$")


def arquivos_dos_lotes() -> list[pathlib.Path]:
    return sorted(p for p in AQUI.glob("lote[0-9]_*.py") if not p.name.endswith("_textos.py"))


def _docstrings(arvore) -> set[int]:
    ids = set()
    for n in ast.walk(arvore):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and n.body:
            p = n.body[0]
            if isinstance(p, ast.Expr) and isinstance(p.value, ast.Constant) and isinstance(p.value.value, str):
                ids.add(id(p.value))
    return ids


def _e_ano(n) -> bool:
    v = getattr(n, "value", None) if isinstance(n, ast.Constant) else None
    return (isinstance(v, int) and not isinstance(v, bool) and 2010 <= v <= 2035) or (isinstance(v, str) and bool(re.fullmatch(_ANO, v)))


def _e_mes(n) -> bool:
    v = getattr(n, "value", None) if isinstance(n, ast.Constant) else None
    return (isinstance(v, int) and not isinstance(v, bool) and 1 <= v <= 12) or (isinstance(v, str) and bool(_MES.match(v)))


def _aaaamm(v: int) -> bool:
    s = str(v)
    if len(s) == 6:
        return 2010 <= v // 100 <= 2035 and 1 <= v % 100 <= 12
    if len(s) == 8:
        return 2010 <= v // 10000 <= 2035 and 1 <= v // 100 % 100 <= 12 and 1 <= v % 100 <= 31
    return False


def _tem_fatia(n) -> bool:
    return any(isinstance(x, ast.Subscript) and isinstance(x.slice, ast.Slice) for x in ast.walk(n))


def _nomes(n):
    if isinstance(n, ast.Name):
        yield n.id
    elif isinstance(n, ast.Attribute):
        yield n.attr
    elif isinstance(n, ast.keyword) and n.arg:
        yield n.arg
    elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        yield n.name
    elif isinstance(n, ast.arg):
        yield n.arg
    elif isinstance(n, ast.alias):
        yield n.asname or n.name


def achados(fonte: str) -> dict[str, list[tuple[int, object]]]:
    """{"zero": [(linha, valor)], "ano": [...]} do código-fonte dado."""
    arvore = ast.parse(fonte)
    docs = _docstrings(arvore)
    out = {"zero": [], "ano": []}
    vistos: set[int] = set()        # constante já contada como ZERO por regra estrutural não conta de novo como ANO

    for n in ast.walk(arvore):
        linha = getattr(n, "lineno", 0)
        for nome in _nomes(n):
            if any(p.search(nome) for p in NOME):
                out["zero"].append((linha, nome))
        seqs = []
        if isinstance(n, ast.Call):
            seqs.append(n.args)
        if isinstance(n, (ast.Tuple, ast.List)):
            seqs.append(n.elts)
        for seq in seqs:
            for a, b in zip(seq, seq[1:]):
                if _e_ano(a) and _e_mes(b):
                    out["zero"].append((linha, f"{a.value}, {b.value}"))
                    vistos.update({id(a), id(b)})
        if isinstance(n, ast.Compare):
            lados = [n.left, *n.comparators]
            for lado in lados:
                if isinstance(lado, ast.Constant) and isinstance(lado.value, str) and _MES.match(lado.value) and \
                        any(_tem_fatia(o) for o in lados if o is not lado):
                    out["zero"].append((linha, lado.value))
                    vistos.add(id(lado))

    for n in ast.walk(arvore):
        if not isinstance(n, ast.Constant) or id(n) in docs or id(n) in vistos:
            continue
        v = n.value
        if isinstance(v, bool):
            continue
        if isinstance(v, int):
            if _aaaamm(v):
                out["zero"].append((n.lineno, v))
            elif 2010 <= v <= 2035:
                out["ano"].append((n.lineno, v))
        elif isinstance(v, str) and v.strip():
            s = v.strip()
            prosa = any(c.isspace() for c in s)
            if prosa and not ("==" in s or "DT_" in s):
                continue
            if any(p.search(s) for p in ZERO):
                out["zero"].append((n.lineno, v))
            elif not prosa and ANO.search(s):
                out["ano"].append((n.lineno, v))
    return out


def varrer() -> dict[str, dict[str, list[tuple[int, object]]]]:
    return {p.name: achados(p.read_text(encoding="utf-8")) for p in arquivos_dos_lotes()}
