✅ **ADR criado:** `docs/adr/0001-migrate-sqlite-to-postgresql.md`

O ADR documenta a decisão de migrar o Mini-ERP de SQLite para PostgreSQL, com:

- **Contexto:** Limitações de SQLite para concorrência e escalabilidade
- **Decisão:** PostgreSQL em produção/CI, SQLite para testes in-memory
- **Rationale:** Elimina contenção, alinha com arquiteturas corporativas reais, reutiliza abstração de DB existente
- **Implementação:** Setup com Docker, script de migração de dados, CI/CD com PostgreSQL
- **Consequências:** Escalabilidade vs. dependência externa (mitigada com Docker + Makefile)

Você pode agora fazer `git add docs/adr/0001-migrate-sqlite-to-postgresql.md && git commit` para registrar a decisão no repositório.