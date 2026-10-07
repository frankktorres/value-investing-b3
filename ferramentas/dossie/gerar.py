"""Anexo mecânico do dossiê (02 v4) e o veredito em JSON. Uso: cd ferramentas && python -m dossie.gerar BLAU3

1ª passada do motor (qualitativo neutro) → evidência (motor, CVM, FRE, triagem) → notas da regra 11 (`notas.py`) com os
insumos não mecânicos do dossiê (`dossie/insumos/<TK>.json`, cada um com fonte) → 2ª passada com a média da regra 11.

O peso dobrado do controlador (doutrina §10) entra sem mexer no motor: o `qualitativo` vai com UMA chave, a média da
regra 11, e a média simples que o motor faz de uma chave é ela mesma. O hall segue com o `QUAL` arbitrado até a decisão
da fatia 7 (divergência declarada).

Saídas: `DOSSIES/dados/<TK>-<data>.md` (anexo, não editar à mão) e `dossie/vereditos/<TK>-<data>.json`.
"""
from __future__ import annotations

import importlib
import json
import pathlib
import sys
from datetime import date

from dossie import base, evidencia as ev, fre, notas
from lote1_bancos import MK
from motor_nao_financeiras import avaliar

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent.parent
FICHAS = {"BLAU3": "dossie.fichas.blau3", "CMIN3": "dossie.fichas.cmin3", "HYPE3": "dossie.fichas.hype3"}
ANO_FRE = 2026
DOUTRINA, TEMPLATE = "v2.2", "02 v4"
NOTAS = ("moat", "gestao", "controlador", "ciclo", "fisher")


def insumos(tk: str) -> dict:
    arq = AQUI / "insumos" / f"{tk}.json"
    return json.loads(arq.read_text(encoding="utf-8")) if arq.exists() else {}


def _valor(ins: dict, chave: str, padrao=None):
    """Insumo do dossiê = {"valor": ..., "fonte": "...", "nota_fonte": "A|B"}; sem fonte A/B não vale (regra 11)."""
    x = ins.get(chave)
    if not x:
        return padrao, "sem insumo do dossiê"
    if x.get("nota_fonte") not in ("A", "B") or not x.get("fonte"):
        raise ValueError(f"insumo {chave} sem fonte A/B: {x}")
    return x["valor"], f"{x['fonte']} [{x['nota_fonte']}]"


def calcular(tk: str) -> dict:
    with base.isolado(tk):      # ticker do hall (HYPE3): os proventos da B3 não vazam para os lotes no mesmo processo
        return _calcular(tk)


