---
nivel: Público
dono: TI Operacional
---

# Runbook: lote noturno do SGC

**Área responsável:** TI Operacional (plantão 24x7)
**Sistema:** SGC, Sistema de Gestão de Cobrança
**Última revisão:** 04/08/2026

## O que é o lote

O lote noturno do SGC importa os arquivos CSV de faturas (Gestão PJ e cartões), emite os boletos,
gera a remessa para o mainframe de cobrança e concilia os pagamentos do retorno do dia. No fim,
gera o relatório diário de inadimplência para a área de Risco.

## Janela

- O lote roda **das 21:30 às 23:00, dias úteis**.
- Durante a janela, **nada de carga pesada no banco do SGC**: nada de consultas analíticas,
  exportações, reindexação ou deploy de qualquer sistema que leia o banco do SGC.
- Consultas de diagnóstico do plantão, se necessárias, só nas tabelas de controle do lote e com
  poucas linhas.

## Como acompanhar

1. No painel "SGC - Lote noturno" do Grafana, confira se as etapas aparecem em ordem:
   importação, emissão, remessa, conciliação, relatório.
2. Cada etapa grava início e fim na tabela de controle do lote. Etapa sem fim depois de 30 minutos
   é sinal de travamento.
3. Ao terminar, o lote grava o status final e o arquivo do relatório no diretório de saída.

## Se o lote falhar

1. Anote a etapa em que parou e a mensagem de erro do log do lote.
2. Verifique espaço em disco no servidor do SGC e no diretório de saída.
3. Verifique se os arquivos CSV de entrada do dia chegaram e não estão vazios.
4. Verifique se outro processo está segurando lock nas tabelas do lote.
5. Não reinicie o lote por conta própria se a falha foi na conciliação: a conciliação baixa
   pagamentos e não pode rodar pela metade duas vezes.
6. Abra chamado na **fila COB-SGC** no ServiceNow com: etapa, horário, mensagem de erro, o que
   já foi verificado e se algum arquivo saiu.
7. Avise o canal #plantao-ti no Slack e acompanhe o chamado até o aceite do N2.

Para escalar além do N2, siga o procedimento de escalonamento da TI Operacional.

## Fora do escopo deste runbook

- Reprocessamento do arquivo de retorno do banco: tem runbook próprio,
  `runbook_reprocessar_retorno.md`.
- Backup do banco do SGC: ver `runbook_backup_sgc.md`.
