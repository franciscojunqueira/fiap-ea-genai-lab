# Política de Segurança da Informação — TechCorp

**Versão:** 3.2
**Última atualização:** 2024-10-01
**Aprovado por:** CISO, Comitê Executivo

## 1. Classificação de Dados

Todos os dados da TechCorp são classificados em 4 níveis:

| Nível | Descrição | Exemplos | Controles |
|-------|-----------|----------|-----------|
| **Público** | Pode ser divulgado externamente | Blog posts, docs de API pública | Nenhum controle especial |
| **Interno** | Apenas funcionários | Organogramas, manuais internos | Autenticação corporativa |
| **Confidencial** | Necessidade de saber (need-to-know) | Dados de clientes, roadmap | Criptografia em repouso + RBAC |
| **Restrito** | Altamente sensível | Dados financeiros, PII, chaves criptográficas | Criptografia end-to-end + MFA + auditoria completa |

## 2. Autenticação e Acesso

- **SSO obrigatório** via Okta para todos os sistemas corporativos
- **MFA obrigatório** para acesso a dados Confidenciais e Restritos
- **Tokens de API** devem ter expiração máxima de 90 dias
- **Service accounts** devem usar mTLS ou tokens JWT com rotação automática
- **Princípio do menor privilégio:** acessos revisados trimestralmente

## 3. Desenvolvimento Seguro

- Todo código deve passar por SAST (SonarQube) antes do merge
- Dependências escaneadas semanalmente com Snyk
- Secrets NUNCA no código — usar HashiCorp Vault
- Container images escaneadas com Trivy antes do deploy
- Penetration testing anual obrigatório por empresa externa

## 4. Resposta a Incidentes

- Incidentes de segurança devem ser reportados em até 1 hora ao CISO
- Classificação de severidade: P1 (breach ativo), P2 (vulnerabilidade explorada), P3 (vulnerabilidade descoberta), P4 (não-conformidade)
- P1 e P2: war room imediato com SRE, Security e Engineering leads
- Post-mortem obrigatório em 48 horas para P1 e P2
- Comunicação externa (clientes/reguladores) em até 72 horas para breach de dados pessoais (LGPD)

## 5. Uso de IA Generativa

- Dados Restritos e Confidenciais NÃO podem ser enviados a LLMs externos (OpenAI, Anthropic) sem anonimização prévia
- Uso de Copilot/ChatGPT permitido apenas para dados Públicos e Internos
- Modelos self-hosted (via Azure OpenAI ou Bedrock) aprovados para dados Confidenciais com DPA assinado
- Todo uso de IA deve ser registrado no catálogo de IA da empresa
- Outputs de LLM que afetam decisões de negócio devem ter revisão humana obrigatória
