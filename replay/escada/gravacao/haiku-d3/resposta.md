✅ **ADR criado e validado com sucesso!**

Criei o **ADR-001: Migração do banco de dados SQLite para PostgreSQL no Mini-ERP** com:

- **3 alternativas reais:** manter SQLite, migrar para PostgreSQL (escolhida) e migrar para MySQL
- **5 requisitos** ligados a concorrência, compatibilidade ORM, zero-downtime, reversão e latência
- **Justificativa clara:** PostgreSQL é o padrão para Python/FastAPI e habilita arquitetura multi-instância
- **Rastreabilidade:** cada requisito vinculado a um sensor/teste de verificação
- **Pendências registradas:** infraestrutura, migrations com Alembic, seed data, backup/restore, treinamento

O arquivo está em `/private/tmp/tmprx8q1xz0/repo/docs/adr/ADR-001-sqlite-para-postgresql.md` e passou na validação com **PASS**.