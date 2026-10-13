#!/usr/bin/env python3
"""Verifica o ambiente dos labs. Executar com `make check` (não importar).

Itens: Python e dependências, Mini-ERP, MCP server, acesso a modelo pela CLI do operador
e presença de `claude`/`codex`. Cada falha diz o que fazer. Código de saída 1 se houver FAIL;
AVISO não reprova.
"""
import asyncio
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = tomllib.loads((RAIZ / "config" / "modelos.toml").read_text(encoding="utf-8"))
# O ERP subiu em 0,35–0,49 s (3 medições, Mac M-series, 12/10/2026). 20 s dão folga para um
# Codespace de 2 cores e para a primeira execução, que compila os .pyc.
ERP_TIMEOUT_S = 20
# `claude auth status` só lê a credencial local; se demorar mais que isto, algo travou.
AUTH_TIMEOUT_S = 15
# As 10 tools herdadas do lab-aula03 da v1. Os labs podem acrescentar tools; estas não podem sumir.
TOOLS_MCP_ORIGINAIS = {
    "listar_produtos", "buscar_produto", "consultar_estoque", "criar_pedido", "listar_pedidos",
    "consultar_pedido", "gerar_fatura_simulada", "consultar_fatura", "enviar_alerta", "listar_alertas",
}
DEPENDENCIAS = ["fastapi", "uvicorn", "sqlalchemy", "pydantic", "httpx", "mcp", "pytest"]

resultados = []


def registrar(estado, item, mensagem=""):
    resultados.append(estado)
    print(f"[{estado:5}] {item}" + (f"\n        {mensagem}" if mensagem else ""), flush=True)


def checar_python():
    if sys.version_info[:2] != (3, 12):
        registrar("FAIL", "Python 3.12", f"Encontrado {sys.version.split()[0]}. Rode pelo make (usa `uv run`), ou recrie o Codespace.")
        return False
    faltando = []
    for nome in DEPENDENCIAS:
        try:
            __import__(nome)
        except ImportError:
            faltando.append(nome)
    if faltando:
        registrar("FAIL", "Dependências Python", f"Faltando: {', '.join(faltando)}. Rode `uv sync` na raiz do repositório.")
        return False
    registrar("PASS", f"Python {sys.version.split()[0]} e dependências")
    return True


def subir_erp(pasta_tmp):
    """Sobe o ERP numa porta livre com banco temporário. Devolve (processo, url) ou (None, mensagem)."""
    import httpx

    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        porta = s.getsockname()[1]
    env = {**os.environ, "ERP_DB_PATH": str(Path(pasta_tmp) / "check.db")}
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--app-dir", str(RAIZ / "mini-erp"),
         "--host", "127.0.0.1", "--port", str(porta), "--log-level", "warning"],
        env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
    url = f"http://127.0.0.1:{porta}"
    limite = time.monotonic() + ERP_TIMEOUT_S
    while time.monotonic() < limite:
        if proc.poll() is not None:
            saida = proc.stdout.read().decode(errors="replace").strip().splitlines()
            return None, f"O processo do ERP terminou. Última linha: {saida[-1] if saida else '(vazia)'}. Rode `make erp` para ver o erro completo."
        try:
            if httpx.get(f"{url}/health", timeout=1).status_code == 200:
                return proc, url
        except httpx.TransportError:
            pass
        time.sleep(0.2)
    proc.terminate()
    return None, f"O ERP não respondeu em {ERP_TIMEOUT_S} s. Rode `make erp` e veja se aparece algum erro."


def checar_erp(url):
    import httpx

    produtos = httpx.get(f"{url}/produtos", timeout=5).json()
    if len(produtos) != 4:
        registrar("FAIL", "Mini-ERP", f"/produtos devolveu {len(produtos)} produtos ativos; esperado 4 (seed). Apague mini-erp/data/mini_erp.db só se tiver mudado o seed.")
        return
    registrar("PASS", "Mini-ERP sobe e responde (/health, /produtos)")


