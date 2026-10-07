"""Fila ranqueada, "o que a análise completa precisa resolver" e o markdown do `06`.

Nada aqui emite palavra de veredito: o texto só usa P/C proxy (com o erro medido), EY e os testes.
Um teste (`test_triagem_regras`) injeta palavra no motor e exige que ela não apareça no `06`.
"""
from __future__ import annotations

import datetime as dt
import math
from dataclasses import dataclass, field

import pandas as pd

from backtest.motor.perfil import normaliza

from . import qualidade as Q
from .config import NOTAS_06_ANTIGO, PADRAO, ConfigTriagem, hash_config
from .universo import JA_ANALISADA, LIQUIDEZ

SIMBOLO = {Q.OK: "✓", Q.FALHA: "✗", Q.INDET: "?", Q.NA: "–"}
POR_PRECO = "preço (P/C proxy acima do corte)"
PERGUNTA = {
    "Q1": "retorno sobre capital ({t}): mostrar ROIC a reposição/ciclo acima do WACC ou descartar",
    "Q2": "caixa ({t}): o lucro vira caixa?",
    "Q3": "balanço ({t}): a dívida se paga sem refinanciar?",
    "Q4": "alocação ({t}): o capital retido rendeu?",
    "Q5": "proventos ({t}): a política de dividendo é recorrente?",
}


@dataclass
class Resultado:
    T: str
    piso: float
    tabela: pd.DataFrame                       # todas as companhias (pré-ledger + avaliadas)
    fila: list[dict] = field(default_factory=list)
    financeiras: list[dict] = field(default_factory=list)
    netnet: list[dict] = field(default_factory=list)
    a_mao: list[dict] = field(default_factory=list)
    por_preco: list[dict] = field(default_factory=list)
    funil: dict = field(default_factory=dict)
    cfg: ConfigTriagem = PADRAO


def n_ok(r: dict) -> int:
    return sum(t.status == Q.OK for t in r["q"].values())


def camada(r: dict) -> str:
    return "A" if r["passa"] else "B"


def pendencias(r: dict, cfg: ConfigTriagem = PADRAO) -> list[str]:
    """O que a análise completa precisa resolver — montado por regra, sem texto livre."""
    p = ["filtro 3 (dono, vetores V1–V6) e filtro 5 (por que o mercado erra): não medidos"]
    if "estatal" in normaliza(r.get("controle", "")):
        p.append("controlador estatal: listar interferências consumadas (§5)")
    for k in ("Q1", "Q2", "Q3", "Q4", "Q5"):
        t = r["q"].get(k)
        if t is not None and t.reprovou:
            p.append(PERGUNTA[k].format(t=t.texto) if t.status == Q.FALHA
                     else f"{k} sem dado suficiente ({t.texto})")
    if r["q"].get("Q1") and r["q"]["Q1"].status == Q.OK and r["plano"] == "industrial":
        p.append("ROIC medido é o contábil: conferir a custo de reposição (D10)")
    if r.get("sem_central"):
        p.append(f"sem central rápido ({r['sem_central']}): calcular o central completo")
    elif not r.get("confiavel"):
        p.append("central rápido não confiável (âncora <= 0 ou dispersão > 3): calcular o central completo")
    elif r.get("dispersao", 0) > cfg.disp_alerta:
        p.append(f"âncoras divergem ({_n(r['dispersao'], 1)}×)")
    if r.get("ciclicidade_diverge"):
        p.append("margem oscila mais que o perfil do FCA indica: normalizar o ciclo (§11.4)")
    if 0 < r.get("n_exercicios", 10) < 10:
        p.append(f"janela de {r['n_exercicios']} exercícios: quebra estrutural ou histórico curto (§11.4)")
    va = r.get("var_acoes", math.nan)
    if isinstance(va, float) and math.isfinite(va) and abs(va) > cfg.q4_acoes_variacao:
        p.append(f"ações variaram {va:+.0%} na janela (emissão/recompra): Q4 aproximado")
    if normaliza(r.get("setor", "")).startswith("emp. adm. part."):
        p.append("holding: EBIT inclui equivalência — SOTP e desconto de holding")
    if r.get("utility"):
        p.append("concessão/regulado: TIR real implícita contra rf e Ke (§4)")
    if r.get("outras_classes"):
        p.append(f"outras classes negociadas ({r['outras_classes']}): escolher a classe, tag along")
    mes = str(r.get("mes_encerramento") or "")
    if mes and mes not in ("12", "12.0"):
        p.append(f"exercício encerra no mês {mes}: inflação por ano desalinhada")
    for t in r.get("cadeia") or [r["ticker"]]:          # nota do código antigo (ODPV3 -> SAUD3)
        if t in NOTAS_06_ANTIGO:
            p.append(NOTAS_06_ANTIGO[t] + (f" [como {t}]" if t != r["ticker"] else ""))
    return p


