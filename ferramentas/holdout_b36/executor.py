"""Executor do hold-out B36 (pré-registro v3, emenda 8). Uso, de `ferramentas/`:

    python -m holdout_b36.executor cadastro            # cadastro.json a partir de selecao.json (só dado, sem leitura)
    python -m holdout_b36.executor coletar TK [TK...]  # CVM (DFP + último ITR até T), proventos e suplemento da B3, StatusInvest
    python -m holdout_b36.executor rodar TK [TK...]    # avalia e grava resultados/<TK>.json (erro vira resultado)

O método é o do hall/dossiê, sem mudança: não financeira pelo `dossie.gerar._calcular` (mesmo código do dossiê), banco e
regulado pelo `motor_financeiras` com os mesmos ajudantes do `lote2_energia`. O ticker entra nos registros globais
(`gerar.FICHAS`, `base.CNPJ/PREGAO`, `proventos_ex.PREGAO/CLASSE`, `coletar_cvm.EMPRESAS`) **só em memória e só durante a
avaliação** (`registrado`): a tela, o golden, `dossie/vereditos/` e `prospectivo/` não veem o hold-out. As séries da CVM vão
para `holdout_b36/dados/cvm_series_holdout.json`, nunca para o arquivo do hall nem para o dos dossiês.

Classe de cada insumo (emenda 8), decidida pelo código a partir de onde o valor veio: `automatico` (dado por código),
`pesquisa` (insumo com fonte A/B no JSON do protocolo) ou `vazio` (ausente; ficou no padrão do método).
"""
from __future__ import annotations

import contextlib
import importlib
import json
import pathlib
import statistics as st
import sys
import time
import traceback
import types
from datetime import date, datetime

AQUI = pathlib.Path(__file__).resolve().parent
SELECAO = AQUI / "selecao.json"
CADASTRO = AQUI / "cadastro.json"
SERIES = AQUI / "dados" / "cvm_series_holdout.json"
INSUMOS = AQUI / "insumos"
RESULTADOS = AQUI / "resultados"
T = "2026-11-19"
ANOS = [str(a) for a in range(2016, 2026)]          # ficha-padrão: os 10 últimos exercícios do DFP
G_REAL = 0.01                                       # ficha-padrão: o do hall e dos dossiês
RAZAO_JANELA = "ficha-padrão do hold-out B36 (emenda 8): os 10 últimos exercícios do DFP, sem escolha por ação"
CICLICOS = ("metalurgia", "siderurgia", "agricultura", "alimentos", "papel", "celulose", "petroleo", "mineracao",
            "extracao mineral", "quimic")
TIPOS = ("banco", "utility", "industrial")
FISHER_N = 15


# ------------------------------------------------------------------------------------------------- tipo e perfil (emenda 8)
def _norm(s: str) -> str:
    import unicodedata
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()


def tipo_do_setor(setor: str) -> str:
    s = _norm(setor)
    if s.strip() == "bancos" or s.endswith("- bancos"):
        return "banco"
    if "energia eletrica" in s or "saneamento" in s:
        return "utility"
    return "industrial"


def perfil_do_setor(setor: str) -> str:
    s = _norm(setor)
    return "ciclica" if any(k in s for k in CICLICOS) else "servicos"


def classe_do_especi(especi: str) -> str:
    e = (especi or "").split()[0].upper() if especi else "ON"
    return {"UNT": "UNT", "PNA": "PNA", "PNB": "PNB", "PN": "PN", "ON": "ON"}.get(e, e)


# ------------------------------------------------------------------------------------------------- cadastro (automático)
def montar_cadastro() -> list[dict]:
    """Uma linha por ação, só com dado (FCA, COTAHIST): CNPJ, código CVM, setor, tipo, perfil, NOMRES, classe, ações/unit."""
    import pandas as pd
    from backtest import cotahist
    from backtest.motor.perfil import acoes_por_papel
    sel = json.loads(SELECAO.read_text(encoding="utf-8"))
    p = pd.read_parquet(cotahist.parquet_de(int(T[:4])), columns=["data", "ticker", "codbdi", "nomres", "especi"])
    p = p[(p["codbdi"] == "02") & (p["data"] <= T)].sort_values("data")
    ult = p.groupby("ticker").last()
    out = []
    for s in sel["escolhidas"]:
        tk = s["ticker"]
        out.append(dict(ticker=tk, ordem=s["ordem"], cnpj=s["cnpj"], cd_cvm=s["cd_cvm"], setor=s["setor"],
                        tipo=tipo_do_setor(s["setor"]), perfil=perfil_do_setor(s["setor"]),
                        pregao=str(ult.loc[tk, "nomres"]).strip(), classe=classe_do_especi(str(ult.loc[tk, "especi"])),
                        acoes_por_unit=acoes_por_papel(tk, s["cnpj"], T)))     # None = unit sem composição legível na FCA (BPAC11)
    return out


