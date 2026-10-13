# Checklist do operador (antes da Aula 1)

O operador é quem tem plano **Claude Pro/Max** (ou **ChatGPT Plus**, como alternativa) e conduz o
agente com a tela compartilhada. Este é o resumo; o passo a passo com telas, portas, como salvar e
como voltar ao Codespace está em [guia_codespace.md](guia_codespace.md). Faça isto antes da aula, não durante: o primeiro build do Codespace
leva alguns minutos.

## 1. Criar o repositório do grupo

1. Entre no GitHub com a sua conta pessoal.
2. No repositório-template, clique em **Use this template → Create a new repository**.
3. Dono: você. Nome: `ea-genai-grupo-N`. Visibilidade: **privado** (a entrega exige).
4. Settings → Collaborators: adicione os colegas do grupo e o professor (`franciscojunqueira`).
5. **Segundo assinante do grupo:** faça também os passos 2 a 4 abaixo, no mesmo repositório. É ele
   quem continua o lab se a sua cota acabar.

## 2. Abrir o Codespace

1. No repositório do grupo: **Code → Codespaces → Create codespace on main**.
2. Espere o build terminar e clique em **Trust Folder & Continue** quando o editor perguntar se você
   confia na pasta.
3. Clique no terminal e rode `make check`. Nessa primeira vez, o resultado esperado é **PASS com 1
   aviso** ("Agente de código instalado, sem login").

## 3. Fazer login no agente

**Claude Code (caminho padrão):**
1. No terminal: `claude`.
2. Escolha o login com a conta Claude (plano Pro/Max).
3. No primeiro "open the external website?", clique em **Cancel**. Abra o link do terminal com
   Ctrl/Cmd+clique, clique em **Open**, confira o seu e-mail em "Logged in as", **Authorize**,
   **Copy code** e cole o código no terminal.
4. Na pergunta *Accessing workspace*, desça até **Yes, I trust this folder** (o marcado é "No, exit").
5. Saia com `/exit`. Telas de cada passo: [guia ilustrado](guia_ilustrado_codespace.md).

**Codex (alternativa, plano ChatGPT):** siga o [guia do Codex](guia_codex.md), passos 5 e 6. Em
resumo: ligue antes, no ChatGPT, a opção de login por código de dispositivo (Configurações →
Segurança), rode `codex login --device-auth` e, nos labs, abra sempre com
`codex --sandbox danger-full-access --ask-for-approval on-request`.

## 4. Conferir

```bash
make check
```

Esperado: `PASS: 4 ok, 0 aviso(s), 0 falha(s)`. O último item faz uma chamada mínima ao modelo
(no Claude Code, o mais barato do plano; no Codex, o modelo padrão).

## 5. Ao terminar

- **Pare o Codespace** (Code → Codespaces → ⋯ → Stop codespace). A cota gratuita é contada em
  core-horas: 120 por mês numa conta Free, o que dá cerca de 60 h numa máquina de 2 cores.
- Conta corporativa: confira antes a política do seu empregador. Conta pessoal não se compartilha.

Algo deu errado? [faq.md](faq.md).
