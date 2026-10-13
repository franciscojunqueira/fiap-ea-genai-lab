# SGC - Sistema de Gestão de Cobrança

Sistema batch de emissão e conciliação de boletos da TechCorp. Atende as faturas dos sistemas
de origem (Gestão PJ e outros) e envia a carteira em atraso para a área de Risco.

Última revisão deste documento: 2019-06.

## Requisitos

- Python 2.7
- Oracle Client 11g (tabelas SGC_* no schema COBRANCA)

## Execução

    python -m sgc ciclo

## Fluxo

1. Importa as faturas dos sistemas de origem (arquivo CSV).
2. Registra os boletos online no core pelo SGC-WS (webservice SOAP).
3. Gera a remessa para o mainframe de cobrança (layout em `layouts/`).
4. Processa o retorno do mainframe.
5. Gera o relatório de inadimplência para a área de Risco.

## Regras

- Vencimento em 30 dias.
- Juros de 1% ao mês e multa de 2%.

## Decisões

A escolha por troca de arquivos em vez de API online está registrada no ADR-07 (2016).

## Operação

Se o lote falhar no processamento do retorno, renomeie o arquivo `RET_` com o sufixo `_R` e
rode o lote de novo.

## Contato

Equipe Cobrança, ramal 4471.
