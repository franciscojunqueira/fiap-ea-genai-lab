# Rubrica do projeto integrador

Avaliação única, em grupo: o **trabalho final (100)**, que é o pacote de arquitetura, entregue
depois da Aula 4. Não há arguição, pitch nem carta com nota.

Todos os integrantes recebem a mesma nota, salvo evidência clara de desequilíbrio na tabela de
contribuição. Uso de IA é permitido e declarado em `pacote/uso-de-ia.md`; não há penalidade por
estilo de texto, só por afirmação que o grupo não verificou.

## De onde vem cada critério

| Critério | Pts | Artefato | Produzido em | Sensor que confere a forma |
|---|---|---|---|---|
| ADR e decisões | 30 | `docs/adr/ADR-*.md` (2 ou 3) | Atividade 1 (fatos do legado), Atividade 2 (1º ADR), harness do Lab 1 e skill `escrevendo-adrs` | `validar_adr.py` (via `make pacote-check`) |
| Design | 20 | `pacote/01-design.md` + `pacote/engenharia-reversa/` | Atividade 1 (C4 do SGC), Lab 2 (decisão de conhecimento), Lab 3 (contrato MCP) | `make er-check`, `make checkpoint-check` |
| Qualidade | 15 | `pacote/02-qualidade.md` | Aula 3 (demonstrações 1 e 3: orquestração e eval); a decisão é do grupo | `make pacote-check` |
| Economia | 15 | `pacote/03-economia.md` | Aula 3 (demonstração 5: custo por rota); a decisão é do grupo | `make pacote-check` |
| Segurança e governança técnica | 20 | `pacote/04-seguranca.md` | Demonstração 1 (ataque e mitigação) e Aula 4 | `make pacote-check` |

Os checks conferem só a forma: arquivos, seções, tabelas, citações que existem, ADR no padrão.
**Regra provisória: pacote com FAIL no `make pacote-check` tem o critério afetado limitado ao nível Parcial.** Vale
o check do repositório-template, rodado pelo professor sobre o commit entregue, e não a cópia do
grupo.

## Trabalho final (100)

Níveis: **Excelente** (90–100% dos pontos), **Bom** (70–89%), **Parcial** (40–69%),
**Insuficiente** (0–39%).

### ADR e decisões (30)

| Nível | Descritor |
|---|---|
| Excelente (27–30) | Cada ADR tem 3 alternativas que alguém competente defenderia; a escolhida tem contras honestos e diz o custo aceito, com um dado do caso ou das demonstrações; a reversão diz o gatilho e o custo de voltar atrás; cada requisito citado (RC-NN do caso ou novo) leva a um sensor concreto. Os ADRs são coerentes entre si e com o design. Pelo menos um usa os fatos da engenharia reversa do SGC. |
| Bom (21–26) | Alternativas reais e rastreabilidade completa, mas um ponto fraco: reversão sem custo, contra da escolhida genérico ou um requisito com sensor vago. |
| Parcial (12–20) | Validador com PASS, mas há alternativa de palha, consequência só positiva ou fato sem origem (número, decisor ou norma que o grupo não verificou). |
| Insuficiente (0–11) | Menos de 2 ADRs, ou decisões que contradizem o design. |

### Design (20)

| Nível | Descritor |
|---|---|
| Excelente (18–20) | O diagrama mostra onde ficam gateway, checagem de permissão e auditoria. A decisão de conhecimento varia por tipo de pergunta e usa os dados do Lab 2. O contrato MCP diz quais ferramentas escrevem, qual aprovação exigem e como tratam operações que não são idempotentes. O acesso ao SGC respeita o que a engenharia reversa mostrou. |
| Bom (14–17) | Tudo presente e coerente, com uma lacuna: dados do Lab 2 citados sem efeito na decisão, ou idempotência ignorada numa ferramenta de escrita. |
| Parcial (8–13) | Diagrama genérico, que serviria para qualquer empresa, ou contrato MCP sem aprovação humana na escrita (RC-04), ou acesso ao SGC que contradiz o que a engenharia reversa mostrou. |
| Insuficiente (0–7) | Faltam o diagrama, a decisão de conhecimento ou o contrato MCP. |

