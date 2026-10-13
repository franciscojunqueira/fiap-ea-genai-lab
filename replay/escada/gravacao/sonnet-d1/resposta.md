Criei o ADR em `docs/adr/0001-migrar-banco-de-sqlite-para-postgresql.md`, com status **Proposto**. Não fiz commit.

O repositório estava vazio, sem código nem métricas do Mini-ERP. Por isso o contexto e os riscos são genéricos, e deixei as premissas marcadas com **[confirmar]**. Os pontos a confirmar são:
- os problemas reais de concorrência e escala;
- a stack e a ferramenta de migrations;
- a hospedagem (gerenciada ou própria);
- o volume de dados e o tempo estimado de carga;
- a quantidade de SQL cru e de funções específicas do SQLite;
- quem opera o banco.

O documento tem estas seções:
- contexto e decisão;
- alternativas consideradas: manter o SQLite, SQLite replicado, MySQL, PostgreSQL gerenciado e PostgreSQL próprio;
- consequências positivas e negativas;
- plano de migração em 8 etapas, plano de reversão e critérios de sucesso;
- questões em aberto.

Se você me passar os dados reais do projeto (stack, volume, número de usuários, hospedagem), eu os incluo e removo os marcadores.