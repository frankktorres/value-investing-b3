"""Fatias 7 e 8 — COTAHIST da B3: download, leitura em streaming, calendário e liquidez.

Uso: python -m backtest.cotahist            (baixa o que falta e gera um parquet por ano)
     python -m backtest.cotahist --conferir (só mostra o estado)

LAYOUT (245 bytes + CRLF = 247 por linha). Conferido em 06/10/2026 contra o PDF oficial da B3
("Layout do arquivo - Cotações Históricas", Revisão 01, 13/04/2017; b3.com.br -> Market Data e
Índices -> Séries Históricas), página por página, e contra um registro real do COTAHIST_A2014.
Posições abaixo são 0-based [ini:fim) = (pos. inicial - 1 : pos. final) do PDF:
  TIPREG 01-02 · DATA 03-10 · CODBDI 11-12 · CODNEG 13-24 · TPMERC 25-27 · NOMRES 28-39 ·
  ESPECI 40-49 · MODREF 53-56 · PREABE 57-69 · PREMAX 70-82 · PREMIN 83-95 · PREMED 96-108 ·
  PREULT 109-121 · TOTNEG 148-152 · QUATOT 153-170 · VOLTOT 171-188 (V99) · FATCOT 211-217 ·
  CODISI 231-242. Preços são (11)V99: duas casas implícitas. FATCOT 1 = cotação unitária,
  1000 = cotação por lote de mil: preço por ação = campo/100/FATCOT. CODBDI 02 = lote padrão;
  TPMERC 010 = mercado a vista.

NUNCA `extractall`: o TXT anual passa de 100 MB e há só ~12 GB livres em C:. A leitura abre o
membro do ZIP e consome em blocos de linhas (test_isolamento proíbe extractall por AST).

Universo gravado: TPMERC 010 e CODBDI em {02, 06, 07, 08, 09, 11}. O 02 sozinho DERRUBARIA do
universo a empresa no dia em que ela entra em recuperação judicial (08), extrajudicial (07),
concordata (06), RAET (09) ou intervenção (11): o papel muda de BDI justo quando está pior, e o
backtest veria só sobreviventes saudáveis — viés de sobrevivência que a espinha COTAHIST existe
para evitar. A coluna `codbdi` fica no parquet para quem quiser o corte estrito em 02.
Também 05 (sancionadas pelos regulamentos: JBSS3, BRKM, AZEV) e 58 (Chapter 11 e afins: GOLL4 desde
30/01/2024, AZUL4, OGXP3, MMXM3, LUPA3) — achado do `adversario` em 06/10/2026: sem o 58 a GOLL4
"deslistava" a R$ 3,93 e ia para o Ibovespa, quando negociou mais 231 pregões caindo (-71% virava -92%).
"""
from __future__ import annotations

import argparse
import sys
import time
import zipfile
from pathlib import Path

import pandas as pd
import requests

AQUI = Path(__file__).resolve().parent
PASTA = AQUI / "dados" / "cotahist"
URLS = ("https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{a}.ZIP",)
PRIMEIRO, ULTIMO = 2014, 2026
TENTATIVAS = 4
MIN_BYTES = 1_000_000
TAMANHO = 245
BDI_UNIVERSO = ("02", "05", "06", "07", "08", "09", "11", "58")
TPMERC_VISTA = "010"

# (inicio0, fim0) — ver docstring.
POS = {
    "tipreg": (0, 2), "data": (2, 10), "codbdi": (10, 12), "ticker": (12, 24), "tpmerc": (24, 27),
    "nomres": (27, 39), "especi": (39, 49), "modref": (52, 56),
    "preabe": (56, 69), "premax": (69, 82), "premin": (82, 95), "premed": (95, 108),
    "preult": (108, 121), "totneg": (147, 152), "quatot": (152, 170), "voltot": (170, 188),
    "fatcot": (210, 217), "codisi": (230, 242),
}
# ESPECI das ações e units (tabela do PDF): ON, PN, PNA..PNH, PNV, PNR, UNT. Fora: DRN/DRE/DR3
# (BDR — em 2022 eram 956 dos 1.475 papéis!), IBO/CI (ETF), DIR/BNS/REC (direitos e recibos).
ESPECIES_ACAO = ("ON", "PN", "PNA", "PNB", "PNC", "PND", "PNE", "PNF", "PNG", "PNH", "PNV", "PNR",
                 "UNT", "OR")
PRECOS = ("preabe", "premax", "premin", "premed", "preult")


def zip_de(ano: int) -> Path:
    return PASTA / f"COTAHIST_A{ano}.ZIP"


