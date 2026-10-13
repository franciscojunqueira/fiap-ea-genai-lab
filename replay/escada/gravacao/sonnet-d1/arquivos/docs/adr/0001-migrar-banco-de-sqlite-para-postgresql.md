# ADR-0001: Migrar o banco de dados do Mini-ERP de SQLite para PostgreSQL

- **Status:** Proposto
- **Data:** 2026-10-12
- **Autor:** Francisco Junqueira
- **Decisores:** a definir

> Nota: o repositório ainda não tem código nem métricas. Os pontos marcados com
> **[confirmar]** são premissas a validar antes de mudar o status para "Aceito".

## Contexto

O Mini-ERP usa SQLite como banco de dados. O SQLite atendeu bem na fase inicial:
não exige servidor, a configuração é mínima e o banco é um único arquivo.

À medida que o sistema ganha usuários e módulos (vendas, estoque, financeiro),
as limitações passam a pesar **[confirmar]**:

- **Concorrência de escrita:** o SQLite permite um único escritor por vez
  (mesmo em modo WAL). Com vários usuários lançando pedidos, movimentando
  estoque e emitindo notas ao mesmo tempo, aumentam os erros `database is locked`.
- **Acesso por rede e múltiplas instâncias:** o banco é um arquivo local. Isso
  impede escalar a aplicação horizontalmente ou separar aplicação e banco.
- **Integridade e tipos:** a tipagem é flexível (type affinity), o que permite
  gravar dados inconsistentes, e o suporte a `ALTER TABLE` é limitado. Para um
  ERP, que lida com valores monetários e datas, isso é um risco.
- **Operação:** não há replicação nativa, backup online com PITR, controle
  granular de permissões nem observabilidade comparável à de um SGBD
  cliente-servidor.
- **Recursos analíticos e de busca:** relatórios gerenciais e busca textual
  exigem recursos que o SQLite cobre apenas parcialmente.

## Decisão

Migrar o banco de dados de produção do Mini-ERP para **PostgreSQL** (versão
estável suportada mais recente, a confirmar com a infraestrutura).

Pontos da decisão:

1. PostgreSQL passa a ser o banco em produção, homologação e desenvolvimento
   (via contêiner), para evitar divergência de comportamento entre ambientes.
   SQLite deixa de ser suportado como banco da aplicação.
2. A migração dos dados será feita com janela de manutenção planejada, com
   validação por contagem de registros e totais por tabela.
3. O esquema será versionado com uma ferramenta de migrations (a que o projeto
   já usa, ou Alembic/Flyway/equivalente à stack **[confirmar]**).
4. Valores monetários usarão `NUMERIC(p, s)`, datas com fuso usarão
   `TIMESTAMPTZ`, e chaves primárias seguirão o padrão já usado (`BIGINT
   GENERATED ... AS IDENTITY` ou UUID).

## Alternativas consideradas

| Alternativa | Prós | Contras |
|---|---|---|
| **Manter SQLite** (com WAL e ajustes) | Sem custo de migração, zero operação | Mantém o limite de escrita e de escala; não resolve rede, replicação nem permissões |
| **SQLite replicado (LiteFS, Litestream, libSQL)** | Mantém o código atual, dá backup contínuo | Ecossistema menos maduro, ainda com um único escritor, pouco conhecido pela equipe |
| **MySQL/MariaDB** | Amplamente disponível, boa operação | Tipos e recursos SQL mais limitados que o PostgreSQL (DDL transacional, JSONB, constraints), sem ganho que justifique |
| **PostgreSQL gerenciado (RDS, Cloud SQL etc.)** | Backups, HA e patches delegados | Custo recorrente e dependência do provedor. **É uma opção de hospedagem do PostgreSQL, não uma alternativa a ele**; fica para decisão separada |
| **PostgreSQL autogerenciado** | Controle total, custo menor | Exige operação própria (backup, upgrades, monitoramento) |

PostgreSQL foi escolhido por oferecer concorrência baseada em MVCC, integridade
forte, DDL transacional, replicação e PITR nativos, extensões (`pg_trgm`,
`pgcrypto`) e um ecossistema maduro, sem custo de licença.

## Consequências

### Positivas

- Múltiplos escritores simultâneos sem bloqueio global.
- Aplicação e banco podem escalar de forma independente.
- Integridade mais forte (tipos estritos, constraints, transações DDL).
- Backup online, replicação e recuperação a um ponto no tempo.
- Controle de acesso por papéis e auditoria melhor.
- Base sólida para relatórios, busca e crescimento futuro.

### Negativas e riscos

- **Complexidade operacional:** passa a existir um servidor para manter,
  monitorar, fazer backup e atualizar.
- **Custo:** infraestrutura adicional (ou serviço gerenciado).
- **Diferenças de dialeto SQL:** `AUTOINCREMENT` vs. identity/sequences,
  `INSERT OR REPLACE` vs. `ON CONFLICT`, funções de data, comparação
  case-sensitive de strings e booleanos nativos. Queries SQL cruas precisam de
  revisão.
- **Dados legados inconsistentes:** a tipagem frouxa do SQLite pode ter deixado
  valores que o PostgreSQL rejeita (ex.: texto em coluna numérica, datas fora
  do formato). A migração pode falhar sem limpeza prévia.
- **Janela de indisponibilidade** durante a virada.
- **Testes:** suítes que usavam SQLite em memória precisarão rodar contra
  PostgreSQL (mais lentas), por exemplo com contêineres efêmeros.

## Plano de migração (alto nível)

1. **Inventário:** listar tabelas, queries SQL cruas, uso de funções
   específicas do SQLite e volume de dados.
2. **Ambiente:** subir PostgreSQL em desenvolvimento (Docker Compose) e CI.
3. **Esquema:** gerar o esquema inicial no PostgreSQL via migrations e
   ajustar tipos (dinheiro, datas, booleanos, chaves).
4. **Código:** adaptar a camada de acesso a dados e as queries incompatíveis;
   rodar a suíte de testes contra PostgreSQL.
5. **Dados:** escrever script de carga (por exemplo `pgloader` ou ETL próprio),
   com limpeza e validação (contagens, somatórios, chaves estrangeiras),
   e reajustar as sequences após a carga.
6. **Ensaio:** executar a migração completa em homologação com cópia dos
   dados de produção e medir o tempo.
7. **Virada:** janela de manutenção, backup final do SQLite, carga, validação
   e troca da configuração.
8. **Pós-virada:** monitorar por alguns dias; manter o arquivo SQLite
   somente leitura por um período definido antes de arquivá-lo.

## Plano de reversão

Até a virada ser confirmada, o SQLite permanece como fonte da verdade. Se a
validação pós-carga falhar, a aplicação volta a apontar para o arquivo SQLite
(backup congelado antes da janela). Depois que houver escrita no PostgreSQL,
a reversão exigiria exportar os dados novos de volta, portanto o ponto de
não retorno deve ser definido explicitamente.

## Critérios de sucesso

- Nenhuma divergência nas validações de contagem e totais por tabela.
- Zero erros de bloqueio de banco sob a carga concorrente esperada.
- Suíte de testes passando contra PostgreSQL em CI.
- Backup automatizado e restauração testada.
- Indisponibilidade dentro da janela acordada.

## Questões em aberto

- Hospedagem: gerenciada ou autogerenciada? (ADR separado)
- Volume atual de dados e tempo estimado de carga.
- Quantas queries SQL cruas existem e quais são específicas do SQLite?
- Haverá necessidade de multi-tenant (schema ou linha por cliente)?
- Quem será responsável pela operação do banco?
