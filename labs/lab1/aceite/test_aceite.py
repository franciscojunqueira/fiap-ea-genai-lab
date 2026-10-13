"""Testes de aceite do Lab 1 (ticket ERP-142). São o sensor do professor: não editar.

Cada falha diz, na linguagem do ticket, o que não está sendo cumprido.
"""
import httpx

# Mouse USB: produto ativo com 100 unidades no seed, folga para os pedidos dos testes.
PRODUTO = 2


def estoque(url):
    return httpx.get(f"{url}/estoque/{PRODUTO}").json()["quantidade"]


def novo_pedido(url, quantidade=3):
    r = httpx.post(f"{url}/pedidos", json={"nome_cliente": "Cliente Sintético Ltda",
                                           "itens": [{"produto_id": PRODUTO, "quantidade": quantidade}]})
    assert r.status_code == 201, f"Criar pedido falhou ({r.status_code}): {r.text[:150]}. O fluxo de pedidos quebrou."
    return r.json()


def cancelar(url, pedido_id):
    return httpx.post(f"{url}/pedidos/{pedido_id}/cancelar")


def test_cancelar_pedido_devolve_o_estoque(erp_url):
    antes = estoque(erp_url)
    pedido = novo_pedido(erp_url)
    r = cancelar(erp_url, pedido["id"])
    assert r.status_code == 200, f"Ticket: cancelar um pedido criado responde 200; respondeu {r.status_code}: {r.text[:150]}"
    assert r.json()["status"] == "CANCELADO", f"Ticket: o pedido volta com status CANCELADO; voltou {r.json().get('status')}"
    assert estoque(erp_url) == antes, f"Ticket: o estoque tem de voltar. Era {antes} antes do pedido e ficou {estoque(erp_url)}"


def test_pedido_faturado_nao_se_cancela(erp_url):
    pedido = novo_pedido(erp_url)
    httpx.post(f"{erp_url}/pedidos/{pedido['id']}/fatura")
    depois_da_fatura = estoque(erp_url)
    r = cancelar(erp_url, pedido["id"])
    assert r.status_code == 409, f"Ticket: pedido faturado não se cancela (409); respondeu {r.status_code}"
    assert r.json().get("detail"), "Ticket: o 409 traz em 'detail' o motivo da recusa"
    assert estoque(erp_url) == depois_da_fatura, "Pedido faturado não pode devolver estoque ao ser recusado"
    status = httpx.get(f"{erp_url}/pedidos/{pedido['id']}").json()["status"]
    assert status == "FATURADO", f"Pedido faturado tem de continuar FATURADO depois da recusa; ficou {status}"


def test_clicar_duas_vezes_nao_devolve_o_estoque_duas_vezes(erp_url):
    antes = estoque(erp_url)
    pedido = novo_pedido(erp_url)
    cancelar(erp_url, pedido["id"])
    r = cancelar(erp_url, pedido["id"])
    assert r.status_code == 200, f"Ticket: clicar de novo dá o mesmo resultado da primeira vez (200); respondeu {r.status_code}"
    assert r.json()["status"] == "CANCELADO", "Ticket: o segundo clique devolve o pedido CANCELADO"
    assert estoque(erp_url) == antes, (f"Ticket: o segundo clique devolveu o estoque outra vez "
                                       f"(era {antes}, ficou {estoque(erp_url)}). Cancelar tem de ser idempotente")


def test_pedido_inexistente_responde_404(erp_url):
    r = cancelar(erp_url, 999999)
    assert r.status_code == 404, f"Ticket: pedido inexistente responde 404; respondeu {r.status_code}"
