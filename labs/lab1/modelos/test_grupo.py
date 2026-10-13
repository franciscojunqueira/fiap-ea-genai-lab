"""Sensor do grupo (Lab 1): um critério de aceite da spec virando teste.

Troquem CA-NN pelo critério escolhido, escrevam o teste e apaguem a linha do skip.
A fixture erp_url sobe o Mini-ERP com um banco temporário. Rode com `make lab1-check`.
Exemplo da forma (de outro ticket): labs/lab1/exemplos/teste_exemplo.py.
"""
import httpx
import pytest


def test_ca_nn(erp_url):
    pytest.skip("Escrevam o teste de um CA da spec e apaguem esta linha")
    pedido = httpx.post(f"{erp_url}/pedidos", json={
        "nome_cliente": "Cliente Sintético Ltda", "itens": [{"produto_id": 2, "quantidade": 1}],
    }).json()
    resposta = httpx.post(f"{erp_url}/pedidos/{pedido['id']}/cancelar")
    # assert ...
