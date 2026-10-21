# Lab 1: spec-driven no Mini-ERP

**O problema.** No Mini-ERP do curso não dá para cancelar um pedido; o atendimento pediu isso no
[ticket.md](ticket.md). Vocês não vão programar: vão **especificar**, deixar um agente de IA (o
Claude Code) implementar e **verificar** o que ele fez e o que inventou.

**Objetivo.** Ver que o ganho não está em pedir melhor ao agente, e sim no que o grupo põe em volta
dele: **guias** que orientam antes (a spec, o `AGENTS.md`) e **sensores** que conferem depois (testes,
a fitness function, a pessoa que verifica).

**Antes da aula:** o operador já tem o Codespace do grupo criado e logado
([guia do Codespace](../../docs/guia_codespace.md), passos 1 a 5). No dia, ele reabre esse Codespace (passo 9).

**Operador com Codex (plano ChatGPT)?** Sigam este README normalmente; no **passo 3**, usem a versão
Codex em [codex.md](codex.md).

**Tempo:** 60 min de trabalho, mais 15 de intervalo, que o grupo faz quando quiser.

**Pronto quando:** `make lab1-check` mostra `lab1-check: PASS (7/7 itens)` e o trabalho foi enviado
com `git push` (passo 5).

**Termos.**
- **Rota:** a porta de entrada da API (`mini-erp/app/routes/`). **Service:** onde fica a regra de
  negócio (`mini-erp/app/services/`). A rota só chama o service; quem fala com o banco é o service.
- **Critério de aceite (CA):** uma frase "Dado..., quando..., então..." que vira teste.
- **Fitness function:** teste automático de arquitetura; aqui, a `camadas` reprova rota que acessa o
  banco.
- **Plano:** antes de mexer no código, o agente mostra o que pretende fazer, e o grupo aprova ou corrige.
- **`AGENTS.md`:** instruções do repositório para o agente, em texto. Ele lê o arquivo inteiro no
  início de toda sessão. O `CLAUDE.md` da raiz só tem a linha `@AGENTS.md`: é o nome que o Claude
  Code procura, e essa linha importa o outro.
- **Skill:** um procedimento pronto, num arquivo `SKILL.md`. O agente lê sempre o nome e a descrição
  do cabeçalho; o resto, só quando o pedido casa com a descrição.
- Os dois são texto, e o agente pode não seguir. O que precisa ser garantido está no
  `.claude/settings.json` (permissões), que o Claude Code aplica (o Codex não tem equivalente:
  tabela no fim).

## Quem faz o quê

Só o **operador** tem o Codespace aberto e digita. Os outros **ditam o conteúdo** do arquivo pelo qual
respondem e conferem na tela compartilhada. Com 4 pessoas, há um autor só.

| Papel | Responde por |
|---|---|
| Operador (quem tem o plano) | digitar os comandos e conduzir o Claude Code |
| Autores (2) | `spec.md` e a seção `## Mini-ERP` do `AGENTS.md` |
| Verificador | `sensores.toml`, `testes/test_grupo.py` e a conferência do que o agente fez |
| Relator | `verificacao.md` (com o verificador); indica o que o operador copia do agente |

## O que vocês fazem: nenhum arquivo novo, 5 arquivos para editar

Quatro desses arquivos **não existem** no repositório até o passo 1: o comando `make lab1` os cria em
`labs/lab1/`, copiando os modelos de [modelos/](modelos/). No site do GitHub vocês não os acham; no
Codespace, depois do `make lab1`, eles aparecem. Editem sempre o arquivo em `labs/lab1/`, **não** o
modelo.

