"""EXEMPLO de teste do grupo para o ticket ERP-077 (estoque baixo), NÃO para o Lab 1. Ler, não executar.

A rota deste exemplo não existe no Mini-ERP: o arquivo serve para mostrar a forma do teste que o
grupo escreve em labs/lab1/testes/test_grupo.py, a partir de UM critério de aceite da spec.
"""
import httpx


def test_ca_02_produto_inativo_nao_aparece(erp_url):
    """CA-02: produto inativo não aparece na lista de reposição."""
    # 1. Preparar: a fixture erp_url sobe o Mini-ERP com o banco inicial, em que a
    #    Webcam HD (produto 5) é inativa. Nada mais a preparar para este CA.

    # 2. Chamar a API como o cliente chamaria
    resposta = httpx.get(f"{erp_url}/produtos/estoque-baixo", params={"limite": 1000})

    # 3. Conferir o que o CA promete, com uma mensagem que diga o que falhou
    assert resposta.status_code == 200, f"Esperava 200, veio {resposta.status_code}: {resposta.text[:120]}"
    ids = [p["produto_id"] for p in resposta.json()]
    assert 5 not in ids, "CA-02: produto inativo não pode aparecer na lista de reposição"

# O que observar:
# - O CA aparece no nome (test_ca_02_..., com sublinhado: nome de função não aceita hífen) e na
#   docstring ("CA-02: ..."). O check aceita qualquer uma das duas formas.
# - Um teste, um critério. Não tente cobrir a spec inteira: os testes de aceite do professor já fazem isso.
# - A mensagem do assert diz, em linguagem de negócio, o que deu errado.
