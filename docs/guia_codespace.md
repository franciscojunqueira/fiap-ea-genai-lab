# Guia do Codespace: do zero ao primeiro exercício

Todos os labs do curso rodam num **Codespace**: um computador na nuvem do GitHub, aberto no seu
navegador, com tudo instalado. Você não instala nada na sua máquina. Siga os passos na ordem.
Prefere ver as telas? O [guia ilustrado](guia_ilustrado_codespace.md) mostra os passos 2 a 6 e 9 com
imagens, marcando onde clicar.

**Quem faz o quê.** Só o **operador** (quem tem plano Claude Pro/Max ou ChatGPT Plus) e o **segundo
assinante** do grupo abrem Codespace. Os demais integrantes fazem só o passo 1 e acompanham pela tela
compartilhada do operador.

> Façam os passos 1 a 5 **antes da Aula 1**. O primeiro Codespace leva alguns minutos para ficar
> pronto, e em aula não há tempo nem suporte para isso.

---

## 1. Conta no GitHub (todos do grupo)

1. Crie uma conta gratuita em **https://github.com/signup**, se ainda não tiver.
2. Mande o seu **nome de usuário** do GitHub para o operador do grupo (a lista de grupos é a planilha
   de autoformação divulgada no Portal do Aluno). Ele vai adicionar você ao repositório do grupo.
3. **Aceite o convite** que chega por e-mail, ou em https://github.com/notifications, em até 7 dias:
   depois disso ele expira e o operador precisa convidar de novo.

## 2. Criar o repositório do grupo (operador, uma vez)

1. Entre em **https://github.com/franciscojunqueira/fiap-ea-genai-lab**.
2. Clique no botão verde **Use this template** e escolha **Create a new repository**. Não use
   *Open in a codespace*: ele abre o Codespace no repositório do professor, não no do grupo.
3. Preencha:
   - **Owner:** a sua conta;
   - **Repository name:** `ea-genai-grupo-N` (N = número do seu grupo na planilha);
   - **Choose visibility:** vem marcado **Public**; clique e troque para **Private** (a entrega exige);
   - deixe **Include all branches** desligado, como já vem.
4. Clique em **Create repository**. Você está agora no repositório do grupo: é nele que o grupo
   trabalha o curso inteiro.
5. Adicione os colegas e o professor: na barra de cima do repositório, **Settings**; no menu da
   esquerda, em *Access*, **Collaborators**; depois **Add people** (o GitHub pode pedir sua senha ou o
   código de verificação de novo). Digite o usuário de cada colega e `franciscojunqueira`.

## 3. Criar o Codespace (operador e segundo assinante, uma vez)

1. No repositório do grupo (não no do professor), clique no botão verde **Code**.
2. Abra a aba **Codespaces** e clique em **Create codespace on main**.
3. Abre uma nova aba do navegador com um editor parecido com o VS Code e o aviso *Building
   codespace...* no canto de baixo. Espere: na primeira vez leva alguns minutos (cerca de 4 no teste
   de 13/10/2026). Não feche a aba.
4. Quando o ambiente fica pronto, aparece a pergunta **"Do you trust the authors of the files in this
   folder?"**. O repositório é do seu grupo: clique em **Trust Folder & Continue**. Sem isso o editor
   fica em *Restricted Mode* e o terminal não abre.
5. O terminal aparece embaixo, com uma mensagem de boas-vindas. Clique nele, digite `make check` e
   tecle Enter (a verificação automática do primeiro build não aparece nesse terminal). Nessa
   primeira vez o esperado é:

   ```text
   [AVISO] Agente de código instalado, sem login
   == PASS: 3 ok, 1 aviso(s), 0 falha(s) ==
   ```

   O aviso some no passo 5.

## 4. Conhecer a tela

| Área | Onde fica | Para quê |
|---|---|---|
| Explorador de arquivos | à esquerda | abrir os arquivos do repositório (ex.: `labs/lab1/README.md`) |
| Editor | no centro | ler e editar arquivos. Um clique num `.md` costuma abri-lo já formatado; se abrir como texto, botão direito no arquivo → **Open Preview** |
| Terminal | embaixo | digitar os comandos (`make ...`, `claude`) |
| Novo terminal | botão **+** no canto do terminal | abrir um segundo terminal, por exemplo para deixar o Mini-ERP rodando |
| Aba **PORTS** | ao lado da aba do terminal (se a janela estiver estreita, no menu **⋯** dessa barra) | abrir no navegador o que roda no Codespace (passo 7) |

