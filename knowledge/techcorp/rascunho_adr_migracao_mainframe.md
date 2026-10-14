---
nivel: Interno
dono: Arquitetura
departamentos: [Arquitetura]
---

# RASCUNHO: ADR-0XX: Retirar a cobrança do mainframe (Projeto Farol)

> **CONFIDENCIAL DA ARQUITETURA. Rascunho, não aprovado.** Não circular fora do departamento de
> Arquitetura. O conteúdo pode mudar por inteiro antes de ir ao Comitê.

**Status:** Rascunho em discussão
**Data da versão:** 29/09/2026
**Autor:** arquiteto do domínio Pagamentos
**Codinome:** Projeto Farol

## Contexto

O mainframe de cobrança recebe a remessa do SGC, registra os boletos e devolve o arquivo de
retorno com os pagamentos. É a última carga de trabalho de negócio no mainframe, que tem contrato
de capacidade com renovação em 2028. Problemas:

- custo de MIPS concentrado em uma única função;
- poucos profissionais que conhecem os programas COBOL de cobrança;
- ciclo diário por arquivo, sem visão do pagamento no mesmo dia.

## Proposta em discussão

Substituir a função de cobrança do mainframe por um serviço de cobrança na plataforma digital,
com registro de boletos e recebimento de pagamentos por eventos no Kafka. O SGC continuaria
mandando remessa e recebendo retorno no mesmo layout, por um adaptador, para não depender da
substituição do SGC.

## Estimativa preliminar

| Item | Estimativa |
|---|---|
| Duração | 18 a 24 meses, em 3 fases |
| Equipe | 2 squads dedicados mais apoio de mainframe |
| Investimento | entre R$ 9 milhões e R$ 12 milhões |
| Retorno | fim do contrato de capacidade de cobrança no mainframe |

Números sem validação da área financeira.

## Riscos

1. Regras de negócio escondidas no COBOL sem documentação.
2. Período de operação paralela com duas fontes de verdade para pagamentos.
3. Dependência do layout de remessa e retorno do SGC, também sem documentação.
4. Concorrência por pessoas com o roadmap do core de pagamentos.
5. Exposição prematura da iniciativa afetar a negociação com o fornecedor do mainframe.

## Questões em aberto

- Fazer antes ou depois da substituição do SGC?
- Comprar plataforma de cobrança pronta ou construir?
- Como provar equivalência de resultados no paralelo?
