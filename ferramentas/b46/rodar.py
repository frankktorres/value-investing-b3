"""B46 — medição da emenda 12 do `docs/PRE-REGISTRO-v3.md` sobre o conjunto de desenvolvimento. Uso, de `ferramentas/`:

    python -m b46.rodar insumos   # ANTES da emenda: indústria, D/E da indústria, D/E a mercado, t, rating (i) por ticker
    python -m b46.rodar medir     # DEPOIS do commit da emenda: variante + choques + conferências → b46/resultado_B46.json
    python -m b46.relatorio       # gera docs/b46/B46-2026-11.md só do JSON
    python -m b46.rodar medir --tentativa 8   # emenda 13 (B57): X2 com a 2.03.05 → b46/resultado_B46_t8.json
    python -m b46.relatorio --tentativa 8     # → docs/b46/B46-2026-11-t8.md (com a sensibilidade do X2 do DFP)

A variante roda sobre o motor congelado por `mock.patch` (como `oraculo/hipoteses.py`): o arquivo do motor não é tocado.
Modos: "base" = motor de hoje; "de" = só o D/E da continuidade (π = 0); "completo" = D/E da continuidade + π.
O modo `insumos` NÃO calcula o Z'' nem o π (ii): o C3 (concordância das duas estimativas) fica cego até a emenda estar no git.
"""
from __future__ import annotations

import contextlib
import json
import math
import pathlib
import sys
import traceback
from dataclasses import replace
from unittest import mock

AQUI = pathlib.Path(__file__).resolve().parent
FERRAMENTAS = AQUI.parent
if str(FERRAMENTAS) not in sys.path:
    sys.path.insert(0, str(FERRAMENTAS))

import credito  # noqa: E402
import mercado  # noqa: E402
import motor_nao_financeiras as M  # noqa: E402
from b46 import calculo as C  # noqa: E402

INSUMOS = AQUI / "insumos"
SAIDA = AQUI / "resultado_B46.json"
SAIDA_T8 = AQUI / "resultado_B46_t8.json"     # emenda 13: tentativa 8/24 (X2 do Z'' com a 2.03.05); a 7/24 não é sobrescrita
TENTATIVA = 7                                 # `medir --tentativa 8` troca para 8 (sensibilidade do X2 do DFP + SAIDA_T8)
SAIDA_INSUMOS = AQUI / "insumos_pre_registro.json"
DOSSIES = ("ALLD3", "BLAU3", "CMIN3", "FESA4", "SHUL4", "VLID3")     # os 6 dossiês do DNA §2 (princípio 5)
CHOQUES = {"preco_0.7": dict(preco=0.7, divida=1.0), "preco_1.3": dict(preco=1.3, divida=1.0),
           "divida_1.1": dict(preco=1.0, divida=1.1)}
LIMITE_PRECO = 0.005     # C2a: |Δcentral| ≤ 0,5% com o preço × 0,7 e × 1,3


class NaoAvaliado(Exception):
    """Insumo da variante ausente: o ticker sai com a razão, nunca com um padrão."""


def _ler(nome: str) -> dict:
    return json.loads((INSUMOS / nome).read_text(encoding="utf-8"))


IND = _ler("damodaran_waccemerg.json")
NOMES = _ler("damodaran_indname_bovespa.json")


def industria(tk: str) -> tuple[str, float, str]:
    """(indústria, D/E da indústria, como achou). Ticker exato no indname; senão a mesma raiz de 4 letras com indústria única."""
    emp = NOMES["empresas"]
    if tk in emp:
        nome, como = emp[tk]["industria"], "ticker"
    else:
        achados = {e["industria"] for t, e in emp.items() if t[:4] == tk[:4]}
        if len(achados) != 1:
            raise NaoAvaliado(f"{tk}: sem indústria no indname do Damodaran ({'raiz ambígua' if achados else 'ausente'})")
        nome, como = achados.pop(), "raiz"
    linha = IND["industrias"].get(nome)
    if linha is None:
        raise NaoAvaliado(f"{tk}: indústria '{nome}' sem linha no waccemerg")
    return nome, C.de_da_participacao(linha["d_sobre_d_mais_e"]), como


