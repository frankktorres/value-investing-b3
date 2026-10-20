"""Fase 3, fatia 2 (20/10/2026): DPA/JCP das não financeiras do hall da API da B3 (`proventos_hall`), não da StatusInvest.

O que se prova: lista fechada de tipos (tipo novo falha alto), restituição de capital fora, data-com até a data do preço,
eventos em ações (B3 + FRE) com o provento do mesmo dia na base antiga, parcelas × repetição classificadas com prova (grupo
novo falha alto), a contagem de ações da CVM bate com os eventos, o oráculo do dossiê (HYPE3, LEVE3), e — o que permite trocar a
fonte sem `--motivo` de método — o central e a palavra não dependem do DPA.
"""
import json
import pathlib
from dataclasses import replace

import pytest

import motor_nao_financeiras as MN
import proventos_hall as ph
from lote1_bancos import MK
from relatorio import procedencia as pr

AQUI = pathlib.Path(__file__).resolve().parent.parent
CVM_ZIP = AQUI / "dados" / "cvm"
COTAHIST = AQUI / "backtest" / "dados" / "cotahist"


def _r(com, valor, tipo="DIVIDENDO", classe="ON", aprov="2025-01-02", lote=1.0):
    return dict(tipo_acao=classe, data_aprovacao=aprov, data_com=com, valor=valor, lote=lote, tipo=tipo)


def _emp(tk):
    import universo
    return next(e for _, emps, _ in universo.GRUPOS for e in emps if e.ticker == tk)


# ---------------------------------------------------------------- regras do coletor (dados sintéticos)
def test_tipo_novo_falha_alto():
    with pytest.raises(ValueError, match="fora da lista de tipos"):
        ph.dpa_jcp("TESTX3", "2026-10-02", regs=[_r("2025-05-01", 1.0, tipo="BONUS EM DINHEIRO")], ev=[], grupos={})


def test_restituicao_classe_e_data_do_preco():
    regs = [_r("2025-05-01", 1.0), _r("2025-06-01", 0.5, tipo="JRS CAP PROPRIO"), _r("2025-07-01", 9.0, tipo="REST CAP DIN"),
            _r("2025-08-01", 7.0, classe="PN"), _r("2026-10-03", 5.0), _r("2026-10-02", 0.25, tipo="RENDIMENTO"),
            _r("2015-12-30", 3.0), _r("2024-03-01", 2.0, lote=1000.0)]
    dpa, jcp = ph.dpa_jcp("TESTX3", "2026-10-02", regs=regs, ev=[], grupos={})
    # restituição de capital fora (§6.4), outra classe fora, data-com depois do preço fora, antes de 2016 fora; lote de 1.000
    assert dpa == {"2024": 0.002, "2025": 1.5, "2026": 0.25} and jcp == {"2025": 0.5}


def test_evento_divide_o_provento_ate_a_data_com_inclusive():
    ev = [{"tipo": "BONIFICACAO", "data_com": "2025-06-01", "multiplicador": 1.25},
          {"tipo": "DESDOBRAMENTO", "data_com": "2025-09-01", "multiplicador": 2.0}]
    regs = [_r("2025-05-01", 1.0), _r("2025-06-01", 1.0), _r("2025-07-01", 1.0), _r("2025-10-01", 1.0)]
    out = [p["valor_hoje"] for p in ph.proventos("TESTX3", "2026-10-02", regs=regs, ev=ev, grupos={})]
    # no mesmo dia da data-com do evento, quem recebe o provento é a ação antiga → divide
    assert out == pytest.approx([1 / 2.5, 1 / 2.5, 1 / 2.0, 1.0])


def test_linhas_iguais_parcela_soma_repeticao_sai_e_grupo_novo_falha():
    regs = [_r("2025-05-01", 0.30), _r("2025-05-01", 0.30), _r("2025-05-01", 0.301), _r("2025-08-01", 0.2, tipo="JRS CAP PROPRIO"),
            _r("2025-08-01", 0.2, tipo="JRS CAP PROPRIO"), _r("2025-09-01", 0.1), _r("2025-09-01", 0.5)]
    with pytest.raises(ValueError, match="parcela ou repetição"):
        ph.dpa_jcp("TESTX3", "2026-10-02", regs=regs, ev=[], grupos={})
    g = {("TESTX3", "2025-05-01", "DIVIDENDO"): (ph.PARCELAS, "teste"),
         ("TESTX3", "2025-08-01", "JRS CAP PROPRIO"): (ph.REPETICAO, "teste")}
    dpa, jcp = ph.dpa_jcp("TESTX3", "2026-10-02", regs=regs, ev=[], grupos=g)
    # valores distintos no mesmo dia (0,1 e 0,5) não são grupo
    assert dpa["2025"] == pytest.approx(0.30 + 0.30 + 0.301 + 0.2 + 0.1 + 0.5) and jcp["2025"] == pytest.approx(0.2)


