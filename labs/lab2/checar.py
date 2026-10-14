#!/usr/bin/env python3
"""Confere o Lab 2 (make lab2-check). Executar.

Cinco itens, cada um com PASS ou com o que fazer para passar:
  1. lab preparado e perguntas e corpus íntegros;  4. decisao.md preenchido, com as linhas do script;
  2. uma execução de cada pipeline (rag, agentica); 5. verificação de 4 respostas pelo verificador.
  3. uma execução com um parâmetro mudado;
O check confere a forma. Se a decisão faz sentido com os números, quem diz é o grupo no debrief.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
sys.path.insert(0, str(LAB))
from rodar import linha  # noqa: E402

SOBRA_DO_MODELO = re.compile(r"^\s*<.*>\s*$", re.MULTILINE)
SECOES = ["Hipótese", "Resultados", "Decisão por tipo de pergunta", "Permissão por documento (RC-02)",
          "Custo × volume", "Pergunta de decisão"]
VEREDITO = re.compile(r"\b(confere|não confere|nao confere|parcial)\b", re.I)
# SHA-256 das perguntas e do corpus; recalcular quando eles mudarem (tests/test_lab2.py acusa a divergência).
INTEGRIDADE = {
    "labs/lab2/perguntas.toml": "61bff205a3b32dbc8f1c7912c142894038e1d0d3d53b0a466ce5622d615a6e8c",
    "knowledge/techcorp/": "10f2b5bc071ae73fe43fc4e8e760eddfe8f0cf3a4b867e055c84e7c12e4cf0e1",
}


def hash_de(rel):
    caminho = RAIZ / rel
    arquivos = sorted(caminho.glob("*.md")) if caminho.is_dir() else [caminho]
    h = hashlib.sha256()
    for a in arquivos:
        h.update(a.name.encode() + a.read_bytes().replace(b"\r\n", b"\n"))  # clone Windows (autocrlf) não conta
    return h.hexdigest()


def secoes(texto):
    resultado, atual = {}, None
    for l in texto.splitlines():
        if l.startswith("## "):
            atual = l[3:].strip()
            resultado[atual] = []
        elif atual is not None:
            resultado[atual].append(l)
    return resultado


def conteudo(linhas):
    return [l for l in linhas if l.strip() and not l.strip().startswith(("<", ">", "<!--"))]


def execucoes():
    resultado = []
    for arquivo in sorted((LAB / "execucoes").glob("*.json")):
        try:
            resultado.append(json.loads(arquivo.read_text(encoding="utf-8"))["resumo"])
        except (json.JSONDecodeError, KeyError):
            continue
    return [e for e in resultado if e.get("respondidas") == 10]


def normalizar(texto):
    return re.sub(r"[\s|]+", " ", texto).strip()


def item_preparado():
    faltam = [f for f in ("config.toml", "decisao.md") if not (LAB / f).exists()]
    if faltam:
        return [f"Faltam {', '.join(faltam)} em labs/lab2/. Rode `make lab2` primeiro."]
    alterados = [rel for rel, h in INTEGRIDADE.items() if hash_de(rel) != h]
    return [] if not alterados else [f"Alterado: {', '.join(alterados)}. As perguntas e o corpus são do professor: "
                                     "restaurem com `git checkout -- <caminho>` e rodem os pipelines de novo."]


def item_pipelines():
    feitas = {e["pipeline"] for e in execucoes() if e["variacao"] == "padrão"}
    faltam = [p for p in ("rag", "agentica") if p not in feitas]
    return [] if not faltam else [f"Falta uma execução completa (10 respostas, config padrão) de: {', '.join(faltam)}. "
                                  f"Rodem `make lab2-rodar PIPELINE={faltam[0]}` (passo 2). Sem cota: `make lab2-replay`."]


def item_variacao():
    if any(e["variacao"] != "padrão" for e in execucoes()):
        return []
    return ["Nenhuma execução com parâmetro mudado. Mudem UM valor em labs/lab2/config.toml (top_k, modelo, acl ou "
            "tamanho_pedaco) e rodem um pipeline de novo (passo 3)."]


def item_decisao():
    texto = (LAB / "decisao.md").read_text(encoding="utf-8")
    achadas = secoes(texto)
    problemas = []
    vazias = [s for s in SECOES if not conteudo(achadas.get(s, []))]
    if vazias:
        problemas.append(f"labs/lab2/decisao.md sem resposta em: {', '.join(vazias)}.")
    if SOBRA_DO_MODELO.search(texto):
        problemas.append("labs/lab2/decisao.md ainda tem linhas de instrução do modelo (começam com '<'): substituam e apaguem.")
    coladas = normalizar("\n".join(achadas.get("Resultados", [])))
    linhas_do_script = [normalizar(linha(e)) for e in execucoes()]
    achadas_linhas = sum(1 for l in linhas_do_script if l in coladas)
    if achadas_linhas < 2:
        problemas.append(f"A seção 'Resultados' tem {achadas_linhas} linha(s) iguais às que o script imprimiu; colem pelo "
                         "menos 2 (rag e agentica), sem editar os números. Para rever uma linha: o .json da execução em labs/lab2/execucoes/.")
    return problemas


def item_verificacao():
    linhas = secoes((LAB / "decisao.md").read_text(encoding="utf-8")).get("Verificação", [])
    conferidas = [l for l in linhas if l.strip().startswith("|") and re.search(r"\bP\d{2}\b", l) and VEREDITO.search(l)]
    if len(conferidas) >= 4:
        return []
    return [f"A tabela da seção 'Verificação' de labs/lab2/decisao.md tem {len(conferidas)} resposta(s) conferida(s); "
            "o verificador confere 4 (3 que o script deu como certas e 1 como errada), com o número da pergunta (P01..P10) "
            "e o veredito: confere, não confere ou parcial."]


ITENS = [
    ("1. Lab preparado; perguntas e corpus íntegros", item_preparado),
    ("2. Execução dos dois pipelines", item_pipelines),
    ("3. Execução com um parâmetro mudado", item_variacao),
    ("4. Decisão de conhecimento com os números", item_decisao),
    ("5. Verificação humana", item_verificacao),
]


def main():
    ok = 0
    for nome, funcao in ITENS:
        problemas = funcao()
        if problemas and nome.startswith("1.") and "make lab2" in problemas[0]:
            print(f"[FALHA] {nome}\n        {problemas[0]}\nlab2-check: FAIL")
            return 1
        print(f"[{'OK' if not problemas else 'FALHA'}] {nome}")
        for p in problemas:
            print(f"        {p}")
        ok += not problemas
    veredito = "PASS" if ok == len(ITENS) else "FAIL"
    print(f"\nlab2-check: {veredito} ({ok}/{len(ITENS)} itens)")
    return 0 if veredito == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
