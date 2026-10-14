"""Corpus TechCorp do Lab 2: cabeçalho de permissão, pedaços e busca BM25. Ler (é importado por rodar.py).

A permissão de cada documento vem do cabeçalho (front matter) que o sistema de origem gravou:
    nivel: Público | Interno | Regulado
    dono: <departamento>
    departamentos: [<dep>, ...]   (opcional: restringe o documento a esses departamentos)
Regra do caso (integrador/caso.md, seção 3): cada usuário vê o próprio nível e os menos sensíveis,
salvo exceção registrada no documento.
"""
import math
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
PASTA = RAIZ / "knowledge" / "techcorp"
NIVEIS = ["Público", "Interno", "Regulado"]
# Nível de cada departamento, pelo caso (seção 3): TI Operacional usa runbooks (Público) e status (Interno).
NIVEL_DO_DEPARTAMENTO = {"Arquitetura": "Interno", "TI Operacional": "Interno", "Risco": "Regulado"}
# Sobreposição entre pedaços, a mesma da v1 (aulas/aula02/RAG/rag_pipeline.py): 20% de 500 caracteres.
SOBREPOSICAO = 100
# Constantes clássicas do BM25 (Robertson e Zaragoza, 2009): saturação do termo e normalização por tamanho.
K1, B = 1.5, 0.75


@dataclass
class Documento:
    arquivo: str
    nivel: str
    dono: str
    departamentos: list
    texto: str      # sem o cabeçalho
    bruto: str      # com o cabeçalho, como está no disco


@dataclass
class Pedaco:
    arquivo: str
    texto: str


def carregar(pasta=PASTA):
    docs = []
    for caminho in sorted(pasta.glob("*.md")):
        bruto = caminho.read_text(encoding="utf-8")
        cabecalho, texto = {}, bruto
        m = re.match(r"^---\n(.*?)\n---\n", bruto, re.S)
        if m:
            texto = bruto[m.end():]
            for linha in m.group(1).splitlines():
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    cabecalho[chave.strip()] = valor.strip()
        nivel = cabecalho.get("nivel")
        if nivel not in NIVEIS:
            raise ValueError(f"{caminho.name}: cabeçalho sem 'nivel' válido ({NIVEIS}).")
        deps = [d.strip() for d in cabecalho.get("departamentos", "").strip("[]").split(",") if d.strip()]
        docs.append(Documento(caminho.name, nivel, cabecalho.get("dono", ""), deps, texto, bruto))
    return docs


def permitido(doc, departamento):
    nivel_usuario = NIVEL_DO_DEPARTAMENTO[departamento]
    if NIVEIS.index(doc.nivel) > NIVEIS.index(nivel_usuario):
        return False
    return not doc.departamentos or departamento in doc.departamentos


def pedacos(docs, tamanho):
    """Janela de `tamanho` caracteres com sobreposição, cortando na quebra de linha (lógica da v1)."""
    resultado = []
    for doc in docs:
        texto, inicio = doc.texto, 0
        while inicio < len(texto):
            fim = min(inicio + tamanho, len(texto))
            if fim < len(texto):
                quebra = texto.rfind("\n", inicio + tamanho // 2, fim)
                fim = quebra if quebra > 0 else fim
            trecho = texto[inicio:fim].strip()
            if trecho:
                resultado.append(Pedaco(doc.arquivo, trecho))
            if fim >= len(texto):
                break
            inicio = max(fim - SOBREPOSICAO, inicio + 1)
    return resultado


def _termos(texto):
    sem_acento = unicodedata.normalize("NFKD", texto.lower()).encode("ascii", "ignore").decode()
    return re.findall(r"[a-z0-9]+(?:[-.,][a-z0-9]+)*", sem_acento)


def buscar(consulta, lista, top_k):
    """BM25 em Python puro: busca lexical, sem modelo de embedding para baixar."""
    tokens = [_termos(p.arquivo + " " + p.texto) for p in lista]
    media = sum(map(len, tokens)) / max(len(tokens), 1)
    df = {}
    for t in tokens:
        for termo in set(t):
            df[termo] = df.get(termo, 0) + 1
    n = len(lista)
    notas = []
    for i, t in enumerate(tokens):
        nota = 0.0
        for termo in set(_termos(consulta)):
            f = t.count(termo)
            if not f:
                continue
            idf = math.log(1 + (n - df[termo] + 0.5) / (df[termo] + 0.5))
            nota += idf * f * (K1 + 1) / (f + K1 * (1 - B + B * len(t) / media))
        notas.append((nota, i))
    return [lista[i] for nota, i in sorted(notas, reverse=True)[:top_k] if nota > 0]
