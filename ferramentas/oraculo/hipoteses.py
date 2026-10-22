"""H1–H11 do PRE-REGISTRO-v3 rodadas só como RELATÓRIO (Fase 2): nada aqui muda palavra, central, golden ou doutrina.

    cd ferramentas && python -m oraculo.hipoteses     # grava docs/oraculo/hipoteses-AAAA-MM-DD.md e .json
Cada função devolve o resultado contra o critério escrito ANTES (pré-registro §2). As variantes de regra (trava de g, ponto de
partida do ponto fixo, referências da H9) rodam sobre cópias em memória das funções do motor, ativadas só dentro de um `with`
(mock.patch); o arquivo do motor não é tocado. Fonte que o `verificador-fonte` não leu no documento primário fica "a conferir".
"""
from __future__ import annotations

import contextlib
import copy
import datetime as dt
import inspect
import itertools
import json
import math
import pathlib
import statistics
import sys
from dataclasses import replace
from functools import cache
from unittest import mock

AQUI = pathlib.Path(__file__).resolve().parent
FERRAMENTAS = AQUI.parent
RAIZ = FERRAMENTAS.parent
SAIDA = RAIZ / "docs" / "oraculo"
if str(FERRAMENTAS) not in sys.path:
    sys.path.insert(0, str(FERRAMENTAS))

import mercado  # noqa: E402
import motor_financeiras as F  # noqa: E402
import motor_nao_financeiras as M  # noqa: E402
from oraculo import reconciliacao as R  # noqa: E402
from oraculo import sanidade as S  # noqa: E402

MK = mercado.vigente()
# Damodaran, ctryprem.html (atualização de 05/01/2026; nota A, lida pelo verificador-fonte em 22/10/2026), linha Brazil
DAMODARAN = dict(spread=0.0213, crp=0.0324, erp_maduro=0.0423, rating="Ba1", data="05/01/2026",
                 url="https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/ctryprem.html")
MERCADO_15_10 = FERRAMENTAS / "dados" / "mercado_2026-10-15.json"
BANCOS_CVM = {"ITUB4": "ITAU UNIBANCO HOLDING", "BBDC4": "BCO BRADESCO S", "BBAS3": "BCO BRASIL S", "ABCB4": "ABC BRASIL",
              "BRSR6": "ESTADO DO RIO GRANDE DO SUL", "BRBI11": "BRBI BR PARTNERS", "BBSE3": "BB SEGURIDADE",
              "CXSE3": "CAIXA SEGURIDADE", "PSSA3": "PORTO SEGURO", "SANB11": "BCO SANTANDER \\(BRASIL\\)"}


# ---------------------------------------------------------------- base comum
@cache
def empresas():
    return S.empresas()


def ind():
    return sorted(t for t, e in empresas().items() if isinstance(e, M.Industrial))


def fin():
    return sorted(t for t, e in empresas().items() if isinstance(e, F.Financeira))


@contextlib.contextmanager
def rapido():
    with mock.patch.object(M, "ke_implicito", lambda *a, **k: None), mock.patch.object(M, "g_implicito", lambda *a, **k: None):
        yield


def avaliar(tk, emp=None, mk=MK):
    emp = emp or empresas()[tk]
    if isinstance(emp, F.Financeira):
        return F.avaliar(emp, mk)
    with rapido():
        return M.avaliar(emp, mk)


@cache
def base(tk):
    return avaliar(tk)


def _variante(func, trocas: dict[str, str]):
    """Cópia em memória de uma função do motor com trechos trocados; globals = o próprio módulo (ativar com mock.patch)."""
    src = inspect.getsource(func)
    for velho, novo in trocas.items():
        assert src.count(velho) == 1, f"{func.__name__}: trecho não achado ou repetido: {velho[:60]}"
        src = src.replace(velho, novo)
    loc = {}
    exec(compile(src, f"<variante {func.__name__}>", "exec"), M.__dict__, loc)
    return loc[func.__name__]


TRAVA_CASA = "cria = roic_c is not None and min(roic_c, roic_rep_c if roic_rep_c is not None else roic_c) > w_nom"
VALORES_V = _variante(M.valores, {TRAVA_CASA: "cria = _CRIA(roic_c, roic_rep_c, w_nom, w_real)"})
ESTRUTURA_V = _variante(M.estrutura_de_capital, {"e0 = pl if pl > 0 else max(d, 1.0)": "e0 = _E0(emp, pl, d)"})
CRIA = {
    "casa": lambda rc, rr, wn, wr: rc is not None and min(rc, rr if rr is not None else rc) > wn,
    # H1, "mesma base": ROIC contábil (nominal) × WACC nominal E ROIC a reposição (≈ real) × WACC real — o "nunca misture" do 01 l.55
    "real": lambda rc, rr, wn, wr: rc is not None and rc > wn and (rr if rr is not None else rc) > wr,
    "sem": lambda rc, rr, wn, wr: rc is not None,       # H9 R-mercado: g declarado sem trava
}
E0 = {"pl": lambda emp, pl, d: pl if pl > 0 else max(d, 1.0),
      "mercado": lambda emp, pl, d: emp.preco * emp.n_acoes / 1000,
      "3pl": lambda emp, pl, d: 3 * pl if pl > 0 else 3 * max(d, 1.0)}


