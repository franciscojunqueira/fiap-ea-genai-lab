"""Regressão do checar_entrega.py: modelos dão FAIL; pacote preenchido dá PASS; ADR sem RC ou com RC inventado dá FAIL."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
SCRIPT = RAIZ / "integrador" / "scripts" / "checar_entrega.py"
ADR_EXEMPLO = RAIZ / ".agents" / "skills" / "escrevendo-adrs" / "reference" / "ADR-003-armazenamento-de-alertas.md"



def rodar(raiz):
    r = subprocess.run([sys.executable, str(SCRIPT), "final", str(raiz)], capture_output=True, text=True)
    return r.returncode, r.stdout


@pytest.fixture
def repo(tmp_path):
    shutil.copytree(RAIZ / "integrador" / "pacote", tmp_path / "integrador" / "pacote")
    shutil.copytree(RAIZ / ".agents" / "skills" / "escrevendo-adrs", tmp_path / ".agents" / "skills" / "escrevendo-adrs")
    shutil.copy(RAIZ / "integrador" / "caso.md", tmp_path / "integrador" / "caso.md")
    (tmp_path / "docs" / "adr").mkdir(parents=True)
    return tmp_path


def preencher(raiz):
    p = raiz / "integrador" / "pacote"
    for nome in ("01-design.md", "02-qualidade.md", "03-economia.md", "04-seguranca.md", "contribuicao.md", "uso-de-ia.md"):
        arq = p / nome
        texto = arq.read_text(encoding="utf-8").replace("PREENCHER", "conteúdo do grupo")
        if nome in ("02-qualidade.md", "04-seguranca.md", "contribuicao.md", "uso-de-ia.md"):
            # replica a linha de exemplo de cada tabela até o mínimo exigido
            linhas = texto.splitlines(True)
            for i, linha in enumerate(linhas):
                if linha.startswith(("| conteúdo do grupo", "| [conteúdo do grupo")):
                    linhas[i] = linha * 5
            texto = "".join(linhas)
        texto = texto.replace("- [ ] Todos", "- [x] Todos").replace("**Link do vídeo:** conteúdo do grupo", "**Link do vídeo:** https://example.com/v")
        arq.write_text(texto, encoding="utf-8")
    for n in (1, 2):
        texto = ADR_EXEMPLO.read_text(encoding="utf-8").replace("ADR-003", f"ADR-00{n}")
        texto = texto.replace("## Contexto\n", "## Contexto\n\nAtende o RC-04 do caso.\n", 1)
        (raiz / "docs" / "adr" / f"ADR-00{n}-exemplo.md").write_text(texto, encoding="utf-8")


# Num repositório de grupo, o pacote já não é o modelo do template: pular em vez de falhar.
so_no_template = pytest.mark.skipif("PREENCHER" not in (RAIZ / "integrador/pacote/01-design.md").read_text(encoding="utf-8"),
                                    reason="Pacote já preenchido: este teste confere os modelos do template")


@so_no_template
def test_modelos_dao_fail_com_mensagem(repo):
    codigo, saida = rodar(repo)
    assert codigo == 1
    assert "PREENCHER" in saida and "ADR" in saida


def test_pacote_preenchido_da_pass(repo):
    preencher(repo)
    codigo, saida = rodar(repo)
    assert codigo == 0, saida
    assert "PASS (trabalho final)" in saida


def test_pacote_nao_exige_a_engenharia_reversa(repo):
    """25/11/2026: a Atividade 1 saiu. Um grupo que a fez e guardou a pasta não perde nada; sem a pasta, também passa."""
    shutil.rmtree(repo / "integrador/pacote/engenharia-reversa", ignore_errors=True)   # num repositório de grupo, ela existe
    preencher(repo)
    codigo, saida = rodar(repo)
    assert codigo == 0 and "engenharia" not in saida, saida


def test_adr_sem_requisito_do_caso_da_fail(repo):
    preencher(repo)
    shutil.copy(ADR_EXEMPLO, repo / "docs" / "adr" / "ADR-003-armazenamento-de-alertas.md")
    codigo, saida = rodar(repo)
    assert codigo == 1
    assert "ADR-003-armazenamento-de-alertas.md: não cita nenhum requisito do caso" in saida


def test_adr_com_requisito_inventado_da_fail(repo):
    preencher(repo)
    adr = repo / "docs" / "adr" / "ADR-001-exemplo.md"
    adr.write_text(adr.read_text(encoding="utf-8").replace("Atende o RC-04", "Atende o RC-04 e o RC-13"), encoding="utf-8")
    codigo, saida = rodar(repo)
    assert codigo == 1 and "cita RC-13, que não existe" in saida
