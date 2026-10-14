---
nivel: Público
dono: TI Operacional
---

# FAQ do plantão de TI Operacional

**Área responsável:** Coordenação de TI Operacional
**Última revisão:** 15/09/2026
**Público:** analistas N1 e N2 do plantão 24x7, inclusive recém-chegados

## Acesso

**Como entro nos sistemas no primeiro dia de plantão?**
Todos os sistemas corporativos usam SSO pelo Okta. O acesso de plantão é liberado pelo
coordenador depois do treinamento de integração. Sistemas com dados Confidenciais ou Restritos
pedem MFA.

**Esqueci a senha ou o MFA não funciona. E agora?**
Use o autoatendimento do Okta. Se não resolver, ligue para a central de serviços pelo ramal
4000, que atende 24x7.

**Preciso acessar o servidor do SGC. Tenho acesso?**
O N1 tem acesso de leitura ao painel e aos logs do lote. Acesso ao servidor e ao banco do SGC é
do N2, com registro no chamado.

## VPN e trabalho remoto

**Como acesso a rede interna de casa?**
Pela VPN corporativa, com o cliente instalado no notebook da empresa. Não há VPN em equipamento
pessoal.

**A VPN cai durante a madrugada. É normal?**
A sessão expira a cada 12 horas. Reconecte. Se cair de novo logo depois de reconectar, abra chamado
para a equipe de Redes.

## Onde ficam as coisas

**Onde estão os runbooks?**
Na base de conhecimento da TI Operacional, na pasta "Runbooks", um por sistema ou procedimento.
Os mais usados: deploy em produção, lote noturno do SGC, reprocessamento do retorno do SGC,
incidente no core de pagamentos e backup do SGC.

**Onde abro chamados?**
No ServiceNow, na fila do sistema afetado. Exemplos: COB-SGC para o SGC e a cobrança,
GPJ-SUPORTE para o Gestão PJ.

**Onde vejo se o sistema está saudável?**
Nos painéis do Grafana. Comece pelo "Service Health" e, para o SGC, pelo "SGC - Lote noturno".

## Quem acionar

**Não sei se devo escalar. O que faço?**
Siga o procedimento de escalonamento da TI Operacional, que define níveis, prioridades e contatos.
Na dúvida, fale com o coordenador de plantão.

**Quem está de plantão nos squads?**
A escala de cada squad está no PagerDuty. Para o SGC, o contato está no procedimento de
escalonamento.

**Posso mexer no banco do SGC durante o lote noturno?**
Não. Veja a janela no runbook do lote noturno do SGC.

## Boas práticas

- Registre tudo no chamado, inclusive o que não funcionou.
- Não execute comando fora de runbook sem o N2.
- Na passagem de turno, liste os chamados abertos e o que está pendente.
