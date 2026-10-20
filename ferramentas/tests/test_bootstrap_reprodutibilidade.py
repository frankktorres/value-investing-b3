"""AUD-38, AUD-73 e AUD-109 (auditoria de 08/10/2026): clone sem ZIPs roda; ZIPs conferem com o manifesto e o snapshot."""
import datetime as dt
import json
import pathlib
import subprocess
import sys

import pytest

import derivados_zip
import manifesto_cvm
import temporada

AQUI = pathlib.Path(__file__).resolve().parent.parent
TEM_ZIPS = all((derivados_zip.CVM / z).exists() for z in ("itr_2026.zip", "itr_2025.zip", "dfp_2025.zip", "fre_2026.zip"))
CHAVES = set(derivados_zip.CHAVES)


def test_snapshot_versionado_cobre_as_chaves_dos_lotes():
    snap = json.loads(derivados_zip.SNAPSHOT.read_text(encoding="utf-8"))
    assert CHAVES <= set(snap)
    assert set(snap["lote4.acoes_jun26"]) >= {"TIMS3", "VIVT3", "ITSA4", "FLRY3", "HYPE3", "ABEV3", "WEGE3", "ITUB"}
    assert all(v > 1e6 for v in snap["lote4.acoes_jun26"].values())
    assert set(snap["lote4.arrendamento_pago"]) == {"VIVT3", "WEGE3"}


def test_manifesto_versionado_lista_os_zips_que_os_lotes_leem():
    reg = manifesto_cvm.carregar()
    for z in ("itr_2026.zip", "itr_2025.zip", "fre_2026.zip", *[f"dfp_{a}.zip" for a in range(2019, 2026)]):
        assert z in reg and len(reg[z]["sha256"]) == 64 and reg[z]["bytes"] > 0


def test_import_dos_lotes_sem_zips_usa_o_snapshot():
    """Processo novo com dados/cvm vazio (sys.modules limpo): o import não pode levantar FileNotFoundError."""
    cod = ("import derivados_zip, pathlib, tempfile;"
           "derivados_zip.CVM = pathlib.Path(tempfile.mkdtemp());"
           "import lote4_saude_telecom as a, lote6_quimica as b;"
           "print(round(a.N['TIMS3']), round(b.N['LEVE3']), round(a.ITSA['acoes_itau']))")
    r = subprocess.run([sys.executable, "-c", cod], cwd=AQUI, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-1500:]
    assert "snapshot" in r.stderr


def test_obter_sem_zip_e_sem_snapshot_da_chave_da_a_receita(tmp_path, monkeypatch):
    monkeypatch.setattr(derivados_zip, "CVM", tmp_path)
    monkeypatch.setattr(derivados_zip, "SNAPSHOT", tmp_path / "nao_existe.json")
    with pytest.raises(FileNotFoundError, match="bootstrap_dados.py --baixar"):
        derivados_zip.obter("x", ["itr_2099.zip"], lambda: 1)


@pytest.mark.skipif(not TEM_ZIPS, reason="ZIPs da CVM ausentes (clone limpo): snapshot não é conferível aqui")
def test_snapshot_igual_ao_recalculo_dos_zips():
    import lote3_agro  # noqa: F401  (P/L histórico, fase 3 fatia 3)
    import lote4_saude_telecom  # noqa: F401  (o import recalcula e preenche CALCULADOS)
    import lote5_petroleo  # noqa: F401
    import lote6_quimica  # noqa: F401
    snap = json.loads(derivados_zip.SNAPSHOT.read_text(encoding="utf-8"))
    for chave in CHAVES:
        assert derivados_zip.CALCULADOS[chave] == snap[chave], f"{chave} defasada: rode `python bootstrap_dados.py --derivados`"


