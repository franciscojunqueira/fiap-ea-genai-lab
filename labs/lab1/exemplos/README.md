# Exemplos preenchidos (outro ticket, não o do Lab 1)

Estes arquivos mostram **o formato e o nível de detalhe** esperados em cada coisa que o grupo monta no
Lab 1. Eles resolvem um ticket **diferente e fictício**, o ERP-077 abaixo, para não entregar a resposta
do ERP-142 (cancelamento de pedido). Não copiem o conteúdo: copiem a forma.

| O grupo monta | Exemplo | O que observar |
|---|---|---|
| `labs/lab1/spec.md` | [spec_exemplo.md](spec_exemplo.md) | cada critério de aceite (CA) vira um teste; nenhum diz *como* implementar |
| seção `## Mini-ERP` do `AGENTS.md` | [agents_secao_exemplo.md](agents_secao_exemplo.md) | só o que o agente não descobre sozinho; curto |
| `labs/lab1/testes/test_grupo.py` | [teste_exemplo.py](teste_exemplo.py) | um CA, citado no nome; prepara, chama, confere |
| `labs/lab1/verificacao.md` | [verificacao_exemplo.md](verificacao_exemplo.md) | afirmações do agente conferidas no código, não aceitas de boa-fé |

O `labs/lab1/sensores.toml` não tem exemplo: é só trocar `ligado = false` por `ligado = true`.

## O ticket do exemplo (fictício)

> **ERP-077: produtos com estoque baixo.** O time de Compras quer, numa chamada só, a lista do que
> precisa repor. Contrato: `GET /produtos/estoque-baixo?limite=N` devolve `200` com a lista
> `[{produto_id, nome, quantidade}]`. Fala do comprador: "produto que saiu de linha não me interessa";
> "se eu não disser o limite, usa 10"; "limite zero ou negativo é erro de digitação, me avisa";
> "quero ver primeiro o que está mais perto de acabar".

O agente não lê esta pasta (está negada no `.claude/settings.json`): os exemplos são para o grupo.
