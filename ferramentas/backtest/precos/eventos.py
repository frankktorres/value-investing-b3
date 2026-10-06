"""Fatia 10 — eventos em ações (desdobramento, grupamento, bonificação) por ticker e data ex.

O COTAHIST publica preço NOMINAL: no dia ex de um desdobramento 1:8 o preço cai 87,5% sem que
ninguém tenha perdido nada. Sem o fator, o retorno total erra de forma multiplicativa.

DATA EX — vem do próprio COTAHIST. O 2º token de ESPECI carrega a marca "ex" por ~8 pregões
("PN  EB  N1"); o 1º dia da marca é a data ex. Medido em 06/10/2026: `EB` marca bonificação E
desdobramento (MGLU3 1:8 em 2017 e 2019, -87%), `EG` marca grupamento (MGLU3 8:1 em 2015, +630%),
e as compostas (`EDB`, `EJB`) juntam provento em dinheiro com bonificação. Logo: marca de evento em
ações = token que começa com "E" e contém "B" ou "G".

FATOR — três fontes, nesta ordem, e cada evento leva `fonte`:
  1. FRE da CVM (fonte A), `capital_social_desdobramento`: quantidade antes e depois da aprovação,
     por classe, aprovações de 2010 a 2023 (a tabela some do FRE de 2024). Pega o que a B3 perde:
     as bonificações anuais da Itaúsa (10% em 2014, 2015, 2016, 2018...).
  2. Suplemento da B3 (fonte A, incompleto): `factor` em % para desdobramento/bonificação (100 =
     dobra; 25 = +25%) e multiplicador direto para grupamento (0,1 = 10:1). Casado por ISIN.
  3. INFERIDO do preço, só onde há marca e nenhuma fonte: razão do dia descontado o Ibovespa,
     encaixada numa grade declarada (`config.proporcoes_evento` + `config.bonificacoes_grade`)
     dentro de `config.tolerancia_proporcao`. Sem encaixe → `sem_fator`: a janela que o atravessa
     sai do painel com status, não entra com retorno errado.
  Detector (sem marca): |retorno do dia descontado o Ibov| > `config.salto_bloqueio` com razão que
  encaixa em `proporcoes_evento` é só REPORTADO (`salto_nao_ajustado`, fator 1): medido, é tick de
  centavo e colapso real (AMBP3 2025), e ajustar apagaria as quebras.

Cada evento com fonte é CONFERIDO contra o preço (`confere_preco`): fator × razão do dia ≈ 1.

`fator` = ações depois / ações antes, por ação antiga. Retorno no dia ex = P_ex × fator / P_antes.
"""
from __future__ import annotations

import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from ..config import PADRAO, Config
from ..ledger.identidade import mapa_ticker_cnpj, tickers_do_cnpj

CVM = Path(__file__).resolve().parent.parent.parent / "dados" / "cvm"
JANELA_APROVACAO_DIAS = 120     # aprovação -> data ex; a AGE costuma marcar o ex em semanas
CONFERE_TOLERANCIA = 0.15       # |fator x razão - 1|: acima disso a fonte e o preço discordam
TOLERANCIA_FONTE_INCRIVEL = 0.05  # encaixe do preço quando a fonte erra por mais de 50%


# ----------------------------------------------------------------------------- marcas do COTAHIST
def _marca(especi: pd.Series) -> pd.Series:
    t = especi.str.split()
    return t.apply(lambda x: x[1] if len(x) >= 2 and x[1].startswith("E") else "")


def preparar(precos: pd.DataFrame, ibov: pd.Series) -> pd.DataFrame:
    """Acrescenta `marca`, `inicio_marca`, `razao` (P/P_anterior) e `razao_adj` (descontado o Ibov)."""
    d = precos.sort_values(["ticker", "data"], ignore_index=True).copy()
    d["marca"] = _marca(d["especi"])
    ant = d.groupby("ticker")["marca"].shift(1).fillna("")
    d["inicio_marca"] = (d["marca"] != "") & (d["marca"] != ant)
    # Evento em ações NOVO só quando a marca B/G aparece e a anterior não a tinha: EB -> EJB é o JCP
    # entrando DURANTE a mesma bonificação (ITSA4 2022-11-11 EB, 2022-11-21 EJB), não outro evento.
    d["inicio_evento_acoes"] = marca_de_acoes(d["marca"]) & ~marca_de_acoes(ant)
    d["preco_ant"] = d.groupby("ticker")["preult"].shift(1)
    d["data_ant"] = d.groupby("ticker")["data"].shift(1)
    d["razao"] = d["preult"] / d["preco_ant"]
    ib = ibov.reindex(d["data"]).to_numpy()
    ib_ant = ibov.reindex(d["data_ant"].fillna("")).to_numpy()
    d["razao_adj"] = d["razao"] / (ib / ib_ant)
    return d


