#!/usr/bin/env python3
# CÓPIA. Origem: scripts/validar_skill.py do repositório de planejamento do curso (privado),
# commit 8a7a289, copiada em 2026-10-12. Não edite aqui: corrija na origem e recopie.
"""Valida uma Agent Skill contra o checklist de boas práticas de skills da Anthropic. Requer Python 3.8+.

Referência: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

Uso:
    python3 scripts/validar_skill.py <diretório-da-skill | caminho/SKILL.md> [...]

Erros (código de saída 1) violam regras obrigatórias do formato.
Avisos apontam desvios do guia que merecem revisão humana.
"""
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

# Limites definidos pelo guia (frontmatter e orçamento de tokens)
NOME_MAX = 64
DESCRICAO_MAX = 1024
CORPO_MAX_LINHAS = 500
# Arquivos de referência acima deste tamanho devem ter sumário no topo
REFERENCIA_LINHAS_SUMARIO = 100
# O guia pede ao menos três cenários de avaliação por skill
EVALS_MINIMO = 3

PALAVRAS_RESERVADAS = ("anthropic", "claude")
INICIO_PRIMEIRA_SEGUNDA_PESSOA = re.compile(
    r"^(i |i'm |i can|you |you can|eu |eu posso|você|voce|use-me|me use)", re.IGNORECASE
)
GATILHO_DE_USO = re.compile(r"\b(use quando|usar quando|use-a quando|use antes|use ao|use sempre que|use before|use when|use it when|when the user|quando o usu[aá]rio|quando (for|houver|precisar))\b", re.IGNORECASE)
TAG_XML = re.compile(r"<[^>]+>")
# Caminho estilo Windows, ex.: scripts\\run.py
CAMINHO_WINDOWS = re.compile(r"\b[\w.-]+\\[\w.\\-]+")
LINK_LOCAL = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
SUMARIO = re.compile(r"^#+\s*(conte[uú]do|sum[aá]rio|[ií]ndice|contents)\b", re.IGNORECASE | re.MULTILINE)


def ler_frontmatter(texto):
    """Extrai o frontmatter YAML simples (chave: valor, com suporte a > e |)."""
    linhas = texto.splitlines()
    if not linhas or linhas[0].strip() != "---":
        return None, texto
    try:
        fim = next(i for i in range(1, len(linhas)) if linhas[i].strip() == "---")
    except StopIteration:
        return None, texto
    campos, chave_atual, bloco = {}, None, []
    for linha in linhas[1:fim]:
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", linha)
        if m and not linha.startswith((" ", "\t")):
            if chave_atual and bloco:
                campos[chave_atual] = " ".join(bloco).strip()
            chave, valor = m.group(1), m.group(2).strip()
            if valor in (">", "|", ">-", "|-"):
                chave_atual, bloco = chave, []
            else:
                campos[chave] = valor.strip("\"'")
                chave_atual, bloco = None, []
        elif chave_atual:
            bloco.append(linha.strip())
        elif linha.startswith((" ", "\t")) and campos:
            ultima = list(campos)[-1]
            campos[ultima] = (campos[ultima] + " " + linha.strip()).strip()
    if chave_atual and bloco:
        campos[chave_atual] = " ".join(bloco).strip()
    return campos, "\n".join(linhas[fim + 1:])


def links_locais(texto):
    return [unquote(alvo) for alvo in LINK_LOCAL.findall(texto) if not re.match(r"^[a-z]+://", alvo)]


