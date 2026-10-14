---
nivel: Público
dono: TI Operacional
---

# Procedimento de escalonamento de incidentes operacionais

**Área responsável:** Coordenação de TI Operacional
**Versão:** 4.0
**Vigência:** a partir de 01/06/2026

## Objetivo

Definir quem atende cada nível de suporte, como um incidente sobe de nível e em quanto tempo o
nível acionado deve dar a primeira resposta. Vale para incidentes operacionais de todos os
sistemas internos. Incidentes de segurança seguem a Política de Segurança da Informação, que
tem classificação própria.

## Níveis de suporte

| Nível | Quem | O que faz |
|---|---|---|
| N1 | Plantão de TI Operacional, 24x7 | registra o chamado, executa runbooks, faz a triagem |
| N2 | Especialistas de TI Operacional por sistema | diagnóstico técnico, ações fora de runbook |
| N3 | Squad dono do sistema | correção de código, de dados ou de integração |

## Prioridades

| Prioridade | Quando usar |
|---|---|
| P1 | sistema crítico parado ou perda financeira em curso, sem contorno |
| P2 | impacto relevante em negócio, com risco financeiro ou de dado incorreto, com contorno parcial |
| P3 | impacto limitado, contorno disponível, sem risco financeiro |

## Prazos de primeira resposta

Prazo contado da abertura do chamado até o primeiro contato do nível acionado:

- **P1 em 15 minutos**
- **P2 em 1 hora**
- **P3 em 1 dia útil**

Primeira resposta não é solução: é o aceite do chamado com o primeiro diagnóstico. Se o prazo
estourar, o N1 aciona o coordenador de plantão.

## Como escalar

1. O N1 escala ao N2 quando o runbook não resolve ou não existe runbook.
2. O N2 escala ao N3 quando a causa está em código, dado ou integração do sistema.
3. P1 vai direto ao N2 e ao N3 ao mesmo tempo, com aviso no canal #plantao-ti.

## Contatos de N3

| Sistema | N3 | Contato |
|---|---|---|
| SGC e cobrança | N3 de Cobrança: plantão do squad de Cobrança, ramal 4410 | fila COB-SGC |
| Core de pagamentos | plantão do squad de Pagamentos | PagerDuty |
| Gestão PJ | plantão do squad Gestão PJ | fila GPJ-SUPORTE |
| Plataforma e deploy | SRE on-call | PagerDuty |
