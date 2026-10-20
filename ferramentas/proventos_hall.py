"""DPA/JCP por ano da data-com das não financeiras do hall, da API pública da B3 (nota A) — fase 3, fatia 2 (20/10/2026).

Antes o DPA/JCP das não financeiras do lote vinha da StatusInvest (C), com correções à mão (`lote4.corrigir_proventos`,
`lote6.ajustar_dpa`). Agora sai do cache do hall em dados/proventos_hall/ (o mesmo do provento já ex, `proventos_ex.py`) e é
aplicado em `motor_nao_financeiras.SI` no carregamento (`aplicar`), antes de qualquer lote — o resultado não depende mais da
ordem de import (AUD-26). A série da StatusInvest fica ao lado (`dpa_statusinvest`/`jcp_statusinvest`) só para a tabela
B3 × StatusInvest e para quem ainda a usa de propósito (g1 da WEGE3, fatia 3).

Regras (generaliza `dossie.base.proventos_b3`):
  · classe do ticker avaliado = `proventos_ex.CLASSE` (PN, PNB, unit; o resto ON) — o dossiê ainda filtra ON fixo (fatia 2b);
  · lista FECHADA de tipos (`TIPOS`): dividendo, JCP e rendimento (atualização do dividendo pela Selic, PETR4) entram;
    restituição de capital em dinheiro fica fora (redução de capital, não lucro — doutrina §6.4; era o "Amortização" da VIVT3
    tirado à mão no lote 4). Tipo novo na B3 falha alto em vez de entrar ou sumir em silêncio;
  · só data-com ATÉ a data do preço (o que foi declarado depois não existia para o preço) e o cache baixado depois dela;
  · linhas iguais (mesma data-com e tipo, valor a ≤ 1%) são, quase sempre, PARCELAS e somam — conferido na DMPL da CVM
    (KLBN11 2025: 4 × R$ 0,228/unit = os R$ 1,112 bi de intercalares; PETR4, TIMS3, B3SA3, WEGE3, FLRY3, RECV3); a repetição
    de verdade (HYPE3 01/02/2024) sai. Cada grupo está classificado com a prova em `GRUPOS_CONFERIDOS`; grupo novo falha alto.
    A regra do AUD-23 (`sem_repeticao`, uma linha só) cortava provento real e segue só no dossiê/backtest (fatia 2b);
  · eventos em ações: suplemento da B3 (cache dados/proventos_hall/suplemento/) + os que a B3 omite e o FRE da CVM traz
    (`EVENTOS_FRE`, conferidos). Provento com data-com ATÉ a data-com do evento (inclusive: no mesmo dia, quem recebe o
    provento é a ação antiga) é dividido pelo multiplicador — R$ por ação de HOJE, a mesma base de `n_acoes`;
  · valor por ação = valueCash ÷ quotedPerShares (lote de 1.000 nos anos 2000).
Conferência das ações: `tests/test_fase3_proventos_b3.py` cruza a contagem de ações do DFP (CVM) ano a ano com os eventos —
salto sem evento nem emissão declarada falha (foi assim que a bonificação de 10% da Klabin em 2024 apareceu).
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
from collections import defaultdict
from datetime import date

import insumos_a
from proventos_ex import CLASSE, PASTA, data_do_preco, registros
from relatorio.modelo import Origem

SUPLEMENTO = PASTA / "suplemento"

# as não financeiras que passam pelos lotes (19 do caminho do lote + HYPE3 e LEVE3, que a tela mostra pelo dossiê)
NF_HALL = ("SUZB3", "KLBN11", "RANI3", "B3SA3", "SMTO3", "KEPL3", "SLCE3",            # lote 3
           "TIMS3", "VIVT3", "FLRY3", "HYPE3", "ABEV3", "WEGE3",                     # lote 4
           "PETR4", "PRIO3", "RECV3", "UGPA3", "VBBR3",                              # lote 5
           "GGBR4", "UNIP6", "LEVE3")                                                # lote 6

# corporateAction da B3 → o que é (None = fora do DPA). Lista fechada: tipo novo falha alto.
TIPOS = {"DIVIDENDO": "dividendo", "JRS CAP PROPRIO": "jcp", "RENDIMENTO": "rendimento", "REST CAP DIN": None}
JCP = "jcp"

# ISIN da classe no suplemento da B3: BR + raiz + fragmento (KLBN11 = BRKLBNCDAM18; GGBR4 = BRGGBRACNPR8)
ISIN_CLASSE = {"ON": "ACNOR", "PN": "ACNPR", "PNA": "ACNPA", "PNB": "ACNPB", "UNT": "CDAM"}

# Tipos de evento com semântica conferida contra a contagem de ações da CVM (fonte A). Nos dois primeiros o `fator_b3` é o %
# de ações novas sobre as antigas, e o multiplicador da quantidade é 1 + fator/100:
#   · BONIFICACAO — BLAU 30,0 em 2026 = 30 novas por 100, batendo 177,7 → 228,8 mi no DFP;
#   · DESDOBRAMENTO — BBAS 100,0 em 15/04/2024 (2 por 1): DFP 2023 → 2024, 2.865.417.020 → 5.730.834.040 ações integralizadas
#     (×2 exato). O fator NÃO é a razão (seria ×100): MGLU 300,0 em 2020 é o 4 por 1.
# GRUPAMENTO (08/10/2026, dossiê LEVE3): a B3 publica o fator como RAZÃO nova ÷ antiga (MGLU 2024: 0,1 = 10 para 1), não
# como percentual — multiplicador = fator, e fator >= 1 falha alto. Os demais tipos falham alto em vez de ajustar errado.
SEMANTICA_CONFERIDA = ("BONIFICACAO", "DESDOBRAMENTO", "GRUPAMENTO")
# par desdobramento + grupamento na mesma data, conferido contra a contagem de ações da CVM (multiplicador = produto):
#   LEVE 14/05/2012: 29.900% e 0,01 = ×3 (FRE: 42.769.500 → 128.308.500 ações);
#   TIMS 02/07/2025: 9.900% e 0,01 = ×1 (DFP 2024 → 2025: 0,987, só recompra);
#   VIVT 14/04/2025: 7.900% e 0,025 = ×2 (DFP 2024 → 2025: 1,965 = 2 × recompra de 1,8%).
PARES_CONFERIDOS = {("LEVE", "2012-05-14"), ("TIMS", "2025-07-02"), ("VIVT", "2025-04-14")}

# Eventos em ações que o suplemento da B3 NÃO traz (ele é incompleto: backtest/precos/eventos.py) e o FRE da CVM traz
# (tabela capital_social_desdobramento: ações antes e depois da aprovação, nota A). Data-com = último pregão antes do 1º dia
# com a marca de evento (E…B) no COTAHIST. Multiplicador = a proporção da bonificação/desdobramento; o FRE dá a razão das
# ações totais (a tesouraria não recebe: SLCE3 2023 = 1,0999), conferida a 0,1% por tests/test_fase3_proventos_b3.py.
_FRE = "CVM, FRE {ano} (capital_social_desdobramento: {antes} → depois, aprovação {aprov}); data-com pelo COTAHIST (marca {marca})"
EVENTOS_FRE = {
    "KEPL3": [dict(tipo="DESDOBRAMENTO", data_com="2022-05-05", aprovacao="2022-05-05", multiplicador=3.0,
                   fonte=_FRE.format(ano=2022, antes="razão 3,0", aprov="05/05/2022", marca="EB 06/05/2022"))],
    "SLCE3": [dict(tipo="DESDOBRAMENTO", data_com="2019-04-30", aprovacao="2019-04-30", multiplicador=2.0,
                   fonte=_FRE.format(ano=2019, antes="razão 2,0", aprov="30/04/2019", marca="EDB 02/05/2019")),
              dict(tipo="BONIFICACAO", data_com="2021-12-30", aprovacao="2021-12-30", multiplicador=1.1,
                   fonte=_FRE.format(ano=2022, antes="razão 1,1000", aprov="30/12/2021", marca="EB 03/01/2022")),
              dict(tipo="BONIFICACAO", data_com="2023-05-08", aprovacao="2023-04-27", multiplicador=1.1,
                   fonte=_FRE.format(ano=2023, antes="razão 1,0999", aprov="27/04/2023", marca="EDB 09/05/2023"))],
    "GGBR4": [dict(tipo="BONIFICACAO", data_com="2023-03-21", aprovacao="2023-02-28", multiplicador=1.05,
                   fonte=_FRE.format(ano=2023, antes="razão 1,0500", aprov="28/02/2023", marca="EDB 22/03/2023"))],
    "UNIP6": [dict(tipo="BONIFICACAO", data_com="2018-12-20", aprovacao="2018-12-20", multiplicador=12 / 11,
                   fonte=_FRE.format(ano=2019, antes="razão 1,0909 = 12/11", aprov="20/12/2018", marca="EB 21/12/2018")),
              dict(tipo="BONIFICACAO", data_com="2019-06-18", aprovacao="2019-06-18", multiplicador=7 / 6,
                   fonte=_FRE.format(ano=2019, antes="razão 1,1667 = 7/6", aprov="18/06/2019", marca="EB 19/06/2019")),
              dict(tipo="BONIFICACAO", data_com="2022-04-20", aprovacao="2022-04-20", multiplicador=1.1,
                   fonte=_FRE.format(ano=2022, antes="razão 1,1000", aprov="20/04/2022", marca="EDB 22/04/2022"))],
    # a tabela de desdobramento some do FRE de 2024: a razão sai do capital integralizado (5.617.892.756 no FRE 2022 →
    # 6.179.682.031 aprovado em 16/04/2024 no FRE 2023/2024 = 1,1000); a B3 também não publica este evento
    "KLBN11": [dict(tipo="BONIFICACAO", data_com="2024-05-06", aprovacao="2024-04-16", multiplicador=1.1,
                    fonte="CVM, FRE 2023/2024 (capital integralizado 5.617.892.756 → 6.179.682.031 ações, aprovação "
                          "16/04/2024); data-com pelo COTAHIST (marca EDB 07/05/2024)")],
}

# Linhas iguais (mesma data-com e tipo, valor a ≤ 1%) na API de proventos em dinheiro: a B3 lista UMA LINHA POR PARCELA, e
# a linha traz o valor da parcela — conferido contra o total declarado na DMPL da CVM (nota A) do ano da aprovação: a SOMA das
# linhas bate, a linha única não. A regra antiga (AUD-23, `sem_repeticao`: uma linha só) cortava provento real nesses casos.
# Repetição de verdade existe (HYPE3 01/02/2024: DMPL = uma linha). Sem dado de pagamento por linha na API (o cashDividends
# do suplemento só mostra o que ainda não foi pago), cada grupo é classificado aqui, com a prova; grupo novo falha alto.
_DMPL = "CVM, DMPL {ano} ({linha}) = R$ {total} — {conta}"
PARCELAS = "parcelas"
REPETICAO = "repeticao"
GRUPOS_CONFERIDOS = {
    ("KLBN11", "2025-12-15", "DIVIDENDO"): (PARCELAS, _DMPL.format(ano=2025, linha="5.06.09 dividendos intercalares",
                                            total="1.112 mi", conta="4 parcelas × R$ 0,228/unit (2026)")),
    ("B3SA3", "2025-12-30", "JRS CAP PROPRIO"): (PARCELAS, _DMPL.format(ano=2025, linha="5.04.07 JCP", total="3.024 mi",
                                                  conta="soma das linhas aprovadas em 2025 = R$ 2.993 mi; uma só = 1.868")),
    ("TIMS3", "2024-04-09", "DIVIDENDO"): (PARCELAS, _DMPL.format(ano="2024 (individual)", linha="5.04.06 dividendos",
                                           total="1.310 mi", conta="3 linhas × R$ 0,18 × 2.421 mi ações = R$ 1.310 mi")),
    ("TIMS3", "2025-04-03", "DIVIDENDO"): (PARCELAS, _DMPL.format(ano="2025 (individual)", linha="5.04.06 + 5.04.07",
                                           total="6.050 mi", conta="soma das linhas aprovadas em 2025 = R$ 6.003 mi")),
    ("FLRY3", "2025-12-02", "DIVIDENDO"): (PARCELAS, _DMPL.format(ano=2025, linha="5.04.06 + 5.04.07 + 5.04.09",
                                           total="913 mi", conta="soma das linhas aprovadas em 2025 = R$ 913 mi")),
    ("WEGE3", "2025-12-19", "DIVIDENDO"): (PARCELAS, _DMPL.format(ano=2025, linha="5.04.06 + 5.04.07 + 5.04.09 + 5.06.04",
                                           total="10.282 mi", conta="soma = R$ 10.282 mi; extraordinário R$ 1,2385 em 3 "
                                           "parcelas (PDF 03/10)")),
    ("PETR4", "2024-04-25", "DIVIDENDO"): (PARCELAS, _DMPL.format(ano=2024, linha="5.04.06 dividendos", total="100.900 mi",
                                           conta="soma das linhas aprovadas em 2024 = R$ 101.852 mi; uma só = 83.811")),
    ("PETR4", "2024-05-02", "DIVIDENDO"): (PARCELAS, _DMPL.format(ano=2024, linha="5.04.06 dividendos", total="100.900 mi",
                                           conta="extraordinário em 2 parcelas iguais; mesma conta da linha acima")),
    ("PETR4", "2025-04-16", "DIVIDENDO"): (PARCELAS, _DMPL.format(ano=2025, linha="5.04.06 dividendos", total="42.309 mi",
                                           conta="soma das linhas aprovadas em 2025 = R$ 42.177 mi; uma só = 37.605")),
    ("PETR4", "2026-04-22", "JRS CAP PROPRIO"): (PARCELAS, "padrão da PETR4 conferido na DMPL de 2024 e 2025 (2 parcelas "
                                                 "iguais); DMPL 2026 ainda não existe — fora da janela do DPA médio"),
    ("PETR4", "2026-06-01", "JRS CAP PROPRIO"): (PARCELAS, "idem PETR4 2026-04-22 (DMPL 2026 pendente; fora da janela)"),
    ("RECV3", "2026-01-08", "DIVIDENDO"): (PARCELAS, _DMPL.format(ano=2025, linha="5.04.06 + 5.04.07 + 5.06.04",
                                           total="564 mi", conta="soma das linhas aprovadas em 2025 = R$ 564 mi; uma só = 364")),
    ("VBBR3", "2024-04-18", "DIVIDENDO"): (PARCELAS, _DMPL.format(ano=2024, linha="5.04.06 + 5.04.07", total="2.007 mi",
                                           conta="soma das linhas aprovadas em 2024 = R$ 1.750 mi (mais perto que uma só, "
                                           "R$ 1.412 mi)")),
    ("HYPE3", "2024-02-01", "JRS CAP PROPRIO"): (REPETICAO, _DMPL.format(ano=2024, linha="5.04.07 JCP", total="661,9 mi",
                                                 conta="uma linha só: JCP aprovado em 2024 sem a repetida = R$ 662 mi; "
                                                 "somando = 723")),
}
TOL_REPETICAO = 0.01         # o mesmo corte do AUD-23 para dizer que duas linhas são "iguais"
# a série começa em 2016: é o que o motor lê (anos pagos de 2016–25; DPA médio de 2021–25) e o que a tela/PDF mostram (10 anos).
# Antes disso os grupos de linhas iguais não foram conferidos (PETR4 2004…) — não entram em vez de entrarem sem prova.
INICIO = "2016-01-01"

JANELA_DUPLICADO = 45        # dias: o mesmo evento nas duas fontes com data-com diferente (aprovação × data-com)

ORIGEM_B3 = Origem("B3 proventos", "A", "B3, proventos em dinheiro por data-com (API pública GetListedCashDividends, "
                   "cache dados/proventos_hall/) na classe do ticker, ajustados pelos eventos em ações (suplemento da B3 + "
                   "FRE da CVM) — proventos_hall.py")


# ---------------------------------------------------------------- eventos em ações
def eventos_em_acoes(tk: str, suplemento, isin_de=lambda tk: None) -> list[dict]:
    """Eventos em ações da B3 (GetListedSupplementCompany, fonte A) pela raiz do ticker, com o multiplicador da quantidade
    de ações (`SEMANTICA_CONFERIDA`); qualquer outro tipo falha alto. `suplemento` = DataFrame no formato de
    `backtest.precos.proventos_b3.carregar_suplemento`; `isin_de(tk)` = ISIN da classe do ticker (dossiê: COTAHIST; hall:
    `ISIN_CLASSE`), consultado só quando a raiz tem mais de um ISIN."""
    s = suplemento[suplemento["raiz"] == tk[:4]]
    isins = sorted({str(i) for i in s.get("isin", []) if str(i)})
    proprio = isin_de(tk) if len(isins) > 1 else None
    if proprio in isins:
        # a classe do próprio ticker decide (LEVE3: a ON tem o par de 2012; a PN, extinta, só os eventos de 1992)
        s = s[s["isin"] == proprio]
        chave = lambda x, f: (x["tipo"], x["data_com"], f)
    elif len(isins) > 1:
        # com o ISIN: cada classe tem o seu conjunto de eventos; conjuntos iguais = o mesmo evento repetido (conta uma vez);
        # conjuntos diferentes = fator diferente por classe, sem semântica conferida. Isso aceita dois eventos do MESMO tipo
        # na mesma data com fatores diferentes (LEVE3, 28/04/1992: bonificações de 20% e 1.080% em ON e PN)
        por_isin = {i: sorted((r["tipo"], str(r["data_com"])[:10], float(r["fator_b3"])) for _, r in s[s["isin"] == i].iterrows())
                    for i in isins}
        if len({tuple(v) for v in por_isin.values()}) > 1:
            raise NotImplementedError(f"{tk}: eventos diferentes por classe {sorted(por_isin)} — ajustar à mão")
        s = s[s["isin"] == isins[0]]
        chave = lambda x, f: (x["tipo"], x["data_com"], f)
    else:
        chave = lambda x, f: (x["tipo"], x["data_com"])
    out = {}
    for _, e in s.iterrows():
        if e["tipo"] not in SEMANTICA_CONFERIDA:
            raise NotImplementedError(f"{tk}: evento {e['tipo']} sem semântica conferida — ajustar à mão")
        f = float(e["fator_b3"])
        if not f > 0:
            raise ValueError(f"{tk}: {e['tipo']} de {e['data_com']} com fator {e['fator_b3']!r}")
        if e["tipo"] == "GRUPAMENTO" and not f < 1:
            raise ValueError(f"{tk}: GRUPAMENTO de {e['data_com']} com fator {f} >= 1 (a B3 publica a razão, ex. 0,1)")
        x = {"tipo": e["tipo"], "data_com": str(e["data_com"])[:10], "aprovacao": str(e["data_aprovacao"])[:10],
             "multiplicador": f if e["tipo"] == "GRUPAMENTO" else 1 + f / 100}
        # a B3 repete o evento por ISIN (ON, PN, UNIT): um só por (tipo, data-com), senão o multiplicador entra ao quadrado
        # (adversário, 07/10); fatores diferentes entre classes na mesma data não têm semântica conferida → falha alto
        k = chave(x, f)
        if k in out and out[k]["multiplicador"] != x["multiplicador"]:
            raise NotImplementedError(f"{tk}: {k} com fatores diferentes por classe — ajustar à mão")
        out[k] = x
    # desdobramento + grupamento na MESMA data-com: a B3 não publica o par de um jeito só (adversário, 08/10). Só passa o par
    # conferido contra a contagem de ações da CVM; o resto falha alto
    datas = {}
    for x in out.values():
        datas.setdefault(x["data_com"], set()).add(x["tipo"])
    for d, tipos in datas.items():
        if {"DESDOBRAMENTO", "GRUPAMENTO"} <= tipos and (tk[:4], d) not in PARES_CONFERIDOS:
            raise NotImplementedError(f"{tk}: desdobramento e grupamento na mesma data ({d}) sem conferência na CVM — ajustar à mão")
    return list(out.values())


def _arquivo_suplemento(tk: str) -> pathlib.Path:
    return SUPLEMENTO / f"{tk[:4]}.json"


def suplemento(tk: str, data_preco: str):
    """Suplemento da B3 da raiz do ticker no cache do hall, no formato de `carregar_suplemento`. Sem arquivo, ou baixado antes
    da data do preço → falha alto (um evento aprovado no intervalo sumiria)."""
    import pandas as pd
    from proventos_ex import _iso, _num
    f = _arquivo_suplemento(tk)
    if not f.exists():
        raise FileNotFoundError(f"{tk}: sem eventos em ações da B3 em {f} — rode `python proventos_hall.py --suplemento`")
    j = json.loads(f.read_text(encoding="utf-8"))
    if j["baixado_em"] < data_preco:
        raise ValueError(f"{tk}: suplemento da B3 baixado em {j['baixado_em']}, antes da data do preço {data_preco}")
    return pd.DataFrame([{"raiz": j["raiz"], "tipo": (r.get("label") or "").strip().upper(), "fator_b3": _num(r.get("factor")),
                          "data_com": _iso(r.get("lastDatePrior")), "data_aprovacao": _iso(r.get("approvedOn")),
                          "isin": r.get("isinCode") or ""} for r in j["stockDividends"]],
                        columns=["raiz", "tipo", "fator_b3", "data_com", "data_aprovacao", "isin"])


def eventos(tk: str, data_preco: str | None = None) -> list[dict]:
    """Eventos em ações do ticker com data-com até a data do preço: suplemento da B3 (classe do ticker) + `EVENTOS_FRE`. O
    mesmo evento nas duas fontes falha alto (o multiplicador entraria ao quadrado) — mesmo tipo a até `JANELA_DUPLICADO` dias,
    porque a B3 pode publicar a data-com um pregão depois (adversário, 20/10)."""
    data_preco = data_preco or data_do_preco()
    sup = suplemento(tk, data_preco)
    frag = ISIN_CLASSE[CLASSE.get(tk, "ON")]
    isin_de = lambda t: next((i for i in sup["isin"] if str(i).startswith(f"BR{t[:4]}{frag}")), None)
    ev = [dict(x, fonte="B3, suplemento (GetListedSupplementCompany)") for x in eventos_em_acoes(tk, sup, isin_de)]
    for x in EVENTOS_FRE.get(tk, []):
        perto = [y for y in ev if y["tipo"] == x["tipo"]
                 and abs((date.fromisoformat(y["data_com"]) - date.fromisoformat(x["data_com"])).days) <= JANELA_DUPLICADO]
        if perto:
            raise ValueError(f"{tk}: {x['tipo']} de {x['data_com']} já está no suplemento da B3 ({perto[0]['data_com']}) — "
                             "tirar de EVENTOS_FRE")
        ev.append(dict(x))
    return sorted((x for x in ev if x["data_com"] <= data_preco), key=lambda x: x["data_com"])


# ---------------------------------------------------------------- proventos em dinheiro
def grupos_iguais(linhas: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """{(data-com, tipo): linhas} dos grupos com 2+ linhas de valor a ≤ TOL_REPETICAO uma da outra (parcela ou repetição)."""
    por = defaultdict(list)
    for r in linhas:
        por[(r["data_com"], r["tipo"])].append(r)
    out = {}
    for k, rs in por.items():
        vs = sorted(r["valor"] / (r["lote"] or 1.0) for r in rs)
        if any(abs(b / a - 1) <= TOL_REPETICAO for a, b in zip(vs, vs[1:]) if a):
            out[k] = rs
    return out


def _sem_repetidas(rs: list[dict]) -> list[dict]:
    """Uma linha por valor (a ≤ TOL_REPETICAO da anterior, em ordem de valor) — a repetição conferida."""
    out = []
    for r in sorted(rs, key=lambda r: r["valor"] / (r["lote"] or 1.0)):
        v = r["valor"] / (r["lote"] or 1.0)
        if not out or abs(v / (out[-1]["valor"] / (out[-1]["lote"] or 1.0)) - 1) > TOL_REPETICAO:
            out.append(r)
    return out


def proventos(tk: str, data_preco: str | None = None, regs: list[dict] | None = None,
              ev: list[dict] | None = None, grupos: dict | None = None) -> list[dict]:
    """Os proventos em dinheiro que entram no DPA, um por linha: classe do ticker, tipo permitido, data-com até a data do preço,
    parcelas somadas e repetição conferida tirada (`GRUPOS_CONFERIDOS`), em R$ por ação de hoje (`valor_hoje`).
    `regs`/`ev`/`grupos` = registros, eventos e classificação prontos (testes). Grupo de linhas iguais sem classificação →
    falha alto (somar ou não muda o DPA em até 4×)."""
    data_preco = data_preco or data_do_preco()
    grupos = GRUPOS_CONFERIDOS if grupos is None else grupos
    regs = registros(tk, data_preco) if regs is None else regs
    ev = eventos(tk, data_preco) if ev is None else ev
    classe = CLASSE.get(tk, "ON")
    linhas = []
    for r in regs:
        if r["tipo_acao"] != classe or not r["data_com"] or not INICIO <= r["data_com"] <= data_preco:
            continue
        if r["tipo"] not in TIPOS:
            raise ValueError(f"{tk}: provento '{r['tipo']}' de {r['data_com']} fora da lista de tipos (proventos_hall.TIPOS) — "
                             "classificar à mão (entra no DPA ou é redução de capital?)")
        if TIPOS[r["tipo"]] is None:
            continue
        linhas.append(r)
    for (com, tipo), rs in grupos_iguais(linhas).items():
        cls = grupos.get((tk, com, tipo))
        if cls is None:
            raise ValueError(f"{tk}: {len(rs)} linhas iguais de {tipo} com data-com {com} na B3 — parcela ou repetição? "
                             "Conferir o total na DMPL da CVM e classificar em proventos_hall.GRUPOS_CONFERIDOS")
        if cls[0] == REPETICAO:
            fica = _sem_repetidas(rs)
            linhas = [r for r in linhas if not any(r is x for x in rs) or any(r is x for x in fica)]
    out = []
    for r in sorted(linhas, key=lambda r: (r["data_com"], r["tipo"], r["valor"])):
        v = r["valor"] / (r["lote"] or 1.0)
        fator = 1.0
        for x in ev:
            if r["data_com"] <= x["data_com"]:       # no mesmo dia, o provento é da ação antiga
                fator *= x["multiplicador"]
        out.append({"data_com": r["data_com"], "tipo": r["tipo"], "data_aprovacao": r["data_aprovacao"],
                    "valor": v, "fator": fator, "valor_hoje": v / fator})
    return out


def dpa_jcp(tk: str, data_preco: str | None = None, **kw) -> tuple[dict[str, float], dict[str, float]]:
    """DPA e JCP por ano da data-com, R$ por ação de hoje."""
    dpa, jcp = defaultdict(float), defaultdict(float)
    for p in proventos(tk, data_preco, **kw):
        dpa[p["data_com"][:4]] += p["valor_hoje"]
        if TIPOS[p["tipo"]] == JCP:
            jcp[p["data_com"][:4]] += p["valor_hoje"]
    return dict(sorted(dpa.items())), dict(sorted(jcp.items()))


def aplicar(si: dict, tks=NF_HALL, data_preco: str | None = None) -> None:
    """Troca, em `si` (o SI do motor), o DPA/JCP da StatusInvest pelo da B3 e registra o valor em `insumos_a`. Idempotente: a
    série da StatusInvest fica guardada uma vez em `dpa_statusinvest`/`jcp_statusinvest`."""
    data_preco = data_preco or data_do_preco()
    for tk in tks:
        s = si[tk]
        s.setdefault("dpa_statusinvest", dict(s["dpa_por_ano_datacom"]))
        s.setdefault("jcp_statusinvest", dict(s.get("jcp_por_ano_datacom") or {}))
        dpa, jcp = dpa_jcp(tk, data_preco)
        s["dpa_por_ano_datacom"] = insumos_a.registrar(tk, "dpa_por_ano_datacom", dpa, ORIGEM_B3)
        s["jcp_por_ano_datacom"] = insumos_a.registrar(tk, "jcp_por_ano_datacom", jcp, ORIGEM_B3)


def origem(tk: str, si: dict) -> Origem | None:
    """ORIGEM_B3 só se o DPA e o JCP que `si` carrega agora são os registrados da B3; senão None."""
    s = si.get(tk) or {}
    o1 = insumos_a.origem(tk, "dpa_por_ano_datacom", s.get("dpa_por_ano_datacom"))
    o2 = insumos_a.origem(tk, "jcp_por_ano_datacom", s.get("jcp_por_ano_datacom"))
    return o1 if (o1 is not None and o2 is not None) else None


def tabela_b3_si(si: dict, tks=NF_HALL, anos=range(2016, 2026)) -> list[tuple[str, str, float, float]]:
    """[(ticker, ano, DPA B3, DPA StatusInvest)] — a tabela do 09 (a série da StatusInvest é a do arquivo vigente)."""
    return [(tk, str(a), float(si[tk]["dpa_por_ano_datacom"].get(str(a), 0.0)),
             float(si[tk]["dpa_statusinvest"].get(str(a), 0.0))) for tk in tks for a in anos]


# ---------------------------------------------------------------- download
def baixar_suplemento(tks=NF_HALL) -> None:
    """Baixa (sempre de novo) o suplemento da B3 (eventos em ações) de cada raiz. Rodar a cada rodada, depois da data do preço."""
    sys.path.insert(0, str(pathlib.Path(__file__).parent))
    from backtest.precos.proventos_b3 import PAUSA, _get
    SUPLEMENTO.mkdir(parents=True, exist_ok=True)
    for raiz in sorted({tk[:4] for tk in tks}):
        j = _get("GetListedSupplementCompany", {"issuingCompany": raiz, "language": "pt-br"},
                 lambda j: isinstance(j, (list, dict)), vazios_aceitos=2)
        j = j[0] if isinstance(j, list) and j else (j if isinstance(j, dict) else {})
        if not j:
            raise ValueError(f"{raiz}: a B3 não devolveu o suplemento — conferir a raiz")
        ev = j.get("stockDividends") or []
        (SUPLEMENTO / f"{raiz}.json").write_text(json.dumps({"raiz": raiz, "baixado_em": date.today().isoformat(),
                                                             "stockDividends": ev}, ensure_ascii=False), encoding="utf-8")
        print(raiz, len(ev), "eventos em ações")
        time.sleep(PAUSA)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    if "--suplemento" in sys.argv:
        baixar_suplemento([a for a in sys.argv[1:] if not a.startswith("--")] or NF_HALL)
