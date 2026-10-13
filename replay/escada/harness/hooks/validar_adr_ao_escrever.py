#!/usr/bin/env python3
"""Hook PostToolUse (Write|Edit) do degrau 4: roda o validador a cada escrita em docs/adr/. Executar.

O Claude Code passa o evento em JSON pela entrada padrão. Se o validador falhar, o hook sai com
código 2: o Claude Code mostra a saída de erro ao agente, que corrige sem ninguém pedir.
Se ESCADA_LOG estiver definida, registra cada disparo nesse arquivo (para o replay).
"""
import json
import os
import subprocess
import sys
from pathlib import Path

evento = json.load(sys.stdin)
caminho = Path(evento.get("tool_input", {}).get("file_path", ""))
raiz = Path(os.environ.get("CLAUDE_PROJECT_DIR", evento.get("cwd", ".")))
if caminho.suffix != ".md" or "docs/adr" not in caminho.as_posix():
    sys.exit(0)

validador = raiz / ".agents" / "skills" / "escrevendo-adrs" / "scripts" / "validar_adr.py"
proc = subprocess.run([sys.executable, str(validador), str(caminho)], capture_output=True, text=True)
if log := os.environ.get("ESCADA_LOG"):
    with open(log, "a", encoding="utf-8") as f:
        f.write(json.dumps({"hook": "validar_adr_ao_escrever", "arquivo": caminho.name,
                            "resultado": "PASS" if proc.returncode == 0 else "FAIL",
                            "erros": proc.stdout.count("ERRO")}, ensure_ascii=False) + "\n")
if proc.returncode != 0:
    print(f"O validador do ADR falhou depois da sua escrita. Corrija cada ERRO:\n{proc.stdout}", file=sys.stderr)
    sys.exit(2)
