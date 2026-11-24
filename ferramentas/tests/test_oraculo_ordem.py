"""Check `ordem` do oráculo (pré-registro v3, emenda 7): emenda em commit próprio, antes do motor que a cita. Repositório git
sintético numa pasta temporária; não depende do histórico do projeto."""
import pathlib
import subprocess

import pytest

from oraculo import ordem as O

PRE = "docs/PRE-REGISTRO-v3.md"
MOTOR = "ferramentas/motor_nao_financeiras.py"
BASE = "# Pré-registro\n\n## 7. Emendas\n1. **22/10/2026 — primeira.**\n"


def _g(repo, *a):
    subprocess.run(["git", "-c", "core.hooksPath=/dev/null", "-c", "user.name=t", "-c", "user.email=t@t", "-c",
                    "commit.gpgsign=false", *a], cwd=repo, check=True, capture_output=True)


def _escreve(repo, rel, texto):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(texto, encoding="utf-8", newline="\n")


def _commit(repo, msg, **arquivos):
    for rel, texto in arquivos.items():
        _escreve(repo, rel, texto)
        _g(repo, "add", rel)
    _g(repo, "commit", "-q", "-m", msg)


@pytest.fixture
def repo(tmp_path):
    _g(tmp_path, "init", "-q")
    _commit(tmp_path, "base", **{PRE: BASE, MOTOR: "x = 1\n"})
    corte = subprocess.run(["git", "rev-parse", "HEAD"], cwd=tmp_path, capture_output=True, text=True).stdout.strip()
    return tmp_path, corte


EMENDA2 = BASE + "2. **24/11/2026 — segunda.**\n"


def test_emenda_em_commit_proprio_antes_do_motor_passa(repo):
    r, corte = repo
    _commit(r, "pre-registro: emenda 2", **{PRE: EMENDA2})
    _commit(r, "motor pela emenda 2", **{MOTOR: "x = 2\n"})
    v = O.verificar(r, corte)
    assert v["status"] == "ok" and v["emendas"] == [1, 2], v


def test_emenda_no_mesmo_commit_do_motor_reprova(repo):
    r, corte = repo
    _commit(r, "motor e emenda 2 juntos", **{PRE: EMENDA2, MOTOR: "x = 2\n"})
    v = O.verificar(r, corte)
    assert v["status"] == "falha" and any("mistura" in p for p in v["problemas"]), v


def test_motor_antes_da_emenda_reprova(repo):
    r, corte = repo
    _commit(r, "motor pela emenda 2", **{MOTOR: "x = 2\n"})
    _commit(r, "pre-registro: emenda 2 (depois)", **{PRE: EMENDA2})
    v = O.verificar(r, corte)
    assert v["status"] == "falha" and any("cita emenda [2]" in p for p in v["problemas"]), v


def test_emenda_antiga_do_corte_vale_e_motor_sem_citar_passa(repo):
    r, corte = repo
    _commit(r, "motor: correção, emenda 1", **{MOTOR: "x = 3\n"})
    _commit(r, "motor: bug sem emenda", **{MOTOR: "x = 4\n"})
    assert O.verificar(r, corte)["status"] == "ok"


def test_arvore_nao_commitada_com_os_dois_reprova(repo):
    r, corte = repo
    _escreve(r, PRE, EMENDA2)
    _escreve(r, MOTOR, "x = 9\n")
    v = O.verificar(r, corte)
    assert v["status"] == "falha" and any("não commitada" in p for p in v["problemas"]), v


def test_corte_fora_do_historico_quebra_alto(repo):
    r, _ = repo
    with pytest.raises(RuntimeError):
        O.verificar(r, "0" * 40)


def test_corte_real_esta_no_historico_do_projeto():
    raiz = pathlib.Path(__file__).resolve().parents[2]
    assert O.verificar(raiz)["status"] in ("ok", "falha")      # roda sem erro de git; o status é o do `python -m oraculo`


