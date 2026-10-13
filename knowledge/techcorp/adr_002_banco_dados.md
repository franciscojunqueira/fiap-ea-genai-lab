# ADR-002: Migração do Oracle para PostgreSQL

**Status:** Em Implementação
**Data:** 2024-09-01
**Decisores:** CTO, VP de Engenharia, Comitê de Arquitetura

## Contexto

O contrato de licenciamento Oracle da TechCorp custa $1.2M/ano e expira em março/2025.
O banco Oracle centralizado atende 23 serviços e apresenta:
- Contenção de locks em horários de pico (19h-22h)
- Impossibilidade de escalar horizontalmente sem custo proibitivo
- Dependência de DBAs especializados Oracle (apenas 2 na empresa)

## Decisão

Migrar progressivamente para PostgreSQL 16 com a seguinte estratégia:
1. Novos serviços obrigatoriamente usam PostgreSQL
2. Serviços existentes migrados por ordem de criticidade inversa (menos críticos primeiro)
3. Serviços financeiros (core banking) permanecem no Oracle até validação completa

## Justificativa

- Redução de custo de licenciamento: $1.2M/ano → ~$180k/ano (infra + suporte Crunchy Data)
- PostgreSQL 16 oferece particionamento nativo e logical replication
- Ecossistema de ferramentas open-source mais amplo (pgBouncer, pg_stat_statements)
- 70% do time de engenharia já tem experiência com PostgreSQL

## Consequências

- Período de coexistência Oracle + PostgreSQL de ~12 meses
- Necessário implementar CDC (Change Data Capture) com Debezium para sincronização
- Risco: incompatibilidades de SQL entre Oracle e PostgreSQL — mitigado com suite de testes de compatibilidade
- Treinamento obrigatório para os 2 DBAs Oracle em PostgreSQL avançado
