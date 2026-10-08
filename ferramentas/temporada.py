"""Temporada de resultados (F8): baixa o ITR novo da CVM, recoleta quem publicou, reavalia o hall e compara com o golden.

Uso (a partir de ferramentas/):
  python temporada.py                 → trimestre mais recente ainda sem coleta (hoje 3T26 = ITR de 30/09/2026)
  python temporada.py --trimestre 3T26
  python temporada.py --simular 2T26  → ensaio com o trimestre que já existe no cache (sem download, nada é gravado fora do boletim)
  python temporada.py --gravar        → além do boletim, grava a coleta nova em dados/cvm_series.json

O ITR é o mesmo do coletor (dados.cvm.gov.br, `itr_cia_aberta_AAAA.zip`, cache em dados/cvm/itr_AAAA.zip).
A coleta nova vai para um arquivo temporário e é injetada SÓ na memória (`CVM` de cada módulo); o `cvm_series.json` oficial
e o golden não mudam sozinhos. Para aceitar: `--gravar` e depois `python rodar_tudo.py --motivo "…"`.
Sem ticker com ITR novo: avisa e sai com código 0.
"""
import argparse
import json
import pathlib
import re
import sys
import tempfile
from datetime import date

import coletar_cvm as cc
from ltm import ltm_de

AQUI = pathlib.Path(__file__).parent
BOLETINS = AQUI.parent / "BOLETINS"
FORA_DO_HALL = {"BLAU3", "CMIN3"}   # dossiês (Etapa 5): coletados em dossie/dados/, não entram na temporada
TRIMESTRE_FIM = {1: (3, 31), 2: (6, 30), 3: (9, 30)}   # 4T sai na DFP, não no ITR


def interpretar_trimestre(rotulo):
    """"3T26" → (2026, 9, "2026-09-30"). 4T não existe no ITR (é a DFP)."""
    m = re.fullmatch(r"([1-3])T(\d{2})", rotulo.strip().upper())
    if not m:
        raise ValueError(f"trimestre inválido: {rotulo!r} (use 1T26, 2T26 ou 3T26; o 4T vem na DFP)")
    q, ano = int(m.group(1)), 2000 + int(m.group(2))
    mes, dia = TRIMESTRE_FIM[q]
    return ano, mes, f"{ano}-{mes:02d}-{dia:02d}"


def trimestre_atual(hoje=None):
    """Último trimestre de ITR que já fechou (mas pode não ter sido publicado)."""
    hoje = hoje or date.today()
    q = (hoje.month - 1) // 3          # trimestres fechados no ano: 0..3
    if q == 0:
        return "3T%02d" % ((hoje.year - 1) % 100)
    return f"{min(q, 3)}T{hoje.year % 100:02d}"


def baixar_itr(ano):
    """Baixa o ITR do ano por cima do cache (o arquivo da CVM é reescrito a cada entrega)."""
    import requests
    CACHE = cc.CACHE
    CACHE.mkdir(parents=True, exist_ok=True)
    alvo = CACHE / f"itr_{ano}.zip"
    r = requests.get(cc.URL["ITR"].format(a=ano), timeout=600)
    r.raise_for_status()
    tmp = alvo.with_suffix(".zip.novo")
    tmp.write_bytes(r.content)
    tmp.replace(alvo)
    return alvo


def quem_publicou(z, tickers, dt_ref, empresas=None):
    """Tickers (de `tickers`, com regra de coleta em `empresas`) cujo ITR no zip traz DT_REFER == dt_ref.
    Devolve (publicaram, ausentes, sem_coleta); só olha a DRE (consolidada, senão individual)."""
    empresas = cc.EMPRESAS if empresas is None else empresas
    ano = dt_ref[:4]
    pub, aus, sem = [], [], []
    for tk in tickers:
        if tk not in empresas:
            sem.append(tk)
            continue
        d = cc.buscar(z, "DRE_con", ano, empresas[tk][0])
        if d is not None and not d.empty and "DT_REFER" in d and (d["DT_REFER"] == dt_ref).any():
            pub.append(tk)
        else:
            aus.append(tk)
    return pub, aus, sem


def _pct(a, b):
    return None if not a or b is None else (b - a) / abs(a)


def _divida(l):
    v = [l.get(k) for k in ("emprest_cp", "emprest_lp")]
    return None if None in v else sum(v)


def causas(ltm_antigo, ltm_novo):
    """Números que explicam a mudança: receita, margem EBIT (pontos), dívida bruta, lucro. None quando faltar dado."""
    a, n = ltm_antigo or {}, ltm_novo or {}
    out = {"receita_pct": _pct(a.get("receita"), n.get("receita")),
           "lucro_pct": _pct(a.get("lucro"), n.get("lucro")),
           "divida_pct": _pct(_divida(a), _divida(n))}
    if a.get("receita") and n.get("receita") and a.get("ebit") is not None and n.get("ebit") is not None:
        out["margem_pp"] = 100 * (n["ebit"] / n["receita"] - a["ebit"] / a["receita"])
    else:
        out["margem_pp"] = None
    return out


