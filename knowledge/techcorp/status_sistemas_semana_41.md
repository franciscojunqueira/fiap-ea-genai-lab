---
nivel: Interno
dono: TI Operacional
---

# Status de sistemas: semana 41 de 2026

**Período:** 05/10/2026 a 11/10/2026
**Elaborado por:** Coordenação de TI Operacional
**Distribuição:** gestores de TI, tech leads, plantão

## Resumo

Semana estável na plataforma digital. Um atraso relevante no lote noturno do SGC e dois incidentes
menores, todos encerrados.

| Sistema | Situação na semana |
|---|---|
| Plataforma digital (47 microsserviços) | normal |
| Core de pagamentos | normal |
| Gestão PJ | um incidente menor (ver abaixo) |
| SGC, lote noturno | um atraso na terça-feira |
| Gateway de APIs | um incidente menor (ver abaixo) |

## Lote noturno do SGC

| Dia | Início | Fim | Situação |
|---|---|---|---|
| Seg 05/10 | 21:30 | 22:41 | concluído |
| Ter 06/10 | 21:30 | 23:47 | concluído com atraso |
| Qua 07/10 | 21:30 | 22:38 | concluído |
| Qui 08/10 | 21:30 | 22:52 | concluído |
| Sex 09/10 | 21:30 | 22:44 | concluído |

**Terça, 06/10/2026:** o lote do SGC atrasou 47 minutos por disco cheio no diretório de saída do
servidor do SGC. A etapa de relatório parou ao gravar o arquivo de inadimplência. O plantão liberou
espaço removendo arquivos de log antigos, e o N2 reiniciou só a etapa de relatório. Nenhum boleto
deixou de ser emitido. O relatório chegou atrasado para a área de Risco na quarta de manhã.

Ação: chamado na fila COB-SGC para criar alerta de ocupação de disco no servidor do SGC.

## Incidentes menores

1. **Gestão PJ, quarta 07/10:** lentidão na tela de pedidos por cerca de 20 minutos, causada por
   uma consulta sem índice depois de um deploy. Corrigida com novo índice; sem perda de dados.
2. **Gateway de APIs, sexta 09/10:** certificado de um serviço interno de homologação expirou e
   o gateway recusou chamadas desse ambiente. Produção não foi afetada. Certificado renovado e
   incluído no inventário de expiração.

## Mudanças executadas

- 3 deploys de serviços não críticos e 1 de serviço business-critical, todos dentro da janela.
- Nenhuma mudança no SGC.

## Pontos de atenção para a semana 42

- Acompanhar o alerta de disco do SGC até a implantação.
- Antecipar mudanças da última semana de outubro, que é blackout de deploy (fechamento do mês).
