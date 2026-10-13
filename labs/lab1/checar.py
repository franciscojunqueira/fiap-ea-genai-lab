#!/usr/bin/env python3
"""Confere o Lab 1 (make lab1-check). Executar.

Sete itens, cada um com PASS ou com o que fazer para passar:
  1. lab preparado (make lab1);           5. teste do grupo escrito e passando;
  2. spec com 3 ou mais critérios CA-NN;  6. testes de aceite do ticket passando;
  3. seção "## Mini-ERP" no AGENTS.md;    7. verificacao.md preenchido pelo verificador.
  4. fitness function camadas ligada e passando;
O check confere a forma e o comportamento da API. Se o agente inventou algo, quem pega é o verificador.
"""
import hashlib
import os
import re
import subprocess
import sys
import tomllib
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
sys.path.insert(0, str(LAB))
import fitness_camadas  # noqa: E402

CA = re.compile(r"\bCA-\d{2}\b")
# Critério de aceite da spec: item de lista que começa por **CA-NN** (o exemplo do modelo não conta)
CRITERIO = re.compile(r"^\s*[-*]\s+\*\*(CA-\d{2})", re.MULTILINE)
# Linhas de instrução dos modelos começam com '<': se sobrar alguma, o arquivo não foi preenchido.
SOBRA_DO_MODELO = re.compile(r"^\s*<.*>\s*$", re.MULTILINE)
EXCECOES_REGISTRADAS = ["routes/faturas.py"]
# SHA-256 dos sensores do professor; recalcular quando eles mudarem (tests/test_lab1.py acusa a divergência).
SENSORES_DO_PROFESSOR = {
    "aceite/test_aceite.py": "0990f446c024cb32a223a2fd1c87bb5fada607c9d54ee0d08f99dbcb00996392",
    "fitness_camadas.py": "5ca268b1b6db2bb1a1b9359731475ee67998feff2c4aa6b3fd326b8c0dec4824",
    "conftest.py": "192870b7235e0fa1cde8a190cf4212cb1d83761d68d68fa15b4a6db632b9bab1",
}
SECOES_VERIFICACAO = ["O que o agente acertou", "O que o agente inventou", "O que o agente omitiu",
                      "O que mudaríamos no harness", "Pergunta de decisão"]


def secoes(texto, nivel="## "):
    """{título: linhas de conteúdo} das seções do nível dado."""
    resultado, atual = {}, None
    for linha in texto.splitlines():
        if linha.startswith(nivel):
            atual = linha[len(nivel):].strip()
            resultado[atual] = []
        elif linha.startswith("#") and atual is not None and not linha.startswith(nivel + "#"):
            atual = None
        elif atual is not None:
            resultado[atual].append(linha)
    return resultado


def conteudo(linhas):
    """Linhas que contam como resposta: não vazias, não instrução do modelo, não a pergunta citada."""
    return [l for l in linhas if l.strip() and not l.strip().startswith(("<", ">"))]


def pytest(caminho):
    """Roda o pytest num diretório do lab; devolve (passou, mensagens das falhas)."""
    # COLUMNS largo: sem terminal, o pytest corta o resumo em 80 colunas e a mensagem acionável some.
    env = {**os.environ, "COLUMNS": "400"}
    proc = subprocess.run([sys.executable, "-m", "pytest", str(caminho), "-q", "-rf", "--tb=no", "-p", "no:cacheprovider"],
                          cwd=RAIZ, capture_output=True, text=True, env=env)
    falhas = [l.split(" - ", 1)[1] if " - " in l else l for l in proc.stdout.splitlines() if l.startswith(("FAILED", "ERROR"))]
    if proc.returncode not in (0, 1) and not falhas:
        falhas = [proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else proc.stderr.strip()[-300:]]
    return proc.returncode == 0, falhas


def item_preparado():
    faltam = [f for f in ("spec.md", "verificacao.md", "sensores.toml", "testes/test_grupo.py") if not (LAB / f).exists()]
    return [] if not faltam else [f"Faltam {', '.join(faltam)} em labs/lab1/. Rode `make lab1` primeiro."]


def item_spec():
    spec = (LAB / "spec.md").read_text(encoding="utf-8")
    problemas = []
    cas = sorted(set(CRITERIO.findall(spec)))
    if len(cas) < 3:
        problemas.append(f"labs/lab1/spec.md tem {len(cas)} critério(s) de aceite ({', '.join(cas) or 'nenhum'}); "
                         f"escrevam pelo menos 3, no formato '- **CA-01:** Dado ..., quando ..., então ...'.")
    if SOBRA_DO_MODELO.search(spec):
        problemas.append("labs/lab1/spec.md ainda tem linhas de instrução do modelo (começam com '<'); preencham e apaguem.")
    return problemas


