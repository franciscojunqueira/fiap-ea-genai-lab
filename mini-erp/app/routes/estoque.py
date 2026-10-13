from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import EstoqueOut
from app.services import estoque as estoque_service

router = APIRouter(tags=["Estoque"])


@router.get("/estoque/{produto_id}", response_model=EstoqueOut)
def consultar_estoque(produto_id: int, db: Session = Depends(get_db)):
    """Consulta estoque de um produto."""
    estoque = estoque_service.consultar(db, produto_id)
    return EstoqueOut(
        produto_id=estoque.produto_id,
        produto_nome=estoque.produto.nome,
        quantidade=estoque.quantidade,
    )