O painel **Chat** que abre à direita é o assistente do próprio GitHub (Copilot), não o Claude Code, e
não é usado no curso. Pode fechá-lo no **X**: sobra espaço para o terminal.

Se o terminal sumir: menu **☰ → Terminal → New Terminal** (atalho ``Ctrl+` `` com a tecla de crase, ou `Ctrl+J`
para mostrar e esconder o painel; no Mac, `Cmd+J`).

## 5. Fazer login no agente (operador e segundo assinante, uma vez)

Cada um entra com a **própria conta**. Os termos da Anthropic e da OpenAI proíbem compartilhar
login ou chave de API, inclusive com colegas ou com o professor; quem não tem plano acompanha pela
tela do operador.

**Claude Code (caminho padrão):**

1. No terminal, digite `claude` e tecle Enter.
2. Na primeira execução ele pergunta o tema (Enter aceita o padrão) e o tipo de login (a opção
   **Claude account with subscription**, Pro/Max, já vem marcada: Enter). O texto exato das telas
   muda entre versões.
3. O editor mostra sozinho **"Do you want Code to open the external website?"**. Neste primeiro aviso,
   clique em **Cancel**: o *Open* daqui tenta voltar para `localhost`, que só existe dentro do
   Codespace, e o navegador mostra *"localhost refused to connect"* (se acontecer, feche essa aba e
   siga).
4. No terminal aparece um link longo e, embaixo, *Paste code here if prompted*. Abra o link com
   `Ctrl`+clique (`Cmd`+clique no Mac); quando o editor perguntar de novo se pode abrir o site, agora
   clique em **Open**.
5. No navegador, **confira o e-mail em "Logged in as"**, no rodapé: tem de ser a sua conta com plano
   (se não for, *Switch account*). Clique em **Authorize**, depois em **Copy code**, volte ao terminal,
   cole o código e tecle Enter (se o navegador perguntar, permita colar).
6. Aparece *Login successful*: Enter. Nas telas seguintes (*Security notes* e configuração do
   terminal), Enter. **Atenção na última**, *Accessing workspace*: a opção marcada é **"No, exit"**, e
   Enter direto fecha o Claude Code. Desça com a seta até **Yes, I trust this folder** e só então
   tecle Enter.
7. Quando o Claude Code abrir, digite `/exit` para sair.
8. Rode `make check`. O esperado agora é **PASS: 4 ok, 0 aviso(s), 0 falha(s)**.

As telas de cada passo estão no [guia ilustrado](guia_ilustrado_codespace.md).

**Codex (alternativa, plano ChatGPT):** no ChatGPT, em configurações de segurança, ative o login por
código de dispositivo (*device code login*); depois rode `codex login --device-auth` no terminal e
siga o que ele mostrar. A [FAQ](faq.md) tem os detalhes.

O login fica guardado no Codespace: nas próximas vezes não precisa repetir, a menos que alguém faça
"Rebuild container".

## 6. Rodar o primeiro exercício (Lab 1, na aula)

1. No explorador, abra `labs/lab1/README.md` com **Open Preview**: é o roteiro do lab.
2. No terminal:
   ```bash
   make lab1         # prepara o lab
   make lab1-check   # FAIL é o esperado agora: as mensagens dizem o que falta
   ```
   O esperado: `[OK] 1. Lab preparado`, os outros itens com `[FALHA]` e a explicação de cada um, e no
   fim `lab1-check: FAIL (1/7 itens)`. É o ponto de partida do lab. A última linha,
   `make: *** [...] Error 1`, também é normal: é como o `make` avisa que o check deu FAIL.
3. Siga o README a partir do passo 2. Cada lab tem o seu `labs/labN/README.md` e confere com
   `make labN-check`.

Para testar antes da aula sem gastar cota: `make lab1` e `make lab1-check` não usam o agente.

## 7. Ver o Mini-ERP no navegador (quando o lab pedir)

1. Abra um segundo terminal (botão **+**) e rode `make erp`. Deixe esse terminal aberto.
2. Clique na aba **PORTS**, ache a porta **8000 (Mini-ERP)** e clique no ícone de **globo** ("Open in
   Browser"). Abre a tela do Mini-ERP; acrescente `/docs` no fim do endereço para ver a API.
3. Para parar o Mini-ERP: volte ao terminal dele e tecle `Ctrl+C`.

A porta é **privada**: só você, logado no GitHub, consegue abrir. Para mostrar ao grupo, compartilhe
a tela.

## 8. Salvar o trabalho no repositório (sempre)

O que fica só no Codespace pode se perder. Ao fim de cada lab e de cada aula, no terminal:

```bash
git add -A
git commit -m "Lab 1 do grupo N"
git push
```

Para a entrega das atividades, o SHA do commit sai com `git rev-parse HEAD`.

## 9. Parar e voltar

- **Parar ao terminar:** em **https://github.com/codespaces**, clique em **⋯** ao lado do Codespace
  → **Stop codespace**. Ou, dentro do editor, `Ctrl+Shift+P` (`Cmd+Shift+P` no Mac) →
  **Codespaces: Stop Current Codespace**.
- **Fechar a aba do navegador não para o Codespace:** ele continua rodando e gastando a cota até
  ficar 30 min sem uso, quando para sozinho. Parado, só ocupa armazenamento.
- **Voltar (no dia da aula):** no repositório do grupo, **Code → Codespaces** e clique no Codespace
  que **já existe**. Não clique em "Create codespace" de novo: isso cria outro do zero, com novo
  build e novo login. Também dá para abrir pela lista em https://github.com/codespaces.
- **Atenção:** um Codespace parado e sem uso por **30 dias é apagado automaticamente**, mesmo que
  tenha trabalho não enviado. Por isso o passo 8.

## 10. Segundo assinante (plano B do grupo)

O segundo assinante faz os passos 3 e 5 no **mesmo repositório do grupo** (ele é colaborador). Se a
cota do operador acabar durante um lab: o operador faz o passo 8 (commit e push), e o segundo
assinante, no Codespace dele, roda `git pull` e continua do mesmo ponto.

## 11. Cota gratuita do Codespaces

Cada conta GitHub Free tem por mês **120 horas-núcleo** e **15 GB** de armazenamento. A máquina do
curso tem 2 núcleos: 1 hora de uso consome 2 horas-núcleo, ou cerca de **60 horas de uso por mês**,
o que basta para o curso. Quem cria o Codespace usa a própria cota. Parar o Codespace (passo 9)
preserva a cota.

## 12. Deu errado?

| Sintoma | O que fazer |
|---|---|
| O Codespace está demorando no primeiro build | Normal na primeira vez. Espere; não feche a aba |
| Editor em *Restricted Mode*, sem terminal | Clique em **Trust Folder & Continue** (passo 3.4) |
| *localhost refused to connect* no navegador | Feche a aba e use o link do terminal com Ctrl/Cmd+clique (passo 5.4) |
| O Claude Code fechou logo depois do login | Foi o Enter em *No, exit*. Rode `claude` de novo e escolha **Yes, I trust this folder** |
| Não vejo o botão **Code → Codespaces** | Você está no repositório do professor ou não aceitou o convite de colaborador. Abra o repositório do grupo |
| `make check` com FAIL | Leia a mensagem: ela diz o que fazer. Cole a saída no agente e peça ajuda. Depois, a [FAQ](faq.md) |
| O terminal sumiu | Menu **☰ → Terminal → New Terminal** |
| A porta 8000 abre uma página de erro | O Mini-ERP não está rodando: rode `make erp` no segundo terminal |
| Perdi o login do Claude Code | Alguém fez "Rebuild container". Repita o passo 5 |
| A cota do plano acabou na aula | Passo 10, ou o replay do lab em `replay/` |

Mais casos: [faq.md](faq.md). Resumo de uma página para o operador:
[checklist_operador.md](checklist_operador.md).

*Limites do GitHub conferidos em 13/10/2026 (podem mudar): parada após 30 min sem uso
(docs.github.com/en/codespaces/setting-your-user-preferences/setting-your-timeout-period-for-github-codespaces),
exclusão após 30 dias parado
(docs.github.com/en/codespaces/setting-your-user-preferences/configuring-automatic-deletion-of-your-codespaces),
cota (docs.github.com/en/billing/concepts/product-billing/github-codespaces), criar a partir de
template (docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template),
portas (docs.github.com/en/codespaces/developing-in-a-codespace/forwarding-ports-in-your-codespace).*
