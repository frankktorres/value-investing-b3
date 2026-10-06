"""Portão de isolamento: o backtest não toca o motor de hoje nem o dado de 2026.

Duas camadas.

ESTÁTICA (por AST, não por grep — grep daria falso positivo em `liquidez_mes_base`): nenhum módulo
do backtest pode importar de `inflacao` algo além de `fator_entre` e `fator_idade`, nem citar por
literal os arquivos de dados de 2026, nem chamar `extractall`.

DINÂMICA: com um sentinela em `builtins.open` e `Path.open`, exercitar o backtest e afirmar que
nenhuma abertura em modo de escrita acontece fora de `backtest/dados/` e que nenhum arquivo
proibido é lido.

Por que isso é teste e não regra escrita: a restrição "não quebrar a regressão" e a defesa contra
look-ahead são a MESMA coisa aqui. `inflacao.DEFLATOR` e companhia estão ancorados no último mês da
série (hoje): usá-los numa data de 2015 corrigiria o imobilizado por 11 anos de IPCA futuro, em
silêncio. `cvm_series.json` e `series_*.json` são a coleta de 2026 (chave literal `ltm_2T26`).
"""
from __future__ import annotations

import ast
import builtins
import pathlib

import pytest

PACOTE = pathlib.Path(__file__).resolve().parent.parent
DADOS_BT = (PACOTE / "dados").resolve()

# NADA de `ferramentas/inflacao.py` entra no backtest. Mesmo `fator_entre`, que parece datado, usa
# MEDIA_ANO[ano] = média dos 12 meses do exercício — em T = 30/06/2020 isso é meio ano de inflação
# futura. O backtest tem `inflacao_pit.py`, que lê a mesma fonte A (SGS 433) e trunca no último mês
# público em T.
INFLACAO_PERMITIDO: set[str] = set()

# Nomes de arquivo da coleta de 2026. Proibidos no runtime do backtest.
ARQUIVOS_PROIBIDOS = ("cvm_series.json", "series_2026", "golden.json")

# Módulos do motor de hoje que carregam dado de 2026 no import, ou que trazem premissa digitada.
IMPORTS_PROIBIDOS = {"motor_nao_financeiras", "universo", "defasagem", "rodar_tudo", "golden"}

# `experimento/proxy.py` lê tests/golden.json de propósito, read-only (é o erro de proxy da
# fatia 12). É a ÚNICA exceção, e está alistada aqui para que a exceção seja visível.
ISENTOS_GOLDEN = {"proxy.py"}


def modulos_do_backtest() -> list[pathlib.Path]:
    return sorted(p for p in PACOTE.rglob("*.py")
                  if "tests" not in p.relative_to(PACOTE).parts and p.name != "__init__.py")


def _arvore(p: pathlib.Path) -> ast.Module:
    return ast.parse(p.read_text(encoding="utf-8"), filename=str(p))


def _ids_de_docstring(arvore: ast.Module) -> set[int]:
    """Nós Constant que são docstring de módulo, classe ou função.

    A proibição é sobre CÓDIGO que abre os arquivos de 2026, não sobre prosa que explica a
    proibição — e explicar por que a cópia existe exige nomear `cvm_series.json`. Sem isto, o teste
    acusava o próprio comentário que documenta a regra.
    """
    ids = set()
    for no in ast.walk(arvore):
        corpo = getattr(no, "body", None)
        if isinstance(no, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and corpo:
            primeiro = corpo[0]
            if isinstance(primeiro, ast.Expr) and isinstance(primeiro.value, ast.Constant) \
                    and isinstance(primeiro.value.value, str):
                ids.add(id(primeiro.value))
    return ids


@pytest.mark.parametrize("modulo", modulos_do_backtest(), ids=lambda p: p.name)
def test_usa_so_a_inflacao_datada(modulo: pathlib.Path) -> None:
    """De `inflacao`, só `fator_entre` e `fator_idade` — as duas que recebem a data."""
    arvore = _arvore(modulo)
    usados: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.ImportFrom) and no.module == "inflacao":
            usados |= {a.name for a in no.names}
        elif isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name) and no.value.id == "inflacao":
            usados.add(no.attr)
    proibidos = usados - INFLACAO_PERMITIDO
    assert not proibidos, (
        f"{modulo.name} usa de inflacao: {sorted(proibidos)}. "
        "Esses são ancorados no último mês da série (hoje) e trazem IPCA futuro para dentro de "
        "uma decisão passada. Use fator_entre/fator_idade, que recebem a data."
    )


