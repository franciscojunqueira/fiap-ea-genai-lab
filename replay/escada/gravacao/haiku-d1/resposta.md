Criei um **ADR completo e profissional** para a migração de SQLite para PostgreSQL. Aqui está o que foi documentado:

## 📋 Arquivos Criados

1. **`docs/adr/0001-migrate-sqlite-to-postgresql.md`** — ADR detalhado com:
   - **Problema**: Limitações do SQLite (concorrência, escalabilidade, recursos)
   - **Decisão**: Migração para PostgreSQL
   - **Contexto**: Justificativas baseadas em crescimento e maturidade do Mini-ERP
   - **Consequências**: Ganhos e desafios (operacional, custo, complexidade)
   - **Alternativas**: MySQL, serviços cloud, dual-write
   - **Plano de execução**: 4 fases (Preparação, Implementação, Cutover, Cleanup)
   - **Métricas de sucesso**: Zero perda de dados, performance, suporte a 100+ usuários
   - **Gestão de riscos**: Tabela com mitigações para os principais riscos

2. **`docs/adr/README.md`** — Estrutura de governança de ADRs:
   - Explica o propósito e benefícios dos ADRs
   - Define os status possíveis
   - Documenta o processo de criação e revisão
   - Fornece template padrão para novos ADRs

## 🎯 Próximos Passos

Para finalizar, você pode:
```bash
cd /private/tmp/tmptl75z9vw/vazia
git add docs/
git commit -m "docs: Add ADR 0001 - Migrate SQLite to PostgreSQL"
```

O ADR está pronto para ser revisado pela equipe, discutido e aprovado antes de iniciar a implementação da migração!