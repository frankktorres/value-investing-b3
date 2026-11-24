"""Onda 1.2 da auditoria de 08/10/2026, bloco 4 — trava de coerência do §9 (AUD-08).

JUSTA pela régua com Bogle fora de ±2 p.p. do Ke: a doutrina manda corrigir antes de publicar; sem a premissa escrita
(`trava_razao`), a palavra é NÃO CONCLUSIVO. No código antigo a trava era só um campo (LEVE3 saía JUSTA com ela falha) e
`aplicar_trava` não existia.
"""
import dataclasses

from motor_financeiras import aplicar_trava


def test_aud08_trava_falha_sem_razao_vira_nao_conclusivo():
    assert aplicar_trava("JUSTA", "JUSTA", False) == "NÃO CONCLUSIVO"
    assert aplicar_trava("JUSTA", "JUSTA", False, "g da ficha diverge do g do Bogle: …") == "JUSTA"
    assert aplicar_trava("JUSTA", "JUSTA", True) == "JUSTA"
    assert aplicar_trava("RADAR", "JUSTA", None) == "JUSTA"           # trava não calculada (None) não decide
    assert aplicar_trava("RADAR", "JUSTA", False) == "NÃO CONCLUSIVO"  # v2.6 (AUD-10): JUSTA final pela dispersão também trava
    assert aplicar_trava("JUSTA", "NÃO CONCLUSIVO", False) == "NÃO CONCLUSIVO"


def test_aud08_no_hall_nenhuma_justa_publica_com_trava_falha():
    import universo
    for tk, it in universo.avaliar_todos().items():
        r = it["r"]
        if r["palavra"] == "JUSTA":
            assert r["trava"] or it["empresa"].trava_razao.strip(), tk


def test_aud08_prio3_e_unip6_nao_conclusivas_pela_trava_e_razao_libera():
    """3T26 (decisão do Frank, 23/11): PRIO3 e UNIP6 JUSTA na régua com a trava falha → NÃO CONCLUSIVO; até o 2T26 eram LEVE3 e
    ISAE4 (hoje RADAR e JUSTA com o LTM de 30/09)."""
    import universo
    import motor_nao_financeiras as M
    t = universo.avaliar_todos()
    for tk in ("PRIO3", "UNIP6"):
        r = t[tk]["r"]
        assert r["palavra_regua"] == "JUSTA" and not r["trava"] and r["palavra"] == "NÃO CONCLUSIVO", tk
        assert "trava" in r["confianca"]
    prio = dataclasses.replace(t["PRIO3"]["empresa"], trava_razao="teste")
    assert M.avaliar(prio, universo.MK)["palavra"] == "JUSTA"


def test_trava_falha_do_numpy_tambem_derruba_a_justa():
    """23/11/2026: a trava vinha como np.False_ e `trava is False` não a via — a PRIO3 saiu JUSTA com a trava falha."""
    import numpy as np
    from motor_financeiras import aplicar_trava
    assert aplicar_trava("JUSTA", "JUSTA", np.False_) == "NÃO CONCLUSIVO"
    assert aplicar_trava("JUSTA", "JUSTA", np.True_) == "JUSTA"
    assert aplicar_trava("JUSTA", "JUSTA", np.False_, "premissa X diverge") == "JUSTA"
    assert aplicar_trava("RADAR", "RADAR", None) == "RADAR"
