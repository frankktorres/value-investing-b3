"""Servidor da tela: só 127.0.0.1, só leitura, tipos certos (módulo ES precisa de text/javascript), sem listar pasta,
sem sair da pasta web/."""
import http.client
import threading

import os

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


def _get_host(s, caminho, host):
    c = http.client.HTTPConnection(*s.server_address, timeout=5)
    c.putrequest("GET", caminho, skip_host=True)
    c.putheader("Host", host)
    c.endheaders()
    r = c.getresponse()
    r.read()
    c.close()
    return r.status


def test_dns_rebinding_host_de_fora_e_recusado(srv):
    porta = srv.server_address[1]
    assert _get_host(srv, "/dados/hall.json", "evil.example") == 403
    assert _get_host(srv, "/dados/hall.json", f"evil.example:{porta}") == 403
    assert _get_host(srv, "/dados/hall.json", f"localhost:{porta}") == 200
    assert _get_host(srv, "/dados/hall.json", f"127.0.0.1:{porta}") == 200


@pytest.mark.parametrize("caminho,status", [("/app.js%00.txt", 400), ("/index.html::$DATA", 404)])
def test_caminho_estranho_responde_sem_derrubar(srv, caminho, status):
    assert _get(srv, caminho)[0].status == status
    assert _get(srv, "/")[0].status == 200                  # o servidor segue de pé


@pytest.mark.parametrize("metodo", ["POST", "PUT", "DELETE"])
def test_somente_leitura(srv, metodo):
    assert _get(srv, "/dados/hall.json", metodo)[0].status in (405, 501)


def test_segundo_servidor_na_mesma_porta_falha(tmp_path, srv):
    """N9: bind exclusivo — dois `painel` na mesma porta davam ERR_CONNECTION_REFUSED intermitente no Windows."""
    with pytest.raises(OSError):
        servir.servidor(srv.server_address[1], tmp_path)


def test_servir_porta_em_uso_sai_com_mensagem(srv, capsys):
    with pytest.raises(SystemExit) as e:
        servir.servir(srv.server_address[1], abrir=False)
    assert e.value.code == 1
    assert "em uso" in capsys.readouterr().err


@pytest.mark.skipif(os.name == "nt", reason="TIME_WAIT/SO_REUSEADDR: semântica POSIX (N13)")
def test_reabrir_logo_depois_de_fechar_com_conexao_atendida(tmp_path):
    """N13: depois de atender uma conexão o servidor fica em TIME_WAIT; reabrir na mesma porta não pode dar "Address in use"."""
    import threading
    import urllib.error
    import urllib.request
    (tmp_path / "index.html").write_text("ok", encoding="utf-8")
    s1 = servir.servidor(0, tmp_path)
    porta = s1.server_address[1]
    t = threading.Thread(target=s1.serve_forever, daemon=True)
    t.start()
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{porta}/index.html", timeout=5).read()
    except urllib.error.HTTPError:
        pass
    s1.shutdown()
    s1.server_close()
    s2 = servir.servidor(porta, tmp_path)          # antes da N13: OSError [Errno 98] Address already in use
    s2.server_close()
