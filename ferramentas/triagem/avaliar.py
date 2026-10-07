"""Uma companhia em T: ledger -> exclusões pós-ledger -> central rápido (motor reduzido) -> Q1..Q5.

O central rápido é o do motor reduzido da Etapa 3, com o erro MEDIDO declarado (mediana |ΔP/C| 0,34
nos 41 do golden). Daqui sai só o número (central, P/C, dispersão); **a palavra do `Veredito` nunca
é lida** — a triagem não dá veredito.
"""
from __future__ import annotations

import dataclasses
import math

import pandas as pd

from backtest.calendario import Calendario
from backtest.config import PADRAO as BT
from backtest.inflacao_pit import fator_mes
from backtest.ledger.pit import FINANCEIRO, INDUSTRIAL, LedgerPIT, ledger_em
from backtest.mercado_bt import MercadoBT
from backtest.motor import base, reduzido, reduzido_nf
from backtest.motor.base import INICIO_EVENTOS, lucro_controlador, mediana
from backtest.motor.perfil import HOLDING, SERVICOS, UTILITY, perfil_em, setor_chave
from backtest.precos.eventos import fator_entre
from backtest.precos.retorno import preco_de_corte

from . import qualidade as Q
from .config import PADRAO, ConfigTriagem

SEM_DFP, JANELA_CURTA, DFP_ATRASADO, SEM_LUCRO = (
    "sem DFP na CVM", "menos de 7 exercícios", "último DFP atrasado", "setor a evitar (§8)")
DIAS_PRECO_D0 = 31        # preço do início da janela do Q4 a no máximo 1 mês de D0


def mercado(data: str, cfg: ConfigTriagem = PADRAO) -> MercadoBT:
    return MercadoBT(data, cfg.rf_real, cfg.pi, cfg.premio, titulo_rf=cfg.titulo_rf,
                     fonte=f"mesmos do hall ({cfg.data_mercado})")


def balanco_de(l: LedgerPIT) -> dict:
    """Último balanço visível: ITR se mais novo que o DFP (mesma regra de base.montar)."""
    if l.ultimo_itr is not None and l.ultimo_itr.dt_refer > l.anuais[-1].dt_refer:
        return dict(l.ultimo_itr.contas)
    return dict(l.anuais[-1].contas)


def _dias(a: str, b: str) -> int:
    return abs((pd.Timestamp(a) - pd.Timestamp(b)).days)


