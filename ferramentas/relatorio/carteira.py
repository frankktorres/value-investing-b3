"""Painel da carteira e da meta de renda: `python -m relatorio CARTEIRA` → RELATORIOS/privado/CARTEIRA-<pregão>.md e .pdf.

Mostra quanto a carteira rende por mês (dividendo + JCP dos últimos 12 meses pela data-com × quantidade de hoje), quanto
falta para a meta, e onde o preço de cada posição está na régua da doutrina (palavra vigente do motor; o P/C ao preço de
hoje é informativo, como no monitor — palavra nova só com veredito novo). Não sugere compra nem venda.
O calendário (`calendario.py`) mostra o mês em que cada provento cai e o que ainda está a receber.

Dado pessoal (quantidade, preço médio, meta, valores) só no `carteira.local.json` (fora do git, `.gitignore`) e no painel
gravado em `RELATORIOS/privado/` — `gravar` confere com `git check-ignore` e recusa destino versionável. No git ficam só
os tickers (`carteira_tickers.json`, DECISOES 13/10 e 19/10).
"""
from __future__ import annotations

import json
import math
import os
import subprocess
from datetime import date
from pathlib import Path

from relatorio import render_md, render_pdf
from relatorio.calendario import ESTIMADO, SEM_DATA, STATUSINVEST, anotar, meses
from relatorio.modelo import Numero, Origem, Relatorio, Secao
from relatorio.render_md import fmt
from relatorio.renda import JCP, RENDA, Renda12m, inicio_da_janela, provento_12m

FERR = Path(__file__).resolve().parents[1]
RAIZ = FERR.parent
LOCAL = FERR / "carteira.local.json"
EXEMPLO = FERR / "carteira.exemplo.json"
TICKERS = FERR / "carteira_tickers.json"
SAIDA = RAIZ / "RELATORIOS" / "privado"
HISTORICO = FERR / "dados" / "privado" / "renda.jsonl"
NAO_CONCLUSIVO = "NÃO CONCLUSIVO"

O_PRECO = Origem("COTAHIST", "A", "B3, cotações históricas: fechamento (PREULT) do último pregão")
O_PROV = Origem("B3 proventos", "A", "API da B3 GetListedCashDividends, data-com nos últimos 12 meses, ajustado por "
                                     "bonificação/desdobramento (GetListedSupplementCompany)")
O_LOCAL = Origem("carteira local", "B", "quantidade digitada pelo Frank a partir do extrato da corretora (arquivo fora do git)")
O_META = Origem("meta do Frank", "B", "meta de renda mensal decidida em 19/10/2026 (DECISOES.md); valor fora do git")
O_IR = Origem("LC 224/2025", "A", "IR retido no JCP, a mesma alíquota do motor (motor_financeiras.IR_JCP)")
O_PAG = Origem("StatusInvest pagamento", "C", "data de pagamento da StatusInvest casada pela data-com, ou estimada pela "
                                             "defasagem média medida nela (defasagem.py); a B3 não publica a data na API")


# ------------------------------------------------------------------------------ entrada
def ler_local(caminho: Path = LOCAL, tickers=None) -> dict:
    """{'meta_mensal': float, 'posicoes': {tk: {'quantidade', 'preco_medio' | None}}}. Falta ou erro → falha alto."""
    if not caminho.exists():
        raise FileNotFoundError(f"sem {caminho.name}: copie {EXEMPLO.name} para {caminho.name} (fica fora do git) e "
                                "preencha a quantidade de cada ticker")
    j = json.loads(caminho.read_text(encoding="utf-8"))
    meta = j.get("meta_mensal")
    if not isinstance(meta, (int, float)) or isinstance(meta, bool) or not meta > 0:
        raise ValueError(f"{caminho.name}: meta_mensal tem de ser um número > 0 (R$ por mês), veio {meta!r}")
    pos = j.get("posicoes")
    if not isinstance(pos, dict) or not pos:
        raise ValueError(f"{caminho.name}: 'posicoes' vazio — um item por ticker, com a quantidade")
    out = {}
    for tk, p in pos.items():
        q = (p or {}).get("quantidade")
        if not isinstance(q, (int, float)) or isinstance(q, bool) or not q > 0:
            raise ValueError(f"{caminho.name}: {tk} sem quantidade (> 0) — preencha com o número de ações do extrato")
        pm = p.get("preco_medio")
        if pm is not None and (not isinstance(pm, (int, float)) or isinstance(pm, bool) or not pm > 0):
            raise ValueError(f"{caminho.name}: {tk} com preco_medio inválido {pm!r} (número > 0 ou null)")
        out[tk] = {"quantidade": q, "preco_medio": float(pm) if pm is not None else None}
    if tickers is not None and set(out) != set(tickers):
        faltam, sobram = sorted(set(tickers) - set(out)), sorted(set(out) - set(tickers))
        raise ValueError(f"{caminho.name} e {TICKERS.name} com tickers diferentes — faltam {faltam}, sobram {sobram}")
    return {"meta_mensal": float(meta), "posicoes": out}


