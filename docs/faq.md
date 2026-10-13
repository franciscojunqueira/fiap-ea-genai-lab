# FAQ

Primeira vez no Codespace? Siga o [guia_codespace.md](guia_codespace.md) ou, com as telas, o [guia ilustrado](guia_ilustrado_codespace.md). Antes de perguntar ao professor: cole a saída do `make check` no seu agente e peça ajuda. Se o
problema persistir, o segundo assinante do grupo assume, ou o grupo segue pelo replay do lab.

## Ambiente

**`make check` deu FAIL em "Dependências Python".** Rode `uv sync` na raiz e depois `make check`.

**`make check` deu FAIL em "Python 3.12".** Você rodou o script fora do `make`. Use `make check`.

**`make erp` diz "address already in use".** Já há um ERP rodando. Use o terminal em que ele está
ou pare todos com `pkill -f uvicorn`.

**FAIL em "MCP server".** Rode `uv run python mcp-server/server.py` para ver o erro. Se você editou
o `server.py`, confira se as 10 tools originais continuam lá.

**O banco do ERP ficou bagunçado.** Pare o ERP, apague `mini-erp/data/mini_erp.db` e rode
`make erp`: o banco é recriado com os dados iniciais.

## Login e cota

**AVISO "Agente de código instalado, sem login".** Normal antes do primeiro login: ver o passo 3 do
[checklist do operador](checklist_operador.md).

**O navegador autorizou, mas o terminal não continuou.** Isso é comum em containers. Copie o código
que o navegador mostrar e cole no terminal.

**Perdi o login depois de um "Rebuild container".** O rebuild apaga `~/.claude`. Faça o login de
novo. Não guarde token de login em variável de ambiente nem em secret: o Lab 6 mostra como conteúdo
malicioso lido pelo agente pode tentar exfiltrar o que está no ambiente.

**Posso usar a conta de um colega ou do professor?** Não. Os termos de uso proíbem compartilhar
login, chave de API ou deixar outra pessoa usar a conta. Cada operador usa a própria conta; quem não
tem plano acompanha pela tela do operador ou entra noutro grupo como verificador externo.

**"Limite do plano atingido".** Troque de operador (o segundo assinante do grupo) ou siga pelo
replay do lab. A cota do plano é do operador, não do curso.

**A cota do Codespaces está acabando.** Pare o Codespace quando não estiver usando. O consumo
aparece em github.com → Settings → Billing.

## Ferramentas

**Por que não usamos GitHub Models?** O serviço foi aposentado em 30/07/2026. As chamadas a modelo
dos labs usam a CLI do operador em modo não interativo (`claude -p`).

**Uso Codex em vez de Claude Code. O que muda?**

| Claude Code | Codex |
|---|---|
| `CLAUDE.md` (aqui, só importa o `AGENTS.md`) | `AGENTS.md` |
| skills em `.claude/skills/` | skills em `.agents/skills/` (mesma skill, por link simbólico) |
| `claude -p "…"` | `codex exec "…"` |
| login: `claude` | login: `codex login --device-auth` |

Os roteiros dos labs são escritos para Claude Code. Com Codex, o grupo usa esta tabela.

**Como vejo as tools do MCP server?** Rode `make erp` num terminal e `make mcp` em outro. O MCP
Inspector abre na porta 6274; o Codespace oferece abri-la no navegador. Se a página recusar a origem,
confira se rodou pelo `make mcp`, que já libera a URL do Codespace.

## Projeto integrador

**`make er-check` diz que uma citação não existe.** O caminho é relativo a `integrador/legado/`
(ex.: `sgc/config.py:12`) ou começa por `integrador/legado/`. Se o arquivo ou a linha não existem,
confira se o agente inventou a referência: registre isso em `invencoes.md`.

**O check deu PASS. Está certo?** O PASS confere a forma: arquivos, tabelas, citações que existem,
ADR no padrão. Se as afirmações são verdadeiras, quem confere é o verificador do grupo, e quem avalia
é a rubrica.

**Posso corrigir os bugs do SGC?** Não. O legado fica como está: as dívidas fazem parte do caso.
Para executá-lo, use `make legado`.

**O professor avisou uma correção no caso ou na rubrica. Como trago?** Siga o passo "Versão que
vale" em `integrador/atividades.md` (`git fetch template` e `git checkout template/main -- …`).

**Onde entrego?** No Portal do Aluno da FIAP, na atividade correspondente: o link do repositório do
grupo e o SHA do commit (`git rev-parse HEAD`).
