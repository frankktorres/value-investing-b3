"""Servidor da tela: só 127.0.0.1, só leitura, tipos certos (módulo ES precisa de text/javascript), sem listar pasta,
sem sair da pasta web/."""
import http.client
import threading

import pytest

from painel import servir


@pytest.fixture()
def srv(tmp_path):
    (tmp_path / "index.html").write_text("<!doctype html><title>t</title>", encoding="utf-8")
    (tmp_path / "app.js").write_text("export const x = 1;", encoding="utf-8")
    (tmp_path / "dados").mkdir()
    (tmp_path / "dados" / "hall.json").write_text('{"versao": 1}', encoding="utf-8")
    (tmp_path.parent / f"{tmp_path.name}-segredo.txt").write_text("fora", encoding="utf-8")
    s = servir.servidor(0, tmp_path)                       # porta livre
    t = threading.Thread(target=s.serve_forever, daemon=True)
    t.start()
    yield s
    s.shutdown()
    s.server_close()


def _get(s, caminho, metodo="GET"):
    c = http.client.HTTPConnection(*s.server_address, timeout=5)
    c.request(metodo, caminho)
    r = c.getresponse()
    corpo = r.read()
    c.close()
    return r, corpo


def test_so_escuta_em_localhost(srv):
    assert srv.server_address[0] == "127.0.0.1"


def test_tipos_e_cabecalhos(srv):
    for caminho, tipo in [("/", "text/html"), ("/app.js", "text/javascript"), ("/dados/hall.json", "application/json")]:
        r, _ = _get(srv, caminho)
        assert r.status == 200 and r.getheader("Content-Type").startswith(tipo), caminho
        assert r.getheader("Cache-Control") == "no-store" and r.getheader("X-Content-Type-Options") == "nosniff"
        assert "default-src 'self'" in r.getheader("Content-Security-Policy")


def test_nao_lista_pasta_nem_sai_da_web(srv):
    assert _get(srv, "/dados/")[0].status == 404
    nome = f"/../{servir.Path(srv.RequestHandlerClass.keywords['directory']).name}-segredo.txt"
    r, corpo = _get(srv, nome)
    assert r.status == 404 and b"fora" not in corpo


@pytest.mark.parametrize("metodo", ["POST", "PUT", "DELETE"])
def test_somente_leitura(srv, metodo):
    assert _get(srv, "/dados/hall.json", metodo)[0].status in (405, 501)
