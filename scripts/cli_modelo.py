"""Chamada a modelo pela CLI do operador, em modo não interativo. Ler (é importado pelos Labs 2 e 3).

Sem chave de API: usa o login do plano do operador (`claude -p`; `codex exec` como alternativa).
Roda sempre numa pasta temporária vazia, para o agente não carregar o AGENTS.md, as skills nem o
.mcp.json do repositório: a chamada mede o pipeline, não o harness do repositório.
"""
import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Resposta:
    texto: str = ""
    estruturado: dict | None = None
    tokens_entrada: int = 0   # entrada nova + lida do cache + gravada no cache
    tokens_novos: int = 0     # entrada sem cache (preço cheio)
    tokens_cache: int = 0     # lidos do cache (0,1× o preço no Haiku 5.5; 0,05× no Sonnet 5.5: Radar)
    tokens_saida: int = 0
    uso_por_modelo: dict = field(default_factory=dict)   # modelUsage do Claude Code, para o custo a preço de API
    duracao_s: float = 0.0
    turnos: int = 0
    modelos: list = field(default_factory=list)
    erro: str = ""


def disponivel(cli="claude"):
    """Mensagem acionável se a CLI não estiver instalada; vazio se estiver."""
    if shutil.which(cli):
        return ""
    if cli == "codex":
        return "`codex` não está no PATH. Veja docs/guia_codex.md."
    return "`claude` não está no PATH. O operador abre o Codespace e faz o login (docs/checklist_operador.md)."


def chamar(prompt, *, sistema, modelo, ferramentas="", pasta=None, esquema=None, max_turnos=None,
           mcp_config=None, permitidas=None, cli="claude", timeout_s=300):
    """Uma pergunta, uma resposta. Nunca levanta exceção: o erro volta em Resposta.erro."""
    with tempfile.TemporaryDirectory() as vazia:
        cwd = pasta or vazia
        if cli == "codex":
            return _codex(prompt, sistema, modelo, cwd, esquema, timeout_s, mcp_config)
        # --restricted prende as ferramentas de arquivo à pasta de trabalho: sem ele, a busca agêntica lê
        # qualquer caminho do disco (medido em 14/10/2026: leu um documento Regulado fora da pasta).
        cmd = ["claude", "-p", prompt, "--model", modelo, "--system-prompt", sistema, "--tools", ferramentas,
               "--output-format", "json", "--no-session-persistence", "--strict-mcp-config", "--restricted"]
        if mcp_config:
            cmd += ["--mcp-config", str(mcp_config)]
        if permitidas:
            cmd += ["--allowedTools", ",".join(permitidas)]
        if max_turnos:
            cmd += ["--max-turns", str(max_turnos)]
        if esquema:
            cmd += ["--json-schema", json.dumps(esquema)]
        inicio = time.monotonic()
        try:
            proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout_s,
                                  stdin=subprocess.DEVNULL)
        except subprocess.TimeoutExpired:
            return Resposta(erro=f"sem resposta em {timeout_s} s", duracao_s=timeout_s)
        duracao = time.monotonic() - inicio
    try:
        dados = json.loads(proc.stdout)
    except json.JSONDecodeError:
        texto = (proc.stderr or proc.stdout).strip()[-300:]
        dica = " Limite do plano atingido: troque de operador ou use o replay." if "limit" in texto.lower() else ""
        return Resposta(erro=f"resposta inesperada do Claude Code: {texto}{dica}", duracao_s=duracao)
    uso = dados.get("usage") or {}
    return Resposta(
        texto=str(dados.get("result") or ""),
        estruturado=dados.get("structured_output"),
        tokens_entrada=uso.get("input_tokens", 0) + uso.get("cache_read_input_tokens", 0)
        + uso.get("cache_creation_input_tokens", 0),
        tokens_novos=uso.get("input_tokens", 0) + uso.get("cache_creation_input_tokens", 0),
        tokens_cache=uso.get("cache_read_input_tokens", 0),
        tokens_saida=uso.get("output_tokens", 0),
        uso_por_modelo=dados.get("modelUsage") or {},
        duracao_s=round(duracao, 1),
        turnos=dados.get("num_turns") or 0,
        modelos=sorted((dados.get("modelUsage") or {}).keys()),
        erro="" if not dados.get("is_error") else str(dados.get("result") or dados.get("subtype"))[:300],
    )