@contextlib.contextmanager
def variante(trava="casa", e0="pl", aliquota=None, desconto=None, dm=0.0):
    """Ativa a regra alternativa no módulo do motor só dentro do bloco."""
    pilha = contextlib.ExitStack()
    pilha.enter_context(mock.patch.object(M, "valores", VALORES_V))
    pilha.enter_context(mock.patch.object(M, "estrutura_de_capital", ESTRUTURA_V))
    pilha.enter_context(mock.patch.object(M, "_CRIA", CRIA[trava], create=True))
    pilha.enter_context(mock.patch.object(M, "_E0", E0[e0], create=True))
    if aliquota is not None:
        pilha.enter_context(mock.patch.object(M, "aliquota_regra", lambda e, t=aliquota: (t, "explicita")))
        pilha.enter_context(mock.patch.object(M, "aliquota", lambda e, t=aliquota: t))
    if desconto is not None:
        pilha.enter_context(mock.patch.object(M, "desconto_pct", lambda e, x=desconto: x))
    if dm:
        orig = M.premissas_operacionais
        pilha.enter_context(mock.patch.object(M, "premissas_operacionais", lambda e: (lambda op: dict(
            op, m25=op["m25"] + dm, m50=op["m50"] + dm, m75=op["m75"] + dm))(orig(e))))
    with pilha:
        yield


def central_industrial(emp, mk=MK, ke_nom=None):
    """Mesmo caminho do `avaliar` até o central (ponto fixo → âncoras → desconto → mediana); `ke_nom` fixa o Ke do acionista."""
    ec = M.estrutura_de_capital(emp, mk)
    r = M.valores(emp, ec["mk"], ke_nom=ke_nom, e_peso=ec["e_peso"])
    return M.central_de(M.descontar(r["anc"], M.desconto_pct(emp)))[0], r, ec


def _rel(a, b):
    return (a - b) / abs(b) if b else math.inf


# ---------------------------------------------------------------- H1
def h1():
    linhas = []
    for tk in ind():
        emp, r0 = empresas()[tk], base(tk)
        casa = CRIA["casa"](r0["roic"], r0["roic_reposicao"], r0["wacc"], r0["wacc_real"])
        real = CRIA["real"](r0["roic"], r0["roic_reposicao"], r0["wacc"], r0["wacc_real"])
        try:
            with variante(trava="real"):
                c1 = central_industrial(emp)[0]
        except Exception as ex:
            c1 = None
        linhas.append(dict(ticker=tk, roic=r0["roic"], roic_rep=r0["roic_reposicao"], wacc=r0["wacc"], wacc_real=r0["wacc_real"],
                           trava_casa=casa, trava_real=real, muda=casa != real, central=r0["central"], central_v=c1,
                           dcentral=_rel(c1, r0["central"]) if c1 is not None else None))
    muda = [l for l in linhas if l["muda"]]
    grandes = [l for l in muda if l["dcentral"] is not None and abs(l["dcentral"]) >= 0.10]
    b_ok = len(muda) >= 3 and len(grandes) >= 3
    return dict(status="a conferir", criterio_b="cumprido" if b_ok else "não cumprido", linhas=linhas,
                resumo=f"(a) gabarito da fonte NÃO lido (Damodaran 2007 / Investment Valuation / Greenwald: PDF sem texto; "
                       f"verificador-fonte 22/10) → (a) não conta e a H1 fica 'a conferir'. (b) com a regra 'mesma base' "
                       f"(contábil × WACC nominal e reposição × WACC real): a trava muda em {len(muda)} industriais "
                       f"({', '.join(l['ticker'] for l in muda) or '—'}), |Δcentral| ≥ 10% em {len(grandes)}.",
                tentativa=True)


