"""Seleção mecânica das 20 ações do hold-out B36 (pré-registro v3, emenda 8). Uso: cd ferramentas && python -m holdout_b36.selecionar

Regra (escrita antes de rodar; o script roda UMA vez e a lista vai para a emenda 8):
1. T = último pregão do COTAHIST até a data-base (19/11/2026). Universo = ações e units do mercado à vista.
2. Liquidez = média do VOLTOT nos 250 pregões até T; dia sem negócio conta zero (`cotahist.liquidez_media`).
3. Um papel por CNPJ, o mais líquido; exclusões mecânicas de `triagem.universo.classificar`: sem identidade na CVM,
   recuperação/falência (FCA + CODBDI), §8 (educação, AZUL, GOLL, IRBR), piso de liquidez da triagem.
4. Pelo menos 10 exercícios distintos de DFP visíveis na CVM em T, com demonstração no ZIP (`documentos_visiveis`).
5. Fora, por CNPJ, o que já foi olhado por gente: os 41 do golden, os 6 dossiês, a fila do `06` de 08/10 e a triagem
   manual de 07/09 (`triagem.config.NOTAS_06_ANTIGO`).
6. As 20 de maior liquidez; empate pela ordem alfabética do ticker.

Proibido por construção: nada aqui lê preço, central, P/C, Q1–Q5 ou notícia. `liquidez_media` lê só data/ticker/especi/
voltot e `ultimo_codbdi` só o CODBDI; a saída mostra ticker, CNPJ, código CVM, liquidez e nº de DFPs.
"""
from __future__ import annotations

import json
import pathlib
import sys

import pandas as pd

DATA_BASE = "2026-11-19"
JANELA = 250
MIN_DFP = 10
N = 20

DOSSIES = ("ALLD3", "BLAU3", "CMIN3", "FESA4", "SHUL4", "VLID3")
# Fila do `06-triagem-e-fila.md` de 08/10/2026 (só os tickers; nenhum número dela entra aqui).
FILA_06 = ("ALLD3", "ALUP11", "BLAU3", "CMIN3", "CYRE3", "FESA4", "GRND3", "INTB3", "LAVV3", "LREN3", "MDNE3", "MGLU3",
           "MILS3", "POMO4", "RIAA3", "SHUL4", "TGMA3", "TOTS3", "VLID3", "VULC3")

AQUI = pathlib.Path(__file__).resolve().parent


def ja_olhados() -> dict[str, str]:
    """ticker -> grupo pelo qual foi olhado por gente (o primeiro que o pegou)."""
    from triagem.config import NOTAS_06_ANTIGO
    from triagem.universo import tickers_analisados
    g: dict[str, str] = {}
    for grupo, tks in (("golden (41)", tickers_analisados()), ("dossiê", DOSSIES), ("fila do 06 de 08/10", FILA_06),
                       ("triagem manual 07/09", tuple(NOTAS_06_ANTIGO))):
        for t in tks:
            g.setdefault(t, grupo)
    return g


def selecionar(tab: pd.DataFrame, n_dfp: dict[int, int], olhados_cnpj: set[str], n: int = N,
               min_dfp: int = MIN_DFP) -> pd.DataFrame:
    """Função pura (o teste injeta tudo). `tab` = saída de `classificar`; devolve a tabela com `motivo_b36` e `ordem`.

    `ordem` (1..n) só nas escolhidas; `motivo_b36` vazio = elegível.
    """
    t = tab.copy()
    t["n_dfp"] = [int(n_dfp.get(int(c), 0)) if pd.notna(c) else 0 for c in t["cd_cvm"]]

    def motivo(l) -> str:
        if l["motivo"]:
            return l["motivo"]
        if l["cnpj"] in olhados_cnpj:
            return "já olhada por gente"
        if l["n_dfp"] < min_dfp:
            return f"menos de {min_dfp} DFPs"
        return ""

    t["motivo_b36"] = [motivo(l) for _, l in t.iterrows()]
    eleg = t[t["motivo_b36"] == ""].sort_values(["liquidez", "ticker"], ascending=[False, True])
    t["ordem"] = pd.NA
    t.loc[eleg.index[:n], "ordem"] = range(1, min(n, len(eleg)) + 1)
    return t


