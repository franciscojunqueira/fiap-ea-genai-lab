#!/usr/bin/env python3
"""Traz do repositório-template os labs novos e as correções (make atualizar). Executar.

O repositório do grupo nasce do template antes da Aula 1 e não recebe sozinho o que o professor publica
depois (Labs 2 a 6, correções). Este script busca o template e copia só os arquivos do professor; os
arquivos do grupo (AGENTS.md, specs, decisões, contratos, ADRs, pacote, código mudado no Lab 1) ficam
como estão. No fim, lista o que mudou: confiram e façam commit.

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


def git(*args, check=True):
    proc = subprocess.run(["git", *args], cwd=RAIZ, capture_output=True, text=True)
    if check and proc.returncode != 0:
        sys.exit(f"git {' '.join(args)} falhou: {proc.stderr.strip()}")
    return proc.stdout


def casa(caminho, padroes):
    return any(fnmatch.fnmatch(caminho, p) for p in padroes)


def main():
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
    if trazidos:
        git("checkout", REF, "--", *trazidos)
    for c in trazidos:
        print(f"  atualizado  {c}")
    for c in mantidos:
        print(f"  mantido     {c} (do grupo; para ver a versão do template: git diff HEAD {REF} -- {c})")
    if any(c in ("pyproject.toml", "uv.lock") for c in trazidos):
        subprocess.run(["uv", "sync", "--frozen", "--quiet"], cwd=RAIZ)
        print("  dependências sincronizadas (uv sync)")
    print(f"\n{len(trazidos)} arquivo(s) atualizado(s). Rodem `make test` e façam commit: "
          "git add -A && git commit -m 'Atualiza do template'")


if __name__ == "__main__":
    main()
