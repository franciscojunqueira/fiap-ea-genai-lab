#!/usr/bin/env python3
"""Prepara o Lab 2 (make lab2). Executar.

Copia o config.toml dos pipelines sem sobrescrever o que já existe e confere se o operador tem a CLI
do agente com login: sem login, para aqui com o passo a passo, em vez de deixar os dois comandos do lab
falharem nas salas. Pode rodar de novo sem estragar nada.
"""
import shutil
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB.parents[1] / "scripts"))
import cli_modelo  # noqa: E402


def main():
    if cli_modelo.disponivel("claude") and cli_modelo.disponivel("codex"):
        print(cli_modelo.disponivel("claude"))
        return 1
    if problema := cli_modelo.logado():
        print(problema)
        return 1
    alvo = LAB / "config.toml"
    if alvo.exists():
        print("  mantido   labs/lab2/config.toml (já existia)")
    else:
        shutil.copy(LAB / "modelos" / "config.toml", alvo)
        print("  criado    labs/lab2/config.toml")
    (LAB / "execucoes").mkdir(exist_ok=True)
    print("\nPronto. Nas salas, o operador roda os dois comandos, um de cada vez:\n"
          "  make lab2-rodar PIPELINE=rag\n"
          "  make lab2-rodar PIPELINE=agentica")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
