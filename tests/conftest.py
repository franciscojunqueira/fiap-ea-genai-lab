"""Fixtures compartilhadas pelos testes de fumaça. Cada teste usa um banco SQLite temporário."""
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx
import pytest

RAIZ = Path(__file__).resolve().parent.parent
# O ERP sobe em ~1 s numa máquina de 2 cores; 20 s cobre a primeira execução, que compila os .pyc.
ERP_TIMEOUT_S = 20


def porta_livre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def erp_url(tmp_path):
    """Sobe o Mini-ERP num processo separado, numa porta livre e com banco temporário."""
    porta = porta_livre()
    env = {**os.environ, "ERP_DB_PATH": str(tmp_path / "erp.db")}
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--app-dir", str(RAIZ / "mini-erp"),
         "--host", "127.0.0.1", "--port", str(porta), "--log-level", "warning"],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    url = f"http://127.0.0.1:{porta}"
    limite = time.monotonic() + ERP_TIMEOUT_S
    try:
        while True:
            try:
                if httpx.get(f"{url}/health", timeout=1).status_code == 200:
                    break
            except httpx.TransportError:
                pass
            if proc.poll() is not None or time.monotonic() > limite:
                saida = proc.stdout.read().decode() if proc.poll() is not None else "(ainda rodando)"
                pytest.fail(f"Mini-ERP não respondeu em {ERP_TIMEOUT_S} s. Saída:\n{saida}")
            time.sleep(0.2)
        yield url
    finally:
        proc.terminate()
        proc.wait(timeout=5)
