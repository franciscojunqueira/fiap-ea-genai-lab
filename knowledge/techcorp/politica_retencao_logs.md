---
nivel: Interno
dono: Arquitetura
---

# Política de retenção de logs e trilhas de auditoria

**Versão:** 1.2
**Data de aprovação:** 05/05/2025
**Aprovado por:** Comitê de Arquitetura e Segurança da Informação
**Área responsável:** Arquitetura, com o SRE

## Objetivo

Definir por quanto tempo cada tipo de registro é guardado, onde fica e quem pode consultá-lo,
equilibrando investigação de incidentes, exigências de auditoria e custo de armazenamento.

## Tipos de registro e prazos

| Tipo | Exemplos | Retenção | Onde |
|---|---|---|---|
| Logs de aplicação | erros, avisos, informações de execução | 90 dias | Grafana Loki (ADR-003) |
| Métricas | latência, taxa de erro, uso de recursos | 13 meses (com redução de resolução) | Grafana Mimir |
| Traces | rastreamento distribuído | 15 dias | Grafana Tempo |
| Trilhas de auditoria | quem acessou, quem alterou, aprovações | 5 anos | armazenamento imutável (WORM) |
| Logs de segurança | autenticação, acesso privilegiado | 5 anos | SIEM da Segurança da Informação |

## Regras

1. **Logs de aplicação ficam 90 dias** e depois são apagados automaticamente.
2. **Trilhas de auditoria ficam 5 anos**, em armazenamento que não permite alteração nem exclusão
   antes do prazo.
3. Log de aplicação não substitui trilha de auditoria: evento que precisa ser auditado é gravado
   na trilha, com usuário, data e hora, ação e objeto.
4. Logs não podem conter senha, token, número completo de cartão nem dado pessoal sem
   mascaramento. CPF e CNPJ aparecem mascarados nos logs de aplicação.
5. Pedido de preservação por investigação ou ordem judicial suspende a exclusão dos registros
   envolvidos até a liberação pelo Jurídico.

## Sistemas legados

Sistemas que não enviam logs ao Loki, como o SGC, mantêm logs locais com rotação própria. O dono
do sistema garante o prazo mínimo desta política, copiando os logs para o armazenamento central
quando a rotação local for menor.

## Acesso

- Logs de aplicação: squads donos e SRE.
- Trilhas de auditoria: Auditoria Interna e Segurança da Informação; squads só por solicitação.
- Toda consulta às trilhas de auditoria também fica registrada.

## Revisão

Revisão anual, ou antes se surgir nova exigência regulatória.
