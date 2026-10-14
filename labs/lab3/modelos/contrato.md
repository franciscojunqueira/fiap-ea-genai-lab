# Lab 3: contrato MCP das tools de ajuste de estoque

<!-- Do grupo (autores e relator). Linhas que começam com '<' são instruções: substituam e apaguem.
A tabela vai para a seção "Contrato MCP" de integrador/pacote/01-design.md (checkpoint). -->

## Contrato

<Uma linha por tool do contrato de vocês (labs/lab3/descricoes/grupo.toml), com o nome completo minierp:nome_da_tool. "Idempotente": chamar duas vezes dá o mesmo resultado? Se não, como vocês protegem? "Departamentos": quem do caso pode usar.>

<E pelo menos uma linha sgc:nome_da_tool para o legado sem API, com o que a Atividade 1 mostrou (arquivo e banco, sem API): por exemplo, ler o status do lote ou pedir o reprocessamento de um retorno, que não é idempotente (como vocês protegem?). Não precisa existir: é o contrato que o adapter teria.>

| Servidor:ferramenta | Lê ou escreve | Entrada | Saída | Aprovação humana | Idempotente | Departamentos |
|---|---|---|---|---|---|---|
| | | | | | | |

## O que a comparação mostrou

<Verificador: o que mudou entre ruim, boa e grupo, cenário por cenário (labs/lab3/comparacoes/). Conferiram no registro de chamadas o que o script contou?>

## Pergunta de decisão

<Que operações de escrita o Bússola oferece no piloto, com que aprovação, e o que acontece se o agente repetir a chamada?>
