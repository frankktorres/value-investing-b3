"""AUD-77: o quadro geral do `03` e o bloco do hall no prompt de sexta são gerados pelo motor (hall03.py);
a marca (S) não é mais digitada. Até a Onda 1.2: SUZB3, GGBR4, PRIO3 sem (S); KLBN11 e SLCE3 (NC) com (S)."""
from __future__ import annotations

from types import SimpleNamespace

import pytest

import hall03 as H


@pytest.fixture(scope="module")
def esp():
    return H.esperado()


def test_03_bate_com_o_motor(esp):
    div = H.divergencias(H.HALL.read_text(encoding="utf-8"), esp)
    assert not div, "\n".join(f"{tk} {c}: 03 {a} × motor {b}" for tk, c, a, b in div)


def test_prompt_de_sexta_tem_o_hall_do_motor(esp):
    bloco = H.bloco_do_prompt(H.PROMPT.read_text(encoding="utf-8"))
    assert bloco == H.lista_prompt(esp)
    assert "ISAE4" in bloco.split("NÃO CONCLUSIVO")[1]          # carteira sem palavra não tem preço de compra


def _item(preco, central, palavra, qualidade=False):
    r = dict(central=central, palavra=palavra, compra=0.7 * central, saida=(1.5 if qualidade else 1.3) * central,
             saida_por_qualidade=qualidade)
    return dict(empresa=SimpleNamespace(preco=preco), r=r)


def test_regra_da_marca_s_e_das_celulas():
    e = H.esperado({"CARA3": _item(13.0, 10.0, "CARA"), "ABAI3": _item(12.99, 10.0, "CARA"),
                    "NCNC3": _item(20.0, 10.0, "NÃO CONCLUSIVO"), "NEGA3": _item(11.2, -3.67, "NÃO CONCLUSIVO"),
                    "QUAL3": _item(14.0, 10.0, "CARA", qualidade=True)})
    assert e["CARA3"]["s"] and not e["ABAI3"]["s"]                # preço = saída já é (S), como no monitor
    assert not e["NCNC3"]["s"] and e["NCNC3"]["compra"] == e["NCNC3"]["saida"] == "n.a."
    assert e["NEGA3"]["pc"] == "n.d." and e["NEGA3"]["central"] == "-3,67"
    assert e["QUAL3"]["saida"] == "15,00 (1,50×)" and not e["QUAL3"]["s"]


MD = """## 1. Quadro

### CARA
| Ticker | Setor | Preço 02/10 | Central | P/C | Compra 0,70× | Saída 1,30× | Pendências v2 / motivo |
|---|---|---|---|---|---|---|---|
| CARA3 | X | 12,00 | **9,00 (onda 1.2)** | 1,33 | 6,30 | 11,70 | motivo sem marca |

### NÃO CONCLUSIVO
| Ticker | Setor | Preço 02/10 | Mediana das âncoras | P/C | Compra 0,70× | Saída 1,30× | Pendências v2 / motivo |
|---|---|---|---|---|---|---|---|
| NCNC3 | Y | 20,00 | **10,00 (v2)** | 2,00 | 7,00 | 13,00 | herdou (S) do tempo de CARA (S) |

## 2. Outra seção
| CARA3 | não é do quadro | 1,00 |
"""


def test_corrigir_e_idempotente_e_so_mexe_no_quadro():
    e = H.esperado({"CARA3": _item(13.0, 10.0, "CARA"), "NCNC3": _item(20.0, 10.0, "NÃO CONCLUSIVO")})
    assert {(tk, c) for tk, c, *_ in H.divergencias(MD, e)} == {
        ("CARA3", "preco"), ("CARA3", "central"), ("CARA3", "pc"), ("CARA3", "compra"), ("CARA3", "saida"),
        ("CARA3", "(S)"), ("NCNC3", "compra"), ("NCNC3", "saida"), ("NCNC3", "(S)")}
    novo = H.corrigir_texto(MD, e)
    assert H.divergencias(novo, e) == [] and H.corrigir_texto(novo, e) == novo
    assert "| CARA3 | X | 13,00 | **10,00 (onda 1.2)** | 1,30 | 7,00 | 13,00 | motivo sem marca (S) |" in novo
    # só a marca do fim sai; "(S) do tempo" no meio da frase é texto, não marca
    assert "| NCNC3 | Y | 20,00 | **10,00 (v2)** | 2,00 | n.a. | n.a. | herdou (S) do tempo de CARA |" in novo
    assert novo.endswith("| CARA3 | não é do quadro | 1,00 |\n")


def test_seção_errada_e_ticker_ausente_aparecem():
    e = H.esperado({"CARA3": _item(13.0, 10.0, "JUSTA"), "SUMI3": _item(1.0, 1.0, "CARA")})
    campos = {(tk, c) for tk, c, *_ in H.divergencias(MD, e)}
    assert ("CARA3", "seção") in campos and ("SUMI3", "ticker") in campos and ("NCNC3", "ticker") in campos


def test_corrigir_nao_corrompe_texto_livre():
    """Revisão do adversário (Onda 1.3): número fora do início da célula do central, sinal unicode e "(S)" no meio
    de uma frase não podem ser trocados em silêncio."""
    e = H.esperado({"CARA3": _item(13.0, 10.0, "CARA")})
    cab = ("## 1. Quadro\n\n### CARA\n| Ticker | Setor | Preço 02/10 | Central | P/C | Compra 0,70× | Saída 1,30× | "
           "Pendências v2 / motivo |\n|---|---|---|---|---|---|---|---|\n")
    md = cab + "| CARA3 | X | 13,00 | **era 12,00, agora 10,00** | 1,30 | 7,00 | 13,00 | segmento (S) do grupo Sul (S) |\n"
    assert ("CARA3", "central") in {(tk, c) for tk, c, *_ in H.divergencias(md, e)}     # não passa como igual
    novo = H.corrigir_texto(md, e)
    assert "segmento (S) do grupo Sul (S) |" in novo                                       # só a marca final conta
    md2 = cab + "| CARA3 | X | 13,00 | **−3,00** | 1,30 | 7,00 | 13,00 | x (S) |\n"
    assert ("CARA3", "central") in {(tk, c) for tk, c, *_ in H.divergencias(md2, e)}
    assert "−-" not in H.corrigir_texto(md2, e)
