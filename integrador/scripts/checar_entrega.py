#!/usr/bin/env python3
"""Confere a estrutura do trabalho final do projeto integrador. Executar: `make pacote-check`.

Uso: python3 integrador/scripts/checar_entrega.py final [raiz do repositório]

Confere só o que é determinístico: arquivos presentes, PREENCHER substituído, seções e tabelas
preenchidas, requisitos RC-NN que existem no caso e ADRs com PASS no validador.
Se o conteúdo é bom, quem julga é a rubrica (integrador/rubrica.md).
"""
import re
import subprocess
import sys
from pathlib import Path

# Mínimos do trabalho final, definidos no enunciado (integrador/atividades.md)
MIN_AMEACAS = 5
MIN_USO_IA = 3
MIN_INTEGRANTES = 4  # grupos de 4 a 5 (proposta, seção 3.2); quem saiu fica na tabela, com a data
MIN_ADRS = 2
MAX_ADRS = 3  # acima disso é aviso: a rubrica pede 2 ou 3 decisões bem defendidas

REQUISITO_CASO = re.compile(r"\bRC-\d{2}\b")


def sem_comentarios(texto):
    return re.sub(r"<!--.*?-->", "", texto, flags=re.DOTALL)


def secoes(texto):
    """{título: corpo} pelos cabeçalhos '## '."""
    partes, atual = {}, None
    for linha in texto.splitlines():
        if linha.startswith("## "):
            atual = linha[3:].strip()
            partes[atual] = []
        elif linha.startswith("# "):
            atual = None
        elif atual is not None:
            partes[atual].append(linha)
    return {k: "\n".join(v).strip() for k, v in partes.items()}


def linhas_de_tabela(texto):
    """Linhas de dados de todas as tabelas do texto, sem os cabeçalhos (a linha antes de cada |---|)."""
    linhas = [l.strip() for l in texto.splitlines()]
    separador = re.compile(r"^\|[\s:|-]+\|$")
    dados = []
    for i, l in enumerate(linhas):
        if not l.startswith("|") or separador.match(l):
            continue
        if i + 1 < len(linhas) and separador.match(linhas[i + 1]):
            continue  # cabeçalho
        dados.append([c.strip() for c in l.strip("|").split("|")])
    return dados


