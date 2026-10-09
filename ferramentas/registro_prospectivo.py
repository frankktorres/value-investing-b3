"""Registro prospectivo dos vereditos — a validação da régua que o backtest não conseguiu fazer.

Por que existe (decisão de 06/10/2026, depois do portão do proxy reprovado na Etapa 3): a régua
depende de julgamento digitado à mão (receita de meio de ciclo, janela, cenários, desconto do
controlador), e nenhum motor mecânico a reproduziu nos 41 do golden (±1 nível 70,7%, mediana
|ΔP/C| 0,34). Um backtest de 2014–2025 testaria outra régua. A única validação fora da amostra que
sobra é registrar o veredito HOJE, com o preço de hoje, e medir depois.

Regras:
  · append-only: uma linha JSON por (origem, data do preço, ticker); nunca editar nem apagar. Registrar de
    novo a mesma data com outro valor LEVANTA erro — correção é nova rodada com nova data;
  · a chave é (origem, data do preço, ticker). `origem` = "hall" (golden das 41; linhas antigas sem o
    campo valem "hall"), "dossie" (vereditos de `dossie/vereditos/*.json`, `--dossie`) — o mesmo
    ticker pode estar no hall e no dossiê sem colidir;
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
     python registro_prospectivo.py --dossie     (data do preço e doutrina vêm de cada veredito)
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
VEREDITOS = AQUI / "dossie" / "vereditos"
CAMPOS = ("palavra", "pc", "central", "lote")
COMPARA = (*CAMPOS, "preco", "doutrina")          # + golden_sha só no hall; no dossiê o sha do arquivo é informativo


def sha_arquivo(bruto: bytes) -> str:
    """sha256 (16 hex) do conteúdo com EOL normalizado para LF.

    AUD-108: com core.autocrlf=true o working tree tem CRLF e o blob do git tem LF; o sha do arquivo cru não batia com
    nenhum blob e mudava de máquina para máquina. Normalizado, é o sha do blob (`git show HEAD:caminho | sha256sum`).
    Linhas gravadas antes de 09/10/2026 usam o sha do arquivo cru em CRLF e não são reverificáveis por este caminho.
    """
    return hashlib.sha256(bruto.replace(b"\r\n", b"\n")).hexdigest()[:16]


def linhas_do_golden(golden: dict, data_preco: str, doutrina: str, sha: str,
                     hoje: str) -> list[dict]:
    out = []
    for tk in sorted(golden["tickers"]):
        g = golden["tickers"][tk]
        pc, central = g["pc"], g["central"]
        # o golden guarda pc e central arredondados: o produto volta com ruído de float
        preco = round(pc * central, 2) if math.isfinite(pc) else None
        out.append({"origem": "hall", "data_preco": data_preco, "ticker": tk, "preco": preco,
                    **{c: (None if isinstance(g[c], float) and math.isinf(g[c]) else g[c])
                       for c in CAMPOS},
                    "doutrina": doutrina, "golden_sha": sha, "registrado_em": hoje})
    return out


def ler(caminho: pathlib.Path = REGISTRO) -> list[dict]:
    if not caminho.exists():
        return []
    return [json.loads(x) for x in caminho.read_text(encoding="utf-8").splitlines() if x.strip()]


def linhas_dos_vereditos(pasta: pathlib.Path, hoje: str) -> list[dict]:
    """Uma linha por veredito de dossiê; `golden_sha` guarda o sha do arquivo do veredito."""
    arquivos = sorted(pasta.glob("*.json"))
    if not arquivos:
        raise FileNotFoundError(f"nenhum veredito em {pasta}")
    out = []
    for f in arquivos:
        bruto = f.read_bytes()
        v = json.loads(bruto.decode("utf-8"))
        for c in ("pc", "central", "preco"):
            if isinstance(v[c], float) and not math.isfinite(v[c]):
                v[c] = None
        out.append({"origem": "dossie", "data_preco": v["data_preco"], "ticker": v["ticker"],
                    "preco": v["preco"], "palavra": v["palavra"], "pc": v["pc"],
                    "central": v["central"], "lote": None, "doutrina": v["doutrina"],
                    "golden_sha": sha_arquivo(bruto), "registrado_em": hoje})
    return out


def _gravar(novas: list[dict], caminho: pathlib.Path) -> int:
    existentes = {(l.get("origem", "hall"), l["data_preco"], l["ticker"]): l for l in ler(caminho)}
    a_gravar, vistas = [], set()
    for l in novas:
        chave = (l["origem"], l["data_preco"], l["ticker"])
        if chave in vistas:
            raise ValueError(f"{l['ticker']} ({l['origem']}) em {l['data_preco']} aparece duas "
                             "vezes na mesma rodada — um veredito por ticker e data")
        vistas.add(chave)
        velho = existentes.get(chave)
        campos = COMPARA + (("golden_sha",) if l["origem"] == "hall" else ())
        if velho is None:
            a_gravar.append(l)
        elif {k: velho.get(k) for k in campos} != {k: l[k] for k in campos}:
            raise ValueError(f"{l['ticker']} ({l['origem']}) em {l['data_preco']} já registrado "
                             "com outro valor — registro é append-only; use outra data de preço")
    if a_gravar:
        caminho.parent.mkdir(exist_ok=True)
        with caminho.open("a", encoding="utf-8", newline="\n") as f:
            for l in a_gravar:
                f.write(json.dumps(l, ensure_ascii=False, sort_keys=True) + "\n")
    return len(a_gravar)


def registrar(data_preco: str, doutrina: str, golden_path: pathlib.Path = GOLDEN,
              caminho: pathlib.Path = REGISTRO, hoje: str | None = None) -> int:
    """Acrescenta a rodada. Devolve quantas linhas novas; 0 se a rodada já estava idêntica."""
    bruto = golden_path.read_bytes()
    sha = sha_arquivo(bruto)
    novas = linhas_do_golden(json.loads(bruto.decode("utf-8")), data_preco, doutrina, sha,
                             hoje or dt.date.today().isoformat())
    return _gravar(novas, caminho)


def registrar_dossies(pasta: pathlib.Path = VEREDITOS, caminho: pathlib.Path = REGISTRO,
                      hoje: str | None = None) -> int:
    """Acrescenta os vereditos de dossiê (origem "dossie"). Idempotente; muda o valor → erro."""
    return _gravar(linhas_dos_vereditos(pasta, hoje or dt.date.today().isoformat()), caminho)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Registro prospectivo dos vereditos do golden")
    ap.add_argument("--data-preco", help="pregão de fechamento dos preços (AAAA-MM-DD)")
    ap.add_argument("--doutrina", help="versão da doutrina, ex.: v2.2")
    ap.add_argument("--dossie", action="store_true",
                    help="registra os vereditos de dossie/vereditos/*.json (origem 'dossie')")
    a = ap.parse_args(argv)
    if a.dossie and (a.data_preco or a.doutrina):
        ap.error("--dossie não combina com --data-preco/--doutrina")
    if a.dossie:
        n = registrar_dossies()
    elif a.data_preco and a.doutrina:
        n = registrar(a.data_preco, a.doutrina)
    else:
        ap.error("informe --dossie, ou --data-preco e --doutrina")
    print(f"{n} linhas novas em {REGISTRO.relative_to(AQUI)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
