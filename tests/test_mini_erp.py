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
