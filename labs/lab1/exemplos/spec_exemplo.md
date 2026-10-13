# Spec: produtos com estoque baixo (EXEMPLO, ticket ERP-077; não é o Lab 1)

## Contexto

Compras abre produto por produto para saber o que repor. Queremos uma consulta que devolva, de uma
vez, os produtos ativos abaixo de um limite de estoque.

## Contrato

`GET /produtos/estoque-baixo?limite=N`: `200` com `[{produto_id, nome, quantidade}]`, ordenada da
menor para a maior quantidade; `400` com `detail` quando o limite for inválido.

## Critérios de aceite

- **CA-01:** Dado um produto ativo com 3 unidades, quando consulto com `limite=5`, então ele aparece na lista com quantidade 3.
- **CA-02:** Dado um produto inativo, quando consulto com qualquer limite, então ele não aparece.
- **CA-03:** Dado `limite=0` ou negativo, quando consulto, então recebo `400` com o motivo em `detail`.
- **CA-04:** Dado um produto ativo com 9 unidades e outro com 12, quando consulto sem informar o limite, então só o de 9 aparece (o limite padrão é 10).
- **CA-05:** Dado mais de um produto abaixo do limite, quando consulto, então a lista vem do menor para o maior estoque ("o que está mais perto de acabar" primeiro).

## Fora do escopo

Comprar ou repor estoque; alterar o cadastro de produtos; mudar o contrato de outras rotas.

## Restrições de arquitetura

A regra fica em `mini-erp/app/services/estoque.py`; a rota só chama o service. O `400` sai de
`RegraDeNegocio(..., status=400)`.

<!--
Como ler este exemplo:
- Cada CA tem uma situação (Dado), uma ação (quando) e um resultado que se confere (então).
- As frases soltas do ticket ("saiu de linha não me interessa") viraram CAs verificáveis (CA-02).
- Todo CA sai do ticket: a spec não inventa requisito. O que o ticket não diz vai para "Fora do escopo"
  ou vira pergunta para quem pediu.
- Nenhum CA diz como implementar: a implementação é do agente; o critério é do grupo.
- "Fora do escopo" diz ao agente o que NÃO fazer: agentes tendem a fazer mais do que foi pedido.
-->
