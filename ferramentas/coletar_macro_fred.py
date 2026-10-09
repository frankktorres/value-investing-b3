"""Coletor das séries macro externas — FRED (Brent/EIA, CPI e PPI/BLS, minério/FMI) e PTAX (BCB SGS 3698) — AUD-81.

Antes, esses arquivos de `dados/macro/` eram versionados sem comando que os refizesse e sem data de coleta: a
atualização e a auditoria dependiam de download manual. Agora:

  · `python coletar_macro_fred.py`              baixa tudo, confere a parte comum com o arquivo atual e grava;
  · `python coletar_macro_fred.py --so brent_fred.csv fred_WPU1017.csv`   só alguns;
  · `python coletar_macro_fred.py --registrar`   (uma vez) cria o manifesto dos arquivos já existentes, sem baixar;
  · `python coletar_macro_fred.py --aceitar-revisoes`   grava mesmo com divergência na parte comum.

Regras: a parte comum tem de bater (o BLS revisa o PPI por até 4 meses — divergência é listada e NADA é gravado, a menos
que se aceite a revisão de propósito, porque o golden mudaria); o arquivo substituído vai para `_historico/`; o
`dados/macro/MANIFESTO_MACRO.json` guarda fonte, URL, data de coleta, intervalo, nº de linhas e sha256 (EOL normalizado)
de cada arquivo, e `tests/test_coletar_macro_fred.py` confere o manifesto contra os arquivos do disco.
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import pathlib
import sys
import time

import requests

from historico_arquivos import guardar

AQUI = pathlib.Path(__file__).resolve().parent
MACRO = AQUI / "dados" / "macro"
MANIFESTO = MACRO / "MANIFESTO_MACRO.json"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={id}"
SGS = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.{serie}/dados?formato=json&dataInicial={ini}&dataFinal={fim}"
H = {"User-Agent": "Mozilla/5.0"}

# arquivo -> (id da série no FRED, o que é e nota da fonte)
SERIES_FRED = {
    "brent_fred.csv": ("DCOILBRENTEU", "Brent spot Europa, US$/bbl diário — EIA via FRED (nota A)"),
    "cpi_us_fred.csv": ("CPIAUCSL", "CPI-U EUA, índice mensal — BLS via FRED (nota A)"),
    "fred_WPU1017.csv": ("WPU1017", "PPI aço e produtos de aço — BLS via FRED (nota A)"),
    "fred_WPU101704.csv": ("WPU101704", "PPI aço, subgrupo — BLS via FRED (nota A)"),
    "fred_WPU1012.csv": ("WPU1012", "PPI ferro-gusa e ferroligas — BLS via FRED (nota A)"),
    "fred_WPU0662.csv": ("WPU0662", "PPI resinas termoplásticas (proxy do PVC) — BLS via FRED (nota A)"),
    "fred_WPU06130302.csv": ("WPU06130302", "PPI soda cáustica — BLS via FRED (nota A)"),
    "fred_PCU3251803251804.csv": ("PCU3251803251804", "PPI cloro-álcalis — BLS via FRED (nota A)"),
    "fred_PIORECRUSDM.csv": ("PIORECRUSDM", "Minério de ferro 62% Fe CFR China, US$/t — FMI via FRED (nota B)"),
}
PTAX = "ptax_media_mensal.json"          # BCB SGS 3698, média mensal da taxa livre dólar (venda)
PTAX_INFO = ("3698", "PTAX — taxa de câmbio livre, dólar americano (venda), média mensal — BCB SGS 3698 (nota A)")
TOL = 1e-9


def sha_normalizado(bruto: bytes) -> str:
    return hashlib.sha256(bruto.replace(b"\r\n", b"\n")).hexdigest()


def _get(url: str, tentativas: int = 5, espera: float = 3.0, timeout: int = 90) -> requests.Response:
    erro = "sem tentativa"
    for i in range(tentativas):
        try:
            r = requests.get(url, headers=H, timeout=timeout)
            if r.status_code == 200:
                return r
            erro = f"HTTP {r.status_code}"
        except requests.RequestException as e:
            erro = str(e)
        time.sleep(espera * (i + 1))
    raise RuntimeError(f"{erro} em {url}")


def parse_fred(texto: str) -> list[tuple[str, str]]:
    """[(data, valor_texto)] sem o cabeçalho; valor "." (feriado/ausente no FRED) fica como veio."""
    linhas = list(csv.reader(io.StringIO(texto.lstrip(chr(0xFEFF)))))
    return [(r[0], r[1]) for r in linhas[1:] if len(r) >= 2 and r[0]]


def divergencias(novo: list[tuple[str, str]], antigo: list[tuple[str, str]]) -> list[str]:
    """Datas do arquivo atual que sumiram ou mudaram de valor no download novo (mês novo no fim não conta)."""
    n = dict(novo)
    out = []
    for d, v in antigo:
        w = n.get(d)
        if w is None:
            out.append(f"{d}: antigo {v} × novo ausente")
            continue
        try:
            if abs(float(v) - float(w)) > TOL * max(1.0, abs(float(v))):
                out.append(f"{d}: antigo {v} × novo {w}")
        except ValueError:
            if v != w:
                out.append(f"{d}: antigo {v} × novo {w}")
    return out


def _resumo(sid: str, desc: str, url: str, bruto: bytes, datas: list[str], coletado_em: str) -> dict:
    return {"serie": sid, "descricao": desc, "url": url, "coletado_em": coletado_em, "linhas": len(datas),
            "primeira": datas[0] if datas else None, "ultima": datas[-1] if datas else None,
            "sha256": sha_normalizado(bruto)}


def _manifesto() -> dict:
    return json.loads(MANIFESTO.read_text(encoding="utf-8")) if MANIFESTO.exists() else {}


def _gravar_manifesto(m: dict, raiz_manifesto: pathlib.Path = MANIFESTO) -> None:
    raiz_manifesto.write_text(json.dumps(m, ensure_ascii=False, indent=1, sort_keys=True) + "\n",
                              encoding="utf-8", newline="\n")


def _datas_ptax(bruto: bytes) -> list[str]:
    return [x["data"] for x in json.loads(bruto.decode("utf-8"))]


def registrar_existentes(pasta: pathlib.Path = MACRO) -> dict:
    """Manifesto dos arquivos que já estavam versionados sem origem registrada (data de coleta desconhecida)."""
    m = _manifesto() if pasta == MACRO else {}
    for arq, (sid, desc) in SERIES_FRED.items():
        f = pasta / arq
        if f.exists() and arq not in m:
            bruto = f.read_bytes()
            m[arq] = _resumo(sid, desc, FRED.format(id=sid), bruto,
                             [d for d, _ in parse_fred(bruto.decode("utf-8"))], "anterior a 2026-10-09 (data não registrada)")
    f = pasta / PTAX
    if f.exists() and PTAX not in m:
        bruto = f.read_bytes()
        m[PTAX] = _resumo(PTAX_INFO[0], PTAX_INFO[1], SGS.format(serie=3698, ini="01/01/2015", fim="..."), bruto,
                          _datas_ptax(bruto), "anterior a 2026-10-09 (data não registrada)")
    return m


def atualizar_fred(arq: str, baixar=lambda url: _get(url).text, pasta: pathlib.Path = MACRO, hoje: str | None = None,
                   aceitar_revisoes: bool = False, raiz=None) -> tuple[str, list[str]]:
    """Baixa uma série FRED, confere a parte comum e grava (copiando o anterior para `_historico/`).

    Devolve (estado, divergências); estado ∈ {"gravado", "sem mudança", "divergiu"}."""
    sid, desc = SERIES_FRED[arq]
    url = FRED.format(id=sid)
    texto = baixar(url).replace("\r\n", "\n")
    novo = parse_fred(texto)
    if not novo or not texto.lstrip(chr(0xFEFF)).startswith(("observation_date", "DATE")):
        raise ValueError(f"{arq}: resposta do FRED sem o formato esperado")
    destino = pasta / arq
    antigo = parse_fred(destino.read_text(encoding="utf-8")) if destino.exists() else []
    div = divergencias(novo, antigo)
    if div and not aceitar_revisoes:
        return "divergiu", div
    bruto = texto.encode("utf-8")
    if destino.exists() and sha_normalizado(destino.read_bytes()) == sha_normalizado(bruto):
        estado = "sem mudança"
    else:
        guardar(destino, "macro fred", bruto, **({"raiz": raiz} if raiz else {}))
        destino.write_bytes(bruto)
        estado = "gravado"
    m = _manifesto() if pasta == MACRO else {}
    m[arq] = _resumo(sid, desc, url, bruto, [d for d, _ in novo], hoje or dt.date.today().isoformat())
    if pasta == MACRO:
        _gravar_manifesto(m)
    return estado, div


def atualizar_ptax(baixar=lambda url: _get(url).json(), pasta: pathlib.Path = MACRO, hoje: str | None = None,
                   aceitar_revisoes: bool = False, raiz=None, desde: int = 2015) -> tuple[str, list[str]]:
    """PTAX média mensal (SGS 3698). Mesmas regras de conferência e histórico."""
    hoje = hoje or dt.date.today().isoformat()
    fim = dt.date.fromisoformat(hoje).strftime("%d/%m/%Y")
    url = SGS.format(serie=3698, ini=f"01/01/{desde}", fim=fim)
    novo = [{"data": r["data"], "valor": r["valor"]} for r in baixar(url)]
    if not novo:
        raise ValueError("PTAX: resposta vazia do SGS 3698")
    destino = pasta / PTAX
    antigo = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else []
    div = divergencias([(r["data"], r["valor"]) for r in novo], [(r["data"], r["valor"]) for r in antigo])
    if div and not aceitar_revisoes:
        return "divergiu", div
    bruto = json.dumps(novo, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if destino.exists() and sha_normalizado(destino.read_bytes()) == sha_normalizado(bruto):
        estado = "sem mudança"
    else:
        guardar(destino, "macro ptax", bruto, **({"raiz": raiz} if raiz else {}))
        destino.write_bytes(bruto)
        estado = "gravado"
    m = _manifesto() if pasta == MACRO else {}
    m[PTAX] = _resumo(PTAX_INFO[0], PTAX_INFO[1], url, bruto, [r["data"] for r in novo], hoje)
    if pasta == MACRO:
        _gravar_manifesto(m)
    return estado, div


def main(argv: list[str] | None = None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--so", nargs="+", metavar="ARQUIVO", help="só estes arquivos (nomes de dados/macro/)")
    ap.add_argument("--registrar", action="store_true", help="cria o manifesto dos arquivos existentes e sai")
    ap.add_argument("--aceitar-revisoes", action="store_true", help="grava mesmo com divergência na parte comum")
    a = ap.parse_args(argv)
    if a.registrar:
        m = registrar_existentes()
        _gravar_manifesto(m)
        print(f"manifesto: {len(m)} arquivos em {MANIFESTO.relative_to(AQUI)}")
        return 0
    alvo = a.so or [*SERIES_FRED, PTAX]
    desconhecidos = [x for x in alvo if x not in SERIES_FRED and x != PTAX]
    if desconhecidos:
        ap.error(f"arquivo fora da lista: {desconhecidos}")
    rc = 0
    for arq in alvo:
        try:
            estado, div = (atualizar_ptax(aceitar_revisoes=a.aceitar_revisoes) if arq == PTAX
                           else atualizar_fred(arq, aceitar_revisoes=a.aceitar_revisoes))
        except Exception as ex:
            print(f"{arq}: ERRO — {ex}")
            rc = 1
            continue
        print(f"{arq}: {estado}" + (f" ({len(div)} divergências na parte comum)" if div else ""))
        if estado == "divergiu":
            print("   nada gravado; use --aceitar-revisoes se a revisão for esperada:")
            print("\n".join("   " + d for d in div[:8]))
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
