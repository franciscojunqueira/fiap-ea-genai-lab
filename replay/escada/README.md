# Escada do harness (replay da demo da Aula 1)

A mesma tarefa em 4 degraus: *"Crie um ADR para migrar o banco do Mini-ERP de SQLite para
PostgreSQL."* O pedido não informa decisores, motivo nem requisitos. Um bom harness registra a
lacuna; um fraco inventa.

| Degrau | O que entra | Guia ou sensor |
|---|---|---|
| 1. Só prompt | pasta vazia | — |
| 2. + contexto | o repositório, com `AGENTS.md` e o código (sem a skill) | guia |
| 3. + loop com testes | o validador do ADR, com a ordem "rode até PASS" | sensor determinístico |
| 4. + harness completo | skill `escrevendo-adrs`; hook que valida a cada escrita; hook que não deixa encerrar sem o subagente `revisor-adr`; escrita só em `docs/adr/` (`harness/`) | guias + sensores |

**Gravar de novo** (gasta cota de quem roda): `python3 replay/escada/gravar.py haiku 1 2 3 4` e
`python3 replay/escada/gravar.py sonnet 1 4`. Cada degrau fica em `gravacao/<modelo>-d<N>/`.

## Gravação de 12/10/2026

Claude Code 2.1.284, conta pessoal no plano Max (o operador típico tem Pro: os modelos são os
mesmos, a cota não). Uma execução por degrau: é registro para a aula, não medida estatística.
Validador = `validar_adr.py` original, rodado depois, fora da pasta do agente.

| Modelo | Degrau | Validador | Turnos | Tokens de entrada | Duração |
|---|---|---|---|---|---|
| Haiku 4.5 | 1 | FAIL (14 erros) | 9 | 235 mil | 52 s |
| Haiku 4.5 | 2 | FAIL (19 erros) | 8 | 208 mil | 38 s |
| Haiku 4.5 | 3 | **PASS** | 9 | 262 mil | 54 s |
| Haiku 4.5 | 4 | **PASS** | 37 | 1.045 mil | 403 s |
| Sonnet 5.5 | 1 | FAIL (13 erros) | 3 | 67 mil | 35 s |
| Sonnet 5.5 | 4 | **PASS** | 13 | 191 mil | 100 s |

## Registro do verificador

Cada ADR foi lido contra o repositório e o pedido. O verificador é uma pessoa, não o agente.

| Degrau | O que o agente inventou ou errou | Quem pegou |
|---|---|---|
| Haiku 1 | Contexto inteiro: "a equipe tem experiência com PostgreSQL", nuvem "AWS/Azure/GCP", "100+ usuários", RTO < 1 h, RPO < 5 min, "abstrações de acesso a dados" numa pasta vazia; criou um `README.md` que ninguém pediu | só o verificador (o validador acusa só o formato) |
| Haiku 2 | Decisores "Enterprise Architecture Team"; motivo "estudantes enfrentam travamentos nos labs"; metade do ADR em inglês | só o verificador |
| Haiku 3 | **PASS no validador** com decisores "Arquitetura FIAP, Time de Backend" e **5 requisitos RQ-01 a RQ-05 que o usuário não deu**; "histórico de bugs em replicação" do MySQL, sem fonte | só o verificador: **o sensor de forma passou, a verdade não** |
| Haiku 4 | Decisores viraram "a confirmar" e o motivo foi para Pendências. Mas o RQ-01 cita o ADR-003 como origem, e o ADR-003 é o **exemplo da skill**, não uma decisão deste repositório. O revisor (também Haiku) pegou "ADR-003 rejeitada" (contradiz) e o "laboratório de escalabilidade" inventado, mas depois **aprovou** o RQ-01 apoiado no exemplo | revisor pegou 2; o verificador pegou o que o revisor aprovou |
| Sonnet 1 | Mesmo sem contexto, escreveu "Decisores: a definir" e uma seção de questões em aberto; inventou módulos ("financeiro") e "pouco conhecido pela equipe" | só o verificador |
| Sonnet 4 | O revisor pegou dois erros reais: "o repositório não tem Docker" (tem um Dockerfile de devcontainer) e `Numeric` (os modelos usam `Float`). O Sonnet corrigiu o Contexto, mas a seção Pendências **ainda diz** "o repositório não tem Docker" | revisor pegou 2; o verificador pegou o que sobrou |

**Leitura para a aula.**
- **Guia muda o comportamento; sensor muda a confiança.** O contexto (degrau 2) não impediu a
  invenção. O validador (degrau 3) consertou o formato e deixou a invenção passar com PASS.
- **Revisor por julgamento ajuda e erra.** Pegou erros reais nos dois modelos, mas aprovou uma
  fonte errada (Haiku) e não reviu a correção (Sonnet). O verificador humano continua no circuito.
- **O harness completo custa.** No Haiku, de 262 mil para 1 milhão de tokens e de 54 s para 6,7 min.
  No Sonnet, 13 turnos e 100 s. Harness é decisão de custo, não só de qualidade.
- **Modelo maior precisa de menos guia, mas não dispensa o sensor:** o Sonnet errou menos e ainda
  deixou uma contradição.

## O que deu errado na gravação (material para o bloco de harness corporativo)

- **Permissão estreita demais** (`gravacao/*-d4-permissao-estreita/`): a regra liberava só
  `python3 .claude/skills/.../validar_adr.py *`. Os agentes chamaram o validador com caminho
  absoluto ou encadeado com `mkdir`, a regra não casou e o modo `dontAsk` negou. Os dois pararam e
  pediram autorização; o Sonnet recusou-se a chutar o número do ADR. Permissão mal calibrada trava
  o trabalho, e o bom agente para em vez de contornar.
- **Repositório não se autoconcede permissões** (`gravacao/*-d4-sem-confianca/`): num workspace que
  ninguém marcou como confiável, o Claude Code ignora o `permissions.allow` do
  `.claude/settings.json` do projeto (aviso: "this workspace has not been trusted"). É uma defesa
  contra repositório malicioso. Por isso o `gravar.py` passa as regras por `--allowedTools`.
  Os hooks do mesmo arquivo rodaram nas duas gravações.
