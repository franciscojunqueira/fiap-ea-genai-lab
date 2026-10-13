# Checklist do operador (antes da Aula 1)

O operador é quem tem plano **Claude Pro/Max** (ou **ChatGPT Plus**, como alternativa) e conduz o
agente com a tela compartilhada. Faça isto antes da aula, não durante: o primeiro build do Codespace
leva alguns minutos.

## 1. Criar o repositório do grupo

1. Entre no GitHub com a sua conta pessoal.
2. No repositório-template, clique em **Use this template → Create a new repository**.
3. Dono: você. Nome: `ea-genai-grupo-N`. Visibilidade: a que o grupo preferir.
4. (Opcional) Settings → Collaborators: adicione os colegas do grupo.

## 2. Abrir o Codespace

1. No repositório do grupo: **Code → Codespaces → Create codespace on main**.
2. Espere o build terminar. No final, o terminal mostra o resultado do `make check`.
3. Nessa primeira vez, o resultado esperado é **PASS com 1 aviso** ("Claude Code instalado, sem login").

## 3. Fazer login no agente

**Claude Code (caminho padrão):**
1. No terminal: `claude`.
2. Escolha o login com a conta Claude (plano Pro/Max).
3. Abra o link no navegador e autorize. Se o terminal pedir um código, copie o que o navegador mostrar e cole no terminal.
4. Saia com `/exit`.

**Codex (alternativa):** ative antes o *device code login* nas configurações de segurança do
ChatGPT e rode `codex login --device-auth`.

## 4. Conferir

```bash
make check
```

Esperado: `PASS: 4 ok, 0 aviso(s), 0 falha(s)`. O último item faz uma chamada mínima ao modelo
mais barato do seu plano.

## 5. Ao terminar

- **Pare o Codespace** (Code → Codespaces → ⋯ → Stop codespace). A cota gratuita é contada em
  core-horas: 120 por mês numa conta Free, o que dá cerca de 60 h numa máquina de 2 cores.
- Conta corporativa: confira antes a política do seu empregador. Conta pessoal não se compartilha.

Algo deu errado? [faq.md](faq.md).