# ---------------------------------------------------------------- H2
def h2():
    linhas, falha_a, falha_b = [], [], []
    for tk in ind():
        emp, r0 = empresas()[tk], base(tk)
        cs = {}
        for k in E0:
            try:
                with variante(e0=k):
                    cs[k] = central_industrial(emp)[0]
            except Exception as ex:
                cs[k] = None
        vals = [c for c in cs.values() if c is not None]
        spread = (max(vals) - min(vals)) / abs(r0["central"]) if len(vals) == len(cs) and r0["central"] else None
        if spread is None or spread > 0.01:
            falha_a.append(tk)
        # (b) caixa a mais (10% da dívida bruta, mín. R$ 1 mi) com a mesma dívida bruta: o central não pode cair
        serie = copy.deepcopy(M.CVM[tk])
        extra = max(0.10 * M.divida_liquida(M.ltm_de(serie))[0], 1000.0)
        for k in ("ltm", "ltm_2T26"):
            if k in serie:
                serie[k]["caixa"] = (serie[k].get("caixa") or 0) + extra
        M.idade_e_fator.cache_clear()
        try:
            with mock.patch.dict(M.CVM, {tk: serie}):
                cb = central_industrial(emp)[0]
        except Exception:
            cb = None
        finally:
            M.idade_e_fator.cache_clear()
        if cb is not None and cb < r0["central"] * (1 - 1e-4):
            falha_b.append(tk)
        linhas.append(dict(ticker=tk, ke_nom=r0["ke_nom_emp"], de=r0["de_peso"], centrais=cs, spread=spread, central_caixa=cb,
                           central=r0["central"]))
    acima = [l["ticker"] for l in linhas if l["ke_nom"] > S.KE_TETO]
    aceita = bool(falha_a) or len(acima) >= 2
    return dict(status="aceita" if aceita else "refutada", linhas=linhas, tentativa=True,
                resumo=f"(a) ponto fixo com 3 partidas (PL, mercado, 3×PL): {len(falha_a)} ticker(s) com |Δcentral| > 1% "
                       f"({', '.join(falha_a) or '—'}). (b) caixa a mais com a mesma bruta baixa o central em {len(falha_b)} "
                       f"({', '.join(falha_b) or '—'}). (c) Ke nominal > 30% em {len(acima)} ({', '.join(acima)}). "
                       f"Critério: aceita se (a) falhar em algum OU ≥ 2 violarem (c).")


# ---------------------------------------------------------------- H3
def _elast(f, x0):
    lo, hi = f(x0 * 0.9), f(x0 * 1.1)
    return {k: (math.log(hi[k]) - math.log(lo[k])) / (math.log(1.1) - math.log(0.9)) if lo[k] > 0 and hi[k] > 0 else None
            for k in hi}


def _cos(u, v):
    nu, nv = math.sqrt(sum(x * x for x in u)), math.sqrt(sum(x * x for x in v))
    return sum(a * b for a, b in zip(u, v)) / (nu * nv) if nu and nv else 0.0


def h3():
    res = {"industrial": [], "financeira": []}
    for tk in ind():
        emp = empresas()[tk]
        _, r0, ec = central_industrial(emp)
        mk, ep, ke0, m0 = ec["mk"], ec["e_peso"], ec["mk"].ke_nom, r0["m"]
        g0 = emp.g_real if emp.g_real else 0.01
        anc = lambda **kw: M.valores(emp, mk, e_peso=ep, **kw)["anc"]
        e = dict(ke=_elast(lambda k: anc(ke_nom=k), ke0), fluxo=_elast(lambda m: anc(margem=m), m0),
                 g=_elast(lambda g: anc(g_real=g), g0))
        res["industrial"].append((tk, e))
    for tk in fin():
        emp = empresas()[tk]
        mk_k = lambda k: F.Mercado((1 + k) / (1 + MK.pi) - 1 - MK.premio, MK.pi, premio=MK.premio)
        orig = F.g_de

        def anc_g(f):
            with mock.patch.object(F, "g_de", lambda emp_, mk_, roe: orig(emp_, mk_, roe) * f):
                return F.ancoras(emp, MK, emp.roe_lp)
        e = dict(ke=_elast(lambda k: F.ancoras(emp, mk_k(k), emp.roe_lp), MK.ke_nom),
                 fluxo=_elast(lambda f: F.ancoras(replace(emp, roe_inicio=emp.roe_inicio * f / emp.roe_lp if emp.roe_lp else
                                                          emp.roe_inicio), MK, f), emp.roe_lp),
                 g=_elast(anc_g, 1.0))
        res["financeira"].append((tk, e))
    saida, veredito = {}, {}
    for motor, lst in res.items():
        todos_altos, baixas, n = 0, collections_counter(), 0
        tab = []
        for tk, e in lst:
            nomes = [k for k in e["ke"] if all(e[d].get(k) is not None for d in ("ke", "fluxo", "g"))]
            vet = {k: [e[d][k] for d in ("ke", "fluxo", "g")] for k in nomes}
            if len(vet) < 2:
                continue
            n += 1
            pares = {(a, b): _cos(vet[a], vet[b]) for a, b in itertools.combinations(sorted(vet), 2)}
            todos_altos += all(c >= 0.95 for c in pares.values())
            for k in vet:
                if all(c < 0.80 for (a, b), c in pares.items() if k in (a, b)):
                    baixas[k] += 1
            tab.append(dict(ticker=tk, vetores={k: [round(x, 3) for x in v] for k, v in vet.items()},
                            cos={f"{a} × {b}": round(c, 3) for (a, b), c in pares.items()}))
        frac = todos_altos / n if n else None
        independente = [k for k, c in baixas.items() if c > n / 2]
        veredito[motor] = ("aceita" if frac is not None and frac >= 0.70 else
                           "refutada" if independente else "inconclusiva")
        saida[motor] = dict(n=n, frac_todos_pares_altos=frac, ancoras_independentes=independente, tabela=tab)
    st = ("aceita" if all(v == "aceita" for v in veredito.values()) else
          "refutada" if all(v == "refutada" for v in veredito.values()) else "mista")
    return dict(status=st, por_motor=veredito, detalhe=saida, tentativa=False,
                resumo="; ".join(f"{m}: {saida[m]['n']} tickers, todos os pares com cos ≥ 0,95 em "
                                 f"{(saida[m]['frac_todos_pares_altos'] or 0):.0%}; âncora com cos < 0,80 na maioria: "
                                 f"{', '.join(saida[m]['ancoras_independentes']) or 'nenhuma'} → {veredito[m]}" for m in saida))


