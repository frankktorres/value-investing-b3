"""Acesso ao LTM de uma empresa do cvm_series.json, independente do trimestre coletado.

O coletor grava o LTM em três chaves: "ltm" (genérica), "ltm_ref" (ex.: "3T26") e "ltm_<ref>" (ex.: "ltm_3T26").
A série antiga só tem "ltm_2T26": é o último recurso.
"""


from contextlib import contextmanager

_CORTE: str | None = None      # data AAAA-MM-DD do recálculo point-in-time (`na_data`); None = LTM vigente da série


def ltm_de(reg):
    if _CORTE is not None:
        return ltm_guardado(reg, ref_na_data(reg, _CORTE))
    if "ltm" in reg:
        return reg["ltm"]
    return reg["ltm_2T26"]


def ltm_ref_de(reg):
    """Rótulo do trimestre do LTM ("2T26", "3T26"...); a série antiga sem "ltm_ref" é 2T26. Dentro de `na_data`, o da data."""
    if _CORTE is not None:
        return ref_na_data(reg, _CORTE)
    return _ref_vigente(reg)


def _ref_vigente(reg):
    if "ltm_ref" in reg:
        return reg["ltm_ref"]
    return "2T26"


@contextmanager
def na_data(data_iso: str | None):
    """Toda leitura de LTM dentro do bloco devolve o trimestre já publicado na data (dossiê recalculado na data dele)."""
    global _CORTE
    antes = _CORTE
    _CORTE = data_iso
    try:
        yield
    finally:
        _CORTE = antes


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


# ---------------------------------------------------------------- LTM na data (point-in-time, 24/11/2026 — B34)
# Um dossiê de 06/10 recalculado em novembro lia o LTM do 3T26 (publicado depois da data dele). Na data D vale o trimestre mais
# recente guardado na série (`ltm_<ref>`) cujo prazo de entrega do ITR já tinha passado em D. O 4T (DFP) tem outro prazo e falha
# alto até ter fonte.
PRAZO_ITR_DIAS = 45        # Resolução CVM 80/2022: ITR em até 45 dias do fim do trimestre (fonte em docs/research/2026-11-24-ke-alavancagem.md)


def _fim_do_trimestre(ref: str):
    import calendar
    import datetime as dt
    t, a = trimestre_e_ano(ref)
    m = 3 * t
    return dt.date(a, m, calendar.monthrange(a, m)[1])


def refs_da_serie(reg) -> list[str]:
    refs = {k[4:] for k in reg if k.startswith("ltm_") and k != "ltm_ref"}
    if not refs and "ltm" in reg:
        refs = {_ref_vigente(reg)}
    return sorted(refs, key=lambda r: trimestre_e_ano(r)[::-1])


def ref_na_data(reg, data_iso: str) -> str:
    """O `ltm_ref` que já estava publicado (pelo prazo legal) na data AAAA-MM-DD."""
    import datetime as dt
    d = dt.date.fromisoformat(data_iso)
    ok = []
    for r in refs_da_serie(reg):
        if trimestre_e_ano(r)[0] == 4:
            raise ValueError(f"LTM {r}: prazo do DFP (4T) sem fonte conferida; decidir antes de usar na data")
        if _fim_do_trimestre(r) + dt.timedelta(days=PRAZO_ITR_DIAS) <= d:
            ok.append(r)
    if not ok:
        raise ValueError(f"nenhum LTM da série publicado até {data_iso} (refs {refs_da_serie(reg)})")
    return ok[-1]


def ltm_guardado(reg, ref: str) -> dict:
    if f"ltm_{ref}" in reg:
        return reg[f"ltm_{ref}"]
    if _ref_vigente(reg) == ref and "ltm" in reg:
        return reg["ltm"]
    raise KeyError(f"série sem o LTM {ref}")
