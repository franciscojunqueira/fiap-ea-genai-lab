# Runbook: Deploy em Produção — TechCorp

**Responsável:** Time de Plataforma
**Última revisão:** 2024-09-15

## Pré-requisitos do Deploy

1. PR aprovado por pelo menos 2 revisores
2. Pipeline CI verde (testes unitários, integração e SAST)
3. Change Request aprovada no ServiceNow (CR obrigatória para serviços críticos)
4. Feature flag configurada para rollout gradual (quando aplicável)

## Janelas de Deploy

| Tipo de Serviço | Janela Permitida | Aprovação Necessária |
|-----------------|-----------------|---------------------|
| Non-critical | Seg-Sex, 09:00-17:00 | Tech Lead |
| Business-critical | Seg-Qui, 10:00-15:00 | Tech Lead + Engineering Manager |
| Core banking | Terça e Quinta, 10:00-14:00 | VP Engineering + Change Advisory Board |

**Blackout periods:** Última semana do mês (fechamento financeiro), Black Friday ± 3 dias

## Processo de Deploy

### 1. Preparação (T-30min)
- Verificar dashboards de baseline no Grafana
- Confirmar que não há incidentes ativos (verificar PagerDuty)
- Notificar canal #deploys no Slack

### 2. Execução
- Deploy via ArgoCD (GitOps): merge na branch `release/*` dispara sync automático
- Rollout strategy: canary 10% → 25% → 50% → 100%
- Cada estágio deve rodar por mínimo 5 minutos antes de avançar
- Monitorar: error rate, latência p99, CPU/memory dos pods

### 3. Validação (T+15min)
- Executar smoke tests automatizados
- Verificar métricas chave no Grafana dashboard "Service Health"
- Confirmar ausência de erros novos no Sentry

### 4. Rollback (se necessário)
- Critérios automáticos de rollback: error rate > 1% ou latência p99 > 500ms
- Rollback manual: reverter commit na branch release, ArgoCD sincroniza automaticamente
- Tempo máximo para decisão de rollback: 10 minutos após detecção de anomalia
- Pós-rollback: incidente P3 aberto automaticamente, post-mortem em 24h

## Contatos de Escalação

| Papel | Nome | Telefone |
|-------|------|----------|
| SRE On-call | Rotação semanal | Ver PagerDuty |
| Platform Lead | Marina Santos | Ramal 4521 |
| VP Engineering | Carlos Mendes | Ramal 4001 |