def custo_api(uso_por_modelo, precos):
    """US$ a preço de API, pela tabela [precos] do config/modelos.toml; None se faltar o preço de algum modelo."""
    total = 0.0
    for modelo, u in uso_por_modelo.items():
        p = precos.get(modelo)
        if not p:
            return None
        total += (u.get("inputTokens", 0) * p["entrada"] + u.get("cacheCreationInputTokens", 0) * p["gravacao_cache"]
                  + u.get("cacheReadInputTokens", 0) * p["leitura_cache"] + u.get("outputTokens", 0) * p["saida"]) / 1e6
    return total


def _codex_mcp(mcp_config):
    """Servidores do --mcp-config do Claude Code viram sobrescritas `-c mcp_servers.<nome>...` do Codex."""
    if not mcp_config:
        return []
    args = []
    for nome, srv in json.loads(Path(mcp_config).read_text(encoding="utf-8"))["mcpServers"].items():
        env = ", ".join(f"{k} = {json.dumps(v)}" for k, v in srv.get("env", {}).items())
        args += ["-c", f"mcp_servers.{nome}.command={json.dumps(srv['command'])}",
                 "-c", f"mcp_servers.{nome}.args={json.dumps(srv.get('args', []))}",
                 "-c", f"mcp_servers.{nome}.env={{{env}}}",
                 "-c", f"mcp_servers.{nome}.default_tools_approval_mode=\"approve\""]
    return args


def _codex(prompt, sistema, modelo, cwd, esquema, timeout_s, mcp_config=None):
    """Caminho Codex: NÃO TESTADO com conta ChatGPT (13/10/2026). Sem sandbox pelo mesmo motivo do Lab 1."""
    cmd = ["codex", "exec", "--json", "--skip-git-repo-check", "--sandbox", "danger-full-access", "-C", cwd,
           *_codex_mcp(mcp_config)]
    if modelo and modelo not in ("padrão", "padrao"):
        cmd += ["-m", modelo]
    arquivo_esquema = None
    if esquema:
        arquivo_esquema = Path(cwd) / ".esquema.json"
        arquivo_esquema.write_text(json.dumps(esquema), encoding="utf-8")
        cmd += ["--output-schema", str(arquivo_esquema)]
    inicio = time.monotonic()
    try:
        proc = subprocess.run(cmd + [f"{sistema}\n\n{prompt}"], capture_output=True, text=True, timeout=timeout_s,
                              stdin=subprocess.DEVNULL, env={**os.environ})
    except subprocess.TimeoutExpired:
        return Resposta(erro=f"sem resposta em {timeout_s} s", duracao_s=timeout_s)
    finally:
        if arquivo_esquema:
            arquivo_esquema.unlink(missing_ok=True)
    resposta = Resposta(duracao_s=round(time.monotonic() - inicio, 1), modelos=[modelo or "codex"])
    for linha in proc.stdout.splitlines():
        try:
            evento = json.loads(linha)
        except json.JSONDecodeError:
            continue
        item = evento.get("item") or {}
        if evento.get("type") == "item.completed" and item.get("type") == "agent_message":
            resposta.texto = item.get("text", "")
        if evento.get("type") == "turn.completed":
            uso = evento.get("usage") or {}
            resposta.tokens_entrada += uso.get("input_tokens", 0)
            resposta.tokens_cache += uso.get("cached_input_tokens", 0)
            resposta.tokens_novos += uso.get("input_tokens", 0) - uso.get("cached_input_tokens", 0)
            resposta.tokens_saida += uso.get("output_tokens", 0)
            resposta.turnos += 1
    if esquema and resposta.texto:
        try:
            resposta.estruturado = json.loads(resposta.texto)
        except json.JSONDecodeError:
            pass
    if not resposta.texto:
        resposta.erro = f"resposta inesperada do Codex: {(proc.stderr or proc.stdout).strip()[-300:]}"
    return resposta
