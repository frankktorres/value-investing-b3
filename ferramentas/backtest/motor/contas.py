"""Contas puras copiadas de motor_nao_financeiras.py — fórmula idêntica, zero acoplamento a 2026.

Por que CÓPIA e não import: `import motor_nao_financeiras` carrega `dados/cvm_series.json` e o
`series_*.json` mais recente no nível de módulo (:22-23) — ~1 MB da coleta de out/2026, com a chave
de período literal `"ltm_2T26"`. O backtest roda com o ledger point-in-time da data de corte, e não
pode ter o dado de 2026 nem em memória: é assim que um look-ahead entra por descuido.

A duplicação se paga com `tests/test_equivalencia_contas.py`, que importa as originais SÓ dentro do
teste e exige resultado idêntico em milhares de dicts aleatórios e em todos os exercícios reais de
`cvm_series.json`. Se alguém mexer numa das duas pontas, o teste quebra.

As oito são as únicas de lá que recebem dicts e nada mais. Ficaram FORA, por não serem puras:
`capex_manutencao`, `mediana_outras` e `anos_validos` chamam `serie(tk)`, que lê o JSON de 2026 —
essas o backtest reimplementa sobre o ledger (fatia 5 em diante).

Fórmulas: doutrina §7 (armadilhas), §9 (qualidade do lucro), §11.1 (quadro clássico).
"""
from __future__ import annotations


def v(d: dict, k: str, default: float = 0.0) -> float:
    """Valor da conta, tratando None como ausente (a CVM traz linha vazia, não zero).

    O original tem `default=None`; aqui o default é numérico porque todo uso nestas oito funções
    passa um número, e isso mantém a inferência de tipo limpa. Comportamento idêntico em todos os
    pontos de chamada — o que o teste de equivalência confere.
    """
    x = d.get(k)
    return default if x is None else x


def divida_liquida(b: dict) -> tuple[float, float, float]:
    """(bruta, caixa, líquida). IFRS 16: o arrendamento é dívida."""
    bruta = v(b, "emprest_cp", 0) + v(b, "emprest_lp", 0) + v(b, "arrendamento", 0)
    caixa = v(b, "caixa", 0) + v(b, "aplic_cp", 0)
    return bruta, caixa, bruta - caixa


def capital_giro(b: dict) -> float:
    """Capital de giro operacional: sem caixa e aplicações no ativo, sem dívida curta no passivo."""
    return (v(b, "ac", 0) - v(b, "caixa", 0) - v(b, "aplic_cp", 0)) - (v(b, "pc", 0) - v(b, "emprest_cp", 0))


def altman_z2(d: dict) -> tuple[float, str]:
    """Altman Z'' (empresa não financeira, mercado emergente). §11.1 — qualidade do lucro."""
    at = d["ativo"]
    x1 = (v(d, "ac", 0) - v(d, "pc", 0)) / at
    x2 = v(d, "reservas_lucro", 0) / at
    x3 = v(d, "ebit", 0) / at
    x4 = v(d, "pl", 0) / (v(d, "pc", 0) + v(d, "pnc", 0))
    z = 3.25 + 6.56 * x1 + 3.26 * x2 + 6.72 * x3 + 1.05 * x4
    zona = "segura" if z > 5.85 else ("cinzenta" if z >= 4.15 else "perigo")
    return z, zona


def piotroski(d: dict, p: dict) -> tuple[int, list[bool]]:
    """F-score de 0 a 9 entre o exercício `d` e o anterior `p`."""
    roa, roa0 = d["lucro"] / d["ativo"], p["lucro"] / p["ativo"]
    alav = v(d, "emprest_lp", 0) / d["ativo"]
    alav0 = v(p, "emprest_lp", 0) / p["ativo"]
    liq, liq0 = d["ac"] / d["pc"], p["ac"] / p["pc"]
    mb, mb0 = v(d, "lucro_bruto", 0) / d["receita"], v(p, "lucro_bruto", 0) / p["receita"]
    giro, giro0 = d["receita"] / d["ativo"], p["receita"] / p["ativo"]
    acoes_ok = not (d.get("acoes") and p.get("acoes") and d["acoes"] > p["acoes"] * 1.005)
    crit = [roa > 0, v(d, "fco", 0) > 0, roa > roa0, v(d, "fco", 0) > d["lucro"], alav < alav0, liq > liq0, acoes_ok,
            mb > mb0, giro > giro0]
    return sum(crit), crit


def beneish(d: dict, p: dict) -> float | None:
    """M-score. Acima de −1,78 é alerta de manipulação de resultado. None quando não calculável."""
    try:
        dsri = (v(d, "receber", 0) / d["receita"]) / (v(p, "receber", 0) / p["receita"])
        gm0 = v(p, "lucro_bruto", 0) / p["receita"]
        gm1 = v(d, "lucro_bruto", 0) / d["receita"]
        gmi = gm0 / gm1
        aq = lambda x: 1 - (v(x, "ac", 0) + v(x, "imobilizado", 0)) / x["ativo"]            # noqa: E731
        aqi = aq(d) / aq(p)
        sgi = d["receita"] / p["receita"]
        dep = lambda x: v(x, "da", 0) / (v(x, "da", 0) + v(x, "imobilizado", 0))            # noqa: E731
        depi = dep(p) / dep(d)
        sga = lambda x: -(v(x, "desp_vendas", 0) + v(x, "desp_ga", 0)) / x["receita"]        # noqa: E731
        sgai = sga(d) / sga(p)
        tata = (d["lucro"] - v(d, "fco", 0)) / d["ativo"]
        lev = lambda x: (v(x, "pc", 0) + v(x, "pnc", 0)) / x["ativo"]                        # noqa: E731
        lvgi = lev(d) / lev(p)
        m = (-4.84 + 0.92 * dsri + 0.528 * gmi + 0.404 * aqi + 0.892 * sgi + 0.115 * depi - 0.172 * sgai
             + 4.679 * tata - 0.327 * lvgi)
        return m
    except (ZeroDivisionError, TypeError):
        return None


def sloan(d: dict, p: dict) -> float:
    """Accruals de Sloan: quanto do lucro não virou caixa, sobre o ativo médio."""
    return (d["lucro"] - v(d, "fco", 0)) / ((d["ativo"] + p["ativo"]) / 2)


def outras(d: dict, liquidas: bool = False) -> float:
    """'Outras receitas operacionais' (3.04.04), opcionalmente líquidas de 3.04.05 sem impairment.

    Empresa que lança ganhos (venda de ativo, crédito tributário) em 'outras despesas' precisa da
    forma líquida; só o impairment lançado DENTRO de 3.04.05 sai daqui, porque é tratado à parte.
    """
    imp = v(d, "impairment_outras", v(d, "impairment", 0))
    return v(d, "outras_receitas_op", 0) + ((v(d, "outras_despesas_op", 0) - imp) if liquidas else 0)


def ebit_aj(d: dict, med_outras: float | None = None, liquidas: bool = False) -> float:
    """EBIT sem o EXCESSO de 'outras receitas' acima da mediana de 10 anos da empresa (§7, armadilha 1).

    Só penaliza. O ganho de valor justo de ativo biológico não é retirado: a exaustão o devolve no
    ciclo, e retirar só o ganho penalizaria duas vezes.
    """
    if med_outras is None or not d.get("receita"):
        return d["ebit"]
    excesso = max(outras(d, liquidas) - med_outras * d["receita"], 0)
    return d["ebit"] - excesso


PURAS = (divida_liquida, capital_giro, altman_z2, piotroski, beneish, sloan, outras, ebit_aj)