def _pct(s: pd.Series, asc: bool) -> pd.Series:
    """Percentil de posto médio, (posto − 0,5) ÷ n: 0 = melhor, 0,5 = neutro. NaN fica NaN."""
    n = s.notna().sum()
    return (s.rank(ascending=asc, method="average") - 0.5) / n if n else s * math.nan


def ordenar(linhas: list[dict], cfg: ConfigTriagem = PADRAO) -> list[dict]:
    if not linhas:
        return []
    d = pd.DataFrame({"i": range(len(linhas)),
                      "camada": [camada(r) for r in linhas],
                      "n_ok": [n_ok(r) for r in linhas],
                      "ey": [r.get("ey", math.nan) for r in linhas],
                      "pc": [r["pc"] if r.get("confiavel") else math.nan for r in linhas]})
    # EY sem valor = pior posto (1,0); P/C sem central confiável = neutro (0,5): não ter central
    # não pode valer mais que ter um central caro, nem menos que um central mediano.
    d["p_ey"] = _pct(d["ey"], asc=False).fillna(1.0)
    d["p_pc"] = _pct(d["pc"], asc=True).fillna(0.5)
    d["preco_score"] = (d["p_ey"] + d["p_pc"]) / 2
    d = d.sort_values(["camada", "n_ok", "preco_score", "i"], ascending=[True, False, True, True])
    return [linhas[i] | {"preco_score": s} for i, s in zip(d["i"], d["preco_score"])]


def montar(tab: pd.DataFrame, linhas: list[dict], T: str, piso: float,
           cfg: ConfigTriagem = PADRAO) -> Resultado:
    avaliadas = [r for r in linhas if not r.get("motivo")]
    pos_ledger = [r for r in linhas if r.get("motivo")]
    r = Resultado(T=T, piso=piso, tabela=_tabela(tab, linhas), cfg=cfg)

    ind = [x for x in avaliadas if x["plano"] == "industrial"]
    r.financeiras = ordenar([x for x in avaliadas if x["plano"] != "industrial"], cfg)
    r.netnet = [x for x in ind if x.get("netnet")]
    r.por_preco = [x for x in ind if x.get("confiavel") and x["pc"] > cfg.corte_pc]
    r.a_mao = [x for x in ind if x.get("sem_central") or x.get("quebra")]
    elegiveis = [x for x in ind if x not in r.por_preco and not x.get("quebra")
                 and (x["passa"] or n_ok(x) >= cfg.fila_min_ok)]
    r.fila = ordenar(elegiveis, cfg)[:cfg.tamanho_fila]
    pos = {x["ticker"]: i for i, x in enumerate(r.fila, 1)}
    r.tabela["fila"] = r.tabela["ticker"].map(pos)

    motivos = tab["motivo"].replace("", pd.NA).dropna().value_counts().to_dict()
    for x in pos_ledger:
        motivos[x["motivo"]] = motivos.get(x["motivo"], 0) + 1
    r.funil = {"universo": len(tab), "excluidas": motivos,
               "avaliadas": len(avaliadas), "industriais": len(ind),
               "financeiras": len(r.financeiras),
               "passam_portao": sum(x["passa"] for x in ind),
               "camada_b": sum(1 for x in ind if not x["passa"] and n_ok(x) >= cfg.fila_min_ok),
               "por_preco": len(r.por_preco)}
    return r


