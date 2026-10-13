from datetime import datetime
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Alertas"])

# Armazenamento em memória
_alertas: list[dict] = []
_seq_id = 0


class AlertaIn(BaseModel):
    tipo: str
    mensagem: str
    detalhes: dict | None = None


class AlertaOut(BaseModel):
    id: int
    timestamp: datetime
    tipo: str
    mensagem: str
    detalhes: dict | None = None


@router.post("/alertas", response_model=AlertaOut, status_code=201)
def criar_alerta(dados: AlertaIn):
    """Registra um alerta (armazenado em memória)."""
    global _seq_id
    _seq_id += 1
    alerta = {
        "id": _seq_id,
        "timestamp": datetime.now(),
        "tipo": dados.tipo,
        "mensagem": dados.mensagem,
        "detalhes": dados.detalhes,
    }
    _alertas.append(alerta)
    return alerta


@router.get("/alertas", response_model=list[AlertaOut])
def listar_alertas():
    """Retorna os últimos 20 alertas (mais recentes primeiro)."""
    return list(reversed(_alertas[-20:]))