def contar_dfp(data_corte: str) -> dict[int, int]:
    """cd_cvm -> nº de exercícios (dt_refer) de DFP visíveis em T com demonstração no ZIP. Sem teto."""
    from backtest.ledger.indice_cvm import SEM_DEMONSTRACAO, documentos_visiveis
    v = documentos_visiveis("dfp", data_corte)
    v = v[v["estado"] != SEM_DEMONSTRACAO]
    return {int(k): int(x) for k, x in v.groupby("cd_cvm")["dt_refer"].nunique().items()}


def montar(data_base: str = DATA_BASE) -> tuple[pd.DataFrame, str]:
    from backtest import cotahist
    from backtest.ledger.identidade import _cnpj_do_ticker_em, mapa_ticker_cnpj
    from backtest.motor.perfil import cd_cvm_do_cnpj
    from triagem.config import IDENTIDADE_MANUAL, PADRAO
    from triagem.universo import classificar, fca_em, piso_liquidez, ultimo_codbdi

    ano = int(data_base[:4])
    cal = cotahist.calendario(range(ano - 1, ano + 1))
    T = cal.janela_anterior(data_base, 1)[1]          # último pregão <= data-base
    liq = cotahist.liquidez_media(T, cal=cal, janela=JANELA)
    cnpj_de = _cnpj_do_ticker_em(mapa_ticker_cnpj(), T)
    cnpj_liq = {t: cnpj_de.get(t) or IDENTIDADE_MANUAL.get(t) for t in liq.index}
    olhados = ja_olhados()
    olhados_cnpj = {c for t in olhados if (c := cnpj_de.get(t) or IDENTIDADE_MANUAL.get(t))}
    # o `classificar` marca o hall como "já analisada"; aqui o conjunto é o da regra 5 e vai à parte
    tab = classificar(liq, cnpj_liq, cd_cvm_do_cnpj, lambda cd: fca_em(int(cd), T), ultimo_codbdi(T),
                      piso_liquidez(T, PADRAO), set(), PADRAO)
    return selecionar(tab, contar_dfp(T), olhados_cnpj), T


def main(argv=None) -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    tab, T = montar()
    esc = tab[tab["ordem"].notna()].sort_values("ordem")
    print(f"B36 · T = {T} · janela {JANELA} pregões · ≥ {MIN_DFP} DFPs · {len(esc)} escolhidas")
    print("| # | Ticker | CNPJ | Cód. CVM | Liquidez (R$ mi/dia) | DFPs | Setor FCA |")
    print("|---|---|---|---|---|---|---|")
    for _, l in esc.iterrows():
        print(f"| {int(l['ordem'])} | {l['ticker']} | {l['cnpj']} | {int(l['cd_cvm'])} | {l['liquidez'] / 1e6:.1f} | "
              f"{l['n_dfp']} | {l.get('setor', '')} |")
    # funil (contagem por motivo, nas companhias acima do piso e no topo de liquidez)
    print("\nFunil (companhias por motivo):")
    for m, k in tab["motivo_b36"].replace("", "elegível").value_counts().items():
        print(f"- {m}: {k}")
    # quem foi pulado no caminho até a 20ª (para a emenda mostrar que a regra foi seguida)
    corte = esc["liquidez"].min() if len(esc) else 0
    pul = tab[(tab["liquidez"] >= corte) & (tab["motivo_b36"] != "")].sort_values("liquidez", ascending=False)
    print(f"\nPuladas acima da liquidez da 20ª ({len(pul)}): " +
          ", ".join(f"{l['ticker']} ({l['motivo_b36']})" for _, l in pul.iterrows()))
    out = AQUI / "selecao.json"
    out.write_text(json.dumps({"T": T, "janela": JANELA, "min_dfp": MIN_DFP,
                               "escolhidas": [dict(ordem=int(l["ordem"]), ticker=l["ticker"], cnpj=l["cnpj"],
                                                   cd_cvm=int(l["cd_cvm"]), liquidez=round(float(l["liquidez"]), 2),
                                                   n_dfp=int(l["n_dfp"]), setor=l.get("setor", ""),
                                                   outras_classes=l.get("outras_classes", ""))
                                              for _, l in esc.iterrows()]},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\nGravado: {out.relative_to(AQUI.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
