"""Trabalho final (make atividade3): resultados da Aula 3 preenchidos sem apagar o que o grupo escreveu."""
import shutil
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "integrador" / "scripts"))
import atividade3  # noqa: E402


def repo(tmp_path):
    shutil.copytree(RAIZ / "integrador" / "pacote", tmp_path / "integrador" / "pacote")
    for pasta in ("replay", "labs"):
        shutil.copytree(RAIZ / pasta, tmp_path / pasta, ignore=shutil.ignore_patterns("execucoes", "estado", "comparacoes"))
    return tmp_path


def test_modelos_do_pacote_iguais_aos_do_script():
    for nome in atividade3.SECAO:
        pacote = (RAIZ / "integrador/pacote" / nome).read_text()
        if "<!-- Prontos: testes do professor" in pacote:
            continue   # repositório de grupo depois do make atividade3: o arquivo já é do grupo (piloto de 16/11/2026)
        assert pacote == (RAIZ / "integrador/scripts/modelos_atividade3" / nome).read_text()


def test_preparar_preenche_os_resultados(tmp_path):
    raiz = repo(tmp_path)
    atividade3.preparar(raiz)
    q = (raiz / "integrador/pacote/02-qualidade.md").read_text()
    e = (raiz / "integrador/pacote/03-economia.md").read_text()
    assert "pass^3" in q and "Agente único" in q and "Haiku com RAG" in q
    assert "roteado" in e and "ESTIMATIVA" in e and "PTAX" in e
    assert "[PREENCHER:" in q and "[PREENCHER:" in e          # as decisões continuam para o grupo


def test_preparar_nao_apaga_o_que_o_grupo_escreveu(tmp_path):
    raiz = repo(tmp_path)
    antigo = "# Qualidade\n\n## Critério de aprovação\n\nO grupo já escreveu aqui.\n"
    (raiz / "integrador/pacote/02-qualidade.md").write_text(antigo)
    msg = atividade3.preparar_arquivo(raiz, "02-qualidade.md", atividade3.resultados_qualidade,
                                      {n: (RAIZ / "integrador/scripts/modelos_atividade3" / n).read_text() for n in atividade3.SECAO})
    assert "mantido" in msg and (raiz / "integrador/pacote/02-qualidade.md").read_text() == antigo


def test_modelo_antigo_intocado_vira_o_novo(tmp_path):
    raiz = repo(tmp_path)
    (raiz / "integrador/pacote/03-economia.md").write_text("# Economia\n\n## Premissas\n\nPREENCHER\n\n## Go/no-go\n\nPREENCHER\n")
    atividade3.preparar(raiz)
    assert "## Go/no-go por cenário" in (raiz / "integrador/pacote/03-economia.md").read_text()
