"""Período derivado do LTM (`ltm.py`), follow-on só fora do balanço (`eventos.py`) e os 3 bugs do 3T26 (23/11/2026).

Bugs que estes testes travam (todos só apareciam com o LTM do 3T26):
  · PETR4/RECV3: janela do barril fixa em jul/25–jun/26 → o barril do trimestre novo entrava como volume na receita de meio;
  · EGIE3: follow-on de jul/2026 e dividendo de ago/2026 somados/tirados do PL de 30/09, que já os continha (VPA +28%);
  · ISAE4: mesmo follow-on contado duas vezes.
"""
import copy
import pathlib
import subprocess
import sys

import pytest

import eventos
import ltm


# ---------------------------------------------------------------- ltm.py
@pytest.mark.parametrize("ref, janela, balanco", [
    ("2T26", ("2025-07", "2026-06"), "2026-06-30"),
    ("3T26", ("2025-10", "2026-09"), "2026-09-30"),
    ("1T27", ("2026-04", "2027-03"), "2027-03-31"),
    ("4T26", ("2026-01", "2026-12"), "2026-12-31"),
])
def test_janela_e_balanco_saem_do_rotulo_do_ltm(ref, janela, balanco):
    assert ltm.janela_ltm(ref) == janela
    assert ltm.data_do_balanco(ref) == balanco


def test_trimestres_atravessam_o_ano():
    assert ltm.trimestres_ate("3T26", 2) == [(2026, 2), (2026, 3)]
    assert ltm.trimestres_ate("1T27", 2) == [(2026, 4), (2027, 1)]
    assert ltm.janela_trimestre(2026, 3) == ("2026-07", "2026-09")


def test_ref_invalida_4t_no_itr_e_grupo_misturado_falham_alto():
    for ruim in ("2T", "5T26", "T226", "2X26"):
        with pytest.raises(ValueError):
            ltm.trimestre_e_ano(ruim)
    with pytest.raises(ValueError, match="DFP"):
        ltm.zip_itr("4T26")
    assert ltm.zip_itr("3T26") == "itr_2026.zip"
    with pytest.raises(ValueError, match="trimestres diferentes"):
        ltm.ref_comum([{"ltm_ref": "2T26"}, {"ltm_ref": "3T26"}])
    assert ltm.ref_comum([{"ltm_ref": "3T26"}, {"ltm_ref": "3T26"}]) == "3T26"


def test_proventos_ex_usa_a_mesma_data_do_balanco():
    import proventos_ex
    assert proventos_ex.data_do_balanco is ltm.data_do_balanco


# ---------------------------------------------------------------- eventos.py (follow-on)
def _reg(ref, acoes_ltm, acoes_dfp=1_142_298_836):
    return {"ltm_ref": ref, "ltm": {"acoes": acoes_ltm}, "anual": {"2024": {"acoes": 815_927_740}, "2025": {"acoes": acoes_dfp}}}


def test_follow_on_entra_so_se_o_balanco_ainda_nao_o_tem():
    """Números reais da EGIE3: 1.142,3 mi de ações em 30/06 e 1.416,4 mi em 30/09 (+274,1 mi da oferta de jul/2026)."""
    f, dentro = eventos.follow_on_e_balanco("EGIE3", _reg("2T26", 1_142_298_836))
    assert not dentro and f["acoes_novas"] == 274_100_000
    _, dentro = eventos.follow_on_e_balanco("EGIE3", _reg("3T26", 1_416_381_520))
    assert dentro


def test_follow_on_data_e_balanco_que_discordam_falham_alto():
    with pytest.raises(ValueError, match="DENTRO"):          # a data diz que já está, mas as ações não subiram
        eventos.follow_on_e_balanco("EGIE3", _reg("3T26", 1_142_298_836))
    with pytest.raises(ValueError, match="FORA"):            # a data diz que não está, mas as ações já subiram
        eventos.follow_on_e_balanco("EGIE3", _reg("2T26", 1_416_381_520))


def test_isae4_acoes_novas_vem_do_valor_e_do_preco_da_oferta():
    f = eventos.follow_on("ISAE4")
    assert eventos.acoes_novas(f) == pytest.approx(1_200_000 * 1000 / 27.0)
    reg = {"ltm_ref": "3T26", "ltm": {"acoes": 703_327_748}, "anual": {"2025": {"acoes": 658_883_304}}}
    assert eventos.follow_on_e_balanco("ISAE4", reg)[1] is True


