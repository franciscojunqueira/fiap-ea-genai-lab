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
    assert professor("integrador/atividade1/saida_agente/invencoes.md") and professor("integrador/scripts/atividade1.py")
    assert professor("labs/lab1/demo.py")
    assert not professor("integrador/pacote/engenharia-reversa/regras.md")
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


def test_atualizar_traz_arquivo_novo_mesmo_fora_da_lista_do_professor(tmp_path, monkeypatch, capsys):
    """Piloto de 16/11/2026: os modelos novos do pacote não chegavam a quem criou o repositório antes deles."""
    import subprocess

    def g(pasta, *args):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=pasta, check=True,
                       capture_output=True)

    template, grupo = tmp_path / "template", tmp_path / "grupo"
    (template / "integrador/pacote").mkdir(parents=True)
    (template / "integrador/pacote/01-design.md").write_text("modelo\n", encoding="utf-8")
    g(tmp_path, "init", "-q", "-b", "main", str(template))
    g(template, "add", "-A")
    g(template, "commit", "-q", "-m", "v1")
    g(tmp_path, "clone", "-q", str(template), str(grupo))
    g(grupo, "remote", "add", "template", str(template))
    (grupo / "integrador/pacote/01-design.md").write_text("do grupo\n", encoding="utf-8")
    g(grupo, "commit", "-q", "-am", "grupo")
    (template / "integrador/pacote/02-qualidade.md").write_text("modelo novo\n", encoding="utf-8")
    (template / "docs/adr").mkdir(parents=True)
    (template / "docs/adr/exemplo.md").write_text("exemplo\n", encoding="utf-8")
    g(template, "add", "-A")
    g(template, "commit", "-q", "-m", "v2")

    monkeypatch.setattr(atualizar, "RAIZ", grupo)
    monkeypatch.setattr(sys, "argv", ["atualizar"])
    monkeypatch.setattr("builtins.input", lambda _: "s")
    atualizar.main()
    saida = capsys.readouterr().out
    assert (grupo / "integrador/pacote/02-qualidade.md").read_text(encoding="utf-8") == "modelo novo\n"
    assert "(novo no template)" in saida
    assert (grupo / "integrador/pacote/01-design.md").read_text(encoding="utf-8") == "do grupo\n"
    assert not (grupo / "docs/adr/exemplo.md").exists()   # padrão do grupo: nunca trazido


def test_atualizar_troca_modelo_antigo_que_o_grupo_nao_editou(tmp_path, monkeypatch, capsys):
    """Piloto de 16/11/2026: o 02-qualidade.md antigo, intocado, ficava, e o make atividade3 o recusava."""
    import subprocess

    def g(pasta, *args):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=pasta, check=True,
                       capture_output=True)

    template, grupo = tmp_path / "template", tmp_path / "grupo"
    (template / "integrador/pacote").mkdir(parents=True)
    (template / "integrador/pacote/02-qualidade.md").write_text("modelo v1\n", encoding="utf-8")
    (template / "integrador/pacote/03-economia.md").write_text("modelo v1\n", encoding="utf-8")
    g(tmp_path, "init", "-q", "-b", "main", str(template))
    g(template, "add", "-A")
    g(template, "commit", "-q", "-m", "v1")
    g(tmp_path, "clone", "-q", str(template), str(grupo))
    g(grupo, "remote", "add", "template", str(template))
    (grupo / "integrador/pacote/03-economia.md").write_text("o grupo escreveu\n", encoding="utf-8")
    g(grupo, "commit", "-q", "-am", "grupo")
    for nome in ("02-qualidade.md", "03-economia.md"):
        (template / "integrador/pacote" / nome).write_text("modelo v2\n", encoding="utf-8")
    g(template, "commit", "-q", "-am", "v2")

    monkeypatch.setattr(atualizar, "RAIZ", grupo)
    monkeypatch.setattr(sys, "argv", ["atualizar"])
    monkeypatch.setattr("builtins.input", lambda _: "s")
    atualizar.main()
    assert "(modelo antigo, sem edição do grupo)" in capsys.readouterr().out
    assert (grupo / "integrador/pacote/02-qualidade.md").read_text(encoding="utf-8") == "modelo v2\n"
    assert (grupo / "integrador/pacote/03-economia.md").read_text(encoding="utf-8") == "o grupo escreveu\n"


