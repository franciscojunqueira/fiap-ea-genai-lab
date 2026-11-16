#!/usr/bin/env python3
"""Demonstração 2 da Aula 1 (make lab1-demo): o agente no ticket e com o sensor de camadas. Executar.

    make lab1-demo ETAPA=ticket       só o ticket: o agente termina o cancelamento do rascunho do colega.
    make lab1-demo ETAPA=harness      o mesmo pedido, com a seção do Mini-ERP no AGENTS.md e a fitness function ligada.
    make lab1-demo-replay             as duas etapas gravadas pelo professor (Haiku 4.5, 13/10/2026), na mesma tela.

Roda o agente por `claude -p` numa cópia isolada do repositório, preparada como o `make lab1` prepara
(com o rascunho do colega na rota): o repositório do professor não muda. Mostra, em palavras simples,
os arquivos que o agente mudou, o teste do ticket, a fitness function, um trecho do resumo do agente,
tokens e tempo. É do professor: o grupo não roda. Gasta cota do plano de quem roda (uma chamada por etapa).
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
from pathlib import Path

LAB = Path(__file__).resolve().parent
RAIZ = LAB.parents[1]
sys.path.insert(0, str(RAIZ / "replay" / "lab1"))
sys.path.insert(0, str(RAIZ / "scripts"))
import gravar  # noqa: E402  (a gravação do Lab 1: a cópia limpa, o harness de exemplo e as ferramentas liberadas)
import cli_modelo  # noqa: E402

GRAVACAO = RAIZ / "replay" / "lab1" / "gravacao"
PROMPT = "Termine o cancelamento de pedido do ticket `labs/lab1/ticket.md`."
TIMEOUT_S = 900
ETAPAS = {
    "ticket": "só o ticket",
    "harness": "o ticket, a seção Mini-ERP no AGENTS.md e a fitness function ligada",
}
# Do harness de exemplo (referencia/exemplo_agents.md) mais uma linha: sem ela, o agente não é mandado a rodar o sensor.
LINHA_DO_SENSOR = ("- Antes de terminar, rode `make lab1-check`: os itens 4 (camadas) e 6 (testes do ticket) precisam passar. "
                   "Os outros itens são do grupo; ignore-os.\n")
ROTULO_DO_REPLAY = "gravação de 13/10/2026, Haiku 4.5"
NOTA_DO_REPLAY_HARNESS = ("na gravação, o harness também tinha a spec e o teste do grupo, e o pedido mandava rodar o "
                          "make lab1-check até passar. Ao vivo, só a seção do AGENTS.md e a fitness function.")
EXPLICA_ARQUIVO = {"routes": "a rota, a porta de entrada da API", "services": "o service, onde fica a regra de negócio"}


def modelo_da_demo():
    config = tomllib.loads((RAIZ / "config" / "modelos.toml").read_text(encoding="utf-8"))
    return config["labs"]["modelo"]


# ----- a tela (a mesma para a execução ao vivo e para a gravação) -----------------------------------------------

def _milhar(n):
    return f"{int(n):,}".replace(",", ".")


def _trecho(texto, limite=700, linhas=9):
    """Os primeiros parágrafos do resumo do agente, sem enfeite de markdown, num tamanho que cabe na tela."""
    limpas = [re.sub(r"[#*`]", "", l).strip() for l in texto.splitlines()]
    escolhidas, total = [], 0
    for l in (l for l in limpas if l):
        if total + len(l) > limite or len(escolhidas) >= linhas:
            break
        escolhidas.append(l)
        total += len(l)
    cortou = len(escolhidas) < len([l for l in limpas if l])
    return escolhidas + (["[...] (o resumo completo está no arquivo resposta.md)"] if cortou else [])


def _leitura(m):
    teste_ok, fitness_ok = m["aceite"] == "PASS", not m["fitness"]
    if teste_ok and not fitness_ok:
        return ("O teste do ticket passou e a fitness function reprovou: a API funciona, mas a regra está no lugar errado. "
                "Só o sensor de arquitetura viu o erro.")
    if teste_ok and fitness_ok:
        return "O teste do ticket e a fitness function passaram: a API funciona e a regra está no service."
    if not teste_ok and fitness_ok:
        return "A fitness function passou, mas o teste do ticket reprovou: a arquitetura está certa e a API ainda não faz o que o ticket pede."
    return "O teste do ticket e a fitness function reprovaram."


def tela(m):
    """O texto da tela de uma etapa. `m` é o dicionário de resultados (veja resultados_da_copia e resultados_da_gravacao)."""
    sai = [f"=== Demonstração 2, etapa {m['etapa']}: {ETAPAS[m['etapa']]} ===",
           f"Modelo: {m['modelo']} ({m['origem']})", ""]
    n = len(m["arquivos"])
    sai.append(f"1. Arquivos que o agente mudou: {n}" if n else "1. Arquivos que o agente mudou: nenhum")
    for a in m["arquivos"]:
        parte = next((v for k, v in EXPLICA_ARQUIVO.items() if f"/{k}/" in a), "")
        sai.append(f"   - {a}" + (f"  ({parte})" if parte else ""))
    detalhe = f" ({m['aceite_resumo']})" if m.get("aceite_resumo") else ""
    sai += ["", f"2. Teste do ticket: {m['aceite']}{detalhe}",
            "   O que isto diz: a API faz o que o ticket pede." if m["aceite"] == "PASS"
            else "   O que isto diz: a API ainda não faz tudo o que o ticket pede."]
    if m["fitness"]:
        sai += ["", f"3. Fitness function (camadas): FAIL, {len(m['fitness'])} linha(s) apontada(s)"]
        sai += [f"   - {l}" for l in m["fitness"]]
        sai.append("   O que isto diz: a rota fala com o banco direto; a regra deveria estar no service.")
    else:
        sai += ["", "3. Fitness function (camadas): PASS", "   O que isto diz: nenhuma rota fala com o banco; a regra está no service."]
    sai += ["", "4. O que o agente disse no resumo (trecho)"] + [f"   | {l}" for l in _trecho(m["resumo"])]
    sai += ["", f"5. Tokens e tempo: {_milhar(m['tokens_entrada'])} de entrada, {_milhar(m['tokens_saida'])} de saída · "
                f"{m['duracao_s']} s · {m['turnos']} turnos", "", f"Leitura: {_leitura(m)}"]
    if m.get("nota"):
        sai.append(f"Nota: {m['nota']}")
    return "\n".join(sai)


# ----- a gravação ------------------------------------------------------------------------------------------------

def resultados_da_gravacao(pasta, etapa):
    metricas = json.loads((pasta / "metricas.json").read_text(encoding="utf-8"))
    fitness = [l for l in (pasta / "fitness.txt").read_text(encoding="utf-8").splitlines() if l.strip() and l.strip() != "camadas: PASS"]
    check = (pasta / "lab1-check.txt").read_text(encoding="utf-8")
    modelo = (metricas.get("modelos_usados") or [metricas.get("modelo", "?")])[0]
    return {"etapa": etapa, "modelo": modelo, "origem": ROTULO_DO_REPLAY, "arquivos": metricas["arquivos_alterados"],
            "aceite": "PASS" if "[OK] 6." in check else "FAIL", "fitness": fitness,
            "resumo": (pasta / "resposta.md").read_text(encoding="utf-8"),
            "tokens_entrada": metricas["tokens_entrada"], "tokens_saida": metricas["tokens_saida"],
            "duracao_s": metricas["duracao_s"], "turnos": metricas["turnos"], "negacoes": len(metricas.get("negacoes_de_permissao") or []),
            "nota": NOTA_DO_REPLAY_HARNESS if etapa == "harness" else ""}


def replay(etapas, pasta=GRAVACAO):
    for i, etapa in enumerate(etapas):
        print(("\n" if i else "") + tela(resultados_da_gravacao(pasta / f"haiku-{etapa}", etapa)))
    return 0


# ----- a execução ao vivo ----------------------------------------------------------------------------------------

def preparar_copia(copia, etapa):
    """Cópia isolada preparada como o make lab1 prepara; na etapa harness, a seção do AGENTS.md e a fitness ligada."""
    shutil.copytree(RAIZ, copia, symlinks=True, ignore=gravar.IGNORAR)
    lab = copia / "labs" / "lab1"
    # Se o professor já rodou o make lab1 no repositório dele, o ticket não pode herdar spec nem sensor ligado.
    for arquivo in ("spec.md", "verificacao.md", "sensores.toml", "testes/test_grupo.py"):
        (lab / arquivo).unlink(missing_ok=True)
    gravar.rodar(copia, sys.executable, "labs/lab1/preparar.py")
    if "RASCUNHO do colega" not in (copia / "mini-erp/app/routes/pedidos.py").read_text(encoding="utf-8"):
        sys.exit("A cópia não ficou com o rascunho do colega na rota (mini-erp/app/routes/pedidos.py). "
                 "Use um repositório sem o cancelamento pronto: git status deve estar limpo.")
    if etapa == "harness":
        gravar.harness_do_grupo(copia, so_guia_e_sensor=True)
        with (copia / "AGENTS.md").open("a", encoding="utf-8") as f:
            f.write(LINHA_DO_SENSOR)
    gravar.rodar(copia, "git", "init", "-q")
    gravar.rodar(copia, "git", "add", "-A")
    gravar.rodar(copia, "git", "-c", "user.name=demo", "-c", "user.email=demo@example.com", "commit", "-qm", "base")


def resultados_da_copia(copia, etapa, modelo, final, duracao):
    gravar.rodar(copia, "git", "add", "-A")
    alterados = [l for l in gravar.rodar(copia, "git", "diff", "--cached", "--name-only").stdout.splitlines() if l]
    aceite = gravar.rodar(copia, sys.executable, "-m", "pytest", "labs/lab1/aceite", "-q", "--tb=no", "-p", "no:cacheprovider")
    resumo_pytest = next((l.strip(" =") for l in reversed(aceite.stdout.splitlines()) if " passed" in l or " failed" in l), "")
    fitness = gravar.rodar(copia, sys.executable, "-c",
                           "import sys; sys.path.insert(0, 'labs/lab1'); import fitness_camadas as f; "
                           "print('\\n'.join(f.verificar(['routes/faturas.py'])))")
    uso = final.get("usage", {})
    return {"etapa": etapa, "modelo": modelo, "origem": "ao vivo", "arquivos": alterados,
            "aceite": "PASS" if aceite.returncode == 0 else "FAIL", "aceite_resumo": resumo_pytest,
            "fitness": [l for l in fitness.stdout.splitlines() if l.strip()], "resumo": str(final.get("result", "")),
            "tokens_entrada": uso.get("input_tokens", 0) + uso.get("cache_read_input_tokens", 0) + uso.get("cache_creation_input_tokens", 0),
            "tokens_saida": uso.get("output_tokens", 0), "duracao_s": round(duracao), "turnos": final.get("num_turns", 0),
            "negacoes": len(final.get("permission_denials") or []),
            "diff": gravar.rodar(copia, "git", "diff", "--cached").stdout}


def ao_vivo(etapa):
    problema = cli_modelo.disponivel() or cli_modelo.logado()
    if problema:
        print(problema + "\nPlano B: make lab1-demo-replay")
        return 1
    modelo = modelo_da_demo()
    with tempfile.TemporaryDirectory() as tmp:
        copia = Path(tmp) / "repo"
        preparar_copia(copia, etapa)
        print(f"O agente ({modelo}) está trabalhando numa cópia isolada, etapa {etapa}. Leva de 1 a 3 minutos...", flush=True)
        ambiente = {**os.environ}
        if (RAIZ / ".venv").is_dir():
            ambiente["UV_PROJECT_ENVIRONMENT"] = str(RAIZ / ".venv")   # a cópia usa o ambiente já pronto, sem recriar
        inicio = time.monotonic()
        try:
            # Desde a v2.1.302 o `claude -p` começa em modo Manual: as ferramentas liberadas vão explícitas.
            proc = subprocess.run(
                ["claude", "-p", PROMPT, "--model", modelo, "--output-format", "stream-json", "--verbose",
                 "--no-session-persistence", "--permission-mode", "acceptEdits", "--allowedTools", gravar.FERRAMENTAS],
                cwd=copia, capture_output=True, text=True, timeout=TIMEOUT_S, stdin=subprocess.DEVNULL, env=ambiente)
        except subprocess.TimeoutExpired:
            print(f"O agente não terminou em {TIMEOUT_S} s. Plano B: make lab1-demo-replay")
            return 1
        duracao = time.monotonic() - inicio
        final = next((json.loads(l) for l in reversed(proc.stdout.splitlines())
                      if l.startswith("{") and json.loads(l).get("type") == "result"), None)
        if final is None or final.get("is_error"):
            texto = str((final or {}).get("result") or proc.stderr or proc.stdout).strip()[-300:]
            dica = " Limite do plano atingido: use make lab1-demo-replay." if "limit" in texto.lower() else ""
            print(f"O Claude Code não devolveu uma resposta: {texto}{dica}")
            return 1
        m = resultados_da_copia(copia, etapa, modelo, final, duracao)
        saida = RAIZ / "resultados" / "lab1-demo" / f"{etapa}-{time.strftime('%Y%m%d-%H%M%S')}"
        saida.mkdir(parents=True)
        (saida / "eventos.jsonl").write_text(proc.stdout.replace(str(Path.home()), "~"), encoding="utf-8")
        (saida / "diff.patch").write_text(m.pop("diff"), encoding="utf-8")
        (saida / "resposta.md").write_text(m["resumo"], encoding="utf-8")
        (saida / "metricas.json").write_text(json.dumps(m, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + tela(m))
    print(f"\n(Registro desta execução em {saida.relative_to(RAIZ)}/)")
    return 0


def main(argv):
    args = argv[1:]
    if args and args[0] == "--replay":
        etapa = args[1] if len(args) > 1 else ""
        if etapa and etapa not in ETAPAS:
            print(__doc__)
            return 2
        return replay([etapa] if etapa else list(ETAPAS))
    if len(args) != 1 or args[0] not in ETAPAS:
        print("Faltou a etapa. Use:\n  make lab1-demo ETAPA=ticket\n  make lab1-demo ETAPA=harness\n"
              "Sem cota: make lab1-demo-replay")
        return 2
    return ao_vivo(args[0])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