def marca_de_acoes(m: pd.Series) -> pd.Series:
    return m.str.startswith("E") & (m.str.contains("B") | m.str.contains("G"))


# ----------------------------------------------------------------------------- fonte 1: FRE
def _classe(especi: str) -> str:
    c = especi.split()[0] if especi else ""
    return "on" if c == "ON" else ("pn" if c.startswith("PN") else "total")


def eventos_fre() -> pd.DataFrame:
    """Uma linha por (cnpj, aprovação, tipo), com fatores total/ON/PN. Última versão do FRE vence."""
    partes = []
    for a in range(2010, 2030):
        f = CVM / f"fre_{a}.zip"
        if not f.exists():
            continue
        with zipfile.ZipFile(f) as z:
            nome = f"fre_cia_aberta_capital_social_desdobramento_{a}.csv"
            if nome not in z.namelist():
                continue
            d = pd.read_csv(z.open(nome), sep=";", encoding="latin-1", dtype=str)
        d["ano_fre"] = a
        partes.append(d)
    d = pd.concat(partes, ignore_index=True)
    n = lambda c: pd.to_numeric(d[c], errors="coerce")          # noqa: E731
    out = pd.DataFrame({
        "cnpj": d["CNPJ_Companhia"], "aprovacao": d["Data_Aprovacao"].str[:10],
        "tipo": d["Tipo_Evento"].str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii")
                 .str.upper().str.strip(),
        "f_total": n("Quantidade_Total_Acoes_Depois_Aprovacao") / n("Quantidade_Total_Acoes_Antes_Aprovacao"),
        "f_on": n("Quantidade_Acoes_Ordinarias_Depois_Aprovacao") / n("Quantidade_Acoes_Ordinarias_Antes_Aprovacao"),
        "f_pn": n("Quantidade_Acoes_Preferenciais_Depois_Aprovacao") / n("Quantidade_Acoes_Preferenciais_Antes_Aprovacao"),
        "ano_fre": d["ano_fre"], "versao": pd.to_numeric(d["Versao"], errors="coerce"),
    })
    out = out.replace([np.inf, -np.inf], np.nan)
    out = out[out["f_total"].notna() & (out["f_total"] > 0) & (out["f_total"] != 1)]
    out = out.sort_values(["cnpj", "aprovacao", "tipo", "ano_fre", "versao"])
    return out.groupby(["cnpj", "aprovacao", "tipo"], as_index=False).tail(1).reset_index(drop=True)


def _casar_fre(fre: pd.DataFrame, d: pd.DataFrame, linhagem: dict[str, str] | None = None
               ) -> pd.DataFrame:
    """Cada evento do FRE -> (ticker, data ex) pelo 1º dia de marca B/G após a aprovação.

    Raízes do CNPJ = as da FCA MAIS as dos códigos antigos da mesma linhagem: a FCA reescreve o
    passado com o código atual (COGN3 "desde 2012"), e o evento de 2015 da KROT3 sumiria."""
    por_cnpj = tickers_do_cnpj(mapa_ticker_cnpj())
    if linhagem:
        membros: dict[str, set[str]] = {}
        for t, lin in linhagem.items():
            membros.setdefault(lin, set()).add(t)
        por_cnpj = {c: ts | {m for t in ts if t in linhagem for m in membros[linhagem[t]]}
                    for c, ts in por_cnpj.items()}
    inicios = d[d["inicio_evento_acoes"]]
    inicios_por_raiz = {r: g for r, g in inicios.groupby(inicios["ticker"].str[:4])}
    linhas = []
    for e in fre.itertuples(index=False):
        raizes = {t[:4] for t in por_cnpj.get(e.cnpj, ())}
        fim = (pd.Timestamp(e.aprovacao) + pd.Timedelta(days=JANELA_APROVACAO_DIAS)).strftime("%Y-%m-%d")
        for r in raizes:
            g = inicios_por_raiz.get(r)
            if g is None:
                continue
            g = g[(g["data"] >= e.aprovacao) & (g["data"] <= fim)]
            for t, gt in g.groupby("ticker"):
                x = gt.iloc[0]
                # Fator da classe do papel ou o total: as colunas por classe do FRE às vezes vêm
                # tortas (ITSA4 2018: PN 1,16, total 1,10, preço diz 1,09). Entre os DOIS valores
                # da fonte, vence o que o preço do dia ex confirma — o preço escolhe, não inventa.
                cl = _classe(x["especi"])
                cands = [e.f_total] + ([getattr(e, f"f_{cl}")] if cl != "total" else [])
                cands = [c for c in cands if isinstance(c, float) and np.isfinite(c) and c > 0]
                ra = x["razao_adj"]
                f = min(cands, key=lambda c: abs(c * ra - 1) if np.isfinite(ra) else 0.0)
                linhas.append({"ticker": t, "data_ex": x["data"], "fator": float(f), "fonte": "fre",
                               "tipo": e.tipo, "aprovacao": e.aprovacao, "marca": x["marca"]})
    return pd.DataFrame(linhas)


