"""Tela (painel): o exportador é vista — palavra vigente, régua do relatório com a nota da fonte, nada pessoal, nada
recalculado, nada gravado fora da pasta ignorada. Fixtures sintéticas (TEST*); o teste real pula sem os dados locais."""
import hashlib
import json
import math
import pathlib
import shutil
import uuid

import pytest

from painel import exportar
from painel.exportar import linha_erro, linha_hall, relatorio_json
from relatorio.modelo import Numero, Origem, Relatorio, Secao

RAIZ = pathlib.Path(__file__).resolve().parents[3]
FERR = RAIZ / "ferramentas"
A, B, C = Origem("CVM", "A"), Origem("RI", "B"), Origem("StatusInvest", "C")
MARCA = dict(dossie=False, fora_do_hall=False, na_carteira=False)


def rel(palavra="CARA", central=10.0, origem_central=(A,), saida_rot="Saída (1,30 × central)", preco=12.0):
    ver = Secao("Veredito", numeros=[
        Numero("Preço", preco, "R$", (Origem("COTAHIST", "A"),)),
        Numero("Valor central", central, "R$", origem_central),
        Numero("Preço ÷ central (P/C)", preco / central if central else None, "x", origem_central),
        Numero("Compra (0,70 × central)", 0.7 * central if central else None, "R$", origem_central),
        Numero(saida_rot, (1.5 if "1,50" in saida_rot else 1.3) * central if central else None, "R$", origem_central)])
    met = Secao("Preço justo por método", numeros=[
        Numero("DCF", 9.0, "R$", (A,), papel="central"), Numero("EPV", 11.0, "R$", (C,), papel="central"),
        Numero("Graham", 8.0, "R$", (C,), papel="informativo"), Numero("Bazin", None, "R$", (), papel="informativo")])
    return Relatorio("TESTA3", "Teste SA", "2026-10-02", "hall, lote 1", palavra, secoes=[ver, met])


def test_palavra_e_a_vigente_e_o_preco_de_hoje_nao_troca_a_palavra():
    x = linha_hall(rel("CARA"), "CARA", 3.0, **MARCA)               # preço de hoje bem abaixo da compra (7,00)
    assert x["palavra"] == "CARA" and x["palavra_motor"] is None
    assert x["situacao"] == "≤ COMPRA" and x["pc_hoje"] == pytest.approx(0.3)   # só o marcador e o P/C mudam


def test_motor_divergente_suspende_a_regua_e_mantem_a_palavra_vigente():
    """Adversário 19/10 (LEVE3): a régua do motor de hoje (que diz NÃO CONCLUSIVO) não aparece sob a palavra JUSTA."""
    x = linha_hall(rel("NÃO CONCLUSIVO"), "JUSTA", 11.0, central_vigente=9.5, **MARCA)
    assert x["palavra"] == "JUSTA" and x["palavra_motor"] == "NÃO CONCLUSIVO"
    assert (x["central"], x["compra"], x["saida"], x["pc_hoje"]) == (None, None, None, None)
    assert x["situacao"] == exportar.SUSPENSA
    assert any("veredito novo" in a and "9,50" in a and "10,00" in a for a in x["avisos"])
    sem = linha_hall(rel("CARA"), None, 11.0, **MARCA)
    assert sem["palavra"] == "CARA" and any("Sem veredito vigente" in a for a in sem["avisos"])
    vazio = linha_hall(rel("CARA"), "", 11.0, **MARCA)                     # "" = sem vigente, não "diverge de ''"
    assert vazio["palavra"] == "CARA" and vazio["compra"] == pytest.approx(7.0) and vazio["palavra_motor"] is None


@pytest.mark.parametrize("palavra", [None, "", "XYZ"])
def test_sem_palavra_valida_nao_tem_regua(palavra):
    """AUD-43: sem palavra final não há preço de compra nem de saída."""
    x = linha_hall(rel(palavra), None, 5.0, **MARCA)
    assert x["compra"] is None and x["saida"] is None and x["pc_hoje"] is None
    assert x["situacao"] not in ("≤ COMPRA", "≥ SAÍDA", "perto da compra")


