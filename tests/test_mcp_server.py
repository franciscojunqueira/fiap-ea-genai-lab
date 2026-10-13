"""Teste de fumaça do MCP server: conecta por stdio, lista as 10 tools e chama uma contra o ERP."""
import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVIDOR = Path(__file__).resolve().parent.parent / "mcp-server" / "server.py"
TOOLS_ESPERADAS = {
    "listar_produtos", "buscar_produto", "consultar_estoque", "criar_pedido", "listar_pedidos",
    "consultar_pedido", "gerar_fatura_simulada", "consultar_fatura", "enviar_alerta", "listar_alertas",
}


async def _sessao(erp_url, acao):
    params = StdioServerParameters(
        command=sys.executable, args=[str(SERVIDOR)], env={**os.environ, "ERP_BASE_URL": erp_url},
    )
    async with stdio_client(params) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()
            return await acao(sessao)


def test_lista_as_10_tools(erp_url):
    resultado = asyncio.run(_sessao(erp_url, lambda s: s.list_tools()))
    assert {t.name for t in resultado.tools} == TOOLS_ESPERADAS


def test_tool_consulta_o_erp(erp_url):
    resultado = asyncio.run(_sessao(erp_url, lambda s: s.call_tool("consultar_estoque", {"produto_id": 2})))
    dados = json.loads(resultado.content[0].text)
    assert dados["produto_nome"] == "Mouse USB" and dados["quantidade"] == 100
