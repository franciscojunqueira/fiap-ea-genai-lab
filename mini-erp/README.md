# Mini-ERP

API REST de distribuição e vendas (FastAPI + SQLite), herdada da v1 do curso. Usada nos Labs 1 e 3.

```bash
make erp      # http://localhost:8000 (interface) e http://localhost:8000/docs (Swagger)
```

O banco (`data/mini_erp.db`) é criado no primeiro uso com 5 produtos, um deles inativo. Para
recomeçar do zero, pare o ERP e apague o arquivo. `ERP_DB_PATH` troca o caminho do banco.

| Método | Rota | O que faz |
|---|---|---|
| GET | `/health` | health check |
| GET | `/produtos`, `/produtos/{id}` | produtos ativos; detalhe |
| GET | `/estoque/{produto_id}` | estoque de um produto |
| POST | `/pedidos` | cria pedido, valida e abate estoque |
| GET | `/pedidos`, `/pedidos/{id}` | últimos pedidos; detalhe com itens |
| POST | `/pedidos/{id}/fatura` | gera fatura simulada |
| GET | `/faturas/{id}` | detalhe da fatura |
| POST/GET | `/alertas` | registra e lista alertas (em memória) |
