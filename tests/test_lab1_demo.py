"""Demonstração 2 da Aula 1: a tela é a mesma para a execução e para a gravação do Haiku 4.5."""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "labs" / "lab1"))
import demo  # noqa: E402


def test_replay_do_ticket_mostra_as_quatro_linhas_da_fitness_com_o_teste_passando(capsys):
    assert demo.main(["demo.py", "--replay", "ticket"]) == 0
    saida = capsys.readouterr().out
    assert "etapa ticket: só o ticket" in saida
    assert "1. Arquivos que o agente mudou: 1" in saida and "mini-erp/app/routes/pedidos.py" in saida
    assert "2. Teste do ticket: PASS" in saida
    assert "3. Fitness function (camadas): FAIL, 4 linha(s)" in saida
    assert saida.count("chama db.") == 3 and "importa Estoque, Pedido" in saida
    assert "5. O que o agente disse no resumo (trecho)" in saida
    assert "6. Tokens e tempo: 470.680 de entrada, 3.975 de saída · 66 s · 16 turnos" in saida
    assert "gravação de 13/10/2026, Haiku 4.5" in saida
    assert "Só o sensor de arquitetura viu o erro" not in saida and "Pergunta para a turma" in saida
    assert "padrão do projeto (similar a faturas.py)" in saida


def test_replay_sem_etapa_mostra_as_duas_na_ordem(capsys):
    assert demo.main(["demo.py", "--replay"]) == 0
    saida = capsys.readouterr().out
    assert saida.index("etapa ticket") < saida.index("etapa harness")
    harness = saida.split("etapa harness")[1]
    assert "3. Fitness function (camadas): PASS" in harness
    assert "2 arquivos" not in harness and "Arquivos que o agente mudou: 2" in harness
    assert "mini-erp/app/services/pedidos.py" in harness and "401.076 de entrada" in harness
    assert "Nota: na gravação" in harness


def test_tela_de_uma_execucao_ao_vivo_tem_o_mesmo_formato():
    m = {"etapa": "ticket", "modelo": "claude-haiku-5-5", "origem": "ao vivo", "arquivos": [], "aceite": "FAIL",
         "aceite_resumo": "2 failed, 2 passed", "fitness": [], "resumo": "Não consegui.\n\nTentei.", "tokens_entrada": 1234567,
         "tokens_saida": 89, "duracao_s": 12, "turnos": 3}
    tela = demo.tela(m)
    assert "1. Arquivos que o agente mudou: nenhum" in tela
    assert "2. Teste do ticket: FAIL (2 failed, 2 passed)" in tela
    assert "1.234.567 de entrada, 89 de saída · 12 s · 3 turnos" in tela
    assert "Pergunta para a turma:" in tela and "Leitura:" not in tela
    assert "não rodou o sensor" in tela


def test_etapa_invalida_ou_ausente_nao_chama_modelo(capsys):
    assert demo.main(["demo.py"]) == 2 and "Faltou a etapa" in capsys.readouterr().out
    assert demo.main(["demo.py", "nada"]) == 2
    assert demo.main(["demo.py", "--replay", "nada"]) == 2


def test_o_modelo_da_demo_vem_da_configuracao(monkeypatch):
    monkeypatch.delenv("MODELO", raising=False)
    assert demo.modelo_da_demo() == "claude-haiku-5-5"


def test_o_loop_do_agente_vem_do_stream_json_no_replay_do_harness(capsys):
    assert demo.main(["demo.py", "--replay", "harness"]) == 0
    saida = capsys.readouterr().out
    assert "O agente rodou o sensor 2 vezes" in saida
    assert "1ª: camadas FAIL em 4 linha(s), teste do ticket FAIL → 2ª: camadas PASS, teste do ticket PASS" in saida


def test_execucoes_do_sensor_le_make_e_fitness_direta():
    import json
    def uso(i, cmd):
        return json.dumps({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": i, "name": "Bash", "input": {"command": cmd}}]}})
    def res(i, texto):
        return json.dumps({"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": i, "content": texto}]}})
    ev = "\n".join([
        uso("a", "make lab1-check 2>&1 | head -100"),
        res("a", "[OK] 3. x\n[FALHA] 4. Fitness function 'camadas'\n        camadas: a.py:5 importa\n        camadas: a.py:9 chama db\n[OK] 6. Testes"),
        uso("b", "python labs/lab1/fitness_camadas.py"), res("b", "camadas: PASS"),
        "{\"type\": \"result\"}", "linha que não é json"])
    assert demo.execucoes_do_sensor(ev) == [{"camadas": "FAIL", "linhas": 2, "aceite": "PASS"}, {"camadas": "PASS", "linhas": 0, "aceite": None}]
    assert "O agente não rodou o sensor" in "\n".join(demo.linhas_do_loop([]))


def test_o_trecho_do_resumo_mostra_a_frase_do_padrao_do_projeto():
    texto = "\n".join(f"linha {i}" for i in range(30)) + "\nA implementação segue o padrão do projeto (similar a `faturas.py`)."
    assert any("padrão do projeto (similar a faturas.py)" in l for l in demo._trecho(texto))


def test_o_modelo_pode_ser_escolhido_por_variavel(monkeypatch):
    monkeypatch.setenv("MODELO", "claude-haiku-4-5")
    assert demo.modelo_da_demo() == "claude-haiku-4-5"
