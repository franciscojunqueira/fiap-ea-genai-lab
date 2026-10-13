#!/usr/bin/env python3
"""Hook Stop do degrau 4: não deixa o agente encerrar com ADR novo sem passar pelo revisor. Executar.

Lê a transcrição da sessão e procura uma chamada ao subagente revisor-adr. Se houver ADR novo ou
alterado em docs/adr/ e nenhuma chamada, bloqueia o encerramento e diz ao agente o que fazer.
Na segunda tentativa (stop_hook_active), deixa encerrar, para não prender o agente num laço.
Se ESCADA_LOG estiver definida, registra cada disparo nesse arquivo (para o replay).
"""
import json
import os
import subprocess
import sys

evento = json.load(sys.stdin)
raiz = os.environ.get("CLAUDE_PROJECT_DIR", evento.get("cwd", "."))


def registrar(resultado):
    if log := os.environ.get("ESCADA_LOG"):
        with open(log, "a", encoding="utf-8") as f:
            f.write(json.dumps({"hook": "exigir_revisor", "resultado": resultado}, ensure_ascii=False) + "\n")


def revisor_chamado(transcricao):
    try:
        linhas = open(transcricao, encoding="utf-8").read().splitlines()
    except OSError:
        return False
    for linha in linhas:
        try:
            conteudo = json.loads(linha).get("message", {}).get("content", [])
        except (json.JSONDecodeError, AttributeError):
            continue
        for bloco in conteudo if isinstance(conteudo, list) else []:
            if (isinstance(bloco, dict) and bloco.get("type") == "tool_use" and bloco.get("name") in ("Agent", "Task")
                    and bloco.get("input", {}).get("subagent_type") == "revisor-adr"):
                return True
    return False


status = subprocess.run(["git", "-C", raiz, "status", "--porcelain", "--", "docs/adr"],
                        capture_output=True, text=True).stdout
adr_mudou = any(l.strip().endswith(".md") for l in status.splitlines())
if not adr_mudou or revisor_chamado(evento.get("transcript_path", "")):
    registrar("liberado")
    sys.exit(0)
if evento.get("stop_hook_active"):
    registrar("liberado sem revisor (segunda tentativa)")
    sys.exit(0)
registrar("bloqueado: revisor não chamado")
print(json.dumps({"decision": "block", "reason": (
    "Há ADR novo ou alterado em docs/adr/ e o subagente revisor-adr ainda não conferiu os fatos. "
    "Delegue a conferência a ele (passe o caminho do ADR e o pedido do usuário) e corrija cada "
    "afirmação 'sem origem' ou 'contradiz': cite a fonte, mova para Pendências como 'a confirmar' ou remova.")}))
