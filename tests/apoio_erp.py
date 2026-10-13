"""Sobe o Mini-ERP num processo separado, para os testes de fumaça e os testes dos labs."""
import os
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

import httpx

RAIZ = Path(__file__).resolve().parent.parent
# Mesmo limite do scripts/check.py: o ERP subiu em menos de 0,5 s nas medições; 20 s dão folga.
ERP_TIMEOUT_S = 20


def porta_livre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextmanager
def erp_rodando(banco: Path):
    """Sobe o ERP numa porta livre, com o banco SQLite indicado, e devolve a URL. Levanta RuntimeError se não subir."""
    porta = porta_livre()
    env = {**os.environ, "ERP_DB_PATH": str(banco)}
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
                raise RuntimeError(f"Mini-ERP não respondeu em {ERP_TIMEOUT_S} s. Saída:\n{saida}")
            time.sleep(0.2)
        yield url
    finally:
        proc.terminate()
        proc.wait(timeout=5)
