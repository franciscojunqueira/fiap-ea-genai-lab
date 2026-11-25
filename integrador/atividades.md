# O trabalho final

O trabalho final é a única entrega do curso. Ele é feito em grupo e vale os 100 pontos. O professor
apresenta este enunciado no fim da Aula 4. Não há atividades entre as aulas, pitch nem arguição.

**Prazo:** `<DATA>`, no Portal do Aluno.

**O que é.** A arquitetura do Bússola, o assistente do caso (`integrador/caso.md`). O grupo entrega 2 ou 3 ADRs
e os arquivos do pacote. Cada arquivo usa o que uma aula mostrou:

| Arquivo | O que o grupo decide | Vem de |
|---|---|---|
| `docs/adr/` (2 ou 3 ADRs) | como o Bússola acessa o SGC; o modelo e as rotas | os fatos do SGC do caso e a Aula 3 |
| `integrador/pacote/01-design.md` | a decisão de conhecimento, o contrato MCP e o diagrama | Aula 2 e Aula 4 |
| `integrador/pacote/02-qualidade.md` | o critério de aceite, o modelo de cada rota e a orquestração | Aula 3 |
| `integrador/pacote/03-economia.md` | o go/no-go de cada cenário e as alavancas de custo | Aula 3 |
| `integrador/pacote/04-seguranca.md` | as ameaças, o control plane e os requisitos regulatórios | Aula 4 |
| `contribuicao.md` e `uso-de-ia.md` | quem fez o quê e o que foi delegado à IA | — |

**O que vem pronto.** Os números das demonstrações do professor, gravados antes das aulas. O `make trabalho`
os coloca no pacote. Os fatos do SGC estão no caso, na seção 1 ("O que o SGC faz de fato"). O grupo
escreve só as decisões.

**Entrega:** commit na `main` do repositório do grupo e, no **Portal do Aluno da FIAP**, o link do
repositório e o **SHA do commit**. O `make trabalho-entregar` mostra os dois prontos para copiar. O
professor corrige esse commit. Deixem o repositório **privado**, com o professor (`franciscojunqueira`)
como colaborador.

**Versão que vale:** o caso, a rubrica e os checks do repositório-template. Se o professor avisar uma
correção, o `make atualizar` a traz.

**Papéis.** Operador (digita os comandos no Codespace dele), verificador (confere o que o agente
escreveu), autores (escrevem as decisões) e relator (cola o link e o SHA no Portal).

## Passos

Um comando por vez, no Codespace do operador, na ordem.

