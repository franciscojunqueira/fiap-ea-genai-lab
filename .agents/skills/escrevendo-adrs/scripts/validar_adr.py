#!/usr/bin/env python3
"""Valida um ADR contra o padrão do repositório (reference/modelo-adr.md). Requer Python 3.8+.

Uso (a partir da raiz do repositório):
    python3 .claude/skills/escrevendo-adrs/scripts/validar_adr.py docs/adr/ADR-001-titulo.md [...]
    python3 .claude/skills/escrevendo-adrs/scripts/validar_adr.py --proximo docs/adr

Verifica só o que é determinístico: formato, seções, alternativas, rastreabilidade.
Se as alternativas são reais e as consequências honestas, quem julga é o checklist do SKILL.md.
Código de saída 1 se algum ADR falhar.
"""
import re
import sys
from datetime import date
from pathlib import Path

# O padrão da empresa e a rubrica do curso pedem 3 alternativas reais
ALTERNATIVAS_MINIMO = 3
SECOES = [
    "Contexto", "Requisitos e restrições", "Alternativas consideradas", "Decisão",
    "Justificativa", "Consequências", "Rastreabilidade", "Pendências",
]
STATUS_VALIDOS = re.compile(r"^(Proposto|Aprovado|Rejeitado|Substituído por ADR-\d{3})$")
NOME_ARQUIVO = re.compile(r"^ADR-(\d{3,})-[a-z0-9]+(-[a-z0-9]+)*\.md$")
TITULO = re.compile(r"^# ADR-(\d{3,}): (\S.*)$")
DATA = re.compile(r"^\d{4}-\d{2}-\d{2}$")
REQUISITO = re.compile(r"\bRQ-\d{2}\b")
# Trechos do modelo (reference/modelo-adr.md) que não podem sobrar no ADR final
RESTOS_DO_MODELO = [
    "AAAA-MM-DD", "ADR-NNN", "Nome da alternativa", "Título curto da decisão",
    "quem decide (papel ou nome)", "O problema, as forças em jogo", "o que a solução precisa atender",
    "quem pediu ou onde está escrito", "Descrição em 1–3 linhas", "Uma frase com o que muda",
    "Por que A2 e não as outras", "risco ou custo, com a mitigação", "teste, fitness function, eval ou revisão que confirma",
    "o que precisa acontecer para rever",
]
# Placeholder isolado: "TODO" como palavra, ou "..." ocupando sozinho um item, campo ou célula
PLACEHOLDER = re.compile(r"\bTODO\b|(^|[:|-])\s*(\.\.\.|…)\s*($|\|)", re.MULTILINE)
# Respostas que não dizem nada: contras vazios, sensores genéricos
VAZIO = re.compile(r"^(nenhum|nenhuma|n/a|-|—|\.\.\.|…)\.?$", re.IGNORECASE)
SENSOR_VAGO = re.compile(r"^(monitorar|monitoramento|acompanhar|acompanhamento|revisar|observar|a definir)\.?$", re.IGNORECASE)


def secoes(texto, nivel):
    """Divide o texto em {título: corpo} pelos cabeçalhos do nível dado (## ou ###)."""
    marca = "#" * nivel + " "
    partes, atual = {}, None
    for linha in texto.splitlines():
        if linha.startswith(marca):
            atual = linha[len(marca):].strip()
            partes[atual] = []
        elif re.match(r"^#{1,%d} " % nivel, linha):
            atual = None
        elif atual is not None:
            partes[atual].append(linha)
    return {k: "\n".join(v).strip() for k, v in partes.items()}


def campo(texto, nome):
    m = re.search(r"^\*\*%s:\*\*\s*(.*)$" % re.escape(nome), texto, re.MULTILINE)
    return m.group(1).strip() if m else None


def linhas_de_tabela(corpo):
    """Linhas de dados de uma tabela markdown, como listas de células."""
    linhas = [l.strip() for l in corpo.splitlines() if l.strip().startswith("|")]
    dados = [l for l in linhas[1:] if not re.match(r"^\|[\s:|-]+\|$", l)]
    return [[c.strip() for c in l.strip("|").split("|")] for l in dados]


