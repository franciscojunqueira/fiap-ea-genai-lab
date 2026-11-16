# Lab 5 (Aula 3): o AI gateway e o custo por rota

**Na Aula 3, este lab é uma demonstração do professor.** Os grupos não rodam nada em aula: acompanham a
tela e respondem no chat. Cada comando abaixo vem com o conceito que ele mostra.

## O gateway simulado

O Bússola não chama o modelo direto: chama o **gateway**, o ponto por onde passa toda chamada a modelo da
empresa. O `gateway.py` lê as regras de `rotas.toml`, decide o caminho do pedido, chama o modelo (o RAG do
Lab 2) e grava o registro em `labs/lab5/estado/registro.jsonl`. Cada decisão aparece numa linha.

| Comando | O que aparece na tela | Conceito | No Azure API Management (APIM v2) |
|---|---|---|---|
| `make lab5-gateway SIMULACAO=residencia` | o pedido da TI vai para a região global; o do Risco, com CPF, vai para a rota no Brasil | **residência** como regra de roteamento (RC-03) | `set-backend-service` dentro de um `choose` |
| `make lab5-gateway SIMULACAO=complexidade` | a pergunta simples vai ao modelo pequeno; a de análise, ao grande | **roteamento por complexidade** | no Foundry, o model router (só em implantação global) |
| `make lab5-gateway SIMULACAO=cota` | o Risco estoura a cota do mês e o pedido é recusado (429) | **cota por área** ligada ao orçamento (RC-08) | `llm-token-limit` com `token-quota` |
| `make lab5-gateway SIMULACAO=cache` | a 2ª pergunta volta do cache; a 3ª, sobre outro assunto, recebe a resposta errada | **cache semântico**: economia e risco | `llm-semantic-cache-lookup` e `-store` |
| `make lab5-gateway SIMULACAO=reserva` | o modelo principal recusa e o gateway desvia para o reserva | **modelo reserva** e circuit breaker (RC-07) | backend pool com prioridade e circuit breaker |
| `make lab5-gateway SIMULACAO=apelido` | a aplicação pede "bussola-padrao"; uma linha no gateway troca a versão | **apelido de modelo**: trocar de modelo sem mudar a aplicação, depois da eval | unified model API (preview em 11/2026) |
| `make lab5-gateway SIMULACAO=registro` | o que o gateway registrou e o que só a aplicação sabe (usuário, fontes) | **registro para auditoria** (RC-05) | tabela `ApiManagementGatewayLlmLog` |

**Simplificações, ditas na aula:** a rota "Brasil" é simulada, porque nenhum modelo Claude roda em região
no Brasil (conferido em 16/11/2026); a complexidade é uma lista de palavras, e não um modelo treinado; o
cache compara palavras, e não embeddings.

## O custo por rota

`make lab5-tco DIVISAO=<nome>` não chama modelo. Ele lê os volumes do caso, a divisão das consultas entre
as arquiteturas (`premissas.toml`), o custo por consulta medido nos testes do Lab 2 e o câmbio e o custo
do gateway, com data. Mostra o custo por mês em cada cenário, contra o orçamento da RC-08.

| `DIVISAO=` | O que mostra |
|---|---|
| `tudo-haiku-rag` | o mais barato, que acerta 7 de 10 |
| `roteado` | o gateway divide entre Haiku e Sonnet com busca agêntica |
| `tudo-sonnet-agentica` | o mais caro medido |
| `multiagente` | uma ESTIMATIVA (3× a busca agêntica do Sonnet, piso da faixa da Anthropic) |

A parcela do Risco que precisa ficar no Brasil sai da conta: o custo dela não foi medido.

## Se algo falhar na aula

`make lab5-gateway-replay` mostra as sete simulações gravadas pelo professor em 16/11/2026. O custo é
determinístico e não precisa de gravação. Não há `make lab5-check`.
