"""Teste de fumaça do Mini-ERP: sobe a API e percorre o fluxo pedido → fatura."""
import httpx


def test_health_e_catalogo(erp_url):
    assert httpx.get(f"{erp_url}/health").json() == {"status": "ok", "service": "mini-erp"}
    produtos = httpx.get(f"{erp_url}/produtos").json()
    assert {p["nome"] for p in produtos} == {"Notebook Básico", "Mouse USB", "Teclado Mecânico", "Monitor 24pol"}


def test_pedido_abate_estoque_e_gera_fatura(erp_url):
    antes = httpx.get(f"{erp_url}/estoque/1").json()["quantidade"]
    pedido = httpx.post(f"{erp_url}/pedidos", json={
        "nome_cliente": "Cliente Sintético Ltda",
        "itens": [{"produto_id": 1, "quantidade": 2}, {"produto_id": 3, "quantidade": 1}],
    })
    assert pedido.status_code == 201
    assert pedido.json()["total"] == 2 * 2500.0 + 350.0
    assert httpx.get(f"{erp_url}/estoque/1").json()["quantidade"] == antes - 2

    fatura = httpx.post(f"{erp_url}/pedidos/{pedido.json()['id']}/fatura")
    assert fatura.status_code == 201
    assert httpx.get(f"{erp_url}/pedidos/{pedido.json()['id']}").json()["status"] == "FATURADO"
    assert httpx.post(f"{erp_url}/pedidos/{pedido.json()['id']}/fatura").status_code == 400


def test_regras_de_negocio(erp_url):
    inativo = httpx.post(f"{erp_url}/pedidos", json={"nome_cliente": "X", "itens": [{"produto_id": 5, "quantidade": 1}]})
    assert inativo.status_code == 400 and "inativo" in inativo.json()["detail"]
    sem_estoque = httpx.post(f"{erp_url}/pedidos", json={"nome_cliente": "X", "itens": [{"produto_id": 1, "quantidade": 999}]})
    assert sem_estoque.status_code == 400 and "Estoque insuficiente" in sem_estoque.json()["detail"]


def test_erp_reset_guarda_o_banco_antigo_e_recria_no_estado_inicial(tmp_path):
    """make erp-reset: renomeia com a data (não apaga) e volta o estoque do produto 3 a 30, sem ajustes."""
    import os
    import sqlite3
    import subprocess
    import sys
    from pathlib import Path
    raiz = Path(__file__).resolve().parent.parent
    banco = tmp_path / "mini_erp.db"
    env = {**os.environ, "ERP_DB_PATH": str(banco)}
    comando = [sys.executable, str(raiz / "scripts" / "erp_reset.py")]
    subprocess.run(comando, env=env, check=True, capture_output=True)
    with sqlite3.connect(banco) as c:
        c.execute("update estoque set quantidade = 50 where produto_id = 3")
    saida = subprocess.run(comando, env=env, check=True, capture_output=True, text=True).stdout
    guardados = list(tmp_path.glob("mini_erp-*.db"))
    assert len(guardados) == 1 and guardados[0].name in saida and "estoque do produto 3 = 30" in saida
    with sqlite3.connect(guardados[0]) as c:
        assert c.execute("select quantidade from estoque where produto_id = 3").fetchone()[0] == 50
    with sqlite3.connect(banco) as c:
        assert c.execute("select quantidade from estoque where produto_id = 3").fetchone()[0] == 30
        assert c.execute("select count(*) from ajuste_estoque").fetchone()[0] == 0
