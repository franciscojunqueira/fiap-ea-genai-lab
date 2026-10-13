# Lab 1: spec-driven no Mini-ERP

**Objetivo.** Fazer um agente implementar o cancelamento de pedido (`labs/lab1/ticket.md`) a partir
de **guias** escritos pelo grupo (spec e `AGENTS.md`), com **sensores** que conferem o resultado:
uma fitness function pronta, um teste escrito pelo grupo e os testes de aceite do ticket.

**Antes:** o operador já está com o Codespace do grupo aberto e logado
([docs/guia_codespace.md](../../docs/guia_codespace.md), passos 1 a 5).

**Tempo:** 60 min de lab. O intervalo de 15 min fica dentro da janela: o grupo para quando quiser.

| Papel | Quem | Neste lab |
|---|---|---|
| Operador | quem tem o plano | conduz o Claude Code, com a tela compartilhada |
| Autores do harness (2) | | escrevem `labs/lab1/spec.md` e a seção `## Mini-ERP` do `AGENTS.md` |
| Verificador | | liga a fitness function, escreve o teste do grupo, confere o que o agente fez |
| Relator | | preenche `labs/lab1/verificacao.md` com o verificador |

## Passos

**1. Preparar (5 min, operador).**
```bash
make lab1         # cria spec, verificação, sensores e teste do grupo; aplica o rascunho do colega
make lab1-check   # FAIL esperado: leiam as mensagens, elas dizem o que falta
```

**2. Escrever os guias (15 min, autores).**
- `labs/lab1/spec.md`: a partir do ticket, **pelo menos 3 critérios de aceite** no formato
  `- **CA-01:** Dado ..., quando ..., então ...`. O ticket tem regras escondidas na fala do
  atendimento: achem todas.
- No `AGENTS.md` da raiz, uma seção `## Mini-ERP` com o que o agente não sabe sozinho: as camadas
  (rota → service → modelo), onde fica a regra de negócio, como os erros viram HTTP
  (`mini-erp/app/services/erros.py`) e que o `verificacao.md` não é dele. Curto: o `AGENTS.md`
  entra em toda conversa.

**3. Ligar os sensores (em paralelo ao passo 2, verificador).**
- Em `labs/lab1/sensores.toml`, troque `ligado = false` por `ligado = true`. É a fitness function
  `camadas`: rotas não acessam o banco; services não conhecem HTTP. Leia a exceção registrada.
- Em `labs/lab1/testes/test_grupo.py`, escreva o teste de **um** CA da spec (cite o CA-NN) e apague
  a linha do `pytest.skip`.

**4. Rodar o agente (20 min, operador).** Abra o Claude Code em modo de plano, para o grupo ler o
plano antes de qualquer edição:
```bash
claude --permission-mode plan
```
Ponto de partida do prompt (os autores podem melhorar):

> Implemente o cancelamento de pedido descrito em `labs/lab1/spec.md`. Siga o `AGENTS.md`.
> Rode `make lab1-check` até passarem os itens de código (4, 5 e 6). Os itens 2, 3 e 7 são do
> grupo: não edite a spec, a seção do Mini-ERP no `AGENTS.md` nem o `verificacao.md`.

Leiam o plano em grupo. Aprovem só se ele puser a regra no service. Depois, deixe o agente
trabalhar.

**5. Verificar (15 min, verificador e relator).** Leiam o diff (`git diff`). Confiram pelo menos 3
afirmações do resumo final do agente no código ou com o ERP rodando (`make erp` e
http://localhost:8000/docs). Preencham `labs/lab1/verificacao.md`, incluindo a pergunta de decisão.
O check confere a forma e o comportamento da API; **o que o agente inventou, só vocês pegam.**

**6. Fechar.** `make lab1-check` com PASS, `git add -A`, commit e push no repositório do grupo.

## O que o `make lab1-check` confere

1. lab preparado;
2. spec com 3 ou mais CA-NN;
3. seção `## Mini-ERP` no `AGENTS.md`;
4. fitness function ligada e passando;
5. teste do grupo passando;
6. testes de aceite do ticket;
7. `verificacao.md` preenchido.

Cada falha diz o arquivo e o que fazer. No fim, há uma linha para a planilha da turma.

Os sensores do professor (`labs/lab1/aceite/`, `fitness_camadas.py`, `checar.py`, `conftest.py`), a
referência e as gravações em `replay/` ficam fora do alcance do agente: o `.claude/settings.json`
nega a leitura e a edição, o `AGENTS.md` avisa e o check confere se os sensores foram alterados e se
a lista de exceções mudou. Enquanto a spec não tiver 3 CAs, o item 6 só diz quantos testes de aceite
falham: as regras são para os autores acharem no ticket. Nenhuma dessas barreiras é completa; por
isso o verificador lê o diff.

## Se a cota acabar

O trabalho está nos arquivos, não na conversa:

1. O operador faz `git add -A`, commit e push do que já existe.
2. O segundo assinante (colaborador do repositório, com o Codespace já aberto antes da aula pelo
   checklist do operador) faz `git pull` no Codespace dele e abre o Claude Code com o mesmo prompt.

Sem nenhum assinante, `make lab1-referencia` aplica o código de referência (rodado por uma pessoa:
o agente é proibido de rodá-lo). O grupo segue com os passos 3 e 5 e registra no `verificacao.md`
que usou a referência.

## Desafio extra (só se o professor liberar)

`make lab1-extra` roda a skill `escrevendo-adrs` sem e com, no Haiku, num cenário que não informa
decisores nem requisitos, e mostra lado a lado o que cada execução escreveu. São 2 execuções da cota
(de 2 a 2,5 min de máquina). O verificador marca o checklist. Note que aqui a skill já existe: o
desafio mede a lacuna dela. Num projeto, a ordem é a inversa (cenários e medição sem a skill
primeiro; a skill mínima depois), e é isso que a Aula 3 pratica. **Ciclo completo:** ajustem o
`SKILL.md` para o Haiku parar de inventar e meçam de novo com `make lab1-extra ARGS=--de-novo`.

## Codex

| No Claude Code | No Codex |
|---|---|
| `CLAUDE.md` importa o `AGENTS.md` | lê o `AGENTS.md` direto |
| `claude --permission-mode plan` | `codex`, depois `/plan` |
| aceitar edições do plano | sandbox `workspace-write` com aprovação `on-request` |
| leitura de `aceite/` e `referencia/` negada no `.claude/settings.json` | sem equivalente: vale só o aviso do `AGENTS.md` |
| `make lab1-extra` (usa `claude -p`) | não se aplica |

O `make lab1`, a fitness function e o `make lab1-check` são os mesmos: não dependem do agente.
