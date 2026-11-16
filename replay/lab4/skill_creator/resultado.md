Os 6 testes terminaram. Critério de acerto: 2 checagens por caso, que são "o problema esperado vem primeiro" e "saída com até 5 linhas".

| Caso (problema esperado) | Com skill | Sem skill |
|---|---|---|
| ADR-101 (alternativa de palha) | 1º lugar ❌ · até 5 linhas ✅. O primeiro item é a reversão. A palha vem em 2º. | 1º lugar ❌ · até 5 linhas ❌. O primeiro item é o gatilho de 80% já disparado. A palha vem como item secundário. |
| ADR-102 (RC-13 não existe) | 1º lugar ✅ · até 5 linhas ✅ | 1º lugar ✅ · até 5 linhas ❌ |
| ADR-103 (reversão "sem custo") | 1º lugar ✅ · até 5 linhas ✅ | 1º lugar ❌ · até 5 linhas ❌. O primeiro item é a falta de justificativa. A reversão vem em 5º. |

| Métrica | Com skill | Sem skill |
|---|---|---|
| Taxa de acerto (6 checagens) | **83%** (5/6) | 17% (1/6) |
| Problema esperado em 1º lugar | 2/3 | 1/3 |
| Saída com até 5 linhas | 3/3 | 0/3 |
| Tempo médio | **17 s** | 40 s |
| Tokens médios | **22,7 mil** | 28,3 mil |

- **Diferença entre os dois lados:** a skill deixou a saída curta e mais rápida e fez as três checagens aparecerem. Sem ela, a saída é um relatório longo e o problema esperado se perde no meio.
- **ADR-101:** o gabarito foi escolha minha (palha primeiro), e nenhum dos dois lados o seguiu. O gatilho de 80% já disparado, que ambos destacaram, é um problema real e talvez mais grave. Se você concorda, o caso passa a ser acerto nos dois lados, e eu ajusto o gabarito ou a skill.
- **Limites:** foi uma rodada, com 3 casos e sem repetições. Não gerei `benchmark.json` nem o viewer do skill-creator, para ficar breve, e os tempos e tokens vêm das notificações dos subagentes.

Arquivos:
- `.claude/skills/revisando-adr-bussola/SKILL.md`
- `.claude/skills/revisando-adr-bussola/evals/evals.json`
- `revisando-adr-bussola-workspace/iteration-1/` (as respostas dos 6 testes)