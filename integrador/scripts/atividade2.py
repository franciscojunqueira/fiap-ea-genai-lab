#!/usr/bin/env python3
"""Atividade 2 (checkpoint) em dois comandos: preparar o modelo para preencher e entregar. Executar.

    make atividade2            prepara as seções "Decisão de conhecimento" e "Contrato MCP" do
                               integrador/pacote/01-design.md com o texto pronto e os espaços
                               [PREENCHER: ...], e mostra os números do Lab 2 do grupo.
    make atividade2-adr DECISAO="..."
                               roda o agente (Sonnet, skill escrevendo-adrs, só escreve em docs/adr/)
                               para registrar o 1º ADR do grupo e roda o validador no fim.
    make atividade2-entregar   roda o make checkpoint-check; com PASS, faz git add, commit e push e
                               mostra o link e o SHA para o Portal. Com FAIL, não envia nada.

O 01-design.md é do grupo: o preparar só troca uma seção que ainda está vazia (só PREENCHER) e nunca
apaga o que o grupo já escreveu.
"""
import json
import os
import re
import subprocess
import sys
import time
import tomllib
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
| minierp:solicitar_ajuste_estoque | Escreve um pedido, não o estoque | produto_id, quantidade (variação com sinal), motivo | número do ajuste, status PENDENTE | Não precisa para pedir. O ajuste só vale depois que uma pessoa aprova | Não: duas chamadas criam dois pedidos; a aprovação barra o segundo | TI Operacional |
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
    print("\nOs números do Lab 2 (linha Acerto):")
    nomes = {"rag": "RAG", "agentica": "busca agêntica"}
    achados = numeros_lab2(raiz)
    if not achados and (raiz / "labs/lab2/usar_replay.py").is_file():
        # Desde 16/11/2026 o Lab 2 é uma demonstração do professor: sem execução do grupo, vêm as gravadas.
        subprocess.run([sys.executable, str(raiz / "labs/lab2/usar_replay.py")], cwd=raiz, capture_output=True)
        achados = numeros_lab2(raiz)
    for pipeline, rotulo in nomes.items():
        n = achados.get(pipeline)
        if n is None:
            print(f"  {rotulo}: sem execução em labs/lab2/execucoes/. Rodem make lab2-replay e digam no texto que são os números da demonstração do professor.")
        else:
            origem = " (números da demonstração do professor: digam isso no texto)" if n["replay"] else ""
            print(f"  {rotulo}: acertou {n['acerto']} de 10{origem}")
    partes = secoes(arquivo.read_text(encoding="utf-8"))
    restantes = sum(sem_comentarios(partes.get(nome, "")).count("PREENCHER") for nome in MODELOS)
    print(f"\nPróximo passo: abram {DESIGN} e troquem cada [PREENCHER: ...] das seções \"Decisão de conhecimento\" "
          f"e \"Contrato MCP\" pela resposta do grupo (faltam {restantes}). As outras seções continuam com PREENCHER: "
          "são do pacote final.")
    print("Depois: make atividade2-entregar")
    return 0


VALIDADOR_ADR = Path(".agents/skills/escrevendo-adrs/scripts/validar_adr.py")
# O agente só escreve em docs/adr/ e só roda o validador. Desde a v2.1.302 o `claude -p` começa em modo Manual:
# o que não está nesta lista é negado, sem perguntar.
# A skill manda rodar o validador por .claude/skills/ (um link para .agents/skills/): as duas grafias entram.
FERRAMENTAS_ADR = ("Read,Glob,Grep,Skill,Write(docs/adr/**),Edit(docs/adr/**),"
                   f"Bash(python3 {VALIDADOR_ADR}:*),Bash(python3 {Path('.claude') / VALIDADOR_ADR.relative_to('.agents')}:*)")
