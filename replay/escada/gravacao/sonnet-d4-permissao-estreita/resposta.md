Não escrevi o ADR. A skill exige reservar o número com `validar_adr.py --proximo docs/adr` e validar o arquivo com o mesmo script, e o Bash está negado neste modo. Sem ele não consigo listar `docs/adr/` (o `Read` dá `EISDIR` e o subagente também não tem como listar). Também não posso garantir o PASS do validador, que é o passo 4 da skill. Prefiro não chutar um número que pode colidir com um ADR existente.

**O que já levantei, com fonte**
- `mini-erp/app/db.py`: o banco é SQLite em arquivo, e o `ERP_DB_PATH` isola testes e `make check`. O engine usa `check_same_thread=False`.
- `mini-erp/app/main.py`: o `lifespan` roda `create_all` e `seed_db` ao subir. Não há migrations.
- `mini-erp/app/models.py`: valores monetários são `Float` (`Produto.preco`, `Pedido.total`, `ItemPedido.preco_unitario` e `subtotal`, `Fatura.valor_total`). `DateTime` usa `datetime.now`, sem timezone. Os status são `String` livre. Há FKs e `unique` em `Estoque.produto_id` e `Fatura.pedido_id`.
- `pyproject.toml`: não há driver PostgreSQL (`psycopg`). A regra do AGENTS.md diz que dependência nova só entra com pedido explícito.
- Não li o devcontainer, os testes nem os labs, então não sei o que mais depende de `ERP_DB_PATH`.

**Como seguir**
1. **Liberar o Bash:** ele roda só o validador, o `--proximo` e um `ls`/`grep` de leitura. Com isso eu reservo o número, escrevo o ADR, valido e chamo o `revisor-adr`.
2. **Informar o número:** você me diz o próximo número de ADR, e eu escrevo, mas sem o PASS do validador. Neste caso o `revisor-adr` ainda confere os fatos, e você roda o validador depois.

**Perguntas antes de escrever**
- A decisão já foi aprovada ou o status inicial é `Proposto`? Vou usar `Proposto`, salvo se você disser o contrário.
- Qual é o motivo da migração (concorrência, várias réplicas, produção)? Sem isso as Pendências ficam abertas e o ADR sai fraco.
- Quem são os decisores?

Vou listar o que não tenho como "a confirmar": volumes, custo do serviço e prazo.