# ----------------------------------------------------------------------------- fonte 2: B3
FATOR_EM_PORCENTO = {"DESDOBRAMENTO", "BONIFICACAO"}


def _casar_b3(sup: pd.DataFrame, d: pd.DataFrame, pregoes: list[str]) -> pd.DataFrame:
    if sup.empty:
        return pd.DataFrame()
    import bisect
    isin_ticker = d.drop_duplicates(["codisi", "ticker"]).groupby("codisi")["ticker"].agg(list).to_dict()
    linhas = []
    for e in sup.drop_duplicates(["isin", "data_com", "tipo", "fator_b3"]).itertuples(index=False):
        if e.tipo in FATOR_EM_PORCENTO:
            f = 1 + e.fator_b3 / 100
        elif e.tipo == "GRUPAMENTO":
            f = e.fator_b3
        else:
            continue
        i = bisect.bisect_right(pregoes, e.data_com)
        # data-com antes do 1º pregão em disco (PETR 2008...) cairia no 1º dia do arquivo
        if not e.data_com or e.data_com < pregoes[0] or i >= len(pregoes) or not (f > 0):
            continue
        for t in isin_ticker.get(e.isin, []):
            linhas.append({"ticker": t, "data_ex": pregoes[i], "fator": float(f), "fonte": "b3",
                           "tipo": e.tipo, "aprovacao": e.data_aprovacao, "marca": ""})
    return pd.DataFrame(linhas)


# ----------------------------------------------------------------------------- fonte 3: inferido
def grade(cfg: Config) -> np.ndarray:
    """Multiplicadores aceitos, MAIS o 1,0 (= nenhum evento): sem ele, qualquer razão em
    [0,9996; 1,0094) encaixava sozinha em 1,02 e o dia parado ganhava uma bonificação inventada."""
    return np.array(sorted(set(cfg.proporcoes_evento) | set(cfg.bonificacoes_grade) | {1.0}))


def _inv(r: float) -> float:
    """1/razão; preço zero ou ausente no COTAHIST vira NaN (nunca encaixa)."""
    return 1 / r if r and np.isfinite(r) else float("nan")


def encaixe(multiplicador: float, g: np.ndarray, tol: float) -> float | None:
    """Fator da grade a menos de `tol` (relativo) do multiplicador, se for ÚNICO; senão None."""
    if not np.isfinite(multiplicador) or multiplicador <= 0:
        return None
    perto = g[np.abs(multiplicador / g - 1) <= tol]
    return float(perto[0]) if len(perto) == 1 else None


