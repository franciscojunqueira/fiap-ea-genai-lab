---
nivel: Interno
dono: Arquitetura
---

# ADR-003: Stack de Observabilidade Unificada

**Status:** Aprovado
**Data:** 2024-07-20
**Decisores:** Comitê de Arquitetura, SRE Lead

## Contexto

A TechCorp utiliza ferramentas de observabilidade fragmentadas:
- Logs: ELK Stack (auto-hospedado, 3 nós Elasticsearch)
- Métricas: Datadog (SaaS, custo crescente — $23k/mês)
- Traces: Jaeger (sub-utilizado, apenas 5 serviços instrumentados)

Problemas identificados:
- Correlação entre logs, métricas e traces é manual e demorada
- MTTR (Mean Time to Resolution) médio de 47 minutos para incidentes P1
- Custo total de observabilidade: $35k/mês

## Decisão

Consolidar para stack baseada em OpenTelemetry + Grafana:
- **Coleta:** OpenTelemetry Collector como agente universal
- **Logs:** Grafana Loki (substituindo ELK)
- **Métricas:** Grafana Mimir (substituindo Datadog)
- **Traces:** Grafana Tempo (substituindo Jaeger)
- **Visualização:** Grafana dashboards unificados

## Justificativa

- OpenTelemetry é padrão CNCF — vendor-neutral e amplamente adotado
- Stack Grafana reduz custo para ~$12k/mês (infra auto-hospedada)
- Correlação nativa entre sinais (logs ↔ traces ↔ métricas) via TraceID
- Meta: reduzir MTTR de 47 para menos de 20 minutos

## Consequências

- Migração em 4 fases ao longo de 6 meses
- Fase 1: instrumentar novos serviços com OTel SDK (já iniciado)
- Fase 2: migrar métricas Datadog → Mimir
- Fase 3: migrar logs ELK → Loki
- Fase 4: aposentar Jaeger, ativar Tempo
- Risco: curva de aprendizado da equipe com nova stack
- Ganho esperado: dashboards unificados com drill-down de métricas para traces
