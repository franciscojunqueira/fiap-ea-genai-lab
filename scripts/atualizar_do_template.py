#!/usr/bin/env python3
"""Traz do repositório-template os labs novos e as correções (make atualizar). Executar.

O repositório do grupo nasce do template antes da Aula 1 e não recebe sozinho o que o professor publica
depois (Labs 2 a 6, correções). Este script busca o template e copia só os arquivos do professor; os
arquivos do grupo (AGENTS.md, specs, decisões, contratos, ADRs, pacote, código mudado no Lab 1) ficam
como estão. Planejar → validar → executar: o script recusa rodar com alteração não commitada, mostra a
lista do que vai trazer e só aplica depois de "s". `--sim` só mostra a lista.

Primeira vez num repositório criado antes deste script existir (uma linha, da raiz do repositório):
    git remote add template https://github.com/franciscojunqueira/fiap-ea-genai-lab.git; git fetch template && git checkout template/main -- scripts/atualizar_do_template.py && python3 scripts/atualizar_do_template.py
"""
import fnmatch
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
    "labs/*/README.md", "labs/*/codex.md", "labs/*/ticket.md", "labs/*/*.py", "labs/*/modelos/*",
    "labs/*/aceite/*", "labs/*/referencia/*", "labs/*/exemplos/*", "labs/*/perguntas.toml",
    "labs/*/descricoes/ruim.toml", "labs/*/descricoes/boa.toml",
]
# Do grupo: nunca sobrescrever, mesmo que case com um padrão acima.
DO_GRUPO = ["docs/adr/*", "labs/*/testes/*", "labs/*/execucoes/*", "labs/*/comparacoes/*", "labs/*/descricoes/grupo.toml"]
# Arquivos do professor que saíram do template: o script os apaga do repositório do grupo, com a mesma confirmação.
# 09/11/2026: o Lab 2 ficou sem check e sem decisao.md (Sessão 4b).
REMOVIDOS = ["labs/lab2/checar.py", "labs/lab2/modelos/decisao.md"]


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
    mudados = [l for l in git("diff", "--name-only", "HEAD", REF).splitlines() if l]
    no_template = set(git("ls-tree", "-r", "--name-only", REF).splitlines())
    trazidos, mantidos = [], []
    for caminho in mudados:
        if caminho not in no_template:
            continue   # existe só no grupo: é do grupo
        if casa(caminho, DO_PROFESSOR) and not casa(caminho, DO_GRUPO):
            trazidos.append(caminho)
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
        print(f"  trazer      {c}")
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
    print(f"\n{len(trazidos)} arquivo(s) trazido(s) e {len(remover)} removido(s). Para desfazer: git checkout HEAD -- <arquivo>. "
          "Rodem `make test` e salvem para o grupo todo: git add -A && git commit -m 'Atualiza do template' && git push")


if __name__ == "__main__":
    main()
