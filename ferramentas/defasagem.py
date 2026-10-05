"""Defasagem do provento: meses entre a data-com e o pagamento, ponderada pelo valor (StatusInvest, eventos de 2023–25).

Doutrina §6.3: o provento é trazido a valor presente ao Ke nominal pela defasagem. Medida aqui por ticker, sem arbítrio.
Amortização/redução de capital fica fora (não é provento, §6.4); eventos sem data de pagamento são ignorados.
"""
import json
import pathlib
from datetime import datetime

DATA_BASE = datetime(2026, 10, 5)   # coleta da StatusInvest; evento já com data-com e sem pagamento datado está atrasado pelo menos até aqui

AQUI = pathlib.Path(__file__).parent
ANOS = ("2023", "2024", "2025")
_SI = None


def _series():
    global _SI
    if _SI is None:
        _SI = json.loads(sorted((AQUI / "dados").glob("series_*.json"))[-1].read_text(encoding="utf-8"))
    return _SI


def meses_entre(com, pag):
    d0, d1 = (datetime.strptime(x, "%d/%m/%Y") for x in (com, pag))
    return max((d1 - d0).days, 0) / 30.4375


def defasagem_meses(tk, si=None, anos=ANOS, ignorar_amortizacao=True):
    """Média ponderada pelo valor da defasagem (meses); 0.0 se não há evento datado. Arredondada a 0,5 mês."""
    si = si or _series()
    soma = peso = 0.0
    for e in si[tk]["eventos"]:
        com, pag, val = e.get("data_com"), e.get("pagamento"), e.get("valor") or 0
        if not com or val <= 0 or com[-4:] not in anos:
            continue
        if not pag or pag == "-":     # não pago ainda: prazo mínimo = data-com → data-base (descartar viesaria para baixo, 06/10)
            pag = DATA_BASE.strftime("%d/%m/%Y")
        if ignorar_amortizacao and (e.get("tipo") or "").startswith("Amortiza"):
            continue
        try:
            m = meses_entre(com, pag)
        except ValueError:
            continue
        soma += m * val
        peso += val
    return round(2 * soma / peso) / 2 if peso else 0.0


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    for tk in sorted(_series()):
        print(f"{tk:7} {defasagem_meses(tk):5.1f} meses")
