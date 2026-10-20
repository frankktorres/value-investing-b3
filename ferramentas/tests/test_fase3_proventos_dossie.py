"""Fase 3, fatia 2b (20/10/2026): o DPA/JCP do dossiê (`dossie.base.proventos_b3`) com as regras do coletor do hall.

O que se prova: (a) a classe do ticker (FESA4/SHUL4 são PN; antes filtrava ON fixo); (b) linhas iguais da B3 = parcelas que
somam, salvo repetição conferida na DMPL — os grupos dos 8 dossiês estão todos classificados; (c) restituição de capital fora
(§6.4); (d) os eventos em ações que a B3 omite e o FRE traz (SHUL4 2018 e 2021) entram no DPA e na diluição; a contagem de
ações da CVM dos dossiês confere com os eventos.
"""
import io
import json
import pathlib
import zipfile

import pytest

import proventos_hall as ph
from dossie import base
from proventos_ex import registros

AQUI = pathlib.Path(__file__).resolve().parent.parent
CVM_ZIP = AQUI / "dados" / "cvm"
DOSSIES = ph.DOSSIES + ("HYPE3", "LEVE3")


def _r(com, valor, tipo="DIVIDENDO", classe="ON"):
    return dict(tipo_acao=classe, data_aprovacao="2025-01-02", data_com=com, valor=valor, lote=1.0, tipo=tipo)


def _cache(tk):
    return json.loads((ph.PASTA / f"{tk}.json").read_text(encoding="utf-8"))["baixado_em"]


# ---------------------------------------------------------------- (a) classe
def test_ticker_pn_le_a_linha_pn():
    regs = [_r("2025-05-02", 1.0), _r("2025-05-02", 1.1, classe="PN")]
    assert ph.dpa_jcp("FESA4", "2026-10-15", regs=regs, ev=[], grupos={})[0] == {"2025": 1.1}
    assert ph.dpa_jcp("VLID3", "2026-10-15", regs=regs, ev=[], grupos={})[0] == {"2025": 1.0}


def test_shul4_do_dossie_e_a_soma_das_linhas_pn():
    pn_2024 = 0.133482227 + 0.110700722 + 0.131092961 + 0.099921967       # 4 JCP da PN em 2024 (a ON paga 10% menos)
    with base.na_data("2026-10-15"):
        dpa, jcp = base.proventos_b3("SHUL4")
    assert dpa["2024"] == pytest.approx(pn_2024, abs=1e-9) and jcp["2024"] == pytest.approx(pn_2024, abs=1e-9)


# ---------------------------------------------------------------- (b) parcelas
def test_parcelas_somam():
    with base.na_data("2026-10-15"):
        vlid, _ = base.proventos_b3("VLID3")
        alld, _ = base.proventos_b3("ALLD3")
    # VLID3 2025: JCP em 4 parcelas em fev e 4 em nov (DMPL 2025: R$ 242,3 mi ≈ 8 linhas × 78,46 mi ações)
    assert vlid["2025"] == pytest.approx(4 * 0.39387731 + 4 * 0.37646831702, abs=1e-9)
    assert alld["2023"] == pytest.approx(0.482726014 + 0.482726015, abs=1e-12)      # DMPL 2023 + ITR 1T24 = R$ 90 mi


def test_repeticao_conferida_sai():
    dpa, _ = base.proventos_b3("HYPE3")
    assert dpa["2024"] == pytest.approx(1.1678, abs=1e-3)       # HYPE3 01/02/2024: a mesma linha duas vezes (DMPL 2024)


@pytest.mark.parametrize("tk", DOSSIES)
def test_grupos_dos_dossies_estao_todos_classificados(tk):
    """Até a data do cache (cobre todo veredito que ele pode servir): grupo novo sem prova, ou classificação velha, falha."""
    from proventos_ex import CLASSE
    dp = _cache(tk)
    linhas = [r for r in registros(tk, dp) if r["tipo_acao"] == CLASSE.get(tk, "ON") and ph.INICIO <= r["data_com"] <= dp
              and ph.TIPOS.get(r["tipo"])]
    achados = {(tk, *k) for k in ph.grupos_iguais(linhas)}
    assert achados == {k for k in ph.GRUPOS_CONFERIDOS if k[0] == tk}


def test_grupo_novo_no_dossie_falha_alto():
    regs = [_r("2025-05-02", 0.5), _r("2025-05-02", 0.5)]
    with pytest.raises(ValueError, match="parcela ou repetição"):
        ph.dpa_jcp("BLAU3", "2026-10-15", regs=regs, ev=[], grupos={})


# ---------------------------------------------------------------- (c) restituição de capital
def test_restituicao_de_capital_fora():
    with base.na_data("2026-10-15"):
        dpa, _ = base.proventos_b3("ALLD3")
    assert dpa["2025"] == pytest.approx(0.73765058864, abs=1e-12)       # sem a REST CAP DIN de R$ 1,898 (DMPL 5.04.08)