def test_evento_das_duas_fontes_com_data_deslocada_falha(monkeypatch):
    """A B3 publicando a bonificação da Klabin de 2024 um pregão depois da data do FRE não pode entrar como 1,1 × 1,1."""
    import pandas as pd
    sup = ph.suplemento("KLBN11", ph.data_do_preco())
    extra = pd.DataFrame([{"raiz": "KLBN", "tipo": "BONIFICACAO", "fator_b3": 10.0, "data_com": "2024-05-07",
                           "data_aprovacao": "2024-04-16", "isin": "BRKLBNCDAM18"}])
    monkeypatch.setattr(ph, "suplemento", lambda tk, dp: pd.concat([sup, extra], ignore_index=True))
    with pytest.raises(ValueError, match="já está no suplemento"):
        ph.eventos("KLBN11")


# ---------------------------------------------------------------- o cache real
@pytest.mark.parametrize("tk", ph.NF_HALL)
def test_grupos_do_cache_estao_todos_classificados(tk):
    from proventos_ex import CLASSE, registros
    dp = ph.data_do_preco()
    linhas = [r for r in registros(tk, dp) if r["tipo_acao"] == CLASSE.get(tk, "ON") and ph.INICIO <= r["data_com"] <= dp
              and ph.TIPOS.get(r["tipo"])]
    achados = {(tk, *k) for k in ph.grupos_iguais(linhas)}
    declarados = {k for k in ph.GRUPOS_CONFERIDOS if k[0] == tk}
    assert achados == declarados, "grupo novo sem prova, ou classificação velha que o cache não tem mais"


def test_aplicar_registra_e_e_idempotente():
    import copy
    antes = copy.deepcopy({tk: MN.SI[tk] for tk in ph.NF_HALL})
    ph.aplicar(MN.SI)
    assert {tk: MN.SI[tk] for tk in ph.NF_HALL} == antes
    for tk in ph.NF_HALL:
        assert ph.origem(tk, MN.SI) is ph.ORIGEM_B3


def test_procedencia_proventos_B3_so_com_o_valor_registrado():
    for tk in ph.NF_HALL:
        t = pr.tabela(dict(tk=tk, empresa=_emp(tk), r=None, mk=MK, data="2026-10-02", dossie=None, financeira=False))
        assert t["proventos"].nota == "A", tk
    s = MN.SI["SUZB3"]
    guardado = s["dpa_por_ano_datacom"]
    try:
        s["dpa_por_ano_datacom"] = dict(guardado, **{"2025": guardado.get("2025", 0) + 0.01})   # mexido depois do registro
        assert pr.proventos_nf(_emp("SUZB3")).nota == "C"
    finally:
        s["dpa_por_ano_datacom"] = guardado
    assert pr.proventos_nf(replace(_emp("SUZB3"), jcp_share=0.5)).nota == "C"                     # fatia de JCP digitada


@pytest.mark.parametrize("tk", ph.NF_HALL)
def test_central_e_palavra_nao_dependem_da_fonte_do_dpa(tk):
    """O que permite a troca de fonte: com o DPA da StatusInvest no lugar do da B3, central, âncoras e palavra são os mesmos."""
    e = _emp(tk)
    antes = MN.avaliar(e, MK)
    s = MN.SI[tk]
    b3 = (s["dpa_por_ano_datacom"], s["jcp_por_ano_datacom"])
    try:
        s["dpa_por_ano_datacom"], s["jcp_por_ano_datacom"] = s["dpa_statusinvest"], s["jcp_statusinvest"]
        depois = MN.avaliar(e, MK)
    finally:
        s["dpa_por_ano_datacom"], s["jcp_por_ano_datacom"] = b3
    assert (depois["central"], depois["palavra"], depois["ancoras"]) == (antes["central"], antes["palavra"], antes["ancoras"])


