#!/usr/bin/env python3
"""Grava o replay do Lab 1 por `claude -p`, numa cópia limpa do repositório. Executar.

Uso (da raiz do repositório):
    python3 replay/lab1/gravar.py <modelo> <condição> [<condição> ...]

Condições:
    ticket   só o ticket: `make lab1`, sem spec nem seção do AGENTS.md; o prompt manda terminar
             o cancelamento do ticket. Mostra o que o agente faz com o rascunho do colega.
    harness  o harness de exemplo do grupo (spec, seção do AGENTS.md, teste do grupo, fitness
             ligada) e o prompt do README. O verificacao.md fica vazio: é do verificador.

Salva em replay/lab1/gravacao/<modelo>-<condição>/: prompt, eventos (stream-json), resposta, diff,
saída do make lab1-check, da fitness function e métricas. Gasta cota do plano de quem roda.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
REF = RAIZ / "labs" / "lab1" / "referencia"
# Teto para a tarefa completa; o Lab 1 reserva 20 min para o agente.
TIMEOUT_S = 1200
FERRAMENTAS = ("Read,Write,Edit,Glob,Grep,Bash(make:*),Bash(uv:*),Bash(python3:*),Bash(git diff:*),"
               "Bash(git status:*),Bash(ls:*),Bash(cat:*),Bash(curl:*)")
IGNORAR = shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "resultados", "*.db",
                                 "core-banking-api", "replay")
PROMPTS = {
    "ticket": "Termine o cancelamento de pedido do ticket `labs/lab1/ticket.md`.",
    "harness": ("Implemente o cancelamento de pedido descrito em `labs/lab1/spec.md`. Siga o `AGENTS.md`. "
                "Rode `make lab1-check` até passarem os itens de código (4, 5 e 6). Os itens 2, 3 e 7 são do "
                "grupo: não edite a spec, a seção do Mini-ERP no `AGENTS.md` nem o `verificacao.md`."),
}


def harness_do_grupo(copia):
    """Os arquivos do grupo, com os exemplos da referência, sem o código da referência."""
    lab = copia / "labs" / "lab1"
    shutil.copy(REF / "exemplo_spec.md", lab / "spec.md")
    shutil.copy(REF / "exemplo_test_grupo.py", lab / "testes" / "test_grupo.py")
    sensores = lab / "sensores.toml"
    sensores.write_text(re.sub(r"^ligado = false", "ligado = true", sensores.read_text(encoding="utf-8"), flags=re.M),
                        encoding="utf-8")
    with (copia / "AGENTS.md").open("a", encoding="utf-8") as f:
        f.write((REF / "exemplo_agents.md").read_text(encoding="utf-8"))


def rodar(copia, *args):
    return subprocess.run(args, cwd=copia, capture_output=True, text=True)


def gravar(modelo, condicao):
    saida = AQUI / "gravacao" / f"{modelo}-{condicao}"
    shutil.rmtree(saida, ignore_errors=True)
    saida.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "repo"
        shutil.copytree(RAIZ, copia, symlinks=True, ignore=IGNORAR)
        rodar(copia, sys.executable, "labs/lab1/preparar.py")
        if condicao == "harness":
            harness_do_grupo(copia)
        rodar(copia, "git", "init", "-q")
        rodar(copia, "git", "add", "-A")
        rodar(copia, "git", "-c", "user.name=replay", "-c", "user.email=replay@example.com", "commit", "-qm", "base")
        prompt = PROMPTS[condicao]
        (saida / "prompt.txt").write_text(prompt, encoding="utf-8")
        inicio = time.monotonic()
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", modelo, "--output-format", "stream-json", "--verbose",
             "--permission-mode", "acceptEdits", "--allowedTools", FERRAMENTAS],
            cwd=copia, capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL,
        )
        duracao = time.monotonic() - inicio
        (saida / "eventos.jsonl").write_text(proc.stdout.replace(str(Path.home()), "~"), encoding="utf-8")
        final = next((json.loads(l) for l in reversed(proc.stdout.splitlines())
                      if l.startswith("{") and json.loads(l).get("type") == "result"), None)
        if final is None:
            print(f"{modelo} {condicao}: resposta inesperada do Claude Code: {(proc.stderr or proc.stdout)[-300:]}")
            return None
        (saida / "resposta.md").write_text(str(final.get("result", "")), encoding="utf-8")
        rodar(copia, "git", "add", "-A")
        (saida / "diff.patch").write_text(rodar(copia, "git", "diff", "--cached").stdout, encoding="utf-8")
        alterados = [l for l in rodar(copia, "git", "diff", "--cached", "--name-only").stdout.splitlines() if l]
        # A fitness function roda ligada nas duas condições: na 'ticket', mostra o que ela teria barrado.
        fitness = rodar(copia, sys.executable, "-c",
                        "import sys; sys.path.insert(0, 'labs/lab1'); import fitness_camadas as f; "
                        "print('\\n'.join(f.verificar(['routes/faturas.py'])) or 'camadas: PASS')")
        (saida / "fitness.txt").write_text(fitness.stdout, encoding="utf-8")
        check = rodar(copia, sys.executable, "labs/lab1/checar.py")
        (saida / "lab1-check.txt").write_text(check.stdout, encoding="utf-8")

    uso = final.get("usage", {})
    metricas = {
        "modelo": modelo, "condicao": condicao, "turnos": final.get("num_turns"),
        "tokens_entrada": uso.get("input_tokens", 0) + uso.get("cache_read_input_tokens", 0) + uso.get("cache_creation_input_tokens", 0),
        "tokens_saida": uso.get("output_tokens", 0), "duracao_s": round(duracao),
        "arquivos_alterados": alterados,
        "camadas": "PASS" if fitness.stdout.strip() == "camadas: PASS" else "FAIL",
        "lab1_check": next((l for l in check.stdout.splitlines() if l.startswith("lab1-check:")), "?"),
        "negacoes_de_permissao": [d.get("tool_input") for d in final.get("permission_denials") or []],
        "modelos_usados": sorted((final.get("modelUsage") or {}).keys()), "data": time.strftime("%Y-%m-%d"),
    }
    (saida / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=2).replace(str(Path.home()), "~"),
                                         encoding="utf-8")
    return metricas


def main(argv):
    if len(argv) < 3 or not all(c in PROMPTS for c in argv[2:]):
        print(__doc__)
        return 2
    print("modelo\tcondicao\tcamadas\tlab1_check\tturnos\ttokens_entrada\tduracao_s")
    for condicao in argv[2:]:
        m = gravar(argv[1], condicao)
        if m:
            print(f"{m['modelo']}\t{condicao}\t{m['camadas']}\t{m['lab1_check']}\t{m['turnos']}\t{m['tokens_entrada']}\t{m['duracao_s']}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
