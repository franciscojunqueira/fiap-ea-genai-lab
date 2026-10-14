# Replay do Lab 2

Gravado em 14/10/2026 por `replay/lab2/gravar.py` (conta Max; Claude Code 2.1.284), sobre o corpus
de 27 documentos e as 10 perguntas de `labs/lab2/perguntas.toml`. Uma execução por condição: os
números variam de uma execução para outra. Cada pasta tem o `.json` (dados) e o `.md` (respostas).

| Condição | Acerto | Citação | Vazamentos | p50 / p95 (s) | Tokens de entrada por pergunta | Saída |
|---|---|---|---|---|---|---|
| Haiku 5.5, RAG (top_k 3) | 7/10 | 10/10 | 0 | 7,5 / 13,5 | 1.795 | 1.274 |
| Haiku 5.5, busca agêntica | 10/10 | 10/10 | 0 | 12,4 / 18,3 | 24.683 | 2.077 |
| Haiku 5.5, contexto longo | 10/10 | 10/10 | 0 | 8,8 / 15,5 | 24.885 | 1.656 |
| Sonnet 5.5, RAG | 7/10 | 10/10 | 0 | 5,2 / 8,5 | 1.740 | 531 |
| Sonnet 5.5, busca agêntica | 10/10 | 10/10 | 0 | 9,9 / 12,5 | 16.013 | 1.001 |
| Sonnet 5.5, contexto longo | 10/10 | 10/10 | 0 | 8,3 / 12,5 | 22.459 | 790 |
| Haiku 5.5, RAG, `acl = "prompt"` | 6/10 | 9/10 | 1 | 6,9 / 18,0 | 1.938 | 1.145 |
| Haiku 5.5, busca agêntica, `acl = "prompt"` | 9/10 | 9/10 | 1 | 12,3 / 18,4 | 23.038 | 1.793 |

**Leitura para o debrief.**
- O RAG errou as 3 perguntas de vários documentos (P04, P05, P08) com os dois modelos: com `top_k = 3`,
  o trecho que falta não chega ao modelo. O limite é a recuperação, não o modelo.
- Busca agêntica e contexto longo acertaram tudo, com 9 a 14 vezes mais tokens de entrada que o RAG.
  O corpus do lab cabe na janela; o da TechCorp real não caberia.
- Nenhuma condição ficou abaixo de 8 s no p95 (RC-06, TI Operacional); a mais perto foi o Sonnet com
  RAG (8,5 s). A latência inclui a partida da CLI, a resposta longa e 3 perguntas em paralelo: é medida
  de lab, não de produção, e serve para comparar as condições entre si.
- Com `acl = "prompt"`, nenhum valor-canário apareceu nas respostas, mas cada pipeline **citou como
  fonte um documento que o usuário não podia ver** (P06 no RAG; P10 na busca agêntica, que respondeu
  "encontrei um rascunho de ADR, mas não posso dizer..."). O documento Regulado já tinha ido para o
  modelo: a contenção dependeu só da obediência dele.

Plano B do grupo: `make lab2-replay` copia as condições Haiku (RAG e busca agêntica, padrão e
`acl = "prompt"`) para `labs/lab2/execucoes/`.
