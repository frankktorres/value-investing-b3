"""Registro prospectivo da FILA da triagem — mede depois se a triagem escolhe melhor que o acaso.

Mesmas regras de `registro_prospectivo.py`: append-only, uma linha JSON por (data da triagem,
ticker); registrar de novo a mesma data com outro valor LEVANTA erro. Vai para o git
(`prospectivo/triagem.jsonl`): é evidência, não cache.

Avaliação DECLARADA AGORA (06/10/2026), antes de existir resultado:
  · horizonte 1 ano a partir de `data_preco`, retorno total pela máquina de
    `backtest/precos/retorno.py`;
  · a fila (camadas A e B juntas, e A sozinha) contra o Ibovespa total e contra as 41 do hall no
    mesmo período: retorno mediano e % que bateu o Ibovespa;
  · leitura só com >= 4 datas de triagem com 1 ano vencido. Sem palavra: a triagem não é veredito.
"""
from __future__ import annotations

import datetime as dt
import json
import math
from pathlib import Path

from .config import hash_config

REGISTRO = Path(__file__).resolve().parent.parent / "prospectivo" / "triagem.jsonl"
CAMPOS = ("posicao", "camada", "preco", "pc_proxy", "ey", "n_ok", "config")


def _f(x):
    """None = sem dado; "inf" = EV <= 0 com EBIT positivo (caixa acima do valor de mercado)."""
    if isinstance(x, float) and math.isinf(x):
        return "inf" if x > 0 else "-inf"
    return None if x is None or (isinstance(x, float) and math.isnan(x)) else round(float(x), 4)


def linhas(r, hoje: str) -> list[dict]:
    from .fila import camada, n_ok
    cfg = hash_config(r.cfg)
    return [{"data_preco": r.T, "ticker": x["ticker"], "posicao": i, "camada": camada(x),
             "preco": _f(x["preco"]), "pc_proxy": _f(x["pc"]) if x.get("confiavel") else None,
             "ey": _f(x.get("ey")), "n_ok": n_ok(x), "config": cfg, "registrado_em": hoje}
            for i, x in enumerate(r.fila, 1)]


def ler(caminho: Path = REGISTRO) -> list[dict]:
    if not caminho.exists():
        return []
    return [json.loads(x) for x in caminho.read_text(encoding="utf-8").splitlines() if x.strip()]


def registrar(r, caminho: Path = REGISTRO, hoje: str | None = None) -> int:
    novas = linhas(r, hoje or dt.date.today().isoformat())
    existentes = {(l["data_preco"], l["ticker"]): l for l in ler(caminho)}
    a_gravar = []
    for l in novas:
        velho = existentes.get((l["data_preco"], l["ticker"]))
        if velho is None:
            a_gravar.append(l)
        elif {k: velho.get(k) for k in CAMPOS} != {k: l[k] for k in CAMPOS}:
            raise ValueError(f"{l['ticker']} em {l['data_preco']} já registrado com outro valor — "
                             "registro é append-only; use outra data de preço")
    if a_gravar:
        caminho.parent.mkdir(exist_ok=True)
        with caminho.open("a", encoding="utf-8", newline="\n") as f:
            for l in a_gravar:
                f.write(json.dumps(l, ensure_ascii=False, sort_keys=True) + "\n")
    return len(a_gravar)