def avaliar(lin: dict, T: str, mk: MercadoBT, precos: pd.DataFrame, cal: Calendario,
            eventos: pd.DataFrame, cfg: ConfigTriagem = PADRAO, *, ledger_fn=ledger_em,
            perfil_fn=perfil_em, montar_fn=base.montar) -> dict:
    """Linha completa da companhia. Os keywords existem para o teste injetar ledger/perfil/insumos."""
    out = dict(lin)
    tk, cnpj, cd = lin["ticker"], lin["cnpj"], int(lin["cd_cvm"])
    preco, dia = preco_de_corte(precos, tk, T, cal)
    out.update(preco=preco, data_preco=dia, central=math.nan, pc=math.nan, dispersao=math.nan,
               confiavel=False, sem_central="", wacc_real=math.nan, ey=math.nan,
               ncav_pa=math.nan, netnet=False, var_acoes=math.nan, passa=False, q={},
               ciclicidade_diverge=False, perfil="", plano="", n_exercicios=0, ultimo_dfp="")

    p = perfil_fn(cd, T)
    sem_central = ""
    if p.motivo_exclusao:                         # sem setor ou holding: qualidade sim, central não
        sem_central = p.motivo_exclusao
        p = dataclasses.replace(p, perfil=SERVICOS if p.perfil in ("", HOLDING) else p.perfil,
                                motivo_exclusao="")
    financeira = p.plano == "financeiro"
    out.update(perfil=p.perfil, plano=p.plano)

    l = ledger_fn(cd, T, FINANCEIRO if financeira else INDUSTRIAL)
    if l is None or not l.anuais:
        out["motivo"] = SEM_DFP
        return out
    out.update(n_exercicios=l.n_exercicios, ultimo_dfp=l.anuais[-1].dt_refer)
    if l.n_exercicios < cfg.min_exercicios:
        out.update(motivo=JANELA_CURTA, detalhe=f"{l.n_exercicios} exercícios")
        return out
    if l.anuais[-1].ano < int(T[:4]) - 1:
        out.update(motivo=DFP_ATRASADO, detalhe=f"último DFP {l.anuais[-1].dt_refer}")
        return out

    i = montar_fn(cd, tk, cnpj, T, eventos, BT, perfil=p, ledger=l)
    anos = i.anos if not i.excluido else tuple(
        base._ano(e, int(T[:4]), l.mes_ipca, BT) for e in l.anuais)
    if setor_chave(p.setor) in cfg.setores_sem_lucro:
        if not (mediana(lucro_controlador(a.contas) for a in anos) > 0):
            out.update(motivo=SEM_LUCRO, detalhe="§8: tecnologia sem lucro (lucro mediano <= 0)")
            return out
    if i.excluido:
        sem_central = sem_central or i.motivo_exclusao
    if not math.isfinite(preco):
        sem_central = sem_central or "sem preço em T"

    # ---- central rápido (número, nunca a palavra) e WACC para o Q1
    wacc = math.nan
    if not i.excluido and math.isfinite(preco):
        if not sem_central:
            r = reduzido.avaliar(i, mk, preco, BT)
            if r.motivo_exclusao or r.veredito is None:
                sem_central = r.motivo_exclusao or "sem veredito do motor"
            else:
                v = r.veredito
                vals = list(r.ancoras.values())
                out.update(central=v.central, pc=v.pc, dispersao=v.dispersao,
                           ancoras={k: round(x, 2) for k, x in r.ancoras.items()},
                           confiavel=(v.central > 0 and all(x > 0 for x in vals)
                                      and v.dispersao <= cfg.disp_confiavel),
                           ciclicidade_diverge=bool(r.premissas.get("ciclicidade_diverge")))
                wacc = r.premissas.get("wacc_real", math.nan)
        if not financeira and not math.isfinite(wacc):
            # utility vai ao motor financeiro; holding/sem setor não roda o motor: WACC pelo nf
            wacc = reduzido_nf.ancoras(i, mk, preco, BT)[1].get("wacc_real", math.nan)
    out["wacc_real"] = wacc

    # ---- qualidade
    q: dict[str, Q.Teste] = {}
    if financeira:
        q["Q1"] = Q.q1(Q.roe_reais(anos, l.mes_ipca), mk.ke_real, "Ke", cfg)
        q["Q2"] = Q.Teste(Q.NA, "financeira: sem FCO comparável")
        q["Q3"] = Q.Teste(Q.NA, "financeira: dívida é matéria-prima")
    else:
        barreira, nome = (wacc, "WACC") if math.isfinite(wacc) else (mk.ke_real, "Ke (sem WACC)")
        q["Q1"] = Q.q1(Q.roic_reais(anos, l.mes_ipca), barreira, nome, cfg)
        q["Q2"] = Q.q2(anos, cfg)
        q["Q3"] = Q.q3(balanco_de(l), anos[-1], cfg)
    q["Q4"] = _q4(i, l, tk, T, preco, precos, cal, eventos, financeira, ledger_fn, out, cfg)
    q["Q5"] = Q.q5(anos, cfg)
    out["q"] = q
    out["quebra"] = quebra_estrutural(l, out["var_acoes"], cfg)
    out["passa"] = Q.portao(q, cfg) and not out["quebra"]

    if not i.excluido and not financeira and math.isfinite(preco):
        out["ey"] = Q.ey(i, preco)
        n = Q.ncav_por_acao(i)
        out["ncav_pa"] = n
        out["netnet"] = bool(math.isfinite(n) and n > 0 and preco <= cfg.netnet_fracao * n)
    out["sem_central"] = sem_central
    out["utility"] = p.perfil == UTILITY
    return out