@pytest.mark.parametrize("modulo", modulos_do_backtest(), ids=lambda p: p.name)
def test_nao_importa_o_motor_acoplado_a_2026(modulo: pathlib.Path) -> None:
    arvore = _arvore(modulo)
    importados: set[str] = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            importados |= {a.name.split(".")[0] for a in no.names}
        elif isinstance(no, ast.ImportFrom) and no.module and no.level == 0:
            importados.add(no.module.split(".")[0])
    proibidos = importados & IMPORTS_PROIBIDOS
    assert not proibidos, (
        f"{modulo.name} importa {sorted(proibidos)}. motor_nao_financeiras carrega 1 MB de dado de "
        "2026 no import; universo/lote* trazem premissa digitada à mão em out/2026."
    )


@pytest.mark.parametrize("modulo", modulos_do_backtest(), ids=lambda p: p.name)
def test_nao_cita_arquivo_de_2026(modulo: pathlib.Path) -> None:
    arvore = _arvore(modulo)
    docstrings = _ids_de_docstring(arvore)
    for no in ast.walk(arvore):
        if isinstance(no, ast.Constant) and isinstance(no.value, str) and id(no) not in docstrings:
            for proibido in ARQUIVOS_PROIBIDOS:
                if proibido in no.value and modulo.name not in ISENTOS_GOLDEN:
                    pytest.fail(f"{modulo.name}:{no.lineno} cita {proibido!r} — dado da coleta de 2026")


def test_a_checagem_de_arquivo_proibido_nao_e_vaga() -> None:
    """Meta-teste: isentar docstring não pode ter desligado a checagem de código.

    Sem isto, um dia alguém "conserta" o teste acima isentando tudo e ele passa a aprovar qualquer
    coisa em silêncio — que é pior do que não ter teste.
    """
    codigo_ruim = 'x = open("dados/cvm_series.json")'
    arvore = ast.parse(codigo_ruim)
    docstrings = _ids_de_docstring(arvore)
    achou = [n.value for n in ast.walk(arvore)
             if isinstance(n, ast.Constant) and isinstance(n.value, str)
             and id(n) not in docstrings
             and any(p in n.value for p in ARQUIVOS_PROIBIDOS)]
    assert achou, "a checagem deixou passar uma abertura literal de cvm_series.json"

    docstring_ok = '"""Explica por que não se usa cvm_series.json."""'
    arvore2 = ast.parse(docstring_ok)
    docstrings2 = _ids_de_docstring(arvore2)
    achou2 = [n.value for n in ast.walk(arvore2)
              if isinstance(n, ast.Constant) and isinstance(n.value, str)
              and id(n) not in docstrings2
              and any(p in n.value for p in ARQUIVOS_PROIBIDOS)]
    assert not achou2, "a checagem está acusando docstring, que é prosa e não abre arquivo"


@pytest.mark.parametrize("modulo", modulos_do_backtest(), ids=lambda p: p.name)
def test_nao_usa_import_dinamico(modulo: pathlib.Path) -> None:
    """Fecha o furo da checagem estática: import dinâmico escapa do AST.

    `importlib.import_module("motor_nao_financeiras")`, `__import__`, `getattr(mod, nome)`,
    `eval` e `exec` permitiriam ler o dado de 2026 sem que `test_nao_importa_o_motor_acoplado_a_2026`
    ou `test_nao_cita_arquivo_de_2026` vissem nada. Proibir é mais barato que detectar.
    """
    arvore = _arvore(modulo)
    for no in ast.walk(arvore):
        if isinstance(no, ast.Name) and no.id in {"__import__", "eval", "exec"}:
            pytest.fail(f"{modulo.name}:{no.lineno} usa {no.id} — import/execução dinâmica")
        if isinstance(no, ast.Attribute) and isinstance(no.value, ast.Name) \
                and no.value.id == "importlib":
            pytest.fail(f"{modulo.name}:{no.lineno} usa importlib — import dinâmico")
        if isinstance(no, (ast.Import, ast.ImportFrom)):
            nomes = ([a.name for a in no.names] if isinstance(no, ast.Import)
                     else [no.module or ""])
            if any(n.split(".")[0] == "importlib" for n in nomes):
                pytest.fail(f"{modulo.name}:{no.lineno} importa importlib")


