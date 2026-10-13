#!/usr/bin/env python3
"""Roda um cenário de eval de uma skill, com ou sem a skill, numa cópia limpa do repositório. Executar.

Uso:
    python3 scripts/testar_skill.py <skill> <nº do cenário> <modelo> [--sem]

Exemplo:
    python3 scripts/testar_skill.py escrevendo-adrs 1 sonnet --sem
    python3 scripts/testar_skill.py escrevendo-adrs 1 sonnet

Lê o cenário em .agents/skills/<skill>/evals/cenarios.json, copia o repositório para uma pasta
temporária (sem a skill, se --sem), roda `claude -p` com a pergunta e guarda a resposta e os
arquivos gerados em resultados/. No fim, imprime uma linha para a planilha. A comparação com o
`expected_behavior` é feita por quem testa (o verificador do grupo), lendo a resposta.
Gasta cota do plano de quem roda: cada execução é uma tarefa completa do agente.
"""
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
# Uma tarefa de ADR leva de 1 a 4 min; 15 min cobre modelos lentos sem deixar a execução presa.
TIMEOUT_S = 900
# O agente lê, escreve e roda os scripts do repositório; nada de rede nem de instalar pacotes.
FERRAMENTAS = "Read,Write,Edit,Glob,Grep,Bash(python3:*),Bash(ls:*),Bash(mkdir:*),Bash(cp:*),Bash(cat:*)"
IGNORAR = shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "resultados", "*.db")


def fotografia(pasta):
    """{arquivo: hash} para descobrir depois o que o agente criou ou alterou."""
    return {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in pasta.rglob("*") if p.is_file()}


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    skill, n, modelo, sem = argv[1], int(argv[2]), argv[3], "--sem" in argv
    pasta_skill = RAIZ / ".agents" / "skills" / skill
    cenarios = json.loads((pasta_skill / "evals" / "cenarios.json").read_text(encoding="utf-8"))
    if not 1 <= n <= len(cenarios):
        print(f"Cenário {n} não existe: {skill} tem {len(cenarios)} cenários.")
        return 2
    cenario = cenarios[n - 1]
    condicao = "sem" if sem else "com"
    saida = RAIZ / "resultados" / f"{skill}-c{n}-{modelo}-{condicao}"
    shutil.rmtree(saida, ignore_errors=True)
    saida.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "repo"
        shutil.copytree(RAIZ, copia, symlinks=True, ignore=IGNORAR)
        for origem, destino in cenario.get("setup", {}).get("copiar", []):
            (copia / destino).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(pasta_skill / origem, copia / destino)
        validador = copia / ".agents" / "skills" / skill / "scripts" / "validar_adr.py"
        shutil.copy(validador, Path(tmp) / "validar_adr.py")  # guardado para conferir depois
        if sem:
            (copia / ".claude" / "skills" / skill).unlink()
            shutil.rmtree(copia / ".agents" / "skills" / skill)
            # Linha de base justa: o AGENTS.md também não cita a skill ausente.
            agents = copia / "AGENTS.md"
            agents.write_text("".join(l for l in agents.read_text(encoding="utf-8").splitlines(True) if skill not in l), encoding="utf-8")
        antes = fotografia(copia)
        inicio = time.monotonic()
        proc = subprocess.run(
            ["claude", "-p", cenario["query"], "--model", modelo, "--output-format", "json",
             "--permission-mode", "acceptEdits", "--allowedTools", FERRAMENTAS],
            cwd=copia, capture_output=True, text=True, timeout=TIMEOUT_S,
        )
        duracao = time.monotonic() - inicio
        try:
            dados = json.loads(proc.stdout)
        except json.JSONDecodeError:
            print(f"Resposta inesperada do Claude Code: {(proc.stderr or proc.stdout)[:300]}")
            return 1
        (saida / "resposta.md").write_text(str(dados.get("result", "")), encoding="utf-8")
        (saida / "execucao.json").write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")
        depois = fotografia(copia)
        novos = sorted(p for p, h in depois.items() if antes.get(p) != h)
        for p in novos:
            destino = saida / "arquivos" / p.relative_to(copia)
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(p, destino)
        adrs = [p for p in novos if p.suffix == ".md"]
        if adrs:
            val = subprocess.run([sys.executable, str(Path(tmp) / "validar_adr.py"), *map(str, adrs)],
                                 capture_output=True, text=True)
            (saida / "validador.txt").write_text(val.stdout, encoding="utf-8")
            veredito = "PASS" if val.returncode == 0 else f"FAIL({val.stdout.count('ERRO')} erros)"
        else:
            veredito = "sem ADR"

    uso = dados.get("usage", {})
    entrada = uso.get("input_tokens", 0) + uso.get("cache_read_input_tokens", 0) + uso.get("cache_creation_input_tokens", 0)
    print("skill\tcenario\tmodelo\tcondicao\tvalidador\tturnos\ttokens_entrada\ttokens_saida\tduracao_s")
    print(f"{skill}\t{n}\t{modelo}\t{condicao}\t{veredito}\t{dados.get('num_turns')}\t{entrada}\t{uso.get('output_tokens', 0)}\t{duracao:.0f}")
    print(f"Resposta e arquivos em {saida.relative_to(RAIZ)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
