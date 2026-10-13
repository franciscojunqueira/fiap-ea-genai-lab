A implementação do cancelamento de pedido foi concluída! Aqui está o resumo das mudanças realizadas:

## Implementação do ERP-142: Cancelamento de Pedido

A rota `POST /pedidos/{id}/cancelar` agora implementa:

✅ **Validações de negócio:**
- Retorna 404 se o pedido não existe
- Retorna 409 se o pedido está faturado (não pode ser cancelado)
- Idempotência: se já está cancelado, apenas retorna 200 sem tentar restaurar estoque novamente

✅ **Lógica de cancelamento:**
- Restaura a quantidade dos itens ao estoque
- Muda o status do pedido para `CANCELADO`
- Faz commit das alterações

Os testes de aceite do ticket **passaram** conforme resultado de `make lab1-check`. A implementação segue o padrão do projeto (similar a `faturas.py`) e atende todos os requisitos descritos no ticket.