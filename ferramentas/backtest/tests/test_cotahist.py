"""Fatias 7-8: layout posicional do COTAHIST, calendário derivado e liquidez.

Os testes sintéticos montam um ZIP minúsculo com registros de 245 bytes escritos CAMPO A CAMPO a
partir do PDF da B3 — se alguém mexer em POS, o registro deixa de ser lido como esperado. Cada
prova de ausência tem meta-teste que injeta o defeito e exige falha (lição da Etapa 3).
"""
from __future__ import annotations

import zipfile

import pandas as pd
import pytest

from backtest import cotahist as C
from backtest.calendario import Calendario
from backtest.config import PADRAO


def _reg(data="20140102", bdi="02", ticker="PETR4", tpmerc="010", especi="PN", preult=1002,
         fatcot=1, quatot=1000, voltot=1_002_000_00, premed=1002, totneg=7) -> bytes:
    """Registro 01 de 245 bytes montado pelo layout do PDF (posições 1-based, inclusive)."""
    r = bytearray(b" " * 245)

    def poe(ini: int, fim: int, txt: str) -> None:
        assert len(txt) == fim - ini + 1, (ini, fim, txt)
        r[ini - 1:fim] = txt.encode("latin-1")

    poe(1, 2, "01"); poe(3, 10, data); poe(11, 12, bdi); poe(13, 24, ticker.ljust(12))
    poe(25, 27, tpmerc); poe(28, 39, "PETROBRAS".ljust(12)); poe(40, 49, especi.ljust(10))
    poe(53, 56, "R$  ")
    for ini, v in ((57, premed), (70, premed), (83, premed), (96, premed), (109, preult)):
        poe(ini, ini + 12, f"{v:013d}")
    poe(148, 152, f"{totneg:05d}"); poe(153, 170, f"{quatot:018d}"); poe(171, 188, f"{voltot:018d}")
    poe(211, 217, f"{fatcot:07d}"); poe(231, 242, "BRPETRACNPR6")
    return bytes(r)