def _calcular(tk: str) -> dict:
    ficha = importlib.import_module(FICHAS[tk])
    r0 = avaliar(ficha.empresa(), MK)
    anos = ficha.ANOS
    ins = insumos(tk)
    cnpj = base.CNPJ[tk]
    eventos = base.eventos_em_acoes(tk)

    mg = ev.margens(tk, anos, r0["op"]["med_outras"], True)
    rec = ev.receitas_reais(tk, anos)
    fr = fre.resumo(cnpj, ANO_FRE)
    rem = fr["remuneracao"]["dados"]
    rem_l, rem_txt = ev.remuneracao_sobre_lucro(tk, rem, anos)
    listado = min(a for a in anos if base.fechamento_do_ano(tk, int(a)))
    dil, dil_txt = ev.diluicao(tk, anos, eventos, listado)
    r1, r1_f = ev.r1_da_triagem(tk), "Q4 da última triagem"
    if r1 is None:      # ticker do hall fica fora da triagem: o mesmo Q4, rodado só para ele, entra como insumo com fonte
        r1, r1_f = _valor(ins, "r1_retido")
    pr_bruto, pr_txt = ev.partes_relacionadas_bruto(tk, fr["partes_relacionadas"]["dados"], anos[-1])
    tag = fre.tag_along(cnpj, ANO_FRE)

    ma, ma_f = _valor(ins, "ma_ruim")
    interf, interf_f = _valor(ins, "interferencias")
    pr, pr_f = _valor(ins, "partes_rel_sobre_receita")
    tag_v, tag_f = _valor(ins, "tag_along", (tag or {}).get("ON") if isinstance(tag, dict) else None)
    disc, disc_f = _valor(ins, "discricionario", False)
    fis = ins.get("fisher", {}).get("respostas") or ["sem"] * 15

    base_n = {
        "moat": notas.moat(r0["roic_serie"], r0["wacc_real"], [m["bruta"] for m in mg.values() if m["bruta"] is not None],
                           [m["ebit"] for m in mg.values()]),
        "ciclo": notas.ciclo(list(rec.values()), [m["ebit"] for m in mg.values()], ev.anos_prejuizo(tk, anos)),
        "gestao": notas.gestao(r1, dil, rem_l, ma),
        "controlador": notas.controlador(fre.tem_controlador(fr["acionistas"]["dados"]), tag_v, pr, interf),
        "fisher": notas.fisher(fis),
    }
    aj = ins.get("ajustes", {})
    final = {k: notas.final(base_n[k], **aj.get(k, {})) for k in NOTAS}
    media = notas.media(*(final[k] for k in NOTAS), discricionario=bool(disc))

    dc = ins.get("desconto_controlador")       # {"tipo": "zero"|"fixo"|"cenarios", "razao": ..., ...} do D3 do dossiê
    r = avaliar(ficha.empresa(qualitativo={"media_regra11": media}, desconto_controlador=dc), MK)
    if not dc:      # regra 8 do 02: a linha de desconto é obrigatória; sem ela o central não está pronto (adversário, 07/10)
        r = dict(r, palavra="NÃO CONCLUSIVO", confianca="não conclusivo (desconto de controlador pendente — D3)")
    return dict(tk=tk, r=r, r0=r0, dc=dc, anos=anos, mg=mg, rec=rec, fr=fr, rem_txt=rem_txt, rem_l=rem_l, dil=dil, dil_txt=dil_txt,
                r1=r1, pr_bruto=pr_bruto, pr_txt=pr_txt, tag=tag, fontes_ins=dict(ma=ma_f, interf=interf_f, pr=pr_f, tag=tag_f,
                disc=disc_f, r1=r1_f), disc=bool(disc), base_n=base_n, aj=aj, final=final, media=media, eventos=eventos,
                mna=ev.mna_provavel(tk, anos), listado=listado,
                norm=ficha.normalizacao(dc) if hasattr(ficha, "normalizacao") else None)      # cíclica: ciclo em número (02 regra 7)


def _bloco_ciclo(n: dict) -> list[str]:
    """Normalização do ciclo em número (02 regra 7): preço, câmbio, margem e volume de meio, e a sensibilidade do método."""
    m, vol = n["minerio"], n["volume"]
    L = ["## Normalização do ciclo (02 regra 7)", "",
         f"Base do índice: {m['base']} (último mês com minério, PTAX, IPCA e CPI-US).", "",
         "| Item | Meio de ciclo (2016–25, R$/US$ de hoje) | 12m (jul/25–jun/26, nominal) |", "|---|---|---|",
         f"| Minério 62% em R$/t | {_f(m['meio_rs_real'], 0)} | {_f(m['ltm_rs'], 0)} |",
         f"| Minério 62% em US$/t | {_f(m['meio_usd_real'], 1)} (real; nominal {_f(m['meio_usd_nominal'], 1)}) | {_f(m['ltm_usd'], 1)} |",
         f"| Câmbio R$/US$ | {_f(m['meio_fx_real'], 3)} (real) | {_f(m['ltm_ptax'], 3)} |",
         f"| Volume vendido (Mt) | {_f(vol['meio'], 1)} — {vol['razao']} | {_f(vol['ltm'], 1)} |", "",
         f"Fator de preço da receita de meio = {_f(m['fator'], 3)} · fator de volume = {_f(vol['fator'], 3)} · "
         f"custo que acompanha o preço = {_f(n['custo_variavel'], 1, True)} da receita.", "",
         "| Exercício | Minério R$/t de hoje | Fator de preço (meio ÷ ano) | Volume (Mt) |", "|---|---|---|---|"]
    for a, f in m["fator_preco"].items():
        L.append(f"| {a} | {_f(m['anual'].loc[int(a), 'rs_real'], 0)} | {_f(f, 3)} | {_f(vol['anos'].get(a), 1)} |")
    L += ["", "| Método (sensibilidade; o adotado foi fixado antes do veredito) | Receita de meio (R$ bi) | Margem EBIT mediana | Central R$ | Régua |",
          "|---|---|---|---|---|"]
    for k, s in n["sensibilidade"].items():
        L.append(f"| {k} | {_f(s['receita_meio'] / 1e6, 2)} | {_f(s['m50'], 1, True)} | {_f(s['central'])} | {s['palavra']} |")
    return L + [""]