def rating_cobertura(emp, ltm) -> tuple[str, float | None]:
    """(i) A conta do `custo_divida` (cobertura normalizada ÷ juros do período → rating sintético), também com `kd_ri`."""
    op = M.premissas_operacionais(emp)
    juros, _ = M.juros_do_periodo(ltm)
    if juros <= 0:
        if M.divida_liquida(ltm)[0] > 0:
            raise NaoAvaliado(f"{emp.ticker}: dívida bruta > 0 sem juros no período (rating (i) não sai)")
        return credito.spread_sintetico(None)[1], None
    cob = op["receita_meio"] * (op["m50"] + op["ajuste_manut"]) / juros
    return credito.spread_sintetico(cob)[1], cob


CAMPOS_Z = ("ativo", "ac", "pc", "reservas_lucro", "lucros_acumulados", "ebit", "pl", "pnc")   # 2.03.05: emenda 13 (B57)


def _dfp(emp, a) -> dict:
    return a["2026" if emp.ticker == "SMTO3" else "2025"]


def z_altman(emp, a, ltm) -> float:
    """(ii) o Z'' do motor sobre o MESMO período que o `avaliar` usa; campo ausente → não avaliado (sem o zero do `v`)."""
    d = ltm if ltm.get("ativo") else _dfp(emp, a)
    faltam = [k for k in CAMPOS_Z if d.get(k) is None]
    if faltam:
        raise NaoAvaliado(f"{emp.ticker}: Z'' sem {', '.join(faltam)}")
    return M.altman_z2(d)[0]


def z_altman_x2_dfp(emp, a, ltm) -> float:
    """Sensibilidade da emenda 13 (pedido do Frank; relatada, não entra no π): o mesmo Z'' com o X2 do ÚLTIMO DFP —
    (2.03.04 + 2.03.05) ÷ ativo do DFP — e X1, X3, X4 do período do `avaliar`. As duas contas do DFP vão ao motor escaladas
    pelo ativo do período, para que o X2 calculado lá dentro seja exatamente o do DFP."""
    d, f = (ltm if ltm.get("ativo") else _dfp(emp, a)), _dfp(emp, a)
    faltam = [k for k in CAMPOS_Z if d.get(k) is None] + [f"DFP {k}" for k in ("ativo", "reservas_lucro", "lucros_acumulados")
                                                         if f.get(k) is None]
    if faltam:
        raise NaoAvaliado(f"{emp.ticker}: Z'' (X2 do DFP) sem {', '.join(faltam)}")
    esc = d["ativo"] / f["ativo"]
    return M.altman_z2({**d, "reservas_lucro": f["reservas_lucro"] * esc, "lucros_acumulados": f["lucros_acumulados"] * esc})[0]


# ------------------------------------------------------------------------------------------------ variante
@contextlib.contextmanager
def _rapido():
    """Ke e g implícitos não entram em central nem palavra (emenda 2): trocados por None, como no oráculo."""
    with mock.patch.object(M, "ke_implicito", lambda *a, **k: None), mock.patch.object(M, "g_implicito", lambda *a, **k: None):
        yield


@contextlib.contextmanager
def _choque_divida(f: float):
    if f == 1.0:
        yield
        return
    dl0, jp0 = M.divida_liquida, M.juros_do_periodo

    def dl(b):
        bruta, caixa, _ = dl0(b)
        return bruta * f, caixa, bruta * f - caixa

    def jp(d):
        j, fonte = jp0(d)
        return j * f, fonte
    with mock.patch.object(M, "divida_liquida", dl), mock.patch.object(M, "juros_do_periodo", jp):
        yield


