# Spec: cancelamento de pedido

## Contexto

O atendimento não consegue cancelar pedidos pela API e pede à TI para mexer no banco (ticket ERP-142).

## Contrato

`POST /pedidos/{id}/cancelar`, sem corpo: `200` com o pedido (formato de `GET /pedidos/{id}`) e status
`CANCELADO`; `404` se não existe; `409` com `detail` se não pode ser cancelado.

## Critérios de aceite

- **CA-01:** Dado um pedido CRIADO, quando é cancelado, então responde 200, o status vira CANCELADO e o estoque de cada item volta.
- **CA-02:** Dado um pedido FATURADO, quando se tenta cancelar, então responde 409 com o motivo, e status e estoque não mudam.
- **CA-03:** Dado um pedido já CANCELADO, quando é cancelado de novo, então responde 200 com o pedido e o estoque não volta outra vez.
- **CA-04:** Dado um id inexistente, quando se tenta cancelar, então responde 404.

## Fora do escopo

Estorno de pedido faturado; mudanças no faturamento (`routes/faturas.py`); mudança no contrato.

## Restrições de arquitetura

A regra fica em `mini-erp/app/services/pedidos.py`; a rota só chama o service. O 409 sai de
`RegraDeNegocio(..., status=409)`.
