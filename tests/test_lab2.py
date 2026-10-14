"""Regressão do Lab 2: permissão do corpus, busca, pontuação e o make lab2-check (FAIL útil, atalhos, PASS)."""
import json
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
    (RAIZ / "labs/lab2/decisao.md").exists(),
    reason="lab 2 já preparado: estes testes conferem o template; o grupo usa make lab2-check",
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


def execucao(lab, pipeline, variacao="padrão", nome=None):
    resumo = {"pipeline": pipeline, "modelo": "claude-haiku-5-5", "variacao": variacao, "grupo": "Grupo 9",
              "respondidas": 10, "acerto": 7, "citacao": 10, "vazamentos": 0, "latencia_p50_s": 7.5,
              "latencia_p95_s": 13.5, "tokens_entrada_por_pergunta": 1795, "tokens_saida_por_pergunta": 1274}
    pasta = lab / "execucoes"
    pasta.mkdir(exist_ok=True)
    (pasta / f"{nome or pipeline + variacao}.json").write_text(json.dumps({"resumo": resumo, "respostas": []}), encoding="utf-8")
    return rodar.linha(resumo)


def rodar_check(copia):
    return subprocess.run([sys.executable, "labs/lab2/checar.py"], cwd=copia, capture_output=True, text=True)


@prepara_lab
def test_lab2_check_falha_no_inicio_e_passa_preenchido(tmp_path):
    copia = tmp_path / "repo"
    shutil.copytree(RAIZ, copia, ignore=IGNORAR)
    lab = copia / "labs/lab2"
    assert "Rode `make lab2` primeiro" in rodar_check(copia).stdout

    assert subprocess.run([sys.executable, "labs/lab2/preparar.py"], cwd=copia, capture_output=True).returncode == 0
    preparado = rodar_check(copia)
    assert preparado.returncode == 1
    assert "make lab2-rodar PIPELINE=rag" in preparado.stdout
    assert "Mudem UM valor" in preparado.stdout
    assert "sem resposta em: Hipótese" in preparado.stdout

    linhas = [execucao(lab, "rag"), execucao(lab, "agentica"), execucao(lab, "rag", "top_k=8")]
    decisao = (lab / "decisao.md").read_text(encoding="utf-8")
    preenchido = []
    for l in decisao.splitlines():
        if l.startswith("<Relator"):
            preenchido += linhas
        elif l.startswith("| |"):
            preenchido += [f"| P0{i} | rag | certo | conferido no runbook | confere |" for i in range(1, 4)]
            preenchido.append("| P04 | rag | errado | faltou o prazo do P2 | confere |")
        elif l.startswith("<"):
            preenchido.append("Texto do grupo.")
        else:
            preenchido.append(l)
    (lab / "decisao.md").write_text("\n".join(preenchido), encoding="utf-8")
    final = rodar_check(copia)
    assert final.returncode == 0, final.stdout
    assert "lab2-check: PASS (5/5 itens)" in final.stdout

    # Atalho 1: editar os números colados
    (lab / "decisao.md").write_text((lab / "decisao.md").read_text(encoding="utf-8").replace("7/10", "10/10"), encoding="utf-8")
    assert "iguais às que o script imprimiu" in rodar_check(copia).stdout
    # Atalho 2: mexer nas perguntas
    perguntas = lab / "perguntas.toml"
    perguntas.write_text(perguntas.read_text(encoding="utf-8").replace("'Redis', ", ""), encoding="utf-8")
    assert "Alterado: labs/lab2/perguntas.toml" in rodar_check(copia).stdout
