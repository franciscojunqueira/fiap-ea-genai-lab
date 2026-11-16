#!/usr/bin/env python3
"""Traz do repositório-template os labs novos e as correções (make atualizar). Executar.

O repositório do grupo nasce do template antes da Aula 1 e não recebe sozinho o que o professor publica
depois (Labs 2 a 6, correções). Este script busca o template e copia só os arquivos do professor; os
arquivos do grupo (AGENTS.md, specs, decisões, contratos, ADRs, pacote, código mudado no Lab 1) ficam
como estão. Planejar → validar → executar: o script recusa rodar com alteração não commitada, mostra a
lista do que vai trazer e só aplica depois de "s"; depois faz o commit (sem push). `--sim` só mostra a lista.

Primeira vez num repositório criado antes deste script existir (uma linha, da raiz do repositório):
    git remote add template https://github.com/franciscojunqueira/fiap-ea-genai-lab.git; git fetch template && git checkout template/main -- scripts/atualizar_do_template.py && python3 scripts/atualizar_do_template.py
"""
import fnmatch
import os
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
URL = "https://github.com/franciscojunqueira/fiap-ea-genai-lab.git"
REF = "template/main"
# Do professor: o template manda. Padrões do fnmatch sobre o caminho relativo à raiz.
DO_PROFESSOR = [
    "Makefile", "pyproject.toml", "uv.lock", "README.md", "config/*", "scripts/*", "tests/*", "knowledge/*",
    "mcp-server/*", "replay/*", "docs/*", ".devcontainer/*", ".github/*", ".claude/settings.json",
    "mini-erp/app/main.py", "mini-erp/app/models_ajustes.py", "mini-erp/app/services/ajustes.py",
    "mini-erp/app/routes/ajustes.py", "mini-erp/app/static/*",
    "integrador/caso.md", "integrador/rubrica.md", "integrador/atividades.md", "integrador/README.md",
    "integrador/scripts/*", "integrador/legado/*",
    # 16/11/2026: a saída gravada do agente da Atividade 1 (make atividade1)
    "integrador/atividade1/*",
    "labs/*/README.md", "labs/*/codex.md", "labs/*/ticket.md", "labs/*/*.py", "labs/*/modelos/*",
    "labs/*/aceite/*", "labs/*/referencia/*", "labs/*/exemplos/*", "labs/*/perguntas.toml",
    "labs/*/descricoes/ruim.toml", "labs/*/descricoes/boa.toml",
    # Aula 3 (16/11/2026): os dados das demonstrações do professor.
    "labs/lab4/casos.toml", "labs/lab4/casos_turma.toml", "labs/lab4/orquestracao/adrs/*", "labs/lab5/rotas.toml", "labs/lab5/premissas.toml",
]
# Do grupo: nunca sobrescrever, mesmo que case com um padrão acima.
DO_GRUPO = ["docs/adr/*", "labs/*/testes/*", "labs/*/execucoes/*", "labs/*/comparacoes/*", "labs/*/descricoes/grupo.toml"]
# Arquivos do professor que saíram do template: o script os apaga do repositório do grupo, com a mesma confirmação.
# 09/11/2026: o Lab 2 ficou sem check e sem decisao.md (Sessão 4b).
REMOVIDOS = ["labs/lab2/checar.py", "labs/lab2/modelos/decisao.md",
             # 16/11/2026: sem pitch nem arguição (Sessão 4c)
             "integrador/pacote/pitch.md"]


def git(*args, check=True):
    proc = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True)
    if check and proc.returncode != 0:
        sys.exit(f"git {' '.join(args)} falhou: {proc.stderr.strip()}")
    return proc.stdout


def casa(caminho, padroes):
    return any(fnmatch.fnmatch(caminho, p) for p in padroes)


def avisar_agents():
    """O AGENTS.md é do grupo e sempre difere do template (o grupo escreve nele no Lab 1). Só avisa quando o
    template tem linhas que o do grupo não tem, e mostra quais: o resto da diferença é trabalho do grupo."""
    do_grupo = set((RAIZ / "AGENTS.md").read_text(encoding="utf-8").splitlines())
    faltam = [l for l in git("show", f"{REF}:AGENTS.md").splitlines() if l.strip() and l not in do_grupo]
    if faltam:
        print(f"\n  O AGENTS.md é do grupo e não é trocado, mas o do template tem {len(faltam)} linha(s) que o de vocês "
              "não tem. Copiem para a mesma seção do AGENTS.md de vocês:")
        for l in faltam:
            print(f"    {l}")


def atualizar_a_si_mesmo():
    """Piloto de 16/11/2026: o grupo rodava a versão antiga deste script, que não conhecia os arquivos novos e os
    deixava de fora. Se o template tem outra versão, troca o script e roda de novo, na mesma execução."""
    if os.environ.get("ATUALIZAR_REEXECUTADO"):
        return
    proprio = Path(__file__).resolve()
    if proprio.parent.parent != RAIZ:
        return   # rodando de fora do repositório do grupo (testes)
    novo = git("show", f"{REF}:scripts/{proprio.name}", check=False)
    if not novo or novo == proprio.read_text(encoding="utf-8"):
        return
    proprio.write_text(novo, encoding="utf-8")
    print("  o próprio script veio do template; rodando a versão nova...")
    os.execve(sys.executable, [sys.executable, str(proprio), *sys.argv[1:]],
              {**os.environ, "ATUALIZAR_REEXECUTADO": "1"})