def _fmt(x, suf):
    return "n/d" if x is None else f"{x * 100:+.1f}%" if suf == "%" else f"{x:+.1f} p.p."


def linha_causas(c):
    return (f"receita {_fmt(c['receita_pct'], '%')} · margem EBIT {_fmt(c['margem_pp'], 'pp')} · "
            f"dívida bruta {_fmt(c['divida_pct'], '%')} · lucro {_fmt(c['lucro_pct'], '%')}")


def _f(x):
    return f"{x:.4f}" if isinstance(x, float) else str(x)


def montar_boletim(dia, ref, publicaram, ausentes, sem_coleta, mud, causas_por_tk, lotes, simulado=False, falhas=()):
    """Texto Markdown do boletim. `mud` = saída de golden.comparar; `causas_por_tk` = {tk: causas()}."""
    L = [f"# Temporada {ref} — {dia}" + (" (SIMULAÇÃO: trimestre que já estava coletado)" if simulado else ""), ""]
    L.append(f"- Publicaram o ITR de {ref}: **{len(publicaram)}** ({', '.join(publicaram) or 'nenhum'}).")
    L.append(f"- Ainda sem ITR de {ref}: {len(ausentes)} ({', '.join(ausentes) or '—'}).")
    if sem_coleta:
        L.append(f"- Fora da coleta CVM (premissas manuais/StatusInvest; não mudam com o ITR): {', '.join(sem_coleta)}.")
    if falhas:
        L.append(f"- **Publicaram mas a coleta falhou** (seguem com o LTM antigo; rode de novo): {', '.join(falhas)}.")
    L.append("")
    por_tk = {}
    for tk, rot, x, y in mud:
        por_tk.setdefault(tk, []).append((rot, x, y))
    trocas = {tk: next((x, y) for r, x, y in v if r == "palavra") for tk, v in por_tk.items() if any(r == "palavra" for r, _, _ in v)}
    if not mud:
        L.append("## Resultado\n\nNenhuma mudança de palavra, de central ou de âncora em relação ao golden.")
    else:
        L.append(f"## Resultado\n\n{len(mud)} mudanças em {len(por_tk)} tickers; **{len(trocas)} trocas de palavra**.")
        if trocas:
            L += ["", "### Mudou de palavra", ""]
            for tk, (x, y) in sorted(trocas.items()):
                L.append(f"- **{tk}**: {x} → {y} — {linha_causas(causas_por_tk.get(tk, causas({}, {})))}")
        L += ["", "### Todas as mudanças (central, âncoras, P/C…)", "", "| Ticker | Campo | Antes | Depois | Por quê (LTM) |", "|---|---|---|---|---|"]
        for tk in sorted(por_tk):
            c = linha_causas(causas_por_tk.get(tk, causas({}, {})))
            for rot, x, y in por_tk[tk]:
                L.append(f"| {tk} | {rot} | {_f(x)} | {_f(y)} | {c} |")
        if lotes:
            L += ["", "### PDFs a reemitir", "", "Lotes com ticker afetado: " + ", ".join(f"`python gerar_pdf_lote{n}.py`" for n in sorted(lotes)) + "."]
    L += ["", "---",
          "O golden **não** é regravado por esta ferramenta. Para aceitar a coleta nova: `python temporada.py --gravar` "
          "e depois `python rodar_tudo.py --motivo \"3T26: …\"` (o motivo vai para `tests/golden_log.md`). "
          "Antes da palavra nova valer, `05-prompt-reavaliacao` para quem trocou.", ""]
    return "\n".join(L)


def ltm_utilizavel(reg):
    l = (reg or {}).get("ltm") or {}
    return "erro" not in l and bool(l.get("receita"))


LOTE_COLETA = 6   # tickers por subprocesso (cada processo devolve a memória dos ZIPs ao terminar)

_CHAMADA = ("import sys, json, pathlib, coletar_cvm as c; a = json.loads(sys.argv[1]); "
            "c.main(a['tks'], anos=a['anos'], arq=pathlib.Path(a['arq']), ano_itr=a['ano'], mes=a['mes'])")


def coletar(tickers, arq, ano, mes, tentativas=3):
    """Recoleta só o LTM (exercício-base + ITR) dos tickers, em subprocessos pequenos (a máquina tem pouca RAM e o coletor lê
    ZIPs grandes); repete os que falharem. Devolve {tk: registro} só dos bons."""
    import subprocess
    bons, faltam = {}, list(tickers)
    for _ in range(tentativas):
        for k in range(0, len(faltam), LOTE_COLETA):
            lote = faltam[k:k + LOTE_COLETA]
            arg = json.dumps({"tks": lote, "anos": [ano - 1], "arq": str(arq), "ano": ano, "mes": mes})
            subprocess.run([sys.executable, "-c", _CHAMADA, arg], cwd=AQUI, check=False)
        if arq.exists():
            tudo = json.loads(arq.read_text(encoding="utf-8"))
            bons.update({tk: tudo[tk] for tk in faltam if ltm_utilizavel(tudo.get(tk))})
        faltam = [tk for tk in faltam if tk not in bons]
        if not faltam:
            break
    return bons


