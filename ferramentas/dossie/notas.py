"""Rubrica das notas qualitativas (0-5) por evidência. Limiares declarados; não mudar sem decisão do Frank.

Cada função devolve `Nota(nome, base, componentes)`; `componentes` explica cada passo com o número usado.
`None` num insumo = "sem evidência" e vale o resultado conservador indicado na regra.
Margens em fração (0.42); desvio-padrão (amostral) comparado em pontos percentuais (x100).
"""
import math
import statistics
from dataclasses import dataclass, field

from motor_financeiras import media_qualitativa

_EPS = 9  # casas decimais para comparar fronteiras sem ruído de ponto flutuante


@dataclass
class Nota:
    nome: str
    base: int
    componentes: list = field(default_factory=list)


def _limitar(x, lo=0, hi=5):
    return max(lo, min(hi, x))


def _dp_pp(serie):
    """Desvio-padrão amostral em p.p. (arredondado para a comparação de fronteiras)."""
    return round(statistics.stdev(serie) * 100, _EPS)


# ------------------------------------------------------------------ moat
def moat(roic_real, wacc_real, margens_brutas, margens_ebit=None):
    """Fração f de exercícios com ROIC real > WACC real; penaliza margem bruta instável; tetos por janela."""
    janela = len(roic_real)
    comp = []
    if janela == 0:
        return Nota("moat", 0, ["janela 0 exercícios de ROIC: sem evidência -> 0"])
    n = sum(1 for v in roic_real.values() if v > wacc_real)
    f = round(n / janela, _EPS)
    if f == 1:
        base = 5
    elif f >= 0.8:
        base = 4
    elif f >= 0.7:
        base = 3
    elif f >= 0.5:
        base = 2
    elif f > 0:
        base = 1
    else:
        base = 0
    comp.append(f"ROIC real > WACC real ({wacc_real:.4f}) em {n} de {janela} exercícios (f={f:.2f}) -> {base}")
    if margens_brutas is not None and len(margens_brutas) >= 3:
        serie, rot = margens_brutas, "margem bruta"
    elif margens_ebit is not None and len(margens_ebit) >= 3:
        serie, rot = margens_ebit, "margem EBIT (margem bruta ausente ou < 3 pontos)"
    else:
        serie, rot = None, ""
    if serie is None:
        base -= 1
        comp.append("sem série de margem (bruta nem EBIT, >= 3 pontos): -1 conservador")
    else:
        dp = _dp_pp(serie)
        if dp > 5:
            base -= 1
            comp.append(f"desvio-padrão da {rot} {dp:.2f} p.p. > 5: -1")
        else:
            comp.append(f"desvio-padrão da {rot} {dp:.2f} p.p. <= 5: sem penalidade")
    teto = 3 if janela < 7 else 4 if janela < 10 else 5
    if base > teto:
        comp.append(f"janela de {janela} exercícios: teto {teto}")
        base = teto
    return Nota("moat", _limitar(base), comp)


# ------------------------------------------------------------------ ciclo
def ciclo(receitas_reais, margens_ebit, anos_prejuizo_operacional):
    """Menor entre a escala da maior queda anual da receita real e a do desvio-padrão da margem EBIT."""
    if len(receitas_reais) < 3 or len(margens_ebit) < 3:
        return Nota("ciclo", 1, [f"série curta (receita {len(receitas_reais)}, margem EBIT {len(margens_ebit)} "
                                 "pontos; mínimo 3): base 1 conservador"])
    quedas = [1 - b / a for a, b in zip(receitas_reais, receitas_reais[1:]) if a > 0]
    q = round(max([0.0] + quedas), _EPS)
    a_ = 5 if q < 0.05 else 4 if q < 0.10 else 3 if q < 0.20 else 2 if q < 0.35 else 1
    dp = _dp_pp(margens_ebit)
    b_ = 5 if dp <= 3 else 4 if dp <= 5 else 3 if dp <= 8 else 2 if dp <= 12 else 1
    base = min(a_, b_)
    comp = [f"maior queda anual da receita real {q * 100:.1f}% -> A={a_}",
            f"desvio-padrão da margem EBIT {dp:.2f} p.p. -> B={b_}",
            f"base = min(A, B) = {base}"]
    if anos_prejuizo_operacional >= 2:
        comp.append(f"{anos_prejuizo_operacional} anos de prejuízo operacional (>= 2): teto 1")
        base = min(base, 1)
    return Nota("ciclo", _limitar(base), comp)


