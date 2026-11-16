# ADR-103: AI gateway do Bússola

**Status:** proposto · **Data:** 2026-11-10 · **Decisores:** Arquitetura de Soluções

## Contexto
Toda chamada do Bússola a um modelo precisa de cota por departamento (RC-08), de registro para
auditoria por 5 anos (RC-05) e de roteamento do dado pessoal para uma região no Brasil (RC-03).

## Alternativas
1. **Azure API Management v2, serviço gerenciado,** com políticas de cota, cache e registro.
2. **LiteLLM, código aberto, hospedado pelo banco.** Sem licença, mas com operação própria.
3. **Sem gateway:** cada aplicação chama o modelo direto.

## Decisão
Usar o Azure API Management v2 na região Brazil South.

## Consequências
- Cota, cache e registro por política, sem código na aplicação.
- O registro do gateway não tem o usuário nem as fontes: a aplicação completa o registro (RC-05).

## Reversão
Sem custo: basta trocar o endereço do gateway nas aplicações.

## Requisitos
RC-03, RC-05, RC-08.
