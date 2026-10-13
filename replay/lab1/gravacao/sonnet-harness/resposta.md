O cancelamento de pedido está implementado, e os itens de código (4, 5 e 6) do `make lab1-check` passam. O item 7 continua em FALHA porque o `verificacao.md` está sem resposta. Esse arquivo é do grupo e eu não o toquei, nem a spec nem o `AGENTS.md`.

Já havia um rascunho de um colega em `routes/pedidos.py` que acessava o banco direto, ao estilo de `faturas.py`, e eu o substituí.

- **Service:** `cancelar` em `mini-erp/app/services/pedidos.py` concentra a regra.
  - Pedido inexistente dá 404, pelo `obter`.
  - Pedido já CANCELADO é devolvido sem mexer no estoque.
  - Pedido que não seja CRIADO (por exemplo FATURADO) levanta `RegraDeNegocio(..., status=409)`, sem alterar status nem estoque.
  - Pedido CRIADO devolve ao estoque a quantidade de cada item e passa para CANCELADO.
- **Rota:** `POST /pedidos/{id}/cancelar` em `mini-erp/app/routes/pedidos.py` só chama o service. Removi os imports de modelo e de `HTTPException`, que ficaram sem uso.

Considerei CRIADO como o único status cancelável, então qualquer status novo no futuro vai dar 409 por padrão.