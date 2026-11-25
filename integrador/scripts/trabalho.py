#!/usr/bin/env python3
"""Trabalho final do projeto integrador em três comandos: preparar, escrever os ADRs e entregar. Executar.

    make trabalho              prepara o pacote: no integrador/pacote/01-design.md, as seções "Decisão de
                               conhecimento" e "Contrato MCP" com o texto pronto e os espaços [PREENCHER: ...];
                               no 02-qualidade.md, no 03-economia.md e no 04-seguranca.md, a seção de resultados
                               com os números das demonstrações do professor. Mostra os números do Lab 2.
    make trabalho-adr TEMA=sgc DECISAO="..."
    make trabalho-adr TEMA=modelo DECISAO="..."
                               roda o agente (Sonnet, skill escrevendo-adrs, só escreve em docs/adr/) para
                               registrar um ADR do grupo e roda o validador no fim.
    make trabalho-entregar     roda o make pacote-check; com PASS, faz git add, commit e push e mostra o
                               link e o SHA para o Portal. Com FAIL, não envia nada.

Os arquivos do pacote são do grupo: o preparar só troca uma seção ainda vazia (PREENCHER), nunca apaga o que
o grupo escreveu e só troca um arquivo inteiro se ele ainda for o modelo antigo, sem nada escrito pelo grupo.
"""
import json
import os
import re
import subprocess
import sys
import time
import tomllib
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "labs" / "lab5"))
from checar_entrega import linhas_de_tabela, secoes, sem_comentarios  # noqa: E402

PACOTE = Path("integrador/pacote")
DESIGN = PACOTE / "01-design.md"
REPLAY = RAIZ / "replay"
SECAO = {"02-qualidade.md": "Resultados das demonstrações", "03-economia.md": "Resultados da demonstração",
         "04-seguranca.md": "Resultados das demonstrações"}
NOMES = {"haiku-rag": "Haiku com RAG", "haiku-agentica": "Haiku com busca agêntica", "sonnet-rag": "Sonnet com RAG",
         "sonnet-agentica": "Sonnet com busca agêntica"}


DECISAO = """<!-- Troquem cada [PREENCHER: ...] inteiro, com os colchetes, pela resposta do grupo.
Os números do Lab 2 aparecem na tela do make trabalho. -->

- Para perguntas de busca exata (P01 e P02), o Bússola usa [PREENCHER: RAG ou busca agêntica?], porque [PREENCHER: o que o Lab 2 mostrou?].
- Para perguntas que juntam vários documentos (P03 a P05), o Bússola usa [PREENCHER: RAG ou busca agêntica?], porque [PREENCHER: o que o Lab 2 mostrou?].
- A permissão por documento (RC-02) fica [PREENCHER: no filtro, antes do modelo, ou só no prompt?], porque [PREENCHER: o que acontece com o documento proibido em cada caso?].
- Na demonstração do Lab 2, o RAG acertou [PREENCHER: número] de 10 perguntas e a busca agêntica acertou [PREENCHER: número] de 10."""

CONTRATO = """<!-- As duas primeiras linhas são as ferramentas da demonstração do Lab 3. Na linha sgc:, troquem só os
dois [PREENCHER: ...], com os fatos do SGC do caso (integrador/caso.md, seção 1, fato S4). -->

| Servidor:ferramenta | Lê ou escreve | Entrada | Saída | Aprovação humana | Idempotente | Departamentos |
|---|---|---|---|---|---|---|
| minierp:solicitar_ajuste_estoque | Escreve um pedido, não o estoque | produto_id, quantidade (variação com sinal), motivo | número do ajuste, status PENDENTE | Não precisa para pedir. O ajuste só vale depois que uma pessoa aprova | Não: duas chamadas criam dois pedidos; a aprovação barra o segundo | TI Operacional |
| minierp:executar_ajuste_estoque | Escreve no estoque | ajuste_id | status EXECUTADO, estoque antes e depois | Sim: o ERP recusa o que não foi aprovado | Sim: a segunda chamada devolve o mesmo resultado | TI Operacional |
| sgc:pedir_reprocessamento_retorno | Escreve um pedido, não reprocessa | nome do arquivo de retorno, motivo | número do pedido, status PENDENTE | [PREENCHER: quem aprova?] | [PREENCHER: reprocessar duas vezes dá o mesmo resultado? Se não, como protegem?] | TI Operacional |"""

