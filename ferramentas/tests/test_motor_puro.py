"""Trava 4.5 (pacote de autonomia, 25/11/2026): motor puro.

`motor_*.py` calcula; não busca na rede, não lê o relógio, não lê nem grava arquivo. Relógio ou rede dentro do motor
tornam o mesmo insumo capaz de dar palavra diferente em dias diferentes (fere o point-in-time e o golden). A leitura que
já existe (motor_nao_financeiras: `derivados_zip.json` no import) fica na catraca `motor_puro_catraca.json`: só cai.
Canário: fonte sintética com cada construção proibida é reprovada; fonte limpa passa.
"""
from __future__ import annotations

import ast
import json
import pathlib

import pytest

AQUI = pathlib.Path(__file__).resolve().parent.parent
CATRACA = pathlib.Path(__file__).with_name("motor_puro_catraca.json")

MODULOS = {  # raiz do import -> família
    **dict.fromkeys(("socket", "ssl", "urllib", "http", "requests", "httpx", "aiohttp", "ftplib", "smtplib"), "rede"),
    **dict.fromkeys(("subprocess", "os", "shutil", "tempfile", "sqlite3"), "processo/sistema"),
    "time": "relógio",
}
RELOGIO = {"now", "today", "utcnow"}                         # datetime.now(), date.today(), datetime.utcnow()
ARQUIVO = {"read_text", "write_text", "read_bytes", "write_bytes", "unlink", "mkdir", "touch",
           "read_csv", "read_parquet", "read_excel", "read_json", "to_csv", "to_parquet", "to_excel", "to_json"}


def impurezas(fonte: str) -> list[tuple[int, str]]:
    """[(linha, família)] das construções impuras na fonte."""
    achados = []
    for no in ast.walk(ast.parse(fonte)):
        if isinstance(no, ast.Import):
            for a in no.names:
                fam = MODULOS.get(a.name.split(".")[0])
                if fam:
                    achados.append((no.lineno, f"import {a.name} ({fam})"))
        elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
            fam = MODULOS.get(no.module.split(".")[0])
            if fam:
                achados.append((no.lineno, f"from {no.module} ({fam})"))
        elif isinstance(no, ast.Call):
            f = no.func
            if isinstance(f, ast.Name) and f.id == "open":
                achados.append((no.lineno, "open (arquivo)"))
            elif isinstance(f, ast.Attribute):
                if f.attr in RELOGIO:
                    achados.append((no.lineno, f".{f.attr}() (relógio)"))
                elif f.attr in ARQUIVO or (f.attr == "open" and not isinstance(f.value, ast.Name)):
                    achados.append((no.lineno, f".{f.attr}() (arquivo)"))
    return sorted(achados)


def _contagem(achados):
    cont: dict[str, int] = {}
    for _, fam in achados:
        cont[fam] = cont.get(fam, 0) + 1
    return cont


@pytest.mark.parametrize("fonte", [
    "import requests",
    "from urllib.request import urlopen",
    "import subprocess",
    "import os",
    "import time",
    "from datetime import datetime\nx = datetime.now()",
    "import datetime\nx = datetime.date.today()",
    "x = open('a.txt').read()",
    "import pathlib\npathlib.Path('a').read_text()",
    "import pandas as pd\npd.read_csv('a.csv')",
    "df.to_parquet('x')",
])
def test_canario_construcao_proibida_e_reprovada(fonte):
    assert impurezas(fonte), fonte


def test_canario_fonte_limpa_passa():
    assert impurezas("import math\nfrom statistics import median\ndef f(x):\n    return math.sqrt(median(x))\n") == []


def test_motores_sem_impureza_nova():
    catraca = json.loads(CATRACA.read_text(encoding="utf-8"))["por_arquivo"]
    motores = sorted(AQUI.glob("motor_*.py"))
    assert motores, "nenhum motor_*.py encontrado"
    subiu, caiu = [], []
    for m in motores:
        achados = impurezas(m.read_text(encoding="utf-8"))
        atual, limite = _contagem(achados), catraca.get(m.name, {})
        for fam, n in atual.items():
            if n > limite.get(fam, 0):
                subiu.append(f"{m.name}: {fam} = {n} (catraca {limite.get(fam, 0)}); linhas "
                             f"{[ln for ln, f in achados if f == fam]}")
        for fam, n in limite.items():
            if atual.get(fam, 0) < n:
                caiu.append(f"{m.name}: {fam} caiu para {atual.get(fam, 0)} (catraca {n})")
    assert not subiu, "motor impuro (rede, relógio ou arquivo) — passe o dado como argumento:\n" + "\n".join(subiu)
    assert not caiu, "impureza removida: baixe a catraca em tests/motor_puro_catraca.json:\n" + "\n".join(caiu)