def situacao(preco: float, ref: dict | None) -> str:
    """Onde o preço está na régua da doutrina (texto neutro; não é ordem)."""
    if ref is None:
        return "sem palavra do motor"
    if ref["palavra"] == NAO_CONCLUSIVO:
        return "sem régua (NÃO CONCLUSIVO)"
    compra, saida = ref.get("compra", math.nan), ref.get("saida", math.nan)
    if not (math.isfinite(compra) and compra > 0 and math.isfinite(saida)):
        return "sem régua"
    if preco <= compra:
        return "no preço de compra ou abaixo"
    if preco >= saida:
        return "na saída ou acima"
    return "entre compra e saída"


# ------------------------------------------------------------------------------ painel (puro)
def _q(q) -> str:
    return f"{q:,.0f}".replace(",", ".") if float(q).is_integer() else fmt(float(q))


def montar(local: dict, precos: dict, pregao: str, refs: dict, rendas: dict, data_palavra: str,
           fora_do_hall=frozenset(), ir_jcp: float = 0.175) -> Relatorio:
    """`rendas[tk]` = Renda12m ou o texto do erro (a renda total sai marcada INCOMPLETA, nunca soma zero calado)."""
    pos = local["posicoes"]
    sem_preco = sorted(tk for tk in pos if not (precos.get(tk, 0) > 0))
    if sem_preco:
        raise ValueError(f"sem fechamento no COTAHIST até {pregao}: {sem_preco}")
    valor = {tk: pos[tk]["quantidade"] * precos[tk] for tk in pos}
    total = sum(valor.values())
    avisos, falhas = [], sorted(tk for tk in pos if not isinstance(rendas.get(tk), Renda12m))
    for tk in falhas:
        avisos.append(f"Renda INCOMPLETA: {tk} sem provento da B3 ({rendas.get(tk) or 'não calculado'}).")

    linhas_pos = []
    for tk in sorted(pos, key=lambda t: -valor[t]):
        ref, p = refs.get(tk), precos[tk]
        central = ref["central"] if ref else math.nan
        compra, saida = (ref["compra"], ref["saida"]) if ref and ref["palavra"] != NAO_CONCLUSIVO else (None, None)
        compra = compra if compra is not None and math.isfinite(compra) else None
        saida = saida if saida is not None and math.isfinite(saida) else None
        reg = situacao(p, ref) + (" · fora do hall" if tk in fora_do_hall else "")
        linhas_pos.append([tk, _q(pos[tk]["quantidade"]), fmt(p, "R$"), fmt(valor[tk], "R$"), fmt(valor[tk] / total, "%"),
                           ref["palavra"] if ref else "—", fmt(central, "R$") if central > 0 else "—",
                           fmt(p / central, "x") if central > 0 else "—",
                           fmt(compra, "R$") if compra is not None else "—",
                           fmt(saida, "R$") if saida is not None else "—", reg])
        if tk in fora_do_hall:
            avisos.append(f"{tk} está fora do hall (falha filtro de qualidade): a palavra do motor é só referência.")
        if ref and ref["palavra"] == NAO_CONCLUSIVO:
            avisos.append(f"{tk} NÃO CONCLUSIVO: sem preço de compra nem de saída pela régua.")
        if ref is None:
            avisos.append(f"{tk} sem palavra no motor do hall.")

    bruta = liquida = 0.0
    linhas_renda, caixa, ignorados = [], [], []
    for tk in sorted(pos, key=lambda t: -valor[t]):
        r, q, pm = rendas.get(tk), pos[tk]["quantidade"], pos[tk]["preco_medio"]
        if not isinstance(r, Renda12m):
            linhas_renda.append([tk, "—", "—", "—", "—", "—", "—"])
            continue
        b, liq = q * r.total, q * (r.total - r.jcp * ir_jcp)
        bruta, liquida = bruta + b, liquida + liq
        linhas_renda.append([tk, fmt(r.total), fmt(r.jcp), fmt(r.total / precos[tk], "%"), fmt(b, "R$"), fmt(liq, "R$"),
                             fmt(r.total / pm, "%") if pm else "—"])
        for e, na_conta in [(e, True) for e in r.eventos] + [(e, False) for e in r.futuros if e["tipo"] in RENDA]:
            v = e.get("ajustado", e["por_acao"])
            caixa.append({"tk": tk, "data_com": e["data_com"], "tipo": e["tipo"], "por_acao": v,
                          "liquido": q * v * ((1 - ir_jcp) if e["tipo"] == JCP else 1.0), "na_conta": na_conta,
                          "so_si": e.get("so_statusinvest", False),
                          "pagamento": e.get("pagamento", SEM_DATA), "origem": e.get("pag_origem", SEM_DATA)})
        ignorados += [f"{tk} {e['data_com']} {e['tipo']} R$ {fmt(e['por_acao'])}" for e in r.ignorados]
        ignorados += [f"{tk} {e['data_com']} {e['tipo']} R$ {fmt(e['por_acao'])} (anunciado)" for e in r.futuros
                      if e["tipo"] not in RENDA]
    sem_data = sorted({c["tk"] for c in caixa if c["na_conta"] and not c["pagamento"]})
    if sem_data:
        avisos.append(f"Sem data de pagamento (fora da StatusInvest e sem defasagem): {', '.join(sem_data)} — não dá para dizer "
                      "se o provento já caiu; ele aparece em \"sem data\" no calendário e fica fora de \"a receber\".")
    linhas_renda.append(["Total", "", "", fmt(bruta / total, "%"), fmt(bruta, "R$"), fmt(liquida, "R$"), ""])
    if ignorados:
        avisos.append("Fora da renda (não é dividendo/JCP/rendimento): " + "; ".join(ignorados) + ".")

    meta = local["meta_mensal"]
    mensal_liq, mensal_bruta = liquida / 12, bruta / 12
    dy_liq = liquida / total
    obs = f"INCOMPLETA: sem {', '.join(falhas)}" if falhas else ""
    fonte_renda = (O_LOCAL, O_PROV, O_IR)
    meta_sec = Secao("Meta de renda", numeros=[
        Numero("Meta (R$ por mês)", meta, "R$", (O_META,)),
        Numero("Renda líquida por mês (média de 12 meses)", mensal_liq, "R$", fonte_renda, obs=obs),
        Numero("Renda bruta por mês (antes do IR do JCP)", mensal_bruta, "R$", (O_LOCAL, O_PROV), obs=obs),
        Numero("Meta atingida", mensal_liq / meta, "%", (*fonte_renda, O_META), obs=obs),
        Numero("Falta por mês", max(0.0, meta - mensal_liq), "R$", (*fonte_renda, O_META), obs=obs),
        Numero("Patrimônio em ações B3 hoje", total, "R$", (O_LOCAL, O_PRECO)),
        Numero("DY líquido de 12 meses da carteira", dy_liq, "%", (*fonte_renda, O_PRECO), obs=obs),
        Numero("Patrimônio que a meta exige a esse DY", meta * 12 / dy_liq if dy_liq > 0 else None, "R$",
               (*fonte_renda, O_PRECO, O_META), obs=obs or "conta da meta, não indica onde investir"),
    ], texto=[f"Renda = provento por ação com data-com de {inicio_da_janela(pregao)} (exclusive) a {pregao} × quantidade "
              "de hoje. É o que a carteira de hoje teria recebido em 12 meses, não previsão. Líquida = JCP menos "
              f"{fmt(ir_jcp, '%')} de IR. Fora da B3 (exterior, cripto) não entra."])
    pos_sec = Secao("Posições na régua da doutrina", tabelas=[(
        "Posições (maior valor primeiro)",
        ["Ticker", "Qtd", "Preço", "Valor", "Peso", "Palavra", "Central", "P/C hoje", "Compra", "Saída", "Na régua"],
        linhas_pos)],
        texto=[f"Palavra, central, compra e saída: motor do hall com preço de {data_palavra}. O P/C usa o fechamento de "
               f"{pregao} e é informativo — palavra nova só com veredito novo. Nada aqui é ordem de compra ou venda."])
    renda_sec = Secao("Renda", tabelas=[(
        "Renda de 12 meses por ticker (R$ por ação de hoje)",
        ["Ticker", "Provento/ação", "dos quais JCP", "DY 12m", "Renda bruta/ano", "Renda líquida/ano", "Yield on cost"],
        linhas_renda)])
    return Relatorio(tk="CARTEIRA", nome="Painel da carteira e da meta", data=pregao,
                     origem=f"carteira local + motor do hall ({data_palavra})", palavra="—",
                     secoes=[meta_sec, pos_sec, renda_sec, calendario_secao(caixa, pregao, obs)], avisos=avisos)


