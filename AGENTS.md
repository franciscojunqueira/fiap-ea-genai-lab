# AGENTS.md

Repositório dos labs do curso Enterprise Architecture with Generative AI (FIAP). Todos os dados são sintéticos.

## Comandos

- Python 3.12 gerenciado pelo `uv`. Rode tudo com `uv run …` ou pelo `make`; não use `pip install`.
- `make check`: verifica o ambiente. `make test`: testes de fumaça. `make erp`: sobe o Mini-ERP na porta 8000.
- Cada lab tem `make labN` e `make labN-check` (PASS/FAIL). As instruções do lab estão em `labs/labN/README.md`.
- Projeto integrador: `integrador/README.md`. Entregas conferidas por `make er-check`, `make checkpoint-check` e `make pacote-check`.

## Estrutura que não é óbvia

- `mini-erp/` e `mcp-server/` têm hífen, então não são pacotes Python: o ERP sobe com `uvicorn app.main:app --app-dir mini-erp`.
- `mcp-server/server.py` chama o ERP por HTTP (`ERP_BASE_URL`, padrão `http://localhost:8000`).
- `ERP_DB_PATH` troca o banco SQLite; os testes usam um banco temporário.
- `integrador/legado/` é um legado mantido como está, de propósito: não corrija nem refatore sem pedido explícito. Para executá-lo, use `make legado` (roda numa pasta isolada), não `python -m sgc`.

## Convenções

- Decisões de arquitetura viram ADR em `docs/adr/`, com a skill `escrevendo-adrs`.
- Dependência nova só com pedido explícito do usuário (`uv add`).
- Nunca grave chaves ou tokens em arquivo; use variáveis de ambiente.