def parquet_de(ano: int) -> Path:
    return PASTA / f"precos_{ano}.parquet"


def _zip_valido(f: Path) -> bool:
    if not f.exists() or f.stat().st_size < MIN_BYTES:
        return False
    try:
        with zipfile.ZipFile(f) as z:
            return bool(z.namelist()) and z.testzip() is None
    except (zipfile.BadZipFile, OSError):
        return False


def baixar(ano: int) -> str:
    """'em disco' | 'baixado' | 'falhou: ...'. Escreve em .parcial e só então renomeia."""
    f = zip_de(ano)
    if _zip_valido(f):
        return "em disco"
    parcial = f.with_suffix(".parcial")
    ultimo_erro = "sem url"
    for url in URLS:
        for tentativa in range(1, TENTATIVAS + 1):
            try:
                with requests.get(url.format(a=ano), timeout=600, stream=True) as r:
                    r.raise_for_status()
                    with parcial.open("wb") as saida:
                        for bloco in r.iter_content(chunk_size=1 << 20):
                            saida.write(bloco)
                parcial.replace(f)
                if not _zip_valido(f):
                    f.unlink(missing_ok=True)
                    raise OSError("ZIP baixado não abre ou veio curto")
                return "baixado"
            except Exception as e:                              # noqa: BLE001 — rede: retenta
                parcial.unlink(missing_ok=True)
                ultimo_erro = f"{type(e).__name__}: {e}"
                time.sleep(5 * tentativa)
    return f"falhou: {ultimo_erro}"


def _linhas(ano: int):
    """Linhas do TXT dentro do ZIP, em streaming (nunca extrai para o disco)."""
    with zipfile.ZipFile(zip_de(ano)) as z:
        nomes = [n for n in z.namelist() if n.upper().endswith(".TXT")]
        if len(nomes) != 1:
            raise ValueError(f"COTAHIST {ano}: esperava 1 TXT, achei {nomes}")
        with z.open(nomes[0]) as f:
            for linha in f:
                yield linha.rstrip(b"\r\n")


