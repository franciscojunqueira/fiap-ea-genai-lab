# Lab 2: RAG × busca agêntica

**O problema.** O Bússola, o assistente do caso (`integrador/caso.md`), precisa responder perguntas
da Arquitetura, do Risco e do plantão de TI com fonte (RC-01) e sem mostrar a um departamento o que
ele não pode ver (RC-02). De onde vem o conhecimento? Vocês não vão programar: vão **medir** dois
jeitos prontos de responder, sobre os mesmos documentos e as mesmas 10 perguntas, e **decidir** com
os números.

**Objetivo.** Ver que a decisão de conhecimento é de arquitetura: custo por pergunta, latência,
permissão e citação, e não "qual é mais moderno". E ver onde a permissão precisa ficar.

**Antes da aula:** o operador tem o Codespace aberto e logado, e rodou `make atualizar` (traz os
Labs 2 e 3 para o repositório do grupo; se o comando não existir, veja "Atualizar do template", no
fim).

**Tempo:** 45 min de trabalho, mais 15 de intervalo, que o grupo faz quando quiser.

**Pronto quando:** `make lab2-check` mostra `lab2-check: PASS (5/5 itens)` e o trabalho foi enviado
com `git push` (passo 5).

**Termos.**
- **Corpus:** os 27 documentos da TechCorp em `knowledge/techcorp/`. Cada um tem um cabeçalho com o
  nível (Público < Interno < Regulado) e, às vezes, os departamentos que podem vê-lo.
- **RAG:** o script recorta os documentos em pedaços, acha os `top_k` pedaços mais parecidos com a
  pergunta (busca por palavras, BM25) e só eles vão para o modelo. Quem escolhe o que o modelo lê é o
  código.
- **Busca agêntica:** o modelo recebe uma pasta com os documentos e procura sozinho (Grep, Glob, Read),
  em várias idas e voltas. Quem escolhe o que ele lê é o modelo.
- **Contexto longo:** todos os documentos vão no prompt. Ninguém escolhe. Vocês veem esta perna no
  replay, no debrief.
- **Permissão no filtro × no prompt:** no filtro, os documentos que o usuário não pode ver nem chegam
  ao modelo. No prompt, chegam, e o modelo é só *pedido* para não usá-los.
- **Fato-canário:** um valor que só existe num documento Regulado. Se aparecer na resposta de quem
  não pode ver o documento, o script marca **vazamento**.
- **`--restricted`:** os scripts chamam o modelo com as ferramentas de arquivo presas à pasta temporária.
  Sem isso, a busca agêntica lê qualquer arquivo do disco, inclusive os documentos Regulados.

## Quem faz o quê

Só o **operador** digita. Os outros ditam e conferem na tela compartilhada.

| Papel | Responde por |
|---|---|
| Operador | os comandos `make` |
| Autores (2) | a hipótese e a decisão em `labs/lab2/decisao.md` |
| Verificador | conferir no corpus 4 respostas e registrar na seção "Verificação" |
| Relator | colar as linhas do script na planilha da turma e na seção "Resultados" |

## O que vocês editam: 2 arquivos

Os dois aparecem em `labs/lab2/` no passo 1 (o `make lab2` os copia de [modelos/](modelos/)).

| Arquivo | O que fazer nele | Quem dita |
|---|---|---|
| `labs/lab2/config.toml` | escrever o nome do grupo em `grupo`; no passo 3, mudar **um** parâmetro | operador |
| `labs/lab2/decisao.md` | responder as 7 seções e apagar as linhas que começam com `<` | autores, verificador, relator |

As perguntas ([perguntas.toml](perguntas.toml)), o corpus e os scripts são do professor: não editem.

## Passos

**1. Preparar e apostar (8 min).** O operador roda:

```bash
make lab2
```

e escreve o nome do grupo em `labs/lab2/config.toml` (`grupo = "Grupo 3"`). Todos leem as 10
perguntas em [perguntas.toml](perguntas.toml): cada uma tem o departamento de quem pergunta e o tipo
(busca exata, vários documentos, sem acesso, regulado com acesso, não está no corpus). **Antes de
rodar**, os autores escrevem a seção "Hipótese" do `decisao.md`: qual dos dois jeitos vai melhor em
cada tipo, e por quê.

**2. Medir (7 min, operador).**

```bash
make lab2-rodar PIPELINE=rag
make lab2-rodar PIPELINE=agentica
```

