from sqlalchemy.orm import Session
from app.models import Produto, Estoque, Pedido, ItemPedido
from app.schemas import PedidoIn
from app.services.erros import NaoEncontrado, RegraDeNegocio


def criar(db: Session, dados: PedidoIn) -> Pedido:
    """Cria um pedido, valida estoque e abate quantidades."""
    if not dados.itens:
        raise RegraDeNegocio("Pedido deve ter pelo menos um item")

    # Validar todos os itens antes de gravar
    itens_validados = []
    for item in dados.itens:
        if item.quantidade <= 0:
            raise RegraDeNegocio(f"Quantidade deve ser maior que zero (produto_id={item.produto_id})")

        produto = db.query(Produto).filter(Produto.id == item.produto_id).first()
        if not produto:
            raise NaoEncontrado(f"Produto {item.produto_id} não encontrado")
        if not produto.ativo:
            raise RegraDeNegocio(f"Produto '{produto.nome}' está inativo")

        estoque = db.query(Estoque).filter(Estoque.produto_id == item.produto_id).first()
        if not estoque or estoque.quantidade < item.quantidade:
            disponivel = estoque.quantidade if estoque else 0
            raise RegraDeNegocio(
                f"Estoque insuficiente para '{produto.nome}': disponível={disponivel}, solicitado={item.quantidade}"
            )

        itens_validados.append((produto, estoque, item.quantidade))

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
    return pedido


def listar_ultimos(db: Session, limit: int) -> list[Pedido]:
    return db.query(Pedido).order_by(Pedido.id.desc()).limit(limit).all()


def obter(db: Session, pedido_id: int) -> Pedido:
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if not pedido:
        raise NaoEncontrado("Pedido não encontrado")
    return pedido