def _estrutura_continuidade(de_ind: float, reg: dict):
    def f(emp, mk):
        _, ltm = M.serie(emp.ticker)
        d = M.divida_do_desconto(emp, ltm)
        e = emp.preco * emp.n_acoes / 1000
        if not e > 0:
            raise ValueError(f"{emp.ticker}: valor de mercado do patrimônio ≤ 0")
        de_m = d / e
        de_c = C.de_continuidade(de_m, de_ind)
        e_c = d / de_c if de_c > 0 else e
        t = M.aliquota(emp)
        reg.update(de_mercado=de_m, de_cont=de_c, t=t)
        return dict(mk=replace(mk, premio=M.PREMIO_KE * (1 + (1 - t) * de_c)), e_peso=e_c, d=d,
                    nota="B46: D/E da continuidade = min(a mercado, indústria Damodaran EM)")
    return f


def _descontar_com_pi(pi: float, reg: dict):
    d0 = M.descontar

    def f(anc, desc):
        sem = d0(anc, desc)
        com = C.ancoras_com_pi(sem, pi)
        reg.setdefault("anc_sem_pi", dict(sem))
        reg.setdefault("anc_com_pi", dict(com))
        return com
    return f


def emp_chocada(emp, choque: dict):
    """Preço × choque["preco"]; os outros passivos financeiros × choque["divida"]. O D do motor (`divida_do_desconto`) =
    dívida bruta com arrendamentos (choque em `_choque_divida`) + outros passivos financeiros: o choque multiplica os dois
    (adversário, 25/11: na CMIN3 o D subia só 4,1% com o choque de "10%")."""
    return replace(emp, preco=emp.preco * choque["preco"],
                   outros_passivos_financeiros=emp.outros_passivos_financeiros * choque["divida"])


def pi_das_estimativas(rating_i: str | None, z: float | None) -> tuple:
    """(π (i), rating (ii), π (ii), π). Emenda 12: com uma só, vale a única — também quando falta a (i) (adversário, 25/11)."""
    pi_i = C.pi_de_classe(rating_i) if rating_i is not None else None
    r_ii = C.rating_altman(z) if z is not None else None
    pi_ii = C.pi_de_classe(r_ii) if r_ii is not None else None
    return pi_i, r_ii, pi_ii, C.pi_combinado(pi_i, pi_ii)


