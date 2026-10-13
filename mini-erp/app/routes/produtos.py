from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import ProdutoOut
from app.services import produtos

router = APIRouter(tags=["Produtos"])


@router.get("/produtos", response_model=list[ProdutoOut])
def listar_produtos(db: Session = Depends(get_db)):
    """Lista todos os produtos ativos."""
    return produtos.listar_ativos(db)


@router.get("/produtos/{produto_id}", response_model=ProdutoOut)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de um produto pelo ID."""
    return produtos.obter(db, produto_id)
