from datetime import datetime
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_db
from app.services import ajustes as ajustes_service

router = APIRouter(tags=["Ajustes de estoque"])


class AjusteIn(BaseModel):
    variacao: int
    motivo: str
    solicitante: str = "agente (MCP)"


class DecisaoIn(BaseModel):
    aprovador: str


class AjusteOut(BaseModel):
    id: int
    produto_id: int
    variacao: int
    motivo: str
    status: str
    solicitado_por: str
    solicitado_em: datetime
    aprovado_por: str | None = None
    decidido_em: datetime | None = None
    executado_em: datetime | None = None
    estoque_antes: int | None = None
    estoque_depois: int | None = None

    model_config = {"from_attributes": True}


@router.post("/estoque/{produto_id}/ajustes", response_model=AjusteOut, status_code=201)
def solicitar_ajuste(produto_id: int, dados: AjusteIn, db: Session = Depends(get_db)):
    """Cria um pedido de ajuste PENDENTE. Não altera o estoque."""
    return ajustes_service.solicitar(db, produto_id, dados.variacao, dados.motivo, dados.solicitante)


@router.get("/ajustes", response_model=list[AjusteOut])
def listar_ajustes(limit: int = 50, db: Session = Depends(get_db)):
    """Trilha dos ajustes: quem pediu, quem aprovou, quando, estoque antes e depois."""
    return ajustes_service.listar(db, limit)


@router.get("/ajustes/{ajuste_id}", response_model=AjusteOut)
def obter_ajuste(ajuste_id: int, db: Session = Depends(get_db)):
    return ajustes_service.obter(db, ajuste_id)


@router.post("/ajustes/{ajuste_id}/aprovar", response_model=AjusteOut)
def aprovar_ajuste(ajuste_id: int, dados: DecisaoIn, db: Session = Depends(get_db)):
    """Aprovação humana, feita pela tela do ERP (aba Aprovações). O agente não tem tool para isto."""
    return ajustes_service.decidir(db, ajuste_id, dados.aprovador, aprovar=True)


@router.post("/ajustes/{ajuste_id}/rejeitar", response_model=AjusteOut)
def rejeitar_ajuste(ajuste_id: int, dados: DecisaoIn, db: Session = Depends(get_db)):
    return ajustes_service.decidir(db, ajuste_id, dados.aprovador, aprovar=False)


@router.post("/ajustes/{ajuste_id}/executar", response_model=AjusteOut)
def executar_ajuste(ajuste_id: int, db: Session = Depends(get_db)):
    """Aplica o ajuste aprovado. Chamar de novo devolve o mesmo resultado, sem aplicar outra vez."""
    return ajustes_service.executar(db, ajuste_id)
