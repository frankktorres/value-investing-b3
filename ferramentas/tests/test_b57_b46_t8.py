"""B46 tentativa 8/24 (emenda 13): a sensibilidade do X2 do DFP é só relatada e a leitura "PASSA frágil" segue o texto."""
from b46 import relatorio as R

OK = dict(passou=True)
NAO = dict(passou=False)


def test_leitura_da_tentativa_8_pelo_texto_da_emenda_13():
    assert R.leitura(OK, OK, OK, OK) == "PASSA"                       # 7/24: sem sensibilidade
    assert R.leitura(OK, OK, OK, OK, OK) == "PASSA"                   # passa nos dois X2
    assert R.leitura(OK, OK, OK, OK, NAO) == "PASSA frágil"           # passa com o da regra, falha com o do DFP
    assert R.leitura(OK, OK, NAO, OK, OK) == "NÃO CONCLUSIVA"         # a sensibilidade nunca faz passar
    assert R.leitura(NAO, OK, OK, OK, OK) == "FALHA"                  # FALHA prevalece


def _linha(tk, de_m, de_i, conc, conc_dfp):
    c = dict(erro=None, central=1.0, de_mercado=de_m, de_ind=de_i, concordam=conc, concordam_x2_dfp=conc_dfp)
    return dict(tk=tk, financeira=False, completo=c)


def test_c3_do_x2_do_dfp_usa_o_mesmo_grupo_e_o_mesmo_limiar():
    res = dict(linhas=[_linha("A", 2.0, 1.0, True, False), _linha("B", 2.0, 1.0, True, True),
                       _linha("C", 2.0, 1.0, False, True), _linha("D", 0.5, 1.0, False, False)])   # D fora do grupo
    r3, r3d = R.c3(res), R.c3_x2_dfp(res)
    assert (r3["n"], r3d["n"]) == (3, 3)
    assert r3["concordam"] == ["A", "B"] and r3["passou"]                # 2 de 3 = 2/3
    assert r3d["concordam"] == ["B", "C"] and r3d["passou"]
    res["linhas"][1]["completo"]["concordam_x2_dfp"] = False
    assert not R.c3_x2_dfp(res)["passou"] and R.c3(res)["passou"]       # só a sensibilidade muda
