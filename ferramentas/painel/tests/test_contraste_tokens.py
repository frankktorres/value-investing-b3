"""N5 (etapa 4 da tela v0.2, parte automática): razão de contraste WCAG 2.x dos pares texto × fundo de `web/tokens.css` nos temas
claro e escuro. Texto ≥ 4,5:1; gráfico/UI ≥ 3:1. Cor não é trocada aqui (visual é decisão do Frank): contorno abaixo de 3:1
precisa estar listado em CONTORNOS_ABAIXO_DE_3; o teste falha se a lista mudar (cor nova ou corrigida)."""
import pathlib
import re

import pytest

TOKENS = pathlib.Path(__file__).resolve().parents[1] / "web" / "tokens.css"
TEXTO = ("--ink", "--ink2", "--ink3", "--ac", "--barata-fg", "--justa-fg", "--cara-fg", "--nc-fg")
FUNDOS = ("--bg", "--sf", "--sf2")
PAR_PROPRIO = {"--barata-fg": "--barata-bg", "--cara-fg": "--cara-bg"}        # texto de chip sobre o fundo do chip
GRAFICO = ("--serie-div", "--serie-jcp")
CONTORNOS = ("--ln2", "--barata-ln", "--cara-ln", "--justa-ln", "--nc-ln")
# (tema, contorno, fundo) abaixo de 3:1 — vazio desde a paleta v0.3 (22/10/2026, pedido do Frank de refazer as cores);
# a lista de 14 pares da paleta anterior (PENDENTE #10) foi resolvida subindo os contornos
CONTORNOS_ABAIXO_DE_3: set[tuple[str, str, str]] = set()


def _temas() -> dict[str, dict[str, str]]:
    css = re.sub(r"/\*.*?\*/", "", TOKENS.read_text(encoding="utf-8"), flags=re.S)
    temas: dict[str, dict[str, str]] = {"escuro": {}, "claro": {}}
    for sel, corpo in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        vs = dict(re.findall(r"(--[\w-]+)\s*:\s*(#[0-9A-Fa-f]{6})\b", corpo))
        alvo = [t for t in temas if f'[data-tema="{t}"]' in sel] or (["escuro"] if ":root" in sel else [])
        for t in alvo:
            temas[t].update(vs)
    return temas


def luminancia(hexa: str) -> float:
    c = [int(hexa[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def razao(a: str, b: str) -> float:
    claro, escuro = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (claro + 0.05) / (escuro + 0.05)


TEMAS = _temas()


def test_razao_wcag_conhecida():
    assert razao("#000000", "#FFFFFF") == pytest.approx(21.0)
    assert razao("#777777", "#FFFFFF") == pytest.approx(4.48, abs=0.02)         # o clássico cinza que reprova por pouco


def test_tokens_lidos_nos_dois_temas():
    for t in ("escuro", "claro"):
        assert {*TEXTO, *FUNDOS, *GRAFICO, *CONTORNOS, "--barata-bg", "--cara-bg"} <= set(TEMAS[t]), t


@pytest.mark.parametrize("tema", ["escuro", "claro"])
def test_texto_tem_4_5_para_1_nos_fundos(tema):
    v, ruins = TEMAS[tema], []
    for fg in TEXTO:
        for bg in (*FUNDOS, *([PAR_PROPRIO[fg]] if fg in PAR_PROPRIO else [])):
            if razao(v[fg], v[bg]) < 4.5:
                ruins.append((fg, bg, round(razao(v[fg], v[bg]), 2)))
    assert not ruins, f"texto abaixo de 4,5:1 no tema {tema} (listar em PENDENTE-FRANK, sem trocar cor): {ruins}"


@pytest.mark.parametrize("tema", ["escuro", "claro"])
def test_series_do_grafico_tem_3_para_1(tema):
    v = TEMAS[tema]
    ruins = [(g, bg, round(razao(v[g], v[bg]), 2)) for g in GRAFICO for bg in ("--bg", "--sf") if razao(v[g], v[bg]) < 3.0]
    assert not ruins, ruins


def test_contornos_abaixo_de_3_sao_so_os_registrados():
    achados = {(t, c, bg) for t, v in TEMAS.items() for c in CONTORNOS for bg in ("--bg", "--sf") if razao(v[c], v[bg]) < 3.0}
    assert achados == CONTORNOS_ABAIXO_DE_3, (
        f"novos: {sorted(achados - CONTORNOS_ABAIXO_DE_3)}; corrigidos: {sorted(CONTORNOS_ABAIXO_DE_3 - achados)} "
        "— atualize a lista e a pendência #10 em docs/PENDENTE-FRANK.md")