def _zip(tmp, ano: int, regs: list[bytes], trailer: int | None = None) -> None:
    n = len(regs) + 2
    head = b"00COTAHIST.%d" % ano + b"BOVESPA " + f"{ano}1230".encode() + b" " * 214
    trl = (b"99COTAHIST.%d" % ano + b"BOVESPA " + f"{ano}1230".encode()
           + f"{trailer if trailer is not None else n:011d}".encode() + b" " * 203)
    assert len(head) == len(trl) == 245
    corpo = b"\r\n".join([head, *regs, trl]) + b"\r\n"
    with zipfile.ZipFile(tmp / f"COTAHIST_A{ano}.ZIP", "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr(f"COTAHIST_A{ano}.TXT", corpo)


@pytest.fixture
def pasta(tmp_path, monkeypatch):
    monkeypatch.setattr(C, "PASTA", tmp_path)
    monkeypatch.setattr(C, "MIN_BYTES", 1)
    return tmp_path


def test_o_registro_sintetico_tem_245_bytes():
    assert len(_reg()) == 245


def test_le_os_campos_nas_posicoes_do_pdf(pasta):
    _zip(pasta, 2014, [_reg(preult=1002, quatot=1000, voltot=1_002_000_00)])
    d = C.ler_ano(2014)
    r = d.iloc[0]
    assert (r["data"], r["codbdi"], r["ticker"], r["especi"], r["codisi"]) == (
        "2014-01-02", "02", "PETR4", "PN", "BRPETRACNPR6")
    assert r["preult"] == pytest.approx(10.02)          # (11)V99: 1002 -> 10,02
    assert r["voltot"] == pytest.approx(1_002_000.0)     # V99 também
    assert r["quatot"] == 1000 and r["totneg"] == 7


def test_fatcot_1000_divide_o_preco_por_acao(pasta):
    _zip(pasta, 2014, [_reg(ticker="XPTO3", preult=500_000, premed=500_000, fatcot=1000)])
    assert C.ler_ano(2014).iloc[0]["preult"] == pytest.approx(5.0)    # 5000,00 por lote de mil


def test_filtra_vista_e_bdi_do_universo(pasta):
    _zip(pasta, 2014, [
        _reg(ticker="PETR4"),
        _reg(ticker="PETRA10", tpmerc="070"),             # opção de compra: fora
        _reg(ticker="FRAC3F", bdi="96", tpmerc="020"),    # fracionário: fora
        _reg(ticker="OIBR3", bdi="08"),                   # recuperação judicial: DENTRO
    ])
    assert sorted(C.ler_ano(2014)["ticker"]) == ["OIBR3", "PETR4"]


def test_meta_posicao_deslocada_e_pega(pasta):
    """Injeta um defeito (campo deslocado 1 byte) e exige que a leitura NÃO bata com o esperado."""
    ruim = bytearray(_reg())
    ruim[24:27], ruim[25:28] = b" 01", b"010"             # TPMERC deslocado
    _zip(pasta, 2014, [bytes(ruim)])
    assert C.ler_ano(2014).empty                          # cai fora do filtro, não vira dado errado


def test_linha_de_tamanho_errado_falha_alto(pasta):
    _zip(pasta, 2014, [_reg()[:-1]])
    with pytest.raises(ValueError, match="bytes"):
        C.ler_ano(2014)


def test_trailer_inconsistente_denuncia_arquivo_truncado(pasta):
    _zip(pasta, 2014, [_reg(), _reg(ticker="VALE3")], trailer=99)
    with pytest.raises(ValueError, match="trailer"):
        C.ler_ano(2014)


@pytest.mark.parametrize("trailer", [4, 2])                # convenção até 2024 e a de 2025
def test_aceita_as_duas_convencoes_de_trailer(pasta, trailer):
    _zip(pasta, 2014, [_reg(), _reg(ticker="VALE3")], trailer=trailer)
    assert len(C.ler_ano(2014)) == 2


def test_fatcot_fora_do_pdf_avisa_mas_le(pasta, capsys):
    _zip(pasta, 2014, [_reg(fatcot=1_000_000, preult=150_000_000, premed=150_000_000)])
    d = C.ler_ano(2014)
    assert d.iloc[0]["preult"] == pytest.approx(1.5)
    assert "AVISO" in capsys.readouterr().out


def test_nunca_ha_extractall_no_modulo():
    import ast
    arv = ast.parse(open(C.__file__, encoding="utf-8").read())
    assert not [n for n in ast.walk(arv) if isinstance(n, ast.Attribute) and n.attr == "extractall"]


def test_calendario_vem_das_datas_do_arquivo_e_31_12_nao_negocia(pasta):
    _zip(pasta, 2014, [_reg(data="20141229"), _reg(data="20141230"), _reg(data="20141230", ticker="X3")])
    C.gerar(2014)
    cal = C.calendario(range(2014, 2015))
    assert cal.pregoes == ("2014-12-29", "2014-12-30")
    assert not cal.negociou_em("2014-12-31") and cal.ultimo_ate("2014-12-31") == "2014-12-30"


def test_liquidez_dia_sem_negocio_conta_zero_e_nao_olha_adiante(pasta):
    regs = [_reg(data=f"2014010{d}", voltot=100_00 * 60) for d in (2, 3)]       # 2 dias de R$ 6000
    regs += [_reg(data="20140106", ticker="OUTRA3", voltot=1)]                    # só marca pregão
    regs += [_reg(data="20140107", voltot=999_999_999_00)]                        # FUTURO ao corte
    _zip(pasta, 2014, regs)
    C.gerar(2014)
    cal = Calendario(("2014-01-02", "2014-01-03", "2014-01-06", "2014-01-07"))
    liq = C.liquidez_media("2014-01-06", cal=cal, janela=3, anos=range(2014, 2015))
    # 3 pregões até 06/01: PETR4 negociou 2 de 3 dias -> (6000 + 6000)/3 = 4000; o 07/01 não entra
    assert liq["PETR4"] == pytest.approx(4000.0)
    assert liq["OUTRA3"] == pytest.approx(0.01 / 3)


def test_so_acoes_descarta_bdr_etf_e_direitos():
    d = pd.DataFrame({"especi": ["ON", "PN  N2", "UNT  N2", "DRN", "IBO", "DIR", "ON  ED"]})
    assert list(C.so_acoes(d)["especi"]) == ["ON", "PN  N2", "UNT  N2", "ON  ED"]


# --- dado real (pulado se o parquet não estiver gerado; é gitignored) --------------------------
def _real():
    if not all(C.parquet_de(a).exists() for a in range(2014, 2027)):
        pytest.skip("parquets do COTAHIST não gerados (python -m backtest.cotahist)")


def test_real_posicoes_batem_por_consistencia_interna():
    """volume/quantidade = preço médio e mín <= último <= máx: só vale se as posições e as escalas
    (V99, FATCOT) estiverem certas. Medido: mediana 1,0002; 99,9994% na ordem."""
    _real()
    d = pd.read_parquet(C.parquet_de(2019))
    q = d[(d["quatot"] > 0) & (d["fatcot"] == 1)]
    r = (q["voltot"] / q["quatot"]) / q["premed"]
    assert 0.999 < r.median() < 1.001
    assert ((d["premin"] <= d["preult"] + 1e-9) & (d["preult"] <= d["premax"] + 1e-9)).mean() > 0.9999


def test_real_calendario_cobre_os_24_cortes_e_os_de_31_12_caem_no_dia_30():
    _real()
    cal = C.calendario()
    for d in PADRAO.datas_corte:
        ult = cal.ultimo_ate(d)
        assert ult is not None and 0 <= (pd.Timestamp(d) - pd.Timestamp(ult)).days <= 4, d
        if d.endswith("12-31"):
            assert not cal.negociou_em(d), f"{d}: a B3 não negocia em 31/12"
    assert 244 <= sum(1 for p in cal.pregoes if p.startswith("2019")) <= 252
