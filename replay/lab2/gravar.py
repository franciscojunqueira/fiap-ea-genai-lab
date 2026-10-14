#!/usr/bin/env python3
"""Grava o replay do Lab 2 por `claude -p`: as 10 perguntas em cada condição. Executar.

Uso (da raiz do repositório):  python3 replay/lab2/gravar.py [<condição> ...]   (sem argumento: todas)

Condições: <modelo>-<pipeline>[-acl-prompt], com modelo haiku (o dos labs, config/modelos.toml) ou
sonnet e pipeline rag, agentica ou contexto. A perna de contexto longo só existe aqui: a turma a vê
no debrief. Salva em replay/lab2/gravacao/<condição>/ o .json e o .md de cada execução e imprime a
linha da planilha. Gasta cota do plano de quem roda (80 chamadas curtas na gravação completa).
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "labs" / "lab2"))
import rodar  # noqa: E402

CONDICOES = ["haiku-rag", "haiku-agentica", "haiku-contexto", "sonnet-rag", "sonnet-agentica", "sonnet-contexto",
             "haiku-rag-acl-prompt", "haiku-agentica-acl-prompt"]


def config_de(condicao):
    config = {**rodar.PADRAO, "grupo": "replay"}
    if condicao.startswith("sonnet"):
        config["modelo"] = "sonnet"
    if condicao.endswith("acl-prompt"):
        config["acl"] = "prompt"
    return config


def main(argv):
    pedidas = argv[1:] or CONDICOES
    if any(c not in CONDICOES for c in pedidas):
        print(__doc__)
        return 2
    for condicao in pedidas:
        pipeline = condicao.split("-")[1]
        destino = Path(__file__).resolve().parent / "gravacao" / condicao
        resumo, linha, _ = rodar.rodar(pipeline, config_de(condicao), destino=destino)
        print(f"{condicao}\t{linha}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
