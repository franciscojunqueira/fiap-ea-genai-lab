---
nivel: Interno
dono: Arquitetura
---

# Ata do Comitê de Arquitetura

**Data:** 17/09/2026, 14:00 às 15:30
**Local:** sala Paulista 3 e videoconferência
**Secretária:** analista de governança de arquitetura
**Presentes:** coordenador de arquitetura (presidente), arquitetos dos domínios Pagamentos,
Onboarding e Plataforma, tech lead do squad de Cobrança, tech lead do squad Gestão PJ, SRE lead,
representante de TI Operacional

## Pauta

1. Integração entre Gestão PJ e SGC
2. Documentação do layout do arquivo do SGC
3. Revisão de custos de observabilidade

## Item 1: integração entre Gestão PJ e SGC

O squad Gestão PJ relatou faturas sem boleto em agosto, descobertas só por reclamação de cliente.
Foi lembrado que a integração por arquivo segue o ADR-005 e que o SGC continua sem API.

**Decisão:** manter a integração por arquivo CSV com o SGC até a substituição do sistema, que
segue sem data definida. Não haverá investimento em API no SGC.

## Item 2: documentação do layout do arquivo

O layout do arquivo existe hoje só no código do Gestão PJ e na rotina de importação do SGC.
TI Operacional relatou que, nas falhas de importação, o plantão não tem onde conferir os campos.

**Decisão:** pedir ao squad de Cobrança a documentação do layout do arquivo (campos, tipos,
obrigatoriedade e regras de rejeição), com prazo **30/11/2026**. Responsável: tech lead do squad
de Cobrança. O documento deve ficar no repositório de documentação de arquitetura.

## Item 3: revisão de custos de observabilidade

O SRE lead apresentou o custo da stack Grafana depois da migração do ADR-003. O armazenamento de
logs cresceu acima do previsto por causa de logs de depuração deixados ativos em produção.

**Decisões:**

- Squads revisam o nível de log dos seus serviços até o próximo comitê.
- SRE propõe, no próximo comitê, amostragem de traces para serviços não críticos.

## Encaminhamentos

| Ação | Responsável | Prazo |
|---|---|---|
| Documentar o layout do arquivo do SGC | squad de Cobrança | conforme item 2 |
| Revisar nível de log por serviço | tech leads | próximo comitê |
| Proposta de amostragem de traces | SRE lead | próximo comitê |

Próxima reunião: 15/10/2026.
