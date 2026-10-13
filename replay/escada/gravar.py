#!/usr/bin/env python3
"""Grava a escada do harness: a mesma tarefa em 4 degraus, por `claude -p`. Executar.

Uso (da raiz do repositório):
    python3 replay/escada/gravar.py <modelo> <degrau> [<degrau> ...]

Exemplo:
    python3 replay/escada/gravar.py haiku 1 2 3 4
    python3 replay/escada/gravar.py sonnet 1 4

Degraus (a tarefa é sempre o cenário 2 da skill escrevendo-adrs, que não informa decisores nem
requisitos: um bom harness registra a lacuna, um fraco inventa):
    1. só prompt: pasta vazia, sem o repositório;
    2. + contexto: cópia do repositório com AGENTS.md e código, sem a skill;
    3. + loop com testes: o degrau 2 mais o validador do ADR como sensor ("rode até PASS");
    4. + harness completo: skill, hook que valida a cada escrita, hook que exige o subagente
       revisor antes de encerrar, permissão de escrita só em docs/adr/ (harness/).

Cada degrau roda numa pasta temporária limpa (com git, para ver o diff) e salva em
replay/escada/gravacao/<modelo>-d<N>/: prompt, eventos (stream-json), resposta, arquivos
alterados, validador, disparos dos hooks e uma linha de métricas. Gasta cota do plano de quem roda.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
AQUI = Path(__file__).resolve().parent
SKILL = "escrevendo-adrs"
VALIDADOR = RAIZ / ".agents" / "skills" / SKILL / "scripts" / "validar_adr.py"
TAREFA = json.loads((RAIZ / ".agents" / "skills" / SKILL / "evals" / "cenarios.json").read_text(encoding="utf-8"))[1]["query"]
LOOP = "\n\nQuando terminar, rode `python3 scripts/validar_adr.py <caminho do ADR>` e corrija até dar PASS."
# Teto para uma tarefa completa do agente; as execuções medidas em 12/10/2026 levaram de 31 s a 86 s.
TIMEOUT_S = 900
# Degraus 1 a 3: as mesmas ferramentas do scripts/testar_skill.py, para comparar com aqueles testes.
FERRAMENTAS = "Read,Write,Edit,Glob,Grep,Bash(python3:*),Bash(ls:*),Bash(mkdir:*),Bash(cp:*),Bash(cat:*)"
IGNORAR = shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "resultados", "*.db",
                                 "core-banking-api", "replay")


def sem_a_skill(copia):
    """Linha de base justa: nada na cópia entrega a skill ou o formato dela (como no testar_skill.py)."""
    (copia / ".claude" / "skills" / SKILL).unlink()
    shutil.rmtree(copia / ".agents" / "skills" / SKILL)
    agents = copia / "AGENTS.md"
    agents.write_text(agents.read_text(encoding="utf-8").replace(f", com a skill `{SKILL}`", ""), encoding="utf-8")
    for p in list(copia.rglob("*")):
        if p.is_file() and not p.is_symlink() and SKILL in p.read_text(encoding="utf-8", errors="ignore"):
            p.unlink()


def com_harness(copia):
    """Degrau 4: instala hooks, subagente e permissões de harness/ na cópia."""
    shutil.copy(AQUI / "harness" / "settings.json", copia / ".claude" / "settings.json")
    shutil.copytree(AQUI / "harness" / "hooks", copia / ".claude" / "hooks")
    shutil.copytree(AQUI / "harness" / "agents", copia / ".claude" / "agents")
    agents = copia / "AGENTS.md"
    agents.write_text(agents.read_text(encoding="utf-8").replace(
        f"com a skill `{SKILL}`.",
        f"com a skill `{SKILL}`. Antes de entregar, o subagente `revisor-adr` confere cada fato do ADR."), encoding="utf-8")


def preparar(degrau, tmp):
    """Monta a pasta do degrau e devolve (pasta, prompt, argumentos de permissão)."""
    if degrau == 1:
        pasta = tmp / "vazia"
        pasta.mkdir()
        return pasta, TAREFA, ["--permission-mode", "acceptEdits", "--allowedTools", FERRAMENTAS]
    pasta = tmp / "repo"
    shutil.copytree(RAIZ, pasta, symlinks=True, ignore=IGNORAR)
    if degrau in (2, 3):
        sem_a_skill(pasta)
        prompt = TAREFA
        if degrau == 3:
            shutil.copy(VALIDADOR, pasta / "scripts" / "validar_adr.py")
            prompt += LOOP
        return pasta, prompt, ["--permission-mode", "acceptEdits", "--allowedTools", FERRAMENTAS]
    com_harness(pasta)
    # As regras vão também pela linha de comando: num workspace que ninguém marcou como confiável,
    # o Claude Code ignora o permissions.allow do .claude/settings.json (um repositório clonado não
    # se autoconcede permissões). dontAsk nega tudo o que essas regras não liberam.
    regras = json.loads((AQUI / "harness" / "settings.json").read_text(encoding="utf-8"))["permissions"]["allow"]
    return pasta, TAREFA, ["--permission-mode", "dontAsk", "--allowedTools", ",".join(regras)]


def git(pasta, *args):
    return subprocess.run(["git", "-C", str(pasta), *args], capture_output=True, text=True).stdout


def gravar(modelo, degrau):
    saida = AQUI / "gravacao" / f"{modelo}-d{degrau}"
    shutil.rmtree(saida, ignore_errors=True)
    saida.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as tmp:
        pasta, prompt, permissoes = preparar(degrau, Path(tmp))
        git(pasta, "init", "-q")
        git(pasta, "add", "-A")
        git(pasta, "-c", "user.name=escada", "-c", "user.email=escada@example.com", "commit", "-qm", "base", "--allow-empty")
        (saida / "prompt.txt").write_text(prompt, encoding="utf-8")
        log_hooks = saida / "hooks.jsonl"
        ambiente = {**os.environ, "ESCADA_LOG": str(log_hooks)}
        inicio = time.monotonic()
        proc = subprocess.run(
            ["claude", "-p", prompt, "--model", modelo, "--output-format", "stream-json", "--verbose", *permissoes],
            cwd=pasta, capture_output=True, text=True, timeout=TIMEOUT_S, env=ambiente,
        )
        duracao = time.monotonic() - inicio
        # A gravação vai para um repositório público: sem o caminho da pasta pessoal de quem gravou
        (saida / "eventos.jsonl").write_text(proc.stdout.replace(str(Path.home()), "~"), encoding="utf-8")
        final = next((json.loads(l) for l in reversed(proc.stdout.splitlines())
                      if l.strip().startswith("{") and json.loads(l).get("type") == "result"), None)
        if final is None:
            print(f"{modelo} d{degrau}: resposta inesperada do Claude Code: {(proc.stderr or proc.stdout)[-300:]}")
            return None
        (saida / "resposta.md").write_text(str(final.get("result", "")), encoding="utf-8")
        git(pasta, "add", "-A")
        alterados = [l for l in git(pasta, "diff", "--cached", "--name-only").splitlines() if l]
        (saida / "diff.patch").write_text(git(pasta, "diff", "--cached"), encoding="utf-8")
        for rel in alterados:
            origem = pasta / rel
            if origem.is_file():
                destino = saida / "arquivos" / rel
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(origem, destino)
        # Sempre o validador original, fora da cópia: o agente pode ter mexido no dele
        adrs = [pasta / r for r in alterados if r.endswith(".md") and (pasta / r).is_file()
                and not r.startswith(".claude/") and Path(r).name not in ("README.md", "AGENTS.md")]
        if adrs:
            val = subprocess.run([sys.executable, str(VALIDADOR), *map(str, adrs)], capture_output=True, text=True)
            (saida / "validador.txt").write_text(val.stdout.replace(str(pasta) + "/", ""), encoding="utf-8")
            veredito = "PASS" if val.returncode == 0 else f"FAIL({val.stdout.count('ERRO')} erros)"
        else:
            veredito = "sem ADR"

    uso = final.get("usage", {})
    entrada = uso.get("input_tokens", 0) + uso.get("cache_read_input_tokens", 0) + uso.get("cache_creation_input_tokens", 0)
    fora_do_adr = [r for r in alterados if not r.startswith("docs/adr/")] if degrau > 1 else []
    metricas = {
        "modelo": modelo, "degrau": degrau, "validador": veredito, "turnos": final.get("num_turns"),
        "tokens_entrada": entrada, "tokens_saida": uso.get("output_tokens", 0), "duracao_s": round(duracao),
        "arquivos_alterados": alterados, "fora_de_docs_adr": fora_do_adr,
        "negacoes_de_permissao": len(final.get("permission_denials") or []),
        "modelos_usados": sorted((final.get("modelUsage") or {}).keys()),
        "data": time.strftime("%Y-%m-%d"),
    }
    (saida / "metricas.json").write_text(json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8")
    return metricas


def main(argv):
    if len(argv) < 3 or not all(a in "1234" and len(a) == 1 for a in argv[2:]):
        print(__doc__)
        return 2
    modelo = argv[1]
    print("modelo\tdegrau\tvalidador\tturnos\ttokens_entrada\ttokens_saida\tduracao_s\tfora_de_docs_adr")
    for d in map(int, argv[2:]):
        m = gravar(modelo, d)
        if m:
            print(f"{modelo}\t{d}\t{m['validador']}\t{m['turnos']}\t{m['tokens_entrada']}\t{m['tokens_saida']}"
                  f"\t{m['duracao_s']}\t{','.join(m['fora_de_docs_adr']) or '-'}", flush=True)
    print(f"Gravações em {(AQUI / 'gravacao').relative_to(RAIZ)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