def collections_counter():
    import collections
    return collections.Counter()


# ---------------------------------------------------------------- H4
def h4():
    m15 = json.loads(MERCADO_15_10.read_text(encoding="utf-8"))
    mk15 = F.Mercado(rf_real=m15["rf_real"], pi=m15["pi"], data="15/10/2026")
    dpi = mk15.pi - MK.pi
    trocas, linhas = [], []
    for tk in ind() + fin():
        try:
            r1 = avaliar(tk, mk=mk15)
        except Exception as ex:
            r1 = None
        p0, p1 = base(tk)["palavra"], (r1 or {}).get("palavra")
        if p1 != p0:
            trocas.append(f"{tk} {p0} → {p1}")
        linhas.append(dict(ticker=tk, palavra=p0, palavra_15_10=p1, central=base(tk)["central"],
                           central_15_10=(r1 or {}).get("central")))
    aceita = abs(dpi) >= 0.005 or bool(trocas)
    return dict(status="aceita" if aceita else "refutada", tentativa=True, linhas=linhas, trocas=trocas,
                resumo=f"Datas: rf e π de 02/10 ({MK.rf_real:.2%}, {MK.pi:.2%}) × 15/10, a coleta com fonte A mais perto do "
                       f"preço de 22/10 ({mk15.rf_real:.2%}, {mk15.pi:.2%}): Δπ = {dpi * 100:+.2f} p.p., ΔKe nominal da casa = "
                       f"{(mk15.ke_nom - MK.ke_nom) * 100:+.2f} p.p.; palavras que mudam (preço do lote): "
                       f"{'; '.join(trocas) or 'nenhuma'}. Horizonte: a π no vértice da rf (~24 anos, NTN-B 2050) não está nos "
                       "arquivos locais (só 756, 1260 e 2520 du) → parte do prazo 'a conferir (dado)'. A doutrina (01 l.53) pede "
                       "o mesmo prazo e o código usa 2520 du: divergência registrada.")


# ---------------------------------------------------------------- H5
def h5():
    ke_casa = MK.rf_real + F.PREMIO_KE
    ke_d = MK.rf_real - DAMODARAN["spread"] + 1.0 * (DAMODARAN["erp_maduro"] + DAMODARAN["crp"])
    dif = ke_casa - ke_d
    return dict(status="refutada (provisória)" if abs(dif) < 0.01 else ("aceita" if dif >= 0.01 else "fora dos dois"),
                ke_casa=ke_casa, ke_damodaran=ke_d, tentativa=False,
                resumo=f"(a) planilha ctryprem ({DAMODARAN['data']}, nota A): Brasil {DAMODARAN['rating']}, spread "
                       f"{DAMODARAN['spread']:.2%}, CRP {DAMODARAN['crp']:.2%}, ERP maduro {DAMODARAN['erp_maduro']:.2%}. "
                       f"(b) Ke_D real = rf {MK.rf_real:.2%} − {DAMODARAN['spread']:.2%} + 1 × ({DAMODARAN['erp_maduro']:.2%} + "
                       f"{DAMODARAN['crp']:.2%}) = {ke_d:.2%} × Ke da casa {ke_casa:.2%}: diferença {dif * 100:+.2f} p.p. "
                       "(|Δ| < 1 p.p. → refutada: o nível de ~12% é defensável). Provisória: o método 'tirar o spread do título "
                       "local' tem apoio nos slides de Damodaran, mas o trecho com página do paper Country Risk não foi lido.")


