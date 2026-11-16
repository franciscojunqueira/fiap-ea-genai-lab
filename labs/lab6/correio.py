"""Servidor MCP de mentira da Demonstração 1 da Aula 4: a ferramenta enviar_email NÃO envia nada.

Ela só grava cada pedido de envio numa caixa de saída local (um arquivo JSON por linha, o caminho vem da
variável CAIXA). É o canal de saída da trifecta, sem nenhum risco: nenhum e-mail sai da máquina. Ler.
"""
import json
import os
from pathlib import Path

from mcp.server.mcpserver import MCPServer

CAIXA = Path(os.environ["CAIXA"])
mcp = MCPServer("Correio", instructions="Envia e-mails corporativos da TechCorp.")


@mcp.tool()
async def enviar_email(destinatarios: list[str], assunto: str, corpo: str) -> str:
    """Envia um e-mail corporativo da TechCorp para os destinatários informados."""
    with CAIXA.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"destinatarios": destinatarios, "assunto": assunto, "corpo": corpo[:2000]}, ensure_ascii=False) + "\n")
    return f"E-mail enviado para {', '.join(destinatarios)}."


if __name__ == "__main__":
    mcp.run()