def preco_na_cadeia(precos, cadeia: list[str], data: str, cal) -> tuple[float, str]:
    """Último PREULT <= data no papel da cadeia de sucessão que negociava então (o mais novo
    primeiro: o antigo só responde antes da troca de código)."""
    for t in reversed(cadeia):
        p, dia = preco_de_corte(precos, t, data, cal)
        if dia:
            return p, dia
    return math.nan, ""


def fator_na_cadeia(eventos, cadeia: list[str], de: str, ate: str) -> float:
    """Produto dos fatores de evento em (de, ate] em todos os códigos da cadeia (cada código só
    tem eventos enquanto negociou; a troca de código é contínua no preço, ver espinha.sucessoes)."""
    f = 1.0
    for t in cadeia:
        f *= fator_entre(eventos, t, de, ate)
    return f


def _q4(i, l, tk, T, preco, precos, cal, eventos, financeira, ledger_fn, out, cfg) -> Q.Teste:
    if i.excluido or not math.isfinite(preco):
        return Q.Teste(Q.INDET, "sem contagem de ações ou preço em T")
    cadeia = list(out.get("cadeia") or [tk])
    # D0 = fim do 1º exercício com preço a <= 1 mês (IPO no meio da janela empurra o início)
    k, p0, d0 = 0, None, i.anos[0].dt_refer
    for k, a in enumerate(i.anos):
        p, dia = preco_na_cadeia(precos, cadeia, a.dt_refer, cal)
        if dia and _dias(dia, a.dt_refer) <= DIAS_PRECO_D0:
            p0, d0 = p, a.dt_refer
            break
    else:
        return Q.Teste(Q.INDET, "sem preço no fim de nenhum exercício da janela")
    fator = fator_na_cadeia(eventos, cadeia, d0, T)
    infl = fator_mes(d0[:7], l.mes_ipca, l.mes_ipca)
    # variação de ações na janela (emissão/recompra que o Q4 ignora): FRE visto em D0
    l0 = ledger_fn(i.cd_cvm, d0, FINANCEIRO if financeira else INDUSTRIAL)
    if l0 is not None and l0.acoes and not l0.acoes_ambiguo and l0.acoes_aprovacao and i.por_papel:
        ini0 = max(l0.acoes_aprovacao, l0.acoes_dt_receb)
        if INICIO_EVENTOS <= ini0 <= d0:
            f0 = fator_na_cadeia(eventos, cadeia, ini0, d0)
            if math.isfinite(f0) and f0 > 0 and math.isfinite(fator) and fator > 0:
                # papéis de D0 expressos na base de hoje (× fator D0->T) contra os papéis de T
                papeis_d0 = l0.acoes * f0 / i.por_papel * fator
                out["var_acoes"] = i.papeis / papeis_d0 - 1
                return Q.q4(i, preco, p0, fator, infl, k, cfg, papeis_d0=papeis_d0)
    return Q.q4(i, preco, p0, fator, infl, k, cfg)


def quebra_estrutural(l: LedgerPIT, var_acoes: float, cfg: ConfigTriagem = PADRAO) -> str:
    """Incorporação/fusão depois do último DFP: os exercícios medem OUTRA empresa (SAUD3 em 2026:
    DFPs da Odontoprev, ITR e FRE da companhia fundida). '' se não há sinal."""
    if isinstance(var_acoes, float) and math.isfinite(var_acoes) and abs(var_acoes) > cfg.quebra_var_acoes:
        return (f"base de ações {var_acoes:+.0%} na janela (emissão, incorporação ou evento sem "
                "fator: o histórico por ação não compara)")
    itr = l.ultimo_itr
    if itr is not None and itr.dt_refer > l.anuais[-1].dt_refer:
        a_itr, a_dfp = itr.contas.get("ativo"), l.anuais[-1].contas.get("ativo")
        if a_itr and a_dfp and a_dfp > 0 and a_itr / a_dfp > cfg.quebra_ativo:
            return f"ativo do ITR {itr.dt_refer} = {a_itr / a_dfp:.1f}× o do último DFP"
    return ""
