---
name: revisando-adr-bussola
description: Revisa um ADR do assistente Bússola contra os requisitos RC-01 a RC-12 de integrador/caso.md e aponta o problema mais grave. Use sempre que alguém pedir para revisar, criticar, conferir, validar ou dar parecer sobre um ADR do Bússola (arquivos em adrs/), mesmo que não mencione "RC" ou "requisitos".
---

# Revisando ADR do Bússola

Um ADR fraco passa na defesa só se o revisor achar o defeito que importa. Por isso a saída é curta: o problema mais grave primeiro, sem lista de nitpicks.

## Passos

1. Leia o ADR e `integrador/caso.md` (seções 3 a 6; a tabela da seção 4 é a fonte única dos requisitos).
2. Faça as três checagens abaixo, além de comparar a decisão com RC-01..RC-12.
3. Ordene os achados por gravidade e escreva a saída.

## Checagens obrigatórias

- **Alternativa de palha:** alguma alternativa existe só para ser descartada (inviável, fora do escopo da seção 6 do caso, ou absurda para o prazo/equipe, RC-10/RC-11)? Alternativas reais devem ser defensáveis.
- **Requisito inexistente:** todo ID citado (RC-NN) existe na tabela da seção 4 e diz o que o ADR afirma? O caso só vai até RC-12; um ID fora disso, ou com conteúdo inventado, invalida a justificativa.
- **Reversão sem custo:** "sem custo" quase nunca é verdade. Aponte se o custo real (retrabalho, migração, dados/logs já gravados, reaprovação) foi omitido, ou se o gatilho já está disparado pelos próprios números do ADR.

Verifique também se o ADR omite requisito que a decisão afeta (ex.: RC-03, RC-05, RC-12).

## Saída

No máximo 5 linhas, em português:

- Linha 1: o problema mais grave, citando o requisito (RC-NN) ou o ponto do caso.md.
- Linhas 2-5: demais problemas, em ordem de gravidade, uma linha cada.
- Se a revisão estiver limpa, diga isso em uma linha. Não invente problema.

Dê a correção em poucas palavras na própria linha. Não repita o ADR nem faça preâmbulo.
