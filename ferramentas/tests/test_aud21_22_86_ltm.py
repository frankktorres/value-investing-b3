"""AUD-21 (comparativo reapresentado), AUD-22 (SMTO3: exercício abr–mar) e AUD-86 (lacunas visíveis) do LTM."""
import zipfile

import pytest

import coletar_cvm as c


def test_aud86_componente_ausente_vira_lacuna_visivel():
    fy = {"receita": 100.0, "ebit": 20.0, "capex": 10.0, "caixa": 5.0, "acoes": 7.0}
    atual = {"receita": 60.0, "ebit": 12.0, "capex": 6.0, "caixa": 9.0}
    anterior = {"receita": 50.0, "ebit": 10.0}                       # capex só no comparativo ausente
    ltm, lacunas, reap = c.combinar_ltm(fy, atual, anterior)
    assert ltm["receita"] == 110.0 and ltm["ebit"] == 22.0
    assert "capex" not in ltm and lacunas == ["capex"]               # antes: sumia em silêncio e o motor lia 0
    assert ltm["caixa"] == 9.0 and ltm["acoes"] == 7.0 and reap == []


def test_aud86_campo_que_nunca_existiu_nao_e_lacuna():
    ltm, lacunas, _ = c.combinar_ltm({"receita": 1.0}, {"receita": 1.0}, {"receita": 1.0})
    assert lacunas == []


def test_aud21_reapresentacao_acima_de_meio_por_cento_e_registrada():
    fy = {"ebit": 100.0, "receita": 500.0}
    atual = {"ebit": 60.0, "receita": 300.0}
    comparativo = {"ebit": 50.0, "receita": 250.0}                   # reapresentado
    original = {"ebit": 45.0, "receita": 250.5}                      # receita: 0,2% (dentro da tolerância)
    ltm, _, reap = c.combinar_ltm(fy, atual, comparativo, original)
    assert ltm["ebit"] == 110.0                                      # usa o comparativo, não o original (115)
    assert reap == [("ebit", 45.0, 50.0)]


def _zip_itr(tmp_path, linhas, ano=2026):
    cab = "DENOM_CIA;CD_CVM;CD_CONTA;DS_CONTA;VL_CONTA;ORDEM_EXERC;DT_REFER;DT_INI_EXERC;VERSAO;ESCALA_MOEDA"
    corpo = "\n".join(";".join(map(str, (("TESTE SA", "000001", "3.01", "Receita", *l, "1", "MIL")))) for l in linhas)
    caminho = tmp_path / f"itr_{ano}.zip"
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr(f"itr_cia_aberta_DRE_con_{ano}.csv", (cab + "\n" + corpo + "\n").encode("latin-1"))   # a CVM usa latin-1
    return zipfile.ZipFile(caminho)


@pytest.fixture
def teste3(monkeypatch):
    monkeypatch.setitem(c.EMPRESAS, "TESTE3", ("cvm:000001", 1))


def test_aud21_itr_ytd_comparativo_le_penultimo_exercicio(tmp_path, monkeypatch, teste3):
    z = _zip_itr(tmp_path, [
        (40, "ÚLTIMO EXERCÍCIO", "2026-06-30", "2026-04-01"), (100, "ÚLTIMO EXERCÍCIO", "2026-06-30", "2026-01-01"),
        (35, "PENÚLTIMO EXERCÍCIO", "2026-06-30", "2025-04-01"), (80, "PENÚLTIMO EXERCÍCIO", "2026-06-30", "2025-01-01")])
    monkeypatch.setattr(c, "zip_de", lambda tipo, ano: z)
    assert c.itr_ytd("TESTE3", 2026, 6)["receita"] == 100
    assert c.itr_ytd("TESTE3", 2026, 6, comparativo=True)["receita"] == 80


def test_aud22_exercicio_abril_marco_usa_ytd_a_partir_de_abril(tmp_path, monkeypatch, teste3):
    z = _zip_itr(tmp_path, [
        (30, "ÚLTIMO EXERCÍCIO", "2026-06-30", "2026-04-01"), (28, "PENÚLTIMO EXERCÍCIO", "2026-06-30", "2025-04-01")])
    monkeypatch.setattr(c, "zip_de", lambda tipo, ano: z)
    assert c.itr_ytd("TESTE3", 2026, 6)["receita"] is None          # com "01" (ano-calendário) o YTD de abril não entra
    assert c.itr_ytd("TESTE3", 2026, 6, mes_ini="04")["receita"] == 30
    assert c.itr_ytd("TESTE3", 2026, 6, comparativo=True, mes_ini="04")["receita"] == 28