| # | Quem | O que fazer | O que aparece |
|---|---|---|---|
| 1 | Operador | `git pull` e depois `make atualizar` (responder `s`) | a lista do que veio do template |
| 2 | Operador | `make trabalho` | "preparada" e "preparado" nos arquivos do pacote e os números do Lab 2: anotem |
| 3 | Autores | abrir `integrador/pacote/01-design.md` no painel de arquivos, à esquerda. Nas seções "Decisão de conhecimento" e "Contrato MCP", os autores dizem as respostas, e o operador troca cada `[PREENCHER: ...]`, com os colchetes. Na linha `sgc:`, o fato S4 e a RC-04 do caso ajudam a responder | — |
| 4 | Operador | o grupo combina, em uma frase, como o Bússola acessa o SGC. Depois, `make trabalho-adr TEMA=sgc DECISAO="a frase do grupo"`, com as aspas, e esperar de 1 a 3 minutos | o nome do arquivo novo em `docs/adr/` e a linha `Resultado do validador: PASS`. Com FAIL, a tela diz o que corrigir. Para pedir outro ADR, apagar antes o que falhou (a tela mostra o `rm`) |
| 5 | Verificador | abrir o ADR no painel de arquivos e responder sim ou não: cada fato do SGC cita o fato do caso (S1 a S6)? Algum decisor, prazo ou requisito foi inventado? As alternativas existem no caso? Corrigir o que o agente inventou | — |
| 6 | Autores | o mesmo do passo 3 em `integrador/pacote/02-qualidade.md`: o critério de aceite, o caso de recusa do grupo, o modelo de cada rota, o que dispara uma nova eval, agente único ou subagentes em cada capacidade e os limites | — |
| 7 | Autores | o mesmo em `integrador/pacote/03-economia.md`: o critério e o go/no-go de cada cenário, o que inverteria cada decisão, as alavancas e onde ficam, o custo de cumprir a RC-03 e a premissa que mais muda a decisão | — |
| 8 | Operador | o grupo combina, em uma frase, o modelo e as rotas do Bússola. Depois, `make trabalho-adr TEMA=modelo DECISAO="a frase do grupo"` | o nome do segundo ADR e o resultado do validador |
| 9 | Verificador | conferir o segundo ADR como no passo 5 | — |
| 10 | Autores | o mesmo em `integrador/pacote/04-seguranca.md`. O resultado do ataque e da mitigação já vem pronto. Faltam a perna cortada em cada capacidade, as três decisões do control plane (residência, identidade e catálogo), onde fica cada controle e os requisitos regulatórios: LGPD e Res. CMN 4.893, arts. 15 e 16. Se o grupo não decidiu o catálogo, apaga a linha do catálogo inteira, com os colchetes, e escreve só: não decidido | — |
| 11 | Autores | voltar ao `01-design.md` e preencher a "Visão geral" e as "Decisões registradas". A "Visão geral" é o diagrama, em Mermaid, com o lugar do gateway, da checagem de permissão e da trilha de auditoria. As "Decisões registradas" têm o link de cada ADR e uma frase sobre ele | — |
| 12 | Todos | preencher `contribuicao.md` e `uso-de-ia.md`. Todos os integrantes revisam | — |
| 13 | Operador | `make trabalho-entregar`. Com FAIL, ele diz o que falta: corrigir e rodar de novo | uma caixa com o link e o SHA |
| 14 | Relator | colar no Portal o link e o SHA da caixa | — |

**O 3º ADR é opcional.** O tema é o roteamento por sensibilidade ou a identidade do Bússola. Quem fizer
abre o `claude` e pede um ADR com a skill `escrevendo-adrs`.

## O que os comandos fazem

**`make trabalho`.** Prepara o pacote. No `01-design.md`, coloca o texto pronto das seções "Decisão de
conhecimento" e "Contrato MCP", com os espaços `[PREENCHER: ...]`. As duas primeiras linhas do contrato são
as ferramentas da demonstração do Lab 3. No `02-qualidade.md`, no `03-economia.md` e no `04-seguranca.md`,
coloca os resultados das demonstrações do professor. Ele nunca apaga o que o grupo já escreveu.

**`make trabalho-adr`.** Roda um agente (Claude Sonnet) com a skill `escrevendo-adrs`. Com `TEMA=sgc`, o agente
usa como fato só o que está na seção 1 do caso ("O que o SGC faz de fato"). Com `TEMA=modelo`, ele usa os
números do `02-qualidade.md` e do `03-economia.md`. Nos dois temas, os requisitos vêm do caso. O agente só
escreve em `docs/adr/`. No fim, o comando roda o validador do ADR e mostra o resultado. O PASS confere só a
forma: a conferência do verificador (passos 5 e 9) é que diz se o ADR é verdadeiro.

**`make trabalho-entregar`.** Roda o `make pacote-check`. O PASS confere a forma: os arquivos, as seções, as
tabelas, os `[PREENCHER: ...]` trocados, os ADRs no padrão e os requisitos RC-NN que existem no caso. Com
PASS, ele faz o commit e o push e mostra o link e o SHA. Com FAIL, não envia nada.

**Números do Lab 2.** São os da demonstração do professor, e o `make trabalho` já os mostra. O texto do
grupo deve dizer que são os números da demonstração do professor. O grupo que rodou o Lab 2 em casa usa os
números dele.

> **Turma de outubro de 2026:** quem já entregou a Atividade 1 ou a 2 no formato anterior não perde nada. A
> pasta `integrador/pacote/engenharia-reversa/` pode ficar no repositório: o check não a exige.

## Como é avaliado

O trabalho final é a nota do curso inteiro, com 100 pontos. Os critérios estão em [rubrica.md](rubrica.md).
