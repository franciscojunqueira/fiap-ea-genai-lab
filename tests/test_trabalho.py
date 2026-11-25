"""Trabalho final (make trabalho, trabalho-adr e trabalho-entregar): o preparar não apaga o que o grupo escreveu;
o ADR usa os fatos do caso; o entregar só envia com PASS."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "integrador" / "scripts"))
import checar_entrega  # noqa: E402
import trabalho  # noqa: E402


def repo(tmp_path):
    shutil.copytree(RAIZ / "integrador" / "pacote", tmp_path / "integrador" / "pacote")
    for pasta in ("replay", "labs"):
        shutil.copytree(RAIZ / pasta, tmp_path / pasta, ignore=shutil.ignore_patterns("execucoes", "estado", "comparacoes"))
    return tmp_path


DESIGN = RAIZ / "integrador" / "pacote" / "01-design.md"
# Depois do `make trabalho` (repositório de grupo), o 01-design.md já está preparado: estes testes conferem o template.
so_no_template = pytest.mark.skipif("sgc:pedir_reprocessamento_retorno" in DESIGN.read_text(encoding="utf-8"),
                                    reason="Pacote já preparado: estes testes conferem o modelo do template")


@so_no_template
def test_preparar_troca_so_as_secoes_vazias_e_e_idempotente():
    original = DESIGN.read_text(encoding="utf-8")
    novo, preparadas, mantidas = trabalho.preparar_design(original)
    assert preparadas == ["Decisão de conhecimento", "Contrato MCP"] and mantidas == []
    partes = checar_entrega.secoes(novo)
    assert "sgc:pedir_reprocessamento_retorno" in partes["Contrato MCP"]
    assert checar_entrega.sem_comentarios(partes["Decisão de conhecimento"]).count("PREENCHER") == 8
    assert checar_entrega.sem_comentarios(partes["Contrato MCP"]).count("PREENCHER") == 2
    # o resto do arquivo não muda
    for nome, corpo in checar_entrega.secoes(original).items():
        if nome not in trabalho.MODELOS:
            assert partes[nome] == corpo
    # rodar de novo não muda nada: as seções já não estão vazias
    de_novo, preparadas2, mantidas2 = trabalho.preparar_design(novo)
    assert de_novo == novo and preparadas2 == [] and len(mantidas2) == 2


@so_no_template
def test_preparar_nunca_apaga_o_texto_do_grupo():
    original = DESIGN.read_text(encoding="utf-8")
    do_grupo = original.replace("PREENCHER\n\n## Contrato MCP", "O Bússola usa RAG para busca exata.\n\n## Contrato MCP", 1)
    assert do_grupo != original
    novo, preparadas, mantidas = trabalho.preparar_design(do_grupo)
    assert "O Bússola usa RAG para busca exata." in novo
    assert mantidas == ["Decisão de conhecimento"] and preparadas == ["Contrato MCP"]


def test_numeros_do_lab2_preferem_as_execucoes_do_grupo(tmp_path):
    pasta = tmp_path / "labs/lab2/execucoes"
    pasta.mkdir(parents=True)
    for nome, pipeline, acerto in [("20261109-070818-rag", "rag", 7), ("replay-x-rag", "rag", 6),
                                   ("replay-x-agentica", "agentica", 10)]:
        (pasta / f"{nome}.json").write_text(json.dumps({"resumo": {"pipeline": pipeline, "acerto": acerto}}), encoding="utf-8")
    n = trabalho.numeros_lab2(tmp_path)
    assert n["rag"]["acerto"] == 7 and not n["rag"]["replay"]
    assert n["agentica"]["acerto"] == 10 and n["agentica"]["replay"]


def test_link_web():
    assert trabalho.link_web("git@github.com:turma/ea-genai-grupo-2.git\n") == "https://github.com/turma/ea-genai-grupo-2"
    assert trabalho.link_web("https://x-access-token:abc@github.com/turma/g.git") == "https://github.com/turma/g"


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
    assert trabalho.entregar(repo, conferir=lambda: 1) == 1
    assert "Nada foi enviado" in capsys.readouterr().out
    assert subprocess.run(["git", "log", "--oneline"], cwd=remoto, capture_output=True, text=True).stdout.count("\n") == 1


def test_entregar_com_pass_faz_commit_push_e_mostra_o_sha(tmp_path, capsys):
    repo, remoto = _repo_com_remoto(tmp_path)
    (repo / "b.txt").write_text("2\n", encoding="utf-8")
    assert trabalho.entregar(repo, conferir=lambda: 0) == 0
    sha = subprocess.run(["git", "rev-parse", "main"], cwd=remoto, capture_output=True, text=True).stdout.strip()
    saida = capsys.readouterr().out
    assert sha and f"SHA:  {sha}" in saida and "Enviado" in saida


def test_cada_espaco_para_preencher_fica_numa_linha_so():
    """Um [PREENCHER: ...] quebrado em duas linhas é fácil de trocar pela metade."""
    import re
    for modelo in trabalho.MODELOS.values():
        for linha in modelo.splitlines():
            assert len(re.findall(r"\[PREENCHER[^\]]*\]", linha)) == linha.count("[PREENCHER"), linha


@so_no_template
def test_numeros_do_replay_dizem_demonstracao_do_professor(tmp_path, capsys):
    raiz = repo(tmp_path)
    pasta = raiz / "labs/lab2/execucoes"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "replay-x-rag.json").write_text(json.dumps({"resumo": {"pipeline": "rag", "acerto": 6}}), encoding="utf-8")
    trabalho.preparar(raiz)
    saida = capsys.readouterr().out
    assert "números da demonstração do professor" in saida
    assert "preparada  01-design.md" in saida and "preparado  02-qualidade.md" in saida


def _repo_do_adr(tmp_path):
    for rel in ("config/modelos.toml", ".agents/skills/escrevendo-adrs/scripts/validar_adr.py", "integrador/caso.md"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(RAIZ / rel, tmp_path / rel)
    (tmp_path / "docs/adr").mkdir(parents=True)
    return tmp_path


def test_adr_sem_decisao_nao_chama_o_agente(tmp_path, capsys):
    chamadas = []
    assert trabalho.adr("  ", tmp_path, chamar=lambda *a: chamadas.append(a), tema="sgc") == 2
    assert not chamadas and "Faltou a decisão" in capsys.readouterr().out


def test_adr_roda_o_validador_no_arquivo_que_o_agente_escreveu(tmp_path, capsys):
    raiz = _repo_do_adr(tmp_path)
    exemplo = RAIZ / ".agents/skills/escrevendo-adrs/reference/ADR-003-armazenamento-de-alertas.md"
    pedidos = []

    def agente(prompt, r, modelo):
        pedidos.append((prompt, modelo))
        shutil.copy(exemplo, r / "docs/adr/ADR-003-acesso-ao-sgc.md")
        return {"result": "ok", "num_turns": 7, "duracao_s": 31}

    assert trabalho.adr("O Bússola lê uma cópia diária do banco do SGC", raiz, chamar=agente, tema="sgc") == 0
    saida = capsys.readouterr().out
    assert "docs/adr/ADR-003-acesso-ao-sgc.md" in saida and "Resultado do validador: PASS" in saida
    assert "O Bússola lê uma cópia diária do banco do SGC" in pedidos[0][0] and "escrevendo-adrs" in pedidos[0][0]
    assert pedidos[0][1] == "claude-sonnet-5-5"


def test_adr_com_fail_no_validador_ou_sem_arquivo_devolve_erro(tmp_path, capsys):
    raiz = _repo_do_adr(tmp_path)

    def adr_ruim(prompt, r, modelo):
        (r / "docs/adr/ADR-001-ruim.md").write_text("# ADR-001: ruim\n", encoding="utf-8")
        return {"result": "ok"}

    assert trabalho.adr("x", raiz, chamar=adr_ruim, tema="modelo") == 1
    saida = capsys.readouterr().out
    assert "Resultado do validador: FAIL" in saida and "rm docs/adr/ADR-001-ruim.md" in saida
    assert trabalho.adr("x", _repo_do_adr(tmp_path / "outro"), chamar=lambda *a: {"result": "não escrevi"}, tema="modelo") == 1
    assert "não escreveu nenhum ADR" in capsys.readouterr().out
    assert trabalho.adr("x", raiz, chamar=lambda *a: {"erro": "sem resposta em 600 s"}, tema="modelo") == 1
    assert "sem resposta" in capsys.readouterr().out


def test_o_agente_do_adr_so_escreve_em_docs_adr():
    ferramentas = trabalho.FERRAMENTAS_ADR.split(",")
    escrita = [f for f in ferramentas if f.startswith(("Write", "Edit"))]
    assert escrita == ["Write(docs/adr/**)", "Edit(docs/adr/**)"]
    assert not any(f.startswith("Bash") and "validar_adr.py" not in f for f in ferramentas)


def test_adr_sem_tema_nao_chama_o_agente(tmp_path, capsys):
    chamadas = []
    assert trabalho.adr("uma decisão", tmp_path, chamar=lambda *a: chamadas.append(a), tema="") == 2
    assert not chamadas and "TEMA=sgc" in capsys.readouterr().out


def test_o_pedido_do_adr_do_sgc_usa_os_fatos_do_caso_e_o_do_modelo_usa_o_pacote():
    sgc = trabalho.PEDIDOS_ADR["sgc"].format(decisao="uma decisão")
    assert "integrador/caso.md, seção 1" in sgc and "S1 a S6" in sgc and "use como fato só" in sgc
    assert "engenharia-reversa" not in sgc and "invencoes" not in sgc
    modelo = trabalho.PEDIDOS_ADR["modelo"].format(decisao="uma decisão")
    assert "02-qualidade.md" in modelo and "03-economia.md" in modelo
    for pedido in (sgc, modelo):
        assert "uma decisão" in pedido and "escrevendo-adrs" in pedido and "Escreva só em docs/adr/" in pedido


def test_os_fatos_do_sgc_existem_no_caso_e_citam_linhas_que_existem():
    caso = (RAIZ / "integrador/caso.md").read_text(encoding="utf-8")
    assert "### O que o SGC faz de fato" in caso
    fatos = re.findall(r"^\| (S\d) \|.*?\| (.*?) \|[^|]*\|$", caso, flags=re.M)
    assert [f for f, _ in fatos] == ["S1", "S2", "S3", "S4", "S5", "S6"]
    for _, onde in fatos:
        for arquivo, ini, fim in re.findall(r"`([\w./-]+):(\d+)(?:-(\d+))?`", onde):
            linhas = (RAIZ / "integrador/legado" / arquivo).read_text(encoding="utf-8").splitlines()
            assert 1 <= int(ini) <= len(linhas) and (not fim or int(fim) <= len(linhas)), (arquivo, ini, fim)


def test_adr_tenta_de_novo_uma_vez_com_pedido_direto_se_o_agente_nao_escreveu(tmp_path, capsys):
    raiz = _repo_do_adr(tmp_path)
    exemplo = RAIZ / ".agents/skills/escrevendo-adrs/reference/ADR-003-armazenamento-de-alertas.md"
    pedidos = []

    def agente(prompt, r, modelo):
        pedidos.append(prompt)
        if len(pedidos) == 2:
            shutil.copy(exemplo, r / "docs/adr/ADR-003-acesso-ao-sgc.md")
        return {"result": "descrevi"}

    assert trabalho.adr("uma decisão", raiz, chamar=agente, tema="sgc") == 0
    assert len(pedidos) == 2 and pedidos[1].startswith("Escreva agora o arquivo do ADR em docs/adr/; não descreva, escreva.")
    assert "Tentando de novo" in capsys.readouterr().out
    # sem escrever nas duas vezes: só duas chamadas, e o grupo é mandado rodar de novo
    outro = _repo_do_adr(tmp_path / "x")
    pedidos.clear()
    assert trabalho.adr("uma decisão", outro, chamar=lambda p, *a: pedidos.append(p) or {"result": "não"}, tema="sgc") == 1
    assert len(pedidos) == 2 and "Rodem o comando de novo" in capsys.readouterr().out


def test_modelos_do_pacote_iguais_aos_do_script():
    for nome in trabalho.SECAO:
        pacote = (RAIZ / "integrador/pacote" / nome).read_text()
        if "<!-- Prontos: testes do professor" in pacote:
            continue   # repositório de grupo depois do make trabalho: o arquivo já é do grupo (piloto de 16/11/2026)
        assert pacote == (RAIZ / "integrador/scripts/modelos_trabalho" / nome).read_text()


def test_preparar_preenche_os_resultados(tmp_path):
    raiz = repo(tmp_path)
    trabalho.preparar(raiz)
    q = (raiz / "integrador/pacote/02-qualidade.md").read_text()
    e = (raiz / "integrador/pacote/03-economia.md").read_text()
    assert "pass^3" in q and "Agente único" in q and "Haiku com RAG" in q
    assert "roteado" in e and "ESTIMATIVA" in e and "PTAX" in e
    assert "[PREENCHER:" in q and "[PREENCHER:" in e          # as decisões continuam para o grupo


def test_preparar_nao_apaga_o_que_o_grupo_escreveu(tmp_path):
    raiz = repo(tmp_path)
    antigo = "# Qualidade\n\n## Critério de aprovação\n\nO grupo já escreveu aqui.\n"
    (raiz / "integrador/pacote/02-qualidade.md").write_text(antigo)
    msg = trabalho.preparar_arquivo(raiz, "02-qualidade.md", trabalho.resultados_qualidade,
                                      {n: (RAIZ / "integrador/scripts/modelos_trabalho" / n).read_text() for n in trabalho.SECAO})
    assert "mantido" in msg and (raiz / "integrador/pacote/02-qualidade.md").read_text() == antigo


def test_modelo_antigo_intocado_vira_o_novo(tmp_path):
    raiz = repo(tmp_path)
    (raiz / "integrador/pacote/03-economia.md").write_text("# Economia\n\n## Premissas\n\nPREENCHER\n\n## Go/no-go\n\nPREENCHER\n")
    trabalho.preparar(raiz)
    assert "## Go/no-go por cenário" in (raiz / "integrador/pacote/03-economia.md").read_text()


def test_secao_igual_ao_modelo_antigo_da_atividade2_vira_o_modelo_novo():
    """Grupo que rodou o make atividade2 e não escreveu nada: o texto antigo citava a Atividade 1 e é trocado."""
    antigo = "# Design\n\n## Decisão de conhecimento\n\n" + trabalho.MODELOS_ANTIGOS["Decisão de conhecimento"] + \
             "\n\n## Contrato MCP\n\n" + trabalho.MODELOS_ANTIGOS["Contrato MCP"] + "\n"
    novo, preparadas, mantidas = trabalho.preparar_design(antigo)
    assert preparadas == ["Decisão de conhecimento", "Contrato MCP"] and mantidas == []
    assert "Atividade" not in novo and "fato S4" in novo
