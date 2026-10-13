from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Estoque
from app.schemas import EstoqueOut

router = APIRouter(tags=["Estoque"])


@router.get("/estoque/{produto_id}", response_model=EstoqueOut)
def consultar_estoque(produto_id: int, db: Session = Depends(get_db)):
    """Consulta estoque de um produto."""
    estoque = db.query(Estoque).filter(Estoque.produto_id == produto_id).first()
    if not estoque:
        raise HTTPException(status_code=404, detail="Estoque não encontrado para este produto")
    return EstoqueOut(
        produto_id=estoque.produto_id,
        produto_nome=estoque.produto.nome,
        quantidade=estoque.quantidade,
    )