def _modulos_com_cvm():
    return [m for m in list(sys.modules.values()) if isinstance(getattr(m, "CVM", None), dict) and getattr(m, "__name__", "").split(".")[0] != "backtest"]


CHAVES_LTM = ("ltm", "ltm_ref")


def injetar(novo):
    """Troca na memória SÓ o LTM dos tickers em `novo` (em todo módulo com `CVM`). Devolve {tk: ltm_antigo}.
    A série "anual" fica como está: os lotes a corrigem no import (ex.: lote4 grava `arrendamento_pago` de TIMS3/VIVT3/WEGE3)
    e o ITR não a altera."""
    antigos = {}
    for m in _modulos_com_cvm():
        for tk, reg in novo.items():
            if tk in m.CVM:
                antigos.setdefault(tk, ltm_de(m.CVM[tk]))
                m.CVM[tk]["ltm"] = reg["ltm"]
                m.CVM[tk]["ltm_ref"] = reg["ltm_ref"]
                m.CVM[tk][f"ltm_{reg['ltm_ref']}"] = reg["ltm"]
    return antigos


def main(argv=None):
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--trimestre", help="ex.: 3T26 (padrão: o último que fechou)")
    ap.add_argument("--simular", metavar="TRIM", help="ensaio com um trimestre já coletado (ex.: 2T26); sem download")
    ap.add_argument("--gravar", action="store_true", help="grava a coleta nova em dados/cvm_series.json")
    ap.add_argument("--saida", help="pasta do boletim (padrão: BOLETINS/)")
    args = ap.parse_args(argv)

    simulado = bool(args.simular)
    rotulo = (args.simular or args.trimestre or trimestre_atual()).upper()
    ano, mes, dt_ref = interpretar_trimestre(rotulo)
    zip_path = cc.CACHE / f"itr_{ano}.zip"
    if not simulado:
        print(f"Baixando {cc.URL['ITR'].format(a=ano)} …")
        zip_path = baixar_itr(ano)
    elif not zip_path.exists():
        print(f"sem cache {zip_path.name} para simular")
        return 2

    import golden
    ant = golden.carregar()
    # o hall = os tickers do golden: detecta e coleta ANTES de carregar os lotes (a coleta lê ZIPs grandes; junto dos lotes falta memória)
    hall = [t for t in ant if t not in FORA_DO_HALL]
    import zipfile
    with zipfile.ZipFile(zip_path) as z:
        pub, aus, sem = quem_publicou(z, hall, dt_ref)
    print(f"ITR {rotulo} ({dt_ref}): {len(pub)} de {len(hall)} tickers do hall publicaram.")
    if not pub:
        print(f"nenhum ticker com {rotulo} ainda")
        return 0

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="temporada_")) / "cvm_series_novo.json"
    novo = coletar(pub, tmp, ano, mes)
    ruins = [tk for tk in pub if tk not in novo]
    if ruins:
        print("coleta sem LTM utilizável (ficam com o LTM antigo): " + ", ".join(ruins))
    import universo   # carrega os lotes (alguns segundos)
    antigos = injetar(novo)
    atual = universo.instantaneo_todos()
    mud = golden.comparar(ant, atual)
    causas_por_tk = {tk: causas(antigos.get(tk), novo[tk]["ltm"]) for tk in novo}
    lotes = {atual[tk]["lote"] for tk in {m[0] for m in mud} if tk in atual}
    dia = date.today().isoformat()
    texto = montar_boletim(dia, rotulo, pub, aus, sem, mud, causas_por_tk, lotes, simulado, ruins)
    pasta = pathlib.Path(args.saida) if args.saida else BOLETINS
    pasta.mkdir(parents=True, exist_ok=True)
    arq = pasta / f"{dia}-temporada{'-simulacao' if simulado else ''}.md"
    arq.write_text(texto, encoding="utf-8")
    print(texto)
    print(f"boletim: {arq}")
    if args.gravar and not simulado:
        alvo = cc.AQUI / "dados" / "cvm_series.json"
        tudo = json.loads(alvo.read_text(encoding="utf-8"))
        for tk, reg in novo.items():   # só o LTM; "anual" e auditoria do arquivo oficial ficam intactos
            tudo[tk].update({"ltm": reg["ltm"], "ltm_ref": reg["ltm_ref"], f"ltm_{reg['ltm_ref']}": reg["ltm"]})
        alvo.write_text(json.dumps(tudo, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"coleta gravada em {alvo.name}. Golden NÃO regravado: rode `python rodar_tudo.py --motivo \"…\"`.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