@pytest.mark.parametrize("msg, nums", [("emendas 4 e 5", {4, 5}), ("emenda 7, motor", {7}), ("sem citação", set()),
                                       ("Emenda 12)", {12}), ("emendas 2–4", {2, 3, 4}), ("emendas 2 a 3", {2, 3}),
                                       ("emenda nº 9", {9}), ("emenda-9", {9}), ("Emenda #9", {9}),
                                       # data na mensagem não é emenda (adversário, 24/11)
                                       ("segue a emenda 1, 24/11/2026", {1}), ("emenda 1 e 2026 ajustes", {1})])
def test_citadas(msg, nums):
    assert O.citadas(msg) == nums


# ---------------------------------------------------------------- escapes do adversário (24/11/2026)
NL = "\n"


def test_qualquer_arquivo_que_cita_emenda_inexistente_reprova(repo):
    r, corte = repo
    _commit(r, "credito: spread pela emenda 9", **{"ferramentas/credito.py": "s = 1" + NL})
    _commit(r, "lote novo, emenda 9", **{"ferramentas/lote10_novos.py": "x = 1" + NL})
    v = O.verificar(r, corte)
    assert v["status"] == "falha" and len(v["problemas"]) == 2, v


def test_emenda_fora_do_paragrafo_7_nao_registra(repo):
    r, corte = repo
    texto = NL.join(["# Pré-registro", "9. **24/11/2026 — fora.**", "", "## 7. Emendas", "1. **22/10/2026 — primeira.**", ""])
    _commit(r, "pre: item fora do §7", **{PRE: texto})
    _commit(r, "motor pela emenda 9", **{MOTOR: "x = 2" + NL})
    assert O.verificar(r, corte)["status"] == "falha"


def test_emenda_sem_negrito_registra_e_apagada_deixa_de_valer(repo):
    r, corte = repo
    _commit(r, "pre: emenda 2", **{PRE: BASE + "2. 24/11/2026 — sem negrito." + NL})
    _commit(r, "motor pela emenda 2", **{MOTOR: "x = 2" + NL})
    assert O.verificar(r, corte)["status"] == "ok"
    _commit(r, "pre: apaga a 2", **{PRE: BASE})
    _commit(r, "motor de novo pela emenda 2", **{MOTOR: "x = 3" + NL})
    assert O.verificar(r, corte)["status"] == "falha"


@pytest.mark.parametrize("cenario", ["renomeia", "novo_motor", "novo_pre"])
def test_arvore_com_renomeacao_ou_arquivo_novo_reprova(repo, cenario):
    r, corte = repo
    if cenario == "renomeia":
        _escreve(r, PRE, EMENDA2)
        _g(r, "mv", MOTOR, "ferramentas/motor_x.py")
    elif cenario == "novo_motor":
        _escreve(r, PRE, EMENDA2)
        _escreve(r, "ferramentas/motor_bancos.py", "x = 1" + NL)
    else:
        _escreve(r, "docs/PRE-REGISTRO-v4.md", BASE)
        _escreve(r, MOTOR, "x = 9" + NL)
    assert O.verificar(r, corte)["status"] == "falha"


def test_merge_que_edita_pre_e_motor_reprova(repo):
    r, corte = repo
    _g(r, "checkout", "-q", "-b", "lado")
    _commit(r, "lado", **{"docs/outro.md": "x" + NL})
    _g(r, "checkout", "-q", "-")
    _commit(r, "principal", **{"docs/mais.md": "y" + NL})
    _g(r, "merge", "--no-ff", "--no-commit", "lado")
    _escreve(r, PRE, EMENDA2)
    _escreve(r, MOTOR, "x = 5" + NL)
    _g(r, "add", PRE, MOTOR)
    _g(r, "commit", "-q", "-m", "merge")
    v = O.verificar(r, corte)
    assert v["status"] == "falha" and any("mistura" in p for p in v["problemas"]), v


def test_caminho_com_espaco(repo):
    r, corte = repo
    _commit(r, "junto", **{"docs/PRE-REGISTRO-v3 b.md": BASE, MOTOR: "x = 2" + NL})
    assert O.verificar(r, corte)["status"] == "falha"
