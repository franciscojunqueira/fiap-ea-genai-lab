# ADR-001: Acesso de agentes de IA ao Mini-ERP

**Status:** Aprovado
**Data:** 2026-10-05
**Decisores:** Arquitetura de Soluções

## Contexto

Agentes de IA precisam consultar e alterar dados do Mini-ERP. Hoje existem a API REST
(`mini-erp/`) e um MCP server local por stdio (`mcp-server/server.py`) com 10 tools.

## Requisitos e restrições

| ID | Requisito ou restrição | Origem |
|---|---|---|
| RQ-01 | Toda escrita no ERP passa por aprovação humana | Pedido da Arquitetura de Soluções |
| RQ-02 | Nenhum custo de infraestrutura | Pedido da Arquitetura de Soluções |
| RQ-03 | Funciona dentro do Codespace | Pedido da Arquitetura de Soluções |

## Alternativas consideradas

### A1: Agente chama a API REST direto

- **Prós:** nenhum componente novo.
- **Contras:** a aprovação humana depende de cada agente; o contrato da tool fica implícito no prompt.

### A2: MCP server local por stdio

- **Prós:** reaproveita `mcp-server/`; o cliente MCP pede aprovação antes de cada tool de escrita; roda no Codespace.
- **Contras:** cada operador sobe o seu processo; não há trilha de auditoria central.

### A3: MCP server remoto atrás de um gateway

- **Prós:** auditoria e política centralizadas.
- **Contras:** exige hospedagem e gateway, o que viola RQ-02.

## Decisão

Adotar **A2: MCP server local por stdio**.

## Justificativa

A2 atende RQ-01 (aprovação no cliente MCP), RQ-02 (sem infraestrutura) e RQ-03 (stdio no Codespace).
A1 deixa RQ-01 a critério de cada agente; A3 viola RQ-02.

## Consequências

### Positivas

- Contrato explícito das tools e aprovação humana nas escritas.

### Negativas e riscos

- Sem trilha de auditoria central; aceito enquanto o uso for de laboratório.

### Reversão

- Rever se surgir exigência de auditoria central. Migrar para A3 custa hospedar o servidor e configurar o gateway; as tools continuam as mesmas.

## Rastreabilidade

| Requisito | Como a decisão atende | Sensor que verifica |
|---|---|---|
| RQ-01 | o cliente MCP pede aprovação nas tools de escrita | teste do Lab 3: escrita sem aprovação é bloqueada |
| RQ-02 | processo local, sem serviço hospedado | `make check` sem serviço externo |
| RQ-03 | transporte stdio | `make check` lista as tools no Codespace |

## Pendências

- Nenhuma.