class Conferencia:
    def __init__(self, raiz):
        self.raiz = raiz
        self.pacote = raiz / "integrador" / "pacote"
        self.erros, self.avisos = [], []

    def ler(self, relativo, ignorar_secao=None):
        caminho = self.pacote / relativo
        if not caminho.is_file():
            self.erros.append(f"Falta integrador/pacote/{relativo}. Recupere o modelo com `git checkout origin/main -- integrador/pacote/{relativo}`.")
            return None
        texto = sem_comentarios(caminho.read_text(encoding="utf-8"))
        if ignorar_secao:
            # seção entregue depois do pacote (ver rubrica.md); não entra na conferência
            texto = re.sub(r"^## %s\n.*?(?=^## |\Z)" % re.escape(ignorar_secao), "", texto, flags=re.DOTALL | re.MULTILINE)
        if "PREENCHER" in texto:
            n = texto.count("PREENCHER")
            self.erros.append(f"integrador/pacote/{relativo}: ainda há {n} 'PREENCHER'. Substitua pelo conteúdo do grupo.")
        return texto

    def secoes_cheias(self, relativo, texto, nomes):
        partes = secoes(texto)
        for nome in nomes:
            corpo = partes.get(nome)
            if corpo is None:
                self.erros.append(f"integrador/pacote/{relativo}: falta a seção '## {nome}' do modelo.")
            elif not corpo.strip():
                self.erros.append(f"integrador/pacote/{relativo}: a seção '## {nome}' está vazia.")
        return partes

    def tabela(self, relativo, texto, minimo, oque):
        linhas = [l for l in linhas_de_tabela(texto) if any(c for c in l)]
        if len(linhas) < minimo:
            self.erros.append(f"integrador/pacote/{relativo}: {len(linhas)} {oque}; o mínimo é {minimo}.")
        return linhas

    def mermaid(self, relativo, texto, minimo):
        blocos = re.findall(r"```mermaid\s*\n(.*?)```", texto, flags=re.DOTALL)
        if len([b for b in blocos if b.strip()]) < minimo:
            self.erros.append(f"integrador/pacote/{relativo}: precisa de {minimo} bloco(s) ```mermaid com o diagrama.")

    def adrs(self, minimo):
        pasta = self.raiz / "docs" / "adr"
        adrs = sorted(pasta.glob("ADR-*.md"))
        if len(adrs) < minimo:
            self.erros.append(f"docs/adr/: {len(adrs)} ADR(s); o trabalho final pede pelo menos {minimo}. Use o make trabalho-adr.")
            return
        if len(adrs) > MAX_ADRS:
            self.avisos.append(f"docs/adr/: {len(adrs)} ADRs. A rubrica avalia 2 ou 3 decisões bem defendidas; mais ADRs não somam pontos.")
        caso = self.raiz / "integrador" / "caso.md"
        validos = set(REQUISITO_CASO.findall(caso.read_text(encoding="utf-8"))) if caso.is_file() else set()
        for adr in adrs:
            citados = set(REQUISITO_CASO.findall(adr.read_text(encoding="utf-8")))
            if not citados & validos:
                self.erros.append(f"docs/adr/{adr.name}: não cita nenhum requisito do caso (RC-01 a RC-12). Ponha na tabela de requisitos os RC-NN de integrador/caso.md que a decisão atende.")
            for rc in sorted(citados - validos):
                self.erros.append(f"docs/adr/{adr.name}: cita {rc}, que não existe em integrador/caso.md.")
        validador = self.raiz / ".agents" / "skills" / "escrevendo-adrs" / "scripts" / "validar_adr.py"
        r = subprocess.run([sys.executable, str(validador)] + [str(a) for a in adrs], capture_output=True, text=True)
        if r.returncode != 0:
            falhas = [l.strip() for l in r.stdout.splitlines() if l.startswith("[FAIL]") or l.strip().startswith("ERRO")]
            self.erros.append("ADRs com FAIL no validador da skill escrevendo-adrs:\n    " + "\n    ".join(falhas))

    def design(self):
        texto = self.ler("01-design.md")
        if texto is None:
            return
        self.mermaid("01-design.md", texto, 1)
        partes = self.secoes_cheias("01-design.md", texto, ["Visão geral", "Decisão de conhecimento", "Contrato MCP",
                                                              "Decisões registradas"])
        self.tabela("01-design.md (Contrato MCP)", partes.get("Contrato MCP", ""), 1, "ferramenta(s)")

    def final(self):
        self.adrs(MIN_ADRS)
        self.design()
        texto = self.ler("02-qualidade.md")
        if texto is not None:
            partes = self.secoes_cheias("02-qualidade.md", texto, [
                "Resultados das demonstrações", "Critério de aceite", "Caso de recusa do grupo", "Modelo de cada rota",
                "O que dispara uma nova eval", "Orquestração por capacidade", "Limites"])
            self.tabela("02-qualidade.md (Modelo de cada rota)", partes.get("Modelo de cada rota", ""), 3, "rota(s)")
            self.tabela("02-qualidade.md (Orquestração por capacidade)", partes.get("Orquestração por capacidade", ""), 3, "capacidade(s)")
        texto = self.ler("03-economia.md")
        if texto is not None:
            partes = self.secoes_cheias("03-economia.md", texto, [
                "Resultados da demonstração", "Go/no-go por cenário", "Alavancas e onde ficam", "Custo de cumprir a RC-03",
                "A premissa que mais muda a decisão"])
            self.tabela("03-economia.md (Go/no-go por cenário)", partes.get("Go/no-go por cenário", ""), 3, "cenário(s)")
        texto = self.ler("04-seguranca.md")
        if texto is not None:
            # "Resultados das demonstrações" veio com a Aula 4 de 16/11/2026: sem ela, só um aviso, para não reprovar um
            # grupo que já tinha escrito o 04 no modelo anterior.
            if "Resultados das demonstrações" not in secoes(texto):
                self.avisos.append("integrador/pacote/04-seguranca.md: falta a seção '## Resultados das demonstrações' "
                                   "(modelo novo da Aula 4). Não reprova; para trazê-la, copiem o texto do grupo, apaguem o arquivo e rodem make trabalho.")
            partes = self.secoes_cheias("04-seguranca.md", texto, ["Modelo de ameaças", "Mitigação testada", "Posição no control plane", "Requisitos regulatórios"])
            self.tabela("04-seguranca.md (Modelo de ameaças)", partes.get("Modelo de ameaças", ""), MIN_AMEACAS, "ameaça(s)")
            self.tabela("04-seguranca.md (Requisitos regulatórios)", partes.get("Requisitos regulatórios", ""), 2, "requisito(s) regulatório(s)")
        texto = self.ler("contribuicao.md")
        if texto is not None:
            self.tabela("contribuicao.md", texto, MIN_INTEGRANTES, "integrante(s) (se alguém saiu, mantenha a linha com a data)")
            if "- [x]" not in texto.lower():
                self.erros.append("integrador/pacote/contribuicao.md: marque '- [x] Todos os integrantes leram e concordam com esta tabela.'")
        texto = self.ler("uso-de-ia.md")
        if texto is not None:
            self.tabela("uso-de-ia.md", texto, MIN_USO_IA, "registro(s) de uso de IA")


def main(argv):
    if len(argv) < 2 or argv[1] != "final":
        print(__doc__)
        return 2
    raiz = Path(argv[2]).resolve() if len(argv) > 2 else Path(__file__).resolve().parent.parent.parent
    c = Conferencia(raiz)
    c.final()
    for e in c.erros:
        print(f"  ERRO  {e}")
    for a in c.avisos:
        print(f"  AVISO {a}")
    if c.erros:
        print(f"FAIL (trabalho final): {len(c.erros)} erro(s). Corrija e rode de novo.")
        return 1
    print("PASS (trabalho final): estrutura completa. O conteúdo é avaliado pela rubrica (integrador/rubrica.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
