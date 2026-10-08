"""Provento já ex que ainda está no caixa do balanço — é dívida (doutrina §11.1, v2.3; AUD-02 da auditoria de 08/10/2026).

O preço da data-base já é ex, mas o dinheiro do provento ainda está no caixa do balanço do LTM: sem tirá-lo, o valor do
acionista conta duas vezes o mesmo real. Duas partes, somadas pelo motor (`motor_nao_financeiras.proventos_ja_ex`) na dívida
líquida e tiradas do Owner Earnings:
  (a) o passivo de proventos do próprio balanço (`proventos_a_pagar`, `coletar_cvm.extras_bp`): declarado até a data do
      balanço. No ITR o provento declarado já tem data-com; o que ainda não for ex na data do preço sai pela B3 (`nao_ex`);
  (b) os proventos APROVADOS depois da data do balanço com data-com antes da data do preço (`depois`): não estão no passivo, mas
      o caixa ainda os guarda. A casa já fazia isso à mão no EGIE3 (lote6 `EGIE_DIV_AGO26`).
Fonte de (b): API pública da B3 (GetListedCashDividends, nota A), cache próprio do hall em dados/proventos_hall/ — baixado
DEPOIS da data do preço (`python proventos_ex.py`), senão um provento aprovado entre o download e o preço sumiria em silêncio.

Limites declarados: o valor é o da classe negociada × todas as ações do motor (UNIP6: a PNB recebe 10% a mais que a ON, o
total sai um pouco alto — conservador); evento sem data de aprovação falha alto.
"""
from __future__ import annotations

import calendar
import json
import pathlib
import sys
import time
from datetime import date

AQUI = pathlib.Path(__file__).parent
PASTA = AQUI / "dados" / "proventos_hall"
MERCADO = AQUI / "dados" / "mercado.json"

# nome de pregão (NOMRES do COTAHIST, que a API da B3 usa como tradingName) de toda não financeira do hall e dos dossiês.
# "/" no nome devolve vazio na API (conferido em 08/10/2026): "AMBEV S/A" e "KLABIN S/A" só respondem como "... SA"
PREGAO = {"SUZB3": "SUZANO S.A.", "KLBN11": "KLABIN SA", "RANI3": "IRANI", "B3SA3": "B3", "SMTO3": "SAO MARTINHO",
          "KEPL3": "KEPLER WEBER", "SLCE3": "SLC AGRICOLA", "TIMS3": "TIM", "VIVT3": "TELEF BRASIL", "FLRY3": "FLEURY",
          "HYPE3": "HYPERA", "ABEV3": "AMBEV SA", "WEGE3": "WEG", "PETR4": "PETROBRAS", "PRIO3": "PETRORIO",
          "RECV3": "PETRORECSA", "UGPA3": "ULTRAPAR", "VBBR3": "VIBRA", "GGBR4": "GERDAU", "UNIP6": "UNIPAR",
          "LEVE3": "METAL LEVE", "CMIN3": "CSNMINERACAO", "BLAU3": "BLAU"}
CLASSE = {"PETR4": "PN", "GGBR4": "PN", "UNIP6": "PNB", "KLBN11": "UNT"}   # classe do ticker avaliado; o resto é ON


def data_do_preco() -> str:
    """Data-base dos preços do hall (mercado.json), 'AAAA-MM-DD'."""
    return json.loads(MERCADO.read_text(encoding="utf-8"))["data_base"]


def _data_iso(s: str) -> str:
    """'02/10/2026' ou '2026-10-02' → '2026-10-02'."""
    return f"{s[6:10]}-{s[3:5]}-{s[0:2]}" if len(s) == 10 and s[2] == "/" else s


def data_do_balanco(ref: str) -> str:
    """'2T26' → '2026-06-30': último dia do trimestre que fecha o LTM."""
    tri, aa = int(ref[0]), 2000 + int(ref[2:])
    mes = 3 * tri
    return date(aa, mes, calendar.monthrange(aa, mes)[1]).isoformat()


def _arquivo(tk: str) -> pathlib.Path:
    return PASTA / f"{tk}.json"


def _iso(s) -> str:
    """'21/08/2026' → '2026-08-21'; vazio ou outro formato → '' (mesma leitura de backtest/precos/proventos_b3)."""
    s = (s or "").strip()
    return f"{s[6:10]}-{s[3:5]}-{s[0:2]}" if len(s) == 10 and s[2] == "/" else ""


def _num(s) -> float:
    """'0,67407131000' → 0.67407131 (a B3 usa vírgula decimal e ponto de milhar); vazio → 0."""
    return float(str(s).replace(".", "").replace(",", ".")) if str(s or "").strip() else 0.0