def avaliar_v(emp, mk, modo: str, choque: dict, reg: dict):
    """Avalia `emp` no modo pedido, com o choque; `reg` recebe os insumos e números do caminho (o último chamado vale)."""
    reg.clear()
    emp = emp_chocada(emp, choque)
    with contextlib.ExitStack() as p:
        p.enter_context(_rapido())
        p.enter_context(_choque_divida(choque["divida"]))
        a, ltm = M.serie(emp.ticker)
        reg["de_mercado"] = M.divida_do_desconto(emp, ltm) / (emp.preco * emp.n_acoes / 1000)
        try:
            r_i, cob = rating_cobertura(emp, ltm)
            reg.update(rating_i=r_i, cobertura=cob)
        except NaoAvaliado as x:
            r_i, cob = None, None
            reg["falta_i"] = str(x)
        if modo in ("de", "completo"):
            nome, de_ind, como = industria(emp.ticker)
            reg.update(industria=nome, de_ind=de_ind, industria_por=como)
            p.enter_context(mock.patch.object(M, "estrutura_de_capital", _estrutura_continuidade(de_ind, reg)))
        if modo == "de":        # π = 0: só registra as âncoras, para a conferência C1 (completo = "só D/E" × (1 − π))
            p.enter_context(mock.patch.object(M, "descontar", _descontar_com_pi(0.0, reg)))
        if modo == "completo":
            try:
                z, falta_ii = z_altman(emp, a, ltm), None
            except NaoAvaliado as x:
                z, falta_ii = None, str(x)
            pi_i, r_ii, pi_ii, pi = pi_das_estimativas(r_i, z)
            if pi is None:
                raise NaoAvaliado(f"{emp.ticker}: π sem nenhuma das duas estimativas ({reg.get('falta_i')}; {falta_ii})")
            reg.update(rating_i=r_i, cobertura=cob, pi_i=pi_i, z=z, rating_ii=r_ii, pi_ii=pi_ii, falta_ii=falta_ii, pi=pi,
                       concordam=C.concordam(pi_i, pi_ii))
            if TENTATIVA == 8:      # sensibilidade (emenda 13): só registrada; o π que desconta as âncoras é o de cima
                try:
                    z_d = z_altman_x2_dfp(emp, a, ltm)
                    pi_ii_d = C.pi_de_classe(C.rating_altman(z_d))
                    reg.update(z_x2_dfp=z_d, pi_ii_x2_dfp=pi_ii_d, concordam_x2_dfp=C.concordam(pi_i, pi_ii_d))
                except NaoAvaliado as x:
                    reg.update(z_x2_dfp=None, falta_x2_dfp=str(x), concordam_x2_dfp=False)
            p.enter_context(mock.patch.object(M, "descontar", _descontar_com_pi(pi, reg)))
        r = M.avaliar(emp, mk)
    reg.update(palavra=r["palavra"], central=r.get("central"), pc=r.get("pc"), ke_nom=r.get("ke_nom_emp"),
               premio=r.get("premio_ke"))
    reg["rf_real"], reg["pi_inflacao"] = mk.rf_real, mk.pi
    return r


# ------------------------------------------------------------------------------------------------ caminhos
def _hall():
    from oraculo import sanidade as S
    return [(tk, e) for tk, e in sorted(S.empresas().items())]


def _rodar_hall(tk, emp, modo, choque):
    reg = {}
    avaliar_v(emp, mercado.vigente(), modo, choque, reg)
    return reg


def _rodar_gerar(tk, modo, choque, data=None, contexto=None):
    from dossie import gerar
    reg = {}
    with contextlib.ExitStack() as p:
        if contexto is not None:
            p.enter_context(contexto)
        p.enter_context(mock.patch.object(gerar, "avaliar", lambda emp, mk: avaliar_v(emp, mk, modo, choque, reg)))
        gerar.calcular(tk, data)
    return reg


def _contexto_b36(tk):
    from holdout_b36 import executor as X
    c = X.cadastro()[tk]
    return X.registrado(c, X.ficha_padrao(c, X._dia_statusinvest(tk)), X.ler_insumos(tk), X.SERIES), X.T


def universo() -> list[dict]:
    """O conjunto de desenvolvimento (DNA §2, princípio 5): hall (todos, financeiras marcadas), 6 dossiês, as 20 da B36."""
    import motor_financeiras as F
    out = [dict(tk=tk, grupo="hall", financeira=isinstance(e, F.Financeira), emp=e) for tk, e in _hall()]
    out += [dict(tk=tk, grupo="dossie", financeira=False) for tk in DOSSIES]
    from holdout_b36 import executor as X
    out += [dict(tk=tk, grupo="b36", financeira=c["tipo"] != "industrial") for tk, c in X.cadastro().items()]
    return out


def rodar_um(u: dict, modo: str, choque: dict) -> dict:
    if u["grupo"] == "hall":
        return _rodar_hall(u["tk"], u["emp"], modo, choque)
    if u["grupo"] == "dossie":
        return _rodar_gerar(u["tk"], modo, choque)
    ctx, t = _contexto_b36(u["tk"])
    return _rodar_gerar(u["tk"], modo, choque, data=t, contexto=ctx)