# ---------------------------------------------------------------- (d) eventos do FRE
def test_eventos_do_fre_que_a_b3_omite_entram_no_dpa():
    with base.na_data("2026-10-15"):
        ev = {(x["tipo"], x["data_com"]): x["multiplicador"] for x in base.eventos("SHUL4")}
        p = [x for x in ph.proventos("SHUL4", "2026-10-15") if x["data_com"] == "2018-10-17"]
    assert ev[("BONIFICACAO", "2018-12-04")] == 1.4 and ev[("BONIFICACAO", "2021-04-15")] == 2.0
    assert ev[("BONIFICACAO", "2022-04-13")] == 2.0                                      # este a B3 publica
    assert [x["valor_hoje"] for x in p] == pytest.approx([0.197354616 / (1.4 * 2 * 2)])


# variação das ações do DFP do dossiê sem evento por ação com data-com no ano (conferido no FRE e no COTAHIST, 20/10/2026)
SEM_EVENTO = {("BLAU3", "2021"): "IPO (abr/2021); desdobramento 1:8 de 2017 é anterior à listagem",
              ("BLAU3", "2025"): "bonificação de 30% aprovada em 15/12/2025, data-com 05/01/2026: o DFP 2025 já conta",
              ("CMIN3", "2021"): "desdobramento 1:30 de 15/10/2020 (FRE) antes do IPO de fev/2021; 1º provento 30/04/2021",
              ("CMIN3", "2025"): "DFP 2025 em escala ×10 (base.CORRECOES_ACOES)",
              ("ALLD3", "2021"): "IPO (jan/2021, DMPL: aumento de capital); grupamento 8:1 de 2020 é anterior à listagem",
              ("VLID3", "2021"): "aumento de capital por subscrição aprovado em 12/03/2021 (FRE 71,2 → 82,1 mi; sem marca de "
                                 "evento no COTAHIST)"}


@pytest.mark.parametrize("tk", ph.DOSSIES)
def test_acoes_do_dossie_conferem_com_os_eventos(tk):
    """Como `test_acoes_da_cvm_conferem_com_os_eventos` do hall, na série do dossiê: foi assim que a bonificação de 2021 da
    Schulz (×2,0, só no FRE) apareceu. HYPE3 e LEVE3 são conferidas pelo teste do hall."""
    a = json.loads(base.SERIES.read_text(encoding="utf-8"))[tk]["anual"]
    with base.na_data("2026-10-15"):
        ev = base.eventos(tk)
    anos = sorted(y for y in a if a[y].get("acoes"))
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


@pytest.mark.skipif(not (CVM_ZIP / "fre_2026.zip").exists(), reason="sem o FRE 2026 (escala das ações; dado local)")
@pytest.mark.parametrize("tk,esperado", [("SHUL4", -0.000255), ("VLID3", 0.025125)])
def test_diluicao_com_eventos_do_fre_e_escala(tk, esperado):
    """SHUL4: sem a bonificação de 2021 do FRE, a diluição saía 14,8% a.a. (gestão −1). VLID3: o DFP 2020 em milhares fazia
    308% a.a. — o CAGR certo (2,5%, subscrição de 2021) segue acima de 2% e a nota não muda."""
    from dossie import evidencia
    from motor_nao_financeiras import ANOS, CVM
    antes = CVM.get(tk)
    CVM[tk] = json.loads(base.SERIES.read_text(encoding="utf-8"))[tk]
    try:
        with base.na_data("2026-10-15"):
            c, _ = evidencia.diluicao(tk, list(ANOS), base.eventos(tk), "2020", lambda q: base.escala(tk, q))
    finally:
        if antes is None:
            CVM.pop(tk)
        else:
            CVM[tk] = antes
    assert c == pytest.approx(esperado, abs=1e-6)


@pytest.mark.skipif(not (CVM_ZIP / "fre_2021.zip").exists(), reason="sem os ZIPs do FRE (dados locais)")
def test_bonificacoes_da_schulz_no_fre():
    """FRE 2021 (tabela capital_social_desdobramento, versão mais recente): as duas bonificações que a B3 não publica."""
    import pandas as pd
    z = zipfile.ZipFile(CVM_ZIP / "fre_2021.zip")
    n = next(x for x in z.namelist() if "desdobramento" in x)
    d = pd.read_csv(io.BytesIO(z.read(n)), sep=";", encoding="latin-1", dtype=str)
    d = d[(d["CNPJ_Companhia"] == base.CNPJ["SHUL4"]) & (d["Tipo_Evento"] == "Bonificação")]
    d = d[d["Versao"] == max(d["Versao"], key=int)]
    razao = {r["Data_Aprovacao"]: float(r["Quantidade_Total_Acoes_Depois_Aprovacao"]) / float(r["Quantidade_Total_Acoes_Antes_Aprovacao"])
             for _, r in d.iterrows()}
    for x in ph.EVENTOS_FRE["SHUL4"]:
        assert razao[x["aprovacao"]] == pytest.approx(x["multiplicador"], abs=1e-6), x
