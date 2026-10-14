---
nivel: Interno
dono: Arquitetura
---

# Catálogo de APIs internas

**Área responsável:** Arquitetura, governança de APIs
**Última atualização:** 30/09/2026
**Fonte:** registro do gateway de APIs (ADR-001) e respostas dos squads

## Como ler este catálogo

- **Status:** Produção, Em construção, Depreciada ou Sem API.
- **Contrato:** OpenAPI 3.1 para REST e Protobuf para gRPC, conforme os padrões obrigatórios da
  arquitetura de microsserviços.
- APIs externas passam pelo gateway; chamadas entre serviços internos usam gRPC.

## APIs

| Sistema ou serviço | API | Dono | Status | Observação |
|---|---|---|---|---|
| Core de pagamentos | API de pagamentos e saldos (REST) | squad de Pagamentos | Produção | consulta de saldo com cache Redis |
| payment-gateway | orquestração de pagamentos (gRPC) | squad de Pagamentos | Produção | PIX, cartão e boleto |
| settlement-engine | liquidação D+1 (gRPC) | squad de Pagamentos | Produção | uso interno |
| kyc-service | validação de documentos (gRPC) | squad de Onboarding | Produção | dados pessoais; acesso restrito |
| credit-scoring | score de crédito (gRPC) | squad de Onboarding | Produção | integra bureaus externos |
| auth-service | autenticação e autorização (REST) | squad de Plataforma | Produção | OAuth2 + RBAC |
| notification-hub | envio de SMS, e-mail e push (gRPC) | squad de Plataforma | Produção | |
| Gestão PJ | API REST de pedidos, faturas, estoque e alertas | squad Gestão PJ | Produção | |
| Gestão PJ | API de relatórios v1 | squad Gestão PJ | Depreciada | desligamento previsto para 2027 |
| SGC | nenhuma | squad de Cobrança | Sem API | sem API (integração por arquivo, ADR-005) |
| Mainframe de cobrança | nenhuma | squad de Cobrança | Sem API | troca por arquivo de remessa e retorno com o SGC |

## Eventos publicados no barramento

Os eventos de domínio seguem o ADR-004 (Kafka). Os mais consumidos:

| Evento | Produtor | Consumidores principais |
|---|---|---|
| pagamento-liquidado | payment-gateway | payment-ledger, core de pagamentos (invalidação de cache) |
| conta-criada | account-provisioning | notification-hub, credit-scoring |
| fatura-emitida | Gestão PJ | notificação ao cliente PJ |

O SGC não publica nem consome eventos.

## Como registrar uma API nova

1. Publique o contrato no repositório de contratos.
2. Registre a rota no gateway, com rate limiting e autenticação.
3. Peça a inclusão neste catálogo por chamado à Arquitetura, informando dono e status.
