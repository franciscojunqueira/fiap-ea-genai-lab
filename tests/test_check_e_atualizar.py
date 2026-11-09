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


def test_aviso_do_agents_so_quando_falta_linha(tmp_path, monkeypatch, capsys):
    template = "# AGENTS.md\n\n- regra A\n- regra B\n"
    monkeypatch.setattr(atualizar, "RAIZ", tmp_path)
    monkeypatch.setattr(atualizar, "git", lambda *args, **kw: template)
    (tmp_path / "AGENTS.md").write_text(template + "\n## Mini-ERP\n- regra do grupo\n", encoding="utf-8")
    atualizar.avisar_agents()
    assert capsys.readouterr().out == ""
    (tmp_path / "AGENTS.md").write_text("# AGENTS.md\n\n- regra A\n", encoding="utf-8")
    atualizar.avisar_agents()
    saida = capsys.readouterr().out
    assert "1 linha(s)" in saida and "- regra B" in saida


def test_atualizar_duas_vezes_sem_commit_nao_bloqueia(tmp_path, monkeypatch, capsys):
    """Piloto de 09/11/2026: a 2ª rodada recusava por arquivos já trazidos (iguais ao template) e sem commit."""
    import subprocess

    def g(pasta, *args):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=pasta, check=True,
                       capture_output=True)

    template, grupo = tmp_path / "template", tmp_path / "grupo"
    (template / "labs/lab3").mkdir(parents=True)
    (template / "labs/lab3/README.md").write_text("v1\n", encoding="utf-8")
    g(tmp_path, "init", "-q", "-b", "main", str(template))
    g(template, "add", "-A")
    g(template, "commit", "-q", "-m", "v1")
    g(tmp_path, "clone", "-q", str(template), str(grupo))
    g(grupo, "remote", "add", "template", str(template))
    (template / "labs/lab3/README.md").write_text("v2\n", encoding="utf-8")
    g(template, "commit", "-q", "-am", "v2")

    monkeypatch.setattr(atualizar, "RAIZ", grupo)
    monkeypatch.setattr(sys, "argv", ["atualizar"])
    monkeypatch.setattr("builtins.input", lambda _: "s")
    atualizar.main()
    assert (grupo / "labs/lab3/README.md").read_text(encoding="utf-8") == "v2\n"
    atualizar.main()   # sem commit entre as rodadas: não pode recusar
    assert "Nada a trazer" in capsys.readouterr().out

    # Alteração do grupo num arquivo do professor, sem commit, continua protegida.
    (grupo / "labs/lab3/README.md").write_text("do grupo\n", encoding="utf-8")
    import pytest
    with pytest.raises(SystemExit, match="alterações sem commit"):
        atualizar.main()
