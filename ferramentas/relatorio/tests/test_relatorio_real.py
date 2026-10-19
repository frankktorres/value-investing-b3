"""O relatório é vista: a palavra e o central são os do veredito vigente, todo número tem fonte (ou o motivo de não ter)
e gerar não toca golden, registro prospectivo nem vereditos do dossiê. Roda com os dados locais (CVM, COTAHIST, B3)."""
import hashlib
import json
import pathlib

import pytest
from dados_opcionais import requer_suplemento_b3

from relatorio.__main__ import gravar
from relatorio.modelo import NOTAS
from relatorio.montar import GOLDEN, montar

RAIZ = pathlib.Path(__file__).resolve().parents[2]
TEM_CVM = (RAIZ / "dados" / "cvm_series.json").exists()
requer_cvm = pytest.mark.skipif(not TEM_CVM, reason="dados/cvm_series.json fora do disco (dados brutos fora do git)")
INTOCADOS = [GOLDEN, RAIZ / "prospectivo" / "registro.jsonl", *sorted((RAIZ / "dossie" / "vereditos").glob("*.json"))]


def _hash(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


@pytest.fixture(scope="module")
def bbse3():
    return montar("BBSE3")


@pytest.fixture(scope="module")
def hype3():
    return montar("HYPE3")


def _todo_numero_tem_fonte_ou_motivo(rel):
    for n in rel.numeros():
        assert n.origens or (n.valor is None and n.obs), n.rotulo
        assert n.nota in NOTAS


@requer_cvm
def test_bbse3_bate_com_o_golden(bbse3):
    g = json.loads(GOLDEN.read_text(encoding="utf-8"))["tickers"]["BBSE3"]
    assert bbse3.palavra == g["palavra"]
    central = next(n for n in bbse3.secoes[0].numeros if n.rotulo == "Valor central")
    assert central.valor == pytest.approx(g["central"], abs=0.01)
    assert not any(a.startswith("DIVERGE") for a in bbse3.avisos)


@requer_cvm
def test_bbse3_central_sem_fonte_ab_e_avisado(bbse3):
    """DDM até o fim do contrato com probabilidade de renovação arbitrada (AUD-58): nota "—", e o cabeçalho diz."""
    central = next(n for n in bbse3.secoes[0].numeros if n.rotulo == "Valor central")
    assert central.nota == "—"
    assert any(a.startswith("O valor central depende") for a in bbse3.avisos)
    _todo_numero_tem_fonte_ou_motivo(bbse3)


@requer_cvm
def test_financeira_mostra_dcf_epv_oe_como_nao_aplicaveis(bbse3):
    preco = next(s for s in bbse3.secoes if s.titulo.startswith("Preço justo"))
    na = {n.rotulo for n in preco.numeros if n.valor is None}
    assert {"DCF", "EPV (Greenwald)", "Buffett — Owner Earnings"} <= na


@requer_cvm
@requer_suplemento_b3
def test_dossie_hype3_bate_com_o_veredito_gravado_e_e_todo_a(hype3):
    salvo = json.loads((RAIZ / "dossie" / "vereditos" / "HYPE3-2026-10-06.json").read_text(encoding="utf-8"))
    assert hype3.data == "2026-10-06"                      # a data-base é a do último veredito gravado
    assert hype3.palavra == salvo["palavra"]
    central = next(n for n in hype3.secoes[0].numeros if n.rotulo == "Valor central")
    assert central.nota == "A"
    _todo_numero_tem_fonte_ou_motivo(hype3)
    rotulos = {n.rotulo.split(" — ")[0] for s in hype3.secoes for n in s.numeros}
    assert {"DCF", "EPV (Greenwald)", "Buffett", "Graham", "Bazin"} <= rotulos


@requer_cvm
@requer_suplemento_b3
def test_gerar_nao_toca_veredito_nem_golden(tmp_path, bbse3, hype3):
    antes = [_hash(p) for p in INTOCADOS]
    for rel in (bbse3, hype3):
        md, js, pdf = gravar(rel, tmp_path)
        assert pdf.read_bytes().startswith(b"%PDF")
        assert md.read_text(encoding="utf-8").startswith(f"# {rel.tk} — ")
        json.loads(js.read_text(encoding="utf-8"))          # JSON válido (inf → null)
    assert [_hash(p) for p in INTOCADOS] == antes


@requer_cvm
def test_ticker_desconhecido_falha_com_o_que_falta():
    with pytest.raises(KeyError, match="ficha"):
        montar("ZZZZ3")