@pytest.mark.parametrize("modulo", modulos_do_backtest(), ids=lambda p: p.name)
def test_nao_descompacta_zip_inteiro(modulo: pathlib.Path) -> None:
    """COTAHIST descompactado passa de 250 MB por ano e só há 19,7 GB livres: leitura é streaming."""
    arvore = _arvore(modulo)
    for no in ast.walk(arvore):
        if isinstance(no, ast.Attribute) and no.attr == "extractall":
            pytest.fail(f"{modulo.name}:{no.lineno} chama extractall — ler em streaming do ZIP")


# ------------------------------------------------------------------------------------- dinâmica
class Sentinela:
    """Registra toda abertura de arquivo durante o trecho exercitado."""

    def __init__(self) -> None:
        self.escritas: list[str] = []
        self.leituras: list[str] = []

    def registrar(self, caminho, modo: str) -> None:
        try:
            p = pathlib.Path(caminho).resolve()
        except (TypeError, ValueError, OSError):
            return
        (self.escritas if any(c in modo for c in "wxa+") else self.leituras).append(str(p))


@pytest.fixture
def sentinela(monkeypatch: pytest.MonkeyPatch) -> Sentinela:
    s = Sentinela()
    open_real, path_open_real = builtins.open, pathlib.Path.open

    # O modo chega posicional ou por keyword: Path.read_text() chama self.open(mode='r', ...).
    # Capturar só posicional dá "got multiple values for argument 'mode'".
    def _modo(a: tuple, kw: dict) -> str:
        return a[0] if a else kw.get("mode", "r")

    def open_vigiado(arquivo, *a, **kw):
        s.registrar(arquivo, _modo(a, kw))
        return open_real(arquivo, *a, **kw)

    def path_open_vigiado(self, *a, **kw):
        s.registrar(self, _modo(a, kw))
        return path_open_real(self, *a, **kw)

    monkeypatch.setattr(builtins, "open", open_vigiado)
    monkeypatch.setattr(pathlib.Path, "open", path_open_vigiado)
    return s


def test_importar_e_usar_o_backtest_nao_escreve_fora_de_dados(sentinela: Sentinela) -> None:
    """Exercita o que já existe do backtest e exige zero escrita fora de backtest/dados/."""
    from backtest import calendario, config

    cfg = config.Config()
    config.hash_config(cfg)
    for d in cfg.datas_corte:
        calendario.mes_ipca_disponivel(d)
        calendario.janela_de(d, cfg)
        calendario.horizonte_fim(d, 5)
        config.limite_liquidez(cfg, d)

    fora = [c for c in sentinela.escritas if DADOS_BT not in pathlib.Path(c).parents]
    assert not fora, f"escreveu fora de backtest/dados/: {fora}"


def test_nao_le_dado_de_2026(sentinela: Sentinela) -> None:
    from backtest import calendario, config

    cfg = config.Config()
    config.limite_liquidez(cfg, "2020-06-30")
    calendario.estrato_de(10, cfg)

    sujas = [c for c in sentinela.leituras
             if any(p in pathlib.Path(c).name for p in ARQUIVOS_PROIBIDOS)]
    assert not sujas, f"leu dado da coleta de 2026: {sujas}"


@pytest.mark.skipif(not (PACOTE / "dados" / "fatos_cvm.parquet").exists(),
                    reason="fatos_cvm.parquet ausente")
def test_o_caminho_do_ledger_tambem_nao_toca_o_dado_de_2026(sentinela: Sentinela) -> None:
    """Fecha o segundo furo: a camada dinâmica exercitava só config e calendario.

    O caminho que de fato lê disco é o do ledger — `pit.ledger_em` puxa `indice_cvm` e o parquet de
    fatos. Sem exercitá-lo sob o sentinela, uma leitura de `cvm_series.json` dentro de `ledger_em`
    passaria batido pela parte dinâmica, e o AST só veria um literal.
    """
    from backtest.ledger import pit

    for f in (pit._fatos, pit._acoes, pit._por_companhia, pit._visiveis):
        f.cache_clear()
    for cd in (1023, 15539):
        pit.ledger_em(cd, "2020-06-30")
        pit.ledger_em(cd, "2020-06-30", pit.FINANCEIRO)

    sujas = [c for c in sentinela.leituras
             if any(p in pathlib.Path(c).name for p in ARQUIVOS_PROIBIDOS)]
    assert not sujas, f"o ledger leu dado da coleta de 2026: {sujas}"
    fora = [c for c in sentinela.escritas if DADOS_BT not in pathlib.Path(c).parents]
    assert not fora, f"o ledger escreveu fora de backtest/dados/: {fora}"