def checar_mcp(url):
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client

    async def listar():
        params = StdioServerParameters(
            command=sys.executable, args=[str(RAIZ / "mcp-server" / "server.py")],
            env={**os.environ, "ERP_BASE_URL": url},
        )
        # O log do servidor vai para o stderr; descartado para não poluir a saída do check.
        async with stdio_client(params, errlog=open(os.devnull, "w")) as (leitura, escrita):
            async with ClientSession(leitura, escrita) as sessao:
                await sessao.initialize()
                tools = (await sessao.list_tools()).tools
                chamada = await sessao.call_tool("consultar_estoque", {"produto_id": 1})
                return tools, chamada

    try:
        tools, chamada = asyncio.run(asyncio.wait_for(listar(), timeout=ERP_TIMEOUT_S))
    except Exception as exc:  # qualquer falha aqui vira mensagem para o aluno
        registrar("FAIL", "MCP server", f"Não conectou por stdio ({type(exc).__name__}: {exc}). Rode `uv run python mcp-server/server.py` e veja o erro.")
        return
    faltando = TOOLS_MCP_ORIGINAIS - {t.name for t in tools}
    if faltando:
        registrar("FAIL", "MCP server", f"Sumiram tools originais: {', '.join(sorted(faltando))}. Confira as edições em mcp-server/server.py.")
    elif chamada.is_error:
        registrar("FAIL", "MCP server", "A tool consultar_estoque falhou contra o ERP. Confira ERP_BASE_URL.")
    else:
        registrar("PASS", f"MCP server lista {len(tools)} tools e consulta o ERP")


def claude_logado():
    try:
        status = subprocess.run(["claude", "auth", "status"], capture_output=True, text=True, timeout=AUTH_TIMEOUT_S)
        return json.loads(status.stdout).get("loggedIn", False)
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        return False


def codex_logado():
    """O Codex guarda a credencial em $CODEX_HOME/auth.json (padrão ~/.codex)."""
    return (Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "auth.json").is_file()


def chamar(comando, timeout):
    """Roda a chamada mínima. Devolve (ok, texto)."""
    try:
        proc = subprocess.run(comando, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"Sem resposta em {timeout} s. Confira a rede do Codespace e tente de novo; persistindo, use o replay do lab."
    return proc.returncode == 0, (proc.stdout or proc.stderr).strip()


def checar_modelo():
    """Acesso a modelo pela CLI do operador (substitui o GitHub Models, aposentado em 30/07/2026)."""
    tem_claude, tem_codex = shutil.which("claude"), shutil.which("codex")
    if not tem_claude and not tem_codex:
        registrar("AVISO", "Agente de código", "Nem `claude` nem `codex` no PATH. Só o operador precisa: ver docs/checklist_operador.md.")
        return
    timeout = CONFIG["check"]["timeout_s"]
    if tem_claude and claude_logado():
        modelo = CONFIG["check"]["claude"]
        ok, saida = chamar(["claude", "-p", "Responda apenas: OK", "--model", modelo, "--output-format", "json",
                            "--tools", "", "--system-prompt", "Responda em uma palavra."], timeout)
        try:
            dados = json.loads(saida)
        except json.JSONDecodeError:
            registrar("FAIL", "Acesso a modelo (Claude Code)", f"Resposta inesperada: {saida[:200]}")
            return
        if dados.get("is_error") or not ok:
            texto = str(dados.get("result", ""))
            dica = "Limite do plano atingido: troque de operador (2º assinante do grupo) ou use o replay." if "limit" in texto.lower() else "Rode `claude` e confira o login."
            registrar("FAIL", "Acesso a modelo (Claude Code)", f"{texto[:200]} — {dica}")
            return
        registrar("PASS", f"Acesso a modelo pelo Claude Code ({modelo}, {dados.get('duration_ms', '?')} ms)")
    elif tem_codex and codex_logado():
        ok, saida = chamar(["codex", "exec", "Responda apenas: OK"], timeout)
        if not ok:
            registrar("FAIL", "Acesso a modelo (Codex)", f"{saida[-200:]} — Rode `codex login --device-auth` e confira o plano.")
            return
        registrar("PASS", "Acesso a modelo pelo Codex")
    else:
        registrar("AVISO", "Agente de código instalado, sem login",
                  "Operador: faça o login (`claude`, ou `codex login --device-auth`) e rode `make check` de novo.")


def main():
    print("== make check ==", flush=True)
    if checar_python():
        with tempfile.TemporaryDirectory() as tmp:
            proc, url = subir_erp(tmp)
            if proc is None:
                registrar("FAIL", "Mini-ERP", url)
                registrar("FAIL", "MCP server", "Não testado: depende do ERP.")
            else:
                try:
                    checar_erp(url)
                    checar_mcp(url)
                finally:
                    proc.terminate()
                    proc.wait(timeout=5)
    checar_modelo()
    falhas, avisos = resultados.count("FAIL"), resultados.count("AVISO")
    print(f"== {'FAIL' if falhas else 'PASS'}: {resultados.count('PASS')} ok, {avisos} aviso(s), {falhas} falha(s) ==")
    return 1 if falhas else 0


if __name__ == "__main__":
    sys.exit(main())