_ORIGEM_PAG = {STATUSINVEST: "StatusInvest", ESTIMADO: "estimada", SEM_DATA: "sem data"}


def calendario_secao(caixa: list[dict], pregao: str, obs: str = "") -> Secao:
    """Mês em que cai cada provento líquido: os da renda de 12 meses (pela data-com) e os anunciados ainda não pagos."""
    conta = [c for c in caixa if c["na_conta"]]
    por_mes: dict[str, list[dict]] = {}
    for c in conta:
        por_mes.setdefault(c["pagamento"][:7] or SEM_DATA, []).append(c)
    datados = sorted(m for m in por_mes if m)
    linhas = []
    for m in (meses(datados[0], datados[-1]) if datados else []) + ([SEM_DATA] if SEM_DATA in por_mes else []):
        cs = por_mes.get(m, [])
        if not cs:
            linhas.append([m, "—", "", "sem pagamento", ""])
            continue
        a_receber = [c["pagamento"] > pregao for c in cs]
        sit = ("sem data" if m == SEM_DATA else "a receber" if all(a_receber) else
               "parte a receber" if any(a_receber) else "pago")
        linhas.append([m or "sem data", fmt(sum(c["liquido"] for c in cs), "R$"), ", ".join(sorted({c["tk"] for c in cs})),
                       sit, " + ".join(sorted({_ORIGEM_PAG[c["origem"]] for c in cs}))])
    pendentes = sorted((c for c in caixa if not c["na_conta"] or c["pagamento"] > pregao),
                       key=lambda c: (c["pagamento"] or "9999", c["tk"], c["data_com"]))
    tabs = [("Pagamento por mês (renda líquida de 12 meses)", ["Mês", "Líquido", "Tickers", "Situação", "Data de"], linhas)]
    if pendentes:
        tabs.append((f"A receber (pagamento depois de {pregao} ou data-com futura)",
                     ["Ticker", "Data-com", "Pagamento", "Data de", "Tipo", "R$/ação", "Líquido", "Na renda de 12m"],
                     [[c["tk"], c["data_com"], c["pagamento"] or "sem data", _ORIGEM_PAG[c["origem"]], c["tipo"],
                       fmt(c["por_acao"]), fmt(c["liquido"], "R$"),
                       "sim" if c["na_conta"] else "não (data-com futura" + ("; só StatusInvest, C)" if c["so_si"] else ")")]
                      for c in pendentes]))
    src, futuros = (O_LOCAL, O_PROV, O_IR), [c for c in caixa if not c["na_conta"]]
    return Secao("Calendário de pagamento", numeros=[
        Numero("A receber da renda de 12 meses (já passou a data-com)",
               sum((c["liquido"] for c in conta if c["pagamento"] > pregao), 0.0), "R$", (*src, O_PAG), obs=obs),
        Numero("Anunciado com data-com futura (fora da renda de 12 meses)", sum((c["liquido"] for c in futuros), 0.0), "R$",
               (*src, O_PAG) if any(c["so_si"] for c in futuros) else src),
    ], tabelas=tabs, texto=["Data de pagamento: StatusInvest (nota C), casada pela data-com; sem ela, estimada = data-com + "
                            "defasagem média do ticker (também C). A renda do painel continua contada pela data-com — o "
                            "calendário só mostra quando o dinheiro cai. Anunciado que a B3 ainda não lista e a StatusInvest "
                            "já mostra entra só na tabela de a receber, marcado C."])