def item_agents():
    agents = (RAIZ / "AGENTS.md").read_text(encoding="utf-8")
    secao = secoes(agents).get("Mini-ERP")
    if secao is None:
        return ["AGENTS.md não tem a seção '## Mini-ERP'. Os autores escrevem ali o que o agente não sabe sozinho: "
                "as camadas (rota → service → modelo), onde ficam as regras de negócio e como rodar os testes do lab."]
    linhas = conteudo(secao)
    problemas = []
    if len(linhas) < 3:
        problemas.append(f"A seção '## Mini-ERP' do AGENTS.md tem {len(linhas)} linha(s); escrevam pelo menos 3 instruções.")
    if "services" not in " ".join(linhas):
        problemas.append("A seção '## Mini-ERP' do AGENTS.md não diz onde fica a regra de negócio (mini-erp/app/services/).")
    return problemas


def item_camadas():
    config = tomllib.loads((LAB / "sensores.toml").read_text(encoding="utf-8"))["camadas"]
    if not config.get("ligado"):
        return ["A fitness function 'camadas' está desligada. Liguem em labs/lab1/sensores.toml (ligado = true)."]
    problemas = []
    if config.get("excecoes") != EXCECOES_REGISTRADAS:
        # Exceção nova silencia o sensor: só com ADR, e o ADR não cabe neste lab.
        problemas.append(f"A lista de exceções de labs/lab1/sensores.toml mudou ({config.get('excecoes')}). "
                         f"Neste lab só vale a dívida registrada {EXCECOES_REGISTRADAS}: devolvam a lista e corrijam o código.")
    return problemas + [f"camadas: {a}" for a in fitness_camadas.verificar(EXCECOES_REGISTRADAS)]


def item_teste_do_grupo():
    arquivo = LAB / "testes" / "test_grupo.py"
    codigo = arquivo.read_text(encoding="utf-8")
    problemas = []
    if "pytest.skip(" in codigo:
        problemas.append("labs/lab1/testes/test_grupo.py ainda tem o pytest.skip do modelo: escrevam o teste e apaguem a linha.")
    if "assert " not in codigo:
        problemas.append("labs/lab1/testes/test_grupo.py não tem nenhum assert: o teste precisa conferir alguma coisa.")
    if not CA.search(codigo):
        problemas.append("labs/lab1/testes/test_grupo.py não diz qual critério da spec testa: citem o CA-NN no nome ou na docstring.")
    if problemas:
        return problemas
    passou, falhas = pytest(LAB / "testes")
    return [] if passou else [f"Teste do grupo falhou: {f}" for f in falhas]


def item_aceite():
    passou, falhas = pytest(LAB / "aceite")
    if passou:
        return []
    if len(set(CRITERIO.findall((LAB / "spec.md").read_text(encoding="utf-8")))) < 3:
        # Antes da spec, o check não entrega as regras escondidas no ticket: achá-las é o trabalho dos autores.
        return [f"{len(falhas)} de 4 testes de aceite do ticket falham. Escrevam a spec primeiro (passo 2): "
                "as regras estão na fala do atendimento, em labs/lab1/ticket.md. Com 3 ou mais CAs, este item mostra cada falha."]
    return [f"Aceite: {f}" for f in falhas]


def item_integridade():
    alterados = [rel for rel, h in SENSORES_DO_PROFESSOR.items()
                 if hashlib.sha256((LAB / rel).read_bytes().replace(b"\r\n", b"\n")).hexdigest() != h]  # clone Windows (autocrlf) não conta como alteração
    return [] if not alterados else [f"Sensor do professor alterado: {', '.join('labs/lab1/' + a for a in alterados)}. "
                                     "Sensor editado não vale como evidência: restaurem com `git checkout -- <arquivo>`."]


def item_verificacao():
    texto = (LAB / "verificacao.md").read_text(encoding="utf-8")
    achadas = secoes(texto)
    vazias = [s for s in SECOES_VERIFICACAO if not conteudo(achadas.get(s, []))]
    return [] if not vazias else [f"labs/lab1/verificacao.md sem resposta em: {', '.join(vazias)}. "
                                  "Quem escreve é o verificador ou o relator, não o agente."]


ITENS = [
    ("1. Lab preparado", item_preparado),
    ("2. Spec com critérios de aceite", item_spec),
    ("3. AGENTS.md com a seção do Mini-ERP", item_agents),
    ("4. Fitness function 'camadas' e sensores íntegros", lambda: item_integridade() + item_camadas()),
    ("5. Teste do grupo", item_teste_do_grupo),
    ("6. Testes de aceite do ticket", item_aceite),
    ("7. Verificação humana", item_verificacao),
]


def main():
    ok = 0
    for nome, funcao in ITENS:
        problemas = funcao()
        if problemas and nome.startswith("1."):
            print(f"[FALHA] {nome}\n        {problemas[0]}\nlab1-check: FAIL")
            return 1
        print(f"[{'OK' if not problemas else 'FALHA'}] {nome}")
        for p in problemas:
            print(f"        {p}")
        ok += not problemas
    veredito = "PASS" if ok == len(ITENS) else "FAIL"
    print(f"\nlab1-check: {veredito} ({ok}/{len(ITENS)} itens)")
    print(f"Linha para a planilha da turma:\tlab1\t{veredito}\t{ok}/{len(ITENS)}")
    return 0 if veredito == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
