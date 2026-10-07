"""Regras da triagem (Etapa 4): exclusões, Q1–Q5, portão, fila, ausência de palavra e registro.

Tudo com dados sintéticos, exceto `test_universo_real` (pula sem o COTAHIST/FCA em disco). Todo teste
que afirma AUSÊNCIA tem meta-teste que injeta o que não pode aparecer e exige que seja pego (lição da
Etapa 3: o sentinela tautológico).
"""
from __future__ import annotations

import dataclasses
import json
import math
from pathlib import Path

import pandas as pd
import pytest

from backtest.calendario import Calendario
from backtest.ledger.pit import Exercicio, LedgerPIT
from backtest.motor.base import Ano, Insumos
from backtest.motor.perfil import Perfil
from backtest.motor.reduzido import Resultado as ResultadoMotor
from backtest.motor.regua import Veredito
from triagem import avaliar as A, fila, qualidade as Q, registro
from triagem.config import PADRAO, ConfigTriagem
from triagem.universo import JA_ANALISADA, LIQUIDEZ, RECUPERACAO, SETOR, SEM_IDENTIDADE, classificar

T = "2026-10-02"
MES = "2026-08"
PISO = 1_000_000.0


# ----------------------------------------------------------------------------- universo
def _fca(setor="Comércio", situacao="Fase Operacional", controle="Privado"):
    return {"setor": setor, "situacao": situacao, "controle": controle, "mes_encerramento": "12"}


def _classificar(liq: dict, cnpj: dict, fca: dict, codbdi: dict | None = None, hall=()):
    return classificar(pd.Series(liq, dtype=float), cnpj, lambda c: {"C1": 1, "C2": 2, "C3": 3, "C4": 4,
                                                                      "C5": 5, "C6": 6, "C7": 7}.get(c),
                       lambda cd: fca.get(cd, _fca()), pd.Series(codbdi or {}, dtype=str), PISO,
                       set(hall))


def test_um_papel_por_companhia_o_mais_liquido():
    t = _classificar({"ABCD3": 2e6, "ABCD4": 9e6, "ABCD11": 1e6}, {k: "C1" for k in ("ABCD3", "ABCD4", "ABCD11")}, {})
    assert list(t["ticker"]) == ["ABCD4"]
    assert t.iloc[0]["outras_classes"] == "ABCD3 ABCD11"
    assert t.iloc[0]["motivo"] == ""


@pytest.mark.parametrize("liq,fca,codbdi,ticker,hall,motivo", [
    (5e5, _fca(), "02", "XPTO3", (), LIQUIDEZ),
    (5e6, _fca(situacao="Em Recuperação Judicial ou Equivalente"), "02", "XPTO3", (), RECUPERACAO),
    (5e6, _fca(situacao="Em Falência"), "02", "XPTO3", (), RECUPERACAO),
    (5e6, _fca(), "08", "XPTO3", (), RECUPERACAO),            # FCA defasada, CODBDI denuncia
    (5e6, _fca(), "58", "XPTO3", (), RECUPERACAO),
    (5e6, _fca(setor="Educação"), "02", "XPTO3", (), SETOR),
    (5e6, _fca(setor="Emp. Adm. Part. - Educação"), "02", "XPTO3", (), SETOR),
    (5e6, _fca(setor="Serviços Transporte e Logística"), "02", "AZUL4", (), SETOR),
    (5e6, _fca(setor="Seguradoras e Corretoras"), "02", "IRBR3", (), SETOR),
    (5e6, _fca(), "02", "XPTO3", ("C1",), JA_ANALISADA),
    (5e6, _fca(), "02", "XPTO3", (), ""),
])
def test_exclusoes_pre_ledger(liq, fca, codbdi, ticker, hall, motivo):
    t = _classificar({ticker: liq}, {ticker: "C1"}, {1: fca}, {ticker: codbdi}, hall)
    assert t.iloc[0]["motivo"] == motivo


def test_sem_cnpj_vai_para_sem_identidade():
    t = _classificar({"ORFA3": 9e6}, {}, {})
    assert t.iloc[0]["motivo"] == SEM_IDENTIDADE