# ---------------------------------------------------------------- H6 e H7
def _mann_kendall(x):
    from scipy.stats import norm
    x = [float(v) for v in x]
    n = len(x)
    s = sum((x[j] > x[i]) - (x[j] < x[i]) for i in range(n - 1) for j in range(i + 1, n))
    grupos = [list(x).count(v) for v in set(x)]
    var = (n * (n - 1) * (2 * n + 5) - sum(t * (t - 1) * (2 * t + 5) for t in grupos)) / 18
    z = (s - 1) / math.sqrt(var) if s > 0 else (s + 1) / math.sqrt(var) if s < 0 else 0.0
    return s, 2 * (1 - norm.cdf(abs(z)))


def _bh(ps, q=0.05):
    m = len(ps)
    ordem = sorted(range(m), key=lambda i: ps[i])
    k = max([r + 1 for r, i in enumerate(ordem) if ps[i] <= q * (r + 1) / m], default=0)
    return {ordem[r] for r in range(k)}


def h7():
    linhas = []
    for tk in ind():
        op = M.premissas_operacionais(empresas()[tk])
        mg = op["margens"]
        s, p = _mann_kendall(mg)
        linhas.append(dict(ticker=tk, perfil=empresas()[tk].perfil, n=len(mg), s=s, p=p, m50=op["m50"],
                           m3=statistics.median(mg[-3:])))
    sig = _bh([l["p"] for l in linhas])
    for i, l in enumerate(linhas):
        l["significativa_bh"] = i in sig
    alvo = [l for l in linhas if l["significativa_bh"] and l["s"] > 0 and l["perfil"] != "ciclica" and l["m3"] - l["m50"] >= 0.02]
    return dict(status="aceita" if len(alvo) >= 3 else "refutada", linhas=linhas, tentativa=False,
                tendencia=[l["ticker"] for l in sorted(linhas, key=lambda l: l["p"]) if l["s"] > 0 and l["perfil"] != "ciclica"],
                resumo=f"Mann-Kendall nas margens da janela de cada industrial ({len(linhas)} testes), BH q = 0,05: "
                       f"{len(sig)} significativas ({', '.join(linhas[i]['ticker'] for i in sorted(sig)) or '—'}); "
                       f"não cíclicas com tendência positiva e m50 ≥ 2 p.p. abaixo da mediana dos 3 últimos: {len(alvo)} "
                       f"({', '.join(l['ticker'] for l in alvo) or '—'}). Critério: aceita se ≥ 3.")


def _roic_dfp(tk, anos):
    """ROIC anual pelo DFP, sem o motor: EBIT (3.05) × (1 − IR/LAIR do ano, preso em [0; 34%]) ÷ média de (PL + DL) do fim do
    ano e do anterior. DL = empréstimos (2.01.04 + 2.02.01) − caixa e aplicações (1.01.01 + 1.01.02)."""
    cap, out = {}, {}
    for ano in [str(int(anos[0]) - 1)] + anos:
        bpa, bpp = R._contas(tk, ano, "BPA"), R._contas(tk, ano, "BPP")
        partes = [R._v(bpp, "2.03"), R._v(bpp, "2.01.04"), R._v(bpp, "2.02.01"), R._v(bpa, "1.01.01"), R._v(bpa, "1.01.02")]
        if None not in partes[:4]:
            pl, ec, el, cx, ap = partes
            cap[ano] = pl + ec + el - cx - (ap or 0)
    for ano in anos:
        dre = R._contas(tk, ano, "DRE")
        ebit, lair, ir = R._v(dre, "3.05"), R._v(dre, "3.07"), R._v(dre, "3.08")
        ant = str(int(ano) - 1)
        if None in (ebit, lair, ir) or ano not in cap or ant not in cap:
            continue
        t = min(max(-ir / lair, 0.0), M.ALIQUOTA_MARGINAL) if lair > 0 else M.ALIQUOTA_MARGINAL
        ci = (cap[ano] + cap[ant]) / 2
        if ci > 0:
            out[ano] = ebit * (1 - t) / ci
    return out


