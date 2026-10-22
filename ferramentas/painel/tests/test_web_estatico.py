"""Tela v0.2 (web/): guarda das regras do HANDOFF que dá para conferir sem navegador — dado só por textContent, nada de
fora da máquina, nenhum fator de valuation fixo no front (vêm de hall.fatores), leitura só do contrato."""
import pathlib
import re

import pytest

WEB = pathlib.Path(__file__).resolve().parents[1] / "web"
JS = sorted(p for p in WEB.rglob("*.js") if "dados" not in p.parts)
TEXTO = JS + sorted(WEB.glob("*.html")) + sorted(WEB.glob("*.css"))


def _sem_comentarios(txt: str) -> str:
    """Tira só comentário de bloco e linha que É comentário: `//` no meio da linha pode estar dentro de string, e cortar
    ali esconderia o resto da linha do teste."""
    txt = re.sub(r"/\*.*?\*/", "", txt, flags=re.S)
    return re.sub(r"^\s*//.*$", "", txt, flags=re.M)


def test_tem_as_quatro_telas():
    assert {p.name for p in (WEB / "telas").glob("*.js")} >= {"hall.js", "empresa.js", "carteira.js", "monitor.js", "sistema.js"}


@pytest.mark.parametrize("arq", JS, ids=lambda p: p.name)
def test_dado_so_por_textcontent(arq):
    txt = _sem_comentarios(arq.read_text(encoding="utf-8"))
    for proibido in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"):
        assert proibido not in txt, f"{arq.name}: {proibido}"


@pytest.mark.parametrize("arq", TEXTO, ids=lambda p: p.name)
def test_nada_sai_da_maquina(arq):
    txt = _sem_comentarios(arq.read_text(encoding="utf-8"))
    urls = [u for u in re.findall(r"https?://[^\s'\")]+", txt) if not u.startswith("http://www.w3.org/2000/svg")]
    assert not urls, f"{arq.name}: {urls}"


@pytest.mark.parametrize("arq", JS, ids=lambda p: p.name)
def test_sem_fator_de_valuation_fixo(arq):
    """Compra 0,70×, parcial 0,80×, saída 1,30×/1,50× e a mediana do central vêm do motor (hall.fatores)."""
    txt = _sem_comentarios(arq.read_text(encoding="utf-8"))
    assert not re.search(r"(?<![\d.])(0?\.[78]0*|1\.[35]0*)(?![\d])", txt), f"{arq.name}: fator fixo"
    assert not re.search(r"(?<![\d.])(7|8|13|15)\s*/\s*10(?![\d])", txt), f"{arq.name}: fator em fração"
    assert not re.search(r"median\w*\s*\(", txt, flags=re.I), f"{arq.name}: mediana"
    # régua fabricada: central × fator, ou fator × central (compra/saída só chegam prontas do contrato)
    assert not re.search(r"central\s*\*|\*\s*[\w.]*central\b", txt), f"{arq.name}: multiplica o central"
    assert not re.search(r"\*\s*[\w.]*\b(compra|saida|fator_saida|saida_qualidade)\b", txt), f"{arq.name}: multiplica fator"


@pytest.mark.parametrize("arq", JS, ids=lambda p: p.name)
def test_estilo_so_por_cssom(arq):
    """A CSP do servidor (`style-src 'self'`) bloqueia estilo inline: só `el.style` (CSSOM) funciona."""
    txt = _sem_comentarios(arq.read_text(encoding="utf-8"))
    assert not re.search(r"setAttribute\(\s*['\"]style|createElement\(\s*['\"]style|cssText\s*=", txt), arq.name


def test_le_so_o_contrato():
    txt = (WEB / "app.js").read_text(encoding="utf-8")
    caminhos = re.findall(r"['`](dados/[^'`]+)['`]", txt)
    assert caminhos and all(c.startswith(("dados/contrato/", "dados/privado/")) for c in caminhos), caminhos
    for arq in JS:
        if arq.name != "app.js":
            assert "fetch(" not in arq.read_text(encoding="utf-8"), arq.name


def test_fontes_locais_e_tema_escuro_padrao():
    html = (WEB / "index.html").read_text(encoding="utf-8")
    assert 'data-tema="escuro"' in html
    css = (WEB / "estilo.css").read_text(encoding="utf-8")
    for f in re.findall(r"url\((fontes/[^)]+)\)", css):
        assert (WEB / f).exists(), f
    assert "Space Grotesk" in css


def test_carteira_valor_em_texto_respeita_ocultar():
    """N6 (QA 21/10): valor da carteira interpolado em texto (`${ct.x.valor}`) precisa do desvio `o ? '•••'`; o caminho
    normal é passar por pessoal(...). O DY líquido 12m vazava com "Ocultar valores" ligado."""
    txt = _sem_comentarios((WEB / "telas" / "carteira.js").read_text(encoding="utf-8"))
    vazam = [e for e in re.findall(r"\$\{([^}]*)\}", txt)
             if re.search(r"\bct\.\w+\.valor\b", e) and not re.match(r"\s*(o|c\.ocultar)\s*\?", e)]
    assert not vazam, vazam
    assert re.search(r"pessoal\(pct\(ct\.dy_liquido_12m\.valor\), o\)", txt)


def test_guardas_de_formato_do_contrato_na_casca():
    """N9: contrato sem `versao`, `hall.json` sem `fatores`/`escala_regua` e hash desconhecido viram faixa de erro, não TypeError
    nem Hall calado."""
    txt = _sem_comentarios((WEB / "app.js").read_text(encoding="utf-8"))
    assert "j.versao === undefined" in txt and "não informa a versão" in txt
    assert "hl.dado.fatores" in txt and "escala_regua" in txt and "está incompleto" in txt
    assert "ROTAS.includes(r.id)" in txt and "não existe" in txt


def test_sistema_na_rota_no_menu_e_so_le_o_contrato():
    """N4: a folha do sistema é rota real (sem o "em breve") e lê só `dados/contrato/sistema.json`."""
    html = (WEB / "index.html").read_text(encoding="utf-8")
    app = _sem_comentarios((WEB / "app.js").read_text(encoding="utf-8"))
    assert "em breve" not in html and 'data-rota="sistema"' in html
    assert "'sistema'" in app and "dados/contrato/sistema.json" in app and "telaSistema" in app