def cadastro() -> dict[str, dict]:
    return {c["ticker"]: c for c in json.loads(CADASTRO.read_text(encoding="utf-8"))}


# ------------------------------------------------------------------------------------------------- registro em memória
@contextlib.contextmanager
def registrado(c: dict, ficha_modulo: str | None = None, insumos: dict | None = None, series: pathlib.Path = SERIES):
    """Põe o ticker nos registros globais só dentro do bloco e devolve tudo como estava ao sair."""
    import coletar_cvm
    import proventos_ex
    from dossie import base, gerar
    tk = c["ticker"]
    alvos = [(gerar.FICHAS, tk, ficha_modulo), (base.CNPJ, tk, c["cnpj"]), (base.PREGAO, tk, c["pregao"]),
             (proventos_ex.PREGAO, tk, c["pregao"]),
             (coletar_cvm.EMPRESAS, tk, (f"cvm:{int(c['cd_cvm']):06d}", int(c["acoes_por_unit"] or 1)))]   # só a coleta usa; banco não coleta CVM
    if c["classe"] != "ON":
        alvos.append((proventos_ex.CLASSE, tk, c["classe"]))
    antes = [(d, k, d.get(k, _AUSENTE)) for d, k, _ in alvos]
    serie_antes, ins_antes = base.SERIES, gerar.insumos
    try:
        for d, k, v in alvos:
            if v is not None:
                d[k] = v
        base.SERIES = series
        if insumos is not None:
            gerar.insumos = lambda t, _i=insumos: _i if t == tk else ins_antes(t)
        yield
    finally:
        for d, k, v in antes:
            if v is _AUSENTE:
                d.pop(k, None)
            else:
                d[k] = v
        base.SERIES, gerar.insumos = serie_antes, ins_antes


_AUSENTE = object()


# ------------------------------------------------------------------------------------------------- ficha-padrão (industrial)
def ficha_padrao(c: dict, dia_statusinvest: str) -> str:
    """Módulo de ficha em memória, igual para todas (emenda 8); devolve o nome para `gerar.FICHAS`."""
    from dossie import base
    from motor_financeiras import SEM_RAZAO
    from motor_nao_financeiras import Industrial
    tk = c["ticker"]
    nome = f"holdout_b36._fichas.{tk.lower()}"
    m = types.ModuleType(nome)
    m.TK, m.ANOS, m.RAZAO_JANELA = tk, list(ANOS), RAZAO_JANELA

    def empresa(qualitativo=None, desconto_controlador=None, **sobrepor):
        base.carregar(tk, dia_statusinvest=dia_statusinvest)
        kw = dict(anos_ciclo=list(ANOS), anos_outras=list(ANOS), janela_razao=RAZAO_JANELA, outras_liquidas=True,
                  g_real=G_REAL, jcp_share=base.jcp_share(tk), pl_hist=base.pl_hist(tk), defasagem_meses=base.defasagem(tk),
                  defasagem_fonte="datas de pagamento da StatusInvest (C, só datas), média ponderada pelo valor",
                  desconto_controlador=desconto_controlador or {"tipo": "zero", "razao": SEM_RAZAO},
                  qualitativo=qualitativo or {})
        kw.update(sobrepor)
        return Industrial(tk, tk, c["perfil"], preco=base.preco(tk), n_acoes=base.acoes_itr(tk, mes=c.get("mes_itr", 6)), **kw)

    m.empresa = empresa
    sys.modules[nome] = m
    return nome


# ------------------------------------------------------------------------------------------------- insumos e classes
CAMPOS_IND = ("ma_ruim", "interferencias", "partes_rel_sobre_receita", "tag_along", "discricionario")
AUTO_IND = ("séries DFP/ITR (CVM)", "preço (COTAHIST)", "ações (ITR)", "proventos (B3)", "defasagem (datas StatusInvest)",
            "FRE: acionistas", "FRE: remuneração", "FRE: partes relacionadas (bruto)", "nota moat (notas.py)",
            "nota ciclo (notas.py)", "nota gestão — base (notas.py)", "ficha: ANOS", "ficha: perfil", "ficha: outras_liquidas",
            "ficha: g_real")