MODELOS = {"Decisão de conhecimento": DECISAO, "Contrato MCP": CONTRATO}
CABECALHO_ANTIGO = """<!-- Critério "Design" da rubrica (15 pts). As seções "Decisão de conhecimento" e
"Contrato MCP" entram no checkpoint (Atividade 2); o resto, no pacote final. -->"""
CABECALHO_NOVO = """<!-- Critério "Design" da rubrica (20 pts). Rodem make trabalho: ele prepara as seções "Decisão de
conhecimento" e "Contrato MCP" com o texto pronto e os espaços [PREENCHER: ...]. -->"""
# O texto que o make atividade2 punha até 25/11/2026. Seção ainda igual a ele (o grupo não escreveu nada) é trocada pelo
# modelo novo, que não cita a Atividade 1.
MODELOS_ANTIGOS = {"Decisão de conhecimento": """<!-- Atividade 2: troquem cada [PREENCHER: ...] inteiro, com os colchetes, pela resposta do grupo.
Os números do Lab 2 aparecem na tela do make atividade2. -->

- Para perguntas de busca exata (P01 e P02), o Bússola usa [PREENCHER: RAG ou busca agêntica?], porque [PREENCHER: o que o Lab 2 mostrou?].
- Para perguntas que juntam vários documentos (P03 a P05), o Bússola usa [PREENCHER: RAG ou busca agêntica?], porque [PREENCHER: o que o Lab 2 mostrou?].
- A permissão por documento (RC-02) fica [PREENCHER: no filtro, antes do modelo, ou só no prompt?], porque [PREENCHER: o que acontece com o documento proibido em cada caso?].
- No Lab 2 do grupo, o RAG acertou [PREENCHER: número] de 10 perguntas e a busca agêntica acertou [PREENCHER: número] de 10.""",
                   "Contrato MCP": """<!-- Atividade 2: as duas primeiras linhas são as tools da demonstração do Lab 3. Na linha sgc:,
troquem só os dois [PREENCHER: ...], com o que a engenharia reversa do grupo (Atividade 1) mostrou. -->

| Servidor:ferramenta | Lê ou escreve | Entrada | Saída | Aprovação humana | Idempotente | Departamentos |
|---|---|---|---|---|---|---|
| minierp:solicitar_ajuste_estoque | Escreve um pedido, não o estoque | produto_id, quantidade (variação com sinal), motivo | número do ajuste, status PENDENTE | Não precisa para pedir. O ajuste só vale depois que uma pessoa aprova | Não: duas chamadas criam dois pedidos; a aprovação barra o segundo | TI Operacional |
| minierp:executar_ajuste_estoque | Escreve no estoque | ajuste_id | status EXECUTADO, estoque antes e depois | Sim: o ERP recusa o que não foi aprovado | Sim: a segunda chamada devolve o mesmo resultado | TI Operacional |
| sgc:pedir_reprocessamento_retorno | Escreve um pedido, não reprocessa | nome do arquivo de retorno, motivo | número do pedido, status PENDENTE | [PREENCHER: quem aprova?] | [PREENCHER: reprocessar duas vezes dá o mesmo resultado? Se não, como protegem?] | TI Operacional |"""}


def git(raiz, *args):
    return subprocess.run(["git", *args], cwd=raiz, capture_output=True, text=True)


def vazia(nome, corpo):
    """A seção ainda é a do template: só PREENCHER (texto) ou só uma linha de PREENCHER (tabela)."""
    if corpo.strip() == MODELOS_ANTIGOS[nome].strip():
        return True
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



