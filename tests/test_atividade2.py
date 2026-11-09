"""Atividade 2 em dois comandos: o preparar não apaga o que o grupo escreveu; o entregar só envia com PASS."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "integrador" / "scripts"))
import atividade2  # noqa: E402
import checar_entrega  # noqa: E402

DESIGN = RAIZ / "integrador" / "pacote" / "01-design.md"


def test_preparar_troca_so_as_secoes_vazias_e_e_idempotente():
    original = DESIGN.read_text(encoding="utf-8")
    novo, preparadas, mantidas = atividade2.preparar_design(original)
    assert preparadas == ["Decisão de conhecimento", "Contrato MCP"] and mantidas == []
    partes = checar_entrega.secoes(novo)
    assert "sgc:pedir_reprocessamento_retorno" in partes["Contrato MCP"]
    assert checar_entrega.sem_comentarios(partes["Decisão de conhecimento"]).count("PREENCHER") == 8
    assert checar_entrega.sem_comentarios(partes["Contrato MCP"]).count("PREENCHER") == 2
    # o resto do arquivo não muda
    for nome, corpo in checar_entrega.secoes(original).items():
        if nome not in atividade2.MODELOS:
            assert partes[nome] == corpo
    # rodar de novo não muda nada: as seções já não estão vazias
    de_novo, preparadas2, mantidas2 = atividade2.preparar_design(novo)
    assert de_novo == novo and preparadas2 == [] and len(mantidas2) == 2


def test_preparar_nunca_apaga_o_texto_do_grupo():
    original = DESIGN.read_text(encoding="utf-8")
    do_grupo = original.replace("PREENCHER\n\n## Contrato MCP", "O Bússola usa RAG para busca exata.\n\n## Contrato MCP", 1)
    assert do_grupo != original
    novo, preparadas, mantidas = atividade2.preparar_design(do_grupo)
    assert "O Bússola usa RAG para busca exata." in novo
    assert mantidas == ["Decisão de conhecimento"] and preparadas == ["Contrato MCP"]


def test_numeros_do_lab2_preferem_as_execucoes_do_grupo(tmp_path):
    pasta = tmp_path / "labs/lab2/execucoes"
    pasta.mkdir(parents=True)
    for nome, pipeline, acerto in [("20261109-070818-rag", "rag", 7), ("replay-x-rag", "rag", 6),
                                   ("replay-x-agentica", "agentica", 10)]:
        (pasta / f"{nome}.json").write_text(json.dumps({"resumo": {"pipeline": pipeline, "acerto": acerto}}), encoding="utf-8")
    n = atividade2.numeros_lab2(tmp_path)
    assert n["rag"]["acerto"] == 7 and not n["rag"]["replay"]
    assert n["agentica"]["acerto"] == 10 and n["agentica"]["replay"]


def test_link_web():
    assert atividade2.link_web("git@github.com:turma/ea-genai-grupo-2.git\n") == "https://github.com/turma/ea-genai-grupo-2"
    assert atividade2.link_web("https://x-access-token:abc@github.com/turma/g.git") == "https://github.com/turma/g"


def _repo_com_remoto(tmp_path):
    def g(pasta, *args):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *args], cwd=pasta, check=True, capture_output=True)
    remoto, repo = tmp_path / "remoto.git", tmp_path / "repo"
    g(tmp_path, "init", "-q", "--bare", "-b", "main", str(remoto))
    g(tmp_path, "init", "-q", "-b", "main", str(repo))
    (repo / "a.txt").write_text("1\n", encoding="utf-8")
    g(repo, "add", "-A")
    g(repo, "commit", "-q", "-m", "inicio")
    g(repo, "remote", "add", "origin", str(remoto))
    g(repo, "push", "-q", "-u", "origin", "main")
    subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
    return repo, remoto


def test_entregar_nao_envia_com_fail(tmp_path, capsys):
    repo, remoto = _repo_com_remoto(tmp_path)
    (repo / "b.txt").write_text("2\n", encoding="utf-8")
    assert atividade2.entregar(repo, conferir=lambda: 1) == 1
    assert "Nada foi enviado" in capsys.readouterr().out
    assert subprocess.run(["git", "log", "--oneline"], cwd=remoto, capture_output=True, text=True).stdout.count("\n") == 1


def test_entregar_com_pass_faz_commit_push_e_mostra_o_sha(tmp_path, capsys):
    repo, remoto = _repo_com_remoto(tmp_path)
    (repo / "b.txt").write_text("2\n", encoding="utf-8")
    assert atividade2.entregar(repo, conferir=lambda: 0) == 0
    sha = subprocess.run(["git", "rev-parse", "main"], cwd=remoto, capture_output=True, text=True).stdout.strip()
    saida = capsys.readouterr().out
    assert sha and f"SHA:  {sha}" in saida and "Enviado" in saida


def test_cada_espaco_para_preencher_fica_numa_linha_so():
    """Um [PREENCHER: ...] quebrado em duas linhas é fácil de trocar pela metade."""
    import re
    for modelo in atividade2.MODELOS.values():
        for linha in modelo.splitlines():
            assert len(re.findall(r"\[PREENCHER[^\]]*\]", linha)) == linha.count("[PREENCHER"), linha
