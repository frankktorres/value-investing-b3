"""Blocos qualitativos e PDF: seis blocos por ticker, cada número com fonte e nota, nenhum CPF/nome de pessoa física, texto
livre só com fonte A/B e PDF que abre. Roda com os dados locais (CVM, FRE, COTAHIST, B3); pula sem eles."""
import json
import pathlib
import re

import pytest
from dados_opcionais import requer_suplemento_b3
from reportlab.platypus import Paragraph

from relatorio import quali, render_pdf
from relatorio.__main__ import gravar
from relatorio.modelo import NOTAS
from relatorio.montar import montar

RAIZ = pathlib.Path(__file__).resolve().parents[2]
requer_cvm = pytest.mark.skipif(not (RAIZ / "dados" / "cvm_series.json").exists(),
                                reason="dados/cvm_series.json fora do disco (dados brutos fora do git)")
requer_fre = pytest.mark.skipif(not (RAIZ / "dados" / "cvm" / "fre_2026.zip").exists(), reason="FRE 2026 fora do disco")
BLOCOS = ["Vantagem competitiva (moat)", "Gestão e alocação de capital", "Endividamento e solidez", "Governança e controlador",
          "Dividendos e JCP", "Riscos e bandeiras"]
CPF = re.compile(r"\d{3}\.\d{3}\.\d{3}-\d{2}|\*{3}\.\d{3}\.\d{3}-\*{2}")


@pytest.fixture(scope="module")
def bbse3():
    return montar("BBSE3")


@pytest.fixture(scope="module")
def hype3():
    return montar("HYPE3")


def _titulos(rel):
    return [s.titulo for s in rel.secoes]


@requer_cvm
@requer_fre
def test_bbse3_tem_os_seis_blocos_e_toda_linha_tem_fonte(bbse3):
    assert [t for t in _titulos(bbse3) if t in BLOCOS] == BLOCOS
    for s in bbse3.secoes:
        for n in s.numeros:
            assert n.origens or (n.valor is None and n.obs), (s.titulo, n.rotulo)
            assert n.nota in NOTAS


@requer_cvm
@requer_fre
def test_bbse3_financeira_diz_que_divida_nao_se_aplica_e_nota_e_arbitrada(bbse3):
    divida = next(s for s in bbse3.secoes if s.titulo.startswith("Endividamento"))
    assert any("Não se aplica a financeira" in t for t in divida.texto)
    moat = next(s for s in bbse3.secoes if s.titulo.startswith("Vantagem"))
    nota = next(n for n in moat.numeros if n.rotulo.startswith("Nota de moat"))
    assert nota.nota == "—"          # nota arbitrada do lote nunca vira A


@requer_cvm
@requer_fre
@requer_suplemento_b3
def test_bbse3_dividendos_da_b3_batem_com_a_media_do_lote(bbse3):
    div = next(s for s in bbse3.secoes if s.titulo.startswith("Dividendos"))
    media = next(n for n in div.numeros if n.rotulo.startswith("DPA médio dos últimos 5"))
    assert media.nota == "A"
    assert media.valor == pytest.approx(2.673, abs=0.01)         # dpa_medio_5a digitado no lote = média da B3


@requer_cvm
@requer_fre
@requer_suplemento_b3
def test_hype3_dossie_traz_notas_com_evidencia_e_bandeiras(hype3):
    assert [t for t in _titulos(hype3) if t in BLOCOS] == BLOCOS
    moat = next(s for s in hype3.secoes if s.titulo.startswith("Vantagem"))
    nota = next(n for n in moat.numeros if n.rotulo.startswith("Nota de moat"))
    assert nota.nota == "A" and "0 de 10" in nota.obs
    riscos = next(s for s in hype3.secoes if s.titulo.startswith("Riscos"))
    assert any("bandeira(s) disparada(s)" in t for t in riscos.texto)
    assert any(n.obs.startswith("DISPARA") for n in riscos.numeros)


@requer_cvm
@requer_fre
@requer_suplemento_b3
def test_relatorio_nao_tem_cpf_nem_nome_de_pessoa_fisica(bbse3, hype3, tmp_path):
    for rel in (bbse3, hype3):
        md, js, _ = gravar(rel, tmp_path)
        for arq in (md, js):
            txt = arq.read_text(encoding="utf-8")
            assert not CPF.search(txt)
            assert "Queiroz" not in txt and "Nelson" not in txt        # controlador e ex-diretor da HYPE3: PF não sai do FRE


@requer_cvm
@requer_fre
@requer_suplemento_b3
def test_pdf_abre_e_leva_os_seis_blocos(bbse3, hype3, tmp_path):
    for rel in (bbse3, hype3):
        pdf = render_pdf.render(rel, tmp_path / f"{rel.tk}.pdf")
        assert pdf.read_bytes().startswith(b"%PDF") and pdf.stat().st_size > 20_000
        titulos = {f.getPlainText() for f in render_pdf.historia(rel, 500) if isinstance(f, Paragraph)}
        assert set(BLOCOS) <= titulos


def test_texto_sem_fonte_ab_levanta(tmp_path, monkeypatch):
    monkeypatch.setattr(quali, "TEXTOS", tmp_path)
    (tmp_path / "ZZZZ3.json").write_text(json.dumps({"moat": {"valor": "marca forte", "fonte": "blog", "nota_fonte": "C"}}),
                                         encoding="utf-8")
    with pytest.raises(ValueError, match="sem fonte A/B"):
        quali.texto_extra("ZZZZ3", "moat")


def test_texto_com_fonte_b_entra_com_a_nota_da_fonte(tmp_path, monkeypatch):
    monkeypatch.setattr(quali, "TEXTOS", tmp_path)
    (tmp_path / "ZZZZ3.json").write_text(json.dumps({"moat": {"valor": "marca forte", "fonte": "RI 2025", "nota_fonte": "B"}}),
                                         encoding="utf-8")
    texto, origem = quali.texto_extra("ZZZZ3", "moat")
    assert texto == "marca forte" and origem.nota == "B"
    assert quali.texto_extra("ZZZZ3", "riscos") == (None, None)          # bloco sem texto: nada é inventado
    assert quali.texto_extra("OUTRO3", "moat") == (None, None)            # ticker sem arquivo
