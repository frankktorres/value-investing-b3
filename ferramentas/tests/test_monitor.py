"""Monitor semanal: fronteiras dos alertas, troca atômica do COTAHIST, aviso de dado velho e a prova
de que, no pregão do hall (02/10/2026), o monitor reproduz o P/C do golden ticker a ticker."""
from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd
import pytest

import monitor_semanal as M


@pytest.mark.parametrize("preco,esperado", [
    (7.0, M.COMPRA), (6.99, M.COMPRA), (7.01, M.OBSERVA), (7.70, M.OBSERVA), (7.71, M.NEUTRO),
    (12.99, M.NEUTRO), (13.0, M.SAIDA), (20.0, M.SAIDA)])
def test_fronteiras_compra_070_saida_130(preco, esperado):
    assert M.alerta(preco, 7.0, 13.0, "CARA") == esperado          # central 10


def test_saida_por_qualidade_150():
    assert M.alerta(14.0, 7.0, 15.0, "CARA") == M.NEUTRO           # 1,40× não alerta quando a saída é 1,50×
    assert M.alerta(15.0, 7.0, 15.0, "CARA") == M.SAIDA


def test_sem_central_nao_alerta():
    assert M.alerta(5.0, math.nan, math.nan, "CARA") == M.SEM
    assert M.alerta(5.0, -1.0, -2.0, "CARA") == M.SEM


@pytest.mark.parametrize("preco", [5.0, 7.0, 10.0, 13.0, 20.0])
def test_nao_conclusivo_nao_emite_compra_nem_saida(preco):
    """AUD-43: a compra só é autorizada pela palavra FINAL (§9); NÃO CONCLUSIVO não tem preço de compra nem
    de saída — o rótulo é outro em qualquer preço, e a palavra é obrigatória (chamada sem ela quebra)."""
    assert M.alerta(preco, 7.0, 13.0, "NÃO CONCLUSIVO") == M.NC
    with pytest.raises(TypeError):
        M.alerta(preco, 7.0, 13.0)                                  # noqa — a palavra não pode faltar


def test_linhas_hall_nao_conclusivo_sem_compra_nem_saida():
    refs = {"AAAA3": dict(central=10.0, palavra="NÃO CONCLUSIVO", lote=6, compra=7.0, saida=13.0,
                          saida_por_qualidade=False),
            "BBBB3": dict(central=10.0, palavra="CARA", lote=6, compra=7.0, saida=13.0, saida_por_qualidade=False)}
    nc, cara = M.linhas_hall(refs, {"AAAA3": 20.0, "BBBB3": 20.0})
    assert nc["alerta"] == M.NC and math.isnan(nc["compra"]) and math.isnan(nc["saida"])
    assert nc["pc"] == pytest.approx(2.0)                          # o P/C continua informativo
    assert cara["alerta"] == M.SAIDA and cara["saida"] == 13.0


def test_carteira_sem_palavra_aparece_nos_alertas():
    hall = [dict(ticker="AAAA3", lote=2, palavra="NÃO CONCLUSIVO", preco=10.0, central=9.0, pc=1.11,
                 compra=math.nan, saida=math.nan, saida_qualidade=False, alerta=M.NC, carteira=True)]
    md = M.markdown(hall, pd.DataFrame(), {}, "2026-10-02", "2026-10-06", "ok")
    alertas = md.split("## Alertas")[1].split("## Carteira")[0]
    assert "Carteira sem palavra" in alertas and "AAAA3" in alertas
    assert M.COMPRA not in alertas.split("Carteira sem palavra")[1]


# ------------------------------------------------------------------ AUD-37: falha ativa e código de saída
def _isolar(monkeypatch, tmp_path: Path, pregao: str):
    monkeypatch.setattr(M, "BOLETINS", tmp_path / "BOLETINS")
    monkeypatch.setattr(M, "HISTORICO", tmp_path / "historico.csv")
    monkeypatch.setattr(M, "RAIZ", tmp_path)                  # AUD-84: _historico/ de teste não vai para o repo
    monkeypatch.setattr(M, "referencias_do_hall", lambda: {"AAAA3": dict(
        central=10.0, palavra="CARA", lote=1, compra=7.0, saida=13.0, saida_por_qualidade=False)})
    monkeypatch.setattr(M, "fila_do_06", lambda: pd.DataFrame())
    monkeypatch.setattr(M, "ultimos_precos", lambda tickers, hoje: ({"AAAA3": 11.0}, pregao))


