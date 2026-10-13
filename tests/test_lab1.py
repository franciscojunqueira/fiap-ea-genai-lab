"""Regressão do make lab1-check: FAIL útil no estado inicial, PASS na referência com os exemplos."""
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
IGNORAR = shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "resultados", "*.db",
                                 "core-banking-api", "replay", "integrador")


def rodar(copia, *args):
    return subprocess.run([sys.executable, *args], cwd=copia, capture_output=True, text=True)


def test_lab1_check_falha_no_inicio_e_passa_na_referencia(tmp_path):
    copia = tmp_path / "repo"
    shutil.copytree(RAIZ, copia, ignore=IGNORAR)

    inicio = rodar(copia, "labs/lab1/checar.py")
    assert inicio.returncode == 1 and "Rode `make lab1` primeiro" in inicio.stdout

    assert rodar(copia, "labs/lab1/preparar.py").returncode == 0
    preparado = rodar(copia, "labs/lab1/checar.py")
    assert preparado.returncode == 1
    assert "'camadas' está desligada" in preparado.stdout
    assert "pedido faturado não se cancela (409); respondeu 200" in preparado.stdout
    assert "devolveu o estoque outra vez" in preparado.stdout

    (copia / "labs/lab1/sensores.toml").write_text(
        (copia / "labs/lab1/sensores.toml").read_text(encoding="utf-8").replace("ligado = false", "ligado = true"), encoding="utf-8")
    ligado = rodar(copia, "labs/lab1/checar.py")
    assert "routes/pedidos.py:5 importa Estoque, Pedido de app.models" in ligado.stdout

    assert rodar(copia, "labs/lab1/referencia/aplicar.py", "--exemplos").returncode == 0
    final = rodar(copia, "labs/lab1/checar.py")
    assert final.returncode == 0, final.stdout
    assert "lab1-check: PASS (7/7 itens)" in final.stdout