def br(x, casas=2):
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def resultados_qualidade(raiz=RAIZ):
    ev = json.loads((raiz / "replay/lab4/eval/eval_k3.json").read_text(encoding="utf-8"))
    casos = ev["casos"]
    tentativas = [t["certo"] for c in casos.values() for t in c["tentativas"]]
    certas = sum(bool(x) for x in tentativas)
    pelo_menos = sum(any(t["certo"] for t in c["tentativas"]) for c in casos.values())
    todas = sum(all(t["certo"] is True for t in c["tentativas"]) for c in casos.values())
    p03 = casos.get("P03", {}).get("tentativas", [])
    linhas = [f"**Demonstração 3, a eval do Bússola** (testes do professor, {ev['modelo']} com RAG, "
              f"{len(casos)} casos × {ev['k']} tentativas):", "",
              "| Medida | Resultado |", "|---|---|",
              f"| Acerto por tentativa | {certas} de {len(tentativas)} ({certas / len(tentativas):.0%}) |",
              f"| pass@{ev['k']}: acertou pelo menos uma vez | {pelo_menos} de {len(casos)} casos |",
              f"| pass^{ev['k']}: acertou todas as vezes | {todas} de {len(casos)} casos |",
              f"| P03 pelo script (procura palavras) | certa em {sum(bool(t['certo']) for t in p03)} de {len(p03)} |",
              "| P03 pelo juiz (lê o sentido) | errada: a resposta não achou o ADR do gateway |", ""]
    modos = {}
    for m in ("unico", "subagentes"):
        arq = raiz / f"replay/lab4/orquestracao/{m}.json"
        if arq.exists():
            modos[m] = json.loads(arq.read_text(encoding="utf-8"))
    if modos:
        sys.path.insert(0, str(RAIZ / "labs" / "lab4"))
        sys.path.insert(0, str(RAIZ / "scripts"))
        import orquestrar
        linhas += [f"**Demonstração 1, um agente × subagentes** (testes do professor, {next(iter(modos.values()))['modelo']}, "
                   "revisão de 3 ADRs com um problema plantado cada):", "",
                   "| Modo | Problemas plantados citados | Tokens | Custo a preço de API |", "|---|---|---|---|"]
        for m, rot in (("unico", "Agente único"), ("subagentes", "3 subagentes")):
            if m in modos:
                r = modos[m]
                achou = sum(orquestrar.achados(r["texto"]).values())
                linhas.append(f"| {rot} | {achou} de 3 | {br(r['tokens'] / 1000, 0)} mil | US$ {br(r['custo_usd'] or 0, 3)} |")
        linhas.append("")
    linhas += ["**Custo por mil consultas e acerto (testes do Lab 2, a preço de API):**", ""]
    for pasta, rot in NOMES.items():
        arqs = sorted((raiz / "replay/lab2/gravacao" / pasta).glob("*.json"))
        if arqs:
            r = json.loads(arqs[-1].read_text(encoding="utf-8"))["resumo"]
            linhas.append(f"- {rot}: US$ {br(r['usd_por_mil_perguntas'])} por mil consultas; acertou {r['acerto']} de 10.")
    return "\n".join(linhas)


def resultados_economia(raiz=RAIZ):
    import tco
    prem = tomllib.loads((raiz / "labs/lab5/premissas.toml").read_text(encoding="utf-8"))
    linhas = ["**Demonstração 5, o custo por rota** (`make lab5-tco`; custo por mês, em reais):", "",
              "| Divisão | US$ por mil consultas | Piloto | Alvo | Expansão |", "|---|---|---|---|---|"]
    for nome, d in prem["divisao"].items():
        res, usd = tco.calcular(nome, prem)
        rot = nome + (" (ESTIMATIVA)" if nome == "multiagente" else "")
        linhas.append(f"| {rot}: {d['descricao']} | {br(usd * 1000)} | R$ {br(res['piloto'][3], 0)} | "
                      f"R$ {br(res['alvo'][3], 0)} | R$ {br(res['expansao'][3], 0)} |")
    c = prem["cambio"]
    linhas += ["", f"Premissas (labs/lab5/premissas.toml): {prem['volumes']['dias_uteis_mes']} dias úteis por mês; câmbio "
               f"R$ {br(c['usd_brl'], 4)} (PTAX de {c['data']}); gateway US$ {prem['infra']['gateway_usd_mes']} por mês "
               "(APIM Standard v2). O custo inclui o gateway.",
               "", "Fora da conta: as 450 consultas por dia do Risco que precisam ficar no Brasil (RC-03), a "
               "observabilidade e os 5 anos de registro (RC-05). Todo \"cabe\" é otimista."]
    return "\n".join(linhas)


