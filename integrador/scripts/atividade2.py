#!/usr/bin/env python3
"""Atividade 2 (checkpoint) em dois comandos: preparar o modelo para preencher e entregar. Executar.

    make atividade2            prepara as seções "Decisão de conhecimento" e "Contrato MCP" do
                               integrador/pacote/01-design.md com o texto pronto e os espaços
                               [PREENCHER: ...], e mostra os números do Lab 2 do grupo.
    make atividade2-entregar   roda o make checkpoint-check; com PASS, faz git add, commit e push e
                               mostra o link e o SHA para o Portal. Com FAIL, não envia nada.

O 01-design.md é do grupo: o preparar só troca uma seção que ainda está vazia (só PREENCHER) e nunca
apaga o que o grupo já escreveu.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from checar_entrega import linhas_de_tabela, secoes, sem_comentarios  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
DESIGN = Path("integrador/pacote/01-design.md")

DECISAO = """<!-- Atividade 2: troquem cada [PREENCHER: ...] inteiro, com os colchetes, pela resposta do grupo.
Os números do Lab 2 aparecem na tela do make atividade2. -->

- Para perguntas de busca exata (P01 e P02), o Bússola usa [PREENCHER: RAG ou busca agêntica?], porque [PREENCHER: o que o Lab 2 mostrou?].
- Para perguntas que juntam vários documentos (P03 a P05), o Bússola usa [PREENCHER: RAG ou busca agêntica?], porque [PREENCHER: o que o Lab 2 mostrou?].
- A permissão por documento (RC-02) fica [PREENCHER: no filtro, antes do modelo, ou só no prompt?], porque [PREENCHER: o que acontece com o documento proibido em cada caso?].
- No Lab 2 do grupo, o RAG acertou [PREENCHER: número] de 10 perguntas e a busca agêntica acertou [PREENCHER: número] de 10."""

CONTRATO = """<!-- Atividade 2: as duas primeiras linhas são as tools da demonstração do Lab 3. Na linha sgc:,
troquem só os dois [PREENCHER: ...], com o que a engenharia reversa do grupo (Atividade 1) mostrou. -->

