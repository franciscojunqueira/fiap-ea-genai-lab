---
nivel: Interno
dono: TI Operacional
---

# Runbook: backup do banco do SGC

**Área responsável:** TI Operacional, equipe de banco de dados
**Sistema:** SGC, Sistema de Gestão de Cobrança
**Última revisão:** 26/08/2026

## Escopo

Backup do banco de dados do SGC e acompanhamento dos testes de restauração. Não cobre os arquivos
de entrada e saída do lote, que são copiados pela rotina de arquivos do servidor.

## Rotina diária

- O backup completo do banco do SGC roda **todos os dias às 03:00**, depois do fim do lote noturno.
- A cópia vai para o armazenamento de backup corporativo, com cópia em segundo site.
- O agendador registra início, fim, tamanho e status de cada execução.

## Conferência pelo plantão

Na passagem de turno da manhã, o N1 confere:

1. Status da execução da noite no agendador: "concluído".
2. Tamanho do backup coerente com os últimos dias (variação maior que 20% merece chamado).
3. Ausência de alerta no painel de backup.

Se o backup falhou:

1. Verifique espaço no destino e conectividade com o servidor do SGC.
2. Não rode o backup manualmente em horário comercial sem o N2: ele pesa no banco.
3. Nunca rode backup manual durante a janela do lote noturno (ver `runbook_lote_sgc.md`).
4. Abra chamado na fila COB-SGC com o log da execução.

## Teste de restauração

- O teste de restauração é **trimestral**, feito pela equipe de banco de dados em ambiente
  isolado, nunca sobre o banco de produção.
- O teste restaura o último backup completo e confere a contagem de registros das tabelas
  principais e a abertura do sistema em modo de consulta.
- **O último teste de restauração, em 08/2026, levou 2h10**, do início da cópia até a validação.
- O resultado de cada teste é registrado no chamado de mudança correspondente.

## Histórico recente

| Teste | Resultado | Observação |
|---|---|---|
| 02/2026 | sucesso | sem observações |
| 05/2026 | sucesso com ressalva | uma tabela de histórico demorou mais que o esperado |
| 08/2026 | sucesso | ver tempo acima |

## Contatos

- Equipe de banco de dados: fila DBA no ServiceNow.
- Dono do sistema: squad de Cobrança.
