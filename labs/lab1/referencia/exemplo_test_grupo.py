"""Sensor do grupo (Lab 1): CA-04, pedido inexistente responde 404."""
import httpx


def test_ca_04_pedido_inexistente(erp_url):
    resposta = httpx.post(f"{erp_url}/pedidos/424242/cancelar")
    assert resposta.status_code == 404