# ----------------------------------------------------------------------------- tabela final
def construir(precos: pd.DataFrame, ibov: pd.Series, suplemento: pd.DataFrame | None = None,
              fre: pd.DataFrame | None = None, cfg: Config = PADRAO,
              linhagem: dict[str, str] | None = None) -> pd.DataFrame:
    """Tabela (ticker, data_ex, fator, fonte, tipo, razao_adj, confere_preco) — um evento por dia."""
    d = preparar(precos, ibov)
    pregoes = sorted(d["data"].unique())
    fre = eventos_fre() if fre is None else fre
    suplemento = pd.DataFrame() if suplemento is None else suplemento
    fontes = pd.concat([_casar_fre(fre, d, linhagem), _casar_b3(suplemento, d, pregoes)],
                       ignore_index=True)

    ordem = {"fre": 0, "b3": 1}
    if not fontes.empty:
        # O MESMO evento pelas duas fontes em dias diferentes (B3 = data-com + 1; FRE = 1º dia da
        # marca): UNIP3 2015 chegava como 0,1 em 12/01 e 0,1 em 13/01 e, sem negócio no dia 12,
        # os dois caíam no mesmo pregão -> fator 0,01. B3 a <= 20 dias de um FRE com o mesmo fator
        # (±1%) é descartado.
        fontes = _sem_duplicata_b3(fontes)
        fontes["ordem"] = fontes["fonte"].map(ordem)
        # mesmo (ticker, data ex) nas duas fontes: vence o FRE (quantidades, não porcentagem)
        # Eventos DISTINTOS da mesma fonte no mesmo dia ex se compõem: KLBN 2014 (desdobramento +
        # bonificação), LIGT3 2021 (grupamento 100:1 + desdobramento 1:100 = fator 1).
        fontes = (fontes.groupby(["ticker", "data_ex", "fonte", "ordem"], as_index=False)
                  .agg(fator=("fator", "prod"), tipo=("tipo", lambda s: "+".join(sorted(set(s)))),
                       aprovacao=("aprovacao", "first"), marca=("marca", "first")))
        fontes = fontes.sort_values(["ticker", "data_ex", "ordem"])
        divergem = (fontes.groupby(["ticker", "data_ex"])["fator"]
                    .agg(lambda s: s.max() / s.min() - 1 > 0.01))
        fontes = fontes.groupby(["ticker", "data_ex"], as_index=False).first()
        fontes["fontes_divergem"] = fontes.set_index(["ticker", "data_ex"]).index.map(divergem).to_numpy()
    else:
        fontes = pd.DataFrame(columns=["ticker", "data_ex", "fator", "fonte", "tipo", "aprovacao",
                                       "marca", "fontes_divergem"])

    g = grade(cfg)
    chave = d.set_index(["ticker", "data"])
    conhecidos = set(zip(fontes["ticker"], fontes["data_ex"]))
    # marca B/G sem fonte (nem no próprio dia nem a até 3 pregões do ticker) -> inferir
    inferidos = []
    vizinhos = {}
    for t, gt in fontes.groupby("ticker"):
        vizinhos[t] = set(gt["data_ex"])
    sem_fonte = d[d["inicio_evento_acoes"]]
    for x in sem_fonte.itertuples(index=False):
        if (x.ticker, x.data) in conhecidos:
            continue
        # marca a até 10 pregões de um evento com fonte é a cauda dele (VIVT3: B3 2,0 em 15/04/2025
        # e outra marca "EBG" em 28/04 com razão 1,0009 — virava `sem_fator` e tirava 8 linhas)
        if _perto(x.ticker, x.data, vizinhos, pregoes, n=10):
            continue
        f = encaixe(_inv(x.razao_adj), g, cfg.tolerancia_proporcao)
        inferidos.append({"ticker": x.ticker, "data_ex": x.data, "fator": f if f else np.nan,
                          "fonte": "inferido" if f else "sem_fator", "tipo": "MARCA " + x.marca,
                          "aprovacao": "", "marca": x.marca, "fontes_divergem": False})
    # detector: salto sem marca nem fonte que encaixa numa proporção de desdobramento/grupamento
    prop = np.array(sorted(cfg.proporcoes_evento))
    salto = d[(d["marca"] == "") & ((d["razao_adj"] - 1).abs() > cfg.salto_bloqueio)]
    for x in salto.itertuples(index=False):
        if (x.ticker, x.data) in conhecidos or _perto(x.ticker, x.data, vizinhos, pregoes):
            continue
        f = encaixe(_inv(x.razao_adj), prop, cfg.tolerancia_proporcao)
        if f:
            # REPORTA, não ajusta (fator 1): medido em 06/10/2026, os saltos sem marca que encaixam
            # em 2x/0,5x são movimento real — tick de centavo em papel de centavos (PDGR3 alternando
            # x2/x0,5 em dias seguidos, OGXP3, MMXM3) e o colapso da AMBP3 em out/2025 (-49%).
            # Ajustar apagaria justamente as quebras. O COTAHIST marca todo evento verdadeiro visto.
            inferidos.append({"ticker": x.ticker, "data_ex": x.data, "fator": 1.0,
                              "fonte": "salto_nao_ajustado", "tipo": f"SALTO ~{f:g}x", "aprovacao": "",
                              "marca": "", "fontes_divergem": False})
    ev = pd.concat([fontes.drop(columns=["ordem"], errors="ignore"), pd.DataFrame(inferidos)],
                   ignore_index=True)
    if ev.empty:
        return ev
    ev["razao_adj"] = [chave["razao_adj"].get((t, dt), np.nan) for t, dt in zip(ev["ticker"], ev["data_ex"])]
    ev["confere_preco"] = (ev["fator"] * ev["razao_adj"] - 1).abs() <= CONFERE_TOLERANCIA
    # Fonte contrariada pelo preço: o preço só CORRIGE quando encaixa sozinho na grade (BIDI 2021:
    # FRE diz 22,6, o dia ex diz 3,1). Sem encaixe a fonte fica, com a flag — grupamento de papel
    # em crise costuma cair forte no próprio dia ex (IRBR3 2023, PDGR3 2023) e a fonte está certa.
    # Discordância acima de 50% (fator x razão fora de [0,5; 1,5]) não é queda do dia: a fonte não
    # é crível, e aí o preço encaixa com tolerância de 5% ou o evento vira `sem_fator`.
    ruim = ev["fonte"].isin(["fre", "b3"]) & ~ev["confere_preco"] & ev["razao_adj"].notna()
    for i in ev.index[ruim]:
        r = ev.at[i, "razao_adj"]
        f = encaixe(_inv(r), g, cfg.tolerancia_proporcao)
        incrivel = not (0.5 <= ev.at[i, "fator"] * r <= 1.5)
        if f is None and incrivel:
            f = encaixe(_inv(r), g, TOLERANCIA_FONTE_INCRIVEL)
        if f:
            ev.at[i, "fonte"] = ev.at[i, "fonte"] + "_corrigido_preco"
            ev.at[i, "fator"] = f
            ev.at[i, "confere_preco"] = True
        elif incrivel:
            ev.at[i, "fonte"] = "sem_fator"
            ev.at[i, "fator"] = np.nan
    # `sem_fator` de fonte incrível quando a OUTRA fonte, conferida pelo preço, traz o mesmo evento a
    # até 20 dias (SANB3 2014: B3 1,0476 em 28/05 confere; FRE composto 0,019 em 29/05 não) — sai.
    ok = ev[ev["fonte"].isin(["fre", "b3"]) & ev["confere_preco"]]
    if not ok.empty:
        j = ev[ev["fonte"] == "sem_fator"].reset_index().merge(ok[["ticker", "data_ex"]], on="ticker",
                                                               suffixes=("", "_ok"))
        perto = (pd.to_datetime(j["data_ex"]) - pd.to_datetime(j["data_ex_ok"])).abs() <= pd.Timedelta(days=20)
        ev = ev.drop(index=j.loc[perto, "index"].unique())
    return ev.sort_values(["ticker", "data_ex"], ignore_index=True)


