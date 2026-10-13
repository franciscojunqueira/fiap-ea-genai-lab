# ADR-003: Armazenamento dos alertas do Mini-ERP

**Status:** Aprovado
**Data:** 2026-10-12
**Decisores:** Arquitetura de Soluções (time do curso)

## Contexto

Os alertas do Mini-ERP (`POST /alertas`, usados pela tool `enviar_alerta` do MCP server) ficam numa
lista em memória (`mini-erp/app/routes/alertas.py`). Um restart do ERP apaga todos os alertas, e o
agente que consulta `listar_alertas` depois de um restart conclui, errado, que nada aconteceu.
O ERP roda num único processo, num Codespace, com SQLite como banco.

## Requisitos e restrições

| ID | Requisito ou restrição | Origem |
|---|---|---|
| RQ-01 | Alertas sobrevivem a restart do ERP | Debrief do Lab 3 (agente concluiu "sem alertas" após restart) |
| RQ-02 | Nenhum serviço novo para subir no Codespace | Regra de labs: o aluno não escreve infraestrutura |
| RQ-03 | Consulta dos 20 alertas mais recentes continua igual | Contrato atual da tool `listar_alertas` |

## Alternativas consideradas

### A1: Manter em memória

- **Prós:** zero mudança; nenhum risco de regressão.
- **Contras:** não atende RQ-01.

### A2: Tabela `alerta` no SQLite existente

Nova tabela no mesmo banco, criada pelo `create_all` que o ERP já executa ao subir.

- **Prós:** atende RQ-01 sem serviço novo (RQ-02); reaproveita sessão e modelos SQLAlchemy.
- **Contras:** o campo `detalhes` (dict) vira JSON serializado; a escrita concorre com pedidos no mesmo arquivo.

### A3: Redis com lista limitada

- **Prós:** `LPUSH` + `LTRIM` resolve "últimos 20" de forma nativa; padrão comum em produção.
- **Contras:** viola RQ-02 (mais um serviço no devcontainer); persistência depende de configurar AOF/RDB.

## Decisão

Adotar **A2: Tabela `alerta` no SQLite existente**. A rota passa a gravar e ler pela sessão do banco.

## Justificativa

A2 é a única alternativa que atende RQ-01 e RQ-02 ao mesmo tempo. A1 falha em RQ-01 e A3 falha em
RQ-02. RQ-03 se mantém com `ORDER BY id DESC LIMIT 20`. A concorrência de escrita no SQLite não
preocupa no volume de um lab (um grupo, poucas escritas por minuto).

## Consequências

### Positivas

- Alertas persistem entre restarts; o agente deixa de tirar conclusões erradas.
- Nenhuma dependência nova.

### Negativas e riscos

- `detalhes` perde a tipagem de dict no banco; mitigação: serializar e desserializar no schema Pydantic.
- Se o ERP um dia rodar com várias réplicas, SQLite deixa de servir; aceito, porque fica fora do escopo do curso.

## Rastreabilidade

| Requisito | Como a decisão atende | Sensor que verifica |
|---|---|---|
| RQ-01 | alertas gravados em tabela | teste: cria alerta, reinicia o ERP, `GET /alertas` devolve o alerta |
| RQ-02 | usa o SQLite que já existe | `make check` continua sem serviço novo |
| RQ-03 | `ORDER BY id DESC LIMIT 20` | teste de contrato da tool `listar_alertas` |

## Pendências

- Nenhuma.