def resultados_seguranca(raiz=RAIZ):
    """Demonstração 1 da Aula 4: as quatro execuções gravadas em replay/lab6/ataque/ (ataque e mitigação)."""
    sys.path.insert(0, str(RAIZ / "labs" / "lab6"))
    import ataque
    gravacoes = {}
    for nome in ataque.ORDEM:
        arq = raiz / "replay/lab6/ataque" / f"{nome}.json"
        if arq.exists():
            gravacoes[nome] = json.loads(arq.read_text(encoding="utf-8"))
    if not gravacoes:
        return "(sem gravação da Demonstração 1 em replay/lab6/ataque/)"
    rotulo = {"nenhuma": "nenhuma (a ferramenta de e-mail liberada)", "sem-saida": "corta o canal de saída (ferramenta negada)",
              "aprovacao": "aprovação humana (envio pendente)"}
    linhas = ["**Demonstração 1, o ataque e a mitigação** (testes do professor, conta de testes, Claude Code "
              f"{next(iter(gravacoes.values()))['claude_code']}; busca agêntica do Lab 2 com o acesso do Risco, um cadastro de "
              "sacados com um \"procedimento operacional\" falso e uma ferramenta de e-mail de mentira):", "",
              "| Modelo | Mitigação | E-mail saiu para o atacante | Envio ao atacante tentado e barrado | Tempo por execução |",
              "|---|---|---|---|---|"]
    for g in gravacoes.values():
        ex = g["execucoes"]
        barrados = sum(any(ataque.para_atacante(m) for m in e["negadas"]) for e in ex)
        tempo = sum(e["dur_s"] for e in ex) / len(ex)
        linhas.append(f"| {g['modelo']} | {rotulo[g['mitigacao']]} | {ataque.contar(ex)} de {g['n']} | "
                      f"{str(barrados) + ' de ' + str(g['n']) if g['mitigacao'] == 'aprovacao' else '—'} | {br(tempo, 0)} s |")
    linhas += ["", "O ataque depende do modelo: o Haiku 5.5 resistiu e o Haiku 4.5, não. A mitigação de arquitetura "
               "funcionou nos dois casos testados, porque corta uma perna da trifecta sem depender do que o modelo decide. "
               "Cinco execuções por linha: é uma demonstração, não uma taxa estatística."]
    return "\n".join(linhas)


def modelo_novo(nome, raiz=RAIZ):
    return (raiz / PACOTE / nome).read_text(encoding="utf-8") if (raiz / PACOTE / nome).exists() else None


def intocado(texto):
    """O arquivo ainda não tem nada escrito pelo grupo: todas as seções são PREENCHER ou linhas de PREENCHER."""
    for corpo in secoes(texto).values():
        # a linha de cabeçalho de uma tabela é do modelo (é a que vem antes do |---|), não do grupo
        sem_cabecalho = re.sub(r"^\|[^\n]*\|\n(?=\|[\s:|-]+\|$)", "", sem_comentarios(corpo), flags=re.M)
        limpo = sem_cabecalho.replace("|", " ").replace("-", " ")
        if limpo.strip() and any(p not in ("PREENCHER",) for p in limpo.split() if p):
            return False
    return True


def preparar_arquivo(raiz, nome, gerar, modelos):
    arquivo = raiz / PACOTE / nome
    texto = arquivo.read_text(encoding="utf-8") if arquivo.exists() else ""
    secao = SECAO[nome]
    if f"## {secao}" not in texto:
        if texto and not intocado(texto):
            return f"  mantido    {nome}: o grupo já escreveu no modelo antigo. Copiem o texto para outro lugar, apaguem o arquivo e rodem make trabalho de novo."
        texto = modelos[nome]
    corpo = secoes(texto).get(secao, "")
    if sem_comentarios(corpo).strip() not in ("", "PREENCHER"):
        return f"  mantido    {nome}: a seção \"{secao}\" já está preenchida"
    antes, depois = texto.split(f"## {secao}", 1)
    resto = depois.split("\n## ", 1)
    texto = antes + f"## {secao}\n\n<!-- Prontos: testes do professor. Não editem esta seção. -->\n\n{gerar(raiz)}\n" + (
        "\n## " + resto[1] if len(resto) > 1 else "")
    arquivo.write_text(texto, encoding="utf-8")
    return f"  preparado  {nome}: resultados das demonstrações preenchidos"


def preparar_design_do_grupo(raiz):
    arquivo = raiz / DESIGN
    texto = arquivo.read_text(encoding="utf-8").replace(CABECALHO_ANTIGO, CABECALHO_NOVO)
    novo, preparadas, mantidas = preparar_design(texto)
    arquivo.write_text(novo, encoding="utf-8")
    for nome in preparadas:
        print(f"  preparada  01-design.md: seção \"{nome}\"")
    for nome in mantidas:
        print(f"  mantida    01-design.md: seção \"{nome}\" (o grupo já escreveu nela; nada foi apagado)")


