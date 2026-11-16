#!/usr/bin/env python3
"""Trabalho final (Atividade 3) em dois comandos: preparar as seções da Aula 3 e entregar. Executar.

    make atividade3            preenche, em integrador/pacote/02-qualidade.md, 03-economia.md e 04-seguranca.md, a
                               seção de resultados com os números das demonstrações do professor (replays das
                               Aulas 3 e 4) e deixa [PREENCHER: ...] só nas decisões do grupo.
    make atividade3-entregar   roda o make pacote-check; com PASS, faz git add, commit e push e mostra o
                               link e o SHA para o Portal. Com FAIL, não envia nada.

Os arquivos do pacote são do grupo: o preparar só troca uma seção de resultados ainda vazia (PREENCHER) e
só troca um arquivo inteiro se ele ainda for o modelo antigo, sem nada escrito pelo grupo.
"""
import json
import re
import sys
import tomllib
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(AQUI))
sys.path.insert(0, str(RAIZ / "labs" / "lab5"))
import atividade2  # noqa: E402
from checar_entrega import secoes, sem_comentarios  # noqa: E402

PACOTE = Path("integrador/pacote")
REPLAY = RAIZ / "replay"
SECAO = {"02-qualidade.md": "Resultados das demonstrações", "03-economia.md": "Resultados da demonstração",
         "04-seguranca.md": "Resultados das demonstrações"}
NOMES = {"haiku-rag": "Haiku com RAG", "haiku-agentica": "Haiku com busca agêntica", "sonnet-rag": "Sonnet com RAG",
         "sonnet-agentica": "Sonnet com busca agêntica"}


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
            return f"  mantido    {nome}: o grupo já escreveu no modelo antigo. Copiem o texto para outro lugar, apaguem o arquivo e rodem make atividade3 de novo."
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


def preparar(raiz=RAIZ):
    # O modelo novo vem do template (integrador/scripts é atualizado pelo make atualizar; o pacote, não).
    modelos = {n: (AQUI / "modelos_atividade3" / n).read_text(encoding="utf-8") for n in SECAO}
    print(preparar_arquivo(raiz, "02-qualidade.md", resultados_qualidade, modelos))
    print(preparar_arquivo(raiz, "03-economia.md", resultados_economia, modelos))
    print(preparar_arquivo(raiz, "04-seguranca.md", resultados_seguranca, modelos))
    faltam = 0
    for n in ("02-qualidade.md", "03-economia.md"):   # o 04 usa o que a Aula 4 ensina: fica para depois dela
        a = raiz / PACOTE / n
        if a.exists():
            faltam += sem_comentarios(a.read_text(encoding="utf-8")).count("PREENCHER")
    print(f"\nPróximo passo: abram {PACOTE}/02-qualidade.md e 03-economia.md e troquem cada [PREENCHER: ...] pela "
          f"decisão do grupo (faltam {faltam}). Os resultados já vêm prontos, inclusive os do 04-seguranca.md.")
    print("Depois da Aula 4: as decisões do 04-seguranca.md, os ADRs, contribuicao.md e uso-de-ia.md. Por fim: make atividade3-entregar")
    return 0


def entregar(raiz=RAIZ):
    return atividade2.entregar(raiz, etapa="final", comando="make atividade3-entregar", mensagem="Trabalho final")


def main(argv):
    if len(argv) < 2 or argv[1] not in ("preparar", "entregar"):
        print(__doc__)
        return 2
    return preparar() if argv[1] == "preparar" else entregar()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
