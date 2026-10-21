# Lab 1 com Codex

Para o grupo cujo operador usa o **Codex** (plano ChatGPT) em vez do Claude Code. O operador faz o
login antes da aula ([guia do Codex](../../docs/guia_codex.md), passo 5). O comando de abrir o Codex,
no passo 6 do mesmo guia, é usado na aula.

Sigam o [README do Lab 1](README.md) normalmente: o problema, os papéis, os arquivos e os passos
**1, 2, 4 e 5** são os mesmos. Só o **passo 3** muda, e está abaixo. O `make lab1-check` confere os
mesmos 7 itens.

## Passo 3 com Codex (20 min, operador)

O agente costuma levar poucos minutos; o resto é o grupo lendo o plano.

1. Abra o Codex com o comando do passo 6 do guia do Codex (sem ele, o agente não consegue rodar o
   check no Codespace):

   ```bash
   codex --sandbox danger-full-access --ask-for-approval on-request
   ```

2. Entre no modo de plano: digite `/plan` e tecle Enter (ou `Shift+Tab`). No modo de plano, o Codex
   investiga o código e propõe um plano antes de editar.
3. Colem o **mesmo prompt** do passo 3 do [README](README.md) (os autores podem melhorá-lo).
4. O Codex lê o código, mostra o plano e pergunta **Implement this plan?**. Leiam em grupo:
   - se o plano põe a regra em `mini-erp/app/services/pedidos.py` e deixa a rota só chamando essa
     função, escolham **Yes, implement this plan**;
   - se não, escolham **No, stay in Plan mode**, digitem o que corrigir (por exemplo: "a regra vai no
     service; a rota só chama") e leiam o novo plano antes de aprovar.
5. Quando ele terminar, o operador copia o resumo final do agente e cola **no topo** do
   `verificacao.md`, antes da primeira seção (lá ele não conta como resposta). Depois digita `/exit`.

## O que é diferente no Codex, e o que o verificador faz a mais

- **Nada impede o agente de ler o material do professor.** No Claude Code, as permissões negam a
  leitura de `labs/lab1/aceite/` (os testes de aceite), `labs/lab1/referencia/` (a solução) e
  `replay/` (as gravações, que trazem a solução completa). No Codex, só o `AGENTS.md` pede que ele
  não leia. O `make lab1-check` acusa se um sensor do professor for **alterado**, mas não percebe
  **leitura**. No passo 4, o verificador confere no que o Codex mostrou na tela se ele abriu algo
  nessas pastas. Se abriu, o relator registra no `verificacao.md`: é material do debrief.
- **O modo de plano é um pedido, não um bloqueio.** Sem o sandbox do Codex, nada impede o agente de
  editar antes de vocês aprovarem o plano. Se aparecer arquivo alterado no painel **Source Control**
  antes da aprovação, registrem também.
- **Sem desafio extra.** O `make lab1-extra` usa o Claude Code.
- **Se a cota acabar:** igual ao README. O segundo assinante pode usar Claude Code ou Codex: o
  trabalho está nos arquivos, não na conversa.
