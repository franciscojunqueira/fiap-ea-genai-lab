# MCP server do Mini-ERP

Expõe o Mini-ERP como 10 tools MCP (transporte stdio), herdado da v1. Usado no Lab 3.
Escrito com o SDK oficial `mcp` 2.x, em que a antiga classe `FastMCP` se chama `MCPServer`.

```bash
make erp      # terminal 1: o servidor MCP chama o ERP por HTTP
make mcp      # terminal 2: MCP Inspector (porta 6274) para ver e chamar as tools
```

Tools: `listar_produtos`, `buscar_produto`, `consultar_estoque`, `criar_pedido`, `listar_pedidos`,
`consultar_pedido`, `gerar_fatura_simulada`, `consultar_fatura`, `enviar_alerta`, `listar_alertas`.
`ERP_BASE_URL` troca o endereço do ERP (padrão `http://localhost:8000`).