def render(rel: Relatorio) -> str:
    cab = [f"# {rel.nome}", "", f"Preços de {rel.data} · {rel.origem}", "",
           "Documento PESSOAL (quantidades e valores): fica só em RELATORIOS/privado/, fora do git. Nota da fonte: A oficial, "
           "B primária com ressalva, C agregador, — sem fonte.", ""]
    return render_md.render(rel, cabecalho=cab)


# ------------------------------------------------------------------------------ dados reais e gravação
def _registros(tk: str, pregao: str, baixar: bool) -> list[dict]:
    import proventos_ex
    try:
        return proventos_ex.registros(tk, pregao)
    except (FileNotFoundError, ValueError):
        if not baixar:
            raise
    proventos_ex.baixar([tk])
    return proventos_ex.registros(tk, pregao)


def _statusinvest() -> dict:
    """Séries vigentes da StatusInvest (datas de pagamento); fora do disco → {} e o calendário sai "sem data"."""
    import series_vigente
    try:
        return series_vigente.carregar()
    except (FileNotFoundError, ValueError):
        return {}


def carregar(hoje: str | None = None, caminho: Path = LOCAL, baixar: bool = True) -> Relatorio:
    import defasagem
    import hall03
    import monitor_semanal
    import proventos_ex
    from backtest.precos.proventos_b3 import carregar_suplemento
    from dossie.base import eventos_em_acoes
    from motor_financeiras import IR_JCP

    local = ler_local(caminho, json.loads(TICKERS.read_text(encoding="utf-8"))["tickers"])
    tks = sorted(local["posicoes"])
    precos, pregao = monitor_semanal.ultimos_precos(tks, hoje or date.today().isoformat())
    todas = monitor_semanal.referencias_do_hall()
    refs = {tk: todas[tk] for tk in tks if tk in todas}
    sup = carregar_suplemento()
    sup = sup[sup["data_com"].astype(str).str[:10] > inicio_da_janela(pregao)]   # só evento da janela ajusta
    si = _statusinvest()
    rendas: dict = {}
    for tk in tks:
        try:
            rendas[tk] = provento_12m(_registros(tk, pregao, baixar), proventos_ex.CLASSE.get(tk, "ON"), pregao,
                                      eventos_em_acoes(tk, sup))
        except (KeyError, ValueError, FileNotFoundError, NotImplementedError) as ex:
            rendas[tk] = f"{type(ex).__name__}: {ex}"
            continue
        if tk in si:                                   # calendário: data de pagamento (C); sem StatusInvest → sem data
            anotar(rendas[tk], si[tk]["eventos"], defasagem.defasagem_meses(tk, si), pregao)
        else:
            anotar(rendas[tk], [], None)
    return montar(local, precos, pregao, refs, rendas, proventos_ex.data_do_preco(),
                  fora_do_hall=frozenset(hall03.FORA_DO_HALL) & set(tks), ir_jcp=IR_JCP)


