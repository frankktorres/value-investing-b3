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


def test_aud08_leve3_e_isae4_nao_conclusivas_pela_trava_e_razao_libera():
    import universo
    import motor_nao_financeiras as M
    t = universo.avaliar_todos()
    for tk in ("LEVE3", "ISAE4"):
        r = t[tk]["r"]
        assert r["palavra_regua"] == "JUSTA" and r["trava"] is False and r["palavra"] == "NÃO CONCLUSIVO", tk
        assert "trava" in r["confianca"]
    leve = dataclasses.replace(t["LEVE3"]["empresa"], trava_razao="teste")
    assert M.avaliar(leve, universo.MK)["palavra"] == "JUSTA"
