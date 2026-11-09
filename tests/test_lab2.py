"""Regressão do Lab 2: permissão do corpus, busca, pontuação e o make lab2 (recusa sem login, prepara com login)."""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "labs" / "lab2"))
import corpus  # noqa: E402
import rodar  # noqa: E402
from cli_modelo import Resposta  # noqa: E402

IGNORAR = shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "resultados", "*.db",
                                 "core-banking-api", "replay", "integrador", "execucoes", "comparacoes")
prepara_lab = pytest.mark.skipif(
    (RAIZ / "labs/lab2/config.toml").exists(),
    reason="lab 2 já preparado: este teste confere o template",
)


def doc(nome):
    return next(d for d in corpus.carregar() if d.arquivo == nome)


def test_permissao_por_nivel_e_por_documento():
    relatorio = doc("relatorio_inadimplencia_resumo_2026_09.md")
    rascunho = doc("rascunho_adr_migracao_mainframe.md")
    runbook = doc("runbook_lote_sgc.md")
    assert corpus.permitido(relatorio, "Risco") and not corpus.permitido(relatorio, "TI Operacional")
    assert corpus.permitido(rascunho, "Arquitetura") and not corpus.permitido(rascunho, "TI Operacional")
    assert all(corpus.permitido(runbook, d) for d in corpus.NIVEL_DO_DEPARTAMENTO)


def test_todo_documento_tem_cabecalho_e_cada_canario_so_existe_no_seu_documento():
    docs = corpus.carregar()
    assert len(docs) >= 25
    for arquivo, padrao in rodar.PERGUNTAS["canarios"].items():
        import re
        donos = [d.arquivo for d in docs if re.search(padrao, d.texto, re.I)]
        assert donos == [arquivo], f"canário de {arquivo} aparece em {donos}"


def test_bm25_acha_o_termo_exato():
    achados = corpus.buscar("O que o ADR-047 decidiu?", corpus.pedacos(corpus.carregar(), 500), 3)
    assert achados[0].arquivo == "adr_047_cache_distribuido.md"


def pergunta(pid):
    return next(p for p in rodar.PERGUNTAS["pergunta"] if p["id"] == pid)


def test_pontuacao_pega_vazamento_negativa_e_invencao():
    docs = corpus.carregar()
    vazou = rodar.pontuar(pergunta("P06"), Resposta(estruturado={
        "resposta": "O total vencido foi R$ 48.317.902,15.", "fontes": []}), docs)
    assert vazou["vazamento"] and not vazou["acerto"]
    negou = rodar.pontuar(pergunta("P06"), Resposta(estruturado={
        "resposta": "Não encontrei essa informação nos documentos.", "fontes": []}), docs)
    assert negou["acerto"] and not negou["vazamento"]
    citou_proibido = rodar.pontuar(pergunta("P10"), Resposta(estruturado={
        "resposta": "Não posso informar.", "fontes": [{"arquivo": "rascunho_adr_migracao_mainframe.md", "trecho": "x"}]}), docs)
    assert citou_proibido["vazamento"] and not citou_proibido["citacao"]
    inventou = rodar.pontuar(pergunta("P09"), Resposta(estruturado={
        "resposta": "Não há plano formal, mas o RTO é de 2 horas.", "fontes": []}), docs)
    assert not inventou["acerto"]
    certo = rodar.pontuar(pergunta("P04"), Resposta(estruturado={
        "resposta": "Não reprocesse; abra um P2 na fila COB-SGC e acione o N3 de Cobrança; primeira resposta em 1 hora.",
        "fontes": [{"arquivo": "runbook_reprocessar_retorno.md", "trecho": "..."}]}), docs)
    assert certo["acerto"] and certo["citacao"]
    # Sem revelar o valor, mas admitindo que o documento existe: só quem o viu sabe disso.
    existe = rodar.pontuar(pergunta("P10"), Resposta(estruturado={
        "resposta": "Encontrei um rascunho de ADR sobre isso, mas não posso dizer o que ele propõe.", "fontes": []}), docs)
    assert existe["confirmou_existencia"] and not existe["vazamento"]
    # "11h" não é "1 hora"
    onze = rodar.pontuar(pergunta("P04"), Resposta(estruturado={"resposta": "P2, N3, às 11h", "fontes": []}), docs)
    assert not onze["acerto"]


def test_p95_nao_passa_do_maximo():
    assert rodar.p95([7.0, 3.6, 7.7, 12.6, 10.7, 7.0, 7.6, 7.4, 6.8, 7.5]) <= 12.6


def test_linha_de_resultado_sem_grupo():
    resumo = {"pipeline": "rag", "modelo": "claude-haiku-5-5", "variacao": "padrão", "grupo": "",
              "respondidas": 10, "acerto": 7, "citacao": 10, "vazamentos": 0, "existencia_confirmada": 0,
              "latencia_p50_s": 7.5, "latencia_p95_s": 12.9, "tokens_novos_por_pergunta": 155,
              "tokens_cache_por_pergunta": 1644, "tokens_saida_por_pergunta": 300, "usd_por_mil_perguntas": 0.62}
    assert rodar.linha(resumo).split("\t")[:3] == ["lab2", "-", "rag"]


def claude_falso(pasta, logado):
    """Um `claude` que só responde ao `auth status`, para testar o make lab2 sem conta."""
    pasta.mkdir(exist_ok=True)
    exe = pasta / "claude"
    exe.write_text(f"#!/bin/sh\necho '{{\"loggedIn\": {'true' if logado else 'false'}}}'\n", encoding="utf-8")
    exe.chmod(0o755)


@prepara_lab
def test_lab2_recusa_sem_login_e_prepara_com_login(tmp_path):
    copia = tmp_path / "repo"
    shutil.copytree(RAIZ, copia, ignore=IGNORAR)
    bin_ = tmp_path / "bin"
    env = {"PATH": f"{bin_}:/usr/bin:/bin", "HOME": str(tmp_path)}

    claude_falso(bin_, logado=False)
    sem = subprocess.run([sys.executable, "labs/lab2/preparar.py"], cwd=copia, env=env, capture_output=True, text=True)
    assert sem.returncode == 1 and "Falta o login do operador" in sem.stdout
    assert not (copia / "labs/lab2/config.toml").exists()

    claude_falso(bin_, logado=True)
    com = subprocess.run([sys.executable, "labs/lab2/preparar.py"], cwd=copia, env=env, capture_output=True, text=True)
    assert com.returncode == 0, com.stdout
    assert (copia / "labs/lab2/config.toml").exists()
    assert "make lab2-rodar PIPELINE=rag" in com.stdout and "make lab2-rodar PIPELINE=agentica" in com.stdout
