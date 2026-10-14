---
nivel: Interno
dono: Arquitetura
---

# ADR-001: Adoção de API Gateway Centralizado

**Status:** Aprovado
**Data:** 2024-08-15
**Decisores:** Comitê de Arquitetura

## Contexto

A TechCorp possui atualmente 47 microsserviços expostos diretamente à internet,
cada um gerenciando sua própria autenticação e rate limiting. Isso resultou em:
- 3 incidentes de segurança nos últimos 6 meses por configuração inconsistente de TLS
- Impossibilidade de aplicar políticas de throttling uniformes
- Dificuldade de observabilidade cross-service

## Decisão

Adotar o Kong Gateway como API Gateway centralizado para todos os serviços externos.

## Justificativa

- Kong oferece plugins nativos para OAuth2, rate limiting e observabilidade
- Licença open-source com suporte enterprise disponível
- Time de plataforma já possui experiência com Kong em projeto anterior
- Alternativas avaliadas: AWS API Gateway (vendor lock-in), Envoy (complexidade operacional maior)

## Consequências

- Todos os novos serviços DEVEM ser expostos via Gateway a partir de setembro/2024
- Serviços existentes serão migrados em 3 ondas até dezembro/2024
- Custo estimado: 2 sprints de engenharia + licença Enterprise ($45k/ano)
- Risco: ponto único de falha — mitigado com deploy multi-AZ e circuit breakers
