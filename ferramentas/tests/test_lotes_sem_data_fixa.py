"""Nenhuma data de mês/dia/trimestre no código dos lotes; anos fixos só numa catraca que cai (23/11/2026).

Origem: com o LTM do 3T26, janelas e datas escritas para o 2T26 erraram em silêncio (barril da PETR4/RECV3, índice da UNIP6/GGBR4,
trimestres da PRIO3, ações e balanço de 30/06, follow-on da EGIE3/ISAE4). Regra do Frank: a correção não pode ser outra data
digitada — sai do LTM (`ltm.py`) ou de dado com fonte (`dados/eventos_societarios.json`).
"""
import datetime as dt
import json
import pathlib
import warnings

import pytest

from tests import datas_fixas as D

CATRACA = pathlib.Path(__file__).with_name("datas_fixas_catraca.json")


def test_nenhuma_data_de_mes_dia_ou_trimestre_nos_lotes():
    zero = {f: a["zero"] for f, a in D.varrer().items() if a["zero"]}
    assert not zero, ("data fixa de mês/dia/trimestre no código dos lotes — derive do LTM (ltm.janela_ltm, data_do_balanco, "
                      f"zip_itr) ou ponha o fato com fonte em dados/: {zero}")


def test_anos_fixos_nos_lotes_so_podem_cair():
    cat = json.loads(CATRACA.read_text(encoding="utf-8"))
    limite = cat["por_arquivo"]
    atual = {f: len(a["ano"]) for f, a in D.varrer().items()}
    novos = {f: n for f, n in atual.items() if f not in limite and n}
    assert not novos, f"lote novo com ano fixo (fora da catraca): {novos}"
    subiu = {f: (limite[f], n) for f, n in atual.items() if f in limite and n > limite[f]}
    assert not subiu, f"ano fixo novo nos lotes (catraca → atual): {subiu} — derive do último DFP/LTM em vez de escrever o ano"
    caiu = {f: (limite[f], n) for f, n in atual.items() if f in limite and n < limite[f]}
    assert not caiu, f"a catraca caiu {caiu}: baixe os números em {CATRACA.name} para travar o ganho"
    if dt.date.today().isoformat() > cat["prazo"] and sum(atual.values()):
        warnings.warn(f"missão {cat['missao']}: prazo {cat['prazo']} vencido com {sum(atual.values())} anos fixos nos lotes")


@pytest.mark.parametrize("fonte, zero, ano", [
    ('x = df.loc["2025-07":"2026-06"]', 2, 0),
    ('d = "2026-06-30"', 1, 0),
    ('DATA = "02/10/2026"', 1, 0),
    ('f = dict(data="jul/2026")', 1, 0),
    ('k = "jul/25"', 1, 0),
    ('r = "3T26"', 1, 0),
    ('n = obter("lote4.acoes_jun26", [], f)', 1, 0),
    # escapes que o adversário achou na 1ª versão (23/11)
    ('d = f"{ano}-06-30"', 1, 0),
    ('d = "20260630"', 1, 0),
    ('d = "30/06/26"', 1, 0),
    ('d = "06/2026"', 1, 0),
    ('d = "2026Q2"', 1, 0),
    ('d = "precos_2026-06-30.csv"', 1, 0),
    ('x = 202606', 1, 0),
    ('d = df[df["DT_REFER"].str[5:7] == "06"]', 1, 0),
    ('d = df.query("DT_REFER == \'2026-06-30\'")', 1, 0),
    ('EGIE_DIV_AGO26 = 770_800', 1, 0),
    ('y = N.acoes_jun26', 1, 0),
    ('y = f(acoes_jun26=1)', 1, 0),
    ('t = itr_ytd(tk, 2026, 6)', 1, 0),
    ('t = date(2026, 6, 30)', 1, 0),
    ('ok = (a, m, d) < ("2025", "12", "01")', 1, 0),
    # catraca (ano de exercício)
    ('a = range(2016, 2026)', 0, 2),
    ('z = "itr_2026.zip"', 0, 1),
    ('y = "2025"', 0, 1),
    # não conta
    ('"""Docstring de 2026-06-30 e jul/2026 não conta."""\nx = 1', 0, 0),
    ('r = "prosa com jul/2026 e 2025 não conta"', 0, 0),
    ('def f():\n    """jun/2026"""\n    return 3', 0, 0),
    ('b = True; n = 1999; m = 2099', 0, 0),
    ('s = ["dataset01", "offset10", "MAR11", "reset_12", "out_24h"]', 0, 0),
    ('v = a["2.01.04"]; c = x == "01"', 0, 0),
])
def test_verificador_pega_o_que_deve_e_ignora_prosa(fonte, zero, ano):
    a = D.achados(fonte)
    assert (len(a["zero"]), len(a["ano"])) == (zero, ano), a


def test_catraca_cobre_os_lotes_que_existem():
    cat = json.loads(CATRACA.read_text(encoding="utf-8"))
    assert set(cat["por_arquivo"]) == {p.name for p in D.arquivos_dos_lotes()}
    assert set(cat["contabil_digitado"]) == {p.name for p in D.arquivos_dos_lotes()}


def test_vpa_e_lpa_digitados_so_podem_cair():
    """Oráculo de 24/11/2026: os 10 bancos e seguradoras do lote 1 avaliam com VPA/LPA do 2T26 digitados ao preço de 19/11.
    Decisão do Frank (24/11): entram na catraca de datas fixas, mesmo prazo (31/01/2027, B32); devem sair do ITR da CVM."""
    cat = json.loads(CATRACA.read_text(encoding="utf-8"))
    limite, atual = cat["contabil_digitado"], D.varrer_contabeis()
    subiu = {f: (limite.get(f, 0), n) for f, n in atual.items() if n > limite.get(f, 0)}
    assert not subiu, f"VPA/LPA digitado novo nos lotes (catraca → atual): {subiu} — leia do ITR/DFP, não digite"
    caiu = {f: (limite[f], n) for f, n in atual.items() if f in limite and n < limite[f]}
    assert not caiu, f"a catraca de VPA/LPA caiu {caiu}: baixe os números em {CATRACA.name}"
    if dt.date.today().isoformat() > cat["prazo"] and sum(atual.values()):
        warnings.warn(f"missão {cat['missao']}: prazo {cat['prazo']} vencido com {sum(atual.values())} VPA/LPA digitados nos lotes")


@pytest.mark.parametrize("fonte, n", [
    ('Financeira("X", vpa=19.75, lpa_12m=4.247)', 2),
    ('Financeira("X", vpa=v, lpa_12m=ltm["lpa"])', 0),     # vindo de dado, não conta
    ('d = dict(vpa=1)', 1),
    ('f(vpa_hist=1.0, roe_lp=0.17)', 0),
])
def test_contador_de_vpa_lpa(fonte, n):
    assert len(D.contabeis_digitados(fonte)) == n
