# ADR-101: Modelo de linguagem do Bússola

**Status:** proposto · **Data:** 2026-11-10 · **Decisores:** Arquitetura de Soluções

## Contexto
O Bússola responde perguntas da Arquitetura, do Risco e da TI Operacional sobre documentos internos
(caso.md, seção 3). O cenário alvo tem 4.500 consultas por dia útil e orçamento de até R$ 35 mil por
mês (RC-08). A TI Operacional precisa de resposta em até 8 s no p95 (RC-06).

## Alternativas
1. **Claude Haiku 5.5 pela API.** Barato e rápido. Acertou 7 de 10 perguntas no RAG dos testes do Lab 2.
2. **Claude Sonnet 5.5 pela API.** Mais caro, mais forte em análise.
3. **Treinar um modelo de linguagem próprio, do zero, no datacenter do banco.** Controle total.

## Decisão
Usar o Claude Haiku 5.5 para todas as perguntas.

## Consequências
- Custo baixo e latência dentro da RC-06.
- Perguntas que juntam dois documentos podem errar, como nos testes do Lab 2. A busca agêntica, que acertou
  10 de 10, fica como alternativa para essas perguntas.
- O dado pessoal do Risco não passa por este modelo: vai para a rota no Brasil do gateway (RC-03, ADR-103).

## Reversão
Gatilho: a eval cair abaixo de 60% de acerto em duas semanas seguidas. Custo: trocar o apelido no gateway,
rodar a eval de novo e revisar o orçamento (o Sonnet custa cerca de 10 vezes o Haiku por consulta).

## Requisitos
RC-03, RC-06, RC-08.
