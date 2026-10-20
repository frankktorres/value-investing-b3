"""Contrato da tela v0.2 (`docs/design/handoff-claude-code/handoff/HANDOFF.md` §7, adaptado aos campos reais):
`python -m painel.contrato` → web/dados/contrato/{hall.json, empresa/<TK>.json, monitor.json} e
web/dados/privado/carteira.json (o único com dado pessoal: peso, renda, meta).

Lê o que já foi calculado — não recalcula valuation nem troca palavra:
- `exportar` (web/dados/hall.json + empresas/<TK>.json): palavra vigente, régua, métodos, sensibilidade, notas, textos;
- COTAHIST: série de 12 meses (fechamento bruto, sem ajuste de provento) e o último pregão de cada ticker;
- `relatorio.carteira.carregar(baixar=False)`: meta, renda, posições e calendário (dado pessoal: só grava em pasta
  ignorada pelo git, conferida antes);
- `monitor/historico.csv`: quem entrou/saiu da compra e da saída entre as duas últimas rodadas.
Campo que o motor não entrega = None (a tela mostra "—" com nota "sem fonte"). A única classificação feita aqui é o tom
da grade de sensibilidade (valor do cenário contra o preço de hoje, nos mesmos fatores da régua — DECISOES 20/10/2026).
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

from painel.exportar import DADOS, _finito, _gravar_json, _sem_caminho

VERSAO = 2
DESTINO = DADOS / "contrato"
PRIVADO = DADOS / "privado"            # dado pessoal (peso, renda, meta): só a carteira grava aqui
NAO_CONCLUSIVO = "NÃO CONCLUSIVO"
ESCALA_REGUA = (0.50, 1.60)               # visual (HANDOFF §2.6): igual em todas as linhas, não é fator do motor
SEM_FONTE = "—"

# eixo do qualitativo ← título da seção do relatório
EIXOS = (("moat", "Vantagem competitiva (moat)"), ("gestao", "Gestão e alocação de capital"),
         ("divida", "Endividamento e solidez"), ("governanca", "Governança e controlador"),
         ("dividendos", "Dividendos e JCP"))


# ------------------------------------------------------------------------------ peças puras
def br_num(s) -> float | None:
    """'R$ 1.234,56' → 1234.56; '12,3%' → 0.123; '1,23×' → 1.23; '—'/'' → None. Número já pronto passa direto."""
    if isinstance(s, (int, float)) and not isinstance(s, bool):
        return _finito(s)
    if not isinstance(s, str):
        return None
    t = s.replace("R$", "").replace("×", "").replace("x", "").replace(" ", "").strip()
    pct = t.endswith("%")
    t = t.rstrip("%").strip().replace(".", "").replace(",", ".")
    if not re.fullmatch(r"[+-]?\d+(\.\d+)?", t):
        return None
    v = float(t)
    return v / 100 if pct else v


def palavra_codigo(p: str | None) -> str | None:
    """Palavra do motor → código do contrato. RADAR fica (o motor tem 5 palavras; decisão A de 20/10/2026)."""
    if not p:
        return None
    return "NAO_CONCLUSIVO" if p == NAO_CONCLUSIVO else p


def fatores() -> dict:
    """Fatores da régua lidos do motor (HANDOFF §2.6: não ficam fixos no front)."""
    import motor_financeiras as m
    return {"compra": m.COMPRA, "compra_parcial_qualidade": m.COMPRA_PARCIAL, "saida": m.SAIDA_PADRAO,
            "saida_qualidade": m.SAIDA_QUALIDADE, "escala_regua": list(ESCALA_REGUA)}


def _secao(bruto: dict, prefixo: str) -> dict | None:
    return next((s for s in bruto.get("secoes", []) if s["titulo"].startswith(prefixo)), None)


def _num(secao: dict | None, prefixo: str) -> dict | None:
    return next((n for n in secao["numeros"] if n["rotulo"].startswith(prefixo)), None) if secao else None


def valor_nota(n: dict | None) -> dict:
    """{valor, nota, fonte, obs} de um número do relatório; ausente → valor None e nota '—'."""
    if n is None:
        return {"valor": None, "nota": SEM_FONTE, "fonte": "sem fonte", "obs": ""}
    v = n["valor"]
    return {"valor": _finito(v) if not isinstance(v, str) else v, "nota": n["nota"], "fonte": n["fonte"],
            "obs": n.get("obs") or ""}


def _nome_descricao(rotulo: str) -> tuple[str, str]:
    nome, _, desc = rotulo.partition(" — ")
    return nome.strip(), desc.strip()


def metodos(bruto: dict) -> tuple[list[dict], list[dict]]:
    """(métodos em R$/ação, indicadores em % ou x) de 'Preço justo por método'. Baixo/alto: o motor não exporta → None."""
    s = _secao(bruto, "Preço justo por método")
    met, ind = [], []
    for n in (s["numeros"] if s else []):
        if n["rotulo"].startswith("Valor central"):
            continue
        nome, desc = _nome_descricao(n["rotulo"])
        item = {"nome": nome, "descricao": desc, "entra_no_central": n["papel"] == "central",
                "baixo": None, "base": _finito(n["valor"]), "alto": None, "unidade": n["unidade"],
                "nota": n["nota"], "fonte": n["fonte"], "obs": n.get("obs") or ""}
        (met if n["unidade"] == "R$" else ind).append(item)
    return met, ind


def classe_cenario(valor: float | None, preco: float | None, compra: float, saida: float) -> str | None:
    """Tom da célula: o central desse cenário contra o preço de hoje, com os fatores da régua do motor.
    bem_acima = preço já estaria na compra (≤ compra × valor); acima = valor > preço; abaixo = preço abaixo da saída;
    bem_abaixo = preço na saída ou acima. Sem preço ou sem valor → None."""
    if valor is None or preco is None or valor <= 0:
        return None
    if preco <= compra * valor:
        return "bem_acima"
    if valor > preco:
        return "acima"
    if preco < saida * valor:
        return "abaixo"
    return "bem_abaixo"


def sensibilidade(bruto: dict, preco: float | None, fat: dict, fator_saida: float | None) -> dict | None:
    """A grade pré-calculada do motor como está (3×3 Ke × margem/ROE de LP; decisão B de 20/10/2026)."""
    s = _secao(bruto, "Sensibilidade")
    if not s or not s["tabelas"]:
        return None
    t = s["tabelas"][0]
    cab, linhas = t["cabecalho"], t["linhas"]
    if len(cab) < 2 or not linhas or any(len(ln) != len(cab) for ln in linhas):
        return None                                        # grade irregular: a tela mostra "sem fonte", não chuta
    eixo_linha, _, eixo_coluna = cab[0].partition("\\")
    valores = [[br_num(c) for c in ln[1:]] for ln in linhas]
    saida = fator_saida or fat["saida"]
    base = next(([i, j] for i, ln in enumerate(linhas) for j, c in enumerate(cab[1:])
                 if ln[0].strip() == "+0 p.p." and c.strip() == "+0 p.p."), None)
    return {"titulo": t["titulo"], "eixo_linha": eixo_linha.strip(), "eixo_coluna": eixo_coluna.strip(),
            "linhas": [ln[0] for ln in linhas], "colunas": cab[1:], "valores": valores,
            "classe": [[classe_cenario(v, preco, fat["compra"], saida) for v in ln] for ln in valores],
            "base": base, "texto": list(s["texto"]), "avisos": list(s["avisos"])}


def premissas(bruto: dict) -> list[dict]:
    """Linhas da seção 'Premissas de julgamento' (o motor só dá texto: tipo vem do título; nota e efeito não existem)."""
    s = _secao(bruto, "Premissas de julgamento")
    out = []
    for x in (s["texto"] if s else []):
        nome, sep, valor = x.partition(": ")
        out.append({"nome": nome.strip() if sep else x.strip(), "valor": valor.strip().rstrip(".") if sep else None,
                    "tipo": "julgamento", "nota": None, "efeito": None})
    return out


def qualitativo(bruto: dict) -> list[dict]:
    """Um cartão por eixo: a nota que o motor dá (escala do próprio rótulo, ex. 0–5), os números e o texto da seção."""
    out = []
    for eixo, titulo in EIXOS:
        s = _secao(bruto, titulo)
        if s is None:
            out.append({"eixo": eixo, "titulo": titulo, "nota_eixo": None, "numeros": [], "texto": [], "avisos": []})
            continue
        nota_n = next((n for n in s["numeros"] if n["rotulo"].startswith("Nota de")), None)
        nota_eixo = None
        if nota_n is not None:
            m = re.search(r"\((\d+)\s*[–-]\s*(\d+)\)", nota_n["rotulo"])
            nota_eixo = {"rotulo": nota_n["rotulo"], "valor": _finito(nota_n["valor"]),
                         "escala": [int(m.group(1)), int(m.group(2))] if m else None,
                         "nota": nota_n["nota"], "fonte": nota_n["fonte"], "obs": nota_n.get("obs") or ""}
        out.append({"eixo": eixo, "titulo": s["titulo"], "nota_eixo": nota_eixo,
                    "numeros": [{"rotulo": n["rotulo"], **valor_nota(n), "unidade": n["unidade"]}
                                for n in s["numeros"] if n is not nota_n],
                    "texto": list(s["texto"]), "avisos": list(s["avisos"])})
    return out


def riscos(bruto: dict) -> dict:
    """Bandeiras do motor (probabilidade × impacto não existe no motor → None)."""
    s = _secao(bruto, "Riscos")
    itens = [{"nome": n["rotulo"], **valor_nota(n), "unidade": n["unidade"],
              "disparou": (n.get("obs") or "").startswith("DISPARA"), "probabilidade": None, "impacto": None}
             for n in (s["numeros"] if s else [])]
    return {"itens": itens, "texto": list(s["texto"]) if s else []}


def proventos(bruto: dict, serie_b3: tuple[dict, dict] | None = None, hoje: str | None = None) -> dict:
    """Histórico por exercício (tabela do dossiê, B3 nota A; senão a série B3 do hall) + números da seção Dividendos."""
    s = _secao(bruto, "Dividendos e JCP")
    historico, fonte_hist = None, None
    tab = next((t for t in (s["tabelas"] if s else []) if t["titulo"].startswith("Proventos por exercício")), None)
    if tab:
        historico = []
        for ln in tab["linhas"]:
            total, jcp = br_num(ln[1]), br_num(ln[2])
            historico.append({"ano": ln[0].split()[0], "parcial": "parcial" in ln[0], "total": total, "jcp": jcp,
                              "dividendos": None if total is None or jcp is None else round(total - jcp, 10)})
        fonte_hist = {"fonte": "B3 proventos", "nota": "A"}
    elif serie_b3:
        dpa, jcp = serie_b3
        hoje_ano = (hoje or date.today().isoformat())[:4]
        historico = [{"ano": a, "parcial": a == hoje_ano, "total": dpa[a], "jcp": jcp.get(a, 0.0),
                      "dividendos": round(dpa[a] - jcp.get(a, 0.0), 10)} for a in sorted(dpa)]
        fonte_hist = {"fonte": "B3 proventos", "nota": "A"}

    def pega(prefixo):
        n = _num(s, prefixo)
        return {**valor_nota(n), "rotulo": n["rotulo"]} if n else None

    return {"historico": historico, "fonte_historico": fonte_hist,
            "dpa_sustentavel": pega("DPA sustentável"), "payout": pega("Payout"),
            "yield_sust": pega("Dividend yield sustentável"),
            "exercicios_com_provento": pega("Exercícios") or pega("Exercícios completos"),
            "defasagem_meses": pega("Defasagem"), "yield_proj": None, "anos_seguidos": None,
            "avisos": list(s["avisos"]) if s else []}


def fontes(bruto: dict) -> list[dict]:
    """Cada origem distinta citada nos números, com a nota e quantos números a usam (data por fonte: o motor não dá)."""
    vistas: dict[tuple[str, str], int] = {}
    for s in bruto.get("secoes", []):
        for n in s["numeros"]:
            for o in n.get("origens", []):
                vistas[(o["fonte"], o["nota"])] = vistas.get((o["fonte"], o["nota"]), 0) + 1
    ordem = {"A": 0, "B": 1, "C": 2, SEM_FONTE: 3}
    return [{"nome": f, "nota": nt, "n_numeros": k, "data": None}
            for (f, nt), k in sorted(vistas.items(), key=lambda x: (ordem.get(x[0][1], 9), -x[1], x[0][0]))]


def linha_hall(bruta: dict, bruto_emp: dict | None, serie: list | None, ultimo: str | None, hoje: str,
               dias_velho: int, fat: dict) -> dict:
    """Linha do hall no contrato, a partir da linha do `exportar` (palavra vigente e régua já resolvidas)."""
    preco, saida = bruta["preco_hoje"], bruta["saida"]
    fator_saida = None if saida is None else fat["saida_qualidade"] if bruta["saida_exc"] else fat["saida"]
    dy = _num(_secao(bruto_emp or {}, "Dividendos e JCP"), "Dividend yield sustentável")
    rf = _num(_secao(bruto_emp or {}, "Riscos"), "Não vence a renda fixa")       # comparação sempre visível (20/10)
    dias = (date.fromisoformat(hoje) - date.fromisoformat(ultimo)).days if ultimo else None
    return {
        "ticker": bruta["tk"], "nome": bruta["nome"] or None, "setor": None, "origem": bruta["origem"],
        "dossie": bruta["dossie"], "data_palavra": bruta["data_palavra"],
        "palavra": palavra_codigo(bruta["palavra"]), "palavra_motor": palavra_codigo(bruta["palavra_motor"]),
        "regua_suspensa": bruta["situacao"] == "régua suspensa",
        "preco": preco, "preco_nota": "A" if preco is not None else SEM_FONTE,
        "compra": bruta["compra"], "central": bruta["central"], "central_nota": bruta["nota_central"],
        "central_fonte": bruta["fonte_central"], "saida": saida, "fator_saida": fator_saida,
        "metodos_central": bruta["n_central"], "metodos_total": bruta["n_central"] + bruta["n_informativo"],
        "pc": bruta["pc_hoje"], "situacao": bruta["situacao"] or None,
        "yield_sust": _finito(dy["valor"]) if dy else None, "yield_nota": dy["nota"] if dy else SEM_FONTE,
        # "Sim" | "Não" | "Empate", como o motor responde a "vence a renda fixa?" (Bogle líquido real ≥ rf líq. + 3 p.p.)
        "vence_rf": rf["valor"] if rf and isinstance(rf["valor"], str) else None,
        "vence_rf_nota": rf["nota"] if rf else SEM_FONTE,
        "vence_rf_criterio": "Bogle líquido real ≥ rf líquida + 3 p.p." if rf else None,
        "serie_12m": serie, "ultimo_pregao": ultimo, "dias_defasagem": dias,
        "velho": None if dias is None else dias > dias_velho,       # sem cotação: desconhecido, não "novo"
        "fora_do_hall": bruta["fora_do_hall"], "na_carteira": bruta["na_carteira"],
        "avisos": list(bruta["avisos"]), "erro": bruta["erro"]}


def empresa(linha: dict, bruto: dict, fat: dict, serie_b3=None, hoje: str | None = None) -> dict:
    met, ind = metodos(bruto)
    centrais = [m for m in met if m["entra_no_central"] and m["base"] is not None]
    return {
        "versao": VERSAO, "cabecalho": linha,
        "leitura": {"metodos_central": len(centrais), "metodos_r$": len(met),
                    "central_com_fonte_ab": sum(1 for m in centrais if m["nota"] in ("A", "B"))},
        "metodos": met, "indicadores": ind,
        "sensibilidade": sensibilidade(bruto, linha["preco"], fat, linha["fator_saida"]),
        "premissas": premissas(bruto), "qualitativo": qualitativo(bruto), "riscos": riscos(bruto),
        "proventos": proventos(bruto, serie_b3, hoje), "fontes": fontes(bruto),
        "avisos": list(bruto.get("avisos", [])), "data_relatorio": bruto.get("data")}


# ------------------------------------------------------------------------------ carteira
def _tabela(rel, titulo_secao: str, prefixo_tabela: str) -> tuple[list, list] | None:
    s = next((x for x in rel.secoes if x.titulo == titulo_secao), None)
    if s is None:
        return None
    t = next(((c, ls) for tt, c, ls in s.tabelas if tt.startswith(prefixo_tabela)), None)
    return t


def _kpi(rel, secao: str, prefixo: str) -> dict:
    s = next((x for x in rel.secoes if x.titulo == secao), None)
    n = next((x for x in s.numeros if x.rotulo.startswith(prefixo)), None) if s else None
    if n is None:
        return {"valor": None, "nota": SEM_FONTE, "obs": ""}
    return {"valor": _finito(n.valor), "nota": n.nota, "obs": n.obs}


def carteira(rel, linhas_hall: dict[str, dict], historico: list[dict]) -> dict:
    """Contrato da carteira a partir do relatório `relatorio.carteira` (tabelas formatadas → número; nada recalculado)."""
    pos = []
    t_pos, t_renda = _tabela(rel, "Posições na régua da doutrina", "Posições"), _tabela(rel, "Renda", "Renda")
    renda = {ln[0]: ln for ln in (t_renda[1] if t_renda else []) if ln[0] != "Total"}
    for ln in (t_pos[1] if t_pos else []):
        tk = ln[0]
        h = linhas_hall.get(tk, {})
        r = renda.get(tk)
        pos.append({"ticker": tk, "peso": br_num(ln[4]), "palavra": h.get("palavra"), "preco": h.get("preco"),
                    "compra": h.get("compra"), "central": h.get("central"), "saida": h.get("saida"),
                    "fator_saida": h.get("fator_saida"), "pc": h.get("pc"), "na_regua": ln[10],
                    "dy_12m": br_num(r[3]) if r else None,
                    "renda_bruta_ano": br_num(r[4]) if r else None, "renda_liquida_ano": br_num(r[5]) if r else None})
    cal = _tabela(rel, "Calendário de pagamento", "Pagamento por mês")
    calendario = [{"mes": ln[0], "liquido": br_num(ln[1]), "dividendos": None, "jcp": None,
                   "tickers": [x for x in ln[2].split(", ") if x], "situacao": ln[3], "data_de": ln[4] or None}
                  for ln in (cal[1] if cal else [])]
    rec = _tabela(rel, "Calendário de pagamento", "A receber")
    pagamentos = [{"ticker": ln[0], "data_com": ln[1], "data": None if ln[2] == "sem data" else ln[2],
                   "data_de": ln[3], "tipo": ln[4], "por_acao_txt": ln[5], "valor": br_num(ln[6]),
                   "na_renda_12m": ln[7] == "sim",
                   "status": {"estimada": "estimado", "sem data": None}.get(ln[3], "declarado"),  # da data
                   "so_statusinvest": "só StatusInvest" in ln[7], "nota": "C", "obs": ln[7]}
                  for ln in (rec[1] if rec else [])]
    renda_liq = _kpi(rel, "Meta de renda", "Renda líquida")
    return {
        "versao": VERSAO, "vazia": False, "erro": None, "pregao": rel.data, "origem": rel.origem,
        "renda_mensal_estimada": renda_liq, "renda_mensal_bruta": _kpi(rel, "Meta de renda", "Renda bruta"),
        "meta": _kpi(rel, "Meta de renda", "Meta (R$"), "pct_meta": _kpi(rel, "Meta de renda", "Meta atingida"),
        "falta": _kpi(rel, "Meta de renda", "Falta"), "patrimonio": _kpi(rel, "Meta de renda", "Patrimônio em"),
        "dy_liquido_12m": _kpi(rel, "Meta de renda", "DY líquido"), "n_papeis": len(pos),
        "incompleta": renda_liq["obs"].startswith("INCOMPLETA"),
        "renda_12m": [{"data": h["data"], "renda_liquida_mensal": h["renda_liquida_mensal"],
                       "pct_meta": h["pct_meta"], "meta": h["meta_mensal"], "incompleta": h["incompleta"]}
                      for h in historico],
        "posicoes": pos, "calendario": calendario, "pagamentos": pagamentos, "setores": None,
        "textos": [x for s in rel.secoes for x in s.texto], "avisos": list(rel.avisos)}


def carteira_vazia(erro: str) -> dict:
    return {"versao": VERSAO, "vazia": True, "erro": erro, "posicoes": [], "calendario": [], "pagamentos": [],
            "renda_12m": [], "setores": None}


# ------------------------------------------------------------------------------ monitor
COMPRA_A, SAIDA_A = "≤ COMPRA", "≥ SAÍDA"


def monitor(linhas: list[dict]) -> dict:
    """Diferença entre as duas últimas rodadas de `monitor/historico.csv` (última linha de cada ticker por rodada)."""
    por_rodada: dict[str, dict[str, dict]] = {}
    for r in linhas:
        por_rodada.setdefault(r["rodada"], {})[r["ticker"]] = r
    rodadas = sorted(por_rodada)
    if not rodadas:
        return {"versao": VERSAO, "rodada": None, "rodada_anterior": None, "entraram_compra": [], "sairam_compra": [],
                "entraram_saida": [], "sairam_saida": [], "sem_mudanca": 0, "novos": [], "removidos": [],
                "tickers": 0, "aviso": None}
    atual = por_rodada[rodadas[-1]]
    ant = por_rodada[rodadas[-2]] if len(rodadas) > 1 else {}

    def item(tk):
        a, b = ant.get(tk, {}), atual.get(tk, {})
        return {"ticker": tk, "alerta_anterior": a.get("alerta") or None, "alerta_atual": b.get("alerta") or None,
                "preco_anterior": _f(a.get("preco")), "preco_atual": _f(b.get("preco")),
                "central_anterior": _f(a.get("central")), "central_atual": _f(b.get("central")),
                "pc_anterior": _f(a.get("pc")), "pc_atual": _f(b.get("pc")),
                "novo": tk not in ant, "removido": tk not in atual}

    listas = {"entraram_compra": [], "sairam_compra": [], "entraram_saida": [], "sairam_saida": []}
    sem = 0
    for tk in (sorted(set(atual) | set(ant)) if ant else []):     # 1ª rodada: nada "entrou"
        a, b = ant.get(tk, {}).get("alerta"), atual.get(tk, {}).get("alerta")
        mudou = False
        for alvo, ent, sai in ((COMPRA_A, "entraram_compra", "sairam_compra"), (SAIDA_A, "entraram_saida", "sairam_saida")):
            if b == alvo and a != alvo:
                listas[ent].append(item(tk)); mudou = True
            elif a == alvo and b != alvo:
                listas[sai].append(item(tk)); mudou = True
        sem += not mudou
    return {"versao": VERSAO, "rodada": rodadas[-1], "pregao": next(iter(atual.values()))["pregao"],
            "rodada_anterior": rodadas[-2] if len(rodadas) > 1 else None, **listas, "sem_mudanca": sem,
            "novos": sorted(set(atual) - set(ant)) if ant else [], "removidos": sorted(set(ant) - set(atual)),
            "tickers": len(atual), "aviso": None}


def _f(x):
    try:
        return _finito(float(x)) if x not in (None, "") else None
    except ValueError:
        return None


# ------------------------------------------------------------------------------ dados reais
def series_12m(tks, hoje: str) -> tuple[dict[str, list], dict[str, str]]:
    """({tk: [[data, fechamento], ...] semanal}, {tk: último pregão}) do COTAHIST, 12 meses até `hoje`."""
    import pandas as pd
    from backtest import cotahist
    ano = int(hoje[:4])
    partes = [pd.read_parquet(cotahist.parquet_de(a), columns=["data", "ticker", "preult"])
              for a in (ano - 1, ano) if cotahist.parquet_de(a).exists()]
    if not partes:
        return {}, {}
    d = pd.concat(partes, ignore_index=True)
    inicio = (date.fromisoformat(hoje) - timedelta(days=365)).isoformat()
    d = d[d["ticker"].isin(list(tks)) & (d["data"] <= hoje) & (d["data"] > inicio) & (d["preult"] > 0)]
    d = d.assign(dt=pd.to_datetime(d["data"])).sort_values("dt")
    series, ultimo = {}, {}
    for tk, g in d.groupby("ticker"):
        sem = g.set_index("dt")["preult"].resample("W-FRI").last().dropna()
        series[tk] = [[ix.date().isoformat(), round(float(v), 4)] for ix, v in sem.items()]
        ultimo[tk] = str(g["data"].iloc[-1])
    return series, ultimo


def _serie_b3(tk: str):
    import proventos_hall
    if tk not in proventos_hall.NF_HALL:
        return None
    try:
        return proventos_hall.dpa_jcp(tk)
    except Exception:                                     # noqa: BLE001 — sem série: a tela mostra "sem fonte"
        return None


def gerar(origem: Path = DADOS, destino: Path = DESTINO, privado: Path = PRIVADO, hoje: str | None = None,
          log=print) -> dict:
    import monitor_semanal
    from relatorio import carteira as mod_carteira
    from relatorio.carteira import garantir_ignorado

    hoje = hoje or date.today().isoformat()
    for p in (destino / "hall.json", destino / "empresa" / "X.json", privado / "carteira.json"):
        garantir_ignorado(p)                               # carteira.json tem dado pessoal: só em pasta ignorada
    hall_bruto = json.loads((origem / "hall.json").read_text(encoding="utf-8"))
    brutos = {}
    for x in hall_bruto["empresas"]:
        p = origem / "empresas" / f"{x['tk']}.json"
        brutos[x["tk"]] = json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
    tks = [x["tk"] for x in hall_bruto["empresas"]]
    avisos = list(hall_bruto["avisos"])
    try:
        series, ultimo = series_12m(tks, hoje)
        if not series:
            avisos.append("Sem série de 12 meses nem último pregão: COTAHIST ausente ou sem os tickers.")
    except (FileNotFoundError, OSError, ValueError) as ex:
        series, ultimo = {}, {}
        avisos.append(_sem_caminho(f"Sem série de 12 meses ({type(ex).__name__}: {ex})."))
    fat = fatores()
    dias_velho = monitor_semanal.DIAS_VELHO
    linhas = {x["tk"]: linha_hall(x, brutos[x["tk"]], series.get(x["tk"]), ultimo.get(x["tk"]), hoje, dias_velho, fat)
              for x in hall_bruto["empresas"]}
    for tk in tks:
        if brutos[tk] is not None:
            _gravar_json(destino / "empresa" / f"{tk}.json", empresa(linhas[tk], brutos[tk], fat, _serie_b3(tk), hoje))
    hall = {"versao": VERSAO, "gerado_em": datetime.now().isoformat(timespec="seconds"), "hoje": hoje,
            "exportado_em": hall_bruto["gerado_em"], "cotacao_em": hall_bruto["pregao_hoje"],
            "demonstracoes_ref": None, "dias_velho": dias_velho, "fatores": fat, "avisos": avisos,
            "legenda": {"yield_sust": "dividend yield sustentável do motor (valor presente, preço de referência do "
                                      "veredito), não projeção",
                        "serie_12m": "fechamento semanal do COTAHIST, sem ajuste de provento",
                        "pc": "preço de hoje ÷ central (informativo; a palavra só muda com veredito novo)",
                        "carteira": "peso e renda por ticker ficam só em privado/carteira.json (a tela junta pelo "
                                    "ticker)"},
            "empresas": list(linhas.values())}
    _gravar_json(destino / "hall.json", hall)

    # dado pessoal: só aqui, só em privado/ (ignorado e conferido acima)
    try:
        cart = carteira(mod_carteira.carregar(hoje, baixar=False), linhas, mod_carteira.ler_historico())
    except Exception as ex:                                # noqa: BLE001 — carteira quebrada não derruba hall/monitor
        cart = carteira_vazia(_sem_caminho(f"{type(ex).__name__}: {ex}"))
    _gravar_json(privado / "carteira.json", cart)

    try:
        with open(monitor_semanal.HISTORICO, encoding="utf-8", newline="") as f:
            mon = monitor(list(csv.DictReader(f)))
    except (OSError, KeyError, csv.Error) as ex:
        mon = {**monitor([]), "aviso": _sem_caminho(f"Não foi possível ler monitor/historico.csv ({type(ex).__name__}: {ex}).")}
    _gravar_json(destino / "monitor.json", mon)
    log(f"contrato: {len(linhas)} empresas · carteira {'vazia' if cart['vazia'] else 'ok'} · monitor {mon['rodada']}")
    return {"hall": hall, "carteira": cart, "monitor": mon}


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="grava o contrato da tela a partir do que `painel.exportar` já gravou")
    ap.add_argument("--hoje", help="data AAAA-MM-DD (padrão: hoje)")
    a = ap.parse_args(argv)
    if not (DADOS / "hall.json").exists():
        print("Sem web/dados/hall.json: rode `python -m painel.exportar` antes.", file=sys.stderr)
        return 1
    gerar(hoje=a.hoje)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