def test_nenhum_evento_entre_a_data_das_acoes_e_a_do_preco():
    """As ações do lote são do DFP 2025 (lote 3/5) ou do ITR de jun/2026 (lotes 4/6): um evento em ações depois de 31/12/2025 e
    até a data do preço deixaria DPA ('por ação de hoje') e `n_acoes` em bases diferentes — falha para conferir à mão."""
    dp = ph.data_do_preco()
    tarde = [(tk, x["tipo"], x["data_com"]) for tk in ph.NF_HALL for x in ph.eventos(tk, dp) if x["data_com"] > "2025-12-31"]
    assert tarde == []


# Variação das ações do DFP sem evento por ação (sem marca E…B/G no COTAHIST no ano): emissão, incorporação, IPO, tesouraria.
SEM_EVENTO = {("KEPL3", "2021"): "ações em circulação +14% sem marca de evento (tesouraria/emissão)",
              ("FLRY3", "2022"): "incorporação do Pardini (emissão de ações)", ("FLRY3", "2023"): "idem, conclusão em 2023",
              ("PRIO3", "2021"): "desdobramento 1:5 (no suplemento) + emissão", ("PRIO3", "2023"): "sem marca; PRIO3 sem provento",
              ("PRIO3", "2022"): "ações do DFP −41% e +70% em 2023 sem marca de evento (formulário); PRIO3 sem provento",
              ("RECV3", "2021"): "desdobramento 1:2 de 01/04/2021 (FRE) antes do IPO de mai/2021 + emissão do IPO; 1º provento em "
                                 "27/04/2022", ("RECV3", "2022"): "emissão (sem marca de evento)",
              ("LEVE3", "2023"): "ações em circulação +5,6% sem marca de evento"}


@pytest.mark.parametrize("tk", ph.NF_HALL)
def test_acoes_da_cvm_conferem_com_os_eventos(tk):
    """Ano a ano, ações do DFP (CVM) ÷ ano anterior ≈ produto dos eventos do ano. Sobra > 3% = evento que falta (a bonificação
    de 10% da Klabin em 2024 não está na B3 nem na tabela de desdobramento do FRE e apareceu aqui); < 0,92 = evento a mais ou
    contado duas vezes, ou grupamento que falta (a maior recompra medida é a B3SA3 2024, 0,938 — adversário, 20/10).
    Limite declarado: evento com data-com no 1º ano da série (SMTO3 2016) ou em ano sem contagem de ações (SLCE3 2016–19) só é
    conferido pelo teste local de FRE/COTAHIST ou pelo suplemento da B3."""
    a = json.loads((AQUI / "dados" / "cvm_series.json").read_text(encoding="utf-8"))[tk]["anual"]
    ev = ph.eventos(tk)
    anos = sorted(y for y in a if "2016" <= y <= "2025" and a[y].get("acoes"))
    ruins = []
    for y0, y1 in zip(anos, anos[1:]):
        k = a[y1]["acoes"] / a[y0]["acoes"]
        k = k / 1000 if k > 500 else (k * 1000 if k < 0.002 else k)       # formulário em milhares num dos anos
        esp = 1.0
        for x in ev:
            if f"{y0}-12-31" < x["data_com"] <= f"{y1}-12-31":
                esp *= x["multiplicador"]
        if (k / esp > 1.03 or k / esp < 0.92) and (tk, y1) not in SEM_EVENTO:
            ruins.append((y1, round(k, 4), round(esp, 4)))
    assert ruins == []


# ---------------------------------------------------------------- conferências locais (precisam dos ZIPs / COTAHIST)
def _marcas(tk, anos):
    import pandas as pd
    out = []
    for a in anos:
        p = pd.read_parquet(COTAHIST / f"precos_{a}.parquet", columns=["data", "ticker", "codbdi", "especi"])
        out.append(p[(p["ticker"] == tk) & (p["codbdi"] == "02")])
    p = pd.concat(out).sort_values("data")
    m = p["especi"].str.split().str[1].fillna("")
    ev = m.str.startswith("E") & (m.str.contains("B") | m.str.contains("G"))
    ini = ev & ~ev.shift(1, fill_value=False)
    datas = p["data"].astype(str).str[:10].tolist()
    return {datas[i - 1]: datas[i] for i, x in enumerate(ini.tolist()) if x and i}      # data-com → 1º dia com a marca