def validar(caminho):
    caminho = Path(caminho).resolve()
    if not caminho.exists():
        return [f"Caminho não encontrado: {caminho}. Passe o diretório da skill ou o SKILL.md."], []
    skill_md = caminho / "SKILL.md" if caminho.is_dir() else caminho
    pasta = skill_md.parent
    erros, avisos = [], []

    if not skill_md.exists():
        return [f"SKILL.md não encontrado em {pasta}."], []

    texto = skill_md.read_text(encoding="utf-8-sig")
    campos, corpo = ler_frontmatter(texto)
    if campos is None:
        return ["Frontmatter YAML ausente: o arquivo deve começar com '---', name, description, '---'."], []

    nome = campos.get("name", "")
    if not nome:
        erros.append("Campo 'name' ausente no frontmatter.")
    else:
        if len(nome) > NOME_MAX:
            erros.append(f"'name' tem {len(nome)} caracteres; o máximo é {NOME_MAX}.")
        if not re.fullmatch(r"[a-z0-9-]+", nome):
            erros.append(f"'name' = '{nome}' só pode ter letras minúsculas, números e hífens.")
        for reservada in PALAVRAS_RESERVADAS:
            if reservada in nome.lower():
                erros.append(f"'name' contém a palavra reservada '{reservada}'.")
        if nome != pasta.name:
            avisos.append(f"'name' ('{nome}') difere do nome da pasta ('{pasta.name}').")

    descricao = campos.get("description", "")
    if not descricao:
        erros.append("Campo 'description' ausente ou vazio.")
    else:
        if len(descricao) > DESCRICAO_MAX:
            erros.append(f"'description' tem {len(descricao)} caracteres; o máximo é {DESCRICAO_MAX}.")
        if TAG_XML.search(descricao) or TAG_XML.search(nome):
            erros.append("'name' e 'description' não podem conter tags XML.")
        if INICIO_PRIMEIRA_SEGUNDA_PESSOA.match(descricao):
            avisos.append("'description' deve estar em terceira pessoa (ex.: 'Gera relatórios…', não 'Eu gero…' ou 'Você pode…').")
        if not GATILHO_DE_USO.search(descricao):
            avisos.append("'description' deve dizer QUANDO usar a skill (ex.: 'Use quando…').")

    n_linhas = len(corpo.splitlines())
    if n_linhas > CORPO_MAX_LINHAS:
        erros.append(f"Corpo do SKILL.md tem {n_linhas} linhas; o guia recomenda até {CORPO_MAX_LINHAS}. Mova detalhes para arquivos de referência.")

    if "\\" in "".join(links_locais(texto)) or CAMINHO_WINDOWS.search(corpo):
        erros.append("Há caminhos com barra invertida (\\). Use sempre '/'.")

    for alvo in links_locais(corpo):
        arquivo = (pasta / alvo).resolve()
        if not arquivo.exists():
            erros.append(f"Link para '{alvo}' no SKILL.md aponta para arquivo inexistente.")
            continue
        if arquivo.suffix == ".md":
            conteudo = arquivo.read_text(encoding="utf-8")
            aninhados = [a for a in links_locais(conteudo) if a.endswith(".md")]
            if aninhados:
                avisos.append(f"'{alvo}' referencia outros .md ({', '.join(aninhados)}); mantenha as referências a um nível do SKILL.md.")
            if len(conteudo.splitlines()) > REFERENCIA_LINHAS_SUMARIO and not SUMARIO.search("\n".join(conteudo.splitlines()[:20])):
                avisos.append(f"'{alvo}' tem mais de {REFERENCIA_LINHAS_SUMARIO} linhas e não tem sumário no topo.")

    pasta_evals = pasta / "evals"
    cenarios = 0
    if pasta_evals.is_dir():
        for arquivo in pasta_evals.glob("*.json"):
            try:
                dados = json.loads(arquivo.read_text(encoding="utf-8-sig"))
            except json.JSONDecodeError as exc:
                erros.append(f"evals/{arquivo.name} não é JSON válido: {exc}.")
                continue
            for i, cenario in enumerate(dados if isinstance(dados, list) else [dados], 1):
                if isinstance(cenario, dict) and cenario.get("query") and cenario.get("expected_behavior"):
                    cenarios += 1
                else:
                    erros.append(f"evals/{arquivo.name}, cenário {i}: precisa ser um objeto com 'query' e 'expected_behavior' não vazios.")
    if cenarios < EVALS_MINIMO:
        avisos.append(f"{cenarios} cenário(s) de avaliação em evals/; o guia recomenda pelo menos {EVALS_MINIMO}.")

    return erros, avisos


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    falhou = False
    for alvo in argv[1:]:
        erros, avisos = validar(alvo)
        estado = "FAIL" if erros else "PASS"
        print(f"[{estado}] {alvo}")
        for e in erros:
            print(f"  ERRO  {e}")
        for a in avisos:
            print(f"  AVISO {a}")
        falhou = falhou or bool(erros)
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
