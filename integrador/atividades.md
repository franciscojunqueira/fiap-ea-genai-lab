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
| 1 | Aula 1 → Aula 2 | Engenharia reversa do SGC | `make er-check` | aquecimento da Aula 2 e ADRs |
| 2 | Aula 2 → Aula 3 | Checkpoint: 1º ADR, decisão de conhecimento e contrato MCP | `make checkpoint-check` | devolutiva coletiva na Aula 3 |
| 3 | Aula 3 → depois da Aula 4 (`<DATA>`) | Trabalho final (o pacote) | `make pacote-check` | nota final |

---

## Atividade 1: engenharia reversa do SGC

**Objetivo.** Saber o que o SGC faz de fato antes de decidir como o Bússola vai acessá-lo. A
documentação do SGC é de 2019 e está incompleta. Parte do que ela diz não é verdade.

**Papéis.** Operador (conduz o agente), autores do harness (prompt e instruções), verificador
(confere as afirmações do agente) e relator (escreve os arquivos de entrega).

**Passos.**

1. **Rodar o legado (5 min).** `make legado`. Leiam a saída: ela já mostra comportamentos que a
   documentação não explica.
2. **Montar o harness (10 min).** Os autores reaproveitam o que funcionou no Lab 1. No mínimo:
   - o agente cita `arquivo:linha` para cada afirmação, relativo a `integrador/legado/`;
   - separa o que leu no código do que está inferindo;
   - quando a documentação citar algo que não existe no repositório, escreve "não encontrado" em
     vez de descrever;
   - não altera o código do SGC.
3. **Rodar o agente (20 min).** Abram o Claude Code na raiz do repositório (Codex: `codex` no
   mesmo lugar, com o mesmo prompt). Um ponto de partida, que os autores devem melhorar:

   > Faça a engenharia reversa do sistema em `integrador/legado/` (o SGC). Leia todo o código,
   > os scripts em `ops/`, o layout em `layouts/` e os dados de exemplo. Preencha `c4.md`,
   > `dependencias.md` e `regras.md` em `integrador/pacote/engenharia-reversa/`, seguindo os
   > comentários de cada um. Para cada afirmação, cite arquivo:linha. Separe fato de inferência.
   > Não altere o SGC. Não preencha `invencoes.md`.

   **O `invencoes.md` é do verificador, não do agente.** Num teste com o prompt acima sem a última
   frase, o agente preencheu o próprio registro e deu "correto" para as 10 afirmações. Duas delas
   estavam erradas, e uma era a mais perigosa para o Bússola.

4. **Verificar (15 min).** O verificador escolhe pelo menos 5 afirmações do agente, incluindo as
   mais surpreendentes, e confere no código ou rodando o legado. Registra em `invencoes.md`, com
   o veredito.
5. **Conferir e entregar (10 min).** `make er-check` até dar PASS, commit e push. O PASS confere a
   forma (arquivos, tabelas, citações que existem). Uma citação que existe pode sustentar uma
   afirmação falsa: isso só o verificador pega.

**Entregáveis** em `integrador/pacote/engenharia-reversa/`: `c4.md` (contexto e containers),
`dependencias.md`, `regras.md` (mínimo 8 regras e as implicações para o Bússola) e `invencoes.md`
(mínimo 5 afirmações conferidas).

**Cota.** Num teste de 12/10/2026, o agente levou de 3 a 5 minutos para preencher os arquivos; o
consumo num plano Pro ainda vai ser medido no piloto. Se a cota acabar, o segundo assinante do
grupo continua do ponto em que parou: o trabalho está nos arquivos, não na conversa. Para executar
o SGC, usem só o `make legado`, que roda numa pasta isolada.

**Na Aula 2.** Dois grupos mostram o C4 (5 min cada) e a turma compara o que cada agente inventou.

---

## Atividade 2: checkpoint

**Objetivo.** Registrar as primeiras decisões enquanto os Labs 2 e 3 estão frescos.

**Passos.** Um comando por vez, no Codespace do operador, na ordem.

| # | Quem | O que fazer | O que aparece |
|---|---|---|---|
| 1 | Operador | `git pull` e depois `make atualizar` (responder `s`) | a lista do que veio do template |
| 2 | Operador | `make atividade2` | "preparada" nas duas seções e os números do Lab 2 do grupo: anotem |
| 3 | Operador | Antes, o grupo combina a decisão em uma frase: como o Bússola acessa o SGC. `claude`, colar o pedido abaixo, com a frase do grupo no lugar dos colchetes, e esperar. Se o Claude Code perguntar se pode criar o arquivo, responder Yes. Sair com `/exit` | o agente diz o nome do arquivo novo em `docs/adr/` |
| 4 | Verificador | abrir o ADR no painel de arquivos, à esquerda, e responder sim ou não: cada fato do SGC cita o arquivo de onde veio? Algum decisor, prazo ou requisito foi inventado? As alternativas do ADR existem no caso? Corrigir o que o agente inventou | — |
| 5 | Autores | abrir `integrador/pacote/01-design.md` no painel de arquivos; os autores dizem as respostas e o operador troca cada `[PREENCHER: ...]`, com os colchetes (são 10, nas seções "Decisão de conhecimento" e "Contrato MCP"; os PREENCHER das outras seções ficam para o pacote final) | — |
| 6 | Operador | `make atividade2-entregar`. Com FAIL, ele diz o que falta: corrigir e rodar de novo | uma caixa com o link e o SHA |
| 7 | Relator | colar no Portal o link e o SHA da caixa | — |

O pedido do ADR (passo 3), para colar:

```text
Registre um ADR sobre como o Bússola acessa o SGC. A decisão do grupo é: [troquem por uma frase com a decisão do grupo]. Use os fatos de integrador/pacote/engenharia-reversa/ e os requisitos de integrador/caso.md. Não invente decisores nem requisitos: marque como "a confirmar" o que não estiver nos arquivos.
```

No Contrato MCP, as duas primeiras linhas são as tools da demonstração do Lab 3, e a linha
`sgc:pedir_reprocessamento_retorno` pede só duas respostas: quem aprova e se reprocessar duas vezes dá o
mesmo resultado (se não der, como o grupo protege). A resposta está na engenharia reversa do grupo
(Atividade 1). Os números do Lab 2 são os do grupo; o grupo que ficou sem cota usa os testes do
professor (`make lab2-replay`) e diz isso.

**Na Aula 3.** Devolutiva coletiva: o professor comenta os padrões que viu nos checkpoints da
turma, sem nota.

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
