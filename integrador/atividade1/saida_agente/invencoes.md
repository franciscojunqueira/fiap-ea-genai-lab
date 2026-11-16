# Registro do que o agente afirmou e o grupo conferiu

<!-- Atividade 1. Papel do verificador: este arquivo é escrito por uma pessoa do grupo, não pelo
agente. Um agente conferindo o que ele mesmo afirmou não é verificação. Aqui vêm 5 afirmações do
agente (a saída dele está em c4.md, dependencias.md e regras.md). Para cada uma, troquem os dois
[PREENCHER: ...]: como vocês conferiram e o veredito (correto, inventado, impreciso ou não
verificável). A dica diz só onde olhar; ela não diz se a afirmação está certa. -->

**Agente e modelo usados:** Claude Sonnet, em 08/11/2026 (saída gravada pelo professor)

| # | O que o agente afirmou (onde) | Onde conferir (dica) | Como conferimos | Veredito |
|---|---|---|---|---|
| 1 | "Gestão PJ não entra por CSV." (`c4.md:118`) | Leiam `sgc/importacao.py:85-101` e `ops/rodar_lote.sh:15-16`, e comparem com a saída do `make legado`. | [PREENCHER: o que vocês leram ou rodaram, e o que viram] | [PREENCHER: correto, inventado, impreciso ou não verificável] |
| 2 | "SGC-WS, webservice SOAP: não encontrado" (`dependencias.md:16`) | Leiam `README.md:20` e `sgc/remessa.py:53-81`, e comparem com a saída do `make legado`. | [PREENCHER: o que vocês leram ou rodaram, e o que viram] | [PREENCHER: correto, inventado, impreciso ou não verificável] |
| 3 | "Calendário só conhece 2019–2024: boleto vence no Natal de 2026" (`regras.md:15`) | Leiam `sgc/calendario.py:6-32`, e comparem com a saída do `make legado`. | [PREENCHER: o que vocês leram ou rodaram, e o que viram] | [PREENCHER: correto, inventado, impreciso ou não verificável] |
| 4 | "Sacado é achado só pelo nome normalizado, pegando o de menor id" (`regras.md:17`) | Leiam `sgc/importacao.py:29-32` e `sgc/util.py:24-27`, e comparem com a saída do `make legado`. | [PREENCHER: o que vocês leram ou rodaram, e o que viram] | [PREENCHER: correto, inventado, impreciso ou não verificável] |
| 5 | "`risco` não é somente leitura: no dia 1 do mês, baixa como perda" (`regras.md:28`) | Leiam `sgc/risco.py:53-56`, e comparem com a saída do `make legado`. | [PREENCHER: o que vocês leram ou rodaram, e o que viram] | [PREENCHER: correto, inventado, impreciso ou não verificável] |

## O que mudaríamos no harness

- [PREENCHER: uma mudança no prompt ou no AGENTS.md que faria o agente errar menos, ligada ao erro que vocês acharam]
- [PREENCHER: uma segunda mudança, ou o que o grupo conferiria sempre à mão, mesmo com o harness melhor]