def _sem_duplicata_b3(fontes: pd.DataFrame, dias: int = 20, tol: float = 0.01) -> pd.DataFrame:
    fre = fontes[fontes["fonte"] == "fre"]
    if fre.empty:
        return fontes
    b3 = fontes[fontes["fonte"] == "b3"].reset_index()
    j = b3.merge(fre[["ticker", "data_ex", "fator"]], on="ticker", suffixes=("", "_fre"))
    perto = (pd.to_datetime(j["data_ex"]) - pd.to_datetime(j["data_ex_fre"])).abs() <= pd.Timedelta(days=dias)
    igual = (j["fator"] / j["fator_fre"] - 1).abs() <= tol
    return fontes.drop(index=j.loc[perto & igual, "index"].unique())


def _perto(ticker: str, data: str, vizinhos: dict, pregoes: list[str], n: int = 3) -> bool:
    import bisect
    datas = vizinhos.get(ticker)
    if not datas:
        return False
    i = bisect.bisect_left(pregoes, data)
    janela = pregoes[max(0, i - n): i + n + 1]
    return any(x in datas for x in janela)


def fator_entre(eventos: pd.DataFrame, ticker: str, de: str, ate: str) -> float:
    """Produto dos fatores com data ex em (de, ate]. Para ajustar a contagem de ações do FRE
    (aprovada em `de`) até o preço de `ate`. NaN se algum evento no intervalo não tem fator."""
    e = eventos[(eventos["ticker"] == ticker) & (eventos["data_ex"] > de) & (eventos["data_ex"] <= ate)]
    return float(e["fator"].prod()) if e["fator"].notna().all() else float("nan")