def registros(tk: str, data_preco: str) -> list[dict]:
    """Proventos em dinheiro do ticker no cache do hall. Sem arquivo, ou baixado antes da data do preço → falha alto."""
    f = _arquivo(tk)
    if not f.exists():
        raise FileNotFoundError(f"{tk}: sem proventos da B3 em {f} — rode `python proventos_ex.py` (AUD-02)")
    j = json.loads(f.read_text(encoding="utf-8"))
    if j["baixado_em"] < data_preco:
        raise ValueError(f"{tk}: proventos da B3 baixados em {j['baixado_em']}, antes da data do preço {data_preco} — "
                         "um provento aprovado no intervalo sumiria; rode `python proventos_ex.py`")
    return [{"tipo_acao": (r.get("typeStock") or "").strip().upper(), "data_aprovacao": _iso(r.get("dateApproval")),
             "data_com": _iso(r.get("lastDatePriorEx")), "valor": _num(r.get("valueCash")),
             "lote": _num(r.get("quotedPerShares")) or 1.0, "tipo": (r.get("corporateAction") or "").strip()}
            for r in j["results"]]


def ajuste_b3(tk: str, n_acoes: float, ref: str, data_preco: str | None = None, regs: list[dict] | None = None) -> dict:
    """{'depois', 'nao_ex'} em R$ mil e os eventos usados. Ticker fora de PREGAO falha alto (série sintética TEST* → zeros).

    depois: aprovado DEPOIS da data do balanço, data-com antes da data do preço (ex no preço, ainda no caixa) → soma à dívida;
    nao_ex: aprovado ATÉ a data do balanço (está no passivo), data-com na data do preço ou depois (não é ex) → sai do passivo.
    `data_preco` aceita 'AAAA-MM-DD' ou 'DD/MM/AAAA' (o Mercado do hall usa o 2º, o do dossiê o 1º)."""
    data_preco = _data_iso(data_preco) if data_preco else data_do_preco()
    if regs is None:
        if tk.startswith("TEST"):          # série sintética dos testes; ticker real sem mapa falha alto (somaria zero em silêncio)
            return {"depois": 0.0, "nao_ex": 0.0, "eventos": []}
        if tk not in PREGAO:
            raise KeyError(f"{tk}: sem nome de pregão em proventos_ex.PREGAO — o provento já ex somaria zero (AUD-02)")
        regs = registros(tk, data_preco)
    bal = data_do_balanco(ref)
    classe = CLASSE.get(tk, "ON")
    depois = nao_ex = 0.0
    usados = []
    for r in regs:
        # a data-com nunca vem antes da aprovação: todo evento que importa tem data-com depois do balanço
        if r["tipo_acao"] != classe or not r["data_com"] or r["data_com"] <= bal:
            continue
        if not r["data_aprovacao"]:
            raise ValueError(f"{tk}: provento de data-com {r['data_com']} sem data de aprovação na B3 — classificar à mão")
        por_acao = r["valor"] / (r["lote"] or 1.0)
        # o fechamento da própria data-com ainda é "com" (a B3 calcula o yield com ele): ex no preço = data-com ANTES da data do preço
        if r["data_aprovacao"] > bal and r["data_com"] < data_preco:
            depois += por_acao
            usados.append(dict(r, parte="depois"))
        elif r["data_aprovacao"] <= bal and r["data_com"] >= data_preco:
            nao_ex += por_acao
            usados.append(dict(r, parte="nao_ex"))
    return {"depois": depois * n_acoes / 1000, "nao_ex": nao_ex * n_acoes / 1000, "eventos": usados}


def baixar(tks=None) -> None:
    """Baixa (sempre de novo) os proventos em dinheiro da B3 de cada ticker do mapa. Rodar a cada rodada, depois da data do preço."""
    sys.path.insert(0, str(AQUI))
    from backtest.precos.proventos_b3 import PAUSA, POR_PAGINA, _get
    PASTA.mkdir(parents=True, exist_ok=True)
    for tk in tks or sorted(PREGAO):
        resultados, pagina, total = [], 1, 1
        while pagina <= total:
            j = _get("GetListedCashDividends",
                     {"language": "pt-br", "pageNumber": pagina, "pageSize": POR_PAGINA, "tradingName": PREGAO[tk]},
                     lambda j: isinstance(j, dict) and "page" in j)
            total = int(j["page"].get("totalPages") or 0)
            resultados += j.get("results") or []
            pagina += 1
            time.sleep(PAUSA)
        if not resultados:
            raise ValueError(f"{tk}: a B3 não devolveu provento para o pregão {PREGAO[tk]!r} — conferir o nome")
        _arquivo(tk).write_text(json.dumps({"ticker": tk, "pregao": PREGAO[tk], "baixado_em": date.today().isoformat(),
                                            "results": resultados}, ensure_ascii=False), encoding="utf-8")
        print(tk, PREGAO[tk], len(resultados), "registros")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    baixar(sys.argv[1:] or None)
