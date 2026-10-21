# Guia do Codex: o caminho para quem tem plano ChatGPT

O caminho padrão do curso é o Claude Code ([guia do Codespace](guia_codespace.md)). Este guia é a
saída alternativa para o **operador** (ou o **segundo assinante**) que tem plano **ChatGPT Plus ou
superior** e vai usar o **Codex**, o agente de código da OpenAI. Ele já vem instalado no Codespace do
curso.

Só muda o que é do agente: o login, o comando que abre o agente e alguns detalhes dentro dos labs.
O Codespace, os `make` e os checks são os mesmos.

> Façam os passos 1 a 5 **antes da Aula 1**, como no guia do Codespace. O preparo termina no passo 5.3,
> quando o `make check` mostra PASS: 4 ok. Os passos 6 a 8 são para a aula e para consulta.

---

## 1 a 4. Conta no GitHub, repositório do grupo, Codespace e a tela

Iguais para todos: siga os passos **1 a 4** do [guia do Codespace](guia_codespace.md) (com telas no
[guia ilustrado](guia_ilustrado_codespace.md)) e volte aqui no passo 5. No fim do passo 3, o
`make check` mostra o mesmo aviso de quem usa Claude:

```text
[AVISO] Agente de código instalado, sem login
== PASS: 3 ok, 1 aviso(s), 0 falha(s) ==
```

## 5. Fazer login no Codex (operador e segundo assinante, uma vez)

Cada um entra com a **própria conta**. Os termos da OpenAI proíbem compartilhar login ou chave de
API, inclusive com colegas ou com o professor.

**5.1 Antes, no ChatGPT (navegador ou celular).** O Codespace não tem navegador próprio, então o
login usa um **código de dispositivo**, e ele vem desligado na conta:

1. Abra o ChatGPT com a conta do seu plano e vá em **Configurações → Segurança**.
2. Ligue a opção de autorização por código de dispositivo para o Codex (em inglês, algo como
   *Enable device code authorization for Codex*; o nome exato pode mudar).
3. Conta de trabalho ou de escola (ChatGPT Business, Enterprise ou Edu): a opção pode não aparecer,
   porque quem libera é o administrador do workspace. Nesse caso, peça a liberação antes da aula ou
   use uma conta pessoal com plano.

**5.2 No terminal do Codespace:**

1. Digite `codex login --device-auth` e tecle Enter. Aparece:

   ```text
   Follow these steps to sign in with ChatGPT using device code authorization:

   1. Open this link in your browser and sign in to your account
      https://auth.openai.com/codex/device

   2. Enter this one-time code (expires in 15 minutes)
      XXXX-XXXXX
   ```

2. Abra o link com `Ctrl`+clique (`Cmd`+clique no Mac); se o editor perguntar se pode abrir o site,
   clique em **Open**.
3. No navegador, entre na **sua** conta do ChatGPT e digite o código que apareceu no terminal. O
   código vale 15 minutos; se expirar, rode o comando de novo.
4. Volte ao terminal: ele mostra que o login deu certo. Para conferir a qualquer momento:
   `codex login status`.

O aviso cinza *"Continue only if you started this login in Codex"* é para você: nunca digite um
código que outra pessoa ou um site lhe passou.

**5.3 Conferir:** rode `make check`. O esperado agora é **PASS: 4 ok, 0 aviso(s), 0 falha(s)**,
com a linha **Acesso a modelo pelo Codex**.

O login fica guardado no Codespace, em `~/.codex/auth.json`. Esse arquivo vale como uma senha: não
copie nem mostre. Nas próximas vezes não precisa repetir o login, a menos que alguém faça "Rebuild
container".

> **Fim do preparo.** Se o `make check` mostrou **PASS: 4 ok, 0 aviso(s), 0 falha(s)**, o ambiente
> do grupo está pronto. Não rodem nada do Lab 1 agora: ele começa na aula. Pare o
> Codespace (passo 9 do [guia do Codespace](guia_codespace.md)) e volte a ele no dia da aula. Os
> passos 6 a 8 deste guia são para a aula e para consulta.

---

## 6. Abrir o Codex nos labs: sempre com este comando

```bash
codex --sandbox danger-full-access --ask-for-approval on-request
```

**Por que esse comando, e não só `codex`.** O Codex tenta isolar cada comando que roda num
*sandbox* próprio. Dentro de um contêiner, como o Codespace, esse sandbox pode não subir: no teste
de 13/10/2026, com a imagem do curso num contêiner local, todo comando falhou com
`bwrap: Can't mount devpts ... Permission denied`, e o agente não conseguiria rodar os testes nem o
`make labN-check`. Para esse caso, a própria OpenAI recomenda desligar o sandbox do Codex e deixar o
isolamento por conta do contêiner. É o que o comando faz:

- `--sandbox danger-full-access`: os comandos do agente rodam direto no Codespace, sem o sandbox
  do Codex;
