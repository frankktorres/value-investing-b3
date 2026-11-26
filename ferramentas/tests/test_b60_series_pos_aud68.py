"""B60 (26/11/2026): nenhuma série (hall, dossiê, B36) com `lucro_controlador` = 0 e lucro ≠ 0 (defeito anterior à AUD-68:
o motor lê o 0 como lucro zero no OE) nem no formato de coleta anterior à AUD-68 (sem `ltm_ref`). Pula se o arquivo não
existir (dados fora do git)."""
import json
import pathlib

import pytest

F = pathlib.Path(__file__).resolve().parent.parent
ARQUIVOS = [F / "dados" / "cvm_series.json", F / "dossie" / "dados" / "cvm_series_dossie.json",
            F / "holdout_b36" / "dados" / "cvm_series_holdout.json"]


def _containers(reg):
    for a, d in reg.get("anual", {}).items():
        yield f"anual/{a}", d
    for k, d in reg.items():
        if (k == "ltm" or k.startswith("ltm_")) and isinstance(d, dict):
            yield k, d


@pytest.mark.parametrize("arq", ARQUIVOS, ids=lambda p: p.name)
def test_sem_lucro_controlador_zero(arq):
    if not arq.exists():
        pytest.skip(f"{arq.name} ausente")
    ruins = [f"{tk} {n}" for tk, reg in json.loads(arq.read_text(encoding="utf-8")).items() for n, d in _containers(reg)
             if isinstance(d, dict) and d.get("lucro_controlador") == 0 and d.get("lucro")]
    assert not ruins, ruins


@pytest.mark.parametrize("arq", ARQUIVOS, ids=lambda p: p.name)
def test_formato_pos_aud68(arq):
    if not arq.exists():
        pytest.skip(f"{arq.name} ausente")
    antigos = [tk for tk, reg in json.loads(arq.read_text(encoding="utf-8")).items() if "ltm_ref" not in reg]
    assert not antigos, antigos
