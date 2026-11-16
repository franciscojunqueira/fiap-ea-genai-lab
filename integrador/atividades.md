# Atividades entre as aulas

Três atividades em grupo. As Atividades 1 e 2 levam cerca de 1 hora. A 3 é o trabalho final: ela
junta o que os labs e as demonstrações produziram e leva mais. Cada uma alimenta a seguinte.

**Entrega:** commit na `main` do repositório do grupo e, na atividade correspondente do **Portal
do Aluno da FIAP**, o link do repositório e o **SHA do commit** (`git rev-parse HEAD`). O professor
corrige esse commit. Deixem o repositório **privado**, com o professor
(`franciscojunqueira`) como colaborador.

**Versão que vale:** o caso, a rubrica e os checks do repositório-template. Se o professor avisar
uma correção, tragam-na com:
`git remote add template https://github.com/franciscojunqueira/fiap-ea-genai-lab.git` (uma vez),
`git fetch template` e `git checkout template/main -- integrador/caso.md integrador/rubrica.md integrador/scripts`.

| # | Quando | Atividade | Conferência | Usada em |
|---|---|---|---|---|
| 1 | Aula 1 → Aula 2 | Engenharia reversa do SGC: conferir a saída de um agente | `make er-check` | bloco elástico da Aula 2 e 1º ADR |
| 2 | Aula 2 → Aula 3 | Checkpoint: 1º ADR, decisão de conhecimento e contrato MCP | `make checkpoint-check` | trabalho final (ADR e Design) |
| 3 | Aula 3 → depois da Aula 4 (`<DATA>`) | Trabalho final (o pacote) | `make pacote-check` | nota final |

---

## Atividade 1: engenharia reversa do SGC

**Objetivo.** Saber o que o SGC faz de fato antes de decidir como o Bússola vai acessá-lo. A
documentação do SGC é de 2019 e está incompleta. Parte do que ela diz não é verdade.

**O que o grupo recebe.** Um agente já fez a engenharia reversa do SGC e escreveu o C4, as
dependências e as regras. O comando `make atividade1` copia essa saída para o pacote do grupo. O
agente errou em alguma coisa, como errará o agente de vocês no projeto. O trabalho do grupo é
conferir o que ele afirmou, não escrever tudo de novo.

**Papéis.** Operador (digita os comandos), verificador (confere as afirmações do agente), autores
(escrevem as implicações e o que mudariam no harness) e relator (cola o link e o SHA no Portal).

**Passos.** Um comando por vez, no Codespace do operador, na ordem. Esta atividade leva cerca de 1 hora
e não chama modelo, então não gasta a cota de ninguém.

| # | Quem | O que fazer | O que aparece |
|---|---|---|---|
| 1 | Operador | `git pull` e depois `make atualizar` (responder `s`) | a lista do que veio do template |
| 2 | Operador | `make legado` | a saída de um ciclo do SGC. Os outros acompanham: ela mostra comportamentos que a documentação não explica |
| 3 | Operador | `make atividade1` | "preparado" nos 4 arquivos de `integrador/pacote/engenharia-reversa/` |
| 4 | Todos | abrir `c4.md`, `dependencias.md` e `regras.md` no painel de arquivos, à esquerda, e ler. É a saída de um agente, gerada em 08/11/2026, e pode conter erros | — |
| 5 | Verificador | abrir `invencoes.md`. São 5 afirmações do agente. Para cada uma, seguir a dica da coluna "Onde conferir", ler o código ou olhar a saída do `make legado`, e trocar os dois `[PREENCHER: ...]` da linha: como conferiram (com o `arquivo:linha` que leram ou o que o `make legado` mostrou) e o veredito. O veredito é uma destas palavras: correto, errado, impreciso ou não verificável | — |
| 6 | Verificador | **corrigir a saída do agente.** Para cada afirmação marcada errada ou imprecisa, abrir o arquivo de origem (`c4.md`, `dependencias.md` ou `regras.md`, o que aparece entre parênteses na linha do `invencoes.md`), corrigir o texto e escrever ao lado a nota `corrigido pelo verificador`. A saída corrigida é o que o ADR da Atividade 2 vai usar | — |
| 7 | Autores | abrir o fim de `regras.md` e trocar os 3 `[PREENCHER: ...]` das "Implicações para o Bússola". Depois, no fim de `invencoes.md`, trocar os 2 `[PREENCHER: ...]` de "O que mudaríamos no harness" | — |
| 8 | Operador | `make atividade1-entregar`. Com FAIL, ele diz o que falta: corrigir e rodar de novo | uma caixa com o link e o SHA |
| 9 | Relator | colar no Portal o link e o SHA da caixa | — |

