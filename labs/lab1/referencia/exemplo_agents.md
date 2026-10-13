
## Mini-ERP

- Camadas: rota (`mini-erp/app/routes/`) → service (`mini-erp/app/services/`) → modelo. A rota não importa modelos nem acessa o banco.
- Regra de negócio fica no service. Erros de negócio: `NaoEncontrado` e `RegraDeNegocio(detalhe, status)` de `services/erros.py`; o `main.py` traduz para HTTP.
- `routes/faturas.py` é dívida registrada (acessa o banco direto): não copie o padrão dele.
- Testes do Lab 1: `make lab1-check`. Não preencha `labs/lab1/verificacao.md`: é do verificador.
