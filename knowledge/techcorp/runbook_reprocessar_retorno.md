---
nivel: Público
dono: TI Operacional
---

# Runbook: reprocessar o arquivo de retorno no SGC

**Área responsável:** TI Operacional
**Sistema:** SGC, Sistema de Gestão de Cobrança
**Última revisão:** 22/07/2026

> **ATENÇÃO: o reprocessamento do retorno não é idempotente: reprocessar o mesmo arquivo baixa
> os pagamentos de novo.** Antes de reprocessar, confirme que o arquivo não foi processado.

## Quando usar

O arquivo de retorno chega do mainframe de cobrança com os pagamentos de boletos do dia. O lote
noturno o processa na etapa de conciliação. Use este runbook só quando o retorno **não** foi
processado: arquivo chegou atrasado, etapa de conciliação falhou antes de começar ou o arquivo
ficou parado no diretório de entrada.

## Antes de reprocessar

1. Confira que não é horário do lote noturno (ver `runbook_lote_sgc.md`). Fora da janela, siga.
2. Localize o arquivo no diretório de entrada de retorno e anote nome, data e tamanho.
3. Consulte a tabela de controle de arquivos do SGC pelo nome do arquivo:
   - sem registro: o arquivo não foi processado, pode seguir;
   - com registro "processado": **pare**. Não reprocesse;
   - com registro "erro" ou "parcial": não reprocesse; abra chamado na fila COB-SGC.
4. Peça a segunda conferência a outro analista do plantão e registre no chamado.

## Como reprocessar

1. Mova o arquivo para o diretório de reprocessamento do SGC.
2. Execute o job de conciliação avulsa pelo agendador, informando o nome do arquivo.
3. Acompanhe o log até a mensagem de fim; anote a quantidade de títulos baixados.
4. Compare essa quantidade com o total de registros de detalhe do arquivo. Diferença acima de
   zero: abra chamado na fila COB-SGC.

## Se um retorno foi processado duas vezes

Sinais: pagamentos baixados em dobro, relatório de inadimplência com queda anormal, cliente com
boleto pago aparecendo com crédito a maior.

1. **Não reprocessar de novo**, nem tentar estornar pela tela do SGC.
2. Abra incidente **P2** na **fila COB-SGC**, com o nome do arquivo e os horários das duas
   execuções.
3. Acione o **N3 de Cobrança** conforme o procedimento de escalonamento da TI Operacional.
4. Avise a área de Risco que o relatório do dia pode estar distorcido.

O estorno das baixas duplicadas é feito só pelo squad de Cobrança.
