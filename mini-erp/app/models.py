from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db import Base


class Produto(Base):
    __tablename__ = "produto"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, default="")
    preco = Column(Float, nullable=False)
    ativo = Column(Boolean, default=True)

    estoque = relationship("Estoque", back_populates="produto", uselist=False)


class Estoque(Base):
    __tablename__ = "estoque"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produto.id"), unique=True, nullable=False)
    quantidade = Column(Integer, nullable=False, default=0)

    produto = relationship("Produto", back_populates="estoque")


class Pedido(Base):
    __tablename__ = "pedido"

    id = Column(Integer, primary_key=True, index=True)
    nome_cliente = Column(String, nullable=False)
    total = Column(Float, default=0.0)
    status = Column(String, default="CRIADO")
    criado_em = Column(DateTime, default=datetime.now)

    itens = relationship("ItemPedido", back_populates="pedido")
    fatura = relationship("Fatura", back_populates="pedido", uselist=False)


class ItemPedido(Base):
    __tablename__ = "item_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedido.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produto.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)

    pedido = relationship("Pedido", back_populates="itens")
    produto = relationship("Produto")


class Fatura(Base):
    __tablename__ = "fatura"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedido.id"), unique=True, nullable=False)
    valor_total = Column(Float, nullable=False)
    status = Column(String, default="GERADA")
    criada_em = Column(DateTime, default=datetime.now)

    pedido = relationship("Pedido", back_populates="fatura")
