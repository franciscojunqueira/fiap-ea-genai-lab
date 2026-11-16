# Lab 4 (Aula 3): orquestrar agentes, a skill e a eval

**Na Aula 3, este lab é uma demonstração do professor.** Os grupos não rodam nada em aula: acompanham a
tela e respondem no chat. Este README é o roteiro da demonstração e serve para quem quiser rever em casa.
Não é aula de programação: cada comando abaixo vem com o conceito que ele mostra.

## As três demonstrações deste lab

| Bloco da aula | Comando | O que aparece na tela | Conceito |
|---|---|---|---|
| ① Arquitetura de agentes | `make lab4-orquestrar MODO=ambos` | a mesma revisão de 3 ADRs feita por um agente e por um orquestrador com 3 subagentes, com os problemas achados, os tokens e o tempo de cada modo | **subagente** e **orquestrador**: o multiagente custa mais tokens e só compensa com contexto poluído, paralelismo ou ferramentas demais |
| ② A skill | `make lab4-skill` | a ordem em que o agente usa a skill `escrevendo-adrs`: carrega o corpo do `SKILL.md`, lê uma referência, roda o validador | **divulgação progressiva**: a skill só entra no contexto quando o pedido combina com a descrição |
| ② A skill | `make lab4-skill-replay` | a skill que o **skill-creator** criou e a tabela com e sem a skill | **skill como ativo**: criada, testada e comparada antes de entrar no catálogo |
| ③ A eval | `make lab4-eval` | 12 casos, 3 tentativas cada, com o avaliador de cada caso, o pass@3 e o pass^3 | **eval**: casos, aplicação, avaliador e resultado; acertar uma vez não é acertar sempre |
| ③ A eval | `make lab4-juiz PERGUNTA=P03` | a resposta da P03 da Aula 2, o que o script disse e o que o juiz disse | **o avaliador também erra**: o script procura palavras, o juiz lê o sentido |

## O que cada demonstração usa

- **Orquestração:** `labs/lab4/orquestracao/adrs/` tem três ADRs sintéticos do Bússola, cada um com um
  problema plantado (uma alternativa que ninguém defenderia, um requisito que não existe no caso e uma
  reversão "sem custo"). O `orquestrar.py` chama o Claude Code nos dois modos, com o mesmo modelo.
- **Skill:** o `skill_carregada.py` copia a skill `escrevendo-adrs` para uma pasta temporária e mostra os
  passos da sessão. O skill-creator é instalado como plugin do marketplace oficial da Anthropic
  (`claude plugin marketplace add anthropics/skills` e `claude plugin install example-skills@anthropic-agent-skills`).
- **Eval:** as 10 perguntas do Lab 2 (`labs/lab2/perguntas.toml`) são conferidas pelo **script**; os casos
  de recusa de `casos.toml` (RC-12) são conferidos pelo **juiz** (`juiz.py`, um modelo com um critério
  escrito em frase). A turma acrescenta casos em `casos_turma.toml`.

## Onde a eval roda (o diagrama da aula)

1. **Antes da produção:** sobre o conjunto de casos de referência. É o portão de go-live, de adoção de uma
   skill e de troca de modelo. Aqui, no Codespace do professor.
2. **Na integração contínua:** a cada mudança de prompt, skill, modelo ou base. É a eval de regressão.
3. **Em produção:** sobre uma amostra das conversas reais, que vem do registro do gateway (Lab 5).

## Se algo falhar na aula

Cada demonstração tem a gravação do professor: `make lab4-orquestrar-replay`, `make lab4-skill-replay` e
`make lab4-replay`. Os números das gravações de 16/11/2026 estão nelas.

## Refazer em casa (opcional)

Com o login do Claude Code no Codespace: `make lab4-orquestrar MODO=unico`, `make lab4-skill` e
`make lab4-eval K=1`. A eval completa (`K=3`) faz 36 chamadas ao modelo e gasta cota do plano.

Não há `make lab4-check`: os números entram prontos no trabalho final, e o grupo escreve as decisões.