def test_excecao_grava_boletim_de_falha(monkeypatch, tmp_path: Path):
    _isolar(monkeypatch, tmp_path, "2026-10-08")

    def quebra():
        raise RuntimeError("cvm_series.json corrompido")
    monkeypatch.setattr(M, "referencias_do_hall", quebra)
    assert M.main(["--sem-download", "--hoje", "2026-10-09"]) == M.RC_FALHA
    md = (tmp_path / "BOLETINS" / "2026-10-09-monitor.md").read_text(encoding="utf-8")
    assert md.startswith("> **MONITOR FALHOU**")
    assert "RuntimeError" in md and "cvm_series.json corrompido" in md and "Traceback" in md


def test_falha_depois_do_boletim_nao_apaga_o_boletim(monkeypatch, tmp_path: Path):
    _isolar(monkeypatch, tmp_path, "2026-10-08")

    def quebra(*a, **k):
        raise OSError("disco cheio")
    monkeypatch.setattr(M, "gravar_historico", quebra)
    assert M.main(["--sem-download", "--hoje", "2026-10-09"]) == M.RC_FALHA
    md = (tmp_path / "BOLETINS" / "2026-10-09-monitor.md").read_text(encoding="utf-8")
    # a falha vai NO TOPO (o prompt de sexta e o aviso do .vbs olham a abertura); o boletim bom fica embaixo
    assert md.startswith("> **MONITOR FALHOU**") and "disco cheio" in md and "# Monitor semanal" in md


def test_falha_ao_gravar_a_propria_falha_ainda_sai_rc_falha(monkeypatch, tmp_path: Path):
    _isolar(monkeypatch, tmp_path, "2026-10-08")
    (tmp_path / "arquivo").write_text("x")
    monkeypatch.setattr(M, "BOLETINS", tmp_path / "arquivo" / "BOLETINS")   # dentro de um arquivo: não grava

    def quebra():
        raise ZeroDivisionError("1/0")
    monkeypatch.setattr(M, "referencias_do_hall", quebra)
    assert M.main(["--sem-download", "--hoje", "2026-10-09"]) == M.RC_FALHA


def test_dado_velho_sai_com_rc_velho_mesmo_sem_download(monkeypatch, tmp_path: Path):
    _isolar(monkeypatch, tmp_path, "2026-09-20")
    assert M.main(["--sem-download", "--hoje", "2026-10-06"]) == M.RC_VELHO


def test_rodada_boa_sai_com_0(monkeypatch, tmp_path: Path):
    real = M.HISTORICO.read_bytes() if M.HISTORICO.exists() else None
    _isolar(monkeypatch, tmp_path, "2026-10-02")
    assert M.main(["--sem-download", "--hoje", "2026-10-06"]) == 0
    assert (tmp_path / "BOLETINS" / "2026-10-06-monitor.md").read_text(encoding="utf-8").startswith("# Monitor")
    # o histórico vai para onde HISTORICO aponta na hora — o versionado não pode ser tocado por teste
    assert "AAAA3" in (tmp_path / "historico.csv").read_text(encoding="utf-8")
    monkeypatch.undo()
    assert (M.HISTORICO.read_bytes() if M.HISTORICO.exists() else None) == real


def test_prompt_da_sexta_exige_o_monitor_desta_sexta():
    """AUD-37: o agente das 18h não pode ler o monitor da semana anterior como atual."""
    p = (Path(__file__).resolve().parents[2] / "PROMPT-AGENTE-NOTICIAS-SEXTA.md").read_text(encoding="utf-8")
    assert "data desta sexta" in p and "MONITOR FALHOU" in p and "sem palavra" in p


def test_troca_atomica_devolve_o_zip_bom(tmp_path: Path):
    destino, novo, velho = tmp_path / "A.ZIP", tmp_path / "A.novo", tmp_path / "A.anterior"
    destino.write_bytes(b"bom")
    novo.write_bytes(b"torto")
    chamadas = []

    def gerar(ano):
        chamadas.append(destino.read_bytes())
        if destino.read_bytes() == b"torto":
            raise ValueError("trailer não confere")
    estado = M.trocar_e_gerar(2026, novo, destino, velho, gerar)
    assert estado.startswith("falhou") and "mantido o anterior" in estado
    assert destino.read_bytes() == b"bom"
    assert chamadas == [b"torto", b"bom"]                  # o parquet foi regerado do bom


