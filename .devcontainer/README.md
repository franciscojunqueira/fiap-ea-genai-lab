# Devcontainer (para o professor)

Os alunos não precisam ler isto. O operador segue `docs/checklist_operador.md`.

| Peça | Origem | Atualizar por turma? |
|---|---|---|
| Python 3.12 | imagem `mcr.microsoft.com/devcontainers/python:3-3.12-bookworm` | não |
| uv | imagem oficial `ghcr.io/astral-sh/uv`, versão fixa em `imagem/Dockerfile` | sim: versão com 2+ semanas |
| Node LTS | feature `ghcr.io/devcontainers/features/node:2` | não |
| Claude Code | feature oficial `ghcr.io/anthropics/devcontainer-features/claude-code:1` (sempre a versão mais recente) | não |
| Codex CLI, MCP Inspector | `npm install -g` no `onCreateCommand` (versão mais recente) | conferir no piloto: `codex --version`, `make mcp` |

Só fontes oficiais (Microsoft, Astral, Anthropic, OpenAI, MCP). Nenhuma feature de comunidade:
é o mesmo critério do checklist de skills e servidores de terceiros da Aula 4.

**Imagem pré-construída.** `imagem/` (Dockerfile + features) é construída pelo workflow
`.github/workflows/imagem-devcontainer.yml` e publicada em `ghcr.io/franciscojunqueira/fiap-ea-genai-lab`
(pacote público). O `devcontainer.json` dos alunos só baixa essa imagem: o repositório do grupo,
criado por "Use this template", não herda prebuild do Codespaces, mas baixa a imagem pronta.
O workflow roda `make test` e `make skill-check` dentro da imagem antes de publicar.

**Por turma:** atualizar a versão do uv em `imagem/Dockerfile` (ou só rodar o workflow
manualmente, em Actions → Imagem do devcontainer → Run workflow, para pegar o Claude Code mais recente).

**Ciclo no Codespace:** `onCreateCommand` instala as dependências Python, o Codex e o MCP Inspector;
`postCreateCommand` roda `make check`. O check de modelo dá AVISO até o operador fazer login, e isso é esperado.

Fontes, verificadas em 2026-10-12: github.com/devcontainers/ci,
docs.github.com/en/codespaces/prebuilding-your-codespaces/about-github-codespaces-prebuilds e
code.claude.com/docs/en/devcontainer.
