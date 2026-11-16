"""Demonstrações da Aula 3 (Labs 4 e 5) sem chamar modelo: custo, gateway, eval e orquestração."""
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "labs" / "lab5"))
sys.path.insert(0, str(RAIZ / "labs" / "lab4"))

import gateway  # noqa: E402
import orquestrar  # noqa: E402


def tco(divisao):
    r = subprocess.run([sys.executable, str(RAIZ / "labs" / "lab5" / "tco.py"), "--divisao", divisao],
                       capture_output=True, text=True, check=True)
    return r.stdout


def test_tco_mostra_veredito_com_margem_e_estimativa():
    # O veredito depende do câmbio do dia (premissas.toml); o teste confere a forma, não o resultado.
    linha_alvo = tco("roteado").split("Alvo")[1].splitlines()[0]
    assert "cabe" in linha_alvo and "%" in linha_alvo
    saida = tco("multiagente")
    assert "ESTIMATIVA" in saida and "acerto não medido" in saida


def test_tco_recusa_divisao_inexistente():
    r = subprocess.run([sys.executable, str(RAIZ / "labs" / "lab5" / "tco.py"), "--divisao", "nao-existe"],
                       capture_output=True, text=True)
    assert r.returncode != 0 and "Opções" in r.stderr


def test_cache_parecida_acima_e_diferente_abaixo_do_limiar():
    base = "Em que horário roda a janela do lote noturno do SGC?"
    assert gateway.semelhanca(base, "Qual é o horário da janela do lote noturno do SGC?") >= 0.7
    # O caso da aula: outro assunto (diurno) e ainda assim acima do limiar. É o risco do cache semântico.
    assert gateway.semelhanca(base, "Em que horário roda a janela do lote diurno do SGC?") >= 0.7
    assert gateway.semelhanca(base, "O que o ADR-047 decidiu sobre o cache do saldo?") < 0.7


def falso_modelo(chamadas):
    def chamar(departamento, pergunta, modelo):
        chamadas.append(modelo)
        r = SimpleNamespace(erro="", duracao_s=1.0, tokens_entrada=1000, tokens_saida=100, uso_por_modelo={})
        return r, f"resposta de {modelo}", ["doc.md"]
    return chamar


def test_gateway_residencia_cota_e_reserva(tmp_path, monkeypatch):
    monkeypatch.setattr(gateway, "ESTADO", tmp_path)
    rotas = gateway.ler_rotas(RAIZ / "labs" / "lab5" / "rotas.toml")
    chamadas = []
    gw = gateway.Gateway(rotas, chamar=falso_modelo(chamadas))
    _, reg = gw.atender("Risco", "Qual o saldo do cliente de CPF 123.456.789-09?")
    assert reg["regiao"] == "Brasil" and not chamadas          # residência: não chama modelo global
    gateway.gravar_estado("cota.json", {"TI Operacional": 599500})
    _, reg = gw.atender("TI Operacional", "Quem é o dono do runbook?")
    assert "cota" in reg["decisao"] and not chamadas           # cota estourada: 429 sem chamar
    gateway.gravar_estado("cota.json", {})
    principal = rotas["apelidos"]["bussola-padrao"]
    gateway.Gateway(rotas, falhar={principal}, chamar=falso_modelo(chamadas)).atender("TI Operacional", "Quem é o dono?")
    assert chamadas == [rotas["apelidos"]["bussola-reserva"]]  # reserva no lugar do principal
    assert len((tmp_path / "registro.jsonl").read_text(encoding="utf-8").splitlines()) == 3


def test_orquestrar_reconhece_os_problemas_plantados():
    texto = ("ADR-101: a alternativa 3 é palha. ADR-102: a RC-13 não existe no caso. "
             "ADR-103: a reversão 'sem custo' ignora o lock-in das políticas.")
    assert all(orquestrar.achados(texto).values())
    assert not any(orquestrar.achados("Os três ADRs estão bons.").values())


def test_eval_junta_lab2_e_recusas():
    import eval as ev
    casos = ev.carregar_casos()
    ids = [c["id"] for c in casos]
    assert ids[:10] == [f"P{i:02d}" for i in range(1, 11)] and "R01" in ids and "R02" in ids
    assert all(c["avaliador"] == "juiz" and c.get("criterio") for c in casos if c["id"].startswith("R"))


def test_complexidade_por_palavra_inteira_e_sem_acento():
    assert gateway.casa_expressao("analise", "Faça uma análise do ADR-047")
    assert gateway.casa_expressao("por que", "Por que o Gestão PJ usa arquivo?")
    assert not gateway.casa_expressao("por que", "Em que horário roda a janela do lote noturno do SGC?")
    assert not gateway.casa_expressao("riscos", "Qual o risco do lote?")