def mostrar_numeros_lab2(raiz):
    print("\nOs números do Lab 2 (linha Acerto), para a Decisão de conhecimento do 01-design.md:")
    nomes = {"rag": "RAG", "agentica": "busca agêntica"}
    achados = numeros_lab2(raiz)
    if not achados and (raiz / "labs/lab2/usar_replay.py").is_file():
        # Desde 16/11/2026 o Lab 2 é uma demonstração do professor: sem execução do grupo, vêm as gravadas.
        subprocess.run([sys.executable, str(raiz / "labs/lab2/usar_replay.py")], cwd=raiz, capture_output=True)
        achados = numeros_lab2(raiz)
    for pipeline, rotulo in nomes.items():
        n = achados.get(pipeline)
        if n is None:
            print(f"  {rotulo}: sem execução em labs/lab2/execucoes/. Rodem make lab2-replay e digam no texto que são "
                  "os números da demonstração do professor.")
        else:
            origem = " (números da demonstração do professor: digam isso no texto)" if n["replay"] else ""
            print(f"  {rotulo}: acertou {n['acerto']} de 10{origem}")


def preparar(raiz=RAIZ):
    # O modelo novo vem do template (integrador/scripts é atualizado pelo make atualizar; o pacote, não).
    modelos = {n: (AQUI / "modelos_trabalho" / n).read_text(encoding="utf-8") for n in SECAO}
    preparar_design_do_grupo(raiz)
    print(preparar_arquivo(raiz, "02-qualidade.md", resultados_qualidade, modelos))
    print(preparar_arquivo(raiz, "03-economia.md", resultados_economia, modelos))
    print(preparar_arquivo(raiz, "04-seguranca.md", resultados_seguranca, modelos))
    mostrar_numeros_lab2(raiz)
    faltam = 0
    for n in ("01-design.md", *SECAO):
        a = raiz / PACOTE / n
        if a.exists():
            faltam += sem_comentarios(a.read_text(encoding="utf-8")).count("PREENCHER")
    print(f"\nPróximo passo: sigam os passos de integrador/atividades.md. Faltam {faltam} [PREENCHER: ...] no pacote; "
          "os resultados das demonstrações já vêm prontos.")
    print('Os ADRs: make trabalho-adr TEMA=sgc DECISAO="..." e make trabalho-adr TEMA=modelo DECISAO="...". '
          "Por fim: make trabalho-entregar")
    return 0


VALIDADOR_ADR = Path(".agents/skills/escrevendo-adrs/scripts/validar_adr.py")
# O agente só escreve em docs/adr/ e só roda o validador. Desde a v2.1.302 o `claude -p` começa em modo Manual:
# o que não está nesta lista é negado, sem perguntar.
# A skill manda rodar o validador por .claude/skills/ (um link para .agents/skills/): as duas grafias entram.
FERRAMENTAS_ADR = ("Read,Glob,Grep,Skill,Write(docs/adr/**),Edit(docs/adr/**),"
                   f"Bash(python3 {VALIDADOR_ADR}:*),Bash(python3 {Path('.claude') / VALIDADOR_ADR.relative_to('.agents')}:*)")
TIMEOUT_ADR_S = 600
FINAL_DO_PEDIDO = ("Não invente decisores nem requisitos: marque como \"a confirmar\" o que não estiver nos arquivos. "
                   "Escreva só em docs/adr/ e rode o validador no fim.")
PEDIDOS_ADR = {
    "sgc": ("Use a skill escrevendo-adrs para registrar um ADR sobre como o Bússola acessa o SGC. A decisão do grupo é: "
            "{decisao}. Os fatos do SGC estão em integrador/caso.md, seção 1, \"O que o SGC faz de fato\" (fatos S1 a S6): "
            "use como fato só o que está lá e cite o fato (por exemplo, \"caso.md, fato S4\"). Os requisitos vêm da seção 4 "
            "do mesmo arquivo. " + FINAL_DO_PEDIDO),
    "modelo": ("Use a skill escrevendo-adrs para registrar um ADR sobre o modelo e as rotas do Bússola. A decisão do grupo "
               "é: {decisao}. Use como fato só os números de integrador/pacote/02-qualidade.md e 03-economia.md e os "
               "requisitos de integrador/caso.md, seção 4, e cite de onde veio cada número. " + FINAL_DO_PEDIDO),
}
EXEMPLO_DECISAO = {"sgc": "O Bússola lê uma cópia diária do banco do SGC, só para leitura",
                   "modelo": "Haiku com RAG nas perguntas simples e Sonnet nas análises, com o roteamento no gateway"}
DIRETO = "Escreva agora o arquivo do ADR em docs/adr/; não descreva, escreva. "


def claude_logado():
    """O Claude Code tem login? (o cli_modelo.logado() também aceita o Codex)"""
    try:
        status = subprocess.run(["claude", "auth", "status"], capture_output=True, text=True, timeout=20)
        return bool(json.loads(status.stdout).get("loggedIn"))
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return False


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


