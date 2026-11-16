# Registro do que o agente afirmou e o grupo conferiu

<!-- Atividade 1. Papel do verificador: este arquivo é escrito por uma pessoa do grupo, não pelo
agente. Um agente conferindo o que ele mesmo afirmou não é verificação. Aqui vêm 5 afirmações do
agente (a saída dele está em c4.md, dependencias.md e regras.md). Para cada uma, troquem os dois
[PREENCHER: ...]: como vocês conferiram (cite arquivo:linha do código ou o que o make legado
mostrou) e o veredito: correto, errado, impreciso ou não verificável. A coluna "Onde conferir" é igual
nas 5 linhas e não diz se a afirmação está certa. Depois da conferência, corrijam no arquivo de origem
(c4.md, dependencias.md ou regras.md) tudo o que marcaram como errado ou impreciso e escrevam ao lado
a nota "corrigido pelo verificador". -->

**Agente e modelo usados:** Claude Sonnet, em 08/11/2026 (saída gravada pelo professor)

| # | O que o agente afirmou (onde) | Onde conferir | Como conferimos | Veredito |
|---|---|---|---|---|
| 1 | "Gestão PJ não entra por CSV." (`c4.md:118`) | Abram `c4.md` e rodem `make legado`. | [PREENCHER: o que vocês leram ou rodaram, e o que viram] | [PREENCHER: correto, errado, impreciso ou não verificável] |
| 2 | "SGC-WS, webservice SOAP: não encontrado" (`dependencias.md:16`) | Abram `dependencias.md` e rodem `make legado`. | [PREENCHER: o que vocês leram ou rodaram, e o que viram] | [PREENCHER: correto, errado, impreciso ou não verificável] |
| 3 | "Calendário só conhece 2019–2024: boleto vence no Natal de 2026" (`regras.md:15`) | Abram `regras.md` e rodem `make legado`. | [PREENCHER: o que vocês leram ou rodaram, e o que viram] | [PREENCHER: correto, errado, impreciso ou não verificável] |
| 4 | "Sacado é achado só pelo nome normalizado, pegando o de menor id" (`regras.md:17`) | Abram `regras.md` e rodem `make legado`. | [PREENCHER: o que vocês leram ou rodaram, e o que viram] | [PREENCHER: correto, errado, impreciso ou não verificável] |
| 5 | "`risco` não é somente leitura: no dia 1 do mês, baixa como perda" (`regras.md:28`) | Abram `regras.md` e rodem `make legado`. | [PREENCHER: o que vocês leram ou rodaram, e o que viram] | [PREENCHER: correto, errado, impreciso ou não verificável] |

## O que mudaríamos no harness

- [PREENCHER: uma mudança no prompt ou no AGENTS.md que faria o agente errar menos, ligada ao erro que vocês acharam]
- [PREENCHER: uma segunda mudança, ou o que o grupo conferiria sempre à mão, mesmo com o harness melhor]
