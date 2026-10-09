"""AUD-83 (histórico do monitor sem duplicata) e AUD-84 (arquivo vigente vai para _historico/ antes de ser sobrescrito)."""
import csv

import pytest

import monitor_semanal as M
from historico_arquivos import gravar_texto, guardar


def _hall(preco=10.0):
    return [{"ticker": "AAAA3", "preco": preco, "central": 20.0, "pc": 0.5, "alerta": "≤ COMPRA"},
            {"ticker": "BBBB3", "preco": 5.0, "central": float("nan"), "pc": float("inf"), "alerta": "NC"}]


def _linhas(caminho):
    with caminho.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_aud83_mesma_rodada_duas_vezes_nao_duplica(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "RAIZ", tmp_path)
    h = tmp_path / "historico.csv"
    M.gravar_historico(_hall(), "2026-10-08", "2026-10-09", h)
    M.gravar_historico(_hall(11.0), "2026-10-08", "2026-10-09", h)         # reexecução com preço corrigido
    M.gravar_historico(_hall(), "2026-10-15", "2026-10-16", h)             # rodada nova acumula
    ls = _linhas(h)
    assert len(ls) == 4
    a = [l for l in ls if l["ticker"] == "AAAA3" and l["rodada"] == "2026-10-09"]
    assert len(a) == 1 and a[0]["preco"] == "11.0"                          # a reexecução substitui


def test_aud84_historico_do_monitor_guarda_a_versao_anterior(tmp_path, monkeypatch):
    monkeypatch.setattr(M, "RAIZ", tmp_path)
    h = tmp_path / "historico.csv"
    M.gravar_historico(_hall(), "2026-10-08", "2026-10-09", h)
    antes = h.read_bytes()
    M.gravar_historico(_hall(11.0), "2026-10-08", "2026-10-09", h)
    guardados = list((tmp_path / "_historico").rglob("historico*.csv"))
    assert len(guardados) == 1 and guardados[0].read_bytes() == antes


def test_aud84_guardar_copia_so_quando_muda_e_nao_apaga_o_que_ja_guardou(tmp_path):
    f = tmp_path / "03.md"
    assert guardar(f, "t", raiz=tmp_path, hoje="2026-10-09") is None          # nada a guardar
    f.write_bytes(b"v1\r\n")
    assert guardar(f, "t", b"v1\n", raiz=tmp_path, hoje="2026-10-09") is None  # conteúdo igual (CRLF×LF não conta)
    c1 = guardar(f, "t", b"v2", raiz=tmp_path, hoje="2026-10-09")
    assert c1 is not None and c1.read_bytes() == b"v1\r\n"
    f.write_bytes(b"v2")
    c2 = guardar(f, "t", b"v3", raiz=tmp_path, hoje="2026-10-09")             # outra versão, mesmo dia
    assert c2 != c1 and c1.read_bytes() == b"v1\r\n" and c2.read_bytes() == b"v2"
    assert guardar(f, "t", None, raiz=tmp_path, hoje="2026-10-09") == c2      # mesma versão: não duplica


def test_aud84_gravar_texto_guarda_e_grava(tmp_path):
    f = tmp_path / "06.md"
    f.write_bytes(b"antigo\n")
    gravar_texto(f, "novo\n", "06 teste", raiz=tmp_path, hoje="2026-10-09", newline="\n")
    assert f.read_bytes() == b"novo\n"
    assert (tmp_path / "_historico" / "2026-10-09 06 teste" / "06.md").read_bytes() == b"antigo\n"


def test_aud84_nenhum_gravador_de_producao_sobrescreve_sem_guardar():
    """Os scripts que regravam o 03, o 06 e os PDFs passam por historico_arquivos."""
    import pathlib
    raiz = pathlib.Path(__file__).resolve().parent.parent
    for nome in [*(f"atualizar_hall_lote{n}.py" for n in range(1, 7)), *(f"gerar_pdf_lote{n}.py" for n in range(1, 7)),
                 "hall03.py", "triagem/rodar.py", "monitor_semanal.py"]:
        assert "historico_arquivos" in (raiz / nome).read_text(encoding="utf-8"), nome