def test_piso_e_o_maior_entre_backtest_e_posicao():
    from triagem.universo import piso_liquidez
    from backtest.config import PADRAO as BT, limite_liquidez
    assert piso_liquidez(T) == max(limite_liquidez(BT, T), PADRAO.volume_minimo_posicao)
    grande = dataclasses.replace(PADRAO, posicao_tipica=10_000_000.0)
    assert piso_liquidez(T, grande) == pytest.approx(10_000_000.0 / (5 * 0.10))


def test_mercado_e_o_mesmo_do_hall():
    import lote1_bancos
    assert (PADRAO.rf_real, PADRAO.pi) == (lote1_bancos.MK.rf_real, lote1_bancos.MK.pi)


def test_corte_de_preco_e_cara_mais_erro_do_proxy():
    assert PADRAO.corte_pc == pytest.approx(1.10 + 0.34)


# ----------------------------------------------------------------------------- qualidade
def _ano(ano, ebit=100.0, pl=1000.0, fco=50.0, div=10.0, lucro=60.0, receita=1000.0, **kw):
    contas = {"ebit": ebit, "pl": pl, "fco": fco, "lucro": lucro, "lucro_controlador": lucro,
              "receita": receita, "lair": 100.0, "ir": -34.0, **kw}
    contas = {k: v for k, v in contas.items() if v is not None}
    return Ano(dt_refer=f"{ano}-12-31", ano=ano, contas=contas, da=20.0, capex=30.0, dividendos=div,
               arrendamento=0.0, real=1.0)


def _anos(n=10, **kw):
    return tuple(_ano(2016 + k, **kw) for k in range(n))


@pytest.mark.parametrize("n,frac,esperado", [(10, 0.7, 7), (7, 0.7, 5), (9, 0.7, 7), (10, 0.8, 8),
                                             (7, 0.8, 6)])
def test_precisa(n, frac, esperado):
    assert Q.precisa(n, frac) == esperado


def test_roic_real_bate_com_a_conta_a_mao():
    anos = _anos()
    r = Q.roic_reais(anos, MES)
    nominal = 100.0 * (1 - 0.34) / 1000.0
    assert r[3] == pytest.approx((1 + nominal) / (1 + Q.inflacao_do_ano(2019, MES)) - 1)


def test_roic_ignora_ano_sem_ebit_e_capital_nao_positivo():
    anos = (_ano(2016), _ano(2017, ebit=None), _ano(2018, pl=-5000.0))
    r = Q.roic_reais(anos, MES)
    assert r[1] is None and r[2] is None and r[0] is not None


@pytest.mark.parametrize("acima,n,status", [(7, 10, Q.OK), (6, 10, Q.FALHA), (5, 7, Q.OK), (4, 7, Q.FALHA)])
def test_q1_fronteira(acima, n, status):
    rs = [0.20] * acima + [0.01] * (n - acima)
    assert Q.q1(rs, 0.10, "WACC").status == status


def test_q1_janela_valida_curta_e_indet():
    assert Q.q1([0.2] * 6 + [None] * 4, 0.10, "WACC").status == Q.INDET


def test_q2_ausente_nao_conta_como_zero():
    anos = tuple(_ano(2016 + k, fco=None if k < 2 else 10.0) for k in range(10))
    t = Q.q2(anos)
    assert t.status == Q.OK and "8/8" in t.texto


def test_q3():
    ult = _ano(2025)
    assert Q.q3({"caixa": 500.0, "emprest_cp": 100.0}, ult).texto == "caixa líquido"
    assert Q.q3({"emprest_lp": 300.0}, ult).status == Q.OK              # 300 / 120 = 2,5
    assert Q.q3({"emprest_lp": 301.0}, ult).status == Q.FALHA
    assert Q.q3({"emprest_lp": 10.0}, _ano(2025, ebit=-50.0)).status == Q.FALHA
    assert Q.q3({}, ult).status == Q.INDET