def h6(tendencia):
    if not any(R.CACHE.glob("dfp_*.zip")):
        return dict(status="a conferir (dado)", resumo="sem os ZIPs da CVM", tentativa=False)
    anos = [str(a) for a in range(2016, 2026)]
    extras = [t for t in tendencia if t != "WEGE3"][:2]
    linhas = []
    for tk in ["WEGE3"] + extras:
        serie = _roic_dfp(tk, anos)
        ult3 = [serie[a] for a in anos[-3:] if a in serie]
        m3 = statistics.median(ult3) if ult3 else None
        motor = base(tk)["roic"]
        linhas.append(dict(ticker=tk, roic_motor=motor, roic_filtro=base(tk)["roic_filtro"], roic_dfp=serie, mediana_3=m3,
                           gap=(m3 - motor) if (m3 is not None and motor is not None) else None))
    w = linhas[0]
    if w["gap"] is not None and abs(w["gap"]) <= 0.03:
        st = "refutada"
    elif w["gap"] is not None and w["gap"] >= 0.05:
        st = "a conferir"       # o (a) ainda precisa bater com o RI (±3 p.p.), que não foi lido em fonte A
    else:
        st = "inconclusiva"
    return dict(status=st, linhas=linhas, tentativa=False,
                resumo="; ".join(f"{l['ticker']}: ROIC do motor {l['roic_motor']:.1%} (menor dos dois {l['roic_filtro']:.1%}) × "
                                 f"mediana 2023–25 pelo DFP {l['mediana_3']:.1%} → motor {l['gap'] * 100:.1f} p.p. abaixo"
                                 for l in linhas if l["mediana_3"] is not None) +
                       ". (b) ROIC divulgado pela WEG (RI): NÃO lido em fonte A (só nota C: 32,5% 4T25, 34,2% 4T24) → a parte "
                       "'o (a) bate com o RI' fica a conferir. (c) '4 de 10 anos' da triagem: não reproduzido nesta rodada. "
                       f"Os 2 outros tickers saem da ordem de tendência da H7 (menor p, não cíclicos): {', '.join(extras) or '—'}.")


# ---------------------------------------------------------------- H8
def _codigos_fin(tk, ano):
    if tk in BANCOS_CVM:
        d = R._demo(ano, "BPP")
        if d is None:
            return []
        return sorted(d.loc[d["DENOM_CIA"].str.contains(BANCOS_CVM[tk], regex=True, na=False), "CD_CVM"].unique().tolist())
    return R._codigos(tk, ano)


def _roe_dfp(tk, anos):
    """ROE anual pelo DFP: lucro atribuído aos controladores ÷ média do PL consolidado sem os não controladores."""
    pl, out = {}, {}

    def contas(ano, demo):
        d = R._demo(ano, demo)
        cods = _codigos_fin(tk, ano)
        sub = d[d["CD_CVM"].isin(cods)] if d is not None else None
        return sub[sub["CD_CVM"] == sub["CD_CVM"].iloc[0]] if sub is not None and len(sub) else None
    for ano in [str(int(anos[0]) - 1)] + anos:
        bpp = contas(ano, "BPP")
        if bpp is None:
            continue
        tot = bpp[bpp["DS_CONTA"].str.fullmatch(r"Patrim[oô]nio L[ií]quido Consolidado", na=False)]
        nc = bpp[bpp["DS_CONTA"].str.contains("N[ãa]o Controlador", regex=True, na=False)
                 & bpp["CD_CONTA"].str.startswith(tot["CD_CONTA"].iloc[0] if len(tot) else "x")]
        if len(tot):
            pl[ano] = float(tot["VL"].iloc[0]) - (float(nc["VL"].iloc[0]) if len(nc) else 0.0)
    for ano in anos:
        dre = contas(ano, "DRE")
        if dre is None or ano not in pl or str(int(ano) - 1) not in pl:
            continue
        lc = dre[dre["DS_CONTA"].str.contains("Atribu[ií]do a S[óo]cios da Empresa Controladora", regex=True, na=False)
                 & dre["CD_CONTA"].str.match(r"3\.\d\d\.01$")]
        if not len(lc):
            continue
        media = (pl[ano] + pl[str(int(ano) - 1)]) / 2
        if media > 0:
            out[ano] = float(lc["VL"].iloc[0]) / media
    return out


def h8():
    from inflacao import inflacao_do_ano
    if not any(R.CACHE.glob("dfp_*.zip")):
        return dict(status="a conferir (dado)", resumo="sem os ZIPs da CVM", tentativa=False)
    anos = [str(a) for a in range(2017, 2026)]
    linhas, diverge, sinal = [], [], []
    ke_r, ke_n = MK.ke_real, MK.ke_nom
    for tk in fin():
        emp = empresas()[tk]
        serie = _roe_dfp(tk, anos)
        if len(serie) < 5:
            linhas.append(dict(ticker=tk, roe_lp=emp.roe_lp, n=len(serie), nota="série curta no DFP"))
            continue
        med = statistics.median(serie.values())
        med_r = statistics.median((1 + x) / (1 + inflacao_do_ano(a)) - 1 for a, x in serie.items())
        d = emp.roe_lp - med
        if abs(d) >= 0.01:
            diverge.append(tk)
        if (med - ke_n > 0) != (med_r - ke_r > 0):
            sinal.append(tk)
        linhas.append(dict(ticker=tk, perfil=emp.perfil, roe_lp=emp.roe_lp, n=len(serie), mediana=med, mediana_real=med_r,
                           dif=d, roe_menos_ke_nom=med - ke_n, roe_menos_ke_real=med_r - ke_r, serie=serie))
    aceita = len(diverge) >= 2 or len(sinal) >= 2
    return dict(status="aceita" if aceita else "refutada", linhas=linhas, tentativa=False,
                resumo=f"{len(fin())} objetos Financeira; ROE pelo DFP 2017–25 (lucro do controlador ÷ PL médio): roe_lp digitado "
                       f"a ≥ 1 p.p. da mediana em {len(diverge)} ({', '.join(diverge) or '—'}); sinal de (ROE − Ke) muda entre "
                       f"nominal ({ke_n:.2%}) e real ({ke_r:.2%}) em {len(sinal)} ({', '.join(sinal) or '—'}). "
                       "Critério: aceita se ≥ 2 em qualquer um. O ROE recorrente do Itaú (RI) não foi lido em fonte A.")


