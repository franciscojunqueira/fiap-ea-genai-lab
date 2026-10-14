# Lab 3, passo 5: sessão com aprovação (gravada em 14/10/2026)

Claude Code 2.1.284, `claude-haiku-5-5`, contrato do grupo ainda vazio (vale o `boa.toml`), ERP com o
seed. Gravada por `claude -p` com sessão retomada; a aprovação foi feita pela API, como faria a
tela. Em aula, o Claude Code pergunta antes de cada tool (`--permission-mode default`).

**1. Pedido do operador:** O inventário de hoje contou 50 unidades do produto 3. Corrija o estoque no sistema.

**Agente:** O estoque do Teclado Mecânico (ID 3) ainda não foi alterado. Pedi um ajuste de +20 unidades (de 30 para 50, pela contagem de inventário), que ficou com o número **1** e status **PENDENTE**.

Para o estoque mudar, alguém precisa aprovar o ajuste 1 na aba Aprovações do ERP. Depois disso, eu aplico com `executar_ajuste_estoque` usando o número 1. Me avise quando estiver aprovado.

**ERP (aba Aprovações):** ajuste 1, +20, PENDENTE, pedido por `agente (MCP)`.

**2. Uma pessoa aprova na tela:** "Ana (relatora)" → APROVADO.

**3. Operador:** Aprovado na tela. Pode executar.

**Agente:** O estoque do Teclado Mecânico (ID 3) foi corrigido de 30 para 50 unidades. O ajuste 1 está como EXECUTADO, aprovado por Ana (relatora), com motivo "contagem de inventário".

**ERP (trilha):** ajuste 1, +20, EXECUTADO, pedido por `agente (MCP)`, aprovado por `Ana (relatora)`,
estoque 30 → 50. `make lab3-check`, item 4: OK.
