"""
MCP Server — Mini-ERP Didático
Expõe tools para consumir a API REST do Mini-ERP (http://localhost:8000).
Transporte: stdio (para uso com Claude Code, Codex ou MCP Inspector).
"""

import json
import os
import sys
import time
import tomllib
from pathlib import Path
from typing import Annotated, Any

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from mcp.types import ToolAnnotations
from pydantic import Field

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


# ── Lab 3: ajuste de estoque com aprovação humana ───────────────────────
# O contrato (nome, descrição, documentação dos parâmetros, anotações) vem de
# labs/lab3/descricoes/<LAB3_VERSAO>.toml; o código abaixo é o adapter e não muda entre as versões.
# A aprovação não está aqui: está no ERP, que recusa executar o que uma pessoa não aprovou.

DESCRICOES = Path(__file__).resolve().parents[1] / "labs" / "lab3" / "descricoes"


def _contrato() -> dict:
    versao = os.environ.get("LAB3_VERSAO", "boa")
    arquivo = DESCRICOES / f"{versao}.toml"
    if not arquivo.exists() or "PREENCHER" in arquivo.read_text(encoding="utf-8"):
        print(f"[mcp-server] {arquivo.name} ausente ou não preenchido; usando boa.toml", file=sys.stderr)
        arquivo = DESCRICOES / "boa.toml"
    return tomllib.loads(arquivo.read_text(encoding="utf-8"))


def _registrar(evento: dict) -> None:
    """Registro das chamadas para o make lab3-comparar (LAB3_LOG); sem a variável, não grava nada."""
    if destino := os.environ.get("LAB3_LOG"):
        with open(destino, "a", encoding="utf-8") as f:
            f.write(json.dumps({"t": round(time.time(), 2), **evento}, ensure_ascii=False) + "\n")


async def _erp_post(path: str, body: dict | None = None) -> dict:
    """POST no ERP; um erro de negócio (4xx) volta ao agente como erro da tool, com o motivo do ERP.

    ToolError, e não ValueError: o SDK esconde do cliente o texto de qualquer outra exceção
    ("Error executing tool ..."), e o agente fica sem saber que falta a aprovação."""
    async with httpx.AsyncClient(base_url=ERP_BASE_URL, timeout=10) as client:
        resp = await client.post(path, json=body)
    if resp.status_code >= 400:
        raise ToolError(f"ERP recusou ({resp.status_code}): {resp.json().get('detail', resp.text)}")
    return resp.json()


def _anotacoes(secao: dict) -> ToolAnnotations | None:
    a = secao.get("anotacoes")
    if not a:
        return None
    return ToolAnnotations(read_only_hint=a.get("somente_leitura"), destructive_hint=a.get("destrutiva"),
                           idempotent_hint=a.get("idempotente"), open_world_hint=False)


def _meta(contrato: dict) -> dict | None:
    # Pede ao Claude Code aprovação a cada chamada, mesmo em modo auto (code.claude.com/docs/en/permissions).
    return {"anthropic/requiresUserInteraction": True} if contrato.get("aprovacao_no_cliente") else None


def registrar_tools_de_ajuste() -> None:
    c = _contrato()
    s, e = c["solicitar"], c["executar"]
    ps, pe = s["parametros"], e["parametros"]

    async def solicitar(produto_id: Annotated[int, Field(description=ps["produto_id"])],
                        quantidade: Annotated[int, Field(description=ps["quantidade"])],
                        motivo: Annotated[str, Field(description=ps["motivo"])] = "") -> str:
        try:
            data = await _erp_post(f"/estoque/{produto_id}/ajustes", {"variacao": quantidade, "motivo": motivo})
        except ToolError as erro:
            _registrar({"tool": s["nome"], "produto_id": produto_id, "quantidade": quantidade, "erro": str(erro)})
            raise
        _registrar({"tool": s["nome"], "produto_id": produto_id, "quantidade": quantidade, "ajuste_id": data["id"]})
        return _fmt(data)

    async def executar(ajuste_id: Annotated[int, Field(description=pe["ajuste_id"])]) -> str:
        try:
            data = await _erp_post(f"/ajustes/{ajuste_id}/executar")
        except ToolError as erro:
            _registrar({"tool": e["nome"], "ajuste_id": ajuste_id, "erro": str(erro)})
            raise
        _registrar({"tool": e["nome"], "ajuste_id": ajuste_id, "status": data["status"]})
        return _fmt(data)

    meta = _meta(c)
    mcp.add_tool(solicitar, name=s["nome"], description=s["descricao"], annotations=_anotacoes(s), meta=meta)
    mcp.add_tool(executar, name=e["nome"], description=e["descricao"], annotations=_anotacoes(e), meta=meta)


registrar_tools_de_ajuste()


# ── Entrypoint ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
