#!/usr/bin/env python3
"""A eval do Bússola (Aula 3, Demonstração 3). Executar: make lab4-eval [K=3] [CASO=<id>].

As quatro peças de uma eval, cada uma num lugar que a turma pode abrir:
  1. os casos:     labs/lab2/perguntas.toml (10 perguntas) + labs/lab4/casos.toml + casos_turma.toml
  2. a aplicação:  o RAG do Lab 2 (labs/lab2/rodar.py), com o filtro de permissão
  3. o avaliador:  o SCRIPT (expressões regulares do Lab 2) ou o JUIZ (labs/lab4/juiz.py), caso a caso
  4. o resultado:  a tabela na tela e um .json em labs/lab4/execucoes/

Cada caso roda K vezes (padrão 3). "Acertou pelo menos uma vez" (pass@k) e "acertou todas as vezes"
(pass^k) são coisas diferentes: num banco, o que importa é a consistência.
"""
import argparse
import json
import sys
import time
import tomllib
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
sys.path.insert(0, str(RAIZ / "labs" / "lab2"))
sys.path.insert(0, str(RAIZ / "scripts"))
sys.path.insert(0, str(LAB))
import cli_modelo  # noqa: E402
import corpus  # noqa: E402
import juiz  # noqa: E402
import rodar  # noqa: E402

# 3 chamadas por vez, como no Lab 2: o plano não acusou excesso de requisições (medido em 13/10/2026).
PARALELO = 3


def carregar_casos():
    casos = [{**p, "avaliador": "script"} for p in rodar.PERGUNTAS["pergunta"]]
    for nome in ("casos.toml", "casos_turma.toml"):
        caminho = LAB / nome
        if caminho.exists():
            casos += tomllib.loads(caminho.read_text(encoding="utf-8")).get("caso", [])
    return casos


def tentar(caso, modelo, docs):
    r, _ = rodar.perguntar(caso, "rag", dict(rodar.PADRAO), docs, modelo, "claude")
    if r.erro:
        return {"certo": None, "motivo": r.erro, "resposta": ""}
    if caso["avaliador"] == "script":
        p = rodar.pontuar(caso, r, docs)
        return {"certo": p["acerto"], "motivo": p["achou"], "resposta": p["resposta"]}
    texto = r.estruturado.get("resposta", "") if isinstance(r.estruturado, dict) else r.texto
    certo, motivo = juiz.julgar(caso["texto"], texto, caso["criterio"])
    return {"certo": certo, "motivo": motivo, "resposta": texto}


def marca(certo):
    return "✓" if certo else ("?" if certo is None else "✗")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=3, help="quantas vezes cada caso roda")
    ap.add_argument("--caso", help="roda só este caso (ex.: T01)")
    a = ap.parse_args()
    msg = cli_modelo.disponivel("claude") or cli_modelo.logado()
    if msg:
        sys.exit(msg)
    casos = carregar_casos()
    if a.caso:
        casos = [c for c in casos if c["id"] == a.caso]
        if not casos:
            sys.exit(f"Caso {a.caso} não encontrado. Confira o id em labs/lab4/casos_turma.toml.")
    modelo = tomllib.loads((RAIZ / "config" / "modelos.toml").read_text(encoding="utf-8"))["labs"]["modelo"]
    docs = corpus.carregar()
    print(f"\nEval do Bússola: {len(casos)} casos × {a.k} tentativas, RAG do Lab 2 no {modelo}.")
    print(f"Avaliador: SCRIPT nas perguntas do Lab 2; JUIZ ({juiz.MODELO_JUIZ}) nos casos de recusa.\n", flush=True)
    tarefas = [(c, t) for c in casos for t in range(a.k)]
    with ThreadPoolExecutor(PARALELO) as pool:
        resultados = list(pool.map(lambda ct: tentar(ct[0], modelo, docs), tarefas))
    por_caso = {}
    for (c, _), res in zip(tarefas, resultados):
        por_caso.setdefault(c["id"], (c, []))[1].append(res)

    print(f"{'Caso':<5} {'Avaliador':<9} {'Tentativas':<11} {'pass@' + str(a.k):<7} {'pass^' + str(a.k):<7} Pergunta")
    tentativas, pelo_menos_uma, todas = 0, 0, 0
    certas = 0
    for cid, (c, res) in por_caso.items():
        oks = [r["certo"] for r in res]
        certas += sum(bool(o) for o in oks)
        tentativas += len(oks)
        alguma, sempre = any(oks), all(o is True for o in oks)
        pelo_menos_uma += alguma
        todas += sempre
        print(f"{cid:<5} {c['avaliador']:<9} {' '.join(marca(o) for o in oks):<11} {'sim' if alguma else 'não':<7} "
              f"{'sim' if sempre else 'NÃO':<7} {c['texto'][:60]}")
    n = len(por_caso)
    print(f"\nAcerto por tentativa: {certas} de {tentativas} ({certas / tentativas:.0%})")
    print(f"pass@{a.k} (acertou pelo menos uma vez): {pelo_menos_uma} de {n} casos")
    print(f"pass^{a.k} (acertou TODAS as vezes):     {todas} de {n} casos")
    print("\nLembretes: o script erra com palavras (a P03 da Aula 2); o juiz também erra; e 12 casos são uma")
    print("amostra pequena: um caso de diferença não separa dois modelos.\n")
    destino = LAB / "execucoes"
    destino.mkdir(exist_ok=True)
    nome = destino / f"{time.strftime('%Y%m%d-%H%M%S')}-eval.json"
    nome.write_text(json.dumps({"modelo": modelo, "k": a.k, "casos": {cid: {"texto": c["texto"], "avaliador": c["avaliador"],
                                "tentativas": res} for cid, (c, res) in por_caso.items()}}, ensure_ascii=False, indent=2),
                    encoding="utf-8")
    print(f"Detalhes (respostas e motivos): {nome.relative_to(RAIZ)}\n")


if __name__ == "__main__":
    main()
