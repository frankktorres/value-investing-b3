"""AUD-24 (série vigente explícita) e AUD-26 (estado compartilhado do lote 4 não depende da ordem de import)."""
import copy
import hashlib
import json
import pathlib
import re
import subprocess
import sys

import pytest

import series_vigente

RAIZ = pathlib.Path(__file__).resolve().parent.parent


def test_aud24_vigente_cobre_o_universo():
    assert len(series_vigente.carregar()) >= series_vigente.TICKERS_ESPERADOS


def test_aud24_parcial_nao_vira_o_vigente(tmp_path):
    """Um series_ parcial mais novo na pasta não pode ser o escolhido; um vigente parcial é recusado no import."""
    cheio = series_vigente.carregar()
    (tmp_path / "series_2026-10-05.json").write_text(json.dumps(cheio), encoding="utf-8")
    (tmp_path / "series_2026-10-07.json").write_text(json.dumps({k: cheio[k] for k in list(cheio)[:2]}), encoding="utf-8")
    assert len(series_vigente.carregar("series_2026-10-05.json", tmp_path)) == len(cheio)
    with pytest.raises(ValueError, match="AUD-24"):
        series_vigente.carregar("series_2026-10-07.json", tmp_path)


def test_aud24_ninguem_volta_ao_glob():
    """Nenhum módulo de produção escolhe a série por 'último da pasta' (montar_series.py só grava)."""
    achados = [p.name for p in RAIZ.glob("*.py")
               if re.search(r"glob\([\"']series_", p.read_text(encoding="utf-8")) and p.name != "series_vigente.py"]
    assert achados == []


def test_aud26_correcoes_do_lote4_sao_idempotentes():
    import lote4_saude_telecom as l4
    from motor_nao_financeiras import CVM, SI
    antes = copy.deepcopy((SI, CVM))
    l4.corrigir_proventos()
    l4.arrendamento_pago_proxy()
    assert (SI, CVM) == antes


_SONDA = """
import hashlib, json, sys
for m in sys.argv[1:]:
    __import__(m)
import universo
snap = universo.instantaneo_todos()
print(hashlib.sha256(json.dumps(snap, sort_keys=True, default=str).encode()).hexdigest())
"""


def _hash_de(*importar_antes):
    r = subprocess.run([sys.executable, "-c", _SONDA, *importar_antes], cwd=RAIZ, capture_output=True, text=True, timeout=600)
    assert r.returncode == 0, r.stderr[-800:]
    return r.stdout.strip().splitlines()[-1]


def test_aud26_resultado_nao_depende_da_ordem_de_import():
    """Importar o lote 4 antes dos outros (ou depois) dá o mesmo instantâneo dos 41."""
    normal = _hash_de()
    invertido = _hash_de("lote6_quimica", "lote5_petroleo", "lote4_saude_telecom")
    assert normal == invertido