- `--ask-for-approval on-request`: o agente roda os comandos sem perguntar, exceto os que o Codex
  considera perigosos; nesses, ele pede a sua aprovação.

**O que fica ao alcance do agente.** Nada do seu computador: o Codespace é uma máquina na nuvem.
Mas tudo o que está **dentro** do Codespace, sim: o repositório inteiro, a rede, o seu login do
Codex (`~/.codex/auth.json`) e o acesso do Codespace ao GitHub. A OpenAI avisa que, sem o sandbox,
um projeto malicioso pode extrair tudo o que está no contêiner, inclusive a credencial do Codex. Por
isso: só abra o Codex no repositório do curso, com dados sintéticos, e não guarde outras senhas ou
chaves no Codespace.

Para o lab, a consequência é esta. Na Aula 1, "o guia pede, a permissão garante". No Codex deste
curso, só existe a primeira metade: o `AGENTS.md` pede que o agente não leia os testes e as
soluções do professor, mas nada o impede. Quem garante é o verificador do grupo, conferindo o que o
agente leu e mudou.

**Na primeira abertura**, o Codex pergunta se você confia na pasta: escolha **Trust and continue**
(o repositório é do seu grupo). Para sair do Codex: `/exit`.

## 7. O que muda nos labs

Cada lab é escrito para o Claude Code e indica onde o Codex é diferente. No **Lab 1**, os passos
1, 2, 4 e 5 do README são iguais; o passo 3 (o agente) tem a versão Codex em
[labs/lab1/codex.md](../labs/lab1/codex.md).

| No Claude Code | No Codex |
|---|---|
| login: `claude` | login: `codex login --device-auth` (passo 5) |
| abrir: `claude --permission-mode plan` | abrir: o comando do passo 6, depois `/plan` |
| aprovar o plano: **Yes, and use auto mode** | aprovar o plano: **Yes, implement this plan** |
| `CLAUDE.md`, que importa o `AGENTS.md` | lê o `AGENTS.md` direto |
| skills em `.claude/skills/` | skills em `.agents/skills/` (a mesma skill) |
| leitura dos testes, soluções e gravações do professor negada nas permissões | sem bloqueio: vale só o pedido do `AGENTS.md` |
| desafio extra do Lab 1 (`make lab1-extra`, usa `claude -p`) | não se aplica |

O `make labN`, a fitness function e o `make labN-check` são os mesmos: não dependem do agente.

**O resto é igual para todos:** salvar o trabalho com `git push`, parar o Codespace, a cota e o
segundo assinante estão nos passos 8 a 11 do [guia do Codespace](guia_codespace.md).

## 8. Deu errado?

| Sintoma | O que fazer |
|---|---|
| `codex: command not found` | A instalação do Codespace falhou. Rode `npm install -g @openai/codex` e depois `codex --version` |
| O `codex login --device-auth` recusa o login ou diz que o código de dispositivo não está habilitado | Falta o passo 5.1: ligue a opção no ChatGPT e rode o comando de novo |
| Conta do trabalho ou da escola sem a opção de código de dispositivo | Quem libera é o administrador do workspace. Peça a liberação ou use uma conta pessoal com plano |
| O código expirou | Rode `codex login --device-auth` de novo: cada código vale 15 minutos |
| `make check` com FAIL em "Acesso a modelo (Codex)" | Rode `codex login status`. Se não estiver logado, refaça o passo 5. Se estiver, leia a mensagem: pode ser o limite do plano |
| Os comandos do agente falham com uma mensagem que começa com `bwrap:` (por exemplo *Permission denied* ou *No permissions to create new namespace*) | O Codex foi aberto sem o comando do passo 6. Saia (`/exit`) e abra com ele |
| Perdi o login | Alguém fez "Rebuild container". Repita o passo 5.2 |
| O limite do plano acabou na aula | O segundo assinante continua (guia do Codespace, passo 10), ou use o replay do lab em `replay/` |

O curso usa o login com o plano ChatGPT. Chave de API da OpenAI não é um caminho do curso.

Mais casos: [faq.md](faq.md). Algo neste guia não bateu com a tela? Avise o professor: o caminho do
Codex ainda não passou por um piloto completo com turma.

*Conferido em 13/10/2026 com o Codex CLI 0.162.1: o texto do login por código de dispositivo e a
falha do sandbox, na imagem do curso num contêiner local (não num Codespace); os rótulos das telas,
no próprio programa. Fontes: login (learn.chatgpt.com/docs/auth); sandbox no Linux, contêineres e o
aviso de extração de credenciais (learn.chatgpt.com/docs/agent-approvals-security); planos que
incluem o Codex (learn.chatgpt.com/docs/pricing); modo de plano (learn.chatgpt.com/guides/best-practices).
Telas e opções do Codex mudam entre versões.*