CAMPOS_FIN = ("payout_politica", "prudencial", "qualitativo", "discricionario")
AUTO_FIN = ("preço (COTAHIST)", "VPA (StatusInvest)", "LPA (StatusInvest)", "ROE de 10 anos (StatusInvest)",
            "ROE atual (StatusInvest)", "DPA de 5 anos (StatusInvest)", "JCP (StatusInvest)", "P/L histórico (StatusInvest)",
            "anos pagos (StatusInvest)")


def ler_insumos(tk: str) -> dict:
    """Insumos do protocolo; a marca "SEM_RAZAO" do protocolo vira a constante do motor (`motor_financeiras.SEM_RAZAO`)."""
    from motor_financeiras import SEM_RAZAO
    f = INSUMOS / f"{tk}.json"
    ins = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    dc = ins.get("desconto_controlador")
    if dc and str(dc.get("razao", "")).strip() == "SEM_RAZAO":
        ins["desconto_controlador"] = dict(dc, razao=SEM_RAZAO)
    return ins


def _tem(ins: dict, k: str) -> bool:
    x = ins.get(k)
    return bool(x) and x.get("nota_fonte") in ("A", "B") and bool(x.get("fonte")) and "valor" in x


def classes(c: dict, ins: dict, extra: dict | None = None) -> list[tuple[str, str]]:
    """[(insumo, classe)] na lista fixa do tipo. `extra` traz o que só se sabe rodando (tag along do FRE, R$ 1 retido)."""
    extra = extra or {}
    dc = ins.get("desconto_controlador")
    from motor_financeiras import SEM_RAZAO
    dc_cls = "pesquisa" if dc and dc.get("razao") and str(dc["razao"]).strip() not in ("SEM_RAZAO", SEM_RAZAO) else "vazio"
    if c["tipo"] == "industrial":
        out = [(k, "automatico") for k in AUTO_IND]
        for k in CAMPOS_IND:
            if _tem(ins, k):
                out.append((k, "pesquisa"))
            elif k == "tag_along" and extra.get("tag_fre") is not None:
                out.append((k, "automatico"))
            else:
                out.append((k, "vazio"))
        out.append(("r1_retido (Q4 da triagem)", "automatico" if extra.get("r1_auto") else "vazio"))
        fis = (ins.get("fisher") or {}).get("respostas") or ["sem"] * FISHER_N
        out += [(f"fisher {i + 1}", "vazio" if r == "sem" else "pesquisa") for i, r in enumerate(fis)]
        out.append(("desconto_controlador", dc_cls))
        return out
    out = [(k, "automatico") for k in AUTO_FIN]
    out.append(("payout", "pesquisa" if _tem(ins, "payout_politica") else "automatico"))
    if c["tipo"] == "utility":
        out.append(("solidez (alavancagem CVM)", "automatico"))
    else:
        pr = (ins.get("prudencial") or {}).get("valor") or {} if _tem(ins, "prudencial") else {}
        out += [(f"prudencial {k}", "pesquisa" if pr.get(k) is not None else "vazio") for k in ("cet1", "inad90", "cobertura")]
    q = (ins.get("qualitativo") or {}).get("valor") or {} if _tem(ins, "qualitativo") else {}
    out += [(f"nota {k}", "pesquisa" if q.get(k) is not None else "vazio") for k in ("moat", "gestao", "controlador", "ciclo", "fisher")]
    out.append(("discricionario", "pesquisa" if _tem(ins, "discricionario") else "vazio"))
    out.append(("desconto_controlador", dc_cls))
    return out


def contagem(cl: list[tuple[str, str]]) -> dict:
    n = {k: sum(1 for _, x in cl if x == k) for k in ("automatico", "pesquisa", "vazio")}
    n["total"] = len(cl)
    n["pct_automatico"] = round(100 * n["automatico"] / n["total"], 1) if n["total"] else 0.0
    return n


# ------------------------------------------------------------------------------------------------- avaliação
def _dia_statusinvest(tk: str) -> str:
    raw = AQUI.parent / "dados" / "raw"
    dias = sorted(x.name for x in raw.iterdir() if x.is_dir() and (x / f"{tk}_indicadores.json").exists())
    if not dias:
        raise FileNotFoundError(f"{tk}: sem coleta da StatusInvest em dados/raw/ — rode `coletar`")
    return dias[-1]


