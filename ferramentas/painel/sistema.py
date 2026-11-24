"""Contrato da tela Sistema (`web/dados/contrato/sistema.json`, missão N4): a idade de cada dado, o último boletim do monitor e da
temporada, a data e o motivo do golden e a última suíte de testes. Só lê arquivos que já existem — o que faltar vira `None`
com o motivo ("sem registro"), nunca um número inventado. Nada aqui é dado pessoal.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import date
from pathlib import Path

AQUI = Path(__file__).resolve().parent.parent          # ferramentas/
RAIZ = AQUI.parent
SEM_REGISTRO = "sem registro"
SUITE = AQUI / "dados" / "suite_ultima.json"           # gravado pelo conftest ao fim de uma suíte completa (ignorado pelo git)
LINHA_LOG = re.compile(r"^- (\d{4}-\d{2}-\d{2}) (\d{2}:\d{2}) — (.*)$")


def _idade(d: str | None, hoje: str) -> int | None:
    try:
        return None if not d else (date.fromisoformat(hoje) - date.fromisoformat(d[:10])).days
    except ValueError:
        return None


def _item(chave: str, rotulo: str, d: str | None, hoje: str, fonte: str, obs: str = "") -> dict:
    return {"chave": chave, "rotulo": rotulo, "data": d, "idade_dias": _idade(d, hoje), "fonte": fonte,
            "obs": obs if d else (obs + "; " if obs else "") + SEM_REGISTRO}


def _json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _boletim(pasta: Path, sufixo: str) -> dict | None:
    """Último `AAAA-MM-DD-<sufixo>.md` de BOLETINS/ (a data vem do nome)."""
    nomes = sorted(p.name for p in pasta.glob(f"*-{sufixo}.md") if re.match(r"\d{4}-\d{2}-\d{2}-", p.name))
    return {"arquivo": nomes[-1], "data": nomes[-1][:10]} if nomes else None


def dados(hoje: str, ultimo_pregao: str | None, ferramentas: Path = AQUI) -> list[dict]:
    d = ferramentas / "dados"
    out = [_item("cotahist", "Cotações (COTAHIST, B3)", ultimo_pregao, hoje, "último pregão do hall no contrato")]
    man = _json(d / "cvm" / "MANIFESTO.json")
    series = _json(d / "cvm_series.json") or {}
    refs = sorted({v.get("ltm_ref") for v in series.values() if isinstance(v, dict) and v.get("ltm_ref")})
    out.append(_item("cvm", "Demonstrações (CVM, DFP/ITR)", (man or {}).get("atualizado_em"), hoje,
                     "dados/cvm/MANIFESTO.json (última conferência dos ZIPs)",
                     f"LTM de {refs[-1]} nas séries" if refs else ""))
    baixados = sorted(x["baixado_em"] for p in (d / "proventos_hall").glob("*.json")
                      if isinstance(x := _json(p), dict) and x.get("baixado_em"))
    out.append(_item("proventos_b3", "Proventos (API da B3)", baixados[0] if baixados else None, hoje,
                     "dados/proventos_hall/*.json — o arquivo mais antigo",
                     f"{len(baixados)} tickers; o mais novo de {baixados[-1]}" if baixados else ""))
    ult_mon = None
    try:
        with open(ferramentas / "monitor" / "historico.csv", encoding="utf-8", newline="") as f:
            ult_mon = max((r["rodada"] for r in csv.DictReader(f)), default=None)
    except (OSError, KeyError, csv.Error):
        pass
    out.append(_item("monitor", "Monitor semanal (rodada)", ult_mon, hoje, "monitor/historico.csv"))
    temp = _boletim(ferramentas.parent / "BOLETINS", "temporada")
    out.append(_item("temporada", "Temporada (último boletim)", temp and temp["data"], hoje, "BOLETINS/*-temporada.md"))
    return out


def golden(ferramentas: Path = AQUI) -> dict | None:
    """Data (da última linha de `tests/golden_log.md`) e motivo (do próprio `golden.json`) do golden vigente."""
    g = _json(ferramentas / "tests" / "golden.json")
    if not isinstance(g, dict):
        return None
    data = hora = None
    try:
        for ln in (ferramentas / "tests" / "golden_log.md").read_text(encoding="utf-8").splitlines():
            if m := LINHA_LOG.match(ln):
                data, hora = m.group(1), m.group(2)
    except OSError:
        pass
    return {"data": data, "hora": hora, "motivo": g.get("motivo"), "tickers": len(g.get("tickers", {}))}


def suite(arquivo: Path = SUITE) -> dict | None:
    """Resultado da última suíte completa (gravado pelo conftest); sem registro → None."""
    s = _json(arquivo)
    return s if isinstance(s, dict) and "passed" in s else None


def montar(hoje: str, ultimo_pregao: str | None, ferramentas: Path = AQUI, arquivo_suite: Path | None = None) -> dict:
    mon = _boletim(ferramentas.parent / "BOLETINS", "monitor")
    temp = _boletim(ferramentas.parent / "BOLETINS", "temporada")
    return {"versao": 2, "hoje": hoje, "dados": dados(hoje, ultimo_pregao, ferramentas),
            "boletins": {"monitor": mon, "temporada": temp},
            "golden": golden(ferramentas), "suite": suite(arquivo_suite or ferramentas / "dados" / "suite_ultima.json"),
            "avisos": ([] if temp else ["Nenhum boletim de temporada ainda (a tarefa diária começou em 22/10)."])}
