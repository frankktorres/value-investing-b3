"""AUD-81: coletor das séries FRED/PTAX com conferência da parte comum, histórico e manifesto — sem rede."""
import json
import pathlib

import coletar_macro_fred as c

MACRO_REAL = pathlib.Path(c.__file__).resolve().parent / "dados" / "macro"
CSV_V1 = "observation_date,WPU1017\n2026-06-01,100.0\n2026-07-01,101.0\n"


def _pasta(tmp_path, texto=CSV_V1):
    p = tmp_path / "macro"
    p.mkdir()
    (p / "fred_WPU1017.csv").write_bytes(texto.encode("utf-8"))
    return p


def test_mes_novo_no_fim_grava_guarda_o_anterior_e_diz_a_data(tmp_path):
    pasta = _pasta(tmp_path)
    novo = CSV_V1 + "2026-08-01,102.5\n"
    est, div = c.atualizar_fred("fred_WPU1017.csv", baixar=lambda url: novo, pasta=pasta, hoje="2026-11-03", raiz=tmp_path)
    assert (est, div) == ("gravado", [])
    assert (pasta / "fred_WPU1017.csv").read_bytes().decode().count("2026-08-01") == 1
    guardado = list((tmp_path / "_historico").rglob("fred_WPU1017.csv"))
    assert len(guardado) == 1 and guardado[0].read_bytes().decode() == CSV_V1       # o arquivo substituído foi guardado


def test_revisao_na_parte_comum_nao_grava_sem_aceitar(tmp_path):
    pasta = _pasta(tmp_path)
    revisado = "observation_date,WPU1017\n2026-06-01,100.0\n2026-07-01,101.7\n2026-08-01,102.5\n"     # BLS revisou jul
    est, div = c.atualizar_fred("fred_WPU1017.csv", baixar=lambda url: revisado, pasta=pasta, raiz=tmp_path)
    assert est == "divergiu" and div == ["2026-07-01: antigo 101.0 × novo 101.7"]
    assert (pasta / "fred_WPU1017.csv").read_bytes().decode() == CSV_V1             # intacto
    est, _ = c.atualizar_fred("fred_WPU1017.csv", baixar=lambda url: revisado, pasta=pasta, raiz=tmp_path, aceitar_revisoes=True)
    assert est == "gravado"


def test_data_que_sumiu_e_divergencia(tmp_path):
    pasta = _pasta(tmp_path)
    curto = "observation_date,WPU1017\n2026-07-01,101.0\n"
    est, div = c.atualizar_fred("fred_WPU1017.csv", baixar=lambda url: curto, pasta=pasta, raiz=tmp_path)
    assert est == "divergiu" and "2026-06-01" in div[0]


def test_resposta_que_nao_e_csv_do_fred_e_recusada(tmp_path):
    import pytest
    pasta = _pasta(tmp_path)
    with pytest.raises(ValueError, match="formato"):
        c.atualizar_fred("fred_WPU1017.csv", baixar=lambda url: "<html>erro</html>", pasta=pasta, raiz=tmp_path)


def test_ptax_mesma_regra(tmp_path):
    pasta = tmp_path / "macro"
    pasta.mkdir()
    v1 = [{"data": "01/06/2026", "valor": "5.1"}, {"data": "01/07/2026", "valor": "5.2"}]
    (pasta / c.PTAX).write_text(json.dumps(v1, separators=(",", ":")), encoding="utf-8")
    est, _ = c.atualizar_ptax(baixar=lambda url: v1 + [{"data": "01/08/2026", "valor": "5.3"}], pasta=pasta, hoje="2026-09-03", raiz=tmp_path)
    assert est == "gravado"
    est, div = c.atualizar_ptax(baixar=lambda url: [{"data": "01/06/2026", "valor": "5.1"}, {"data": "01/07/2026", "valor": "5.25"}],
                                pasta=pasta, hoje="2026-09-04", raiz=tmp_path)
    assert est == "divergiu" and len(div) == 2          # jul revisado e ago ausente


def test_manifesto_do_repo_confere_com_os_arquivos():
    """Todo arquivo macro lido pelos lotes está no manifesto, com o sha256 e a data de coleta."""
    m = json.loads((MACRO_REAL / "MANIFESTO_MACRO.json").read_text(encoding="utf-8"))
    esperados = {*c.SERIES_FRED, c.PTAX}
    assert set(m) == esperados
    for arq, info in m.items():
        assert c.sha_normalizado((MACRO_REAL / arq).read_bytes()) == info["sha256"], f"{arq} mudou sem passar pelo coletor"
        assert info["coletado_em"] and info["url"] and info["linhas"] > 0
