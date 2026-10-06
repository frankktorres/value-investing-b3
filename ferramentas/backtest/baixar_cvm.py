"""Fatia 4 — completa o cache de ZIPs da CVM para trás, até o início do dado estruturado.

O motor de hoje só precisa de 2016+; o backtest precisa de 2010+ para ter janela de ciclo nas
safras antigas. Conferido na fonte em 06/10/2026: DFP existe desde 2010, ITR desde 2011.

Uso: python -m backtest.baixar_cvm            (baixa o que falta)
     python -m backtest.baixar_cvm --conferir (só lista o estado, não baixa)

Retomável: nunca rebaixa arquivo que já está no disco, e escreve em .parcial antes de renomear,
para que uma queda de rede não deixe ZIP truncado passando por completo (MAQUINA.md: job longo
sempre com retomada).
"""
from __future__ import annotations

import argparse
import sys
import time
import zipfile
from pathlib import Path

import requests

AQUI = Path(__file__).resolve().parent
CACHE = AQUI.parent / "dados" / "cvm"
_BASE = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC"
URL = {"dfp": f"{_BASE}/DFP/DADOS/dfp_cia_aberta_{{a}}.zip",
       "itr": f"{_BASE}/ITR/DADOS/itr_cia_aberta_{{a}}.zip",
       # FCA: `valor_mobiliario` dá o mapa ticker <-> CNPJ DATADO (Codigo_Negociacao com
       # Data_Inicio/Fim_Negociacao). É o que resolve o risco de identidade: buscar o preço de 2015
       # por "ISAE4" devolve vazio (era TRPL4) ou, pior, devolve outra coisa.
       "fca": f"{_BASE}/FCA/DADOS/fca_cia_aberta_{{a}}.zip",
       # FRE: `capital_social` dá a contagem de ações de 2010 em diante — o `composicao_capital` da
       # DFP/ITR só existe de 2020, e sem ações não há valor por ação em 12 dos 24 cortes.
       # ATENÇÃO: usar Tipo_Capital = "Capital Integralizado". Medido no BB de 2026, "Capital
       # Emitido" (autorizado) dá 5,73 bi contra 2,87 bi de integralizadas — o dobro exato, que
       # cortaria todo o P/C pela metade.
       "fre": f"{_BASE}/FRE/DADOS/fre_cia_aberta_{{a}}.zip"}

# O que o backtest precisa, somado ao que o motor de hoje já deixou em disco.
# Conferido na fonte em 06/10/2026: DFP e FCA e FRE desde 2010, ITR desde 2011.
PRIMEIRO = {"dfp": 2010, "itr": 2011, "fca": 2010, "fre": 2010}
ULTIMO = 2026
TENTATIVAS = 4
MIN_BYTES = 100_000      # ano cheio: ~10 MB (DFP), ~30 MB (ITR), ~1 MB (FCA), ~8 MB (FRE)


def alvos() -> list[tuple[str, int]]:
    return [(t, a) for t in URL for a in range(PRIMEIRO[t], ULTIMO + 1)]


def caminho(tipo: str, ano: int) -> Path:
    return CACHE / f"{tipo}_{ano}.zip"


def valido(f: Path) -> bool:
    """ZIP presente, com tamanho plausível e lista de membros legível."""
    if not f.exists() or f.stat().st_size < MIN_BYTES:
        return False
    try:
        with zipfile.ZipFile(f) as z:
            return bool(z.namelist()) and z.testzip() is None
    except (zipfile.BadZipFile, OSError):
        return False


def baixar(tipo: str, ano: int) -> str:
    """Devolve 'em disco', 'baixado' ou 'falhou: ...'. Nunca deixa arquivo parcial no lugar final."""
    f = caminho(tipo, ano)
    if valido(f):
        return "em disco"
    parcial = f.with_suffix(".parcial")
    url = URL[tipo].format(a=ano)
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            with requests.get(url, timeout=600, stream=True) as r:
                r.raise_for_status()
                with parcial.open("wb") as saida:
                    for bloco in r.iter_content(chunk_size=1 << 20):
                        saida.write(bloco)
            parcial.replace(f)
            if not valido(f):
                f.unlink(missing_ok=True)
                raise OSError("ZIP baixado não abre ou veio curto")
            return "baixado"
        except Exception as e:                                  # noqa: BLE001 — rede: qualquer falha retenta
            parcial.unlink(missing_ok=True)
            if tentativa == TENTATIVAS:
                return f"falhou: {type(e).__name__}: {e}"
            time.sleep(5 * tentativa)
    return "falhou"


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--conferir", action="store_true", help="só mostra o estado do cache")
    args = p.parse_args(argv)

    CACHE.mkdir(parents=True, exist_ok=True)
    falhas, baixados, tinha = [], [], []
    for tipo, ano in alvos():
        if args.conferir:
            estado = "em disco" if valido(caminho(tipo, ano)) else "FALTA"
            print(f"{tipo}_{ano}.zip  {estado}")
            continue
        estado = baixar(tipo, ano)
        mb = caminho(tipo, ano).stat().st_size / 1e6 if caminho(tipo, ano).exists() else 0
        print(f"{tipo}_{ano}.zip  {estado}  {mb:.1f} MB", flush=True)
        (falhas if estado.startswith("falhou") else baixados if estado == "baixado" else tinha).append(
            f"{tipo}_{ano}")

    if args.conferir:
        return 0
    print(f"\n{len(tinha)} já em disco · {len(baixados)} baixados · {len(falhas)} falharam")
    if falhas:
        print("falhas: " + ", ".join(falhas), file=sys.stderr)
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