def _ins(anos, papeis=1_000_000.0, balanco=None):
    p = Perfil(1, "Comércio", "servicos", "2026-01-01", "")
    return Insumos(ticker="XPTO3", cd_cvm=1, data_corte=T, perfil=p, ledger=None, anos=anos,
                   balanco=balanco or {}, papeis=papeis, por_papel=1)


def test_q4_ok_falha_materialidade_e_ipo():
    anos = _anos(lucro=110.0, div=10.0)                  # retido 100 × 9 = 900 (R$ mil)
    i = _ins(anos)
    # VM em R$ mil = preço × 1 mi papéis / 1000 = preço × 1000
    assert Q.q4(i, 3.0, 1.0, 1.0, 1.0).status == Q.OK      # ΔVM 2000 / 900
    assert Q.q4(i, 1.5, 1.0, 1.0, 1.0).status == Q.FALHA   # ΔVM 500 / 900
    assert Q.q4(i, 3.0, 1.0, 2.0, 1.0).valor == pytest.approx((3000 - 500) / 900)   # desdobramento 2:1
    assert Q.q4(i, 3.0, 10.0, 1.0, 1.0).status == Q.NA     # retido 900 < 10% de VM0 10000
    assert Q.q4(i, 3.0, None, 1.0, 1.0).status == Q.INDET
    ipo = Q.q4(i, 3.0, 1.0, 1.0, 1.0, k=6)                 # sobram 3 exercícios
    assert ipo.status == Q.OK and "(3 exerc.)" in ipo.texto
    assert Q.q4(i, 3.0, 1.0, 1.0, 1.0, k=7).status == Q.INDET


def test_q4_sem_lucro_retido_e_na():
    i = _ins(_anos(lucro=10.0, div=10.0))
    assert Q.q4(i, 3.0, 1.0, 1.0, 1.0).status == Q.NA


def test_q5():
    anos = tuple(_ano(2016 + k, div=0.0 if k < 3 else 5.0) for k in range(10))
    assert Q.q5(anos).status == Q.FALHA
    anos = tuple(_ano(2016 + k, div=0.0 if k < 2 else 5.0) for k in range(10))
    assert Q.q5(anos).status == Q.OK


def _q(**st):
    base = {k: Q.Teste(Q.OK, "") for k in ("Q1", "Q2", "Q3", "Q4", "Q5")}
    return base | {k: Q.Teste(v, "") for k, v in st.items()}


def test_portao():
    assert Q.portao(_q())
    assert Q.portao(_q(Q4=Q.FALHA))
    assert Q.portao(_q(Q4=Q.NA, Q2=Q.FALHA))
    assert not Q.portao(_q(Q2=Q.FALHA, Q3=Q.INDET))          # indet conta como reprovação
    assert not Q.portao(_q(Q1=Q.INDET))
    assert not Q.portao(_q(Q1=Q.FALHA))


def test_ncav_e_ey():
    i = _ins(_anos(), balanco={"ac": 5000.0, "pc": 1000.0, "pnc": 1000.0, "caixa": 0.0})
    assert Q.ncav_por_acao(i) == pytest.approx(3.0)          # 3000 mil / 1 mi papéis
    assert Q.ey(i, 2.0) == pytest.approx(100.0 / 2000.0)
    i2 = _ins(_anos(), balanco={"caixa": 5000.0})
    assert Q.ey(i2, 2.0) == math.inf                         # EV <= 0 com EBIT > 0


# ----------------------------------------------------------------------------- avaliar + fila
TOKEN = "PALAVRA_INJETADA"


def _ledger(n=10):
    anuais = tuple(Exercicio(dt_refer=f"{2016 + k}-12-31", dt_receb=f"{2017 + k}-03-20", versao=1,
                             versao_disco=1, estado="limpo", conjunto="con",
                             contas=dict(_ano(2016 + k, lucro=110.0).contas)) for k in range(n))
    return LedgerPIT(cd_cvm=1, data_corte=T, plano="industrial", anuais=anuais, ultimo_itr=None,
                     acoes=1e6, acoes_dt_refer="2025-12-31", acoes_dt_receb="2026-05-01",
                     acoes_fonte="fre", acoes_ambiguo=False, mes_ipca=MES, acoes_aprovacao="2020-01-01")