**Como conferir uma afirmação.** O verificador lê a linha que o agente citou e olha se o código
diz o que o agente disse. Quando a afirmação diz que algo nunca acontece, ele também procura no código e
nos dados de exemplo um caso em que acontece. Depois, compara com o que o `make legado` mostrou.

**O que o `make atividade1-entregar` confere.** O PASS confere a forma: os arquivos, as tabelas, os
espaços `[PREENCHER: ...]` trocados, as citações que existem, o veredito de cada afirmação (uma das quatro
palavras), a evidência em "Como conferimos" (`arquivo:linha` ou `make legado`), pelo menos 3 implicações
para o Bússola e a nota `corrigido pelo verificador` nos arquivos de origem do que foi marcado errado ou impreciso. Uma citação que existe pode sustentar
uma afirmação falsa, e isso só o verificador pega. Se o grupo tiver tempo, deve conferir mais afirmações
do que as 5 do `invencoes.md`.

**Entregáveis** em `integrador/pacote/engenharia-reversa/`: `c4.md`, `dependencias.md` e `regras.md`
(com as implicações para o Bússola) e `invencoes.md` (as 5 afirmações conferidas e o que mudariam no
harness). Os três primeiros já corrigidos pelo verificador. Para executar o SGC, usem só o `make legado`, que roda numa pasta isolada.

**Na Aula 2.** O que os grupos acharam de errado entra no bloco elástico da aula.

---

## Atividade 2: checkpoint

**Objetivo.** Registrar as primeiras decisões enquanto os Labs 2 e 3 estão frescos.

**Passos.** Um comando por vez, no Codespace do operador, na ordem.

| # | Quem | O que fazer | O que aparece |
|---|---|---|---|
| 1 | Operador | `git pull` e depois `make atualizar` (responder `s`) | a lista do que veio do template |
| 2 | Operador | `make atividade2` | "preparada" nas duas seções e os números do Lab 2 (os da demonstração do professor, se o grupo não rodou o lab): anotem |
| 3 | Operador | Antes, o grupo combina a decisão em uma frase: como o Bússola acessa o SGC. Depois, `make atividade2-adr DECISAO="a frase do grupo"`, com as aspas, e esperar de 1 a 3 minutos | o nome do arquivo novo em `docs/adr/` e a linha `Resultado do validador: PASS`. Com FAIL, rodar de novo |
| 4 | Verificador | abrir o ADR no painel de arquivos, à esquerda, e responder sim ou não: cada fato do SGC cita o arquivo de onde veio? Algum decisor, prazo ou requisito foi inventado? As alternativas do ADR existem no caso? Corrigir o que o agente inventou | — |
| 5 | Autores | abrir `integrador/pacote/01-design.md` no painel de arquivos; os autores dizem as respostas e o operador troca cada `[PREENCHER: ...]`, com os colchetes (são 10, nas seções "Decisão de conhecimento" e "Contrato MCP"; os PREENCHER das outras seções ficam para o pacote final) | — |
| 6 | Operador | `make atividade2-entregar`. Com FAIL, ele diz o que falta: corrigir e rodar de novo | uma caixa com o link e o SHA |
| 7 | Relator | colar no Portal o link e o SHA da caixa | — |

