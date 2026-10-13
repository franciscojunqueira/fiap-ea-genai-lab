from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import PedidoIn, PedidoOut, ItemPedidoOut
from app.services import pedidos

router = APIRouter(tags=["Pedidos"])


@router.post("/pedidos", response_model=PedidoOut, status_code=201)
def criar_pedido(dados: PedidoIn, db: Session = Depends(get_db)):
    """Cria um pedido, valida estoque e abate quantidades."""
    return _pedido_to_out(pedidos.criar(db, dados))


@router.get("/pedidos", response_model=list[PedidoOut])
def listar_pedidos(limit: int = 10, db: Session = Depends(get_db)):
    """Retorna os últimos pedidos (padrão: 10)."""
    return [_pedido_to_out(p) for p in pedidos.listar_ultimos(db, limit)]


@router.post("/pedidos/{pedido_id}/cancelar", response_model=PedidoOut)
def cancelar_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Cancela o pedido e devolve o estoque (ERP-142); pedido faturado responde 409."""
    return _pedido_to_out(pedidos.cancelar(db, pedido_id))


@router.get("/pedidos/{pedido_id}", response_model=PedidoOut)
def obter_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de um pedido com seus itens."""
    return _pedido_to_out(pedidos.obter(db, pedido_id))


def _pedido_to_out(pedido) -> PedidoOut:
    return PedidoOut(
        id=pedido.id,
        nome_cliente=pedido.nome_cliente,
        total=pedido.total,
        status=pedido.status,
        criado_em=pedido.criado_em,
        itens=[
            ItemPedidoOut(
                produto_id=item.produto_id,
                produto_nome=item.produto.nome,
                quantidade=item.quantidade,
                preco_unitario=item.preco_unitario,
                subtotal=item.subtotal,
            )
            for item in pedido.itens
        ],
    )