def _avaliar(monkeypatch, *, ticker="XPTO3", preco=2.0, setor="Comércio", n=10, pc=0.5, lucro=110.0):
    pregoes = ("2016-12-30", "2026-10-01", "2026-10-02")
    cal = Calendario(pregoes)
    precos = pd.DataFrame({"data": list(pregoes), "ticker": ticker, "preult": [1.0, preco, preco]})
    eventos = pd.DataFrame(columns=["ticker", "data_ex", "fator"])
    perfil = Perfil(1, setor, "servicos", "2026-01-01", "")
    anos = tuple(_ano(2016 + k, lucro=lucro) for k in range(n))

    def montar(cd, tk, cnpj, data, ev, cfg, perfil=None, ledger=None):
        return _ins(anos, balanco={"caixa": 100.0})

    def avaliar_motor(i, mk, p, cfg):
        central = p / pc
        v = Veredito(central, 1.2, pc, TOKEN, TOKEN, "normal", False)
        return ResultadoMotor(i, {"a": central, "b": central * 1.1, "c": central * 0.95},
                              # WACC real −10%: todo ROIC real sintético fica acima (Q1 ok)
                              {"wacc_real": -0.10, "ciclicidade_diverge": 0.0}, v)
    monkeypatch.setattr(A.reduzido, "avaliar", avaliar_motor)
    lin = {"ticker": ticker, "cnpj": "C1", "cd_cvm": 1, "motivo": "", "detalhe": "",
           "setor": setor, "outras_classes": "", "controle": "Privado", "mes_encerramento": "12"}
    return A.avaliar(lin, T, A.mercado(T), precos, cal, eventos, ledger_fn=lambda cd, d, p: _ledger(n),
                     perfil_fn=lambda cd, d: perfil, montar_fn=montar)


def _vaza(obj, token: str) -> bool:
    if isinstance(obj, dict):
        return any(_vaza(k, token) or _vaza(v, token) for k, v in obj.items())
    if isinstance(obj, (list, tuple)):
        return any(_vaza(v, token) for v in obj)
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return _vaza(dataclasses.asdict(obj), token)
    return token in str(obj)


def test_meta_detector_de_vazamento_pega_a_palavra():
    v = Veredito(1.0, 1.0, 1.0, TOKEN, TOKEN, "normal", False)
    assert _vaza({"x": [{"y": v}]}, TOKEN)
    assert not _vaza({"x": [{"y": 1.0}]}, TOKEN)


def test_palavra_do_motor_nunca_sai_da_triagem(monkeypatch):
    r = _avaliar(monkeypatch)
    assert r["confiavel"] and r["pc"] == pytest.approx(0.5)
    assert not _vaza(r, TOKEN)
    res = fila.montar(_tab([r]), [r], T, PISO)
    md = fila.markdown(res)
    assert TOKEN not in md
    assert "XPTO3" in md


def test_avaliar_monta_q1_a_q5(monkeypatch):
    r = _avaliar(monkeypatch)
    assert set(r["q"]) == {"Q1", "Q2", "Q3", "Q4", "Q5"}
    assert r["q"]["Q1"].status == Q.OK
    assert r["q"]["Q3"].texto == "caixa líquido"
    assert r["q"]["Q5"].status == Q.OK


def test_janela_curta_e_tecnologia_sem_lucro(monkeypatch):
    assert _avaliar(monkeypatch, n=6)["motivo"] == A.JANELA_CURTA
    tec = _avaliar(monkeypatch, setor="Comunicação e Informática", lucro=-5.0)
    assert tec["motivo"] == A.SEM_LUCRO
    assert _avaliar(monkeypatch, setor="Comunicação e Informática")["motivo"] == ""