def garantir_ignorado(caminho: Path) -> None:
    """O painel tem dado pessoal: só grava em caminho que o git ignora (fora do repo ou versionável → recusa)."""
    r = subprocess.run(["git", "check-ignore", "-q", "--", str(caminho)], cwd=RAIZ, capture_output=True)
    if r.returncode != 0:
        raise PermissionError(f"{caminho} não é ignorado pelo git — o painel tem dado pessoal e só grava em "
                              f"{SAIDA.relative_to(RAIZ)}/ (ver .gitignore)")


INTRO_PDF = ["**Documento pessoal** (quantidades e valores): fica só em RELATORIOS/privado/, fora do git. "
             "Mostra a renda, a meta e a posição do preço na régua da doutrina — não é ordem de compra nem de venda."]


def gravar(rel: Relatorio, pasta: Path = SAIDA) -> list[Path]:
    md, pdf = pasta / f"{rel.tk}-{rel.data}.md", pasta / f"{rel.tk}-{rel.data}.pdf"
    for p in (md, pdf):                                  # confere os dois antes de gravar qualquer um
        garantir_ignorado(p)
    pasta.mkdir(parents=True, exist_ok=True)
    md.write_text(render(rel), encoding="utf-8")
    render_pdf.render(rel, pdf, intro=[f"Preços de {rel.data} · {rel.origem}", *INTRO_PDF], rotulo=f"{rel.tk} {rel.data} · pessoal")
    return [md, pdf]


