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

Pendente: primeira rodada (cenário 1, Sonnet e Opus, sem e com a skill).
