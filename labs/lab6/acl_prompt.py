#!/usr/bin/env python3
"""Demonstração 2 da Aula 4: o filtro antes da busca × o pedido no prompt (make lab6-acl-prompt). Executar.

Mostra, a partir das gravações do Lab 2 (replay/lab2/gravacao/), as respostas em que o modelo admitiu que o
documento proibido existe quando a permissão estava só no prompt (acl = "prompt"), ao lado do mesmo pipeline
com o filtro antes da busca. Não chama modelo.
"""
import json
import sys
import textwrap
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
GRAVACAO = RAIZ / "replay" / "lab2" / "gravacao"


def carregar(pasta):
    arquivos = sorted((GRAVACAO / pasta).glob("*.json"))
    if not arquivos:
        sys.exit(f"Falta a gravação replay/lab2/gravacao/{pasta}/.")
    return json.loads(arquivos[-1].read_text(encoding="utf-8"))


def admitiram(dados):
    return [r for r in dados["respostas"] if r.get("confirmou_existencia")]


def main():
    filtro, prompt = carregar("haiku-rag"), carregar("haiku-rag-acl-prompt")
    f, p = filtro["resumo"], prompt["resumo"]
    print(f'\n=== O mesmo Bússola, a mesma pergunta, duas formas de controlar o acesso ({p["modelo"]}, RAG) ===')
    print(f'\n  filtro antes da busca: o modelo nunca vê o documento proibido. Admitiu que ele existe: {f["existencia_confirmada"]} de {f["respondidas"]}')
    print(f'  pedido no prompt:      todos os documentos entram no contexto e o prompt só PEDE que o modelo respeite o departamento. '
          f'Admitiu que o documento existe: {p["existencia_confirmada"]} de {p["respondidas"]}')
    for r in admitiram(prompt):
        print(f'\n  {r["id"]} · usuário de {r["departamento"]}: {r["pergunta"]}')
        print(textwrap.indent(textwrap.fill(r["resposta"].split("\n\n")[0], 104), "    resposta> "))
    print("\n  O que as duas respostas revelam: o modelo VIU o documento (ele diz o nível, o departamento e o assunto).")
    print("  Nenhuma deu o número. Mas pedir no prompt não é controle de acesso: o dado já estava no contexto, e o")
    print("  resultado depende da pergunta, do modelo e da sorte. O controle é o filtro por identidade antes do modelo.\n")
    if len(admitiram(prompt)) != 2:
        sys.exit("Atenção: a gravação deveria ter 2 respostas que admitiram o documento proibido.")


if __name__ == "__main__":
    main()
