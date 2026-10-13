Perfeito! Os itens de código (4, 5 e 6) passaram. Implementei:

1. **Função `cancelar()` em `services/pedidos.py`** que:
   - Levanta `NaoEncontrado` (404) se o pedido não existe
   - Levanta `RegraDeNegocio` com status 409 se o pedido foi faturado
   - É idempotente: se já cancelado, devolve sem alterar estoque novamente
   - Devolve estoque dos itens e muda status para CANCELADO

2. **Rota limpa em `routes/pedidos.py`** que:
   - Remove o acesso direto ao banco
   - Chama o service e retorna o pedido formatado

O teste de aceite passou completamente, validando CA-02 (pedido faturado não cancela com 409) e CA-03 (cancelamento idempotente).