def avaliar_industrial(c: dict, data: str, ins: dict, ficha_modulo: str | None = None, series: pathlib.Path = SERIES) -> dict:
    from dossie import base, evidencia as ev, gerar
    tk = c["ticker"]
    nome = ficha_modulo or ficha_padrao(c, _dia_statusinvest(tk))
    with registrado(c, nome, ins, series):
        cc = gerar.calcular(tk, data)
    r = cc["r"]
    extra = dict(tag_fre=cc["tag"], r1_auto=cc["fontes_ins"]["r1"] == "Q4 da última triagem" and cc["r1"] is not None)
    return dict(palavra=r["palavra"], palavra_regua=r.get("palavra_regua"), pc=r.get("pc"), central=r.get("central"),
                preco=cc["preco"], ke_nom=r.get("ke_nom_emp", cc["mk"].ke_nom), dispersao=r.get("dispersao"),
                confianca=r.get("confianca"), notas_regra11=cc["final"], desc_controlador=r.get("desc_controlador"),
                _extra=extra)


def _si_holdout(tk: str) -> dict:
    from montar_series import series
    return json.loads(json.dumps(series(tk, _dia_statusinvest(tk))))       # chaves de ano em texto, como no hall


def avaliar_financeira(c: dict, data: str, ins: dict) -> dict:
    import lote2_energia as L2
    from dossie import base
    from motor_financeiras import SEM_RAZAO, Financeira, avaliar
    tk = c["ticker"]
    si = _si_holdout(tk)
    cvm = json.loads(SERIES.read_text(encoding="utf-8"))[tk]
    antes = {n: (d.get(tk, _AUSENTE)) for n, d in (("SI", L2.SI), ("CVM", L2.CVM))}
    try:
        L2.SI[tk], L2.CVM[tk] = si, cvm
        with base.na_data(data):
            mk = base.mercado(data)
            preco = base.preco(tk, data)
        lpa = si["indicadores"]["lpa"]["anos"]
        dp = L2.dpas(tk)
        pays = [dp.get(str(a), 0) / lpa[str(a)] for a in range(2021, 2026) if lpa.get(str(a)) and lpa[str(a)] > 0]
        payout = ins["payout_politica"]["valor"] if _tem(ins, "payout_politica") else (st.median(pays) if pays else 0.0)
        dc = ins.get("desconto_controlador") or {"tipo": "zero", "razao": SEM_RAZAO}
        q = ins["qualitativo"]["valor"] if _tem(ins, "qualitativo") else {}
        disc = bool(ins["discricionario"]["valor"]) if _tem(ins, "discricionario") else False
        kw = dict(preco=preco, vpa=L2.ind(tk, "vpa"), lpa_12m=L2.ind(tk, "lpa"), roe_lp=L2.roe_lp(tk),
                  roe_inicio=L2.ind(tk, "roe") / 100, payout=payout, dpa_medio_5a=L2.dpa5(tk), jcp_share=L2.jcp(tk),
                  pl_hist=L2.pl_hist(tk), desconto_controlador=dc, anos_pagos_10=L2.anos_pagos(tk), qualitativo=q,
                  controlador_discricionario=disc,
                  controlador_discricionario_fonte=ins["discricionario"]["fonte"] if disc else "")
        if c["tipo"] == "utility":
            kw["solidez_manual"] = L2.solidez(tk)
        else:
            kw["prudencial"] = ins["prudencial"]["valor"] if _tem(ins, "prudencial") else {}
        r = avaliar(Financeira(tk, tk, c["tipo"], **kw), mk)
    finally:
        for n, d in (("SI", L2.SI), ("CVM", L2.CVM)):
            if antes[n] is _AUSENTE:
                d.pop(tk, None)
            else:
                d[tk] = antes[n]
    return dict(palavra=r["palavra"], palavra_regua=r.get("palavra_regua"), pc=r.get("pc"), central=r.get("central"),
                preco=preco, ke_nom=r.get("ke"), dispersao=r.get("dispersao"), confianca=r.get("confianca"),
                notas=r.get("notas"), desc_controlador=r.get("desc_controlador"), payout=payout, _extra={})


