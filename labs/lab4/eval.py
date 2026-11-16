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
import re
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
# Campos que todo caso de casos.toml e casos_turma.toml precisa ter. O juiz usa o critério.
OBRIGATORIOS = ("id", "departamento", "texto", "criterio")


def plural(n, singular, plural_):
    return f"{n} {singular if n == 1 else plural_}"


def erro_de_toml(nome, e):
    """A mensagem em português; o detalhe técnico do tomllib vai entre parênteses, no fim."""
    linha = re.search(r"line (\d+)", str(e))
    onde = f" perto da linha {linha.group(1)}" if linha else ""
    return f"labs/lab4/{nome} tem um erro de digitação{onde}. Confira as aspas e rode de novo. (Detalhe técnico: {e}.)"


def validar(caso, nome, n):
    """Para antes de chamar o modelo se faltar um campo no caso."""
    quem = f"o caso {caso['id']}" if caso.get("id") else f"o {n}º caso"
    for campo in OBRIGATORIOS:
        if not str(caso.get(campo, "")).strip():
            sys.exit(f"labs/lab4/{nome}: {quem} não tem o campo '{campo}'. "
                     f"Acrescente a linha {campo} = \"...\" (veja o modelo no topo do arquivo) e rode de novo.")
    caso.setdefault("avaliador", "juiz")
    if caso["avaliador"] != "juiz":
        sys.exit(f"labs/lab4/{nome}: {quem} tem avaliador = \"{caso['avaliador']}\". Aqui o avaliador é sempre \"juiz\".")


def carregar_casos():
    casos = [{**p, "avaliador": "script"} for p in rodar.PERGUNTAS["pergunta"]]
    for nome in ("casos.toml", "casos_turma.toml"):
        caminho = LAB / nome
        if caminho.exists():
            try:
                novos = tomllib.loads(caminho.read_text(encoding="utf-8")).get("caso", [])
            except tomllib.TOMLDecodeError as e:
                sys.exit(erro_de_toml(nome, e))
            for n, caso in enumerate(novos, 1):
                validar(caso, nome, n)
            casos += novos
    validos = set(corpus.NIVEL_DO_DEPARTAMENTO)
    for c in casos:
        if c.get("departamento") not in validos:
            sys.exit(f"Caso {c.get('id')}: departamento '{c.get('departamento')}' inválido. Use: {', '.join(sorted(validos))}.")
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


def certas_casos(certos, n):
    return f"{certos} de {plural(n, 'caso', 'casos')}"


def marca(certo):
    return "✓" if certo else ("?" if certo is None else "✗")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--k", type=int, default=3, help="quantas vezes cada caso roda")
    ap.add_argument("--caso", help="roda só este caso (ex.: T01)")
    a = ap.parse_args()
    # Os casos são conferidos antes do login e antes de qualquer chamada: um erro de digitação aparece logo.
    casos = carregar_casos()
    if a.caso:
        casos = [c for c in casos if c["id"] == a.caso]
        if not casos:
            sys.exit(f"Caso {a.caso} não encontrado. Confira o id em labs/lab4/casos_turma.toml.")
    msg = cli_modelo.disponivel("claude") or cli_modelo.logado()
    if msg:
        sys.exit(msg)
    modelo = tomllib.loads((RAIZ / "config" / "modelos.toml").read_text(encoding="utf-8"))["labs"]["modelo"]
    docs = corpus.carregar()
    print(f"\nEval do Bússola: {plural(len(casos), 'caso', 'casos')} × {plural(a.k, 'tentativa', 'tentativas')}, "
          f"RAG do Lab 2 no {modelo}.")
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
    if a.caso:
        # Um caso só: a tela mostra por que cada tentativa deu certo ou errado.
        print("\nMotivo de cada tentativa:")
        for i, r in enumerate(por_caso[a.caso][1], 1):
            print(f"  {i}. {marca(r['certo'])} {r['motivo']}")
    n = len(por_caso)
    print(f"\nAcerto por tentativa: {certas} de {tentativas} ({certas / tentativas:.0%})")
    print(f"pass@{a.k} (acertou pelo menos uma vez): {certas_casos(pelo_menos_uma, n)}")
    print(f"pass^{a.k} (acertou TODAS as vezes):     {certas_casos(todas, n)}")
    amostra = f"{plural(n, 'caso', 'casos')} {'é' if n == 1 else 'são'} uma"
    print(f"\nLembretes: o script erra com palavras (a P03 da Aula 2); o juiz também erra; e {amostra}")
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