def test_falha_ao_gravar_empresa_da_uma_linha_de_erro_sem_tmp_nem_caminho(monkeypatch):
    destino = exportar.DADOS / f"_teste_{uuid.uuid4().hex[:8]}"
    monkeypatch.setattr(exportar, "tickers", lambda: (["TESTA3", "TESTB4"], set()))
    monkeypatch.setattr(exportar, "palavra_vigente", lambda tk, d, dos: ("CARA", 10.0))
    def montar(tk):
        r = rel()
        r.tk = tk
        return r
    monkeypatch.setattr("relatorio.montar.montar", montar)
    monkeypatch.setattr("monitor_semanal.ultimos_precos", lambda tks, hoje: ({"TESTA3": 11.0}, "2026-10-15"))
    real = exportar._gravar_json

    def quebra(caminho, obj, tentativas=5):
        if caminho.name == "TESTA3.json":
            raise PermissionError(f"[WinError 5] Acesso negado: '{caminho}.tmp' -> '{caminho}'")
        return real(caminho, obj, tentativas)
    monkeypatch.setattr(exportar, "_gravar_json", quebra)
    try:
        hall = exportar.exportar(destino, hoje="2026-10-16", log=lambda *_: None)
        assert [x["tk"] for x in hall["empresas"]] == ["TESTA3", "TESTB4"]                 # uma linha por ticker
        a = hall["empresas"][0]
        assert a["erro"].startswith("PermissionError") and str(exportar.RAIZ_REPO) not in a["erro"]
        assert not list(destino.rglob("*.tmp"))
    finally:
        shutil.rmtree(destino, ignore_errors=True)


def test_gravar_json_tenta_de_novo_e_limpa_tmp(monkeypatch):
    destino = exportar.DADOS / f"_teste_{uuid.uuid4().hex[:8]}"
    chamadas = []

    def replace(a, b):
        chamadas.append(a)
        raise PermissionError("ocupado")
    monkeypatch.setattr(exportar.os, "replace", replace)
    monkeypatch.setattr(exportar.time, "sleep", lambda s: None)
    try:
        with pytest.raises(PermissionError):
            exportar._gravar_json(destino / "x.json", {"a": 1}, tentativas=3)
        assert len(chamadas) == 3 and not list(destino.glob("*.tmp"))
    finally:
        shutil.rmtree(destino, ignore_errors=True)


def test_regua_nota_e_metodos():
    x = linha_hall(rel(origem_central=(A, C)), "CARA", 11.0, **MARCA)
    assert (x["central"], x["compra"], x["saida"]) == pytest.approx((10.0, 7.0, 13.0))
    assert x["nota_central"] == "C" and "StatusInvest" in x["fonte_central"]   # pior das origens, nunca promovida
    assert x["saida_exc"] is False and (x["n_central"], x["n_informativo"]) == (2, 1)   # Bazin sem valor não conta
    exc = linha_hall(rel(saida_rot="Saída (1,50 × central)"), "CARA", 11.0, **MARCA)
    assert exc["saida_exc"] is True and exc["saida"] == pytest.approx(15.0)


def test_nao_conclusivo_sem_regua_nem_pc():
    x = linha_hall(rel("NÃO CONCLUSIVO"), "NÃO CONCLUSIVO", 11.0, **MARCA)
    assert x["compra"] is None and x["saida"] is None and x["pc_hoje"] is None
    assert x["situacao"] == "sem palavra" and x["central"] == 10.0              # central fica, só informativo


@pytest.mark.parametrize("central", [0.0, -5.0, math.nan, math.inf, None, "12"])
def test_central_invalido_nao_vira_regua(central):
    r = rel()
    next(n for n in r.secoes[0].numeros if n.rotulo == "Valor central").valor = central
    x = linha_hall(r, "CARA", 11.0, **MARCA)
    assert x["central"] is None and x["compra"] is None and x["saida"] is None and x["pc_hoje"] is None


@pytest.mark.parametrize("preco", [None, 0.0, -1.0, math.nan])
def test_sem_preco_de_hoje(preco):
    x = linha_hall(rel(), "CARA", preco, **MARCA)
    assert x["preco_hoje"] is None and x["pc_hoje"] is None and x["situacao"] == exportar.SEM_PRECO


def test_erro_aparece_como_linha():
    x = linha_erro("TESTB4", KeyError("sem ficha"), dossie=True, fora_do_hall=False, na_carteira=True)
    assert x["tk"] == "TESTB4" and "KeyError" in x["erro"] and x["palavra"] is None and x["na_carteira"] is True
    assert set(x) == set(linha_hall(rel(), "CARA", 11.0, **MARCA))                # mesmo contrato da linha boa