| Arquivo | De onde vem | O que fazer nele | Quem dita | Exemplo (de outro ticket) |
|---|---|---|---|---|
| `labs/lab1/spec.md` | `make lab1` | preencher as 5 seções do modelo e apagar as linhas que começam com `<`; em "Critérios de aceite", **3 ou mais**, tirados do ticket | autores | [spec_exemplo.md](exemplos/spec_exemplo.md) |
| `AGENTS.md` (raiz do repositório) | já existe | **acrescentar no fim** uma seção `## Mini-ERP` de 4 a 6 linhas | autores | [agents_secao_exemplo.md](exemplos/agents_secao_exemplo.md) |
| `labs/lab1/sensores.toml` | `make lab1` | trocar `ligado = false` por `ligado = true` | verificador | não precisa |
| `labs/lab1/testes/test_grupo.py` | `make lab1` | escrever o teste de **1** critério da spec e apagar a linha `pytest.skip(...)` | verificador | [teste_exemplo.py](exemplos/teste_exemplo.py) |
| `labs/lab1/verificacao.md` | `make lab1` | responder as 5 seções | relator e verificador | [verificacao_exemplo.md](exemplos/verificacao_exemplo.md) |

**O código não é com vocês:** `mini-erp/app/services/pedidos.py` e `mini-erp/app/routes/pedidos.py`
são editados **pelo agente** (passo 3). Os exemplos resolvem outro ticket (estoque baixo): mostram a
forma, não a resposta.

## Passos

**1. Preparar (5 min).** O operador roda:

```bash
make lab1
make lab1-check
```

O esperado é `lab1-check: FAIL (1/7 itens)`, com uma explicação em cada falha, e a última linha
`make: *** [...] Error 1`. Isso é normal: o FAIL é o ponto de partida, e as mensagens dizem o que falta.