# ---------------------------------------------------------------- H9
FATORES = ("taxa", "margem", "g", "aliquota", "desconto")


def _central_s(emp, s: frozenset, ref: dict, casa: dict):
    kw = dict(trava=ref["g"] if "g" in s else "casa",
              aliquota=ref["aliquota"] if "aliquota" in s else None,
              desconto=0.0 if "desconto" in s else None,
              dm=(ref["margem"] - casa["m"]) if "margem" in s else 0.0)
    with variante(**kw):
        ke = ref["taxa"] if "taxa" in s else None
        if ke is None:
            return central_industrial(emp)[0]
        ec = M.estrutura_de_capital(emp, MK)
        r = M.valores(emp, ec["mk"], ke_nom=ke, e_peso=ec["e_peso"])
        return M.central_de(M.descontar(r["anc"], M.desconto_pct(emp)))[0]


def _shapley(v):
    n = len(FATORES)
    phi = {}
    for f in FATORES:
        outros = [x for x in FATORES if x != f]
        tot = 0.0
        for k in range(n):
            for sub in itertools.combinations(outros, k):
                peso = math.factorial(k) * math.factorial(n - k - 1) / math.factorial(n)
                tot += peso * (v[frozenset(sub) | {f}] - v[frozenset(sub)])
        phi[f] = tot
    return phi


def h9():
    precos = S.precos_hall()
    ke_d_real = MK.rf_real - DAMODARAN["spread"] + DAMODARAN["erp_maduro"] + DAMODARAN["crp"]
    ke_d_nom = (1 + ke_d_real) * (1 + MK.pi) - 1
    out = {"R-mercado": [], "R-fonte": []}
    for tk in ind():
        emp = empresas()[tk]
        r0 = base(tk)
        if not (r0["central"] > 0):
            continue
        preco = precos.get(tk, emp.preco)
        _, ltm = M.serie(tk)
        m_ltm = M.ebit_aj(ltm, r0["op"]["med_outras"], emp.outras_liquidas) / ltm["receita"] if ltm.get("receita") else r0["m"]
        ec = M.estrutura_de_capital(emp, MK)
        ke_impl = M.ke_implicito(emp, ec["mk"], ec["e_peso"])
        t_med = M.mediana_efetiva(emp)
        casa = dict(m=r0["m"])
        refs = {"R-mercado": dict(taxa=ke_impl, margem=m_ltm, g="sem", aliquota=t_med),
                "R-fonte": dict(taxa=ke_d_nom, margem=r0["m"], g="casa", aliquota=M.ALIQUOTA_MARGINAL)}
        for nome, ref in refs.items():
            if ref["taxa"] is None:
                continue
            try:
                v = {frozenset(s): math.log(preco / _central_s(emp, frozenset(s), ref, casa))
                     for k in range(len(FATORES) + 1) for s in itertools.combinations(FATORES, k)}
            except (ValueError, ZeroDivisionError):
                continue
            phi = _shapley(v)
            tot = sum(phi.values())
            out[nome].append(dict(ticker=tk, log_pc=v[frozenset()], phi=phi,
                                  fracao={f: (phi[f] / tot if tot else None) for f in FATORES}))
    resumo = {}
    for nome, lst in out.items():
        med = {f: statistics.median([l["fracao"][f] for l in lst if l["fracao"][f] is not None]) if lst else None for f in FATORES}
        dom = max(med, key=lambda f: abs(med[f] or 0)) if lst else None
        resumo[nome] = dict(n=len(lst), fracao_mediana=med, dominante=dom, empilhado=all(abs(x or 0) <= 0.5 for x in med.values()))
    emp_ok = all(r["empilhado"] for r in resumo.values())
    diverge = resumo["R-mercado"]["dominante"] != resumo["R-fonte"]["dominante"]
    return dict(status=("empilhamento confirmado" if emp_ok else "empilhamento não confirmado") +
                       (" · fator dominante diverge entre as referências (não se conclui)" if diverge else ""),
                tentativa=True, detalhe=out, resumo_ref=resumo,
                resumo="; ".join(f"{n} ({r['n']} industriais): fração mediana " +
                                 ", ".join(f"{f} {(r['fracao_mediana'][f] or 0):.0%}" for f in FATORES) +
                                 f" → dominante {r['dominante']}" for n, r in resumo.items()) +
                       ". R-fonte: taxa = Ke de Damodaran com β = 1 (β setorial não lido — marcado); margem do ciclo completo "
                       "e g = reinvestimento × ROIC sem regra com fonte → ficam no valor da casa (marcados); alíquota 34% legal "
                       "(crédito em VP não modelado — marcado). Financeiras fora (sem margem, alíquota nem trava de g).")


