---
nivel: Interno
dono: Arquitetura
---

# ADR-047: Cache distribuído com Redis para consultas de saldo

**Status:** Aprovado
**Data:** 12/03/2025
**Decisores:** Comitê de Arquitetura, squad de Pagamentos
**Autor:** Tech lead do squad de Pagamentos

## Contexto

A consulta de saldo é a operação mais chamada da API de pagamentos e saldos do core. Em horário
de pico, cerca de 80% das leituras no banco Oracle do core (que segue no Oracle, ADR-002) são
consultas de saldo repetidas para a mesma conta em poucos minutos (app, internet banking e Gestão PJ consultando em sequência). Cada
réplica do serviço mantinha um cache local em memória, o que gerava três problemas:

- respostas diferentes para a mesma conta conforme a réplica que atendia;
- cache frio a cada deploy canário, com pico de leitura no banco;
- nenhuma forma de invalidar o saldo de todas as réplicas depois de um lançamento.

## Decisão

1. Adotar **Redis em cluster** (Redis 7, 3 primários e 3 réplicas, multi-AZ) como cache
   distribuído das consultas de saldo.
2. TTL de **300 segundos** para a chave de saldo de cada conta.
3. Invalidação por evento: todo lançamento publicado no barramento Kafka (ADR-004) remove a
   chave da conta afetada. O TTL é só a rede de proteção caso um evento se perca.
4. Em falha do Redis, o serviço lê direto do banco (circuit breaker com Resilience4j), sem erro
   para o cliente.

## Alternativas rejeitadas

| Alternativa | Motivo da rejeição |
|---|---|
| Manter o cache local por réplica | não resolve a inconsistência entre réplicas |
| Réplica de leitura do Oracle | reduz a carga, mas não a latência; custo de licença adicional |
| Memcached | sem replicação nativa nem estruturas de dados que usamos em outros casos |
| Cache gerenciado de outro provedor | fora da nuvem atual; latência entre provedores |

## Consequências

- Leitura de saldo passa a ser eventualmente consistente dentro do TTL quando um evento se
  perde. O extrato e a efetivação de pagamento continuam lendo do banco, nunca do cache.
- O squad de Pagamentos passa a operar o cluster Redis, com alertas de memória e de taxa de acerto.
- Toda nova chave de cache do core precisa declarar TTL e evento de invalidação no pull request.
- Revisão da decisão prevista para março de 2026, com base na taxa de acerto medida.
