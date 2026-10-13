from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Produto
from app.schemas import ProdutoOut

router = APIRouter(tags=["Produtos"])


@router.get("/produtos", response_model=list[ProdutoOut])
def listar_produtos(db: Session = Depends(get_db)):
    """Lista todos os produtos ativos."""
    return db.query(Produto).filter(Produto.ativo == True).all()


@router.get("/produtos/{produto_id}", response_model=ProdutoOut)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de um produto pelo ID."""
    produto = db.query(Produto).filter(Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto
