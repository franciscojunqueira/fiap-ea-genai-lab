# Verificação (EXEMPLO do ticket ERP-077, estoque baixo; não é o Lab 1)

Escrita pelo verificador e pelo relator depois de ler o diff e testar a API. Repare que cada linha diz
**como** foi conferida.

## O que o agente acertou

- Pôs a regra em `services/estoque.py` e a rota só chama o service: conferido no `git diff`.
- Produto inativo fica de fora (CA-02): chamamos `/produtos/estoque-baixo?limite=1000` no `/docs` e a
  Webcam HD não apareceu.
- Ordenação do menor para o maior (CA-05): conferida na mesma chamada.

## O que o agente inventou

- No resumo final, disse que "criou um índice no banco para a consulta ficar rápida". Não há índice
  nenhum no diff: só a função no service e a rota.

## O que o agente omitiu

- Nenhum teste para o CA-04 (limite padrão 10). O comportamento está certo quando chamamos sem o
  parâmetro, mas nada impede que ele quebre numa mudança futura.

## O que mudaríamos no harness

- Na spec: dizer que o limite padrão precisa de teste próprio.
- No `AGENTS.md`: "não afirme no resumo o que não está no diff".

## Pergunta de decisão

> Que regra deste lab vocês poriam no harness de todos os repositórios da TechCorp, em que nível
> (Público, Interno, Regulado) ela seria obrigatória, e quanto custa (tempo de CI, tokens, atrito
> para quem desenvolve)?

Exemplo de resposta (para outro tema): "Todo endpoint novo tem um teste de contrato de erro (`400`
com `detail`), obrigatório em Interno e Regulado. Custa um teste por endpoint e alguns segundos de
CI; o atrito é pequeno, e um erro sem `detail` vira chamado no suporte."