def test_troca_atomica_aceita_o_novo(tmp_path: Path):
    destino, novo, velho = tmp_path / "A.ZIP", tmp_path / "A.novo", tmp_path / "A.anterior"
    destino.write_bytes(b"velho")
    novo.write_bytes(b"novo")
    assert M.trocar_e_gerar(2026, novo, destino, velho, lambda a: None) == "atualizado"
    assert destino.read_bytes() == b"novo" and not velho.exists() and not novo.exists()


def test_ano_novo_sem_zip_anterior(tmp_path: Path):
    destino, novo = tmp_path / "A2027.ZIP", tmp_path / "A2027.novo"
    novo.write_bytes(b"x")
    assert M.trocar_e_gerar(2027, novo, destino, tmp_path / "v", lambda a: None) == "atualizado"


def _hall():
    return [dict(ticker="AAAA3", lote=1, palavra="CARA", preco=10.0, central=5.0, pc=2.0, compra=3.5,
                 saida=6.5, saida_qualidade=False, alerta=M.SAIDA, carteira=True)]


def test_dado_velho_no_topo():
    md = M.markdown(_hall(), pd.DataFrame(), {}, "2026-09-20", "2026-10-06", "falhou: x")
    assert md.startswith("> **DADO VELHO:**")
    md = M.markdown(_hall(), pd.DataFrame(), {}, "2026-10-02", "2026-10-06", "atualizado")
    assert "DADO VELHO" not in md


def test_monitor_nao_muda_palavra():
    md = M.markdown(_hall(), pd.DataFrame(), {}, "2026-10-02", "2026-10-06", "ok")
    assert "| CARA |" in md and "não muda palavra" in md


COTA = Path(__file__).resolve().parent.parent / "backtest" / "dados" / "cotahist" / "precos_2026.parquet"


@pytest.mark.skipif(not COTA.exists(), reason="COTAHIST 2026 fora do disco")
def test_no_pregao_do_hall_reproduz_o_golden():
    """Em 02/10/2026 (preços do 03) o P/C do monitor = o do golden a 2%: mesma fonte de central."""
    refs = M.referencias_do_hall()
    precos, pregao = M.ultimos_precos(set(refs), "2026-10-02")
    assert pregao == "2026-10-02"
    g = json.loads((Path(__file__).parent / "golden.json").read_text(encoding="utf-8"))["tickers"]
    comparados = 0
    for x in M.linhas_hall(refs, precos):
        gp = g[x["ticker"]]["pc"]
        if math.isfinite(gp):
            assert x["pc"] == pytest.approx(gp, rel=0.02), x["ticker"]
            comparados += 1
    assert comparados == 40      # só a RECV3 tem central ≤ 0 (a KLBN11 voltou a positivo com o ponto fixo partindo do contábil)


@pytest.mark.skipif(not COTA.exists(), reason="COTAHIST 2026 fora do disco")
def test_nenhum_nao_conclusivo_do_hall_sai_compra_ou_saida():
    """AUD-43 com o hall de verdade: em 06/10/2026 KLBN11 e SLCE3 (NÃO CONCLUSIVO) saíam '≥ SAÍDA'."""
    refs = M.referencias_do_hall()
    precos, _ = M.ultimos_precos(set(refs), "2026-10-06")
    nc = [x for x in M.linhas_hall(refs, precos) if x["palavra"] == "NÃO CONCLUSIVO"]
    assert {x["ticker"] for x in nc} >= {"ISAE4", "KLBN11", "SLCE3"}
    assert all(x["alerta"] in (M.NC, "sem preço") for x in nc), [(x["ticker"], x["alerta"]) for x in nc]


def test_ano_novo_com_arquivo_torto_nao_fica_no_lugar(tmp_path: Path):
    destino, novo = tmp_path / "A2027.ZIP", tmp_path / "A2027.novo"
    novo.write_bytes(b"torto")

    def gerar(ano):
        raise ValueError("trailer")
    estado = M.trocar_e_gerar(2027, novo, destino, tmp_path / "v", gerar)
    assert "não havia arquivo anterior" in estado
    assert not destino.exists() and (tmp_path / "A2027.rejeitado").exists()


def test_anterior_que_tambem_nao_regera_nao_estoura(tmp_path: Path):
    destino, novo, velho = tmp_path / "A.ZIP", tmp_path / "A.novo", tmp_path / "A.anterior"
    destino.write_bytes(b"velho")
    novo.write_bytes(b"novo")

    def gerar(ano):
        raise ValueError("sempre")
    estado = M.trocar_e_gerar(2026, novo, destino, velho, gerar)
    assert "também não regerou" in estado and destino.read_bytes() == b"velho"
