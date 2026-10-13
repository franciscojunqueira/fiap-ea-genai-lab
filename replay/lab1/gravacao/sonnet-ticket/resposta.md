O cancelamento do ERP-142 está implementado e os testes de aceite do ticket passam (item 6 do `make lab1-check`). O `make lab1-check` como um todo continua em FAIL (2/7). Os itens que faltam são os do grupo, e eu não os toquei.

**O que mudei**
- **`mini-erp/app/services/pedidos.py`**: nova função `cancelar`, onde fica a regra de negócio.
  - Pedido inexistente dá `404`, pelo `obter`.
  - Pedido já `CANCELADO` devolve `200` com o mesmo pedido e não devolve o estoque outra vez, então o clique duplo é seguro.
  - Pedido faturado (com fatura, ou status `FATURADO`) dá `409` com o motivo no `detail`, pelo `RegraDeNegocio`.
  - Nos demais casos, devolve os itens ao estoque, muda o status para `CANCELADO` e grava.
- **`mini-erp/app/routes/pedidos.py`**: no rascunho do colega, a rota acessava o banco e levantava `HTTPException` direto. Ela agora só chama `pedidos.cancelar`, no mesmo padrão das outras rotas. O rascunho também não tratava o pedido faturado nem o clique duplo, e esses dois casos agora estão cobertos. Removi os imports que ficaram sem uso (`HTTPException`, `Pedido`, `Estoque`).

**O que falta, e é do grupo** (o README do lab e o `AGENTS.md` pedem que o agente não mexa nisso)
- Item 2: `labs/lab1/spec.md`, com pelo menos 3 critérios de aceite no formato CA-NN.
- Item 3: a seção `## Mini-ERP` no `AGENTS.md`.
- Item 4: ligar a fitness function em `sensores.toml`. Ela deve passar com a mudança, mas não rodei com ela ligada.
- Item 5: o teste do grupo em `labs/lab1/testes/test_grupo.py`.
- Item 7: o `verificacao.md`.

Se quiser, escrevo algum desses itens, mas aí o lab deixa de ser um exercício de verificação do grupo.