#!/usr/bin/env python3
"""Prepara o Lab 3 (make lab3). Executar.

Copia o contrato do grupo (descricoes/grupo.toml) e o contrato.md sem sobrescrever o que já existe e
registra o servidor MCP do Mini-ERP para o Claude Code no .mcp.json da raiz (com o contrato do grupo).
Pode rodar de novo sem estragar nada.
"""
import json
import shutil
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))
import cli_modelo  # noqa: E402

COPIAS = {"modelos/grupo.toml": "descricoes/grupo.toml", "modelos/contrato.md": "contrato.md"}
# Caminhos relativos: o Claude Code abre o servidor a partir da raiz do repositório, onde o operador o inicia.
SERVIDOR = {"command": ".venv/bin/python", "args": ["mcp-server/server.py"], "env": {"LAB3_VERSAO": "grupo"}}


def main():
    for origem, destino in COPIAS.items():
        alvo = LAB / destino
        if alvo.exists():
            print(f"  mantido   labs/lab3/{destino} (já existia)")
            continue
        shutil.copy(LAB / origem, alvo)
        print(f"  criado    labs/lab3/{destino}")
    mcp_json = RAIZ / ".mcp.json"
    config = json.loads(mcp_json.read_text(encoding="utf-8")) if mcp_json.exists() else {}
    if "minierp" in config.get("mcpServers", {}):
        print("  mantido   .mcp.json (o servidor minierp já está lá)")
    else:
        config.setdefault("mcpServers", {})["minierp"] = SERVIDOR
        mcp_json.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("  criado    .mcp.json com o servidor minierp (contrato do grupo; até ele ser preenchido, vale o boa.toml)")
    if problema := cli_modelo.disponivel("claude"):
        print(f"\nAviso: {problema}")
    print("\nPróximo passo: `make erp` num segundo terminal e `make lab3-comparar VERSAO=ruim` (passo 2 de labs/lab3/README.md).")


if __name__ == "__main__":
    main()
