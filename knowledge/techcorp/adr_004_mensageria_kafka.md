---
nivel: Interno
dono: Arquitetura
---

# ADR-004: Kafka como barramento de eventos

**Status:** Aprovado
**Data:** 2024-10-14
**Decisores:** Comitê de Arquitetura, SRE Lead

## Contexto

A plataforma digital já usava Apache Kafka em alguns fluxos de pagamentos, mas sem regra comum:
cada squad escolhia entre Kafka, SQS e chamadas síncronas para avisar outros serviços de um fato
de negócio. Consequências observadas:

- eventos de domínio duplicados em formatos diferentes para o mesmo fato;
- serviços acoplados por chamadas síncronas em cadeia, com falhas em cascata;
- nenhum controle de quem produz e quem consome cada tópico.

## Decisão

Adotar o **Apache Kafka** (3.6, gerenciado pelo squad de Plataforma) como barramento único de
eventos de domínio da plataforma digital, com as regras:

1. Todo evento de domínio é publicado no Kafka, em tópico com dono declarado.
2. Esquemas registrados no Schema Registry, em Avro, com compatibilidade retroativa obrigatória.
3. Retenção padrão de 7 dias; tópicos com retenção maior precisam de justificativa.
4. Consumidores idempotentes: o mesmo evento pode chegar mais de uma vez.
5. SQS continua para filas de tarefas e dead-letter queues, não para eventos de domínio.

## Alternativas avaliadas

| Alternativa | Por que não |
|---|---|
| Amazon SNS + SQS para tudo | sem reprocessamento por offset; ordenação limitada |
| RabbitMQ | menor vazão e menos experiência no time |
| Continuar sem padrão | mantém o problema |

## Consequências

- Squads passam a desenhar integrações por eventos antes de chamadas síncronas.
- O squad de Plataforma opera o cluster e o Schema Registry, com painéis no Grafana (ADR-003).
- Tópicos existentes migram para o padrão de nomes e esquema até março de 2025.
- Sistemas legados que não publicam eventos (por exemplo, os que trocam arquivos) ficam fora do
  barramento até ganharem um adaptador.
- Risco: crescimento descontrolado de tópicos; mitigado pela revisão trimestral de tópicos sem
  consumidor.
