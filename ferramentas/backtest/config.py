"""Parâmetros CONGELADOS do backtest — a trava anti-sobreajuste.

Nenhuma constante do experimento mora solta no código: tudo passa por aqui, e `hash_config()` vai
impresso no PDF. Mudar qualquer número muda o hash, então uma conclusão publicada fica amarrada à
configuração que a produziu. Calibrar a régua até ela "acertar" o passado é o risco #5 do
PLANO-DE-MELHORIAS-2026-10.md; esta é a defesa mecânica contra ele.

Decisões do Frank em 06/10/2026 (plan mode da Etapa 3):
  universo = espinha COTAHIST · safras de janela curta em coorte estratificado ·
  portão de proxy declarado antes de medir, com "parar e reportar" se falhar.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field

# 30/06 e 31/12 de 2014 a 2025 — as 24 datas pedidas pela F3. A data de corte é nominal; o pregão
# efetivo (último <= T) sai de calendario.ultimo_pregao_ate.
DATAS_CORTE: tuple[str, ...] = tuple(
    f"{ano}-{mes}" for ano in range(2014, 2026) for mes in ("06-30", "12-31")
)

# Exercícios anuais publicados em cada corte, dado que o dado estruturado da CVM começa em 2010
# (DFP) e a DFP do exercício Y chega em ~mar/Y+1. Conferido na fonte em 06/10/2026.
# Consequência que manda no desenho: a doutrina §11.4 exige janela de 10 exercícios, e o estrato
# n=10 só existe de 2020-06 em diante — 12 dos 24 cortes, e só 2 deles (2020-06, 2020-12) caem na
# janela de calibração. Ver ESTRATO_RECOMENDACAO.
EXERCICIOS_POR_CORTE: dict[str, int] = {
    d: min(10, int(d[:4]) - 1 - 2010 + 1) for d in DATAS_CORTE
}


@dataclass(frozen=True)
class Config:
    # ---- grade do experimento
    datas_corte: tuple[str, ...] = DATAS_CORTE
    horizontes_anos: tuple[int, ...] = (1, 3, 5)
    premios: tuple[float, ...] = (0.03, 0.04, 0.05, 0.06)      # prêmio do Ke; 0,05 é a régua da casa
    compras: tuple[float, ...] = (0.60, 0.70, 0.80)            # múltiplo do central que autoriza compra
    # §9 v2.2 tem DUAS réguas de saída: 1,30× padrão e 1,50× na exceção de qualidade (ROIC real >
    # WACC real a custo de reposição em >= 8 exercícios, janela >= 10, nota de Qualidade >= 8).
    # Hoje só a LEVE3 qualifica, e por 0,005 de nota — o backtest é a única evidência que pode
    # existir sobre se a exceção ajuda ou atrapalha. Medir as duas lado a lado.
    saidas: tuple[float, ...] = (1.30, 1.50)
    exc_qualidade_anos_roic: int = 8
    exc_qualidade_janela_min: int = 10
    exc_qualidade_nota_min: float = 8.0

    # ---- régua (§9 e §11.3). Reimplementada, não reinventada: o portão da fatia 11 exige que
    # estes números reproduzam palavra e central dos 41 tickers de tests/golden.json.
    palavra_barata: float = 0.70
    palavra_radar: float = 0.90
    palavra_justa: float = 1.10
    disp_desce: float = 1.80            # dispersão acima disso desce um nível
    disp_inconclusivo: float = 3.00     # acima disso não emite palavra

    # ---- janela do ciclo (§11.4)
    janela_max: int = 10
    janela_min: int = 5                 # filtro de entrada; as safras de n=4 vão a coorte separado
    quebra_limite: float = 0.25         # mede e sinaliza, NUNCA troca a janela sozinha

    # ---- filtro de liquidez, em R$ REAIS (ver nota longa abaixo)
    liquidez_min_base: float = 500_000.0
    # MÊS-âncora declarado, não ano: a média do exercício é truncada no corte, então "R$ de 2014"
    # vale 1,55% diferente visto de 2014-05 e de 2016-05, e a base do filtro de universo tem de
    # ser a mesma régua nos 24 cortes. 2014-05 é o último mês de IPCA público no primeiro corte.
    liquidez_mes_base: str = "2014-05"
    liquidez_pregoes: int = 60
    reportar_liquidez_nominal: bool = True

    # ---- preços e eventos
    salto_bloqueio: float = 0.20        # |retorno diário| sem provento conhecido levanta suspeita
    proporcoes_evento: tuple[float, ...] = (2, 3, 4, 5, 10, 0.5, 1 / 3, 0.25, 0.2, 0.1)
    tolerancia_proporcao: float = 0.02
    # Bonificações usuais na B3 (multiplicador de ações), para inferir o fator onde o COTAHIST marca
    # o ex (EB) e nem o FRE nem a B3 trazem o número. Declarada em 06/10/2026, antes de medir.
    bonificacoes_grade: tuple[float, ...] = (1.02, 1.03, 1.05, 1.10, 1.15, 1.20, 1.25, 1.30, 1.50)
    # Proventos entram BRUTOS no retorno total: é a convenção do Ibovespa, o benchmark. O JCP paga
    # 15% de IR na fonte para a pessoa física; a variante líquida sai como coluna, não como regra.
    proventos_brutos: bool = True
    jcp_ir: float = 0.15
    regra_deslistagem: str = "ibov"     # primária; "truncado" e "falencia" entram como robustez

    # ---- contaminação por reapresentação (escada do plano, §Fatia 6)
    regra_contaminacao: str = "A+B"     # A exclui ticker-data contaminado, B inclui com flag
    contaminacao_tolerancia: float = 0.02

    # ---- divisão calibração / validação
    janela_calibracao: tuple[str, str] = ("2014-01-01", "2020-12-31")
    janela_validacao: tuple[str, str] = ("2021-01-01", "2025-12-31")

    # ---- portão do erro de proxy (fatia 12). Declarado ANTES de medir.
    proxy_concordancia_min: float = 0.80    # palavra exata ou dentro de um nível, nos 41 do golden
    proxy_delta_pc_max: float = 0.15        # mediana de |ΔP/C|

    # ---- estatística
    semente: int = 20261006
    bootstrap_n: int = 2000
    permutacao_n: int = 10000
    ic: float = 0.90                    # 90%, não 95%: menos falsa precisão com n pequeno
    n_datas_min_para_ic: int = 4        # célula abaixo disso sai sem intervalo de confiança
    estratos: tuple[tuple[int, int], ...] = ((4, 4), (5, 6), (7, 9), (10, 10))

    # ---- âncoras do motor reduzido, por perfil
    ancoras_nao_financeira: tuple[str, ...] = (
        "EPV de meio de ciclo", "Owner Earnings capitalizado", "Valor de reprodução")
    ancoras_financeira: tuple[str, ...] = (
        "P/VP justificado", "DDM 2 estágios", "Lucro normalizado capitalizado")

    # ---- defaults congelados a priori, iguais para todos (risco #12 do plano)
    spread_kd: float = 0.02
    aliquota_efetiva_fallback: float = 0.34
    pib_real_lp: float = 0.02
    notas: tuple[str, ...] = field(default=(), repr=False)


# ---------------------------------------------------------------------------- liquidez em R$ reais
# Por que o limite de liquidez NÃO é nominal: R$ 500 mil/dia em 2014 é um filtro muito mais
# apertado do que R$ 500 mil/dia em 2025 (o IPCA quase dobrou no período). Um corte nominal fixo
# enxuga o universo das safras antigas em direção a empresa grande — justamente as safras de queda
# do Ibovespa que o coorte estratificado quer preservar. É o mesmo viés de inflação que a Etapa 2
# corrigiu no capex de manutenção (D9: Δreceita REAL, não nominal).
#
# O limite é declarado em R$ do MÊS-âncora e convertido para cada data de corte por
# inflacao_pit.fator_mes, que usa só meses de IPCA já públicos em T. O mês-âncora é 2014-05 — o
# último mês público no PRIMEIRO corte, não hoje: assim a conversão nunca precisa de inflação
# posterior à data, e a base é a MESMA nos 24 cortes.
#
# Deliberadamente NÃO se usa nada de `ferramentas/inflacao.py` — nem `fator_entre`. Aquele módulo
# deriva tudo do último mês da série (DEFLATOR, indice_ha, reposicao) e até o MEDIA_ANO que o
# fator_entre usa é a média dos 12 meses do ano; em T = 30/06/2020 isso é meio ano de inflação que
# ninguém conhecia. Ver backtest/inflacao_pit.py, que lê a MESMA fonte A (SGS 433) e trunca em T.
#
# O PDF reporta o tamanho do universo por data com os dois filtros (real e nominal plano): a
# diferença entre eles é um achado em si, não um detalhe de implementação.

def limite_liquidez(cfg: Config, data_corte: str) -> float:
    """Limite de liquidez em R$ nominais da data de corte, convertido só com IPCA <= T."""
    from .calendario import mes_ipca_disponivel
    from .inflacao_pit import fator_mes
    corte_mes = mes_ipca_disponivel(data_corte)
    return cfg.liquidez_min_base * fator_mes(cfg.liquidez_mes_base, corte_mes, corte_mes)


# ------------------------------------------------------------------- estrato que embasa a decisão
# A doutrina §11.4 manda janela de 10 exercícios, então o número que embasa recalibrar o prêmio ou
# a margem tem de vir do estrato n=10 — misturar centrais calculados com 4 e com 10 exercícios
# responde a pergunta errada.
#
# Mas n=10 só existe de 2020-06 em diante: 12 dos 24 cortes, e só 2 deles (2020-06 e 2020-12) caem
# na janela de calibração. A 5 anos, n=10 tem EXATAMENTE esses 2 cortes. Consequências, declaradas
# antes de medir:
#   · a recomendação sai de n=10 no horizonte de 1 ANO (12 cortes, ~6 blocos independentes), e a
#     estatística principal é o teste de permutação DENTRO da data de corte, que controla o retorno
#     do mercado e não supõe independência entre datas;
#   · n=10 a 3 anos entra como direção, a 5 anos NÃO entra (2 cortes = nenhum poder);
#   · n>=7 nos três horizontes entra como teste de amplitude, porque é o estrato mais alto que
#     atravessa as duas janelas (de 2017-06 em diante, 18 cortes);
#   · para o estrato n=10 a divisão calibração/validação praticamente NÃO EXISTE (10 dos 12 cortes
#     estão na validação). O PDF diz isso em caixa: o fora-da-amostra da doutrina-fiel é fraco, e
#     essa é uma limitação do dado disponível, não uma escolha de método.
#
# ASSIMETRIA QUE VAI IMPRESSA AO LADO DA RECOMENDAÇÃO. Sem fora-da-amostra, o estrato doutrina-fiel
# pode REFUTAR a régua, não VALIDÁ-LA:
#   · se a BARATA perder para a CARA, para o Ibovespa ou para o Tesouro IPCA+ mesmo DENTRO da
#     amostra, isso é condenatório e basta para mexer na doutrina;
#   · se a BARATA ganhar, não é evidência de que ganharia fora da amostra, e portanto NÃO sustenta
#     sozinho recalibrar o prêmio de 5 p.p. nem a margem de 30%.
# Sem essa frase ao lado do número, um resultado in-sample daqui a seis meses é lido como prova.
ASSIMETRIA_REFUTA_VALIDA = (
    "O estrato n=10 (a janela que a doutrina §11.4 manda) vive 10 dos 12 cortes dentro da janela "
    "de validação, então para ele não há fora-da-amostra. Consequência lógica: este backtest pode "
    "REFUTAR a régua, não validá-la. Resultado ruim dentro da amostra é condenatório e basta para "
    "mexer na doutrina; resultado bom não sustenta sozinho recalibrar o prêmio nem a margem."
)
ESTRATO_RECOMENDACAO = {
    "estrato": (10, 10),
    "horizonte_decisao": 1,
    "horizonte_direcao": 3,
    "horizontes_sem_poder": (5,),
    "estrato_amplitude": (7, 9),
    "cortes_n10": tuple(d for d, n in EXERCICIOS_POR_CORTE.items() if n == 10),
    "cortes_n10_na_calibracao": tuple(
        d for d, n in EXERCICIOS_POR_CORTE.items() if n == 10 and d < "2021-01-01"),
}


def hash_config(cfg: Config) -> str:
    """Hash estável da configuração; vai impresso no PDF e no painel."""
    bruto = json.dumps(asdict(cfg), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(bruto.encode("utf-8")).hexdigest()[:16]


PADRAO = Config()

if __name__ == "__main__":
    print(f"hash: {hash_config(PADRAO)}")
    print(f"{len(PADRAO.datas_corte)} datas de corte: {PADRAO.datas_corte[0]} .. {PADRAO.datas_corte[-1]}")
    for lo, hi in PADRAO.estratos:
        ds = [d for d, n in EXERCICIOS_POR_CORTE.items() if lo <= n <= hi]
        calib = [d for d in ds if d < PADRAO.janela_validacao[0]]
        print(f"  estrato n={lo}-{hi}: {len(ds)} cortes ({len(calib)} na calibração)")
