# Rubrica do projeto integrador

Avaliação única, em grupo: **pacote de arquitetura (70)** + **arguição ao vivo (30)**. O pitch
gravado de 5 minutos é condição para a arguição e não tem nota própria.

Todos os integrantes recebem a mesma nota, salvo evidência clara de desequilíbrio na tabela de
contribuição ou na arguição. Uso de IA é permitido e declarado em `pacote/uso-de-ia.md`; não há
penalidade por estilo de texto, só por afirmação que o grupo não verificou.

## De onde vem cada critério

| Critério | Pts | Artefato | Produzido em | Sensor que confere a forma |
|---|---|---|---|---|
| ADR e decisões | 20 | `docs/adr/ADR-*.md` (2 ou 3) | Atividade 1 (fatos do legado), Atividade 2 (1º ADR), harness do Lab 1 e skill `escrevendo-adrs` | `validar_adr.py` (via `make pacote-check`) |
| Design | 15 | `pacote/01-design.md` + `pacote/engenharia-reversa/` | Atividade 1 (C4 do SGC), Lab 2 (decisão de conhecimento), Lab 3 (contrato MCP) | `make er-check`, `make checkpoint-check` |
| Qualidade | 10 | `pacote/02-qualidade.md` | Lab 4 (evals) | `make pacote-check` |
| Economia | 10 | `pacote/03-economia.md` | Lab 5 (TCO) | `make pacote-check` |
| Segurança e governança técnica | 15 | `pacote/04-seguranca.md` | Lab 6 (red team e mitigação), Aula 4; a seção "Mitigação testada" é entregue até 24h depois da Aula 4 | `make lab6-check`, `make pacote-check` |
| Carta de mudança de requisito | 15 | arguição | Aula 4 | — |
| Trade-offs | 15 | arguição | Aula 4 | — |

Os checks conferem só a forma: arquivos, seções, tabelas, citações que existem, ADR no padrão.
**Pacote com FAIL no `make pacote-check` tem o critério afetado limitado ao nível Parcial.** Vale
o check do repositório-template, rodado pelo professor sobre o commit entregue, e não a cópia do
grupo.

## Pacote (70)

Níveis: **Excelente** (90–100% dos pontos), **Bom** (70–89%), **Parcial** (40–69%),
**Insuficiente** (0–39%).

### ADR e decisões (20)

| Nível | Descritor |
|---|---|
| Excelente (18–20) | Cada ADR tem 3 alternativas que alguém competente defenderia; a escolhida tem contras honestos; a reversão diz o gatilho e o custo de voltar atrás; cada requisito citado (RC-NN do caso ou novo) leva a um sensor concreto. Os ADRs são coerentes entre si e com o design. Pelo menos um usa os fatos da engenharia reversa do SGC. |
| Bom (14–17) | Alternativas reais e rastreabilidade completa, mas um ponto fraco: reversão sem custo, contra da escolhida genérico ou um requisito com sensor vago. |
| Parcial (8–13) | Validador com PASS, mas há alternativa de palha, consequência só positiva ou fato sem origem (número, decisor ou norma que o grupo não verificou). |
| Insuficiente (0–7) | Menos de 2 ADRs, ou decisões que contradizem o design. |

### Design (15)

| Nível | Descritor |
|---|---|
| Excelente (14–15) | O diagrama mostra onde ficam gateway, checagem de permissão e auditoria. A decisão de conhecimento varia por tipo de pergunta e usa os dados do Lab 2. O contrato MCP diz quais ferramentas escrevem, qual aprovação exigem e como tratam operações que não são idempotentes. O acesso ao SGC respeita o que a engenharia reversa mostrou. |
| Bom (11–13) | Tudo presente e coerente, com uma lacuna: dados do Lab 2 citados sem efeito na decisão, ou idempotência ignorada numa ferramenta de escrita. |
| Parcial (6–10) | Diagrama genérico, que serviria para qualquer empresa, ou contrato MCP sem aprovação humana na escrita (RC-04), ou acesso ao SGC que contradiz o que a engenharia reversa mostrou. |
| Insuficiente (0–5) | Faltam o diagrama, a decisão de conhecimento ou o contrato MCP. |

