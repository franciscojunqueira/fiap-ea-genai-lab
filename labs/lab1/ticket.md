# Ticket ERP-142: cancelar pedido

**Pedido por:** Atendimento comercial · **Prioridade:** alta

Hoje não dá para cancelar pedido no Mini-ERP: o atendimento liga para a TI, que mexe no banco à
mão. Queremos o cancelamento pela API (a tela é de outro time).

## Contrato (combinado com o time da tela; não muda)

- `POST /pedidos/{id}/cancelar`, sem corpo.
- Sucesso: `200`, com o pedido no mesmo formato de `GET /pedidos/{id}` e status `CANCELADO`.
- Pedido inexistente: `404`.
- Pedido que não pode ser cancelado: `409`, com `detail` dizendo o motivo.

## O que o atendimento contou

- "Quando cancela, os produtos voltam para a prateleira, né? O estoque tem que voltar."
- "O financeiro já brigou com a gente: pedido faturado não se cancela por aqui. Isso é estorno, outro processo."
- "Às vezes a tela trava e a pessoa clica duas vezes. Clicar de novo tem que dar o mesmo resultado
  da primeira vez: o pedido cancelado, sem devolver o estoque outra vez."
- "Um colega começou isso numa sexta à noite, está em `mini-erp/app/routes/pedidos.py`. Aproveitem o que der."