def validar(caminho):
    caminho = Path(caminho)
    if not caminho.is_file():
        return [f"Arquivo não encontrado: {caminho}. Passe o caminho do .md do ADR."]
    erros = []
    texto = caminho.read_text(encoding="utf-8-sig")

    m_arquivo = NOME_ARQUIVO.match(caminho.name)
    if not m_arquivo:
        erros.append(f"Nome do arquivo '{caminho.name}' fora do padrão. Use ADR-NNN-titulo-em-kebab-case.md (ex.: ADR-004-cache-de-produtos.md).")

    primeira = next((l for l in texto.splitlines() if l.strip()), "")
    m_titulo = TITULO.match(primeira)
    if not m_titulo:
        erros.append("A primeira linha deve ser '# ADR-NNN: Título' (ex.: '# ADR-004: Cache de produtos no gateway').")
    elif m_arquivo and m_titulo.group(1) != m_arquivo.group(1):
        erros.append(f"O título diz ADR-{m_titulo.group(1)} e o arquivo diz ADR-{m_arquivo.group(1)}; use o mesmo número.")

    status = campo(texto, "Status")
    if status is None or not STATUS_VALIDOS.match(status):
        erros.append(f"'**Status:**' = '{status}'. Use Proposto, Aprovado, Rejeitado ou 'Substituído por ADR-NNN'.")
    data = campo(texto, "Data")
    try:
        if not DATA.match(data or ""):
            raise ValueError
        date.fromisoformat(data)
    except ValueError:
        erros.append(f"'**Data:**' = '{data}'. Use uma data real no formato AAAA-MM-DD.")
    if not campo(texto, "Decisores"):
        erros.append("'**Decisores:**' vazio. Se ainda não se sabe quem decide, escreva 'a confirmar' e registre em Pendências.")

    h2 = secoes(texto, 2)
    presentes = [s for s in SECOES if s in h2]
    for s in SECOES:
        if s not in h2:
            erros.append(f"Falta a seção '## {s}'. Copie o esqueleto de reference/modelo-adr.md.")
        elif not h2[s]:
            erros.append(f"A seção '## {s}' está vazia.")
    ordem_real = [t for t in h2 if t in SECOES]
    if ordem_real != presentes:
        erros.append(f"Seções fora de ordem. Ordem esperada: {', '.join(SECOES)}.")

    requisitos = []
    for linha in linhas_de_tabela(h2.get("Requisitos e restrições", "")):
        if linha and REQUISITO.fullmatch(linha[0]):
            requisitos.append(linha[0])
    if not requisitos:
        erros.append("A tabela de 'Requisitos e restrições' não tem nenhuma linha com ID no formato RQ-01.")

    alternativas = {}
    for titulo, corpo in secoes(h2.get("Alternativas consideradas", ""), 3).items():
        m = re.match(r"^(A\d+):\s*\S", titulo)
        if not m:
            erros.append(f"Alternativa '### {titulo}' fora do padrão. Use '### A1: Nome da alternativa'.")
            continue
        nome = titulo.split(":", 1)[1].strip().lower()
        if nome in [t.split(":", 1)[1].strip().lower() for t in alternativas.values()]:
            erros.append(f"{m.group(1)} repete o nome de outra alternativa ('{nome}'). Alternativas precisam ser diferentes.")
        alternativas[m.group(1)] = titulo
        for rotulo in ("Prós", "Contras"):
            m_item = re.search(r"\*\*%s:\*\*\s*(.*)" % rotulo, corpo)
            if not m_item or not m_item.group(1).strip() or VAZIO.match(m_item.group(1).strip()):
                erros.append(f"{m.group(1)} sem '**{rotulo}:**' preenchido. Toda alternativa real tem prós e contras; 'nenhum' não vale.")
    if len(alternativas) < ALTERNATIVAS_MINIMO:
        erros.append(f"{len(alternativas)} alternativa(s); o padrão exige pelo menos {ALTERNATIVAS_MINIMO} alternativas reais (### A1, ### A2, ### A3).")

    m_decisao = re.search(r"Adotar \*\*(A\d+)\b", h2.get("Decisão", ""))
    if not m_decisao:
        erros.append("A '## Decisão' deve começar por 'Adotar **A<n>: Nome**', indicando a alternativa escolhida.")
    elif alternativas and m_decisao.group(1) not in alternativas:
        erros.append(f"A '## Decisão' adota {m_decisao.group(1)}, que não existe em 'Alternativas consideradas'.")

    if requisitos and not REQUISITO.search(h2.get("Justificativa", "")):
        erros.append("A '## Justificativa' não cita nenhum requisito. Explique a escolha citando os IDs (RQ-01…).")

    consequencias = secoes(h2.get("Consequências", ""), 3)
    for sub in ("Positivas", "Negativas e riscos", "Reversão"):
        if not re.search(r"^\s*-\s+\S", consequencias.get(sub, ""), re.MULTILINE):
            erros.append(f"Falta '### {sub}' com ao menos um item em '## Consequências'. Toda decisão tem custo; registre-o.")

    rastreados = {}
    for linha in linhas_de_tabela(h2.get("Rastreabilidade", "")):
        if linha and REQUISITO.fullmatch(linha[0]):
            rastreados[linha[0]] = linha
    for rq in requisitos:
        if rq not in rastreados:
            erros.append(f"{rq} não aparece na tabela de '## Rastreabilidade'.")
        elif len(rastreados[rq]) < 3 or not all(c and not VAZIO.match(c) for c in rastreados[rq][1:3]):
            erros.append(f"{rq} na '## Rastreabilidade' precisa dizer como a decisão atende e qual sensor verifica.")
        elif SENSOR_VAGO.match(rastreados[rq][2]):
            erros.append(f"{rq}: sensor '{rastreados[rq][2]}' é vago. Diga qual teste, fitness function, eval ou revisão confirma.")

    for resto in RESTOS_DO_MODELO:
        if resto in texto:
            erros.append(f"Sobrou texto do modelo: '{resto}'. Substitua pelo conteúdo real ou registre em Pendências.")
    if PLACEHOLDER.search(texto):
        erros.append("Sobrou um 'TODO' ou um '...' no lugar de conteúdo. Preencha ou registre em Pendências.")
    return erros


def proximo_numero(pasta):
    numeros = [int(m.group(1)) for p in Path(pasta).glob("ADR-*.md") if (m := NOME_ARQUIVO.match(p.name))]
    return f"ADR-{max(numeros, default=0) + 1:03d}"  # passa de 999 para 1000, aceito pelo padrão


def main(argv):
    if len(argv) == 3 and argv[1] == "--proximo":
        print(proximo_numero(argv[2]))
        return 0
    if len(argv) < 2 or argv[1].startswith("-"):
        print(__doc__)
        return 2
    falhou = False
    for alvo in argv[1:]:
        erros = validar(alvo)
        print(f"[{'FAIL' if erros else 'PASS'}] {alvo}")
        for e in erros:
            print(f"  ERRO  {e}")
        falhou = falhou or bool(erros)
    return 1 if falhou else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