def adr(decisao, raiz=RAIZ, chamar=None, tema="sgc"):
    """Um ADR do grupo por `claude -p`, com a skill escrevendo-adrs. Devolve 0 se o validador deu PASS."""
    tema = (tema or "").strip().lower()
    if tema not in PEDIDOS_ADR:
        print("Faltou o tema do ADR. Rodem de novo com TEMA=sgc (como o Bússola acessa o SGC) ou TEMA=modelo "
              "(o modelo e as rotas do Bússola), por exemplo:\n"
              f'  make trabalho-adr TEMA=sgc DECISAO="{EXEMPLO_DECISAO["sgc"]}"')
        return 2
    decisao = (decisao or "").strip()
    if not decisao:
        print('Faltou a decisão do grupo. Escrevam uma frase e rodem de novo, por exemplo:\n'
              f'  make trabalho-adr TEMA={tema} DECISAO="{EXEMPLO_DECISAO[tema]}"')
        return 2
    chamar = chamar or chamar_agente
    if chamar is chamar_agente:
        sys.path.insert(0, str(raiz / "scripts"))
        import cli_modelo
        problema = cli_modelo.disponivel() or cli_modelo.logado()
        if problema:
            print(problema)
            return 1
        if not claude_logado():
            # Revisão de 25/11/2026: o logado() aceita o Codex, mas este comando só roda o Claude Code.
            print("O make trabalho-adr usa o Claude Code, e o operador está logado só no Codex. Plano B: abram o codex, "
                  "colem o pedido abaixo e esperem o ADR em docs/adr/. Depois, rodem make pacote-check.\n\n"
                  + PEDIDOS_ADR[tema].format(decisao=decisao))
            return 1
    pasta = raiz / "docs" / "adr"
    antes = {a: a.stat().st_mtime_ns for a in pasta.glob("ADR-*.md")}
    print("O agente está escrevendo o ADR (leva de 1 a 3 minutos)...", flush=True)
    def novos_adrs():
        return sorted(a for a in pasta.glob("ADR-*.md") if antes.get(a) != a.stat().st_mtime_ns)

    pedido = PEDIDOS_ADR[tema].format(decisao=decisao)
    resposta = chamar(pedido, raiz, modelo_adr(raiz))
    if resposta.get("erro") or resposta.get("is_error"):
        print(f"O agente não terminou: {resposta.get('erro') or str(resposta.get('result'))[:300]}")
        return 1
    if not novos_adrs():
        # Aconteceu em 1 de 3 testes (16/11/2026): o agente descreveu o ADR e não escreveu. Uma nova tentativa, direta.
        print("O agente descreveu o ADR sem escrever o arquivo. Tentando de novo, com um pedido mais direto...", flush=True)
        resposta2 = chamar(DIRETO + pedido, raiz, modelo_adr(raiz))
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
        print("O PASS confere só a forma. O verificador abre o ADR e responde sim ou não: cada fato cita de onde veio "
              "(o fato do caso ou o arquivo do pacote)? Algum decisor, prazo ou requisito foi inventado? "
              "As alternativas existem no caso?")
    else:
        nomes = " ".join(str(a.relative_to(raiz)) for a in novos)
        print("Corrijam à mão o que o validador aponta acima. Para pedir um ADR novo, apaguem antes o que falhou "
              f"(rm {nomes}): o make pacote-check confere todos os ADRs da pasta.")
    return 0 if ok else 1


def link_web(remoto):
    """URL do remoto (https ou ssh) para o link do repositório no navegador."""
    remoto = remoto.strip()
    m = re.match(r"git@([^:]+):(.+)", remoto)
    if m:
        remoto = f"https://{m.group(1)}/{m.group(2)}"
    remoto = re.sub(r"https://[^@/]+@", "https://", remoto)
    return re.sub(r"\.git$", "", remoto)


def entregar(raiz=RAIZ, conferir=None, etapa="final", comando="make trabalho-entregar", mensagem="Trabalho final"):
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
    if len(argv) < 2 or argv[1] not in ("preparar", "adr", "entregar"):
        print(__doc__)
        return 2
    if argv[1] == "adr":   # o make passa TEMA e DECISAO como variáveis de ambiente
        return adr(os.environ.get("DECISAO", ""), tema=os.environ.get("TEMA", ""))
    return preparar() if argv[1] == "preparar" else entregar()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
