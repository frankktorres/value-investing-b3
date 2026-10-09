"""AUD-05: o backup leva o que não se recria (dados/ sem cvm/ + evidência do proxy) e nunca a si mesmo."""
import zipfile

import backup_dados as B


def _arvore(tmp_path):
    dados = tmp_path / "dados"
    (dados / "cvm").mkdir(parents=True)
    (dados / "cvm" / "dfp_2025.zip").write_bytes(b"x")
    (dados / "macro").mkdir()
    (dados / "macro" / "ipca.json").write_text("{}")
    ev = tmp_path / "backtest" / "dados"
    ev.mkdir(parents=True)
    (ev / "proxy_consultas.log").write_text("1\n")
    (ev / "proxy_2026-10-05.json").write_text("{}")
    (ev / "retornos.parquet").write_bytes(b"x")          # derivado reconstruível: fora
    return dados, ev


def test_zip_leva_evidencia_e_deixa_de_fora_cvm_e_derivados(tmp_path):
    dados, ev = _arvore(tmp_path)
    z = B.zipar(tmp_path / "bk", dados=dados, hoje="2026-01-01", evidencia=(ev,))
    nomes = sorted(zipfile.ZipFile(z).namelist())
    assert nomes == ["backtest/dados/proxy_2026-10-05.json", "backtest/dados/proxy_consultas.log", "dados/macro/ipca.json"]


def test_destino_dentro_de_dados_nao_entra_no_proprio_zip(tmp_path):
    dados, ev = _arvore(tmp_path)
    B.zipar(dados / "bk", dados=dados, hoje="2026-01-01", evidencia=(ev,))
    z = B.zipar(dados / "bk", dados=dados, hoje="2026-01-02", evidencia=(ev,))
    assert not [n for n in zipfile.ZipFile(z).namelist() if "bk/" in n]
