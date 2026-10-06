"""Registro prospectivo dos vereditos — a validação da régua que o backtest não conseguiu fazer.

Por que existe (decisão de 06/10/2026, depois do portão do proxy reprovado na Etapa 3): a régua
depende de julgamento digitado à mão (receita de meio de ciclo, janela, cenários, desconto do
controlador), e nenhum motor mecânico a reproduziu nos 41 do golden (±1 nível 70,7%, mediana
|ΔP/C| 0,34). Um backtest de 2014–2025 testaria outra régua. A única validação fora da amostra que
sobra é registrar o veredito HOJE, com o preço de hoje, e medir depois.

Regras:
  · append-only: uma linha JSON por (data do preço, ticker); nunca editar nem apagar. Registrar de
    novo a mesma data com outro valor LEVANTA erro — correção é nova rodada com nova data;
  · registra o golden aprovado (o estado que passou no `rodar_tudo.py`), com o sha do golden e a
    versão da doutrina — a régua que produziu cada linha fica identificável;
  · vai para o git (`prospectivo/registro.jsonl`), não para `dados/`: é evidência, não cache.

Avaliação DECLARADA AGORA, antes de existir resultado (mudar depois = olhar o resultado):
  · horizonte principal 1 ano, direção em 3 anos, a partir de `data_preco`;
  · retorno total (proventos brutos reinvestidos, eventos ajustados) pela máquina de
    `backtest/precos/retorno.py`, contra o Ibovespa total no mesmo período;
  · tabela por palavra (BARATA, RADAR, JUSTA, CARA): retorno mediano e % que bateu o Ibovespa;
  · a pergunta é ordinal: BARATA/RADAR ganham de CARA? Um único registro não decide nada — a
    leitura começa quando houver >= 4 datas de registro com horizonte de 1 ano vencido.

Uso: python registro_prospectivo.py --data-preco 2026-10-02 --doutrina v2.2
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import pathlib
import sys

AQUI = pathlib.Path(__file__).parent
GOLDEN = AQUI / "tests" / "golden.json"
REGISTRO = AQUI / "prospectivo" / "registro.jsonl"
CAMPOS = ("palavra", "pc", "central", "lote")


def linhas_do_golden(golden: dict, data_preco: str, doutrina: str, sha: str,
                     hoje: str) -> list[dict]:
    out = []
    for tk in sorted(golden["tickers"]):
        g = golden["tickers"][tk]
        pc, central = g["pc"], g["central"]
        # o golden guarda pc e central arredondados: o produto volta com ruído de float
        preco = round(pc * central, 2) if math.isfinite(pc) else None
        out.append({"data_preco": data_preco, "ticker": tk, "preco": preco,
                    **{c: (None if isinstance(g[c], float) and math.isinf(g[c]) else g[c])
                       for c in CAMPOS},
                    "doutrina": doutrina, "golden_sha": sha, "registrado_em": hoje})
    return out


def ler(caminho: pathlib.Path = REGISTRO) -> list[dict]:
    if not caminho.exists():
        return []
    return [json.loads(x) for x in caminho.read_text(encoding="utf-8").splitlines() if x.strip()]


def registrar(data_preco: str, doutrina: str, golden_path: pathlib.Path = GOLDEN,
              caminho: pathlib.Path = REGISTRO, hoje: str | None = None) -> int:
    """Acrescenta a rodada. Devolve quantas linhas novas; 0 se a rodada já estava idêntica."""
    bruto = golden_path.read_bytes()
    sha = hashlib.sha256(bruto).hexdigest()[:16]
    novas = linhas_do_golden(json.loads(bruto.decode("utf-8")), data_preco, doutrina, sha,
                             hoje or dt.date.today().isoformat())
    existentes = {(l["data_preco"], l["ticker"]): l for l in ler(caminho)}
    a_gravar = []
    for l in novas:
        velho = existentes.get((l["data_preco"], l["ticker"]))
        if velho is None:
            a_gravar.append(l)
        elif {k: velho[k] for k in (*CAMPOS, "preco", "golden_sha")} != \
                {k: l[k] for k in (*CAMPOS, "preco", "golden_sha")}:
            raise ValueError(f"{l['ticker']} em {data_preco} já registrado com outro valor — "
                             "registro é append-only; use outra data de preço")
    if a_gravar:
        caminho.parent.mkdir(exist_ok=True)
        with caminho.open("a", encoding="utf-8", newline="\n") as f:
            for l in a_gravar:
                f.write(json.dumps(l, ensure_ascii=False, sort_keys=True) + "\n")
    return len(a_gravar)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Registro prospectivo dos vereditos do golden")
    ap.add_argument("--data-preco", required=True, help="pregão de fechamento dos preços (AAAA-MM-DD)")
    ap.add_argument("--doutrina", required=True, help="versão da doutrina, ex.: v2.2")
    a = ap.parse_args(argv)
    n = registrar(a.data_preco, a.doutrina)
    print(f"{n} linhas novas em {REGISTRO.relative_to(AQUI)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