TIMEOUT_ADR_S = 600
PEDIDO_ADR = ("Use a skill escrevendo-adrs para registrar um ADR sobre como o Bússola acessa o SGC. A decisão do grupo é: {decisao}. "
              "Leia antes integrador/pacote/engenharia-reversa/invencoes.md: é a conferência que o verificador do grupo fez das "
              "afirmações do agente da engenharia reversa. Use como fato só o que está conferido em integrador/pacote/engenharia-reversa/ "
              "(c4.md, dependencias.md e regras.md) e nunca use como fato uma afirmação que o verificador marcou como errada ou "
              "imprecisa: se precisar dela, use a versão corrigida no arquivo de origem ou marque \"a confirmar\". "
              "Os requisitos vêm de integrador/caso.md. "
              "Não invente decisores nem requisitos: marque como \"a confirmar\" o que não estiver nos arquivos. "
              "Escreva só em docs/adr/ e rode o validador no fim.")
PEDIDO_ADR_DIRETO = ("Escreva agora o arquivo do ADR em docs/adr/; não descreva, escreva. " + PEDIDO_ADR)


def modelo_adr(raiz):
    config = tomllib.loads((raiz / "config" / "modelos.toml").read_text(encoding="utf-8"))
    return config.get("atividades", {}).get("modelo_adr", "sonnet")


def chamar_agente(prompt, raiz, modelo):
    """Roda o claude -p na raiz do repositório. Devolve o evento final (dict) ou {"erro": mensagem}."""
    inicio = time.monotonic()
    try:
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", modelo, "--output-format", "json", "--no-session-persistence",
             "--max-turns", "40", "--allowedTools", FERRAMENTAS_ADR],
            cwd=raiz, capture_output=True, text=True, timeout=TIMEOUT_ADR_S, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        return {"erro": f"o agente não terminou em {TIMEOUT_ADR_S} s"}
    try:
        dados = json.loads(proc.stdout)
    except json.JSONDecodeError:
        texto = (proc.stderr or proc.stdout).strip()[-300:]
        dica = " Limite do plano atingido: o segundo assinante do grupo roda o comando." if "limit" in texto.lower() else ""
        return {"erro": f"resposta inesperada do Claude Code: {texto}{dica}"}
    dados["duracao_s"] = round(time.monotonic() - inicio)
    return dados


