from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Produto, Estoque, Pedido, ItemPedido
from app.schemas import PedidoIn, PedidoOut, ItemPedidoOut

router = APIRouter(tags=["Pedidos"])


@router.post("/pedidos", response_model=PedidoOut, status_code=201)
def criar_pedido(dados: PedidoIn, db: Session = Depends(get_db)):
    """Cria um pedido, valida estoque e abate quantidades."""
    if not dados.itens:
        raise HTTPException(status_code=400, detail="Pedido deve ter pelo menos um item")

    # Validar todos os itens antes de gravar
    itens_validados = []
    for item in dados.itens:
        if item.quantidade <= 0:
            raise HTTPException(status_code=400, detail=f"Quantidade deve ser maior que zero (produto_id={item.produto_id})")

        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise HTTPException(status_code=404, detail=f"Produto {item.produto_id} não encontrado")
        if not produto.ativo:
            raise HTTPException(status_code=400, detail=f"Produto '{produto.nome}' está inativo")

        estoque = db.query(Estoque).filter(Estoque.produto_id == item.produto_id).first()
        if not estoque or estoque.quantidade < item.quantidade:
            disponivel = estoque.quantidade if estoque else 0
            raise HTTPException(
                status_code=400,
                detail=f"Estoque insuficiente para '{produto.nome}': disponível={disponivel}, solicitado={item.quantidade}",
            )

        itens_validados.append((produto, estoque, item.quantidade))

    # Criar pedido
    pedido = Pedido(nome_cliente=dados.nome_cliente)
    db.add(pedido)
    db.flush()

    total = 0.0
    for produto, estoque, quantidade in itens_validados:
        subtotal = quantidade * produto.preco
        total += subtotal

        db.add(ItemPedido(
            pedido_id=pedido.id,
            produto_id=produto.id,
            quantidade=quantidade,
            preco_unitario=produto.preco,
            subtotal=subtotal,
        ))

        # Abater estoque
        estoque.quantidade -= quantidade

    pedido.total = total
    db.commit()
    db.refresh(pedido)

    return _pedido_to_out(pedido)


@router.get("/pedidos", response_model=list[PedidoOut])
def listar_pedidos(limit: int = 10, db: Session = Depends(get_db)):
    """Retorna os últimos pedidos (padrão: 10)."""
    pedidos = db.query(Pedido).order_by(Pedido.id.desc()).limit(limit).all()
    return [_pedido_to_out(p) for p in pedidos]


@router.get("/pedidos/{pedido_id}", response_model=PedidoOut)
def obter_pedido(pedido_id: int, db: Session = Depends(get_db)):
    """Retorna detalhes de um pedido com seus itens."""
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return _pedido_to_out(pedido)


def _pedido_to_out(pedido: Pedido) -> PedidoOut:
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
