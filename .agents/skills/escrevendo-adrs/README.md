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