# ------------------------------------------------------------------ gestão
def gestao(r1_retido, cagr_acoes, rem_sobre_lucro, ma_ruim):
    """Parte de 3: R$1 retido, diluição, remuneração/lucro e histórico de M&A."""
    base, comp = 3, ["parte de 3"]
    if r1_retido is None:
        base -= 1
        comp.append("R$1 retido sem evidência: -1 conservador")
    elif isinstance(r1_retido, str):
        comp.append(f"R$1 retido '{r1_retido}' (retenção <= 0, teste indefinido): 0")
    elif r1_retido >= 1.5:
        base += 1
        comp.append(f"R$1 retido {r1_retido:.2f} >= 1,5: +1")
    elif r1_retido < 1.0:
        base -= 1
        comp.append(f"R$1 retido {r1_retido:.2f} < 1,0: -1")
    else:
        comp.append(f"R$1 retido {r1_retido:.2f} entre 1,0 e 1,5: 0")
    if cagr_acoes is None:
        base -= 1
        comp.append("CAGR das ações sem evidência: -1 conservador")
    elif round(cagr_acoes, _EPS) >= 0.02:
        base -= 1
        comp.append(f"CAGR das ações {cagr_acoes * 100:.2f}% a.a. >= 2%: -1 (diluição)")
    elif round(cagr_acoes, _EPS) <= -0.01:
        base += 1
        comp.append(f"CAGR das ações {cagr_acoes * 100:.2f}% a.a. <= -1%: +1 (recompra)")
    else:
        comp.append(f"CAGR das ações {cagr_acoes * 100:.2f}% a.a.: 0")
    if rem_sobre_lucro is None:
        base -= 1
        comp.append("remuneração/lucro sem evidência: -1 conservador")
    elif round(rem_sobre_lucro, _EPS) > 0.05:
        base -= 1
        comp.append(f"remuneração/lucro {rem_sobre_lucro * 100:.2f}% > 5%: -1")
    else:
        comp.append(f"remuneração/lucro {rem_sobre_lucro * 100:.2f}% <= 5%: 0")
    if ma_ruim is None:
        base -= 1
        comp.append("histórico de M&A sem evidência: -1 conservador")
    elif ma_ruim:
        base -= 1
        comp.append("M&A destruidor de valor: -1")
    else:
        comp.append("M&A sem destruição de valor: 0")
    return Nota("gestao", _limitar(base), comp)


# ------------------------------------------------------------------ controlador
def controlador(tem_controlador, tag_along, partes_rel_sobre_receita, interferencias):
    """Alinhamento do controlador: tag along, partes relacionadas/receita e interferências consumadas."""
    if tem_controlador is None:
        base, comp = 4, ["controlador sem evidência: base 4 conservador"]
    elif tem_controlador:
        base, comp = 4, ["tem controlador: base 4"]
    else:
        base, comp = 5, ["sem controlador (capital pulverizado): base 5"]
    if tag_along is None:
        base -= 1
        comp.append("tag along sem evidência: -1 conservador")
    elif round(tag_along, _EPS) < 1.0:
        base -= 1
        comp.append(f"tag along {tag_along * 100:.0f}% < 100%: -1")
    else:
        comp.append(f"tag along {tag_along * 100:.0f}%: 0")
    p = partes_rel_sobre_receita
    if p is None:
        base -= 1
        comp.append("partes relacionadas/receita sem evidência: -1 conservador")
    elif round(p, _EPS) > 0.15:
        base -= 2
        comp.append(f"partes relacionadas {p * 100:.1f}% da receita > 15%: -2")
    elif round(p, _EPS) > 0.05:
        base -= 1
        comp.append(f"partes relacionadas {p * 100:.1f}% da receita > 5%: -1")
    else:
        comp.append(f"partes relacionadas {p * 100:.1f}% da receita <= 5%: 0")
    n = interferencias
    if n is None:      # busca não feita/documentada ≠ "nenhuma": conservador como os demais (achado do adversário, 07/10)
        base -= 1
        comp.append("interferências consumadas sem evidência (busca não documentada): -1 conservador")
    elif n < 0:
        raise ValueError("interferencias deve ser >= 0")
    else:
        desc = min(n, 3)
        base -= desc
        comp.append(f"{n} interferência(s) consumada(s) em 15 anos: -{desc}" if n else "nenhuma interferência consumada (busca documentada): 0")
    return Nota("controlador", _limitar(base), comp)


# ------------------------------------------------------------------ Fisher
def fisher(respostas):
    """15 perguntas ('sim' | 'nao' | 'sem'); nota = 5 x (sim/15) com arredondamento half-up."""
    if len(respostas) != 15:
        raise ValueError(f"fisher exige exatamente 15 respostas, recebeu {len(respostas)}")
    if any(r not in ("sim", "nao", "sem") for r in respostas):
        raise ValueError("respostas devem ser 'sim', 'nao' ou 'sem'")
    n = sum(1 for r in respostas if r == "sim")
    base = math.floor(5 * n / 15 + 0.5)
    sem = sum(1 for r in respostas if r == "sem")
    return Nota("fisher", base, [f"{n} 'sim' de 15 ({sem} sem evidência): 5 x {n}/15 = {5 * n / 15:.2f} -> {base}"])


# ------------------------------------------------------------------ fechamento
def final(nota, ajuste=0, fonte="", nota_fonte=""):
    """Nota final: base +/- ajuste de 1 ponto, só com fonte nota A ou B; limitada a 0-5."""
    if ajuste not in (-1, 0, 1):
        raise ValueError("ajuste deve ser -1, 0 ou +1")
    if ajuste != 0:
        if not fonte or not fonte.strip():
            raise ValueError("ajuste exige fonte")
        if nota_fonte not in ("A", "B"):
            raise ValueError("ajuste exige fonte nota A ou B")
    return _limitar(nota.base + ajuste)


def media(moat, gestao, controlador, ciclo, fisher, discricionario):
    """Média da doutrina §10: (moat + gestão + c x controlador + ciclo + fisher) / (4 + c); c = 2 se discricionário.
    Conta única no motor (`motor_financeiras.media_qualitativa`, v2.3) — aqui só se repassa."""
    return media_qualitativa(para_qual(moat, gestao, controlador, ciclo, fisher), discricionario)


def para_qual(moat, gestao, controlador, ciclo, fisher):
    """Notas finais no formato do `QUAL` dos lotes (chaves moat, gestao, controlador, ciclo, fisher). O peso do controlador
    não vai no dict: o motor o aplica pela flag `controlador_discricionario` (v2.3; até a v2.2 a média era simples)."""
    return {"moat": moat, "gestao": gestao, "controlador": controlador, "ciclo": ciclo, "fisher": fisher}
