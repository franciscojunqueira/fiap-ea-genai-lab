# ADR-002: Cache de produtos

**Status:** Aprovado
**Data:** 2026-10-01
**Decisores:** Time de plataforma

## Contexto

O endpoint `GET /produtos` é chamado pelo agente a cada pedido. Queremos reduzir a latência.

## Decisão

Usar Redis como cache do catálogo de produtos, com TTL de 5 minutos.

## Justificativa

Redis é o padrão de mercado e reduz a latência em 90%, conforme auditoria de performance PERF-2025-114.

## Consequências

- Latência menor no catálogo.