@pytest.mark.skipif(not (CVM_ZIP / "fre_2023.zip").exists() or not (COTAHIST / "precos_2024.parquet").exists(),
                    reason="sem os ZIPs do FRE ou o COTAHIST (dados locais)")
def test_eventos_fre_conferem_no_fre_e_no_cotahist():
    from backtest.precos.eventos import eventos_fre
    from backtest.ledger.identidade import mapa_ticker_cnpj, tickers_do_cnpj
    cnpj = {t: c for c, ts in tickers_do_cnpj(mapa_ticker_cnpj()).items() for t in ts}
    fre = eventos_fre()
    for tk, evs in ph.EVENTOS_FRE.items():
        anos = sorted({int(x["data_com"][:4]) for x in evs} | {int(x["data_com"][:4]) + 1 for x in evs})
        marcas = _marcas(tk, [a for a in anos if (COTAHIST / f"precos_{a}.parquet").exists()])
        for x in evs:
            assert x["data_com"] in marcas, (tk, x["data_com"], "data-com não é o pregão antes da marca E…B no COTAHIST")
            if tk == "KLBN11":
                continue                         # razão do capital integralizado (a tabela de desdobramento some em 2024)
            f = fre[(fre["cnpj"] == cnpj[tk]) & (fre["aprovacao"] == x["aprovacao"]) & (fre["tipo"] == x["tipo"])]
            assert len(f) == 1, (tk, x)
            assert abs(float(f["f_total"].iloc[0]) / x["multiplicador"] - 1) < 1e-3, (tk, x, float(f["f_total"].iloc[0]))


@pytest.mark.skipif(not (CVM_ZIP / "fre_2023.zip").exists(), reason="sem os ZIPs do FRE (dados locais)")
def test_bonificacao_klabin_2024_no_capital_integralizado():
    import io
    import zipfile
    import pandas as pd

    def total(ano):
        z = zipfile.ZipFile(CVM_ZIP / f"fre_{ano}.zip")
        d = pd.read_csv(io.BytesIO(z.read(f"fre_cia_aberta_capital_social_{ano}.csv")), sep=";", encoding="latin-1", dtype=str)
        d = d[(d["CNPJ_Companhia"] == "89.637.490/0001-45") & (d["Tipo_Capital"] == "Capital Integralizado")]
        return float(d.sort_values("Versao", key=lambda s: s.astype(int)).iloc[-1]["Quantidade_Total_Acoes"])
    assert total(2023) / total(2022) == pytest.approx(1.1, abs=1e-6)


@pytest.mark.skipif(not (COTAHIST / "precos_2023.parquet").exists(), reason="sem o COTAHIST (dado local)")
def test_sem_evento_declarado_nao_tem_marca_no_cotahist():
    for (tk, ano), _ in SEM_EVENTO.items():
        if tk in ("PRIO3", "RECV3") and ano == "2021":
            continue                                   # PRIO3: desdobramento no suplemento; RECV3: ainda não listada
        conhecidos = {x["data_com"] for x in ph.eventos(tk)}
        assert set(_marcas(tk, [int(ano)])) <= conhecidos, (tk, ano)     # só a marca dos eventos já contados (FLRY3 2023)


@pytest.mark.skipif(not (AQUI / "backtest" / "dados" / "proventos" / "dinheiro").exists(),
                    reason="sem o cache de proventos do backtest (dado local)")
@pytest.mark.parametrize("tk", ["HYPE3", "LEVE3"])
def test_oraculo_igual_ao_dossie(tk):
    """O coletor do hall e `dossie.base.proventos_b3` (outro cache, outro código) dão o mesmo DPA/JCP de 2016 a 2025. Única
    diferença conhecida: o dossiê soma a restituição de capital da HYPE3 de 2017 (R$ 1,30, fatia 2b)."""
    from dossie.base import proventos_b3
    dpa_d, jcp_d = proventos_b3(tk)
    dpa_h, jcp_h = ph.dpa_jcp(tk)
    conhecida = {("HYPE3", "2017"): 1.300515236}
    for a in map(str, range(2016, 2026)):
        assert dpa_h.get(a, 0) + conhecida.get((tk, a), 0) == pytest.approx(dpa_d.get(a, 0), abs=1e-9), (tk, a)
        assert jcp_h.get(a, 0) == pytest.approx(jcp_d.get(a, 0), abs=1e-9), (tk, a)
