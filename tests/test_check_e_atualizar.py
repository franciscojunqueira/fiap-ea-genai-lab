"""Regressão da última linha do make check (NÃO PRONTO sem login) e das listas do make atualizar."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "scripts"))
import atualizar_do_template as atualizar  # noqa: E402
import check  # noqa: E402


def test_ultima_linha_do_check():
    assert check.resumo(["PASS"] * 4, False) == "== PASS: 4 ok, 0 aviso(s), 0 falha(s) =="
    sem_login = check.resumo(["PASS"] * 3 + ["AVISO"], True)
    assert sem_login.startswith("== NÃO PRONTO: 3 ok, 1 aviso(s), 0 falha(s).") and "login" in sem_login
    assert check.resumo(["PASS", "FAIL", "AVISO"], True).startswith("== FAIL:")


def test_atualizar_traz_os_arquivos_do_professor_e_preserva_os_do_grupo():
    professor = lambda c: atualizar.casa(c, atualizar.DO_PROFESSOR) and not atualizar.casa(c, atualizar.DO_GRUPO)
    assert professor("labs/lab3/descricoes/boa.toml")
    assert professor("labs/lab2/README.md") and professor("labs/lab2/preparar.py")
    assert not professor("labs/lab3/descricoes/grupo.toml")
    assert not professor("labs/lab2/execucoes/20261109-010333-rag.md")


def test_removidos_nao_existem_mais_no_template():
    for caminho in atualizar.REMOVIDOS:
        assert not (RAIZ / caminho).exists(), caminho
