#!/usr/bin/env python3
"""Prepara o Lab 2 (make lab2). Executar.

Copia os arquivos do grupo (config.toml e decisao.md) sem sobrescrever o que já existe e confere se
a CLI do agente está instalada. Pode rodar de novo sem estragar nada.
"""
import shutil
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB.parents[1] / "scripts"))
import cli_modelo  # noqa: E402

COPIAS = {"modelos/config.toml": "config.toml", "modelos/decisao.md": "decisao.md"}


def main():
    for origem, destino in COPIAS.items():
        alvo = LAB / destino
        if alvo.exists():
            print(f"  mantido   labs/lab2/{destino} (já existia)")
            continue
        shutil.copy(LAB / origem, alvo)
        print(f"  criado    labs/lab2/{destino}")
    (LAB / "execucoes").mkdir(exist_ok=True)
    if problema := cli_modelo.disponivel("claude"):
        print(f"\nAviso: {problema}")
    print("\nPróximo passo: preencham `grupo` em labs/lab2/config.toml, leiam labs/lab2/perguntas.toml e escrevam "
          "a hipótese em labs/lab2/decisao.md (passo 1 de labs/lab2/README.md).")


if __name__ == "__main__":
    main()
