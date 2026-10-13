from datetime import datetime
from pydantic import BaseModel


# --- Produto ---

class ProdutoOut(BaseModel):
    id: int
    nome: str
    descricao: str
    preco: float
    ativo: bool

    model_config = {"from_attributes": True}


# --- Estoque ---

class EstoqueOut(BaseModel):
    produto_id: int
    produto_nome: str
    quantidade: int


# --- Pedido (request) ---

class ItemPedidoIn(BaseModel):
    produto_id: int
    quantidade: int


class PedidoIn(BaseModel):
    nome_cliente: str
    itens: list[ItemPedidoIn]


# --- Pedido (response) ---

class ItemPedidoOut(BaseModel):
    produto_id: int
    produto_nome: str
    quantidade: int
    preco_unitario: float
    subtotal: float


class PedidoOut(BaseModel):
    id: int
    nome_cliente: str
    total: float
    status: str
    criado_em: datetime
    itens: list[ItemPedidoOut]


# --- Fatura ---

class FaturaOut(BaseModel):
    id: int
    pedido_id: int
    valor_total: float
    status: str
    criada_em: datetime
