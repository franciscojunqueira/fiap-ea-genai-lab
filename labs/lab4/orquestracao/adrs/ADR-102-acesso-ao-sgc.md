# ADR-102: Como o Bússola acessa o SGC

**Status:** proposto · **Data:** 2026-11-10 · **Decisores:** Arquitetura de Soluções

## Contexto
O SGC não tem API. Ele grava o relatório de inadimplência em arquivo, e o lote noturno roda das 21:30
às 23:00 (RC-09). A RC-13 exige que o Bússola consulte o saldo do SGC em tempo real, a cada pergunta.

## Alternativas
1. **Ler o arquivo do relatório depois do lote noturno.** Dado com até um dia de atraso.
2. **Criar um adapter MCP que consulta o banco do SGC a cada pergunta.** Atende a RC-13.
3. **Pedir ao time do SGC uma API nova.** Prazo de 6 meses, fora do piloto (RC-11).

## Decisão
Criar o adapter MCP que consulta o banco do SGC a cada pergunta, só leitura.

## Consequências
- Atende a RC-13.
- Carga no banco do SGC durante o dia; o adapter não roda na janela do lote (RC-09).

## Reversão
Gatilho: carga acima de 20% no banco do SGC. Custo: desligar o adapter e voltar a ler o arquivo, cerca de
2 semanas de trabalho.

## Requisitos
RC-09, RC-11, RC-13.