def ler_ano(ano: int) -> pd.DataFrame:
    """Parquet-ready: registros 01, TPMERC 010, CODBDI do universo. Falha alto em linha torta."""
    registros = []
    trailer = None
    n = 0
    for n, bruta in enumerate(_linhas(ano), start=1):
        if len(bruta) != TAMANHO:
            raise ValueError(f"COTAHIST {ano} linha {n}: {len(bruta)} bytes, esperado {TAMANHO}")
        tip = bruta[0:2]
        if tip == b"00":
            if bruta[2:15].decode("latin-1") != f"COTAHIST.{ano}":
                raise ValueError(f"COTAHIST {ano}: header inesperado {bruta[:31]!r}")
            continue
        if tip == b"99":
            trailer = int(bruta[31:42])
            continue
        if tip != b"01":
            raise ValueError(f"COTAHIST {ano} linha {n}: TIPREG {tip!r}")
        if bruta[10:12].decode("ascii") not in BDI_UNIVERSO or bruta[24:27] != b"010":
            continue
        registros.append(bruta)
    # Trailer = total de registros (PDF §3.3: incluindo header e trailer, o que vale de 2014 a 2024).
    # O arquivo de 2025 passou a contar só os registros 01 (n - 2). Qualquer das duas convenções
    # prova que o arquivo não veio truncado; outro número, não.
    if trailer is None or trailer not in (n, n - 2):
        raise ValueError(f"COTAHIST {ano}: trailer {trailer} != {n} linhas lidas (truncado?)")

    if not registros:
        return pd.DataFrame(columns=[k for k in POS if k not in ("tipreg", "tpmerc")])

    def campo(nome: str) -> list[str]:
        a, b = POS[nome]
        return [r[a:b].decode("latin-1") for r in registros]

    d = pd.DataFrame({k: campo(k) for k in POS if k not in ("tipreg", "tpmerc")})
    d["data"] = pd.to_datetime(d["data"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
    for c in ("ticker", "nomres", "especi", "modref", "codisi"):
        d[c] = d[c].str.strip()
    fat = pd.to_numeric(d["fatcot"])
    if (fat < 1).any():
        raise ValueError(f"COTAHIST {ano}: FATCOT < 1")
    # O PDF só prevê 1 e 1000, mas a B3 publicou 1.000.000 (VSPT3, nov/2016: cotação por milhão de
    # ações). Dividir por FATCOT continua certo; só avisa, para o atípico não passar em silêncio.
    atipicos = fat[~fat.isin([1, 1000])]
    if len(atipicos):
        print(f"  AVISO {ano}: {len(atipicos)} registros com FATCOT fora de {{1, 1000}}: "
              f"{sorted(atipicos.unique())}", flush=True)
    d["fatcot"] = fat.astype("int32")      # int16 estourava em 1.000.000
    for c in PRECOS:                                           # por AÇÃO, em R$
        d[c] = pd.to_numeric(d[c]) / 100 / d["fatcot"]
    d["totneg"] = pd.to_numeric(d["totneg"]).astype("int32")
    d["quatot"] = pd.to_numeric(d["quatot"]).astype("int64")
    d["voltot"] = pd.to_numeric(d["voltot"]) / 100             # R$ negociados no dia
    return d.sort_values(["data", "ticker"], ignore_index=True)


def gerar(ano: int) -> Path:
    d = ler_ano(ano)
    destino = parquet_de(ano)
    d.to_parquet(destino, index=False)
    return destino


# ----------------------------------------------------------------------------- calendário
def pregoes(anos: range | None = None) -> tuple[str, ...]:
    """Conjunto de DATAs do COTAHIST = calendário de negociação da B3, ordenado.

    Qualquer ano em disco vale; um dia sem nenhum papel do universo não existe como pregão.
    """
    datas: set[str] = set()
    for a in anos or range(PRIMEIRO, ULTIMO + 1):
        p = parquet_de(a)
        if p.exists():
            datas.update(pd.read_parquet(p, columns=["data"])["data"].unique())
    return tuple(sorted(datas))


def calendario(anos: range | None = None):
    from .calendario import Calendario
    return Calendario(pregoes(anos))


# ----------------------------------------------------------------------------- liquidez
def so_acoes(d: pd.DataFrame) -> pd.DataFrame:
    """Só ações e units (descarta BDR, ETF, direitos, recibos)."""
    return d[d["especi"].str.split().str[0].isin(ESPECIES_ACAO)]


def liquidez_media(corte: str, cal=None, janela: int | None = None,
                   anos: range | None = None) -> pd.Series:
    """Volume diário médio em R$ nominais, por ticker, nos `janela` pregões até `corte`.

    Só ações/units (`so_acoes`). Média sobre TODOS os pregões da janela (dia sem negócio conta
    zero): papel que negocia 1 dia em 60 não é líquido. Só lê dado <= o último pregão <= corte (nada de olhar à frente).
    """
    from .config import PADRAO
    cal = cal or calendario()
    n = janela or PADRAO.liquidez_pregoes
    jan = cal.janela_anterior(corte, n)
    if jan is None:
        return pd.Series(dtype="float64")
    ini, fim = jan
    anos = anos or range(int(ini[:4]), int(fim[:4]) + 1)
    partes = [pd.read_parquet(parquet_de(a), columns=["data", "ticker", "especi", "voltot"]) for a in anos]
    d = pd.concat(partes, ignore_index=True)
    d = so_acoes(d[(d["data"] >= ini) & (d["data"] <= fim)])
    return (d.groupby("ticker")["voltot"].sum() / n).rename("liquidez")


def universo_liquido(corte: str, cfg=None, cal=None, real: bool = True) -> pd.Series:
    """Tickers com liquidez >= limite (R$ reais do mês-âncora, convertido só com IPCA <= T)."""
    from .config import PADRAO, limite_liquidez
    cfg = cfg or PADRAO
    liq = liquidez_media(corte, cal=cal, janela=cfg.liquidez_pregoes)
    lim = limite_liquidez(cfg, corte) if real else cfg.liquidez_min_base
    return liq[liq >= lim]


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--conferir", action="store_true")
    args = p.parse_args(argv)
    PASTA.mkdir(parents=True, exist_ok=True)
    falhas = []
    for ano in range(PRIMEIRO, ULTIMO + 1):
        if args.conferir:
            print(f"{ano}  zip={'ok' if _zip_valido(zip_de(ano)) else 'FALTA'}  "
                  f"parquet={'ok' if parquet_de(ano).exists() else 'FALTA'}")
            continue
        estado = baixar(ano)
        print(f"COTAHIST_A{ano}.ZIP  {estado}", flush=True)
        if estado.startswith("falhou"):
            falhas.append(ano)
            continue
        if not parquet_de(ano).exists():
            gerar(ano)
            print(f"  precos_{ano}.parquet gerado", flush=True)
    if falhas:
        print(f"falhas: {falhas}", file=sys.stderr)
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
