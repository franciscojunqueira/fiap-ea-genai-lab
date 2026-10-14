#!/usr/bin/env python3
"""Confere o Lab 3 (make lab3-check). Executar.

Cinco itens, cada um com PASS ou com o que fazer para passar:
  1. lab preparado e contratos do professor íntegros;   4. ajuste aprovado por uma pessoa e executado uma vez;
  2. comparações ruim e boa registradas;               5. contrato.md com a linha de cada tool, uma tool do SGC e a pergunta de decisão.
  3. contrato do grupo comparado, sem executar sem aprovação e sem inventar quantidade;
O check confere a forma e o estado do ERP. Se o contrato é bom para o Bússola, quem diz é o grupo.
"""
import hashlib
import json
import os
import re
import sqlite3
import sys
import tomllib
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
SOBRA_DO_MODELO = re.compile(r"^\s*<.*>\s*$", re.MULTILINE)
# O mesmo banco do `make erp` (mini-erp/app/db.py); ERP_DB_PATH troca, como no ERP.
BANCO = Path(os.environ.get("ERP_DB_PATH", RAIZ / "mini-erp" / "data" / "mini_erp.db"))
# SHA-256 dos contratos do professor; recalcular quando eles mudarem (tests/test_lab3.py acusa a divergência).
INTEGRIDADE = {
    "descricoes/ruim.toml": "8d4aaead76c9df83f99485f3bf6503d3f2b857a573fda637d994fd21bb0c439a",
    "descricoes/boa.toml": "11f51c3d3dbea3873fc86cb96d104f69d65c8e1e370cb6d957102fcff95c1998",
}


def comparacoes(versao):
    resultado = []
    for arquivo in sorted((LAB / "comparacoes").glob("*.json")):
        try:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if dados.get("resumo", {}).get("versao") == versao and dados["resumo"].get("respondidos") == 3:
            resultado.append(dados)
    return resultado


