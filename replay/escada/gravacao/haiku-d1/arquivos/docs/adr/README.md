# Architecture Decision Records (ADRs)

Este diretório contém as decisões arquiteturais importantes do Mini-ERP, documentadas como ADRs (Architecture Decision Records).

## O que é um ADR?

Um ADR é um documento que registra uma decisão arquitetural importante, seu contexto, consequências e alternativas consideradas. ADRs ajudam a:

- Documentar o "porquê" por trás das decisões
- Facilitar onboarding de novos membros do time
- Servir como ponto de referência para futuras mudanças
- Manter histórico de decisões e trade-offs

## ADRs Atuais

| # | Título | Status | Data |
|---|--------|--------|------|
| [0001](./0001-migrate-sqlite-to-postgresql.md) | Migração de SQLite para PostgreSQL | Proposto | 2026-10-12 |

## Status

- **Proposto**: Decisão sugerida, aguardando aprovação
- **Aceito**: Decisão aprovada e em implementação
- **Implementado**: Decisão concluída e em produção
- **Revogado**: Decisão foi substituída por outra
- **Obsoleto**: Decisão não é mais relevante

## Processo de ADR

### Criação

1. Criar novo arquivo `NNNN-titulo-da-decisao.md`
2. Usar template padrão com seções obrigatórias
3. Submeter como PR para revisão
4. Aproveitar comentários do time para refinamento
5. Marcar como "Aceito" após aprovação

### Revisão

- Code review padrão do projeto
- Envolvimento de stakeholders relevantes
- Discussão de alternativas e trade-offs

### Manutenção

- Atualizar status conforme progresso
- Adicionar à tabela acima
- Referenciar ADRs em documentação relevante

## Template Padrão

```markdown
# ADR NNNN: Título da Decisão

**Data:** YYYY-MM-DD  
**Status:** Proposto/Aceito/Implementado/Revogado/Obsoleto  
**Autor:** Nome

## Problema

Descrever o problema que motivou a decisão.

## Contexto

Informações relevantes sobre o projeto, restrições, constraints.

## Decisão

A decisão arquitetural tomada.

## Consequências

Impactos positivos e negativos.

## Alternativas Consideradas

Outras opções exploradas e por que foram descartadas.

## Referências

Links relevantes e documentação.
```

## Referências

- [ADR GitHub](https://adr.github.io/)
- [Documenting Architecture Decisions](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions)
