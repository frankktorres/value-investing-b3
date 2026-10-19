"""Exporta para a tela o que os motores já calcularam: `python -m painel.exportar` → web/dados/hall.json e
web/dados/empresas/<TK>.json.

A tela só lê. Nada aqui recalcula conta, troca palavra ou grava veredito:
- palavra = a VIGENTE (dossiê gravado vence o hall; senão o golden — `relatorio.montar.vigente`); se o motor de hoje
  disser outra, vai em `palavra_motor` com aviso, como no relatório;
- central, compra e saída = os do relatório (`relatorio.montar`), com a nota da fonte (pior das origens, `modelo.pior`);
- o preço de hoje (COTAHIST) só posiciona o marcador na régua e o P/C informativo, igual ao monitor.
Dado pessoal não entra: da carteira só o ticker (já versionado em `carteira_tickers.json`). A pasta de saída é ignorada
pelo git (`garantir_ignorado` antes de gravar) — o JSON muda a cada rodada e é regerável.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

from relatorio.__main__ import _sem_inf
from relatorio.modelo import Numero, Relatorio

VERSAO = 1
AQUI = Path(__file__).resolve().parent
WEB = AQUI / "web"
DADOS = WEB / "dados"
NAO_CONCLUSIVO = "NÃO CONCLUSIVO"
SEM_PRECO = "sem preço de hoje"


# ------------------------------------------------------------------------------ peças puras
def numero_json(n: Numero) -> dict:
    """Número com a nota e a fonte já resolvidas (no modelo são @property e não entram no asdict)."""
    return {"rotulo": n.rotulo, "valor": n.valor, "unidade": n.unidade, "papel": n.papel, "obs": n.obs,
            "nota": n.nota, "fonte": n.fonte,
            "origens": [{"fonte": o.fonte, "nota": o.nota, "detalhe": o.detalhe} for o in n.origens]}


def relatorio_json(rel: Relatorio) -> dict:
    return _sem_inf({
        "versao": VERSAO, "tk": rel.tk, "nome": rel.nome, "data": rel.data, "origem": rel.origem,
        "palavra_motor": rel.palavra, "avisos": list(rel.avisos),
        "secoes": [{"titulo": s.titulo, "numeros": [numero_json(n) for n in s.numeros], "texto": list(s.texto),
                    "avisos": list(s.avisos),
                    "tabelas": [{"titulo": t, "cabecalho": list(c), "linhas": [list(x) for x in ls]}
                                for t, c, ls in s.tabelas]}
                   for s in rel.secoes]})


def _secao(rel: Relatorio, titulo: str):
    return next((s for s in rel.secoes if s.titulo == titulo), None)


def _num(rel: Relatorio, titulo: str, prefixo: str) -> Numero | None:
    s = _secao(rel, titulo)
    return next((n for n in s.numeros if n.rotulo.startswith(prefixo)), None) if s else None


def _finito(v) -> float | None:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) else None


def linha_hall(rel: Relatorio, vigente: str | None, preco_hoje: float | None, *, dossie: bool,
               fora_do_hall: bool, na_carteira: bool) -> dict:
    """Uma linha do hall a partir do relatório já montado. Pura: testável com relatório sintético."""
    from monitor_semanal import alerta
    n_central, n_preco = _num(rel, "Veredito", "Valor central"), _num(rel, "Veredito", "Preço")
    n_compra, n_saida = _num(rel, "Veredito", "Compra ("), _num(rel, "Veredito", "Saída (")
    palavra = vigente or rel.palavra
    avisos = []
    if vigente is None:
        avisos.append("Sem veredito vigente gravado: mostra a palavra do motor.")
    elif vigente != rel.palavra:
        avisos.append(f"O motor hoje diz {rel.palavra}; a palavra vigente ({vigente}) só muda com veredito novo.")
    central = _finito(n_central.valor) if n_central else None
    central = central if central and central > 0 else None
    nc = palavra == NAO_CONCLUSIVO or central is None
    compra = None if nc or n_compra is None else _finito(n_compra.valor)
    saida = None if nc or n_saida is None else _finito(n_saida.valor)
    preco = _finito(preco_hoje)
    preco = preco if preco and preco > 0 else None
    if preco is None:
        situacao = SEM_PRECO
    else:
        situacao = alerta(preco, compra if compra is not None else math.nan,
                          saida if saida is not None else math.nan, palavra)
    metodos = (_secao(rel, "Preço justo por método") or rel.secoes[0]).numeros if rel.secoes else []
    return {
        "tk": rel.tk, "nome": rel.nome, "origem": rel.origem, "dossie": dossie, "data_palavra": rel.data,
        "palavra": palavra, "palavra_motor": rel.palavra if rel.palavra != palavra else None,
        "central": central, "nota_central": n_central.nota if n_central else "—",
        "fonte_central": n_central.fonte if n_central else "",
        "compra": compra, "saida": saida,
        "saida_exc": bool(saida is not None and n_saida is not None and n_saida.rotulo.startswith("Saída (1,50")),
        "preco_ref": _finito(n_preco.valor) if n_preco else None, "nota_preco_ref": n_preco.nota if n_preco else "—",
        # sem palavra não há régua: o P/C de um central só informativo enganaria (fica no relatório da empresa)
        "preco_hoje": preco, "pc_hoje": preco / central if preco and central and not nc else None, "situacao": situacao,
        "n_central": sum(1 for n in metodos if n.papel == "central" and _finito(n.valor) is not None),
        "n_informativo": sum(1 for n in metodos if n.papel == "informativo" and _finito(n.valor) is not None),
        "fora_do_hall": fora_do_hall, "na_carteira": na_carteira, "avisos": avisos, "erro": None}


def linha_erro(tk: str, erro: BaseException, *, dossie: bool, fora_do_hall: bool, na_carteira: bool) -> dict:
    """O ticker que não montou aparece com o erro — nunca some da tela."""
    return {"tk": tk, "nome": "", "origem": "dossiê" if dossie else "hall", "dossie": dossie, "data_palavra": None,
            "palavra": None, "palavra_motor": None, "central": None, "nota_central": "—", "fonte_central": "",
            "compra": None, "saida": None, "saida_exc": False, "preco_ref": None, "nota_preco_ref": "—",
            "preco_hoje": None, "pc_hoje": None, "situacao": "erro", "n_central": 0, "n_informativo": 0,
            "fora_do_hall": fora_do_hall, "na_carteira": na_carteira, "avisos": [],
            "erro": f"{type(erro).__name__}: {erro}"}


# ------------------------------------------------------------------------------ dados reais
def palavra_vigente(tk: str, data: str, dossie: bool) -> str | None:
    from relatorio.caso import veredito_gravado
    from relatorio.montar import vigente
    return vigente({"tk": tk, "data": data, "dossie": True if dossie else None,
                    "gravado": veredito_gravado(tk, data) if dossie else None})[1]


def tickers() -> tuple[list[str], set[str]]:
    """(todos os tickers da tela, os que têm ficha de dossiê) — hall (41) ∪ dossiês."""
    import universo
    from dossie import gerar
    hall = {e.ticker for _, emps, _ in universo.GRUPOS for e in emps}
    return sorted(hall | set(gerar.FICHAS)), set(gerar.FICHAS)


@contextmanager
def _motor_uma_vez():
    """O hall roda o motor uma vez só na exportação (cada `montar` de ticker do hall chamaria `avaliar_todos` de novo,
    ~2,5 s cada). Mesmo resultado: o motor é determinístico e nada é gravado."""
    import universo
    original = universo.avaliar_todos
    memo = original()
    universo.avaliar_todos = lambda: memo
    try:
        yield
    finally:
        universo.avaliar_todos = original


def _gravar_json(caminho: Path, obj) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    tmp = caminho.with_name(caminho.name + ".tmp")
    tmp.write_text(json.dumps(_sem_inf(obj), ensure_ascii=False, allow_nan=False, indent=1), encoding="utf-8",
                   newline="\n")
    os.replace(tmp, caminho)


def exportar(destino: Path = DADOS, hoje: str | None = None, log=print) -> dict:
    import hall03
    import monitor_semanal
    from relatorio.carteira import garantir_ignorado
    from relatorio.montar import montar

    hoje = hoje or date.today().isoformat()
    for p in (destino / "hall.json", destino / "empresas" / "X.json"):
        garantir_ignorado(p)                                    # dado regerável fica fora do git (e do Stop-hook)
    tks, dossies = tickers()
    carteira = set(monitor_semanal.CARTEIRA)
    avisos = []
    try:
        precos, pregao = monitor_semanal.ultimos_precos(tks, hoje)
    except (FileNotFoundError, ValueError, OSError) as ex:      # sem COTAHIST: régua e palavra valem, sem preço de hoje
        precos, pregao = {}, None
        avisos.append(f"Sem cotação de hoje ({type(ex).__name__}: {ex}).")
    velho = pregao is None or (date.fromisoformat(hoje) - date.fromisoformat(pregao)).days > monitor_semanal.DIAS_VELHO
    linhas, t0 = [], time.time()
    with _motor_uma_vez():
        for i, tk in enumerate(tks, 1):
            marca = dict(dossie=tk in dossies, fora_do_hall=tk in hall03.FORA_DO_HALL, na_carteira=tk in carteira)
            try:
                rel = montar(tk)
                linhas.append(linha_hall(rel, palavra_vigente(tk, rel.data, tk in dossies), precos.get(tk), **marca))
                _gravar_json(destino / "empresas" / f"{tk}.json", relatorio_json(rel))
            except Exception as ex:                             # noqa: BLE001 — a linha mostra o erro, nunca some
                linhas.append(linha_erro(tk, ex, **marca))
            log(f"[{i}/{len(tks)}] {tk} {linhas[-1]['palavra'] or linhas[-1]['erro']} ({time.time() - t0:.0f} s)")
    hall = {"versao": VERSAO, "gerado_em": datetime.now().isoformat(timespec="seconds"), "hoje": hoje,
            "pregao_hoje": pregao, "dado_velho": velho, "dias_velho": monitor_semanal.DIAS_VELHO, "avisos": avisos,
            "empresas": linhas}
    _gravar_json(destino / "hall.json", hall)
    return hall


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="exporta o hall e os relatórios para a tela (não grava veredito)")
    ap.add_argument("--hoje", help="data AAAA-MM-DD para o preço de hoje (padrão: hoje)")
    a = ap.parse_args(argv)
    hall = exportar(hoje=a.hoje)
    erros = [x["tk"] for x in hall["empresas"] if x["erro"]]
    print(f"hall.json: {len(hall['empresas'])} empresas · pregão {hall['pregao_hoje']}"
          + (f" · ERRO em {', '.join(erros)}" if erros else ""))
    return 1 if erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
