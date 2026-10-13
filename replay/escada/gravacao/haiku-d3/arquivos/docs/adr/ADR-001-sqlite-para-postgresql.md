# ADR-001: Migração do banco de dados SQLite para PostgreSQL no Mini-ERP

**Status:** Proposto

**Data:** 2026-10-12

**Decisores:** Arquitetura FIAP, Time de Backend

## Contexto

O Mini-ERP atualmente utiliza SQLite como banco de dados, adequado para desenvolvimento e testes. Porém, conforme o sistema cresce, há pressão por escalabilidade, concorrência e funcionalidades avançadas. A migração para PostgreSQL permite suportar múltiplas instâncias, transações complexas e ferramentas de monitoramento mais robustas.

## Requisitos e restrições

| ID     | Descrição | Prioridade |
|--------|-----------|-----------|
| RQ-01  | Suportar múltiplas conexões simultâneas sem corrupção de dados | Alta |
| RQ-02  | Manter compatibilidade com a atual interface de acesso (SQLAlchemy ORM) | Alta |
| RQ-03  | Executar migração sem perda de dados | Alta |
| RQ-04  | Permitir reversão rápida em caso de falha crítica | Média |
| RQ-05  | Reduzir latência de queries sob carga | Média |

## Alternativas consideradas

### A1: Continuar com SQLite + arquivo em filesystem

**Prós:**
- Sem dependências externas
- Simples configuração local
- Perfecto para desenvolvimento isolado

**Contras:**
- Concorrência limitada (locks exclusivos)
- Sem suporte nativo para transações MVCC
- Impossível rodar múltiplas instâncias do Mini-ERP em paralelo
- Ferramentas de backup e monitoramento limitadas

### A2: Migrar para PostgreSQL

**Prós:**
- Suporta centenas de conexões simultâneas
- MVCC nativo, transações ACID robustas
- Índices avançados (B-tree, GiST, GIN)
- Ferramentas maduras de backup, replicação e monitoramento (pgBackRest, Patroni)
- Compatível com SQLAlchemy ORM (mesma interface)
- Comunidade grande, documentação extensiva

**Contras:**
- Requer instalação/manutenção de servidor (ou uso de PaaS)
- Overhead inicial de setup e migração
- Custo operacional (se usar cloud)
- Requer variáveis de ambiente (`ERP_DB_URL`)

### A3: Migrar para MySQL 8+

**Prós:**
- Suporta concorrência e transações ACID
- Comunidade grande
- Compatível com SQLAlchemy ORM

**Contras:**
- Compatibilidade com SQLAlchemy é menos robusta que com PostgreSQL
- Menos recursos avançados que PostgreSQL (ex.: GENERATED ALWAYS, ranges)
- Histórico de bugs em replicação
- Não alinha com stack padrão de Python/FastAPI

## Decisão

Adotar **A2: Migração para PostgreSQL**.

A decisão atende RQ-01, RQ-02 e RQ-05, permitindo que o Mini-ERP suporte múltiplas instâncias, aplicações de teste paralelo e observabilidade em produção, sem quebrar a interface ORM existente.

## Justificativa

PostgreSQL é o padrão de facto em aplicações Python/FastAPI robustas. Atende completamente RQ-01 (concorrência) e RQ-02 (compatibilidade SQLAlchemy) com menor overhead que MySQL. A comunidade e ferramentas de suporte (RQ-05, monitoramento) são maduras. O curso Enterprise Architecture incentiva decisões escaláveis; SQLite é inadequado para arquitetura de múltiplas camadas. A reversão (RQ-04) é viável via Docker Compose + container PostgreSQL descartável.

## Consequências

### Positivas

- Mini-ERP pode rodar múltiplas instâncias em paralelo (ex.: para testes)
- Queries complexas e índices avançados ficam disponíveis
- Ferramentas de monitoramento (pgAdmin, Prometheus) integram-se naturalmente
- Ambiente de dev/test/prod usa mesma tecnologia (reduz surpresas)
- MVCC permite leituras enquanto escritas ocorrem, sem locks

### Negativas e riscos

- **Dependência externa:** PostgreSQL precisa estar rodando (mitigado com Docker Compose)
- **Custo de migração:** scripts de schema e dados precisam ser criados e testados (mitigado com revisão rigorosa)
- **Overhead inicial:** tempo para setup local ou em cloud (mitigado com automação em Makefile)
- **Risco de corrupção em migração:** se scripts rodarem parcialmente (mitigado com transações, backup pré-migração, testes)

### Reversão

- Restaurar backup do banco SQLite anterior dentro de 2 semanas da migração
- Voltar código para tag anterior do repositório e remover variáveis de ambiente `ERP_DB_URL`
- Reconfigurar `ERP_DB_PATH` para apontar ao SQLite local se necessário rollback completo

## Rastreabilidade

| RQ    | Como a decisão atende | Sensor / Verificação |
|-------|--------------------   |----------------------|
| RQ-01 | PostgreSQL MVCC suporta concorrência sem locks | Teste com `pytest -n auto` (pytest-xdist) contra PG; validar sem deadlocks |
| RQ-02 | SQLAlchemy dialeto `postgresql://` já existe | Rodar `make test` contra PG; verificar se SQL gerado é idêntico |
| RQ-03 | Script de migração com rollback transacional | Executar migração em sandbox, validar row counts e índices pós-migração |
| RQ-04 | Docker Compose + snapshots facilitam rollback | Documentação de passos de reversão + teste mensal |
| RQ-05 | Índices B-tree no PG vs SQLite AUTOINCREMENT | Benchmark de queries lentas pré/pós; target: <10% latência atual |

## Pendências

- [ ] Escolher infraestrutura: PostgreSQL local (development.db → postgres:15 em Docker), cloud (RDS), ou Neon
- [ ] Escrever migrations (Alembic) para schema atual
- [ ] Validar seed data em ambiente de teste
- [ ] Documentar backup/restore procedures
- [ ] Treinar time em ferramentas PostgreSQL (psql, pgAdmin)
- [ ] Agendamento da migração (alinhar com releases)