### Qualidade (10)

| Nível | Descritor |
|---|---|
| Excelente (9–10) | Critério de aprovação definido antes de rodar; casos próprios, incluindo recusas (permissão, RC-12); pelo menos 2 modelos com repetição; o modelo escolhido é o mais barato que passa; limites das evals declarados. |
| Bom (7–8) | Como acima, sem repetição ou sem casos de recusa. |
| Parcial (4–6) | Resultados sem critério prévio, ou escolha de modelo que não decorre dos resultados. |
| Insuficiente (0–3) | Sem resultados medidos. |

### Economia (10)

| Nível | Descritor |
|---|---|
| Excelente (9–10) | Os 3 cenários do caso, com custo por consulta; cada premissa tem origem (caso, Lab 4, preços datados); custos além do token; critério de go/no-go definido antes e aplicado; diz o que mudaria a decisão. |
| Bom (7–8) | Como acima, com premissas sem origem ou sem os custos além do token. |
| Parcial (4–6) | Só custo de token, ou um único cenário. |
| Insuficiente (0–3) | Sem números ou com números sem nenhuma origem. |

### Segurança e governança técnica (15)

| Nível | Descritor |
|---|---|
| Excelente (14–15) | Modelo de ameaças específico do Bússola, com a perna da trifecta de cada ameaça; mitigação do Lab 6 com evidência e risco residual; posição no control plane com roteamento pelos 3 níveis de sensibilidade e identidade do agente; cada norma da seção 5 do caso vira requisito arquitetural localizado no design. |
| Bom (11–13) | Tudo presente, com um ponto genérico (ameaça de manual, sem vetor do caso) ou norma sem requisito arquitetural. |
| Parcial (6–10) | Lista de controles sem ligação com as ameaças, ou mitigação sem evidência de teste. |
| Insuficiente (0–5) | Sem modelo de ameaças ou sem mitigação. |

## Arguição (30)

Nove minutos por grupo, na Aula 4:

| Tempo | O que acontece |
|---|---|
| 0:00–0:30 | sorteio da carta |
| 0:30–2:30 | preparo do grupo (2 min) |
| 2:30–5:30 | resposta do grupo (3 min) |
| 5:30–6:30 | réplica do professor |
| 6:30–8:30 | pergunta de trade-off a um integrante sorteado |
| 8:30–9:00 | troca de grupo |

**Categorias das cartas** (as cartas em si são sorteadas na hora): residência de dados,
orçamento, SLA, explicabilidade, legado sem API, incidente de injeção. Cada carta muda um
requisito do caso e afeta pelo menos duas decisões do pacote. Não existe resposta certa: avalia-se
o raciocínio.

### Carta de mudança de requisito (15)

| Nível | Descritor |
|---|---|
| Excelente (14–15) | Identifica quais decisões do próprio pacote a carta derruba; propõe mudança concreta com o trade-off explícito (o que piora); diz como verificar que a mudança funcionou (sensor). |
| Bom (11–13) | Mudança concreta e trade-off claro, sem dizer como verificar, ou deixando de fora uma decisão afetada. |
| Parcial (6–10) | Resposta genérica ("colocar um gateway", "usar outro modelo") sem ligação com o próprio pacote. |
| Insuficiente (0–5) | Não identifica o impacto ou nega que a carta afeta o projeto. |

### Trade-offs (15)

Pergunta dirigida a um integrante sorteado, sobre uma decisão do pacote ("por que não A2?", "o
que acontece se o volume for o da expansão?").

| Nível | Descritor |
|---|---|
| Excelente (14–15) | Explica a decisão, a alternativa descartada e o custo aceito, com os dados do pacote. |
| Bom (11–13) | Explica a decisão e o custo, sem a alternativa ou sem os dados. |
| Parcial (6–10) | Descreve o que foi feito, não por quê. |
| Insuficiente (0–5) | Não conhece a decisão. |
