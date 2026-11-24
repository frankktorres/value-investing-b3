"""Testes de regressão da Parte A da auditoria (30/10/2026).

Cada teste aqui FALHA sem a respectiva correção da Parte A e PASSA com ela.
"""
import json
import os
import pathlib
import subprocess
import sys
import zipfile

import pytest

RAIZ_FERR = pathlib.Path(__file__).resolve().parents[1]
RAIZ_REPO = RAIZ_FERR.parent


def _linha_cotahist(
    tp_reg="01",
    data="20260102",
    codbdi="02",
    codneg="PETR4",
    tpmerc="010",
    nomres="PETROBRAS",
    especi="PN      N2",
    preult=3624,
    fatcot=1,
) -> bytes:
    """Monta uma linha posicional de 245 bytes do COTAHIST da B3."""
    buf = bytearray(b" " * 245)
    buf[0:2] = tp_reg.encode("latin-1")
    buf[2:10] = data.encode("latin-1")
    buf[10:12] = codbdi.encode("latin-1")
    buf[12:24] = codneg.ljust(12).encode("latin-1")
    buf[24:27] = tpmerc.encode("latin-1")
    buf[27:39] = nomres.ljust(12)[:12].encode("latin-1")
    buf[39:49] = especi.ljust(10)[:10].encode("latin-1")
    buf[56:69] = f"{preult:013d}".encode("latin-1")
    buf[69:82] = f"{preult:013d}".encode("latin-1")
    buf[82:95] = f"{preult:013d}".encode("latin-1")
    buf[95:108] = f"{preult:013d}".encode("latin-1")
    buf[108:121] = f"{preult:013d}".encode("latin-1")
    buf[121:134] = f"{preult:013d}".encode("latin-1")
    buf[134:147] = f"{preult:013d}".encode("latin-1")
    buf[147:152] = f"{10:05d}".encode("latin-1")
    buf[152:170] = f"{1000:018d}".encode("latin-1")
    buf[170:188] = f"{3624000:018d}".encode("latin-1")
    buf[188:201] = f"{0:013d}".encode("latin-1")
    buf[201:202] = b"0"
    buf[202:210] = b"99991231"
    buf[210:217] = f"{fatcot:07d}".encode("latin-1")
    buf[217:230] = f"{0:013d}".encode("latin-1")
    buf[230:242] = b"BRPETRACNPR6"
    buf[242:245] = b"100"
    assert len(buf) == 245
    return bytes(buf)


def test_cotahist_aceita_linha_utf8_246_bytes_e_ignora_fora_do_universo(tmp_path, monkeypatch):
    """F6-01: linha UTF-8 de 246 bytes (1 char acentuado em NOMRES) é reconvertida a latin-1 (245B),
    e linha fora do universo (ex.: opção tpmerc=070 com 248B) é ignorada sem quebrar o parser."""
    import backtest.cotahist as CH

    header = b"00COTAHIST.2026BOVESPA 20260102" + b" " * (245 - 31)
    # Registro 1: ação à vista com 'Ç' em UTF-8 (2 bytes -> linha fica com 246 bytes)
    reg_vista = bytearray(_linha_cotahist(codbdi="02", codneg="ACAO3", tpmerc="010", nomres="ACAO"))
    reg_utf8_246 = bytes(reg_vista[:28]) + "Ç".encode("utf-8") + bytes(reg_vista[29:])
    assert len(reg_utf8_246) == 246

    # Registro 2: opção (codbdi=78, tpmerc=070) corrompida com 248 bytes — fora do universo à vista
    reg_opcao_248 = _linha_cotahist(codbdi="78", codneg="PETRA123", tpmerc="070") + b"XYZ"
    assert len(reg_opcao_248) == 248

    trailer = bytearray(b" " * 245)
    trailer[0:2] = b"99"
    trailer[31:42] = f"{4:011d}".encode("latin-1")  # 4 linhas no arquivo

    zp = tmp_path / "COTAHIST_A2026.ZIP"
    with zipfile.ZipFile(zp, "w") as zf:
        zf.writestr("COTAHIST_A2026.TXT", b"\r\n".join([header, reg_utf8_246, reg_opcao_248, bytes(trailer)]) + b"\r\n")

    monkeypatch.setattr(CH, "zip_de", lambda ano: zp)
    df = CH.ler_ano(2026)
    assert len(df) == 1
    assert df.iloc[0]["ticker"] == "ACAO3"
    assert df.iloc[0]["preult"] == pytest.approx(36.24)

    # Mas linha truncada (244 bytes) DENTRO do universo (codbdi=02, tpmerc=010) continua levantando ValueError
    reg_truncado_244 = _linha_cotahist(codbdi="02", codneg="VALE3", tpmerc="010")[:-1]
    zp_ruim = tmp_path / "COTAHIST_RUIM.ZIP"
    with zipfile.ZipFile(zp_ruim, "w") as zf:
        zf.writestr("COTAHIST_A2026.TXT", b"\r\n".join([header, reg_truncado_244, bytes(trailer)]) + b"\r\n")
    monkeypatch.setattr(CH, "zip_de", lambda ano: zp_ruim)
    with pytest.raises(ValueError, match="244 bytes"):
        CH.ler_ano(2026)


