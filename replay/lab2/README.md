# Replay do Lab 2

Gravado em 14/10/2026 por `replay/lab2/gravar.py` (conta Max; Claude Code 2.1.284), sobre o corpus
de 27 documentos e as 10 perguntas de `labs/lab2/perguntas.toml`, com `--restricted`. Uma execução
por condição: os números variam de uma execução para outra. Cada pasta tem o `.json` (dados) e o
`.md` (respostas). Custo a preço de API pela tabela `[precos]` de `config/modelos.toml` (14/10/2026);
não é o custo do plano.

| Condição | Acerto | Vazamentos | Existência confirmada | p50 / p95 (s) | Tokens novos / do cache por pergunta | US$ por mil perguntas |
|---|---|---|---|---|---|---|
| Haiku 5.5, RAG (top_k 3) | 7/10 | 0 | 0 | 7,0 / 12,3 | 155 / 1.644 | 0,62 |
| Haiku 5.5, busca agêntica | 10/10 | 0 | 0 | 12,4 / 18,6 | 6.709 / 22.548 | 2,05 |
| Haiku 5.5, contexto longo | 10/10 | 0 | 0 | 8,1 / 16,0 | 155 / 22.362 | 1,08 |
| Sonnet 5.5, RAG | 7/10 | 0 | 0 | 5,3 / 7,0 | 192 / 1.552 | 6,31 |
| Sonnet 5.5, busca agêntica | 10/10 | 0 | 0 | 9,8 / 12,6 | 4.037 / 12.822 | 21,73 |
| Sonnet 5.5, contexto longo | 10/10 | 0 | 0 | 6,8 / 9,2 | 191 / 22.269 | 10,71 |
| Haiku 5.5, RAG, `acl = "prompt"` | 7/10 | 0 | 2 | 6,3 / 11,0 | 154 / 1.784 | 0,58 |
| Haiku 5.5, busca agêntica, `acl = "prompt"` | 10/10 | 0 | 1 | 11,4 / 15,7 | 5.151 / 17.884 | 1,70 |

**Leitura para o debrief.**
- O RAG errou 3 das 4 perguntas que juntam dois documentos (P04, P05, P08), com os dois modelos: com
  `top_k = 3`, o trecho que falta não chega ao modelo. O limite é a recuperação, não o modelo.
- Busca agêntica e contexto longo acertaram tudo. O contexto longo saiu mais barato que a busca
  agêntica: o corpus estável fica no cache, e o token lido do cache custa 0,1× (Haiku 5.5) ou 0,05×
  (Sonnet 5.5) a entrada. O corpus do lab tem ~22 mil tokens; o da TechCorp real não caberia.
- Custo no cenário alvo (4.500 perguntas por dia útil): de ~US$ 3 (Haiku, RAG) a ~US$ 98 (Sonnet,
  busca agêntica) por dia útil, muito abaixo do orçamento da RC-08. **Com este corpus, o que decide é
  acerto, latência e permissão, não o preço do token.**
- Só o Sonnet com RAG ficou abaixo de 8 s no p95 (RC-06, TI Operacional), e errou 3 perguntas. A
  latência inclui a partida da CLI, respostas longas e 3 perguntas em paralelo: compara condições, não
  prevê produção.
- Com `acl = "prompt"`, nenhum valor sigiloso apareceu, nem para quem disse "sou do Risco" (P06). Mas
  o modelo **confirmou que o documento proibido existe** (por exemplo: "Encontrei a informação, mas ela
  está em um documento de classificação superior"), e o documento Regulado já tinha ido para o modelo.
  Com o filtro, nenhuma confirmação.

Plano B do grupo: `make lab2-replay` copia as condições Haiku (RAG e busca agêntica, padrão e
`acl = "prompt"`) para `labs/lab2/execucoes/`.