def _tabela(tab: pd.DataFrame, linhas: list[dict]) -> pd.DataFrame:
    av = {x["ticker"]: x for x in linhas}
    out = []
    for lin in tab.to_dict("records"):
        x = av.get(lin["ticker"], lin)
        out.append({k: x.get(k) for k in ("ticker", "cnpj", "cd_cvm", "setor", "liquidez", "motivo",
                                           "detalhe", "preco", "data_preco", "central", "pc",
                                           "dispersao", "confiavel", "sem_central", "ey", "ncav_pa",
                                           "netnet", "passa", "n_exercicios", "wacc_real", "quebra",
                                           "var_acoes")}
                   | {k: f"{t.status} {t.texto}" for k, t in (x.get("q") or {}).items()})
    return pd.DataFrame(out)


# ----------------------------------------------------------------------------------- markdown
def _n(x, nd=2) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    if isinstance(x, float) and math.isinf(x):
        return "∞"
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pc(r: dict) -> str:
    if r.get("sem_central") or not math.isfinite(r.get("pc", math.nan)):
        return "—"
    s = _n(r["pc"])
    return s if r.get("confiavel") else f"{s} (n/c)"


def _qs(r: dict) -> str:
    return " ".join(SIMBOLO[r["q"][k].status] for k in ("Q1", "Q2", "Q3", "Q4", "Q5"))


def _ey(r: dict) -> str:
    e = r.get("ey", math.nan)
    if isinstance(e, float) and math.isinf(e):
        return "EV ≤ 0"
    return "—" if not math.isfinite(e) else f"{e:.1%}".replace(".", ",")


def _linha(i: int, r: dict) -> str:
    return (f"| {i} | **{r['ticker']}** | {camada(r)} | {r.get('setor', '')} | {_n(r['preco'])} | "
            f"{_pc(r)} | {_ey(r)} | {_qs(r)} |")


CAB = ("| # | Ticker | Camada | Setor (FCA) | Preço | P/C proxy | EY | Q1 Q2 Q3 Q4 Q5 |\n"
       "|---|---|---|---|---|---|---|---|")


