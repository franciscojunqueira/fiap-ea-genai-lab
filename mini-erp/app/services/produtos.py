from sqlalchemy.orm import Session
from app.models import Produto
from app.services.erros import NaoEncontrado


def listar_ativos(db: Session) -> list[Produto]:
    return db.query(Produto).filter(Produto.ativo == True).all()  # noqa: E712


def obter(db: Session, produto_id: int) -> Produto:
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise NaoEncontrado("Produto não encontrado")
    return produto
