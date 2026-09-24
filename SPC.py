#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPC - Sistema de Prestação de Contas
Prefeitura Municipal de Cosmópolis - SP
Ponto de entrada da aplicação
"""

import logging
import os
import socket
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


MODULOS_OBRIGATORIOS = (
    ("flask", "Flask"),
    ("flask_login", "Flask-Login"),
    ("flask_sqlalchemy", "Flask-SQLAlchemy"),
)


class _FiltroRuidoWerkzeug(logging.Filter):
    _BLOQUEIOS = (
        "Running on",
        "development server",
        "Restarting with",
        "Debugger PIN",
        "Debugger is active",
        "Press CTRL+C",
        "WARNING: This is a development server",
    )

    def filter(self, record):
        mensagem = record.getMessage()
        return not any(trecho in mensagem for trecho in self._BLOQUEIOS)


def configurar_console():
    if sys.platform != "win32":
        return
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        import ctypes

        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
        handle = ctypes.windll.kernel32.GetStdHandle(-11)
        modo = ctypes.c_uint32()
        if ctypes.windll.kernel32.GetConsoleMode(handle, ctypes.byref(modo)):
            ctypes.windll.kernel32.SetConsoleMode(handle, modo.value | 0x0004)
    except Exception:
        pass
    try:
        import colorama

        colorama.just_fix_windows_console()
    except Exception:
        pass


def _usa_cor():
    return sys.stdout.isatty()


def _c(codigo, texto):
    if not _usa_cor():
        return texto
    return f"\033[{codigo}m{texto}\033[0m"


def _imprimir(texto=""):
    try:
        print(texto)
    except UnicodeEncodeError:
        print(texto.encode("ascii", "replace").decode("ascii"))


def verificar_dependencias():
    ausentes = []
    for modulo, pacote in MODULOS_OBRIGATORIOS:
        try:
            __import__(modulo)
        except ImportError:
            ausentes.append(pacote)
    if not ausentes:
        return
    python_cmd = f'"{sys.executable}" -m pip install {" ".join(ausentes)}'
    _imprimir()
    _imprimir(_c("1;31", "  SPC — ambiente Python incompleto"))
    _imprimir()
    _imprimir(f"  Interpretador : {sys.executable}")
    _imprimir(f"  Pacotes       : {', '.join(ausentes)}")
    _imprimir(f"    {python_cmd}")
    _imprimir()
    sys.exit(1)


def _silenciar_banner_flask():
    try:
        from flask import cli

        cli.show_server_banner = lambda *args, **kwargs: None
    except Exception:
        pass
    logger = logging.getLogger("werkzeug")
    if not any(isinstance(f, _FiltroRuidoWerkzeug) for f in logger.filters):
        logger.addFilter(_FiltroRuidoWerkzeug())


def _eh_filho_do_reloader():
    return os.environ.get("WERKZEUG_RUN_MAIN") == "true"


def _ip_rede():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ip = sock.getsockname()[0]
        sock.close()
        if ip and not ip.startswith("127."):
            return ip
    except Exception:
        pass
    return None


def _imprimir_banner(host, port, ambiente, versao, debug, producao=False):
    local = f"http://127.0.0.1:{port}"
    rede_ip = _ip_rede() if host in ("0.0.0.0", "::") else None
    largura = 62
    linha = "─" * largura
    _imprimir()
    _imprimir(_c("1;36", "  SPC — Sistema de Prestação de Contas"))
    _imprimir(_c("36", "  Prefeitura Municipal de Cosmópolis — SP"))
    _imprimir(f"  {linha}")
    _imprimir(f'  {_c("1;32", "Local")}       {local}')
    if rede_ip:
        _imprimir(f'  {_c("1;32", "Rede")}        http://{rede_ip}:{port}')
    _imprimir(f"  Versão      {versao}")
    _imprimir(f"  Ambiente    {ambiente}  ·  Python {sys.version.split()[0]}")
    if producao:
        _imprimir("  Servidor    Waitress")
    elif debug:
        _imprimir(_c("33", "  Debug       ativo — não use em produção"))
    _imprimir("  Encerrar    CTRL+C")
    _imprimir(f"  {linha}")
    _imprimir()


configurar_console()
verificar_dependencias()

from app import create_app  # noqa: E402

app = create_app()


def main():
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", app.config.get("PORTA", 5735)))
    ambiente = os.getenv("FLASK_ENV", "development")
    debug = ambiente == "development"
    versao = app.config.get("VERSAO", "1.0.0")
    _silenciar_banner_flask()
    if ambiente == "production":
        _imprimir_banner(host, port, ambiente, versao, debug=False, producao=True)
        from waitress import serve

        serve(app, host=host, port=port, threads=8)
        return
    if debug and _eh_filho_do_reloader():
        _imprimir_banner(host, port, ambiente, versao, debug=True)
    elif not debug:
        _imprimir_banner(host, port, ambiente, versao, debug=False)
    app.run(debug=debug, host=host, port=port, threaded=True, use_reloader=debug)


if __name__ == "__main__":
    main()
