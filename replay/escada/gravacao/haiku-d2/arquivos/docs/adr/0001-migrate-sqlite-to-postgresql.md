# ADR 0001: Migrar o banco de dados do Mini-ERP de SQLite para PostgreSQL

**Status:** Proposed

**Date:** 2026-10-12

**Deciders:** Enterprise Architecture Team

---

## Context

O Mini-ERP atualmente utiliza SQLite como banco de dados, um arquivo local simples e sem dependências externas. Conforme o sistema cresce em complexidade e escala:

- **Concorrência:** SQLite tem limitações com escrita simultânea em múltiplas transações
- **Escalabilidade:** Estudantes trabalhando em paralelo durante labs enfrentam travamentos
- **Produção:** A infraestrutura target (PostgreSQL) é mais adequada para ambientes corporativos reais
- **Aprendizado:** Alunos devem trabalhar com bancos SQL profissionais usados em arquitetura corporativa

Atualmente, a abstração do banco já existe via `ERP_DB_PATH` (variável de ambiente), permitindo trocar o arquivo SQLite. Isso facilita testes com bancos temporários.

---

## Decision

**Migrar o Mini-ERP para usar PostgreSQL como banco de dados principal**, mantendo SQLite como opção para testes e desenvolvimento local quando apropriado.

### Escopo

1. **Banco padrão:** PostgreSQL em produção / CI
2. **Testes:** SQLite em memória ou temporário (sem dependência externa)
3. **Desenvolvimento local:** Opção de PostgreSQL via Docker ou SQLite
4. **Código:** Reutilizar abstração existente; SQLAlchemy/ORM já suporta ambos

---

## Rationale

- **Eliminaria bloqueios:** Múltiplos estudantes rodando labs simultaneamente sem contenção de escrita
- **Realismo corporativo:** Alinha com stacks reais de arquitetura corporativa (PostgreSQL é padrão)
- **Sem reengenharia:** A abstração de DB já existe; é plug-and-play de connection string
- **Testes isolados:** SQLite em memória mantém tests rápidos e sem dependências
- **Dados sintéticos persistem:** Importar dados de testes em PostgreSQL é trivial com SQL dump/restore

---

## Implementation Strategy

### 1. **Preparação**
   - Revisar schema SQLite atual e mapear tipos SQL (se houver incompatibilidades menores)
   - Validar que ORM em uso suporta PostgreSQL sem breaking changes

### 2. **Migração do código**
   - Atualizar `mini-erp/app/main.py` para aceitar conexão PostgreSQL via env vars
   - Criar script `mini-erp/migrate_db.py` para importar dados do SQLite em PostgreSQL
   - Adicionar docker-compose.yml com PostgreSQL (dev/test)

### 3. **CI/CD**
   - Arquivo `.github/workflows/test.yml`: spin up PostgreSQL container, rodar testes
   - Fallback: manter testes com SQLite in-memory quando PostgreSQL não estiver disponível

### 4. **Documentação**
   - Atualizar `mini-erp/README.md` com passos para setup local (Docker + PostgreSQL)
   - Adicionar guia de migração para usuários existentes (backup SQLite → importar para PG)

### 5. **Dados iniciais**
   - Manter seed de dados sintéticos (SQL ou fixtures); importar em ambos os bancos

---

## Consequences

### Positivas
- ✅ Escalabilidade sob concorrência (suporte a múltiplas transações simultâneas)
- ✅ Aprendizado de real-world architectures (PostgreSQL em produção)
- ✅ Sem breaking changes no código (ORM abstrai diferenças)
- ✅ Testes rápidos e isolados com SQLite in-memory

### Negativas / Mitigações
- ❌ **Dependência externa:** PostgreSQL precisa estar rodando
  - **Mitigação:** Docker Compose fornecido; testes usam SQLite
- ❌ **Configuração extra:** Devs locais precisam instalar/rodar PostgreSQL
  - **Mitigação:** Automação via Makefile (`make postgres-up`, `make postgres-down`)
- ❌ **Curva de aprendizado:** Alunos novos precisam aprender administração PostgreSQL
  - **Mitigação:** Documentação; labs cobrem setup gradualmente

---

## Alternatives Considered

### A1: Manter SQLite
**Rejeitado:** Não resolve contenção em escrita; não reflete arquiteturas corporativas.

### A2: Usar MariaDB/MySQL
**Rejeitado:** PostgreSQL é mais robusto para ACID; melhor suporte em stacks cloud modernos (AWS RDS, Azure Database, GCP Cloud SQL favorecem PG).

### A3: Suporte a múltiplos bancos
**Rejeitado:** Aumenta complexidade de testes e manutenção; sem ganho pedagógico significativo.

---

## Success Criteria

- ✓ Testes rodam em CI com PostgreSQL sem falhas
- ✓ Múltiplos estudantes podem rodar labs em paralelo sem travamentos
- ✓ SQLite ainda disponível para testes unitários (sem ext. deps)
- ✓ Documentação clara para setup local
- ✓ Script de migração de dados existentes funciona

---

## Related ADRs

— (primeira decisão arquitetônica registrada)

---

## References

- [SQLAlchemy: Multiple Databases](https://docs.sqlalchemy.org/en/20/faq/connections.html)
- [PostgreSQL vs SQLite](https://www.postgresql.org/docs/current/intro.html)
