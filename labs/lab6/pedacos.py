#!/usr/bin/env python3
"""Demonstração 4 da Aula 4: o tamanho do pedaço e o top-k decidem se o documento certo chega ao modelo.

    make lab6-pedacos PERGUNTA=P03 TAMANHO=500 TOPK=3

Usa a mesma busca BM25 e o mesmo corte em pedaços do Lab 2 (labs/lab2/corpus.py), com o acesso do departamento
de quem pergunta. Imprime o ranking, marca os pedaços dos documentos-fonte da pergunta (os que o Lab 2 espera
nas fontes) e desenha a linha do corte: só o que fica acima dela vai para o modelo. Não chama modelo.
"""
import argparse
import sys
import tomllib
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
sys.path.insert(0, str(RAIZ / "labs" / "lab2"))
import corpus  # noqa: E402

PERGUNTAS = tomllib.loads((RAIZ / "labs" / "lab2" / "perguntas.toml").read_text(encoding="utf-8"))["pergunta"]


def ranking(pergunta, tamanho, topk, docs=None):
    """Devolve (lista de pedaços na ordem do ranking, total de pedaços). Mesma chamada que o RAG do Lab 2 faz,
    com o top-k estendido até o fim para a tela mostrar onde cada documento-fonte ficou."""
    docs = docs if docs is not None else corpus.carregar()
    visiveis = [d for d in docs if corpus.permitido(d, pergunta["departamento"])]
    todos = corpus.pedacos(visiveis, tamanho)
    return corpus.buscar(pergunta["texto"], todos, len(todos)), len(todos)


def posicoes(ordem, fontes):
    """{arquivo-fonte: posição (a partir de 1) do pedaço mais bem colocado}; None se nenhum pedaço pontuou."""
    achadas = {f: None for f in fontes}
    for i, p in enumerate(ordem, 1):
        if p.arquivo in achadas and achadas[p.arquivo] is None:
            achadas[p.arquivo] = i
    return achadas


def mostrar(pergunta, tamanho, topk, linhas=14):
    ordem, total = ranking(pergunta, tamanho, topk)
    fontes = pergunta["fontes"]
    achadas = posicoes(ordem, fontes)
    print(f'\n{pergunta["id"]} ({pergunta["departamento"]}): {pergunta["texto"]}')
    print(f"Pedaços de {tamanho} caracteres: {total} no acesso do departamento; {len(ordem)} com alguma palavra da pergunta. "
          f"Vão ao modelo os {topk} primeiros.\n")
    ate = max(linhas, *(v for v in achadas.values() if v), topk)
    for i, p in enumerate(ordem[:ate], 1):
        marca = "  <== fonte" if p.arquivo in fontes else ""
        trecho = " ".join(p.texto.split())[:58]
        print(f"  {i:>3}  {p.arquivo:<38} {trecho}{marca}")
        if i == topk:
            print(f"       {'-' * 20} corte do top-{topk}: daqui para baixo o modelo não vê {'-' * 6}")
    print()
    for arq, pos in achadas.items():
        if pos is None:
            print(f"  {arq}: nenhum pedaço pontuou (a busca nem lista o documento).")
        else:
            print(f"  {arq}: melhor pedaço em {pos}º lugar -> " + ("DENTRO do corte: o modelo recebe." if pos <= topk
                  else f"FORA do corte (top-{topk}): o modelo não recebe."))
    return achadas


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pergunta", default="P03")
    ap.add_argument("--tamanho", type=int, default=500)
    ap.add_argument("--topk", type=int, default=3)
    a = ap.parse_args()
    escolhida = next((p for p in PERGUNTAS if p["id"] == a.pergunta.upper()), None)
    if not escolhida:
        sys.exit(f"Pergunta '{a.pergunta}' não existe. Use uma de: {', '.join(p['id'] for p in PERGUNTAS)}.")
    if a.tamanho < 100 or a.topk < 1:
        sys.exit("TAMANHO precisa ser pelo menos 100 e TOPK pelo menos 1.")
    mostrar(escolhida, a.tamanho, a.topk)


if __name__ == "__main__":
    main()
