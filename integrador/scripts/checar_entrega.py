#!/usr/bin/env python3
"""Confere a estrutura das entregas do projeto integrador. Executar: `make er-check`,
`make checkpoint-check` ou `make pacote-check`.

Uso: python3 integrador/scripts/checar_entrega.py {er|checkpoint|final} [raiz do repositório]

Confere só o que é determinístico: arquivos presentes, PREENCHER substituído, seções e tabelas
preenchidas, citações arquivo:linha que existem de fato no legado e ADRs com PASS no validador.
Se o conteúdo é bom, quem julga é a rubrica (integrador/rubrica.md).
"""
import re
import subprocess
import sys
from pathlib import Path

# Mínimos de cada entrega, definidos nos enunciados (integrador/atividades.md)
MIN_REGRAS = 8
MIN_AFIRMACOES = 5
MIN_AMEACAS = 5
MIN_USO_IA = 3
MIN_INTEGRANTES = 4  # grupos de 4 a 5 (proposta, seção 3.2); quem saiu fica na tabela, com a data
MIN_ADRS = {"checkpoint": 1, "final": 2}
MAX_ADRS = 3  # acima disso é aviso: a rubrica pede 2 ou 3 decisões bem defendidas

CITACAO = re.compile(r"`?(?:integrador/legado/)?([\w./-]+\.(?:py|sh|txt|cpy|csv|md)):(\d+)(?:-(\d+))?`?")
REQUISITO_CASO = re.compile(r"\bRC-\d{2}\b")
URL = re.compile(r"https?://\S+")


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
        self.legado = raiz / "integrador" / "legado"
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

    def citacoes(self, relativo, texto, exigir_por_linha=False):
        """Cada arquivo:linha precisa existir em integrador/legado/. É o sensor contra referência inventada."""
        for arquivo, ini, fim in CITACAO.findall(texto):
            alvo = self.legado / arquivo
            if not alvo.is_file():
                self.erros.append(f"integrador/pacote/{relativo}: cita '{arquivo}', que não existe em integrador/legado/. Confira o caminho (relativo a integrador/legado/) ou se o agente inventou.")
                continue
            total = len(alvo.read_text(encoding="utf-8", errors="ignore").splitlines())
            for n in (ini, fim):
                if n and not 1 <= int(n) <= total:
                    self.erros.append(f"integrador/pacote/{relativo}: '{arquivo}:{n}' aponta para uma linha que não existe ({arquivo} tem {total} linhas).")
        if exigir_por_linha:
            for i, linha in enumerate(linhas_de_tabela(texto), 1):
                if not CITACAO.search(" ".join(linha)):
                    self.erros.append(f"integrador/pacote/{relativo}: a linha {i} da tabela não tem evidência no formato arquivo:linha (ex.: sgc/config.py:12).")

    def adrs(self, minimo):
        pasta = self.raiz / "docs" / "adr"
        adrs = sorted(pasta.glob("ADR-*.md"))
        if len(adrs) < minimo:
            self.erros.append(f"docs/adr/: {len(adrs)} ADR(s); esta entrega pede pelo menos {minimo}. Use a skill escrevendo-adrs.")
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

    def er(self):
        base = "engenharia-reversa/"
        texto = self.ler(base + "c4.md")
        if texto is not None:
            self.mermaid(base + "c4.md", texto, 2)
        texto = self.ler(base + "dependencias.md")
        if texto is not None:
            self.tabela(base + "dependencias.md", texto, 1, "dependência(s)")
            self.citacoes(base + "dependencias.md", texto, exigir_por_linha=True)
        texto = self.ler(base + "regras.md")
        if texto is not None:
            self.tabela(base + "regras.md", texto, MIN_REGRAS, "regra(s)")
            self.citacoes(base + "regras.md", texto, exigir_por_linha=True)
            self.secoes_cheias(base + "regras.md", texto, ["Implicações para o Bússola"])
        texto = self.ler(base + "invencoes.md")
        if texto is not None:
            # sem conferir citações: registrar uma referência que o agente inventou é o objetivo do arquivo
            self.tabela(base + "invencoes.md", texto, MIN_AFIRMACOES, "afirmação(ões) conferida(s)")

    def design(self, completo):
        texto = self.ler("01-design.md") if completo else self._design_parcial()
        if texto is None:
            return
        nomes = ["Decisão de conhecimento", "Contrato MCP"]
        if completo:
            nomes = ["Visão geral"] + nomes + ["Decisões registradas"]
            self.mermaid("01-design.md", texto, 1)
        partes = self.secoes_cheias("01-design.md", texto, nomes)
        self.tabela("01-design.md (Contrato MCP)", partes.get("Contrato MCP", ""), 1, "ferramenta(s)")

    def _design_parcial(self):
        """No checkpoint só valem as seções de conhecimento e MCP; o resto pode ter PREENCHER."""
        caminho = self.pacote / "01-design.md"
        if not caminho.is_file():
            self.erros.append("Falta integrador/pacote/01-design.md.")
            return None
        partes = secoes(sem_comentarios(caminho.read_text(encoding="utf-8")))
        for nome in ("Decisão de conhecimento", "Contrato MCP"):
            if "PREENCHER" in partes.get(nome, ""):
                self.erros.append(f"integrador/pacote/01-design.md: a seção '## {nome}' ainda tem 'PREENCHER'.")
        return "\n".join(f"## {k}\n{v}" for k, v in partes.items() if k in ("Decisão de conhecimento", "Contrato MCP"))

    def final(self):
        self.er()
        self.adrs(MIN_ADRS["final"])
        self.design(completo=True)
        texto = self.ler("02-qualidade.md")
        if texto is not None:
            partes = self.secoes_cheias("02-qualidade.md", texto, ["Critério de aprovação", "Casos de teste", "Resultados", "Escolha e limites"])
            self.tabela("02-qualidade.md (Resultados)", partes.get("Resultados", ""), 2, "linha(s) de resultado (pelo menos 2 modelos)")
        texto = self.ler("03-economia.md")
        if texto is not None:
            self.secoes_cheias("03-economia.md", texto, ["Premissas", "Custo por cenário", "Além do token", "Go/no-go"])
        texto = self.ler("04-seguranca.md", ignorar_secao="Mitigação testada")
        if texto is not None:
            partes = self.secoes_cheias("04-seguranca.md", texto, ["Modelo de ameaças", "Posição no control plane", "Requisitos regulatórios"])
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
        texto = self.ler("pitch.md")
        if texto is not None and not URL.search(texto):
            self.erros.append("integrador/pacote/pitch.md: falta o link do vídeo (http...).")


def main(argv):
    if len(argv) < 2 or argv[1] not in ("er", "checkpoint", "final"):
        print(__doc__)
        return 2
    raiz = Path(argv[2]).resolve() if len(argv) > 2 else Path(__file__).resolve().parent.parent.parent
    c = Conferencia(raiz)
    etapa = argv[1]
    if etapa == "er":
        c.er()
    elif etapa == "checkpoint":
        c.adrs(MIN_ADRS["checkpoint"])
        c.design(completo=False)
    else:
        c.final()
    for e in c.erros:
        print(f"  ERRO  {e}")
    for a in c.avisos:
        print(f"  AVISO {a}")
    nome = {"er": "engenharia reversa", "checkpoint": "checkpoint", "final": "pacote final"}[etapa]
    if c.erros:
        print(f"FAIL ({nome}): {len(c.erros)} erro(s). Corrija e rode de novo.")
        return 1
    print(f"PASS ({nome}): estrutura completa. O conteúdo é avaliado pela rubrica (integrador/rubrica.md).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