Enquanto isso, os outros abrem no GitHub, cada um no seu navegador, o [AGENTS.md](../../AGENTS.md) e o
[SKILL.md da escrevendo-adrs](../../.agents/skills/escrevendo-adrs/SKILL.md), onde basta a tabelinha
`name | description` no topo da página (é o cabeçalho). Quem ainda não aceitou o convite do
repositório do grupo abre os mesmos arquivos no
[repositório-template](https://github.com/franciscojunqueira/fiap-ea-genai-lab/blob/main/AGENTS.md).
Dois minutos, e respondam em voz alta: o que o agente lê no início de toda sessão? Da skill, o que
ele lê sempre e o que só quando o pedido casa com a descrição? (Respostas nos **Termos**, acima.) No
passo 2, os autores escrevem no fim desse mesmo `AGENTS.md`.

**2. Guias e sensores (15 min, autores e verificador ao mesmo tempo).** Os autores ditam ao operador; o
verificador rascunha o teste num bloco de notas ou no chat do grupo e dita quando os autores terminarem.

Autores:
- `labs/lab1/spec.md`: cada critério no formato `- **CA-01:** Dado ..., quando ..., então ...`. O
  ticket tem regras escondidas na fala do atendimento: achem todas.
- Seção `## Mini-ERP` no fim do `AGENTS.md`: o que o agente não sabe sozinho. A regra de negócio fica
  em `mini-erp/app/services/` (escrevam esse caminho: o check procura por ele), a rota só chama o
  service, e os erros saem de `mini-erp/app/services/erros.py`. Digam também que a spec, os testes do
  grupo e o `verificacao.md` não são dele.

Verificador:
- `labs/lab1/sensores.toml`: `ligado = true`. Isso liga a fitness function `camadas`, que reprova
  rota acessando o banco.
- `labs/lab1/testes/test_grupo.py`: escolham **uma** regra do ticket e escrevam o teste dela. Prefiram
  uma que o código atual erra (pedido faturado ou clique duplo); o modelo traz as chamadas prontas,
  comentadas. Ponham no nome do teste o número que o CA recebeu na spec (`test_ca_03_...`), conferindo
  com os autores. O teste precisa de pelo menos um `assert` (a conferência). **É esperado que o item 5
  do check falhe até o passo 3**: o teste mostra o erro que o agente vai corrigir.

**3. Agente (20 min, operador).** O agente costuma levar 1 ou 2 minutos; o resto é o grupo lendo o plano.

```bash
claude --permission-mode plan
```

Colem o prompt abaixo (os autores podem melhorá-lo):

```text
Implemente o cancelamento de pedido descrito em labs/lab1/spec.md. Siga o AGENTS.md. Rode make lab1-check até passarem os itens 4, 5 e 6. Não edite labs/lab1/spec.md, labs/lab1/sensores.toml, labs/lab1/testes/, labs/lab1/verificacao.md nem a seção Mini-ERP do AGENTS.md: são do grupo.
```

O agente lê o código e mostra um **plano**. Leiam em grupo:
- se o plano põe a regra em `mini-erp/app/services/pedidos.py` e deixa a rota só chamando essa
  função, escolham **Yes, and use auto mode**;
- se não, escolham **Tell Claude what to change** e digitem o que corrigir.

Quando ele terminar, o operador copia o resumo final do agente e cola **no topo** do `verificacao.md`,
antes da primeira seção (lá ele não conta como resposta). Depois digita `/exit`.

**4. Verificar (15 min, verificador e relator).**
- Vejam o que mudou no painel **Source Control** (ícone de ramificação, à esquerda): clique em cada
  arquivo para ver o antes e o depois.
- Confiram **pelo menos 3 afirmações** do resumo do agente no código. Para ver a API funcionando,
  abram um segundo terminal (botão **+** do terminal), rodem `make erp` e abram a porta 8000 na aba
  **Ports** ([guia do Codespace](../../docs/guia_codespace.md), passo 7); acrescentem `/docs` ao
  endereço.
- Preencham as 5 seções do `verificacao.md`. O check confere a forma; **o que o agente inventou, só
  vocês pegam.**

**5. Fechar (5 min, operador).**

```bash
make lab1-check
git add -A
git commit -m "Lab 1 do grupo N"
git push
```

Se der FAIL, corrijam o que a mensagem diz e rodem `make lab1-check` de novo antes do commit. Com
PASS 7/7, o relator cola na planilha da turma a linha que o check imprime no fim.

## O que o `make lab1-check` confere

1 lab preparado · 2 spec com 3 ou mais CAs · 3 seção `## Mini-ERP` · 4 fitness function ligada e
passando · 5 teste do grupo passando · 6 testes de aceite do ticket · 7 `verificacao.md` preenchido.

Os sensores do professor (`aceite/`, `checar.py`, `conftest.py`, `fitness_camadas.py`) ficam fora do alcance do
agente, mas nenhuma barreira é completa: por isso o verificador lê o que mudou.

## Se a cota acabar

1. O operador roda `git add -A`, `git commit -m "Lab 1 parcial"` e `git push`.
2. O segundo assinante, no Codespace dele, roda `git pull` e continua do passo 3 com o mesmo prompt.

Sem nenhum assinante: uma **pessoa** (nunca o agente) roda `make lab1-referencia`, que aplica o código
de referência. O grupo faz os passos 2, 4 e 5 e registra no `verificacao.md` que usou a referência.

## Desafio extra (só se o professor liberar)

`make lab1-extra` roda a skill `escrevendo-adrs` sem e com a skill, no Haiku, e mostra lado a lado o
que cada execução escreveu (2 a 3 min, 2 chamadas da cota). O verificador marca o checklist que
aparece. Para ir além: ajustem `.agents/skills/escrevendo-adrs/SKILL.md` para o Haiku parar de inventar
e meçam de novo com `make lab1-extra ARGS=--de-novo`.

## Codex

| No Claude Code | No Codex |
|---|---|
| `CLAUDE.md` importa o `AGENTS.md` | lê o `AGENTS.md` direto |
| `claude --permission-mode plan` | `codex --sandbox danger-full-access --ask-for-approval on-request`, depois `/plan` |
| **Yes, and use auto mode** no plano | **Yes, implement this plan**; sem o sandbox do Codex, que não sobe no Codespace ([guia do Codex](../../docs/guia_codex.md), passo 6) |
| leitura de `aceite/`, `referencia/`, `exemplos/` e `replay/` negada no `.claude/settings.json` | sem bloqueio: vale só o pedido do `AGENTS.md`, e o verificador confere |
| `make lab1-extra` (usa `claude -p`) | não se aplica |

Passo 3 completo com Codex: [codex.md](codex.md). O `make lab1`, a fitness function e o `make lab1-check` são os mesmos: não dependem do agente.