def _linha(tk, passa=True, n_ok=5, ey=0.1, pc=0.8, confiavel=True, motivo="", plano="industrial"):
    st = [Q.OK] * n_ok + [Q.FALHA] * (5 - n_ok)
    return {"ticker": tk, "motivo": motivo, "plano": plano, "passa": passa, "ey": ey, "pc": pc,
            "confiavel": confiavel, "sem_central": "", "netnet": False, "preco": 10.0, "setor": "S",
            "q": {k: Q.Teste(s, "") for k, s in zip(("Q1", "Q2", "Q3", "Q4", "Q5"), st)}}


def test_ordenar_camada_depois_contagem_depois_preco():
    ls = [_linha("B3OK", passa=False, n_ok=4, ey=0.5), _linha("A_CARO", ey=0.01, pc=1.4),
          _linha("A_BARATO", ey=0.3, pc=0.5), _linha("A4", n_ok=4, ey=0.9, pc=0.3)]
    assert [x["ticker"] for x in fila.ordenar(ls)] == ["A_BARATO", "A_CARO", "A4", "B3OK"]


def _tab(ls):
    return pd.DataFrame([{"ticker": x["ticker"], "cnpj": x["ticker"], "cd_cvm": 1,
                          "motivo": "", "detalhe": "", "setor": "S", "liquidez": 5e6} for x in ls])


def test_fila_respeita_corte_de_preco_e_minimo_de_testes():
    ls = [_linha("CARA_CONF", pc=1.5), _linha("CARA_NC", pc=1.5, confiavel=False),
          _linha("POUCO", passa=False, n_ok=2), _linha("BOA")]
    r = fila.montar(_tab(ls), ls, T, PISO)
    assert {x["ticker"] for x in r.fila} == {"BOA", "CARA_NC"}
    assert [x["ticker"] for x in r.por_preco] == ["CARA_CONF"]


def test_central_nao_confiavel_nao_e_premiado():
    ls = [_linha("NC", confiavel=False, pc=0.1), _linha("BARATO", pc=0.4), _linha("MEDIO", pc=0.8),
          _linha("CARO", pc=1.2)]
    ordem = [x["ticker"] for x in fila.ordenar(ls)]
    assert ordem.index("BARATO") < ordem.index("NC") < ordem.index("CARO")


def test_excluida_nunca_entra_na_fila():
    boa = _linha("BOA")
    rj = _linha("RJ", ey=9.9, pc=0.1, motivo=A.JANELA_CURTA)
    r = fila.montar(_tab([boa, rj]), [boa, rj], T, PISO)
    assert "RJ" not in [x["ticker"] for x in r.fila]
    # meta: sem o filtro de motivo, a mesma linha seria a 1ª da fila — o teste acima não é vazio
    assert fila.ordenar([boa, rj])[0]["ticker"] == "RJ"


def test_financeira_fica_fora_da_fila_principal():
    ls = [_linha("BANCO", plano="financeiro"), _linha("BOA")]
    r = fila.montar(_tab(ls), ls, T, PISO)
    assert [x["ticker"] for x in r.fila] == ["BOA"]
    assert [x["ticker"] for x in r.financeiras] == ["BANCO"]


def test_markdown_deterministico():
    ls = [_linha("BOA"), _linha("OUTRA", passa=False, n_ok=3)]
    r = fila.montar(_tab(ls), ls, T, PISO)
    assert fila.markdown(r) == fila.markdown(r)


# ----------------------------------------------------------------------------- registro
def test_registro_append_only(tmp_path: Path):
    ls = [_linha("BOA"), _linha("OUTRA", passa=False, n_ok=3)]
    r = fila.montar(_tab(ls), ls, T, PISO)
    arq = tmp_path / "triagem.jsonl"
    assert registro.registrar(r, arq, hoje="2026-10-06") == 2
    assert registro.registrar(r, arq, hoje="2026-10-07") == 0          # mesma rodada: nada novo
    r.fila[0]["preco"] = 99.0
    with pytest.raises(ValueError, match="append-only"):
        registro.registrar(r, arq)
    linhas = [json.loads(x) for x in arq.read_text(encoding="utf-8").splitlines()]
    assert [l["posicao"] for l in linhas] == [1, 2] and all("palavra" not in l for l in linhas)


