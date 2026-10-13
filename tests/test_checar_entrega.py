"""Regressão do checar_entrega.py: modelos dão FAIL; pacote preenchido dá PASS; citação inventada e ADR sem RC dão FAIL."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "integrador" / "scripts" / "checar_entrega.py"
ADR_EXEMPLO = RAIZ / ".agents" / "skills" / "escrevendo-adrs" / "reference" / "ADR-003-armazenamento-de-alertas.md"

LINHA_TABELA = "| {n} | item {n} | sgc/config.py:{n} | leitura do código |\n"
CABECALHO = "| # | Item | Evidência | Verificada por |\n|---|---|---|---|\n"


def rodar(etapa, raiz):
    r = subprocess.run([sys.executable, str(SCRIPT), etapa, str(raiz)], capture_output=True, text=True)
    return r.returncode, r.stdout


@pytest.fixture
def repo(tmp_path):
    shutil.copytree(RAIZ / "integrador" / "legado", tmp_path / "integrador" / "legado",
                    ignore=shutil.ignore_patterns("execucao", "__pycache__"))
    shutil.copytree(RAIZ / "integrador" / "pacote", tmp_path / "integrador" / "pacote")
    shutil.copytree(RAIZ / ".agents" / "skills" / "escrevendo-adrs", tmp_path / ".agents" / "skills" / "escrevendo-adrs")
    shutil.copy(RAIZ / "integrador" / "caso.md", tmp_path / "integrador" / "caso.md")
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    return tmp_path


def preencher(raiz):
    p = raiz / "integrador" / "pacote"
    er = p / "engenharia-reversa"
    mermaid = "```mermaid\nflowchart LR\n    A --> B\n```\n"
    (er / "c4.md").write_text(f"# C4\n\n## Contexto\n\n{mermaid}\n## Containers\n\n{mermaid}\n## O que mudou\n\n- lê o banco do ERP\n")
    tabela = CABECALHO + "".join(LINHA_TABELA.format(n=n) for n in range(1, 9))
    (er / "dependencias.md").write_text("# Dependências\n\n" + tabela)
    (er / "regras.md").write_text("# Regras\n\n" + tabela + "\n## Implicações para o Bússola\n\n- reprocessar exige idempotência\n")
    (er / "invencoes.md").write_text("# Registro\n\n**Agente:** Claude Code, Sonnet\n\n" + CABECALHO
                                     + "".join(f"| {n} | afirmação {n} | li o código | correto |\n" for n in range(1, 6)))
    for nome in ("01-design.md", "02-qualidade.md", "03-economia.md", "04-seguranca.md", "contribuicao.md", "uso-de-ia.md", "pitch.md"):
        arq = p / nome
        texto = arq.read_text(encoding="utf-8").replace("PREENCHER", "conteúdo do grupo")
        if nome in ("02-qualidade.md", "04-seguranca.md", "contribuicao.md", "uso-de-ia.md"):
            # replica a linha de exemplo de cada tabela até o mínimo exigido
            linhas = texto.splitlines(True)
            for i, linha in enumerate(linhas):
                if linha.startswith("| conteúdo do grupo"):
                    linhas[i] = linha * 5
            texto = "".join(linhas)
        texto = texto.replace("- [ ] Todos", "- [x] Todos").replace("**Link do vídeo:** conteúdo do grupo", "**Link do vídeo:** https://example.com/v")
        arq.write_text(texto, encoding="utf-8")
    for n in (1, 2):
        texto = ADR_EXEMPLO.read_text(encoding="utf-8").replace("ADR-003", f"ADR-00{n}")
        texto = texto.replace("## Contexto\n", "## Contexto\n\nAtende o RC-04 do caso.\n", 1)
        (raiz / "docs" / "adr" / f"ADR-00{n}-exemplo.md").write_text(texto, encoding="utf-8")


def test_modelos_dao_fail_com_mensagem(repo):
    for etapa in ("er", "checkpoint", "final"):
        codigo, saida = rodar(etapa, repo)
        assert codigo == 1
        assert "PREENCHER" in saida or "ADR" in saida


def test_pacote_preenchido_da_pass(repo):
    preencher(repo)
    for etapa in ("er", "checkpoint", "final"):
        codigo, saida = rodar(etapa, repo)
        assert codigo == 0, saida


def test_citacao_inventada_da_fail(repo):
    preencher(repo)
    regras = repo / "integrador" / "pacote" / "engenharia-reversa" / "regras.md"
    regras.write_text(regras.read_text() + "| 9 | API online | sgc/api_ws.py:10 | o agente disse |\n| 10 | x | sgc/config.py:9999 | idem |\n")
    codigo, saida = rodar("er", repo)
    assert codigo == 1
    assert "sgc/api_ws.py" in saida and "9999" in saida


def test_variacoes_legitimas_nao_dao_fail(repo):
    """Prefixo integrador/legado/, segunda tabela no arquivo e citação inventada registrada pelo verificador."""
    preencher(repo)
    er = repo / "integrador" / "pacote" / "engenharia-reversa"
    deps = er / "dependencias.md"
    deps.write_text(deps.read_text().replace("sgc/config.py:1 ", "integrador/legado/sgc/config.py:1 ")
                    + "\n## Implícitas\n\n" + CABECALHO + LINHA_TABELA.format(n=9))
    inv = er / "invencoes.md"
    inv.write_text(inv.read_text() + "| 6 | API em sgc/api_ws.py:10 | busca no repositório | inventado |\n")
    codigo, saida = rodar("er", repo)
    assert codigo == 0, saida


def test_adr_sem_requisito_do_caso_da_fail(repo):
    preencher(repo)
    shutil.copy(ADR_EXEMPLO, repo / "docs" / "adr" / "ADR-003-armazenamento-de-alertas.md")
    codigo, saida = rodar("final", repo)
    assert codigo == 1
    assert "ADR-003-armazenamento-de-alertas.md: não cita nenhum requisito do caso" in saida
