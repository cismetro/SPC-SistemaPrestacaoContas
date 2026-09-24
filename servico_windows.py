# -*- coding: utf-8 -*-
"""Serviço Windows SPC-SistemaPrestacaoContas.

Instalação (prompt elevado):
    SPC_venv\\Scripts\\python.exe servico_windows.py install
    SPC_venv\\Scripts\\python.exe servico_windows.py start
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

try:
    import servicemanager
    import win32event
    import win32service
    import win32serviceutil
except ImportError as exc:
    raise SystemExit(
        "pywin32 não está instalado neste interpretador. "
        "Use o Python do ambiente SPC_venv."
    ) from exc


class SPCService(win32serviceutil.ServiceFramework):
    _svc_name_ = "SPC-SistemaPrestacaoContas"
    _svc_display_name_ = "SPC-SistemaPrestacaoContas"
    _svc_description_ = (
        "Sistema de Prestação de Contas dos repasses ao terceiro setor. "
        "Prefeitura Municipal de Cosmópolis. Não transmite arquivos ao Audesp."
    )

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)
        self.processo = None

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ""),
        )
        ambiente = os.environ.copy()
        ambiente["FLASK_ENV"] = "production"
        ambiente["PORT"] = "5735"
        ambiente["PYTHONIOENCODING"] = "utf-8"
        self.processo = subprocess.Popen(
            [sys.executable, str(ROOT / "SPC.py")],
            cwd=str(ROOT),
            env=ambiente,
        )
        while True:
            resultado = win32event.WaitForSingleObject(self.stop_event, 1000)
            if resultado == win32event.WAIT_OBJECT_0:
                break
            if self.processo.poll() is not None:
                break
        if self.processo and self.processo.poll() is None:
            self.processo.terminate()
            try:
                self.processo.wait(timeout=20)
            except subprocess.TimeoutExpired:
                self.processo.kill()


if __name__ == "__main__":
    win32serviceutil.HandleCommandLine(SPCService)
