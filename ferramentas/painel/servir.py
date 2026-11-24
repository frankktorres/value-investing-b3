"""Servidor de arquivos da tela: só em 127.0.0.1 (nada sai desta máquina), só leitura (GET/HEAD), pasta `web/`.

Tipos fixos no código: no Windows o `mimetypes` lê o registro e pode servir `.js` como text/plain — e o navegador recusa
módulo ES com tipo errado.
"""
from __future__ import annotations

import os
import socket
import sys
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from painel.exportar import WEB

HOST, PORTA = "127.0.0.1", 8765
TIPOS = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
         ".json": "application/json; charset=utf-8", ".woff2": "font/woff2", ".svg": "image/svg+xml",
         ".txt": "text/plain; charset=utf-8", "": "application/octet-stream"}


class Leitura(SimpleHTTPRequestHandler):
    extensions_map = TIPOS

    def send_head(self):
        # DNS rebinding: só atende quem chamou pelo nome local (um site de fora não lê os dados pelo navegador)
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        if host not in ("127.0.0.1", "localhost"):
            self.send_error(403, "só 127.0.0.1")
            return None
        caminho = self.path.split("?", 1)[0].split("#", 1)[0]
        if "%00" in caminho or "\x00" in caminho:
            self.send_error(400)
            return None
        try:
            if ":" in self.translate_path(self.path)[2:]:       # fluxo alternativo do NTFS (arquivo::$DATA)
                self.send_error(404)
                return None
            return super().send_head()
        except ValueError:                                      # caractere inválido no caminho
            self.send_error(400)
            return None

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")             # o JSON muda a cada exportação
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; img-src 'self' data:; style-src 'self'")
        super().end_headers()

    def list_directory(self, path):                                # sem listagem de pasta
        self.send_error(404)
        return None

    def log_message(self, format, *args):                          # terminal limpo  # noqa: A002
        pass


class Exclusivo(ThreadingHTTPServer):
    """Bind exclusivo: no Windows `SO_REUSEADDR` deixa um 2º servidor subir na mesma porta e as conexões se dividem entre
    os dois (ERR_CONNECTION_REFUSED intermitente). Aqui o 2º falha com OSError (N9)."""
    allow_reuse_address = False

    def server_bind(self):
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def servidor(porta: int = PORTA, pasta: Path = WEB) -> ThreadingHTTPServer:
    return Exclusivo((HOST, porta), partial(Leitura, directory=str(pasta)))


def servir(porta: int = PORTA, abrir: bool = True) -> None:
    try:
        srv = servidor(porta)
    except OSError as e:
        print(f"Porta {porta} em uso (já há uma Mesa de Value aberta?): {e.strerror or e}. "
              f"Abra http://{HOST}:{porta}/ ou feche o outro servidor.", file=sys.stderr)
        raise SystemExit(1)
    url = f"http://{HOST}:{srv.server_address[1]}/"
    print(f"Mesa de Value em {url} (Ctrl+C para parar)", flush=True)
    if abrir:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        srv.server_close()
