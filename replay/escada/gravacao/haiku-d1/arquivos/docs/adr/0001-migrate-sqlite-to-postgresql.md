# ADR 0001: Migração de SQLite para PostgreSQL

**Data:** 2026-10-12  
**Status:** Proposto  
**Autor:** Francisco Junqueira

## Problema

O Mini-ERP atual utiliza SQLite como banco de dados, o que apresenta limitações para o crescimento e operação da plataforma em ambiente de produção:

- **Concorrência limitada**: SQLite não foi projetado para múltiplos acessos simultâneos, podendo causar locks de escrita
- **Escalabilidade**: Difícil escalar horizontalmente ou aplicar sharding
- **Recursos avançados**: Falta suporte a transações ACID robustas em cenários de alta concorrência
- **Operações de backup**: Requer parar a aplicação ou usar backup a quente complexo
- **Monitoramento**: Limitado em capacidades de monitoramento e auditoria
- **Performance**: Em datasets maiores, a performance degrada significativamente

Esses fatores impedem a transição do Mini-ERP para produção em cenários com múltiplos usuários simultâneos.

## Contexto

- O Mini-ERP está em fase de crescimento, com previsão de múltiplos usuários concorrentes
- O código atual está estruturado com abstrações de acesso a dados que facilitam a migração
- A equipe tem experiência com PostgreSQL
- Infraestrutura de produção será hospedada em cloud (AWS/Azure/GCP)

## Decisão

**Migrar de SQLite para PostgreSQL como banco de dados principal do Mini-ERP.**

### Justificativa

PostgreSQL oferece:

1. **Concorrência robusta**: MVCC (Multi-Version Concurrency Control) permite leituras e escritas simultâneas
2. **Escalabilidade**: Suporta datasets de qualquer tamanho e múltiplas réplicas
3. **Reliability**: Transações ACID verdadeiras, WAL (Write-Ahead Logging) para durabilidade
4. **Recursos avançados**: JSON/JSONB, Full-Text Search, Extensões customizadas
5. **Operações**: Backup/restore, replicação, particionamento nativos
6. **Monitoramento**: Ferramentas maduras e integração com observabilidade
7. **Custo**: Open-source, sem licensing fees

## Consequências

### Positivas ✓

- Aplicação pronta para produção com múltiplos usuários simultâneos
- Melhor performance em operações complexas e datasets maiores
- Capacidade de implementar replicação e alta disponibilidade
- Suporte a features avançadas (JSON, FTS, etc.)
- Mais opções de backup, restore e disaster recovery
- Melhor experiência operacional (monitoramento, logs, etc.)

### Negativas ✗

- Aumento de complexidade operacional (nova ferramenta para manter)
- Custo de infraestrutura (PostgreSQL requer mais recursos que SQLite)
- Esforço de migração:
  - Adaptação do código de acesso a dados
  - Migração de dados existentes
  - Testes abrangentes
  - Downtime durante migração (planejado)
- Curva de aprendizado para operação e tuning
- Dependência de serviço gerenciado ou self-hosted

## Plano de Execução

### Fase 1: Preparação
- [ ] Audit do schema atual e identificação de incompatibilidades
- [ ] Setup de PostgreSQL (local para dev, staging, produção)
- [ ] Criação de scripts de migração de dados

### Fase 2: Implementação
- [ ] Atualizar camada de acesso a dados (se necessário)
- [ ] Criar schema no PostgreSQL com same estrutura
- [ ] Implementar migração de dados com validação
- [ ] Testes em staging com dados reais

### Fase 3: Cutover
- [ ] Backup final do SQLite
- [ ] Migração de dados em produção
- [ ] Validação de integridade
- [ ] Switchover para PostgreSQL
- [ ] Monitoramento pós-migração

### Fase 4: Cleanup
- [ ] Arquivamento do banco SQLite
- [ ] Documentação de lições aprendidas
- [ ] Otimizações baseadas em telemetria

## Alternativas Consideradas

### 1. Manter SQLite com Read Replicas
**Descartado**: SQLite não suporta replicação nativa de forma confiável

### 2. Migrar para MySQL/MariaDB
**Descartado**: PostgreSQL é mais robusto para casos de uso similares; MySQL/MariaDB têm complexidade operacional similar com menos features avançadas

### 3. Cloud Database Service (AWS RDS, Azure Database, GCP Cloud SQL)
**Recomendado como opção complementar**: Usar PostgreSQL gerenciado em vez de self-hosted para reduzir carga operacional. Aplicável na Fase 1.

### 4. Migração Gradual com Dual-Write
**Considerado**: Escrever em ambos os bancos durante transição. Aumenta complexidade e risco. Usar apenas se downtime for absolutamente inaceitável.

## Métricas de Sucesso

- ✓ Migração concluída com zero perda de dados
- ✓ Performance igual ou superior (p95 latency < baseline SQLite)
- ✓ Suporte a 100+ usuários concorrentes sem degradação
- ✓ RTO (Recovery Time Objective) < 1 hora
- ✓ RPO (Recovery Point Objective) < 5 minutos

## Riscos e Mitigação

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|--------|-----------|
| Perda de dados durante migração | Baixa | Crítico | Backups antes/depois, validação de integridade, teste em staging |
| Downtime maior que esperado | Média | Alto | Plano detalhado, rollback procedure, comunicação aos stakeholders |
| Performance pior que SQLite | Baixa | Alto | Profiling em staging, índices otimizados, tuning de parameters |
| Incompatibilidade de driver/ORM | Baixa | Médio | Testes com drivers atuais, vendor verification |

## Referências

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [SQLite vs PostgreSQL](https://www.postgresql.org/about/featurematrix/)
- [AWS Database Migration Best Practices](https://docs.aws.amazon.com/dms/)
- [ADR: Architecture Decision Records](https://adr.github.io/)

## Próximos Passos

1. Obter aprovação dos stakeholders
2. Iniciar Fase 1 (Preparação)
3. Estimar esforço com precisão após audit completo
4. Agendar kickoff da migração