def _tentar(u, modo, choque) -> dict:
    try:
        return dict(rodar_um(u, modo, choque), erro=None)
    except NaoAvaliado as x:
        return dict(erro=dict(tipo="não avaliado", mensagem=str(x)))
    except Exception as x:      # noqa: BLE001 — a medição registra a falha com o lugar, não a esconde
        tb = traceback.extract_tb(x.__traceback__)[-1]
        return dict(erro=dict(tipo=type(x).__name__, mensagem=str(x)[:400], onde=f"{pathlib.Path(tb.filename).name}:{tb.lineno}"))


def _limpo(x):
    if isinstance(x, float) and not math.isfinite(x):
        return str(x)
    if isinstance(x, dict):
        return {k: _limpo(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [_limpo(v) for v in x]
    return x


def insumos() -> list[dict]:
    """Tabela da emenda 12 (antes de rodar a variante): só o motor de hoje + a classificação da fonte."""
    linhas = []
    um = dict(preco=1.0, divida=1.0)
    for u in universo():
        if u["financeira"]:
            linhas.append(dict(tk=u["tk"], grupo=u["grupo"], financeira=True))
            continue
        b = _tentar(u, "base", um)
        lin = dict(tk=u["tk"], grupo=u["grupo"], financeira=False, erro_base=b.get("erro"),
                   de_mercado=b.get("de_mercado"), t=None, ke_base=b.get("ke_nom"), palavra_base=b.get("palavra"),
                   rating_i=b.get("rating_i"), falta_i=b.get("falta_i"))
        try:
            nome, de_ind, como = industria(u["tk"])
            lin.update(industria=nome, de_ind=de_ind, industria_por=como)
        except NaoAvaliado as x:
            lin.update(industria=None, falta_industria=str(x))
        linhas.append(lin)
        print(u["tk"], lin.get("industria"), lin.get("de_ind") and round(lin["de_ind"], 3),
              lin.get("de_mercado") and round(lin["de_mercado"], 2), lin.get("rating_i"), (b.get("erro") or {}).get("mensagem", "")[:80])
    return linhas


def medir() -> dict:
    um = dict(preco=1.0, divida=1.0)
    linhas = []
    for u in universo():
        lin = dict(tk=u["tk"], grupo=u["grupo"], financeira=u["financeira"])
        if u["financeira"]:
            linhas.append(lin)
            continue
        lin["base"] = _tentar(u, "base", um)
        lin["de"] = _tentar(u, "de", um)
        lin["completo"] = _tentar(u, "completo", um)
        lin["choques"] = {n: _tentar(u, "completo", ch) for n, ch in CHOQUES.items()}
        lin["base_divida_1.1"] = _tentar(u, "base", CHOQUES["divida_1.1"])
        linhas.append(lin)
        c = lin["completo"]
        print(u["tk"], lin["base"].get("palavra"), "→", c.get("palavra"), "Ke", c.get("ke_nom") and round(c["ke_nom"], 4),
              "π", c.get("pi") and round(c["pi"], 3), (c.get("erro") or {}).get("mensagem", "")[:80])
    return dict(emenda=12 if TENTATIVA == 7 else 13, tentativa=TENTATIVA, data_mercado_hall=str(mercado.vigente().data), fontes=dict(waccemerg={k: IND[k] for k in IND if k != "industrias"},
                indname={k: NOMES[k] for k in NOMES if k != "empresas"}), linhas=linhas)


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    a = list(argv if argv is not None else sys.argv[1:])
    if a[:1] == ["insumos"]:
        SAIDA_INSUMOS.write_text(json.dumps(_limpo(insumos()), ensure_ascii=False, indent=1), encoding="utf-8")
        return 0
    if a[:1] == ["medir"]:
        global TENTATIVA
        if a[1:] not in ([], ["--tentativa", "8"]):
            print(__doc__)
            return 2
        TENTATIVA = 8 if a[1:] else 7
        (SAIDA_T8 if TENTATIVA == 8 else SAIDA).write_text(json.dumps(_limpo(medir()), ensure_ascii=False, indent=1, default=str), encoding="utf-8")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
