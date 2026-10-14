---
nivel: Interno
dono: Arquitetura
---

# Arquitetura de Microsserviços — TechCorp

**Documento:** Visão Geral Arquitetural
**Versão:** 2.1
**Data:** 2024-08-01

## Visão Geral

A TechCorp opera uma plataforma de serviços financeiros digitais com 47 microsserviços
distribuídos em 3 domínios de negócio:

### Domínio: Pagamentos (18 serviços)
- **payment-gateway:** Orquestra fluxos de pagamento (PIX, cartão, boleto)
- **fraud-detection:** Análise em tempo real com ML (latência < 100ms)
- **settlement-engine:** Reconciliação e liquidação D+1
- **payment-ledger:** Livro-razão de transações (append-only, imutável)

### Domínio: Onboarding (12 serviços)
- **kyc-service:** Know Your Customer — validação de documentos e biometria
- **credit-scoring:** Score de crédito integrado com bureaus (Serasa, SPC)
- **account-provisioning:** Criação de contas e cartões virtuais
- **notification-hub:** Envio de SMS, email, push (integrado com AWS SNS)

### Domínio: Plataforma (17 serviços)
- **auth-service:** Autenticação e autorização (OAuth2 + RBAC)
- **config-service:** Configuração centralizada (Spring Cloud Config)
- **api-gateway:** Kong Gateway (ADR-001) — roteamento, rate limiting, TLS
- **event-bus:** Apache Kafka — 12 tópicos, retenção 7 dias

## Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Linguagens | Java 21 (70%), Go 1.22 (20%), Python 3.12 (10% — ML) |
| Runtime | Kubernetes 1.29 no EKS |
| Service Mesh | Istio 1.20 (mTLS entre serviços) |
| CI/CD | GitHub Actions → ArgoCD (GitOps) |
| Banco de Dados | PostgreSQL 16 (principal), Redis 7 (cache), DynamoDB (sessões) |
| Mensageria | Apache Kafka 3.6, Amazon SQS (dead-letter queues) |
| Observabilidade | OpenTelemetry → Grafana Stack (ADR-003) |

## Padrões Obrigatórios

1. **Comunicação síncrona:** gRPC entre serviços internos, REST apenas para APIs externas
2. **Comunicação assíncrona:** Kafka para eventos de domínio, SQS para tasks
3. **Circuit Breaker:** Resilience4j obrigatório para chamadas entre serviços
4. **Idempotência:** Toda operação de escrita deve ser idempotente (idempotency key obrigatória)
5. **Health checks:** /health e /ready obrigatórios em todos os serviços
6. **Documentação:** OpenAPI 3.1 obrigatória para APIs REST, Protobuf para gRPC

## SLAs e SLOs

| Serviço | Disponibilidade | Latência p99 | RPS máximo |
|---------|----------------|--------------|------------|
| payment-gateway | 99.99% | < 200ms | 5,000 |
| fraud-detection | 99.95% | < 100ms | 10,000 |
| auth-service | 99.99% | < 50ms | 20,000 |
| Demais serviços | 99.9% | < 500ms | 1,000 |