def rodar(tk: str, data: str = T, gravar: bool = True) -> dict:
    """Avalia um ticker do hold-out; erro vira resultado (tipo, mensagem, onde), nunca para o lote."""
    c = cadastro()[tk]
    ins = ler_insumos(tk)
    t0 = time.perf_counter()
    res = dict(ticker=tk, tipo=c["tipo"], perfil=c["perfil"], data=data, rodado_em=datetime.now().isoformat(timespec="seconds"))
    extra = {}
    try:
        out = avaliar_industrial(c, data, ins) if c["tipo"] == "industrial" else avaliar_financeira(c, data, ins)
        extra = out.pop("_extra")
        res.update(out, erro=None)
    except Exception as e:      # noqa: BLE001 — a B36 registra a falha (emenda 8), não a conserta
        tb = traceback.extract_tb(e.__traceback__)[-1]
        res.update(palavra=None, erro=dict(tipo=type(e).__name__, mensagem=str(e)[:500], onde=f"{pathlib.Path(tb.filename).name}:{tb.lineno}"))
    res["segundos_avaliacao"] = round(time.perf_counter() - t0, 1)
    cl = classes(c, ins, extra)
    res["insumos"] = [dict(insumo=k, classe=x) for k, x in cl]
    res["contagem"] = contagem(cl)
    res["meta_insumos"] = ins.get("_meta", {})
    if gravar:
        RESULTADOS.mkdir(parents=True, exist_ok=True)
        (RESULTADOS / f"{tk}.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return res


# ------------------------------------------------------------------------------------------------- coleta
def mes_itr(c: dict) -> int:
    """Último ITR de 2026 entregue até T para o CNPJ (point-in-time): 9 se o do 3T já estava na CVM, senão 6."""
    import io
    import zipfile
    import pandas as pd
    z = zipfile.ZipFile(AQUI.parent / "dados" / "cvm" / "itr_2026.zip")
    n = [x for x in z.namelist() if x.endswith("itr_cia_aberta_2026.csv")][0]
    d = pd.read_csv(io.BytesIO(z.read(n)), sep=";", encoding="latin-1", dtype=str)
    d = d[(d["CNPJ_CIA"] == c["cnpj"]) & (d["DT_RECEB"] <= T)]
    return 9 if (d["DT_REFER"].str[5:7] == "09").any() else 6


def coletar(tk: str) -> dict:
    import coletar_cvm
    import coletar_statusinvest
    import proventos_ex
    import proventos_hall
    todos = json.loads(CADASTRO.read_text(encoding="utf-8"))
    c = next(x for x in todos if x["ticker"] == tk)
    tempos = {}
    with registrado(c):
        t0 = time.perf_counter()
        c["mes_itr"] = mes_itr(c)
        SERIES.parent.mkdir(parents=True, exist_ok=True)
        if c["tipo"] != "banco":        # o banco roda pelos dados da StatusInvest (como o hall); o plano de contas é outro
            coletar_cvm.main([tk], arq=SERIES, ano_itr=2026, mes=c["mes_itr"])
        tempos["cvm"] = round(time.perf_counter() - t0, 1)
        t0 = time.perf_counter()
        proventos_ex.baixar([tk])
        proventos_hall.baixar_suplemento([tk])
        tempos["b3"] = round(time.perf_counter() - t0, 1)
        t0 = time.perf_counter()
        coletar_statusinvest.coletar(tk)
        tempos["statusinvest"] = round(time.perf_counter() - t0, 1)
    c["coleta"] = dict(em=date.today().isoformat(), segundos=tempos)
    CADASTRO.write_text(json.dumps(todos, ensure_ascii=False, indent=1), encoding="utf-8")
    return c


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    a = list(argv if argv is not None else sys.argv[1:])
    if not a:
        print(__doc__)
        return 2
    cmd, tks = a[0], [t.upper() for t in a[1:]]
    if cmd == "cadastro":
        cad = montar_cadastro()
        CADASTRO.write_text(json.dumps(cad, ensure_ascii=False, indent=1), encoding="utf-8")
        for x in cad:
            print(f"{x['ordem']:2} {x['ticker']:7} {x['tipo']:10} {x['perfil']:8} {x['classe']:4} unit={x['acoes_por_unit']} {x['pregao']}")
        return 0
    if cmd == "coletar":
        for tk in tks:
            try:
                c = coletar(tk)
                print("ok", tk, c["coleta"])
            except Exception as e:      # noqa: BLE001
                print("ERRO coleta", tk, type(e).__name__, str(e)[:300])
        return 0
    if cmd == "rodar":
        for tk in tks:
            r = rodar(tk)
            e = r["erro"]
            print(tk, r["palavra"], "P/C", r.get("pc") and round(r["pc"], 2), "Ke", r.get("ke_nom") and round(r["ke_nom"], 4),
                  r["contagem"], ("ERRO " + e["tipo"] + ": " + e["mensagem"][:200] + " @" + e["onde"]) if e else "")
        return 0
    print(f"comando desconhecido: {cmd}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