# ---------------------------------------------------------------- H10, H11
def h10():
    sys.path.insert(0, str(FERRAMENTAS / "tests"))
    import test_oraculo_propriedades as T
    contagem = {}
    for campo, chaves in T.CRITICOS.items():
        ruins = []
        for tk in ind():
            emp = empresas()[tk]
            with T._serie(tk, T._sem_campo(M.CVM[tk], chaves)):
                try:
                    r = avaliar(tk, emp)
                    r = avaliar(tk, replace(emp, preco=0.8 * r["central"])) if r["central"] > 0 else None
                except Exception:
                    r = None
            if r is not None and r["palavra"] in T.DECISAO:
                ruins.append(tk)
        contagem[campo] = ruins
    aceita = any(contagem.values())
    return dict(status="aceita (bug)" if aceita else "refutada", contagem=contagem, tentativa=False,
                resumo="Campo tirado de todos os períodos, preço a 0,8 × o central que sobra: " +
                       "; ".join(f"{c} → {len(v)} de {len(ind())} com palavra de decisão" for c, v in contagem.items()) +
                       ". Ligada ao xfail estrito test_h10_* (campos abertos) e à propriedade estrita (lucro, receita).")


def h11():
    reg = [tk for tk in fin() if empresas()[tk].perfil not in ("banco", "seguradora", "holding_seguro")]
    return dict(status="a conferir", tentativa=False,
                resumo=f"Reguladas nos lotes: {', '.join(reg)}. Ke real da casa {MK.ke_real:.2%}. Nenhuma nota técnica lida no "
                       "documento primário (ANEEL 401/403, ARSESP 404, AGEPAR e ARSAE só por resumo; verificador-fonte 22/10) → "
                       "todos os reguladores 'a conferir', fora da contagem. Pista nota C, sem efeito: WACC real depois de impostos "
                       "noticiado de 7,9% a 9,8% (ANEEL 2026: distribuição 8,10%, transmissão 8,00%; Sabesp 7,86%; Copasa 9,7–9,8%).")


# ---------------------------------------------------------------- relatório
def _limpo(x):
    if isinstance(x, dict):
        return {str(k): _limpo(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [_limpo(v) for v in x]
    if isinstance(x, float):
        return None if not math.isfinite(x) else round(x, 6)
    return x


def main(argv: list[str] | None = None) -> int:
    hoje = dt.date.today().isoformat()
    res = {}
    for nome, f in (("H1", h1), ("H2", h2), ("H3", h3), ("H4", h4), ("H5", h5), ("H7", h7)):
        print(f"[hipóteses] {nome}…", flush=True)
        res[nome] = f()
    res["H6"] = h6(res["H7"]["tendencia"])
    for nome, f in (("H8", h8), ("H9", h9), ("H10", h10), ("H11", h11)):
        print(f"[hipóteses] {nome}…", flush=True)
        res[nome] = f()
    ordem = [f"H{i}" for i in range(1, 12)]
    md = [f"# H1–H11 como relatório — {hoje}", "",
          "Gerado por `cd ferramentas && python -m oraculo.hipoteses` (PRE-REGISTRO-v3 §2, critérios escritos antes). Só relata: "
          "nenhuma palavra, central, golden ou doutrina mudou. Variantes rodam em cópias em memória do motor.", "",
          "| H | status | tentativa (§0.4) | resumo |", "|---|---|---|---|"]
    for h in ordem:
        md.append(f"| {h} | **{res[h]['status']}** | {'sim' if res[h].get('tentativa') else 'não'} | "
                  f"{res[h]['resumo'].replace('|', '/')} |")
    SAIDA.mkdir(parents=True, exist_ok=True)
    (SAIDA / f"hipoteses-{hoje}.md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    (SAIDA / f"hipoteses-{hoje}.json").write_text(json.dumps(_limpo(res), ensure_ascii=False, indent=1), encoding="utf-8",
                                                  newline="\n")
    print("\n".join(md))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