def test_sem_follow_on_cadastrado_e_keyerror():
    with pytest.raises(KeyError):
        eventos.follow_on_e_balanco("XXXX3", _reg("2T26", 1))


# ---------------------------------------------------------------- os bugs, com os módulos reais
def test_egie3_dividendo_pos_balanco_vem_da_b3_e_some_no_3t26():
    """2T26: o dividendo aprovado em 05/08 (data-com 20/08) sai do PL de 30/06 — R$ 770,8 mi, antes digitados. 3T26: ele já está
    no passivo do balanço de 30/09 e não sai de novo."""
    from proventos_ex import ajuste_b3
    n = 1_142_298_836 + 274_100_000
    antes = ajuste_b3("EGIE3", n, "2T26", "02/10/2026")["depois"]
    assert antes == pytest.approx(770_800, abs=100)
    assert ajuste_b3("EGIE3", n, "3T26", "19/11/2026")["depois"] == 0.0


def test_janela_do_barril_anda_com_o_ltm():
    import lote5_petroleo as L5
    reg = L5.CVM["PETR4"]
    original = copy.deepcopy({k: reg.get(k) for k in ("ltm_ref",)})
    try:
        reg["ltm_ref"] = "2T26"
        b2 = L5.barril_do_ltm("PETR4")
        reg["ltm_ref"] = "3T26"
        b3 = L5.barril_do_ltm("PETR4")
    finally:
        reg["ltm_ref"] = original["ltm_ref"]
    assert b2["janela"] == ("2025-07", "2026-06") and b3["janela"] == ("2025-10", "2026-09")
    # conta independente do motor, direto dos arquivos: média mensal do Brent (FRED) × PTAX média mensal (BCB) nos 12 meses
    import json as _json
    import pandas as pd
    macro = pathlib.Path(__file__).resolve().parents[1] / "dados" / "macro"
    b = pd.read_csv(macro / "brent_fred.csv")
    b = pd.Series(pd.to_numeric(b.iloc[:, 1], errors="coerce").values, index=pd.to_datetime(b.iloc[:, 0])).dropna()
    brent = b.resample("MS").mean()
    p = _json.loads((macro / "ptax_media_mensal.json").read_text(encoding="utf-8"))
    ptax = pd.Series([float(x["valor"]) for x in p], index=pd.to_datetime([x["data"] for x in p], dayfirst=True))
    mao = (brent * ptax).dropna().loc["2025-07":"2026-06"]
    assert len(mao) == 12 and b2["barril"] == pytest.approx(mao.mean(), rel=1e-12)


TEM_ZIP_ITR = (pathlib.Path(__file__).resolve().parents[1] / "dados" / "cvm" / "itr_2026.zip").exists()


@pytest.mark.skipif(not TEM_ZIP_ITR, reason="sem o ITR da CVM no disco: as ações de 30/09 saem do ZIP")
def test_egie3_e_isae4_com_o_balanco_de_30_09_nao_contam_a_oferta_de_novo():
    """Ponta a ponta (oráculo, 23/11): com o balanço de 30/09 (números do ITR da CVM), o VPA tem de ser PL do controlador ÷
    ações do balanço — a oferta e o dividendo já estão nele. Com o código antigo a EGIE3 dava 20,41."""
    cod = """
import copy, json, series_vigente
c = series_vigente.carregar_cvm()
for tk, pl, nc, n in (("EGIE3", 22454922.0, 1137314.0, 1416381520.0), ("ISAE4", 24033582.0, 180998.0, 703327748.0)):
    r = copy.deepcopy(c[tk]); r["ltm_ref"] = "3T26"; r["ltm"] = dict(r["ltm"], pl=pl, nao_controladores=nc, acoes=n)
    series_vigente.CVM_SOBREPOSTO[tk] = r
import lote6_quimica as L6, lote2_energia as L2
isae = next(e for e in L2.EMPRESAS if e.ticker == "ISAE4")
print(json.dumps(dict(egie_vpa=L6.EGIE.vpa, egie_n=L6.N["EGIE3"], egie_div=L6.EGIE_DADOS["div_depois"],
                      egie_dentro=L6.EGIE_FO_NO_BALANCO, isae_vpa=isae.vpa)))
"""
    p = subprocess.run([sys.executable, "-c", cod], cwd=pathlib.Path(__file__).resolve().parents[1], capture_output=True,
                       text=True, timeout=600)
    assert p.returncode == 0, p.stderr[-1500:]
    import json as _json
    r = _json.loads(p.stdout.strip().splitlines()[-1])
    assert r["egie_dentro"] is True and r["egie_div"] == 0.0
    assert r["egie_n"] == pytest.approx(1416381520.0, rel=1e-4)                  # ações de 30/09 no ITR, sem somar a oferta
    assert r["egie_vpa"] == pytest.approx((22454922.0 - 1137314.0) * 1000 / r["egie_n"], rel=1e-9)
    assert r["egie_vpa"] == pytest.approx(15.05, abs=0.01)
    assert r["isae_vpa"] == pytest.approx((24033582.0 - 180998.0) * 1000 / 703327748.0, rel=1e-9)


