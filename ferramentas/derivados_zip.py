"""Valores que os lotes 4 e 6 derivam dos ZIPs da CVM, com snapshot versionado (AUD-38, auditoria de 08/10/2026).

Antes, `lote4_saude_telecom` e `lote6_quimica` abriam `itr_2026.zip` etc. no import: num clone limpo (ZIPs ficam fora do git)
`import universo` quebrava e o pytest abortava na coleta. Agora:
  · os ZIPs existem → o valor é recalculado deles (o parser continua sendo o que vale);
  · não existem → lê `dados/derivados_zip.json` (snapshot versionado, gerado pelo mesmo código) e avisa em stderr;
  · nem ZIP nem snapshot da chave → erro com a receita (`python bootstrap_dados.py --baixar`).
`tests/test_bootstrap_reprodutibilidade.py` confere o snapshot contra o recálculo quando os ZIPs estão presentes.
Regerar o snapshot: `python bootstrap_dados.py --derivados`.
"""
from __future__ import annotations

import json
import pathlib
import sys

AQUI = pathlib.Path(__file__).parent
CVM = AQUI / "dados" / "cvm"
SNAPSHOT = AQUI / "dados" / "derivados_zip.json"
CALCULADOS: dict[str, object] = {}      # o que foi recalculado dos ZIPs nesta execução (alimenta o --derivados e o teste)
_AVISADO: set[str] = set()


def _snapshot() -> dict:
    return json.loads(SNAPSHOT.read_text(encoding="utf-8")) if SNAPSHOT.exists() else {}


def obter(chave: str, zips: list[str], calcular):
    """`calcular()` se todos os `zips` existem em dados/cvm; senão o snapshot da `chave`."""
    if all((CVM / z).exists() for z in zips):
        valor = calcular()
        CALCULADOS[chave] = json.loads(json.dumps(valor))       # forma que o JSON preserva (chaves str, listas)
        return valor
    snap = _snapshot()
    if chave not in snap:
        faltam = [z for z in zips if not (CVM / z).exists()]
        raise FileNotFoundError(f"'{chave}' precisa de {faltam} em dados/cvm e não há snapshot em {SNAPSHOT.name}: "
                                "rode `python bootstrap_dados.py --baixar`")
    if chave not in _AVISADO:
        _AVISADO.add(chave)
        print(f"[derivados_zip] ZIPs ausentes → usando o snapshot de '{chave}' ({SNAPSHOT.name})", file=sys.stderr)
    return snap[chave]


CHAVES = ("lote4.acoes_jun26", "lote4.arrendamento_pago", "lote4.itsa", "lote5.base_prio3", "lote6.acoes_jun26")


def gravar_snapshot() -> int:
    """Grava os valores recalculados nesta execução (merge com o snapshot atual). Devolve quantas chaves.
    Exige TODAS as chaves: ZIPs parciais misturariam versões de ZIP no mesmo snapshot."""
    faltam = [c for c in CHAVES if c not in CALCULADOS]
    if faltam:
        raise RuntimeError(f"não recalculadas dos ZIPs (ZIPs ausentes?): {faltam}; snapshot não gravado")
    snap = _snapshot()
    snap.update(CALCULADOS)
    SNAPSHOT.write_text(json.dumps(snap, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return len(CALCULADOS)