def intocado(caminho):
    """O arquivo do grupo é igual a alguma versão antiga do template: o grupo não escreveu nele. Piloto de
    16/11/2026: os modelos antigos do pacote ficavam, e o make atividade3 os recusava como "já escritos"."""
    atual = git("hash-object", "--", caminho, check=False).strip()
    if not atual:
        return False
    for commit in git("log", "--format=%H", REF, "--", caminho, check=False).split():
        if git("rev-parse", "--verify", "--quiet", f"{commit}:{caminho}", check=False).strip() == atual:
            return True
    return False


def main():
    simular = "--sim" in sys.argv
    # Caminhos com alteração sem commit (inclusive arquivos novos). O próprio script pode ter acabado de vir do
    # template (linha de primeira vez): não conta.
    sujos = {l[3:].split(" -> ")[-1].strip('"') for l in git("status", "--porcelain", "--untracked-files=all").splitlines() if l.strip()}
    sujos.discard(f"scripts/{Path(__file__).name}")
    if "template" not in git("remote").split():
        git("remote", "add", "template", URL)
        print(f"  remoto 'template' adicionado ({URL})")
    print("  buscando o template...")
    git("fetch", "--quiet", "template")
    atualizar_a_si_mesmo()
    # Compara o template com os arquivos como estão no disco, não com o último commit: um arquivo já trazido
    # por uma rodada anterior e ainda sem commit está em dia e não pode bloquear a próxima rodada.
    mudados = [l for l in git("diff", "--name-only", REF).splitlines() if l]
    no_template = set(git("ls-tree", "-r", "--name-only", REF).splitlines())
    trazidos, mantidos, novos, antigos = [], [], set(), set()
    for caminho in mudados:
        if caminho not in no_template:
            continue   # existe só no grupo: é do grupo
        ausente = not (RAIZ / caminho).exists()
        if casa(caminho, DO_GRUPO):
            if not ausente:
                mantidos.append(caminho)
        elif casa(caminho, DO_PROFESSOR):
            trazidos.append(caminho)
        elif ausente or intocado(caminho):
            # Piloto de 16/11/2026: um arquivo que o grupo nem tem não é trabalho do grupo. Sem esta regra, os
            # modelos novos do pacote (02, 03 e 04) nunca chegavam a quem criou o repositório antes deles.
            trazidos.append(caminho)
            if ausente:
                novos.add(caminho)
            else:
                antigos.add(caminho)
        else:
            mantidos.append(caminho)
    remover = [c for c in REMOVIDOS if (RAIZ / c).exists() and c not in no_template]
    # Só recusa se a alteração sem commit está num arquivo que o script vai trocar ou apagar: é o único caso em
    # que algo se perderia. Arquivos do grupo (execuções do Lab 2, config.toml, AGENTS.md) não atrapalham.
    em_risco = sorted(sujos & set(trazidos + remover))
    if em_risco:
        sys.exit("Há alterações sem commit em arquivo(s) que o template vai trocar: " + ", ".join(em_risco) + ". "
                 "Façam commit antes (git add -A && git commit -m 'Antes de atualizar') e rodem de novo: assim, "
                 "a versão de vocês pode ser recuperada com o git.")
    for c in trazidos:
        print(f"  trazer      {c}" + (" (novo no template)" if c in novos else
                                         " (modelo antigo, sem edição do grupo)" if c in antigos else ""))
    for c in remover:
        print(f"  remover     {c} (saiu do template)")
    for c in mantidos:
        print(f"  manter      {c} (do grupo)")
    if "AGENTS.md" in mantidos:
        avisar_agents()
    if not trazidos and not remover:
        print("\nNada a trazer: o repositório já está com os arquivos do professor em dia.")
        return
    if simular:
        print(f"\n{len(trazidos)} arquivo(s) seriam trazidos e {len(remover)} removidos (--sim: nada foi alterado).")
        return
    if input(f"\nTrazer {len(trazidos)} arquivo(s) do template e remover {len(remover)}? [s/N] ").strip().lower() not in ("s", "sim"):
        print("Nada foi alterado.")
        return
    if trazidos:
        git("checkout", REF, "--", *trazidos)
    if remover:
        git("rm", "-q", "--", *remover)
    if any(c in ("pyproject.toml", "uv.lock") for c in trazidos):
        subprocess.run(["uv", "sync", "--frozen", "--quiet"], cwd=RAIZ)
        print("  dependências sincronizadas (uv sync)")
    # O commit leva só o que esta rodada trouxe ou removeu, mais o próprio script se ele mudou (veio do template
    # na rodada): sem isso sobrava `M scripts/atualizar_do_template.py` sem commit. Outras alterações do grupo ficam fora.
    proprio = f"scripts/{Path(__file__).name}"
    caminhos = list(dict.fromkeys(trazidos + remover))
    if git("status", "--porcelain", "--", proprio).strip() and proprio not in caminhos:
        git("add", "--", proprio)
        caminhos.append(proprio)
    commit = subprocess.run(["git", "commit", "-q", "-m", "Atualiza do template: labs novos e correções do professor",
                             "--", *caminhos], cwd=RAIZ, capture_output=True, text=True)
    if commit.returncode == 0:
        print(f"\n{len(trazidos)} arquivo(s) trazido(s) e {len(remover)} removido(s), e o commit já foi feito "
              "(\"Atualiza do template\"). Falta só enviar para o grupo: git push. Rodem antes `make test`. "
              "Para desfazer: git revert HEAD")
    else:
        print(f"\n{len(trazidos)} arquivo(s) trazido(s) e {len(remover)} removido(s), mas o commit NÃO foi feito "
              f"({commit.stderr.strip() or commit.stdout.strip()}). Faça: git add -A && git commit -m 'Atualiza do template' && git push")

if __name__ == "__main__":
    main()
