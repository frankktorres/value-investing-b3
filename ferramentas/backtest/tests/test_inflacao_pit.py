"""O índice de IPCA do backtest: point-in-time, e conferido contra o da mesa.

O isolamento por AST (test_isolamento) impede o backtest de usar `ferramentas/inflacao.py`, o que
cria DUAS implementações do mesmo índice lendo o mesmo arquivo. Sem conferência cruzada, um erro de
acumulação em qualquer das duas passaria calado e contaminaria tudo que vem depois.

A conferência: no último mês comum, o índice acumulado tem de COINCIDIR. A fonte é a mesma (SGS
433); o que difere é só o truncamento. Se divergirem, é bug de acumulação, não diferença de método.
"""
from __future__ import annotations

import pytest

from backtest import inflacao_pit as pit
from backtest.calendario import mes_ipca_disponivel
from backtest.config import PADRAO, limite_liquidez


def test_confere_com_o_indice_da_mesa_no_ultimo_mes_comum() -> None:
    """Mesma fonte, mesma acumulação: as razões entre meses têm de ser idênticas."""
    import inflacao

    primeiro, ultimo = pit.cobertura()
    assert inflacao.DATA_BASE.endswith(ultimo[:4]), \
        f"séries em anos diferentes: mesa {inflacao.DATA_BASE}, backtest {ultimo}"

    # Razão entre dois meses quaisquer: imune à base arbitrária de cada implementação.
    for de, para in (("1995-01", "2005-01"), ("2010-06", "2020-06"), ("2014-05", ultimo)):
        n_de = int(de[:4]) * 12 + int(de[5:]) - 1
        n_para = int(para[:4]) * 12 + int(para[5:]) - 1
        mesa = inflacao._INDICE[n_para] / inflacao._INDICE[n_de]
        meu = pit.fator_mes(de, para, ultimo)
        assert meu == pytest.approx(mesa, rel=1e-12), \
            f"índice divergiu entre {de} e {para}: mesa {mesa}, backtest {meu}"


def test_media_do_exercicio_confere_quando_o_ano_ja_fechou() -> None:
    """Para exercício inteiramente passado, a média do backtest = MEDIA_ANO da mesa (12 meses)."""
    import inflacao

    _, ultimo = pit.cobertura()
    for ano in (1999, 2008, 2014, 2020, 2024):
        assert pit.media_ano(ano, ultimo) == pytest.approx(inflacao.MEDIA_ANO[ano], rel=1e-12)


# ------------------------------------------------------------------------- o que torna PIT
def test_pedir_mes_futuro_levanta_em_vez_de_devolver_o_extremo() -> None:
    """A mesa satura no extremo da série em silêncio; aqui olhar para frente é erro."""
    with pytest.raises(ValueError, match="não era público"):
        pit.indice_mes("2020-12", "2020-05")


def test_media_do_ano_do_corte_e_parcial() -> None:
    """Em T = 30/06/2020 conhece-se jan–mai/2020, não o ano inteiro."""
    import inflacao

    parcial = pit.media_ano(2020, "2020-05")
    cheia = inflacao.MEDIA_ANO[2020]
    assert parcial != pytest.approx(cheia), \
        "a média do ano do corte tem de ser parcial; se coincidir, o truncamento não está agindo"
    assert parcial < cheia, "com inflação positiva no ano, a média parcial do início é menor"


def test_ipca_disponivel_e_sempre_o_mes_anterior_ao_corte() -> None:
    for d in PADRAO.datas_corte:
        m = mes_ipca_disponivel(d)
        assert m < d[:7], f"{d}: IPCA de {m} não seria público (sai ~dia 10 do mês seguinte)"


# ------------------------------------------------------------------- o limite real de liquidez
def test_limite_de_liquidez_cresce_e_tem_base_estavel() -> None:
    """A base é um MÊS fixo (2014-05), então o limite é monotônico e a régua é a mesma em todo corte."""
    limites = [limite_liquidez(PADRAO, d) for d in PADRAO.datas_corte]
    assert limites == sorted(limites), f"limite real tem de crescer com a inflação: {limites}"
    assert limites[0] == pytest.approx(PADRAO.liquidez_min_base, rel=1e-6), \
        "no primeiro corte o limite é o próprio valor declarado"
    assert limites[-1] / limites[0] == pytest.approx(1.84, abs=0.05), \
        "IPCA acumulado de 2014-05 a 2025-11 é ~84%"


def test_limite_de_liquidez_nao_depende_de_quando_foi_calculado() -> None:
    """Regressão do bug que a base ANUAL tinha: o denominador mudava com a data do corte."""
    base = PADRAO.liquidez_mes_base
    for corte in ("2014-05", "2016-05", "2025-11"):
        assert pit.indice_mes(base, corte) == pytest.approx(
            pit.indice_mes(base, "2025-11"), rel=1e-12), \
            "o índice do mês-âncora é um número fixo; se variar com o corte, a base não é estável"
