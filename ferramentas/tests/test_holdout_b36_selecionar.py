"""B36: o seletor do hold-out aplica a regra mecânica da emenda 8 e não lê preço nem valuation."""
import ast
import pathlib

import pandas as pd

from holdout_b36 import selecionar as S


def _tab(linhas):
    base = {"outras_classes": "", "setor": "", "detalhe": ""}
    return pd.DataFrame([dict(base, **l) for l in linhas])


def test_regra_exclui_por_motivo_olhado_e_dfp_e_ordena_por_liquidez():
    tab = _tab([
        {"ticker": "AAAA3", "cnpj": "1", "cd_cvm": 1, "liquidez": 90e6, "motivo": ""},
        {"ticker": "BBBB3", "cnpj": "2", "cd_cvm": 2, "liquidez": 80e6, "motivo": "recuperação/falência/liquidação"},
        {"ticker": "CCCC3", "cnpj": "3", "cd_cvm": 3, "liquidez": 70e6, "motivo": ""},        # olhada por gente
        {"ticker": "DDDD3", "cnpj": "4", "cd_cvm": 4, "liquidez": 60e6, "motivo": ""},        # 9 DFPs
        {"ticker": "EEEE3", "cnpj": "5", "cd_cvm": 5, "liquidez": 50e6, "motivo": ""},
        {"ticker": "FFFF3", "cnpj": "6", "cd_cvm": 6, "liquidez": 50e6, "motivo": ""},        # empate: alfabética
        {"ticker": "GGGG3", "cnpj": "", "cd_cvm": None, "liquidez": 99e6, "motivo": "sem identidade na CVM"},
    ])
    n_dfp = {1: 12, 2: 15, 3: 15, 4: 9, 5: 10, 6: 17}
    t = S.selecionar(tab, n_dfp, olhados_cnpj={"3"}, n=2)
    m = dict(zip(t["ticker"], t["motivo_b36"]))
    assert m["BBBB3"].startswith("recuperação") and m["GGGG3"] == "sem identidade na CVM"
    assert m["CCCC3"] == "já olhada por gente" and m["DDDD3"] == "menos de 10 DFPs"
    esc = t[t["ordem"].notna()].sort_values("ordem")["ticker"].tolist()
    assert esc == ["AAAA3", "EEEE3"]          # FFFF3 empata com EEEE3 e perde na ordem alfabética


def test_menos_de_n_elegiveis_nao_inventa():
    tab = _tab([{"ticker": "AAAA3", "cnpj": "1", "cd_cvm": 1, "liquidez": 1e6, "motivo": ""}])
    t = S.selecionar(tab, {1: 10}, set(), n=20)
    assert t["ordem"].notna().sum() == 1


def test_ja_olhados_inclui_os_quatro_grupos():
    g = S.ja_olhados()
    assert {"ITSA4", "BBAS3", "ALLD3", "CMIN3", "LREN3", "TOTS3", "VALE3", "ODPV3"} <= set(g)
    assert len({t for t, grupo in g.items() if grupo == "golden (41)"}) == 41


def test_seletor_nao_le_coluna_de_preco_nem_valuation():
    """A regra proíbe olhar preço/valuation: nenhuma coluna de preço do COTAHIST nem módulo de valuation no código."""
    src = pathlib.Path(S.__file__).read_text(encoding="utf-8")
    arv = ast.parse(src)
    for n in ast.walk(arv):                                    # tira docstrings (a regra escrita cita o que é proibido)
        if isinstance(n, (ast.Module, ast.FunctionDef)) and n.body and isinstance(n.body[0], ast.Expr) \
                and isinstance(n.body[0].value, ast.Constant) and isinstance(n.body[0].value.value, str):
            n.body = n.body[1:] or [ast.Pass()]
    codigo = ast.unparse(arv)                                  # sem comentários
    for proibido in ("preult", "premed", "preabe", "premax", "premin", "fechamento", "triagem.avaliar", "motor_",
                     "central", "golden.json", "mercado"):
        assert proibido not in codigo.replace("tickers_analisados", ""), proibido