TEM_ITR = (pathlib.Path(__file__).resolve().parents[1] / "dados" / "cvm" / "itr_2026.zip").exists()


@pytest.mark.skipif(not TEM_ITR, reason="sem o ITR da CVM no disco: as ações de 30/09 só saem do ZIP")
def test_publicacao_parcial_na_temporada_nao_quebra_o_import():
    """Adversário, 23/11: com só a TIMS3 num trimestre e o resto do lote 4 em outro (temporada com publicação parcial), o import
    levantava "trimestres diferentes" e derrubava a própria temporada. Agora cada ticker lê as ações da data do próprio LTM.
    Relativo ao LTM vigente (a gravação do 3T26 quebrou a versão com "3T26"/"2T26" escritos): a TIMS3 vai ao trimestre anterior."""
    cod = ("import copy, sys, series_vigente, ltm; c = series_vigente.carregar_cvm(); vig = ltm.ltm_ref_de(c['VIVT3']);"
           "a, t = ltm.trimestres_ate(vig, 2)[0]; ant = f'{t}T{a % 100:02d}';"
           "r = copy.deepcopy(c['TIMS3']); r['ltm_ref'] = ant;"
           "series_vigente.CVM_SOBREPOSTO['TIMS3'] = r; import lote4_saude_telecom as L;"
           "print(ant, vig, L.REFS4['TIMS3'] == ant, L.REFS4['VIVT3'] == vig, L.N['TIMS3'] > 1e9)")
    p = subprocess.run([sys.executable, "-c", cod], cwd=pathlib.Path(__file__).resolve().parents[1], capture_output=True, text=True,
                       timeout=600)
    assert p.returncode == 0, p.stderr[-1500:]
    ant, vig, *ok = p.stdout.split()
    assert ant != vig and ok == ["True", "True", "True"], p.stdout


def test_cmin3_janela_do_minerio_anda_com_o_ltm():
    """Adversário, 23/11: o dossiê da CMIN3 tinha a mesma janela fixa (jul/25–jun/26) do barril."""
    from dossie.fichas import cmin3 as C
    m2 = C.minerio()
    reg = C.CVM["CMIN3"]
    antes = reg.get("ltm_ref")
    try:
        reg["ltm_ref"] = "3T26"
        try:
            m3 = C.minerio()
        except ValueError as e:          # dados/macro sem setembro: falha alto, nunca média de 11 meses
            assert "12m incompletos em 2025-10" in str(e)
        else:
            assert m3["fator"] != m2["fator"]
    finally:
        if antes is None:
            reg.pop("ltm_ref", None)
        else:
            reg["ltm_ref"] = antes
        C.minerio.cache_clear()


def test_indice_de_preco_do_lote6_usa_os_12m_do_ltm():
    """Os 12m do índice são os do LTM; mês que o BLS ainda não publicou (ou não foi coletado) → falha alto, nunca média de 11."""
    import lote6_quimica as L6
    assert L6.indice({"WPU1017": 1.0}, "2T26")["janela_ltm"] == ("2025-07", "2026-06")
    vig = ltm.ltm_ref_de(L6.CVM["GGBR4"])                     # relativo ao vigente (a gravação do 3T26 mudou o LTM)
    a_vig = L6.indice({"WPU1017": 1.0}, vig)
    assert a_vig["janela_ltm"] == ltm.janela_ltm(vig) and a_vig["fator"] == pytest.approx(L6.ACO["fator"])
    a, t = ltm.trimestres_ate(vig, 2)[0]
    a_ant = L6.indice({"WPU1017": 1.0}, f"{t}T{a % 100:02d}")
    assert a_ant["janela_ltm"] != a_vig["janela_ltm"] and a_ant["fator"] != a_vig["fator"]
    with pytest.raises(ValueError, match="de 12 meses"):      # mês que o BLS ainda não publicou: falha alto, nunca média de 11
        L6.indice({"WPU1017": 1.0}, "4T35")
