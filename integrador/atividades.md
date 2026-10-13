# Atividades entre as aulas

Três atividades em grupo. As Atividades 1 e 2 levam cerca de 1 hora; a 3 junta o que os labs
produziram e leva mais. Cada uma alimenta a seguinte e o pacote final.

**Entrega:** commit na `main` do repositório do grupo e, na atividade correspondente do **Portal
do Aluno da FIAP**, o link do repositório e o **SHA do commit** (`git rev-parse HEAD`). O professor
corrige esse commit. Deixem o repositório **privado**, com o professor
(`franciscojunqueira`) como colaborador.

**Versão que vale:** o caso, a rubrica e os checks do repositório-template. Se o professor avisar
uma correção, tragam-na com:
`git remote add template https://github.com/franciscojunqueira/fiap-ea-genai-lab.git` (uma vez),
`git fetch template` e `git checkout template/main -- integrador/caso.md integrador/rubrica.md integrador/scripts`.

| # | Quando | Atividade | Conferência | Usada em |
|---|---|---|---|---|
| 1 | Aula 1 → Aula 2 | Engenharia reversa do SGC | `make er-check` | aquecimento da Aula 2 e ADRs |
| 2 | Aula 2 → Aula 3 | Checkpoint: 1º ADR, decisão de conhecimento e contrato MCP | `make checkpoint-check` | devolutiva coletiva na Aula 3 |
| 3 | Aula 3 → Aula 4 | Pacote final e pitch gravado, **48h antes da Aula 4** | `make pacote-check` | arguição na Aula 4 |

---

## Atividade 1: engenharia reversa do SGC

**Objetivo.** Saber o que o SGC faz de fato antes de decidir como o Bússola vai acessá-lo. A
documentação do SGC é de 2019 e está incompleta. Parte do que ela diz não é verdade.

**Papéis.** Operador (conduz o agente), autores do harness (prompt e instruções), verificador
(confere as afirmações do agente) e relator (escreve os arquivos de entrega).

**Passos.**

1. **Rodar o legado (5 min).** `make legado`. Leiam a saída: ela já mostra comportamentos que a
   documentação não explica.
2. **Montar o harness (10 min).** Os autores reaproveitam o que funcionou no Lab 1. No mínimo:
   - o agente cita `arquivo:linha` para cada afirmação, relativo a `integrador/legado/`;
   - separa o que leu no código do que está inferindo;
   - quando a documentação citar algo que não existe no repositório, escreve "não encontrado" em
     vez de descrever;
   - não altera o código do SGC.
3. **Rodar o agente (20 min).** Abram o Claude Code na raiz do repositório (Codex: `codex` no
   mesmo lugar, com o mesmo prompt). Um ponto de partida, que os autores devem melhorar:

   > Faça a engenharia reversa do sistema em `integrador/legado/` (o SGC). Leia todo o código,
   > os scripts em `ops/`, o layout em `layouts/` e os dados de exemplo. Preencha `c4.md`,
   > `dependencias.md` e `regras.md` em `integrador/pacote/engenharia-reversa/`, seguindo os
   > comentários de cada um. Para cada afirmação, cite arquivo:linha. Separe fato de inferência.
   > Não altere o SGC. Não preencha `invencoes.md`.

   **O `invencoes.md` é do verificador, não do agente.** Num teste com o prompt acima sem a última
   frase, o agente preencheu o próprio registro e deu "correto" para as 10 afirmações. Duas delas
   estavam erradas, e uma era a mais perigosa para o Bússola.

4. **Verificar (15 min).** O verificador escolhe pelo menos 5 afirmações do agente, incluindo as
   mais surpreendentes, e confere no código ou rodando o legado. Registra em `invencoes.md`, com
   o veredito.
5. **Conferir e entregar (10 min).** `make er-check` até dar PASS, commit e push. O PASS confere a
   forma (arquivos, tabelas, citações que existem). Uma citação que existe pode sustentar uma
   afirmação falsa: isso só o verificador pega.

**Entregáveis** em `integrador/pacote/engenharia-reversa/`: `c4.md` (contexto e containers),
`dependencias.md`, `regras.md` (mínimo 8 regras e as implicações para o Bússola) e `invencoes.md`
(mínimo 5 afirmações conferidas).

**Cota.** Num teste de 12/10/2026, o agente levou de 3 a 5 minutos para preencher os arquivos; o
consumo num plano Pro ainda vai ser medido no piloto. Se a cota acabar, o segundo assinante do
grupo continua do ponto em que parou: o trabalho está nos arquivos, não na conversa. Para executar
o SGC, usem só o `make legado`, que roda numa pasta isolada.

**Na Aula 2.** Dois grupos mostram o C4 (5 min cada) e a turma compara o que cada agente inventou.

---

## Atividade 2: checkpoint

**Objetivo.** Registrar as primeiras decisões enquanto os Labs 2 e 3 estão frescos.

**Passos.**

1. **1º ADR**, com a skill `escrevendo-adrs` (peça ao agente: "registre um ADR sobre ..."). Tema
   sugerido: como o Bússola acessa o SGC, com os fatos da Atividade 1. Citem os requisitos do
   caso (RC-NN) na tabela de requisitos.
2. **`pacote/01-design.md`, seção "Decisão de conhecimento"**: o que o Bússola usa para cada tipo de
   pergunta, com os dados do Lab 2.
3. **`pacote/01-design.md`, seção "Contrato MCP"**: as ferramentas do Lab 3 mais as de acesso ao SGC.
4. `make checkpoint-check` até dar PASS, commit e push.

**Na Aula 3.** Devolutiva coletiva: o professor comenta os padrões que viu nos checkpoints da
turma, sem nota.

---

## Atividade 3: pacote final e pitch

**Prazo:** 48 horas antes do início da Aula 4. Exceção: a seção "Mitigação testada" de
`04-seguranca.md` vai até 24h depois da Aula 4, porque o Lab 6 acontece na própria aula (novo SHA
no Portal do Aluno).

**Passos.**

1. Completem o pacote (`integrador/pacote/README.md` lista os arquivos) e cheguem a 2 ou 3 ADRs.
2. Preencham `contribuicao.md` e `uso-de-ia.md`. Todos os integrantes revisam.
3. Gravem o pitch de 5 minutos (instruções em `pacote/pitch.md`) e coloquem o link.
4. `make pacote-check` até dar PASS, commit e push.

**Na Aula 4.** Arguição de 9 minutos por grupo, com carta de mudança de requisito e pergunta a um
integrante sorteado. Preparem-se para defender qualquer decisão do pacote: quem responde é
sorteado na hora. Critérios em [rubrica.md](rubrica.md).