O `make atividade2-adr` roda um agente (Claude Sonnet) com a skill `escrevendo-adrs`. Ele lê a conferência do
verificador (`invencoes.md`), os fatos da engenharia reversa do grupo (Atividade 1) e os requisitos do caso,
sem usar como fato o que foi marcado errado ou impreciso, e escreve o ADR em `docs/adr/`. Ele não
mexe em mais nenhum arquivo. No fim, o comando roda o validador do ADR e mostra o resultado e o caminho do
arquivo. O PASS confere só a forma: o passo 4 é o que confere se o ADR é verdadeiro.

No Contrato MCP, as duas primeiras linhas são as tools da demonstração do Lab 3, e a linha
`sgc:pedir_reprocessamento_retorno` pede só duas respostas: quem aprova e se reprocessar duas vezes dá o
mesmo resultado (se não der, como o grupo protege). A resposta está na engenharia reversa do grupo
(Atividade 1). Os números do Lab 2 são os da demonstração do professor, e o `make atividade2` já os
traz. O texto do grupo deve dizer que são os números da demonstração do professor. O grupo que rodou o Lab 2
em casa usa os números dele.

---

## Atividade 3: trabalho final

**Prazo:** `<DATA>`, no Portal do Aluno. É um prazo único: ele
inclui o `04-seguranca.md`, que usa o que a Aula 4 ensina. Não há pitch.

**O que vem pronto.** Os números das demonstrações do professor, gravados antes da aula: a eval, a
orquestração e o custo por rota da Aula 3; o ataque e a mitigação da Aula 4. O grupo escreve só as
decisões.

**Passos.** Um comando por vez, no Codespace do operador, na ordem.

| # | Quem | O que fazer | O que aparece |
|---|---|---|---|
| 1 | Operador | `git pull` e depois `make atualizar` (responder `s`) | a lista do que veio do template |
| 2 | Operador | `make atividade3` | "preparado" em `02-qualidade.md` e `03-economia.md`, com os resultados das demonstrações |
| 3 | Autores | abrir `integrador/pacote/02-qualidade.md` no painel de arquivos; os autores dizem as respostas e o operador troca cada `[PREENCHER: ...]`, com os colchetes: o critério de aceite, o caso de recusa do grupo, o modelo de cada rota, o que dispara uma nova eval, agente único ou subagentes em cada capacidade e os limites | — |
| 4 | Autores | o mesmo em `integrador/pacote/03-economia.md`: o critério e o go/no-go de cada cenário, o que inverteria cada decisão, as alavancas e onde ficam, o custo de cumprir a RC-03 e a premissa que mais muda a decisão | — |
| 5 | Operador | `claude`, colar o pedido do 2º ADR (abaixo), sobre o modelo do Bússola, com a decisão do grupo no lugar dos colchetes, e esperar. Sair com `/exit` | o agente diz o nome do arquivo novo em `docs/adr/` |
| 6 | Verificador | conferir o ADR novo como na Atividade 2: cada fato cita a origem? Algum decisor, prazo ou requisito foi inventado? | — |
| 7 | Relator e autores | depois da Aula 4: completar `01-design.md` (diagrama) e `04-seguranca.md`. Se o grupo fizer o 3º ADR, o tema é o roteamento por sensibilidade ou a identidade do Bússola | — |
| 8 | Todos | preencher `contribuicao.md` e `uso-de-ia.md`; todos os integrantes revisam | — |
| 9 | Operador | `make atividade3-entregar`. Com FAIL, ele diz o que falta: corrigir e rodar de novo | uma caixa com o link e o SHA |
| 10 | Relator | colar no Portal o link e o SHA da caixa | — |

O pedido do 2º ADR (passo 5), para colar:

```text
Registre um ADR sobre o modelo e as rotas do Bússola. A decisão do grupo é: [troquem por uma frase com a decisão do grupo]. Use os números de integrador/pacote/02-qualidade.md e 03-economia.md e os requisitos de integrador/caso.md. Não invente decisores nem requisitos: marque como "a confirmar" o que não estiver nos arquivos.
```

**Como é avaliado.** O trabalho final é a nota do curso inteiro, com 100 pontos. Critérios em
[rubrica.md](rubrica.md).