@pytest.mark.skipif(not TEM_ZIPS, reason="ZIPs da CVM ausentes (clone limpo): manifesto não é conferível aqui")
def test_zips_conferem_com_o_manifesto():
    r = manifesto_cvm.verificar()
    assert not r["diferem"], f"ZIP diferente do manifesto (a CVM reescreveu?): {r['diferem']}"


def test_verificar_aponta_diferem_faltam_e_sem_registro(tmp_path):
    (tmp_path / "a.zip").write_bytes(b"1")
    (tmp_path / "b.zip").write_bytes(b"2")
    (tmp_path / "c.zip").write_bytes(b"3")
    man = tmp_path / "M.json"
    manifesto_cvm.gerar(tmp_path, man)
    (tmp_path / "b.zip").write_bytes(b"22")
    (tmp_path / "c.zip").unlink()
    (tmp_path / "d.zip").write_bytes(b"4")
    r = manifesto_cvm.verificar(tmp_path, man)
    assert (r["ok"], r["diferem"], r["faltam"], r["sem_registro"]) == (["a.zip"], ["b.zip"], ["c.zip"], ["d.zip"])


def test_guardar_anterior_copia_datada_so_se_mudou(tmp_path):
    alvo, novo = tmp_path / "itr_2026.zip", tmp_path / "itr_2026.zip.novo"
    novo.write_bytes(b"v1")
    assert temporada.guardar_anterior(alvo, novo) is None              # não havia ZIP
    alvo.write_bytes(b"v1")
    assert temporada.guardar_anterior(alvo, novo) is None              # idêntico
    novo.write_bytes(b"v2")
    hoje = dt.date(2026, 10, 9)
    c1 = temporada.guardar_anterior(alvo, novo, hoje)
    c2 = temporada.guardar_anterior(alvo, novo, hoje)
    assert c1.name == "itr_2026_2026-10-09.zip" and c2.name == "itr_2026_2026-10-09_2.zip"
    assert c1.read_bytes() == b"v1" and alvo.read_bytes() == b"v1"      # a cópia é do anterior; o alvo é trocado pelo chamador


def test_import_do_universo_sem_zips_nao_vai_a_rede():
    """Adversário: `import universo` baixava itr_2026.zip sozinho (lote5). Sem ZIP e sem rede tem de importar pelo snapshot."""
    cod = ("import derivados_zip, coletar_cvm, pathlib, tempfile;"
           "t = pathlib.Path(tempfile.mkdtemp()); derivados_zip.CVM = t; coletar_cvm.CACHE = t;"
           "import requests; requests.get = lambda *a, **k: (_ for _ in ()).throw(RuntimeError('REDE'));"
           "import universo; print('ok', len(list(t.iterdir())))")
    r = subprocess.run([sys.executable, "-c", cod], cwd=AQUI, capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, r.stderr[-1500:]
    assert r.stdout.strip() == "ok 0"


def test_gravar_snapshot_exige_todas_as_chaves(monkeypatch):
    monkeypatch.setattr(derivados_zip, "CALCULADOS", {"lote4.itsa": {}})
    with pytest.raises(RuntimeError, match="snapshot não gravado"):
        derivados_zip.gravar_snapshot()


def test_baixar_itr_recusa_resposta_que_nao_e_zip(tmp_path, monkeypatch):
    import types

    import coletar_cvm
    import requests
    monkeypatch.setattr(coletar_cvm, "CACHE", tmp_path)
    monkeypatch.setattr(manifesto_cvm, "MANIFESTO", tmp_path / "M.json")
    (tmp_path / "itr_2026.zip").write_bytes(b"original")
    monkeypatch.setattr(requests, "get", lambda *a, **k: types.SimpleNamespace(content=b"<html>fora do ar</html>", raise_for_status=lambda: None))
    with pytest.raises(ValueError, match="não é um ZIP"):
        temporada.baixar_itr(2026)
    assert (tmp_path / "itr_2026.zip").read_bytes() == b"original"
    assert not (tmp_path / "itr_2026.zip.novo").exists() and not (tmp_path / "M.json").exists()
