# Seção do AGENTS.md (EXEMPLO de um sistema fictício; não é o Lab 1)

O grupo escreve, no `AGENTS.md` da raiz, uma seção `## Mini-ERP` no mesmo estilo. Este exemplo é de
um sistema inventado, o "Gestão PJ", só para mostrar a forma:

```markdown
## Gestão PJ

- Código em `gestao-pj/`; a regra de negócio fica em `gestao-pj/regras/`, nunca nas rotas.
- Datas sempre em UTC no banco; a tela converte. Não converta fuso no backend.
- Erro de negócio: levante `ErroDeCadastro(motivo)`; quem traduz para HTTP é `app.py`.
- Antes de dizer que terminou, rode `make pj-check` e mostre a saída.
- `gestao-pj/legado/` é código antigo mantido como está: não refatore.
```

**O que observar:**

- **Só o que o agente não sabe sozinho.** Ele lê o código; não sabe a convenção da equipe, o que é
  dívida aceita nem qual comando prova que terminou.
- **Curto.** O `AGENTS.md` entra em toda conversa e gasta contexto: 4 a 6 linhas bastam.
- **Instrução verificável.** "Rode `make pj-check`" pode ser conferido; "escreva código limpo", não.
- **O que não tocar** é tão importante quanto o que fazer.
- Na seção `## Mini-ERP` do Lab 1, o check confere que ela diz onde fica a regra de negócio.
