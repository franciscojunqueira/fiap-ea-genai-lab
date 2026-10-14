---
nivel: Público
dono: TI Operacional
---

# FAQ de suporte do Gestão PJ

**Área responsável:** TI Operacional, com o squad Gestão PJ
**Última revisão:** 02/09/2026
**Público:** analistas de suporte N1 e N2

O Gestão PJ é o ERP de vendas e faturamento que o banco oferece aos clientes pessoa jurídica.
Chamados vão para a fila GPJ-SUPORTE no ServiceNow.

## Pedidos

**O cliente diz que o pedido não foi criado. O que verificar?**
Confira na tela de pedidos se o pedido existe. O Gestão PJ recusa o pedido quando algum produto
está inativo ou quando não há estoque suficiente; a mensagem de erro aparece para o cliente.

**O pedido abate o estoque na hora?**
Sim. Ao criar o pedido, o sistema valida e abate o estoque de cada item.

**Dá para cancelar um pedido?**
O cancelamento é feito pelo próprio cliente, antes da emissão da fatura. Depois da fatura, só pelo
squad Gestão PJ, por chamado.

## Faturas

**O cliente emitiu a fatura, mas o boleto não chegou. Por quê?**
A fatura vira boleto no SGC, no lote noturno do dia útil. Fatura emitida hoje só tem boleto no dia
seguinte. Se passou de um dia útil, abra chamado na fila COB-SGC com o número da fatura.

**Posso alterar o valor de uma fatura?**
Não. Fatura emitida não muda; o caminho é cancelar e emitir outra, pelo squad Gestão PJ.

## Estoque

**O cliente quer corrigir o estoque de um produto. Como faço?**
**Ajuste de estoque exige aprovação de um supervisor.** O analista registra o pedido de ajuste com
o motivo (inventário, perda, devolução) e o supervisor do suporte aprova antes da execução.

**O estoque está negativo. É erro?**
É. O sistema não deveria permitir. Abra chamado na fila GPJ-SUPORTE com o produto e os últimos
pedidos.

## Alertas

**O que são os alertas do Gestão PJ?**
Avisos registrados para o cliente ou para o suporte, por exemplo estoque baixo ou fatura sem
boleto. O suporte pode registrar um alerta; o squad Gestão PJ define os tipos disponíveis.

## Acesso e cadastro

**O cliente não consegue entrar no Gestão PJ.**
O acesso usa as credenciais do internet banking PJ. Problemas de senha vão para a central de
atendimento PJ, não para a TI Operacional.

**Quem pode ver os dados de um cliente?**
Só o suporte, durante o atendimento de um chamado do próprio cliente.