def _par_template_grupo(tmp_path, monkeypatch):
    """Template com 3 arquivos e um clone (grupo) com o remoto 'template'; devolve (template, grupo, g)."""
    import subprocess
    for chave in ("NAME", "EMAIL"):   # o commit do script usa o git puro: dá identidade pelo ambiente
        monkeypatch.setenv(f"GIT_AUTHOR_{chave}", "t")
        monkeypatch.setenv(f"GIT_COMMITTER_{chave}", "t@t" if chave == "EMAIL" else "t")

    def g(pasta, *args):
        return subprocess.run(["git", *args], cwd=pasta, check=True, capture_output=True, text=True).stdout

    template, grupo = tmp_path / "template", tmp_path / "grupo"
    (template / "labs/lab3").mkdir(parents=True)
    (template / "integrador/pacote").mkdir(parents=True)
    (template / "labs/lab2").mkdir(parents=True)
    (template / "labs/lab3/README.md").write_text("v1\n", encoding="utf-8")
    (template / "labs/lab2/checar.py").write_text("v1\n", encoding="utf-8")
    (template / "integrador/pacote/01-design.md").write_text("modelo\n", encoding="utf-8")
    g(tmp_path, "init", "-q", "-b", "main", str(template))
    g(template, "add", "-A")
    g(template, "commit", "-q", "-m", "v1")
    g(tmp_path, "clone", "-q", str(template), str(grupo))
    g(grupo, "remote", "add", "template", str(template))
    return template, grupo, g


def test_atualizar_commita_so_a_rodada_e_deixa_o_trabalho_do_grupo_fora(tmp_path, monkeypatch, capsys):
    """16/11/2026: o commit automático leva os arquivos trazidos e removidos e nada além; sem push."""
    template, grupo, g = _par_template_grupo(tmp_path, monkeypatch)
    (template / "labs/lab3/README.md").write_text("v2\n", encoding="utf-8")
    (template / "labs/lab2/checar.py").unlink()   # saiu do template: o script o remove do grupo
    g(template, "add", "-A")
    g(template, "commit", "-q", "-m", "v2")
    # Trabalho do grupo, sem commit, em arquivo que o template não mexeu (e um arquivo novo qualquer).
    (grupo / "integrador/pacote/01-design.md").write_text("do grupo\n", encoding="utf-8")
    (grupo / "anotacao.txt").write_text("rascunho\n", encoding="utf-8")
    antes = g(grupo, "rev-parse", "HEAD").strip()

    monkeypatch.setattr(atualizar, "RAIZ", grupo)
    monkeypatch.setattr(sys, "argv", ["atualizar"])
    monkeypatch.setattr("builtins.input", lambda _: "s")
    atualizar.main()
    saida = capsys.readouterr().out

    assert g(grupo, "rev-list", "--count", f"{antes}..HEAD").strip() == "1"
    levados = set(g(grupo, "show", "--name-only", "--format=", "HEAD").split())
    assert levados == {"labs/lab3/README.md", "labs/lab2/checar.py"}
    assert (grupo / "integrador/pacote/01-design.md").read_text(encoding="utf-8") == "do grupo\n"   # intacto
    assert (grupo / "anotacao.txt").exists()
    restante = set(l[3:] for l in g(grupo, "status", "--porcelain", "--untracked-files=all").splitlines())
    assert restante == {"integrador/pacote/01-design.md", "anotacao.txt"}   # ainda sem commit
    assert "o commit já foi feito" in saida and "git push" in saida


def test_atualizar_sem_mudancas_nao_faz_commit_vazio(tmp_path, monkeypatch, capsys):
    template, grupo, g = _par_template_grupo(tmp_path, monkeypatch)
    antes = g(grupo, "rev-parse", "HEAD").strip()
    monkeypatch.setattr(atualizar, "RAIZ", grupo)
    monkeypatch.setattr(sys, "argv", ["atualizar"])
    monkeypatch.setattr("builtins.input", lambda _: "s")
    atualizar.main()
    assert "Nada a trazer" in capsys.readouterr().out
    assert g(grupo, "rev-parse", "HEAD").strip() == antes


def test_atualizar_commita_sobras_de_rodada_antiga_sem_levar_edicao_do_grupo(tmp_path, monkeypatch, capsys):
    """Grupo que rodou a versão antiga do script: os arquivos já trazidos ficaram sem commit e a rodada nova não os
    via. O commit os leva (estão iguais ao template); o arquivo editado pelo grupo continua de fora."""
    template, grupo, g = _par_template_grupo(tmp_path, monkeypatch)
    (template / "labs/lab3/README.md").write_text("v2\n", encoding="utf-8")
    g(template, "commit", "-q", "-am", "v2")
    g(grupo, "fetch", "-q", "template")
    g(grupo, "checkout", "template/main", "--", "labs/lab3/README.md")   # o que a versão antiga fazia
    (grupo / "integrador/pacote/01-design.md").write_text("do grupo\n", encoding="utf-8")
    monkeypatch.setattr(atualizar, "RAIZ", grupo)
    monkeypatch.setattr(sys, "argv", ["atualizar"])
    monkeypatch.setattr("builtins.input", lambda _: "s")
    atualizar.main()
    assert "Nada a trazer" in capsys.readouterr().out
    assert g(grupo, "show", "--name-only", "--format=", "HEAD").split() == ["labs/lab3/README.md"]
    assert g(grupo, "status", "--porcelain").strip() == "M integrador/pacote/01-design.md"