def contrato_do_grupo():
    try:
        return tomllib.loads((LAB / "descricoes" / "grupo.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None


def item_preparado():
    faltam = [f for f in ("descricoes/grupo.toml", "contrato.md") if not (LAB / f).exists()]
    if faltam or not (RAIZ / ".mcp.json").exists():
        return [f"Faltam {', '.join(faltam) or '.mcp.json'}. Rode `make lab3` primeiro."]
    alterados = [rel for rel, h in INTEGRIDADE.items()
                 if hashlib.sha256((LAB / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest() != h]
    return [] if not alterados else [f"Contrato do professor alterado: {', '.join('labs/lab3/' + a for a in alterados)}. "
                                     "Restaurem com `git checkout -- <arquivo>`: o grupo escreve só o grupo.toml."]


def item_ruim_boa():
    faltam = [v for v in ("ruim", "boa") if not comparacoes(v)]
    return [] if not faltam else [f"Falta a comparação de: {', '.join(faltam)}. Rodem `make lab3-comparar VERSAO={faltam[0]}` "
                                  "(passo 2). Sem cota: `make lab3-replay`."]


def item_grupo():
    texto = (LAB / "descricoes" / "grupo.toml").read_text(encoding="utf-8")
    if "PREENCHER" in texto:
        return ["labs/lab3/descricoes/grupo.toml ainda tem PREENCHER: os autores escrevem o contrato (passo 3)."]
    feitas = comparacoes("grupo")
    if not feitas:
        return ["Falta a comparação do contrato do grupo: `make lab3-comparar VERSAO=grupo` (passo 4)."]
    ultima = feitas[-1]["cenarios"]
    problemas = []
    executou = [c["cenario"] for c in ultima if not c["nao_executou"]]
    if executou:
        problemas.append(f"Com o contrato do grupo, o agente tentou executar sem aprovação em: {', '.join(executou)}. "
                         "Digam na descrição que a execução só vale depois da aprovação na tela e o que responder ao usuário.")
    sem_qtd = next(c for c in ultima if c["cenario"] == "sem_quantidade")
    if not sem_qtd["variacao_ok"]:
        problemas.append(f"Sem quantidade no pedido, o agente supôs uma ({sem_qtd['ajustes_pedidos']}). "
                         "Digam na descrição o que fazer quando falta a quantidade ou o motivo.")
    return problemas


def item_aprovacao_ao_vivo():
    if not BANCO.exists():
        return [f"Não achei o banco do ERP ({BANCO.relative_to(RAIZ) if BANCO.is_relative_to(RAIZ) else BANCO}). "
                "Façam o passo 5 com o `make erp` rodando."]
    try:
        with sqlite3.connect(BANCO) as con:
            linhas = con.execute("SELECT id, solicitado_por, aprovado_por, status FROM ajuste_estoque").fetchall()
    except sqlite3.OperationalError:
        linhas = []
    feitos = [l for l in linhas if l[3] == "EXECUTADO" and (l[2] or "").strip() and l[1] != l[2]]
    if feitos:
        return []
    pendentes = [l[0] for l in linhas if l[3] in ("PENDENTE", "APROVADO")]
    dica = f" Há ajuste(s) {pendentes} esperando aprovação ou execução." if pendentes else ""
    return ["O ERP não tem nenhum ajuste pedido pelo agente, aprovado por uma pessoa na aba Aprovações e executado "
            f"(passo 5).{dica}"]


def item_contrato():
    texto = (LAB / "contrato.md").read_text(encoding="utf-8")
    problemas = []
    if SOBRA_DO_MODELO.search(texto):
        problemas.append("labs/lab3/contrato.md ainda tem linhas de instrução do modelo (começam com '<'): substituam e apaguem.")
    grupo = contrato_do_grupo()
    nomes = [grupo["solicitar"]["nome"], grupo["executar"]["nome"]] if grupo and "PREENCHER" not in str(grupo) else []
    linhas = [l for l in texto.splitlines() if l.strip().startswith("| minierp:")]
    completas = [l for l in linhas if all(c.strip() for c in l.strip().strip("|").split("|")) and len(l.split("|")) >= 9]
    faltam = [n for n in nomes if not any(f"minierp:{n}" in l for l in completas)]
    sgc = [l for l in texto.splitlines() if l.strip().startswith("| sgc:")
           and all(c.strip() for c in l.strip().strip("|").split("|")) and len(l.split("|")) >= 9]
    if not sgc:
        problemas.append("A tabela de labs/lab3/contrato.md não tem nenhuma linha completa sgc:nome_da_tool: o contrato do "
                         "legado sem API (o SGC), com aprovação e idempotência pensadas a partir da Atividade 1.")
    decisao = texto.split("## Pergunta de decisão", 1)[-1] if "## Pergunta de decisão" in texto else ""
    if not [l for l in decisao.splitlines() if l.strip() and not l.strip().startswith(("<", "#"))]:
        problemas.append("labs/lab3/contrato.md sem resposta em 'Pergunta de decisão' (relator).")
    if not nomes:
        problemas.append("Escrevam primeiro o contrato em labs/lab3/descricoes/grupo.toml; a tabela usa os nomes de lá.")
    elif faltam:
        problemas.append(f"A tabela de labs/lab3/contrato.md não tem linha completa (7 colunas preenchidas) para: "
                         f"{', '.join('minierp:' + n for n in faltam)}.")
    return problemas


ITENS = [
    ("1. Lab preparado; contratos do professor íntegros", item_preparado),
    ("2. Comparações ruim e boa", item_ruim_boa),
    ("3. Contrato do grupo comparado", item_grupo),
    ("4. Escrita aprovada por uma pessoa e executada", item_aprovacao_ao_vivo),
    ("5. Contrato MCP registrado (Mini-ERP e SGC) e pergunta de decisão", item_contrato),
]


def main():
    ok = 0
    for nome, funcao in ITENS:
        problemas = funcao()
        if problemas and nome.startswith("1.") and "make lab3" in problemas[0]:
            print(f"[FALHA] {nome}\n        {problemas[0]}\nlab3-check: FAIL")
            return 1
        print(f"[{'OK' if not problemas else 'FALHA'}] {nome}")
        for p in problemas:
            print(f"        {p}")
        ok += not problemas
    veredito = "PASS" if ok == len(ITENS) else "FAIL"
    print(f"\nlab3-check: {veredito} ({ok}/{len(ITENS)} itens)")
    return 0 if veredito == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
