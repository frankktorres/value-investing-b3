"""B45 (26/11/2026): compra de frota lançada no caixa OPERACIONAL (locadoras: MOVI3 6.01.03.03, RENT3 6.01.02.03) é
investimento em imobilizado que o coletor não via — ele só lê capex em 6.02. Com 245 mi de capex contra 10,3 bi de frota
comprada (MOVI3, DFP 2025), o OE somava a depreciação da frota e não descontava a compra (âncora OE 8,65 > preço 5,64).
Regra: havendo essa linha, `capex` fica None ("não avaliado", princípio 2 do DNA) e o valor vai para `capex_frota_fco`, com a
linha na auditoria. Nenhuma empresa do hall/dossiês tem a linha (medido na DFP 2025): o golden não muda."""
import pandas as pd

import coletar_cvm as C


def _dfc(linhas):
    return pd.DataFrame(linhas, columns=["CD_CONTA", "DS_CONTA", "VL_CONTA"]).astype({"VL_CONTA": float})


BASE = [("6.01.01.02", "Depreciações e Amortizações", 2430.0),
        ("6.02.03", "Adições ao ativo imobilizado para investimento e intangível", -245.0)]


def test_sem_linha_de_frota_capex_igual():
    e, aud = C.dfc_extra(_dfc(BASE))
    assert e["capex"] == 245.0
    assert e["capex_frota_fco"] == 0.0
    assert aud["linhas_capex_frota_fco"] == []


def test_frota_no_fco_deixa_capex_nao_avaliado():
    d = _dfc(BASE + [("6.01.03.03", "Compra de Ativo Imobilizado para Locação, Caixa Desembolsado", -10268.0)])
    e, aud = C.dfc_extra(d)
    assert e["capex"] is None                                   # não avaliado, nunca os 245 do 6.02
    assert e["capex_frota_fco"] == 10268.0
    assert aud["linhas_capex_frota_fco"] == ["Compra de Ativo Imobilizado para Locação, Caixa Desembolsado"]


def test_rotulos_das_locadoras():
    for ds in ("Aquisição de carros, líq. da variação do saldo a pagar a montadoras de carros",
               "Compra de ativo imobilizado operacional para locação", "Aquisição de veículos",
               "Aquisição e renovação de frota de veículos"):
        e, _ = C.dfc_extra(_dfc(BASE + [("6.01.02.03", ds, -100.0)]))
        assert e["capex"] is None and e["capex_frota_fco"] == 100.0, ds


def test_linha_que_nao_e_frota_nao_dispara():
    # variação de estoque de veículo de concessionária ou baixa contábil não é compra de frota; valor positivo também não
    for cd, ds, vl in (("6.01.02.01", "Estoques", -50.0), ("6.01.01.03", "Baixa de veículos", 30.0),
                       ("6.01.02.05", "Aquisição de veículos", 40.0)):
        e, _ = C.dfc_extra(_dfc(BASE + [(cd, ds, vl)]))
        assert e["capex"] == 245.0, ds
