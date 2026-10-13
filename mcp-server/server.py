"""
MCP Server — Mini-ERP Didático
Expõe tools para consumir a API REST do Mini-ERP (http://localhost:8000).
Transporte: stdio (para uso com Claude Code, Codex ou MCP Inspector).
"""

import json
import os
from typing import Any

import httpx
from mcp.server.mcpserver import MCPServer

# Porta padrão do `make erp`; sobrescreva com ERP_BASE_URL se o ERP estiver em outro endereço.
ERP_BASE_URL = os.environ.get("ERP_BASE_URL", "http://localhost:8000")

mcp = MCPServer(
    "Mini-ERP",
    instructions=(
        "Servidor MCP para o Mini-ERP Didático. "
        "Use as tools disponíveis para consultar produtos, estoque, "
        "criar pedidos e gerar faturas."
    ),
)


async def _erp_request(method: str, path: str, body: dict | None = None) -> dict | list:
    """Faz requisição HTTP ao ERP e retorna o JSON de resposta."""
    # 10 s: o ERP é local e responde em milissegundos; acima disso, ele não está de pé.
    async with httpx.AsyncClient(base_url=ERP_BASE_URL, timeout=10) as client:
        if method == "GET":
            resp = await client.get(path)
        else:
            resp = await client.post(path, json=body)
        resp.raise_for_status()
        return resp.json()


def _fmt(data: Any) -> str:
    """Formata dados como JSON legível."""
    return json.dumps(data, ensure_ascii=False, indent=2)


# ── Tools ────────────────────────────────────────────────────────────────


@mcp.tool()
async def listar_produtos() -> str:
    """Lista todos os produtos ativos do ERP.

    Retorna nome, preço, descrição e status de cada produto.
    Use para descobrir quais produtos estão disponíveis antes de criar pedidos.
    """
    data = await _erp_request("GET", "/produtos")
    return _fmt(data)


@mcp.tool()
async def buscar_produto(produto_id: int) -> str:
    """Busca detalhes de um produto específico pelo ID.

    Args:
        produto_id: ID do produto no ERP.
    """
    data = await _erp_request("GET", f"/produtos/{produto_id}")
    return _fmt(data)


@mcp.tool()
async def consultar_estoque(produto_id: int) -> str:
    """Consulta a quantidade em estoque de um produto.

    Args:
        produto_id: ID do produto para verificar estoque.
    """
    data = await _erp_request("GET", f"/estoque/{produto_id}")
    return _fmt(data)


@mcp.tool()
async def criar_pedido(nome_cliente: str, itens: list[dict]) -> str:
    """Cria um novo pedido no ERP.

    Valida estoque disponível e reduz automaticamente as quantidades.

    Args:
        nome_cliente: Nome do cliente que está fazendo o pedido.
        itens: Lista de itens. Cada item é um dict com 'produto_id' (int) e 'quantidade' (int).
              Exemplo: [{"produto_id": 1, "quantidade": 2}, {"produto_id": 3, "quantidade": 1}]
    """
    body = {"nome_cliente": nome_cliente, "itens": itens}
    data = await _erp_request("POST", "/pedidos", body)
    return _fmt(data)


@mcp.tool()
async def listar_pedidos(limit: int = 10) -> str:
    """Lista os pedidos mais recentes do ERP.

    Args:
        limit: Número máximo de pedidos a retornar (padrão: 10).
    """
    data = await _erp_request("GET", f"/pedidos?limit={limit}")
    return _fmt(data)


@mcp.tool()
async def consultar_pedido(pedido_id: int) -> str:
    """Consulta detalhes de um pedido específico, incluindo itens e status.

    Args:
        pedido_id: ID do pedido no ERP.
    """
    data = await _erp_request("GET", f"/pedidos/{pedido_id}")
    return _fmt(data)


@mcp.tool()
async def gerar_fatura_simulada(pedido_id: int) -> str:
    """Gera uma fatura para um pedido existente.

    O pedido deve existir e ainda não ter fatura. Após a geração,
    o status do pedido muda para FATURADO.

    Args:
        pedido_id: ID do pedido para faturar.
    """
    data = await _erp_request("POST", f"/pedidos/{pedido_id}/fatura")
    return _fmt(data)


@mcp.tool()
async def consultar_fatura(fatura_id: int) -> str:
    """Consulta detalhes de uma fatura pelo ID.

    Args:
        fatura_id: ID da fatura no ERP.
    """
    data = await _erp_request("GET", f"/faturas/{fatura_id}")
    return _fmt(data)


@mcp.tool()
async def enviar_alerta(tipo: str, mensagem: str, detalhes: dict | None = None) -> str:
    """Envia um alerta ao ERP (ex: estoque insuficiente, erro de faturamento).

    Args:
        tipo: Tipo do alerta (ex: 'estoque_insuficiente', 'erro_faturamento').
        mensagem: Descrição do alerta.
        detalhes: Dados adicionais opcionais (ex: {"produto_id": 1, "estoque_atual": 0}).
    """
    body = {"tipo": tipo, "mensagem": mensagem}
    if detalhes:
        body["detalhes"] = detalhes
    data = await _erp_request("POST", "/alertas", body)
    return _fmt(data)


@mcp.tool()
async def listar_alertas() -> str:
    """Lista os últimos 20 alertas registrados no ERP (mais recentes primeiro)."""
    data = await _erp_request("GET", "/alertas")
    return _fmt(data)


# ── Entrypoint ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
