---
name: escrevendo-adrs
description: Escreve e revisa Architecture Decision Records (ADRs) no padrão do repositório, com três alternativas reais, consequências positivas e negativas e rastreabilidade de requisito a decisão, conferidos por um validador. Use quando o usuário pedir para registrar, documentar, justificar ou revisar uma decisão de arquitetura, criar um ADR ou substituir um ADR existente.
---

# Escrevendo ADRs

Liberdade **baixa** no formato (o validador decide) e **alta** no conteúdo (o raciocínio é seu).
Os comandos rodam a partir da raiz do repositório. Os ADRs ficam em `docs/adr/`.

## Fluxo

Copie o checklist na resposta e marque cada passo concluído:

```
ADR:
- [ ] 1. Fatos levantados
- [ ] 2. Número reservado
- [ ] 3. ADR escrito a partir do modelo
- [ ] 4. Validador com PASS
- [ ] 5. Checklist de julgamento conferido
```

**1. Fatos.** Leia o que o usuário forneceu, os ADRs em `docs/adr/` e o código ou documento citado.
Todo fato do ADR precisa de origem: arquivo, medição ou pedido do usuário. O que faltar (decisores,
volumes, custos) vai para `## Pendências` como "a confirmar". Não invente.

**2. Número.**
```bash
python3 .claude/skills/escrevendo-adrs/scripts/validar_adr.py --proximo docs/adr
```
Arquivo: `docs/adr/ADR-NNN-titulo-em-kebab-case.md`. Status inicial: `Proposto`, salvo se o
usuário disser que a decisão já foi aprovada.

**3. Escrita.** Copie o esqueleto de [reference/modelo-adr.md](reference/modelo-adr.md) sem mudar
títulos nem ordem das seções. Para ver um ADR completo, leia
[reference/ADR-003-armazenamento-de-alertas.md](reference/ADR-003-armazenamento-de-alertas.md).

**4. Validação.** Rode, corrija cada ERRO e repita até dar PASS:
```bash
python3 .claude/skills/escrevendo-adrs/scripts/validar_adr.py docs/adr/ADR-NNN-titulo.md
```

**5. Julgamento.** O validador não enxerga isto. Confira cada item e corrija antes de entregar:

- **Alternativas reais:** alguém competente defenderia cada uma? "Não fazer nada" só entra se for viável.
- **Contras da escolhida:** a alternativa adotada tem contras honestos, não só prós.
- **Consequências negativas** com mitigação ou "aceito".
- **Números** (latência, custo, volume) só com fonte; sem fonte, escreva "estimativa" e diga a base.
- **Nada inventado:** não cite ADR, auditoria, norma ou ata que você não encontrou no repositório
  ou que o usuário não forneceu. Se um documento existente fizer isso, aponte na revisão.
- **Rastreabilidade:** cada requisito aponta para um sensor concreto (teste, fitness function, eval
  ou revisão), não para "monitorar".

## Revisar um ADR existente

Rode o validador e o checklist do passo 5 e devolva os problemas em lista, do mais grave ao menos
grave. Corrija o formato se o usuário pedir, mas **não troque a decisão**: mudar a decisão é um ADR
novo.

## Substituir um ADR

Escreva o novo ADR citando o antigo no Contexto. No antigo, troque só o Status para
`Substituído por ADR-NNN`. O texto do antigo não muda: ele é o registro histórico.
