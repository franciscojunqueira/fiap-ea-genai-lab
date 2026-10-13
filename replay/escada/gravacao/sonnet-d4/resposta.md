O ADR está em `docs/adr/ADR-001-migrar-banco-do-mini-erp-para-postgresql.md`, com status Proposto. Ele passa no validador e o `revisor-adr` conferiu os fatos. Depois da revisão corrigi os pontos que ele marcou, mas não pedi uma segunda revisão. Só rodei o validador de novo, que deu PASS.

Correções feitas:
- **Docker:** eu tinha escrito que o repositório não tem Docker. Ele tem um Dockerfile de devcontainer em `.devcontainer/imagem/`. Não tem compose nem serviço de banco, e o texto agora diz isso.
- **`Numeric`:** os modelos usam `Float`, não `Numeric`. O texto agora cita `Float`.
- **Sensor de RQ-05:** `make lab1-check` e `make lab3-check` são placeholders que sempre saem com erro, então não servem de sensor. A tabela de rastreabilidade avisa isso.
- **Sem fonte:** afirmações técnicas gerais, estimativas e propostas passaram a vir marcadas como tais. RQ-05 agora consta como premissa do autor, a confirmar. O teste contra PostgreSQL ficou descrito como trabalho futuro.

As "Pendências" continuam abertas: motivo da migração, decisores, como provisionar o PostgreSQL, autorização para o `uv add` do driver e se algum dado do `mini_erp.db` precisa ser preservado. Não mexi em código nem em dependências.