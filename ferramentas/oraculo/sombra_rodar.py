"""Roda o motor-sombra (`oraculo/sombra.py`) sobre as empresas dos lotes e compara o central com o do motor.

Só relatório (docs/oraculo/sombra-AAAA-MM-DD.md + .json); nenhuma palavra, central ou golden muda. Os insumos passados à sombra
são os que o motor declara no resultado (receita de meio, margens dos cenários, alíquota, WACC/Ke da empresa no ponto fixo, g,
capital, ponte, ações, fluxo normalizado do acionista, desconto) — "mesma entrada" (PROMPT do oráculo, Fase 4); a conta é a da
sombra. Uso: `cd ferramentas && python -m oraculo.sombra_rodar`.
"""
from __future__ import annotations

import json
import sys
from unittest import mock
from datetime import date
from pathlib import Path

import mercado
import motor_financeiras as F
import motor_nao_financeiras as M
from oraculo import sanidade as S
from oraculo import sombra

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "docs" / "oraculo"


def insumos_industrial(emp, r) -> dict:
    op = r["op"]
    return dict(perfil=emp.perfil, pi=r["_pi"], wacc_nom=r["wacc"], ke_nom=r["ke_nom_emp"], receita_meio=op["receita_meio"],
                m25=op["m25"], m50=r["m"], m75=op["m75"], ajuste_manut=op["ajuste_manut"], t=r["aliquota"], g=r["gr"],
                g1=emp.g1_real, anos_g1=emp.anos_g1, cap_inv=r["cap_inv"], cap_rep=r["cap_inv_reposicao"], dl=r["dl"],
                minor=r["minor"], n=r["n"], oe_norm=r["oe_norm"], declinio_sem_liberacao=emp.declinio_sem_liberacao,
                passivos_acionista=emp.outros_passivos + emp.outros_passivos_financeiros + r["proventos_ja_ex"]["total"],
                reproducao=r["reprod"] if emp.usar_reproducao_como_ancora else None, desc=r["desc_controlador"])


def insumos_financeira(emp, mk) -> dict:
    return dict(vpa=emp.vpa, roe_inicio=emp.roe_inicio, roe_lp=emp.roe_lp, payout=emp.payout, ke_nom=mk.ke_nom,
                g_teto=mk.g_teto, dc=emp.desconto_controlador)


def explicar(emp, mk, x: dict, r: dict) -> str:
    """Causas conhecidas de divergência (limites declarados da sombra). Crédito fiscal com prazo: o motor roda de novo com o
    crédito zerado (`beneficio_fiscal` → 0; o ponto fixo refaz WACC/Ke) e a sombra recebe os insumos DESSA rodada — se as duas
    batem, a divergência do central é o crédito (revisor de 23/10: conferir só o EPV era quase tautológico e a âncora errada)."""
    motivos = []
    if r.get("beneficio_fiscal_acao"):
        with mock.patch.object(M, "beneficio_fiscal", lambda *a, **k: 0.0):
            r0 = M.avaliar(emp, mk)
        r0["_pi"] = mk.pi
        s0 = sombra.industrial(insumos_industrial(emp, r0))
        d0 = sombra.divergencia(s0["central"], r0["central"])
        ok = d0 is not None and abs(d0) <= sombra.TOLERANCIA
        motivos.append(f"crédito fiscal com prazo (a sombra não o tem): sem o crédito, motor {_br(r0['central'])} × sombra "
                       f"{_br(s0['central'])} ({_pct(d0)}) → " + ("confere: a divergência é o crédito" if ok else "NÃO confere — investigar")
                       + f"; efeito do crédito no central do motor {_br(r['central'] - r0['central'])}")
    if x.get("g1") is not None:
        motivos.append("2 estágios (g1)")
    return "; ".join(motivos)


def rodar(empresas=None) -> list[dict]:
    mk = mercado.vigente()
    linhas = []
    for tk, emp in sorted((empresas or S.empresas()).items()):
        if isinstance(emp, F.Financeira):
            if emp.horizonte_finito or emp.sotp is not None:
                linhas.append(dict(ticker=tk, tipo="financeira", fora="SOTP ou contrato finito: fora da sombra"))
                continue
            r = F.avaliar(emp, mk)
            s = sombra.financeira(insumos_financeira(emp, mk))
            linhas.append(dict(ticker=tk, tipo="financeira", motor=r["central"], sombra=s["central"],
                               div=sombra.divergencia(s["central"], r["central"]), ancoras_motor=r["ancoras"],
                               ancoras_sombra=s["ancoras"], explicacao=""))
            continue
        r = M.avaliar(emp, mk)
        r["_pi"] = mk.pi
        x = insumos_industrial(emp, r)
        s = sombra.industrial(x)
        linhas.append(dict(ticker=tk, tipo="industrial", motor=r["central"], sombra=s["central"],
                           div=sombra.divergencia(s["central"], r["central"]), ancoras_motor=r["ancoras"],
                           ancoras_sombra=s["ancoras"], explicacao=explicar(emp, mk, x, r)))
    return linhas


def _br(x, casas=2):
    return "—" if x is None else f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(x):
    return "—" if x is None else f"{100 * x:+.2f}%".replace(".", ",")


def gravar(linhas, hoje=None) -> Path:
    hoje = hoje or date.today().isoformat()
    PASTA.mkdir(parents=True, exist_ok=True)
    (PASTA / f"sombra-{hoje}.json").write_text(json.dumps(linhas, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    acima = [l for l in linhas if l.get("div") is not None and abs(l["div"]) > sombra.TOLERANCIA]
    md = [f"# Motor-sombra × motor — {hoje}", "",
          f"Gerado por `cd ferramentas && python -m oraculo.sombra_rodar`. Tolerância pré-registrada |Δcentral| ≤ "
          f"{100 * sombra.TOLERANCIA:.0f}% (PRE-REGISTRO-v3 §3). Só relatório: nenhuma palavra, central ou golden muda.", "",
          f"{len(linhas)} empresas · {sum(1 for l in linhas if 'div' in l)} comparadas · {len(acima)} acima da tolerância.", "",
          "| ticker | tipo | central motor | central sombra | Δ | explicação |", "|---|---|---|---|---|---|"]
    for l in linhas:
        if "fora" in l:
            md.append(f"| {l['ticker']} | {l['tipo']} | — | — | — | {l['fora']} |")
        else:
            md.append(f"| {l['ticker']} | {l['tipo']} | {_br(l['motor'])} | {_br(l['sombra'])} | {_pct(l['div'])} | {l['explicacao']} |")
    md += ["", "**Limites (o que a sombra NÃO confere):** o WACC e o Ke da empresa entram prontos do ponto fixo do motor (não conferem o",
           "Hamada nem o achado A1); o fluxo normalizado do acionista (OE) e as margens dos cenários entram prontos (não conferem a",
           "normalização); o crédito fiscal com prazo e o SOTP/contrato finito ficam fora. Ela confere a composição: FCFF, trava de g,",
           "reinvestimento, 2 estágios, ponderação dos cenários, ponte firma → acionista, desconto do controlador e mediana."]
    caminho = PASTA / f"sombra-{hoje}.md"
    caminho.write_text("\n".join(md) + "\n", encoding="utf-8")
    return caminho


if __name__ == "__main__":
    print(gravar(rodar(), sys.argv[1] if len(sys.argv) > 1 else None))