def _f(x, casas=2, pct=False):
    if x is None:
        return "—"
    if isinstance(x, str):
        return x
    return f"{100 * x:,.{casas}f}%".replace(",", "X").replace(".", ",").replace("X", ".") if pct else \
        f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def anexo(c: dict) -> str:
    tk, r, fr = c["tk"], c["r"], c["fr"]
    L = [f"# {tk} — anexo mecânico do dossiê ({TEMPLATE}) · data-base {base.DATA_BASE} · doutrina {DOUTRINA}",
         f"*Gerado por `python -m dossie.gerar {tk}` em {date.today().isoformat()} — não editar à mão. Fontes: CVM DFP/ITR/FRE (A), "
         "COTAHIST e proventos da B3 (A), StatusInvest só para datas de pagamento (C).*", "",
         "## Veredito mecânico (motor do hall, Ke da casa)", "",
         f"Preço R$ {_f(base.preco(tk))} · central R$ {_f(r['central'])} · P/C {_f(r['pc'])} · "
         f"régua **{r['palavra_regua']}** → palavra final **{r['palavra']}** (dispersão {_f(r['dispersao'])}, confiança {r['confianca']})", "",
         "| Âncora | R$/ação |", "|---|---|"] + [f"| {k} | {_f(v)} |" for k, v in r["ancoras"].items()] + [
         "", f"WACC real {_f(r['wacc_real'], 1, True)} · ROIC filtro {_f(r['roic_filtro'], 1, True)} · margem normalizada "
         f"{_f(r['m'], 1, True)} · g implícito (DCF reverso) {_f(r['g_implicito'], 1, True)} · vence a RF? {r['vence_rf']} · "
         f"DL/EBITDA {_f(r['dl_ebitda'])} · defasagem do provento {_f(r['defasagem_meses'], 1)} meses",
         f"Compra R$ {_f(r.get('compra'))} · saída R$ {_f(r.get('saida'))} · notas: " +
         " · ".join(f"{k} {_f(v, 1)}" for k, v in r["notas"].items()), ""]
    if c.get("norm"):
        L += _bloco_ciclo(c["norm"])
    L += ["## Série por exercício", "", "| Exercício | Receita real (R$ mi) | Margem bruta | Margem EBIT aj. | ROIC real (reposição) |",
          "|---|---|---|---|---|"]
    for a in c["anos"]:
        m = c["mg"].get(a, {})
        L.append(f"| {a} | {_f(c['rec'].get(a, 0) / 1e3, 0)} | {_f(m.get('bruta'), 1, True)} | {_f(m.get('ebit'), 1, True)} | "
                 f"{_f(c['r0']['roic_serie'].get(a), 1, True)} |")
    L += ["", "## Notas por evidência (regra 11)", "", "| Nota | Base | Componentes | Ajuste | Final |", "|---|---|---|---|---|"]
    for k in NOTAS:
        aj = c["aj"].get(k, {})
        L.append(f"| {k} | {c['base_n'][k].base} | {'; '.join(c['base_n'][k].componentes)} | "
                 f"{aj.get('ajuste', 0):+d} {('(' + aj.get('fonte', '') + ' [' + aj.get('nota_fonte', '') + '])') if aj.get('ajuste') else ''} | "
                 f"**{c['final'][k]}** |")
    L += ["", f"Média da regra 11 = **{_f(c['media'], 2)}** (controlador com peso {'2 — poder discricionário: ' + c['fontes_ins']['disc'] if c['disc'] else '1'}). "
          f"Insumos do dossiê: M&A {c['fontes_ins']['ma']} · interferências {c['fontes_ins']['interf']} · partes relacionadas "
          f"{c['fontes_ins']['pr']} · tag along {c['fontes_ins']['tag']}.", "",
          "## Gestão e controle (FRE " + str(ANO_FRE) + ", versão " + str(fr["documento"]["versao"] if fr.get("documento") else "—") + ")", "",
          f"- R$ 1 retido (Q4 da triagem, mesmo dia-base): {_f(c['r1'])} — {c['fontes_ins']['r1']}",
          f"- Diluição: {_f(c['dil'], 2, True)} a.a. — {c['dil_txt']}",
          f"- Remuneração da administração ÷ lucro: {_f(c['rem_l'], 2, True)} — {c['rem_txt']}",
          f"- Partes relacionadas (bruto do FRE, só pista): {_f(c['pr_bruto'], 1, True)} — {c['pr_txt']}",
          f"- Saltos de intangível/investimentos > 20% do ativo (M&A a examinar): {', '.join(c['mna']) or 'nenhum'}",
          f"- Tag along no FRE: {c['tag'] if c['tag'] is not None else 'não há tabela no FRE (ver estatuto/FCA)'}",
          f"- Eventos em ações (B3): {c['eventos'] or 'nenhum'}", "", "**Acionistas (1º nível)**", "",
          "| Acionista | ON % | Total % | Controlador | Acordo |", "|---|---|---|---|---|"]
    for x in sorted(fr["acionistas"]["dados"], key=lambda x: -(x.get("pct_total") or 0))[:10]:
        L.append(f"| {x['acionista']} | {_f(x.get('pct_on'), 2)} | {_f(x.get('pct_total'), 2)} | {'sim' if x['controlador'] else ''} | "
                 f"{'sim' if x['acordo'] else ''} |")
    L += ["", "**Remuneração da administração (R$ mi por exercício)**", ""]
    for ex, v in sorted(fr["remuneracao"]["dados"].items()):
        L.append(f"- {ex}{' (PREVISTA, orçamento — fora das contas)' if ex > c['anos'][-1] else ''}: total {_f(v['total'] / 1e6, 1)} — " + ", ".join(f"{o} {_f(x / 1e6, 1)}" for o, x in v.items()
                                                                       if o not in ("total", "total_informado") and x))
    L += ["", "**Partes relacionadas (FRE; maiores montantes)**", "", "| Parte | Relação | Data | Montante (R$ mi) | Natureza |", "|---|---|---|---|---|"]
    for p in sorted(fr["partes_relacionadas"]["dados"], key=lambda p: -(p["montante"] or 0))[:12]:
        L.append(f"| {p['parte']} | {p['relacao']} | {p['data']} | {_f((p['montante'] or 0) / 1e6, 1)} | {(p['natureza'] or '')[:90]} |")
    rf_ = fr.get("relacao_familiar", {}).get("dados") or []
    L += ["", f"Relação familiar entre administradores (FRE): {len(rf_)} registro(s)" +
          ("".join(f"\n- {x['cargo_administrador']} ↔ {x['cargo_pessoa_relacionada']} ({x['parentesco']})" for x in rf_))]
    if fr.get("free_float", {}).get("dados"):
        L.append(f"\nFree float (FRE): {fr['free_float']['dados']}")
    L += ["", "**Fontes FRE:** " + "; ".join(f"{k}: {v['fonte'].get('link', '')}" for k, v in fr.items()
                                            if isinstance(v, dict) and v.get("fonte"))[:900]]
    if tk in {t for t, _ in base.CORRECOES_ACOES}:
        L += ["", "**Correções declaradas do dado da CVM:** " + "; ".join(f"{a}: {t}" for (t_, a), (_, t) in base.CORRECOES_ACOES.items() if t_ == tk)]
    return "\n".join(L) + "\n"


def veredito(c: dict) -> dict:
    r = c["r"]
    return dict(ticker=c["tk"], data_preco=base.DATA_BASE, preco=round(base.preco(c["tk"]), 2), central=round(r["central"], 4),
                pc=round(r["pc"], 4), palavra=r["palavra"], palavra_regua=r["palavra_regua"], notas_regra11=c["final"],
                desc_controlador=round(r["desc_controlador"], 4), desc_controlador_razao=(c["dc"] or {}).get("razao", "PENDENTE"),
                media_regra11=round(c["media"], 4), discricionario=c["disc"], doutrina=DOUTRINA, template=TEMPLATE,
                gerado_em=date.today().isoformat())


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    tk = (argv or sys.argv[1:])[0].upper()
    c = calcular(tk)
    d_md = RAIZ / "DOSSIES" / "dados"
    d_js = AQUI / "vereditos"
    d_md.mkdir(parents=True, exist_ok=True)
    d_js.mkdir(parents=True, exist_ok=True)
    (d_md / f"{tk}-{base.DATA_BASE}.md").write_text(anexo(c), encoding="utf-8")
    v = veredito(c)
    (d_js / f"{tk}-{base.DATA_BASE}.json").write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(v, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
