from sqlalchemy.orm import Session
from app.models import Estoque
from app.services.erros import NaoEncontrado


def consultar(db: Session, produto_id: int) -> Estoque:
    estoque = db.query(Estoque).filter(Estoque.produto_id == produto_id).first()
    if not estoque:
        raise NaoEncontrado("Estoque não encontrado para este produto")
    return estoque
