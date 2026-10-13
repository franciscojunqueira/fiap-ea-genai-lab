# Devcontainer (para o professor)

Os alunos não precisam ler isto. O operador segue `docs/checklist_operador.md`.

| Peça | Origem | Atualizar por turma? |
|---|---|---|
| Python 3.12 | imagem `mcr.microsoft.com/devcontainers/python:3-3.12-bookworm` | não |
| uv | imagem oficial `ghcr.io/astral-sh/uv`, versão fixa no `Dockerfile` | sim: versão com 2+ semanas |
| Node LTS | feature `ghcr.io/devcontainers/features/node:2` | não |
| Claude Code | feature oficial `ghcr.io/anthropics/devcontainer-features/claude-code:1` (sempre a versão mais recente) | não |
| Codex CLI, MCP Inspector | `npm install -g` no `onCreateCommand` (versão mais recente) | conferir no piloto: `codex --version`, `make mcp` |

Só fontes oficiais (Microsoft, Astral, Anthropic, OpenAI, MCP). Nenhuma feature de comunidade:
é o mesmo critério do checklist de skills e servidores de terceiros da Aula 4.

**Ciclo:** `onCreateCommand` instala as dependências (entra no prebuild); `postCreateCommand` roda
`make check`. O check de modelo dá AVISO até o operador fazer login, e isso é esperado.

## Prebuild (opcional, recomendado antes de cada turma)

1. No repositório-template: Settings → Codespaces → Set up prebuild.
2. Branch `main`, este `devcontainer.json`, gatilho "On configuration change", região mais próxima, histórico 1.
3. O armazenamento do prebuild é cobrado da conta dona do repositório (a do professor), dentro dos
   GB incluídos. Quando eles acabam, o GitHub desativa novos prebuilds.

**Limite:** o prebuild vale para codespaces abertos **neste** repositório. Um repositório criado por
"Use this template" não herda o prebuild, então o primeiro build no repositório do grupo leva alguns
minutos (tempo ainda não medido: medir no piloto). Fontes, verificadas em 2026-10-12:
docs.github.com/en/codespaces/prebuilding-your-codespaces/configuring-prebuilds e
code.claude.com/docs/en/devcontainer.
