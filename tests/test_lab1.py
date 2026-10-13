"""Regressão do make lab1-check: FAIL útil no estado inicial, sensores à prova de atalho, PASS na referência."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent

# Estes testes conferem o template e partem do lab NÃO preparado. Depois do `make lab1` (repositório de
# grupo), a cópia já traz spec, sensores e código alterados: pular em vez de falhar, para o `make test`
# do grupo não acusar um erro que não é dele.
pytestmark = pytest.mark.skipif(
    (RAIZ / "labs/lab1/spec.md").exists(),
    reason="lab 1 já preparado: estes testes conferem o template; o grupo usa make lab1-check",
)
IGNORAR =shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "resultados", "*.db",
                                 "core-banking-api", "replay", "integrador")


def rodar(copia, *args):
    return subprocess.run([sys.executable, *args], cwd=copia, capture_output=True, text=True)


def trocar(arquivo, velho, novo):
    arquivo.write_text(arquivo.read_text(encoding="utf-8").replace(velho, novo), encoding="utf-8")


def test_lab1_check_falha_no_inicio_e_passa_na_referencia(tmp_path):
    copia = tmp_path / "repo"
    shutil.copytree(RAIZ, copia, ignore=IGNORAR)
    lab = copia / "labs/lab1"

    inicio = rodar(copia, "labs/lab1/checar.py")
    assert inicio.returncode == 1 and "Rode `make lab1` primeiro" in inicio.stdout

    assert rodar(copia, "labs/lab1/preparar.py").returncode == 0
    preparado = rodar(copia, "labs/lab1/checar.py")
    assert preparado.returncode == 1
    assert "'camadas' está desligada" in preparado.stdout
    # Antes da spec, o check não entrega as regras escondidas no ticket
    assert "2 de 4 testes de aceite do ticket falham" in preparado.stdout
    assert "409" not in preparado.stdout

    trocar(lab / "sensores.toml", "ligado = false", "ligado = true")
    ligado = rodar(copia, "labs/lab1/checar.py")
    assert "routes/pedidos.py:5 importa Estoque, Pedido de app.models" in ligado.stdout

    # Com a spec escrita, cada falha de aceite aparece com a regra do ticket
    shutil.copy(lab / "referencia/exemplo_spec.md", lab / "spec.md")
    com_spec = rodar(copia, "labs/lab1/checar.py")
    assert "pedido faturado não se cancela (409); respondeu 200" in com_spec.stdout
    assert "devolveu o estoque outra vez" in com_spec.stdout

    assert rodar(copia, "labs/lab1/referencia/aplicar.py", "--exemplos").returncode == 0
    final = rodar(copia, "labs/lab1/checar.py")
    assert final.returncode == 0, final.stdout
    assert "lab1-check: PASS (7/7 itens)" in final.stdout


def test_lab1_check_nao_aceita_atalhos(tmp_path):
    copia = tmp_path / "repo"
    shutil.copytree(RAIZ, copia, ignore=IGNORAR)
    lab = copia / "labs/lab1"
    rodar(copia, "labs/lab1/preparar.py")
    rodar(copia, "labs/lab1/referencia/aplicar.py", "--exemplos")
    assert rodar(copia, "labs/lab1/checar.py").returncode == 0

    # 1. Silenciar o sensor com uma exceção nova
    trocar(lab / "sensores.toml", 'excecoes = ["routes/faturas.py"]', 'excecoes = ["routes/faturas.py", "routes/pedidos.py"]')
    assert "A lista de exceções de labs/lab1/sensores.toml mudou" in rodar(copia, "labs/lab1/checar.py").stdout
    trocar(lab / "sensores.toml", 'excecoes = ["routes/faturas.py", "routes/pedidos.py"]', 'excecoes = ["routes/faturas.py"]')

    # 2. Acessar o banco na rota com outro nome de import e de variável
    rota = copia / "mini-erp/app/routes/pedidos.py"
    trocar(rota, "from app.services import pedidos\n", "from app.services import pedidos\nimport app.models as m\n")
    trocar(rota, '    """Retorna os últimos pedidos (padrão: 10)."""\n',
           '    """Retorna os últimos pedidos (padrão: 10)."""\n    banco = db\n    banco.query(m.Pedido).count()\n')
    saida = rodar(copia, "labs/lab1/checar.py").stdout
    assert "importa app.models" in saida and "chama banco.query() direto" in saida
    trocar(rota, "import app.models as m\n", "")
    trocar(rota, "    banco = db\n    banco.query(m.Pedido).count()\n", "")

    # 3. Editar um teste de aceite
    trocar(lab / "aceite/test_aceite.py", "== 409", "in (200, 409)")
    assert "Sensor do professor alterado: labs/lab1/aceite/test_aceite.py" in rodar(copia, "labs/lab1/checar.py").stdout