def adr(decisao, raiz=RAIZ, chamar=None):
    """1º ADR do grupo por `claude -p`, com a skill escrevendo-adrs. Devolve 0 se o validador deu PASS."""
    decisao = (decisao or "").strip()
    if not decisao:
        print('Faltou a decisão do grupo. Escrevam uma frase e rodem de novo, por exemplo:\n'
              '  make atividade2-adr DECISAO="O Bússola lê uma cópia diária do banco do SGC, só para leitura"')
        return 2
    chamar = chamar or chamar_agente
    if chamar is chamar_agente:
        sys.path.insert(0, str(raiz / "scripts"))
        import cli_modelo
        problema = cli_modelo.disponivel() or cli_modelo.logado()
        if problema:
            print(problema)
            return 1
    pasta = raiz / "docs" / "adr"
    antes = {a: a.stat().st_mtime_ns for a in pasta.glob("ADR-*.md")}
    print(f"O agente está escrevendo o ADR (leva de 1 a 3 minutos)...", flush=True)
    def novos_adrs():
        return sorted(a for a in pasta.glob("ADR-*.md") if antes.get(a) != a.stat().st_mtime_ns)

    resposta = chamar(PEDIDO_ADR.format(decisao=decisao), raiz, modelo_adr(raiz))
    if resposta.get("erro") or resposta.get("is_error"):
        print(f"O agente não terminou: {resposta.get('erro') or str(resposta.get('result'))[:300]}")
        return 1
    if not novos_adrs():
        # Aconteceu em 1 de 3 testes (16/11/2026): o agente descreveu o ADR e não escreveu. Uma nova tentativa, direta.
        print("O agente descreveu o ADR sem escrever o arquivo. Tentando de novo, com um pedido mais direto...", flush=True)
        resposta2 = chamar(PEDIDO_ADR_DIRETO.format(decisao=decisao), raiz, modelo_adr(raiz))
        if resposta2.get("erro") or resposta2.get("is_error"):
            print(f"O agente não terminou: {resposta2.get('erro') or str(resposta2.get('result'))[:300]}")
            return 1
        resposta = resposta2
    novos = novos_adrs()
    if not novos:
        print("O agente não escreveu nenhum ADR em docs/adr/. O que ele respondeu:\n  "
              + str(resposta.get("result", ""))[:600].replace("\n", "\n  ")
              + "\nRodem o comando de novo; se repetir, chamem o professor.")
        return 1
    saida = subprocess.run([sys.executable, str(raiz / VALIDADOR_ADR), *map(str, novos)], cwd=raiz, capture_output=True, text=True)
    ok = saida.returncode == 0
    print("\nValidador do ADR:")
    print("  " + (saida.stdout.strip() or saida.stderr.strip()).replace("\n", "\n  "))
    for a in novos:
        print(f"\nADR escrito: {a.relative_to(raiz)}")
    uso = resposta.get("usage") or {}
    entrada = sum(uso.get(k, 0) for k in ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens"))
    milhar = lambda n: f"{int(n):,}".replace(",", ".")
    tokens = f", {milhar(entrada)} tokens de entrada, {milhar(uso.get('output_tokens', 0))} de saída" if uso else ""
    print(f"Resultado do validador: {'PASS' if ok else 'FAIL'}"
          f" ({resposta.get('duracao_s', '?')} s, {resposta.get('num_turns', '?')} turnos{tokens})")
    if ok:
        print("O PASS confere só a forma. O verificador abre o ADR e responde sim ou não: cada fato do SGC cita o arquivo "
              "de onde veio? Algum decisor, prazo ou requisito foi inventado? As alternativas existem no caso?")
    else:
        print("Rodem o comando de novo ou corrijam à mão o que o validador aponta acima.")
    return 0 if ok else 1


def link_web(remoto):
    """URL do remoto (https ou ssh) para o link do repositório no navegador."""
    remoto = remoto.strip()
    m = re.match(r"git@([^:]+):(.+)", remoto)
    if m:
        remoto = f"https://{m.group(1)}/{m.group(2)}"
    remoto = re.sub(r"https://[^@/]+@", "https://", remoto)
    return re.sub(r"\.git$", "", remoto)


def entregar(raiz=RAIZ, conferir=None, etapa="checkpoint", comando="make atividade2-entregar", mensagem="Atividade 2 (checkpoint)"):
    conferir = conferir or (lambda: subprocess.run(
        [sys.executable, str(raiz / "integrador/scripts/checar_entrega.py"), etapa, str(raiz)]).returncode)
    if conferir() != 0:
        print(f"\nNada foi enviado. Corrijam o que a mensagem acima pede e rodem {comando} de novo.")
        return 1
    git(raiz, "add", "-A")
    if git(raiz, "diff", "--cached", "--quiet").returncode != 0:
        r = git(raiz, "commit", "-q", "-m", mensagem)
        if r.returncode != 0:
            print(f"\nO commit falhou: {r.stderr.strip() or r.stdout.strip()}")
            return 1
    r = git(raiz, "push", "-q")
    if r.returncode != 0:
        print(f"\nO push falhou: {r.stderr.strip()}\nSe a mensagem fala em 'fetch first' ou 'rejected', rodem git pull "
              f"e depois {comando} de novo.")
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
    if len(argv) < 2 or argv[1] not in ("preparar", "entregar", "adr"):
        print(__doc__)
        return 2
    if argv[1] == "adr":
        return adr(os.environ.get("DECISAO", ""))   # o make passa DECISAO="..." como variável de ambiente
    return preparar() if argv[1] == "preparar" else entregar()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
