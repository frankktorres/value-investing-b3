"""Trava da pasta `UPLOAD CLAUDE DESKTOP/` (26/11/2026): a cópia bate com o MANIFESTO, a fonte no repo também (doc mudou
sem rodar o gerador → reprova), nada fora do MANIFESTO e nenhum segredo. Conserto: `cd ferramentas && python -m
desktop.atualizar` (ou `ATUALIZAR.bat`) e commitar a pasta. Canários: segredo inventado e hash adulterado reprovam."""
import pathlib

import pytest

from desktop import atualizar as A

CONSERTO = "rode `cd ferramentas && python -m desktop.atualizar` (ou ATUALIZAR.bat) e commite a pasta"
LINHAS = A.ler_manifesto()


def test_manifesto_existe_e_cobre_a_lista():
    assert LINHAS, f"MANIFESTO.txt ausente ou vazio: {CONSERTO}"
    esperado = {n for _, n, _ in A.COPIAS} | set(A.GERADOS)
    assert {x["arquivo"] for x in LINHAS} == esperado, CONSERTO


def test_nada_fora_do_manifesto():
    na_pasta = {p.name for p in A.DESTINO.iterdir() if p.is_file()} - {A.MANIFESTO.name}
    assert na_pasta == {x["arquivo"] for x in LINHAS}, f"arquivo sobrando/faltando na pasta: {CONSERTO}"


@pytest.mark.parametrize("x", LINHAS, ids=lambda x: x["arquivo"])
def test_copia_igual_ao_manifesto(x):
    assert A.hash_arquivo(A.DESTINO / x["arquivo"]) == x["sha256"], f"{x['arquivo']} difere do MANIFESTO: {CONSERTO}"


@pytest.mark.parametrize("x", [x for x in LINHAS if x["origem"] != "gerador"], ids=lambda x: x["arquivo"])
def test_fonte_igual_a_copia(x):
    assert A.hash_arquivo(A.RAIZ / x["origem"]) == x["sha256"], f"{x['origem']} mudou depois da cópia: {CONSERTO}"


def test_sem_segredo_na_pasta():
    achados = [s for p in A.DESTINO.iterdir() if p.is_file() for s in A.segredos(p.name, p.read_bytes())]
    assert not achados, achados


@pytest.mark.parametrize("nome,conteudo", [
    ("x.md", b"chave: sk-ant-api03-AAAAAAAAAAAAAAAAAAAAAAAA"),
    ("x.md", b"token = ghp_abcdefghijklmnopqrstuvwxyz0123456789"),
    ("x.txt", b"-----BEGIN RSA PRIVATE KEY-----"),
    ("x.md", b"API_KEY=abcdefghijklmnopqrstuvwxyz123456"),
    (".env", b"nada"),
    ("carteira.local.json", b"{}"),
])
def test_canario_segredo_reprova(nome, conteudo):
    assert A.segredos(nome, conteudo)


def test_canario_texto_comum_passa():
    assert not A.segredos("x.md", "O token do Ke é a taxa; senha: ver cofre. api_key fica no .env".encode())


def test_canario_hash_adulterado(tmp_path):
    p = tmp_path / "a.md"
    p.write_bytes(b"linha\r\n")
    q = tmp_path / "b.md"
    q.write_bytes(b"linha\n")
    assert A.hash_arquivo(p) == A.hash_arquivo(q)               # CRLF da máquina = LF da nuvem
    q.write_bytes(b"linha!\n")
    assert A.hash_arquivo(p) != A.hash_arquivo(q)


def test_canario_manifesto(tmp_path):
    m = tmp_path / "M.txt"
    m.write_text("cab\n\n# arquivo\torigem\tdata\tsha256\na.md\tdocs/a.md\t2026-11-26\tabc\n\n## fim\n", encoding="utf-8")
    assert A.ler_manifesto(m) == [dict(arquivo="a.md", origem="docs/a.md", data="2026-11-26", sha256="abc")]
    assert pathlib.Path(A.RAIZ / "ferramentas" / "desktop" / "atualizar.py").exists()
