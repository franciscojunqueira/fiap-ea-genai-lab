---
nivel: Interno
dono: Arquitetura
---

# ADR-005: Integração do Gestão PJ com o SGC por arquivo CSV

**Status:** Aprovado
**Data:** 20/05/2019
**Decisores:** Comitê de Arquitetura, gerência de Cobrança, gerência do produto Gestão PJ
**Repositório:** ADRs de integração (numeração própria, anterior à série da plataforma digital)

## Contexto

O Gestão PJ passou a gerar faturas para os clientes PJ, e cada fatura precisa virar boleto. Quem
emite boletos e concilia pagamentos é o SGC, Sistema de Gestão de Cobrança, implantado em 2011 e
mantido por fornecedor externo. O SGC:

- não tem API: recebe dados só por arquivo ou digitação na tela;
- já importa um arquivo CSV diário dos cartões, no lote noturno;
- só pode ser alterado pelo fornecedor, que cobrava **R$ 380 mil** pela camada de serviços
  (API) proposta, com prazo de 9 meses.

## Decisão

Integrar o Gestão PJ ao SGC por **arquivo CSV diário**:

1. O Gestão PJ gera, no fim do dia útil, um arquivo com as faturas emitidas no dia.
2. O arquivo segue um **layout próprio**, definido pelo squad de Cobrança junto com o
   fornecedor, com uma linha por fatura.
3. O arquivo é depositado no diretório de entrada do SGC antes do início do lote noturno.
4. O lote do SGC importa o arquivo e emite os boletos.

## Alternativas consideradas

| Alternativa | Por que não |
|---|---|
| Camada de serviços (API) no SGC | custo do fornecedor e prazo; o SGC tinha substituição prevista |
| Gestão PJ gravar direto no banco do SGC | quebra o suporte do fornecedor e pula as validações do SGC |
| Digitação manual das faturas | inviável no volume esperado |

## Consequências

- **Acoplamento por layout:** qualquer mudança de campo no Gestão PJ exige mudança no SGC, e o
  layout fica documentado só no código dos dois lados.
- **Sem confirmação de recebimento:** o Gestão PJ não sabe se o arquivo foi importado, nem quais
  linhas foram rejeitadas. Fatura sem boleto só aparece quando o cliente reclama.
- Latência de até um dia útil entre a fatura e o boleto.
- Erro no arquivo afeta o lote inteiro da noite.
- A substituição do SGC, prevista na época, não aconteceu; a decisão vale enquanto o SGC existir.
