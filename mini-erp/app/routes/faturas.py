from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Pedido, Fatura
from app.schemas import FaturaOut

router = APIRouter(tags=["Faturas"])


@router.post("/pedidos/{pedido_id}/fatura", response_model=FaturaOut, status_code=201)
def gerar_fatura(pedido_id: int, db: Session = Depends(get_db)):
    """Gera fatura simulada para um pedido."""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if pedido.fatura:
        raise HTTPException(status_code=400, detail="Pedido já possui fatura gerada")

    fatura = Fatura(pedido_id=pedido.id, valor_total=pedido.total)
    pedido.status = "FATURADO"

    db.add(fatura)
    db.commit()
    db.refresh(fatura)

    return FaturaOut(
        id=fatura.id,
        pedido_id=fatura.pedido_id,
        valor_total=fatura.valor_total,
        status=fatura.status,
        criada_em=fatura.criada_em,
    )


@router.get("/faturas/{fatura_id}", response_model=FaturaOut)
def obter_fatura(fatura_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de uma fatura."""
    fatura = db.query(Fatura).filter(Fatura.id == fatura_id).first()
    if not fatura:
        raise HTTPException(status_code=404, detail="Fatura não encontrada")
    return FaturaOut(
        id=fatura.id,
        pedido_id=fatura.pedido_id,
        valor_total=fatura.valor_total,
        status=fatura.status,
        criada_em=fatura.criada_em,
    )