def test_conftest_skip_de_plataforma_estrutural():
    """F6-03 + Correção 2: _skip_de_plataforma usa critério estrutural (marcador `plataforma` ou
    expressão `skipif` com os.name/sys.platform/platform.system), e NÃO substring no texto do motivo."""
    import conftest

    @pytest.mark.skipif(os.name == "nt", reason="qualquer texto sem palavra-chave")
    def fn_skip_so():
        pass

    @pytest.mark.skipif(not False, reason="dado POSIX ausente no disco")
    def fn_skip_dado_com_palavra_posix():
        pass

    class _ItemFake:
        def __init__(self, obj, tem_marker=False):
            self.obj = obj
            self._tem_marker = tem_marker

        def get_closest_marker(self, nome):
            return object() if (nome == "plataforma" and self._tem_marker) else None

    assert conftest._skip_de_plataforma(_ItemFake(fn_skip_so)) is True
    assert conftest._skip_de_plataforma(_ItemFake(fn_skip_dado_com_palavra_posix)) is False
    assert conftest._skip_de_plataforma(_ItemFake(fn_skip_dado_com_palavra_posix, tem_marker=True)) is True


def test_auto_commit_so_snapshot_em_wip_nunca_no_master_e_dry_nao_trava(tmp_path):
    """Decisão de 24/11/2026 (F49 do UNION) + F6-02/F6-06: o hook Stop só guarda snapshot em `wip/auto` — `master`
    (local e remoto), HEAD, índice e árvore de trabalho ficam intocados, mesmo para doc, deleção e arquivo protegido —
    e `--dry` não trava no stdin."""
    hook_path = RAIZ_REPO / ".claude" / "hooks" / "auto_commit.py"
    # 1. Subprocesso com stdin em PIPE (não-TTY): com --dry não pode ler stdin
    proc = subprocess.run(
        [sys.executable, str(hook_path), "--dry"],
        cwd=str(RAIZ_REPO),
        input="",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert proc.returncode == 0

    # 2. Hook de verdade num repositório descartável com remoto: só `wip/auto` muda
    fora = ("CLAUDE_CODE_REMOTE", "GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE")
    env = {k: v for k, v in os.environ.items() if k not in fora}
    repo, origem = tmp_path / "repo", tmp_path / "origem.git"
    env.update(CLAUDE_PROJECT_DIR=str(repo), GIT_AUTHOR_NAME="teste", GIT_AUTHOR_EMAIL="teste@example.invalid",
               GIT_COMMITTER_NAME="teste", GIT_COMMITTER_EMAIL="teste@example.invalid")

    def g(*args, cwd=repo):
        r = subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=", *args], cwd=str(cwd), env=env,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
        assert r.returncode == 0, f"git {args}: {r.stderr}"
        return r.stdout.strip()

    g("init", "-q", "--bare", str(origem), cwd=tmp_path)
    g("init", "-q", "-b", "master", str(repo), cwd=tmp_path)
    (repo / "docs").mkdir()
    (repo / "docs" / "BACKLOG.md").write_text("antes\n", encoding="utf-8")
    (repo / "01-doutrina-value-investing.md").write_text("doutrina antes\n", encoding="utf-8")
    (repo / "some.md").write_text("vai ser apagado\n", encoding="utf-8")
    g("add", "--", "docs/BACKLOG.md", "01-doutrina-value-investing.md", "some.md")
    g("commit", "-q", "-m", "base")
    g("remote", "add", "origin", str(origem))
    g("push", "-q", "-u", "origin", "master")
    base = g("rev-parse", "HEAD")

    (repo / "docs" / "BACKLOG.md").write_text("depois\n", encoding="utf-8")          # só doc: antes ia ao master
    (repo / "01-doutrina-value-investing.md").write_text("doutrina depois\n", encoding="utf-8")  # protegido
    (repo / "some.md").unlink()                                                        # deleção
    (repo / "novo.md").write_text("novo\n", encoding="utf-8")                          # não rastreado
    status_antes = g("status", "--porcelain")

    def rodar_hook():
        r = subprocess.run([sys.executable, str(hook_path)], cwd=str(repo), env=env, input="{}", capture_output=True,
                           text=True, timeout=120)
        assert r.returncode == 0
        return json.loads(r.stdout)["systemMessage"]

    aviso = rodar_hook()
    assert "wip/auto" in aviso and "push ok" in aviso, aviso

    assert g("rev-parse", "--abbrev-ref", "HEAD") == "master"
    assert g("rev-parse", "HEAD") == base                                   # master local intocado
    assert g("ls-remote", "origin", "refs/heads/master").split()[0] == base  # master remoto intocado
    assert g("status", "--porcelain") == status_antes                       # índice e árvore intocados
    wip = g("rev-parse", "wip/auto")
    assert wip != base
    assert g("ls-remote", "origin", "refs/heads/wip/auto").split()[0] == wip  # só wip/auto foi empurrado
    assert g("show", "wip/auto:docs/BACKLOG.md") == "depois"
    assert g("show", "wip/auto:01-doutrina-value-investing.md") == "doutrina depois"
    assert sorted(g("ls-tree", "-r", "--name-only", "wip/auto").split()) == [
        "01-doutrina-value-investing.md", "docs/BACKLOG.md", "novo.md"]

    # 3. Sem mudança nova, não empilha snapshot repetido; e o master continua onde estava
    assert "nada novo" in rodar_hook()
    assert g("rev-parse", "wip/auto") == wip
    assert g("rev-parse", "master") == base


def test_conferir_noite_exclui_carteira_privada_e_hypothesis():
    """F6-05: carteira.local.json, dados/privado e .hypothesis estão em FORA e nunca vão para worktrees."""
    import conferir_noite as C

    exemplos_bloqueados = [
        "ferramentas/carteira.local.json",
        "ferramentas/dados/privado/carteira.json",
        "ferramentas/.hypothesis/examples/abc",
    ]
    for cam in exemplos_bloqueados:
        assert any(f in cam for f in C.FORA), f"{cam} deveria ser filtrado por conferir_noite.FORA"


def test_motor_nao_financeiras_carrega_arrendamento_pago_sem_importar_lote4():
    """F1-01: avaliar() em motor_nao_financeiras não depende da ordem de import de lote4_saude_telecom."""
    codigo = (
        "import sys; "
        "import motor_nao_financeiras as M; "
        "assert 'lote4_saude_telecom' not in sys.modules; "
        "assert (M.CVM['VIVT3']['anual']['2025'].get('arrendamento_pago') or 0) > 0; "
        "t = M.CVM['TIMS3']['anual']; "
        "assert t['2021'].get('arrendamento_pago') == (t['2020']['arrendamento_pago'] + t['2022']['arrendamento_pago']) / 2"
    )
    proc = subprocess.run(
        [sys.executable, "-c", codigo],
        cwd=str(RAIZ_FERR),
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert proc.returncode == 0, f"Falhou: {proc.stderr}"


def test_gerar_pdf_lote4_central_rapido_aplica_desconto_controlador():
    """F1-04: central_rapido em gerar_pdf_lote4 aplica desconto_pct(emp) exatamente como avaliar()."""
    import gerar_pdf_lote4 as G4
    import lote4_saude_telecom as L4
    from motor_nao_financeiras import avaliar

    for emp in L4.EMPRESAS:
        if emp.ticker in ("VIVT3", "WEGE3"):
            c_pdf = G4.central_rapido(emp)
            c_motor = avaliar(emp, L4.MK)["central"]
            assert c_pdf == pytest.approx(c_motor, rel=1e-9), f"Divergência em {emp.ticker}: {c_pdf} vs {c_motor}"


def test_historico_arquivos_guardar_cria_pasta_pai(tmp_path):
    """F1-04: guardar() cria a pasta pai quando o arquivo de destino está numa subpasta ainda inexistente."""
    from historico_arquivos import guardar

    alvo = tmp_path / "nova_subpasta" / "relatorio.pdf"
    hist = tmp_path / "_historico"
    assert not alvo.parent.exists()
    guardar(alvo, "teste", b"%PDF-1.4 conteudo", hist)
    assert alvo.parent.is_dir()


def test_coletar_statusinvest_recusa_http_erro_e_html_invalido(tmp_path, monkeypatch):
    """F6-07: coletar() valida status HTTP 200 e JSON válido antes de gravar cache em disco."""
    import coletar_statusinvest as CS
    import requests

    monkeypatch.setattr(CS, "BASE", tmp_path)

    class _RespFake:
        def __init__(self, status_code, text):
            self.status_code = status_code
            self.text = text

    # Caso 1: HTTP 403 no POST de indicatorhistoricallist
    monkeypatch.setattr(requests, "post", lambda *a, **kw: _RespFake(403, '{"erro": "forbidden"}'))
    with pytest.raises(RuntimeError, match="403"):
        CS.coletar("TEST3")
    assert not (tmp_path / "TEST3_indicadores.json").exists()

    # Caso 2: HTTP 200 mas corpo HTML (bloqueio Cloudflare) em vez de JSON
    import json
    monkeypatch.setattr(requests, "post", lambda *a, **kw: _RespFake(200, "<html> Cloudflare </html>"))
    with pytest.raises(json.JSONDecodeError):
        CS.coletar("TEST3")
    assert not (tmp_path / "TEST3_indicadores.json").exists()