Cada comando faz 10 chamadas ao modelo (3 por vez) e leva de 1 a 3 minutos. No fim, imprime um
resumo e a **linha para a planilha da turma**, e grava as respostas num `.md` em `labs/lab2/execucoes/`.
O relator cola as duas linhas na planilha e na seção "Resultados".

A linha traz, nesta ordem: acerto, citação, vazamentos (o valor sigiloso apareceu ou o documento
proibido foi citado), existência confirmada (a resposta admitiu que o documento proibido existe),
latência p50 e p95, tokens novos, tokens lidos do cache e tokens de saída por pergunta, e **US$ por mil
perguntas**: o custo a preço de API, calculado pelo script com a tabela de preços de
`config/modelos.toml` (datada). O plano do operador não cobra assim, mas o Bússola em produção
cobraria; o token lido do cache custa uma fração do novo (Radar).

**3. Mudar uma coisa (10 min).** Escolham **um** parâmetro em `labs/lab2/config.toml`, mudem e rodem
de novo **um** pipeline. Sugestões:
- `top_k = 8`: o RAG acerta mais perguntas de vários documentos? Quanto custa a mais?
- `modelo = "sonnet"`: um modelo maior compensa o custo?
- `acl = "prompt"`: o que acontece com os vazamentos quando a permissão é só um pedido ao modelo?
- `tamanho_pedaco = 1500`: pedaços maiores ajudam?

Os grupos escolhem coisas diferentes: no debrief, a planilha junta tudo. Depois, voltem o parâmetro ao
valor original.

**4. Conferir (10 min, verificador e relator).** Abram o `.md` de uma execução em `labs/lab2/execucoes/`.
O script acerta por **expressão regular**: ele confere se os fatos esperados aparecem, não se a
resposta é verdadeira. O verificador escolhe 3 respostas que o script deu como **certas** e 1 dada
como **errada**, confere no corpus (`knowledge/techcorp/`) e preenche a tabela da seção "Verificação"
com o número da pergunta (P01 a P10) e o veredito: `confere`, `não confere` ou `parcial`.

**5. Decidir e fechar (10 min).** Os autores escrevem as seções "Decisão por tipo de pergunta",
"Permissão por documento (RC-02)", "Custo × volume" e "Pergunta de decisão". Usem os números das
linhas, não impressões. O operador fecha:

```bash
make lab2-check
git add -A
git commit -m "Lab 2 do grupo N"
git push
```

O esperado antes de terminar é FAIL, com uma explicação em cada falha e a última linha
`make: *** [...] Error 1`: as mensagens dizem o que falta. Essa decisão vai para a seção "Decisão de
conhecimento" do `integrador/pacote/01-design.md`, no checkpoint.

## O que o `make lab2-check` confere

1 lab preparado, perguntas e corpus sem alteração · 2 uma execução completa de `rag` e uma de
`agentica` · 3 uma execução com um parâmetro mudado · 4 `decisao.md` preenchido, com pelo menos 2
linhas do script coladas sem edição · 5 quatro respostas conferidas pelo verificador.

## Se a cota acabar

1. O segundo assinante do grupo continua do passo em que pararam: o trabalho está nos arquivos.
2. Sem nenhum assinante: uma **pessoa** (nunca o agente) roda `make lab2-replay`, que copia para
   `labs/lab2/execucoes/` as execuções gravadas pelo professor: os dois pipelines e a variação
   `acl = "prompt"` (as linhas saem com "replay" no lugar do nome do grupo). Com elas, façam os passos
   4 e 5 e registrem no `decisao.md` que usaram o replay.

## Codex

| No Claude Code | No Codex |
|---|---|
| `make lab2-rodar PIPELINE=rag` | `make lab2-rodar PIPELINE=rag CLI=codex` (usa `codex exec`; **não testado** com conta ChatGPT em 13/10/2026) |
| modelo do `config/modelos.toml` | o modelo padrão da conta ChatGPT; os números não comparam com os dos grupos Claude |
| busca agêntica com Grep, Glob e Read | o Codex busca com os comandos dele, na mesma pasta temporária |

Se o caminho Codex falhar, usem `make lab2-replay` e registrem no `decisao.md`.

## Atualizar do template

Repositório criado antes de os Labs 2 e 3 existirem e sem o `make atualizar`: rodem uma vez, na raiz
do repositório, a linha abaixo. Ela traz só os arquivos do professor; os do grupo ficam como estão.

```bash
git remote add template https://github.com/franciscojunqueira/fiap-ea-genai-lab.git; git fetch template && git checkout template/main -- scripts/atualizar_do_template.py && python3 scripts/atualizar_do_template.py
```
