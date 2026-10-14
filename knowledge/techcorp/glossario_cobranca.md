---
nivel: Público
dono: TI Operacional
---

# Glossário de cobrança

**Área responsável:** TI Operacional, com revisão do squad de Cobrança
**Última revisão:** 18/08/2026

Termos usados nos runbooks, nos chamados da fila COB-SGC e nas conversas com o squad de Cobrança.

**Baixa**
Registro, no SGC, de que um boleto foi pago. A baixa tira o título da carteira em aberto. Uma
baixa indevida faz um título em aberto parecer pago.

**Boleto**
Documento de cobrança com código de barras e linha digitável. Na TechCorp, os boletos das faturas
do Gestão PJ e dos cartões são emitidos pelo SGC.

**Carteira em aberto**
Conjunto de boletos emitidos e ainda não pagos, vencidos ou a vencer.

**CNAB**
Padrão de layout de arquivos de troca entre empresas e bancos para cobrança, definido pela
FEBRABAN, com linhas de tamanho fixo e campos por posição. É a referência usual para arquivos de
remessa e retorno de cobrança.

**Conciliação**
Comparação entre os pagamentos informados no retorno e os títulos em aberto no SGC, que resulta
nas baixas. Divergências vão para uma fila de tratamento manual.

**Fatura**
Documento de venda emitido no Gestão PJ. Cada fatura chega ao SGC pelo arquivo CSV diário e vira
um boleto.

**Lote noturno**
Processamento do SGC nos dias úteis à noite: importação dos arquivos de faturas, emissão de
boletos, geração da remessa, conciliação do retorno e geração do relatório diário de
inadimplência. Horário e cuidados estão no runbook do lote.

**Remessa**
Arquivo que o SGC envia ao mainframe de cobrança com os boletos novos, alterações e pedidos de
baixa manual.

**Retorno**
Arquivo que o mainframe de cobrança devolve ao SGC com os pagamentos recebidos e as ocorrências
(registro, rejeição, liquidação). É a entrada da conciliação.

**Título**
Nome genérico para cada obrigação cobrada. No dia a dia, título e boleto são usados como
sinônimos.

**Vencido**
Título não pago depois da data de vencimento. O relatório de inadimplência agrupa os vencidos
por faixa de dias de atraso.