def markdown(r: Resultado) -> str:
    c, f = r.cfg, r.funil
    rf_dias = (dt.date.fromisoformat(r.T) - dt.date.fromisoformat(c.data_mercado)).days
    aviso_rf = ("" if abs(rf_dias) <= c.aviso_mercado_dias else
                f"\n> **Atenção:** a rf é de {c.data_mercado}, {abs(rf_dias)} dias distante de T — atualizar antes de decidir.\n")
    s = [f"""# TRIAGEM E FILA DE ANÁLISE

*Gerado por `python -m triagem.rodar` em {dt.date.today().isoformat()} — **não editar à mão** (a próxima rodada sobrescreve;
o histórico fica em `_historico/` e em `prospectivo/triagem.jsonl`). Config `{hash_config(c)}`.*

**Regra dura (vale desde 07/09):** a triagem define **a fila**, nunca o veredito. Prova antiga: LEVE3 passou 7/7 e a análise
completa deu JUSTA/CARA; UNIP6 passou 5/7 e deu ARMADILHA. Aqui não existe palavra: o central rápido é o do motor reduzido da
Etapa 3, cujo erro **medido** contra a régua completa é de **±{_n(c.erro_proxy_pc)} de P/C** (mediana |ΔP/C| nos 41 do hall,
consulta única de 06/10/2026). A D5 continua aberta: nenhuma régua desta mesa tem validação empírica.

## 1. Como a fila é feita

**Data:** preços de fechamento de **{r.T}** (COTAHIST, B3) · rf {c.rf_real:.2%} real ({c.titulo_rf}) · π {c.pi:.2%} ·
Ke real = rf + {c.premio:.0%} — os mesmos do hall.{aviso_rf}

**Universo:** toda ação/unit com negócio nos 60 pregões até T, **uma linha por companhia** (a classe mais líquida).
**Liquidez mínima R$ {_n(r.piso / 1e6)} mi/dia** = maior entre o piso do backtest (R$ 500 mil de mai/2014 corrigidos pelo
IPCA) e o volume que permite vender uma posição de R$ {_n(c.posicao_tipica, 0)} em {c.pregoes_saida} pregões com até
{c.participacao_max:.0%} do volume (posição típica declarada pelo Frank em 06/10/2026).

**Exclusões (doutrina §8 e §2), nesta ordem:** liquidez · sem identidade na CVM · recuperação judicial/extrajudicial,
falência ou liquidação (FCA `Situação do emissor` ou CODBDI de recuperação no último pregão) · setores a evitar (educação;
aviação e resseguro por ticker; tecnologia sem lucro) · já analisada no hall · sem DFP · menos de {c.min_exercicios}
exercícios · último DFP atrasado.

**Qualidade (Buffett), sobre o ledger point-in-time da CVM:**

| Teste | Régua | Filtro |
|---|---|---|
| Q1 | ROIC real (contábil, Fisher pelo IPCA do ano) > WACC real de hoje em ≥ {c.q1_frac:.0%} dos exercícios; financeira: ROE real > Ke real | 1 |
| Q2 | FCO > 0 em ≥ {c.q2_frac:.0%} dos exercícios | 2 |
| Q3 | DL/EBITDA ≤ {_n(c.q3_dl_ebitda, 1)} no último balanço, ou caixa líquido | 2 |
| Q4 | R$ 1 retido virou ≥ R$ {_n(c.q4_minimo)} de valor de mercado (real; ações de D0 pelo FRE quando há); prejuízo acumulado reprova; n/a se o retido < {c.q4_materialidade:.0%} do valor inicial | 3 (alocação) |
| Q5 | pagou provento em ≥ {c.q5_frac:.0%} dos exercícios | 4 |

✓ passou · ✗ reprovou · ? dado insuficiente (conta como reprovação) · – não se aplica.
**Portão (camada A):** Q1 ✓ e no máximo {c.max_reprovacoes_q2_q5} reprovação em Q2–Q5. **Camada B:** ≥ {c.fila_min_ok} testes ✓,
fora do portão — entra para a análise completa resolver o que reprovou. A fila ordena por camada, nº de ✓ e preço
(média dos percentis do EY de Greenblatt e do P/C proxy; sem central confiável o P/C conta como mediano).

**Preço, sem palavra:** P/C proxy = preço ÷ central rápido (EPV de meio de ciclo, Owner Earnings, reprodução). "(n/c)" =
não confiável (âncora ≤ 0 ou dispersão > {_n(c.disp_confiavel, 1)}). Sai da fila quem tem central confiável e
**P/C proxy > {_n(c.corte_pc)}** (= {_n(c.limite_cara)} + o erro de {_n(c.erro_proxy_pc)}: mesmo com o erro a favor
ficaria acima de 1,10). EY = EBIT ajustado (sem o excesso de outras receitas, §7) ÷ (valor de mercado + dívida líquida).

**Funil:** {f['universo']} companhias negociadas → {f['avaliadas']} avaliadas ({f['industriais']} não financeiras,
{f['financeiras']} financeiras) → **{f['passam_portao']} passam no portão** · {f['camada_b']} na camada B ·
{f['por_preco']} fora por preço.
"""]
    s.append(f"## 2. Fila ({len(r.fila)})\n\n{CAB}")
    s += [_linha(i, x) for i, x in enumerate(r.fila, 1)]
    s.append("\n### O que cada análise completa precisa resolver\n")
    for x in r.fila:
        q = "; ".join(f"{k} {t.texto}" for k, t in x["q"].items())
        s.append(f"- **{x['ticker']}** ({camada(x)}; {q})")
        s += [f"  - {p}" for p in pendencias(x, c)]

    s.append("\n## 3. Financeiras — dado incompleto, conferir à mão\n")
    s.append("O ledger da CVM perde o lucro de bancos em parte dos anos (regex de descrição, defeito conhecido da Etapa 3, "
             "não corrigido). Q2, Q3, NCAV e EY não se aplicam.\n")
    s.append(CAB)
    s += [_linha(i, x) for i, x in enumerate(r.financeiras, 1)]

    s.append("\n## 4. Deep value — Graham net-net (fora da fila)\n")
    s.append(f"Preço ≤ {c.netnet_fracao:.0%} do NCAV por ação (ativo circulante − passivo total − minoritários). "
             "Dispensa o Q1 (exceção de Graham/Schloss no §2), não as exclusões. Construtora/incorporadora: o AC é "
             "estoque de imóveis e o NCAV superestima.\n")
    if r.netnet:
        s.append("| Ticker | Setor | Preço | NCAV/ação | Q1 Q2 Q3 Q4 Q5 |\n|---|---|---|---|---|")
        s += [f"| **{x['ticker']}** | {x.get('setor', '')} | {_n(x['preco'])} | {_n(x['ncav_pa'])} | {_qs(x)} |"
              for x in r.netnet]
    else:
        s.append("Nenhuma.")

    s.append("\n## 5. Avaliar à mão — sem central rápido ou com quebra estrutural\n")
    s.append(f"Quebra estrutural = a base de ações mudou mais de {c.quebra_var_acoes:.0%} entre o início da janela e T "
             f"(emissão grande, incorporação, ou evento em ações que a tabela de eventos não capturou — variações de "
             f"milhares de % são esse último caso) ou o ativo do ITR mais novo passa de {_n(c.quebra_ativo, 1)}× o do "
             "último DFP. Os exercícios por ação não comparam com o preço de hoje, então nem o portão nem o central "
             "valem: a análise começa por reconstruir a base.\n")
    if r.a_mao:
        s.append("| Ticker | Setor | Motivo | Q1 Q2 Q3 Q4 Q5 |\n|---|---|---|---|")
        s += [f"| **{x['ticker']}** | {x.get('setor', '')} | "
              f"{'quebra estrutural: ' + x['quebra'] if x.get('quebra') else x['sem_central']} | {_qs(x)} |"
              for x in r.a_mao]
    else:
        s.append("Nenhuma.")

    s.append(f"\n## 6. Fora da fila por preço (P/C proxy > {_n(c.corte_pc)} com central confiável)\n")
    s.append(", ".join(f"{x['ticker']} ({_n(x['pc'])})" for x in sorted(r.por_preco, key=lambda x: x["pc"]))
             or "Nenhuma.")

    s.append("\n## 7. Excluídas\n\n| Motivo | Nº |\n|---|---|")
    s += [f"| {m} | {n} |" for m, n in sorted(f["excluidas"].items(), key=lambda kv: -kv[1])]
    t = r.tabela
    lista = t[t["motivo"].fillna("").ne("") & ~t["motivo"].isin([LIQUIDEZ, JA_ANALISADA])]
    s.append("\n| Ticker | Motivo | Detalhe |\n|---|---|---|")
    s += [f"| {x['ticker']} | {x['motivo']} | {x['detalhe'] or ''} |"
          for x in lista.sort_values(["motivo", "ticker"]).to_dict("records")]
    hall = sorted(t.loc[t["motivo"] == JA_ANALISADA, "ticker"])
    s.append(f"\n**Já analisadas no hall ({len(hall)}; ver `03`):** {', '.join(hall)}.")

    s.append("""
## 8. Como pedir uma triagem nova

> "Rode a triagem (`cd ferramentas && python -m triagem.rodar`) e me diga quais da fila valeriam o prompt completo."

Cada análise completa parte das pendências da seção 2 e usa o `02-prompt-analise-completa.md`. O veredito só existe depois
dela — e entra no registro prospectivo (`registro_prospectivo.py`).
""")
    return "\n".join(s)