def test_relatorio_json_leva_nota_e_fonte_e_nao_tem_nan():
    r = rel()
    r.secoes[0].numeros.append(Numero("Ke implícito", math.inf, "%", (B,)))
    r.secoes[0].tabelas.append(("Sens", ["Ke", "+0"], [["9%", "7,64"]]))
    j = relatorio_json(r)
    s = json.dumps(j, allow_nan=False)                                          # inf → null, senão levanta
    ver = j["secoes"][0]
    assert ver["numeros"][1]["nota"] == "A" and ver["numeros"][1]["fonte"] == "CVM"
    assert ver["numeros"][-1]["valor"] is None and ver["tabelas"][0]["linhas"] == [["9%", "7,64"]]
    assert j["palavra_motor"] == "CARA" and j["versao"] == exportar.VERSAO and "NaN" not in s


CHAVES_PESSOAIS = ("quantidade", "preco_medio", "meta", "valor", "peso", "renda", "patrimonio")


def test_linha_sem_chave_pessoal():
    for k in linha_hall(rel(), "CARA", 11.0, **MARCA):
        assert not any(p in k for p in CHAVES_PESSOAIS), k


def test_destino_padrao_e_ignorado_e_destino_versionavel_e_recusado(tmp_path):
    import subprocess
    for p in (exportar.DADOS / "hall.json", exportar.DADOS / "empresas" / "X.json"):
        assert subprocess.run(["git", "check-ignore", "-q", "--", str(p)], cwd=RAIZ).returncode == 0
    with pytest.raises(PermissionError):
        exportar.exportar(tmp_path)                                             # fora do repo → recusa antes de rodar
    assert not any(tmp_path.iterdir())


def test_painel_nao_importa_carteira_local():
    """A tela pública não lê o arquivo de quantidades (dado pessoal entra só na fatia da carteira, em pasta ignorada)."""
    for arq in (FERR / "painel").rglob("*.py"):
        if "tests" not in arq.parts:
            txt = arq.read_text(encoding="utf-8")
            assert "carteira.local" not in txt and "ler_local" not in txt and "carregar(" not in txt, arq


# ------------------------------------------------------------------------------ real (dados locais)
TEM_DADOS = (FERR / "dados" / "cvm_series.json").exists()
INTOCADOS = [FERR / "tests" / "golden.json", FERR / "prospectivo" / "registro.jsonl",
             *sorted((FERR / "dossie" / "vereditos").glob("*.json"))]


def _hash(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


@pytest.mark.skipif(not TEM_DADOS, reason="dados/cvm_series.json fora do disco (dados brutos fora do git)")
def test_exportacao_real_e_vista():
    antes = {p: _hash(p) for p in INTOCADOS}
    destino = exportar.DADOS / f"_teste_{uuid.uuid4().hex[:8]}"                 # dentro da pasta ignorada
    try:
        exportar.exportar(destino, hoje="2026-10-16", log=lambda *_: None)
        js = json.loads((destino / "hall.json").read_text(encoding="utf-8"))
        assert js["versao"] == exportar.VERSAO and js["pregao_hoje"] <= "2026-10-16"
        e = {x["tk"]: x for x in js["empresas"]}
        assert len(e) >= 41 and not [t for t, x in e.items() if x["erro"]]
        golden = json.loads((FERR / "tests" / "golden.json").read_text(encoding="utf-8"))["tickers"]
        from dossie.gerar import FICHAS
        for tk, g in golden.items():
            if tk not in FICHAS:
                assert e[tk]["palavra"] == g["palavra"], tk                         # hall: palavra do golden
        for tk in FICHAS:
            assert (destino / "empresas" / f"{tk}.json").exists()
        assert e["LEVE3"]["dossie"] and e["LEVE3"]["palavra"] == "JUSTA"            # dossiê vence (DECISOES 19/10)
        assert set(json.loads((FERR / "carteira_tickers.json").read_text(encoding="utf-8"))["tickers"]) \
            == {t for t, x in e.items() if x["na_carteira"]}
    finally:
        shutil.rmtree(destino, ignore_errors=True)
    assert {p: _hash(p) for p in INTOCADOS} == antes
