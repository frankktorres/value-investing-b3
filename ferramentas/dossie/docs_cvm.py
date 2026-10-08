"""Baixa do RAD/CVM o documento completo de um DFP/ITR (fonte A) e extrai os PDFs embutidos (notas, relatório, release).

Uso (a partir de ferramentas/):  python -m dossie.docs_cvm "MAHLE METAL LEVE" dfp 2025
                                 python -m dossie.docs_cvm "TIM S.A." itr 2026 --refer 2026-06-30
Saída: dados/cvm/docs/<PASTA>/<tipo><ano>_v<versao>/ com doc.bin, NN_*.pdf e NN_*.txt (pdftotext -layout).
O link vem da coluna LINK_DOC do índice da CVM em dados/cvm/<tipo>_cia_aberta_<ano>.csv (dentro do zip). O RAD corta a
conexão às vezes: até 6 tentativas, com espera crescente. O .bin é um zip SEM diretório central: os PDFs vêm em base64 na tag
ImagemObjetoArquivoPdf do XML (método do dossiê da HYPE3, 07/10/2026).
"""
from __future__ import annotations

import argparse
import base64
import csv
import io
import pathlib
import re
import struct
import subprocess
import sys
import time
import urllib.request
import zipfile
import zlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
CVM = RAIZ / "dados" / "cvm"


def link(denom: str, tipo: str, ano: int, refer: str | None = None) -> tuple[str, str, str]:
    """(LINK_DOC, versão, DENOM_CIA) da versão mais recente do documento da companhia cujo nome contém `denom`."""
    z = zipfile.ZipFile(CVM / f"{tipo}_{ano}.zip")
    r = csv.DictReader(io.TextIOWrapper(z.open(f"{tipo}_cia_aberta_{ano}.csv"), encoding="latin-1"), delimiter=";")
    achados = [x for x in r if denom.upper() in x["DENOM_CIA"].upper() and (refer is None or x["DT_REFER"] == refer)]
    if not achados:
        raise SystemExit(f"nenhum {tipo} {ano} com '{denom}'" + (f" em {refer}" if refer else ""))
    nomes = {x["DENOM_CIA"] for x in achados}
    if len(nomes) > 1:
        raise SystemExit(f"'{denom}' ambíguo: {sorted(nomes)}")
    x = max(achados, key=lambda x: (x["DT_REFER"], int(x["VERSAO"])))
    return x["LINK_DOC"], x["VERSAO"], x["DENOM_CIA"]


def baixar(url: str, destino: pathlib.Path) -> None:
    """O RAD derruba o http do urllib e do WebClient (WinError 10054, 08/10); o curl por https passa."""
    https = url.replace("http://", "https://", 1)
    for k in range(6):
        try:
            if k % 2 == 0:
                subprocess.run(["curl", "-sS", "-L", "--max-time", "300", "-A", "Mozilla/5.0", "-o", str(destino), https],
                               check=True, capture_output=True, timeout=320)
            else:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=120) as r:
                    destino.write_bytes(r.read())
            if destino.exists() and destino.stat().st_size > 1000:
                return
        except Exception as e:
            print(f"tentativa {k + 1}: {e}", file=sys.stderr)
        time.sleep(3 * (k + 1))
    raise SystemExit(f"falhou: {url}")


def extrair(pasta: pathlib.Path) -> list[str]:
    b = (pasta / "doc.bin").read_bytes()
    i, n, saida = 0, 0, []
    while True:
        i = b.find(b"PK\x03\x04", i)
        if i < 0:
            break
        _, _, _, metodo, _, _, _, csize, _, ln, lx = struct.unpack("<IHHHHHIIIHH", b[i:i + 30])
        ini = i + 30 + ln + lx
        dados = zlib.decompressobj(-15).decompress(b[ini:ini + csize] if csize else b[ini:]) if metodo == 8 else b[ini:ini + csize]
        i = ini + max(csize, 1)
        for m in re.finditer(rb"<ImagemObjetoArquivoPdf>(.*?)</ImagemObjetoArquivoPdf>", dados, re.S):
            out = pasta / f"{n:02d}_pdf{n}.pdf"
            out.write_bytes(base64.b64decode(re.sub(rb"\s", b"", m.group(1))))
            subprocess.run(["pdftotext", "-enc", "UTF-8", "-layout", str(out), str(out.with_suffix(".txt"))], check=False)
            saida.append(out.name)
            n += 1
    return saida


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("denom")
    ap.add_argument("tipo", choices=["dfp", "itr"])
    ap.add_argument("ano", type=int)
    ap.add_argument("--refer", help="DT_REFER (AAAA-MM-DD) quando há mais de um no ano (ITR)")
    ap.add_argument("--pasta", help="nome da pasta em dados/cvm/docs/ (padrão: 1ª palavra do nome)")
    a = ap.parse_args(argv)
    url, versao, nome = link(a.denom, a.tipo, a.ano, a.refer)
    sufixo = a.tipo + str(a.ano) + (a.refer[5:7] if a.refer else "")
    pasta = CVM / "docs" / (a.pasta or nome.split()[0].upper()) / f"{sufixo}_v{versao}"
    pasta.mkdir(parents=True, exist_ok=True)
    if not (pasta / "doc.bin").exists():
        baixar(url, pasta / "doc.bin")
    print(nome, url)
    for f in extrair(pasta):
        print(pasta / f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
