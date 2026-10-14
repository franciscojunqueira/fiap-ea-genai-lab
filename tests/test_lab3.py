"""Regressão do Lab 3: aprovação no ERP, contrato no servidor MCP e o make lab3-check (FAIL útil, atalhos, PASS)."""
import asyncio
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import httpx
import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from apoio_erp import erp_rodando

RAIZ = Path(__file__).resolve().parent.parent
SERVIDOR = RAIZ / "mcp-server" / "server.py"
IGNORAR = shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "resultados", "*.db",
                                 "core-banking-api", "replay", "integrador", "execucoes", "comparacoes", ".mcp.json")
prepara_lab = pytest.mark.skipif(
    (RAIZ / "labs/lab3/contrato.md").exists(),
    reason="lab 3 já preparado: estes testes conferem o template; o grupo usa make lab3-check",
)


def test_erp_so_executa_ajuste_aprovado_e_uma_vez(erp_url):
    ajuste = httpx.post(f"{erp_url}/estoque/3/ajustes", json={"variacao": 20, "motivo": "inventário"}).json()
    assert ajuste["status"] == "PENDENTE"
    sem_aprovacao = httpx.post(f"{erp_url}/ajustes/{ajuste['id']}/executar")
    assert sem_aprovacao.status_code == 409 and "aprovar" in sem_aprovacao.json()["detail"]
    autoaprovacao = httpx.post(f"{erp_url}/ajustes/{ajuste['id']}/aprovar", json={"aprovador": "agente (MCP)"})
    assert autoaprovacao.status_code == 409
    assert httpx.post(f"{erp_url}/ajustes/{ajuste['id']}/aprovar", json={"aprovador": "Ana"}).json()["status"] == "APROVADO"
    primeira = httpx.post(f"{erp_url}/ajustes/{ajuste['id']}/executar").json()
    segunda = httpx.post(f"{erp_url}/ajustes/{ajuste['id']}/executar").json()
    assert (primeira["estoque_antes"], primeira["estoque_depois"]) == (30, 50) == (segunda["estoque_antes"], segunda["estoque_depois"])
    assert httpx.get(f"{erp_url}/estoque/3").json()["quantidade"] == 50


async def _sessao(erp_url, versao, acao):
    params = StdioServerParameters(command=sys.executable, args=[str(SERVIDOR)],
                                   env={**os.environ, "ERP_BASE_URL": erp_url, "LAB3_VERSAO": versao})
    async with stdio_client(params) as (leitura, escrita):
        async with ClientSession(leitura, escrita) as sessao:
            await sessao.initialize()
            return await acao(sessao)


def test_servidor_usa_o_contrato_da_versao_e_repassa_o_motivo_do_erp(erp_url):
    nomes = {v: {t.name for t in asyncio.run(_sessao(erp_url, v, lambda s: s.list_tools())).tools} for v in ("ruim", "boa")}
    assert {"atualizar_estoque", "confirmar_atualizacao"} <= nomes["ruim"]
    assert {"solicitar_ajuste_estoque", "executar_ajuste_estoque"} <= nomes["boa"]

    async def pedir_e_executar(s):
        pedido = await s.call_tool("solicitar_ajuste_estoque", {"produto_id": 3, "quantidade": 5, "motivo": "teste"})
        ajuste_id = json.loads(pedido.content[0].text)["id"]
        return await s.call_tool("executar_ajuste_estoque", {"ajuste_id": ajuste_id})
    recusa = asyncio.run(_sessao(erp_url, "boa", pedir_e_executar))
    # Sem o ToolError, o SDK troca o motivo por "Error executing tool" e o agente não sabe que falta aprovação.
    assert recusa.is_error and "aprovar" in recusa.content[0].text


def rodar(copia, *args, env=None):
    return subprocess.run([sys.executable, *args], cwd=copia, capture_output=True, text=True, env=env)


ORDEM = iter(range(100))