# ----------------------------------------------------------------------------- dado real
CVM = Path(__file__).resolve().parent.parent / "dados" / "cvm" / "fca_2026.zip"
COTA = Path(__file__).resolve().parent.parent / "backtest" / "dados" / "cotahist" / "precos_2026.parquet"


@pytest.mark.skipif(not (CVM.exists() and COTA.exists()), reason="FCA/COTAHIST fora do disco")
def test_universo_real():
    from triagem.universo import universo
    tab, piso = universo(T)
    m = dict(zip(tab["ticker"], tab["motivo"]))
    assert 900_000 < piso < 1_100_000
    assert sum(v == JA_ANALISADA for v in m.values()) == 41
    assert m.get("AMER3") == RECUPERACAO                 # FCA: em recuperação judicial
    assert m.get("COGN3") == SETOR                       # educação
    assert m.get("CSNA3") == ""                          # identidade manual (FCA com lixo "4030")
    assert len(tab) == tab["cnpj"].replace("", pd.NA).dropna().nunique() + (tab["cnpj"] == "").sum()


# ----------------------------------------------------------------------------- achados do adversário (06/10/2026)
def test_quebra_estrutural_por_acoes_e_por_ativo():
    l = _ledger()
    assert A.quebra_estrutural(l, 4.14).startswith("base de ações +414%")   # SAUD3
    assert A.quebra_estrutural(l, 0.17) == ""
    itr = Exercicio(dt_refer="2026-06-30", dt_receb="2026-08-10", versao=1, versao_disco=1,
                    estado="limpo", conjunto="con", contas={"ativo": 41_700.0})
    anuais = l.anuais[:-1] + (dataclasses.replace(l.anuais[-1], contas={**l.anuais[-1].contas,
                                                                        "ativo": 1_900.0}),)
    l2 = dataclasses.replace(l, anuais=anuais, ultimo_itr=itr)
    assert "ativo do ITR" in A.quebra_estrutural(l2, math.nan)


def test_quebra_tira_do_portao_e_da_fila():
    q = _linha("FUNDIDA")
    q["quebra"] = "base de ações +414% na janela"
    boa = _linha("BOA")
    r = fila.montar(_tab([q, boa]), [q, boa], T, PISO)
    assert [x["ticker"] for x in r.fila] == ["BOA"]
    assert [x["ticker"] for x in r.a_mao] == ["FUNDIDA"]


def test_q4_prejuizo_acumulado_reprova():
    i = _ins(_anos(lucro=-50.0, div=0.0))
    assert Q.q4(i, 3.0, 1.0, 1.0, 1.0).status == Q.FALHA


def test_q4_usa_papeis_de_d0_quando_conhecidos():
    i = _ins(_anos(lucro=110.0, div=10.0))                 # retido 900; papéis hoje 1 mi
    # emissão: em D0 eram 500 mil papéis -> VM0 = 1 × 500 mil = 500 (R$ mil)
    t = Q.q4(i, 3.0, 1.0, 1.0, 1.0, papeis_d0=500_000.0)
    assert t.valor == pytest.approx((3000 - 500) / 900)


def test_ey_usa_ebit_ajustado():
    # outras receitas de 300 no último ano contra mediana ~0: EBIT 400 vira 100
    anos = _anos()[:-1] + (_ano(2025, ebit=400.0, outras_receitas_op=300.0),)
    i = _ins(anos, balanco={"caixa": 0.0})
    assert Q.ey(i, 1.0) == pytest.approx(100.0 / 1000.0)


def test_nota_antiga_segue_a_troca_de_codigo():
    x = _linha("SAUD3")
    x.update(cadeia=["ODPV3", "SAUD3"], plano="industrial")
    pendencias_txt = fila.pendencias(x)
    assert any("[como ODPV3]" in s for s in pendencias_txt), pendencias_txt
    assert not any("caro" in s.lower() for s in pendencias_txt)


def test_registro_distingue_ev_negativo_de_ausente():
    assert registro._f(math.inf) == "inf" and registro._f(math.nan) is None
