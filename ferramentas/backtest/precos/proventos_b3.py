"""Fatia 9 — proventos em dinheiro (e a 2ª fonte de eventos em ações) da API pública da B3.

Uso: python -m backtest.precos.proventos_b3            (baixa o que falta; retomável)
     python -m backtest.precos.proventos_b3 --conferir (só mostra o estado do cache)

FONTE (nota A, a própria bolsa): sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/
  · GetListedCashDividends/{base64 json}  — histórico de proventos em dinheiro por `tradingName`.
    O `tradingName` é o nome de pregão, que é exatamente o NOMRES do COTAHIST (12 caracteres).
    Conferido em 06/10/2026: cobre DESLISTADAS (SMILES 2017-21, LOJAS AMERIC desde 1996, CIELO,
    SUL AMERICA), traz o valor NOMINAL da época e o fechamento da data-com
    (`closingPricePriorExDate`), que permite conferir cada linha contra o PREULT do COTAHIST.
    `pageSize` acima de ~120 devolve corpo inválido; a API devolve vazio intermitente → retry.
  · GetListedSupplementCompany/{base64 json} — `stockDividends` por raiz de 4 letras. INCOMPLETO
    (perde MGLU 2015/2017/2019 e as bonificações anuais da ITSA) e só cobre quem está listado hoje:
    é a 2ª fonte de eventos em ações, atrás do FRE da CVM (ver eventos.py).

Cache: um JSON por nome/raiz em backtest/dados/proventos/, com a data do download. Os arquivos
são o insumo bruto; nada aqui interpreta o dado (isso é `carregar_dinheiro`).
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import requests

AQUI = Path(__file__).resolve().parent.parent
PASTA = AQUI / "dados" / "proventos"
API = "https://sistemaswebb3-listados.b3.com.br/listedCompaniesProxy/CompanyCall/"
CABECALHO = {"User-Agent": "Mozilla/5.0"}
POR_PAGINA = 120
TENTATIVAS = 5
PAUSA = 0.3


def _b64(o: dict) -> str:
    return base64.b64encode(json.dumps(o).encode()).decode()


def _get(endpoint: str, payload: dict, valido, vazios_aceitos: int = 0) -> object:
    """GET com retry. `valido(json)` decide se a resposta é boa; corpo vazio/ruim conta como falha.

    `vazios_aceitos` > 0: depois de tantos corpos vazios SEGUIDOS (HTTP 200), devolve None em vez
    de falhar — o suplemento responde assim para quem não está listado hoje (ABRE, ARZZ, KROT).
    """
    erro = ""
    vazios = 0
    for i in range(TENTATIVAS):
        try:
            r = requests.get(API + endpoint + "/" + _b64(payload), headers=CABECALHO, timeout=60)
            if r.status_code == 200 and not r.text.strip():
                vazios += 1
                if vazios_aceitos and vazios >= vazios_aceitos:
                    return None
            if r.status_code == 200 and r.text.strip():
                j = r.json()
                if valido(j):
                    return j
                erro = f"resposta inválida: {r.text[:120]!r}"
            else:
                erro = f"HTTP {r.status_code}"
        except (requests.RequestException, ValueError) as e:
            erro = repr(e)[:160]
        time.sleep(2 ** (i + 1))
    raise RuntimeError(f"{endpoint} {payload}: {erro}")


def _slug(nome: str) -> str:
    base = re.sub(r"[^A-Za-z0-9]+", "_", nome).strip("_") or "vazio"
    return f"{base}_{hashlib.sha1(nome.encode()).hexdigest()[:6]}"


def arquivo_dinheiro(nome: str) -> Path:
    return PASTA / "dinheiro" / f"{_slug(nome)}.json"


def arquivo_suplemento(raiz: str) -> Path:
    return PASTA / "suplemento" / f"{raiz}.json"


def baixar_dinheiro(nome: str) -> str:
    f = arquivo_dinheiro(nome)
    if f.exists():
        return "em disco"
    resultados: list[dict] = []
    pagina, total = 1, 1
    while pagina <= total:
        j = _get("GetListedCashDividends",
                 {"language": "pt-br", "pageNumber": pagina, "pageSize": POR_PAGINA, "tradingName": nome},
                 lambda j: isinstance(j, dict) and "page" in j)
        total = int(j["page"].get("totalPages") or 0)
        resultados += j.get("results") or []
        pagina += 1
        time.sleep(PAUSA)
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".parcial")
    tmp.write_text(json.dumps({"nome": nome, "baixado_em": date.today().isoformat(),
                               "results": resultados}, ensure_ascii=False), encoding="utf-8")
    tmp.replace(f)
    return f"baixado ({len(resultados)})"


def baixar_suplemento(raiz: str) -> str:
    f = arquivo_suplemento(raiz)
    if f.exists():
        return "em disco"
    j = _get("GetListedSupplementCompany", {"issuingCompany": raiz, "language": "pt-br"},
             lambda j: isinstance(j, (list, dict)), vazios_aceitos=2)
    j = j[0] if isinstance(j, list) and j else (j if isinstance(j, dict) else {})
    f.parent.mkdir(parents=True, exist_ok=True)
    tmp = f.with_suffix(".parcial")
    tmp.write_text(json.dumps({"raiz": raiz, "baixado_em": date.today().isoformat(),
                               "stockDividends": j.get("stockDividends") or []},
                              ensure_ascii=False), encoding="utf-8")
    tmp.replace(f)
    time.sleep(PAUSA)
    return "baixado"


# ----------------------------------------------------------------------------- o que baixar
def alvos() -> tuple[list[str], list[str]]:
    """Nomes de pregão e raízes de TODO papel que esteve no universo de algum corte.

    Por CODISI, não por ticker: a companhia que troca de nome de pregão depois de T (LOJAS AMERIC
    -> AMERICANAS) paga proventos sob o nome novo, e esses entram no retorno T -> T+h.
    """
    from .espinha import precos_acoes, universo_por_corte
    u = universo_por_corte()
    p = precos_acoes()
    isins = p.loc[p["ticker"].isin(set(u["ticker"])), "codisi"].unique()
    q = p[p["codisi"].isin(isins)]
    nomes = sorted(set(q["nomres"].str.strip()) - {""})
    raizes = sorted(set(q["ticker"].str[:4]))
    return nomes, raizes


# ----------------------------------------------------------------------------- leitura
def _num(s: str | None) -> float:
    if s is None or str(s).strip() == "":
        return float("nan")
    return float(str(s).replace(".", "").replace(",", "."))


def _iso(s: str | None) -> str:
    s = (s or "").strip()
    return f"{s[6:10]}-{s[3:5]}-{s[0:2]}" if len(s) == 10 and s[2] == "/" else ""


def carregar_dinheiro() -> pd.DataFrame:
    """Todos os registros em cache, brutos mas tipados. Uma linha por (nome, registro)."""
    linhas = []
    for f in sorted((PASTA / "dinheiro").glob("*.json")):
        j = json.loads(f.read_text(encoding="utf-8"))
        for r in j["results"]:
            linhas.append({
                "nome": j["nome"], "tipo_acao": (r.get("typeStock") or "").strip().upper(),
                "tipo": (r.get("corporateAction") or "").strip().upper(),
                "data_aprovacao": _iso(r.get("dateApproval")), "data_com": _iso(r.get("lastDatePriorEx")),
                "valor": _num(r.get("valueCash")), "lote": _num(r.get("quotedPerShares")) or 1.0,
                "preco_data_com": _num(r.get("closingPricePriorExDate")),
                "data_preco_com": _iso(r.get("dateClosingPricePriorExDate")),
            })
    return pd.DataFrame(linhas)


def carregar_suplemento() -> pd.DataFrame:
    linhas = []
    for f in sorted((PASTA / "suplemento").glob("*.json")):
        j = json.loads(f.read_text(encoding="utf-8"))
        for r in j["stockDividends"]:
            linhas.append({"raiz": j["raiz"], "tipo": (r.get("label") or "").strip().upper(),
                           "fator_b3": _num(r.get("factor")), "data_com": _iso(r.get("lastDatePrior")),
                           "data_aprovacao": _iso(r.get("approvedOn")), "isin": r.get("isinCode") or ""})
    return pd.DataFrame(linhas)


CONFERE_PRECO = 0.01
DUPLICATA_TOL = 0.01


def dinheiro_por_ticker(precos: pd.DataFrame, pregoes: list[str], linhagem: dict[str, str],
                        desde: str = "2014-01-01") -> tuple[pd.DataFrame, pd.DataFrame]:
    """Proventos casados a ticker, com data ex. Devolve (casados, não_casados).

    Casamento: candidatos = tickers da MESMA LINHAGEM (`espinha.linhagem`: sucessão de código,
    TRPL4 -> ISAE4) de qualquer papel que já teve aquele nome de pregão e aquela classe. Por linhagem
    e não por nome porque a B3 devolve o histórico inteiro sob o nome ATUAL (ISA ENERGIA traz os
    proventos da época TRAN PAULIST/TRPL4), e não por ISIN porque o ISIN muda com o código.
    Fica o candidato cujo PREULT na data do fechamento da data-com bate com o `closingPrice` do
    registro a ±1%. Medido em 06/10/2026: dos casados, a razão é 1,000 com desvio zero — o valor do
    provento é nominal da época, nunca ajustado por evento posterior (risco #4 do plano).
    Data ex = 1º pregão do calendário depois da data-com. Valor por ação = valueCash / lote.
    """
    import bisect
    c = carregar_dinheiro()
    c = c[c["data_com"] >= desde].reset_index(drop=True)
    c["rid"] = c.index
    q = precos.assign(classe=precos["especi"].str.split().str[0], nome=precos["nomres"].str.strip())
    q["lin"] = q["ticker"].map(linhagem)
    ids = q.drop_duplicates(["nome", "classe", "lin"])[["nome", "classe", "lin"]]
    membros = q.drop_duplicates(["lin", "ticker"])[["lin", "ticker"]]
    cand = ids.merge(membros, on="lin")[["nome", "classe", "ticker"]].drop_duplicates()
    m = c.merge(cand, left_on=["nome", "tipo_acao"], right_on=["nome", "classe"], how="inner")
    px = q.set_index(["ticker", "data"])["preult"]
    m["preco_cotahist"] = [px.get((t, d), np.nan) for t, d in zip(m["ticker"], m["data_preco_com"])]
    m["conferido"] = (m["preco_data_com"] / m["lote"] / m["preco_cotahist"] - 1).abs() <= CONFERE_PRECO
    # Papel que não negociou na data-com (TAEE3 em 2016) não tem como ser conferido: entra se for o
    # ÚNICO candidato e não tiver preço naquele dia, com `conferido=False` para o relatório contar.
    n_cand = m.groupby("rid")["ticker"].transform("size")
    sem_preco = m["preco_cotahist"].isna()
    m = m[m["conferido"] | ((n_cand == 1) & sem_preco)]
    nao = c[~c["rid"].isin(m["rid"])]
    # Um por (ticker, data-com, tipo, valor). Duas origens de repetição: o mesmo evento chega pelo
    # nome antigo e pelo novo; e a B3 lista uma linha POR PARCELA com o valor TOTAL (CEMIG paga em
    # 30/06 e 30/12 e as duas linhas trazem o mesmo `rate`). Medido em 06/10/2026 pela queda do
    # preço no dia ex: inclinação queda x valor = 0,76 nos repetidos contra 0,82 nos únicos (se o
    # `rate` fosse por parcela, os repetidos dariam ~1,6). Somar as linhas dobraria o provento.
    # Repetição com diferença na 7ª-8ª casa (RECV3 0,341323 x 0,341322; ALLD3; TIMS3 a 0,2%) também é
    # repetição (achado do `adversario`): dentro de (ticker, data-com, tipo), valor a <= 1% do
    # anterior é a mesma linha. Proventos distintos no mesmo dia têm valores longe (PETR4 3T22:
    # 1,1558 e 1,6002).
    m = m.sort_values(["ticker", "data_com", "tipo", "valor"])
    ant = m.groupby(["ticker", "data_com", "tipo"])["valor"].shift(1)
    m = m[~((m["valor"] / ant - 1).abs() <= DUPLICATA_TOL)]
    m["data_ex"] = [pregoes[i] if i < len(pregoes) else ""
                    for i in (bisect.bisect_right(pregoes, d) for d in m["data_com"])]
    m["valor_acao"] = m["valor"] / m["lote"]
    cols = ["ticker", "data_com", "data_ex", "tipo", "valor_acao", "conferido", "nome", "tipo_acao",
            "data_aprovacao"]
    return m[cols].sort_values(["ticker", "data_ex"], ignore_index=True), nao


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--conferir", action="store_true")
    args = p.parse_args(argv)
    nomes, raizes = alvos()
    faltam_n = [n for n in nomes if not arquivo_dinheiro(n).exists()]
    faltam_r = [r for r in raizes if not arquivo_suplemento(r).exists()]
    print(f"{len(nomes)} nomes ({len(faltam_n)} faltam) · {len(raizes)} raízes ({len(faltam_r)} faltam)",
          flush=True)
    if args.conferir:
        return 0
    falhas = []
    for i, n in enumerate(faltam_n, 1):
        try:
            s = baixar_dinheiro(n)
        except RuntimeError as e:
            s = f"falhou: {e}"
            falhas.append(n)
        if i % 25 == 0 or s.startswith("falhou"):
            print(f"  [{i}/{len(faltam_n)}] {n}: {s}", flush=True)
    for i, r in enumerate(faltam_r, 1):
        try:
            baixar_suplemento(r)
        except RuntimeError as e:
            falhas.append(r)
            print(f"  suplemento {r}: falhou: {e}", flush=True)
    print(f"fim: {len(falhas)} falhas", flush=True)
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