| Servidor:ferramenta | Lê ou escreve | Entrada | Saída | Aprovação humana | Idempotente | Departamentos |
|---|---|---|---|---|---|---|
| minierp:solicitar_ajuste_estoque | Escreve um pedido, não o estoque | produto_id, quantidade (variação com sinal), motivo | número do ajuste, status PENDENTE | Não para pedir; o ajuste só vale depois de aprovado na tela | Não: duas chamadas criam dois pedidos; a aprovação barra o segundo | TI Operacional |
| minierp:executar_ajuste_estoque | Escreve no estoque | ajuste_id | status EXECUTADO, estoque antes e depois | Sim: o ERP recusa o que não foi aprovado | Sim: a segunda chamada devolve o mesmo resultado | TI Operacional |
| sgc:pedir_reprocessamento_retorno | Escreve um pedido, não reprocessa | nome do arquivo de retorno, motivo | número do pedido, status PENDENTE | [PREENCHER: quem aprova?] | [PREENCHER: reprocessar duas vezes dá o mesmo resultado? Se não, como protegem?] | TI Operacional |"""

MODELOS = {"Decisão de conhecimento": DECISAO, "Contrato MCP": CONTRATO}


def git(raiz, *args):
    return subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True)


def vazia(nome, corpo):
    """A seção ainda é a do template: só PREENCHER (texto) ou só uma linha de PREENCHER (tabela)."""
    texto = sem_comentarios(corpo).strip()
    if nome == "Contrato MCP":
        linhas = linhas_de_tabela(texto)
        return not linhas or all(all(c in ("PREENCHER", "") for c in l) for l in linhas)
    return texto in ("", "PREENCHER")


def preparar_design(texto):
    """Troca o corpo das seções vazias pelo modelo. Devolve (texto novo, preparadas, mantidas)."""
    linhas = texto.split("\n")
    saida, preparadas, mantidas = [], [], []
    i = 0
    while i < len(linhas):
        linha = linhas[i]
        saida.append(linha)
        i += 1
        nome = linha[3:].strip() if linha.startswith("## ") else None
        if nome not in MODELOS:
            continue
        fim = i
        while fim < len(linhas) and not linhas[fim].startswith(("## ", "# ")):
            fim += 1
        corpo = "\n".join(linhas[i:fim])
        if vazia(nome, corpo):
            saida += ["", MODELOS[nome], ""]
            preparadas.append(nome)
        else:
            saida += linhas[i:fim]
            mantidas.append(nome)
        i = fim
    return "\n".join(saida), preparadas, mantidas


def numeros_lab2(raiz):
    """Última execução de cada pipeline em labs/lab2/execucoes/; as do grupo antes das do replay."""
    pasta = raiz / "labs" / "lab2" / "execucoes"
    achados = {}
    for arquivo in sorted(pasta.glob("*.json")) if pasta.exists() else []:
        try:
            resumo = json.loads(arquivo.read_text(encoding="utf-8"))["resumo"]
        except (ValueError, KeyError):
            continue
        replay = arquivo.name.startswith("replay-")
        atual = achados.get(resumo.get("pipeline"))
        if atual is None or atual["replay"] or not replay:
            achados[resumo.get("pipeline")] = {"acerto": resumo.get("acerto"), "replay": replay, "arquivo": arquivo.name}
    return achados


def preparar(raiz=RAIZ):
    arquivo = raiz / DESIGN
    novo, preparadas, mantidas = preparar_design(arquivo.read_text(encoding="utf-8"))
    arquivo.write_text(novo, encoding="utf-8")
    for nome in preparadas:
        print(f"  preparada  seção \"{nome}\" do {DESIGN}")
    for nome in mantidas:
        print(f"  mantida    seção \"{nome}\" (o grupo já escreveu nela; nada foi apagado)")
    print("\nOs números do Lab 2 de vocês (linha Acerto):")
    nomes = {"rag": "RAG", "agentica": "busca agêntica"}
    achados = numeros_lab2(raiz)
    for pipeline, rotulo in nomes.items():
        n = achados.get(pipeline)
        if n is None:
            print(f"  {rotulo}: sem execução em labs/lab2/execucoes/. Rodem make lab2-replay e digam no texto que são os testes do professor.")
        else:
            origem = " (testes do professor: digam isso no texto)" if n["replay"] else ""
            print(f"  {rotulo}: acertou {n['acerto']} de 10{origem}")
    partes = secoes(arquivo.read_text(encoding="utf-8"))
    restantes = sum(sem_comentarios(partes.get(nome, "")).count("PREENCHER") for nome in MODELOS)
    print(f"\nPróximo passo: abram {DESIGN} e troquem cada [PREENCHER: ...] das seções \"Decisão de conhecimento\" "
          f"e \"Contrato MCP\" pela resposta do grupo (faltam {restantes}). As outras seções continuam com PREENCHER: "
          "são do pacote final.")
    print("Depois: make atividade2-entregar")
    return 0


def link_web(remoto):
    """URL do remoto (https ou ssh) para o link do repositório no navegador."""
    remoto = remoto.strip()
    m = re.match(r"git@([^:]+):(.+)", remoto)
    if m:
        remoto = f"https://{m.group(1)}/{m.group(2)}"
    remoto = re.sub(r"https://[^@/]+@", "https://", remoto)
    return re.sub(r"\.git$", "", remoto)


def entregar(raiz=RAIZ, conferir=None):
    conferir = conferir or (lambda: subprocess.run(
        [sys.executable, str(raiz / "integrador/scripts/checar_entrega.py"), "checkpoint", str(raiz)]).returncode)
    if conferir() != 0:
        print("\nNada foi enviado. Corrijam o que a mensagem acima pede e rodem make atividade2-entregar de novo.")
        return 1
    git(raiz, "add", "-A")
    if git(raiz, "diff", "--cached", "--quiet").returncode != 0:
        r = git(raiz, "commit", "-q", "-m", "Atividade 2 (checkpoint)")
        if r.returncode != 0:
            print(f"\nO commit falhou: {r.stderr.strip() or r.stdout.strip()}")
            return 1
    r = git(raiz, "push", "-q")
    if r.returncode != 0:
        print(f"\nO push falhou: {r.stderr.strip()}\nSe a mensagem fala em 'fetch first' ou 'rejected', rodem git pull "
              "e depois make atividade2-entregar de novo.")
        return 1
    sha = git(raiz, "rev-parse", "HEAD").stdout.strip()
    link = link_web(git(raiz, "remote", "get-url", "origin").stdout)
    linhas = ["Enviado. O relator cola no Portal:", f"  link: {link}", f"  SHA:  {sha}"]
    largura = max(len(l) for l in linhas) + 2
    print("\n+" + "-" * largura + "+")
    for l in linhas:
        print(f"| {l.ljust(largura - 1)}|")
    print("+" + "-" * largura + "+")
    return 0


def main(argv):
    if len(argv) < 2 or argv[1] not in ("preparar", "entregar"):
        print(__doc__)
        return 2
    return preparar() if argv[1] == "preparar" else entregar()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