# ------------------------------------------------------------------------------ histórico rumo à meta
_CAMPOS = ("data", "meta_mensal", "renda_liquida_mensal", "renda_bruta_mensal", "pct_meta", "patrimonio", "incompleta")
BARRA = 20                                       # "#" por 100% da meta


def resumo(rel: Relatorio) -> dict:
    """A linha do histórico: os números do painel de hoje (tudo em R$ por mês, salvo `patrimonio`)."""
    def n(rotulo: str) -> Numero:
        return next(x for x in rel.numeros() if x.rotulo.startswith(rotulo))
    liq = n("Renda líquida por mês")
    return {"data": rel.data, "meta_mensal": n("Meta (R$").valor, "renda_liquida_mensal": liq.valor,
            "renda_bruta_mensal": n("Renda bruta por mês").valor, "pct_meta": n("Meta atingida").valor,
            "patrimonio": n("Patrimônio em ações").valor, "incompleta": bool(liq.obs.startswith("INCOMPLETA"))}


def ler_historico(caminho: Path = HISTORICO) -> list[dict]:
    """Linhas por data (uma por geração). Arquivo ausente → []; linha estragada falha alto (não perde renda calada)."""
    if not caminho.exists():
        return []
    out = []
    for i, linha in enumerate(caminho.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not linha.strip():
            continue
        r = None
        try:
            r = json.loads(linha)
            ok = (isinstance(r, dict) and all(c in r for c in _CAMPOS) and isinstance(r["data"], str)
                  and isinstance(r["incompleta"], bool)
                  and all(isinstance(r[c], (int, float)) and not isinstance(r[c], bool) and math.isfinite(r[c])
                          for c in _CAMPOS[1:6]))
        except ValueError:
            ok = False
        if not ok:
            raise ValueError(f"{caminho.name} linha {i} inválida — corrija ou apague a linha (o resto do histórico fica)")
        out.append(r)
    return sorted(out, key=lambda r: r["data"])


def com_linha(hist: list[dict], nova: dict) -> list[dict]:
    """Histórico com a linha de hoje: mesma data (pregão) substitui, data nova acrescenta."""
    return sorted([r for r in hist if r["data"] != nova["data"]] + [nova], key=lambda r: r["data"])


def escrever_historico(hist: list[dict], caminho: Path = HISTORICO) -> None:
    garantir_ignorado(caminho)                       # renda em R$ é dado pessoal
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_name(caminho.name + ".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in hist), encoding="utf-8", newline="\n")
    os.replace(tmp, caminho)


def evolucao_secao(hist: list[dict]) -> Secao:
    """Evolução rumo à meta: uma linha por pregão gerado. Linha INCOMPLETA (sem provento de algum ticker) não compara."""
    linhas, ant = [], None
    for r in hist:
        pct = r["pct_meta"]
        var = "—" if ant is None or r["incompleta"] or ant["incompleta"] else fmt(r["renda_liquida_mensal"] - ant["renda_liquida_mensal"], "R$")
        linhas.append([r["data"], fmt(r["renda_liquida_mensal"], "R$") + (" (incompleta)" if r["incompleta"] else ""),
                       fmt(r["meta_mensal"], "R$"), fmt(pct, "%"), var, "#" * min(BARRA, round(pct * BARRA))])
        ant = r
    return Secao("Evolução rumo à meta", tabelas=[(
        "Uma linha por geração do painel (pregão do preço)",
        ["Pregão", "Renda líquida/mês", "Meta/mês", "% da meta", "Variação", f"Meta ({BARRA} # = 100%)"], linhas)],
        texto=["A renda de cada linha é a de 12 meses pela data-com com a quantidade da época em que o painel foi gerado: "
               "muda com preço, proventos e aporte, e não é previsão. Fica em ferramentas/dados/privado/ (fora do git)."])


def painel(rel: Relatorio, pasta: Path = SAIDA, caminho_hist: Path = HISTORICO) -> list[Path]:
    """Acrescenta a evolução ao painel, grava MD+PDF e só então registra a linha do dia (falha ao gravar não suja o histórico)."""
    garantir_ignorado(caminho_hist)
    hist = com_linha(ler_historico(caminho_hist), resumo(rel))
    rel.secoes.append(evolucao_secao(hist))
    arquivos = gravar(rel, pasta)
    escrever_historico(hist, caminho_hist)
    return arquivos
