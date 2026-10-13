# escrevendo-adrs (para quem mantém a skill)

Este arquivo é para pessoas e não é carregado pelo agente: o agente lê só o `SKILL.md` e, sob
demanda, os arquivos que ele cita.

| Arquivo | Papel |
|---|---|
| `SKILL.md` | fluxo de 5 passos e checklist de julgamento |
| `reference/modelo-adr.md` | esqueleto do ADR (liberdade baixa no formato) |
| `reference/ADR-003-armazenamento-de-alertas.md` | exemplo completo que passa no validador |
| `scripts/validar_adr.py` | ciclo de feedback determinístico; regressão em `tests/test_validar_adr.py` |
| `evals/cenarios.json` | 5 cenários (criar, criar com lacunas, revisar, substituir, regulatório) |

## Como testar em uso real

```bash
python3 scripts/testar_skill.py escrevendo-adrs <cenário> <modelo> --sem   # linha de base
python3 scripts/testar_skill.py escrevendo-adrs <cenário> <modelo>         # com a skill
```

Leia `resultados/<...>/resposta.md` e os arquivos gerados, e marque cada `expected_behavior`.
**Compare as duas condições pelos itens de julgamento** (alternativas reais, contras honestos,
nada inventado, reversão, sensores). O validador mede o formato do repositório, que a linha de
base não tem como conhecer: o PASS dele só é comparável entre execuções com a skill.

## Resultados

**2026-10-12, cenário 1** (acesso de agentes ao Mini-ERP). Claude Code 2.1.284, conta pessoal no
plano **Max** (o operador típico tem Pro: a cota foi a do Max, mas os modelos são os mesmos).
Aliases: `sonnet` = claude-sonnet-5-5 e `opus` = claude-opus-5-5. Uma execução por condição: o
resultado é indício, não medida estatística.

| Modelo | Condição | Validador | Turnos | Tokens entrada / saída | Duração |
|---|---|---|---|---|---|
| Sonnet | sem | n/a (formato livre) | 4 | 97.181 / 2.835 | 27 s |
| Sonnet | com | PASS | 9 | 134.007 / 4.529 | 46 s |
| Opus | sem | n/a (formato livre) | 11 | 190.365 / 4.990 | 66 s |
| Opus | com | PASS | 10 | 272.162 / 7.202 | 86 s |

Itens de julgamento (`expected_behavior`), nas 2 execuções sem e nas 2 com a skill:

| Item | Sem | Com |
|---|---|---|
| Três alternativas com prós e contras específicos | 2/2 | 2/2 |
| Consequência negativa da escolhida, com mitigação ou "aceito" | 2/2 | 2/2 |
| Cada requisito ligado a um sensor concreto (teste, revisão, `make`) | 0/2 | 2/2 |
| Reversão com gatilho **e** custo de voltar atrás | 0/2 (só gatilho) | 2/2 |
| Lacunas registradas como pendência, em vez de assumidas | 0/2 | 2/2 |
| Nada inventado | 1/2 (Sonnet disse "9 tools"; são 10) | 2/2 |

**Leitura.** Nos dois modelos, a skill não melhora o raciocínio sobre alternativas, que já é bom sem
ela. O que ela acrescenta é o que a rubrica cobra e o modelo não faz sozinho: rastreabilidade de
requisito a sensor, custo de reversão e pendências explícitas. Custa de 38% a 43% mais tokens de
entrada e de 20 s a 30 s a mais. O que fica para o professor: rodar os cenários 2 a 5 no piloto com
uma conta Pro.

**Ajuste feito durante o teste:** na primeira rodada sem a skill, os dois modelos acharam
`tests/test_validar_adr.py` na cópia e copiaram o formato a partir dele. O `testar_skill.py` passou
a remover, na condição sem, todo arquivo que cite a skill. Os números acima são da rodada limpa.

**2026-10-12, cenários 2 e 3, Sonnet e Haiku** (o modelo padrão do plano Pro e o mais barato).
Aliases: `sonnet` = claude-sonnet-5-5 e `haiku` = claude-haiku-4-5. Duas repetições por condição.
Correção **às cegas** por um subagente independente: as 16 saídas foram anonimizadas e avaliadas
pelos critérios de `evals/cenarios.json`, reescritos em termos neutros. A nota é a média das 2
repetições. O cenário 2 vale até 7 pontos; o 3, até 4.

| Cenário | Modelo | Sem a skill | Com a skill | Tokens de entrada (média, sem → com) |
|---|---|---|---|---|
| 2: criar ADR sem dados | Sonnet | 5,0 | **7,0** | 133 mil → 177 mil |
| 2: criar ADR sem dados | Haiku | 2,0 | **4,75** | 206 mil → 344 mil |
| 3: revisar ADR com auditoria inventada | Sonnet | 3,5 | **4,0** | 56 mil → 96 mil |
| 3: revisar ADR com auditoria inventada | Haiku | 2,75 | **4,0** | 48 mil → 182 mil |

**O que aparece:**
- Melhora nas 4 combinações. O maior ganho é no Haiku, como prevê o guia de boas práticas
  (modelos menores dependem mais de orientação).
- **Invenção.** O Sonnet não inventou nada em nenhuma condição. O Haiku inventou nas 4 execuções do
  cenário 2, **inclusive com a skill**: decisores ("Arquitetura de Soluções (time do curso)"),
  volumes ("~100 pedidos por lab", "volume > 1GB") e uma afirmação técnica falsa sobre SQLite e WAL.
  A skill organiza o ADR e leva o Haiku a criar Pendências, mas não impede a invenção. O validador
  não pega isso, porque é julgamento, não formato.
- **Escopo.** Sem a skill, o Haiku alterou o `README.md` do repositório sem pedido (2 de 2
  execuções) e uma vez escreveu o ADR em inglês. Com a skill, não houve desvio de escopo.
- **Revisão (cenário 3).** Sem a skill, o Haiku não contestou a auditoria inventada com clareza.
  Com a skill, os dois modelos a apontaram como inverificável e deram veredito ordenado.
- **Custo.** A skill aumenta os tokens de entrada: cerca de 1,3× no Sonnet e de 1,7× a 3,8× no Haiku.
  O Haiku com a skill fez de 17 a 24 turnos no cenário 2.

**Incidente na correção:** a primeira anonimização apagou linhas inteiras que citavam o validador.
Em duas respostas do Sonnet com a skill, isso removeu o veredito e a contestação da auditoria, e as
notas saíram baixas demais. As respostas foram reexportadas com troca de termos, e o mesmo corretor
reavaliou as 16 execuções. A tabela acima usa a reavaliação.
