"""Acesso ao LTM de uma empresa do cvm_series.json, independente do trimestre coletado.

O coletor grava o LTM em três chaves: "ltm" (genérica), "ltm_ref" (ex.: "3T26") e "ltm_<ref>" (ex.: "ltm_3T26").
A série antiga só tem "ltm_2T26": é o último recurso.
"""


def ltm_de(reg):
    if "ltm" in reg:
        return reg["ltm"]
    return reg["ltm_2T26"]


def ltm_ref_de(reg):
    """Rótulo do trimestre do LTM ("2T26", "3T26"...); a série antiga sem "ltm_ref" é 2T26."""
    if "ltm_ref" in reg:
        return reg["ltm_ref"]
    return "2T26"


# ---------------------------------------------------------------- período derivado do rótulo do LTM (23/11/2026)
# Os lotes não escrevem mais data de trimestre, mês ou dia: tudo sai daqui a partir do `ltm_ref` da série vigente
# (`tests/test_lotes_sem_data_fixa.py` reprova data fixa nos lotes). Assim, ao passar de 2T26 para 3T26, janela de preço,
# data do balanço, ZIP e trimestres andam juntos com o LTM.
def trimestre_e_ano(ref: str) -> tuple[int, int]:
    """"3T26" → (3, 2026). Só 1T–4T com ano de 2 dígitos; o resto falha alto."""
    r = ref.strip().upper()
    if len(r) != 4 or r[1] != "T" or r[0] not in "1234" or not r[2:].isdigit():
        raise ValueError(f"ltm_ref inválido: {ref!r} (esperado nTaa, ex.: 3T26)")
    return int(r[0]), 2000 + int(r[2:])


def ano_de(ref: str) -> int:
    return trimestre_e_ano(ref)[1]


def mes_do_balanco(ref: str) -> int:
    """Mês do balanço que fecha o LTM: 1T → 3, 2T → 6, 3T → 9, 4T → 12."""
    return 3 * trimestre_e_ano(ref)[0]


def data_do_balanco(ref: str) -> str:
    """"2T26" → "2026-06-30": último dia do trimestre que fecha o LTM."""
    import calendar
    from datetime import date
    ano, mes = ano_de(ref), mes_do_balanco(ref)
    return date(ano, mes, calendar.monthrange(ano, mes)[1]).isoformat()


def _mes_menos(ano: int, mes: int, k: int) -> tuple[int, int]:
    n = ano * 12 + (mes - 1) - k
    return n // 12, n % 12 + 1


def janela_ltm(ref: str) -> tuple[str, str]:
    """Os 12 meses do LTM como ("AAAA-MM", "AAAA-MM"): "2T26" → ("2025-07", "2026-06"); "3T26" → ("2025-10", "2026-09")."""
    ano, mes = ano_de(ref), mes_do_balanco(ref)
    a0, m0 = _mes_menos(ano, mes, 11)
    return f"{a0:04d}-{m0:02d}", f"{ano:04d}-{mes:02d}"


def janela_trimestre(ano: int, tri: int) -> tuple[str, str]:
    """Meses de um trimestre como ("AAAA-MM", "AAAA-MM"): (2026, 3) → ("2026-07", "2026-09")."""
    fim = 3 * tri
    return f"{ano:04d}-{fim - 2:02d}", f"{ano:04d}-{fim:02d}"


def trimestres_ate(ref: str, n: int) -> list[tuple[int, int]]:
    """Os `n` últimos trimestres até o do LTM, do mais antigo ao mais novo: ("3T26", 2) → [(2026, 2), (2026, 3)]."""
    tri, ano = trimestre_e_ano(ref)
    out = []
    for _ in range(n):
        out.append((ano, tri))
        tri, ano = (tri - 1, ano) if tri > 1 else (4, ano - 1)
    return out[::-1]


def zip_itr(ref: str) -> str:
    """ZIP da CVM com o ITR do trimestre do LTM ("3T26" → "itr_2026.zip"). O 4T não existe no ITR (vem no DFP) → falha alto."""
    if trimestre_e_ano(ref)[0] == 4:
        raise ValueError(f"LTM {ref}: o 4T sai no DFP, não no ITR — leitura do balanço pelo DFP ainda não implementada")
    return f"itr_{ano_de(ref)}.zip"


def ref_comum(regs) -> str:
    """O `ltm_ref` único de um grupo de séries (ex.: os tickers de um lote). Refs diferentes no mesmo grupo misturariam datas
    de balanço numa só leitura de ZIP/snapshot → falha alto (rodar a temporada de quem falta)."""
    refs = {ltm_ref_de(r) for r in regs}
    if len(refs) != 1:
        raise ValueError(f"séries com LTM de trimestres diferentes no mesmo grupo: {sorted(refs)} — recoletar (temporada.py)")
    return refs.pop()
