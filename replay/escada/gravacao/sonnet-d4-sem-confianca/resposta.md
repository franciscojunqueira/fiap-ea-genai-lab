Não consegui criar o ADR. O modo atual (don't ask) negou as chamadas de `Write` e de `Bash`, então nenhum arquivo foi escrito. Também não rodei o validador (`validar_adr.py`), nem o `revisor-adr`, e não reservei o número com `--proximo`. Não vou contornar a negação por outro caminho.

`docs/adr/` está vazio, então o número provável é ADR-001. Isso é inferência minha, não resultado do `--proximo`.

**O que levantei do repositório:**
- `mini-erp/app/db.py` monta `sqlite:///{DB_PATH}` e usa `check_same_thread=False`.
- `ERP_DB_PATH` isola o banco nos testes (`tests/conftest.py`) e no `make check` (`scripts/check.py`).
- O `pyproject.toml` não tem driver PostgreSQL. Segundo o `AGENTS.md`, dependência nova só entra com pedido explícito (`uv add`).
- Você não informou decisores, motivo, volumes nem custo, então não inventei nenhum.

**O que o ADR-001 conteria** (Status Proposto, 2026-10-12):
- **Alternativas:**
  - A1: manter SQLite.
  - A2: PostgreSQL como único banco.
  - A3: PostgreSQL configurável, com SQLite como padrão.
- **Decisão:** A3, condicionada a confirmar o motivo da migração. Se o motivo não se confirmar, cai para A1.
- **Requisitos:**
  - RQ-01: testes e `make check` continuam isolados.
  - RQ-02: dependência nova só com pedido explícito.
  - RQ-03: o contrato HTTP não muda.
  - RQ-04: motivo da migração, a confirmar.
- **Sensores:**
  - RQ-01: `make test` e `make check` passam sem serviço de banco.
  - RQ-02: revisão do diff de `pyproject.toml` e `uv.lock`.
  - RQ-03: testes de fumaça sobre os endpoints, e diff vazio em `mcp-server/`.
  - RQ-04: revisão com o solicitante antes de aprovar.
- **Reversão:** barata enquanto o SQLite for o padrão, porque basta não definir `DATABASE_URL`. Fica mais cara depois que os dados passarem a viver só no PostgreSQL.
- **Pendências:**
  - decisores;
  - motivo da migração;
  - volumes e réplicas;
  - onde o PostgreSQL rodaria e o custo;
  - migração dos dados existentes;
  - ferramenta de versionamento de schema (seria outra dependência);
  - `integrador/legado/` fica fora do escopo.

**Como seguir:** libere `Write` e `Bash` (ou mude o modo de permissão) e eu crio o arquivo, rodo o validador e chamo o `revisor-adr`. Se preferir, me diga o motivo da migração e os decisores. Aí o ADR sai com menos pendências.