"""Coleta séries da StatusInvest (agregador — fonte de SÉRIES, nunca de fato isolado; doutrina/02 regra 1).

Uso: python coletar_statusinvest.py BBAS3 ITUB4 ...   → grava dados/raw/<data>/<TICKER>_*.json (cache: não recoleta)
"""
import json
import pathlib
import re
import sys
import time
from datetime import date

import requests

H = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36",
     "X-Requested-With": "XMLHttpRequest"}
BASE = pathlib.Path(__file__).parent / "dados" / "raw" / date.today().isoformat()


def _get(url, **kw):
    for tent in range(3):
        try:
            r = requests.get(url, headers=H, timeout=40, **kw)
            if r.status_code == 200:
                return r
        except requests.RequestException:
            pass
        time.sleep(2 + 3 * tent)
    raise RuntimeError(f"falhou: {url}")


def coletar(tk: str):
    BASE.mkdir(parents=True, exist_ok=True)
    t = tk.lower()
    alvo = BASE / f"{tk}_indicadores.json"
    if not alvo.exists():
        r = requests.post("https://statusinvest.com.br/acao/indicatorhistoricallist",
                          data={"codes[]": t, "time": "5", "byQuarter": "false", "futureData": "false"},
                          headers={**H, "Referer": f"https://statusinvest.com.br/acoes/{t}"}, timeout=40)
        alvo.write_text(r.text, encoding="utf-8")
    alvo = BASE / f"{tk}_proventos.json"
    if not alvo.exists():
        r = _get(f"https://statusinvest.com.br/acao/companytickerprovents?ticker={tk}&chartProventsType=2")
        alvo.write_text(r.text, encoding="utf-8")
    alvo = BASE / f"{tk}_pagina.json"
    if not alvo.exists():
        html = _get(f"https://statusinvest.com.br/acoes/{t}").text
        def achar(rotulo):
            m = re.search(rotulo + r".{0,400}?<strong[^>]*>\s*([\d\.,\-]+)\s*</strong>", html, re.S | re.I)
            return m.group(1) if m else None
        pag = {
            "preco": achar(r"Valor atual"),
            "n_papeis": achar(r"N.{1,3} total de papéis"),
            "free_float": achar(r"Free float"),
            "tag_along": achar(r"Tag Along"),
            "liquidez_media_diaria": achar(r"Liquidez média diária"),
            "valor_mercado": achar(r"Valor de mercado"),
            "patrimonio_liquido": achar(r"Patrimônio líquido"),
        }
        alvo.write_text(json.dumps(pag, ensure_ascii=False, indent=1), encoding="utf-8")
    return tk


if __name__ == "__main__":
    for tk in sys.argv[1:]:
        print("ok", coletar(tk.upper()))
        time.sleep(1.5)
