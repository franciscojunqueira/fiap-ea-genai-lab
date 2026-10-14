"""Ajuste de estoque com aprovação humana (Lab 3). Arquivo separado de models.py para o `make atualizar`
não sobrescrever o que o grupo mudou no Lab 1."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from app.db import Base


class AjusteEstoque(Base):
    __tablename__ = "ajuste_estoque"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produto.id"), nullable=False)
    variacao = Column(Integer, nullable=False)          # +entrada / -saída, nunca o valor final
    motivo = Column(String, nullable=False)
    status = Column(String, default="PENDENTE")         # PENDENTE → APROVADO → EXECUTADO, ou REJEITADO
    solicitado_por = Column(String, nullable=False)
    solicitado_em = Column(DateTime, default=datetime.now)
    aprovado_por = Column(String)
    decidido_em = Column(DateTime)
    executado_em = Column(DateTime)
    estoque_antes = Column(Integer)
    estoque_depois = Column(Integer)
