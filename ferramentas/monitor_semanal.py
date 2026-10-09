"""Monitor semanal de preço do hall (Etapa 4 / F4, D12) — roda sozinho pelo Agendador do Windows.

O que faz:
  1. baixa de novo o COTAHIST ANUAL do ano corrente (a B3 o acumula no ano; ~90 MB) para um arquivo
     temporário e só troca o ZIP antigo depois que o novo abre E o parser confere o trailer — um
     download torto nunca apaga o bom;
  2. pega o fechamento do último pregão para os 41 do hall e para a fila do `06`;
  3. compara com compra (0,70×), saída (1,30× ou 1,50× pela exceção de qualidade) e central, que
     vêm de `universo.avaliar_todos()` — a mesma fonte do `03` (`precos_de_referencia`);
  4. grava `BOLETINS/AAAA-MM-DD-monitor.md` (lido pelo agente de notícias de sexta) e acrescenta a
     `monitor/historico.csv`.

**Nunca muda a palavra do `03`.** O central não mudou; quem muda a palavra é a reavaliação (05).
O monitor só diz quem cruzou uma fronteira e precisa de reavaliação antes de qualquer decisão.
NÃO CONCLUSIVO não tem compra nem saída (§9: a compra só vem da palavra FINAL) — rótulo "sem palavra" (AUD-43).

Código de saída (vira o LastTaskResult; o .vbs abre um aviso na tela se ≠ 0 — AUD-37):
0 ok · 20 DADO VELHO (último pregão > 7 dias) · 21 exceção (o boletim do dia diz "MONITOR FALHOU" com o
traceback). Códigos altos de propósito: 1 é o que o `cmd` e o Python devolvem quando nem chegam a rodar o main.

    cd ferramentas && python monitor_semanal.py [--sem-download] [--hoje AAAA-MM-DD]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import io
import math
import shutil
import sys
import time
import traceback
from pathlib import Path

import pandas as pd

from historico_arquivos import guardar

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
BOLETINS = RAIZ / "BOLETINS"
HISTORICO = AQUI / "monitor" / "historico.csv"
DIAS_VELHO = 7                 # último pregão mais antigo que isso -> "DADO VELHO" no topo
FAIXA_OBSERVACAO = 0.10        # até 10% acima da compra -> observação
# Carteira do Frank (PROMPT-AGENTE-NOTICIAS-SEXTA.md e diário 09, 05/10/2026: vender ITSA4, ABCB4,
# RANI3; manter ISAE4). Atualizar quando a carteira mudar — a F6 cria o registro real.
CARTEIRA = ("ISAE4", "ITSA4", "ABCB4", "RANI3")

COMPRA, OBSERVA, SAIDA, NEUTRO, SEM = "≤ COMPRA", "perto da compra", "≥ SAÍDA", "", "sem central"
NC = "sem palavra"             # NÃO CONCLUSIVO: nem compra nem saída pela régua
NAO_CONCLUSIVO = "NÃO CONCLUSIVO"
RC_VELHO, RC_FALHA = 20, 21    # lidos pelo agendador/monitor_semanal.vbs


# ------------------------------------------------------------------------------ COTAHIST
def atualizar_cotahist(ano: int, log=print) -> str:
    """Baixa o anual de `ano` de novo e regera o parquet. Troca atômica: o ZIP velho volta se o
    novo não abrir ou o trailer não conferir."""
    import requests
    from backtest import cotahist
    destino = cotahist.zip_de(ano)
    novo = destino.with_suffix(".novo")
    velho = destino.with_suffix(".anterior")
    ultimo = "sem url"
    for url in cotahist.URLS:
        for tentativa in range(1, cotahist.TENTATIVAS + 1):
            try:
                with requests.get(url.format(a=ano), timeout=600, stream=True) as r:
                    r.raise_for_status()
                    with novo.open("wb") as f:
                        for bloco in r.iter_content(chunk_size=1 << 20):
                            f.write(bloco)
                if not cotahist._zip_valido(novo):
                    raise OSError("ZIP novo não abre ou veio curto")
                break
            except Exception as e:                                  # noqa: BLE001 — rede: retenta
                novo.unlink(missing_ok=True)
                ultimo = f"{type(e).__name__}: {e}"
                time.sleep(5 * tentativa)
        else:
            continue
        break
    else:
        return f"falhou: {ultimo}"
    return trocar_e_gerar(ano, novo, destino, velho, cotahist.gerar)


def trocar_e_gerar(ano: int, novo: Path, destino: Path, velho: Path, gerar) -> str:
    """Põe `novo` no lugar de `destino` e gera o parquet; se o parser recusar, devolve o velho."""
    tinha = destino.exists()
    if tinha:
        shutil.copyfile(destino, velho)
    novo.replace(destino)
    try:
        gerar(ano)
    except Exception as e:                                          # noqa: BLE001
        motivo = f"parser recusou o arquivo novo ({type(e).__name__}: {e})"
        if not tinha:
            destino.replace(destino.with_suffix(".rejeitado"))
            return f"falhou: {motivo}; não havia arquivo anterior (o recusado ficou em .rejeitado)"
        velho.replace(destino)
        try:
            gerar(ano)
        except Exception as e2:                                     # noqa: BLE001
            return f"falhou: {motivo}; e o anterior também não regerou ({type(e2).__name__}: {e2})"
        return f"falhou: {motivo}; mantido o anterior"
    velho.unlink(missing_ok=True)
    return "atualizado"


def ultimos_precos(tickers, hoje: str) -> tuple[dict[str, float], str]:
    """{ticker: PREULT do último pregão <= hoje} e a data desse pregão."""
    from backtest import cotahist
    ano = int(hoje[:4])
    partes = [pd.read_parquet(cotahist.parquet_de(a), columns=["data", "ticker", "preult"])
              for a in (ano - 1, ano) if cotahist.parquet_de(a).exists()]
    d = pd.concat(partes, ignore_index=True)
    d = d[(d["data"] <= hoje) & (d["preult"] > 0)]
    pregao = str(d["data"].max())
    d = d[d["ticker"].isin(set(tickers))].sort_values("data").groupby("ticker").tail(1)
    return dict(zip(d["ticker"], d["preult"].astype(float))), pregao


# ------------------------------------------------------------------------------ alertas
def alerta(preco: float, compra: float, saida: float, palavra: str) -> str:
    """`palavra` é obrigatória (AUD-43): sem palavra final não há preço de compra nem de saída (§9)."""
    if palavra == NAO_CONCLUSIVO:
        return NC
    if not (math.isfinite(compra) and compra > 0 and math.isfinite(saida)):
        return SEM
    if preco <= compra:
        return COMPRA
    if preco >= saida:
        return SAIDA
    if preco <= compra * (1 + FAIXA_OBSERVACAO):
        return OBSERVA
    return NEUTRO


def referencias_do_hall() -> dict[str, dict]:
    """{ticker: central, compra, saida, saida_por_qualidade, palavra, lote} — motor do hall."""
    import universo
    out = {}
    for tk, it in universo.avaliar_todos().items():
        r = it["r"]
        central = float(r["central"])
        if "compra" in r:
            ref = {k: r[k] for k in ("compra", "saida", "saida_por_qualidade")}
        else:
            from motor_financeiras import precos_de_referencia
            ref = precos_de_referencia(central, False)
        out[tk] = dict(central=central, palavra=r["palavra"], lote=it["lote"], **ref)
    return out


def linhas_hall(refs: dict, precos: dict) -> list[dict]:
    out = []
    for tk in sorted(refs):
        r, p = refs[tk], precos.get(tk, math.nan)
        tem_regua = r["central"] > 0 and r["palavra"] != NAO_CONCLUSIVO
        compra, saida = (r["compra"], r["saida"]) if tem_regua else (math.nan, math.nan)
        out.append(dict(ticker=tk, lote=r["lote"], palavra=r["palavra"], preco=p, central=r["central"],
                        pc=p / r["central"] if r["central"] > 0 else math.nan, compra=compra,
                        saida=saida, saida_qualidade=r["saida_por_qualidade"],
                        alerta=alerta(p, compra, saida, r["palavra"]) if math.isfinite(p) else "sem preço",
                        carteira=tk in CARTEIRA))
    return out


def fila_do_06() -> pd.DataFrame:
    """Linhas da fila na triagem mais recente (triagem/dados/triagem_T.csv)."""
    arqs = sorted((AQUI / "triagem" / "dados").glob("triagem_*.csv"))
    if not arqs:
        return pd.DataFrame()
    d = pd.read_csv(arqs[-1])
    if "fila" not in d:
        return pd.DataFrame()
    d = d[d["fila"].notna()].sort_values("fila")
    d.attrs["arquivo"] = arqs[-1].name
    return d


# ------------------------------------------------------------------------------ saída
def _n(x, nd=2) -> str:
    if x is None or (isinstance(x, float) and not math.isfinite(x)):
        return "—"
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def markdown(hall: list[dict], fila: pd.DataFrame, precos_fila: dict, pregao: str, hoje: str,
             estado_download: str) -> str:
    dias = (dt.date.fromisoformat(hoje) - dt.date.fromisoformat(pregao)).days
    s = []
    if dias > DIAS_VELHO:
        s.append(f"> **DADO VELHO:** o último pregão é de {pregao}, {dias} dias antes de hoje. "
                 f"Download: {estado_download}.\n")
    s.append(f"# Monitor semanal de preço — {hoje}\n")
    import mercado
    mv = mercado.dados()      # AUD-78: o central é de uma data de taxa; o monitor a declara
    s.append(f"Fechamento de **{pregao}** (COTAHIST, B3). Centrais, compra e saída do `03`, calculados com rf "
             f"{mv['rf_real']:.2%} real e π {mv['pi']:.2%} de **{mv['data']}** ({mv['rf_tipo']}; "
             f"{mercado.idade_dias(mv['data'], hoje)} dias antes de hoje). "
             f"Download: {estado_download}. **O monitor não muda palavra:** quem cruzou uma fronteira "
             "precisa do `05-prompt-reavaliacao.md` antes de qualquer decisão.\n")
    alertas = [x for x in hall if x["alerta"] in (COMPRA, SAIDA, OBSERVA)]
    s.append("## Alertas\n")
    if alertas:
        s.append("| Ticker | Alerta | Preço | Compra | Saída | P/C | Palavra no 03 | Carteira |\n|---|---|---|---|---|---|---|---|")
        for x in sorted(alertas, key=lambda x: (x["alerta"] != COMPRA, x["alerta"] != SAIDA, x["ticker"])):
            s.append(f"| **{x['ticker']}** | {x['alerta']} | {_n(x['preco'])} | {_n(x['compra'])} | "
                     f"{_n(x['saida'])}{' (1,50×)' if x['saida_qualidade'] else ''} | {_n(x['pc'])} | "
                     f"{x['palavra']} | {'sim' if x['carteira'] else ''} |")
        s.append("\n≤ COMPRA → rodar o 05 antes de decidir · ≥ SAÍDA → rever a venda · perto da compra = até "
                 f"{FAIXA_OBSERVACAO:.0%} acima do preço de compra.")
    else:
        s.append("Nenhum papel do hall cruzou compra ou saída.")
    sem_palavra = [x["ticker"] for x in hall if x["carteira"] and x["alerta"] == NC]
    if sem_palavra:
        s.append(f"\n**Carteira sem palavra (NÃO CONCLUSIVO):** {', '.join(sem_palavra)} — sem preço de compra nem "
                 "de saída pela régua (§9); escrever a premissa que diverge (`trava_razao`) ou rodar o 05 antes de "
                 "qualquer decisão. Só a tese quebrada vende sem palavra.")
    s.append(f"\n*\"{NC}\" = NÃO CONCLUSIVO no `03`: o central não sustenta compra nem saída; o P/C é só informativo.*")
    s.append("\n## Carteira\n")
    s.append("| Ticker | Preço | Central | P/C | Compra | Saída | Alerta |\n|---|---|---|---|---|---|---|")
    for x in [x for x in hall if x["carteira"]]:
        s.append(f"| {x['ticker']} | {_n(x['preco'])} | {_n(x['central'])} | {_n(x['pc'])} | "
                 f"{_n(x['compra'])} | {_n(x['saida'])} | {x['alerta'] or '—'} |")
    s.append("\n## Hall completo (41)\n")
    s.append("| Ticker | Lote | Palavra no 03 | Preço | Central | P/C | Compra | Saída | Alerta |\n|---|---|---|---|---|---|---|---|---|")
    for x in sorted(hall, key=lambda x: (x["pc"] if math.isfinite(x["pc"]) else 99)):
        s.append(f"| {x['ticker']} | {x['lote']} | {x['palavra']} | {_n(x['preco'])} | {_n(x['central'])} | "
                 f"{_n(x['pc'])} | {_n(x['compra'])} | {_n(x['saida'])} | {x['alerta'] or '—'} |")
    if not fila.empty:
        s.append(f"\n## Fila da triagem ({fila.attrs.get('arquivo', '')}) — sem alerta, sem palavra\n")
        s.append("P/C proxy = preço ÷ central rápido do motor reduzido (erro e corte medidos: ver `06`).\n")
        s.append("| # | Ticker | Preço na triagem | Preço agora | P/C proxy agora |\n|---|---|---|---|---|")
        for x in fila.to_dict("records"):
            p = precos_fila.get(x["ticker"], math.nan)
            c = x.get("central")
            pc = p / c if (x.get("confiavel") in (True, "True") and c and c > 0) else math.nan
            s.append(f"| {int(x['fila'])} | {x['ticker']} | {_n(x['preco'])} | {_n(p)} | {_n(pc)} |")
    return "\n".join(s) + "\n"


def gravar_historico(hall: list[dict], pregao: str, hoje: str, caminho: Path | None = None) -> None:
    # o caminho é resolvido na CHAMADA: um default `= HISTORICO` fica preso na definição e o teste que troca
    # `HISTORICO` gravava no histórico versionado (achado na Onda 1.3)
    caminho = caminho or HISTORICO
    caminho.parent.mkdir(parents=True, exist_ok=True)
    cab = ["rodada", "pregao", "ticker", "preco", "central", "pc", "alerta"]
    linhas: dict[tuple[str, str, str], list] = {}
    if caminho.exists():
        with caminho.open(encoding="utf-8", newline="") as f:
            for r in csv.reader(f):
                if r and r != cab:
                    linhas[(r[0], r[1], r[2])] = r
    # AUD-83: upsert por (rodada, pregão, ticker) — rodar o monitor duas vezes no mesmo dia substitui, não duplica
    for x in hall:
        linhas[(hoje, pregao, x["ticker"])] = [hoje, pregao, x["ticker"], x["preco"], x["central"],
                                              round(x["pc"], 4) if math.isfinite(x["pc"]) else "", x["alerta"]]
    buf = io.StringIO(newline="")
    w = csv.writer(buf)
    w.writerow(cab)
    w.writerows(linhas.values())
    novo = buf.getvalue().encode("utf-8")
    guardar(caminho, "monitor historico", novo, RAIZ)      # AUD-84: a versão anterior vai para _historico/
    caminho.write_bytes(novo)


def boletim_de(hoje: str) -> Path:
    return BOLETINS / f"{hoje}-monitor.md"


def gravar_falha(hoje: str, erro: BaseException) -> Path:
    """AUD-37: a falha vira boletim (o agente de sexta e o Frank leem BOLETINS/, não o log ignorado pelo git).
    Se o boletim do dia já foi escrito antes da falha, ele fica, com a falha NO TOPO (o prompt de sexta e o aviso
    do .vbs procuram "MONITOR FALHOU" na abertura do arquivo)."""
    rastro = "".join(traceback.format_exception(type(erro), erro, erro.__traceback__))[-4000:]
    bloco = (f"> **MONITOR FALHOU** em {hoje}: `{type(erro).__name__}: {erro}`. Os alertas abaixo (se houver) "
             "podem estar incompletos; o boletim de uma semana anterior **não** vale como desta semana. "
             "Corrigir e rodar `python monitor_semanal.py` de novo.\n\n```\n" + rastro + "\n```\n")
    BOLETINS.mkdir(parents=True, exist_ok=True)
    destino = boletim_de(hoje)
    if destino.exists():
        destino.write_text(bloco + "\n" + destino.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    else:
        destino.write_text(bloco, encoding="utf-8", newline="\n")
    return destino


def _rodar(a) -> int:
    estado = "pulado (--sem-download)" if a.sem_download else atualizar_cotahist(int(a.hoje[:4]))
    print(f"COTAHIST {a.hoje[:4]}: {estado}", flush=True)
    refs = referencias_do_hall()
    fila = fila_do_06()
    tickers = set(refs) | set(fila["ticker"] if not fila.empty else [])
    precos, pregao = ultimos_precos(tickers, a.hoje)
    hall = linhas_hall(refs, precos)
    BOLETINS.mkdir(parents=True, exist_ok=True)
    saida = boletim_de(a.hoje)
    saida.write_text(markdown(hall, fila, precos, pregao, a.hoje, estado), encoding="utf-8", newline="\n")
    gravar_historico(hall, pregao, a.hoje)
    n = sum(x["alerta"] in (COMPRA, SAIDA) for x in hall)
    print(f"{saida.name} · pregão {pregao} · {n} alerta(s) de compra/saída")
    velho = (dt.date.fromisoformat(a.hoje) - dt.date.fromisoformat(pregao)).days > DIAS_VELHO
    return RC_VELHO if velho else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sem-download", action="store_true")
    ap.add_argument("--hoje", default=dt.date.today().isoformat())
    a = ap.parse_args(argv)
    try:
        return _rodar(a)
    except Exception as e:                                          # noqa: BLE001 — falha vira boletim e RC_FALHA
        traceback.print_exc()
        try:
            print(f"falha registrada em {gravar_falha(a.hoje, e).name}", flush=True)
        except Exception as e2:                                     # noqa: BLE001 — nem o boletim gravou: o log diz
            print(f"e o boletim de falha também não gravou ({type(e2).__name__}: {e2})", flush=True)
        return RC_FALHA


if __name__ == "__main__":
    sys.exit(main())