### Qualidade (15)

Os resultados das demonstrações da Aula 3 vêm prontos no `02-qualidade.md` (`make atividade3`). A nota está
nas decisões do grupo.

| Nível | Descritor |
|---|---|
| Excelente (14–15) | O critério de aceite é explícito: a taxa mínima e a regra de recusa. O grupo escreve um caso de recusa próprio (permissão ou RC-12), com a resposta esperada. O modelo de cada rota sai dos números da demonstração, e a rota no Brasil tem uma saída para a RC-03. O grupo diz pelo menos dois gatilhos de nova eval (um deles, a troca de modelo pelo fornecedor). Para cada capacidade, decide entre agente único e subagentes pelo critério (contexto, paralelismo ou ferramentas). Diz o que a eval não cobre. |
| Bom (11–13) | Como acima, mas falta um destes itens: o caso de recusa próprio, a rota no Brasil, os gatilhos ou os limites. |
| Parcial (6–10) | Critério vago ("respostas boas"); modelo de rota que não decorre dos números; ou orquestração escolhida sem critério ("subagentes porque é melhor"). |
| Insuficiente (0–5) | Sem critério de aceite ou sem o modelo das rotas. |

### Economia (15)

Os custos da Demonstração 5 vêm prontos no `03-economia.md` (`make atividade3`). A nota está nas decisões do grupo.

| Nível | Descritor |
|---|---|
| Excelente (14–15) | O grupo diz o critério de go/no-go de cada cenário. No cenário alvo, o critério é o orçamento da RC-08; no piloto e na expansão, o grupo diz qual critério usa. O grupo decide cada cenário aplicando o seu critério, com a divisão de rotas escolhida, e diz o que inverteria cada decisão. Diz pelo menos duas alavancas e onde cada uma fica (gateway ou aplicação). Diz como atende a RC-03 e o que isso faz com o custo, e qual premissa mais muda a decisão. |
| Bom (11–13) | Go/no-go por cenário com critério, mas falta um destes itens: o que inverteria a decisão, onde ficam as alavancas, a RC-03 ou a premissa que mais pesa. |
| Parcial (6–10) | Um único go/no-go para todos os cenários, ou decisão que contradiz os números. |
| Insuficiente (0–5) | Sem decisão de go/no-go. |

### Segurança e governança técnica (20)

| Nível | Descritor |
|---|---|
| Excelente (18–20) | Modelo de ameaças específico do Bússola, com a perna da trifecta de cada ameaça. A mitigação da Demonstração 1 aplicada ao Bússola: que perna ela corta, em que capacidade, e o risco que sobra. O control plane nas três decisões. A primeira é o roteamento pelos 3 níveis de sensibilidade, com a residência (RC-03). A segunda é a identidade com que o Bússola acessa os dados, a do usuário ou a própria, e como a permissão do usuário (RC-02) é checada quando o Bússola chama uma ferramenta. A terceira é o catálogo: que modelos, skills e servidores MCP a empresa aprova para o Bússola, e quem é o dono de cada um. Cada norma aplicável da seção 5 do caso (LGPD e Res. CMN 4.893) vira requisito arquitetural localizado no design. |
| Bom (14–17) | Tudo presente, com um ponto genérico (ameaça de manual, sem vetor do caso) ou norma sem requisito arquitetural. O control plane sem o catálogo também fica no Bom, com ou sem um desses pontos. |
| Parcial (8–13) | Lista de controles sem ligação com as ameaças, ou control plane sem a identidade ou sem a residência. |
| Insuficiente (0–7) | Sem modelo de ameaças ou sem control plane. |

**Regra de transição (turma de outubro de 2026).** Até 16/11/2026, a rubrica pedia "o limite de gasto" como
terceira decisão do control plane. O grupo desta turma que escreveu o limite de gasto no lugar do catálogo não perde
ponto por isso. O limite de gasto vale como a terceira decisão.

**O catálogo e o `make pacote-check`.** Um `[PREENCHER]` que sobrar na linha do catálogo faz o check dar FAIL. Esse
FAIL não limita o critério ao nível Parcial: a falta do catálogo cai no Bom, como diz a tabela.
