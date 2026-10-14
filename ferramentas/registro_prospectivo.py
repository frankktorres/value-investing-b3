"""Registro prospectivo dos vereditos — a validação da régua que o backtest não conseguiu fazer.

Por que existe (decisão de 06/10/2026, depois do portão do proxy reprovado na Etapa 3): a régua
depende de julgamento digitado à mão (receita de meio de ciclo, janela, cenários, desconto do
controlador), e nenhum motor mecânico a reproduziu nos 41 do golden (±1 nível 70,7%, mediana
|ΔP/C| 0,34). Um backtest de 2014–2025 testaria outra régua. A única validação fora da amostra que
sobra é registrar o veredito HOJE, com o preço de hoje, e medir depois.

Regras:
  · append-only: uma linha JSON por (origem, data do preço, ticker); nunca editar nem apagar. Registrar de
    novo a mesma data com outro valor LEVANTA erro — correção é nova rodada com nova data;
  · a chave é (origem, data do preço, ticker). `origem` = "hall" (golden das 41; linhas antigas sem o
    campo valem "hall"), "dossie" (vereditos de `dossie/vereditos/*.json`, `--dossie`) — o mesmo
    ticker pode estar no hall e no dossiê sem colidir;
  · registra o golden aprovado (o estado que passou no `rodar_tudo.py`), com o sha do golden e a
    versão da doutrina — a régua que produziu cada linha fica identificável;
  · vai para o git (`prospectivo/registro.jsonl`), não para `dados/`: é evidência, não cache;
  · AUD-102: o append-only é conferido, não só combinado. `prospectivo/registro.chain` guarda, por linha, o sha256
    encadeado (sha(anterior + linha)); `verificar()` recalcula e acusa linha editada, apagada ou inserida. Linha
    acrescentada à mão sem passar por `_gravar` também é acusada (a corrente não cobre). Limite: quem reescreve
    registro E corrente juntos passa — o git (`git diff HEAD`) é a segunda trava;
  · AUD-82: o preço gravado é o fechamento oficial do snapshot `dados/precos_hall_<data>.csv` quando a data do
    preço é a dele; fora disso cai em pc × central arredondado (None se a P/C não existe). Linhas já gravadas
    em 02/10/2026 (PRIO3, UGPA3, UNIP6, VBBR3 com preço de site; RECV3 None) ficam como estão: o passado não se edita.

Avaliação PRÉ-REGISTRADA (revisão de 14/10/2026, B25 — AUD-32/98/99, decisão do Frank; antes de qualquer horizonte vencido).
A versão de 06/10 (palavra × Ibovespa, "BARATA/RADAR ganham de CARA?") não tinha poder: 1 RADAR contra 34 CARA (AUD-32) e o
Ibovespa favorecia o hall (AUD-98). Mudar o que segue depois de existir resultado = olhar o resultado:
  · uma linha por (ticker, rodada), rodada = `data_preco`; hall e dossiê na mesma rodada → vale o dossiê; linha registrada
    depois do pregão do preço é marcada `retroativa` e a leitura sem elas é sensibilidade obrigatória (AUD-99);
  · horizonte principal 1 ano (`HORIZONTE_DIAS`), direção em 3 anos, a partir de `data_preco`;
  · retorno total (proventos brutos reinvestidos, eventos ajustados) pela máquina de `backtest/precos/retorno.py`;
    **retorno excedente = retorno do ticker − média simples do retorno do hall no mesmo período** (hall = rodada de origem
    "hall" mais recente com data <= a da linha). O Ibovespa fica só informativo (AUD-98);
  · **critério contínuo**: IC de postos (Spearman) entre P/C e retorno excedente em cada rodada com >= `N_MIN_IC` linhas
    válidas; hipótese IC < 0. Leitura só com >= `RODADAS_MIN` rodadas: "apoia" se a média dos IC < 0 com t <= −2 entre
    rodadas; "contraria" se a média >= 0; senão "inconclusiva" (função `avaliar`). P/C ausente e retorno ausente
    (None/NaN/inf) saem e são contados — do ticker em `excluidas`, do comparador em `hall_sem_retorno`; a tabela por palavra vira descrição, não critério.

Uso: python registro_prospectivo.py --data-preco 2026-10-02 --doutrina v2.2
     python registro_prospectivo.py --dossie     (data do preço e doutrina vêm de cada veredito)
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import pathlib
import sys

AQUI = pathlib.Path(__file__).parent
GOLDEN = AQUI / "tests" / "golden.json"
REGISTRO = AQUI / "prospectivo" / "registro.jsonl"
VEREDITOS = AQUI / "dossie" / "vereditos"
CAMPOS = ("palavra", "pc", "central", "lote")
COMPARA = (*CAMPOS, "preco", "doutrina")          # + golden_sha só no hall; no dossiê o sha do arquivo é informativo


def sha_arquivo(bruto: bytes) -> str:
    """sha256 (16 hex) do conteúdo com EOL normalizado para LF.

    AUD-108: com core.autocrlf=true o working tree tem CRLF e o blob do git tem LF; o sha do arquivo cru não batia com
    nenhum blob e mudava de máquina para máquina. Normalizado, é o sha do blob (`git show HEAD:caminho | sha256sum`).
    Linhas gravadas antes de 09/10/2026 usam o sha do arquivo cru em CRLF e não são reverificáveis por este caminho.
    """
    return hashlib.sha256(bruto.replace(b"\r\n", b"\n")).hexdigest()[:16]


def precos_oficiais(data_preco: str) -> dict[str, float]:
    """Fechamentos do snapshot do hall quando `data_preco` é a data dele; senão vazio (AUD-82)."""
    import precos_hall
    return precos_hall.ler() if data_preco == precos_hall.PRECO_DATA else {}


def linhas_do_golden(golden: dict, data_preco: str, doutrina: str, sha: str,
                     hoje: str, precos: dict[str, float] | None = None) -> list[dict]:
    out = []
    precos = precos or {}
    for tk in sorted(golden["tickers"]):
        g = golden["tickers"][tk]
        pc, central = g["pc"], g["central"]
        # o golden guarda pc e central arredondados: o produto volta com ruído de float — só vale sem preço oficial
        preco = precos.get(tk)
        if preco is None:
            preco = round(pc * central, 2) if pc is not None and math.isfinite(pc) else None   # AUD-52: pc null sem central
        out.append({"origem": "hall", "data_preco": data_preco, "ticker": tk, "preco": preco,
                    **{c: (None if isinstance(g[c], float) and math.isinf(g[c]) else g[c])
                       for c in CAMPOS},
                    "doutrina": doutrina, "golden_sha": sha, "registrado_em": hoje})
    return out


def ler(caminho: pathlib.Path = REGISTRO) -> list[dict]:
    if not caminho.exists():
        return []
    return [json.loads(x) for x in caminho.read_text(encoding="utf-8").splitlines() if x.strip()]


def linhas_dos_vereditos(pasta: pathlib.Path, hoje: str) -> list[dict]:
    """Uma linha por veredito de dossiê; `golden_sha` guarda o sha do arquivo do veredito."""
    arquivos = sorted(pasta.glob("*.json"))
    if not arquivos:
        raise FileNotFoundError(f"nenhum veredito em {pasta}")
    out = []
    for f in arquivos:
        bruto = f.read_bytes()
        v = json.loads(bruto.decode("utf-8"))
        for c in ("pc", "central", "preco"):
            if isinstance(v[c], float) and not math.isfinite(v[c]):
                v[c] = None
        out.append({"origem": "dossie", "data_preco": v["data_preco"], "ticker": v["ticker"],
                    "preco": v["preco"], "palavra": v["palavra"], "pc": v["pc"],
                    "central": v["central"], "lote": None, "doutrina": v["doutrina"],
                    "golden_sha": sha_arquivo(bruto), "registrado_em": hoje})
    return out


def _elo(anterior: str, linha: str) -> str:
    return hashlib.sha256((anterior + linha).encode("utf-8")).hexdigest()


def _corrente(linhas: list[str]) -> list[str]:
    out, h = [], ""
    for x in linhas:
        h = _elo(h, x)
        out.append(h)
    return out


def _caminho_corrente(caminho: pathlib.Path) -> pathlib.Path:
    return caminho.with_suffix(".chain")


def _linhas_cruas(caminho: pathlib.Path) -> list[str]:
    if not caminho.exists():
        return []
    return [x for x in caminho.read_text(encoding="utf-8").splitlines() if x.strip()]


def verificar(caminho: pathlib.Path = REGISTRO) -> list[str]:
    """Problemas de integridade do registro contra a corrente (lista vazia = íntegro). AUD-102."""
    linhas = _linhas_cruas(caminho)
    cc = _caminho_corrente(caminho)
    guardada = cc.read_text(encoding="utf-8").split() if cc.exists() else []
    if not guardada and linhas:
        return [f"{cc.name} ausente ou vazio: registro sem corrente"]
    esperada = _corrente(linhas)
    if len(guardada) != len(esperada):
        return [f"{len(linhas)} linhas no registro, {len(guardada)} na corrente"]
    return [f"linha {i + 1} ({json.loads(linhas[i]).get('ticker')}) não bate com a corrente: editada, "
            "apagada ou inserida" for i, (a, b) in enumerate(zip(guardada, esperada)) if a != b][:5]


def _gravar(novas: list[dict], caminho: pathlib.Path) -> int:
    problemas = verificar(caminho)
    if problemas:
        raise ValueError(f"registro adulterado, nada gravado (AUD-102): {problemas}")
    existentes = {(l.get("origem", "hall"), l["data_preco"], l["ticker"]): l for l in ler(caminho)}
    a_gravar, vistas = [], set()
    for l in novas:
        chave = (l["origem"], l["data_preco"], l["ticker"])
        if chave in vistas:
            raise ValueError(f"{l['ticker']} ({l['origem']}) em {l['data_preco']} aparece duas "
                             "vezes na mesma rodada — um veredito por ticker e data")
        vistas.add(chave)
        velho = existentes.get(chave)
        campos = COMPARA + (("golden_sha",) if l["origem"] == "hall" else ())
        if velho is None:
            a_gravar.append(l)
        elif {k: velho.get(k) for k in campos} != {k: l[k] for k in campos}:
            raise ValueError(f"{l['ticker']} ({l['origem']}) em {l['data_preco']} já registrado "
                             "com outro valor — registro é append-only; use outra data de preço")
    if a_gravar:
        caminho.parent.mkdir(exist_ok=True)
        textos = [json.dumps(l, ensure_ascii=False, sort_keys=True) for l in a_gravar]
        antes = _corrente(_linhas_cruas(caminho))
        h, elos = (antes[-1] if antes else ""), []
        for x in textos:
            h = _elo(h, x)
            elos.append(h)
        cc = _caminho_corrente(caminho)
        tam = {p: p.stat().st_size if p.exists() else None for p in (caminho, cc)}
        try:
            with caminho.open("a", encoding="utf-8", newline="\n") as f:
                f.write("".join(x + "\n" for x in textos))
            with cc.open("a", encoding="utf-8", newline="\n") as f:
                f.write("".join(e + "\n" for e in elos))
        except BaseException:
            for p, n in tam.items():            # falha no meio: desfaz, senão o registro fica "adulterado" para sempre
                if n is None:
                    p.unlink(missing_ok=True)
                elif p.exists():
                    with p.open("r+b") as f:
                        f.truncate(n)
            raise
    return len(a_gravar)


def registrar(data_preco: str, doutrina: str, golden_path: pathlib.Path = GOLDEN,
              caminho: pathlib.Path = REGISTRO, hoje: str | None = None) -> int:
    """Acrescenta a rodada. Devolve quantas linhas novas; 0 se a rodada já estava idêntica."""
    bruto = golden_path.read_bytes()
    sha = sha_arquivo(bruto)
    novas = linhas_do_golden(json.loads(bruto.decode("utf-8")), data_preco, doutrina, sha,
                             hoje or dt.date.today().isoformat(), precos_oficiais(data_preco))
    return _gravar(novas, caminho)


def registrar_dossies(pasta: pathlib.Path = VEREDITOS, caminho: pathlib.Path = REGISTRO,
                      hoje: str | None = None) -> int:
    """Acrescenta os vereditos de dossiê (origem "dossie"). Idempotente; muda o valor → erro."""
    return _gravar(linhas_dos_vereditos(pasta, hoje or dt.date.today().isoformat()), caminho)



# ---------------------------------------------------------------- avaliação pré-registrada (B25, 14/10/2026: AUD-32/98/99)
# Funções puras: o retorno total entra como função injetada `retorno(ticker, inicio_iso, fim_iso) -> float | None` (fração),
# a mesma máquina do `backtest/precos/retorno.py` na leitura real. Nada aqui lê preço; a 1ª leitura possível é out/2027.
HORIZONTE_DIAS = 365          # horizonte principal: 1 ano a partir de data_preco (direção em 3 anos = 1095)
N_MIN_IC = 10                 # rodada com menos linhas válidas não entra no IC (só descrita)
RODADAS_MIN = 4               # leitura só com >= 4 rodadas vencidas
T_CRITICO = 2.0               # |t| da média dos IC entre rodadas


def retroativa(linha: dict) -> bool:
    """AUD-99: registrada depois do pregão do preço (o mercado já andou quando a linha entrou)."""
    return str(linha.get("registrado_em", "")) > str(linha["data_preco"])


def linhas_validas(registro: list[dict], sem_retroativas: bool = False) -> list[dict]:
    """Uma linha por (ticker, rodada), rodada = data_preco (AUD-99). Hall e dossiê na mesma rodada: vale o dossiê (análise
    completa, posterior ao lote); a outra segue no registro (append-only), fora da leitura. Cada linha sai com `retroativa`.
    `sem_retroativas`: as retroativas saem ANTES da escolha — um dossiê retroativo devolve a vez à linha do hall, se ela não for."""
    por: dict[tuple[str, str], dict] = {}
    for l in registro:
        l = {**l, "origem": l.get("origem", "hall")}
        if l["origem"] not in ("hall", "dossie"):
            raise ValueError(f"{l['ticker']}: origem desconhecida {l['origem']!r} em {l['data_preco']}")
        if sem_retroativas and retroativa(l):
            continue
        k = (l["data_preco"], l["ticker"])
        velho = por.get(k)
        if velho is None or (velho["origem"] == "hall" and l["origem"] == "dossie"):
            por[k] = l
        elif velho["origem"] == l["origem"]:
            raise ValueError(f"{l['ticker']} ({l['origem']}) duas vezes em {l['data_preco']}: registro inválido")
    return [{**l, "retroativa": retroativa(l)} for _, l in sorted(por.items())]


def _postos(xs: list[float]) -> list[float]:
    """Postos 1..n; empates recebem o posto médio."""
    ordem = sorted(range(len(xs)), key=lambda i: xs[i])
    r = [0.0] * len(xs)
    i = 0
    while i < len(ordem):
        j = i
        while j + 1 < len(ordem) and xs[ordem[j + 1]] == xs[ordem[i]]:
            j += 1
        for k in range(i, j + 1):
            r[ordem[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def ic_postos(xs: list[float], ys: list[float]) -> float | None:
    """IC de postos (Spearman = Pearson dos postos). None se n < 2 ou um dos lados não varia."""
    if len(xs) != len(ys):
        raise ValueError("ic_postos: listas de tamanhos diferentes")
    if len(xs) < 2:
        return None
    rx, ry = _postos(xs), _postos(ys)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    sxy = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else None


def _fim(data_iso: str, dias: int) -> str:
    return (dt.date.fromisoformat(data_iso) + dt.timedelta(days=dias)).isoformat()


def hall_da_rodada(registro: list[dict], data_preco: str) -> list[str]:
    """Comparador (AUD-98): os tickers da rodada de origem "hall" mais recente com data <= data_preco."""
    datas = sorted({l["data_preco"] for l in registro if l.get("origem", "hall") == "hall" and l["data_preco"] <= data_preco})
    if not datas:
        return []
    return sorted({l["ticker"] for l in registro if l.get("origem", "hall") == "hall" and l["data_preco"] == datas[-1]})


def _retorno_ok(r) -> float | None:
    """None, NaN e ±inf são retorno AUSENTE (a máquina do backtest marca falta de fator com NaN): nunca entram em conta."""
    return float(r) if isinstance(r, (int, float)) and math.isfinite(r) else None


def excedentes(registro: list[dict], retorno, hoje: str, horizonte_dias: int = HORIZONTE_DIAS,
               sem_retroativas: bool = False) -> list[dict]:
    """Linhas válidas com horizonte vencido + retorno total, média simples do hall no MESMO período e excedente (AUD-98).
    Retorno ausente (None/NaN/inf: sem cotação, delisting sem valor de saída) do ticker → excedente None, sai do IC e é
    contado; de um ticker do hall → sai da média e é contado em `hall_sem_retorno` (viés de sobrevivência visível)."""
    medias: dict[tuple[str, str], tuple[float | None, int, int]] = {}
    out = []
    for l in linhas_validas(registro, sem_retroativas):
        fim = _fim(l["data_preco"], horizonte_dias)
        if fim > hoje:
            continue
        chave = (l["data_preco"], fim)
        if chave not in medias:
            hall = hall_da_rodada(registro, l["data_preco"])
            rs = [r for tk in hall if (r := _retorno_ok(retorno(tk, l["data_preco"], fim))) is not None]
            medias[chave] = (sum(rs) / len(rs) if rs else None, len(hall), len(hall) - len(rs))
        r = _retorno_ok(retorno(l["ticker"], l["data_preco"], fim))
        m, n_hall, sem = medias[chave]
        out.append({**l, "fim": fim, "retorno": r, "media_hall": m, "n_hall": n_hall, "hall_sem_retorno": sem,
                    "excedente": None if r is None or m is None else r - m})
    return out


def _pc_ok(pc) -> bool:
    return isinstance(pc, (int, float)) and math.isfinite(pc)


def avaliar(registro: list[dict], retorno, hoje: str, sem_retroativas: bool = False,
            horizonte_dias: int = HORIZONTE_DIAS) -> dict:
    """Critério pré-registrado (AUD-32): IC de postos entre P/C e retorno excedente, por rodada; hipótese IC < 0 (P/C menor,
    excedente maior). Leitura com >= RODADAS_MIN rodadas no IC: "apoia" se a média dos IC < 0 e t <= −T_CRITICO; "contraria"
    se a média >= 0 (a régua não ordena); senão "inconclusiva". `sem_retroativas=True` é a sensibilidade obrigatória."""
    ex = excedentes(registro, retorno, hoje, horizonte_dias, sem_retroativas)
    por: dict[str, list[dict]] = {}
    for e in ex:
        por.setdefault(e["data_preco"], []).append(e)
    rodadas, pequenas = [], []
    for data, ls in sorted(por.items()):
        ok = [e for e in ls if _pc_ok(e["pc"]) and e["excedente"] is not None]
        linha = {"data_preco": data, "n": len(ok), "excluidas": len(ls) - len(ok),
                 "hall_sem_retorno": max(e["hall_sem_retorno"] for e in ls)}
        if len(ok) < N_MIN_IC:
            pequenas.append(linha)
            continue
        linha["ic"] = ic_postos([e["pc"] for e in ok], [e["excedente"] for e in ok])
        rodadas.append(linha)
    ics = [r["ic"] for r in rodadas if r["ic"] is not None]
    media = sum(ics) / len(ics) if ics else None
    t = None
    if len(ics) >= 2:
        dp = math.sqrt(sum((x - media) ** 2 for x in ics) / (len(ics) - 1))
        t = media / (dp / math.sqrt(len(ics))) if dp > 0 else (math.copysign(math.inf, media) if media else None)
    if len(ics) < RODADAS_MIN:
        leitura = f"inconclusiva: {len(ics)} rodada(s) no IC, mínimo {RODADAS_MIN}"
    elif media >= 0:
        leitura = "contraria: IC médio >= 0 (a régua não ordena o retorno excedente)"
    elif t is not None and t <= -T_CRITICO:
        leitura = "apoia: IC médio < 0 com t <= -2"
    else:
        leitura = "inconclusiva: IC médio < 0 sem t <= -2"
    return {"rodadas": rodadas, "fora_do_ic": pequenas, "ic_medio": media, "t": t, "leitura": leitura,
            "sem_retroativas": sem_retroativas, "horizonte_dias": horizonte_dias}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Registro prospectivo dos vereditos do golden")
    ap.add_argument("--data-preco", help="pregão de fechamento dos preços (AAAA-MM-DD)")
    ap.add_argument("--doutrina", help="versão da doutrina, ex.: v2.2")
    ap.add_argument("--dossie", action="store_true",
                    help="registra os vereditos de dossie/vereditos/*.json (origem 'dossie')")
    ap.add_argument("--verificar", action="store_true", help="confere a corrente do registro (AUD-102)")
    a = ap.parse_args(argv)
    if a.verificar:
        p = verificar()
        print("registro íntegro" if not p else "\n".join(p))
        return 1 if p else 0
    if a.dossie and (a.data_preco or a.doutrina):
        ap.error("--dossie não combina com --data-preco/--doutrina")
    if a.dossie:
        n = registrar_dossies()
    elif a.data_preco and a.doutrina:
        n = registrar(a.data_preco, a.doutrina)
    else:
        ap.error("informe --dossie, ou --data-preco e --doutrina")
    print(f"{n} linhas novas em {REGISTRO.relative_to(AQUI)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
