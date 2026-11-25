"""Regras do relatório do hold-out B36 (emenda 8): absurdo, Ke > 30%, previsto × observado."""
import math

from holdout_b36 import relatorio as R


def _r(**kw):
    base = dict(erro=None, palavra="CARA", pc=1.5, central=10.0, ke_nom=0.2, dispersao=1.2)
    base.update(kw)
    return base


def test_absurdo_pelos_limites_da_emenda():
    assert R.absurdo(_r(central=0.0, pc=math.inf))
    assert R.absurdo(_r(central=-3.0))
    assert R.absurdo(_r(pc=5.01)) and R.absurdo(_r(pc=0.19))
    assert not R.absurdo(_r(pc=5.0)) and not R.absurdo(_r(pc=0.2))
    assert not R.absurdo(_r(erro={"tipo": "X"}, central=None, pc=None))     # erro não conta como absurdo


def test_ke30_estrito_e_so_sem_erro():
    assert R.ke30(_r(ke_nom=0.3001)) and not R.ke30(_r(ke_nom=0.30))
    assert not R.ke30(_r(erro={"tipo": "X"}, ke_nom=0.9))


def test_confere_previsoes():
    nc = _r(palavra="NÃO CONCLUSIVO", ke_nom=0.5)
    assert R.confere("NÃO CONCLUSIVO (Ke > 30%)", nc)
    assert not R.confere("NÃO CONCLUSIVO (Ke > 30%)", _r(palavra="NÃO CONCLUSIVO"))
    assert R.confere("valor absurdo (P/C > 5)", _r(pc=40))
    assert not R.confere("valor absurdo (P/C > 5)", _r(central=-1, pc=math.inf * -1))
    assert R.confere("erro", _r(erro={"tipo": "ValueError"}))
    assert R.confere("roda", nc) and not R.confere("roda", _r(erro={"tipo": "X"}))
    assert not R.confere("roda, sem absurdo", _r(pc=6))


def test_todas_as_20_tem_previsao():
    import json
    cad = json.loads((R.AQUI / "cadastro.json").read_text(encoding="utf-8"))
    assert {c["ticker"] for c in cad} == set(R.PREVISTO)