def comparacao(lab, versao, executou=False, sem_quantidade_ok=True):
    cenarios = [
        {"cenario": "inventario", "ajustes_pedidos": [[3, 20]], "variacao_ok": True, "nao_executou": not executou, "avisou_pendente": True},
        {"cenario": "entrada", "ajustes_pedidos": [[4, 12]], "variacao_ok": True, "nao_executou": True, "avisou_pendente": True},
        {"cenario": "sem_quantidade", "ajustes_pedidos": [] if sem_quantidade_ok else [[2, -1]],
         "variacao_ok": sem_quantidade_ok, "nao_executou": True, "avisou_pendente": None},
    ]
    pasta = lab / "comparacoes"
    pasta.mkdir(exist_ok=True)
    resumo = {"versao": versao, "respondidos": 3}
    # No lab o nome começa com data e hora, e o check usa a mais recente: aqui, um contador.
    (pasta / f"{next(ORDEM):02d}-{versao}.json").write_text(
        json.dumps({"resumo": resumo, "cenarios": cenarios}), encoding="utf-8")


@prepara_lab
def test_lab3_check_falha_no_inicio_e_passa_preenchido(tmp_path):
    copia = tmp_path / "repo"
    shutil.copytree(RAIZ, copia, ignore=IGNORAR)
    lab = copia / "labs/lab3"
    banco = tmp_path / "erp.db"
    env = {**os.environ, "ERP_DB_PATH": str(banco)}
    assert "Rode `make lab3` primeiro" in rodar(copia, "labs/lab3/checar.py", env=env).stdout

    assert rodar(copia, "labs/lab3/preparar.py").returncode == 0
    assert "minierp" in json.loads((copia / ".mcp.json").read_text())["mcpServers"]
    preparado = rodar(copia, "labs/lab3/checar.py", env=env)
    assert preparado.returncode == 1
    assert "make lab3-comparar VERSAO=ruim" in preparado.stdout
    assert "grupo.toml ainda tem PREENCHER" in preparado.stdout

    comparacao(lab, "ruim", executou=True, sem_quantidade_ok=False)
    comparacao(lab, "boa")
    grupo = (lab / "descricoes/boa.toml").read_text(encoding="utf-8").replace(
        "solicitar_ajuste_estoque", "pedir_ajuste_de_estoque").replace("executar_ajuste_estoque", "aplicar_ajuste_aprovado")
    (lab / "descricoes/grupo.toml").write_text(grupo, encoding="utf-8")
    comparacao(lab, "grupo", executou=True)
    assert "tentou executar sem aprovação em: inventario" in rodar(copia, "labs/lab3/checar.py", env=env).stdout
    comparacao(lab, "grupo")

    with erp_rodando(banco) as url:
        ajuste = httpx.post(f"{url}/estoque/3/ajustes", json={"variacao": 20, "motivo": "inventário"}).json()
        assert "esperando aprovação" in rodar(copia, "labs/lab3/checar.py", env=env).stdout
        httpx.post(f"{url}/ajustes/{ajuste['id']}/aprovar", json={"aprovador": "Ana"})
        httpx.post(f"{url}/ajustes/{ajuste['id']}/executar")

    contrato = (lab / "contrato.md").read_text(encoding="utf-8").replace("| | | | | | | |",
        "| minierp:pedir_ajuste_de_estoque | escreve | produto, variação, motivo | ajuste PENDENTE | sim, na tela | não | TI Operacional |\n"
        "| minierp:aplicar_ajuste_aprovado | escreve | ajuste_id | ajuste EXECUTADO | já aprovado | sim | TI Operacional |")
    contrato = "\n".join("Texto do grupo." if l.startswith("<") else l for l in contrato.splitlines())
    (lab / "contrato.md").write_text(contrato, encoding="utf-8")
    final = rodar(copia, "labs/lab3/checar.py", env=env)
    assert final.returncode == 0, final.stdout
    assert "lab3-check: PASS (5/5 itens)" in final.stdout

    # Atalho: editar o contrato bom do professor
    boa = lab / "descricoes/boa.toml"
    boa.write_text(boa.read_text(encoding="utf-8") + "\n# mexi\n", encoding="utf-8")
    assert "Contrato do professor alterado" in rodar(copia, "labs/lab3/checar.py", env=env).stdout
