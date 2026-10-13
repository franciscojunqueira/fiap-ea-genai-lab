# Replay do Lab 1

Duas condições, gravadas por `claude -p` numa cópia limpa depois do `make lab1`:

- **ticket:** só o ticket, sem spec nem seção do `AGENTS.md`; prompt "Termine o cancelamento de
  pedido do ticket". A fitness function é conferida depois, ligada, para mostrar o que ela teria barrado.
- **harness:** o harness de exemplo do grupo (spec com 4 CAs, seção `## Mini-ERP` no `AGENTS.md`,
  teste do grupo, fitness ligada) e o prompt do README do lab. O `verificacao.md` fica vazio: é humano.

**Gravar de novo** (gasta cota de quem roda): `python3 replay/lab1/gravar.py sonnet ticket harness`.
Cada condição fica em `gravacao/<modelo>-<condição>/` (diff, resposta, `lab1-check.txt`, métricas).

## Gravação de 12–13/10/2026

Claude Code 2.1.284, conta pessoal no plano Max. Uma execução por condição: é registro, não medida.

| Modelo | Condição | Camadas | Aceite | `lab1-check` | Turnos | Tokens de entrada | Duração |
|---|---|---|---|---|---|---|---|
| Sonnet 5.5 | ticket | PASS | PASS | 2/7 (itens do grupo vazios) | 8 | 138 mil | 27 s |
| Sonnet 5.5 | harness | PASS | PASS | 6/7 (falta só a verificação humana) | 15 | 212 mil | 33 s |
| Haiku 4.5 | ticket | **FAIL (4 violações)** | PASS | 2/7 | 16 | 471 mil | 66 s |
| Haiku 4.5 | harness | PASS | PASS | 6/7 | 19 | 401 mil | 76 s |

## Registro do verificador

| Condição | O que aconteceu | Quem pegou |
|---|---|---|
| Haiku, ticket | Completou o rascunho **na rota**, acessando o banco direto. A API funciona (aceite PASS), mas a arquitetura não: a fitness function aponta 4 linhas. No resumo, afirmou que a implementação "segue o padrão do projeto (similar a `faturas.py`)": copiou a dívida registrada e chamou de padrão | fitness function (as linhas); verificador (a afirmação falsa) |
| Haiku, ticket | **Tentou ler os testes de aceite**, apesar do aviso no `AGENTS.md`. A regra `deny` do `.claude/settings.json` negou a leitura | permissão (guia determinístico) |
| Haiku, harness | Moveu a regra para o service; disse que o aceite validava "CA-02 e CA-03", o que é verdade, mas o teste do grupo cobre o CA-04 | verificador |
| Sonnet, ticket | Mesmo sem spec, pôs a regra no service, tratou faturado e clique duplo e listou o que era do grupo sem tocar | — |
| Sonnet, harness | Considerou só `CRIADO` como cancelável ("qualquer status novo vai dar 409"): decisão não pedida, registrada no resumo | verificador (decidir se aceita) |

**Leitura para o debrief.**
- **O mesmo comportamento da API pode esconder um defeito de arquitetura:** só o sensor de camadas
  viu a rota do Haiku. Os testes de aceite passaram nos dois casos.
- **O código existente é um guia forte:** o Sonnet seguiu as rotas finas sem que ninguém mandasse.
  O Haiku seguiu o rascunho. O harness do grupo levou os dois ao mesmo resultado.
- **Guia pede, permissão garante:** o `AGENTS.md` mandava não ler os testes de aceite; o Haiku
  tentou, e só a regra `deny` o barrou. (No workspace não confiável da gravação, o `deny` do projeto
  valeu; o `allow`, não: ver `replay/escada/README.md`.)
- **Consumo:** o agente leva menos de 1,5 min. O tempo do lab é da spec e da verificação.
