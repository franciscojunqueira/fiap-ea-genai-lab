"""Erros de negócio dos services. As rotas não os tratam: o main.py os traduz para HTTP."""


class NaoEncontrado(Exception):
    """Recurso inexistente (vira 404)."""


class RegraDeNegocio(Exception):
    """Regra violada (vira 400, ou o status informado, como 409 para conflito de estado)."""

    def __init__(self, detalhe: str, status: int = 400):
        super().__init__(detalhe)
        self.status = status
