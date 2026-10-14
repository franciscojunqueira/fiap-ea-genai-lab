---
nivel: Público
dono: TI Operacional
---

# Runbook: incidente no core de pagamentos

**Área responsável:** TI Operacional, com o squad de Pagamentos
**Sistema:** core de pagamentos (API de pagamentos e saldos)
**Última revisão:** 10/09/2026

## Quando usar

Use este runbook quando houver sinal de problema no core de pagamentos:

- alerta do Grafana de taxa de erro ou latência da API de pagamentos e saldos;
- aumento de reclamações de PIX, cartão ou boleto que não liquidam;
- saldo divergente relatado por cliente ou pelo atendimento;
- falha em massa de pagamentos vindos do Gestão PJ.

O core de pagamentos é sistema crítico: em caso de dúvida, trate como incidente e escale.

## Primeiros passos do N1

1. Abra o painel "Service Health" e filtre os serviços payment-gateway, settlement-engine e
   payment-ledger. Anote o horário de início do desvio.
2. Verifique no PagerDuty se já existe incidente aberto para o mesmo sintoma. Se existir, junte-se
   a ele em vez de abrir outro.
3. Verifique no canal #deploys se houve deploy nos serviços de pagamento nas últimas horas.
4. Confira se o gateway de APIs está saudável; erro no gateway aparece como erro em todos os
   serviços ao mesmo tempo.
5. Abra o incidente no ServiceNow com os sintomas, horários e painéis consultados.

## Quem acionar

- **Squad de Pagamentos**, pelo plantão no PagerDuty, em todo incidente do core de pagamentos.
- **SRE on-call**, se a causa parecer de infraestrutura (cluster, rede, banco).
- **Segurança da Informação**, se houver suspeita de fraude ou acesso indevido; nesse caso vale a
  Política de Segurança da Informação.
- Coordenador de plantão, para avisar a diretoria quando houver perda financeira em curso.

A prioridade do incidente e os contatos seguem o procedimento de escalonamento da TI Operacional.

## O que o plantão não faz

- Não reinicia pods do payment-ledger: o livro-razão é append-only e o reinício pode deixar
  lançamentos pendentes. Só o squad de Pagamentos decide.
- Não altera saldo, lançamento ou status de pagamento em banco de dados.
- Não limpa o cache de saldo manualmente; a invalidação é automática por evento.
- Não faz rollback sem o squad de Pagamentos, exceto o rollback automático do pipeline de deploy.

## Depois do incidente

- Registre a linha do tempo no chamado.
- Post-mortem conduzido pelo squad de Pagamentos, com participação do plantão.
