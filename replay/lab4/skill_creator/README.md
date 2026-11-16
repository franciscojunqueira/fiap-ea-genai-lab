# Replay: o skill-creator cria e testa uma skill (Aula 3, Demonstração 2)

Gravado em 16/11/2026 pelo professor, na conta de testes, com o Claude Code 2.1.284 e o modelo
claude-sonnet-5-5. O skill-creator veio do plugin `example-skills` do marketplace oficial da Anthropic:

```bash
claude plugin marketplace add anthropics/skills
claude plugin install example-skills@anthropic-agent-skills
```

O pedido (em modo não interativo, com as respostas da entrevista já dadas) pediu a skill
`revisando-adr-bussola`, três casos de teste com os ADRs de `labs/lab4/orquestracao/adrs/` e a comparação
com e sem a skill.

- `skill_criada/SKILL.md`: a skill que o skill-creator escreveu.
- `skill_criada/evals/evals.json`: os três casos de teste que ele criou.
- `resultado.md`: a tabela final, com e sem a skill.

**Números da sessão:** cerca de 36 s até criar a skill e disparar os testes; 6 subagentes (3 casos com a
skill e 3 sem); cerca de 1 milhão de tokens no total; US$ 0,89 a preço de API. Com a skill: 5 de 6
checagens; sem a skill: 1 de 6. Uma rodada, 3 casos, sem repetição: é uma amostra pequena.
